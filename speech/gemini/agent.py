import os

from google import genai

class GeminiAgent():
    def __init__(self):
        self.client = genai.Client()

    def generate_response(self, model_name, prompt):
        response = self.client.models.generate_content(
            model=model_name, contents=prompt
        )
        return response
