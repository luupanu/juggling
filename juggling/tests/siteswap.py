from siteswap import (
    all_siteswaps,
    number_of_juggling_patterns
)

import unittest

class TestAllSiteswaps(unittest.TestCase):
    def test_all_siteswaps(self):
        input('\nWarning: these tests might take a few minutes to run. Press ENTER to continue\n')
        for period in range(1, 9):
            for balls in range(1, 9):
                for max_throw in range(balls, 16):
                    print(f'Testing period={period} balls={balls} max_throw={max_throw}', end=' ')
                    self.assertTrue(
                        len(all_siteswaps(balls, period, max_throw)) == number_of_juggling_patterns(balls, period, max_throw)
                    )
                    print('...OK')

if __name__ == '__main__':
    unittest.main()
