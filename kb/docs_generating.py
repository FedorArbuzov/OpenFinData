#!/usr/bin/python
# -*- coding: utf-8 -*-

from kb.kb_db_creation import *
from os import getcwd, remove
import json
import pycurl
import requests
import subprocess
import datetime


class DocsGenerationAlternative:
    def __init__(self, core):
        self.file_name = 'kb\data_for_indexing.json'
        self.core = core

    def generate_docs(self):
        data = DocsGenerationAlternative._create_values() + \
               DocsGenerationAlternative._create_cubes() + \
               DocsGenerationAlternative._create_measures()

        self._write_to_file(data)

    def clear_index(self):
        dlt_str = 'http://localhost:8983/solr/{}/update?stream.body=%3Cdelete%3E%3Cquery%3E*:*%3C/query%3E%3C/delete%3E&commit=true'
        requests.get(dlt_str.format(self.core))
        try:
            remove('{}\\{}'.format(getcwd(), self.file_name))
        except FileNotFoundError:
            pass

    def create_core(self):
        status_str = 'http://localhost:8983/solr/admin/cores?action=STATUS&core={}&wt=json'
        solr_response = requests.get(status_str.format(self.core))
        solr_response = json.loads(solr_response.text)
        if solr_response['status'][self.core]:
            print('Ядро {} уже существует'.format(self.core))
        else:
            create_core_str = 'http://localhost:8983/solr/admin/cores?action=CREATE&name={}&configSet=basic_configs'
            solr_response = requests.get(create_core_str.format(self.core))
            if solr_response.status_code == 200:
                print('Ядро {} автоматически создано'.format(self.core))
            else:
                print('Что-то пошло не так: ошибка {}'.format(solr_response.status_code))

    def index_created_documents_via_curl(self):
        # TODO: разобраться с pycurl.error: (6, 'Could not resolve: localhost (Domain name not found)')
        c = pycurl.Curl()
        c.setopt(c.URL, 'http://localhost:8983/solr/{}/update?commit=true'.format(self.core))
        c.setopt(c.HTTPPOST,
                 [
                     ('fileupload',
                      (c.FORM_FILE, getcwd() + '\\{}'.format(self.file_name),
                       c.FORM_CONTENTTYPE, 'application/json')
                      ),
                 ])
        c.perform()

    def index_created_documents_via_cmd(self, path_to_post_jar_file):
        path_to_json_data_file = '{}\\{}'.format(getcwd(), self.file_name)
        command = r'java -Dauto -Dc={} -Dfiletypes=json -jar {} {}'.format(self.core, path_to_post_jar_file,
                                                                           path_to_json_data_file)
        subprocess.Popen(command, shell=True, stdout=subprocess.PIPE).wait()
        print('Документы проиндексированы')

    def _write_to_file(self, docs):
        json_data = json.dumps(docs)
        with open(self.file_name, 'a') as file:
            file.write(json_data)

    @staticmethod
    def _create_values():
        current_year = datetime.datetime.now().year
        year_values = [i for i in range(2007, current_year + 1)]
        year_values.extend([i for i in range(7, current_year-1999)])
        for i in range(len(year_values)):
            year_values.insert(0, {'type': 'year_dimension', 'fvalue': year_values.pop()})

        # TODO: подправить ключ на верхний регистр
        territory_values = []
        dimension = Dimension.get(Dimension.label == 'Territories')
        for dimension_value in Dimension_Value.select().where(Dimension_Value.dimension_id == dimension.id):
            for value in Value.select().where(Value.id == dimension_value.value_id):
                territory_values.append(value.lem_index_value)

        td = {}

        for item in territory_values:
            td[item] = []
            for value in Value.select().where(Value.lem_index_value == item):
                td[item].append({'id': value.id, 'fvalue': value.cube_value})

        for key, value in td.items():
            for item in value:
                for dimension_value in Dimension_Value.select().where(Dimension_Value.value_id == item['id']):
                    for dimension in Dimension.select().where(Dimension.id == dimension_value.dimension_id):
                        for cube_dimension in Cube_Dimension.select().where(
                                        Cube_Dimension.dimension_id == dimension.id):
                            for cube in Cube.select().where(Cube.id == cube_dimension.cube_id):
                                item['cube'] = cube.name
                item.pop('id', None)

        territory_values.clear()

        for key, value in td.items():
            d = {'type': 'territory_dimension', 'verbal': key}
            for item in value:
                d[item['cube']] = item['fvalue']
            territory_values.append(d)

        values = []
        for cube in Cube.select():
            for dim_cub in Cube_Dimension.select().where(Cube_Dimension.cube_id == cube.id):
                for dimension in Dimension.select().where(Dimension.id == dim_cub.dimension_id):
                    if dimension.label not in ('Years', 'Territories'):
                        for dimension_value in Dimension_Value.select().where(
                                        Dimension_Value.dimension_id == dimension.id):
                            for value in Value.select().where(Value.id == dimension_value.value_id):
                                values.append({
                                    'type': 'dimension',
                                    'cube': cube.name,
                                    'name': dimension.label,
                                    'verbal': value.lem_index_value,
                                    'fvalue': value.cube_value})

        return year_values + territory_values + values

    @staticmethod
    def _create_cubes():
        cubes = []
        for cube in Cube.select():
            cubes.append({
                'type': 'cube',
                'cube': cube.name,
                'description': cube.lem_description})
        return cubes

    @staticmethod
    def _create_measures():
        measures = []
        for measure in Measure.select():
            if measure.cube_value != 'VALUE':
                for cube_measure in Cube_Measure.select().where(Cube_Measure.measure_id == measure.id):
                    for cube in Cube.select().where(Cube.id == cube_measure.cube_id):
                        measures.append({
                            'type': 'measure',
                            'cube': cube.name,
                            'verbal': measure.lem_index_value,
                            'formal': measure.cube_value
                        })
        return measures
