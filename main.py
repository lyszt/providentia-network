import datetime
import json
import os
import logging
import atexit
import multiprocessing

import flask
import discord
import google.generativeai as genai
from flask import request, Flask, jsonify
from dotenv import load_dotenv
from rich.console import Console
from rich.markdown import Markdown
from brasilapy.constants import APIVersion, FipeTipoVeiculo, IBGEProvider, TaxaJurosType
from Modules.Configuration.configure import *
from Modules.Executioner.discord import *
load_dotenv(dotenv_path=".env")
DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')
GEMINI_TOKEN = os.getenv('GEMINI_TOKEN')
genai.configure(api_key=GEMINI_TOKEN)

if DISCORD_TOKEN is None:
    print("DISCORD_TOKEN is not found. Make sure the .env file is in the right location.")

app = Flask(__name__)
intents = discord.Intents.default()
intents.message_content = True

global discord_client
discord_client = discord.Client(intents=intents)

console = Console(color_system="windows")

logging.basicConfig(filename='providence.log',
                    level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s',
                    datefmt="%H:%M:%S")

logger = logging.StreamHandler()
logger.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
logger.setFormatter(formatter)
logging.getLogger('').addHandler(logger)

with open('index.html') as f:
    index_html = f.read()

@app.after_request
def after_request(response: flask.Response):
    logging.info(f"Request received: {response}")
    console.log(Markdown(Outils().logResponse(request)))


@app.route('/')
def index():
    return index_html

def run_discord():
    class DiscordLogger(logging.Handler):
        def emit(self, record):
            console.log(f"[cyan][DISCORD][/cyan] {record.getMessage()}")

    discord_logger = logging.getLogger("discord")
    discord_logger.setLevel(logging.INFO)
    discord_logger.addHandler(DiscordLogger())

    @discord_client.event
    async def on_message(message):
        text_message = message.content.lower()
        if message.author == discord_client.user.bot or message.author == discord_client.user:
            pass
        elif str(message.author.id) == '1047943536374464583':
            if "providentia," in text_message:
                await DiscordAgent().execute_order(message, message.content, discord_client)

    logging.info("Starting Discord bot...")
    discord_client.run(DISCORD_TOKEN)


def run_flask():
    logging.info("Starting Flask app...")
    app.run(host="0.0.0.0", port=5000, use_reloader=False)

def initialize():
    console.log(Markdown(f"""
# PROVIDENTIA NETWORK
## **PROVIDENCE** is online.
### Today is {datetime.datetime.now().strftime('%A, %B %d, %Y')}
"""))
    try:
        Setup()
    except Exception as err:
        logging.error(err)





@atexit.register
def shutdown():
    logging.info("Shutting down processes...")
    console.log("[red]Shutting down all services...[/red]")

if __name__ == '__main__':
    setup = multiprocessing.Process(target=initialize)
    mainApp = multiprocessing.Process(target=run_flask)
    discordApp = multiprocessing.Process(target=run_discord)

    processes = [setup, mainApp, discordApp]

    try:
        setup.start()
        setup.join()

        mainApp.start()
        discordApp.start()

        mainApp.join()
        discordApp.join()
    except Exception as err:
        logging.error(f"Error: {err}")
    finally:
        shutdown()
