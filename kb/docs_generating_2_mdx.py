#!/usr/bin/python
# -*- coding: utf-8 -*-

from kb.db_creation import *
from os import getcwd, listdir, remove
import json
import pycurl


def write_to_file(docs):
    json_data = json.dumps(docs)
    with open('data_for_indexing.json', 'a') as file:
        file.write(json_data)


def create_values():
    values = []
    for value in Value.select():
        for dimension_value in Dimension_Value.raw(
                        'select dimension_id from dimension_value where value_id = %s' % value.id):
            for dimension in Dimension.raw('select label from dimension where id = %s' % dimension_value.dimension_id):
                values.append(
                    {'verbal': value.index_nvalue, 'formal': {'dimension': dimension.label, 'fvalue': value.fvalue}})
    return values

    
def create_cubes():
    cubes = []
    for cube in Cube.select():
        cubes.append({'cube': cube.name, 'tags': cube.tags})
    return cubes


def index_created_documents(core='kb2'):
    # создание пути к папке, в которой хранятся документы
    path = getcwd()

    # получение названия всех json файлов, в папке
    json_file_names = [f for f in listdir(path) if f.endswith('.json')]

    c = pycurl.Curl()
    c.setopt(c.URL, 'http://localhost:8983/solr/{}/update?commit=true'.format(core))

    for file_name in json_file_names:
        c.setopt(c.HTTPPOST,
                 [
                     ('fileupload',
                      (c.FORM_FILE, getcwd() + '\\{}'.format(file_name),
                       c.FORM_CONTENTTYPE, 'application/json')
                      ),
                 ])
        c.perform()


data = create_values() + create_cubes()
write_to_file(data)
index_created_documents()
# remove(getcwd()+"\\data_for_indexing.json")
