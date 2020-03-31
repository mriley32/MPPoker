#MAIN
import sys
import random
import deck
from PyQt5 import QtGui, QtCore
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
#from PyQt5.QtGui import QImage, QPalette, QBrush, QPixmap
from PyQt5.QtCore import *

deck = deck.Deck()
deck.shuffle()

def deal():
	#print("Made it here!")
	print(deck.deal_one())

def deal_hole_cards(MainWindow):
	card_one = deck.deal_one()
	card_two = deck.deal_one()
	print(card_one)
	print(card_two)

	labelc1 = QLabel(MainWindow)
	labelc2 = QLabel(MainWindow)
	card1im = QPixmap("Images/Cards/"+str(card_one)+".png")
	card2im = QPixmap("Images/Cards/"+str(card_two)+".png")
	labelc1.setPixmap(card1im)
	labelc1.move(600,700)
	labelc1.setGeometry(564,700,72,96)
	labelc1.show()

	labelc2.setPixmap(card2im)
	labelc2.move(600,700)
	labelc2.setGeometry(600,700,72,96)
	labelc2.show()
	#MainWindow.setCentralWidget(labelc1)
	#MainWindow.show()


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

    deal_hole = QPushButton('Deal Hole Cards', self)
    deal_hole.clicked.connect(lambda: deal_hole_cards(self))
    deal_hole.resize(120,75)
    deal_hole.move(4,650)
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
