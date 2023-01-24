import time
from datetime import datetime
from threading import Thread
import configparser
import db

print("-------------------------------\n\n daytimehandler \n\n ---------------------------")

data = configparser.ConfigParser()
data.read("setting.ini", encoding='utf-8')

def is00AM():
    limitResetHour = int(data['prefs']['dayLimitsResetTime'].split(":")[0])
    limitResetMinute = int(data['prefs']['dayLimitsResetTime'].split(":")[1])
    while True:
        curHour, curMinute = int(datetime.now().hour), int(datetime.now().minute)
        if curHour == limitResetHour and curMinute == limitResetMinute:
            db.resetDayLimit()
            print(f'{datetime.now()} dailylimit reset')
            time.sleep(72000)
        else:
            time.sleep(30)


timecheckThread = Thread(target=is00AM)
timecheckThread.start()