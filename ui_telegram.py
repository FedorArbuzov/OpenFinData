import telebot
import requests
from telebot import types
from logs_retriever import LogsRetriever
from db.user_support_library import check_user_existence, create_user, create_feedback, get_feedbacks
from speechkit import text_to_speech

import constants
import config
import uuid
import datetime

from messenger_manager import MessengerManager

API_TOKEN = config.TELEGRAM_API_TOKEN4
bot = telebot.TeleBot(API_TOKEN)

logsRetriever = LogsRetriever('logs.log')

user_name_str = '{} {}'


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


@bot.message_handler(commands=['getlog'])
def get_all_logs(message):
    # bot.send_message(message.chat.id, logsRetriever.get_log(kind='all'))
    log_file = open('logs.log', 'rb')
    bot.send_document(message.chat.id, data=log_file)


@bot.message_handler(commands=['getsessionlog'])
def get_all_logs(message):
    time_span = None
    try:
        time_span = int(message.text.split()[1])
    except IndexError:
        pass
    if time_span:
        bot.send_message(message.chat.id,
                         logsRetriever.get_log(kind='session', user_id=message.chat.id, time_delta=time_span))
    else:
        bot.send_message(message.chat.id, logsRetriever.get_log(kind='session', user_id=message.chat.id))


@bot.message_handler(commands=['getrequestlog'])
def get_all_logs(message):
    bot.send_message(message.chat.id, logsRetriever.get_log(kind='request', user_id=message.chat.id))


# /search message handler
@bot.message_handler(commands=['search'])
def repeat_all_messages(message):
    bot.send_message(message.chat.id, constants.MSG_NO_BUTTON_SUPPORT, parse_mode='HTML')


@bot.message_handler(commands=['fb'])
def leave_feedback(message):
    if not check_user_existence(message.chat.id):
        create_user(message.chat.id,
                    message.chat.username,
                    ' '.join([message.chat.first_name, message.chat.last_name]))
    feedback = message.text[4:].strip()

    if feedback:
        create_feedback(message.chat.id,
                        datetime.datetime.fromtimestamp(message.date),
                        feedback)
        bot.send_message(message.chat.id, constants.MSG_WE_GOT_YOUR_FEEDBACK)
    else:
        bot.send_message(message.chat.id,
                         constants.MSG_LEAVE_YOUR_FEEDBACK,
                         parse_mode='HTML')


@bot.message_handler(commands=['getfeedback'])
def get_user_feedbacks(message):
    fbs = get_feedbacks()
    if fbs:
        bot.send_message(message.chat.id, fbs)
    else:
        bot.send_message(message.chat.id, 'Отзывов нет')


# Text handler
@bot.message_handler(content_types=['text'])
def salute(message):
    greets = MessengerManager.greetings(message.text.strip())
    if greets:
        bot.send_message(message.chat.id, greets)
    else:
        process_response(message)


@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call):
    if call.data == 'full_documentation':
        file1 = open('files\\Datatron User Guide.pdf', 'rb')
        bot.send_document(chat_id=call.message.chat.id, data=file1)
    elif call.data == 'intro_video':
        bot.send_message(call.message.chat.id, 'https://youtu.be/swok2pcFtNI')
    elif call.data == 'correct_response':
        request_id = call.message.text.split()[-1]
        MessengerManager.log_data('ID-запроса: {}\tМодуль: {}\tКорректность: {}'.format(request_id, __name__, '+'))
    elif call.data == 'incorrect_response':
        request_id = call.message.text.split()[-1]
        MessengerManager.log_data('ID-запроса: {}\tМодуль: {}\tКорректность: {}'.format(request_id, __name__, '-'))


# inline mode handler
@bot.inline_handler(lambda query: len(query.query) >= 0)
def query_text(query):
    input_message_content = query.query

    user_name = user_name_str.format(query.from_user.first_name, query.from_user.last_name)
    m2_result = MessengerManager.make_request_directly_to_m2(input_message_content, 'TG-INLINE',
                                                             query.from_user.id, user_name, uuid.uuid4())

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
    process_response(message, format='voice', file_content=file.content)


def process_response(message, format='text', file_content=None):
    request_id = uuid.uuid4()
    user_name = user_name_str.format(message.chat.first_name, message.chat.last_name)

    if format == 'text':
        result = MessengerManager.make_request(message.text, 'TG', message.chat.id, user_name, request_id)
    else:
        result = MessengerManager.make_voice_request(file_content, "TG", message.chat.id, user_name, request_id)

    if not result.status:
        bot.send_message(message.chat.id, result.error)
    else:
        if format == 'text':
            response_str = parse_feedback(result.feedback) + '\n\n<b>Ответ: {}</b>\nID-запроса: {}'
        else:
            response_str = parse_feedback(result.feedback, user_request_notification=True)
            response_str += '\n\n<b>Ответ: {}</b>\nID-запроса: {}'

        bot.send_message(message.chat.id, result.message)
        bot.send_message(message.chat.id,
                         response_str.format(result.response, request_id),
                         parse_mode='HTML',
                         reply_markup=constants.RESPONSE_QUALITY)
        bot.send_voice(message.chat.id, text_to_speech(result.response))


def parse_feedback(fb, user_request_notification=False):
    fb_exp = fb['formal']
    fb_norm = fb['verbal']
    exp = '<b>Экспертная обратная связь</b>\nКуб: {}\nМера: {}\nИзмерения: {}'
    norm = '<b>Дататрон выделил следующие параметры (обычная обратная связь)</b>:\n{}'
    exp = exp.format(fb_exp['cube'], fb_exp['measure'],
                     ', '.join([i['dim'] + ': ' + i['val'] for i in fb_exp['dims']]))
    norm = norm.format('1. {}\n'.format(
        fb_norm['measure']) + '\n'.join([str(idx + 2) + '. ' + i for idx, i in enumerate(fb_norm['dims'])]))

    cntk_response = '<b>CNTK разбивка</b>\n{}'
    r = ['{}. {}: {}'.format(idx+1, i['tag'].lower(), i['word'].lower()) for idx, i in enumerate(fb['cntk'])]
    cntk_response = cntk_response.format(', '.join(r))

    user_request = ''
    if user_request_notification:
        user_request = '<b>Ваш запрос</b>\nДататрон решил, что Вы его спросили следующее: "{}"\n\n'
        user_request = user_request.format(fb['user_request'])

    return '{}{}\n\n{}\n\n{}'.format(user_request, exp, norm, cntk_response)


# polling cycle
if __name__ == '__main__':
    bot.polling(none_stop=True)
