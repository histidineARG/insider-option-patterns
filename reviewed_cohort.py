"""Extract the evidence-overlay cohort, preserving old snapshots and review gates."""
from collections import Counter
from datetime import date
import hashlib
import json
from pathlib import Path

import pymysql

from ma_stock_confirmation import measure
from market_calendar import sessions
from research_cohort import calendar_features, daily_sql, write_rows
from sec_match import connection


REVIEW_FIELDS = (
    'review_status', 'finding', 'locator', 'source', 'timing_source', 'timing_locator',
    'earlier_public_date_lower', 'earlier_public_date_upper', 'earlier_public_session',
    'earlier_source', 'earlier_locator', 'conflicting_source', 'conflicting_locator',
    'identity_source', 'identity_locator', 'cik_verified',
    'share_class_notes', 'split_ticker_change_reviewed', 'reincarnation_reviewed',
    'post_event_ticker_notes', 'consideration_notes', 'corporate_action_items_reviewed',
    'corporate_action_notes',
    'first_public_disclosure_verified', 'corporate_action_review_complete',
    'first_public_lower_utc', 'first_public_upper_utc',
    'announcement_session', 'issuer_cik', 'issuer', 'eligibility', 'date_verified',
    'discovery_basis',
    'price_action_vetting_status', 'price_action_notes', 'price_action_hazards',
    'jump_cause', 'jump_cause_detail', 'news_filter', 'news_locator')


def inputs(root):
    ledger = json.loads((root / 'data/event_review_overrides.json').read_text())
    original = json.loads((root / 'results/research_cohort/event_cohort.json').read_text())
    identity_fields = {'symbol', 'issuer', 'announcement_date', 'announcement_session',
                       'source', 'date_verified', 'eligibility', 'timing_source', 'timing_locator'}
    rows = {(r['symbol'], r['announcement_date']):
            {k: v for k, v in r.items() if k in identity_fields} for r in original
            if r['cohort_status'] == 'price_qualified'}
    for review in ledger['events'] + ledger['additional_candidates']:
        key = review['symbol'], review['announcement_date']
        rows[key] = dict(rows.get(key, {}), **review)
    for row in rows.values():
        row['event_id'] = f"{row['symbol']}:{row['announcement_date']}"
        row.setdefault('review_status', 'first_disclosure_and_corporate_action_review_pending')
        row.setdefault('first_public_disclosure_verified', False)
        row.setdefault('corporate_action_review_complete', False)
        row['training_label_ready'] = False
    return sorted(rows.values(), key=lambda r: r['event_id'])


def apply_saved_reviews(root=Path('.')):
    """Refresh review fields on saved events without re-querying prices or chains."""
    ledger = json.loads((root / 'data/event_review_overrides.json').read_text())
    path = root / 'results/reviewed_cohort/events.json'
    events = json.loads(path.read_text())
    by_key = {(r['symbol'], r['announcement_date']): r
              for r in ledger['events'] + ledger['additional_candidates']}
    for row in events:
        review = by_key.get((row['symbol'], row['announcement_date']))
        if not review:
            continue
        for name in REVIEW_FIELDS:
            if name in review:
                row[name] = review[name]
        row['training_label_ready'] = False
        row.setdefault('first_public_disclosure_verified', False)
        row.setdefault('corporate_action_review_complete', False)
    write_rows(root / 'results/reviewed_cohort', 'events', events)
    source_paths = ['data/event_review_overrides.json', 'results/research_cohort/event_cohort.json',
                    'data/calendar/nyse_sessions.json']
    manifest = dict(event_count=len(events), feature_rows=None,
                    review_status_counts=dict(Counter(r['review_status'] for r in events)),
                    price_status_counts=dict(Counter(r.get('price_qualification_status') for r in events)),
                    training_ready_events=sum(r.get('training_label_ready') for r in events),
                    source_sha256={p: hashlib.sha256((root/p).read_bytes()).hexdigest() for p in source_paths},
                    notes=['Review fields refreshed offline from event_review_overrides.json.',
                           'Price and option feature measurements were not requeryed.',
                           'No event is training-ready.'])
    prior = json.loads((root / 'results/reviewed_cohort/manifest.json').read_text())
    for key in ('feature_rows', 'quote_screen'):
        if key in prior:
            manifest[key] = prior[key]
    (root / 'results/reviewed_cohort/manifest.json').write_text(json.dumps(manifest, indent=2) + '\n')
    lines = ['# Evidence-overlay cohort', '',
             'Primary-source findings overlay the preserved earlier snapshots. Additional candidates '
             'come from acquirer releases, independently of observed option activity. '
             'Volume does not determine price qualification.', '',
             '| Event | Price change | Price status | Valid feature days | Days with quote candidates | Review status |',
             '| --- | ---: | ---: | ---: | ---: | --- |']
    for r in events:
        change = f"{r['close_return_pct']:.2f}%" if r.get('close_return_pct') is not None else 'unknown'
        lines.append(f"| {r['event_id']} | {change} | {r.get('price_qualification_status')} | "
                     f"{r.get('valid_feature_days', 0)} | {r.get('days_with_usable_quote_candidates', 0)} | "
                     f"{r['review_status']} |")
    lines += ['', 'Earlier-disclosure findings, conflicts, source URLs, and locators are preserved in '
              'events.json. First-disclosure and corporate-action gates remain explicit; price-qualified '
              'is not training-ready. Quote counts use fixed present-day research assumptions in manifest.json; '
              'they are not validated historical liquidity or standard-contract eligibility.', '']
    (root / 'results/reviewed_cohort/REPORT.md').write_text('\n'.join(lines))
    return manifest


def quote_sql():
    # No OI eligibility filter: publication timing is not established.
    eligible = ("`type`='call' AND underlying_last>0 AND "
                "strike BETWEEN underlying_last*1.03 AND underlying_last*1.50 "
                "AND DATEDIFF(edate,qdate) BETWEEN 14 AND 60 "
                "AND bid>0 AND ask>=bid AND ask<=10 "
                "AND (ask-bid)<=0.5*((ask+bid)/2) AND volume>=10")
    return daily_sql().replace('\n      FROM optiondaily',
        f', SUM(CASE WHEN {eligible} THEN 1 ELSE 0 END) AS usable_quote_contracts\n      FROM optiondaily')


def run(c, root=Path('.')):
    calendar = sessions(root=root)
    events, features = [], []
    try:
        with c.cursor() as q:
            q.execute('SET SESSION MAX_EXECUTION_TIME=60000')
            q.execute('START TRANSACTION READ ONLY')
            for item in inputs(root):
                row = dict(item)
                event = date.fromisoformat(row['announcement_date'])
                reaction = next(d for d in calendar if d > event or
                                (d == event and row['announcement_session'] != 'after_close'))
                i = calendar.index(reaction)
                try:
                    q.execute('SELECT qdate,open,high,low,close,volume FROM stockquote '
                              'WHERE symbol=%s AND qdate BETWEEN %s AND %s ORDER BY qdate',
                              (row['symbol'], calendar[i-20], reaction))
                    row.update(measure(q.fetchall(), reaction, calendar[i-1], calendar[i-20:i], 2))
                    prior = [d for d in calendar if d < event]
                    q.execute(quote_sql(), (row['symbol'], prior[-50], prior[-1]))
                    days = q.fetchall()
                    daily = calendar_features(days, calendar, event)
                    row['option_coverage_status'] = 'observed_chain' if days else 'no_rows_listing_status_unknown'
                    row['valid_feature_days'] = sum(bool(r.get('chain_observed') and
                        r.get('baseline_complete') and r.get('volume_data_valid')) for r in daily)
                    row['days_with_usable_quote_candidates'] = sum(r.get('usable_quote_contracts', 0) > 0 for r in daily)
                    row['price_qualification_status'] = ('price_qualified' if row.get('price_jump_at_least_15pct')
                        else ('price_below_15pct' if 'price_jump_at_least_15pct' in row else 'price_unmeasurable'))
                    features.extend(dict(r, symbol=row['symbol'], event_id=row['event_id'],
                                         announcement_date=row['announcement_date']) for r in daily)
                except pymysql.MySQLError as exc:
                    row.update(option_coverage_status='query_failed', query_error=str(exc),
                               price_qualification_status='query_failed')
                events.append(row)
    finally:
        c.rollback()
    folder = root / 'results/reviewed_cohort'
    folder.mkdir(parents=True, exist_ok=True)
    write_rows(folder, 'events', events)
    write_rows(folder, 'features', features)
    source_paths = ['data/event_review_overrides.json', 'results/research_cohort/event_cohort.json',
                    'data/calendar/nyse_sessions.json']
    manifest = dict(event_count=len(events), feature_rows=len(features),
                    review_status_counts=dict(Counter(r['review_status'] for r in events)),
                    price_status_counts=dict(Counter(r['price_qualification_status'] for r in events)),
                    training_ready_events=sum(r['training_label_ready'] for r in events),
                    source_sha256={p: hashlib.sha256((root/p).read_bytes()).hexdigest() for p in source_paths},
                    quote_screen=dict(call=True, otm_fraction=[0.03, 0.50], dte=[14, 60],
                        minimum_bid_exclusive=0, minimum_volume=10, maximum_ask=10,
                        maximum_relative_spread=0.5, multiplier_verified=False,
                        vendor_delivery_timing_verified=False),
                    notes=['Quote candidates are diagnostics, not asserted executable contracts.',
                           'No option listing status is inferred from absent rows.',
                           'All labels remain unknown until evidence gates pass.',
                           'Raw prices are not corrected from conflicting legal allegations.'])
    (folder / 'manifest.json').write_text(json.dumps(manifest, indent=2) + '\n')
    lines = ['# Evidence-overlay cohort', '',
             'Primary-source findings overlay the preserved earlier snapshots. Additional candidates '
             'come from acquirer releases, independently of observed option activity. '
             'Volume does not determine price qualification.', '',
             '| Event | Price change | Price status | Valid feature days | Days with quote candidates | Review status |',
             '| --- | ---: | --- | ---: | ---: | --- |']
    for r in events:
        change = f"{r['close_return_pct']:.2f}%" if r.get('close_return_pct') is not None else 'unknown'
        lines.append(f"| {r['event_id']} | {change} | {r['price_qualification_status']} | "
                     f"{r.get('valid_feature_days', 0)} | {r.get('days_with_usable_quote_candidates', 0)} | {r['review_status']} |")
    lines += ['', 'Earlier-disclosure findings, conflicts, source URLs, and locators are preserved in '
              'events.json. First-disclosure and corporate-action gates remain explicit; price-qualified '
              'is not training-ready. Quote counts use fixed present-day research assumptions in manifest.json; '
              'they are not validated historical liquidity or standard-contract eligibility.', '']
    (folder / 'REPORT.md').write_text('\n'.join(lines))
    return manifest


if __name__ == '__main__':
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == '--apply-reviews-only':
        print(json.dumps(apply_saved_reviews(), indent=2))
    else:
        with connection() as c:
            print(json.dumps(run(c), indent=2))
