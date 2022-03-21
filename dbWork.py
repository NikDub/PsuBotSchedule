import datetime
import string

import pyodbc

# import sqlite3
# connection = sqlite3.connect('data.sqlite')

connection = pyodbc.connect('Driver={PostgreSQL ODBC Driver(UNICODE)};'
                            'UID=postgres;'
                            'PWD=1;'
                            'Server=localhost;Database=Kikusha;Trusted_Connection=yes')
dbCursor = connection.cursor()


def getUserByTid(Tid):
    return dbCursor.execute(f"select * from users where userTid = {Tid}")


def getUserGroupByTid(Tid):
    return dbCursor.execute(f"select groupid from users where userTid = {Tid}")


def getUserTid():
    return dbCursor.execute(f"select userTid from users")


def getUserByStartGroup(strStart):
    return dbCursor.execute(f"select b.userTid from groups as a, users as b where b.groupid = a.id and lower(a.name) "
                            f"like '{strStart.lower()}%'")


def getUserTeacher():
    return dbCursor.execute(f"select userTid from users where rollid = 3")


def getTeacherForCheck(usertid):
    return dbCursor.execute(f"select userTid from users where rollid = 3 and usertid = {usertid}")


def getStudentForCheck(usertid):
    return dbCursor.execute(f"select userTid from users where rollid = 2 and usertid = {usertid}")


def getGroupByName(name):
    return dbCursor.execute(f"select * from groups where name = '{name}'")


def createGroup(name):
    dbCursor.execute(f"insert into groups(name) values('{name}')")
    dbCursor.commit()


def setGroupForUser(userid, groupid, subgroup):
    dbCursor.execute(f"update users set groupid={groupid}, subgroup = {subgroup} where usertid = {userid}")
    dbCursor.commit()


def createUser(data):
    dbCursor.execute(f"insert into users(rollid, groupid, fullname, username, subgroup, userTid) values(2,null, "
                     f"'{data.full_name}', '{data.username}', null, {data.id})")
    dbCursor.commit()


def getOlderGroup(userid):
    return dbCursor.execute(f"select a.name from users as b, groups as a where b.isOlder=true and a.id = b.groupid"
                            f" and b.userTid = {userid}")


def getOlderForCheck(userTid):
    return dbCursor.execute(f"select * from users where usertid = {userTid} and isolder = true")


def getOlders():
    return dbCursor.execute(f"select * from users where isolder = true")


def dataSet(userid, time, data, datetime1):
    userID = getUserByTid(userid).fetchone()[0]
    dbCursor.execute(
        f"insert into datapass(userid, time, textstr, status,  datetime) values({userID}, '{time}', '{data}', '0', '{datetime1}')")
    dbCursor.commit()


def dataGet():
    return dbCursor.execute(f"select c.name, a.time, a.datetime, a.textstr, a.id from datapass as a, users as b, "
                            f"Groups as c where a.userid=b.id and b.groupid = c.id and a.status = 0")


def selectDataRepeat(addGroup, addTime, addDate):
    return dbCursor.execute(f"select * from users as a, datapass as b, groups as c where a.id = b.userid and c.id = "
                            f"a.groupid and c.name = '{addGroup}' and b.time = '{addTime}' and b.datetime = '{addDate}'")


def setStatus(data):
    for item in data:
        dbCursor.execute(f"update datapass set status = 1 where id = {item[4]}")
    dbCursor.commit()


def LogInfo(datetime1: datetime, userid: string, command: string, msg: string):
    if command == '0':
        command = ' '
    else:
        command = command.replace('/', '')

    dbCursor.execute(
        f"insert into chatlog(userid, command, text, datetime) values({userid}, '{command}', '{msg}','{datetime1}')")
    dbCursor.commit()


def getRole(user):
    return dbCursor.execute(f"select b.name from users a, roles b where b.id=a.rollid and a.usertid = {user.id}") \
        .fetchone()


def adminSQL_setRollAsAdmin(userid):
    dbCursor.execute(f"update users set rollid = 1 where usertid = {userid} ")
    dbCursor.commit()


def adminSQL_setRollAsTeacher(userid):
    dbCursor.execute(f"update users set rollid = 3 where usertid = {userid} ")
    dbCursor.commit()


def adminSQL_setRollAsOlder(userid):
    dbCursor.execute(f"update users set isolder = true where usertid = {userid} ")
    dbCursor.commit()


def getSubByUser(usertid):
    return dbCursor.execute(f"select b.id, b.subforless, b.subforday, b.userid from users as a, subscribers as b where "
                            f"a.id = b.userid and a.usertid = {usertid}")


def createSubForUser(usertid):
    dbCursor.execute(f"insert into subscribers(subforday, subforless, userid) values(0,0,"
                     f" {getUserByTid(usertid).fetchone()[0]})")
    dbCursor.commit()


def subUserToDay(userid, set_day):
    dbCursor.execute(f"update subscribers set subforday = {set_day} where userid = {userid}")
    dbCursor.commit()


def subUserToLess(userid, set_lass, time):
    dbCursor.execute(f"update subscribers set subforless = {set_lass}, lesstime = {time} where userid = {userid}")
    dbCursor.commit()


def getUserSubsToDay():
    return dbCursor.execute(f"select a.id, a.usertid, a.rollid from users as a, subscribers as b where a.id = b.userid "
                            f"and b.subforday = true")


def getUserSubsToDayNow(userTid):
    return dbCursor.execute(f"select a.id, a.usertid, a.rollid from users as a where a.usertid = {userTid}")


def getUserSubsToLess():
    return dbCursor.execute(f"select a.id, a.usertid, a.rollid from users as a, subscribers as b where a.id = b.userid "
                            f"and b.subforless = true")


def getScheduleToDay(userid, day, week):
    return dbCursor.execute(f"select distinct f.name, g.name, g.housing, d.timestart, d.timestop, b.lesstime "
                            f" from users as a, Schedules as c, LessonsTime as d, WeekColors as e, Subjects as f, "
                            f" Rooms as g, Days as h, subscribers as b"
                            f" where a.groupid = c.groupid "
                            f" and b.userid = a.id"
                            f" and c.dayid = h.id "
                            f" and c.lessonstimeid = d.id "
                            f" and c.roomid = g.id and  "
                            f" c.subjectnameid = f.id "
                            f" and c.week_colorid = e.id "
                            f" and (cast(a.subgroup as int) = c.subgroup or c.subgroup = 0) "
                            f" and a.id = {userid} "
                            f" and h.id = {day} "
                            f" and (e.id = {week} or e.id = 3) "
                            f" order by d.timestart").fetchall()


def getScheduleToDayNow(userid, day, week):
    return dbCursor.execute(f"select distinct f.name, g.name, g.housing, d.timestart, d.timestop "
                            f" from users as a, Schedules as c, LessonsTime as d, WeekColors as e, Subjects as f, "
                            f" Rooms as g, Days as h"
                            f" where a.groupid = c.groupid "
                            f" and c.dayid = h.id "
                            f" and c.lessonstimeid = d.id "
                            f" and c.roomid = g.id and  "
                            f" c.subjectnameid = f.id "
                            f" and c.week_colorid = e.id "
                            f" and (cast(a.subgroup as int) = c.subgroup or c.subgroup = 0) "
                            f" and a.id = {userid} "
                            f" and h.id = {day} "
                            f" and (e.id = {week} or e.id = 3) "
                            f" order by d.timestart").fetchall()


def getScheduleToDayForTeach(userid, day, week):
    return dbCursor.execute(f"select distinct f.name, g.name, g.housing, d.timestart, d.timestop, b.lesstime, "
                            f"a.name, c.subgroup, a.id "
                            f"from Schedules as c, LessonsTime as d, WeekColors as e, Subjects as f, Rooms as g, "
                            f"Days as h, subscribers as b, Groups as a "
                            f"where c.teacherid = {userid} "
                            f"and b.userid = c.teacherid "
                            f"and a.id = c.groupid "
                            f"and c.dayid = h.id "
                            f"and c.lessonstimeid = d.id "
                            f"and c.roomid = g.id "
                            f"and c.subjectnameid = f.id "
                            f"and c.week_colorid = e.id "
                            f"and h.id = {day} "
                            f"and (e.id = {week} or e.id = 3) order by d.timestart").fetchall()


def getScheduleToDayForTeachNow(userid, day, week):
    return dbCursor.execute(f"select distinct f.name, g.name, g.housing, d.timestart, d.timestop, a.name, c.subgroup, "
                            f"a.id "
                            f"from Schedules as c, LessonsTime as d, WeekColors as e, Subjects as f, Rooms as g, "
                            f"Days as h, Groups as a "
                            f"where c.teacherid = {userid} "
                            f"and a.id = c.groupid "
                            f"and c.dayid = h.id "
                            f"and c.lessonstimeid = d.id "
                            f"and c.roomid = g.id "
                            f"and c.subjectnameid = f.id "
                            f"and c.week_colorid = e.id "
                            f"and h.id = {day} "
                            f"and (e.id = {week} or e.id = 3) order by d.timestart").fetchall()


def getWeekNumberByUser(userid):
    return dbCursor.execute(f"select c.weekstartnumber "
                            f"from users as a, Groups as b, WeekStart as c "
                            f"where a.groupid = b.id and b.id = c.groupid and a.id = {userid}").fetchone()


def getWeekNumberByGroup(groupid):
    return dbCursor.execute(f"select weekstartnumber "
                            f"from WeekStart "
                            f"where groupid = {groupid}").fetchone()


def getScheduleByTeacher(str, day, week):
    return dbCursor.execute(f"select distinct f.name, g.name, g.housing, d.timestart, d.timestop, a.name, c.subgroup, "
                            f"a.id "
                            f"from Schedules as c, LessonsTime as d, WeekColors as e, Subjects as f, Rooms as g, "
                            f"Days as h, Groups as a, users as b, Teachers as t "
                            f"where "
                            f"c.teacherid = b.id "
                            f"and t.id = b.id "
                            f"and t.name LIKE '{str}%' "
                            f"and a.id = c.groupid "
                            f"and c.dayid = h.id "
                            f"and c.lessonstimeid = d.id "
                            f"and c.roomid = g.id "
                            f"and c.subjectnameid = f.id "
                            f"and c.week_colorid = e.id "
                            f"and h.id = {day} "
                            f"and (e.id = {week} or e.id = 3) order by d.timestart").fetchall()


def getScheduleByGroup(str, day, week):
    return dbCursor.execute(f"select distinct f.name, g.name, g.housing, d.timestart, d.timestop, a.name, c.subgroup, "
                            f"a.id "
                            f"from Groups as a, Schedules as c, LessonsTime as d, WeekColors as e, Subjects as f, "
                            f"Rooms as g, Days as h "
                            f"where "
                            f"a.name Like '{str}%' "
                            f"and a.id = c.groupid "
                            f"and c.dayid = h.id "
                            f"and c.lessonstimeid = d.id "
                            f"and c.roomid = g.id "
                            f"and c.subjectnameid = f.id "
                            f"and c.week_colorid = e.id "
                            f"and h.id =  {day} "
                            f"and (e.id = {week} or e.id = 3) order by d.timestart")


def getDayName(id):
    return dbCursor.execute(f"select name from days where id = {id}").fetchone()


def getTeacherByName(name):
    return dbCursor.execute(f"select name from teachers where name like '{name}%'").fetchone()


def getGroupByNameForSend(name):
    return dbCursor.execute(f"select name from groups where name like '{name}%'").fetchone()
