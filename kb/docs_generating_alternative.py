#!/usr/bin/python
# -*- coding: utf-8 -*-

from kb.kb_db_creation import *
from os import getcwd, remove
import json
import pycurl
import requests
import subprocess


class DocsGenerationAlternative:
    def __init__(self, core):
        self.file_name = 'kb\data_for_indexing.json'
        self.core = core

    def generate_docs(self):
        data = DocsGenerationAlternative._create_values() + \
               DocsGenerationAlternative._create_cubes() +\
               DocsGenerationAlternative._create_measures()

        self._write_to_file(data)

    def clear_index(self):
        dlt_str = 'http://localhost:8983/solr/{}/update?stream.body=%3Cdelete%3E%3Cquery%3E*:*%3C/query%3E%3C/delete%3E&commit=true'
        requests.get(dlt_str.format(self.core))
        try:
            remove('{}\\{}'.format(getcwd(), self.file_name))
        except FileNotFoundError:
            pass

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
        values = []
        for value in Value.select():
            for dimension_value in Dimension_Value.select().where(Dimension_Value.value_id == value.id):
                for dimension in Dimension.select().where(Dimension.id == dimension_value.dimension_id):
                    for dim_cub in Cube_Dimension.select().where(Cube_Dimension.dimension_id == dimension.id):
                        for cube in Cube.select().where(Cube.id == dim_cub.cube_id):
                            values.append({
                                'type': 'dimension',
                                'cube': cube.name,
                                'name': dimension.label,
                                'verbal': value.lem_index_value,
                                'fvalue': value.cube_value})
        return values

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

    # TODO: сделать структуру документа через класс
    class DocumentStructure:
        def __init__(self):
            structure = None
