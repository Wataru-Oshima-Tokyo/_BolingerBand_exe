from math import e
from os import close
import pandas as pd
import numpy as np
from time import sleep
import datetime
import requests
import sqlite3
import os
import constVariables

class Bolinger_band():
    def __init__(self):
        self.now = datetime.datetime.utcnow() 
        self.todays_date = str(self.now.strftime("%Y%m%d")) 
        self.window = 300 
        self.dbname = './files/bolinger_db.db'
        self.dfname = './files/bolinger_db.csv'
        self.access_token = constVariables.CVAL.access_token
        self.accountID = constVariables.CVAL.accountID
        self.pastDate = self.now - datetime.timedelta(hours=16) 
        self.currentPrice = 0
        
        
    def initialize(self):
        df_exists = os.path.exists(self.dfname)
        db_exists = os.path.exists(self.dbname)
        if df_exists:
            os.remove(self.dfname)
        if db_exists:
            os.remove(self.dbname)

    def cumulativeResult(self):
        pastDate_strf = self.pastDate.strftime("%Y%m%d%H")
        current_time = self.now.strftime("%Y%m%d%H")
        print(current_time)
        while pastDate_strf != current_time:
            self.getData()
            self.pastDate = self.pastDate+datetime.timedelta(hours=1)
            pastDate_strf = self.pastDate.strftime("%Y%m%d%H")

        
    def timeModified(self, date):
        date = str(date)
        choppedStr = date.split(" ")
        ChoppedStr2 = choppedStr[1].split(".")
        ChoppedStr3 = ChoppedStr2[0].split(":")
        ChopppedStr4 = ChoppedStr3[0]+":00:00"
        modifiedTime = choppedStr[0] +"T"+ChopppedStr4 + ".000000000Z"
        return modifiedTime
        
    def getData(self):
        self.datefrom = self.timeModified(self.pastDate)
        API_URL =  "https://api-fxpractice.oanda.com"
        INSTRUMENT = "USD_JPY"
        self.period = "S5"
        count =720 
        self.url = API_URL + "/v3/instruments/%s/candles?count=%s&price=M&granularity=%s&smooth=True&from=%s" % (INSTRUMENT, count, self.period,self.datefrom)

        self.headers = {
                        "Authorization" : "Bearer " + self.access_token
            }
        starttime = self.pastDate

        response = requests.get(self.url, headers=self.headers)

        Response_Body = response.json()
        i = 0
        end = 0;
        try:
            openPrice_start = float(Response_Body["candles"][0]["mid"]["o"])
            end = len(Response_Body["candles"])-1
            closePrice_end = float(Response_Body["candles"][end]["mid"]["c"])
            self.currentPrice = float(Response_Body["candles"][end]["mid"]["c"])
        except IndexError:
            print("returned no result")
            pass
        openPrices = []
        closePrices = []
        while i<end:
            prices= []
            try:
                openPrice = float(Response_Body["candles"][i]["mid"]["o"])
                closePrice = float(Response_Body["candles"][i]["mid"]["c"])
                highPrice = float(Response_Body["candles"][i]["mid"]["h"])
                lowPrice = float(Response_Body["candles"][i]["mid"]["l"])
                prices.append(openPrice)
                prices.append(highPrice)
                prices.append(lowPrice)
                prices.append(closePrice)
                now = starttime+datetime.timedelta(seconds=i*5)
                self.writeResult(now, prices)
            except e:
                print(e)
                break
            i = i+1
    


    def bolinger_band(self):
        df = pd.read_csv(self.dfname)
        df.index = pd.to_datetime(df.index)
        self.bband = pd.DataFrame()
        self.bband['time'] = df['time']
        self.bband['open'] = df['open']
        self.bband['close'] = df['close']
        self.bband['mean'] = df['close'].rolling(window=self.window).mean() 
        self.bband['std'] = df['close'].rolling(window=self.window).std()
        self.bband['upper'] = self.bband['mean'] + (self.bband['std'] * 2)
        self.bband['lower'] = self.bband['mean'] - (self.bband['std'] * 2)
        return self.bband



    def writeResult(self, todays_date, prices):
        cdate = todays_date.strftime("%y-%m-%d")
        ctime = todays_date.strftime("%H:%M%:%S")      
        conn = sqlite3.connect(self.dbname)
        cur = conn.cursor()

        try:
            cur.execute('CREATE TABLE price(date text, time text, open text, high text, low text, close text)')

        except:
            conn.rollback()

            pass

        cur.execute('INSERT INTO price(date, time, open, high, low, close) VALUES(?,?,?,?,?,?)',(str(cdate), str(ctime), prices[0], prices[1], prices[2],prices[3]))
        conn.commit()
        cur.close()

        conn.close()

    def makeCSVfiles(self):
        conn = sqlite3.connect(self.dbname)
        cur = conn.cursor()

        dfdata = pd.read_sql('SELECT * FROM price', conn)
        try:

            data = self.todays_date+"data" 
            dfdata.to_csv(self.dfname, encoding='utf_8_sig')
            print("success to convert to csv file")
        except:
            self.dfname = ""
            print("failed to convert to csv file")
        cur.close()
        conn.close()


    
    
        

if __name__ == '__main__':
    try:
        bolinger = Bolinger_band()
        bolinger.initialize()
        bolinger.cumulativeResult()
        bolinger.makeCSVfiles()

    except e:
        print(e)
        pass
    