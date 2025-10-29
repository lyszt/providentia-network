import json
import uuid  # --- (NEW) --- Import the UUID module

from pydantic import BaseModel, Field
import datetime
from ..gemini.agent import GeminiAgent
from typing import Any, Optional

# --- ContextStruct (No changes needed) ---
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
    is_done_thinking: bool = Field(
        description="Are these enough steps of thought or should we continue?"
    )
    regrets_choice: bool = Field(
        description="Are you going the right way? Should you return back to a previous step?"
    )


# --- Updated ThinkingManager ---
class ThinkingManager:
    def __init__(self, message, iteration: int = 0, previous: Optional["ThinkingManager"] = None,
                 summarized_thought=""):
        gemini_agent = GeminiAgent()
        self.next = []
        self.id = str(uuid.uuid4())  # --- (NEW) --- Assign a unique ID to this thought

        self.previous = previous

        if previous is not None:
            previous.next.append(self)

        self.message = message
        self.iteration = iteration
        self.iteration += 1
        self.max_iterations = 15
        analysis_prompt: str = f"""
        You are an intelligent AI classifier. 
        Your task is to analyze the user's message and detail
        each field according to the message received. 
        [ Filling instructions ]
        steps_to_complete: Fill this field with what the agent will need to perform to make the user happy. 
        user_enquiry: Describe the user request in detail. 
        needs_command: Does the user require a command in the command list? [Currently there is no command list, so keep it false. ]
        [LAST THOUGHT]
        {summarized_thought}
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

            if not self.context["is_done_thinking"] and self.iteration <= self.max_iterations:
                summarize_thought = GeminiAgent().generate_response("gemini-2.5-flash-lite", "Summarize "
                                                                                             f"the thought process in first person: {self.context}")
                ThinkingManager(previous=self, message=message, summarized_thought=summarize_thought)

        except (json.JSONDecodeError, Exception) as e:
            print(f"Error decoding command from LLM: {e}")
            self.context = None

    def build_thought_tree_prompt(self) -> str:
        """
        Builds a text representation of the entire thought process
        by traversing up to the root, then recursively printing the tree.
        """

        root = self
        while root.previous is not None:
            root = root.previous

        output_lines = []
        self._build_tree_recursive(root, 0, output_lines)
        print("\n".join(output_lines))
        return "\n".join(output_lines)

    def _build_tree_recursive(self, node: "ThinkingManager", depth: int, output_lines: list):
        """
        Recursively traverses the thought tree and build the string.
        """
        if node.context is None:
            return

        indent = "  " * depth
        plan = node.context.get('steps_for_completion', 'No plan generated.')
        regrets = node.context.get('regrets_choice', False)

        prefix = ""
        if regrets:
            prefix = "[REGRETTED] "
        elif node.context.get('is_done_thinking', False):
            prefix = "[FINAL] "

        output_lines.append(f"{indent}{prefix}Thought (ID: {node.id}, Depth: {depth}): {plan}")

        for child_node in node.next:
            self._build_tree_recursive(child_node, depth + 1, output_lines)

    def generate_self_prompt(self):
        thought_tree_string = self.build_thought_tree_prompt()

        root = self
        while root.previous is not None:
            root = root.previous
        original_user_message = root.message

        return f"""
        [ ORIGINAL USER MESSAGE ]
        {original_user_message}

        [ I need to respond to this user. ]
        [ Here is my complete thought process on how to answer: ]
        {thought_tree_string}

        [ Based on this plan, provide the final response. Follow the *last* thought. ]
        """