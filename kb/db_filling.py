from kb.kb_db_creation import *
from kb.kb_support_library import create_automative_cube_description
from text_preprocessing import TextPreprocessing
from os import remove, getcwd, path
import json

sep1 = ';'


class KnowledgeBaseSupport:
    def __init__(self, data_source_file, db_file):
        self.data_source_file = data_source_file
        self.db_file = db_file

    def set_up_db(self, overwrite=False):
        self._create_db(overwrite=overwrite)
        if self.data_source_file.endswith('.sql'):
            data_source_file_path = '{}\\{}\\{}'.format(getcwd(), 'kb', self.data_source_file)
            # Чтение данных из файла
            with open(data_source_file_path, 'r', encoding="utf-8") as file:
                inserts = file.read().split(';')[1:-2]

            # Построчное исполнение команд
            for i in inserts:
                database.execute_sql(i)
        else:
            data_set_list = self._read_data()

            if type(data_set_list) is not list:
                data_set_list = [data_set_list]

            KnowledgeBaseSupport._transfer_data_to_db(data_set_list)
            KnowledgeBaseSupport._create_cube_lem_description(data_set_list)

    def _create_db(self, overwrite=False):
        db_file_path = r'{}\{}\{}'.format(getcwd(), 'kb', self.db_file)
        if overwrite:
            try:
                remove(db_file_path)
                create_tables()
            except FileNotFoundError:
                create_tables()
        else:
            if not path.isfile(db_file_path):
                create_tables()

    @staticmethod
    def read_data():
        data_set_list = []

        # cube_metadata_file = '{}\\{}\\{}'.format(getcwd(), 'kb', 'cubes_metadata.txt')
        cube_metadata_file = '{}\\{}'.format(getcwd(), 'cubes_metadata.txt')

        with open(cube_metadata_file, 'r', encoding='utf-8') as file:
            data = file.read()
        cube_metadata = json.loads(data)

        tp = TextPreprocessing('Filling db')

        for item in cube_metadata:
            cube_data_set = DataSet()
            cube_data_set.cube = {'name': item['formal_name'],
                                  'lem_description': '-'}

            for dimension in item['dimensions']:
                cube_data_set.dimensions[dimension['name'].upper()] = None

            for measure in item['measures']:
                cube_data_set.measures.append({'full_value': measure['caption'],
                                               'lem_index_value': tp.normalization(measure['caption']),
                                               'cube_value': measure['name']})
            for element in item['cube_elements']:
                dim_name = element['hierarchyName'].upper()
                if not cube_data_set.dimensions[dim_name]:
                    cube_data_set.dimensions[dim_name] = []

                # игнорирование "не указанных", "не определенных" параметров
                normalized_elem = tp.normalization(element['caption'])
                if not [item for item in ('неуказанный', 'не определить') if item in normalized_elem]:
                    cube_data_set.dimensions[dim_name].append({'full_value': element['caption'],
                                                               'lem_index_value': normalized_elem,
                                                               'cube_value': element['name']})
            data_set_list.append(cube_data_set)

        return data_set_list

    @staticmethod
    def _transfer_data_to_db(data_set):
        for item in data_set:
            # Занесение куба
            cube = Cube.create(**item.cube)

            # Занесение мер & связка мер с кубов
            for measure in item.measures:
                m = Measure.create(**measure)
                Cube_Measure.create(cube=cube, measure=m)

            # Занесение измерений & занесение значений & связка значений и измерений
            for dimension_name, dimension_values in item.dimensions.items():
                d = Dimension.create(label=dimension_name)
                Cube_Dimension.create(cube=cube, dimension=d)
                for dimension_value in dimension_values:
                    v = Value.create(**dimension_value)
                    Dimension_Value.create(value=v, dimension=d)

    @staticmethod
    def _create_cube_lem_description(data_set):
        cubes = [item.cube['name'] for item in data_set]
        for cube in Cube.select().where(Cube.name in cubes):
            if cube.lem_description == '-':
                description = create_automative_cube_description(cube.name)
                Cube.update(lem_description=description).where(Cube.name == cube.name).execute()


class DataSet:
    def __init__(self):
        self.cube = None
        self.dimensions = {}
        self.measures = []


def fill_new_cubes():
    import time
    start_time = time.time()
    data = KnowledgeBaseSupport.read_data()
    print("Прреобразование данных выполнялось за {} секунд".format(time.time() - start_time))
    start_time = time.time()
    KnowledgeBaseSupport._transfer_data_to_db(data)
    print("Занесение данных в БД выполнялось за {} секунд".format(time.time() - start_time))
    start_time = time.time()
    KnowledgeBaseSupport._create_cube_lem_description(data)
    print("Создание автоматического описания выполнялось за {} секунд".format(time.time() - start_time))


# fill_new_cubes()
