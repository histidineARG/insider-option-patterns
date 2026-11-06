"""Same-session non-2.02 8-K hints for price-jump news queue CIKs.

Never auto-keeps from item codes. Item 1.01 -> ma_candidate_hint only.
"""

from __future__ import annotations

import argparse
import json
from collections import defaultdict
from datetime import date
from pathlib import Path

from edgar_earnings_calendar import BASE, fetch_json, pad_cik
from price_jump_examine import load_session_meta, parse_acceptance, reaction_session_with_meta


def extract_all_8k_rows(filings: dict) -> list[dict]:
    rows = []
    forms = filings.get('form') or []
    items_list = filings.get('items') or [''] * len(forms)
    for i, form in enumerate(forms):
        if not str(form).startswith('8-K'):
            continue
        items = items_list[i] or ''
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


def filings_8k_for_cik(cik, pause: float = 0.12) -> list[dict]:
    padded = pad_cik(cik)
    root = fetch_json(f'{BASE}/CIK{padded}.json', pause=pause)
    rows = extract_all_8k_rows(root.get('filings', {}).get('recent', {}))
    for archive in root.get('filings', {}).get('files') or []:
        name = archive.get('name')
        if not name:
            continue
        try:
            archived = fetch_json(f'{BASE}/{name}', pause=pause)
        except Exception:  # noqa: BLE001
            continue
        rows.extend(extract_all_8k_rows(archived))
    by_acc = {r['accession']: r for r in rows}
    out = sorted(by_acc.values(), key=lambda r: r['acceptance_datetime'])
    for r in out:
        r['cik'] = padded
        r['issuer_name'] = root.get('name')
        r['tickers'] = root.get('tickers') or []
        r['source'] = f'{BASE}/CIK{padded}.json'
        r['locator'] = f"8-K items={r['items']}; accession={r['accession']}"
    return out


def normalize_items(items: str) -> set[str]:
    return {p.strip() for p in (items or '').replace(' ', '').split(',') if p.strip()}


def hint_for_items(items: set[str]) -> str | None:
    if '1.01' in items:
        return 'ma_candidate_hint'
    if items & {'7.01', '8.01'}:
        return 'soft_disclosure_hint'
    if '2.02' in items:
        return 'earnings_item_present'
    return 'other_8k_same_session'


def run(root: Path = Path('.'), pause: float = 0.12) -> dict:
    queue_path = root / 'results/price_jump_examine/news_queue_ge50.json'
    queue_payload = json.loads(queue_path.read_text())
    rows = queue_payload.get('first_batch') or queue_payload.get('queue') or []
    session_meta = load_session_meta(root)
    out_dir = root / 'results/price_jump_examine'
    cache_dir = out_dir / 'edgar_8k_by_cik'
    cache_dir.mkdir(parents=True, exist_ok=True)

    ciks = sorted({r['cik'] for r in rows if r.get('cik')})
    by_cik_filings = {}
    errors = []
    for i, cik in enumerate(ciks):
        cache = cache_dir / f'{pad_cik(cik)}.json'
        try:
            if cache.exists():
                filings = json.loads(cache.read_text())
            else:
                filings = filings_8k_for_cik(cik, pause=pause)
                cache.write_text(json.dumps(filings, indent=2) + '\n')
            by_cik_filings[pad_cik(cik)] = filings
        except Exception as exc:  # noqa: BLE001
            errors.append(dict(cik=pad_cik(cik), error=str(exc)))
        if (i + 1) % 10 == 0:
            print(f'8-K assist progress {i+1}/{len(ciks)}', flush=True)

    # reaction session -> filings
    assist = []
    for r in rows:
        cik = pad_cik(r['cik'])
        q = date.fromisoformat(r['qdate'])
        matched = []
        for er in by_cik_filings.get(cik, []):
            try:
                acc = parse_acceptance(er['acceptance_datetime'])
            except ValueError:
                continue
            react = reaction_session_with_meta(acc, session_meta)
            if react != q:
                continue
            items = normalize_items(er.get('items') or '')
            matched.append(dict(
                items=er.get('items'),
                item_set=sorted(items),
                hint=hint_for_items(items),
                accession=er.get('accession'),
                acceptance_datetime=er.get('acceptance_datetime'),
                filing_date=er.get('filing_date'),
                locator=er.get('locator'),
                issuer_name=er.get('issuer_name'),
                tickers=er.get('tickers'),
            ))
        hints = sorted({m['hint'] for m in matched if m.get('hint')})
        assist.append(dict(
            symbol=r['symbol'],
            qdate=r['qdate'],
            cik=cik,
            close_return=r['close_return'],
            prev_close=r['prev_close'],
            same_session_8k=matched,
            hints=hints,
            ma_candidate_hint='ma_candidate_hint' in hints,
        ))

    payload = dict(
        as_of=date.today().isoformat(),
        n_queue_rows=len(rows),
        n_ciks=len(ciks),
        n_with_any_8k=sum(1 for a in assist if a['same_session_8k']),
        n_ma_candidate_hint=sum(1 for a in assist if a['ma_candidate_hint']),
        n_errors=len(errors),
        errors=errors,
        notes=[
            'Hints only; never auto-keep from item codes.',
            'Item 1.01 marks ma_candidate_hint; 7.01/8.01 are soft_disclosure_hint.',
        ],
        rows=assist,
    )
    path = out_dir / 'edgar_assist_ge50.json'
    path.write_text(json.dumps(payload, indent=2) + '\n')
    print(json.dumps(dict(
        n_queue_rows=payload['n_queue_rows'],
        n_ciks=payload['n_ciks'],
        n_with_any_8k=payload['n_with_any_8k'],
        n_ma_candidate_hint=payload['n_ma_candidate_hint'],
        n_errors=payload['n_errors'],
        path=str(path),
    ), indent=2))
    return payload


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--pause', type=float, default=0.12)
    args = p.parse_args(argv)
    run(Path('.'), pause=args.pause)


if __name__ == '__main__':
    main()
