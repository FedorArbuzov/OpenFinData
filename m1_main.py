import telebot
import datetime
import sqlite3
import requests
from transliterate import translit as tr
from telebot import types
from m1_req import main_func
from m1_req import main_place
from m1_req import main_sector
from m2_main import M2Retrieving
from m3_main import M3Visualizing
from m1_speechkit import speech_to_text
from config import TELEGRAM_API_TOKEN1
from config import TELEGRAM_API_TOKEN2

API_TOKEN = TELEGRAM_API_TOKEN1
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
                         "Мы забыли про ваш предыдущий вопрос. "
                         "Можете начать снова с командой /findata")


'''
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
'''


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
            # bot.send_message(message.chat.id, 'Спасибо!')
        else:
            print(s)
            s = main_place(s)
            if (s != None):

                cursor.execute("UPDATE users SET place=\"" + s + "\" WHERE userid=" + str(message.chat.id) + ";")
                connection.commit()
                connection.close()
                # bot.send_message(message.chat.id, 'Спасибо!')
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
            # print(i1)
            if i1 == '0':
                k += 1
    if (k > 2):
        bot.send_message(message.chat.id,
                         "Похоже, вы передали нам не всю информацию. Мы не сможем дать вам корректную информацию.")
    else:
        connection = sqlite3.connect('users.db')
        cursor = connection.cursor()
        # bot.send_message(message.chat.id, "Сейчас мы сформируем ответ и отправим его вам.")
        s_main = "INSERT INTO users (id, userid, subject, place, year, sector, planned_or_actual, thm) VALUES(NULL, " + \
                 str(message.chat.id) + ", \"" + str(0) + "\", \"" + str(0) + "\", \"" + str(0) + "\", \"" + str(
            0) + "\", \"" + str(0) + "\", \"" + str(0) + "\")"
        cursor.execute(s_main)
        connection.commit()
        connection.close()

    new_data = []
    count = 0
    while count <= 7:
        for item in data:
            new_data.append(item[count])
            count += 1
            print(count)
            print(new_data)

    for n, i in enumerate(new_data):
        if i == 0 or i == '0' or i == None:
            new_data[n] = 'null'
        if i == "дефицит/профицит":
            new_data[n] = "дефицит"

    new_data[3] = new_data[3].lower()
    s_mod2, filename1, filename2 = '', '', ''
    s_mod2 += str(new_data[2]) + ',' + str(new_data[5]) + ',' + str(new_data[6]) + ',' + str(new_data[4]) + ',' + str(
        new_data[7]) + ',' + str(new_data[3])

    querying_and_visualizing(message, s_mod2)


# команда старта
@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.send_message(message.chat.id, 'Я — экспертная система OpenFinData. Я могу представить вам '
                                      'финансовый отчет о любой области за определенный год.\n'
                                      'Чтобы получить список команд, нажмите /help\n'
                                      'Чтобы сразу приступить к формированию отчета, введите /findata')


# команды помощи
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
        cursor.execute(
            "DELETE FROM users WHERE userid = " + str(message.chat.id))  # удаление ранее введенной юзером информации
        connection.commit()
        connection.close()

    s = message.text[9:]
    if (s == ""):
        # bot.send_message(message.chat.id, "Выберите предметную область:")
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
        s_mod2 = ""
        s_mod2 += s1[0] + "," + s1[4] + "," + "null" + "," + str(s1[2]) + "," + "null" + "," + s1[1]
        querying_and_visualizing(message, s_mod2)


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
            # print(i1)
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
                             'Если вы хотите узнать информацию о Российской Федерации в целом, введите /cr. '
                             'Если вас интересует конкретный регион, введите /cr *название региона* '
                             '(например, /cr Московская область):')

        else:
            bot.send_message(message.chat.id,
                             "Данные за этот год отсутствуют. Повторите ввод:")

    if message.text == '-':
        cursor.execute("UPDATE users SET year=" + 'null' + " WHERE userid=" + str(message.chat.id) + ";")
        connection.commit()
        connection.close()
        bot.send_message(message.chat.id,
                         'Если вы хотите узнать информацию о Российской Федерации в целом, введите /cr. '
                         'Если вас интересует конкретный регион, введите /cr *название региона* '
                         '(например, /cr Московская область):')

    if (message.text == "доходы" or message.text == "расходы" or message.text == "дефицит/профицит"
        or message.text == "налоговый" or message.text == "неналоговый") and (
                len(data) != 0):
        k = message.text
        if (message.text == "доходы" or message.text == "расходы" or message.text == "дефицит/профицит"):
            cursor.execute("UPDATE users SET subject=\"" + str(k) + "\" WHERE userid=" + str(message.chat.id) + ";")
            connection.commit()
            connection.close()
        if (message.text == "налоговый" or message.text == "неналоговый"):
            cursor.execute(
                "UPDATE users SET planned_or_actual=\"" + str(k) + "\" WHERE userid=" + str(message.chat.id) + ";")
            connection.commit()
            connection.close()
        if (k == "расходы"):
            national_issues_button = types.InlineKeyboardButton('Общегосударственные вопросы', callback_data='2')
            national_defence_button = types.InlineKeyboardButton('Нац. оборона', callback_data='3')
            law_enforcement_button = types.InlineKeyboardButton('Нац. безопасность', callback_data='4')
            national_economy_button = types.InlineKeyboardButton('Нац. экономика', callback_data='5')
            hcs_button = types.InlineKeyboardButton('ЖКХ', callback_data='6')
            environmental_protection_button = types.InlineKeyboardButton('Защита окружающей среды', callback_data='7')
            education_button = types.InlineKeyboardButton('Образование', callback_data='8')
            culture_and_cinematography_button = types.InlineKeyboardButton('Культура', callback_data='9')
            health_care_button = types.InlineKeyboardButton('Здравоохранение', callback_data='10')
            social_policy_button = types.InlineKeyboardButton('Соц. политика', callback_data='11')
            physical_culture_and_sport = types.InlineKeyboardButton('Спорт', callback_data='12')
            none_button = types.InlineKeyboardButton('🤔', callback_data='13')

            keyboard = types.InlineKeyboardMarkup()
            keyboard.add(national_issues_button)
            keyboard.add(national_defence_button, education_button)
            keyboard.add(law_enforcement_button, national_economy_button)
            keyboard.add(physical_culture_and_sport, culture_and_cinematography_button, hcs_button)
            keyboard.add(environmental_protection_button)
            keyboard.add(health_care_button, social_policy_button)
            keyboard.add(none_button)

            bot.send_message(message.chat.id, 'Выберите сферу: ', reply_markup=keyboard)
            # bot.send_message(message.chat.id, "Введите тип:")

            markup = types.ReplyKeyboardMarkup()
            markup.row('фактический')
            markup.row('плановый')
            markup.row('текущий')
            markup.row('запланированный')
            bot.send_message(message.chat.id, "После выберите тип расходов:", reply_markup=markup)
        elif (k == "дефицит/профицит" or k == "налоговый" or k == "неналоговый"):
            # bot.send_message(message.chat.id, "Введите тип:")
            markup = types.ReplyKeyboardMarkup()
            markup.row('плановый')
            markup.row('текущий')
            markup.row("null")
            bot.send_message(message.chat.id, "Выбирайте:", reply_markup=markup)
        elif (k == "доходы"):
            markup = types.ReplyKeyboardMarkup()
            markup.row('налоговый')
            markup.row('неналоговый')
            bot.send_message(message.chat.id, "Выбирайте:", reply_markup=markup)

    if (message.text == "фактический" or
                message.text == "плановый" or
                message.text == "текущий" or
                message.text == "запланированный" or
                message.text == "null") and (
                len(data) != 0):
        k = 0
        if (message.text == "фактический"):
            markup = types.ReplyKeyboardHide()
            k = message.text
            bot.send_message(message.chat.id,
                             "Введите год с 2007 по текущий в формате ГГГГ (например, 2010) или введите -, чтобы не указывать год:",
                             reply_markup=markup)

            cursor.execute(
                "UPDATE users SET sector=\"" + str(k) + "\" WHERE userid=" + str(message.chat.id) + ";")
            connection.commit()
            connection.close()

        if (message.text == "плановый"):
            markup = types.ReplyKeyboardHide()
            k = message.text
            bot.send_message(message.chat.id,
                             "Введите год с 2007 по текущий в формате ГГГГ (например, 2010) или введите -, чтобы не указывать год:",
                             reply_markup=markup)
            cursor.execute(
                "UPDATE users SET sector=\"" + str(k) + "\" WHERE userid=" + str(message.chat.id) + ";")

            connection.commit()
            connection.close()

            markup = types.ReplyKeyboardHide()

        if (message.text == "текущий" or message.text == "null"):
            markup = types.ReplyKeyboardHide()
            k = message.text
            bot.send_message(message.chat.id, "Вы выбрали текущий год", reply_markup=markup)
            cursor.execute(
                "UPDATE users SET sector=\"" + str(k) + "\" WHERE userid=" + str(message.chat.id) + ";")
            cursor.execute(
                "UPDATE users SET year=" + "null" + " WHERE userid=" + str(message.chat.id) + ";")
            connection.commit()
            connection.close()
            bot.send_message(message.chat.id, 'Если вы хотите узнать информацию о Российской Федерации в целом, '
                                              'введите /cr. Если вас интересует конкретный регион, введите '
                                              '/cr *название региона* (например, /cr Московская область):')

        if (message.text == "запланированный"):
            markup = types.ReplyKeyboardHide()
            k = message.text
            bot.send_message(message.chat.id, "Вы выбрали " + str(now_date.year), reply_markup=markup)
            cursor.execute(
                "UPDATE users SET sector=\"" + str(k) + "\" WHERE userid=" + str(message.chat.id) + ";")
            cursor.execute(
                "UPDATE users SET year=" + "null" + " WHERE userid=" + str(message.chat.id) + ";")
            connection.commit()
            connection.close()
            bot.send_message(message.chat.id, 'Если вы хотите узнать информацию о Российской Федерации в целом, '
                                              'введите /cr. Если вас интересует конкретный регион, введите '
                                              '/cr *название региона* (например, /cr Московская область):')


@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call):
    if call.message:
        connection = sqlite3.connect('users.db')
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM users WHERE userid = " + str(call.message.chat.id))
        data = cursor.fetchall()
        if call.data == '2':
            if len(data) != 0:
                cursor.execute("UPDATE users SET thm=\"" + call.data + "\" WHERE userid=" + str(
                    call.message.chat.id) + ";")
                bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                      text='Вы выбрали Общегосударственные вопросы')
        elif call.data == '3':
            if len(data) != 0:
                cursor.execute("UPDATE users SET thm=\"" + call.data + "\" WHERE userid=" + str(
                    call.message.chat.id) + ";")
                bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                      text='Вы выбрали Национальную оборону')
        elif call.data == '4':
            if len(data) != 0:
                cursor.execute("UPDATE users SET thm=\"" + call.data + "\" WHERE userid=" + str(
                    call.message.chat.id) + ";")
                bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                      text='Вы выбрали Национальную безопасность и правоохранительные органы')
        elif call.data == '5':
            if len(data) != 0:
                cursor.execute("UPDATE users SET thm=\"" + call.data + "\" WHERE userid=" + str(
                    call.message.chat.id) + ";")
                bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                      text='Вы выбрали Национальную экономику')
        elif call.data == '6':
            if len(data) != 0:
                cursor.execute("UPDATE users SET thm=\"" + call.data + "\" WHERE userid=" + str(
                    call.message.chat.id) + ";")
                bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                      text='Вы выбрали ЖКХ')
        elif call.data == '7':
            if len(data) != 0:
                cursor.execute("UPDATE users SET thm=\"" + call.data + "\" WHERE userid=" + str(
                    call.message.chat.id) + ";")
                bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                      text='Вы выбрали Защиту окружающей среды')
        elif call.data == '8':
            if len(data) != 0:
                cursor.execute("UPDATE users SET thm=\"" + call.data + "\" WHERE userid=" + str(
                    call.message.chat.id) + ";")
                bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                      text='Вы выбрали Образование')
        elif call.data == '9':
            if len(data) != 0:
                cursor.execute("UPDATE users SET thm=\"" + call.data + "\" WHERE userid=" + str(
                    call.message.chat.id) + ";")
                bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                      text='Вы выбрали Культуру')
        elif call.data == '10':
            if len(data) != 0:
                cursor.execute("UPDATE users SET thm=\"" + call.data + "\" WHERE userid=" + str(
                    call.message.chat.id) + ";")
                bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                      text='Вы выбрали здравоохранение')
        elif call.data == '11':
            if len(data) != 0:
                cursor.execute("UPDATE users SET thm=\"" + call.data + "\" WHERE userid=" + str(
                    call.message.chat.id) + ";")
                bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                      text='Вы выбрали Социальную политику')
        elif call.data == '12':
            if len(data) != 0:
                cursor.execute("UPDATE users SET thm=\"" + call.data + "\" WHERE userid=" + str(
                    call.message.chat.id) + ";")
                bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                      text="Вы выбрали Спорт и физическую культуру")
        elif call.data == '13':
            if len(data) != 0:
                cursor.execute("UPDATE users SET thm=\"" + 'null' + "\" WHERE userid=" + str(
                    call.message.chat.id) + ";")
                bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                      text='Вы выбрали Отсутствие конкретной сферы')
        connection.commit()
        connection.close()


@bot.message_handler(content_types=["voice"])
def voice_processing(message):
    connection = sqlite3.connect('users.db')
    cursor = connection.cursor()
    cursor.execute(
        "DELETE FROM users WHERE userid = " + str(message.chat.id))  # удаление ранее введенной юзером информации
    connection.commit()
    connection.close()

    file_info = bot.get_file(message.voice.file_id)
    file = requests.get('https://api.telegram.org/file/bot{0}/{1}'.format(TELEGRAM_API_TOKEN1, file_info.file_path))
    text = speech_to_text(bytes=file.content)

    if text is not None:
        msg = 'Ваш запрос: "' + text + '". Подождите чуть-чуть, идет его обработка!'
        bot.send_message(message.chat.id, msg)
        s1 = main_func(text)
        s_mod2 = ""
        s_mod2 += s1[0] + "," + s1[4] + "," + "null" + "," + str(s1[2]) + "," + "null" + "," + s1[1]
        querying_and_visualizing(message, s_mod2)
    else:
        msg = "Не удалось распознать текст сообщения😥 Попробуйте еще раз!"
        bot.send_message(message.chat.id, msg)


def file_naming(request_string):
    request_string = tr(request_string, 'ru', reversed=True)
    filename_svg = request_string.replace('null', '')
    filename_svg = filename_svg.replace(',', '_')
    filename_svg = filename_svg.replace('__', '_') + '.svg'
    filename_pdf = filename_svg.replace('.svg', '.pdf')
    names = [filename_svg, filename_pdf]
    return names


def querying_and_visualizing(message, s_mod2):
    names = file_naming(s_mod2)
    result = M2Retrieving.get_data(s_mod2)
    if result.status is False:
        bot.send_message(message.chat.id, result.message)
    else:
        bot.send_message(message.chat.id, "Все хорошо")
        print(result.response)
        bot.send_message(message.chat.id, "Спасибо! Сейчас мы сформируем ответ и отправим его вам.")

        m3_result = M3Visualizing.create_response(message.chat.id, result.response, names[0], names[1])
        if m3_result.is_file is False:
            bot.send_message(message.chat.id, m3_result.number)
        else:
            path = m3_result.path + "\\"
            bot.send_message(message.chat.id, m3_result.number)
            file1 = open(path + names[0], 'rb')
            file2 = open(path + names[1], 'rb')
            bot.send_document(message.chat.id, file1)
            bot.send_document(message.chat.id, file2)


if __name__ == '__main__':
    bot.polling(none_stop=True)
