import datetime
import json
import os
import logging
import atexit
import multiprocessing
from functools import wraps
from multiprocessing import Process

import flask
import discord
import openai
import asyncio
import telebot
import pandas
from bcb import sgs

from dateutil.relativedelta import relativedelta

from google import genai
from google.genai import types
from flask import request, Flask, jsonify



from dotenv import load_dotenv
from peewee import SqliteDatabase
from rich.console import Console
from rich.markdown import Markdown

from Data.build import DatabaseConstructor
from Modules.Configuration.configure import *
from Modules.Executioner.discord import *
from Modules.Executioner.ponto import bater_ponto
from Modules.Executioner.weather import Weather
from Modules.Language.response import *
from Modules.Security.verify import Verification

from Data import build

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
        DatabaseConstructor(consol=console).build()
    except Exception as err:
        logging.error(err)

def run_telegram():
    bot = telebot.TeleBot(TELEGRAM_TOKEN)
    console.log(f"Running telegram bot. At ID: {bot.bot_id}")
    commands = ["start","help","hello",'weather','clima','note','reminder']

    def requires_verification(func):
        @wraps(func)
        def wrapper(message):
            if Verification().verify_telegram(message.from_user.id):
                return func(message)
            else:
                bot.reply_to(message, "Forgive me, but I can't respond to you.")
            return wrapper

    @bot.message_handler(commands=['start','hello','help'])
    def send_welcome(message):
        bot.reply_to(message, f"""Greetings. I am Providentia Magnata, in service of Lygon.\n
        I serve the emperor and the emperor alone. Commands from other people will not be heard, unless they're
        whitelisted.\n
        COMMANDS: {commands}""")

    @bot.message_handler(commands=['note','reminder'])
    @requires_verification
    def set_note(message):
        bot.reply_to(message, "Command in development.")
    @bot.message_handler(commands=['weather','clima'])
    @requires_verification
    def send_weather(message):

            weather = asyncio.run(Weather().get())
            response = asyncio.run(Language(gemini_client, console).generate_from_prompt(f"""
            Based on what you know about the city of Chapecó, explain this weather,
            and describe it. Say if it's normal or anomalous, the geographic information
            of Chapecó climate. Say hello to the user, he's asking for the current climate.
            
            Write everything in paragraphs without using special formatting. Don't make anything
            bold, just use plain simple text.
            {weather}
            """))
            bot.reply_to(message, response)
    @bot.message_handler(func=lambda msg: True)
    @requires_verification
    def interpret(message):
        response = asyncio.run(Language(gemini_client, console).generate_simple_response(message.text))
        bot.reply_to(message, response)

    bot.infinity_polling()

@atexit.register
def shutdown():
    console.log("Shutting down process..")
    console.log("[red]Shutting down all services...[/red]")
    DatabaseConstructor(consol=console).terminate_db()


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
