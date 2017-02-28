import requests
from constants import ERROR_IN_MDX_REQUEST, ERROR_NO_DOCS_FOUND, ERROR_NULL_DATA_FOR_SUCH_REQUEST
from kb.support_library import get_full_nvalues_for_dimensions, get_full_nvalue_for_measure
import json
import logging
import re


# Module, which is responsible for getting required from user data
class DataRetrieving:
    @staticmethod
    def get_data(user_request):
        """Единственный API метод для 2го модуля.

        Принимает на вход запрос пользователя.
        Возвращает объект класса M2Result."""

        result = M2Result()
        # предварительная обработка входной строки
        filtered_user_request = DataRetrieving._preprocessing_request(user_request)
        docs = DataRetrieving._send_request_to_solr(filtered_user_request)
        if docs['response']['numFound']:
            id_query, mdx_query, verbal_query = DataRetrieving._parse_solr_response(docs)

            api_response, cube = DataRetrieving._send_request_to_server(mdx_query)
            api_response = api_response.text

            # Обработка случая, когда MDX-запрос некорректен
            if '"success":false' in api_response:
                result.message = ERROR_IN_MDX_REQUEST
                result.response = api_response
            # Обработка случая, когда данных нет
            elif not json.loads(api_response)["cells"][0][0]["value"]:
                result.message = ERROR_NULL_DATA_FOR_SUCH_REQUEST
                result.response = None
            # В остальных случаях
            else:
                result.status = True
                result.response = json.loads(api_response)["cells"][0][0]["value"]

                # Формирование фидбэка
                result.message = DataRetrieving._form_feedback(mdx_query, cube)

            logging.info('{}\t{}\t{}\t{}\t{}'.format(__name__, user_request, id_query, verbal_query, result.response))
        else:
            result.message = ERROR_NO_DOCS_FOUND

        return result

    @staticmethod
    def _preprocessing_request(user_request):
        """Метод для работы с Solr

        Принимает на вход запрос пользователя.
        Возвращает строку, содержащую в себе только цифры, буквы и нужные пробелов"""

        return re.sub(r'[^\w\s]', '', user_request)

    @staticmethod
    def _send_request_to_solr(filtered_user_request):
        """Метод для работы с Solr

        Принимает на вход обработанный запрос пользователя.
        Возвращает документ (так как rows=1) в виде JSON-объекта"""

        json_response = requests.get(
            'http://localhost:8983/solr/kb/select/?q=%s&rows=1&wt=json' % filtered_user_request).text
        docs = json.loads(json_response)
        return docs

    @staticmethod
    def _parse_solr_response(solr_docs):
        """Парсер документа (а позже набора документов)

        Принимает на вход JSON-объект.
        Возвращает id, MDX и вербальный запросы, содержащиеся в документе"""
        id_query = solr_docs['response']['docs'][0]['id']
        mdx_query = solr_docs['response']['docs'][0]['mdx_query'][0]
        verbal_query = solr_docs['response']['docs'][0]['verbal_query'][0]
        return id_query, mdx_query, verbal_query

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
        api_response = requests.post('http://conf.test.fm.epbs.ru/mdxexpert/CellsetByMdx', d)

        return api_response, cube

    @staticmethod
    def _form_feedback(mdx_query, cube):
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
        full_verbal_dimensions_value = get_full_nvalues_for_dimensions([i['val'] for i in dims_vals])
        full_verbal_measure_value = get_full_nvalue_for_measure(measure_value, cube)

        # фидбек в удобном виде для конвертации в JSON-объект
        feedback = {'formal': {'cube': cube, 'measure': measure_value, 'dims': dims_vals},
                    'verbal': {'measure': full_verbal_measure_value, 'dims': full_verbal_dimensions_value}}

        return feedback


class M2Result:
    def __init__(self, status=False, message='', response=''):
        self.status = status  # Variable, which shows first module if result of request is successful or not
        self.message = message  # Variable for containing error- and feedback-messages
        self.response = response  # Variable for storing JSON-response from server
