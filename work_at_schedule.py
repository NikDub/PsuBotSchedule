import asyncio
import datetime

from help import sendScheduleDay, sendScheduleLess
from pygsheetsApi import pygsheetsWrite


async def RequestAtTime():
    print(datetime.datetime.now().strftime('%H:%M:%S'))
    pygsheetsWrite()


async def RequestSendDay():
    print(datetime.datetime.now().strftime('%H:%M:%S'))
    await sendScheduleDay(1)


async def scheduleStart():

    while True:
        hours = int(datetime.datetime.now().time().strftime("%H"))
        minutes = int(datetime.datetime.now().time().strftime("%M"))
        second = int(datetime.datetime.now().time().strftime("%S"))
        if hours == 11 and minutes == 00 and second == 00:
            await RequestAtTime()
        if hours == 20 and minutes == 00 and second == 00:
            await RequestAtTime()
        if hours == 20 and minutes == 00 and second == 00:
            await RequestSendDay()

        if second % 1 == 0:
            await sendScheduleLess()

        await asyncio.sleep(1)
