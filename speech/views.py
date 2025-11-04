import json
import os

from django.shortcuts import render

from .context_manager.ThinkingManager import ThinkingManager
from .gemini import agent as gemini_agent
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

MAX_CHARS = 4080

@api_view(['POST'])
def deep_think(request):
    """
    Deep thinking view: runs the ThinkingManager (heavy) to produce a final response.
    """
    prompt = str(request.data.get('prompt', '')).strip()
    agent = gemini_agent.GeminiAgent()

    instructions = (
        "Answer directly. You are in a chat environment.\n"
        f"{ThinkingManager(message=prompt).generate_self_prompt()}"
    )

    try:
        response = agent.generate_response("gemini-2.5-flash", instructions).text
    except Exception as error:
        return Response({"error": str(error)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    if len(response) > MAX_CHARS:
        response = response[:MAX_CHARS - 12] + "\n\n[truncated]"

    return Response({"response": response}, status=status.HTTP_200_OK)


@api_view(['POST'])
def simple_response(request):
    """
    Lightweight simple response view: directly queries Gemini with the provided prompt
    and returns the text without invoking the ThinkingManager.
    """
    prompt = str(request.data.get('prompt', '')).strip()
    if not prompt:
        return Response({"error": "No prompt provided."}, status=status.HTTP_400_BAD_REQUEST)

    agent = gemini_agent.GeminiAgent()

    instructions = (
        "You are a helpful assistant. Answer the user's prompt directly and concisely.\n"
        f"User prompt: {prompt}\n"
        "Provide only the answer text, no extra metadata."
    )

    try:
        response = agent.generate_response("gemini-2.5-flash-lite", instructions).text
    except Exception as error:
        return Response({"error": str(error)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    if len(response) > MAX_CHARS:
        response = response[:MAX_CHARS - 12] + "\n\n[truncated]"

    return Response({"response": response}, status=status.HTTP_200_OK)
