import datetime
import json
import os
import logging
import atexit
import multiprocessing
from multiprocessing import Process

import flask
import discord
import openai
import asyncio
import telebot

from google import genai
from google.genai import types
from flask import request, Flask, jsonify



from dotenv import load_dotenv
from rich.console import Console
from rich.markdown import Markdown
from Modules.Configuration.configure import *
from Modules.Executioner.discord import *
from Modules.Executioner.ponto import bater_ponto
from Modules.Language.response import *

load_dotenv(dotenv_path=".env")
GEMINI_TOKEN = os.getenv('GEMINI_TOKEN')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')

if DISCORD_TOKEN is None:
    print("DISCORD_TOKEN is not found. Make sure the .env file is in the right location.")

gemini_client = genai.Client(api_key=GEMINI_TOKEN, http_options={'api_version': 'v1alpha'})

app = Flask(__name__)
intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.reactions = True
intents.members = True

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
    console.log(f"Request received: {response}")
    console.log(Markdown(Outils().logResponse(request)))
    return response


@app.route('/')
def index():
    return index_html

@app.route('/baterponto')
def bater():
    login = os.getenv('UFFSLOGIN')
    senha = os.getenv('UFFSSENHA')
    try:
        bater_ponto(login, senha, console)
        return jsonify({'message': 'Success'}, 200)
    except Exception as e:
        return jsonify({'message': str(e)}, 500)



def run_flask():
    console.log("Starting Flask app...")
    app.run(host="0.0.0.0", port=5000, use_reloader=False)


def initialize():
    console.log(Markdown(f"""
# PROVIDENTIA NETWORK
## **PROVIDENCE** has awakened.
### Today is {datetime.datetime.now().strftime('%A, %B %d, %Y')}
"""))
    try:
        Setup()
    except Exception as err:
        logging.error(err)

def run_telegram():
    bot = telebot.TeleBot(TELEGRAM_TOKEN)
    console.log(f"Running telegram bot. At ID: {bot.bot_id}")

    @bot.message_handler(func=lambda msg: True)
    def interpret(message):
        response = asyncio.run(Language(gemini_client, console).generate_simple_response(message.text))
        bot.reply_to(message, response)

    bot.infinity_polling()

@atexit.register
def shutdown():
    console.log("Shutting down process..")
    console.log("[red]Shutting down all services...[/red]")


if __name__ == '__main__':
    setup = multiprocessing.Process(target=initialize)
    mainApp = multiprocessing.Process(target=run_flask)
    telegram = multiprocessing.Process(target=run_telegram)
    processes = [setup, mainApp]

    try:
        setup.start()
        setup.join()


        mainApp.start()
        telegram.start()
        # discordApp.start()

        mainApp.join()
    except Exception as err:
        logging.error(f"Error: {err}")
    finally:
        shutdown()
