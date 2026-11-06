"""Audit stored issuer CIKs against data.sec.gov submissions metadata."""
import hashlib
import json
from pathlib import Path
import re
import urllib.request

from research_cohort import write_rows


UA = 'insider-option-patterns/0.1 (research; local CIK audit)'


def lookup(cik):
    padded = str(cik).lstrip('0').zfill(10)
    url = f'https://data.sec.gov/submissions/CIK{padded}.json'
    req = urllib.request.Request(url, headers={'User-Agent': UA, 'Accept-Encoding': 'identity'})
    with urllib.request.urlopen(req, timeout=30) as resp:
        data = json.load(resp)
    return dict(cik=padded, name=data.get('name'), tickers=data.get('tickers') or [],
                former_names=[f.get('name') for f in (data.get('formerNames') or [])[:5]])


def tokens(name):
    # Keep 3-character tokens so short tickers/names like CEB or ADT can match.
    return {w for w in re.findall(r'[a-z0-9]+', (name or '').lower()) if len(w) >= 3}


def suspicious(event_name, edgar_name, former_names=None):
    if not event_name:
        return True
    left = tokens(event_name)
    if not left:
        return True
    for candidate in [edgar_name] + list(former_names or []):
        if left & tokens(candidate):
            return False
    return True


def run(root=Path('.'), fetch=lookup):
    events = json.loads((root/'results/reviewed_cohort/events.json').read_text())
    rows = []
    for event in events:
        cik = event.get('issuer_cik')
        row = dict(event_id=event['event_id'], symbol=event['symbol'],
                   stored_issuer=event.get('issuer'), stored_cik=cik,
                   lookup_status='pending')
        if not cik:
            row.update(lookup_status='missing_cik', suspicious=True)
            rows.append(row)
            continue
        try:
            meta = fetch(cik)
            row.update(lookup_status='ok', edgar_name=meta['name'], edgar_tickers=meta['tickers'],
                       former_names=meta['former_names'],
                       suspicious=suspicious(event.get('issuer'), meta['name'], meta['former_names']))
        except Exception as exc:
            row.update(lookup_status='query_failed', query_error=str(exc), suspicious=True)
        rows.append(row)
    folder = root/'results/cik_audit'
    folder.mkdir(parents=True, exist_ok=True)
    write_rows(folder, 'cik_checks', rows)
    manifest = dict(events=len(rows),
                    suspicious=sum(bool(r.get('suspicious')) for r in rows),
                    query_failed=sum(r['lookup_status']=='query_failed' for r in rows),
                    source_sha256={'results/reviewed_cohort/events.json':
                                   hashlib.sha256((root/'results/reviewed_cohort/events.json').read_bytes()).hexdigest()})
    (folder/'manifest.json').write_text(json.dumps(manifest, indent=2) + '\n')
    lines = ['# Issuer CIK audit', '',
             f"{manifest['events']} events checked against data.sec.gov submissions. "
             f"{manifest['suspicious']} marked suspicious by conservative name overlap. "
             'Suspicious is a diagnostic, not proof of error.', '',
             '| Event | Stored issuer | Stored CIK | EDGAR name | Suspicious |',
             '| --- | --- | ---: | --- | --- |']
    for r in rows:
        lines.append(f"| {r['event_id']} | {r.get('stored_issuer')} | {r.get('stored_cik')} | "
                     f"{r.get('edgar_name', r['lookup_status'])} | {r.get('suspicious')} |")
    lines += ['', 'Correct CIKs in event_review_overrides.json rather than silently rewriting price series.', '']
    (folder/'REPORT.md').write_text('\n'.join(lines))
    return manifest


if __name__ == '__main__':
    print(json.dumps(run(), indent=2))
