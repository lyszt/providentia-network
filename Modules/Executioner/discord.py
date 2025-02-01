import hashlib
import importlib
import logging
import os
import re
import sys
import requests
import feedparser
from brasilapy.constants import TaxaJurosType
from bs4 import BeautifulSoup
from pathlib import Path
import google.generativeai as genai
from google.generativeai.types import HarmCategory, HarmBlockThreshold
from brasilapy import BrasilAPI
import discord

class SecurityError(Exception):
    pass

class DiscordAgent:
    def __init__(self):
        pass

    async def execute_order(self, interaction, request: str, client):
        def setCommand(prompt: str) -> str:
            try:
                logging.info(f"Generating command for prompt: {prompt}")
                model = genai.GenerativeModel("gemini-2.0-flash-exp",
                                              generation_config={"temperature": 0.2})

                system_prompt = f"""GENERATE PYTHON CODE FOR DISCORD BOT, REACTING TO USER INSIDE
                FUNCTION:
        Input: {prompt}
        RULES:
        0. Don't query or do anything with message.content. NEVER repeat what the user said
        1. ONLY generate code inside the function: async def execute(message, client):
        2. NO markdown, comments, or text formatting
        3. 4-space indentation EXACTLY. Put FOUR SPACES everytime you indent.
        4. Strings should be in the language of the prompt
        5. Strict discord.py syntax
        6. You are strictly prohibited to make if statements
        7. Import all used libraries, if any. Do not import
        OBS: You can use brasilapy to find information about Brazil.
        Example usage:
        from brasilapy.constants import APIVersion, FipeTipoVeiculo, IBGEProvider, TaxaJurosType
        from brasilapy import BrasilAPI
        client = BrasilAPI()
        feriados = client.get_feriados();
        # brasilAPI is not asynchronous. BrasilAPI responds with class objects.
        Access using feriados.name, for example
        ======================================
        EXAMPLE OUTPUT:
        async def execute(interaction):
            await interaction.response.send_message("Greetings.")
        

        """
                response = model.generate_content(system_prompt,
                                                  safety_settings={
                                                      HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
                                                      HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
                                                  })

                logging.info(f"Generated command: {response.text} - Input: {prompt}")

                # Clean the generated code
                clean_code = re.sub(
                    r'```.*?```|#.*|"interaction"|`',
                    '',
                    response.text
                ).strip()

                # Ensure it starts with the correct function definition
                if not clean_code.startswith("async def execute(interaction):"):
                    clean_code = f"async def execute(interaction):\n    {clean_code}"

                return clean_code
            except Exception as e:
                logging.error(f"Command generation error: {str(e)}")
                return '''async def execute(interaction):
            await interaction.response.send_message("Systems critical - engineer required.")'''

        def buildCommand(command_code: str):
            try:
                # 1. Create temp directory if needed
                os.makedirs("temp", exist_ok=True)

                # 2. Write to temp/command.py
                file_path = os.path.join("temp", "command.py")
                with open(file_path, "w", encoding='UTF-8') as f:
                    f.write(command_code)

                # 3. Import from temp directory
                spec = importlib.util.spec_from_file_location(
                    "temp.command",
                    file_path
                )
                command_module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(command_module)

                return command_module

            except Exception as e:
                logging.error(f"Command build failed: {e}")
                return None

        logging.info("Creating dynamic command...")
        command_code = setCommand(request)
        module = buildCommand(command_code)
        if module and hasattr(module, 'execute'):
            try:
                await module.execute(interaction, client)
            except Exception as err:
                await interaction.channel.send(f"Detected error: {err}")