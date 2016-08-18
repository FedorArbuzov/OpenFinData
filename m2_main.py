import requests
import datetime
from m1_req import distance
from m2_lib import mappers
from m2_lib import param2
from m2_lib import sphere
from m2_lib import places
from m2_lib import places_cld
from m2_lib import feedback


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

        # Find MDX-sampler for formed mapper
        mdx_skeleton = M2Retrieving.__get_mdx_skeleton_for_mapper(mapper, params, response)

        # Escaping this method if no mdx skeleton for current mapper is found
        if mdx_skeleton == 0 or mdx_skeleton is None:
            return response

        # Forming POST-data (cube and query) for request
        mdx_cube_and_query = M2Retrieving.__refactor_mdx_skeleton(mdx_skeleton, params, mapper)

        # Sending request
        M2Retrieving.__send_mdx_request(mdx_cube_and_query[0], mdx_cube_and_query[1], response)

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
                exp_differ = True
        else:
            response.message = 'Неверно выбрана предметная область😏 Попробуйте еще раз /search'
            return response

        # Processing param1
        if parameters[1] in codes[1]:
            mapper += str(codes[1].get(parameters[1])) + '.'
        else:
            response.message = 'Неверно выбрана 1я характеристика предметной области (' + \
                               parameters[1] + '). Попробуйте еще раз /search'
            return response

        # Processing param2
        if parameters[2] == 'null':
            mapper += '0.'
        elif parameters[2] in param2:
            mapper += '1.'
        else:
            message = 'Параметр "' + parameters[2] + '" не верен. ' \
                                                     'Допустимые значения: "все", ' \
                                                     '"налоговый" и "неналоговый"'
            response.message = message
            return response

        # Processing year
        now_year = datetime.datetime.now().year
        if parameters[3] == 'null':
            mapper += '0.'
        else:
            # Refactoring input year parameter if year is defined only by 1 or 2 last numbers
            year_len = len(parameters[3])
            if year_len == 1 or year_len == 2:
                parameters[3] = '2' + '0'*(3-year_len) + parameters[3]

            if 2006 < int(parameters[3]) < now_year:
                mapper += '1.'
            else:
                response.message = 'Введите год из промежутка c 2007 по ' + str(datetime.datetime.now().year - 1) + '🙈'
                return response

        # Processing sphere
        if exp_differ is True:
            mapper += '1.'
        else:
            if exp_differ is False and parameters[4] in sphere:
                mapper += '0.'
            else:
                response.message = 'Неверно указана сфера ("' + parameters[4] + '"). Попробуйте еще раз /search'
                return response

        # Processing territory
        if parameters[5] == 'null':
            mapper += '0'
        elif parameters[5] in places:
            mapper += '1'
        else:
            response.message = 'Неверно указана территория ("' + parameters[4] + '"). Попробуйте еще раз /search'
            return response

        return mapper

    @staticmethod
    def __get_mdx_skeleton_for_mapper(mapper, params, response):
        """Finding MDX sampler for mapper"""

        mdx_skeleton = mappers.get(mapper, 0)

        # Processing error message for which MDX-query is not ready yet
        if mdx_skeleton is None:
            response.message = 'Данный запрос еще в стадии разработки'

        # Finding the nearest mapper to given and forming response
        if mdx_skeleton == 0:
            message = 'Запрос чуть-чуть некорректен🤔 Пожалуйста, подправьте его, выбрав ' \
                      'один из предложенных вариантов:\r\n'
            index = 1
            for i in list(mappers.keys()):
                if distance(i, mapper) == 1:
                    message += '- ' + M2Retrieving.__hint(i, mapper, params)
                    index += 1
            if index == 1:
                message = 'В запросе неверно несколько параметров: попробуйте изменить запрос.   '

            response.message = feedback(params) + '\n\n' + message[:-2] + '\n Жмите /search'

        return mdx_skeleton

    @staticmethod
    def __refactor_mdx_skeleton(mdx_skeleton, params, mapper):
        """Replacing marks in MDX samplers by real data"""

        mdx_cube_and_query = []

        # Defining name of the cube from MDX-query
        query_by_elements = mdx_skeleton.split(' ')
        from_element = query_by_elements[query_by_elements.index('FROM') + 1]
        cube = from_element[1:len(from_element) - 4]

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
                        data = param2[params[param_id]][1]
                    else:
                        data = param2[params[param_id]][0]

                # Replacing year
                if param_id == 3:
                    data = str(params[param_id])

                # Replacing sphere
                if param_id == 4:
                    data = sphere[params[param_id]]

                # Replacing territory
                if param_id == 5:
                    if 'CLDO02' in mdx_skeleton:
                        data = '08-' + places_cld[params[param_id]]
                    else:
                        data = '08-' + places[params[param_id]]

                # Replacing mark by parameter
                mdx_skeleton = mdx_skeleton.replace(star, data)

                # Cutting temp in order ro find next mark
                temp = temp[i + 1:]

        # Adding cube and MDX-query
        mdx_cube_and_query.append(cube)
        mdx_cube_and_query.append(mdx_skeleton)

        return mdx_cube_and_query

    @staticmethod
    def __send_mdx_request(data_mart_code, mdx_query, response):
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
            'год (по умолчанию данные ' + str(datetime.datetime.now().year) + " г.)",
            'конкретную сферу',
            'конкретный регион'
        )

        items1, items2 = true_mapper.split('.'), false_mapper.split('.')
        error_message = ''
        count = 0

        # TODO: Check hint algorithm
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
                            error_message = 'Не указывайте параметр "' + params[count][:-2] + '"ые\r\n'

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


class Result:
    def __init__(self, status=False, message='', response='', theme=''):
        self.status = status
        self.message = message
        self.response = response
        self.theme = theme
