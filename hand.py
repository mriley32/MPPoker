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
    """Class representing a hand of cards

    Attributes:
       cards: a list of deck.Card
    """
    
    def __init__(self, cards=[]):
        # Make a copy to avoid any aliasing problems with the caller
        self.cards = cards.copy()

    def from_str(input_str):
        return Hand([deck.Card.from_str(s) for s in input_str.split(" ")])

    def __str__(self):
        return " ".join(str(c) for c in self.cards) 
        
    def hand_rank(self):
        """Return the best poker hand that can be made from these cards.

        Returns:
          list where first element is HandRank and other elements are what is
          needed to rank this hard. For example, if the hand is 
          2s 2h 9s 9h Td, the list returned is
          [TWO_PAIR, 9, 2, 10]
       
        Raises:
          ValueError: if the hand has less than 5 cards
        """
        return [HIGH_CARD]
