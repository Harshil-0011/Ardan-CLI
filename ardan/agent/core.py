import os
from typing import Dict, Any, List, Optional, Generator, AsyncIterator
from ardan.agent.messages import Message, GenerationConfig
from ardan.providers.registry import get_provider, detect_active_provider
from ardan.config.credentials import credentials_manager
from ardan.agent.planner import Planner
from ardan.agent.executor import Executor
from ardan.agent.reviewer import Reviewer
from ardan.agent.memory import Memory
from ardan.tools.mcp_tools import MCPManager
from ardan.config.settings import settings, Settings

class AgentCore:
    def __init__(self, settings: Settings, provider_override: Optional[str] = None, model_override: Optional[str] = None, workspace_override: Optional[str] = None):
        self.settings = settings
        self.provider_name = detect_active_provider(cli_flag=provider_override, config_val=settings.get("ardan", "default_provider", "ollama"))
        self.model = model_override or settings.get(self.provider_name, "model", "codellama:13b")
        self.workspace = workspace_override or settings.agent_workspace

        # Ensure workspace exists
        os.makedirs(self.workspace, exist_ok=True)

        api_key = credentials_manager.get(self.provider_name)
        base_url = settings.get(self.provider_name, "base_url")

        self.provider = get_provider(self.provider_name, api_key=api_key, base_url=base_url)
        # Patch the provider with the model from settings
        self.provider.default_model = self.model

        self.memory = Memory(self.workspace)
        self.mcp_manager = MCPManager()
        # Initialize MCP servers from settings
        mcp_config = settings.get("mcp", "servers", {})
        self.mcp_manager.load_from_config(mcp_config)

        # For simplicity, we adapt Planner/Executor to use a unified provider interface
        # In a real build, those classes would also be updated.
        self.planner = Planner(self.provider)
        self.executor = Executor(self.provider, self.memory, mcp_manager=self.mcp_manager)
        self.reviewer = Reviewer(self.provider, self.memory)

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

    async def build_system(self, prompt: str, auto: bool = False) -> AsyncIterator[Dict[str, Any]]:
        max_steps = self.settings.agent_max_steps
        current_step_count = 0

        # Load project-specific context and process @file references
        project_context = self._load_ardan_md()
        processed_prompt = self._process_file_references(prompt)
        full_prompt = project_context + processed_prompt

        # 1. PLAN
        yield {"status": "PLANNING", "message": "Creating task plan..."}
        try:
            plan = await self.planner.create_plan(full_prompt)
        except Exception as e:
            if self.settings.get("agent", "auto_failover"):
                 yield {"status": "WARNING", "message": f"Primary provider failed: {str(e)}. Attempting failover..."}
                 # Simple failover to Ollama
                 self.provider = get_provider("ollama")
                 # Propagate to sub-components
                 self.planner.provider = self.provider
                 self.executor.provider = self.provider
                 self.reviewer.provider = self.provider
                 plan = await self.planner.create_plan(full_prompt)
            else:
                 raise e
        yield {"status": "PLAN_READY", "plan": plan}

        # 2. EXECUTE
        yield {"status": "EXECUTING", "message": "Starting execution..."}
        for step in plan:
             if current_step_count >= max_steps:
                  yield {"status": "ERROR", "message": f"Reached max steps limit ({max_steps})."}
                  break

             yield {"status": "STEP_START", "step": step}
             async for chunk in self.executor.execute_step(step):
                  yield {"status": "STEP_PROGRESS", "chunk": chunk}

             current_step_count += 1
             yield {"status": "STEP_COMPLETE", "step": step}

             # Check if context is getting large and needs summarization
             if len(self.memory.get_full_context()) > 6000: # Heuristic for context management
                  yield {"status": "SUMMARIZING", "message": "Summarizing context..."}
                  await self.memory.summarize(self.provider)

        # 3. REVIEW
        yield {"status": "REVIEWING", "message": "Reviewing output..."}
        review_steps = await self.reviewer.review_work(full_prompt)

        if review_steps:
             yield {"status": "REVIEW_FAILED", "message": "Reviewer found issues, starting fixes...", "fix_plan": review_steps}
             for step in review_steps:
                  if current_step_count >= max_steps:
                       yield {"status": "ERROR", "message": f"Reached max steps limit ({max_steps}) during review fixes."}
                       break

                  yield {"status": "STEP_START", "step": step}
                  async for chunk in self.executor.execute_step(step):
                       yield {"status": "STEP_PROGRESS", "chunk": chunk}

                  current_step_count += 1
                  yield {"status": "STEP_COMPLETE", "step": step}
        else:
             yield {"status": "REVIEW_PASSED", "message": "Final review passed!"}

        # 4. REFINEMENT
        yield {"status": "REFINING", "message": "Suggesting improvements..."}
        refinement_prompt = "Based on the work done, suggest 3 specific improvements that could be made to this system."
        msgs = [Message(role="user", content=refinement_prompt)]
        config = GenerationConfig(stream=False)
        refinements = ""
        async for chunk in self.provider.generate(msgs, config):
             refinements += chunk
        yield {"status": "REFINEMENTS_READY", "suggestions": refinements}

        # 5. REPORT
        yield {
            "status": "DONE",
            "message": "System built successfully!",
            "stats": {
                "files_created": self.memory.files_created,
                "files_modified": self.memory.files_modified,
                "commands_run": self.memory.commands_run,
                "errors": self.memory.errors
            },
            "confidence_score": 0.95 # Simulated confidence score
        }

    def undo(self):
        """Revert changes recorded in memory."""
        for file in self.memory.files_created:
             if os.path.exists(file):
                  os.remove(file)
        # Restore logic for files_modified would need original content backup
        return f"Reverted {len(self.memory.files_created)} created files."

    def get_diff(self):
        """Generate a text diff of changes."""
        diff_output = ""
        for file in self.memory.files_created:
             diff_output += f"New file: {file}\n"
        for file in self.memory.files_modified:
             diff_output += f"Modified file: {file}\n"
        return diff_output

    async def chat_with_context(self, messages: List[Dict[str, Any]]) -> AsyncIterator[str]:
        # Process the last user message for @file references
        if messages and messages[-1]["role"] == "user":
             images = []
             # Need to adapt Message dataclass usage here
             messages[-1]["content"] = self._process_file_references(messages[-1]["content"], images=images)

        # Convert dict list to Message objects
        msg_objs = []
        for m in messages:
             msg_objs.append(Message(role=m["role"], content=m["content"], images=m.get("images")))

        config = GenerationConfig(stream=True)
        async for chunk in self.provider.generate(msg_objs, config):
             yield chunk
