# -*- coding: utf-8 -*-
import nltk
import pymorphy2
import logging
import json
from string import punctuation as pct
from nltk.stem.snowball import SnowballStemmer
from nltk.corpus import stopwords


class TextPreprocessing:
    def __init__(self, request_id, norming_style='lem'):
        self.request_id = request_id
        self.norming_style = norming_style
        self.language = 'russian'

    def normalization(self, text):
        # TODO: стемминг или лематизация?
        # TODO: обработка направильного спеллинга
        stemmer = SnowballStemmer(self.language)  # Стеммер
        morph = pymorphy2.MorphAnalyzer()  # Лемматизатор

        tokens = nltk.word_tokenize(text)

        stop_words = stopwords.words(self.language)
        # TODO: расширить список
        stop_words += "также иной".split()

        # Убираем знаки пунктуации и стоп слова
        tokens = [t for t in tokens if (t not in stop_words) and (t not in list(pct) + ["«", "»"])]

        if self.norming_style == 'stem':
            # Стемминг
            tokens = [stemmer.stem(t) for t in tokens]
        else:
            # Лемматизация
            tokens = [morph.parse(t)[0].normal_form for t in tokens]

        tokens = TextPreprocessing._delete_repeating_with_saving_order(tokens)

        normalized_request = ' '.join(tokens)

        logging_str = "ID-запроса: {}\tМодуль: {}\tЗапрос после нормализации: {}"
        logging.info(logging_str.format(self.request_id, __name__, normalized_request))

        return normalized_request

    @staticmethod
    def _delete_repeating_with_saving_order(tokens):
        # Распределени слов по повторениям
        fdist = nltk.FreqDist(tokens)

        # Отбор слов, повторяющихся более одного раза
        repeatings = [(i, fdist[i]) for i in fdist.keys() if fdist[i] > 1]

        # переворот листа для убирания повторов с конца
        tokens.reverse()

        # Удаление повторов
        for rep in repeatings:
            i = 0
            while i < rep[1] - 1:
                tokens.remove(rep[0])
                i += 1

        # возвращение исходного порядка
        tokens.reverse()

        return tokens

    @staticmethod
    def log_to_dict(log):
        """Принимает строку логов и возрврашает dict отображение, если это возможно"""
        json_str = ''
        try:
            log = log.split('\t')[1:]
            for l in log:
                l = l.split(':')
                json_str += '"{}": "{}",'.format(l[0].strip(), l[1].strip())

            json_str = '{' + json_str[:-1] + '}'
            return json.loads(json_str)
        except IndexError as e:
            print('TextPreprocessing: ' + str(e))
            return None
