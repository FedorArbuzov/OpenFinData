import json
import math


def get_documents():
    with open('output_1st_part_minfin_docs.json', 'r', encoding='utf-8') as file:
        docs = json.loads(file.read())

    # Использование для поиска ключевых слов лемматизированного полного ответа
    return [elem['lem_full_answer'] for elem in docs]


def doc_tokens(doc):
    # Фильтрация документа от цифр
    tokens_without_nums = [token for token in doc.split() if not token.isdigit()]
    return tokens_without_nums


def tf(word, doc):
    # TF: частота слова в документе
    return doc.count(word)


def documents_contain_word(word, doc_list):
    # количество документов, в которых встречается слово
    return 1 + sum(1 for document in doc_list if word in document)


def idf(word, doc_list):
    # IDF: логарифм от общего количества документов деленного на количество документов, в которых встречается слово
    return math.log(len(doc_list) / float(documents_contain_word(word, doc_list)))


def tfidf(word, doc, doc_list):
    # TFхIDF
    return tf(word, doc) * idf(word, doc_list)


def calculate_score(documents):
    # Словарь с рассчетами
    score = {}
    for idx, doc in enumerate(documents):
        score[idx] = []
        for token in doc_tokens(doc):
            score[idx].append({'term': token,
                               'tf': tf(token, doc),
                               'idf': idf(token, documents),
                               'tfidf': tfidf(token, doc, documents)})

    # сортировка элементов в словаре в порядке убывания индекса TF-IDF
    for document_id in score:
        score[document_id] = sorted(score[document_id], key=lambda d: d['tfidf'], reverse=True)

    return score


def top_words(score, top=5):
    # Топ наиболее характеризующих каждый документ слов
    docs_key_words = []
    for document_id in score:
        for word in score[document_id][:top]:
            resulting_str = 'Doc: {} word: {} TF: {} IDF: {} TF-IDF: {}'
            docs_key_words.append(
                resulting_str.format(document_id, word['term'], word['tf'], word['idf'], word['tfidf']))
    return docs_key_words


docs = get_documents()
score = calculate_score(docs)
print('\n'.join(top_words(score)))
