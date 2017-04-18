from kb.support_library import get_cube_dimensions
import re
import json
import requests


class Solr:
    def __init__(self, core):
        self.core = core

    def get_data(self, user_request, docs_type="base"):
        if docs_type == "base":
            filtered_user_request = Solr._preprocessing_request(user_request)
            try:
                docs = self._send_request_to_solr(filtered_user_request, docs_type=docs_type)

                if docs['response']['numFound']:
                    id_query, mdx_query, verbal_query = Solr._parse_solr_response(docs, docs_type=docs_type)
                    return DrSolrResult(True, id_query, mdx_query, verbal_query)
                else:
                    raise Exception('Жокументы не найдены')
            except Exception as e:
                print('Solr: ' + str(e))
                return DrSolrResult(error=str(e))

        if docs_type == "alternative":
            try:
                docs = self._send_request_to_solr(user_request, docs_type=docs_type)

                if docs['response']['numFound']:
                    mdx_query = self._parse_solr_response(docs, docs_type=docs_type)
                    return DrSolrResult(True, mdx_query=mdx_query)
                else:
                    raise Exception('Жокументы не найдены')
            except Exception as e:
                print('Solr: ' + str(e))
                return DrSolrResult(error=str(e))

    @staticmethod
    def _preprocessing_request(user_request):
        """Метод для работы с Solr

        Принимает на вход запрос пользователя.
        Возвращает строку, содержащую в себе только цифры, буквы и нужные пробелов"""

        return re.sub(r'[^\w\s]', '', user_request)

    def _send_request_to_solr(self, filtered_user_request, docs_type):
        """Метод для работы с Solr

        Принимает на вход обработанный запрос пользователя и множественны/единичный ожидаемый ответ
        Возвращает документ (так как rows=1) в виде JSON-объекта"""

        multiple_param = ""

        if docs_type == "base":
            multiple_param = "&row=1"

        request = 'http://localhost:8983/solr/{}/select/?q={}{}&wt=json'.format(self.core, filtered_user_request,
                                                                                multiple_param)
        json_response = requests.get(request).text
        docs = json.loads(json_response)
        return docs

    @staticmethod
    def _parse_solr_response(solr_docs, docs_type):
        """Парсер документа (а позже набора документов)

        Принимает на вход JSON-объект.
        Возвращает id, MDX и вербальный запросы, содержащиеся в документе"""
        if docs_type == "base":
            id_query = solr_docs['response']['docs'][0]['id']
            mdx_query = solr_docs['response']['docs'][0]['mdx_query'][0]
            verbal_query = solr_docs['response']['docs'][0]['verbal_query']
            return id_query, mdx_query, verbal_query
        if docs_type == "alternative":
            dim_list = []
            cube_list = []
            solr_docs = solr_docs['response']['docs']
            for doc in solr_docs:
                if "dimension" in doc.keys():
                    if doc['dimension'][0] in dim_list:
                        continue
                    else:
                        dim_list.append(doc['dimension'][0])
                        dim_list.append(doc)
                else:
                    cube_list.append(doc['cube'][0])

            dim_list = list(filter(lambda elem: type(elem) is not str, dim_list))

            try:
                cube_dimensions = get_cube_dimensions(cube_list[0])
            except IndexError:
                raise Exception('Ошибка в сборе MDX-запроса - не найден куб')

            try:
                # только те измерения, которые есть в кубе
                correct_dim_list = list(filter(lambda elem: elem['dimension'][0] in cube_dimensions, dim_list))

                mdx_template = 'SELECT {{[MEASURES].[{}]}} ON COLUMNS FROM [{}.DB] WHERE ({})'

                dim_tmp, dim_str = "[{}].[{}]", ""
                for doc in correct_dim_list:
                    dim_str += dim_tmp.format(doc['dimension'][0], doc['fvalue'][0]) + ','

                mdx_filled_template = mdx_template.format('VALUE', cube_list[0], dim_str[:-1])
                return mdx_filled_template
            except IndexError:
                raise Exception('Ошибка в сборе MDX-запроса - другая ошибка')


class DrSolrResult:
    def __init__(self, status=False, id_query=0, mdx_query='', verbal_query='', error=''):
        self.status = status
        self.id_query = id_query
        self.mdx_query = mdx_query
        self.verbal_query = verbal_query
        self.error = error
