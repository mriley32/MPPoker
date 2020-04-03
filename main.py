#MAIN
import sys
import random
import deck
from PyQt5 import QtGui, QtCore
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
#from PyQt5.QtGui import QImage, QPalette, QBrush, QPixmap
from PyQt5.QtCore import *


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

deck = deck.Deck()
deck.shuffle()

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

  labelc1 = QLabel(MainWindow)
  card1im = QPixmap("Images/Cards/"+str(card_one)+".png")
  labelc1.setPixmap(card1im)
  labelc1.setGeometry(639,300,72,96)
  labelc1.show()

def deal_river_card(MainWindow):
  card_one = deck.deal_one()
  print(card_one)
  labelc1 = QLabel(MainWindow)
  card1im = QPixmap("Images/Cards/"+str(card_one)+".png")
  labelc1.setPixmap(card1im)
  labelc1.setGeometry(714,300,72,96)
  labelc1.show()

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
