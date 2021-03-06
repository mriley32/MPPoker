import unittest

import deck

import cards


class CardsTestCase(unittest.TestCase):
    def test_empty_init(self):
        h = cards.PlayerCards()

    def test_init_from_str(self):
        h = cards.PlayerCards.from_str("2s 3d 4h")
        self.assertEqual([deck.Card.from_str("2s"),
                          deck.Card.from_str("3d"),
                          deck.Card.from_str("4h")],
                         h.cards)
        self.assertEqual("2s 3d 4h", str(h))

    def test_hand_rank_ordering(self):
        r1 = [cards.HandRank.FULL_HOUSE, 2, 3]
        r2 = [cards.HandRank.FULL_HOUSE, 2, 3]
        r3 = [cards.HandRank.TWO_PAIR, 10, 9, 8]

        self.assertEqual(r1, r2)
        self.assertNotEqual(r1, r3)
        self.assertLess(r3, r1)
        self.assertLessEqual(r3, r1)
        self.assertLessEqual(r1, r2)
        self.assertGreater(r1, r3)
        self.assertGreaterEqual(r1, r3)
        self.assertGreaterEqual(r1, r2)

    def test_combine(self):
        h1 = cards.PlayerCards.from_str("2c 3d")
        h2 = cards.PlayerCards.from_str("4h 5s")
        self.assertEqual("2c 3d 4h 5s", str(h1.combine(h2)))
    
    def test_hand_rank_too_few_cards(self):
        with self.assertRaises(ValueError):
            cards.PlayerCards.from_str("2s 3c").hand_rank()
        
    def test_hand_rank_5_card(self):
        # for straight flushes. check that we check the high and
        # the low.
        self.assertEqual([cards.HandRank.STRAIGHT_FLUSH, 10],
                         cards.PlayerCards.from_str("9s Ts 8s 7s 6s").hand_rank())
        self.assertEqual([cards.HandRank.STRAIGHT_FLUSH, 14],
                         cards.PlayerCards.from_str("Js Ts Qs Ks As").hand_rank())
        self.assertEqual([cards.HandRank.STRAIGHT_FLUSH, 5],
                         cards.PlayerCards.from_str("4s 2s As 3s 5s").hand_rank())

        self.assertEqual([cards.HandRank.FOUR_OF_A_KIND, 8, 14],
                         cards.PlayerCards.from_str("8s 8c 8d As 8h").hand_rank())
        # Makes sure we don't call four of a kind a low hand
        self.assertEqual([cards.HandRank.FOUR_OF_A_KIND, 14, 8],
                         cards.PlayerCards.from_str("Ac Ad Ah As 8h").hand_rank())

        self.assertEqual([cards.HandRank.FULL_HOUSE, 2, 3],
                         cards.PlayerCards.from_str("2s 2c 3d 3h 2h").hand_rank())
        self.assertEqual([cards.HandRank.FULL_HOUSE, 3, 14],
                         cards.PlayerCards.from_str("As Ac 3d 3h 3h").hand_rank())

        self.assertEqual([cards.HandRank.FLUSH, 14, 12, 10, 8, 6],
                         cards.PlayerCards.from_str("As Ts 8s 6s Qs").hand_rank())

        # for straights, check that we get the high and the low
        self.assertEqual([cards.HandRank.STRAIGHT, 10],
                         cards.PlayerCards.from_str("9c Td 8s 7s 6s").hand_rank())
        self.assertEqual([cards.HandRank.STRAIGHT, 14],
                         cards.PlayerCards.from_str("Jc Td Qs Ks As").hand_rank())
        self.assertEqual([cards.HandRank.STRAIGHT, 5],
                         cards.PlayerCards.from_str("5c 4d 3s 2s As").hand_rank())

        self.assertEqual([cards.HandRank.THREE_OF_A_KIND, 10, 9, 8],
                         cards.PlayerCards.from_str("9s Ts Td Tc 8s").hand_rank())

        self.assertEqual([cards.HandRank.TWO_PAIR, 11, 9, 12],
                         cards.PlayerCards.from_str("9s 9c Js Jd Qc").hand_rank())

        self.assertEqual([cards.HandRank.ONE_PAIR, 3, 7, 6, 5],
                         cards.PlayerCards.from_str("3s 3c 5c 6h 7s").hand_rank())

        self.assertEqual([cards.HandRank.HIGH_CARD, 10, 8, 6, 4, 2],
                         cards.PlayerCards.from_str("2s 4c 6d 8s Ts").hand_rank())


    def test_hand_rank_7_card(self):
        self.assertEqual(
            [cards.HandRank.STRAIGHT_FLUSH, 10],
            cards.PlayerCards.from_str("9s Ts 8s 7s 6s 2s 3s").hand_rank())
        self.assertEqual(
            [cards.HandRank.FULL_HOUSE, 11, 10],
            cards.PlayerCards.from_str("Js Ts Jc 2c 2s Jd Td").hand_rank())
        
        

    
if __name__ == '__main__':
    unittest.main()
