import datetime


def timeParse(timeStr):
    if datetime.time.fromisoformat("10:25") >= datetime.time.fromisoformat(timeStr) >= datetime.time.fromisoformat(
            "09:00"):
        return "09:00"
    elif datetime.time.fromisoformat(timeStr) <= datetime.time.fromisoformat("12:15"):
        return "10:30"
    elif datetime.time.fromisoformat(timeStr) <= datetime.time.fromisoformat("13:45"):
        return "12:20"
    elif datetime.time.fromisoformat(timeStr) <= datetime.time.fromisoformat("15:25"):
        return "13:50"
    elif datetime.time.fromisoformat(timeStr) <= datetime.time.fromisoformat("16:55"):
        return "15:30"
    elif datetime.time.fromisoformat(timeStr) <= datetime.time.fromisoformat("18:15"):
        return "17:00"


def timeInRange(time1, time2, time3):
    if datetime.time.fromisoformat(
            time2) > datetime.time.fromisoformat(time3):
        return True
    if datetime.time.fromisoformat(time1) > datetime.time.fromisoformat(time2):
        return True
    return False


def checkFileToRepeat(addGroup, addTime, addDate):
    dataFile = open('Data/data.txt', "r", 256, "utf-8")
    posDataFromFile = dataFile.read()
    dataFile.close()

    if posDataFromFile == "":
        return

    for item in posDataFromFile.split("|"):
        data = item.strip().splitlines()
        if len(data) == 0:
            return False
        if addDate == data[2] and timeParse(addTime) == timeParse(timeParse(data[1])) and data[0] == addGroup:
            return True
    return False


def IsAdminCheck(msg):
    dataFile = open('Data/Admin.txt', "r", 256, "utf-8")
    posDataFromFile = dataFile.read()
    dataFile.close()
    AdminList = posDataFromFile.split("\n")
    flag = 0
    for item in AdminList:
        if item.split(" ")[0] == msg.from_user.username:
            flag = 1
    if flag == 0:
        return False
    else:
        return True
