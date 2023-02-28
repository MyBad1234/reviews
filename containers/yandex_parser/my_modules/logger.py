import datetime

def errorLog(text):
    file = open(file="./data/logs/errors.log", mode="a+", encoding="utf-8")
    file.write(str(datetime.datetime.now().strftime("%d.%m.%Y %H:%M:%S"))+": "+text+"\n")
    file.close()

def parseLog(text):
    file = open(file="./data/logs/parse.log", mode="a+", encoding="utf-8")
    file.write(str(datetime.datetime.now().strftime("%d.%m.%Y %H:%M:%S"))+": "+text+"\n")
    file.close()