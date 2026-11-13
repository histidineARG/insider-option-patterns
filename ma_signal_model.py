"""Logistic model for the pre-announcement window.

Positives are the sessions before a deal whose ten-session path is at least 15%.
Negatives are the same stock's earnings window and a same-length window 60
sessions earlier. Features stop the session before the headline. Fit uses years
through 2019, 2020–2021 is the check, and 2024-11-13 onward is not used.
"""
import json
import math
from datetime import date, timedelta
from pathlib import Path

from insider_model import auc, fit_ridge_logistic, predict
from ma_candidate_screen import covering, fetch_chain, series_metrics
from insider_resolved import connect, load_sessions

FEATURES = ('log_peak_call', 'log_oi_build', 'otm_share', 'log_call_put', 'pre_return')
OPTION_FEATURES = tuple(name for name in FEATURES if name != 'pre_return')
TRAIN_END = 2019
VAL_YEARS = {2020, 2021}
HOLDOUT = date(2024, 11, 13)
PLACEBO_SHIFT = 60
RIDGE = 1.0


def fold_of(qdate: date) -> str:
    if qdate >= HOLDOUT:
        return 'holdout'
    if qdate.year <= TRAIN_END:
        return 'train'
    if qdate.year in VAL_YEARS:
        return 'val'
    return 'later'


def window_features(rows, edate, days, closes):
    metric = series_metrics(rows, edate, days) if edate else None
    if metric is None:
        return None
    calls = puts = 0
    for day in days:
        rec = rows.get(day, {}).get(edate)
        if not rec:
            continue
        calls += rec['call_vol']
        puts += rec['put_vol']
    start = closes.get(days[0])
    end = closes.get(days[-1])
    pre = 0.0 if not start or not end else end / start - 1
    return dict(
        log_peak_call=math.log1p(metric['peak_call']),
        log_oi_build=math.log1p(metric['max_oi_build']),
        otm_share=0.0 if metric['otm_share'] is None else metric['otm_share'],
        log_call_put=math.log1p(calls / (puts + 1)),
        pre_return=pre,
    )


def overlaps_earnings(days, earnings):
    dayset = set(days)
    return any(day in dayset for day in earnings)


def design(samples, features=FEATURES, means=None, sds=None):
    raw = [[sample[name] for name in features] for sample in samples]
    if means is None:
        means, sds = [], []
        for col in range(len(features)):
            values = [row[col] for row in raw]
            center = sum(values) / len(values)
            spread = math.sqrt(sum((value - center) ** 2 for value in values) / len(values))
            means.append(center)
            sds.append(spread or 1.0)
    scaled = [[1.0] + [(row[i] - means[i]) / sds[i] for i in range(len(features))] for row in raw]
    return scaled, means, sds


def evaluate(samples, features=FEATURES):
    train = [row for row in samples if row['fold'] == 'train']
    if len({row['label'] for row in train}) < 2:
        return dict(fit=False, reason='training fold lacks both classes', features=list(features))
    matrix, means, sds = design(train, features)
    beta = fit_ridge_logistic(matrix, [row['label'] for row in train], ridge=RIDGE)
    scores = {}
    for row in samples:
        scaled, _, _ = design([row], features, means, sds)
        scores[id(row)] = predict(beta, scaled[0])
    report = dict(fit=True, n_train=len(train), features=list(features), coefficients={'intercept': beta[0]})
    report['coefficients'].update({name: beta[i + 1] for i, name in enumerate(features)})
    for fold in ('train', 'val', 'later'):
        group = [row for row in samples if row['fold'] == fold]
        report[fold] = dict(
            n=len(group),
            positives=sum(row['label'] for row in group),
            auc=auc([scores[id(row)] for row in group], [row['label'] for row in group]),
            paired_earnings=_paired(group, scores, 'earnings'),
            paired_ordinary=_paired(group, scores, 'ordinary'),
        )
    report['holdout_positives'] = sum(row['fold'] == 'holdout' for row in samples)
    return report


def train_means(samples):
    means = {}
    for role in ('deal', 'earnings', 'ordinary'):
        rows = [row for row in samples if row['fold'] == 'train' and row['role'] == role]
        if not rows:
            continue
        means[role] = {name: sum(row[name] for row in rows) / len(rows) for name in FEATURES}
        means[role]['n'] = len(rows)
    return means


def _paired(group, scores, role):
    deals = {(row['symbol'], row['event']): scores[id(row)] for row in group if row['role'] == 'deal'}
    wins = losses = 0
    for row in group:
        if row['role'] != role:
            continue
        deal = deals.get((row['symbol'], row['event']))
        if deal is None:
            continue
        if deal > scores[id(row)]:
            wins += 1
        elif deal < scores[id(row)]:
            losses += 1
    total = wins + losses
    return dict(wins=wins, losses=losses, n=total, win_rate=(wins / total) if total else None)


def _closes(connection, symbol, start, end):
    with connection.cursor() as cursor:
        cursor.execute(
            'SELECT qdate, close FROM stockquote WHERE symbol=%s AND qdate BETWEEN %s AND %s',
            (symbol, start, end),
        )
        return {row['qdate']: float(row['close']) for row in cursor.fetchall() if row['close']}


def features_for(connection, sessions, index, symbol, days, cover_event):
    if len(days) < 5 or days[0] not in index:
        return None
    rows = fetch_chain(connection, symbol, days[0], days[-1])
    expiries = {edate for day_rows in rows.values() for edate in day_rows}
    cover = covering(expiries, cover_event, 'monthly')
    closes = _closes(connection, symbol, days[0], days[-1])
    return window_features(rows, cover, days, closes)


def run(root: Path) -> dict:
    sessions = load_sessions(root)
    index = {day: i for i, day in enumerate(sessions)}
    payload = json.loads((root / 'results/insider_footprint/candidate_screen.json').read_text())
    events = [row for row in payload['events'] if row.get('admitted') and row.get('t_start')]
    symbols = sorted({row['symbol'] for row in events})
    connection = connect()
    earnings = {symbol: [] for symbol in symbols}
    samples = []
    try:
        with connection.cursor() as cursor:
            cursor.execute('SET SESSION MAX_EXECUTION_TIME=300000')
            cursor.execute('START TRANSACTION READ ONLY')
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
                        earnings.setdefault(row['symbol'].upper(), []).append(row['reaction'])
        for n, event in enumerate(events, start=1):
            day = date.fromisoformat(event['qdate'])
            start = date.fromisoformat(event['t_start'])
            if day not in index or start not in index or index[start] >= index[day]:
                continue
            window = sessions[index[start]:index[day]]
            if overlaps_earnings(window, earnings.get(event['symbol'], [])):
                continue
            deal = features_for(connection, sessions, index, event['symbol'], window, day)
            if deal is None:
                continue
            samples.append(dict(symbol=event['symbol'], event=event['qdate'], role='deal',
                                label=1, fold=fold_of(day), **deal))
            prior = [item for item in earnings.get(event['symbol'], [])
                     if item in index and index[item] + len(window) < index[start]]
            if prior:
                earn = max(prior)
                earn_window = sessions[index[earn] - len(window):index[earn]]
                feat = features_for(connection, sessions, index, event['symbol'], earn_window, earn)
                if feat:
                    samples.append(dict(symbol=event['symbol'], event=event['qdate'], role='earnings',
                                        label=0, fold=fold_of(day), **feat))
            if index[day] > PLACEBO_SHIFT + len(window):
                placebo_end = sessions[index[day] - PLACEBO_SHIFT]
                ordinary = sessions[index[placebo_end] - len(window):index[placebo_end]]
                feat = features_for(connection, sessions, index, event['symbol'], ordinary, placebo_end)
                if feat:
                    samples.append(dict(symbol=event['symbol'], event=event['qdate'], role='ordinary',
                                        label=0, fold=fold_of(day), **feat))
            if n % 100 == 0:
                print(f'windows {n} samples {len(samples)}', flush=True)
    finally:
        connection.rollback()
        connection.close()
    kept = [row for row in samples if row['fold'] != 'holdout']
    report = evaluate(kept)
    report['train_means'] = train_means(kept)
    report['without_pre_return'] = evaluate(kept, features=OPTION_FEATURES)
    report['holdout_rows'] = sum(row['fold'] == 'holdout' for row in samples)
    folder = root / 'results' / 'insider_footprint'
    (folder / 'signal_model.json').write_text(json.dumps(report, indent=2) + '\n')
    (folder / 'SIGNAL_MODEL.md').write_text(render(report))
    print(json.dumps(report, indent=2), flush=True)
    return report


def _fmt(value):
    return 'n/a' if value is None else f'{value:.3f}'


def _pair(pair):
    if not pair or not pair['n']:
        return 'n/a'
    return f"{pair['wins']}/{pair['n']} ({pair['win_rate']:.0%})"


def render(report) -> str:
    if not report.get('fit'):
        return '# Signal model\n\n' + report.get('reason', 'The model did not fit.') + '\n'
    lines = [
        '# Pre-news signal model',
        '',
        'The five-feature logistic separates deal windows from the same stock’s earnings and ordinary windows because of the stock’s own return across the window. Deal windows in the training years are up about 17% from the first session of the window to the session before the headline. Earnings windows and ordinary windows are about flat. That return belongs in the model because the question includes the price path. It is also close to the rule that admitted the window: the ten-session path through the announcement had to be at least 15%. The announcement session itself stays out of every feature.',
        '',
        'The four option features on the covering monthly expiry — peak call volume, open-interest build, out-of-the-money share, and call/put volume — are a weak separator once that return is set aside. On 2020–2021 the deal window scores above its earnings window 64% of the time. On 2022 through 2024-11-12 the share is 51%. The five-feature coefficients stay as fit. This second table is a reading of the same rows.',
        '',
        'A positive is the window before a deal whose ten-session path is at least 15%. Negatives are that stock’s earnings window and a same-length window 60 sessions earlier. Volume and open interest stay on one expiry. Fit uses 2013–2019. 2020–2021 is the check. The holdout, 2024-11-13 onward, stays out of the fit.',
        '',
        '| Fold | Rows | AUC | Deal scores above its earnings | Deal scores above its ordinary window |',
        '| --- | ---: | ---: | ---: | ---: |',
    ]
    for label, key in (('2013–2019 train', 'train'), ('2020–2021 check', 'val'), ('2022 through 2024-11-12', 'later')):
        fold = report[key]
        lines.append(
            f"| {label} | {fold['positives']} deals in {fold['n']} | {_fmt(fold['auc'])} | "
            f"{_pair(fold['paired_earnings'])} | {_pair(fold['paired_ordinary'])} |"
        )
    lines += ['', 'Standardized coefficients, fit on 2013–2019:', '']
    for name, weight in report['coefficients'].items():
        lines.append(f'- {name}: {weight:.3f}')
    means = report.get('train_means') or {}
    if means:
        lines += ['', 'Mean feature value on the 2013–2019 rows:', '',
                  '| Window | Rows | Stock return across the window | Log peak call volume | Log OI build |',
                  '| --- | ---: | ---: | ---: | ---: |']
        for role, label in (('deal', 'Deal'), ('earnings', 'Earnings'), ('ordinary', 'Ordinary')):
            row = means.get(role)
            if not row:
                continue
            lines.append(
                f"| {label} | {row['n']} | {row['pre_return']:.3f} | {row['log_peak_call']:.3f} | {row['log_oi_build']:.3f} |"
            )
    dropped = report.get('without_pre_return')
    if dropped and dropped.get('fit'):
        lines += [
            '',
            'The same split and the same ridge, with the stock return removed, leaves the four option features. That check is a reading of the fit above. It is not a second model and it was not used to change the five-feature coefficients.',
            '',
            '| Fold | AUC | Deal scores above its earnings | Deal scores above its ordinary window |',
            '| --- | ---: | ---: | ---: |',
        ]
        for label, key in (('2013–2019 train', 'train'), ('2020–2021 check', 'val'), ('2022 through 2024-11-12', 'later')):
            fold = dropped[key]
            lines.append(
                f"| {label} | {_fmt(fold['auc'])} | {_pair(fold['paired_earnings'])} | {_pair(fold['paired_ordinary'])} |"
            )
        lines += ['', 'Option-only coefficients:', '']
        for name, weight in dropped['coefficients'].items():
            lines.append(f'- {name}: {weight:.3f}')
    lines += [
        '',
        f"Holdout rows from 2024-11-13 onward: {report['holdout_rows']}. That window was not used.",
        '',
        'The earnings calendar ends on 2022-01-04, so the 2022–2024 earnings pairs are only the deals that still have an earlier earnings date on file.',
        '',
        'A higher score means the window looks more like the pre-deal windows in the training years than like that stock’s earnings or ordinary windows. It is not an identification of a trader.',
        '',
    ]
    return '\n'.join(lines)


def main():
    run(Path('.'))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
