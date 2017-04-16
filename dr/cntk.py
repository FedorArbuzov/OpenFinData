import json
import re
import requests

class CNTK:
    """Метод для работы с Solr
    Принимает на вход запрос пользователя.
import requests

    Возвращает строку, содержащую в себе только цифры, буквы и нужные пробелов"""

    @staticmethod
    def _preprocessing_request(user_request):
        return re.sub(r'[^\w\s]', '', user_request)

    @staticmethod
    def _send_request_to_cntk(filtered_user_request):
        response = requests.get('http://localhost:8020/%s' % filtered_user_request).text
        return response

    @staticmethod
    def get_data(user_request):
        filtered_user_request = CNTK._preprocessing_request(user_request)
        tags = CNTK._send_request_to_cntk(filtered_user_request)
        return CNTKResult(True, tags)


class CNTKResult:
    def __init__(self, status=False, tags=''):
        self.status = status
        self.tags = tags