"""Score the frozen logistic. Coefficients are not refit.

2022 through 2024-11-12 and the holdout from 2024-11-13 use the rebuilt
announcement table. Precision is reported at fixed rank cuts. SEC cases,
including the AFOP share purchases, are ranked against the windows in their fold.
"""
from __future__ import annotations

import json
from datetime import date, timedelta
from pathlib import Path

from insider_model import auc, fit_ridge_logistic, predict
from insider_resolved import connect, load_sessions
from ma_candidate_screen import score_event
from ma_news_pool import path_return, quotes_for
from ma_signal_model import (
    FEATURES, HOLDOUT, OPTION_FEATURES, PLACEBO_SHIFT, RIDGE, _paired, design,
    features_for, fold_of, overlaps_earnings,
)
from precision_score import fold_report, true_case_report

MIN_RETURN = 0.15
TARGET_ROLES = {'proxy_target', 'recommendation_target', 'tender_target'}


def feature_bounds(case: dict, sessions: list[date], index: dict) -> tuple[int, int] | None:
    """Inclusive session indexes for the case window. After-close keeps the announcement session."""
    event = date.fromisoformat(case['event_date'])
    if event not in index or index[event] < 10:
        return None
    end = index[event] if case.get('announcement_session') == 'after_close' else index[event] - 1
    if end < 0:
        return None
    trade = date.fromisoformat(case['trade_start'])
    start = index[event] - 10
    if trade in index and index[trade] < start:
        start = index[trade]
    if start > end:
        return None
    return start, end


def _beta(report: dict, names: tuple[str, ...]) -> list[float]:
    coeff = report['coefficients']
    return [coeff['intercept']] + [coeff[name] for name in names]


def _score(features: dict, names: tuple[str, ...], means: list[float], sds: list[float], beta: list[float]) -> float:
    scaled, _, _ = design([features], names, means, sds)
    return predict(beta, scaled[0])


def _earnings_map(connection, symbols: list[str], extra: dict[str, list[date]]) -> dict[str, list[date]]:
    found = {symbol: list(extra.get(symbol, [])) for symbol in symbols}
    with connection.cursor() as cursor:
        for start in range(0, len(symbols), 400):
            chunk = symbols[start:start + 400]
            marks = ','.join(['%s'] * len(chunk))
            cursor.execute(
                f'''SELECT symbol, COALESCE(rxdate, erdate) AS reaction
                    FROM erdate WHERE symbol IN ({marks})''',
                chunk,
            )
            for row in cursor.fetchall():
                if row['reaction']:
                    found.setdefault(row['symbol'].upper(), []).append(row['reaction'])
    for symbol, days in found.items():
        found[symbol] = sorted(set(days))
    return found


def _load_extra_earnings(root: Path) -> dict[str, list[date]]:
    path = root / 'data' / 'edgar_deals' / 'earnings_8k_2022_2026.json'
    if not path.exists():
        return {}
    found = {}
    for row in json.loads(path.read_text()):
        if row.get('symbol') and row.get('reaction_session'):
            found.setdefault(row['symbol'].upper(), []).append(date.fromisoformat(row['reaction_session']))
    return found


def _price_confirm(connection, sessions, index, deals: list[dict]) -> list[dict]:
    by_symbol = {}
    for row in deals:
        if row.get('symbol') and row.get('qdate'):
            by_symbol.setdefault(row['symbol'], []).append(row)
    confirmed = []
    for symbol, items in by_symbol.items():
        start = min(date.fromisoformat(row['qdate']) for row in items) - timedelta(days=30)
        end = max(date.fromisoformat(row['qdate']) for row in items)
        stock = quotes_for(connection, symbol, start, end)
        for row in items:
            day = date.fromisoformat(row['qdate'])
            reaction, path = path_return(stock, sessions, index, day)
            if reaction is None or (path < MIN_RETURN and reaction < MIN_RETURN):
                continue
            confirmed.append(dict(
                symbol=symbol, qdate=day, title=(row.get('issuer_name') or symbol)[:240],
                sources=[f"edgar:{row.get('form_role')}:{row.get('accession')}"],
                reaction=reaction, path=path, form_role=row.get('form_role'),
            ))
    return confirmed


def _merge_earliest(rows: list[dict]) -> list[dict]:
    rows = sorted(rows, key=lambda row: (row['symbol'], row['qdate']))
    kept = []
    for row in rows:
        if kept and kept[-1]['symbol'] == row['symbol'] and (row['qdate'] - kept[-1]['qdate']).days <= 7:
            kept[-1]['sources'] = sorted(set(kept[-1]['sources']) | set(row['sources']))
            continue
        kept.append(dict(row))
    return kept


def _windows_for(connection, sessions, index, symbol, day, window, earnings, form_role='') -> list[dict]:
    rows = []
    deal = features_for(connection, sessions, index, symbol, window, day)
    if deal is None:
        return rows
    fold = fold_of(day)
    base = dict(symbol=symbol, event=day.isoformat(), year=str(day.year), fold=fold, form_role=form_role)
    rows.append(dict(base, role='deal', label=1, **deal))
    prior = [item for item in earnings.get(symbol, []) if item in index and index[item] + len(window) < index[window[0]]]
    if prior:
        earn = max(prior)
        earn_window = sessions[index[earn] - len(window):index[earn]]
        feat = features_for(connection, sessions, index, symbol, earn_window, earn)
        if feat:
            rows.append(dict(base, role='earnings', label=0, **feat))
    anchor = index[day]
    if anchor > PLACEBO_SHIFT + len(window):
        placebo_end = sessions[anchor - PLACEBO_SHIFT]
        ordinary = sessions[index[placebo_end] - len(window):index[placebo_end]]
        feat = features_for(connection, sessions, index, symbol, ordinary, placebo_end)
        if feat:
            rows.append(dict(base, role='ordinary', label=0, **feat))
    return rows


def _attach(samples, names, means, sds, beta, field):
    for row in samples:
        row[field] = _score(row, names, means, sds, beta)


def _check_fit(train, names, stored):
    matrix, means, sds = design(train, names)
    beta = fit_ridge_logistic(matrix, [row['label'] for row in train], ridge=RIDGE)
    gap = max(abs(beta[i] - stored[i]) for i in range(len(stored)))
    return means, sds, gap


def run(root: Path) -> dict:
    table = root / 'data' / 'edgar_deals' / 'announcements.json'
    provenance_path = root / 'data' / 'edgar_deals' / 'provenance.json'
    if not table.exists() or not provenance_path.exists():
        raise SystemExit('EDGAR announcement table is missing')
    provenance = json.loads(provenance_path.read_text())
    deals = json.loads(table.read_text())
    target = [row for row in deals if row.get('form_role') in TARGET_ROLES]
    mapped = [row for row in target if row.get('symbol')]
    rate = (len(mapped) / len(target)) if target else 0
    if target and rate < 0.40:
        report = dict(scored=False, reason='ticker mapping below 40% of target-side filings',
                      target_side=len(target), mapped=len(mapped), rate=rate, provenance=provenance)
        _write(root, report)
        return report
    sessions = load_sessions(root)
    index = {day: i for i, day in enumerate(sessions)}
    frozen = json.loads((root / 'results/insider_footprint/signal_model.json').read_text())
    connection = connect()
    try:
        with connection.cursor() as cursor:
            cursor.execute('SET SESSION MAX_EXECUTION_TIME=300000')
            cursor.execute('START TRANSACTION READ ONLY')
            cursor.execute("SELECT qdate, close FROM stockquote WHERE symbol='SPY' AND qdate>='2012-06-01'")
            spy = {row['qdate']: float(row['close']) for row in cursor.fetchall() if row['close']}
        fresh = _price_confirm(connection, sessions, index, deals)
        old_payload = json.loads((root / 'results/insider_footprint/ma_news_pool.json').read_text())
        old = []
        for row in old_payload['events']:
            day = date.fromisoformat(row['qdate'])
            if day < date(2022, 1, 1):
                continue
            old.append(dict(symbol=row['symbol'], qdate=day, title=row.get('title') or '',
                            sources=list(row.get('sources') or ['prior_pool']),
                            reaction=row['reaction'], path=row['path'], form_role='prior_pool'))
        merged = _merge_earliest(fresh + old)
        strict = [row for row in merged if row['path'] >= MIN_RETURN]
        extra = _load_extra_earnings(root)
        symbols = sorted({row['symbol'] for row in strict})
        earnings = _earnings_map(connection, symbols, extra)
        admitted = []
        for event in strict:
            record = score_event(connection, sessions, index, spy, earnings, dict(
                symbol=event['symbol'], qdate=event['qdate'].isoformat(),
                title=event['title'], path=event['path'], reaction=event['reaction'],
            ))
            record['form_role'] = event.get('form_role')
            record['sources'] = event.get('sources')
            if record.get('admitted'):
                admitted.append(record)
        screen = json.loads((root / 'results/insider_footprint/candidate_screen.json').read_text())
        historical = [row for row in screen['events'] if row.get('admitted') and row['qdate'] < '2022-01-01']
        hist_symbols = sorted({row['symbol'] for row in historical} | {row['symbol'] for row in admitted})
        earnings = _earnings_map(connection, hist_symbols, extra)
        samples = []
        for event in historical:
            day = date.fromisoformat(event['qdate'])
            start = date.fromisoformat(event['t_start'])
            if day not in index or start not in index or index[start] >= index[day]:
                continue
            window = sessions[index[start]:index[day]]
            if overlaps_earnings(window, earnings.get(event['symbol'], [])):
                continue
            samples.extend(_windows_for(connection, sessions, index, event['symbol'], day, window, earnings, 'historical'))
        rebuilt = []
        for event in admitted:
            day = date.fromisoformat(event['qdate'])
            start = date.fromisoformat(event['t_start'])
            window = sessions[index[start]:index[day]]
            if overlaps_earnings(window, earnings.get(event['symbol'], [])):
                continue
            rebuilt.extend(_windows_for(
                connection, sessions, index, event['symbol'], day, window, earnings, event.get('form_role') or ''))
        train = [row for row in samples if row['fold'] == 'train']
        five_means, five_sds, five_gap = _check_fit(train, FEATURES, _beta(frozen, FEATURES))
        option_means, option_sds, option_gap = _check_fit(
            train, OPTION_FEATURES, _beta(frozen['without_pre_return'], OPTION_FEATURES))
        if five_gap > 1e-3 or option_gap > 1e-3:
            report = dict(scored=False, reason='recovered coefficients do not match the frozen fit',
                          five_gap=five_gap, option_gap=option_gap)
            _write(root, report)
            return report
        five_beta = _beta(frozen, FEATURES)
        option_beta = _beta(frozen['without_pre_return'], OPTION_FEATURES)
        scored = [row for row in samples if row['fold'] in ('train', 'val')] + rebuilt
        _attach(scored, FEATURES, five_means, five_sds, five_beta, 'score')
        _attach(scored, OPTION_FEATURES, option_means, option_sds, option_beta, 'option_score')
        cases = _score_cases(connection, sessions, index, earnings, five_means, five_sds, five_beta,
                             option_means, option_sds, option_beta, root)
    finally:
        connection.rollback()
        connection.close()
    report = _assemble(deals, provenance, merged, strict, admitted, scored, cases, five_gap, option_gap)
    _write(root, report)
    return report


def _score_cases(connection, sessions, index, earnings, five_means, five_sds, five_beta,
                 option_means, option_sds, option_beta, root):
    payload = json.loads((root / 'data/sec_cases.json').read_text())
    scored = []
    for case in payload['cases']:
        bounds = feature_bounds(case, sessions, index)
        if bounds is None:
            scored.append(dict(id=case['id'], symbol=case['symbol'], event=case['event_date'],
                               instrument=case.get('instrument'), score=None, option_score=None,
                               reason='no_window'))
            continue
        start, end = bounds
        window = sessions[start:end + 1]
        day = sessions[end]
        feat = features_for(connection, sessions, index, case['symbol'], window, date.fromisoformat(case['event_date']))
        if feat is None:
            scored.append(dict(id=case['id'], symbol=case['symbol'], event=case['event_date'],
                               instrument=case.get('instrument'), score=None, option_score=None,
                               reason='no_monthly'))
            continue
        fold = fold_of(date.fromisoformat(case['event_date']))
        scored.append(dict(
            id=case['id'], symbol=case['symbol'], event=case['event_date'],
            instrument=case.get('instrument'), fold=fold,
            score=_score(feat, FEATURES, five_means, five_sds, five_beta),
            option_score=_score(feat, OPTION_FEATURES, option_means, option_sds, option_beta),
            overlaps_earnings=overlaps_earnings(window, earnings.get(case['symbol'], [])),
        ))
    return scored


def _model_block(rows, score_field, cases):
    labeled = [dict(row, score=row[score_field]) for row in rows]
    folds = {}
    for fold in ('train', 'val', 'later', 'holdout'):
        group = [row for row in labeled if row['fold'] == fold]
        block = fold_report(group) if group else dict(
            n=0, positives=0, base_rate=None, average_precision=None, at_k={}, at_fraction={}, precision_recall=[])
        block['paired'] = _paired_view(group)
        case_group = [dict(case, score=case.get(score_field)) for case in cases
                      if case.get('fold') == fold and case.get(score_field) is not None]
        block['true_cases'] = true_case_report(case_group, group)
        folds[fold] = block
    return folds


def _paired_view(group):
    if not group:
        return dict(earnings=None, ordinary=None, auc=None)
    scores = {id(row): row['score'] for row in group}
    return dict(
        earnings=_paired(group, scores, 'earnings'),
        ordinary=_paired(group, scores, 'ordinary'),
        auc=auc([row['score'] for row in group], [row['label'] for row in group]),
    )


def _assemble(deals, provenance, merged, strict, admitted, scored, cases, five_gap, option_gap):
    roles = {}
    for row in admitted:
        roles[row.get('form_role') or 'unknown'] = roles.get(row.get('form_role') or 'unknown', 0) + 1
    holdout_events = [row for row in admitted if row['qdate'] >= HOLDOUT.isoformat()]
    return dict(
        scored=True,
        coefficient_gap=dict(five=five_gap, option=option_gap),
        edgar_deals=len(deals),
        edgar_with_symbol=sum(1 for row in deals if row.get('symbol')),
        price_confirmed_2022_on=len(merged),
        strict_path=len(strict),
        admitted=len(admitted),
        holdout_events=len(holdout_events),
        admitted_roles=roles,
        provenance_counts=dict(deals=provenance.get('deals'), with_symbol=provenance.get('with_symbol'),
                               earnings_rows=provenance.get('earnings_rows')),
        five_feature=_model_block(scored, 'score', cases),
        option_only=_model_block(scored, 'option_score', cases),
        cases=cases,
        proposal=(
            'No new alert threshold is frozen. The rank cuts 10, 25, 50, 100, 1%, and 5% '
            'are the ones specified for this report. A cutoff chosen from these numbers would '
            'be a proposal for a later frozen test.'
        ),
    )


def _write(root: Path, report: dict) -> None:
    folder = root / 'results' / 'insider_footprint'
    folder.mkdir(parents=True, exist_ok=True)
    stored = json.loads(json.dumps(report))
    for model in ('five_feature', 'option_only'):
        for fold in stored.get(model, {}):
            stored[model][fold].pop('precision_recall', None)
    (folder / 'holdout_score.json').write_text(json.dumps(stored, indent=2) + '\n')
    text = render(report)
    (folder / 'HOLDOUT_SCORE.md').write_text(text)
    _append_dated(folder / 'VALIDATION.md', text)
    _append_dated(folder / 'SIGNAL_MODEL.md', text)
    print(json.dumps({key: report.get(key) for key in ('scored', 'admitted', 'holdout_events', 'reason')}, indent=2), flush=True)


def _append_dated(path: Path, text: str) -> None:
    prior = path.read_text() if path.exists() else ''
    marker = '## Scored holdout, 2026-11-13'
    if marker in prior:
        prior = prior.split(marker)[0].rstrip() + '\n'
    path.write_text(prior.rstrip() + '\n\n' + text)


def _fmt(value):
    return 'n/a' if value is None else f'{value:.3f}'


def _cut_line(block, key, label):
    cut = block.get(key, {}).get(label) or {}
    precision = cut.get('precision')
    return f"{label} {cut.get('hits', 0)}/{cut.get('k', 0)} ({_fmt(precision)})"


def render(report: dict) -> str:
    if not report.get('scored'):
        return '# Scored holdout, 2026-11-13\n\n' + report.get('reason', 'Not scored.') + '\n'
    lines = [
        '## Scored holdout, 2026-11-13',
        '',
        'The five-feature and option-only coefficients are the frozen 2013–2019 fit. This pass checks that a fresh read of those training rows reproduces them, then scores the rebuilt 2022–2026 announcements. Deal-window precision counts a pre-deal window as the positive. That is not an insider hit rate. The resolved cases, including AFOP, are ranked separately. AFOP’s charged trades are common shares.',
        '',
        f"EDGAR deals in the clean table: {report['edgar_deals']}, with a ticker: {report['edgar_with_symbol']}. Price-confirmed rows from 2022 on, after the seven-day merge: {report['price_confirmed_2022_on']}. Strict ten-session path: {report['strict_path']}. Admitted: {report['admitted']}. Holdout events: {report['holdout_events']}.",
        '',
        'Admitted rows by filing role: ' + ', '.join(f"{name} {count}" for name, count in sorted(report['admitted_roles'].items())),
        '',
        report['proposal'],
        '',
    ]
    for title, key in (('Five-feature score', 'five_feature'), ('Option-only score', 'option_only')):
        lines += [f'### {title}', '']
        lines.append('| Fold | Windows | Deal base rate | Average precision | AUC | Above earnings | Above ordinary |')
        lines.append('| --- | ---: | ---: | ---: | ---: | ---: | ---: |')
        for fold, label in (('train', '2013–2019'), ('val', '2020–2021'), ('later', '2022 through 2024-11-12'), ('holdout', '2024-11-13 on')):
            block = report[key][fold]
            paired = block.get('paired') or {}
            earn = (paired.get('earnings') or {}).get('win_rate')
            ordinary = (paired.get('ordinary') or {}).get('win_rate')
            lines.append(
                f"| {label} | {block['positives']} of {block['n']} | {_fmt(block['base_rate'])} | "
                f"{_fmt(block['average_precision'])} | {_fmt((paired or {}).get('auc'))} | {_fmt(earn)} | {_fmt(ordinary)} |"
            )
        lines += ['', 'Deal precision at the fixed rank cuts:', '']
        for fold, label in (('later', '2022 through 2024-11-12'), ('holdout', '2024-11-13 on'), ('val', '2020–2021')):
            block = report[key][fold]
            if not block['n']:
                lines.append(f'- {label}: no scored windows.')
                continue
            cuts = ', '.join(_cut_line(block['at_k'], str(k), str(k)) for k in (10, 25, 50, 100))
            fractions = ', '.join(_cut_line(block['at_fraction'], name, name) for name in ('1%', '5%'))
            lines.append(f'- {label}: {cuts}; {fractions}.')
        lines.append('')
        lines.append('True cases in that fold, ranked on this score:')
        lines.append('')
        for fold, label in (('train', '2013–2019'), ('val', '2020–2021'), ('later', '2022 through 2024-11-12'), ('holdout', '2024-11-13 on')):
            cases = report[key][fold]['true_cases']
            if not cases['n_cases']:
                continue
            lines.append(f'- {label}: {cases["n_cases"]} scored cases.')
            for case in cases['cases']:
                if case.get('rank') is None:
                    lines.append(f"  - {case['id']} {case.get('symbol')} unscored ({case.get('reason')}).")
                    continue
                lines.append(
                    f"  - {case['id']} {case['symbol']} {case.get('instrument')} rank {case['rank']} of {case['universe']}."
                )
            for k, cut in cases['at_k'].items():
                per = _fmt(cut['false_alerts_per_true_case'])
                lines.append(f"  - top {k}: {cut['cases']} cases inside, {cut['false_alerts']} other windows, {per} other windows per scored case.")
        lines.append('')
    lines.append('A rank is a review tag. It is not an identification of a trader.')
    lines.append('')
    return '\n'.join(lines)


def main():
    run(Path('.'))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
