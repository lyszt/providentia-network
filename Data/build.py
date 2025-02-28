import os

from pandas.io.sql import SQLiteDatabase

from .models import *
import sqlite3
import peewee
from rich import console

class DatabaseConstructor:
    def __init__(self, consol: console.Console):
        self.db = peewee.SqliteDatabase("main.db")
        self.console = consol
    def build(self):
        try:
            self.console.log(f"Connecting to db obj {self.db}")
            self.db.connect()
        except peewee.OperationalError as e:
            if 'Connection already opened' not in str(e):
                self.console.log(e)
                raise
        db_to_create = [Notes]
        self.console.log(f"Creating database items {db_to_create}")
        self.db.create_tables([item for item in db_to_create], safe = True)

    def terminate_db(self):
        def termination():
            db_to_terminate = [Notes]
            self.console.log(f"Initiation of termination procedures. \n")
            self.db.close()
            self.console.log("Termination succeeded.")