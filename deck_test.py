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

    def test_init_invalid(self):
        with self.assertRaises(ValueError):
            deck.Card(-1)
        with self.assertRaises(ValueError):
            deck.Card(52)
        with self.assertRaises(ValueError):
            deck.Card(1000)

    def test_from_str(self):
        for idx in range(52):
            c = deck.Card(idx)
            new_card = deck.Card.from_str(str(c))
            self.assertEqual(idx, new_card.card_idx)
            
            
if __name__ == '__main__':
    unittest.main()
