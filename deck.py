from enum import Enum
import random
import sys


class Suit(Enum):
    CLUBS = 0
    DIAMONS = 1
    HEARTS = 2
    SPADES = 3


class Card:
    _SUIT_STR = ["c", "d", "h", "s"]
    _RANK_STR = ["", "", "2", "3", "4", "5", "6", "7", "8", "9", "T", "J", "Q", "K", "A"]

    def from_str(s):
        if len(s) != 2:
            raise ValueError("Bad card string: {}".format(s))
        return Card(
            Card._SUIT_STR.index(s[1]) * 13 +
            Card._RANK_STR.index(s[0]) - 2)

    def __init__(self, idx):
        if idx < 0 or idx > 51:
            raise ValueError("Invalid card index {}".format(idx))
        self.card_idx = idx

    def __str__(self):
        return Card._RANK_STR[self.rank()] + Card._SUIT_STR[self.suit().value]

    def __eq__(self, other):
        return self.card_idx == other.card_idx
    
    def suit(self):
        return Suit(self.card_idx // 13)

    def rank(self):
        return (self.card_idx % 13) + 2

class Deck:

    def __init__(self, order=range(52)):
        if len(order) != 52:
            raise ValueError("Incorrect number of cards in order: {}".format(order))
        if len(set(order)) != 52:
            raise ValueError("Non unique cards in order: {}".format(order))
        self.our_deck = [Card(x) for x in order]
        self.next_card_idx = 0

    def from_initial_cards_str(top_cards_str):
        """Create a deck with the top cards given.

        Args:
          top_cards_str: Space sepaated string of two character card string

        Returns
          Deck
        """
        order = [Card.from_str(s).card_idx for s in top_cards_str.split(" ")]
        for i in range(52):
            if i not in order:
                order.append(i)
        return Deck(order=order)
        
    def shuffle(self):
        random.shuffle(self.our_deck)
        self.next_card_idx = 0

    def deal(self, num):
        self.next_card_idx += num
        return self.our_deck[self.next_card_idx - num: self.next_card_idx]

    def deal_one(self):
        return self.deal(1)[0]

