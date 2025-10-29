import json

from pydantic import BaseModel, Field
import datetime
from ..gemini.agent import GeminiAgent
from typing import Any

class ContextStruct(BaseModel):
    user_enquiry: str = Field(
        description="The raw, unaltered text query received from the user."
    )
    user_name: str = Field(
        description="The display name or identifier for the user who sent the query."
    )
    needs_command: bool = Field(
        description="A flag indicating if the query requires an external tool or command to be executed."
    )
    client_platform: str = Field(
        description="The source application the query originated from."
    )
    category: str = Field(
        description="The general classification or topic of the user's enquiry."
    )
    steps_for_completion: str = Field(
        description="The high-level plan or steps generated for the AI agent to follow."
    )
    date_of_request: datetime.datetime = Field(
        default_factory=datetime.datetime.now,
        description="The timestamp marking when this context object was created."
    )

class ContextManager:
    def __init__(self, message):
        gemini_agent = GeminiAgent()
        self.message = message
        analysis_prompt: str = f"""
        You are an intelligent AI classifier. 
        Your task is to analyze the user's message and detail
        each field according to the message received. 
        [ Filling instructions ]
        steps_to_complete: Fill this field with what the agent will need to perform to make the user happy. 
        user_enquiry: Describe the user request in detail. 
        needs_command: Does the user require a command in the command list? [Currently there is no command list, so keep it false. ]
        
        [ USER MESSAGE ] 
        {self.message}

        """

        try:
            response = gemini_agent.client.models.generate_content(
                model="gemini-2.5-flash-lite",
                config={
                    "response_mime_type": "application/json",
                    "response_schema": ContextStruct,
                },
                contents=analysis_prompt
            )

            command_obj = ContextStruct.model_validate_json(response.text)
            self.context = command_obj.model_dump()

        except (json.JSONDecodeError, Exception) as e:
            print(f"Error decoding command from LLM: {e}")
            self.context = None

    def generate_self_prompt(self):
        lines_list = [f"{key}: {value}" for key, value in self.context.items()]
        analyzed_context_string = "\n".join(lines_list)

        return f"""
        {self.message}
        [ I need to respond to this user. ]
        [ Here are the instruction and context needed to respond. Follow the plan throughly. ]
        {analyzed_context_string}
        """

