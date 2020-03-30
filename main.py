#MAIN
import sys
import random
import deck
from PyQt5.QtWidgets import *
from PyQt5.QtGui import QImage, QPalette, QBrush
from PyQt5.QtCore import *
from PyQt5 import QtGui, QtCore

deck = deck.Deck()

def deal():
	#print("Made it here!")
	print(deck.deal_one())

class MainWindow(QMainWindow):
  def __init__(self):
    QMainWindow.__init__(self)
    self.setWindowTitle("Matt and Pat Poker")
    self.setGeometry(100,100,1200,800)
    oImage = QImage("Basic.png")
    #oImage = QImage("Cards.png")
    sImage = oImage.scaled(QSize(1200,800))
    palette = QPalette()
    palette.setBrush(10,QBrush(sImage))
    self.setPalette(palette)

    deal_button = QPushButton('Deal', self)
    deal_button.clicked.connect(deal)
    deal_button.resize(120,75)
    deal_button.move(4,725)
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
