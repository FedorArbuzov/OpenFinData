import json
import re
import requests


class Solr:
    @staticmethod
    def get_data(user_request):
        filtered_user_request = Solr._preprocessing_request(user_request)
        docs = Solr._send_request_to_solr(filtered_user_request)
        if docs['response']['numFound']:
            id_query, mdx_query, verbal_query = Solr._parse_solr_response(docs)
            return DrSolrResult(True, id_query, mdx_query, verbal_query)

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


class DrSolrResult:
    def __init__(self, status=False, id_query=0, mdx_query='', verbal_query=''):
        self.status = status
        self.id_query = id_query
        self.mdx_query = mdx_query
        self.verbal_query = verbal_query
