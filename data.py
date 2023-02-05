#!/usr/bin/env python
from peewee import *
from playhouse.sqlite_ext import SqliteExtDatabase
import datetime


db = SqliteExtDatabase('data.db')


class BaseModel(Model):
    class Meta:
        database = db


class Website(BaseModel):
    chat_id = CharField()
    url = CharField()
    created_date = DateTimeField(default=datetime.datetime.now)
    method = CharField(default='')
    param = CharField(default='')
    last = CharField(default='')


db.connect()

if not Website.table_exists():
    db.create_tables([Website])