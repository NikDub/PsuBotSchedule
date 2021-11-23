# import sqlite3
import threading
from work_at_schedule import scheduleStart
from aiogram import *
from help import *
from pygsheetsApi import *

bot = Bot(token="1965454446:AAHxZEz1xwDGs0AUDMzt3ik6dYx36e_2BPA")
dp = Dispatcher(bot)


# conn = sqlite3.connect("Bot_DB.db")


@dp.message_handler(commands=['start'])
async def send_start(msg: types.Message):
    print(msg.from_user.full_name + "\n" + msg.text + "\n")
    await msg.answer(f'Я бот. Приятно познакомиться, {msg.from_user.full_name}')


@dp.message_handler(commands=['help'])
async def send_help(msg: types.Message):
    print(msg.from_user.full_name + "\n" + msg.text + "\n")
    await msg.answer(f'Принимаются сообщения следующего вида(у - если причина уважительная): \n'
                     f'\t/visit\n'
                     f'\tИванов\n'
                     f'\tПетров у\n'
                     f'\t. . . . . . . . . . . . . . . . . . . . .\n'
                     f'\tСидоров\n')


@dp.message_handler(commands=['visit'])
async def send_visit(msg: types.Message):
    print(f"{msg.from_user.full_name} {msg.from_user.username}\n{msg.text}\n")

    fileWithNameGroup = open("Data/name by group.txt", "r", 256, "utf-8")
    elderByGroup = fileWithNameGroup.readlines()
    fileWithNameGroup.close()

    group = ""
    for elder in elderByGroup:
        if elder.lower().find(msg.from_user.username.lower()) != -1:
            group = elder.replace("\n", "").split()[1]
    if group == "":
        await msg.answer(f'Вас нет в базе старост, вы не можете отправлять данные об отсутствующих')
        return

    timeMSG = msg.date.strftime("%H:%M")
    if timeInRange("09:00", timeMSG, "18:20"):
        await msg.answer('Сейчас вы не можете отправить данные об отсутствующих, данные принимаются с 9:00 по 18:20')
        return

    date = datetime.datetime.now().strftime("%d.%m.%Y")
    if checkFileToRepeat(addGroup=group, addDate=date, addTime=timeMSG):
        await msg.answer('Вы уже отправляли данные об отстутсвующих на этой паре')
        return

    message = msg.text.splitlines()
    students_to_print = "\n".join(sorted(message[1:]))
    if len(message) == 1:
        return await msg.answer("Вы отправили пустую команду или не соблюдаете правильность написания сообщения(/help)")
    dateStartPair = timeParse(timeMSG)
    await msg.answer(f'Получены следующие данные:\n'
                     f'Группа - {group}\n'
                     f'Время отправки - {timeMSG}\n'
                     f'Время начала пары -{dateStartPair}\n'
                     f'Дата - {date}\n'
                     f"Отсутвующие - \n{students_to_print}\n")

    with open('Data/data.txt', "a", 256, "utf-8") as file:
        file.write(
            f'{group}\n{timeMSG}\n{date}\n{students_to_print}\n|\n')


# регистрация новых старост
@dp.message_handler(commands=['registration'])
async def send_registration(msg: types.Message):
    if IsAdminCheck(msg):
        print(f"/registration {msg.from_user.username} {msg.text.upper().split()[1]} {msg.from_user.full_name}\n")

        await msg.answer(f"Вы были зарегестрированы как староста группы {msg.text.upper().split()[1]}")

        with open('name by group.txt', "a", 256, "utf-8") as file:
            file.write(
                f'{msg.from_user.username} {msg.text.upper().split()[1]} {msg.from_user.full_name}\n')
    else:
        await msg.reply("У вас нет доступа к данному запросу")


@dp.message_handler(commands=['write'])
async def send_write(msg: types.Message):
    if IsAdminCheck(msg):
        await msg.answer("Запись данных в таблицу началась ▶️")
        pygsheetsWrite()
        await msg.reply("Данные были записаны в таблицу ⏹")
    else:
        await msg.reply("У вас нет доступа к данному запросу")


async def set_default_commands(dp):
    await dp.bot.set_my_commands([
        types.BotCommand("start", "Команда для начала работы с ботом"),
        types.BotCommand("help", "Описание основных команд бота"),
        types.BotCommand("visit", "Команда, позволяющая отправить данные о посещении"),
        types.BotCommand("registration",
                         "Команда в данный момент не доступна, позволяющая регистрироваться как староста группы"),
    ])


@dp.message_handler(content_types=['text'])
async def get_text_messages(msg: types.Message):
    if msg.text.lower() == 'привет':
        await msg.answer('Привет!')
    elif msg.text.lower() == "охаё":
        await msg.answer("Коницивааааа!🥰")
    else:
        await msg.answer('Такой команды я еще не изучил😞')


if __name__ == '__main__':
    threading.Thread(target=scheduleStart).start()
    executor.start_polling(dp, on_startup=set_default_commands)
