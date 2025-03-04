import os
from .models import *
import sqlite3
import peewee
from rich import console

class DatabaseConstructor:
    def __init__(self, consol: console.Console):
        self.db = peewee.SqliteDatabase("main.db")
        self.console = consol
        self.console.log("Running database constructor.")
        self.databases = [Notes, TelegramMessages]
    def build(self):
        self.console.log("Building database...")
        try:
            self.console.log(f"Connecting to db obj {self.db} to {os.getcwd()}")
            self.db.connect()
        except peewee.OperationalError as e:
            if 'Connection already opened' not in str(e):
                self.console.log(e)
                raise
        self.console.log(f"Creating database items {self.databases}")
        self.db.create_tables([item for item in self.databases], safe = True)

    def terminate_db(self):
        def termination():
            db_to_terminate = [self.databases]
            self.console.log(f"Initiation of termination procedures. \n")
            self.db.close()
            self.console.log("Termination succeeded.")