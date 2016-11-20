import requests
import datetime
import data
from m1_req import DataParser
from db_creation import Parameter, ParameterType, ParameterMap, Theme, ThemeType, Query
from constants import ERROR_PARSING
from constants import ERROR_INCORRECT_YEAR
from constants import MSG_IN_DEVELOPMENT
from constants import ERROR_NO_DATA_GOT

EMPTY_INDICATOR = 'null'


# Module, which is responsible for getting required from user data
class M2Retrieving:
    @staticmethod
    def get_data(input_string, using_db=False):
        """Getting JSON data based on input parameters"""

        # Splitting input string in parameters: [Theme, Property, Property2, Year, Sphere, Territory]
        params = input_string.split(',')

        # Creating response object
        response = Result()

        # Creating mapper based on list of parameters
        if not using_db:
            mapper = M2Retrieving._list_to_mapper(params, response)
        else:
            mapper = M2Retrieving._get_param_set_from_db(params, response)

        # If response.message is not empty, notification of user about the error
        if response.message != "":
            return response

        if not using_db:
            print("M2: params - {}, mapper - {}".format(params, mapper))

        # Find MDX-sampler for formed mapper
        if not using_db:
            mdx_skeleton = M2Retrieving._get_mdx_skeleton_for_mapper(mapper, params, response)
        else:
            mdx_skeleton = M2Retrieving._get_template_query_from_db(mapper, params, response)

        # Escaping this method if no mdx skeleton for current mapper is found
        if mdx_skeleton == -1 or mdx_skeleton is None:
            return response

        # Forming POST-data (cube and query) for request
        mdx_cube_and_query = M2Retrieving._refactor_mdx_skeleton(mdx_skeleton, params, mapper, response)

        # Sending request
        M2Retrieving._send_mdx_request(mdx_cube_and_query[0], mdx_cube_and_query[1], response, params)
        return response

    @staticmethod
    def _list_to_mapper(parameters, response):
        """Refactoring input parameters in mapper"""

        NULL_VALUE = '0.'
        NOT_NULL_VALUE = '1.'

        mapper = ''

        # Processing theme
        exp_differ = False
        if parameters[0] in data.SUBJECT:
            mapper += data.SUBJECT[parameters[0]] + '.'
            response.theme = parameters[0]

            # Marking expenditure request
            if mapper == data.SUBJECT['расходы'] + '.':
                exp_differ = True
        else:
            response.message = ERROR_PARSING
            return

        # Processing param1
        if parameters[1] in data.TYPES:
            mapper += data.TYPES[parameters[1]] + '.'
        else:
            response.message = ERROR_PARSING
            return

        # Processing param2
        if parameters[2] == EMPTY_INDICATOR:
            mapper += NULL_VALUE
        elif parameters[2] in data.NALOG_NENALOG:
            mapper += NOT_NULL_VALUE
        else:
            response.message = ERROR_PARSING
            return

        # Processing year
        now_year = datetime.datetime.now().year
        if parameters[3] == EMPTY_INDICATOR:
            mapper += NULL_VALUE

            # Refactoring 'Фактические' in 'текущие' if year is null
            if mapper[2] == data.TYPES['фактический']:
                mapper = "{}{}.{}".format(mapper[:2], data.TYPES['текущий'], mapper[4:])
                parameters[1] = 'текущий'
        else:
            # Refactoring input year parameter if year is defined only by 1 or 2 last numbers
            year_len = len(parameters[3])
            if year_len == 1 or year_len == 2:
                parameters[3] = '2' + '0' * (3 - year_len) + parameters[3]

            if 2006 < int(parameters[3]) <= now_year:
                # Processing 2016 year
                if parameters[3] == str(now_year):
                    mapper += NULL_VALUE
                    parameters[3] = EMPTY_INDICATOR

                    # Refactoring 'Фактические' in 'текущие' if year is 2016
                    if mapper[2] == data.TYPES['фактический']:
                        mapper = "{}{}.{}".format(mapper[:2], data.TYPES['текущий'], mapper[4:])
                        parameters[1] = 'текущий'
                else:
                    mapper += NOT_NULL_VALUE
            else:
                response.message = ERROR_INCORRECT_YEAR % str(datetime.datetime.now().year)
                return

        # Processing sphere
        # Turning on sphere details for all requests about expenditures
        if exp_differ is True and parameters[4] in data.SPHERES:
            mapper += NOT_NULL_VALUE
        # Turning off sphere details for all other requests
        elif exp_differ is False and parameters[4] in data.SPHERES:
            mapper += NULL_VALUE
        else:
            response.message = ERROR_PARSING
            return

        # Processing territory
        if parameters[5] == EMPTY_INDICATOR:
            mapper += NULL_VALUE[:-1]
        elif parameters[5] in data.PLACES:
            mapper += NOT_NULL_VALUE[:-1]
        else:
            response.message = ERROR_PARSING
            return

        return mapper

    @staticmethod
    def _get_param_set_from_db(parameters, response):
        param_set = []

        # Processing theme
        exp_differ = False
        p1 = ThemeType.select().where(ThemeType.type == parameters[0])
        if len(p1):
            param_set.append(p1)

            # Marking expenditure request
            for _p1 in p1:
                if _p1.type == 'расходы':
                    exp_differ = True
        else:
            response.message = ERROR_PARSING
            return

        # Processing param1
        if parameters[1] == EMPTY_INDICATOR:
            p2 = ParameterType.select().where(ParameterType.type == 'фактический')
            param_set.append(p2)
        else:
            p2 = ParameterType.select().where(ParameterType.type == parameters[1])
            if len(p2):
                param_set.append(p2)
            else:
                response.message = ERROR_PARSING
                return

        # Processing param2
        if parameters[2] == EMPTY_INDICATOR:
            pass
        else:
            p3 = Parameter.select().where((Parameter.tagValue == parameters[2]) & (Parameter.type == 7))
            if len(p3):
                param_set.append(ParameterType.select().where(ParameterType.type == 'тип доходов'))
            else:
                response.message = ERROR_PARSING
                return

        # Processing year
        now_year = datetime.datetime.now().year
        if parameters[3] == EMPTY_INDICATOR:
            # Refactoring 'Фактические' in 'текущие' if year is null
            for param in p2:
                if param.type == 'фактический':
                    del param_set[1]
                    param_set.append(ParameterType.select().where(ParameterType.type == 'текущий'))
                    parameters[1] = 'текущий'
        else:
            # Refactoring input year parameter if year is defined only by 1 or 2 last numbers
            year_len = len(parameters[3])
            if year_len == 1 or year_len == 2:
                parameters[3] = '2' + '0' * (3 - year_len) + parameters[3]

            if 2006 < int(parameters[3]) <= now_year:
                # Processing 2016 year
                if parameters[3] == str(now_year):
                    parameters[3] = EMPTY_INDICATOR

                    # Refactoring 'Фактические' in 'текущие' if year is 2016
                    for param in p2:
                        if param.type == 'фактический':
                            del param_set[1]
                            param_set.append(ParameterType.select().where(ParameterType.type == 'текущий'))
                            parameters[1] = 'текущий'
                else:
                    param_set.append(ParameterType.select().where(ParameterType.type == 'год'))
            else:
                response.message = ERROR_INCORRECT_YEAR % str(datetime.datetime.now().year)
                return

        # Processing sphere
        # Turning on sphere details for all requests about expenditures
        p5 = Parameter.select().where((Parameter.tagValue == parameters[4]) & (Parameter.type == 3))
        if exp_differ is True and len(p5):
            param_set.append(ParameterType.select().where(ParameterType.type == 'сфера'))
        # Turning off sphere details for all other requests
        elif exp_differ is False and len(p5):
            pass
        else:
            response.message = ERROR_PARSING
            return

        # Processing territory
        p6 = Parameter.select().where((Parameter.tagValue == parameters[5]) & (Parameter.type == 1))
        if parameters[5] == EMPTY_INDICATOR:
            pass
        elif len(p6):
            param_set.append(ParameterType.select().where(ParameterType.type == 'территория'))
        else:
            response.message = ERROR_PARSING
            return

        return param_set

    @staticmethod
    def _get_mdx_skeleton_for_mapper(mapper, params, response):
        """Finding MDX sampler for mapper"""

        # Trying to find necessary MDX-skeleton for given mapper or returning 0 if nothing is found
        mdx_skeleton = data.MAPPERS.get(mapper, -1)

        # Processing error message for which MDX-query is not ready yet
        if mdx_skeleton is None:
            response.message = MSG_IN_DEVELOPMENT
            return mdx_skeleton

        # Finding the nearest mapper to given and forming response for user
        if mdx_skeleton == -1:
            message = 'Запрос чуть-чуть некорректен🤔 Пожалуйста, подправьте его, выбрав ' \
                      'один из предложенных вариантов:\r\n'
            index = 1
            for i in list(data.MAPPERS.keys()):
                if DataParser.distance(i, mapper) == 1:
                    message += '- ' + M2Retrieving.__hint(i, mapper, params)
                    index += 1
            if index == 1:
                message = 'В запросе неверно несколько параметров: попробуйте изменить запрос.   '

            response.message = M2Retrieving._feedback(params) + '\n\n' + message[:-2] + '\n Жмите /search'

        return mdx_skeleton

    @staticmethod
    def _get_template_query_from_db(mapper, params, response):
        current_theme_sets = ParameterMap.select().where(ParameterMap.theme_type == mapper.pop(0))

        data = []
        i = -1

        old_set_id = -1
        cur_set_id = -1
        for r in current_theme_sets:
            cur_set_id = r.paramSet
            if cur_set_id == old_set_id:
                data[i][1].append(r.parameter_type)
                old_set_id = cur_set_id
            else:
                data.append([])
                i += 1
                data[i].append(r.paramSet)
                data[i].append([])
                data[i][1].append(r.parameter_type)
                old_set_id = cur_set_id

        def _transform(arr):
            new_arr = []
            for a1 in arr:
                for a2 in a1:
                    new_arr.append(a2)
            return new_arr

        mapper = _transform(mapper)
        param_ser = None

        for row in data:
            if set(mapper) == set(row[1]):
                param_ser = row[0]
                break

        if param_ser is None:
            response.message = 'Обработка запроса не удалась'
            return

        ps = ParameterMap.select().where(ParameterMap.paramSet == param_ser).limit(1)

        id_param_set = 0
        for p in ps:
            id_param_set = p.id

        query = Query.select().where(Query.parameterMap == id_param_set)
        for q in query:
            return q.templateQuery1

    @staticmethod
    def _refactor_mdx_skeleton(mdx_skeleton, params, mapper, response):
        """Replacing marks in MDX samplers by real data"""

        mdx_cube_and_query = []

        # Defining name of the cube from MDX-query
        query_by_elements = mdx_skeleton.split(' ')
        from_element = query_by_elements[query_by_elements.index('FROM') + 1]
        cube = from_element[1:len(from_element) - 4]

        # Creating marker for correct understanding "-/+" for deficit/surplus questions in different cubes
        if cube == 'FSYR01':
            response.theme = '1' + response.theme
        else:
            response.theme = '0' + response.theme

        # If there are '*' in MDX-sampler for substitution
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
                        d = data.NALOG_NENALOG[params[param_id]][1]
                    else:
                        d = data.NALOG_NENALOG[params[param_id]][0]

                # Replacing year
                if param_id == 3:
                    d = str(params[param_id])

                # Replacing sphere
                if param_id == 4:
                    d = data.SPHERES[params[param_id]][1]

                # Replacing territory
                if param_id == 5:
                    if 'CLDO02' in mdx_skeleton:
                        d = '08-' + data.PLACES[params[param_id]][1]
                    else:
                        d = '08-' + data.PLACES[params[param_id]][0]

                # Replacing '*' by proper parameter
                mdx_skeleton = mdx_skeleton.replace(star, d)

                # Cutting temp in order ro find next '*'
                temp = temp[i + 1:]

        # Adding cube and MDX-query
        mdx_cube_and_query.append(cube)
        mdx_cube_and_query.append(mdx_skeleton)

        return mdx_cube_and_query

    @staticmethod
    def _send_mdx_request(data_mart_code, mdx_query, response, params):
        """Sending POST request to remote server"""

        d = {'dataMartCode': data_mart_code, 'mdxQuery': mdx_query}
        r = requests.post('http://conf.test.fm.epbs.ru/mdxexpert/CellsetByMdx', d)

        # Processing if MDX-query fails
        if '"success":false' in r.text:
            response.message = ERROR_NO_DATA_GOT
            response.response = r.text
            return

        # Updating params of resulting object
        response.status = True
        response.message = M2Retrieving._feedback(params)
        response.response = r.text

    @staticmethod
    def _feedback(params):
        """Forming response how we have understood user's request"""

        # TODO: To make more abstract
        if params[0] == "дефицит":
            theme = ' дефицит/профицит'

            if params[1] == EMPTY_INDICATOR:
                param_1 = 'Фактический'
            else:
                param_1 = params[1][0].upper() + params[1][1:]

            if params[3] == EMPTY_INDICATOR:
                if param_1 == 'Плановый':
                    year = ' в ' + str(datetime.datetime.now().year) + ' году'
                else:
                    year = ''
            else:
                year = " в " + params[3] + " году"

            if params[5] == EMPTY_INDICATOR:
                territory = " " + data.PLACES[EMPTY_INDICATOR]
            else:
                territory = ' ' + data.PLACES[params[5]][2]

            response = param_1 + theme + territory + year
        else:
            theme = " " + params[0]

            if params[1] == EMPTY_INDICATOR:
                param_1 = "Фактические"
            else:
                param_1 = params[1][0].upper() + params[1][1:-1] + "е"

            if params[2] == EMPTY_INDICATOR:
                param_2 = ""
            else:
                param_2 = " " + params[2][:-1] + "е"

            if params[3] == EMPTY_INDICATOR:
                if param_1 == 'Плановые':
                    year_3 = ' в 2016 году'
                else:
                    year_3 = ''
            else:
                year_3 = " в " + params[3] + " году"

            sphere_4 = " " + data.SPHERES[params[4]][0]

            if params[5] == EMPTY_INDICATOR:
                territory = ' ' + data.PLACES[EMPTY_INDICATOR]
            else:
                territory = ' ' + data.PLACES[params[5]][2]

            response = param_1 + param_2 + theme + territory + sphere_4 + year_3

        return 'Я понял ваш запрос как: "' + response + '".'


class Result:
    def __init__(self, status=False, message='', response='', theme=''):
        self.status = status  # Variable, which shows first module if result of request is successful or not
        self.message = message  # Variable for containing error- and feedback-messages
        self.response = response  # Variable for storing JSON-response from server
        self.theme = theme  # Variable for defining difference between requests about deficit to different cubes
