"""Rank cuts for a frozen score. Precision here is deal-window precision unless a row is marked as a true case.

Top-k and top-percent cuts are the ones named for this report. They are not a
threshold chosen after seeing a fold.
"""
from __future__ import annotations

import math

KS = (10, 25, 50, 100)
FRACTIONS = (0.01, 0.05)


def _ordered(rows: list[dict]) -> list[dict]:
    return sorted(rows, key=lambda row: (-float(row['score']), row.get('symbol') or '', row.get('event') or ''))


def average_precision(rows: list[dict], label_key: str = 'label') -> float | None:
    ordered = _ordered(rows)
    positives = [row for row in ordered if row.get(label_key)]
    if not positives or not ordered:
        return None
    hit = 0
    total = 0.0
    for rank, row in enumerate(ordered, start=1):
        if row.get(label_key):
            hit += 1
            total += hit / rank
    return total / len(positives)


def precision_recall(rows: list[dict], label_key: str = 'label') -> list[dict]:
    ordered = _ordered(rows)
    positives = sum(1 for row in ordered if row.get(label_key))
    if not positives:
        return []
    hit = 0
    curve = []
    for rank, row in enumerate(ordered, start=1):
        if not row.get(label_key):
            continue
        hit += 1
        curve.append(dict(rank=rank, precision=hit / rank, recall=hit / positives))
    return curve


def _cut(ordered: list[dict], k: int, label_key: str) -> dict:
    k = min(k, len(ordered))
    chosen = ordered[:k]
    hits = sum(1 for row in chosen if row.get(label_key))
    return dict(k=k, hits=hits, precision=(hits / k) if k else None)


def alerts_by_year(rows: list[dict], k: int, label_key: str = 'label') -> list[dict]:
    ordered = _ordered(rows)
    chosen = ordered[:min(k, len(ordered))]
    years = {}
    for row in chosen:
        bucket = years.setdefault(str(row.get('year')), dict(alerts=0, deal=0, earnings=0, ordinary=0, other=0))
        bucket['alerts'] += 1
        role = row.get('role')
        if role in ('deal', 'earnings', 'ordinary'):
            bucket[role] += 1
        else:
            bucket['other'] += 1
    report = []
    for year, bucket in sorted(years.items()):
        alerts = bucket['alerts']
        report.append(dict(
            year=year, alerts=alerts,
            deal_share=(bucket['deal'] / alerts) if alerts else None,
            earnings_share=(bucket['earnings'] / alerts) if alerts else None,
            ordinary_share=(bucket['ordinary'] / alerts) if alerts else None,
        ))
    return report


def fold_report(rows: list[dict], label_key: str = 'label', ks=KS) -> dict:
    ordered = _ordered(rows)
    positives = sum(1 for row in ordered if row.get(label_key))
    base = (positives / len(ordered)) if ordered else None
    at_k = {}
    for k in ks:
        at_k[str(k)] = _cut(ordered, k, label_key)
        at_k[str(k)]['alerts_by_year'] = alerts_by_year(rows, k, label_key)
    at_fraction = {}
    for fraction in FRACTIONS:
        k = max(1, math.ceil(len(ordered) * fraction)) if ordered else 0
        at_fraction[f'{fraction:.0%}'] = _cut(ordered, k, label_key)
        at_fraction[f'{fraction:.0%}']['alerts_by_year'] = alerts_by_year(rows, k, label_key)
    return dict(
        n=len(ordered),
        positives=positives,
        base_rate=base,
        average_precision=average_precision(rows, label_key),
        at_k=at_k,
        at_fraction=at_fraction,
        precision_recall=precision_recall(rows, label_key),
    )


def rank_of(score: float, universe: list[float]) -> int:
    return 1 + sum(other > score for other in universe)


def true_case_report(cases: list[dict], universe: list[dict], ks=KS) -> dict:
    """cases have score and id. universe rows are the scored windows in the same fold."""
    scores = [float(row['score']) for row in universe]
    ranked = []
    for case in cases:
        if case.get('score') is None:
            ranked.append(dict(id=case.get('id'), symbol=case.get('symbol'), rank=None, reason=case.get('reason')))
            continue
        ranked.append(dict(
            id=case['id'], symbol=case.get('symbol'), event=case.get('event'),
            instrument=case.get('instrument'), score=case['score'],
            rank=rank_of(float(case['score']), scores), universe=len(scores),
        ))
    scored = [row for row in ranked if row.get('rank')]
    cuts = {}
    n_cases = len(scored)
    for k in ks:
        inside = [row for row in scored if row['rank'] <= k]
        false_alerts = max(k - len(inside), 0)
        cuts[str(k)] = dict(
            cases=len(inside),
            false_alerts=false_alerts,
            false_alerts_per_true_case=(false_alerts / n_cases) if n_cases else None,
        )
    return dict(n_cases=n_cases, cases=ranked, at_k=cuts)
