import os
from typing import Dict, Any, List, Optional, Generator
from ardan.ollama.client import OllamaClient
from ardan.agent.planner import Planner
from ardan.agent.executor import Executor
from ardan.agent.reviewer import Reviewer
from ardan.agent.memory import Memory
from ardan.tools.mcp_tools import MCPManager
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
        self.mcp_manager = MCPManager()
        # Initialize MCP servers from settings
        mcp_config = settings.get("mcp", "servers", {})
        self.mcp_manager.load_from_config(mcp_config)

        self.planner = Planner(self.client)
        self.executor = Executor(self.client, self.memory, mcp_manager=self.mcp_manager)
        self.reviewer = Reviewer(self.client, self.memory)

    def _load_ardan_md(self) -> str:
        ardan_md_path = os.path.join(self.workspace, "ARDAN.md")
        if os.path.exists(ardan_md_path):
            try:
                with open(ardan_md_path, "r") as f:
                    return f"\nProject Context (ARDAN.md):\n{f.read()}\n"
            except:
                pass
        return ""

    def _process_file_references(self, prompt: str, images: List[str] = None) -> str:
        # Simple regex to find @path/to/file references
        import re
        refs = re.findall(r"@([^\s]+)", prompt)
        processed_prompt = prompt

        for ref in refs:
            if os.path.exists(ref):
                try:
                    # Check if it's an image
                    ext = os.path.splitext(ref)[1].lower()
                    if ext in [".png", ".jpg", ".jpeg", ".webp"]:
                         if images is not None:
                              import base64
                              with open(ref, "rb") as f:
                                   images.append(base64.b64encode(f.read()).decode("utf-8"))
                         processed_prompt = processed_prompt.replace(f"@{ref}", f"[Image: {ref}]")
                    else:
                        with open(ref, "r") as f:
                            content = f.read()
                            processed_prompt += f"\n\n--- Content of {ref} ---\n{content}\n"
                except:
                    pass
        return processed_prompt

    def build_system(self, prompt: str, auto: bool = False) -> Generator[Dict[str, Any], None, None]:
        max_steps = self.settings.agent_max_steps
        current_step_count = 0

        # Load project-specific context and process @file references
        project_context = self._load_ardan_md()
        processed_prompt = self._process_file_references(prompt)
        full_prompt = project_context + processed_prompt

        # 1. PLAN
        yield {"status": "PLANNING", "message": "Creating task plan..."}
        plan = self.planner.create_plan(full_prompt)
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
        review_steps = self.reviewer.review_work(full_prompt)

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

    def chat_with_context(self, messages: List[Dict[str, Any]]) -> Generator[str, None, None]:
        # Process the last user message for @file references
        if messages and messages[-1]["role"] == "user":
             images = []
             messages[-1]["content"] = self._process_file_references(messages[-1]["content"], images=images)
             if images:
                  messages[-1]["images"] = images

        for chunk in self.client.chat(messages, stream=True):
             yield chunk
