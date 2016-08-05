import telebot
import datetime
import sqlite3
from telebot import types
from req import main_func
from req import main_place
from req import main_sector
from m2retrieving import M2Retrieving
from m3visualizing import M3Visualizing

API_TOKEN = '231161869:AAFpafehgQl9V-5f6-1KvwjPkzhbgdqDflU'
bot = telebot.TeleBot(API_TOKEN)

# первое подключение к бд
connection_first = sqlite3.connect('subscribe.db')
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
                         "Мы забыли про ваш предыдущий вопрос. Можете начать снова с командой /findata")


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
                         "Вы уже задали нам вопрос. Сейчас мы ответим на него и вы сможете задать следующий")
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
    cursor.execute("SELECT * FROM users WHERE userid = " + str(message.chat.id))
    data = cursor.fetchall()
    if len(data) != 0:
        s = str(message.text)[4:]
        if s == "":
            cursor.execute("UPDATE users SET place=\"" + "null" + "\" WHERE userid=" + str(message.chat.id) + ";")
            connection.commit()
            connection.close()
            bot.send_message(message.chat.id, 'Спасибо!')
        else:
            print(s)
            s = main_place(s)
            if (s != None):

                cursor.execute("UPDATE users SET place=\"" + s + "\" WHERE userid=" + str(message.chat.id) + ";")
                connection.commit()
                connection.close()
                bot.send_message(message.chat.id, 'Спасибо!')
            else:
                bot.send_message(message.chat.id, "Боюсь, что мы вас не поняли 😰")
    else:
        bot.send_message(message.chat.id, "Эта команда имеет смысл только внутри потока команд /findata. "
                                          "Начните с команды /findata, если хотите получить финансовые данные")

    con = sqlite3.connect('users.db')
    cursor = con.cursor()
    cursor.execute("SELECT * FROM users WHERE userid = " + str(message.chat.id))
    data = cursor.fetchall()
    con.close()
    k = 0
    for i in data:
        for i1 in i:
            #print(i1)
            if i1 == '0':
                k += 1
    if(k > 2):
        bot.send_message(message.chat.id, "Похоже, вы передали нам не всю информацию. Мы не сможем дать вам корректную информацию.")
    else:
        bot.send_message(message.chat.id, "Сейчас мы сформируем ответ и отправим его вам.")
    for i in data:
        for i1 in i:
            pass


# Ввод сферы
@bot.message_handler(commands=['thm'])
def send_welcome(message):
    connection = sqlite3.connect('users.db')
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM users WHERE userid = " + str(message.chat.id))
    data = cursor.fetchall()
    print(data)
    if len(data) != 0:
        s = str(message.text)
        ss = s[5:]
        if ss == "":
            cursor.execute("UPDATE users SET thm=\"" + "null" + "\" WHERE userid=" + str(message.chat.id) + ";")
            connection.commit()
            connection.close()
            bot.send_message(message.chat.id,
                             "Если вы хотите узнать информацию о Российской Федерации в целом, "
                             "введите /cr. Если вас интересует конкретный регион, введите /cr *название региона* "
                             "(например, /cr Московская область):")
        else:
            print(ss)
            ss = main_sector(ss)
            print(ss)
            if (ss == None):
                bot.send_message(message.chat.id, "Боюсь, что мы вас не поняли ?.Попробуйте еще раз")
            else:

                cursor.execute("UPDATE users SET subject=\"" + ss + "\" WHERE userid=" + str(message.chat.id) + ";")
                connection.commit()
                connection.close()
                bot.send_message(message.chat.id,
                                 "Если вы хотите узнать информацию о Российской Федерации в целом, "
                                 "введите /cr. Если вас интересует конкретный регион, введите /cr *название региона* "
                                 "(например, /cr Московская область):")
    else:
        bot.send_message(message.chat.id, "Ой. Эта команда имеет смысл только внутри потока комманд /findata. "
                                          "Если вы хотите получить финансовые данные, то начните с команнды /findata.")


# команда старта
@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.send_message(message.chat.id, 'Я — экспертная система OpenFinData. Я могу представить вам '
                                      'финансовый отчет о любой области за определенный год.\n'
                                      'Чтобы получить список команд, нажмите /help\n'
                                      'Чтобы сразу приступить к формированию отчета, введите /findata')


# команды старта и помощи
@bot.message_handler(commands=['help'])
def send_welcome(message):
    bot.send_message(message.chat.id, '<b>Список команд:</b>\n'
                                      '/start   — начать работу с ботом\n'
                                      '/findata — получить финансовый отчет\n'
                                      '/thmscribe — подписаться на ежедневную рассылку\n'
                                      '/unsubscribe', parse_mode='HTML')

"""
@bot.message_handler(commands=['subscribe'])
def send_welcome(message):
    # print(message.chat.id)
    p = message.chat.id
    connection = sqlite3.connect('subscribe.db')
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


@bot.message_handler(commands=['unsubscribe'])
def repeat_all_messages(message):
    bot.send_message(message.chat.id,
                     "Вы отписались от нашей рассылки. Пусть это останется на вашей совести.Но если захотите вернуться, то вы всегда сможете это сделать с помощью команды /thmscribe")
    connection = sqlite3.connect('subscribe.db')
    cursor = connection.cursor()
    query = "DELETE FROM users WHERE userid = " + str(message.chat.id) + ";"
    cursor.execute(query)
    connection.commit()
    connection.close()
"""

@bot.message_handler(commands=['findata'])
def repeat_all_messages(message):
    connection = sqlite3.connect('users.db')
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM users WHERE userid = " + str(message.chat.id))
    data = cursor.fetchall()

    if len(data) != 0:
        cursor.execute("DELETE FROM users WHERE userid = " + str(message.chat.id))  # удаление ранее введенной юзером информации
        connection.commit()
        connection.close()

    s = message.text[9:]
    if (s == ""):
        #bot.send_message(message.chat.id, "Выберите предметную область:")
        markup = types.ReplyKeyboardMarkup()
        markup.row('доходы')
        markup.row('расходы')
        markup.row('дефицит/профицит')
        bot.send_message(message.chat.id, "Выбирайте", reply_markup=markup)
        connection = sqlite3.connect('users.db')
        cursor = connection.cursor()
        s_main = "INSERT INTO users (id, userid, subject, place, year, sector, planned_or_actual, thm) VALUES(NULL, " + \
                 str(message.chat.id) + ", \"" + str(0) + "\", \"" + str(0) + "\", \"" + str(0) + "\", \"" + str(
            0) + "\", \"" + str(0) + "\", \"" + str(0) + "\")"
        cursor.execute(s_main)
        connection.commit()
        connection.close()

    else:
        s1 = main_func(s)
        s_main = "INSERT INTO users (id, userid, subject, place, year, sector, planned_or_actual) VALUES(NULL, " + \
                     str(message.chat.id) + ", \"" + str(s1[0]) + "\", \"" + str(s1[1]) + "\", \"" + str(
        s1[2]) + "\", \"" + str(s1[3]) + "\", \"" + str(s1[4]) + "\")"
        connection = sqlite3.connect("users.db")
        cursor = connection.cursor()
        cursor.execute(s_main)
        connection.commit()
        connection.close()
        s_mod2 = ""
        s_mod2 += s1[0] + "," + s1[4] + "," + "null" + "," + str(s1[2]) + "," + "null" + "," + s1[1]
        print(s_mod2)
        result = M2Retrieving.get_data(s_mod2)
        if result.status is False:
            bot.send_message(message.chat.id, result.message)
        else:
            bot.send_message(message.chat.id, "Все хорошо")
            print(result.response)
            bot.send_message(message.chat.id, "Спасибо! Сейчас мы сформируем ответ и отправим его вам.")
            file = open('result.pdf','rb')
            # TODO: отправка в чат
            # TODO: обработка строки


@bot.message_handler(content_types=["text"])
def repeat_all_messages(message):
    print(message.text)

    markup = types.ReplyKeyboardHide()

    connection = sqlite3.connect('users.db')
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM users WHERE userid = " + str(message.chat.id))
    data = cursor.fetchall()
    print(data)
    k = 0
    for i in data:
        for i1 in i:
            #print(i1)
            if i1 == '0':
                k += 1
    print(k)
    now_date = datetime.date.today()

    if represents_int(message.text) and len(data) != 0:
        i = int(message.text)
        if 2006 < i < 2016:
            cursor.execute("UPDATE users SET year=" + str(i) + " WHERE userid=" + str(message.chat.id) + ";")
            connection.commit()
            connection.close()
            bot.send_message(message.chat.id,
                             "Если вы хотите узнать информацию о бюджете в целом, введите /thm. Если вас интересует "
                             "конкретная область, введите /thm *название сферы* (например, /thm образование):")
        else:
            bot.send_message(message.chat.id,
                             "Данные за этот год отсутствуют. Повторите ввод:")

    if (message.text == "доходы" or message.text == "расходы" or message.text == "дефицит/профицит"
        or message.text == "налоговые" or message.text == "неналоговые") and (
                len(data) != 0):
        k = message.text
        if(message.text == "доходы" or message.text == "расходы" or message.text == "дефицит/профицит"):
            cursor.execute("UPDATE users SET subject=\"" + str(k) + "\" WHERE userid=" + str(message.chat.id) + ";")
            connection.commit()
            connection.close()
        if(message.text == "налоговые" or message.text == "неналоговые"):
            cursor.execute("UPDATE users SET planned_or_actual=\"" + str(k) + "\" WHERE userid=" + str(message.chat.id) + ";")
            connection.commit()
            connection.close()
        if(k == "расходы"):
            #bot.send_message(message.chat.id, "Введите тип:")
            markup = types.ReplyKeyboardMarkup()
            markup.row('фактические')
            markup.row('плановые')
            markup.row('текущие')
            markup.row('запланированные')
            bot.send_message(message.chat.id, "Выбирайте:", reply_markup=markup)
        elif(k == "дефицит/профицит" or k == "налоговые" or k == "неналоговые"):
            #bot.send_message(message.chat.id, "Введите тип:")
            markup = types.ReplyKeyboardMarkup()
            markup.row('плановые')
            markup.row('текущие')
            markup.row("null")
            bot.send_message(message.chat.id, "Выбирайте:", reply_markup=markup)
        elif(k == "доходы"):
            markup = types.ReplyKeyboardMarkup()
            markup.row('налоговые')
            markup.row('неналоговые')
            bot.send_message(message.chat.id, "Выбирайте:", reply_markup=markup)



    if (message.text == "фактические" or message.text == "плановые" or message.text == "текущие" or message.text == "запланированные" or message.text == "null") and (
                len(data) != 0):
        k = 0
        if (message.text == "фактические"):
            markup = types.ReplyKeyboardHide()
            k = message.text
            bot.send_message(message.chat.id,
                             "Введите год с 2007 по текущий в формате ГГГГ (например, 2010):", reply_markup= markup)
            cursor.execute(
                "UPDATE users SET sector=\"" + str(k) +  "\" WHERE userid=" + str(message.chat.id) + ";")
            connection.commit()
            connection.close()



        if (message.text == "плановые"):
            markup = types.ReplyKeyboardHide()
            k = message.text
            bot.send_message(message.chat.id,
                             "Введите год с 2007 по текущий в формате ГГГГ (например, 2010):", reply_markup= markup)
            cursor.execute(
                "UPDATE users SET sector=\"" + str(k) + "\" WHERE userid=" + str(message.chat.id) + ";")

            connection.commit()
            connection.close()

            markup = types.ReplyKeyboardHide()

        if (message.text == "текущие" or message.text == "null"):
            markup = types.ReplyKeyboardHide()
            k = message.text
            bot.send_message(message.chat.id, "Вы выбрали " + str(now_date.year), reply_markup=markup)
            cursor.execute(
                "UPDATE users SET sector=\"" + str(k) + "\" WHERE userid=" + str(message.chat.id) + ";")
            cursor.execute(
                "UPDATE users SET year=" + "null" + " WHERE userid=" + str(message.chat.id) + ";")
            connection.commit()
            connection.close()
            bot.send_message(message.chat.id,
                             "Если вы хотите узнать информацию о бюджете в целом, введите /thm. Если вас интересует "
                             "конкретная область, введите /thm *название сферы* (например, /thm образование):")

        if (message.text == "запланированные"):
            markup = types.ReplyKeyboardHide()
            k = message.text
            bot.send_message(message.chat.id, "Вы выбрали " + str(now_date.year), reply_markup=markup)
            cursor.execute(
                "UPDATE users SET sector=\"" + str(k) + "\" WHERE userid=" + str(message.chat.id) + ";")
            cursor.execute(
                "UPDATE users SET year=" + "null" + " WHERE userid=" + str(message.chat.id) + ";")
            connection.commit()
            connection.close()
            bot.send_message(message.chat.id,
                             "Если вы хотите узнать информацию о бюджете в целом, введите /thm. Если вас интересует "
                             "конкретная область, введите /thm *название сферы* (например, /thm образование):")


if __name__ == '__main__':
    bot.polling(none_stop=True)
