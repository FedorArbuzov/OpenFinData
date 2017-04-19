from messenger_manager import MessengerManager
from constants import CMD_START_MSG
import socket


def parse_feedback(fb):
    fb_exp = fb['formal']
    fb_norm = fb['verbal']
    exp = 'Экспертная обратная связь:\nКуб: {}\nМера: {}\nИзмерения: {}'
    norm = 'Дататрон выделил следующие параметры (обычная обратная связь):\n{}'
    exp = exp.format(fb_exp['cube'], fb_exp['measure'], ', '.join([i['dim'] + ': ' + i['val'] for i in fb_exp['dims']]))
    norm = norm.format('0. {}\n'.format(
        fb_norm['measure']) + '\n'.join([str(idx + 1) + '. ' + i for idx, i in enumerate(fb_norm['dims'])]))
    line = "==" * 10
    return '{0}\n{1}\n{0}\n{2}\n{0}'.format(line, exp, norm)


print(CMD_START_MSG)

while True:
    text = input('Введите запрос: ')
    text = text.strip()
    if text:
        greets = MessengerManager.greetings(text)
        if greets:
            print(greets)
            continue

        result = None

        # user_id - имя компьютера
        result = MessengerManager.make_request(text, 'CMD', socket.gethostname())
        if not result.status:
            print(result.error)
        else:
            print(result.message)
            print(parse_feedback(result.feedback))
            print('Ответ: ' + result.response)
