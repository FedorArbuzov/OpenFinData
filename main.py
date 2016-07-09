# This is a simple echo bot using the decorator mechanism.
# It echoes any incoming text messages.

import telebot
import schedule
import time
import sqlite3
#from telebot import types

API_TOKEN = '231161869:AAFpafehgQl9V-5f6-1KvwjPkzhbgdqDflU'
print(time.time())
#bot = telebot.TeleBot(API_TOKEN)

bot = telebot.TeleBot(API_TOKEN)
# tb.send_message(chatid, message)
#tb.send_message(153987416, 'gogo power ranger')
subscribers = []

"""""
@bot.message_handler(content_types=["text"])
def repeat_all_messages(message): #
    #bot.send_message(message.chat.id, message.text)
    bot.send_message(message.chat.id, "непонятно 😅😅😅😅")
"""
@bot.message_handler(commands=['help', 'start'])
def send_welcome(message):
    msg = bot.send_message(message.chat.id, 'Привет! Я bot!')
    @bot.message_handler(commands=['help1', 'start1'])
    def send_welcome(message):
        msg = bot.send_message(message.chat.id, 'Приветулиии')

@bot.message_handler(commands=['delivery'])
def send_welcome(message):
    print(message.chat.id)
    subscribers.append(message.chat.id)
    msg = bot.send_message(message.chat.id, 'Вы подписались на нашу рассылку!')

@bot.message_handler(content_types=["location"])
def repeat_all_messages(message): #
    #bot.send_message(message.chat.id, message.text)
    bot.send_message(message.chat.id, "hiiii 😅😅😅😅"+str(message.location))

@bot.message_handler(content_types=["text"])
def repeat_all_messages(message): #
    #bot.send_message(message.chat.id, message.text)
    bot.send_message(message.chat.id, "непонятно 😅😅😅😅")

if __name__ == '__main__':
     bot.polling(none_stop=True)