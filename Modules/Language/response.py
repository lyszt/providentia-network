from google import genai
from google.genai import types
from rich import console

from Modules.Prompts import prompts

class Language:
    def __init__(self, gemini_client: genai.Client, console_obj: console.Console):
        self.console = console_obj
        self.gemini_client = gemini_client
        pass

    async def generate_simple_response(self, prompt):
        try:
            self.console.log(f"Generating command for prompt: {prompt}")

            system_prompt = f"{prompts.prompts['identity']} - USER PROMPT: {prompt}"
            response = self.gemini_client.models.generate_content(
                model="gemini-2.0-flash",
                contents=system_prompt,
            )
            return response.text
        except Exception as err:
            return err