import os
from typing import Dict, Any, List, Optional, Generator
from ardan.ollama.client import OllamaClient
from ardan.agent.planner import Planner
from ardan.agent.executor import Executor
from ardan.agent.reviewer import Reviewer
from ardan.agent.memory import Memory
from ardan.config.settings import Settings

class AgentCore:
    def __init__(self, settings: Settings, model_override: Optional[str] = None, workspace_override: Optional[str] = None):
        self.settings = settings
        self.model = model_override or settings.ollama_model
        self.workspace = workspace_override or settings.agent_workspace

        # Ensure workspace exists
        os.makedirs(self.workspace, exist_ok=True)

        self.client = OllamaClient(
            base_url=settings.ollama_base_url,
            model=self.model,
            temperature=settings.ollama_temperature,
            num_ctx=settings.ollama_num_ctx
        )

        self.memory = Memory(self.workspace)
        self.planner = Planner(self.client)
        self.executor = Executor(self.client, self.memory)
        self.reviewer = Reviewer(self.client, self.memory)

    def build_system(self, prompt: str, auto: bool = False) -> Generator[Dict[str, Any], None, None]:
        max_steps = self.settings.agent_max_steps
        current_step_count = 0

        # 1. PLAN
        yield {"status": "PLANNING", "message": "Creating task plan..."}
        plan = self.planner.create_plan(prompt)
        yield {"status": "PLAN_READY", "plan": plan}

        # 2. EXECUTE
        yield {"status": "EXECUTING", "message": "Starting execution..."}
        for step in plan:
             if current_step_count >= max_steps:
                  yield {"status": "ERROR", "message": f"Reached max steps limit ({max_steps})."}
                  break

             yield {"status": "STEP_START", "step": step}
             for chunk in self.executor.execute_step(step):
                  yield {"status": "STEP_PROGRESS", "chunk": chunk}

             current_step_count += 1
             yield {"status": "STEP_COMPLETE", "step": step}

             # Check if context is getting large and needs summarization
             if len(self.memory.get_full_context()) > 6000: # Heuristic for context management
                  yield {"status": "SUMMARIZING", "message": "Summarizing context..."}
                  self.memory.summarize(self.client)

        # 3. REVIEW
        yield {"status": "REVIEWING", "message": "Reviewing output..."}
        review_steps = self.reviewer.review_work(prompt)

        if review_steps:
             yield {"status": "REVIEW_FAILED", "message": "Reviewer found issues, starting fixes...", "fix_plan": review_steps}
             for step in review_steps:
                  if current_step_count >= max_steps:
                       yield {"status": "ERROR", "message": f"Reached max steps limit ({max_steps}) during review fixes."}
                       break

                  yield {"status": "STEP_START", "step": step}
                  for chunk in self.executor.execute_step(step):
                       yield {"status": "STEP_PROGRESS", "chunk": chunk}

                  current_step_count += 1
                  yield {"status": "STEP_COMPLETE", "step": step}
        else:
             yield {"status": "REVIEW_PASSED", "message": "Final review passed!"}

        # 4. REPORT
        yield {
            "status": "DONE",
            "message": "System built successfully!",
            "stats": {
                "files_created": self.memory.files_created,
                "files_modified": self.memory.files_modified,
                "commands_run": self.memory.commands_run,
                "errors": self.memory.errors
            }
        }

    def chat(self, user_msg: str) -> Generator[str, None, None]:
        # Simple chat interaction for REPL
        for chunk in self.client.chat([{"role": "user", "content": user_msg}], stream=True):
             yield chunk
