import unittest

from evaluation import alert_episodes, blocked_gates, fit_logistic, fixed_rule_diagnostics, predict_proba
from trading_assumptions import blocked_trading_gates


class EvaluationTests(unittest.TestCase):
    def test_gates_block_when_labels_and_eligibility_are_absent(self):
        observations = [dict(training_label=None, historical_security_identity_verified=False,
                             vendor_delivery_timing_verified=False, quote_eligibility_verified=False)]
        blocked = blocked_gates(dict(known_positive_labels=0, research_eligible=0),
                                dict(population_evaluation_requires=[
                                    'verified_outcome_labels', 'historical_security_identity',
                                    'complete_population_frame', 'natural_prevalence_or_valid_sampling_design',
                                    'vendor_delivery_timing', 'passed_coverage_audit']),
                                observations)
        self.assertIn('verified_outcome_labels', blocked)
        self.assertIn('vendor_delivery_timing', blocked)

    def test_episodes_respect_cooldown(self):
        rows = [
            dict(symbol='AAA', qdate='2020-01-02', observation_id='AAA:2020-01-02',
                 outcome_event_ids=[], training_label=None),
            dict(symbol='AAA', qdate='2020-01-03', observation_id='AAA:2020-01-03',
                 outcome_event_ids=[], training_label=None),
            dict(symbol='AAA', qdate='2020-01-20', observation_id='AAA:2020-01-20',
                 outcome_event_ids=['E1'], training_label=1),
        ]
        index = {'2020-01-02': 0, '2020-01-03': 1, '2020-01-20': 12}
        episodes = alert_episodes(rows, [True, True, True], cooldown_sessions=10, calendar_index=index)
        self.assertEqual(len(episodes), 2)
        self.assertEqual(episodes[0]['start'], '2020-01-02')
        self.assertEqual(episodes[0]['end'], '2020-01-03')
        self.assertEqual(episodes[1]['episode_label'], 1)

    def test_logistic_separates_simple_classes(self):
        rows = [
            dict(training_label=0, chain_observed=True, baseline_complete=True, volume_data_valid=True,
                 otm_call_volume=0, otm_mean20=0, call_share=0.2, top_otm_call_share=0.1,
                 zero_volume_baseline=True),
            dict(training_label=1, chain_observed=True, baseline_complete=True, volume_data_valid=True,
                 otm_call_volume=1000, otm_mean20=10, call_share=0.9, top_otm_call_share=0.8,
                 zero_volume_baseline=False),
        ]
        names = ['log1p_otm_call_volume', 'log1p_otm_mean20', 'call_share',
                 'top_otm_call_share', 'zero_volume_baseline']
        weights = fit_logistic(rows, names, iterations=500)
        self.assertGreater(predict_proba(rows[1], weights, names), predict_proba(rows[0], weights, names))

    def test_fixed_rule_diagnostics_do_not_authorize_population_metrics(self):
        rows = [dict(symbol='AAA', qdate='2020-01-02', observation_id='AAA:2020-01-02',
                     chain_observed=True, baseline_complete=True, volume_data_valid=True,
                     otm_call_volume=500, otm_mean20=10, otm_ratio20=50, zero_volume_baseline=False,
                     purge_reason=None, partition='train', training_label=None, outcome_event_ids=[])]
        protocol = dict(fixed_rules=[[100, 3]], episode_cooldown_sessions=10)
        summary, episodes = fixed_rule_diagnostics(rows, protocol, {'2020-01-02': 0})
        self.assertFalse(summary[0]['population_metrics_authorized'])
        self.assertEqual(len(episodes), 1)

    def test_trading_remains_blocked_without_eligible_labeled_rows(self):
        blocked = blocked_trading_gates(
            dict(population_evaluation_authorized=False),
            dict(research_eligible=0, known_positive_labels=0))
        self.assertIn('population_evaluation_unauthorized', blocked)
        self.assertIn('vendor_delivery_timing_unverified', blocked)


if __name__ == '__main__':
    unittest.main()
