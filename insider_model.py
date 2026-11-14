"""Chronological logistic on the pre-jump call footprint.

Features and the ridge penalty are fixed. Training uses 2013–2014 only.
2015 is reported and does not change the fit. 2016 is the holdout.

A class-2 jump is an event label, not an insider-trading label. Many of those
jumps have no informed option trade. The fit therefore asks only whether a
footprint is common across the set. A pattern that belongs to a minority
would appear in the upper tail of the paired score gap, not as a high AUC.
"""
import math
import statistics

FEATURE_NAMES = (
    'log_volume_ratio',
    'band_share',
    'top_share',
    'call_fraction',
    'log_band_turnover',
)
RIDGE = 1.0
TRAIN_YEARS = (2013, 2014)
VAL_YEARS = (2015,)
TEST_YEARS = (2016,)
MIN_OBSERVED_WINDOW = 8
MIN_BASELINE = 10


def window_features(window, baseline) -> dict | None:
    """Features from the window session with the largest call-volume ratio."""
    if len(window) < MIN_OBSERVED_WINDOW or len(baseline) < MIN_BASELINE:
        return None
    mean = statistics.fmean(day['call_vol'] for day in baseline)
    chosen = None
    chosen_ratio = None
    for day in window:
        volume = day['call_vol']
        ratio = volume / mean if mean else float(volume)
        if chosen is None or ratio > chosen_ratio or (ratio == chosen_ratio and volume > chosen['call_vol']):
            chosen = day
            chosen_ratio = ratio
    volume = chosen['call_vol']
    puts = int(chosen.get('put_vol') or 0)
    band = chosen['band_vol']
    open_interest = int(chosen.get('band_oi') or 0)
    share = (band / volume) if volume else 0.0
    top = chosen.get('top_share')
    return dict(
        session=chosen['qdate'].isoformat() if hasattr(chosen['qdate'], 'isoformat') else str(chosen['qdate']),
        log_volume_ratio=math.log1p(chosen_ratio),
        band_share=share,
        top_share=0.0 if top is None else float(top),
        call_fraction=(volume / (volume + puts)) if (volume + puts) else 0.5,
        log_band_turnover=math.log1p(band / (open_interest + 1)),
    )


def _matrix(samples, names, means=None, sds=None):
    raw = [[sample['features'][name] for name in names] for sample in samples]
    if means is None:
        means = []
        sds = []
        for col in range(len(names)):
            values = [row[col] for row in raw]
            means.append(statistics.fmean(values))
            spread = statistics.pstdev(values)
            sds.append(spread if spread else 1.0)
    scaled = []
    for row in raw:
        scaled.append([1.0] + [(row[i] - means[i]) / sds[i] for i in range(len(names))])
    return scaled, means, sds


def solve(matrix, rhs):
    size = len(rhs)
    rows = [matrix[i][:] + [rhs[i]] for i in range(size)]
    for col in range(size):
        pivot = max(range(col, size), key=lambda r: abs(rows[r][col]))
        if abs(rows[pivot][col]) < 1e-12:
            raise ZeroDivisionError('singular logistic system')
        rows[col], rows[pivot] = rows[pivot], rows[col]
        scale = rows[col][col]
        for j in range(col, size + 1):
            rows[col][j] /= scale
        for row in range(size):
            if row == col:
                continue
            factor = rows[row][col]
            for j in range(col, size + 1):
                rows[row][j] -= factor * rows[col][j]
    return [rows[i][size] for i in range(size)]


def fit_ridge_logistic(design, labels, ridge=RIDGE, iterations=40):
    width = len(design[0])
    beta = [0.0] * width
    for _ in range(iterations):
        fitted = [_sigmoid(sum(design[i][j] * beta[j] for j in range(width))) for i in range(len(design))]
        gram = [[0.0] * width for _ in range(width)]
        rhs = [0.0] * width
        for i, row in enumerate(design):
            weight = max(fitted[i] * (1.0 - fitted[i]), 1e-6)
            working = sum(row[j] * beta[j] for j in range(width)) + (labels[i] - fitted[i]) / weight
            for a in range(width):
                rhs[a] += row[a] * weight * working
                for b in range(width):
                    gram[a][b] += row[a] * weight * row[b]
        for j in range(1, width):
            gram[j][j] += ridge
        beta = solve(gram, rhs)
    return beta


def _sigmoid(value):
    value = max(-20.0, min(20.0, value))
    return 1.0 / (1.0 + math.exp(-value))


def predict(beta, row):
    return _sigmoid(sum(weight * value for weight, value in zip(beta, row)))


def auc(scores, labels):
    positives = [score for score, label in zip(scores, labels) if label == 1]
    negatives = [score for score, label in zip(scores, labels) if label == 0]
    if not positives or not negatives:
        return None
    wins = ties = 0
    for positive in positives:
        for negative in negatives:
            if positive > negative:
                wins += 1
            elif positive == negative:
                ties += 1
    return (wins + 0.5 * ties) / (len(positives) * len(negatives))


def paired(samples, scores_by_id, role):
    wins = losses = ties = 0
    for sample in samples:
        if sample['role'] != 'case':
            continue
        control = scores_by_id.get((sample['symbol'], sample['event'], role))
        case = scores_by_id.get((sample['symbol'], sample['event'], 'case'))
        if control is None or case is None:
            continue
        if case > control:
            wins += 1
        elif case < control:
            losses += 1
        else:
            ties += 1
    total = wins + losses + ties
    return dict(n=total, wins=wins, losses=losses, ties=ties,
                win_rate=(wins / total) if total else None)


def score_gaps(samples, scores_by_id, role) -> list[float]:
    gaps = []
    for sample in samples:
        if sample['role'] != 'case':
            continue
        case = scores_by_id.get((sample['symbol'], sample['event'], 'case'))
        control = scores_by_id.get((sample['symbol'], sample['event'], role))
        if case is None or control is None:
            continue
        gaps.append(case - control)
    return gaps


def gap_quantiles(values) -> dict | None:
    if not values:
        return None
    ordered = sorted(values)

    def at(fraction):
        position = (len(ordered) - 1) * fraction
        low = int(position)
        high = min(low + 1, len(ordered) - 1)
        return ordered[low] + (ordered[high] - ordered[low]) * (position - low)

    return dict(n=len(values), p10=at(0.10), p50=at(0.50), p90=at(0.90))


def _fold_report(samples, scores_by_id):
    scores = [scores_by_id[(s['symbol'], s['event'], s['role'])] for s in samples]
    labels = [s['label'] for s in samples]
    return dict(
        n=len(samples),
        positives=sum(labels),
        negatives=len(labels) - sum(labels),
        auc=auc(scores, labels),
        paired_placebo=paired(samples, scores_by_id, 'placebo'),
        paired_earnings=paired(samples, scores_by_id, 'earnings'),
        gap_versus_placebo=gap_quantiles(score_gaps(samples, scores_by_id, 'placebo')),
        gap_versus_earnings=gap_quantiles(score_gaps(samples, scores_by_id, 'earnings')),
    )


def evaluate_model(samples, names=FEATURE_NAMES, ridge=RIDGE):
    """Fit on 2013–2014 and score every year with that one model."""
    train = [s for s in samples if s['year'] in TRAIN_YEARS and s['role'] in ('case', 'placebo', 'earnings')]
    if len(train) < len(names) + 2 or len({s['label'] for s in train}) < 2:
        return dict(fit=False, reason='training fold lacks both classes')
    design, means, sds = _matrix(train, names)
    beta = fit_ridge_logistic(design, [s['label'] for s in train], ridge=ridge)
    scores_by_id = {}
    for sample in samples:
        if sample['role'] not in ('case', 'placebo', 'earnings'):
            continue
        row, _, _ = _matrix([sample], names, means, sds)
        scores_by_id[(sample['symbol'], sample['event'], sample['role'])] = predict(beta, row[0])
    volume_only = None
    if 'log_volume_ratio' in names:
        volume_design, volume_means, volume_sds = _matrix(train, ('log_volume_ratio',))
        volume_beta = fit_ridge_logistic(volume_design, [s['label'] for s in train], ridge=ridge)
        holdout = [s for s in samples if s['year'] in TEST_YEARS and s['role'] in ('case', 'placebo', 'earnings')]
        holdout_scores = []
        holdout_labels = []
        for sample in holdout:
            row, _, _ = _matrix([sample], ('log_volume_ratio',), volume_means, volume_sds)
            holdout_scores.append(predict(volume_beta, row[0]))
            holdout_labels.append(sample['label'])
        volume_only = auc(holdout_scores, holdout_labels)
    folds = {}
    for name, years in (('train', TRAIN_YEARS), ('validation_2015', VAL_YEARS), ('holdout_2016', TEST_YEARS)):
        fold = [s for s in samples if s['year'] in years and s['role'] in ('case', 'placebo', 'earnings')]
        folds[name] = _fold_report(fold, scores_by_id)
    coefficients = {'intercept': beta[0]}
    coefficients.update({names[i]: beta[i + 1] for i in range(len(names))})
    return dict(
        fit=True,
        ridge=ridge,
        features=list(names),
        train_years=list(TRAIN_YEARS),
        n_train=len(train),
        coefficients=coefficients,
        standardization=dict(mean=dict(zip(names, means)), sd=dict(zip(names, sds))),
        folds=folds,
        volume_only_holdout_auc=volume_only,
    )


def samples_from_records(records) -> list[dict]:
    samples = []
    for record in records:
        if record.get('tier') != 'A':
            continue
        year = int(record['qdate'][:4])
        event = record['qdate']
        specs = (
            ('case', record, 1),
            ('placebo', record.get('placebo') or {}, 0),
            ('earnings', record.get('earnings') or {}, 0),
        )
        for role, source, label in specs:
            features = source.get('features') if isinstance(source, dict) else None
            if not features:
                continue
            samples.append(dict(symbol=record['symbol'], event=event, role=role, year=year,
                                label=label, features=features))
    return samples


def render_model_report(result) -> str:
    if not result.get('fit'):
        return '# Footprint logistic\n\n' + result.get('reason', 'The model did not fit.') + '\n'
    holdout = result['folds']['holdout_2016']
    validation = result['folds']['validation_2015']
    train = result['folds']['train']
    lines = [
        '# Footprint logistic',
        '',
        'One ridge logistic. Features are taken from the single pre-event session with the largest call-volume ratio: log volume ratio, share of call volume in the delta 0.10–0.35 band, that band\'s top strike share, call share of call-plus-put volume, and log band volume per contract of open interest. Ridge penalty is 1 on the standardized features. Fit uses 2013–2014. The 2015 numbers were not used to change anything. 2016 is the holdout.',
        '',
        'The label is a class-2 window versus that name\'s own placebo and earnings windows. Many of those jumps have no informed option trade, so the positive class is a mixture. A higher score means the session looks more like the pre-jump windows in the training years. It is not a probability that a person traded on inside information. AUC near one half means the footprint is not common to the set. A minority pattern would show as a positive upper tail in the score gap, with the median gap still near zero.',
        '',
        '| Fold | Windows | AUC | M&A scores above its placebo | M&A scores above its earnings |',
        '| --- | ---: | ---: | ---: | ---: |',
    ]
    for label, fold in (('2013–2014 train', train), ('2015 validation', validation), ('2016 holdout', holdout)):
        lines.append(
            f"| {label} | {fold['positives']} cases, {fold['negatives']} controls | "
            f"{_fmt(fold['auc'])} | {_pair(fold['paired_placebo'])} | {_pair(fold['paired_earnings'])} |"
        )
    lines += [
        '',
        f"A model that uses only the volume ratio has 2016 AUC {_fmt(result['volume_only_holdout_auc'])}.",
        '',
        'Paired score gap on the holdout, case minus control. The median is the typical event. The 90th percentile is the upper tail, where a minority of informed trades would have to sit:',
        '',
        f"| Versus | 10th | Median | 90th |",
        '| --- | ---: | ---: | ---: |',
        f"| Placebo | {_gap(holdout.get('gap_versus_placebo'), 'p10')} | {_gap(holdout.get('gap_versus_placebo'), 'p50')} | {_gap(holdout.get('gap_versus_placebo'), 'p90')} |",
        f"| Earnings | {_gap(holdout.get('gap_versus_earnings'), 'p10')} | {_gap(holdout.get('gap_versus_earnings'), 'p50')} | {_gap(holdout.get('gap_versus_earnings'), 'p90')} |",
        '',
        'Standardized coefficients, intercept unpenalized:',
        '',
    ]
    for name, weight in result['coefficients'].items():
        lines.append(f'- {name}: {weight:.3f}')
    lines += [
        '',
        'Thresholds and the penalty were not revised after these numbers. No trading result is claimed.',
        '',
    ]
    return '\n'.join(lines)


def _fmt(value):
    return 'n/a' if value is None else f'{value:.3f}'


def _gap(summary, key):
    if not summary:
        return 'n/a'
    return _fmt(summary.get(key))


def _pair(pair):
    if not pair['n']:
        return 'n/a'
    rate = 'n/a' if pair['win_rate'] is None else f"{pair['win_rate']:.0%}"
    return f"{pair['wins']}/{pair['n']} ({rate})"
