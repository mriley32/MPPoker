import unittest

import deck


class CardTestCase(unittest.TestCase):

        def test_str(self):
                self.assertEqual("2c", str(deck.Card(0)))
                self.assertEqual("2d", str(deck.Card(13)))
                self.assertEqual("Th", str(deck.Card(34)))
                self.assertEqual("Jh", str(deck.Card(35)))
                self.assertEqual("Qh", str(deck.Card(36)))
                self.assertEqual("Kh", str(deck.Card(37)))
                self.assertEqual("As", str(deck.Card(51)))
                         

if __name__ == '__main__':
    unittest.main()
