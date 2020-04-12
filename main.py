#MAIN
import sys
import random
import deck
import cards
from PyQt5 import QtGui, QtCore
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
#from PyQt5.QtGui import QImage, QPalette, QBrush, QPixmap
from PyQt5.QtCore import *
from itertools import combinations


#These are the widgets which will end up displaying all our cards.
#We delete all these everytime a new hand is dealt
global_c_count = 0
card_widgets = []

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


def best_player():
  return plyr_ranks.index(max(plyr_ranks))


def deal():
	#print("Made it here!")
	print(deck.deal_one())

def deal_all_hole_cards(MainWindow):
  global global_c_count
  for x in range(9):
    card_one = deck.deal_one()
    card_two = deck.deal_one()
    print(card_one)
    print(card_two)
    card_widgets.append(QLabel(MainWindow))
    card1im = QPixmap("Images/Cards/"+str(card_one)+".png")
    card_widgets[global_c_count].setPixmap(card1im)
    card_widgets[global_c_count].setGeometry(all_plyr_coords[x][0],all_plyr_coords[x][1],72,96)
    card_widgets[global_c_count].show()
    global_c_count += 1;
    
    card_widgets.append(QLabel(MainWindow))
    card2im = QPixmap("Images/Cards/"+str(card_two)+".png")
    card_widgets[global_c_count].setPixmap(card2im)
    card_widgets[global_c_count].setGeometry(all_plyr_coords[x][0]+36,all_plyr_coords[x][1],72,96)
    card_widgets[global_c_count].show()
    global_c_count += 1
    plyr_cards.append([card_one,card_two])
  #print(plyr_cards)

#TODO MATT FIX TO HAVE LABELS BE DYNAMIC
#Actually we won't really be using this too much right now, but still to do
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
  global global_c_count

  card_one = deck.deal_one()
  card_two = deck.deal_one()
  card_three = deck.deal_one()
  print(card_one)
  print(card_two)
  print(card_three)
  comm_cards.append(card_one)
  comm_cards.append(card_two)
  comm_cards.append(card_three)

  card_widgets.append(QLabel(MainWindow))
  card_widgets.append(QLabel(MainWindow))
  card_widgets.append(QLabel(MainWindow))
  card1im = QPixmap("Images/Cards/"+str(card_one)+".png")
  card2im = QPixmap("Images/Cards/"+str(card_two)+".png")
  card3im = QPixmap("Images/Cards/"+str(card_three)+".png")
  
  card_widgets[global_c_count].setPixmap(card1im)
  card_widgets[global_c_count].setGeometry(414,300,72,96)
  card_widgets[global_c_count].show()

  card_widgets[global_c_count+1].setPixmap(card2im)
  card_widgets[global_c_count+1].setGeometry(489,300,72,96)
  card_widgets[global_c_count+1].show()

  card_widgets[global_c_count+2].setPixmap(card3im)
  card_widgets[global_c_count+2].setGeometry(564,300,72,96)
  card_widgets[global_c_count+2].show()
  global_c_count += 3

def deal_turn_card(MainWindow):
  global global_c_count
  card_one = deck.deal_one()
  print(card_one)
  comm_cards.append(card_one)

  card_widgets.append(QLabel(MainWindow))
  card1im = QPixmap("Images/Cards/"+str(card_one)+".png")
  card_widgets[global_c_count].setPixmap(card1im)
  card_widgets[global_c_count].setGeometry(639,300,72,96)
  card_widgets[global_c_count].show()
  global_c_count += 1

def deal_river_card(MainWindow):
  global global_c_count
  card_one = deck.deal_one()
  print(card_one)
  comm_cards.append(card_one)

  card_widgets.append(QLabel(MainWindow))
  card1im = QPixmap("Images/Cards/"+str(card_one)+".png")
  card_widgets[global_c_count].setPixmap(card1im)
  card_widgets[global_c_count].setGeometry(714,300,72,96)
  card_widgets[global_c_count].show()
  global_c_count += 1

  comm_hand = cards.PlayerCards(comm_cards)
  for x in plyr_cards:
    this_rank = cards.PlayerCards(x).combine(comm_hand).hand_rank()
    plyr_ranks.append(this_rank)
    print(this_rank)

  best_plyr = best_player()

  card_widgets.append(QLabel(MainWindow))
  starim = QPixmap("Images/Gold-Star.png")
  card_widgets[global_c_count].setPixmap(starim)
  card_widgets[global_c_count].setGeometry(all_plyr_coords[best_plyr][0],all_plyr_coords[best_plyr][1]-105,100,100)
  print("Player: " + str(best_plyr + 1))
  card_widgets[global_c_count].show()
  global_c_count += 1

def reset_cards(MainWindow):
  #reshuffle deck obviously and remove card images
  global global_c_count
  global_c_count = 0
  deck.shuffle()
  for x in card_widgets:
    x.hide()
    x.destroy()
  print("here1")
  print(card_widgets)
  print("here2")
  card_widgets.clear()
  comm_cards.clear()
  plyr_ranks.clear()
  plyr_cards.clear()
  print(card_widgets)

  

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
