#include<curl/curl.h>
#include<stdio.h>
#include<stdlib.h>
#include<string>
#include<iostream>
#include<time.h>
#include<pthread.h>
#include<thread>
#include <unistd.h>
using namespace std;
typedef struct Bid_and_Ask{
    double bid, bid_Volume;
    double ask, ask_Volume;
}Bid_and_Ask;

class myCURL{
    public:
        // Variables
        CURL *curl;
        string result;
        Bid_and_Ask *B_and_A;
        // Functions
        myCURL(string &URL, size_t (*func)(void*, size_t, size_t, string*)){
            curl = curl_easy_init();
            if (!curl){
                fprintf(stderr, "init fail\n");
            }
            curl_easy_setopt(curl, CURLOPT_URL, URL.c_str());
            curl_easy_setopt(curl, CURLOPT_WRITEFUNCTION, func);
            curl_easy_setopt(curl, CURLOPT_WRITEDATA, &result);
            curl_easy_setopt(curl, CURLOPT_SSL_VERIFYPEER, false);
            curl_easy_setopt(curl, CURLOPT_ENCODING, "gzip");
            B_and_A = (Bid_and_Ask *)malloc(sizeof(Bid_and_Ask));
        }
        void get_bid_and_ask();
};

void myCURL::get_bid_and_ask(){
    int bid_off, bid_len;
    int ask_off, ask_len;

    CURLcode perform_result = curl_easy_perform(curl);
    if (perform_result != CURLE_OK){
        cout << "perform fail." << endl;
    }
    bid_off = result.find("bids\":[[") + 8; // 8 it the length of bids":[[
    bid_len = result.substr(bid_off).find("]");

    ask_off = result.find("asks\":[[") + 8; // 8 it the length of "bids\":[["
    ask_len = result.substr(ask_off).find("]");

    string bid_str = result.substr(bid_off, bid_len);
    string ask_str = result.substr(ask_off, ask_len);
    int bid_middle = bid_str.find(",");
    int ask_middle = ask_str.find(",");

    string bid, bidVolume;
    string ask, askVolume;
    bid = bid_str.substr(1, bid_middle - 2); bidVolume = bid_str.substr(bid_middle + 2, bid_str.length() - bid_middle - 3);
    ask = ask_str.substr(1, ask_middle - 2); askVolume = ask_str.substr(ask_middle + 2, ask_str.length() - ask_middle - 3);

    // cout << bid << ' ' << bidVolume << ' ' << ask << ' ' << askVolume << endl;
    B_and_A->bid = atof(bid.c_str());
    B_and_A->bid_Volume = atof(bidVolume.c_str());
    B_and_A->ask = atof(ask.c_str());
    B_and_A->ask_Volume= atof(askVolume.c_str());

    return;
}

size_t curl_cb( void *content, size_t size, size_t nmemb, string *buffer ) {	
    // cout << "call back is called" << endl;
	buffer->append((char*)content, size*nmemb);
	return size*nmemb;
}

void handle_curl(myCURL &curl){
    while (true){
        curl.get_bid_and_ask();
    }
    return;
}

// string api = "7chcOVGdbCgsrfkvAiP5rSJl1omPylJWV5TlbF2nbm7Fd0HbpgiMCuftxVxeGfIf";
// string secret = "1JAhH6u4jI2jtlfEZohcWFeRX9DQkgIw5wWOx5ENxA15vC1DbDLHA5MLCO13rkYA";
int main(){
    string URL_1 = "https://api.binance.com/api/v3/depth?symbol=BTCUSDT&limit=100";
    string URL_2 = "https://api.binance.com/api/v3/depth?symbol=ETHUSDT&limit=100";
    string URL_3 = "https://api.binance.com/api/v3/depth?symbol=ETHBTC&limit=100";
    
    myCURL pair_1(URL_1, &curl_cb);
    myCURL pair_2(URL_2, &curl_cb);
    myCURL pair_3(URL_3, &curl_cb);
    // pair_1.myCURL_handle();

    thread thread_pair_1 (handle_curl, ref(pair_1));
    thread thread_pair_2 (handle_curl, ref(pair_2));
    thread thread_pair_3 (handle_curl, ref(pair_3));
    double trading_fee = 0.001;
    sleep(1);
    // while (thread_pair_1.joinable() && thread_pair_2.joinable() && thread_pair_3.joinable()){
    while (true){
        if (1 / pair_1.B_and_A->ask * 1 / pair_3.B_and_A->ask * pair_2.B_and_A->bid > (1 + trading_fee) * (1 + trading_fee) * (1 + trading_fee)){
            cout << "buy BTC/USDT -> buy ETH/BTC -> sell ETH/USDT" << " :profit: " << 1 / pair_1.B_and_A->ask * 1 / pair_3.B_and_A->ask * pair_2.B_and_A->bid - (1 + trading_fee) * (1 + trading_fee) * (1 + trading_fee) << endl;
        }
        if (1 / pair_2.B_and_A->ask * pair_3.B_and_A->bid * pair_1.B_and_A->bid > (1 + trading_fee) * (1 + trading_fee) * (1 + trading_fee)){
            cout << "buy ETH/USDT -> sell ETH/BTC -> sell BTC/USDT" << " :profit: " << 1 / pair_2.B_and_A->ask * pair_3.B_and_A->bid * pair_1.B_and_A->bid - (1 + trading_fee) * (1 + trading_fee) * (1 + trading_fee) << endl;
        }
    }

    thread_pair_1.join();
    thread_pair_2.join();
    thread_pair_3.join();

    curl_easy_cleanup(pair_1.curl);
    curl_easy_cleanup(pair_2.curl);
    curl_easy_cleanup(pair_3.curl);
    return 0;
}