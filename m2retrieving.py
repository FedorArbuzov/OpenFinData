from datetime import datetime


# Module, which is responsible for getting required from user data
class M2Retrieving:
    @staticmethod
    def get_data(input_string):
        """Getting JSON data based on input parameters"""

        # 1. Преобразовать входную строку в лист
        params = input_string.split(',')
        response = Result(request=input_string)

        # 2. Создать мэп списка
        response = M2Retrieving._list_to_mapper(params, response)
        if response.message != "":
            print(response.message)
            print(response.status)
            print(response.mapper)
            print(response.request)
            return response

        # 3. Проверить какому из существующих мэпов соответствует данный мэп
        # 4. Получить MDX запрос для мэпа
        mdx_skeleton = M2Retrieving._get_mdx_skeleton_for_mapper(response)

        if mdx_skeleton == 0:
            print(response.message)
            return response

        # 5. Подставить в MDX запрос вместо '*1, *2, *3 и тд' параметры
        # 6. Отправить MDX запрос
        mdx_query = M2Retrieving._refactor_mdx_skeleton(mdx_skeleton, params)
        result = M2Retrieving._send_mdx_request(mdx_query)
        if len(result == 0):
            return False
        return result

    @staticmethod
    def _list_to_mapper(parameters, response):
        """Refactoring input parameters in mapper"""

        # Inner codes for refactoring list in mapper
        _codes = (
            {
                'Расходы': 2,
                'Доходы': 3,
                'Дефицит': 4,
                'Профицит': 4
            },

            {
                'Плановый': 2,
                'Фактический': 3,
                'Текущий': 4,
                'Запланированный': 5
            }
        )

        mapper = ''

        if parameters[0] in _codes[0]:
            mapper += str(_codes[0].get(parameters[0])) + '.'
        else:
            response.status = False
            response.message = 'Неверно выбрана предметная область.'
            return response

        if parameters[1] == 'null':
            mapper += '0.'
        elif parameters[1] in _codes[1]:
            mapper += str(_codes[1].get(parameters[1])) + '.'
        else:
            response.status = False
            response.message = 'Неверно выбрана 1я характеристика предметной области'
            return response

        if parameters[2] == 'null':
            mapper += '0.'
        elif parameters[2] in _codes[2]:
            mapper += str(_codes[2].get(parameters[2])) + '.'
        else:
            response.status = False
            message = 'Параметр "' + parameters[2] + '" не верен. ' \
                                                     'Допустимы: отсутствие этого параметра, ' \
                                                     'значение "налоговый" или "неналоговый"'
            response.message = message
            return response

        if parameters[3] == 'null':
            mapper += '0.'
        elif int(parameters[3]) > 2006 and int(parameters[3]) <= datetime.today().year:
            mapper += '1.'
        else:
            response.status = False
            response.message = 'Введите год от 2007 до ' + str(datetime.today().year) + '.'
            return response

        if parameters[4] == 'null':
            mapper += '0.'
        else:
            mapper += '1.'

        if parameters[5] == 'null':
            mapper += '0'
        else:
            mapper += '1'

        response.mapper = mapper
        return response

    @staticmethod
    def _mapper_to_words(mapper):
        """Refactoring mapper in word constructions"""
        # Inner codes for refactoring mapper in list
        _codes = (
            {
                2: 'Расходы',
                3: 'Доходы',
                4: 'Дефицит/Профицит'
            },
            {
                0: 'Тип(пустой параметр)',
                2: 'Плановый',
                3: 'Фактический',
                4: 'Текущий',
                5: 'Запланированный'
            },
            {
                1: 'Налоговый/Неналоговый',
                0: 'Группа расходов(пустой параметр)'
            },
            {
                1: 'Год',
                0: 'Год(пустой параметр)'
            },
            {
                1: 'Сфера',
                0: 'Сфера(пустой параметр)'
            },
            {
                1: 'Территория',
                0: 'Территория (пустой параметр)'
            }
        )

        words = '/'
        items = mapper.split('.')
        index = 0
        for i in items:
            words += _codes[index].get(int(i)) + '/'
            index += 1
        return words

    @staticmethod
    def _distance(a, b):
        """Levenshtein algorithm for finding the nearest mapper for requested one"""
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

    _mappers = {
        # Expenditures' mappers
        '2.3.0.1.0.0': None,
        '2.2.0.1.1.0': None,
        '2.3.0.1.1.0': None,
        '2.5.0.1.1.0': None,
        '2.4.0.0.1.0': None,
        '2.3.0.1.0.1': None,
        '2.2.0.1.1.1': None,
        '2.3.0.1.1.1': None,
        '2.5.0.0.1.1': None,
        '2.4.0.0.1.1': None,

        # Profits' mappers
        '3.0.0.1.0.0': None,
        '3.2.0.1.0.0': None,
        '3.0.1.1.0.0': None,  # гд
        '3.2.1.1.0.0': None,  # гд
        '3.2.0.0.0.0': None,
        '3.2.1.0.0.0': None,  # гд-показатели исполнения бюджета
        '3.4.0.0.0.0': None,
        '3.4.1.0.0.0': None,  # гд-показатели исполнения бюджета
        '3.0.0.1.0.1': None,
        '3.2.0.1.0.1': None,
        '3.2.0.0.0.1': None,
        '3.2.1.0.0.1': None,  # гд
        '3.4.0.0.0.1': None,
        '3.4.1.0.0.1': None,  # гд

        # Deficit/surplus's mappers
        '4.2.0.0.0.0': None,
        '4.4.0.0.0.0': None,
        '4.0.0.1.0.0': None,
        '4.0.0.1.0.1': None,
        '4.2.0.1.0.1': None,
        '4.4.0.0.0.1': None
    }

    # Outer codes for substitution in MDX-query
    _places = {
        'Российская  Федерация': 2,
        'Крымский федеральный округ': 91128,
        'Республика Крым': 91129,
        'г. Севастополь': 91139,
        'г. Байконур': 93015,
        'Северо-Кавказский федеральный округ': 24604,
        'Ставропольский край': 3086,
        'Республика Ингушетия': 2135,
        'Республика Дагестан': 4,
        'Кабардино-Балкарская Республика': 2374,
        'Республика Северная Осетия - Алания': 2507,
        'Карачаево-Черкесская Республика': 1354,
        'Чеченская республика': 2136,
        'Южный федеральный округ': 3,
        'Краснодарский край': 749,
        'Астраханская область': 1176,
        'Волгоградская область': 1512,
        'Ростовская область': 2622,
        'Республика Адыгея (Адыгея)': 1451,
        'Республика Калмыкия': 2006,
        'Приволжский федеральный округ': 3417,
        'Нижегородская область': 4439,
        'Кировская область': 7726,
        'Самарская область': 5140,
        'Оренбургская область': 5483,
        'Пензенская область': 9475,
        'Пермский край': 24541,
        'Саратовская область': 8860,
        'Ульяновская область': 6097,
        'Республика Башкортостан': 3418,
        'Республика Марий Эл': 9301,
        'Республика Мордовия': 7265,
        'Республика Татарстан (Татарстан)': 6265,
        'Удмуртская республика': 9907,
        'Чувашская Республика - Чувашия': 8208,
        'Северо-Западный федеральный округ': 10249,
        'Архангельская область': 11867,
        'Ненецкий автономный округ': 10575,
        'Вологодская область': 10809,
        'Калининградская область': 10293,
        'г. Санкт-Петербург': 11755,
        'Ленинградская область': 11404,
        'Мурманская область': 10250,
        'Новгородская область': 11182,
        'Псковская область': 10330,
        'Республика Карелия': 11627,
        'Республика Коми': 10597,
        'Сибирский федеральный округ': 12097,
        'Алтайский край': 13781,
        'Красноярский край': 15777,
        'Иркутская область': 12232,
        'Кемеровская область': 14580,
        'Новосибирская область': 14804,
        'Омская область': 13356,
        'Томская область': 15593,
        'Забайкальский край': 24584,
        'Республика Бурятия': 15295,
        'Республика Алтай': 12792,
        'Республика Тыва': 12649,
        'Республика Хакасия': 12130,
        'Уральский федеральный округ': 16333,
        'Курганская область': 16921,
        'Свердловская область': 16827,
        'Тюменская область': 16507,
        'Ханты-Мансийский автономный округ - Югра': 16334,
        'Ямало-Ненецкий автономный округ': 16448,
        'Челябинская область': 17380,
        'Центральный федеральный округ': 19099,
        'Белгородская область': 22729,
        'Брянская область': 22143,
        'Владимирская область': 21258,
        'Воронежская область': 23249,
        'Ивановская область': 23067,
        'Тверская область': 21386,
        'Калужская область': 20350,
        'Костромская область': 20774,
        'Курская область': 19479,
        'Липецкая область': 20018,
        'г. Москва': 23783,
        'Московская область': 19100,
        'Орловская область': 24262,
        'Рязанская область': 22433,
        'Смоленская область': 21792,
        'Тамбовская область': 23909,
        'Тульская область': 21078,
        'Ярославская область': 20670,
        'Дальневосточный федеральный округ': 17698,
        'Приморский край': 18354,
        'Хабаровский край': 18540,
        'Амурская область': 18776,
        'Камчатский край': 24543,
        'Магаданская область': 18239,
        'Сахалинская область': 18294,
        'Чукотский автономный округ': 18184,
        'Республика Саха (Якутия)': 17699,
        'Еврейская автономная область': 18317
    }


class Result:
    def __init__(self, request='', status=False, message='', mapper='', response=''):
        self.request = request
        self.status = status
        self.message = message
        self.mapper = mapper
        self.response = response


M2Retrieving.get_data('Доходы,null,null,2010,jjj,jjj')
