import json
from text_preprocessing import TextPreprocessing
import uuid
import subprocess
from os import getcwd
from config import SETTINGS
import requests
import pycurl

input_file = 'input_1st_part_minfin_docs.txt'
output_file = 'output_1st_part_minfin_docs.json'


def read_data():
    with open(input_file, 'r') as file:
        data = file.read()
    return json.loads(data)


def normalize_data(data):
    tp = TextPreprocessing(uuid.uuid4())
    for item in data:
        for key, value in item.items():
            if key in ('question', 'key_words'):
                item[key] = tp.normalization(value)
        item['lem_full_answer'] = tp.normalization(item['full_answer'])
    return data


def write_data(data):
    with open(output_file, 'w') as file:
        file.write(json.dumps(data))


def index_data_via_cmd(core='new_minfin', path_to_post_jar_file=SETTINGS.get('PATH_TO_SOLR_POST_JAR_FILE')):
    dlt_str = 'http://localhost:8983/solr/{}/update?stream.body=%3Cdelete%3E%3Cquery%3E*:*%3C/query%3E%3C/delete%3E&commit=true'
    requests.get(dlt_str.format(core))

    path_to_json_data_file = '{}\\{}'.format(getcwd(), output_file)
    command = r'java -Dauto -Dc={} -Dfiletypes=json -jar {} {}'.format(core, path_to_post_jar_file,
                                                                       path_to_json_data_file)
    subprocess.Popen(command, shell=True, stdout=subprocess.PIPE).wait()
    print('Документы проиндексированы')


def index_data_via_curl(core='new_minfin'):
    # TODO: разобраться с pycurl.error: (6, 'Could not resolve: localhost (Domain name not found)')
    dlt_str = 'http://localhost:8983/solr/{}/update?stream.body=%3Cdelete%3E%3Cquery%3E*:*%3C/query%3E%3C/delete%3E&commit=true'
    requests.get(dlt_str.format(core))

    c = pycurl.Curl()
    c.setopt(c.URL, 'http://localhost:8983/solr/{}/update?commit=true'.format(core))
    c.setopt(c.HTTPPOST,
             [
                 ('fileupload',
                  (c.FORM_FILE, getcwd() + '\\{}'.format(output_file),
                   c.FORM_CONTENTTYPE, 'application/json')
                  ),
             ])
    c.perform()


# d = read_data()
# d = normalize_data(d)
# write_data(d)
# index_data()
# index_data_via_curl()
