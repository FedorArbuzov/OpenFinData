from config import SETTINGS
from peewee import *

database = SqliteDatabase(SETTINGS.PATH_TO_KNOWLEDGEBASE)


class BaseModel(Model):
    class Meta:
        database = SqliteDatabase(SETTINGS.PATH_TO_KNOWLEDGEBASE)


class Value(BaseModel):
    full_value = CharField()
    lem_index_value = CharField()
    cube_value = CharField()


class Measure(BaseModel):
    full_value = CharField()
    lem_index_value = CharField()
    cube_value = CharField()
    format = CharField()


class Dimension(BaseModel):
    label = CharField()


class Dimension_Value(BaseModel):
    value = ForeignKeyField(Value)
    dimension = ForeignKeyField(Dimension)

    class Meta:
        primary_key = CompositeKey('value', 'dimension')


class Cube(BaseModel):
    name = CharField()
    lem_description = CharField()
    default_measure = ForeignKeyField(Measure, null=True)


class Cube_Dimension(BaseModel):
    dimension = ForeignKeyField(Dimension)
    cube = ForeignKeyField(Cube)

    class Meta:
        primary_key = CompositeKey('dimension', 'cube')


class Cube_Measure(BaseModel):
    measure = ForeignKeyField(Measure)
    cube = ForeignKeyField(Cube)

    class Meta:
        primary_key = CompositeKey('measure', 'cube')


def create_tables():
    database.connect()
    database.create_tables(
        [Dimension, Cube, Measure, Cube_Measure, Cube_Dimension, Dimension_Value, Value])


def drop_tables():
    database.drop_tables(
        [Dimension, Cube, Measure, Cube_Measure, Cube_Dimension, Dimension_Value, Value])
