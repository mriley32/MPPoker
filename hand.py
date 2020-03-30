from enum import Enum, unique

import deck

@unique
class HandRank(Enum):
    HIGH_CARD = 0
    ONE_PAIR = 1
    TWO_PAIR = 2
    THREE_OF_A_KIND = 3
    STRAIGHT = 4
    FLUSH = 5
    FULL_HOUSE = 6
    FOUR_OF_A_KIND = 7
    STRAIGHT_FLUSH = 8


class Hand:
    def __init__(self):
        self.cards = []

    def hand_rank(self):
        return [HIGH_CARD]
