import telebot
import requests
import logging
from transliterate import translit as tr
from telebot import types

import constants
import config
from m1_req import main_func
from m1_req import hello_back
from m1_speechkit import speech_to_text
from m1_speechkit import SpeechException
from m2_main import M2Retrieving
from m3_main import M3Visualizing

API_TOKEN = config.TELEGRAM_API_TOKEN1
bot = telebot.TeleBot(API_TOKEN)

logging.basicConfig(filename='logs.log', level=50, format='%(asctime)s\t%(message)s', datefmt='%Y-%m-%d %H:%M')


# /start command handler; send start-message to the user
@bot.message_handler(commands=[constants.COMMANDS[0]])
def send_welcome(message):
    bot.send_message(message.chat.id, constants.START_MSG, parse_mode='HTML')


# /help command handler; send hello-message to the user
@bot.message_handler(commands=[constants.COMMANDS[1]])
def send_welcome(message):
    bot.send_message(
        message.chat.id,
        constants.HELP_MSG,
        parse_mode='HTML',
        reply_markup=constants.HELP_KEYBOARD,
        disable_web_page_preview=True)


# /search message handler
@bot.message_handler(commands=[constants.COMMANDS[2]])
def repeat_all_messages(message):
    command_length = len(constants.COMMANDS[2])
    message_text = message.text[command_length + 2:].lower()
    if message_text != '':
        # Logging request
        logging.critical("{}\t{}".format(message.chat.id, message_text))

        s1 = main_func(message_text)
        s_mod2 = forming_string_from_neural(s1)
        querying_and_visualizing(message, s_mod2)
    else:
        bot.send_message(message.chat.id, constants.MSG_NO_BUTTON_SUPPORT, parse_mode='HTML')


# Text handler | PRESSING NON-INLINE BUTTONS RETURNS TEXT TOO!
@bot.message_handler(content_types=['text'])
def repeat_all_messages(message):
    # check if user wants us to salute him
    if hello_back(message.text) is not None:
        bot.send_message(message.chat.id, hello_back(message.text))


# inline mode handler
@bot.inline_handler(lambda query: len(query.query) >= 0)
def query_text(query):
    input_message_content = query.query
    s1 = main_func(input_message_content)
    s_mod2 = forming_string_from_neural(s1)  # receive Module 2-friendly string format
    print(s_mod2)
    result_array = []
    result = M2Retrieving.get_data(s_mod2)  # check if current user string is correct
    if result.status is False:  # in case the string is not correct we ask user to keep typing
        msg = types.InlineQueryResultArticle(id='0',
                                             title='Продолжайте ввод запроса',
                                             input_message_content=types.InputTextMessageContent(
                                                 message_text=input_message_content + '\nЗапрос не удался😢'
                                             ))
        result_array.append(msg)  # Nothing works without this list, I dunno why :P
        bot.answer_inline_query(query.id, result_array)

    else:
        logging.critical("{}\t{}".format("inline", input_message_content))
        m3_result = M3Visualizing.create_response(query.id, result.response, result.theme, visualization=False)
        try:
            if m3_result.data is False:
                msg_append_text = ': ' + constants.ERROR_NULL_DATA_FOR_SUCH_REQUEST_SHORT
                title = 'Данных нет'
            else:
                msg_append_text = ':\n' + str(m3_result.number)
                title = str(m3_result.number)

            msg = types.InlineQueryResultArticle(id='1',
                                                 title=title,
                                                 input_message_content=types.InputTextMessageContent(
                                                     message_text=input_message_content + msg_append_text),
                                                 )
            result_array.append(msg)

        finally:
            bot.answer_inline_query(query.id, result_array)


@bot.message_handler(content_types=['voice'])
def voice_processing(message):
    file_info = bot.get_file(message.voice.file_id)
    file = requests.get(
        'https://api.telegram.org/file/bot{0}/{1}'.format(API_TOKEN, file_info.file_path))
    try:
        text = speech_to_text(bytes=file.content)
        logging.critical("{}\t{}".format(message.chat.id, text))
    except SpeechException:
        msg = constants.ERROR_CANNOT_UNDERSTAND_VOICE
        bot.send_message(message.chat.id, msg)
    else:
        s1 = main_func(text)
        s_mod2 = forming_string_from_neural(s1)
        querying_and_visualizing(message, s_mod2)


def file_naming(request_string):
    request_string = tr(request_string, 'ru', reversed=True)
    filename = request_string.replace('null', '')
    filename = filename.replace(',', '_')

    for i in range(0, 3):
        filename = filename.replace('__', '_')

    if filename[len(filename) - 1] == '_':
        filename = filename[:len(filename) - 1]

    filename_svg = 'diagram_' + filename + '.svg'
    filename_pdf = 'table_' + filename + '.pdf'
    names = [filename_svg, filename_pdf]
    return names


def forming_string_from_neural(s1):
    s_mod2 = ''
    if s1[0] == 'расходы':
        s_mod2 += s1[0] + ',' + s1[4] + ',' + 'null' + ',' + str(s1[2]) + ',' + str(s1[3]) + ',' + s1[1]
    elif s1[0] == 'доходы':
        s_mod2 += s1[0] + ',' + s1[4] + ',' + str(s1[3]) + ',' + str(s1[2]) + ',' + 'null' + ',' + s1[1]
    elif s1[0] == 'дефицит':
        s_mod2 += s1[0] + ',' + s1[4] + ',' + 'null' + ',' + str(s1[2]) + ',' + 'null' + ',' + s1[1]
    return s_mod2


def querying_and_visualizing(message, s_mod2, notify_user=True):
    print(s_mod2)
    try:
        m2_result = M2Retrieving.get_data(s_mod2)
        if m2_result.status is False:
            bot.send_message(message.chat.id, m2_result.message)
        else:
            bot.send_message(message.chat.id, constants.MSG_WE_WILL_FORM_DATA_AND_SEND_YOU)
            names = file_naming(s_mod2)
            m3_result = M3Visualizing.create_response(message.chat.id, m2_result.response, m2_result.theme,
                                                      filename_svg=names[0], filename_pdf=names[1])
            if m3_result.data is False:
                bot.send_message(message.chat.id, constants.ERROR_NULL_DATA_FOR_SUCH_REQUEST_LONG)
            else:
                # Informing user how system understood him in case of voice and text processing
                if notify_user is True:
                    bot.send_message(message.chat.id, m2_result.message)

                if m3_result.is_file is False:
                    bot.send_message(message.chat.id, m3_result.number)
                else:
                    path = m3_result.path + '\\'
                    bot.send_message(message.chat.id, m3_result.number)
                    file1 = open(path + names[0], 'rb')
                    file2 = open(path + names[1], 'rb')
                    bot.send_document(message.chat.id, file1)
                    bot.send_document(message.chat.id, file2)
    except Exception as e:
        print(e)
        bot.send_message(message.chat.id, constants.ERROR_SERVER_DOES_NOT_RESPONSE)


# polling cycle
if __name__ == '__main__':
    bot.polling(none_stop=True)
