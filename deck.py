from enum import Enum
import random
import sys

class Suit(Enum):
        CLUBS = 0
        DIAMONS = 1
        HEARTS = 2
        SPADES = 3

_SUIT_STR = ["c", "d", "h", "s"]
        

                
class Card:
        def __init__(self, idx):
                self.card_idx = idx
                
        def __str__(self):
                return str(self.rank()) + _SUIT_STR[self.suit().value]

        def suit(self):
                return Suit(self.card_idx // 13)

        def rank(self):
                return (self.card_idx % 13) + 2
        

class Deck:

	def __init__(self):
		self.our_deck = ["Ac" ,"2c","3c","4c","5c","6c","7c","8c","9c","Tc","Jc","Qc","Kc",
				"As" ,"2s","3s","4s","5s","6s","7s","8s","9s","Ts","Js","Qs","Ks",
				"Ad" ,"2d","3d","4d","5d","6d","7d","8d","9d","Td","Jd","Qd","Kd",
				"Ah" ,"2h","3h","4h","5h","6h","7h","8h","9h","Th","Jh","Qh","Kh"];
		self.cards_dealt  = []
	def deal_one(self):
		done = 0;
		current_ind = random.randint(0,51)
		while(done == 0):
			if(current_ind in self.cards_dealt):
				continue
			else:
				self.cards_dealt.append(current_ind)
				print(self.cards_dealt)
				done = 1
				return self.our_deck[current_ind]



