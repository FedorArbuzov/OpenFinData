import re
from m1_work_class import quest
import datetime
import sqlite3

key_words = ['год',
             'текущий', 'прошлый',
             'доход', 'расход', 'дефицит', 'доля', 'долг',
             'образование', 'среднее', 'начальное', 'высшее',
             'объем', 'общий', 'общем',
             'плановый', 'запланированный', 'фактический', 'бюждет', 'этот',
             'Российская Федерация', 'Россия', 'РФ',
             'Северо-Кавказский федеральный',
             'Ставропольский',
             'Ингушетия',
             'Дагестан',
             'Кабардино-Балкарская',
             'Осетия',
             'Карачаево-Черкесская',
             'Чеченская',
             'Южный',
             'Краснодарский',
             'астраханская',
             'Волгоградская',
             'Ростовская',
             'адыгея', 'адыгея',
             'Калмыкия',
             'Приволжский',
             'Нижегородская',
             'Кировская',
             'Самарская',
             'Оренбургская',
             'Пензенская',
             'Пермский',
             'Саратовская',
             'Ульяновская',
             'Башкортостан',
             'Марий Эл',
             'Мордовия',
             'Татарстан',
             'Удмуртская', 'Удмуртия',
             'Чувашская', 'Чувашия',
             'Северо-Западный',
             'архангельская',
             'Ненецкий',
             'Вологодская',
             'Калининградская',
             'Санкт-Петербург',
             'Ленинградская',
             'Мурманская',
             'Новгородская',
             'Псковская',
             'Карелия',
             'Коми',
             'Сибирский',
             'алтайский',
             'Красноярский',
             'Кемеровская',
             'Иркутская',
             'Новосибирская',
             'Омская',
             'Томская',
             'Забайкальский',
             'Бурятия',
             'алтай',
             'Тыва',
             'Хакасия',
             'Уральский',
             'Курганская',
             'Свердловская',
             'Тюменская',
             'Ханты-Мансийский',
             'Ямало-Ненецкий',
             'Челябинская',
             'Центральный',
             'Белгородская',
             'Брянская',
             'Владимирская',
             'Воронежская',
             'Ивановская',
             'Тверская',
             'Калужская',
             'Костромская',
             'Курская',
             'Липецкая',
             'Москва',
             'Московская',
             'Орловская',
             'Рязанская',
             'Смоленская',
             'Тамбовская',
             'Тульская',
             'Ярославская',
             'Дальневосточный',
             'Приморский',
             'Хабаровский',
             'амурская',
             'Камчатский',
             'Магаданская',
             'Сахалинская',
             'Чукотский',
             'Саха', 'Якутия',
             'Еврейская',
             'Крымский',
             'Крым',
             'Севастополь',
             'Байконур',  # sections of rev and cons
             'безопасность',
             'образование',
             'охрана',
             'жкх',
             'культура',
             'здравоохранение',
             'спорт',
             'экология']
useless_pile_of_crap = [
    'в', 'без', 'до', 'из', 'к', 'на', 'по', 'о', 'от', 'перед', 'при', 'через', 'с', 'у', 'за', 'над', 'об', 'под',
    'про', 'для',
    'республика', 'республики',
    'республики', 'республик',
    'республике', 'республикам',
    'республику', 'республики',
    'республикой',
    'республикою', 'республиками',
    'республике', 'республиках',
    'область', 'области', 'областью', 'областей', 'областям', 'областями', 'областях',
    'автономный', 'автономного', 'автономному', 'автономного', 'автономным', 'автономном', 'автномном', 'автономная',
    'автономной', 'автономную', 'автономною', 'автономна', 'автономные', 'автономных', 'автономными',
    'федеральный', 'федерального', 'федеральному', 'федеральным', 'федеральном', 'федерален', 'федеральных',
    'федеральным', 'федеральными',
    'край', 'края', 'краю', 'краем', 'крае', 'краев', 'краям', 'краями', 'краях']
list_of_int = []
useless_word_in_sen = []


def RepresentsInt(s):
    try:
        int(s)
        return True
    except ValueError:
        return False


# the Levenstein distance algorithm
def distance(a: object, b: object) -> object:
    """Calculates the Levenshtein distance between a and b."""
    n, m = len(a), len(b)
    if n > m:
        # Make sure n <= m, to use O(min(n,m)) space
        a, b = b, a
        n, m = m, n

    current_row = range(n + 1)  # Keep current and previous row, not entire matrix
    for i in range(1, m + 1):
        previous_row, current_row = current_row, [i] + [0] * n
        for j in range(1, n + 1):
            add, delete, change = previous_row[j] + 1, current_row[j - 1] + 1, previous_row[j - 1]
            if a[j - 1] != b[i - 1]:
                change += 1
            current_row[j] = min(add, delete, change)

    return current_row[n]


# Основная функция
def check_the_territories(str_user):
    minimum_value = 123
    index_of_the_most_likely_variant = 0
    i = 0
    for _ in key_words:
        distance_between_input_and_table_data = distance(str_user, key_words[i])
        if distance_between_input_and_table_data < minimum_value:
            minimum_value = distance_between_input_and_table_data
            index_of_the_most_likely_variant = i
        i += 1

    return index_of_the_most_likely_variant


def main_place(s):
    s = re.sub(r'[^\w\s]', '', s)
    list1 = s.split()
    for s in useless_pile_of_crap:
        if s in list1:
            list1.remove(s)


    i = 0
    for _ in list1:
        result = check_the_territories(list1[i])
        i += 1
        for s in key_words[20:-8]:
            if (s == key_words[result]):
                return s

def main_sector(s):
    s = re.sub(r'[^\w\s]', '', s)
    list1 = s.split()
    for s in useless_pile_of_crap:
        if s in list1:
            list1.remove(s)
    i = 0
    for _ in list1:
        result = check_the_territories(list1[i])
        i += 1
        for s in key_words[-8:]:
            if (s == key_words[result]):
                return s


def main_func(s):
    s = re.sub(r'[^\w\s]', '', s)
    list1 = s.split()
    list_of_int = []
    for i in range(len(list1)):
        if RepresentsInt(list1[i]):
            list_of_int.append(list1[i])

    for s in useless_pile_of_crap:
        if s in list1:
            list1.remove(s)


    for s in list_of_int:
        if s in list1:
            list1.remove(s)

    user_req = quest()

    i = 0
    now_date = datetime.date.today()
    for _ in list1:
        result = check_the_territories(list1[i])

        if key_words[result] == 'плановый':
            user_req.planned_or_actual = 'плановый'
        if key_words[result] == 'запланированный':
            user_req.planned_or_actual = 'запланированный'
        if key_words[result] == 'фактический':
            user_req.planned_or_actual = "фактический"

        if key_words[result] == 'бюджет':
            user_req.sector = 'бюджет'
        if key_words[result] == "доход":
            user_req.subject = "доходы"
        if key_words[result] == "расход":
            user_req.subject = "расходы"
        if key_words[result] == "дефицит":
            user_req.subject = "дефицит"
        if key_words[result] == 'текущий':
            user_req.year = now_date.year
        if key_words[result] == 'прошлый':
            user_req.year = now_date.year - 1

        for s in key_words[20:-8]:
            if (s == key_words[result]):
                user_req.place = s

        for s in key_words[-8:]:
            if (s == key_words[result]):
                user_req.sector = s

        i += 1
    if user_req.sector == "":
        user_req.sector = "null"
    if user_req.planned_or_actual == "":
        user_req.planned_or_actual = "null"
    if user_req.place == "":
        user_req.place = "null"
    if user_req.year == 0 or user_req.year == now_date.year or user_req.year == now_date.year - 1:
        if len(list_of_int) != 0:
            user_req.year = int(list_of_int[0])

    print(user_req.planned_or_actual)
    print(user_req.subject)
    if user_req.year == 0 and user_req.year < 2016 and user_req.year > 2006:
        user_req.year = now_date.year
    print(user_req.year)
    print(user_req.place)
    print(user_req.sector)
    user_r = [user_req.subject, user_req.place.lower(), user_req.year, user_req.sector, user_req.planned_or_actual]
    return user_r
