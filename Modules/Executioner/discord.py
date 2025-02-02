import asyncio
import hashlib
import importlib
import logging
import os
import re
import sys
from concurrent.futures import ThreadPoolExecutor

import requests
import pyperclip
import feedparser
import pyautogui
import keyboard
import threading
from bs4 import BeautifulSoup
from pathlib import Path
from google import genai
from google.genai import types
from rich.console import Console
from main import gemini_client
from .audio import Speak
GEMINI_TOKEN = os.getenv('GEMINI_TOKEN')
import discord
class SecurityError(Exception):
    pass

class DiscordAgent:
    def __init__(self, gemini_client: genai.Client, console_obj: Console):
        self.console = console_obj
        self.gemini_client = gemini_client
        pass

    async def execute_order(self, interaction, request: str, client):
        def setCommand(prompt: str) -> dict:
            try:
                self.console.log(f"Generating command for prompt: {prompt}")

                system_prompt = f"""GENERATE PYTHON CODE FOR DISCORD BOT, REACTING TO USER INSIDE
                FUNCTION:
        Input: {prompt}
        RULES:
        0. Don't query or do anything with message.content. NEVER repeat what the user said
        1. ONLY generate code inside the function: async def execute(message, client, console):
        2. NO markdown, comments, or text formatting
        3. 4-space indentation EXACTLY. Put FOUR SPACES everytime you indent.
        4. Strings should be in the language of the prompt
        5. Strict discord.py syntax
        6. You are strictly prohibited to make if statements
        7. Import all used libraries, if any. 
        8. If doing ssh connections using asyncssh, use known_hosts=None
        ======================================
        EXAMPLE OUTPUT:
        async def execute(message, client, console):
            await interaction.response.send_message("Greetings.")
        

        """
                response = gemini_client.models.generate_content(
                    model="gemini-2.0-flash-thinking-exp-01-21",
                    config={'thinking_config': {'include_thoughts': True}},
                    contents=system_prompt,
                )

                # Clean the generated code
                clean_code = re.sub(
                    r'```.*?```|#.*|"interaction"|`',
                    '',
                    response.text
                ).strip()
                clean_code = clean_code.replace("python","", 1)
                process = {
                    'command_code': clean_code,
                    'thoughts': [part for part in response.candidates[0].content.parts if part.thought]
                }

                return process
            except Exception as e:
                self.console.log(f"[red]Command generation error: {str(e)}[\\red]")
                code = '''async def execute(message, client, console)
            await interaction.response.send_message("Systems critical - engineer required.")'''
                process = {
                    'command_code': code,
                    'thoughts': []
                }
                return process

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
                self.console.log(f"C[red]Command build failed: {e}[\\red]")
                return None

        async def execute_module(interaction, client, module, logger):
            if module and hasattr(module, 'execute'):
                try:
                    await module.execute(interaction, client, logger)
                except Exception as err:
                    await interaction.channel.send(f"Detected error: {err}")

        # Unified audio generation function
        def build_audio(text):
            Speak().text_to_speech(text)
            Speak().play_audio("temp/speech.mp3")

        # Main command handler
        result = setCommand(request)
        module = buildCommand(result['command_code'])

        if result['thoughts']:
            for thought in result['thoughts']:
                self.console.log(f"[green]{thought}[/green]")  # Fixed closing tag
                # Process all thoughts in parallel
                with ThreadPoolExecutor() as pool:
                    await asyncio.get_event_loop().run_in_executor(
                        pool,
                        build_audio,
                        thought
                    )
        else:
            # Offload blocking Gemini call to thread
            with ThreadPoolExecutor() as pool:
                thought = await asyncio.get_event_loop().run_in_executor(
                    pool,
                    lambda: gemini_client.models.generate_content(
                        model="gemini-1.5-flash",
                        contents=f"You are a voice assistant."
                                 f"In first person, summarize the actions you have performed in {result['command_code']}."
                                 f"Speak in past tense."
                                 f"Be respectful, serious, and call me sir.",
                    )
                )

            self.console.log(f"[green]{thought.text}[/green]")

            # Run module execution and audio in parallel
            with ThreadPoolExecutor() as pool:
                await asyncio.gather(
                    execute_module(interaction, client, module, self.console),
                    asyncio.get_event_loop().run_in_executor(
                        pool,
                        build_audio,
                        thought.text
                    )
                )


