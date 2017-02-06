import telebot
import requests
from telebot import types

import constants
import config

from messenger_manager import MessengerManager

API_TOKEN = config.TELEGRAM_API_TOKEN1
bot = telebot.TeleBot(API_TOKEN)


# /start command handler; send start-message to the user
@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.send_message(message.chat.id, constants.TELEGRAM_START_MSG, parse_mode='HTML')


# /help command handler; send hello-message to the user
@bot.message_handler(commands=['help'])
def send_welcome(message):
    bot.send_message(
        message.chat.id,
        constants.HELP_MSG,
        parse_mode='HTML',
        reply_markup=constants.HELP_KEYBOARD,
        disable_web_page_preview=True)


# /search message handler
@bot.message_handler(commands=['search'])
def repeat_all_messages(message):
    command_length = len('search')
    message_text = message.text[command_length + 2:].lower()
    if message_text != '':
        r = MessengerManager.make_request(message_text, 'TG')
        if len(r.messages) == 1:
            bot.send_message(message.chat.id, r.messages[0])
        else:
            for m in r.messages:
                bot.send_message(message.chat.id, m)
            if r.is_file:
                path = r.path + '\\'
                file1 = open(path + r.file_names[0], 'rb')
                file2 = open(path + r.file_names[1], 'rb')
                bot.send_document(message.chat.id, file1)
                bot.send_document(message.chat.id, file2)

    else:
        bot.send_message(message.chat.id, constants.MSG_NO_BUTTON_SUPPORT, parse_mode='HTML')


# Text handler
@bot.message_handler(content_types=['text'])
def salute(message):
    message_text = message.text.lower().strip()

    greets = MessengerManager.greetings(message.text)
    if greets:
        bot.send_message(message.chat.id, greets)
    else:
        result = MessengerManager.make_request(message_text, 'TG')
        if len(result.messages) == 1:
            bot.send_message(message.chat.id, result.messages[0])
        else:
            for msg in result.messages:
                bot.send_message(message.chat.id, msg)


@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call):
    if call.data == 'full_documentation':
        file1 = open('files\\Datatron User Guide.pdf', 'rb')
        bot.send_document(chat_id=call.message.chat.id, data=file1)
    elif call.data == 'intro_video':
        bot.send_message(call.message.chat.id, 'https://youtu.be/swok2pcFtNI')


# inline mode handler
@bot.inline_handler(lambda query: len(query.query) >= 0)
def query_text(query):
    input_message_content = query.query

    m2_result = MessengerManager.make_request_m2(input_message_content, 'TG-INLINE')

    result_array = []
    if m2_result.status is False:  # in case the string is not correct we ask user to keep typing
        msg = types.InlineQueryResultArticle(id='0',
                                             title='Продолжайте ввод запроса',
                                             input_message_content=types.InputTextMessageContent(
                                                 message_text=input_message_content + '\nЗапрос не удался😢'
                                             ))
        result_array.append(msg)  # Nothing works without this list, I dunno why :P
        bot.answer_inline_query(query.id, result_array)

    else:
        try:
            msg_append_text = ':\n' + str(m2_result.response)
            title = str(m2_result.response)

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
    file = requests.get('https://api.telegram.org/file/bot{0}/{1}'.format(API_TOKEN, file_info.file_path))
    r = MessengerManager.make_voice_request(file.content, "TG")

    if type(r) is str:
        bot.send_message(message.chat.id, r.messages[0])
    else:
        if len(r.messages) == 1:
            bot.send_message(message.chat.id, r.messages[0])
        else:
            for m in r.messages:
                bot.send_message(message.chat.id, m)


# polling cycle
if __name__ == '__main__':
    bot.polling(none_stop=True)
