from peewee import *

DATABASE = 'KB-data.db'
database = SqliteDatabase(DATABASE)


class BaseModel(Model):
    class Meta:
        database = database


class Tag(BaseModel):
    tag = CharField()
    weight = FloatField()

    # class Meta:
    #     database = database


class Collocation(BaseModel):
    collocation = CharField()
    weight = FloatField()

    # class Meta:
    #     database = database


class ThemeType(BaseModel):
    type = CharField()

    # class Meta:
    #     database = database


class Theme(BaseModel):
    tag = ForeignKeyField(Tag, null=True, related_name='d_tag')
    collocation = ForeignKeyField(Collocation, null=True, related_name='d_collocation')
    type = ForeignKeyField(ThemeType, related_name='d_theme')

    # class Meta:
    #     database = database


class ParameterType(BaseModel):
    type = CharField()

    # class Meta:
    #     database = database


# TODO: null==True где нужно, а где нет?
class Parameter(BaseModel):
    type = ForeignKeyField(ParameterType, related_name='p_type')
    tagValue = CharField(null=True)
    feedbackValue = CharField(null=True)
    value1 = CharField(null=True)
    value2 = CharField(null=True)
    value3 = CharField(null=True)

    # class Meta:
    #     database = database


class ParameterMap(BaseModel):
    paramSet = BigIntegerField()
    theme_type = ForeignKeyField(ThemeType, related_name='pm_themeType')
    parameter_type = ForeignKeyField(ParameterType, related_name='pm_parameterType')

    # class Meta:
    #     primary_key = CompositeKey('ParamaterMap_id', 'paramSet')


class ResourceType(BaseModel):
    type = CharField()

    # class Meta:
    #     database = database


class Query(BaseModel):
    parameterMap = ForeignKeyField(ParameterMap, related_name='parameterMap')
    resource1 = ForeignKeyField(ResourceType, related_name='q_resource1')
    resource2 = ForeignKeyField(ResourceType, related_name='q_resource2', null=True)
    resource3 = ForeignKeyField(ResourceType, related_name='q_resource3', null=True)
    templateQuery1 = CharField()
    templateQuery2 = CharField(null=True)
    templateQuery3 = CharField(null=True)

    # class Meta:
    #     database = database


def create_tables():
    database.connect()
    database.create_tables(
        [Tag, Collocation, ThemeType, Theme, ParameterType, Parameter, ParameterMap, ResourceType, Query])


def drop_tables():
    database.drop_tables(
        [Tag, Collocation, ThemeType, Theme, ParameterType, Parameter, ParameterMap, ResourceType, Query])
