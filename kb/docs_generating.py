from kb.db_creation import *
from itertools import combinations, chain, product
from kb.support_library import logging, query_data, filter_combinations, report, docs_needed
from os import getcwd, listdir, mkdir
from os.path import isfile, join
import json
import pycurl
import time


def get_cube_name(cube_id):
    """Получение названия куба по id"""

    return Cube.get(Cube.id == cube_id).name


def get_cube_measures_dimensions(cube_id):
    """Формирование словарей имеющихся у конкретного куба измерений и мер"""

    # словарь мер вида {id: (вербальное значение, формальное значение)}
    # например, {1: (текущие расходы, VALUE), 2: (плановые доходы, PLANONYEAR)}
    md = {}
    for m in Cube_Value.raw('select value_id from cube_value where cube_id = %s' % cube_id):
        for v in Value.raw('select index_nvalue, fvalue from value where id = %s' % m.value_id):
            md[m.value_id] = (v.index_nvalue, v.fvalue)

    # словарь измерений вида {id: формальное название измерения}
    # например, {1: 'TERRITORIES', 2: 'RZPR', 3: 'BGLEVELS'}
    dd = {}
    for cd in Cube_Dimension.raw('select dimension_id from cube_dimension where cube_id = %s' % cube_id):
        for d in Dimension.raw('select label from dimension where id = %s' % cd.dimension_id):
            dd[cd.dimension_id] = d.label

    return md, dd


def get_dimension_and_measure_combinations(dd, md, dimension_limit=3):
    """Создание всех возможных комбинаций измерений

    Вход: словарь из всех измерений и мер куба
    Выход: массив из возможных наборов комбинаций измерений и мер"""

    # Строк для логирования результатов данного методы
    log_all_possible_combinations = []

    # все возможные сочетания измерений — например, [(1,2),(1,2,3),(1,2,5)...], где цифры - id измерений
    dimension_sets = []

    # Массив для хранения полного набора комбинаций
    dimension_measure_sets = []

    # выбираем все возможные комбинации измерений по i элементов, где i больше либо равен 1 и
    # меньше либо равен количеству измерений куба
    for number in range(1, dimension_limit + 1):
        combination_with_i_items = list(combinations(dd.keys(), number))

        # добавляем получившихся набор комбинаций для i-го количества элементов в общий массив
        dimension_sets.append(combination_with_i_items)

    # уплощаем массив, лишая его лишней вложенности
    dimension_sets = list(chain(*dimension_sets))

    for m_id in md:
        for idx, d_set in enumerate(dimension_sets):
            # логируем получившийся набор
            log_all_possible_combinations.append(
                '{}. M:{} D:{}\n'.format(idx, md[m_id][1], ''.join([dd[d_id] + ' ' for d_id in d_set])))

            # добавляем получившийся объединенный набор (мера + измерение) в массив
            dimension_measure_sets.append([m_id, d_set])

    # записываем в файл получившиеся наборы
    logging('1st all_possible_combinations', ''.join(log_all_possible_combinations))

    return dimension_measure_sets


def generate_documents(md, dd, dimension_measure_sets, cube_id, cube_name):
    """Генерация документов

    Вход: cловари из имеющихся мер и измерений куба, полный набор сочитающихся измерений и мер, название куба
    Выход: набор документов"""

    # начало исполнение метода
    start_time = time.time()

    # все значения измерений куба
    dim_vals = []
    # сгенерированные документы
    docs = []
    # количество созданных документов
    docs_count = 0
    # шаблон MDX запроса
    mdx_template = 'SELECT {{[MEASURES].[{}]}} ON COLUMNS FROM [{}.DB] WHERE ({})'

    # выбор из БД значений всех измерений куба
    for idx, d_id in enumerate(dd):
        dim_vals.append([])
        dim_vals[idx].append(d_id)
        dim_vals[idx].append([])
        for dv in Dimension_Value.raw('select value_id from dimension_value where dimension_id = %s' % d_id):
            for v in Value.raw('select fvalue, index_nvalue from value where id = %s' % dv.value_id):
                dim_vals[idx][1].append((v.index_nvalue, v.fvalue))

    # для каждого набора измерений с мерой
    for dim_set in dimension_measure_sets:
        # массив со всеми (за некоторыми исключениями) значениями определенного набора измерений
        set_values_list = []

        # для каждого id измерения в наборе измерений
        for d_id in dim_set[1]:
            # выбор нужного измерения со значениями
            dim_val = list(filter(lambda d: d[0] == d_id, dim_vals))[0]

            set_values_list.append(dim_val[1])

        # все возможные сочетания измерений со значениями
        combs = list(product(*set_values_list))
        combs = filter_combinations(combs, dim_set[1], dd)

        for item in combs:
            # cтроки для сохранения нескольких фомальных/вербальных значений переменных
            fvalues, nvalues = [], []

            for elem, d_id in zip(item, dim_set[1]):
                fvalues.append('[{}].[{}],'.format(dd[d_id], elem[1]))
                nvalues.append(elem[0] + ' ')

            # убираем ненунжныю запятую и пробел в конце строки
            fvalues, nvalues = ''.join(fvalues)[:-1], ''.join(nvalues)[:-1]

            # mdx-запрос
            fr = mdx_template.format(md[dim_set[0]][1], cube_name, fvalues)

            # вербальный запрос
            nr = md[dim_set[0]][0] + ' ' + nvalues

            docs.append({'cube': cube_id, 'mdx_query': fr, 'verbal_query': nr})
            docs_count += 1

            # каждые 5000 документов выводим их количество
            if docs_count % 20000 == 0:
                print('{} / {}'.format(len(docs), docs_count))

        step_size = 200
        with database.atomic():
            for step in range(0, len(docs), step_size):
                Documents.insert_many(docs[step:step + step_size]).execute()
        docs.clear()

    print('Документов создалось: {}'.format(docs_count))
    print("Время выполнение методы: %s минут" % ((time.time() - start_time) / 60))


def learn_model(cube_id):
    """Отсеивание нерабочих документов

    Вход: набор документов
    Выход: набор документов только с работающими запросами"""

    # Строка для логирования результатов данного методы
    log_request_result = []

    count_all_docs = 0
    count_deleted = 0

    for idx, document in enumerate(Documents.select().where(Documents.id == cube_id)):
        request_result = query_data(document.mdx_query)
        idx_step_string = '{}. {}: {}\n'.format(idx, document.mdx_query, request_result[1])
        print(idx_step_string[:-1])

        log_request_result.append(idx_step_string)

        # TODO: умное удаление ненужных строк
        if not request_result[0]:
            Documents.delete(document)
            count_deleted += 1
        count_all_docs = idx

    print('Документов осталось: {0}, сокращение: {1:.2%}'.format(count_all_docs - count_deleted,
                                                                 count_deleted / count_all_docs))
    logging('2nd request result', ''.join(log_request_result))


def generate_json(cube_id, cube_name, max_obj_num=100000):
    """Генерация json документов

    Вход: набор документов
    Выход: None"""
    # Создаем папку для хранения сгенерированных документов для конкретного куба
    try:
        mkdir(cube_name)
    except FileExistsError:
        pass

    i, j = 0, max_obj_num
    docs = []

    for document in Documents.select().where(Documents.id == cube_id):
        docs.append({'ID': document.id, 'mdx_query': document.mdx_query, 'verbal_query': document.verbal_query})

    # for documents in Documents.select().where(Documents.id == cube_id):
    for idx in range(len(docs) // max_obj_num + 1):
        # указываем путь и название файла для записи
        doc_name = '{}\\{}\\{}.json'.format(getcwd(), cube_name, idx)
        json_str = json.dumps(docs[i:j])

        with open(doc_name, 'w', encoding='utf-8') as file:
            file.write(json_str)

        i += max_obj_num
        j += max_obj_num


def index_created_documents(cube_name):
    """Генерация json документов

    Вход: название куба
    Выход: None"""
    pass
    # создание пути к папке, в которой хранятся документы
    path = '{}\\{}'.format(getcwd(), cube_name)

    # получение названия всех файлов, в папке
    json_file_names = [f for f in listdir(path) if isfile(join(path, f))]

    c = pycurl.Curl()
    c.setopt(c.URL, 'http://localhost:8983/solr/kb/update?commit=true')

    # индексирование всех файлов в Solr
    # см. http://pycurl.io/docs/latest/quickstart.html
    # это работает, но непонятны детали (см на 182-248 стр. из Apache Solr Reference Guide)
    for file_name in json_file_names:
        c.setopt(c.HTTPPOST,
                 [
                     ('fileupload',
                      (c.FORM_FILE, r'C:\Users\User\PycharmProjects\Simplify\%s\%s' % (cube_name, file_name),
                       c.FORM_CONTENTTYPE, 'application/json')
                      ),
                 ])
        c.perform()


for cube in Cube.raw('select id from cube'):
    id_cube = cube.id
    name_cube = get_cube_name(id_cube)

    mdict, ddict = get_cube_measures_dimensions(id_cube)

    measure_dim_sets = get_dimension_and_measure_combinations(ddict, mdict)

    dim_count, doc_count = docs_needed(mdict, ddict, measure_dim_sets)

    generate_documents(mdict, ddict, measure_dim_sets, id_cube, name_cube)

    # # обучение путем проверки корректности документа, через реальный запрос к серверу
    # # !ОСТОРОЖНО!
    # only_working_documents = learn_model(id_cube)
    # # !ОСТОРОЖНО!

    # generate_json(id_cube)

    # generate_json(only_working_documents, name_cube, max_obj_num=5000)

    # index_created_documents(name_cube)

    report(id_cube, name_cube, mdict, ddict, measure_dim_sets, dim_count, doc_count)
