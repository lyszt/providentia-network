import json
import os

from django.shortcuts import render

from .context_manager.ContextManager import ContextManager
from .gemini import agent as gemini_agent
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

@api_view(['POST'])
def simple_response(request):
    """ Fast response using a lighter model."""
    agent = gemini_agent.GeminiAgent()

    prompt = request.data.get('prompt', '')
    instructions = ContextManager(message=prompt).generate_self_prompt()
    print(instructions)



    model = "gemini-2.5-flash-lite"
    try:
        data = {
            "response": agent.generate_response(model, instructions).text
        }
    except Exception as e:
        data = {
            "error": str(e)
        }
        return Response(data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    return Response(data, status=status.HTTP_200_OK)
