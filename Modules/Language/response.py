from google import genai
from google.genai import types
from rich import console

from Modules.Prompts import prompts

class Language:
    def __init__(self, gemini_client: genai.Client, console_obj: console.Console):
        self.console = console_obj
        self.gemini_client = gemini_client
        pass

    async def generate_simple_response(self, prompt: list):
        try:
            self.console.log(f"Generating command for prompt: {prompt}")

            system_prompt = f"{prompts.prompts['identity']} - IMPORTANT: REPLY IN USER LANGUAGE {prompt[0]} USER PROMPT: {prompt[1]}"
            response = self.gemini_client.models.generate_content(
                model="gemini-2.0-flash",
                contents=system_prompt,
            )
            return response.text
        except Exception as err:
            return err

    async def generate_from_prompt(self, prompt):
        try:
            self.console.log(f"Generating command for direct prompt.")

            system_prompt = prompt
            response = self.gemini_client.models.generate_content(
                model="gemini-2.0-flash",
                contents=system_prompt,
            )
            return response.text
        except Exception as err:
            return err

    async def generate_economic_summary(self, data: dict):
        try:
            self.console.log(f"Generating economic summary.")

            system_prompt = f"{prompts.prompts['economic_summary']} - CURRENT DATA: {data}"
            response = self.gemini_client.models.generate_content(
                model="gemini-2.0-flash-thinking-exp-01-21",
                contents=system_prompt,
            )
            return response.text
        except Exception as err:
            return err