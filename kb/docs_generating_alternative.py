#!/usr/bin/python
# -*- coding: utf-8 -*-

from kb.db_creation import *
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
        data = DocsGenerationAlternative._create_values() + DocsGenerationAlternative._create_cubes()
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
            for dimension_value in Dimension_Value.raw(
                            'select dimension_id from dimension_value where value_id = %s' % value.id):
                for dimension in Dimension.raw(
                                'select label from dimension where id = %s' % dimension_value.dimension_id):
                    values.append(
                        {'verbal': value.lem_index_value, 'dimension': dimension.label, 'fvalue': value.cube_value})
        return values

    @staticmethod
    def _create_cubes():
        cubes = []
        for cube in Cube.select():
            cubes.append({'cube': cube.name, 'tags': cube.lem_description})
        return cubes


# TODO: сделать структуру документа через класс
class DocumentStructure:
    def __init__(self):
        structure = None
