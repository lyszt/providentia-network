from peewee import Model, CharField, SqliteDatabase, DateTimeField, BooleanField, TextField, IntegerField, \
    ForeignKeyField, FloatField
import os.path
import datetime

db = SqliteDatabase("main.db")
class Notes(Model):
    class Meta:
        database = db

    id = IntegerField(primary_key=True)
    title = CharField(null=False, max_length=255)
    reminder = CharField(null=False)
    date_target = DateTimeField(null=True)
    created_at = DateTimeField(null=True, default = datetime.datetime.now)
    updated_at = DateTimeField(null=True)
    is_pinned = BooleanField(default=False)
    is_archived = BooleanField(default=False)