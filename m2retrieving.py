from datetime import datetime
import requests


# Module, which is responsible for getting required from user data
class M2Retrieving:
    @staticmethod
    def get_data(input_string):
        """Getting JSON data based on input parameters"""

        # Splitting input string in parameters
        params = input_string.split(',')  # [Theme, Property, Property2, Year, Sphere, Territory]

        # Creating response object
        response = Result()

        # Creating mapper based on list of parameters
        response = M2Retrieving._list_to_mapper(params, response)

        if response.message != "":
            return response

        # Find MDX-sampler for formed mapper
        mdx_skeleton = M2Retrieving._get_mdx_skeleton_for_mapper(response)

        # Escaping this method if no mdx skeleton for current mapper is found
        if mdx_skeleton == 0 or mdx_skeleton is None:
            return response

        # Forming POST-data (cube and query) for request
        mdx_cube_and_query = M2Retrieving._refactor_mdx_skeleton(mdx_skeleton, params)

        # Sending request
        M2Retrieving._send_mdx_request(mdx_cube_and_query[0], mdx_cube_and_query[1], response)

        # Displaying data for testing
        print('Mapper: ' + response.mapper)
        print('Status: ' + str(response.status))
        print('Message: ' + str(response.message))
        print('Response: ' + response.response)
        return response

    @staticmethod
    def _list_to_mapper(parameters, response):
        """Refactoring input parameters in mapper"""

        # Inner codes for refactoring list in mapper
        _codes = (
            {
                'расходы': 2,
                'доходы': 3,
                'дефицит': 4,
                'профицит': 4
            },

            {
                'плановый': 2,
                'фактический': 3,
                'текущий': 4,
                'запланированный': 5
            },

            {
                'налоговый': 1,
                'неналоговый': 1
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

        i = 3
        while i < 6:
            if parameters[i] == 'null':
                mapper += '0.'
            else:
                mapper += '1.'
            i += 1

        response.mapper = mapper

        return response

    @staticmethod
    def _get_mdx_skeleton_for_mapper(response):
        """Finding MDX sampler for mapper"""

        mdx_skeleton = _mappers.get(response.mapper, 0)

        # Processing error message for which MDX-query is not ready yet
        if mdx_skeleton is None:
            response.message = 'Данный запрос еще в стадии разработки'

        # Finding the nearest mapper to given and forming response
        if mdx_skeleton == 0:
            index = 1
            message2 = "Возможные варианты:\r\n"
            message1 = "Введенные параметры:\r\n" + _mapper_to_words(response.mapper)

            for i in list(_mappers.keys()):
                if _distance(i, response.mapper) == 1:
                    message2 += str(index) + '.' + _mapper_to_words(i) + '\r\n'
                    index += 1

            response.message = message1 + '\r\nДанный запрос некорректен:(\r\n' + message2[:-3]

        return mdx_skeleton

    @staticmethod
    def _refactor_mdx_skeleton(mdx_skeleton, params):
        """Replacing marks in MDX samplers by real data"""

        # Codes for substitution in final MDX-query
        _codes = (
            {
                'общегосударственные вопросы': '[RZPR].[14-848223],[RZPR].[14-413272],[RZPR].[14-342647],'
                                               '[RZPR].[14-413273],[RZPR].[14-413274],[RZPR].[14-413275],'
                                               '[RZPR].[14-413276],[RZPR].[14-413277],[RZPR].[14-413278],'
                                               '[RZPR].[14-413279],[RZPR].[14-848224],[RZPR].[14-413281],'
                                               '[RZPR].[14-413282],[RZPR].[14-848249]',

                'национальная оборона': '[RZPR].[14-413284],[RZPR].[14-413285],[RZPR].[14-413286],[RZPR].[14-413287],'
                                        '[RZPR].[14-413288],[RZPR].[14-413289],[RZPR].[14-413290],[RZPR].[14-413291]',

                'национальная безопасность и правоохранительная деятельность': '[RZPR].[14-850484],[RZPR].[14-413293],'
                                                                               '[RZPR].[14-413294],[RZPR].[14-853732],'
                                                                               '[RZPR].[14-413296],[RZPR].[14-855436],'
                                                                               '[RZPR].[14-854333],[RZPR].[14-854342],'
                                                                               '[RZPR].[14-854482],[RZPR].[14-108129],'
                                                                               '[RZPR].[14-852920],[RZPR].[14-850760],'
                                                                               '[RZPR].[14-1203368],[RZPR].[14-853005],'
                                                                               '[RZPR].[14-850485]',

                'национальная экономика': '[RZPR].[14-848398],[RZPR].[14-848399],[RZPR].[14-1203160],'
                                          '[RZPR].[14-850771],[RZPR].[14-857652],[RZPR].[14-850172],'
                                          '[RZPR].[14-849065],[RZPR].[14-849070],[RZPR].[14-851151],'
                                          '[RZPR].[14-1203167],[RZPR].[14-1203168],[RZPR].[14-1203169],'
                                          '[RZPR].[14-848501]',

                'жилищно-коммунальное хозяйство': '[RZPR].[14-848260],[RZPR].[14-848261],[RZPR].[14-850428],'
                                                  '[RZPR].[14-1203187],[RZPR].[14-881303],[RZPR].[14-849768]',

                'охрана окружающей среды': '[RZPR].[14-1203414],[RZPR].[14-1203191],[RZPR].[14-872910],'
                                           '[RZPR].[14-872714],[RZPR].[14-848836]',

                'образование': '[RZPR].[14-872691],[RZPR].[14-848266],[RZPR].[14-848267],[RZPR].[14-849320],'
                               '[RZPR].[14-343261],[RZPR].[14-848274],[RZPR].[14-849333],[RZPR].[14-873227],'
                               '[RZPR].[14-850050],[RZPR].[14-849520],[RZPR].[14-849303]',

                'культура, кинематография': '[RZPR].[14-848294],[RZPR].[14-848295],[RZPR].[14-873473],'
                                            '[RZPR].[14-873499],[RZPR].[14-873512]',

                'здравоохранение': '[RZPR].[14-848302],[RZPR].[14-872659],[RZPR].[14-848317],[RZPR].[14-343881],'
                                   '[RZPR].[14-108717],[RZPR].[14-349151],[RZPR].[14-349155],[RZPR].[14-349159],'
                                   '[RZPR].[14-849621],[RZPR].[14-349163]',

                'социальная политика': '[RZPR].[14-848345],[RZPR].[14-349188],[RZPR].[14-349196],'
                                       '[RZPR].[14-848346],[RZPR].[14-874840],[RZPR].[14-851908],'
                                       '[RZPR].[14-849729]',

                'физическая культура и спорт': '[RZPR].[14-1203401],[RZPR].[14-850455],[RZPR].[14-866083],'
                                               '[RZPR].[14-850952],[RZPR].[14-413257],[RZPR].[14-413258],'
                                               '[RZPR].[14-413259],[RZPR].[14-413260],[RZPR].[14-851607],'
                                               '[RZPR].[14-413262],[RZPR].[14-413263],[RZPR].[14-413264],'
                                               '[RZPR].[14-413265],[RZPR].[14-413266],[RZPR].[14-413267],'
                                               '[RZPR].[14-413268],[RZPR].[14-413269],[RZPR].[14-413270],'
            },

            {
                'налоговый': '12',
                'неналоговый': '13'
            }
        )

        mdx_cube_and_query = []

        # If there are marks for substitution in MDX-sampler
        if '*' in mdx_skeleton:
            temp = mdx_skeleton
            while temp.find('*') != -1:
                i = temp.find('*')
                star = temp[i:i + 2]
                param_id = int(star[1])

                # Forming output param instead of *2, *3, *4, *5
                if param_id == 2:
                    data = _codes[0].get(params[param_id])
                if param_id == 3:
                    data = str(params[param_id])
                if param_id == 4:  # TODO: Доделать показатели бюджета для CLDO01.DB
                    data = _codes[1].get(params[param_id])
                if param_id == 5:
                    data = '08-' + _places[params[param_id]]

                # Replacing mark by parameter
                mdx_skeleton = mdx_skeleton.replace(star, data)

                # Cutting temp in order ro find next mark
                temp = temp[i + 1:]

        # Defining name of the cube from MDX-query
        query_by_elements = mdx_skeleton.split(' ')
        from_element = query_by_elements[query_by_elements.index('FROM') + 1]
        cube = from_element[1:len(from_element) - 4]

        # Adding cube and MDX-query
        mdx_cube_and_query.append(cube)
        mdx_cube_and_query.append(mdx_skeleton)

        return mdx_cube_and_query

    @staticmethod
    def _send_mdx_request(data_mart_code, mdx_query, response):
        """Sending POST request to remote server"""

        data = {'dataMartCode': data_mart_code, 'mdxQuery': mdx_query}
        r = requests.post('http://conf.test.fm.epbs.ru/mdxexpert/CellsetByMdx', data)

        # Processing if MDX-query fails
        if '"success": false' in r.text:
            response.message = 'Запрос не удался:('
            response.response = r.text
            return

        # Updating params of resulting object
        response.status = True
        response.message = 'OK'
        response.response = r.text


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
            0: 'Территория(пустой параметр)'
        }
    )

    # Output word construction
    words = '/'

    items = mapper.split('.')
    index = 0
    for i in items:
        words += _codes[index].get(int(i)) + '/'
        index += 1
    return words


@staticmethod
def _distance(a, b):
    """Levenshtein algorithm"""

    n, m = len(a), len(b)
    if n > m:
        a, b = b, a
        n, m = m, n
    current_row = range(n + 1)
    for i in range(1, m + 1):
        previous_row, current_row = current_row, [i] + [0] * n
        for j in range(1, n + 1):
            add, delete, change = previous_row[j] + 1, current_row[j - 1] + 1, previous_row[j - 1]
            if a[j - 1] != b[i - 1]:
                change += 1
            current_row[j] = min(add, delete, change)

    return current_row[n]

# Mappers for requests
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
    '4.4.0.0.0.0': 'SELECT {[Measures].[FACTBGYEAR]} ON COLUMNS FROM [CLDO01.DB]',
    '4.2.0.0.0.0': 'SELECT {[Measures].[PLANONYEAR]} ON COLUMNS FROM [CLDO01.DB]',
    '4.0.0.1.0.0': 'SELECT {[Measures].[VALUE]} ON COLUMNS FROM [FSYR01.DB] WHERE ([BGLevels].[09-3],[Years].[*3])',
    '4.0.0.1.0.1': 'SELECT {[Measures].[VALUE]} ON COLUMNS FROM [FSYR01.DB] WHERE ([BGLevels].[09-3],[Years].[*3],[Territories].[*5])',
    '4.2.0.0.0.1': 'SELECT {[Measures].[PLAN_ONYEAR]} ON COLUMNS FROM [CLDO02.DB] WHERE [TERRITORIES].[*5]',
    '4.4.0.0.0.1': 'SELECT {[Measures].[FACT_BGYEAR]}  ON COLUMNS FROM [CLDO02.DB] WHERE ([BGLevels].[09-3],[Territories].[*5])'
}

# Outer codes for substitution in MDX-query
_places = {
    'г. байконур': '93015',
    'приволжский федеральный округ': '3417',
    'северо-западный федеральный округ': '10249',
    'сибирский федеральный округ': '12097',
    'уральский федеральный округ': '16333',
    'центральный федеральный округ': '19099',
    'амурская область': '67708',
    'еврейская автономная область': '67705',
    'камчатский край': '67728',
    'магаданская область': '67703',
    'приморский край': '67706',
    'республика саха (якутия)': '67642',
    'сахалинская область': '67704',
    'хабаровский край': '67707',
    'чукотский автономный округ': '67640',
    'дальневосточный федеральный округ': '17698',
    'г. севастополь': '93011',
    'республика крым': '93010',
    'крымский федеральный округ': '91128',
    'кировская область': '67663',
    'нижегородская область': '67656',
    'оренбургская область': '67659',
    'пензенская область': '67667',
    'пермский край': '67727',
    'республика башкортостан': '67655',
    'республика марий эл': '67666',
    'республика мордовия': '67662',
    'республика татарстан (татарстан)': '67661',
    'самарская область': '67658',
    'саратовская область': '67665',
    'удмуртская республика': '67668',
    'ульяновская область': '67660',
    'чувашская республика - чувашия': '67664',
    'архангельская область': '67678',
    'вологодская область': '67674',
    'г. санкт-петербург': '67639',
    'калининградская область': '67670',
    'ленинградская область': '67676',
    'мурманская область': '67669',
    'ненецкий автономный округ': '67672',
    'новгородская область': '67675',
    'псковская область': '67671',
    'республика карелия': '67677',
    'республика коми': '67673',
    'кабардино-балкарская республика': '67651',
    'карачаево-черкесская республика': '67638',
    'республика дагестан': '67643',
    'республика ингушетия': '67649',
    'республика северная осетия - алания': '67652',
    'ставропольский край': '67654',
    'чеченская республика': '67650',
    'северо-кавказский федеральный округ': '24604',
    'алтайский край': '67688',
    'забайкальский край': '67729',
    'иркутская область': '67682',
    'кемеровская область': '67689',
    'красноярский край': '67694',
    'новосибирская область': '67690',
    'омская область': '67687',
    'республика алтай': '67684',
    'республика бурятия': '67691',
    'республика тыва': '67683',
    'республика хакасия': '67681',
    'томская область': '67692',
    'курганская область': '67699',
    'свердловская область': '67698',
    'тюменская область': '67697',
    'ханты-мансийский автономный округ - югра': '67695',
    'челябинская область': '67700',
    'ямало-ненецкий автономный округ': '67696',
    'белгородская область': '67721',
    'брянская область': '67719',
    'владимирская область': '67716',
    'воронежская область': '67723',
    'г. москва': '67724',
    'ивановская область': '67722',
    'калужская область': '67712',
    'костромская область': '67714',
    'курская область': '67710',
    'липецкая область': '67711',
    'московская область': '67709',
    'орловская область': '67726',
    'рязанская область': '67720',
    'смоленская область': '67718',
    'тамбовская область': '67725',
    'тверская область': '67717',
    'тульская область': '67715',
    'ярославская область': '67713',
    'астраханская область': '67645',
    'волгоградская область': '67647',
    'краснодарский край': '67644',
    'республика адыгея (адыгея)': '67646',
    'республика калмыкия': '67648',
    'ростовская область': '67653',
    'южный федеральный округ': '3',
    'российская федерация': '2'
}


class Result:
    def __init__(self, status=False, message='', mapper='', response=''):
        self.status = status
        self.message = message
        self.mapper = mapper
        self.response = response


M2Retrieving.get_data('дефицит,null,null,2012,null,Ростовская область')