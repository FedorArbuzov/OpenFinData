from messenger_manager import MessengerManager
from constants import CMD_START_MSG

print(CMD_START_MSG)

continue_case = ('Y', 'y')
flag = True

while flag:
    text = input('Введите запрос: ')
    if text.strip() != '':
        greets = MessengerManager.greetings(text)
        if greets:
            print(greets)
            continue

        result = MessengerManager.make_request(text.lower(), 'CMD')
        if len(result.messages) == 1:
            print(result.messages[0])
        else:
            for msg in result.messages:
                print(msg)

        y_n = input('Продолжить Y/N? ')
        if y_n in continue_case:
            flag = True
        else:
            flag = False
    else:
        print('Введите не пустую строку!')
