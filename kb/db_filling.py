from kb.db_creation import *
from text_normalization import normalization
from os import remove, getcwd, path

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
            KnowledgeBaseSupport._transfer_data_to_db(data_set_list)

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

    def _read_data(self):
        data_set_list = []

        data_source_file_path = '{}\\{}\\{}'.format(getcwd(), 'data', self.data_source_file)
        with open(data_source_file_path, encoding='utf-8') as file:
            data_set = None
            dimension_flag = ''

            for line in file:
                if line.startswith('Cube'):
                    if not data_set:
                        data_set = DataSet()
                    else:
                        data_set_list.append(data_set)
                        data_set = DataSet()

                    line = line.split(sep1)
                    data_set.cube = {'name': line[2].strip(), 'description': line[1].strip()}
                elif line.startswith('Measures'):
                    line = line.split(sep1)

                    value = line[1].split(" - ")

                    cube_value = value[0].strip()
                    verbal_value = value[1].strip()

                    if '-' in verbal_value:
                        verbal_value = verbal_value.split('-')[1]

                    data_set.measures.append({'full_value': verbal_value,
                                              'lem_index_value': normalization(verbal_value, type='lem'),
                                              'cube_value': cube_value})

                else:
                    line = line.split(sep1)
                    line[0] = line[0].strip()

                    if dimension_flag != line[0]:
                        data_set.dimensions[line[0]] = []
                        dimension_flag = line[0]

                    value = line[1].split(" - ")
                    try:
                        cube_value = value[0].strip()
                        verbal_value = value[1].strip()

                        if '-' in verbal_value:
                            verbal_value = verbal_value.split('-')[1]

                        data_set.dimensions[line[0]].append({'full_value': verbal_value,
                                                             'lem_index_value': normalization(verbal_value, type='lem'),
                                                             'cube_value': cube_value})
                    except IndexError:
                        data_set.dimensions[line[0]].append({'full_value': line[1], 'lem_index_value': line[1],
                                                             'cube_value': line[1]})
            data_set_list.append(data_set)

        return data_set_list

    @staticmethod
    def _transfer_data_to_db(data_set):
        # Если добавляется один куб
        if type(data_set) is not list:
            data_set = [data_set]

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


class DataSet:
    def __init__(self):
        self.cube = None
        self.dimensions = {}
        self.measures = []


# peewee - помнить про insert_many, dicts(), tuples()