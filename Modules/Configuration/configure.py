# System
import datetime
import logging
import os
import shutil
import pathlib

# Essential
import flask
import peewee
import sqlite3
import logging
import requests
from werkzeug.exceptions import UnsupportedMediaType


# ==============================================================

#=============================================
class Outils:
    def __init__(self):
        pass
    def logResponse(self, request) -> str:
        response = f"""
## Request received.
=============================
- **Method:** {request.method}
- **Path:** {request.path}
- **Remote Address:** {request.remote_addr}
"""
        try:
            response += f"**Form Data**: {request.form}\n"
        except UnsupportedMediaType:
            pass
        try:
            logging.info(f"JSON Data: {request.get_json()}\n")
        except UnsupportedMediaType:
            pass
        return response

class Setup:
    def __init__(self):
        self.makeTemp()

    # TEMPORARY FILES

    def makeTemp(self):
        TEMP = "temp"
        if os.path.exists(TEMP) and os.path.isdir(TEMP):
            for filename in os.listdir(TEMP):
                file_path = os.path.join(TEMP, filename)
                os.remove(file_path)
        else:
            try:
                original_umask = os.umask(0)
                os.makedirs('temp', 0o777)  # Use octal notation
            finally:
                os.umask(original_umask)
