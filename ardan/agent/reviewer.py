import json
from typing import Dict, Any, List, Optional
from ardan.agent.messages import Message, GenerationConfig
from ardan.ollama.prompts import REVIEWER_SYSTEM
from ardan.agent.memory import Memory

class Reviewer:
    def __init__(self, provider: Any, memory: Memory):
        self.provider = provider
        self.memory = memory

    async def review_work(self, task: str) -> Optional[List[Dict[str, Any]]]:
        # Construct summary of work for reviewer
        context = self.memory.get_full_context()
        files_created = ", ".join(self.memory.files_created)
        files_modified = ", ".join(self.memory.files_modified)
        commands_run = ", ".join(self.memory.commands_run)

        prompt = f"""
        Original Task: {task}
        Files Created: {files_created}
        Files Modified: {files_modified}
        Commands Run: {commands_run}

        History of actions:
        {context}

        Review the work and determine if it's complete and correct according to the original task.
        """

        msgs = [
             Message(role="system", content=REVIEWER_SYSTEM),
             Message(role="user", content=prompt)
        ]
        config = GenerationConfig(stream=False)
        response = ""
        async for chunk in self.provider.generate(msgs, config):
             response += chunk

        if "PASSED" in response:
            return None

        # If not passed, parse the response into a list of new steps
        # Similar logic to Planner
        try:
             start_index = response.find("[")
             end_index = response.rfind("]") + 1
             if start_index != -1 and end_index != 0:
                  json_str = response[start_index:end_index]
                  new_steps = json.loads(json_str)
                  return new_steps
             else:
                  # Fallback: create a single step with the feedback
                  return [{"id": 999, "description": f"Fix issues reported by reviewer: {response}", "tool_hint": "", "depends_on": []}]
        except (json.JSONDecodeError, ValueError):
             return [{"id": 999, "description": f"Fix issues reported by reviewer: {response}", "tool_hint": "", "depends_on": []}]
