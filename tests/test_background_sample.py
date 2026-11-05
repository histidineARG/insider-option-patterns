import unittest

from background_sample import choose


class BackgroundSamplingTests(unittest.TestCase):
    def test_sampling_is_reproducible_independent_of_input_order(self):
        values=list(range(100))
        self.assertEqual(choose(values,10,'seed'),choose(values[::-1],10,'seed'))
        self.assertNotEqual(choose(values,10,'seed'),choose(values,10,'other seed'))

    def test_small_population_does_not_duplicate_observations(self):
        self.assertEqual(choose(['B','A'],5,'seed'),['A','B'])
        self.assertEqual(choose([],5,'seed'),[])


if __name__=='__main__':unittest.main()
