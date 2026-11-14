import unittest

from quiet_otm_screen import apply_floors
from quiet_screen import classify_volume


class ShortDatedOtmTests(unittest.TestCase):
    def test_baseline_and_signal_day_floors(self):
        loud = classify_volume([0, 0, 0, 0, 800], 100)
        kept = apply_floors(loud, [0, 0, 0, 0, 800], 100)
        self.assertTrue(kept['single'])
        thin = apply_floors(loud, [0, 0, 0, 0, 800], 50)
        self.assertFalse(thin['single'])
        small = apply_floors(loud, [0, 0, 0, 0, 400], 100)
        self.assertFalse(small['single'])

    def test_multi_day_still_needs_500_on_the_loudest_day(self):
        loud = classify_volume([0, 0, 400, 450, 100], 100)
        self.assertTrue(loud['multi'])
        gated = apply_floors(loud, [0, 0, 400, 450, 100], 100)
        self.assertFalse(gated['multi'])


if __name__ == '__main__':
    unittest.main()
