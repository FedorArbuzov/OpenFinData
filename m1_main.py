import telebot
import datetime
import sqlite3
import requests
from transliterate import translit as tr
from telebot import types
from m1_req import main_func
from m1_req import main_place
from m2_main import M2Retrieving
from m2_lib import feedback
from m3_main import M3Visualizing
from m1_speechkit import speech_to_text
from config import TELEGRAM_API_TOKEN1
from config import TELEGRAM_API_TOKEN2
from config import TELEGRAM_API_TOKEN_FINAL

# Constants for text and messages
START_MSG = 'Я — экспертная система Datatron. С помощью меня можно быстро получить' \
            'доступ к финансовым данным по любой области.\n' \
            'Чтобы получить список команд, нажмите /help\n' \
            'Чтобы сразу приступить к работе, введите /search'
COMMANDS_MSG = '<b>Список команд:</b>\n' \
               '/start — начать работу с ботом\n' \
               '/help — список команд\n' \
               '/search — получить данные'
TERRITORY_MSG = 'Чтобы узнать информацию о Российской Федерации в целом, просто нажмите /cr. ' \
                'Чтобу узнать данные по конкретному региону, введите /cr *название региона* ' \
                '(например, /cr Московская область)'
YEAR_MSG = 'Введите год цифрами с 2007 по ' + \
           str(datetime.datetime.now().year - 1) + \
           ' или поставьте "-" для получения данных за нынешний год'

ERROR_CR_MSG = 'Рановато вы перешли на области😏 Начните лучше с команды /search'
ERROR_NO_UNDERSTANDING = 'Боюсь, что мы вас не поняли 😰'
ERROR_NOT_FULL_INFO = 'Похоже, вы передали нам не всю информацию🙃 Попробуйте начать сначала /search'
ERROR_NO_DATA_THIS_YEAR = 'Упс, данных за такой год, к сожалению, нет🙈 Попробуйте еще раз!'
ERROR_CHECK_INPUT = 'Хмм... Проверьте правильность ввода🔎'
ERROR_CANNOT_UNDERSTAND_VOICE = 'Не удалось распознать текст сообщения😥 Попробуйте еще раз!'
ERROR_NULL_DATA_FOR_SUCH_REQUEST = 'К сожалению, этих данных в системе нет🤕 Не отчаивайтесь! Есть много ' \
                                   'других цифр😉 Жми /search'

MSG_BEFORE_THEMES = 'Жмакните на одну из кнопок!'
MSG_BEFORE_SPHERE = 'Какая сфера расходов вас интересует?'
MSG_BEFORE_NALOG_NENALOG = 'Налоговые или неналоговые?'
MSG_BEFORE_TYPE_EXPENDITURES = 'После укажите тип расходов:'
MSG_BEFORE_TYPE_PROFIT = 'Выберите тип:'
MSG_AFTER_VOICE_INPUT = 'Подождите совсем чуть-чуть, идет его обработка!?'
MSG_WE_WILL_FORM_DATA_AND_SEND_YOU = "Спасибо! Сейчас мы сформируем ответ🙌 и отправим его вам😊"

API_TOKEN = TELEGRAM_API_TOKEN_FINAL
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


# команда выбора региона (choose region)
@bot.message_handler(commands=['cr'])
def send_welcome(message):
    connection = sqlite3.connect('users.db')
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM users WHERE userid = " + str(message.chat.id))
    data = cursor.fetchall()
    if len(data) != 0:
        s = str(message.text)[4:]
        if s == "" or main_place(s) is not None:
            if s == '':
                cursor.execute("UPDATE users SET place=\"" + "null" + "\" WHERE userid=" + str(message.chat.id) + ";")
                connection.commit()
                connection.close()

            if main_place(s) is not None:
                s = main_place(s)
                cursor.execute("UPDATE users SET place=\"" + s + "\" WHERE userid=" + str(message.chat.id) + ";")
                connection.commit()
                connection.close()

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
            if k > 2:
                bot.send_message(message.chat.id, ERROR_NOT_FULL_INFO)
            else:
                connection = sqlite3.connect('users.db')
                cursor = connection.cursor()
                s_main = "INSERT INTO users (id, userid, subject, place, year, sector, planned_or_actual, thm) VALUES(NULL, " + \
                         str(message.chat.id) + ", \"" + str(0) + "\", \"" + str(0) + "\", \"" + str(
                    0) + "\", \"" + str(
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

            for n, i in enumerate(new_data):
                if i == 0 or i == '0' or i is None:
                    new_data[n] = 'null'
                if i == "дефицит/профицит":
                    new_data[n] = "дефицит"

            new_data[3] = new_data[3].lower()
            s_mod2, filename1, filename2 = '', '', ''
            s_mod2 += str(new_data[2]) + ',' + str(new_data[5]) + ',' + str(new_data[6]) + ',' + str(
                new_data[4]) + ',' + str(
                new_data[7]) + ',' + str(new_data[3])

            querying_and_visualizing(message, s_mod2)
        else:
            bot.send_message(message.chat.id, ERROR_NO_UNDERSTANDING)
    else:
        bot.send_message(message.chat.id, ERROR_CR_MSG)


# команда старта
@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.send_message(message.chat.id, START_MSG)


# команды помощи
@bot.message_handler(commands=['help'])
def send_welcome(message):
    bot.send_message(message.chat.id, COMMANDS_MSG, parse_mode='HTML')


@bot.message_handler(commands=['search'])
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
    if s == "":
        # bot.send_message(message.chat.id, "Выберите предметную область:")
        markup = types.ReplyKeyboardMarkup()
        markup.row('доходы')
        markup.row('расходы')
        markup.row('дефицит/профицит')
        bot.send_message(message.chat.id, MSG_BEFORE_THEMES, reply_markup=markup)
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
        s_mod2 = forming_string_from_neural(s1)
        querying_and_visualizing(message, s_mod2)


@bot.message_handler(content_types=["text"])
def repeat_all_messages(message):
    markup = types.ReplyKeyboardHide()

    connection = sqlite3.connect('users.db')
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM users WHERE userid = " + str(message.chat.id))
    data = cursor.fetchall()
    k = 0
    for i in data:
        for i1 in i:
            if i1 == '0':
                k += 1

    now_date = datetime.date.today()

    if represents_int(message.text) and len(data) != 0:
        i = int(message.text)
        if 2006 < i < now_date.year:
            cursor.execute("UPDATE users SET year=" + str(i) + " WHERE userid=" + str(message.chat.id) + ";")
            connection.commit()
            connection.close()
            bot.send_message(message.chat.id, TERRITORY_MSG)

        else:
            bot.send_message(message.chat.id, ERROR_NO_DATA_THIS_YEAR)

    elif message.text == '-':
        cursor.execute("UPDATE users SET year=" + 'null' + " WHERE userid=" + str(message.chat.id) + ";")
        connection.commit()
        connection.close()
        bot.send_message(message.chat.id, TERRITORY_MSG)

    elif (message.text == "доходы" or message.text == "расходы" or message.text == "дефицит/профицит"
          or message.text == "налоговые" or message.text == "неналоговые" or message.text == "все") and (
                len(data) != 0):
        k = message.text
        if message.text == "доходы" or message.text == "расходы" or message.text == "дефицит/профицит":
            cursor.execute("UPDATE users SET subject=\"" + str(k) + "\" WHERE userid=" + str(message.chat.id) + ";")
            connection.commit()
            connection.close()
        if message.text == "налоговые" or message.text == "неналоговые" or message.text == "все":
            if message.text == "все":
                k_clone = "null"
            elif message.text == "налоговые":
                k_clone = "налоговый"
            else:
                k_clone = "неналоговый"
            cursor.execute(
                "UPDATE users SET planned_or_actual=\"" + k_clone + "\" WHERE userid=" + str(message.chat.id) + ";")
            connection.commit()
            connection.close()
        if k == "расходы":
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
            none_button = types.InlineKeyboardButton('Расходы в целом', callback_data='13')

            keyboard = types.InlineKeyboardMarkup()
            keyboard.add(national_issues_button)
            keyboard.add(national_defence_button, education_button)
            keyboard.add(law_enforcement_button, national_economy_button)
            keyboard.add(physical_culture_and_sport, culture_and_cinematography_button, hcs_button)
            keyboard.add(environmental_protection_button)
            keyboard.add(health_care_button, social_policy_button)
            keyboard.add(none_button)

            bot.send_message(message.chat.id, MSG_BEFORE_SPHERE, reply_markup=keyboard)
            markup = types.ReplyKeyboardMarkup()
            markup.row('плановые')
            markup.row('текущие')
            markup.row('фактические')
            bot.send_message(message.chat.id, MSG_BEFORE_TYPE_EXPENDITURES, reply_markup=markup)
        elif k == "дефицит/профицит" or k == "налоговые" or k == "неналоговые" or k == "все":
            markup = types.ReplyKeyboardMarkup()
            if k == "дефицит/профицит":
                markup.row('плановый')
                markup.row('текущий')
                markup.row('фактический')
            else:
                markup.row('плановые')
                markup.row('текущие')
                markup.row("фактические")
            bot.send_message(message.chat.id, MSG_BEFORE_TYPE_PROFIT, reply_markup=markup)
        elif k == "доходы":
            markup = types.ReplyKeyboardMarkup()
            markup.row('налоговые')
            markup.row('неналоговые')
            markup.row('все')
            bot.send_message(message.chat.id, MSG_BEFORE_NALOG_NENALOG, reply_markup=markup)

    elif (message.text == "фактические" or message.text == "фактический" or
                  message.text == "плановые" or message.text == "плановый" or
                  message.text == "текущие" or message.text == "текущий" or
                  message.text == "все") and (len(data) != 0):
        k = 0
        if message.text == "фактические" or message.text == "фактический":
            markup = types.ReplyKeyboardHide()
            k = "фактический"
            bot.send_message(message.chat.id, YEAR_MSG, reply_markup=markup)

            cursor.execute(
                "UPDATE users SET sector=\"" + str(k) + "\" WHERE userid=" + str(message.chat.id) + ";")
            connection.commit()
            connection.close()

        if message.text == "плановые" or message.text == "плановый":
            markup = types.ReplyKeyboardHide()
            if message.text == "плановые":
                k = "плановый"
            elif message.text == "плановый":
                k = message.text
            bot.send_message(message.chat.id, YEAR_MSG, reply_markup=markup)
            cursor.execute(
                "UPDATE users SET sector=\"" + str(k) + "\" WHERE userid=" + str(message.chat.id) + ";")

            connection.commit()
            connection.close()

            markup = types.ReplyKeyboardHide()

        if message.text == "текущие" or message.text == "текущий":
            markup = types.ReplyKeyboardHide()
            k = "текущий"
            cursor.execute(
                "UPDATE users SET sector=\"" + str(k) + "\" WHERE userid=" + str(message.chat.id) + ";")
            cursor.execute(
                "UPDATE users SET year=" + "null" + " WHERE userid=" + str(message.chat.id) + ";")
            connection.commit()
            connection.close()
            bot.send_message(message.chat.id, TERRITORY_MSG, reply_markup=markup)
    else:
        bot.send_message(message.chat.id, ERROR_CHECK_INPUT)


@bot.inline_handler(lambda query: len(query.query) > 0)
def query_text(query):
    text = query.query
    input_message_content = text
    s1 = main_func(text)
    s_mod2 = forming_string_from_neural(s1)
    print(s_mod2)

    result = M2Retrieving.get_data(s_mod2)
    filename1, filename2 = 'f1', 'f2'
    if result.status is False:
        pass
    else:
        m3_result = M3Visualizing.create_response(query.id, result.response, filename1, filename2, visualization=False)
        try:
            result_array = []
            msg = types.InlineQueryResultArticle(id='1',
                                                 title=input_message_content,
                                                 input_message_content=types.InputTextMessageContent(
                                                     message_text=input_message_content + ':\n' + str(
                                                         m3_result.number)),
                                                 )
            result_array.append(msg)

        finally:
            bot.answer_inline_query(query.id, result_array)


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
                                      text='Вы выбрали "Общегосударственные вопросы"')
        elif call.data == '3':
            if len(data) != 0:
                cursor.execute("UPDATE users SET thm=\"" + call.data + "\" WHERE userid=" + str(
                    call.message.chat.id) + ";")
                bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                      text='Вы выбрали "Национальную оборону"')
        elif call.data == '4':
            if len(data) != 0:
                cursor.execute("UPDATE users SET thm=\"" + call.data + "\" WHERE userid=" + str(
                    call.message.chat.id) + ";")
                bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                      text='Вы выбрали "Национальную безопасность и правоохранительные органы"')
        elif call.data == '5':
            if len(data) != 0:
                cursor.execute("UPDATE users SET thm=\"" + call.data + "\" WHERE userid=" + str(
                    call.message.chat.id) + ";")
                bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                      text='Вы выбрали "Национальную экономику"')
        elif call.data == '6':
            if len(data) != 0:
                cursor.execute("UPDATE users SET thm=\"" + call.data + "\" WHERE userid=" + str(
                    call.message.chat.id) + ";")
                bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                      text='Вы выбрали "ЖКХ"')
        elif call.data == '7':
            if len(data) != 0:
                cursor.execute("UPDATE users SET thm=\"" + call.data + "\" WHERE userid=" + str(
                    call.message.chat.id) + ";")
                bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                      text='Вы выбрали "Защиту окружающей среды"')
        elif call.data == '8':
            if len(data) != 0:
                cursor.execute("UPDATE users SET thm=\"" + call.data + "\" WHERE userid=" + str(
                    call.message.chat.id) + ";")
                bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                      text='Вы выбрали "Образование"')
        elif call.data == '9':
            if len(data) != 0:
                cursor.execute("UPDATE users SET thm=\"" + call.data + "\" WHERE userid=" + str(
                    call.message.chat.id) + ";")
                bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                      text='Вы выбрали "Культуру"')
        elif call.data == '10':
            if len(data) != 0:
                cursor.execute("UPDATE users SET thm=\"" + call.data + "\" WHERE userid=" + str(
                    call.message.chat.id) + ";")
                bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                      text='Вы выбрали "Здравоохранение"')
        elif call.data == '11':
            if len(data) != 0:
                cursor.execute("UPDATE users SET thm=\"" + call.data + "\" WHERE userid=" + str(
                    call.message.chat.id) + ";")
                bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                      text='Вы выбрали "Социальную политику"')
        elif call.data == '12':
            if len(data) != 0:
                cursor.execute("UPDATE users SET thm=\"" + call.data + "\" WHERE userid=" + str(
                    call.message.chat.id) + ";")
                bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                      text='Вы выбрали "Спорт и физическую культуру"')
        elif call.data == '13':
            if len(data) != 0:
                cursor.execute("UPDATE users SET thm=\"" + 'null' + "\" WHERE userid=" + str(
                    call.message.chat.id) + ";")
                bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                      text='Вы выбрали "Расходы в целом"')
        connection.commit()
        connection.close()


@bot.message_handler(content_types=["voice"])
def voice_processing(message):
    connection = sqlite3.connect('users.db')
    cursor = connection.cursor()
    cursor.execute(
        "DELETE FROM users WHERE userid = " + str(message.chat.id))
    connection.commit()
    connection.close()

    file_info = bot.get_file(message.voice.file_id)
    file = requests.get(
        'https://api.telegram.org/file/bot{0}/{1}'.format(TELEGRAM_API_TOKEN_FINAL, file_info.file_path))
    text = speech_to_text(bytes=file.content)

    if text is not None:
        msg = 'Ваш запрос: "' + text + '". '
        bot.send_message(message.chat.id, msg)
        s1 = main_func(text)
        s_mod2 = forming_string_from_neural(s1)

        querying_and_visualizing(message, s_mod2)
    else:
        msg = ERROR_CANNOT_UNDERSTAND_VOICE
        bot.send_message(message.chat.id, msg)


def file_naming(request_string):
    request_string = tr(request_string, 'ru', reversed=True)
    filename = request_string.replace('null', '').replace(',', '_').replace('__', '_')
    filename_svg = filename + '.svg'
    filename_pdf = filename + '.pdf'
    names = [filename_svg, filename_pdf]
    return names


def forming_string_from_neural(s1):
    s_mod2 = ""
    if s1[0] == "расходы":
        s_mod2 += s1[0] + "," + s1[4] + "," + "null" + "," + str(s1[2]) + "," + str(s1[3]) + "," + s1[1]
    elif s1[0] == "доходы":
        s_mod2 += s1[0] + "," + s1[4] + "," + str(s1[3]) + "," + str(s1[2]) + "," + "null" + "," + s1[1]
    elif s1[0] == "дефицит":
        s_mod2 += s1[0] + "," + s1[4] + "," + "null" + "," + str(s1[2]) + "," + "null" + "," + s1[1]
    return s_mod2


def querying_and_visualizing(message, s_mod2):
    print(s_mod2)
    names = file_naming(s_mod2)
    result = M2Retrieving.get_data(s_mod2)
    if result.status is False:
        bot.send_message(message.chat.id, result.message)
    else:
        bot.send_message(message.chat.id, MSG_WE_WILL_FORM_DATA_AND_SEND_YOU)

        m3_result = M3Visualizing.create_response(message.chat.id, result.response, names[0], names[1])
        if m3_result.is_file is False:
            if m3_result.number[0] == "0":
                bot.send_message(message.chat.id, ERROR_NULL_DATA_FOR_SUCH_REQUEST)
            else:
                bot.send_message(message.chat.id, m3_result.number)
        else:
            if m3_result.number[0] == "0":
                bot.send_message(message.chat.id, ERROR_NULL_DATA_FOR_SUCH_REQUEST)
            else:
                path = m3_result.path + "\\"
                bot.send_message(message.chat.id, m3_result.number)
                file1 = open(path + names[0], 'rb')
                file2 = open(path + names[1], 'rb')
                bot.send_document(message.chat.id, file1)
                bot.send_document(message.chat.id, file2)


if __name__ == '__main__':
    bot.polling(none_stop=True)
