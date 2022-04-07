
import bolinger_band, constVariables, decision,sendEmailtoTheUser,WriteDBAndReport
import datetime
from time import time, sleep

class Main():
    def __init__(self,):
        self.bb = bolinger_band.Bolinger_band()
        self.dm = decision.Decision()
        self.db = WriteDBAndReport.WriteDBAndReport()
        self.now = datetime.datetime.utcnow()
        self.todays_date = str(self.now.strftime("%Y%m%d")) 

    def cycle(self):
        selfDestruction = 0
        lower = 0;
        order = False
        start = False
        total = 0 
        win = 0
        while selfDestruction < 86000:
            timerStart = time()
            self.now = datetime.datetime.utcnow() 
            selftime=[]
            selftime.append(int(self.now.strftime("%H")))
            selftime.append(int(self.now.strftime("%M")))
            selftime.append(int(self.now.strftime("%S")))
            if (int(selftime[0]) == 0 or int(selftime[0]) == 8 or int(selftime[0]) == 16)  and (int(selftime[1]) == 0 and int(selftime[2]) <5):
                if start:
                    self.recordData()                
                start = False 
                order = False
                repeat = 2
                while repeat>0:
                    self.bb = bolinger_band.Bolinger_band()
                    try:
                        self.bb.initialize()
                        self.bb.cumulativeResult()
                        self.bb.makeCSVfiles()
                        self.bband  = self.bb.bolinger_band() 
                        lower = float(self.bband['lower'][len(self.bband)-1]) 
                        self.dm = decision.Decision() 
                        print("My current balance is " + str(self.dm.orderUnits))
                        print("The target price is " + str(lower))
                        print("The current price is " + str(self.bb.currentPrice))
                        lowEnough =float(self.bb.currentPrice) -.05
                        lowEnough = round(lowEnough, 3) 
                        if (lowEnough > lower):    
                            self.dm.limitOrder(lower)  
                            order = True
                            repeat = 0
                        else:
                            print("The current sitaion is not a good timing to use bolinger band method")
                            print("The target price should be lower than " + str(lowEnough))
                            repeat -=1;
                            sleep(1800)
                    except :
                        repeat = -1
                        print("It did not return valid values")
                        pass
                sleep(10)

            if order:               
                self.dm.checkIfTraded()
                if self.dm.traded and not start: 
                    print("Started the deal")
                    start = True
                    order = False

            if start:
                if self.dm.checkIfClosed(): 
                    tdr = self.dm.tdr
                    if tdr >0:
                        result = 3
                    elif tdr <0:
                        result = -3
                    else:
                        result = 0
                    self.db.writeResult(result)
                    self.db.readDatafromresultDBandShowTheRateOfWin()
                    start = False


            sleep(1)
            elapsedTime = time() -timerStart
            selfDestruction += int(elapsedTime)
            if selfDestruction%600==0:
                for i in range(len(selftime)):
                    if i != len(selftime)-1:
                        print(str(selftime[i]) + ":" ,end="")
                    else:
                        print(str(selftime[i]))
                print("cumulative time is " + str(selfDestruction))
                if(order):
                    print("Pending")
                elif(start):
                    print(self.dm.tdr)
                    print("not decided yet")
        self.recordData()
        
    def recordData(self):
        self.dm.closeOrder() 
        tdr = float(self.dm.tdr)
        if tdr >0:
            result = 1
        elif tdr <0:
            result = -1
        else:
            result = 0
        self.db.writeResult(result)
        self.dm.tdr = 0
        self.db.readDatafromresultDBandShowTheRateOfWin()



if __name__ == '__main__':
    ma = Main()
    whatDate = ma.now.strftime("%A")
    print(whatDate)
    if(whatDate == "Saturday" or whatDate == "Sunday"):
        sleep(3600)
        pass
    else:
        ma.cycle()
    
