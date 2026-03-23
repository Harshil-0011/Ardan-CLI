import os
from typing import Dict, Any, List, Optional, AsyncIterator
from ardan.config.settings import Settings
from ardan.agent.memory import Memory
from ardan.agent.planner import Planner
from ardan.agent.executor import Executor
from ardan.agent.reviewer import Reviewer
from ardan.providers.registry import get_provider_instance, detect_active_provider, failover_generate
from ardan.agent.messages import Message, GenerationConfig

class AgentCore:
    def __init__(self, settings: Settings, provider_override: Optional[str] = None, model_override: Optional[str] = None, workspace_override: Optional[str] = None, session_id: Optional[int] = None):
        self.settings = settings
        self.provider_name = detect_active_provider(
            cli_flag=provider_override,
            env_var=os.getenv("ARDAN_PROVIDER"),
            config_val=settings.get("ardan", "default_provider", "ollama")
        )
        self.workspace = workspace_override or settings.agent_workspace
        os.makedirs(self.workspace, exist_ok=True)

        self.provider = get_provider_instance(self.provider_name, settings.config)
        self.model = model_override or self.provider.default_model
        self.provider.default_model = self.model

        self.memory = Memory(self.workspace, session_id=session_id)
        self.planner = Planner(self.provider)
        self.executor = Executor(self.provider, self.memory, settings=settings.config)
        self.reviewer = Reviewer(self.provider, self.memory)

    async def build_system(self, prompt: str, auto: bool = False) -> AsyncIterator[Dict[str, Any]]:
        # 1. PLAN
        yield {"status": "PLANNING", "message": "Analyzing request..."}
        plan = await self.planner.create_plan(prompt)
        yield {"status": "PLAN_READY", "plan": plan}

        # 2. EXECUTE with dependency management
        completed = set()
        while len(completed) < len(plan):
             ready_steps = [s for s in plan if s["id"] not in completed and all(dep in completed for dep in s.get("depends_on", []))]
             if not ready_steps: break # Circular dependency or error

             if len(ready_steps) > 1:
                  yield {"status": "EXECUTING_PARALLEL", "steps": ready_steps}
                  async for chunk in self.executor.run_parallel(ready_steps):
                       yield {"status": "STEP_PROGRESS", "chunk": chunk}
                  for s in ready_steps: completed.add(s["id"])
             else:
                  step = ready_steps[0]
                  yield {"status": "STEP_START", "step": step}
                  async for chunk in self.executor.execute_step(step):
                       yield {"status": "STEP_PROGRESS", "chunk": chunk}
                  completed.add(step["id"])
                  yield {"status": "STEP_COMPLETE", "step": step}

        # 3. REVIEW (Self-correction)
        yield {"status": "REVIEWING", "message": "Performing senior code review..."}
        fix_plan = await self.reviewer.review_work(prompt)
        if fix_plan:
            yield {"status": "FIXING", "message": "Applying corrections...", "fix_plan": fix_plan}
            for step in fix_plan:
                 async for chunk in self.executor.execute_step(step):
                      yield {"status": "FIX_PROGRESS", "chunk": chunk}

        # 4. CONFIDENCE & SUGGEST
        yield {"status": "FINALIZING", "message": "Finalizing build..."}
        suggestions = await self._generate_suggestions()

        # Calculate confidence score based on tool results and reviewer passes
        errors = len(self.memory.errors)
        steps = len(self.memory.history)
        confidence = max(0.0, 1.0 - (errors / max(1, steps)))

        yield {
            "status": "DONE",
            "message": "System built successfully!",
            "stats": {
                "files_created": self.memory.files_created,
                "commands_run": self.memory.commands_run
            },
            "suggestions": suggestions,
            "confidence": confidence
        }

    async def _generate_suggestions(self) -> List[str]:
        """Use the AI provider to suggest real improvements."""
        prompt = f"Based on the system built so far: {self.memory.get_context_summary()}, suggest 3 specific follow-up improvements."
        msgs = [Message(role="user", content=prompt)]
        res = ""
        async for chunk in self.provider.generate(msgs, GenerationConfig(stream=False)):
             res += chunk
        # Simple split by bullet points or newlines
        return [s.strip() for s in res.split("\n") if s.strip() and (s.strip()[0].isdigit() or s.strip()[0] == "•")][:3]

    async def chat(self, user_input: str) -> AsyncIterator[str]:
        # Simple chat implementation
        messages = [Message(role="user", content=user_input)]
        async for chunk in self.provider.generate(messages, GenerationConfig()):
            yield chunk
