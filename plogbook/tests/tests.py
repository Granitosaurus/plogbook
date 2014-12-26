from plogbook import utils

import unittest

# Here's our "unit tests".
class UtilsTestsunittest.TestCase):

    def test_truncate(self):
        tests = ((['test', 20], 'test'),
                 (['12345678910', 10], '1234567...'),
                 (['12345678910', 10, False, True], '...5678910'),
                 (['alapugaciova', 3, True], 'ala'),
                 (['alapugaciova', 9, True, True], 'pugaciova'),
                 (['banana', 5], 'ba...'),)

        for test in tests:
            self.failUnlessEqual(utils.truncate(*test[0]), test[1])


def main():
    unittest.main()

if __name__ == '__main__':
    main()