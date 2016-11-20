from m1_manager import MessengerManager
from constants import CMD_START_MSG

print(CMD_START_MSG)

continue_case = ('Y', 'y')
flag = True

while flag:
    text = input('Введите запрос: ')
    if text.strip() != '':
        msg = MessengerManager.greetings(text)
        if msg:
            print(msg)
            continue

        r = MessengerManager.make_request(text.lower(), 'CMD', visualisation=False)
        if len(r.messages) == 1:
            print(r.messages[0])
        else:
            for m in r.messages:
                print(m)

        y_n = input('Продолжить Y/N? ')
        if y_n in continue_case:
            flag = True
        else:
            flag = False
    else:
        print('Введите не пустую строку!')
