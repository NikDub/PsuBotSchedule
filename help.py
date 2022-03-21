from bot_init import bot
from dbWork import *
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


def subIsExist(usertid):
    userSub = getSubByUser(usertid).fetchone()
    if userSub is None:
        createSubForUser(usertid)

    return getSubByUser(usertid).fetchone()


def subToDay(usertid):
    userSub = subIsExist(usertid)
    if not userSub[2]:
        subUserToDay(userSub[3], 1)
        return True
    else:
        subUserToDay(userSub[3], 0)
        return False


def subToLess(usertid, time):
    userSub = subIsExist(usertid)
    if not userSub[1]:
        subUserToLess(userSub[3], 1, time)
        return True
    else:
        subUserToLess(userSub[3], 0, 0)
        return False


def checkFileToRepeat(addGroup, addTime, addDate):
    if selectDataRepeat(addGroup, addTime, addDate).fetchone() is None:
        return False
    else:
        return True


def IsAdminCheck(msg):
    if getRole(msg.from_user)[0] == "admin":
        return True
    else:
        return False


def IsOlder(usertid):
    if getOlderForCheck(usertid).fetchone() is None:
        return False
    else:
        return True


def IsTeacher(usertid):
    if getTeacherForCheck(usertid).fetchone() is None:
        return False
    else:
        return True


def isStudent(usertid):
    if getStudentForCheck(usertid).fetchone() is None:
        return False
    else:
        return True


async def sendScheduleDay(day):
    dayOfWeek = int(datetime.datetime.today().date().strftime("%w"))
    day_next = 0
    if dayOfWeek == 0:
        dayOfWeek = 7

    dayOfWeek += day

    if dayOfWeek == 8:
        dayOfWeek = 1
        day_next = 1

    weekNumber = int(datetime.datetime.today().date().strftime("%W"))
    weekNum = weekNumber

    if day_next == 1:
        weekNumber += 1

    if weekNumber % 2 == 1:
        weekNumber = 1
        text_week = "⚪️Белая неделя"
    else:
        weekNumber = 2
        text_week = "🟢 Зеленая неделя"

    tomorrow = datetime.date.today() + datetime.timedelta(days=day)

    for item in getUserSubsToDay().fetchall():
        flag = 0
        str_for_user = f"Дата: {tomorrow.strftime('%d.%m.%Y')} {text_week}"

        if item[2] == 2:
            str_for_user += f"({weekNum - getWeekNumberByUser(item[0])[0] + 1})\n\n"
            for i in getScheduleToDay(item[0], dayOfWeek, weekNumber):
                str_for_user += f"⭐️ {i[3]} - {i[4]} {i[0]} {i[1] + i[2]}\n\n"
                flag = 1
        elif item[2] == 3:
            str_for_user += f"\n\n"
            for i in getScheduleToDayForTeach(item[0], dayOfWeek, weekNumber):
                subtext = f"Подгруппа {i[7]}"
                if i[7] == 0:
                    subtext = ""

                str_for_user += f"⭐️ {i[3]} - {i[4]} {i[0]} {i[1] + i[2]} - {i[6]} {subtext} " \
                                f"({weekNum - getWeekNumberByGroup(i[8])[0] + 1})\n\n"
                flag = 1

        if flag == 1:
            await bot.send_message(item[1], str_for_user)
        elif day == 0:
            await bot.send_message(item[1], str_for_user + "На завтра расписания нет!😏")
    return


async def sendScheduleDayNow(day, usertid):
    dayOfWeek = int(datetime.datetime.today().date().strftime("%w"))
    day_next = 0
    if dayOfWeek == 0:
        dayOfWeek = 7

    dayOfWeek += day

    if dayOfWeek == 8:
        dayOfWeek = 1
        day_next = 1

    weekNumber = int(datetime.datetime.today().date().strftime("%W"))
    weekNum = weekNumber

    if day_next == 1:
        weekNumber += 1

    if weekNumber % 2 == 1:
        weekNumber = 1
        text_week = "⚪️Белая неделя"
    else:
        weekNumber = 2
        text_week = "🟢 Зеленая неделя"

    tomorrow = datetime.date.today() + datetime.timedelta(days=day)
    for item in getUserSubsToDayNow(usertid).fetchall():
        flag = 0
        str_for_user = f"Дата: {tomorrow.strftime('%d.%m.%Y')} {text_week} "
        if item[2] == 2:
            str_for_user += f"({weekNum - getWeekNumberByUser(item[0])[0] + 1})\n\n"
            for i in getScheduleToDayNow(item[0], dayOfWeek, weekNumber):
                str_for_user += f"⭐️ {i[3]} - {i[4]} {i[0]} {i[1] + i[2]}\n\n"
                flag = 1
        elif item[2] == 3:
            str_for_user += f"\n\n"
            for i in getScheduleToDayForTeachNow(item[0], dayOfWeek, weekNumber):
                subtext = f"Подгруппа {i[6]}"
                if i[6] == 0:
                    subtext = ""

                str_for_user += f"⭐️ {i[3]} - {i[4]} {i[0]} {i[1] + i[2]} - {i[5]} {subtext} " \
                                f"({weekNum - getWeekNumberByGroup(i[7])[0] + 1})\n\n"
                flag = 1

        if flag == 1:
            await bot.send_message(item[1], str_for_user)
        elif flag == 0:
            if day == 0:
                await bot.send_message(item[1], str_for_user + "На сегодня расписания нет!😏")
            elif day == 1:
                await bot.send_message(item[1], str_for_user + "На завтра расписания нет!😏")
    return


async def sendScheduleLess():
    timeNow = datetime.datetime.now().time()
    dayOfWeek = int(datetime.datetime.today().date().strftime("%w"))
    if dayOfWeek == 0:
        dayOfWeek = 7

    weekNumber = int(datetime.datetime.today().date().strftime("%W"))
    weekNum = weekNumber
    if weekNumber % 2 == 1:
        weekNumber = 1
        text_week = "⚪️Белая неделя"
    else:
        weekNumber = 2
        text_week = "🟢 Зеленая неделя"

    tomorrow = datetime.date.today()

    for item in getUserSubsToLess().fetchall():
        flag = 0
        str_for_user = f"Дата: {tomorrow.strftime('%d.%m.%Y')} {text_week}"
        if item[2] == 2:
            str_for_user += f"({weekNum - getWeekNumberByUser(item[0])[0] + 1})\n\n"

            for i in getScheduleToDay(item[0], dayOfWeek, weekNumber):
                time_interval = datetime.datetime.strptime(i[3], "%H:%M:%S") - \
                                datetime.datetime.strptime(timeNow.strftime('%H:%M:%S'), "%H:%M:%S")
                time_leave = time_interval.seconds / 60
                if time_leave == i[5]:
                    str_for_user += f"⭐️ {i[3]} - {i[4]} {i[0]} {i[1] + i[2]}\n\n"
                    flag = 1
        elif item[2] == 3:
            str_for_user += f"\n\n"

            for i in getScheduleToDayForTeach(item[0], dayOfWeek, weekNumber):
                time_interval = datetime.datetime.strptime(i[3], "%H:%M:%S") - \
                                datetime.datetime.strptime(timeNow.strftime('%H:%M:%S'), "%H:%M:%S")

                time_leave = time_interval.seconds / 60
                if time_leave == i[5]:
                    subtext = f"Подгруппа {i[7]}"
                    if i[7] == 0:
                        subtext = ""

                    str_for_user += f"⭐️ {i[3]} - {i[4]} {i[0]} {i[1] + i[2]} - {i[6]} {subtext} " \
                                    f"({weekNum - getWeekNumberByGroup(i[8])[0] + 1})\n\n"
                    flag = 1
        if flag:
            await bot.send_message(item[1], str_for_user)
    return


async def sendScheduleByTeacher(str, day, usertid, week):
    str = " ".join(str)
    if week % 2 == 1:
        week = 1
        text_week = "⚪️Белая неделя"
    else:
        week = 2
        text_week = "🟢 Зеленая неделя"

    flag = 0
    str_for_user = f"{getDayName(day)[0]} {text_week} \n{getTeacherByName(str)[0]}\n\n"
    for i in getScheduleByTeacher(str, day, week):
        subtext = f"Подгруппа {i[6]}"
        if i[6] == 0:
            subtext = ""

        str_for_user += f"⭐️ {i[3]} - {i[4]} {i[0]} {i[1] + i[2]} - {i[5]} {subtext}\n\n"
        flag = 1

    if flag == 1:
        await bot.send_message(usertid, str_for_user)
    elif flag == 0:
        await bot.send_message(usertid, str_for_user + "Расписания нет!😏")


async def sendScheduleByGroup(str, day, usertid, week):
    if week % 2 == 1:
        week = 1
        text_week = "⚪️Белая неделя"
    else:
        week = 2
        text_week = "🟢 Зеленая неделя"

    flag = 0
    str_for_user = f"{getDayName(day)[0]} {text_week} \n{getGroupByNameForSend(str)[0]}\n\n"
    for i in getScheduleByGroup(str, day, week):
        subtext = f"Подгруппа {i[6]}"
        if i[6] == 0:
            subtext = ""

        str_for_user += f"⭐️ {i[3]} - {i[4]} {i[0]} {i[1] + i[2]} - {i[5]} {subtext}\n\n"
        flag = 1

    if flag == 1:
        await bot.send_message(usertid, str_for_user)
    elif flag == 0:
        await bot.send_message(usertid, str_for_user + "Расписания нет!😏")
