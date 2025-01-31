import datetime
import json

# App
import flask
import discord
from flask import request, Flask, jsonify
# Essentials
import os
from dotenv import load_dotenv
import logging
# Tools
from rich.console import Console
from rich.markdown import Markdown
# IMPORTED MODULES
from Modules.Configuration.configure import *

load_dotenv(dotenv_path=".env")

DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')
if DISCORD_TOKEN is None:
    print("DISCORD_TOKEN is not found. Make sure the .env file is in the right location.")
app = Flask(__name__)
console = Console(color_system="windows")

intents = discord.Intents.default()
intents.message_content = True
discord_client = discord.Client(intents=intents)

with open('index.html') as f:
    index_html = f.read()

@app.after_request
def after_request(response: flask.Response):
    logging.info(f"Request received: {response}")
    console.print(Markdown(Outils().logResponse(request)))
    return response
@app.route('/')
def index():
    return index_html

if __name__ == '__main__':
    console.print(Markdown(f"""
# PROVIDENTIA NETWORK
## **PROVIDENCE**is online. Today is {datetime.datetime.now().strftime('%A, %B %d, %Y')}"""))
    Setuṕ()
    discord_client.run(DISCORD_TOKEN)
    app.run(debug=True)

