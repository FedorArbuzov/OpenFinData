import requests
from constants import ERROR_IN_MDX_REQUEST, ERROR_NO_DOCS_FOUND, ERROR_NULL_DATA_FOR_SUCH_REQUEST
from kb.kb_support_library import get_full_values_for_dimensions, get_full_value_for_measure, get_representation_format
from text_preprocessing import TextPreprocessing
import json
import logging
from dr.solr import Solr
from dr.cntk import CNTK
import uuid
from config import SETTINGS


# Module, which is responsible for getting required from user data
class DataRetrieving:
    @staticmethod
    def get_data(user_request, request_id):
        """Единственный API метод для 2го модуля.

        Принимает на вход запрос пользователя.
        Возвращает объект класса M2Result."""

        cntk_result = [{'tagmeaning': 'Нет тега', 'word': 'Нет слова'}]
        # try:
        #    cntk_result = CNTK.get_data(user_request)
        # except:
        #   pass

        result = M2Result()
        solr = Solr(SETTINGS.SOLR_MAIN_CORE)

        tp = TextPreprocessing(request_id)
        normalized_user_request = tp.normalization(user_request.lower())

        solr_result = solr.get_data(normalized_user_request)
        if solr_result.status:
            # api_response, cube = '{"cells":[[{"value":"11111"}], "smth"]}', 'Куб'
            api_response, cube = DataRetrieving._send_request_to_server(solr_result.mdx_query)
            api_response = api_response.text
            feedback = DataRetrieving._form_feedback(solr_result.mdx_query, cube, cntk_result, user_request)

            value = None

            # Обработка случая, когда MDX-запрос некорректен
            if 'Доступ закрыт!' in api_response:
                result.message = "Доступ закрыт"
                result.response = api_response
                value = api_response
            elif '"success":false' in api_response:
                result.message = ERROR_IN_MDX_REQUEST
                result.response = api_response
                value = api_response
            # Обработка случая, когда данных нет
            elif not json.loads(api_response)["cells"][0][0]["value"]:
                result.message = ERROR_NULL_DATA_FOR_SUCH_REQUEST
                result.response = None
            # В остальных случаях
            else:
                result.status = True

                # TODO: доработать форматирование
                value = float(json.loads(api_response)["cells"][0][0]["value"])

                value_format = get_representation_format(solr_result.mdx_query)
                if not value_format:
                    formatted_value = DataRetrieving._format_numerical(value)
                    result.response = formatted_value
                elif value_format == 1:
                    formatted_value = '{}%'.format(value)
                    result.response = formatted_value

                # Формирование фидбэка
                result.message = feedback
            logging_str = 'ID-запроса: {}\tМодуль: {}\tОтвет Solr: {}\tMDX-запрос: {}\tЧисло: {}'

            feedback_verbal = feedback['verbal']
            verbal = '0. {}'.format(feedback_verbal['measure']) + ' '
            verbal += ' '.join([str(idx + 1) + '. ' + i for idx, i in enumerate(feedback_verbal['dims'])])

            logging.info(logging_str.format(request_id, __name__, verbal, solr_result.mdx_query, value))
        else:
            result.message = ERROR_NO_DOCS_FOUND
            logging_str = 'ID-запроса: {}\tМодуль: {}\tОтвет Solr: {}'
            logging.warning(logging_str.format(request_id, __name__, solr_result.error))

        return result

    @staticmethod
    def get_minfin_data(user_request):
        tp = TextPreprocessing(uuid.uuid4())
        return Solr.get_minfin_docs(tp.normalization(user_request))

    @staticmethod
    def _send_request_to_server(mdx_query):
        """Отправка запроса к серверу

        Принимает на вход MDX-запрос
        Возвращает объект класса request.model.Response и куб"""

        # Парсинг строки MDX-запроса для выделения из нее названия куба
        query_by_elements = mdx_query.split(' ')
        from_element = query_by_elements[query_by_elements.index('FROM') + 1]
        cube = from_element[1:len(from_element) - 4]

        # Подготовка POST-данных и запрос к серверу
        d = {'dataMartCode': cube, 'mdxQuery': mdx_query}
        api_response = requests.post('http://conf.prod.fm.epbs.ru/mdxexpert/CellsetByMdx', d)

        return api_response, cube

    @staticmethod
    def _form_feedback(mdx_query, cube, cntk_result, user_request):
        """Формироварие обратной связи

        Принимает на вход MDX-запрос и куб
        Возвращает cловарь"""

        # Разбиваем MDX-запрос на две части
        left_part, right_part = mdx_query.split('(')

        # Вытаскиваем меру из левой части
        measure_value = left_part.split('}')[0].split('.')[1][1:-1]

        # Собираем название измерения и его значение из второй
        dims_vals = []
        for item in right_part[:-1].split(','):
            item = item.split('.')
            dims_vals.append({'dim': item[0][1:-1], 'val': item[1][1:-1]})

        # Полные вербальные отражения значений измерений и меры
        full_verbal_dimensions_value = get_full_values_for_dimensions([i['val'] for i in dims_vals])
        full_verbal_measure_value = get_full_value_for_measure(measure_value, cube)

        # фидбек в удобном виде для конвертации в JSON-объект
        feedback = {'formal': {'cube': cube, 'measure': measure_value, 'dims': dims_vals},
                    'verbal': {'measure': full_verbal_measure_value, 'dims': full_verbal_dimensions_value},
                    'cntk': cntk_result, 'user_request': user_request}

        return feedback

    @staticmethod
    def _format_numerical(number):
        str_num = str(number)

        # Если число через точку
        if '.' in str_num:
            str_num = str_num.split('.')[0]
        num_len = len(str_num)

        if num_len < 6:
            return str_num
        elif 6 < num_len <= 9:
            return '{},{} {}'.format(str_num[:-6], str_num[-6], 'млн')
        elif 9 < num_len <= 12:
            return '{},{} {}'.format(str_num[:-9], str_num[-9], 'млрд')
        else:
            return '{},{} {}'.format(str_num[:-12], str_num[-12], 'трлн')


class M2Result:
    def __init__(self, status=False, message='', response=''):
        self.status = status  # Variable, which shows first module if result of request is successful or not
        self.message = message  # Variable for containing error- and feedback-messages
        self.response = response  # Variable for storing JSON-response from server

    def toJSON(self):
        return json.dumps(self, default=lambda obj: obj.__dict__, sort_keys=True, indent=4)
