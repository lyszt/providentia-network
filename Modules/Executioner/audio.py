import os

import pygame
from openai import OpenAI
from pathlib import Path

class Speak:
    def __init__(self):
        pass
    def text_to_speech(self, text: str):
        client = OpenAI()
        speech_filepath = os.path.join("temp", "speech.mp3")
        try:
            os.remove(speech_filepath)
        except FileNotFoundError:
            pass
        with client.audio.speech.with_streaming_response.create(
            model="tts-1",
            voice="coral",
            input=f"{text}",
        ) as response:
            response.stream_to_file(speech_filepath)

    def play_audio(self, filename):
        pygame.mixer.init()
        pygame.mixer.music.load(filename)
        pygame.mixer.music.play()
