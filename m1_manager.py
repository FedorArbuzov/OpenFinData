from transliterate import translit as tr

import logging
import constants
from m1_speechkit import speech_to_text
from m1_speechkit import SpeechException
from m2_main import M2Retrieving
from m3_main import M3Visualizing
from m1_req import DataParser

logging.basicConfig(filename='logs.log', level=50, format='%(asctime)s\t%(message)s', datefmt='%Y-%m-%d %H:%M')


class MessengerManager:
    """Класс MessengerManager имеет API из 5 методов. Подробнее в документации к ним"""

    @staticmethod
    def make_request(text, source, using_db=False, visualisation=True):
        """Самый универсальный API метод для текстовых запросов.

        Принимает на вход запрос (text), источник запроса (source),
        а также по умолчанию не использует БД как источник данных и включает
        визуализацию, если она возможна.

        Возвращает объект класса M1Result."""

        logging.critical("{}\t{}".format(source, text))

        dp = DataParser(using_db=using_db)  # using DB or not
        s1 = dp.main_func(text)
        s_mod2 = MessengerManager._forming_string_from_neural(s1)
        return MessengerManager._querying_and_visualizing(s_mod2, visualization=visualisation)

    @staticmethod
    def make_request_m2(text, source, using_db=False):
        """API метод, используемый на данный момент только в inline-режиме

        Принимает на вход запрос (text), источник запроса (source),
        а также по умолчанию не использует БД как источник данных. Данный
        метод позволяет получить ответ исключительно от второго модуля.

        В inline-режиме используется для проверки может ли система обработать
        запрос пользователя или нет.

        Возвращает объект класса M2Result."""

        logging.critical("{}\t{}".format(source, text))

        dp = DataParser(using_db=using_db)
        s1 = dp.main_func(text)
        s_mod2 = MessengerManager._forming_string_from_neural(s1)
        return M2Retrieving.get_data(s_mod2)

    @staticmethod
    def make_request_m3(m2_result):
        """API метод, используемый на данный момент только в inline-режиме

        Принимает на вход результат выполнения второго модуля.

        В inline-режиме используется для получения данных по запросу.

         Возвращает объект класса M3Result."""

        return M3Visualizing.create_response(m2_result.response, m2_result.theme, visualization=False)

    @staticmethod
    def parse_voice(record_bytes, source, using_db=False, visualisation=True):
        """Универсальный API метод для обработки голосовых запросов

        Принимает на вход набор байтов записи (record_bytes), источник запроса (source),
        а также по умолчанию не использует БД как источник данных и включает
        визуализацию, если она возможна.

        Возвращает объект класса M1Result."""

        try:
            text = speech_to_text(bytes=record_bytes)
            logging.critical("{}\t{}".format(source, text))
        except SpeechException:
            return constants.ERROR_CANNOT_UNDERSTAND_VOICE
        else:
            dp = DataParser(using_db=using_db)  # using DB or not
            s1 = dp.main_func(text)
            s_mod2 = MessengerManager._forming_string_from_neural(s1)
            return MessengerManager._querying_and_visualizing(s_mod2, visualization=visualisation)

    @staticmethod
    def greetings(text):
        """API метод для обработки приветствий от пользователя

        Принимает на вход сообщение (text). Возращает либо None, либо строку."""
        if DataParser.hello_back(text) is not None:
            return DataParser.hello_back(text)

    @staticmethod
    def _file_naming(request_string):
        request_string = tr(request_string, 'ru', reversed=True)
        filename = request_string.replace('null', '')
        filename = filename.replace(',', '_')

        for i in range(0, 3):
            filename = filename.replace('__', '_')

        if filename[len(filename) - 1] == '_':
            filename = filename[:len(filename) - 1]

        filename_svg = 'diagram_' + filename + '.svg'
        filename_pdf = 'table_' + filename + '.pdf'
        names = [filename_svg, filename_pdf]
        return names

    @staticmethod
    def _forming_string_from_neural(s1):
        s_mod2 = ''
        if s1[0] == 'расходы':
            s_mod2 += s1[0] + ',' + s1[4] + ',' + 'null' + ',' + str(s1[2]) + ',' + str(s1[3]) + ',' + s1[1]
        elif s1[0] == 'доходы':
            s_mod2 += s1[0] + ',' + s1[4] + ',' + str(s1[3]) + ',' + str(s1[2]) + ',' + 'null' + ',' + s1[1]
        elif s1[0] == 'дефицит' or s1[0] == "профицит/дефицит":
            s_mod2 += s1[0] + ',' + s1[4] + ',' + 'null' + ',' + str(s1[2]) + ',' + 'null' + ',' + s1[1]
        return s_mod2

    @staticmethod
    def _querying_and_visualizing(s_mod2, notify_user=True, visualization=True):
        print(s_mod2)
        general_result = M1Result()
        messages = []
        try:
            m2_result = M2Retrieving.get_data(s_mod2)
            if m2_result.status is False:
                messages.append(m2_result.message)
            else:
                messages.append(constants.MSG_WE_WILL_FORM_DATA_AND_SEND_YOU)
                names = MessengerManager._file_naming(s_mod2)
                general_result.file_names = names
                m3_result = M3Visualizing.create_response(m2_result.response, m2_result.theme,
                                                          filename_svg=names[0], filename_pdf=names[1],
                                                          visualization=visualization)
                if m3_result.data is False:
                    messages.append(constants.ERROR_NULL_DATA_FOR_SUCH_REQUEST_LONG)
                else:
                    if m3_result.is_file is False:
                        general_result.is_file = False

                    general_result.path = m3_result.path

                    # Informing user how system understood him in case of voice and text processing
                    if notify_user is True:
                        messages.append(m2_result.message)

                    messages.append(m3_result.number)

        except Exception as e:
            print(e)
            messages.append(constants.ERROR_SERVER_DOES_NOT_RESPONSE)

        general_result.messages = messages
        return general_result


class M1Result:
    def __init__(self, messages=None, is_file=True, file_names=None, path=None):
        self.messages = messages  # Variable, which storage all messages from _querying_and_visualizing()
        self.is_file = is_file  # Variable for defining if file in M3Visualizing was created
        self.file_names = file_names  # Variable for containing names of created files
        self.path = path  # Variable for containing path to user folder
