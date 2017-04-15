# -*- coding: utf-8 -*-
import nltk
import pymorphy2
from string import punctuation as pct
from nltk.stem.snowball import SnowballStemmer
from nltk.corpus import stopwords

language = "russian"


def normalization(text, type='stem'):
    # TODO: стемминг или лематизация?
    stemmer = SnowballStemmer(language)  # Стеммер
    morph = pymorphy2.MorphAnalyzer()  # Лемматизатор

    tokens = nltk.word_tokenize(text)

    stop_words = stopwords.words(language)
    # TODO: расширить список
    stop_words += "также иной".split()

    # Убираем знаки пунктуации и стоп слова
    tokens = [t for t in tokens if (t not in stop_words) and (t not in list(pct) + ["«", "»"])]

    if type == 'stem':
        # Стемминг
        tokens = [stemmer.stem(t) for t in tokens]
    else:
        # Лемматизация
        tokens = [morph.parse(t)[0].normal_form for t in tokens]

    tokens = delete_repeating_with_saving_order(tokens)

    return ' '.join(tokens)


def delete_repeating_with_saving_order(tokens):
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
