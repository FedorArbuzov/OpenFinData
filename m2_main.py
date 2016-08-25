import requests
import datetime
from m1_req import distance
import constants


# Module, which is responsible for getting required from user data
class M2Retrieving:
    @staticmethod
    def get_data(input_string):
        """Getting JSON data based on input parameters"""

        # Splitting input string in parameters: [Theme, Property, Property2, Year, Sphere, Territory]
        params = input_string.split(',')

        # Creating response object
        response = Result()

        # Creating mapper based on list of parameters
        mapper = M2Retrieving.__list_to_mapper(params, response)

        if response.message != "":
            return response

        print(params)
        print(mapper)
        # Find MDX-sampler for formed mapper
        mdx_skeleton = M2Retrieving.__get_mdx_skeleton_for_mapper(mapper, params, response)

        # Escaping this method if no mdx skeleton for current mapper is found
        if mdx_skeleton == 0 or mdx_skeleton is None:
            return response

        # Forming POST-data (cube and query) for request
        mdx_cube_and_query = M2Retrieving.__refactor_mdx_skeleton(mdx_skeleton, params, mapper, response)

        # Sending request
        M2Retrieving.__send_mdx_request(mdx_cube_and_query[0], mdx_cube_and_query[1], response, params)
        return response

    @staticmethod
    def __list_to_mapper(parameters, response):
        """Refactoring input parameters in mapper"""

        # Inner codes for refactoring list in mapper
        codes = (
            {
                'расходы': 2,
                'доходы': 3,
                'дефицит': 4,
            },

            {
                'null': 3,  # By default is "фактический"
                'плановый': 2,
                'фактический': 3,
                'текущий': 4
            }
        )

        mapper = ''

        # TODO: refactor processing of mapper
        # Processing theme
        exp_differ = False
        if parameters[0] in codes[0]:
            mapper += str(codes[0].get(parameters[0])) + '.'
            response.theme = parameters[0]
            if mapper == '2.':
                exp_differ = True  # Marking expenditure request
        else:
            response.message = 'Неверно выбрана предметная область😏 Попробуйте еще раз /search'
            return

        # Processing param1
        if parameters[1] in codes[1]:
            mapper += str(codes[1].get(parameters[1])) + '.'
        else:
            response.message = 'Что-то пошло не так🙃 Проверьте ваш запрос на корректность'
            return

        # Processing param2
        if parameters[2] == 'null':
            mapper += '0.'
        elif parameters[2] in constants.PARAM2:
            mapper += '1.'
        else:
            response.message = 'Что-то пошло не так🙃 Проверьте ваш запрос на корректность'
            return

        # Processing year
        now_year = datetime.datetime.now().year
        if parameters[3] == 'null':
            mapper += '0.'

            # Refactoring 'Фактические' in 'текущие'
            if mapper[2] == '3':
                mapper = mapper[:2] + '4.' + mapper[4:]
                parameters[1] = 'текущий'
        else:
            # Refactoring input year parameter if year is defined only by 1 or 2 last numbers
            year_len = len(parameters[3])
            if year_len == 1 or year_len == 2:
                parameters[3] = '2' + '0' * (3 - year_len) + parameters[3]

            if 2006 < int(parameters[3]) <= now_year:
                # Processing 2016 year
                if parameters[3] == '2016':
                    mapper += '0.'

                    # Refactoring 'Фактические' in 'текущие'
                    if mapper[2] == '3':
                        mapper = mapper[:2] + '4.' + mapper[4:]
                        parameters[1] = 'текущий'
                else:
                    mapper += '1.'
            else:
                response.message = 'Введите год из промежутка c 2007 по ' + str(datetime.datetime.now().year) + '🙈'
                return

        # Processing sphere
        if exp_differ is True and parameters[4] in constants.SPHERES:
            mapper += '1.'
        elif exp_differ is False and parameters[4] in constants.SPHERES:
            mapper += '0.'
        else:
            response.message = 'Что-то пошло не так🙃 Проверьте ваш запрос на корректность'
            return

        # Processing territory
        if parameters[5] == 'null':
            mapper += '0'
        elif parameters[5] in constants.PLACES:
            mapper += '1'
        else:
            response.message = 'Что-то пошло не так🙃 Проверьте ваш запрос на корректность'
            return

        return mapper

    @staticmethod
    def __get_mdx_skeleton_for_mapper(mapper, params, response):
        """Finding MDX sampler for mapper"""

        mdx_skeleton = constants.MAPPERS.get(mapper, 0)

        # Processing error message for which MDX-query is not ready yet
        # if mdx_skeleton is None:
        #     response.message = 'Данный запрос еще в стадии разработки'

        # Finding the nearest mapper to given and forming response
        if mdx_skeleton == 0:
            message = 'Запрос чуть-чуть некорректен🤔 Пожалуйста, подправьте его, выбрав ' \
                      'один из предложенных вариантов:\r\n'
            index = 1
            for i in list(constants.MAPPERS.keys()):
                if distance(i, mapper) == 1:
                    message += '- ' + M2Retrieving.__hint(i, mapper, params)
                    index += 1
            if index == 1:
                message = 'В запросе неверно несколько параметров: попробуйте изменить запрос.   '

            response.message = M2Retrieving.feedback(params) + '\n\n' + message[:-2] + '\n Жмите /search'

        return mdx_skeleton

    @staticmethod
    def __refactor_mdx_skeleton(mdx_skeleton, params, mapper, response):
        """Replacing marks in MDX samplers by real data"""

        mdx_cube_and_query = []

        # Defining name of the cube from MDX-query
        query_by_elements = mdx_skeleton.split(' ')
        from_element = query_by_elements[query_by_elements.index('FROM') + 1]
        cube = from_element[1:len(from_element) - 4]

        # Creating marker for displaying results about deficit/surplus
        if cube == 'FSYR01':
            response.theme = '1' + response.theme
        else:
            response.theme = '0' + response.theme

        # If there are marks for substitution in MDX-sampler
        if '*' in mdx_skeleton:
            temp = mdx_skeleton
            while temp.find('*') != -1:
                i = temp.find('*')
                star = temp[i:i + 2]
                param_id = int(star[1])

                # Forming output param instead of *2, *3, *4, *5
                # Replacing property2
                if param_id == 2:
                    if mapper in ('3.2.1.0.0.0', '3.4.1.0.0.0'):
                        data = constants.PARAM2[params[param_id]][1]
                    else:
                        data = constants.PARAM2[params[param_id]][0]

                # Replacing year
                if param_id == 3:
                    data = str(params[param_id])

                # Replacing sphere
                if param_id == 4:
                    data = constants.SPHERES[params[param_id]]

                # Replacing territory
                if param_id == 5:
                    if 'CLDO02' in mdx_skeleton:
                        data = '08-' + constants.PLACES_FOR_CLDO02[params[param_id]]
                    else:
                        data = '08-' + constants.PLACES[params[param_id]][0]

                # Replacing mark by parameter
                mdx_skeleton = mdx_skeleton.replace(star, data)

                # Cutting temp in order ro find next mark
                temp = temp[i + 1:]

        # Adding cube and MDX-query
        mdx_cube_and_query.append(cube)
        mdx_cube_and_query.append(mdx_skeleton)

        return mdx_cube_and_query

    @staticmethod
    def __send_mdx_request(data_mart_code, mdx_query, response, params):
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
        response.message = M2Retrieving.feedback(params)
        response.response = r.text

    @staticmethod
    def __hint(true_mapper, false_mapper, params):
        """Transfer in words steps which should be made in order to form correct request"""

        # Inner codes for refactoring difference between correct and incorrect mapper in help message
        codes = (
            {
                2: 'расходы',
                3: 'доходы',
                4: 'профицит/дефицит',
            },
            {
                2: 'плановый',
                3: 'фактический',
                4: 'текущий'
            },
            'налоговые/неналоговые',
            'год (отличный от ' + str(datetime.datetime.now().year) + " г.)",
            'конкретную сферу',
            'конкретный регион'
        )

        items1, items2 = true_mapper.split('.'), false_mapper.split('.')
        error_message = ''
        count = 0

        for i1, i2 in zip(items1, items2):
            if i1 != i2:
                i1 = int(i1)
                i2 = int(i2)

                # If error is in existence or absence of parameter (without considering param1)
                if (i1 == 0 or i1 == 1) and count != 1:

                    # If parameter is not given but should be
                    if i1 > i2:
                        error_message = 'Укажите ' + codes[count] + '\r\n'

                        # If error is in param2
                        if count == 2:
                            error_message = 'Укажите параметр "' + codes[count] + '"\r\n'

                    # If parameter is given but should not be
                    else:
                        error_message = 'Не указывайте ' + codes[count] + '\r\n'

                        # If error is in param2
                        if count == 2:
                            error_message = 'Не указывайте параметр "' + params[count][:-2] + 'ые"\r\n'

                # If parameter exist but should be another or error is in param1
                else:

                    # If there is no param1 but should be
                    if i2 == 0 and count == 1:
                        error_message = 'Добавьте параметр "' + codes[count].get(i1) + '"\r\n'
                    # If there is param1 but should not be
                    elif i1 == 0 and count == 1:
                        error_message = 'Не указывайте параметр "' + codes[count].get(i2) + '"\r\n'
                    else:
                        error_message = 'Замените параметр "' + codes[count].get(i2) + \
                                        '" на "' + codes[count].get(i1) + '"\r\n'
            count += 1

        return error_message

    @staticmethod
    def feedback(params):
        """Forming response how we have understood user's request"""
        # TODO: Refactor code

        if params[0] == "дефицит":
            theme = " дефицит/профицит"

            if params[1] == "null":
                param_1 = "Фактический"
            else:
                param_1 = params[1][0].upper() + params[1][1:]

            if params[3] == "null":
                if param_1 == 'Плановый':
                    year = ' в 2016 году'
                else:
                    year = ''
            else:
                year = " в " + params[3] + " году"

            if params[5] == "null":
                territory = " федерального бюджета"
            else:
                territory = ' ' + constants.PLACES[params[5]][1]

            response = param_1 + theme + territory + year
        else:
            theme = " " + params[0]

            if params[1] == "null":
                param_1 = "Фактические"
            else:
                param_1 = params[1][0].upper() + params[1][1:-1] + "е"

            if params[2] == "null":
                param_2 = ""
            else:
                param_2 = " " + params[2][:-1] + "е"

            if params[3] == "null":
                if param_1 == 'Плановые':
                    year_3 = ' в 2016 году'
                else:
                    year_3 = ''
            else:
                year_3 = " в " + params[3] + " году"

            if params[4] == "null":
                sphere_4 = ""
            else:
                spheres = {
                    '2': 'общегосударственные вопросы',
                    '3': 'национальную оборону',
                    '4': 'национальную безопасность и правоохранительную деятельность',
                    '5': 'национальную экономику',
                    '6': 'жилищно-коммунальное хозяйство',
                    '7': 'охрану окружающей среды',
                    '8': 'образование',
                    '9': 'культуру и кинематографию',
                    '10': 'здравоохранение',
                    '11': 'социальную политику',
                    '12': 'спорт'
                }
                sphere_4 = " на " + spheres.get(params[4])

            if params[5] == "null":
                territory = " федерального бюджета"
            else:
                territory = ' ' + constants.PLACES[params[5]][1]

            response = param_1 + param_2 + theme + territory + sphere_4 + year_3

        return 'Я понял ваш запрос как: "' + response + '".'


class Result:
    def __init__(self, status=False, message='', response='', theme=''):
        self.status = status
        self.message = message
        self.response = response
        self.theme = theme
