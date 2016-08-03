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
            # print('Mapper: ' + response.mapper)
            # print('Status: ' + str(response.status))
            # print('Message: ' + str(response.message))
            # print('Response: ' + response.response)
            return response

        # Find MDX-sampler for formed mapper
        mdx_skeleton = M2Retrieving._get_mdx_skeleton_for_mapper(response)

        # Escaping this method if no mdx skeleton for current mapper is found
        if mdx_skeleton == 0 or mdx_skeleton is None:
            # print('Mapper: ' + response.mapper)
            # print('Status: ' + str(response.status))
            # print('Message: ' + str(response.message))
            # print('Response: ' + response.response)
            return response

        # Forming POST-data (cube and query) for request
        mdx_cube_and_query = M2Retrieving._refactor_mdx_skeleton(mdx_skeleton, params)

        # Sending request
        M2Retrieving._send_mdx_request(mdx_cube_and_query[0], mdx_cube_and_query[1], response)

        # Displaying data for testing
        # print('Mapper: ' + response.mapper)
        # print('Status: ' + str(response.status))
        # print('Message: ' + str(response.message))
        # if response.status is False:
        #     print('Response: ' + response.response)
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

        response.mapper = mapper[:len(mapper) - 1]

        return response

    @staticmethod
    def _get_mdx_skeleton_for_mapper(response):
        """Finding MDX sampler for mapper"""

        mdx_skeleton = M2Retrieving._mappers.get(response.mapper, 0)

        # Processing error message for which MDX-query is not ready yet
        if mdx_skeleton is None:
            response.message = 'Данный запрос еще в стадии разработки'

        # Finding the nearest mapper to given and forming response
        if mdx_skeleton == 0:
            index = 1
            message2 = "Возможные варианты:\r\n"
            message1 = "Введенные параметры:\r\n" + M2Retrieving._mapper_to_words(response.mapper)

            for i in list(M2Retrieving._mappers.keys()):
                if M2Retrieving._distance(i, response.mapper) == 1:
                    message2 += str(index) + '.' + M2Retrieving._mapper_to_words(i) + '\r\n'
                    index += 1
            if index == 1:
                message2 = 'В запросе неверно несколько параметров. Попробуйте изменить запрос.   '
            response.message = message1 + '\r\nДанный запрос некорректен:(\r\n' + message2[:-3]

        return mdx_skeleton

    @staticmethod
    def _refactor_mdx_skeleton(mdx_skeleton, params):
        """Replacing marks in MDX samplers by real data"""

        # Codes for substitution in final MDX-query
        _codes = (
            {
                'null': '[RZPR].[14-848223],[RZPR].[14-413284],[RZPR].[14-850484],[RZPR].[14-848398],'
                        '[RZPR].[14-848260],[RZPR].[14-1203414],[RZPR].[14-848266],[RZPR].[14-848294],'
                        '[RZPR].[14-848302],[RZPR].[14-848345],[RZPR].[14-1203401],[RZPR].[14-413259],'
                        '[RZPR].[14-413264],[RZPR].[14-413267],[RZPR].[14-1203208],[RZPR].[14-1203195]',

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
                                               '[RZPR].[14-413268],[RZPR].[14-413269],[RZPR].[14-413270]'
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
                # TODO: Доделать показатели бюджета для CLDO01.DB
                if param_id == 2:  # Replacing property2
                    data = _codes[1].get(params[param_id])
                if param_id == 3:  # Replacing year
                    data = str(params[param_id])
                if param_id == 4:
                    data = _codes[0].get(params[param_id])
                if param_id == 5:  # Replacing territory
                    data = '08-' + M2Retrieving._places[params[param_id]]

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
        words = ''

        items = mapper.split('.')
        index = 0
        for i in items:
            words += _codes[index].get(int(i)) + '*'
            index += 1
        return words[:len(words) - 1]

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
        '2.3.0.1.0.0': 'SELECT {[Measures].[VALUE]} ON COLUMNS, {*4} ON ROWS FROM [EXYR03.DB] WHERE ([BGLevels].[09-1],[Years].[*3],[Marks].[03-4])',
        '2.2.0.1.1.0': 'SELECT {[Measures].[VALUE]} ON COLUMNS, {*4} ON ROWS FROM [EXYR03.DB] WHERE ([BGLevels].[09-1],[Years].[*3],[Marks].[03-3])',
        '2.3.0.1.1.0': 'SELECT {[Measures].[VALUE]} ON COLUMNS, {*4} ON ROWS FROM [EXYR03.DB] WHERE ([BGLevels].[09-1],[Years].[*3],[MARKS].[03-4])',
        '2.5.0.1.1.0': 'SELECT {[Measures].[VALUE]} ON COLUMNS, {*4} ON ROWS FROM [EXDO01.DB] WHERE ([BGLevels].[09-1],[Marks].[03-3])',
        '2.4.0.0.1.0': 'SELECT {[Measures].[VALUE]} ON COLUMNS, {*4} ON ROWS FROM [EXDO01.DB] WHERE ([BGLevels].[09-1],[Marks].[03-4])',

        '2.3.0.1.0.1': 'SELECT {[Measures].[VALUE]} ON COLUMNS, {*4} ON ROWS FROM [EXYR03.DB] WHERE ([BGLevels].[09-3],[Years].[*3],[Territories].[*5],[Marks].[03-4])',
        '2.2.0.1.1.1': 'SELECT {[Measures].[VALUE]} ON COLUMNS, {*4} ON ROWS FROM [EXYR03.DB] WHERE ([BGLevels].[09-3],[Years].[*3],[Territories].[*5],[Marks].[03-3])',
        '2.3.0.1.1.1': 'SELECT {[Measures].[VALUE]} ON COLUMNS, {*4} ON ROWS FROM [EXYR03.DB] WHERE ([BGLevels].[09-3],[Years].[*3],[Territories].[*5],[Marks].[03-4])',
        '2.5.0.0.1.1': 'SELECT {[Measures].[VALUE]} ON COLUMNS, {*4} ON ROWS FROM [EXDO01.DB] WHERE ([BGLevels].[09-3],[Territories].[*5],[Marks].[03-3])',
        '2.4.0.0.1.1': 'SELECT {[Measures].[VALUE]} ON COLUMNS, {*4} ON ROWS FROM [EXDO01.DB] WHERE ([BGLevels].[09-3],[Territories].[*5],[Marks].[03-4])',

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
        '4.4.0.0.0.0': None,
        '4.2.0.0.0.0': None,
        '4.0.0.1.0.0': 'SELECT {[Measures].[VALUE]} ON COLUMNS FROM [FSYR01.DB] WHERE ([BGLevels].[09-1], [Marks].[03-6],[Years].[*3])',
        '4.0.0.1.0.1': 'SELECT {[Measures].[VALUE]}  ON COLUMNS FROM [FSYR01.DB] WHERE ([BGLevels].[09-3],[Years].[*3],[Territories].[*5],[Marks].[03-6])',
        '4.2.0.0.0.1': None,
        '4.4.0.0.0.1': None
    }

    # Outer codes for substitution in MDX-query
    _places = {
        'байконур': '93015',
        'приволжский': '3417',
        'северо-западный': '10249',
        'сибирский': '12097',
        'уральский': '16333',
        'центральный': '19099',
        'амурская': '67708',
        'еврейская': '67705',
        'камчатский': '67728',
        'магаданская': '67703',
        'приморский': '67706',
        'саха': '67642',
        'якутия': '67642',
        'сахалинская': '67704',
        'хабаровский': '67707',
        'чукотский': '67640',
        'дальневосточный': '17698',
        'севастополь': '93011',
        'крым': '93010',
        'крымский': '91128',
        'кировская': '67663',
        'нижегородская': '67656',
        'оренбургская': '67659',
        'пензенская': '67667',
        'пермский': '67727',
        'башкортостан': '67655',
        'марий эл': '67666',
        'мордовия': '67662',
        'татарстан': '67661',
        'самарская': '67658',
        'саратовская': '67665',
        'удмуртская': '67668',
        'ульяновская': '67660',
        'чувашская': '67664',
        'чувашия': '67664',
        'архангельская': '67678',
        'вологодская': '67674',
        'санкт-петербург': '67639',
        'калининградская': '67670',
        'ленинградская': '67676',
        'мурманская': '67669',
        'ненецкий': '67672',
        'новгородская': '67675',
        'псковская': '67671',
        'карелия': '67677',
        'коми': '67673',
        'кабардино-балкарская': '67651',
        'карачаево-черкесская': '67638',
        'дагестан': '67643',
        'ингушетия': '67649',
        'осетия': '67652',
        'алания': '67652',
        'ставропольский': '67654',
        'чеченская': '67650',
        'северо-кавказский': '24604',
        'алтайский': '67688',
        'забайкальский': '67729',
        'иркутская': '67682',
        'кемеровская': '67689',
        'красноярский': '67694',
        'новосибирская': '67690',
        'омская': '67687',
        'алтай': '67684',
        'бурятия': '67691',
        'тыва': '67683',
        'хакасия': '67681',
        'томская': '67692',
        'курганская': '67699',
        'свердловская': '67698',
        'тюменская': '67697',
        'ханты-мансийский': '67695',
        'югра': '67695',
        'челябинская': '67700',
        'ямало-ненецкий': '67696',
        'белгородская': '67721',
        'брянская': '67719',
        'владимирская': '67716',
        'воронежская': '67723',
        'москва': '67724',
        'ивановская': '67722',
        'калужская': '67712',
        'костромская': '67714',
        'курская': '67710',
        'липецкая': '67711',
        'московская': '67709',
        'орловская': '67726',
        'рязанская': '67720',
        'смоленская': '67718',
        'тамбовская': '67725',
        'тверская': '67717',
        'тульская': '67715',
        'ярославская': '67713',
        'астраханская': '67645',
        'волгоградская': '67647',
        'краснодарский': '67644',
        'адыгея': '67646',
        'калмыкия': '67648',
        'ростовская': '67653',
        'южный': '3',
        'российская федерация': '2',
        'россия': 2,
        'рф': 2
    }


class Result:
    def __init__(self, status=False, message='', mapper='', response=''):
        self.status = status
        self.message = message
        self.mapper = mapper
        self.response = response

# Testing expenditures
# print(1)
# M2Retrieving.get_data('расходы,фактический,null,2011,null,null')
# print(2)
# M2Retrieving.get_data('расходы,плановый,null,2012,образование,null')
# print(3)
# M2Retrieving.get_data('расходы,фактический,null,2013,национальная оборона,null')
# print(4)
# M2Retrieving.get_data('расходы,запланированный,null,2014,физическая культура и спорт,null')
# print(5)
# M2Retrieving.get_data('расходы,текущий,null,null,общегосударственные вопросы,null')
# print(6)
# M2Retrieving.get_data('расходы,фактический,null,2010,null,республика крым')
# print(7)
# M2Retrieving.get_data('расходы,плановый,null,2009,образование,г. севастополь')
# print(8)
# M2Retrieving.get_data('расходы,фактический,null,2010,null,пермский край')
# print(9)
# M2Retrieving.get_data('расходы,запланированный,null,null,здравоохранение,г. санкт-петербург')
# print(10)
# M2Retrieving.get_data('расходы,текущий,null,null,охрана окружающей среды,республика коми')
