from peewee import *

DATABASE = 'knowledge_base.db'
database = SqliteDatabase(DATABASE)


class BaseModel(Model):
    class Meta:
        database = database


class Tag(BaseModel):
    value = CharField()
    displayValue = CharField(null=True)


class ParameterName(BaseModel):
    name = CharField()


class Parameter(BaseModel):
    name = ForeignKeyField(ParameterName)


class ParameterSet(BaseModel):
    id = BigIntegerField(primary_key=True)


class Parameter_ParameterSet(BaseModel):
    parameter = ForeignKeyField(Parameter)
    parameterSet = ForeignKeyField(ParameterSet)


class ExampleRequests(BaseModel):
    parameterSet = ForeignKeyField(ParameterSet)
    request = CharField()


class LOV(BaseModel):
    parameter = ForeignKeyField(Parameter)


class Value(BaseModel):
    lov = ForeignKeyField(LOV)
    tag = ForeignKeyField(Tag)
    value = CharField()


class DimensionLabel(BaseModel):
    label = CharField()


class Dimension(BaseModel):
    parameter = ForeignKeyField(Parameter)
    label = ForeignKeyField(DimensionLabel)


class Resource(BaseModel):
    type = CharField()
    name = CharField(null=True)
    tags = CharField()
    description = CharField()


class Measure(BaseModel):
    label = CharField
    parameter = ForeignKeyField(Parameter)


class Cube(BaseModel):
    resource = ForeignKeyField(Resource, primary_key=True)


class Cube_Measure(BaseModel):
    measure = ForeignKeyField(Measure)
    cube = ForeignKeyField(Cube)

    class Meta:
        primary_key = CompositeKey('measure', 'cube')


class Cube_Dimension(BaseModel):
    dimension = ForeignKeyField(Dimension)
    cube = ForeignKeyField(Cube)
    mdx_transformation = CharField()

    class Meta:
        primary_key = CompositeKey('dimension', 'cube')


class Query(BaseModel):
    resource = ForeignKeyField(Resource)
    parameterSet = ForeignKeyField(ParameterSet)
    cube = ForeignKeyField(Cube)
    mdx_template = CharField()
    request_template = CharField()


class Resource_Parameter(BaseModel):
    resource = ForeignKeyField(Resource)
    parameter = ForeignKeyField(Parameter)

    class Meta:
        primary_key = CompositeKey('resource', 'parameter')


class ResourceLink(BaseModel):
    resource1 = BigIntegerField()
    resource2 = BigIntegerField()


class ParameterMap(BaseModel):
    resourceLink = ForeignKeyField(ResourceLink)
    fromParam = ForeignKeyField(Parameter, related_name='from_param')
    toParam = ForeignKeyField(Parameter, related_name='to_param')


class ResourceLink_ParameterSet(BaseModel):
    resourceLink = ForeignKeyField(ResourceLink)
    parameterSet = ForeignKeyField(ParameterSet)


def create_tables():
    database.connect()
    database.create_tables(
        [Tag, ParameterName, Parameter, ParameterSet, Parameter_ParameterSet, ExampleRequests,LOV, Value,
         DimensionLabel, Dimension, Resource, Measure, Cube, Cube_Measure, Cube_Dimension, Query, Resource_Parameter,
         ResourceLink, ParameterMap, ResourceLink_ParameterSet])


def drop_tables():
    database.drop_tables(
        [Tag, ParameterName, Parameter, ParameterSet, Parameter_ParameterSet, ExampleRequests, LOV, Value,
         DimensionLabel, Dimension, Resource, Measure, Cube, Cube_Measure, Cube_Dimension, Query, Resource_Parameter,
         ResourceLink, ParameterMap, ResourceLink_ParameterSet])