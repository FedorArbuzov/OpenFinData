import json
import re
import requests


class Solr:
    @staticmethod
    def get_data(user_request, docs_type="base"):
        filtered_user_request = Solr._preprocessing_request(user_request)

        if docs_type == "base":
            try:
                docs = Solr._send_request_to_solr(filtered_user_request, docs_type=docs_type)

                if docs['response']['numFound']:
                    id_query, mdx_query, verbal_query = Solr._parse_solr_response(docs, docs_type=docs_type)
                    return DrSolrResult(True, id_query, mdx_query, verbal_query)
            except:
                return DrSolrResult()

        if docs_type == "alternative":
            try:
                docs = Solr._send_request_to_solr(filtered_user_request, docs_type=docs_type)

                if docs['response']['numFound']:
                    mdx_query = Solr._parse_solr_response(docs, docs_type=docs_type)
                    return DrSolrResult(True, mdx_query=mdx_query)
            except:
                return DrSolrResult()

    @staticmethod
    def _preprocessing_request(user_request):
        """Метод для работы с Solr

        Принимает на вход запрос пользователя.
        Возвращает строку, содержащую в себе только цифры, буквы и нужные пробелов"""

        return re.sub(r'[^\w\s]', '', user_request)

    @staticmethod
    def _send_request_to_solr(filtered_user_request, docs_type):
        """Метод для работы с Solr

        Принимает на вход обработанный запрос пользователя и множественны/единичный ожидаемый ответ
        Возвращает документ (так как rows=1) в виде JSON-объекта"""

        multiple_param = ""

        if docs_type == "base":
            multiple_param = "&row=1"

        request = 'http://localhost:8983/solr/kb/select/?q={}{}&wt=json'.format(filtered_user_request, multiple_param)
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

            mdx_template = 'SELECT {{[MEASURES].[{}]}} ON COLUMNS FROM [{}.DB] WHERE ({})'

            dim_tmp, dim_str = "[{}].[{}]", ""
            for doc in dim_list:
                dim_str += dim_tmp.format(doc['dimension'][0], doc['fvalue'][0]) + ','

            return mdx_template.format('VALUE', cube_list[0], dim_str[:-1])


class DrSolrResult:
    def __init__(self, status=False, id_query=0, mdx_query='', verbal_query=''):
        self.status = status
        self.id_query = id_query
        self.mdx_query = mdx_query
        self.verbal_query = verbal_query
import json
import re
import requests


class Solr:
    @staticmethod
    def get_data(user_request):
        filtered_user_request = Solr._preprocessing_request(user_request)
        try:
            docs = Solr._send_request_to_solr(filtered_user_request)

            if docs['response']['numFound']:
                id_query, mdx_query, verbal_query = Solr._parse_solr_response(docs)
                return DrSolrResult(True, id_query, mdx_query, verbal_query)
        except:
            return DrSolrResult(False)

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
            'http://localhost:8983/solr/knowledgebase/select/?q=%s&rows=1&wt=json' % filtered_user_request).text
        docs = json.loads(json_response)
        return docs

    @staticmethod
    def _parse_solr_response(solr_docs):
        """Парсер документа (а позже набора документов)

        Принимает на вход JSON-объект.
        Возвращает id, MDX и вербальный запросы, содержащиеся в документе"""
        id_query = solr_docs['response']['docs'][0]['id']
        mdx_query = solr_docs['response']['docs'][0]['mdx_query'][0]
        verbal_query = solr_docs['response']['docs'][0]['verbal_query']
        return id_query, mdx_query, verbal_query


class DrSolrResult:
    def __init__(self, status=False, id_query=0, mdx_query='', verbal_query=''):
        self.status = status
        self.id_query = id_query
        self.mdx_query = mdx_query
        self.verbal_query = verbal_query
