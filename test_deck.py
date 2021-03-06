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

    def test_from_str_invalid(self):
        with self.assertRaises(ValueError):
            deck.Card.from_str("foobar")
        with self.assertRaises(ValueError):
            deck.Card.from_str("2")
        with self.assertRaises(ValueError):
            deck.Card.from_str("")


class DeckTestCase(unittest.TestCase):

    def test_deal_one(self):
        d = deck.Deck()

        self.assertEqual("2c", str(d.deal_one()))
        self.assertEqual("3c", str(d.deal_one()))
        self.assertEqual("4c", str(d.deal_one()))

    def test_deal(self):
        d = deck.Deck()

        actual = d.deal(3)
        self.assertEqual(3, len(actual))
        self.assertEqual("2c", str(actual[0]))
        self.assertEqual("3c", str(actual[1]))
        self.assertEqual("4c", str(actual[2]))

    def test_deal_one_invalid(self):
        d = deck.Deck()
        for _ in range(52):
            d.deal_one()
        with self.assertRaises(IndexError):
            d.deal_one()

    def test_shuffle(self):
        # It's annoying hard to test a shuffle. We'll just make sure
        # it runs and the first two cards are different.
        d = deck.Deck()
        d.shuffle()
        c1 = d.deal_one()
        c2 = d.deal_one()
        self.assertNotEqual(c1, c2)

    def test_invalid_order(self):
        with self.assertRaises(ValueError):
            deck.Deck(order=[1] * 52)
        with self.assertRaises(ValueError):
            deck.Deck(order=[1, 2])

    def test_order(self):
        order = list(range(52))
        order.remove(50)
        order.insert(0, 50)
        d = deck.Deck(order=order)
        self.assertEqual(deck.Card(50), d.our_deck[0])
        self.assertEqual(deck.Card(0), d.our_deck[1])
        self.assertEqual(deck.Card(49), d.our_deck[50])
        self.assertEqual(deck.Card(51), d.our_deck[51])

    def test_from_intial_cards_str(self):
        d = deck.Deck.from_initial_cards_str("Ac As Ad")
        self.assertEqual(deck.Card.from_str("Ac"), d.our_deck[0])
        self.assertEqual(deck.Card.from_str("As"), d.our_deck[1])
        self.assertEqual(deck.Card.from_str("Ad"), d.our_deck[2])
        
        
if __name__ == '__main__':
    unittest.main()
