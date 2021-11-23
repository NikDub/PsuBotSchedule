import datetime
import time
import schedule
from pygsheetsApi import pygsheetsWrite


def ReqestAtTime():
    print(datetime.datetime.now().strftime('%H:%M:%S'))
    pygsheetsWrite()


def scheduleStart():
    # срабатывает в 11:00 ежедневно, служит для отправки посещения первых пар
    schedule.every().day.at("11:00").do(ReqestAtTime)
    # срабатывает в 20:00 ежедневно, служит для сбора статистики за день
    schedule.every().day.at("20:00").do(ReqestAtTime)

    while True:
        schedule.run_pending()
        time.sleep(20)
