import json
from typing import List, Dict, Any
from ardan.ollama.client import OllamaClient
from ardan.ollama.prompts import PLANNER_SYSTEM

class Planner:
    def __init__(self, client: OllamaClient):
        self.client = client

    def create_plan(self, prompt: str) -> List[Dict[str, Any]]:
        # Using generate with system prompt for planner
        response = self.client.generate(prompt, system=PLANNER_SYSTEM, stream=False)

        # Clean response if it contains anything outside the JSON array
        # Simple heuristic: find the first [ and the last ]
        try:
            start_index = response.find("[")
            end_index = response.rfind("]") + 1
            if start_index == -1 or end_index == 0:
                 raise ValueError("JSON array not found in LLM response.")

            json_str = response[start_index:end_index]
            plan = json.loads(json_str)
            return plan
        except (json.JSONDecodeError, ValueError) as e:
            # Fallback or error reporting
            raise Exception(f"Failed to parse plan from LLM: {str(e)}\nRaw response: {response}")

    def display_plan(self, plan: List[Dict[str, Any]]):
        # UI logic will handle the actual Rich table display
        pass
