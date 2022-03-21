# -*- coding: utf-8 -*-
import asyncio
import re

from bot_init import *
from help import *
from pygsheetsApi import *
from work_at_schedule import scheduleStart

loop = asyncio.get_event_loop()
dispatcher = Dispatcher(bot, loop=loop)
adminUserNik2Dub = 451589191


@dispatcher.message_handler(commands=['start'])
async def send_start(msg: types.Message):
    await Log(msg)
    await msg.answer(f'Я бот. Приятно познакомиться, {msg.from_user.full_name}')


@dispatcher.message_handler(commands=['help'])
async def send_help(msg: types.Message):
    await Log(msg)

    await msg.answer(f"💬/subscribe_day - команда для подписки на ежедневную рассылку расписания занятий (в 20:00) "
                     f"на следующий день.\n"
                     f"Для отписки используйте команду повторно.")

    await msg.answer(f"💬'/subscribe_less Х' - команда для получения уведомления о следующей паре за Х минут до "
                     f"её начала.\n"
                     f"Для отписки используйте команду повторно.")

    await msg.answer(f"💬/schedule_now - команда для получения расписание прямо сейчас.")
    await msg.answer(f"💬/schedule_tomorrow - команда для получения расписание прямо сейчас на следующий день.")
    await msg.answer(f"💬'/schedule_teacher x y z' - команда для получения расписание преподавателя.\n"
                     f"x - День недели(1-7)\n"
                     f"y - Неделя(1 - белая, 2 - зеленая)\n"
                     f"z - Фамилия преподавателя(Если нужно добавьте имя через пробел)\n"
                     f"Например:\n"
                     f"/schedule_teacher 1 1 Скуковская Александра\n"
                     f"/schedule_teacher 4 2 Дьякова")
    await msg.answer(f"💬'/schedule_group x y z' - команда для получения расписание группы.\n"
                     f"x - День недели(1-7)\n"
                     f"y - Неделя(1 - белая, 2 - зеленая)\n"
                     f"z - Название группы\n"
                     f"Например:\n"
                     f"/schedule_group 1 1 20-МС\n"
                     f"/schedule_group 4 2 19-ИТ-3")

    if IsAdminCheck(msg) or isStudent(msg.from_user.id):
        await msg.answer("💬/registration - команда, позволяющая регистрироваться как участник группы с указанием"
                         " подгруппы.\n"
                         "Например:\n\n"
                         "/registration 20-ИТ-1 1\n\n"
                         "/registration 20-МС 2")

    if IsAdminCheck(msg) or IsTeacher(msg.from_user.id):
        await msg.answer("💬/notify - команда для рассылки уведомлений.\n"
                         "Для отправки уведомления преподавателям напишите на второй строке t, всем - all. "
                         "Для того, чтобы отправить уведомление конкретной группе или потоку укажите название "
                         "группы/групп или потока/потоков.\n"
                         "Например:\n"
                         "'20', '20-ит', '20-ит-1' или же перечень групп/паттернов - '20-ит 21-вс 19-мс 21-ит-1'\n "
                         "На третей строке пишется текст объявления\n"
                         "Например:\n\n"
                         "/notify\n"
                         "20-ИТ 19 18-ит-2\n"
                         "Завтра в 13:50 встреча в актовом зале!\n")

        await msg.answer(f"💬/write - команда для переноса данных о посещении в онлайн таблицу")

    if IsAdminCheck(msg) or IsOlder(msg.from_user.id):
        await msg.answer("Принимаются сообщения следующего вида (у - пропуск по уважительной причине): \n\n"
                         "\t💬/visit\n"
                         "\tИванов\n"
                         "\tПетров у\n"
                         "\t. . . . . . . . . . . . . . . . . . . . .\n"
                         "\tСидоров\n")


@dispatcher.message_handler(commands=['visit'])
async def send_visit(msg: types.Message):
    await Log(msg)

    if not IsOlder(msg.from_user.id):
        await msg.answer(f'Вас нет в базе старост, поэтому вы не можете отправлять данные об отсутствующих!')
        return

    group = getOlderGroup(msg.from_user.id).fetchone()

    timeMSG = msg.date.strftime("%H:%M")
    if timeInRange("09:00", timeMSG, "18:20"):
        await msg.answer('Сейчас вы не можете отправить данные об отсутствующих, данные принимаются с 9:00 по 18:20!')
        return

    date = datetime.datetime.now().strftime("%d.%m.%Y")
    if checkFileToRepeat(addGroup=group, addDate=date, addTime=timeMSG):
        await msg.answer("Вы уже отправляли данные об отстутсвующих на этой паре!")
        return

    message = msg.text.splitlines()
    students_to_print = "\n".join(sorted(message[1:]))
    if len(message) == 1:
        await msg.reply('Ваше сообщение некорректно!(/help)')

    dateStartPair = timeParse(timeMSG)
    dataSet(msg.from_user.id, timeMSG, students_to_print, date)

    await msg.answer(f'Получены следующие данные:\n'
                     f'Группа - {group}\n'
                     f'Время отправки - {timeMSG}\n'
                     f'Время начала пары -{dateStartPair}\n'
                     f'Дата - {date}\n'
                     f"Отсутвующие - \n{students_to_print}\n")


@dispatcher.message_handler(commands=['registration'])
async def send_registration(msg: types.Message):
    await Log(msg)
    if not isStudent(msg.from_user.id):
        await msg.answer(f'Регистрацию необходимо проходить только студентам!')
        return

    # noinspection PyBroadException
    try:
        if len(msg.text.upper().split()) == 3:
            groupname = msg.text.upper().split()[1]
            subgroup = int(msg.text.upper().split()[2])
            test = re.match(r'\d{2}-[а-яА-Я]{2,3}(-\d)?', groupname.strip())
            if test and test.regs[0][1] == len(groupname.strip()) and (subgroup == 1 or subgroup == 2):
                groupIs = getGroupByName(groupname)
                if groupIs.rowcount == 0:
                    createGroup(groupname)
                groupIs = getGroupByName(groupname).fetchone()

                setGroupForUser(msg.from_user.id, groupIs[0], subgroup)
                await msg.answer(f'Вы были зарегестрированы как участник группы {groupname} подгруппа {subgroup}.')
                return
        await msg.reply('Ваше сообщение некорректно!(/help)')
    except BaseException:
        await msg.reply('Ваше сообщение некорректно!(/help)')


@dispatcher.message_handler(commands=['write'])
async def send_write(msg: types.Message):
    await Log(msg)
    if IsAdminCheck(msg) or IsTeacher(msg.from_user.id):
        await msg.answer("Запись данных в таблицу начата ▶️")
        pygsheetsWrite()
        await msg.reply("Данные были записаны в таблицу ⏹")
    else:
        await msg.reply("У вас нет доступа к данной команде!")


@dispatcher.message_handler(commands=['notify'])
async def send_notify(msg: types.Message):
    await Log(msg)
    if IsAdminCheck(msg) or IsTeacher(msg.from_user.id):
        # noinspection PyBroadException
        try:
            strArray = msg.text.splitlines()
            strgourps = strArray[1].split()
            if len(strArray) >= 3:
                if strArray[1].lower() == 'all':
                    for item in getUserTid().fetchall():
                        await bot.send_message(item[0], " ".join(strArray[2::]) + f"\n@{msg.from_user.username}")
                elif strArray[1].lower() == 't':
                    for item in getUserTeacher().fetchall():
                        await bot.send_message(item[0], " ".join(strArray[2::]) + f"\n@{msg.from_user.username}")
                elif len(strgourps) > 1:
                    for groupI in strgourps:
                        for item in getUserByStartGroup(groupI).fetchall():
                            await bot.send_message(item[0], " ".join(strArray[2::]) + f"\n@{msg.from_user.username}")
                else:
                    for item in getUserByStartGroup(strArray[1]).fetchall():
                        await bot.send_message(item[0], " ".join(strArray[2::]) + f"\n@{msg.from_user.username}")
            else:
                await msg.reply('Ваше сообщение некорректно!(/help)')

        except BaseException:
            await msg.reply('Ваше сообщение некорректно!(/help)')

    else:
        await msg.reply("У вас нет доступа к данной команде!")


@dispatcher.message_handler(commands=['subscribe_day'])
async def subscribe_day(msg: types.Message):
    await Log(msg)

    if getUserGroupByTid(msg.from_user.id).fetchone()[0] is None and isStudent(msg.from_user.id):
        await msg.answer("Необходимо пройти регистрацию (/registration)!")
        return

    if subToDay(msg.from_user.id):
        await msg.answer("Подписка на ежедневную рассылку расписания оформлена.")
    else:
        await msg.answer("Подписка на ежедневную рассылку расписания отменена.")


@dispatcher.message_handler(commands=['subscribe_less'])
async def subscribe_less(msg: types.Message):
    await Log(msg)

    if getUserGroupByTid(msg.from_user.id).fetchone()[0] is None and isStudent(msg.from_user.id):
        await msg.answer("Необходимо пройти регистрацию (/registration)!")
        return

    # noinspection PyBroadException
    try:
        time = msg.text.split()[1]
        if subToLess(msg.from_user.id, time):
            await msg.answer(f"Подписка на уведомление о паре за {time} минут до начала оформлена.")
        else:
            await msg.answer("Подписка на уведомление о паре отменена.")
    except BaseException:
        await msg.reply('Ваше сообщение некорректно!(/help)')


@dispatcher.message_handler(commands=['schedule_now'])
async def getNowSchedule(msg: types.Message):
    await Log(msg)
    await sendScheduleDayNow(0, msg.from_user.id)


@dispatcher.message_handler(commands=['schedule_tomorrow'])
async def getNowSchedule(msg: types.Message):
    await Log(msg)
    await sendScheduleDayNow(1, msg.from_user.id)


@dispatcher.message_handler(commands=['schedule_teacher'])
async def getTeacherSchedule(msg: types.Message):
    await Log(msg)
    try:
        strParse = msg.text.split()
        if len(strParse) >= 4:
            await sendScheduleByTeacher(strParse[3:], strParse[1], msg.from_user.id, int(strParse[2]))
        else:
            await msg.reply('Ваше сообщение некорректно!(/help)')
    except BaseException:
        await msg.reply('Ваше сообщение некорректно!(/help)')


@dispatcher.message_handler(commands=['schedule_group'])
async def getGroupSchedule(msg: types.Message):
    await Log(msg)
    try:
        strParse = msg.text.split()
        if len(strParse) == 4:
            await sendScheduleByGroup(strParse[3].upper(), strParse[1], msg.from_user.id, int(strParse[2]))
        else:
            await msg.reply('Ваше сообщение некорректно!(/help)')
    except BaseException:
        await msg.reply('Ваше сообщение некорректно!(/help)')


@dispatcher.message_handler(content_types=['text'])
async def get_text_messages(msg: types.Message):
    await Log(msg)
    if msg.text.lower() == 'привет':
        await msg.answer('Привет!')
    elif msg.text.lower() == "охаё":
        await msg.answer("Коницивааааа!🥰")
    elif msg.text.lower() == "аниме":
        await msg.answer("Для дебилов!👌")
    elif msg.text.lower() == "как дела?":
        await msg.answer("лучше чем у тебя😜")
    else:
        await msg.answer('Такой команды я еще не изучил😞')


async def Log(msg):
    # noinspection PyBroadException
    try:
        print(f'{msg.date}  {msg.from_user.username} {msg.from_user.full_name} {msg.text}')
    except Exception:
        await bot.send_message(adminUserNik2Dub, msg.text + "\n" + msg.from_user.id.__str__()+"\n"+msg.from_user.username+"\n"+msg.from_user.full_name)
        print(f'{msg.date}  {msg.from_user.username} {msg.from_user.full_name}')

    userTid = getUserByTid(msg.from_user.id).fetchone()
    if userTid is None:
        await admin_set_role(msg.from_user)
        createUser(msg.from_user)
    userTid = getUserByTid(msg.from_user.id).fetchone()

    if msg.text.split()[0].startswith('/'):
        if len(msg.text.split()) > 1:
            LogInfo(msg.date.strftime("%Y-%m-%d %I:%M:%S %p"), userTid[0], msg.text.split()[0],
                    " ".join(msg.text.split()[1::]))
        else:
            LogInfo(msg.date.strftime("%Y-%m-%d %I:%M:%S %p"), userTid[0], msg.text, "")
    else:
        LogInfo(msg.date.strftime("%Y-%m-%d %I:%M:%S %p"), userTid[0], "0", msg.text)


async def admin_set_role(user):
    keyboard = types.InlineKeyboardMarkup(resize_keyboard=True)
    keyboard.add(types.InlineKeyboardButton(text="Администратор", callback_data="set_admin"))
    keyboard.add(types.InlineKeyboardButton(text="Преподаватель", callback_data="set_teacher"))
    keyboard.add(types.InlineKeyboardButton(text="Староста", callback_data="set_older"))
    await bot.send_message(adminUserNik2Dub, f"\n{user.id} {user.username} {user.full_name}", reply_markup=keyboard)


@dispatcher.callback_query_handler(text="set_admin")
async def set_admin(call: types.CallbackQuery):
    adminSQL_setRollAsAdmin(call.message.text.split()[0])
    await call.message.answer(call.message.text + ' \n<b>сделали админом</b>', parse_mode=types.ParseMode.HTML)


@dispatcher.callback_query_handler(text="set_teacher")
async def set_teacher(call: types.CallbackQuery):
    adminSQL_setRollAsTeacher(call.message.text.split()[0])
    await call.message.answer(call.message.text + ' \n<b>сделали преподователем</b>', parse_mode=types.ParseMode.HTML)


@dispatcher.callback_query_handler(text="set_older")
async def set_older(call: types.CallbackQuery):
    adminSQL_setRollAsOlder(call.message.text.split()[0])
    await call.message.answer(call.message.text + ' \n<b>сделали старостой</b>', parse_mode=types.ParseMode.HTML)


async def set_default_commands(dp: Dispatcher):
    await dp.bot.set_my_commands([
        types.BotCommand("start", '🟩 Начало работы с ботом'),
        types.BotCommand("help", "🟩 Описание основных команд бота"),
        types.BotCommand("registration", "🟩 Регистрация"),
        types.BotCommand("subscribe_day", "🟩 Ежедневная подписка на расписание"),
        types.BotCommand("subscribe_less", "🟩 Подписка на уведомление перед парой"),
        types.BotCommand("schedule_now", "🟩 Расписание на сегодня"),
        types.BotCommand("schedule_tomorrow", "🟩 Расписание на завтра"),
        types.BotCommand("schedule_teacher", "🟩 Расписание преподавателя"),
        types.BotCommand("schedule_group", "🟩 Расписание группы"),
        types.BotCommand("visit", '🟨 Отправка данных о посещении'),
        types.BotCommand("write", "🟧 Запись данных в онлайн таблицу"),
        types.BotCommand("notify", "🟧 Рассылка сообщений")
    ])

    asyncio.create_task(scheduleStart())

if __name__ == '__main__':
    executor.start_polling(dispatcher, on_startup=set_default_commands)
