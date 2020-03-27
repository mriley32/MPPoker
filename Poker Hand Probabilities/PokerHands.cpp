#include <string.h>
#include <stdio.h>
#include <iostream>
#include "Deck.h"
using namespace std;

int main(){
	//printf("Hello World\n");
	//string myname = "matthew\n";
	//cout << myname;
	//cout << deck[3];
	
	Deck mydeck;
	string mycard;
	vector<string> myhand;
	
	long trials = 10000;
	int straights = 0;
	int num_straights = 100;

	int flushes = 0;
	int num_flushes = 100;

	bool foundflushes = false;
	bool foundstraights = false;
	for(int i = 0; i<trials; i++){
		mydeck.NewDeck();
		myhand = mydeck.Deal7Hand();
		//mydeck.PrintHand(myhand);
		bool isitf = mydeck.IsFlush(myhand);
		bool isits = mydeck.IsStraight(myhand);
		//mydeck.PrintHand(myhand);
		//cout << isit << "\n";
		if(isitf){
			flushes++;
			cout << "FLUSH\n";
			mydeck.PrintHand(myhand);
		}
		if(isits){
			straights++;
			cout << "STRAIGHT\n";
			mydeck.PrintHand(myhand);
		}
	}
	cout <<"TRIALS : "<<trials<<"\n";
	cout << "TOTAL FLUSHES: "<<flushes<<"\n";
	cout << "TOTAL STRAIGHTS: "<<straights<<"\n";
	/*while(mycard != "empty"){
		cout << mycard << "\n";
		mycard = mydeck.DealOne();
		//cout << mycard;
	}*/
	return 0;
}