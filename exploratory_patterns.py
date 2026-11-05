"""Describe fixed volume rules without assigning negatives or estimating accuracy."""
from collections import defaultdict
import json
from pathlib import Path

from research_cohort import write_rows


def valid(row):
    return bool(row.get('chain_observed') and row.get('baseline_complete') and row.get('volume_data_valid'))


def alert(row,minimum_volume,multiple):
    if not valid(row):return None
    if row['otm_call_volume']<minimum_volume:return False
    return bool(row.get('zero_volume_baseline') or
                (row.get('otm_ratio20') is not None and row['otm_ratio20']>=multiple))


def run(root=Path('.')):
    events=json.loads((root/'results/research_cohort/pre_event_features.json').read_text())
    background=json.loads((root/'results/background_sample/observations.json').read_text())
    groups=defaultdict(list)
    for r in events:groups[r['symbol'],r['announcement_date']].append(r)
    summary=[];details=[]
    for minimum_volume,multiple in [(100,3),(500,5),(1000,10)]:
        key=f'volume_{minimum_volume}_ratio_{multiple}'
        hits=0;eligible=0
        for (symbol,event),rows in sorted(groups.items()):
            window=sorted(rows,key=lambda r:r['qdate'])[-10:]
            usable=[r for r in window if valid(r) and r['next_close_strictly_before_announcement']]
            alerts=[r for r in usable if alert(r,minimum_volume,multiple)]
            if usable:eligible+=1
            if alerts:hits+=1
            details.append(dict(rule=key,symbol=symbol,announcement_date=event,
                                observed_valid_entry_proxy_sessions=len(usable),
                                full_10_session_window_observed=all(valid(r) for r in window) and len(window)==10,
                                descriptive_alert_sessions=len(alerts),
                                first_alert_date=alerts[0]['qdate'] if alerts else None))
        bg_valid=[r for r in background if valid(r)]
        summary.append(dict(rule=key,min_otm_call_volume=minimum_volume,min_ratio20=multiple,
                            events_with_any_usable_entry_proxy_session=eligible,
                            events_with_descriptive_alert=hits,
                            background_valid_observations=len(bg_valid),
                            background_alert_observations=sum(bool(alert(r,minimum_volume,multiple)) for r in bg_valid),
                            accuracy_estimated=False))
    folder=root/'results/exploratory_patterns';folder.mkdir(parents=True,exist_ok=True)
    write_rows(folder,'rule_summary',summary);write_rows(folder,'event_diagnostics',details)
    lines=['# Exploratory option-volume rules','',
           'These fixed rules are descriptive diagnostics, not fitted models, selected thresholds, or a backtest. No observations have been assigned reliable negative labels. Event and background samples have different selection and coverage; their counts cannot establish precision, false-positive rates, false-negative rates, or profitability.','',
           'Calls are OTM with 1–60 days to expiry. Each rule requires minimum aggregate volume and a multiple of the preceding 20 calendar sessions. A genuine zero baseline qualifies if current volume meets the minimum. Missing or invalid baseline data produces no evaluable observation, rather than a negative result.','',
           'Event counts use the last 10 pre-announcement sessions and require the next-session close proxy to precede the announcement date. They are not adjusted for earlier public rumors or real vendor delivery times. Background counts refer to individual sampled stock-days, not alert episodes.','',
           '| Minimum volume | Prior-volume multiple | Events with alert / events with usable data | Background observations with alert / usable observations |',
           '| ---: | ---: | ---: | ---: |']
    for r in summary:
        lines.append(f"| {r['min_otm_call_volume']} | {r['min_ratio20']} | {r['events_with_descriptive_alert']} / {r['events_with_any_usable_entry_proxy_session']} | {r['background_alert_observations']} / {r['background_valid_observations']} |")
    lines+=['','Do not choose a winning threshold from this table. Next steps are primary-source first-disclosure review, event-universe expansion, historical security classification and coverage repair, followed by chronological training/validation/test construction. An event without an alert in this diagnostic is not yet a validated false negative.','']
    (folder/'REPORT.md').write_text('\n'.join(lines))
    print(json.dumps(summary,indent=2))
    return summary


if __name__=='__main__':run()
