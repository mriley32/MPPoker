import sys
from PIL import Image


if __name__ == "__main__":
	im = Image.open('../Images/Cards.png')
	im.show()

	our_deck = ["Ac" ,"2c","3c","4c","5c","6c","7c","8c","9c","Tc","Jc","Qc","Kc",
				"As" ,"2s","3s","4s","5s","6s","7s","8s","9s","Ts","Js","Qs","Ks",
				"Ah" ,"2h","3h","4h","5h","6h","7h","8h","9h","Th","Jh","Qh","Kh",
				"Ad" ,"2d","3d","4d","5d","6d","7d","8d","9d","Td","Jd","Qd","Kd"];

	#im1 = im.crop((1,1,72,96))
	#im1.show()
	#im.save('../Images/bs-test.png','PNG')

	for x in range(52):
		#Cards are 72 pix wide, 96 pix tall
		# 1 pix between cards in columns, 2 pix between cards in rowa
		# 1 pix of space between image edge and card as well.
		left = ((x % 13) * 73) + 1
		upper = 1 + (x // 13) * 98
		right = left + 72
		lower = upper + 96
		single_card = im.crop((left,upper,right,lower))
		single_card.save("../Images/Cards/"+our_deck[x]+".png")