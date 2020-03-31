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

    def __init__(self):
        self.our_deck = [Card(x) for x in range(52)]
        self.next_card_idx = 0

    def shuffle(self):
        random.shuffle(self.our_deck)
        self.next_card_idx = 0

    def deal_one(self):
        self.next_card_idx += 1
        # TODO(matt): Remove this "str" when you switch to deal_one returning a card
        return (self.our_deck[self.next_card_idx - 1])
