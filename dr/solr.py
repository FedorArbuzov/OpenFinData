from kb.kb_support_library import get_cube_dimensions, check_dimension_value_in_cube
import re
import json
import requests


class Solr:
    def __init__(self, core):
        self.core = core

    def get_data(self, user_request):
        try:
            docs = self._send_request_to_solr(user_request)

            if docs['response']['numFound']:
                mdx_query = self._parse_solr_response(docs)
                return DrSolrResult(True, mdx_query=mdx_query)
            else:
                raise Exception('Документы не найдены')
        except Exception as e:
            print('Solr: ' + str(e))
            return DrSolrResult(error=str(e))

    @staticmethod
    def _preprocessing_request(user_request):
        """Метод для работы с Solr

        Принимает на вход запрос пользователя.
        Возвращает строку, содержащую в себе только цифры, буквы и нужные пробелов"""

        return re.sub(r'[^\w\s]', '', user_request)

    def _send_request_to_solr(self, filtered_user_request):
        """Метод для работы с Solr

        Принимает на вход обработанный запрос пользователя и множественны/единичный ожидаемый ответ
        Возвращает документ (так как rows=1) в виде JSON-объекта"""

        request = 'http://localhost:8983/solr/{}/select/?q={}&wt=json'.format(self.core, filtered_user_request)
        json_response = requests.get(request).text
        docs = json.loads(json_response)
        return docs

    @staticmethod
    def _parse_solr_response(solr_docs):
        """Парсер набора документов

        Принимает на вход JSON-объект.
        Возвращает MDX"""
        mdx_template = 'SELECT {{[MEASURES].[{}]}} ON COLUMNS FROM [{}.DB] WHERE ({})'

        # TODO: работа над скрытыми параметрами: территория -> уровень бюджета
        # TODO: улучшать алгоритм сборки

        dim_list = []
        measure_list = []
        solr_docs = solr_docs['response']['docs']
        for doc in solr_docs:
            if doc['type'][0] == 'dimension':
                if doc['name'][0] in dim_list:
                    continue
                else:
                    dim_list.append(doc['name'][0])
                    dim_list.append(doc)
            if doc['type'][0] == 'measure':
                measure_list.append(doc)

        # Очистка от ненужных элементов
        dim_list = list(filter(lambda elem: type(elem) is not str, dim_list))

        # Максимальная группа измерений от куба лучшего элемента
        reference_cube = dim_list[0]['cube'][0]
        dim_list = [doc for doc in dim_list if doc['cube'][0] == reference_cube]

        dim_tmp, dim_str = "[{}].[{}]", []
        for doc in dim_list:
            dim_str.append(dim_tmp.format(doc['name'][0], doc['fvalue'][0]))

        measure = 'VALUE'
        if measure_list:
            measure_list = [item for item in measure_list if item['cube'][0] == reference_cube]
            if measure_list:
                measure = measure_list[0]['formal'][0]

        mdx_filled_template = mdx_template.format(measure, reference_cube, ','.join(dim_str))
        return mdx_filled_template

    @staticmethod
    def get_minfin_docs(user_request):
        request = 'http://localhost:8983/solr/{}/select/?q={}&wt=json'.format('minfin', user_request)
        json_response = requests.get(request).text
        docs = json.loads(json_response)

        if docs['response']['numFound']:
            fa = docs['response']['docs'][0]['full_answer'][0]
            sa = docs['response']['docs'][0]['short_answer'][0]
            return sa, fa
        else:
            return None

class DrSolrResult:
    def __init__(self, status=False, id_query=0, mdx_query='', error=''):
        self.status = status
        self.id_query = id_query
        self.mdx_query = mdx_query
        self.error = error
