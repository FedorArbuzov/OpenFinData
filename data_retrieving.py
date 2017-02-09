import requests
from constants import ERROR_NO_DATA_GOT, ERROR_NO_DOCS_FOUND
import json
import logging


# Module, which is responsible for getting required from user data
class DataRetrieving:
    @staticmethod
    def get_data(user_request):
        """Единственный API метод для 2го модуля.

        Возвращает объект класса M2Result из m2_main."""
        result = M2Result()

        docs = DataRetrieving._send_request_to_solr(user_request)
        if docs['response']['numFound']:
            id_query, mdx_query, verbal_query = DataRetrieving._parse_solr_response(docs)
            logging.info('{}\t{}\t{}\t{}'.format(__name__, user_request, id_query, verbal_query))
            DataRetrieving._send_request_to_server(mdx_query, result)
        else:
            result.message = ERROR_NO_DOCS_FOUND

        return result

    @staticmethod
    def _send_request_to_solr(user_request):
        json_response = requests.get('http://localhost:8983/solr/kb/select/?q=%s&rows=1&wt=json' % user_request).text
        docs = json.loads(json_response)
        return docs

    @staticmethod
    def _parse_solr_response(solr_docs):
        id_query = solr_docs['response']['docs'][0]['id'][0]
        # mdx_query = solr_docs['response']['docs'][0]['mdx_query'][0]
        # verbal_query = solr_docs['response']['docs'][0]['verbal_query'][0]
        mdx_query = solr_docs['response']['docs'][0]['mdx'][0]
        verbal_query = solr_docs['response']['docs'][0]['query'][0]
        return id_query, mdx_query, verbal_query

    @staticmethod
    def _send_request_to_server(mdx_query, result):
        """Sending POST request to remote server"""

        query_by_elements = mdx_query.split(' ')
        from_element = query_by_elements[query_by_elements.index('FROM') + 1]
        cube = from_element[1:len(from_element) - 4]

        d = {'dataMartCode': cube, 'mdxQuery': mdx_query}
        r = requests.post('http://conf.test.fm.epbs.ru/mdxexpert/CellsetByMdx', d)

        # Processing if MDX-query fails
        if '"success":false' in r.text:
            result.message = ERROR_NO_DATA_GOT  # TODO: назначить другое сообщение
            result.response = r.text
            return

        # Updating params of resulting object
        result.status = True
        result.response = json.loads(r.text)["cells"][0][0]["value"]


class M2Result:
    def __init__(self, status=False, message='', response=''):
        self.status = status  # Variable, which shows first module if result of request is successful or not
        self.message = message  # Variable for containing error- and feedback-messages
        self.response = response  # Variable for storing JSON-response from server
