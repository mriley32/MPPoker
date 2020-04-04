#MAIN
import sys
import random
import deck
import hand
from PyQt5 import QtGui, QtCore
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
#from PyQt5.QtGui import QImage, QPalette, QBrush, QPixmap
from PyQt5.QtCore import *
from itertools import combinations


#These are the widgets which will end up displaying all our cards.
global_c_count = 0

plyr1 = [564,700]
plyr2 = [300,600]
plyr3 = [820,600]
plyr4 = [115,355]
plyr5 = [200,150]
plyr6 = [900,150]
plyr7 = [975,355]
plyr8 = [684,50]
plyr9 = [444,50]
all_plyr_coords = [plyr1,plyr2,plyr3,plyr4,plyr5,plyr6,plyr7,plyr8,plyr9]

plyr_cards = []
comm_cards = []
plyr_ranks = []

deck = deck.Deck()
deck.shuffle()

def hand_rank_7(c_hand, hole_cards):
#ranks a 7 card hand where self has the 5 community cards and cards = two hole cards
  #print(hole_cards)
  comm_cards = c_hand.copy()
  comm_cards.append(hole_cards[0])
  comm_cards.append(hole_cards[1])
  #Just makes every possible combination, 7 choose 5
  allpossibles = list(combinations(comm_cards,5))
  c_rank = []
  i = 0
  for c in allpossibles:
    this_hand = hand.Hand(list(c))
    #print(str(this_hand))
    if i == 0:
      c_rank = this_hand.hand_rank()
      i = 1
      continue
    else:
      test_rank = this_hand.hand_rank()
      if(hand.compare_hrank(c_rank,test_rank) == 1):
        c_rank = test_rank

  print(c_rank)
  return c_rank

def best_player():
  #Just looks at all 9 players hand ranks and returns which one is best
  ans = 8
  c_rank = plyr_ranks[8]
  for x in range(8):
    new_rank = plyr_ranks[x]
    if(hand.compare_hrank(c_rank,new_rank) == 1):
      c_rank = new_rank
      ans = x
  #print(c_rank)
  return ans


def deal():
	#print("Made it here!")
	print(deck.deal_one())

def deal_all_hole_cards(MainWindow):
  for x in range(9):
    card_one = deck.deal_one()
    card_two = deck.deal_one()
    print(card_one)
    print(card_two)
    labelc1 = QLabel(MainWindow)
    labelc2 = QLabel(MainWindow)
    card1im = QPixmap("Images/Cards/"+str(card_one)+".png")
    card2im = QPixmap("Images/Cards/"+str(card_two)+".png")
    labelc1.setPixmap(card1im)
    labelc2.setPixmap(card2im)

    labelc1.setGeometry(all_plyr_coords[x][0],all_plyr_coords[x][1],72,96)
    labelc2.setGeometry(all_plyr_coords[x][0]+36,all_plyr_coords[x][1],72,96)

    labelc1.show()
    labelc2.show()
    plyr_cards.append([card_one,card_two])
  #print(plyr_cards)

def deal_hole_cards(MainWindow, plyr_coords):
  card_one = deck.deal_one()
  card_two = deck.deal_one()
  print(card_one)
  print(card_two)

  labelc1 = QLabel(MainWindow)
  labelc2 = QLabel(MainWindow)
  card1im = QPixmap("Images/Cards/"+str(card_one)+".png")
  card2im = QPixmap("Images/Cards/"+str(card_two)+".png")

  labelc1.setPixmap(card1im)
  #labelc1.move(600,700)
  labelc1.setGeometry(plyr_coords[0],plyr_coords[1],72,96)
  labelc1.show()

  labelc2.setPixmap(card2im)
  #labelc2.move(600,700)
  labelc2.setGeometry(plyr_coords[0]+36,plyr_coords[1],72,96)
  labelc2.show()

def deal_flop_cards(MainWindow):
  card_one = deck.deal_one()
  card_two = deck.deal_one()
  card_three = deck.deal_one()
  print(card_one)
  print(card_two)
  print(card_three)
  comm_cards.append(card_one)
  comm_cards.append(card_two)
  comm_cards.append(card_three)

  labelc1 = QLabel(MainWindow)
  labelc2 = QLabel(MainWindow)
  labelc3 = QLabel(MainWindow)
  card1im = QPixmap("Images/Cards/"+str(card_one)+".png")
  card2im = QPixmap("Images/Cards/"+str(card_two)+".png")
  card3im = QPixmap("Images/Cards/"+str(card_three)+".png")
  
  labelc1.setPixmap(card1im)
  #labelc1.move(600,700)
  labelc1.setGeometry(414,300,72,96)
  labelc1.show()

  labelc2.setPixmap(card2im)
  #labelc2.move(600,700)
  labelc2.setGeometry(489,300,72,96)
  labelc2.show()

  labelc3.setPixmap(card3im)
  #labelc2.move(600,700)
  labelc3.setGeometry(564,300,72,96)
  labelc3.show()

def deal_turn_card(MainWindow):
  card_one = deck.deal_one()
  print(card_one)
  comm_cards.append(card_one)

  labelc1 = QLabel(MainWindow)
  card1im = QPixmap("Images/Cards/"+str(card_one)+".png")
  labelc1.setPixmap(card1im)
  labelc1.setGeometry(639,300,72,96)
  labelc1.show()

def deal_river_card(MainWindow):
  card_one = deck.deal_one()
  print(card_one)
  comm_cards.append(card_one)

  labelc1 = QLabel(MainWindow)
  card1im = QPixmap("Images/Cards/"+str(card_one)+".png")
  labelc1.setPixmap(card1im)
  labelc1.setGeometry(714,300,72,96)
  labelc1.show()

  #comm_hand = hand.Hand(comm_cards)
  for x in plyr_cards:
    this_rank = hand_rank_7(comm_cards,x)
    plyr_ranks.append(this_rank)
    print(this_rank)

  best_plyr = best_player()

  starlabel = QLabel(MainWindow)
  starim = QPixmap("Images/Gold-Star.png")
  starlabel.setPixmap(starim)
  starlabel.setGeometry(all_plyr_coords[best_plyr][0],all_plyr_coords[best_plyr][1]-105,100,100)
  print("Player: " + str(best_plyr + 1))
  starlabel.show()

def reset_cards(MainWindow):
  labels = MainWindow.findchildren()
  print("here1")
  print(labels)

class MainWindow(QMainWindow):
  def __init__(self):
    QMainWindow.__init__(self)
    self.setWindowTitle("Matt and Pat Poker")
    self.setGeometry(100,100,1200,800)
    oImage = QImage("Images/Basic.png")
    #oImage = QImage("Cards.png")
    sImage = oImage.scaled(QSize(1200,800))
    palette = QPalette()
    palette.setBrush(10,QBrush(sImage))
    self.setPalette(palette)

    deal_button = QPushButton('Deal', self)
    deal_button.clicked.connect(deal)
    deal_button.resize(120,75)
    deal_button.move(4,725)

    deal_all = QPushButton('Deal All', self)
    deal_all.clicked.connect(lambda: deal_all_hole_cards(self))
    deal_all.resize(120,75)
    deal_all.move(124,725)

    deal_hole = QPushButton('Deal Hole Cards', self)
    deal_hole.clicked.connect(lambda: deal_hole_cards(self,plyr4))
    deal_hole.resize(120,75)
    deal_hole.move(4,650)

    deal_flop = QPushButton('Deal Flop Cards', self)
    deal_flop.clicked.connect(lambda: deal_flop_cards(self))
    deal_flop.resize(120,75)
    deal_flop.move(4,575)

    deal_turn = QPushButton('Deal Turn Card', self)
    deal_turn.clicked.connect(lambda: deal_turn_card(self))
    deal_turn.resize(120,75)
    deal_turn.move(4,500)

    deal_river = QPushButton('Deal River Card', self)
    deal_river.clicked.connect(lambda: deal_river_card(self))
    deal_river.resize(120,75)
    deal_river.move(4,425)

    reset = QPushButton('Reset', self)
    reset.clicked.connect(lambda: reset_cards(self))
    reset.resize(120,75)
    reset.move(4,350)
    #deal_button.show()
    self.show()

if __name__ == "__main__":
  app = QApplication([])

  #label = QLabel('Hello World!')
  #label.show()
  #window = QWidget()
  #layout = QVBoxLayout()
  #layout.addWidget(QPushButton('Top'))
  #layout.addWidget(QPushButton('Bottom'))
  #window.setLayout(layout)
  #window.show()

  #deck = deck()
  #print(deck.our_deck[0])
  #while(1):
  #  print(random.randint(0,51))
  oMainWindow = MainWindow()
  app.exec_()
