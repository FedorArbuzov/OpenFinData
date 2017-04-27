from config import PATH_TO_USER_DB_SERVER, PATH_TO_USER_DB_DIMA
from peewee import *

database = SqliteDatabase(PATH_TO_USER_DB_SERVER)


class BaseModel(Model):
    class Meta:
        database = SqliteDatabase(PATH_TO_USER_DB_SERVER)


class User(BaseModel):
    user_id = IntegerField()
    user_name = CharField()
    full_user_name = CharField()


class Feedback(BaseModel):
    user = ForeignKeyField(User)
    time = CharField()
    feedback = CharField()


def create_tables():
    database.connect()
    database.create_tables(
        [User, Feedback])


def drop_tables():
    database.drop_tables(
        [User, Feedback])

# create_tables()
# drop_tables()
