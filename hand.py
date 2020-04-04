from enum import Enum, unique
import functools
import itertools


import deck

@unique
@functools.total_ordering
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

    def __eq__(self, other):
        return self.value == other.value

    def __ne__(self, other):
        return self.value != other.value

    def __lt__(self, other):
        return self.value < other.value
    
def compare_hrank(rank0,rank1):
    #Meant to tell which rank is higher from ranks returned by hand_rank
    #0 for rank0, 1 for rank1, 2 for tie (split pot)
    ans = 2
    i = 0
    for x in range(len(rank0)):
        if i == 0:
            i = 1 #only need .value for the first item which is an enum
            if(rank0[x].value > rank1[x].value):
                ans = 0
                return ans
            if(rank0[x].value < rank1[x].value):
                ans = 1
                return ans
        else:
            if(rank0[x] > rank1[x]):
                ans = 0
                return ans
            if(rank0[x] < rank1[x]):
                ans = 1
                return ans
    return ans;

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

    def hand_print(self):
        for c in self.cards:
            print(str(c)+ " "),  
        print() 

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
        if len(self.cards) < 5:
            raise ValueError("Not enough cards ({}) in {} to get hand rank"
                             .format(len(self.cards), self))

        if len(self.cards) > 5:
            return max(Hand(list(cards)).hand_rank()
                       for cards in itertools.combinations(self.cards, 5))
        
        # To make finding the low straights easier, we'll keep two
        # versions of our rank counts, one with the low ace included
        # and one without.
        rank_counts = [0] * 15
        rank_counts_low_ace = [0] * 15
        for c in self.cards:
            rank_counts[c.rank()] += 1
            rank_counts_low_ace[c.rank()] += 1
            if c.rank() == 14:
                rank_counts_low_ace[1] += 1

        # We'll need this for straight and for straight flush, so
        # we'll calculate it here.
        straight_high_rank = None
        num_straight_cards = 0
        for rank, count in enumerate(rank_counts_low_ace):
            if count == 1:
                num_straight_cards += 1
                if num_straight_cards >= 5:
                    straight_high_rank = rank
            elif count == 0:
                num_straight_cards = 0

        # The list of single cards is needed to fill out the ranking
        # array for several hands so we'll just do it here.
        sorted_singles = list(reversed([
                r for r, count in enumerate(rank_counts) if count == 1]))
        
                
        suit_counts = [0] * 4
        for c in self.cards:
            suit_counts[c.suit().value] += 1

        # straight flush
        try:
            suit_counts.index(5)
            if straight_high_rank:
                return [HandRank.STRAIGHT_FLUSH, straight_high_rank]
        except ValueError:
            pass
            
        # four of a kind
        try:
            four_of_a_kind_rank = rank_counts.index(4)
            other_rank = rank_counts.index(1)
            return [HandRank.FOUR_OF_A_KIND, four_of_a_kind_rank, other_rank]
        except ValueError:
            pass

        # full house
        try:
            high_rank = rank_counts.index(3)
            low_rank = rank_counts.index(2)
            return [HandRank.FULL_HOUSE, high_rank, low_rank]
        except ValueError:
            pass

        # flush
        try:
            suit_counts.index(5)
            return [HandRank.FLUSH] + sorted_singles
        except ValueError:
            pass

        # straight
        if straight_high_rank:
            return [HandRank.STRAIGHT, straight_high_rank]

        # three of a kind
        try:
            rank = rank_counts.index(3)
            return [HandRank.THREE_OF_A_KIND, rank] + sorted_singles
        except ValueError:
            pass

        # two of a kind
        try:
            low_rank = rank_counts.index(2)
            high_rank = rank_counts[low_rank + 1:].index(2) + low_rank + 1
            return [HandRank.TWO_PAIR, high_rank, low_rank] + sorted_singles
        except ValueError:
            pass

        # one pair
        try:
            rank = rank_counts.index(2)
            return [HandRank.ONE_PAIR, rank] + sorted_singles
        except ValueError:
            pass

        return [HandRank.HIGH_CARD] + sorted_singles

    def hand_rank_7(self, hole_cards):
        #ranks a 7 card hand where self has the 5 community cards and cards = two hole cards
        c_cards = self.cards
        c_cards.append(hole_cards[0])
        c_cards.append(hole_cards[1])
        #Just makes every possible combination, 7 choose 5
        allpossibles = list(itertools.combinations(c_cards,5))
        c_rank = []
        i = 0
        for c_hand in allpossibles:
            s
            if i == 0:
                c_rank = self.hand_rank(c_hand)
                continue
            else:
                test_rank = hand_rank(c_hand)
                if(compare_hrank(c_rank,test_rank) == 1):
                    c_rank = test_rank

        print(c_rank)
