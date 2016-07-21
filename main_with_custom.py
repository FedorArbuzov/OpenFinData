# This is a main decorator mechanism.

import telebot
import schedule
import time
import datetime
import dateutil.tz
import sqlite3
import geocoder
import json
from telebot import types
import re
from req import main_func


# from telebot import types

API_TOKEN = '231161869:AAFpafehgQl9V-5f6-1KvwjPkzhbgdqDflU'
# print(time.time())


bot = telebot.TeleBot(API_TOKEN)

con = sqlite3.connect('delivery.db')
cur = con.cursor()
k = cur.fetchall()
for i in range(len(k)):
    print(k[i][1])
con.commit()
con.close()

@bot.message_handler(commands=['custom'])
def send_welcome(message):
    s = message.text[8:]
    s1 = main_func(s)
    bot.send_message(message.chat.id, s1)

@bot.message_handler(commands=['cr'])
def send_welcome(message):
    s = str(message.text)
    ss = s[4:]
    print(ss)
    con = sqlite3.connect('users.db')
    cur = con.cursor()
    cur.execute("UPDATE users SET reg=\"" + ss + "\" WHERE userid=" + str(message.chat.id) + ";")
    con.commit()
    con.close()
    bot.send_message(message.chat.id, 'Спасибо! Сейчас мы сформируем ответ и отправим его вам.')

@bot.message_handler(commands=['help', 'start'])
def send_welcome(message):
    msg = bot.send_message(message.chat.id, 'Привет! Я bot!')



@bot.message_handler(commands=['delivery'])
def send_welcome(message):
    # print(message.chat.id)
    p = message.chat.id
    con = sqlite3.connect('delivery.db')
    cur = con.cursor()
    cur.execute('SELECT * FROM users')
    k = cur.fetchall()
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
        cur.execute(s)
    else:
        bot.send_message(p, "Добрейший вечерочек, а вы уже подписались на нашу рассылку. Зачем это делать еше раз ?  ")
    con.commit()
    con.close()


@bot.message_handler(commands=['delivery_off'])
def repeat_all_messages(message):
    bot.send_message(message.chat.id, "Вы отписались от нашей рассылки. Пусть это останется на вашей совести.Но если захотите вернуться, то вы всегда сможете это сделать с помощью команды /delivery")
    con = sqlite3.connect('delivery.db')
    cur = con.cursor()
    query = "DELETE FROM users WHERE userid = "+ str(message.chat.id) +";"
    cur.execute(query)
    con.commit()
    con.close()

@bot.message_handler(commands=['findata'])
def repeat_all_messages(message):
    """
    #bot.send_message(message.chat.id, "hiiii 😅😅😅😅" )
    con = sqlite3.connect('users.db')
    cur = con.cursor()
    cur.execute("SELECT rowid FROM users WHERE userid = " + str(message.chat.id))
    data = cur.fetchall()
    if len(data) == 0:
    """
    bot.send_message(message.chat.id, "Привет! Наша система может составить финансовый  отчет по любому региону России. Для начала выберете предметную область:")
    markup = types.ReplyKeyboardMarkup()
    markup.row('доход')
    markup.row('расход')
    markup.row('дефицит')
    markup.row('долг')
    bot.send_message(message.chat.id, "Выбирайте:", reply_markup=markup)
    con = sqlite3.connect('users.db')
    cur = con.cursor()
    s = "INSERT INTO users (id, userid, params, ti, reg) VALUES(NULL," + str(message.chat.id) + ", 1, 0, 0)"
    cur.execute(s)
    con.commit()
    con.close()


@bot.message_handler(content_types=["text"])
def repeat_all_messages(message):
    print(message.text)


    markup = types.ReplyKeyboardHide()


    con = sqlite3.connect('users.db')
    cur = con.cursor()
    cur.execute("SELECT rowid FROM users WHERE userid = " + str(message.chat.id))
    data = cur.fetchall()


    if(re.match("[12][0-9][0-9][0-9][.][01][0-9][ ][12][0-9][0-9][0-9][.][01][0-9]", message.text) != None):
        print(message.text)
        s = ""
        for i in message.text:
            s += i
        #print(re.match("[12][0-9][0-9][0-9][.][01][0-9][-][12][0-9][0-9][0-9][.][01][0-9]", message.text))
        bot.send_message(message.chat.id, "Молодец")
        cur.execute("UPDATE users SET ti=\"" + s + "\" WHERE userid=" + str(message.chat.id) + ";")
        con.commit()
        con.close()
        bot.send_message(message.chat.id,
                         "Осталось совсем чуть-чуть. Необходимо выбрать субъект для которого вы хотите увидеть статистику. Напишите  " +
                         "команду /cr (choose region) и после него напишите название региона ")


    now_date = datetime.date.today()



    if(message.text == "доход" or message.text == "расход" or message.text == "дефицит" or message.text == "долг") and(len(data) != 0):
        k = 0
        if(message.text == "доход"):
            k = 11
        elif(message.text == "расход"):
            k = 21
        elif(message.text == "дефицит"):
            k = 31
        elif(message.text == "долг"):
            k = 41
        cur.execute("UPDATE users SET params=" + str(k) + " WHERE userid="+ str(message.chat.id) +";")
        con.commit()
        con.close()
        bot.send_message(message.chat.id, "Вы выбрали " + message.text, reply_markup=markup)
        bot.send_message(message.chat.id, "Ок, мы опредедились с первым пунктом. Теперь давай выберем временной промежуток:")
        markup = types.ReplyKeyboardMarkup()
        markup.row('Текущий год')
        markup.row('Текущий месяц')
        markup.row('Ввести временной промежуток самому')
        bot.send_message(message.chat.id, "Выбирайте:", reply_markup=markup)



    if (message.text == "Текущий год" or message.text == "Текущий месяц" or message.text == "Ввести временной промежуток самому") and (len(data) != 0):
        k = 0
        if(message.text == "Текущий год"):
            bot.send_message(message.chat.id, "Вы выбрали " + str(now_date.year), reply_markup=markup)
            k = now_date.year
            cur.execute("UPDATE users SET ti=" + str(k) + " WHERE userid=" + str(message.chat.id) + ";")
            con.commit()
            con.close()
            bot.send_message(message.chat.id,
                         "Осталось совсем чуть-чуть. Необходимо выбрать субъект для которого вы хотите увидеть статистику. Напишите  " +
                         "команду /cr (choose region) и после него напишите название региона ")
        if(message.text == "Текущий месяц"):
            bot.send_message(message.chat.id, "Вы выбрали " + str((now_date.year * 100) + now_date.month), reply_markup=markup)
            k = (now_date.year * 100) + "." + now_date.month
            cur.execute("UPDATE users SET ti=" + str(k) + " WHERE userid=" + str(message.chat.id) + ";")
            con.commit()
            con.close()
            bot.send_message(message.chat.id,
                             "Осталось совсем чуть-чуть. Необходимо выбрать субъект для которого вы хотите увидеть статистику. Напишите  " +
                             "команду /cr (choose region) и после него напишите название региона ")

        if (message.text == "Ввести временной промежуток самому"):
            bot.send_message(message.chat.id, "Если вы хотите сами ввести времменной промежуток, то тогда вам придется следовать " +
            "следущему шаблону(иначе мы просто не сможем вас понять). гггг.мм гггг.мм где первая часть -  это момент с которого " +
                             "вам нужно получить данные, а вторая часть - это момент по который вам нужно получить данные. Так если вам " +
                             "нужно получить данные с января 2004 по январь 2016, то вы должны просто написать 2004.01 2016.01 через пробел")

            markup = types.ReplyKeyboardHide()
            bot.send_message(message.chat.id, "Теперь введите свой временной промежуток: ", reply_markup=markup)



if __name__ == '__main__':
    bot.polling(none_stop=True)
