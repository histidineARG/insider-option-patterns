from datetime import date
import unittest

from insider_footprint import (
    BASELINE,
    MIN_VOLUME,
    WINDOW,
    control_rows,
    evaluate,
    mcnemar,
    rate_row,
    score_window,
    span,
)


class FootprintRuleTests(unittest.TestCase):
    def day(self, offset, call_vol, band_vol, top_share=1.0):
        return dict(qdate=date(2024, 1, 1).fromordinal(date(2024, 6, 1).toordinal() + offset),
                    call_vol=call_vol, band_vol=band_vol, top_share=top_share)

    def quiet_baseline(self):
        return [self.day(i, 10, 2, 0.5) for i in range(BASELINE)]

    def test_concentrated_surge_alerts(self):
        window = [self.day(100, 10, 2)] * (WINDOW - 1) + [self.day(110, 400, 200, 0.8)]
        scored = score_window(window, self.quiet_baseline())
        self.assertTrue(scored['eligible'])
        self.assertTrue(scored['hit'])
        self.assertEqual(len(scored['alert_dates']), 1)

    def test_high_volume_outside_the_band_does_not_alert(self):
        window = [self.day(110, 400, 20, 1.0)] + [self.day(111 + i, 10, 2) for i in range(WINDOW - 1)]
        scored = score_window(window, self.quiet_baseline())
        self.assertTrue(scored['eligible'])
        self.assertFalse(scored['hit'])

    def test_diffuse_band_does_not_alert(self):
        window = [self.day(110, 400, 200, 0.2)] + [self.day(111 + i, 10, 2) for i in range(WINDOW - 1)]
        scored = score_window(window, self.quiet_baseline())
        self.assertFalse(scored['hit'])

    def test_short_history_is_ineligible(self):
        scored = score_window([self.day(i, 400, 200) for i in range(WINDOW)],
                              [self.day(i, 10, 2) for i in range(5)])
        self.assertFalse(scored['eligible'])
        self.assertFalse(scored['hit'])

    def test_missing_chain_day_is_not_filled_with_zero(self):
        sessions = [date(2024, 1, 1).fromordinal(date(2024, 1, 1).toordinal() + i) for i in range(120)]
        # Treat every day as a session for this unit. Drop the day before the jump.
        jump = sessions[90]
        window, baseline = span(sessions, {d: i for i, d in enumerate(sessions)}, jump)
        by_date = {d: dict(qdate=d, call_vol=10, band_vol=2, top_share=1.0) for d in baseline}
        for d in window[:-1]:
            by_date[d] = dict(qdate=d, call_vol=10, band_vol=2, top_share=1.0)
        by_date[window[-1]] = dict(qdate=window[-1], call_vol=500, band_vol=400, top_share=0.9)
        # Remove one earlier window day entirely.
        del by_date[window[0]]
        scored = evaluate(by_date, window, baseline)
        self.assertEqual(scored['observed_window'], WINDOW - 1)
        self.assertTrue(scored['hit'])

    def test_jump_session_is_outside_the_window(self):
        sessions = [date(2024, 1, 1).fromordinal(date(2024, 1, 1).toordinal() + i) for i in range(120)]
        jump = sessions[90]
        window, baseline = span(sessions, {d: i for i, d in enumerate(sessions)}, jump)
        self.assertNotIn(jump, window)
        self.assertEqual(len(window), WINDOW)
        self.assertEqual(len(baseline), BASELINE)
        self.assertLess(window[-1], jump)

    def test_zero_baseline_still_requires_the_minimum_print(self):
        baseline = [self.day(i, 0, 0) for i in range(BASELINE)]
        quiet = [self.day(100 + i, MIN_VOLUME - 1, MIN_VOLUME - 1, 1.0) for i in range(WINDOW)]
        self.assertFalse(score_window(quiet, baseline)['hit'])
        loud = quiet[:-1] + [self.day(120, MIN_VOLUME, int(MIN_VOLUME * 0.8), 1.0)]
        self.assertTrue(score_window(loud, baseline)['hit'])

    def test_control_rows_keep_their_own_eligibility(self):
        records = [dict(placebo=dict(eligible=True, hit=True, max_ratio=4.0))]
        rows = control_rows(records, 'placebo')
        self.assertEqual(rate_row(rows)['hits'], 1)
        self.assertEqual(rate_row(rows)['eligible'], 1)

    def test_mcnemar_pairs(self):
        result = mcnemar([(True, False), (True, False), (False, True), (False, False)])
        self.assertEqual(result['case_only'], 2)
        self.assertEqual(result['control_only'], 1)
        self.assertEqual(result['neither'], 1)
        self.assertIsNotNone(result['chi2'])


if __name__ == '__main__':
    unittest.main()
