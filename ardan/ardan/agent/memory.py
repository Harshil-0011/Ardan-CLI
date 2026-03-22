import os
import json
import time
from typing import List, Dict, Any

class Memory:
    def __init__(self, workspace: str):
        self.workspace = workspace
        self.session_dir = os.path.join(workspace, ".ardan")
        os.makedirs(self.session_dir, exist_ok=True)
        self.session_file = os.path.join(self.session_dir, f"session_{int(time.time())}.json")
        self.history: List[Dict[str, Any]] = []
        self.files_created: List[str] = []
        self.files_modified: List[str] = []
        self.commands_run: List[str] = []
        self.errors: List[str] = []

    def add_step(self, step_type: str, content: Any):
        step = {
            "timestamp": time.time(),
            "type": step_type,
            "content": content
        }
        self.history.append(step)
        self._save_session()

    def record_file_created(self, path: str):
        if path not in self.files_created:
            self.files_created.append(path)

    def record_file_modified(self, path: str):
        if path not in self.files_modified:
            self.files_modified.append(path)

    def record_command_run(self, command: str):
        self.commands_run.append(command)

    def record_error(self, error: str):
        self.errors.append(error)

    def _save_session(self):
        data = {
            "history": self.history,
            "files_created": self.files_created,
            "files_modified": self.files_modified,
            "commands_run": self.commands_run,
            "errors": self.errors
        }
        with open(self.session_file, "w") as f:
            json.dump(data, f, indent=2)

    def get_full_context(self) -> str:
        # Simple string representation of history for LLM context
        context_parts = []
        for step in self.history:
             context_parts.append(f"[{step['type']}] {step['content']}")
        return "\n".join(context_parts)

    async def summarize(self, provider: Any):
        """Summarize the current history using the LLM to keep context window manageable."""
        if not self.history:
            return

        context = self.get_full_context()
        prompt = f"Summarize the following agent history into a concise summary that preserves all key actions, decisions, and findings:\n\n{context}"

        from ardan.agent.messages import Message, GenerationConfig
        msgs = [
             Message(role="system", content="You are a helpful assistant that summarizes technical logs."),
             Message(role="user", content=prompt)
        ]
        config = GenerationConfig(stream=False)
        summary = ""
        async for chunk in provider.generate(msgs, config):
             summary += chunk

        # Reset history to a single summary step
        self.history = [{
            "timestamp": time.time(),
            "type": "SUMMARY",
            "content": summary
        }]
        self._save_session()
