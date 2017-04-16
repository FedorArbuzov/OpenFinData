import requests
from constants import ERROR_IN_MDX_REQUEST, ERROR_NO_DOCS_FOUND, ERROR_NULL_DATA_FOR_SUCH_REQUEST
from kb.support_library import get_full_values_for_dimensions, get_full_value_for_measure
from text_normalization import normalization
import json
import logging
from dr.solr import Solr
from dr.cntk import CNTK


# Module, which is responsible for getting required from user data
class DataRetrieving:
    @staticmethod
    def get_data(user_request, user_id, method='solr', docs_type='base'):
        """Единственный API метод для 2го модуля.

        Принимает на вход запрос пользователя.
        Возвращает объект класса M2Result."""
        cntk_result = CNTK.get_data(user_request)
        print(cntk_result.tags)


        result = M2Result()
        result.cntk_response = cntk_result.tags
        # предварительная обработка входной строки
        if method == 'solr':
            if docs_type == 'base':
                solr = Solr('knowledgebase')
                user_request = user_request.lower()
            else:
                solr = Solr('kb')
                user_request = normalization(user_request.lower(), type='lem')
            solr_result = solr.get_data(user_request, docs_type=docs_type)
            if solr_result.status:
                api_response, cube = DataRetrieving._send_request_to_server(solr_result.mdx_query)
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
                    result.message = DataRetrieving._form_feedback(solr_result.mdx_query, cube)

                logging_str = 'Модуль: {}\tID-пользователя: {}\tОтвет Solr: {}\tMDX-запрос: {}\tЧисло: {}'
                logging.info(logging_str.format(__name__, user_id, solr_result.verbal_query, solr_result.mdx_query,
                                          result.response))
            else:
                result.message = ERROR_NO_DOCS_FOUND
                logging_str = 'Модуль: {}\tID-пользователя: {}\tОтвет Solr: {}'
                logging.info(logging_str.format(__name__, user_id, ERROR_NO_DOCS_FOUND))

        return result

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
        full_verbal_dimensions_value = get_full_values_for_dimensions([i['val'] for i in dims_vals])
        full_verbal_measure_value = get_full_value_for_measure(measure_value, cube)

        # фидбек в удобном виде для конвертации в JSON-объект
        feedback = {'formal': {'cube': cube, 'measure': measure_value, 'dims': dims_vals},
                    'verbal': {'measure': full_verbal_measure_value, 'dims': full_verbal_dimensions_value}}

        return feedback

    @staticmethod
    def object_processing():
        pass


class M2Result:
    def __init__(self, status=False, message='', response='', cntk_response=''):
        self.status = status  # Variable, which shows first module if result of request is successful or not
        self.message = message  # Variable for containing error- and feedback-messages
        self.response = response  # Variable for storing JSON-response from server
        self.cntk_response = cntk_response #Variable for cntk

    def toJSON(self):
        return json.dumps(self, default=lambda obj: obj.__dict__, sort_keys=True, indent=4)
