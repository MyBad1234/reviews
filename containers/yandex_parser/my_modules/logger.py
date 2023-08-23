import datetime

def errorLog(text):
    file = open(file="errors.log", mode="a+", encoding="utf-8")
    file.write(str(datetime.datetime.now().strftime("%d.%m.%Y %H:%M:%S"))+": "+text+"\n")
    file.close()

def parseLog(text):
    file = open(file="parse.log", mode="a+", encoding="utf-8")
    file.write(str(datetime.datetime.now().strftime("%d.%m.%Y %H:%M:%S"))+": "+text+"\n")
    file.close()