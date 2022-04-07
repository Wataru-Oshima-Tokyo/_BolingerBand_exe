import csv
import pandas as pd
import math
import datetime
import psycopg2
import constVariables,sendEmailtoTheUser

class WriteDBAndReport():
    def __init__(self):
        self.email = sendEmailtoTheUser.Email()
        self.now = datetime.datetime.now()
        self.todays_date = str(self.now.strftime("%Y%m%d")) 

    def get_connection(self):
        return psycopg2.connect(
            host = constVariables.CVAL.host,
            database = constVariables.CVAL.database,
            user = constVariables.CVAL.user,
            password = constVariables.CVAL.password,
            port = constVariables.CVAL.port)

    def initial_connection(self):
        self.now = datetime.datetime.now()
        self.todays_date = str(self.now.strftime("%Y%m%d")) 
        self.conn = self.get_connection()
        self.cur = self.conn.cursor()

    def connection_close(self):
        self.cur.close()
        self.conn.close()


    def reportResult(self, content):
        title = "The cumulative result"
        self.email.main(content, title)

    def readDatafromresultDBandShowTheRateOfWin(self):
        self.initial_connection()
        self.cur.execute('SELECT * FROM percent')
        totalWin =0
        totalGame = 0
        for row in self.cur:
            win =0
            draw = 99999
            try:
                win = float(row[3])
            except:
                win = -1
            try:
                draw = float(row[5])
            except:
                pass
            try :
                lose = float(row[4])
            except:
                lose =-1
            if win == 3.0:
                totalWin +=1
                totalGame +=1
            elif win ==1:
                totalWin +=1
                totalGame +=1
            elif draw == 0:
                pass
            elif lose == -3.0:
                totalGame +=1
            else:
                totalGame +=1
        try:
            rateOfWin = (totalWin/totalGame)*100
        except:
            rateOfWin = 0
        msg = "So far you have tried " + str(totalGame) + " times and won " +str(totalWin) +" times.\nSo your rate of win is " + str(rateOfWin) + "%."
        print(msg)
        self.connection_close()
        self.reportResult(msg)

    def writeResult(self,rate):
        self.initial_connection()
        rate = float(rate)
        current_time = 'h' + self.now.strftime("%H") 
        try:
            self.cur.execute('CREATE TABLE percent(id SERIAL NOT NULL, date text, time text, win text, lose text, draw text, PRIMARY KEY (id))')
        except:
            self.conn.rollback()
            pass
        if(rate >0):
            try:
                self.cur.execute('INSERT INTO percent(date, time, win) VALUES(%s,%s,%s)',(self.todays_date,current_time,rate))
            except:
                self.conn.rollback()
            pass
        elif(rate<0):
            try:
                self.cur.execute('INSERT INTO percent(date, time, lose) VALUES(%s,%s,%s)',(self.todays_date,current_time,rate))
            except:
                self.conn.rollback()
            pass
        else:
            try:
                self.cur.execute('INSERT INTO percent(date, time, draw) VALUES(%s,%s,%s)',(self.todays_date,current_time,rate))
            except:
                self.conn.rollback()
            pass
        self.conn.commit()
        self.cur.execute('SELECT * FROM percent')
        print(self.cur.fetchall())
        self.connection_close()

if __name__ == "__main__":
    wrd = WriteDBAndReport()
