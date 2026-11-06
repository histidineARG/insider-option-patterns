"""Build an earnings-report calendar from EDGAR 8-K Item 2.02 filings.

Keep/drop policy for ≥15% jumps uses this calendar to drop class 1 (earnings).
Classes 2–4 (M&A / biotech trial / tech breakthrough) remain keep-when-found.

Source: data.sec.gov submissions JSON (recent + archived files). An 8-K is treated
as an earnings disclosure when form is 8-K/8-K/A and items contain 2.02.
"""

from __future__ import annotations

import argparse
import json
import time
import urllib.error
import urllib.request
from pathlib import Path


UA = 'insider-option-patterns research bill@localhost'
BASE = 'https://data.sec.gov/submissions'


def fetch_json(url: str, pause: float = 0.12) -> dict:
    req = urllib.request.Request(url, headers={'User-Agent': UA})
    with urllib.request.urlopen(req, timeout=60) as resp:
        payload = json.load(resp)
    time.sleep(pause)
    return payload


def pad_cik(cik) -> str:
    return str(int(cik)).zfill(10)


def extract_item_202_rows(filings: dict) -> list[dict]:
    rows = []
    forms = filings.get('form') or []
    items_list = filings.get('items') or [''] * len(forms)
    for i, form in enumerate(forms):
        items = items_list[i] or ''
        if not str(form).startswith('8-K'):
            continue
        if '2.02' not in items.replace(' ', ''):
            continue
        rows.append(dict(
            form=form,
            items=items,
            filing_date=filings['filingDate'][i],
            acceptance_datetime=filings['acceptanceDateTime'][i],
            report_date=(filings.get('reportDate') or [None] * len(forms))[i] or None,
            accession=filings['accessionNumber'][i],
            primary_document=(filings.get('primaryDocument') or [None] * len(forms))[i],
        ))
    return rows


def filings_for_cik(cik, pause: float = 0.12) -> list[dict]:
    padded = pad_cik(cik)
    root = fetch_json(f'{BASE}/CIK{padded}.json', pause=pause)
    rows = extract_item_202_rows(root.get('filings', {}).get('recent', {}))
    for archive in root.get('filings', {}).get('files') or []:
        name = archive.get('name')
        if not name:
            continue
        try:
            archived = fetch_json(f'{BASE}/{name}', pause=pause)
        except urllib.error.HTTPError:
            continue
        rows.extend(extract_item_202_rows(archived))
    # de-dupe by accession
    by_acc = {r['accession']: r for r in rows}
    out = sorted(by_acc.values(), key=lambda r: r['acceptance_datetime'])
    for r in out:
        r['cik'] = padded
        r['issuer_name'] = root.get('name')
        r['tickers'] = root.get('tickers') or []
        r['exchanges'] = root.get('exchanges') or []
        r['source'] = f'{BASE}/CIK{padded}.json'
        r['locator'] = f"8-K items={r['items']}; accession={r['accession']}"
    return out


def load_ciks(path: Path) -> list[int]:
    raw = json.loads(path.read_text())
    if isinstance(raw, dict) and 'ciks' in raw:
        return [int(x) for x in raw['ciks']]
    if isinstance(raw, list):
        return [int(x) for x in raw]
    raise ValueError(f'unsupported CIK list format: {path}')


def run(ciks: list[int], root: Path = Path('.'), pause: float = 0.12) -> dict:
    out_dir = root / 'results' / 'edgar_earnings_calendar'
    out_dir.mkdir(parents=True, exist_ok=True)
    cache_dir = out_dir / 'by_cik'
    cache_dir.mkdir(parents=True, exist_ok=True)

    all_rows = []
    errors = []
    for i, cik in enumerate(sorted(set(int(c) for c in ciks))):
        cache = cache_dir / f'{pad_cik(cik)}.json'
        try:
            if cache.exists():
                rows = json.loads(cache.read_text())
            else:
                rows = filings_for_cik(cik, pause=pause)
                cache.write_text(json.dumps(rows, indent=2) + '\n')
            all_rows.extend(rows)
        except Exception as exc:  # noqa: BLE001 - persist and continue census
            errors.append(dict(cik=pad_cik(cik), error=str(exc)))
        if (i + 1) % 25 == 0:
            print(f'earnings calendar progress {i+1}/{len(ciks)}', flush=True)

    all_rows.sort(key=lambda r: (r['cik'], r['acceptance_datetime']))
    payload = dict(
        as_of='2026-11-06',
        definition=(
            'EDGAR 8-K/8-K/A filings whose items include 2.02 (Results of Operations '
            'and Financial Condition). Used as the earnings-report calendar for dropping '
            'class-1 ≥15% jumps. Keep classes remain 2 M&A, 3 biotech trial, 4 tech breakthrough.'
        ),
        n_ciks_requested=len(set(int(c) for c in ciks)),
        n_ciks_ok=len({r['cik'] for r in all_rows}),
        n_filings=len(all_rows),
        n_errors=len(errors),
        errors=errors[:100],
        filings=all_rows,
    )
    (out_dir / 'earnings_8k_202.json').write_text(json.dumps(payload, indent=2) + '\n')
    # flat csv
    import csv
    fields = ['cik', 'issuer_name', 'filing_date', 'acceptance_datetime', 'report_date',
              'form', 'items', 'accession', 'locator', 'source']
    with (out_dir / 'earnings_8k_202.csv').open('w', newline='') as fh:
        w = csv.DictWriter(fh, fieldnames=fields, extrasaction='ignore')
        w.writeheader()
        for r in all_rows:
            w.writerow(r)
    manifest = dict(
        n_ciks_requested=payload['n_ciks_requested'],
        n_ciks_ok=payload['n_ciks_ok'],
        n_filings=payload['n_filings'],
        n_errors=payload['n_errors'],
        notes=[
            'Item 2.02 is the EDGAR earnings-results disclosure used for class-1 drops.',
            'Acceptance datetime is the public EDGAR stamp; map to NYSE reaction session separately.',
            'Cached per-CIK under results/edgar_earnings_calendar/by_cik/.',
        ],
    )
    (out_dir / 'manifest.json').write_text(json.dumps(manifest, indent=2) + '\n')
    lines = [
        '# EDGAR earnings calendar (8-K Item 2.02)',
        '',
        payload['definition'],
        '',
        f"CIKs requested **{payload['n_ciks_requested']}**, with filings **{payload['n_ciks_ok']}**, "
        f"Item 2.02 rows **{payload['n_filings']}**, fetch errors **{payload['n_errors']}**.",
        '',
        'Used to drop earnings-driven ≥15% jumps (news-filter class 1).',
        '',
    ]
    (out_dir / 'REPORT.md').write_text('\n'.join(lines))
    return manifest


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--ciks', type=Path, help='JSON list of CIKs or {"ciks": [...]}')
    p.add_argument('--cik', action='append', type=int, default=[], help='CIK to include')
    p.add_argument('--pause', type=float, default=0.12)
    args = p.parse_args(argv)
    ciks = list(args.cik)
    if args.ciks:
        ciks.extend(load_ciks(args.ciks))
    if not ciks:
        raise SystemExit('provide --cik and/or --ciks')
    manifest = run(ciks, pause=args.pause)
    print(json.dumps(manifest, indent=2))


if __name__ == '__main__':
    main()
