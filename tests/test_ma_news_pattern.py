import unittest

from ma_news_pattern import held_into_event


class HeldIntoEventTests(unittest.TestCase):
    def test_a_built_position_still_open_on_the_announcement(self):
        self.assertTrue(held_into_event([91, 589, 1639]))

    def test_a_position_closed_before_the_announcement(self):
        self.assertFalse(held_into_event([0, 128, 19]))

    def test_a_single_print_is_not_enough(self):
        self.assertFalse(held_into_event([1060]))


if __name__ == '__main__':
    unittest.main()
