#include <string>
#include <stdio.h>
#include <iostream>
#include <time.h>
#include <stdlib.h>
#include <vector>
#include <algorithm>
#include <stdlib.h>

using namespace std;

class Deck{
private:
	char order_list[14] = "A23456789TJQK";
	vector<int> cards_dealt;
	vector<string> our_deck;
	vector<string> MakeLinear(vector<string> hand);
public:
	Deck();
	string DealOne();//deal one random card
	vector<string> Deal5Hand(); //Deal a random 5card hand
	vector<string> Deal7Hand(); //Deal a random 7card hand
	void NewDeck();//Return all cards to deck
	bool IsStraight(vector<string> hand);//is there a straight in this hand
	bool IsFlush5C(vector<string> hand);//are these five cards a flush
	bool IsFlush(vector<string> hand);//Flush for any amount of cards, typically 7
	void PrintHand(vector<string> hand);
};

Deck::Deck(){
	srand(time(NULL));
	//*order_list = "A23456789TJQK";
	our_deck = { "Ac" ,"2c","3c","4c","5c","6c","7c","8c","9c","Tc","Jc","Qc","Kc","As","2s","3s","4s","5s","6s","7s","8s","9s","Ts","Js","Qs","Ks","Ad","2d","3d","4d","5d","6d","7d","8d","9d","Td","Jd","Qd","Kd","Ah","2h","3h","4h","5h","6h","7h","8h","9h","Th","Jh","Qh","Kh"};
}

void Deck::NewDeck(){
	cards_dealt.clear();
}

string Deck::DealOne(){
	if(cards_dealt.size() == 52){
		return "empty";
	}
	//cout << "here\n";
	bool done = false;
	string ans;
	while(!done){
	int c_index = rand() % 52;//pick a random card
		if(find(cards_dealt.begin(),cards_dealt.end(),c_index) == cards_dealt.end()){
			cards_dealt.push_back(c_index);
			done = true;
			ans = our_deck[c_index];
		}
	}
	return ans;
}

vector<string> Deck::Deal5Hand(){
	vector<string> ans;
	ans.push_back(DealOne());
	ans.push_back(DealOne());
	ans.push_back(DealOne());
	ans.push_back(DealOne());
	ans.push_back(DealOne());
	return ans;
}

vector<string> Deck::Deal7Hand(){
	vector<string> ans;
	ans.push_back(DealOne());
	ans.push_back(DealOne());
	ans.push_back(DealOne());
	ans.push_back(DealOne());
	ans.push_back(DealOne());
	ans.push_back(DealOne());
	ans.push_back(DealOne());
	return ans;
}

void Deck::PrintHand(vector<string> hand){
	for(int i = 0; i<hand.size(); i++){
		cout << hand[i];
		if(i != hand.size()-1){
			cout << "-";
		}
	}
	cout << "\n";
}

bool Deck::IsFlush5C(vector<string> hand){//Determines flush out of five cards
	char looking_for = hand[0][1];//First elements suit - 8c-9h-Jd-2c-5s would give us 'c'
	for(int i = 1; i < hand.size(); i++){
		if(hand[i][1]!=looking_for){
			return false;
		}
	}
	return true;
}

bool Deck::IsFlush(vector<string> hand){
	char d = 'd';
	char h = 'h';
	char c = 'c';
	char s = 's';

	int dcount = 0;
	int hcount = 0;
	int ccount = 0;
	int scount = 0;
	bool ans = false;

	for(int i = 0; i < hand.size(); i++){
		switch(hand[i][1]){
			case 'h':
				hcount++;
				break;
			case 'd':
				dcount++;
				break;
			case 's':
				scount++;
				break;
			case 'c':
				ccount++;
				break;
		}
		if(hcount > 4 || dcount > 4 || scount > 4 || ccount > 4){
			ans = true;
			break;
		}
	}
	return ans;
}

bool Deck::IsStraight(vector<string> hand){
//This function checks the A-5 straight, then 206, then 3-7, all the way to T-A Straight
	//int magicnum = 0; //How many cards of the straight we currently have, this hits 5, you've got it!
	char looking_for[1];
	string current_check;
	for(int i = 1; i < 11; i++){//Checking each straight starting tat A-T
		bool next_num = false;
		while(!next_num){
			for(int j = i; j < i + 5; j++){
				switch(j){
					case 1:
						*looking_for = 'A';
						break;
					case 14:
						*looking_for = 'A';
						break;
					case 13:
						*looking_for = 'K';
						break;
					case 12:
						*looking_for = 'Q';
						break;
					case 11:
						*looking_for = 'J';
						break;
					case 10:
						*looking_for = 'T';
						break;
					default:
						sprintf(looking_for,"%d",j);
				}
				//cout <<"Looking For: "<< looking_for << "\n";
				bool found = false;
				for(int k = 0; k<hand.size(); k++){
					current_check = hand[k];
					//cout<<current_check[0];
					if(current_check[0] == *looking_for){
						found = true;
						//cout << "FOUND!"<<current_check[0]<<"\n";
						continue;
					}

				}
				if(found == false){
					next_num = true;
					//magicnum = 0;
					j = i+5;
					continue;
				}
				else{
					//cout <<"INHERE\n";
					if(j == i+4){//we have found the 5th number in the straight and the previous 4
						return true;
					}
				}
			}
		}

	}
	return false;
}















