import datetime
import json
import os
import logging
import atexit
import multiprocessing
import time
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
from Data.models import *
from Modules.Configuration.configure import *
from Modules.Executioner.discord import *
from Modules.Executioner.ponto import bater_ponto
from Modules.Executioner.weather import Weather
from Modules.Language.response import *
from Modules.Security.verify import Verification

from Data import build

load_dotenv(dotenv_path=".env")
DB = SqliteDatabase("main.db")
GEMINI_TOKEN = os.getenv('GEMINI_TOKEN')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')

USER_CONFIG = "Config/preferences.json"



gemini_client = genai.Client(api_key=GEMINI_TOKEN, http_options={'api_version': 'v1alpha'})

app = Flask(__name__)



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

_background_loop = None

def get_background_loop():
    global _background_loop
    if _background_loop is None:
        _background_loop = asyncio.new_event_loop()
        threading.Thread(target=_background_loop.run_forever, daemon=True).start()
    return _background_loop

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
    commands = ["start","help","hello",'weather','clima','note','reminder']
    with open(USER_CONFIG) as f:
        preferred_language = json.load(f)
        preferred_language = preferred_language['preferred_language']


    def verified_handler(**registration_kwargs):
        def decorator(handler):
            @wraps(handler)
            def wrapper(message):
                if not Verification().verify_telegram(message.from_user.id):
                    return bot.reply_to(message, "Forgive me, but I can't respond to you.")
                return handler(message)

            bot.register_message_handler(wrapper, **registration_kwargs)
            return wrapper

        return decorator

    @bot.message_handler(commands=['self_manifest'])
    def self_manifest(message):
        console.log(f"Received self manifest: {message.from_user}")
        bot.reply_to(message,"Você foi identificado pelos meus sistemas.")

    @bot.message_handler(commands=['start','hello','help'])
    def send_welcome(message):
        bot.reply_to(message, f"""Greetings. I am Providentia Magnata, in service of Lygon.\n
        I serve the emperor and the emperor alone. Commands from other people will not be heard, unless they're
        whitelisted.\n
        COMMANDS: {commands}""")

    # Free commands
    @bot.message_handler(commands=['count'])
    def count_time(message):
        count_of_time = message.text.split(' ')
        if len(count_of_time) > 1 and count_of_time[1].isnumeric():
            count_of_time = int(count_of_time[1])
            bot.send_message(message.chat.id, f"Counting {count_of_time} minutes")
            for i in range(count_of_time * 60, 0, -1):
                time.sleep(1)
                if(i % 10) == 0:
                    bot.send_message(message.chat.id, str(i))
            bot.reply_to(message, f"{count_of_time} minute(s) have already passed.")

        else:
            bot.reply_to(message, "Provide a valid argument. FORMAT: /count [INTEGER]")
    # Premium commands
    @verified_handler(commands=['note','reminder'])
    def set_note(message):
        bot.reply_to(message, "Command in development.")

    @verified_handler(commands=['send'])
    def send(message):
        arguments = message.text.split(' ')
        if len(arguments) < 4:
            bot.reply_to(message, "Provide a valid argument. FORMAT: /send [APP] [CHAT ID] [MESSAGE]")
            return

        if arguments[1].lower() == 'discord' and arguments[2].isnumeric():
            chat_id = arguments[2]
            sentence = " ".join(arguments[3:])
            try:
                # This one command schedules the Discord send_message coroutine to run
                asyncio.run_coroutine_threadsafe(
                    DiscordAgent(console_obj=console, gemini_client=gemini_client).send_message(input=sentence,
                                                                                                chat_id=chat_id),
                    get_background_loop()
                )
            except Exception as e:
                bot.reply_to(message, f"Error: {str(e)}")
        else:
            bot.reply_to(message, "Provide a valid argument. FORMAT: /send [APP] [CHAT ID] [MESSAGE]")

    @verified_handler(commands=['weather','clima'])
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
    @verified_handler(func=lambda msg: True)
    def interpret(message):
        previous_messages = TelegramMessages.select().where(TelegramMessages.user_id == int(message.from_user.id)).order_by(TelegramMessages.created_at.desc()).limit(20)
        TelegramMessages.create(user_id = message.from_user.id, content = message.text)
        previous_messages = [f"{message.from_user.first_name} says: {sentence.content} at {sentence.created_at}" for sentence in previous_messages]
        response = asyncio.run(Language(gemini_client, console).generate_simple_response([preferred_language if message.from_user.id == 6320851817 else message.from_user.language_code,
        f"PREVIOUS MESSAGES, FULL CONVERSATION: {previous_messages} - USER MESSAGE: {message.text}"]))
        bot.reply_to(message, response)


    bot.infinity_polling()

@atexit.register
def shutdown():
    console.log("Shutting down process..")
    console.log("[red]Shutting down all services...[/red]")
    DatabaseConstructor(consol=console).terminate_db()


if __name__ == '__main__':
    DatabaseConstructor(consol=console).build()
    setup = multiprocessing.Process(target=initialize)
    mainApp = multiprocessing.Process(target=run_flask)
    telegram = multiprocessing.Process(target=run_telegram)
    processes = [setup, mainApp]

    try:
        setup.start()
        setup.join()


        mainApp.start()
        telegram.start()

        mainApp.join()
    except Exception as err:
        logging.error(f"Error: {err}")
    finally:
        shutdown()
