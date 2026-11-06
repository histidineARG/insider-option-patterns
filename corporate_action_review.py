"""Structured corporate-action / identity checklist; never auto-marks complete."""
from collections import Counter
import hashlib
import json
from pathlib import Path

from research_cohort import write_rows


REQUIRED = [
    'issuer_cik_matches_edgar',
    'ticker_maps_to_issuer_on_announcement_date',
    'share_class_or_ads_terms_recorded',
    'no_unresolved_split_or_ticker_change_in_feature_window',
    'post_event_ticker_reincarnation_checked',
    'consideration_special_items_recorded',
]


def evaluate(event, ledger_row=None):
    """Return checklist booleans and remaining blockers from review evidence only."""
    review = dict(event)
    if ledger_row:
        review.update(ledger_row)
    status = review.get('review_status') or ''
    identity_ok = bool(review.get('identity_source') or 'identity_corrected' in status
                       or review.get('cik_verified'))
    checks = {
        'issuer_cik_matches_edgar': identity_ok,
        'ticker_maps_to_issuer_on_announcement_date': bool(review.get('issuer_cik') and identity_ok),
        'share_class_or_ads_terms_recorded': bool(
            review.get('share_class_notes') or status == 'announcement_verified_ads_terms_reviewed'),
        'no_unresolved_split_or_ticker_change_in_feature_window': bool(
            review.get('split_ticker_change_reviewed')),
        'post_event_ticker_reincarnation_checked': bool(
            review.get('post_event_ticker_notes') or review.get('reincarnation_reviewed')),
        'consideration_special_items_recorded': bool(
            review.get('consideration_notes') or review.get('corporate_action_items_reviewed')),
    }
    blockers = [name for name in REQUIRED if not checks[name]]
    return dict(
        event_id=review.get('event_id') or f"{review['symbol']}:{review['announcement_date']}",
        symbol=review['symbol'],
        announcement_date=review['announcement_date'],
        checks=checks,
        blockers=blockers,
        corporate_action_review_complete=False,  # never auto-complete
        ready_to_mark_complete=len(blockers) == 0,
        notes=review.get('corporate_action_notes'),
    )


def run(root=Path('.')):
    events = json.loads((root/'results/reviewed_cohort/events.json').read_text())
    ledger = json.loads((root/'data/event_review_overrides.json').read_text())
    by_key = {(r['symbol'], r['announcement_date']): r
              for r in ledger['events'] + ledger['additional_candidates']}
    rows = [evaluate(event, by_key.get((event['symbol'], event['announcement_date'])))
            for event in events]
    folder = root/'results/corporate_action_review'
    folder.mkdir(parents=True, exist_ok=True)
    write_rows(folder, 'checklist', rows)
    manifest = dict(
        events=len(rows),
        ready_to_mark_complete=sum(r['ready_to_mark_complete'] for r in rows),
        marked_complete=sum(r['corporate_action_review_complete'] for r in rows),
        blocker_counts=dict(Counter(b for r in rows for b in r['blockers'])),
        source_sha256={
            'results/reviewed_cohort/events.json':
                hashlib.sha256((root/'results/reviewed_cohort/events.json').read_bytes()).hexdigest(),
            'data/event_review_overrides.json':
                hashlib.sha256((root/'data/event_review_overrides.json').read_bytes()).hexdigest(),
        },
        notes=['Checklist readiness is not corporate_action_review_complete.',
               'No event is auto-marked complete by this tool.'])
    (folder/'manifest.json').write_text(json.dumps(manifest, indent=2) + '\n')
    lines = ['# Corporate-action and identity checklist', '',
             f"{manifest['events']} events evaluated. {manifest['ready_to_mark_complete']} have all "
             'checklist items evidenced in review fields; none are auto-marked complete.', '',
             '| Event | Ready for manual complete mark | Remaining blockers |',
             '| --- | --- | --- |']
    for r in rows:
        blockers = ', '.join(r['blockers']) if r['blockers'] else 'none'
        lines.append(f"| {r['event_id']} | {r['ready_to_mark_complete']} | {blockers} |")
    lines += ['', 'Populate share-class, split/ticker-change, reincarnation, and consideration '
              'notes in event_review_overrides.json before marking corporate_action_review_complete.', '']
    (folder/'REPORT.md').write_text('\n'.join(lines))
    return manifest


if __name__ == '__main__':
    print(json.dumps(run(), indent=2))
