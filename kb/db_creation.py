from peewee import *

DATABASE = 'knowledge_base.db'
database = SqliteDatabase(DATABASE)


class BaseModel(Model):
    class Meta:
        database = database


class Value(BaseModel):
    full_nvalue = CharField()
    index_nvalue = CharField()
    fvalue = CharField()
    mdx_extra = CharField(null=True)


class Dimension(BaseModel):
    label = CharField()


class Dimension_Value(BaseModel):
    value = ForeignKeyField(Value)
    dimension = ForeignKeyField(Dimension)

    class Meta:
        primary_key = CompositeKey('value', 'dimension')


class Cube(BaseModel):
    name = CharField()
    tags = CharField()


class Cube_Value(BaseModel):
    cube = ForeignKeyField(Cube)
    value = ForeignKeyField(Value)

    class Meta:
        primary_key = CompositeKey('cube', 'value')


class Cube_Dimension(BaseModel):
    dimension = ForeignKeyField(Dimension)
    cube = ForeignKeyField(Cube)

    class Meta:
        primary_key = CompositeKey('dimension', 'cube')


class Documents(BaseModel):
    cube = ForeignKeyField(Cube)
    mdx_query = CharField()
    verbal_query = CharField()


def create_tables():
    database.connect()
    database.create_tables(
        [Dimension, Cube, Cube_Value, Cube_Dimension, Value, Dimension_Value, Documents])


def drop_tables():
    database.drop_tables(
        [Dimension, Cube, Cube_Value, Cube_Dimension, Value, Dimension_Value, Documents])


def create_database(create=True):
    if create:
        create_tables()

        inserts = ""
        with open('knowledge_base.db.sql', 'r', encoding="utf-8") as file:
            inserts = file.read().split(';')[1:-2]

        for i in inserts:
            database.execute_sql(i)
    else:
        drop_tables()

create_database()
# create_database(create=False)