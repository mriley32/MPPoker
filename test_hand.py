import unittest

import deck

import hand


class HandTestCase(unittest.TestCase):
    def test_empty_init(self):
        h = hand.Hand()

    def test_init_from_str(self):
        h = hand.Hand.from_str("2s 3d 4h")
        self.assertEqual([deck.Card.from_str("2s"),
                          deck.Card.from_str("3d"),
                          deck.Card.from_str("4h")],
                         h.cards)
        self.assertEqual("2s 3d 4h", str(h))

    def test_hand_rank_5_card(self):
        pass

if __name__ == '__main__':
    unittest.main()
