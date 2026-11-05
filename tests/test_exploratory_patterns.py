import unittest

from exploratory_patterns import alert


class ExploratoryPatternTests(unittest.TestCase):
    def test_missing_data_is_not_a_negative(self):
        self.assertIsNone(alert(dict(chain_observed=False),100,3))

    def test_zero_baseline_requires_minimum_volume(self):
        row=dict(chain_observed=True,baseline_complete=True,volume_data_valid=True,
                 otm_call_volume=100,zero_volume_baseline=True,otm_ratio20=None)
        self.assertTrue(alert(row,100,3))
        self.assertFalse(alert(row,101,3))

    def test_nonzero_baseline_threshold_is_inclusive(self):
        row=dict(chain_observed=True,baseline_complete=True,volume_data_valid=True,
                 otm_call_volume=100,zero_volume_baseline=False,otm_ratio20=3)
        self.assertTrue(alert(row,100,3))
        row['otm_ratio20']=2.999
        self.assertFalse(alert(row,100,3))


if __name__=='__main__':unittest.main()
