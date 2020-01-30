#!/usr/bin/python3.8

import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime, timedelta
import time
import argparse
import robin_stocks
from getpass import getpass
import os
from platform import system


# Scrape data from website
def stock_listGenerator(stock_table):
    stock_list = []

    for stock in range(0, len(stock_table)):
        stock_info = stock_table[stock].find_all(class_="Va(m)")
        stock_dictionary = {}
        for info in stock_info:
            if info.get("aria-label") == "% Change":
                # print('{:<20}{:<20}'.format(info.get("aria-label"), float(info.get_text()[1:-1])))
                if "," in info.get_text()[1:-1]:
                    infoNoComma = info.get_text()[1:-1].replace(",","")
                    stock_dictionary[info.get("aria-label")] = float(infoNoComma)
                else:
                    stock_dictionary[info.get("aria-label")] = float(info.get_text()[1:-1])
            else:
                # print('{:<20}{:<20}'.format(info.get("aria-label"),info.get_text()))
                stock_dictionary[info.get("aria-label")] = info.get_text()
        stock_list.append(stock_dictionary)
        # print("\n")
    return stock_list


# Store the stock list into a json file
def stock_Storage(stock_list, filepath):
    current_time = time.localtime()
    string_time = time.strftime('%d-%m-%Y', current_time)
    file_date = datetime.utcnow().strftime('%d-%m-%Y')

    with open(filepath + "Stocks"+string_time+".json", "w") as f:
        json.dump(stock_list, f, indent=4)
    f.close()


# Sort the stocks in order from highest percent change to lowest
def stock_list_sorted(stock_list):
    newlist = sorted(stock_list, key=lambda k: k['% Change'], reverse=True)
    return newlist


# Find stocks that have repeate from the day prior
def stock_repeats(minus_day_count, filepath):
    minus_days = minus_day_count
    yesterday_data = []
    today_data = []
    repeated_data = []
    old_file_date = (datetime.utcnow() - timedelta(days=minus_days)).strftime('%d-%m-%Y')
    file_date = datetime.utcnow().strftime('%d-%m-%Y')
    current_time = time.localtime()
    string_time = time.strftime('%d-%m-%Y', current_time)

    with open(filepath+"Stocks"+old_file_date+".json", "r") as f1:
        yesterday_data = json.load(f1)
    f1.close()
    with open(filepath+"Stocks"+string_time+".json", "r") as f2:
        today_data = json.load(f2)
    f2.close()
    #print(today_data)
    for new_data in today_data:
        for old_data in yesterday_data:
            if new_data["Symbol"] == old_data["Symbol"]:
                repeated_data.append(new_data)
            else:
                continue
    return repeated_data


# Gather Robinhood data on stock
def stock_Worthiness(stocks):
    stock_list = stocks
    stock_data = []  # In development
    stock_earnings = {}  # In development
    stock_eps_year = []  # In development the idea is to get the eps from the stock for last 4 quarters and make sure the p/e ratio has been increasing.
    #  Calculated by share price divide by the eps
    stock_initial_list = []
    stock_invest = []
    magic_count = 0

    for stock in stock_list:
        if float(stock['% Change']) > 4 and float(stock["Price (Intraday)"]) < 60:
            stock_initial_list.append(stock["Symbol"])

    for stock in stock_initial_list:
        stock_data.append(robin_stocks.get_stock_quote_by_symbol(stock))
        if stock not in stock_earnings:
            stock_earnings[stock] = {}

        for stock_earning in robin_stocks.get_earnings(stock):
            try:
                if int(stock_earning['year']) == 2019 or 2018:
                    if stock_earning['eps']['estimate'] != None and stock_earning['eps']['actual'] != None:
                        stock_eps = {"eps":stock_earning['eps']}
                        if stock_earning["year"] not in stock_earnings[stock]:
                            #  stock_earnings[stock] = {stock_earning["year"]:{}}
                            stock_earnings[stock][stock_earning["year"]] = {stock_earning["quarter"] : stock_eps}
                        else:
                            stock_earnings[stock][stock_earning["year"]][stock_earning["quarter"]] = stock_eps


                '''
                if int(stock_earning['year']) == 2019 or 2018:
                    stock_eps_list = [{"year": stock_earning['year'], "quarter": stock_earning['quarter'], "eps": stock_earning['eps']}]
                    stock_earnings.append()
                '''
            except TypeError:
                continue

    for stock in stock_data:
        if stock is not None:
            stock_history = robin_stocks.get_historicals(stock['symbol'], span='5year', bounds='regular')
            stock_12month_price = int(float(stock_history[-48]['close_price']))  # 48 weeks ago close_price
            stock_9month_price = int(float(stock_history[-36]['close_price']))  # 36 weeks ago close_price
            stock_6month_price = int(float(stock_history[-24]['close_price']))  # 24 weeks ago close_price
            stock_3month_price = int(float(stock_history[-12]['close_price']))  # 12 weeks ago close_price
            stock_2month_price = int(float(stock_history[-8]['close_price']))  # 8 weeks ago close_price
            stock_1month_price = int(float(stock_history[-4]['close_price']))  # 4 weeks ago close_price
            stock_rec_price = int(float(stock_history[-1]['close_price']))  # Recent close_price
            counter = 0

            try:

                if stock_1month_price > stock_3month_price and stock_rec_price > stock_6month_price:

                    if stock_earnings[stock['symbol']][2019][1]['eps']['estimate'] < stock_earnings[stock['symbol']][2019][1]['eps']['actual']:
                        counter += 1
                    
                    if stock_earnings[stock['symbol']][2019][2]['eps']['estimate'] < stock_earnings[stock['symbol']][2019][2]['eps']['actual']:
                        counter += 2
                    try:
                        if stock_earnings[stock['symbol']][2019][3]['eps']['estimate'] < stock_earnings[stock['symbol']][2019][3]['eps']['actual']:
                            counter += 3
                    except:
                        print("{} hasn't reported 3rd quarter earnings.".format(stock_earnings[stock['symbol']]))
                if counter >= 3:
                    stock_invest.append(stock['symbol'])

                    #print(stock_earnings[stock['symbol']][2019][1]['eps'][estimate] < stock_earnings[stock['symbol']][2019][1]['eps'][actual])
            except KeyError:
                continue
    f = open(input("filename: "), 'w')
    f.write(" {} ".format(stock_invest))
    '''
            if stock_recent_price > stock_12month_price and stock_recent_price > stock_6month_price and stock_recent_price > stock_1month_price:
                if stock_1month_price > stock_9month_price and stock_1month_price > stock_3month_price and stock_1month_price > stock_2month_price:
                    print(stock['symbol'])
                    #  for i in stock_earnings[stock['symbol']][2018]:
                    #      print(stock_earnings[stock['symbol']][2018][i]['eps'])
            '''

            # print(robin_stocks.get_historicals(stock['symbol'], span='5year', bounds='regular')[0]['open_price'])

    # previous_close = stock['previous_close']
    # now_price = stock['ask_price']




    # print(stock_invest)


# Invest into stocks that have repeated from the day before.
def invest_Stock(stocks):
    stocks_list = stocks
    stock_invest = []
    stock_data = []
    stock_earnings = []  # In development

    for stock in stocks_list:
        if stock['% Change'] > 4:
            stock_invest.append(stock["Symbol"])

    watchlist = robin_stocks.build_holdings()  # In development
    user_profile = robin_stocks.build_user_profile()  # In development
    print(stocks_list)
    print("\n\n")
    print(stock_invest)
    with open("./TradeHistory/"+input("Two Stock Filename: ")+".json",'w') as f:
        json.dump(stock_invest[0:2], f, indent=4)
    f.close()
        #stock_data.append(robin_stocks.get_stock_quote_by_symbol(stock))
    # print(stock_data)
    '''
    for stock in stock_data:
        # print(stock)
        try:
            start_price = float(stock['previous_close'])
            now_price = float(stock['ask_price'])
            limit_price = ((now_price - start_price)/2) + start_price
            if now_price < 75:
                for earns in robin_stocks.get_earnings(stock["symbol"]):
                    if earns["year"] == 2019 and earns["quarter"] < 4:
                        print(earns)
        except TypeError as detail:
            print(f"\033[33m{detail}\033[3m")
    '''

'''
                if float(stock_earns[0]['estimate']) < float(stock_earns[0]['actiual']):
                    print(stock_earns['symbol'])
                '''

            # robin_stocks.order_buy_limit(stock["symbol"],2, limit_price)

    # print(stock_data)


"""
    robin_stocks.login("", "")
    watchlist = robin_stocks.build_holdings()
    #thor = robin_stocks.get_earnings("UUGWF")
    upperbound = robin_stocks.get_top_movers('up')
    user_profile = robin_stocks.build_user_profile()

    with open("User_profile.json", "w") as f:
        json.dump(watchlist, f, indent=4)
        json.dump(user_profile, f, indent=4)
        json.dump(upperbound, f, indent=4)
    f.close()
    robin_stocks.logout()
"""


def invested_Stock_Storage(invested_Stocks):
    stocks = invested_Stocks


def main():
    # Command Line Arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("-r", "-read", action='store', dest='read_arg', type=str, metavar='', help="Read a file from the specified filename.")
    parser.add_argument("-d", "-minus", action='store', dest="minus_days", type=int, default=1, metavar='', help="Days ago to research from")
    args = parser.parse_args()
    read_arg = args.read_arg  # In development
    minus_days = args.minus_days
    username = input("Robinhood Username: ")
    password = getpass("Robinhood Password: ")
    filepath = os.getcwd()

    if system() == 'Linux':
        filepath = filepath + '/StockData/'
        if os.path.isdir('./StockData') == False:
            os.mkdir('./StockData')
    elif system() == 'Windows':
        filepath = filepath + '\\StockData\\'
        if os.path.isdir('.\\StockData\\') == False:
            os.mkdir('.\\StockData')

    # Gather data
    page = requests.get("https://finance.yahoo.com/gainers")
    soup = BeautifulSoup(page.content, 'html.parser')
    stocks = soup.find(id="scr-res-table")
    stock_table = stocks.find_all(class_="simpTblRow")

    stock_list = stock_listGenerator(stock_table)  # Create dictionary list of stock data
    stock_sorted_list = stock_list_sorted(stock_list)  # Sort stock data with highest being the greatest change
    stock_Storage(stock_sorted_list,filepath)  # Store the data in a json file
    stock_repeated_list = stock_repeats(minus_days,filepath)  # Dictionary list with stocks from today that also were top gainers the day before
    stock_repeated_sorted = stock_list_sorted(stock_repeated_list)  # Sort stock data with highest change being at the top

    robin_stocks.login(username, password) # Login to robinhood
    stock_good = stock_Worthiness(stock_repeated_sorted)  # Filter stocks for good quality by earnings and price history

    invested_stocks = invest_Stock(stock_repeated_sorted) # Invest into worthy stocks
    # invested_Stock_Storage(invested_stocks) # Store stocks that were brought into a json file

    # stock_Sell_Ready = stock_Sell_Ready_List() # Filter stocks from invested stock JSON or portfolio and return stocks ready to variable
    # sellstocks() # Sell stocks that were identified by stock_Sell_Ready

    robin_stocks.logout()


if __name__ == '__main__':
    main()
