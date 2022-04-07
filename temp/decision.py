import datetime
import requests
from time import sleep
import re
import pandas as pd
import math 
import os
import json
from oandapyV20 import API
from oandapyV20.exceptions import V20Error
from oandapyV20.endpoints.pricing import PricingStream
import oandapyV20.endpoints.orders as orders
import oandapyV20.endpoints.positions as positions
import oandapyV20.endpoints.accounts as accounts
import oandapyV20.endpoints.trades as trades
import constVariables, sendEmailtoTheUser

class Decision():
    def __init__(self):
        self.now = datetime.datetime.utcnow()
        self.access_token = constVariables.CVAL.access_token
        self.accountID = constVariables.CVAL.accountID
        self.api = API(access_token=self.access_token, environment="practice")
        self.r = accounts.AccountSummary(self.accountID)
        self.acc = self.api.request(self.r)
        self.orderUnits = self.acc['account']['balance']
        self.cancelHours = 8 
        self.leverage = 25
        self.orderId =''
        self.traded = False
        self.tdr = 0
        self.tradeId=''
        self.email = sendEmailtoTheUser.Email()
        API_URL =  "https://api-fxpractice.oanda.com"  
        self.url = API_URL + "/v3/accounts/%s/orders" % str(self.accountID)
        self.headers = {
                    "Content-Type" : "application/json", 
                    "Authorization" : "Bearer " + self.access_token
                }  
        balance = 0
        LOST = 1
        flag = True

    def limitOrder(self, target):
        try:
            orderUnits = float(self.orderUnits)
            orderUnits = math.floor(orderUnits)
        except:
            orderUnits = 1
        price = float(target)
        price = round(price, 3) 
        if(price !=0):
            Pip_location = -2
            TP_pips = 30 
            SL_pips = 30 
            orderUnits = orderUnits*self.leverage
            TP_distance = round(price + TP_pips * (10**Pip_location),3)
            SL_distance = round(price - SL_pips * (10**Pip_location),3)
            cancelTime = self.now+ datetime.timedelta(hours = self.cancelHours)
            cancelTime = self.timeModified(cancelTime)
            print("canceltime should be " +str(cancelTime))
            typeOfOrder = "LIMIT"
            data_Market = {
                            "order": {
                                    "units": str(orderUnits),
                                    "price": str(price),
                                    "instrument": "USD_JPY",
                                    "timeInForce": "GTD",
                                    "gtdTime":str(cancelTime),
                                    "type": typeOfOrder,
                                    "positionFill": "DEFAULT",
                                    "takeProfitOnFill" : {
                                        "price": str(TP_distance),
                                        "timeInForce": "GTD",
                                        "gtdTime":str(cancelTime),
                                        }, 
                                    "stopLossOnFill" : {
                                        "price": str(SL_distance),
                                        "timeInForce": "GTD",
                                        "gtdTime":str(cancelTime),
                                        }   
                                    }
                            }
            
            data = json.dumps(data_Market)
            try:

                Response_Body = requests.post(self.url, headers=self.headers, data=data)

                Response_Body.raise_for_status()
                print("注文が確定しました")
                print(json.dumps(Response_Body.json(), indent=2))
                print("オーダーIDは以下です")
                self.orderId = json.dumps(Response_Body.json()['orderCreateTransaction']['id'])
                self.orderId = self.orderId.strip('"')
                print(self.orderId)

            except Exception as e:
                    if "Response_Body" in locals(): 
                            print("Status Error from Server(raise) : %s" %Response_Body.text)
                    
                    print("エラーが発生しました。\nError(e) : %s" %e)


    def checkIfTraded(self):
        try:
            r = trades.OpenTrades(self.accountID)
            check = self.api.request(r)
            self.tradeId = str(check['trades'][0]['id'])
            print("TradeID は以下です\n" + self.tradeId)
            self.traded = True
        except:
            self.traded = False

    def checkIfClosed(self):
        try:
            tr = trades.TradeDetails(accountID=self.accountID, tradeID=self.tradeId)
            trade = self.api.request(tr)
            self.tdr = float(trade['trade']['realizedPL'])
            if self.tdr >0:
                return True
            else:
                return False
        except:
            return False

    def closeOrder(self):
        try:
            r = trades.TradeClose(self.accountID ,tradeID=self.tradeId)
            self.api.request(r)
            print("約定が確定しました")
        except:
            print("すでに約定しています")
        sleep(2)
        content =""
        try:
            r = trades.TradeDetails(self.accountID ,tradeID=self.tradeId)
            tradeDetail = self.api.request(r)
            self.tdr =tradeDetail["trade"]["realizedPL"]
            print(self.tdr)
            content = "you got " + str(self.tdr) + " for " + str(self.tradeId)
        except:
            print("failed to get the realizedPL")
            self.tdr = 0
            content = "We failed to fetch the realiszed PL  for " + str(self.tradeId)
        self.email.main("About realizedPL", content)
        

    def cancelOrder(self):
        pass

    def timeModified(self, date):
        date = str(date)
        choppedStr = date.split(" ")
        ChoppedStr2 = choppedStr[1].split(".")
        ChoppedStr3 = ChoppedStr2[0].split(":")
        ChopppedStr4 = ChoppedStr3[0]+":00:00"
        modifiedTime = choppedStr[0] +"T"+ChopppedStr4 + ".000000000Z"
        return modifiedTime

if __name__ == "__main__":
    order = Decision()
    order.stopOrder(112.10)
