import unittest

import deck


class CardTestCase(unittest.TestCase):

        def test_str(self):
                self.assertEqual("2c", str(deck.Card(0)))
                         

if __name__ == '__main__':
    unittest.main()
