# This is a main  decorator mechanism.

import telebot
import datetime
import sqlite3
from telebot import types
from req import main_func

API_TOKEN = '231161869:AAFpafehgQl9V-5f6-1KvwjPkzhbgdqDflU'
bot = telebot.TeleBot(API_TOKEN)

# первое подключение к бд
connection_first = sqlite3.connect('delivery.db')
cursor_first = connection_first.cursor()
k = cursor_first.fetchall()  # считывание строки
for i in range(len(k)):
    print(k[i][1])
connection_first.commit()
connection_first.close()


# проверяет, является ли строка, введенная пользователем, числом
def represents_int(s):
    try:
        int(s)
        return True
    except ValueError:
        return False


# остановка ввода запроса
@bot.message_handler(commands=['stopfin'])
def repeat_all_messages(message):
    connection = sqlite3.connect('users.db')
    cursor = connection.cursor()
    cursor.execute("SELECT rowid FROM users WHERE userid = " + str(message.chat.id))
    data = cursor.fetchall()
    if len(data) != 0:
        cursor.execute(
            "DELETE FROM users WHERE userid = " + str(message.chat.id))  # удаление ранее введенной юзером информации
        connection.commit()
        connection.close()
        bot.send_message(message.chat.id,
                         "Окей, мы забыли про ваш предыдущий вопрос. Можете начать снова с командой /findata")


# строковый ввод вопроса
@bot.message_handler(commands=['custom'])
def send_welcome(message):
    # подключение к бд
    connection = sqlite3.connect('users.db')
    cursor = connection.cursor()
    cursor.execute("SELECT rowid FROM users WHERE userid = " + str(message.chat.id))
    data = cursor.fetchall()

    # защита от предварительного ввода пользователем запроса во время обработки предыдущего
    if len(data) != 0:
        bot.send_message(message.chat.id,
                         "Вы уже задали нам вопрос. Сейчас мы ответим на него и вы сможете задать следующий.")
    else:
        s = message.text[8:]
        s1 = main_func(s)
        # заполнение строки запроса к бд
        s_main = "INSERT INTO users (id, userid, subject, place, year, sector, planned_or_actual) VALUES(NULL, {0}, \"{1}\", \"{2}\", \"{3}\", \"{4}\", \"{5}\")".format(
            str(message.chat.id), str(s1[0]), str(s1[1]), str(s1[2]), str(s1[3]), str(s1[4]))
        cursor.execute(s_main)
        connection.commit()
        connection.close()
        bot.send_message(message.chat.id, "Мы получили ваш запрос и скоро на него ответим")


# команда выбора региона (choose region)
@bot.message_handler(commands=['cr'])
def send_welcome(message):
    connection = sqlite3.connect('users.db')
    cursor = connection.cursor()
    cursor.execute("SELECT rowid FROM users WHERE userid = " + str(message.chat.id))
    data = cursor.fetchall()
    if len(data) != 0:
        s = str(message.text)[4:]
        print(s)
        cursor.execute("UPDATE users SET place=\"" + s + "\" WHERE userid=" + str(message.chat.id) + ";")
        connection.commit()
        connection.close()
        bot.send_message(message.chat.id, 'Спасибо! Сейчас мы сформируем ответ и отправим его вам.')
    else:
        bot.send_message(message.chat.id, "Упс! "
                                          "Эта команда имеет смысл только внутри потока комманд /findata. "
                                          "Начните с команды /findata, если хотите получить финансовые данные")


# Ввод сферы
@bot.message_handler(commands=['sub'])
def send_welcome(message):
    connection = sqlite3.connect('users.db')
    cursor = connection.cursor()
    cursor.execute("SELECT rowid FROM users WHERE userid = " + str(message.chat.id))
    data = cursor.fetchall()
    if len(data) != 0:
        s = str(message.text)
        ss = s[5:]
        print(ss)
        cursor.execute("UPDATE users SET subject=\"" + ss + "\" WHERE userid=" + str(message.chat.id) + ";")
        connection.commit()
        connection.close()
        bot.send_message(message.chat.id,
                         "Окей, осталось совсем чуть-чуть. Введите регион, о котором хотите узнать."
                         "Для этого введите команду /cr (choose region) и после нее через пробел название региона."
                         "Например, если вы хотите узнать о Ярославской области, то вам просто нужно будет написать"
                         "/cr Ярославская область. Если вы узнать информацию о России в целом, просто напишите комманду /cr")
    else:
        bot.send_message(message.chat.id, "Ой. Эта команда имеет смысл только внутри потока комманд /findata. "
                                          "Если вы хотите получить финансовые данные, то начните с команнды /findata.")


# команды старта и помощи
@bot.message_handler(commands=['help', 'start'])
def send_welcome(message):
    msg = bot.send_message(message.chat.id, 'Привет! Я bot!')


@bot.message_handler(commands=['delivery'])
def send_welcome(message):
    # print(message.chat.id)
    p = message.chat.id
    connection = sqlite3.connect('delivery.db')
    cursor = connection.cursor()
    cursor.execute('SELECT * FROM users')
    k = cursor.fetchall()
    t = True
    for i in range(len(k)):
        print(k[i][1])
        print(p)
        if (k[i][1] == p):
            t = False
            break
    if (t):
        bot.send_message(message.chat.id, 'Вы подписались на нашу рассылку!')
        s = 'INSERT INTO users (id, userid) VALUES(NULL, ' + str(p) + ')'
        cursor.execute(s)
    else:
        bot.send_message(p, "Добрейший вечерочек, а вы уже подписались на нашу рассылку. Зачем это делать еше раз ?  ")
    connection.commit()
    connection.close()


@bot.message_handler(commands=['delivery_off'])
def repeat_all_messages(message):
    bot.send_message(message.chat.id,
                     "Вы отписались от нашей рассылки. Пусть это останется на вашей совести.Но если захотите вернуться, то вы всегда сможете это сделать с помощью команды /delivery")
    connection = sqlite3.connect('delivery.db')
    cursor = connection.cursor()
    query = "DELETE FROM users WHERE userid = " + str(message.chat.id) + ";"
    cursor.execute(query)
    connection.commit()
    connection.close()


@bot.message_handler(commands=['findata'])
def repeat_all_messages(message):
    connection = sqlite3.connect('users.db')
    cursor = connection.cursor()
    cursor.execute("SELECT rowid FROM users WHERE userid = " + str(message.chat.id))
    data = cursor.fetchall()

    if len(data) != 0:

        bot.send_message(message.chat.id, " Подождите, мы еще не справились с вашей предыдущей командой. "
                                          "Давайте сначала закончим с ней. Вы всегда можете прервать работу с нашим ботом с помощью команды /stopfin")

    else:

        s = message.text[9:]
        if (s == ""):
            bot.send_message(message.chat.id,
                             "Привет! Наша система может составить финансовый  отчет по любому региону России. Для начала выберете предметную область:")
            markup = types.ReplyKeyboardMarkup()
            markup.row('доход')
            markup.row('расход')
            markup.row('дефицит')
            markup.row('долг')
            bot.send_message(message.chat.id, "Выбирайте:", reply_markup=markup)

            connection = sqlite3.connect('users.db')
            cursor = connection.cursor()
            s_main = "INSERT INTO users (id, userid, subject, place, year, sector, planned_or_actual) VALUES(NULL, " + \
                     str(message.chat.id) + ", \"" + str(0) + "\", \"" + str(0) + "\", \"" + str(0) + "\", \"" + str(
                0) + "\", \"" + str(0) + "\")"
            cursor.execute(s_main)
            connection.commit()
            connection.close()
        else:
            s1 = main_func(s)
            s_main = "INSERT INTO users (id, userid, subject, place, year, sector, planned_or_actual) VALUES(NULL, " + \
                     str(message.chat.id) + ", \"" + str(s1[0]) + "\", \"" + str(s1[1]) + "\", \"" + str(
                s1[2]) + "\", \"" + str(s1[3]) + "\", \"" + str(s1[4]) + "\")"
            cursor.execute(s_main)
            connection.commit()
            connection.close()

            bot.send_message(message.chat.id, "Мы обработали ваш запрос и сейчас на него ответим.")


@bot.message_handler(content_types=["text"])
def repeat_all_messages(message):
    print(message.text)

    markup = types.ReplyKeyboardHide()

    connection = sqlite3.connect('users.db')
    cursor = connection.cursor()
    cursor.execute("SELECT rowid FROM users WHERE userid = " + str(message.chat.id))
    data = cursor.fetchall()

    now_date = datetime.date.today()

    if represents_int(message.text) and len(data) != 0:
        i = int(message.text)
        if 1900 < i < 2016:
            cursor.execute("UPDATE users SET year=" + str(i) + " WHERE userid=" + str(message.chat.id) + ";")
            connection.commit()
            connection.close()
            bot.send_message(message.chat.id,
                             "Осталось немного. Сейчас вам нужно ввести сферу о которой вы хотите узнать."
                             " Для этого введите команду /sub (subject) и после нее через пробел название сферы."
                             "Например, если вы хотите узнать об образовании, то вам просто нужно будет написать"
                             "/sub образование. Если вы узнать информацию о бюджете в целом, просто напишите комманду /sub")
        else:
            bot.send_message(message.chat.id,
                             "Боюсь у нас нет данных за этот год. Попробуйте еще раз")

    if (
                            message.text == "доход" or message.text == "расход" or message.text == "дефицит" or message.text == "долг") and (
                len(data) != 0):
        k = message.text
        cursor.execute("UPDATE users SET subject=\"" + str(k) + "\" WHERE userid=" + str(message.chat.id) + ";")
        connection.commit()
        connection.close()
        bot.send_message(message.chat.id, "Вы выбрали " + message.text, reply_markup=markup)
        bot.send_message(message.chat.id,
                         "Ок, мы опредедились с первым пунктом. Теперь давай выберем временной промежуток:")
        markup = types.ReplyKeyboardMarkup()
        markup.row('фактические')
        markup.row('плановые')
        markup.row('текущие')
        markup.row('запланированные')
        bot.send_message(message.chat.id, "Выбирайте:", reply_markup=markup)

    if (
                            message.text == "фактические" or message.text == "плановые" or message.text == "текущие" or message.text == "запланированные") and (
                len(data) != 0):
        k = 0
        if (message.text == "фактические"):
            bot.send_message(message.chat.id,
                             "Ок. Мы можем выдать вам эту информацию по конкретному году. Вам просто нужно ввести год в формате гггг. Например 2004.")

            markup = types.ReplyKeyboardHide()
            bot.send_message(message.chat.id, "Теперь введите свой временной промежуток: ", reply_markup=markup)

        if (message.text == "плановые"):
            bot.send_message(message.chat.id,
                             "Ок. Мы можем выдать вам эту информацию по конкретному году. Вам просто нужно ввести год в формате гггг. Например 2004.")

            markup = types.ReplyKeyboardHide()
            bot.send_message(message.chat.id, "Теперь введите свой временной промежуток: ", reply_markup=markup)

        if (message.text == "текущие"):
            bot.send_message(message.chat.id, "Вы выбрали " + str(now_date.year), reply_markup=markup)
            cursor.execute(
                "UPDATE users SET year=" + str(now_date.year) + " WHERE userid=" + str(message.chat.id) + ";")
            connection.commit()
            connection.close()
            bot.send_message(message.chat.id,
                             "Осталось немного. Сейчас вам нужно ввести сферу о которой вы хотите узнать."
                             " Для этого введите команду /sub (subject) и после нее через пробел название сферы."
                             "Например, если вы хотите узнать об образовании, то вам просто нужно будет написать"
                             "/sub образование. Если вы узнать информацию о бюджете в целом, просто напишите комманду /sub")

        if (message.text == "запланированные"):
            bot.send_message(message.chat.id, "Вы выбрали " + str(now_date.year), reply_markup=markup)
            cursor.execute(
                "UPDATE users SET year=" + str(now_date.year) + " WHERE userid=" + str(message.chat.id) + ";")
            connection.commit()
            connection.close()
            bot.send_message(message.chat.id,
                             "Осталось немного. Сейчас вам нужно ввести сферу о которой вы хотите узнать."
                             " Для этого введите команду /sub (subject) и после нее через пробел название сферы."
                             "Например, если вы хотите узнать об образовании, то вам просто нужно будет написать"
                             "/sub образование. Если вы узнать информацию о бюджете в целом, просто напишите комманду /sub")


if __name__ == '__main__':
    bot.polling(none_stop=True)
