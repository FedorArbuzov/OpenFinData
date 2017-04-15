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
    message_text = message.text[command_length + 2:]
    if message_text:
        # user_id - id пользователя
        result = MessengerManager.make_request(message_text, 'TG', message.chat.id)
        if not result.status:
            bot.send_message(message.chat.id, result.error)
        else:
            bot.send_message(message.chat.id, result.message)
            bot.send_message(message.chat.id, parse_feedback(result.feedback))
            bot.send_message(message.chat.id, 'Ответ: ' + result.response)
    else:
        bot.send_message(message.chat.id, constants.MSG_NO_BUTTON_SUPPORT, parse_mode='HTML')


# Text handler
@bot.message_handler(content_types=['text'])
def salute(message):
    message_text = message.text.strip()

    greets = MessengerManager.greetings(message.text)
    if greets:
        bot.send_message(message.chat.id, greets)
    else:
        # user_id - id пользователя
        result = MessengerManager.make_request(message_text, 'TG', message.chat.id)
        if not result.status:
            bot.send_message(message.chat.id, result.error)
        else:
            bot.send_message(message.chat.id, result.message)
            bot.send_message(message.chat.id, parse_feedback(result.feedback), parse_mode='HTML')
            bot.send_message(message.chat.id, 'Ответ: ' + result.response)


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

    m2_result = MessengerManager.make_request_directly_to_m2(input_message_content, 'TG-INLINE')

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
    # user_id - id пользователя
    result = MessengerManager.make_voice_request(file.content, "TG", message.chat.id)
    if not result.status:
        bot.send_message(message.chat.id, result.error)
    else:
        bot.send_message(message.chat.id, result.message)
        bot.send_message(message.chat.id, parse_feedback(result.feedback), parse_mode='HTML')
        bot.send_message(message.chat.id, 'Ответ: ' + result.response)


def parse_feedback(fb):
    fb_exp = fb['formal']
    fb_norm = fb['verbal']
    exp = '<b>Экспертная обратная связь</b>\nКуб: {}\nМера: {}\nИзмерения: {}'
    norm = '<b>Дататрон выделил следующие параметры (обычная обратная связь)</b>:\n{}'
    exp = exp.format(fb_exp['cube'], fb_exp['measure'],
                     ', '.join([i['dim'] + ': ' + i['val'] for i in fb_exp['dims']]))
    norm = norm.format('0. {}\n'.format(
        fb_norm['measure']) + '\n'.join([str(idx + 1) + '. ' + i for idx, i in enumerate(fb_norm['dims'])]))
    return '{}\n\n{}'.format(exp, norm)


# polling cycle
if __name__ == '__main__':
    bot.polling(none_stop=True)
