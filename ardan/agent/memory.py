import os
import json
import time
from typing import List, Dict, Any, Optional
from ardan.agent.messages import Message

class Memory:
    def __init__(self, workspace: str, session_id: Optional[int] = None):
        self.workspace = workspace
        self.session_dir = os.path.join(workspace, ".ardan")
        os.makedirs(self.session_dir, exist_ok=True)
        self.history: List[Dict[str, Any]] = []
        self.files_created: List[str] = []
        self.files_modified: List[str] = []
        self.commands_run: List[str] = []
        self.errors: List[str] = []
        self._cache = {}
        self.backups: Dict[str, str] = {} # path -> content before modification

        if session_id:
             self.session_id = session_id
             self.session_file = os.path.join(self.session_dir, f"session_{self.session_id}.json")
             self._load()
        else:
             # Find latest session if it exists, otherwise create new
             sessions = sorted([s for s in os.listdir(self.session_dir) if s.startswith("session_") and s.endswith(".json")])
             if sessions:
                  self.session_id = int(sessions[-1].split("_")[1].split(".")[0])
                  self.session_file = os.path.join(self.session_dir, sessions[-1])
                  self._load()
             else:
                  self.session_id = int(time.time())
                  self.session_file = os.path.join(self.session_dir, f"session_{self.session_id}.json")

    def _load(self):
        if os.path.exists(self.session_file):
             with open(self.session_file, "r") as f:
                  data = json.load(f)
                  self.history = data.get("history", [])
                  self.files_created = data.get("files_created", [])
                  self.files_modified = data.get("files_modified", [])
                  self.commands_run = data.get("commands_run", [])
                  self.errors = data.get("errors", [])

    def add_step(self, type: str, content: Any):
        step = {"timestamp": time.time(), "type": type, "content": content}
        self.history.append(step)
        self._save()

    def _save(self):
        data = {
            "history": self.history,
            "files_created": self.files_created,
            "files_modified": self.files_modified,
            "commands_run": self.commands_run,
            "errors": self.errors,
            "backups": self.backups
        }
        with open(self.session_file, "w") as f:
            json.dump(data, f, indent=2)

    def get_full_context(self) -> str:
        context = ""
        for h in self.history:
             context += f"[{h['type']}] {str(h['content'])}\n"
        return context

    def get_context_summary(self) -> str:
        summary = ""
        for h in self.history[-10:]:
            summary += f"[{h['type']}] {str(h['content'])[:200]}...\n"
        return summary

    async def summarize(self, provider: Any):
        """Uses the AI provider to summarize the current session history."""
        if len(self.history) < 5: return

        context = self.get_full_context()
        msgs = [
             Message(role="system", content="Summarize the following agent session history into a concise technical summary."),
             Message(role="user", content=context)
        ]
        summary = ""
        from ardan.agent.messages import GenerationConfig
        async for chunk in provider.generate(msgs, GenerationConfig(stream=False)):
             summary += chunk

        self.history = [{"timestamp": time.time(), "type": "SUMMARY", "content": summary}]
        self._save()

    def record_modification(self, path: str):
        """Back up file content before modification."""
        if path not in self.backups and os.path.exists(path):
            try:
                with open(path, "r") as f:
                    self.backups[path] = f.read()
            except:
                pass
        if path not in self.files_modified:
             self.files_modified.append(path)

    def undo_last_run(self):
        """Reverts all file creations and modifications from the session."""
        for f, content in self.backups.items():
            try:
                with open(f, "w") as file:
                    file.write(content)
            except:
                pass

        for f in self.files_created:
            if os.path.exists(f):
                os.remove(f)
        return len(self.files_created) + len(self.backups)

    def get_diff(self) -> str:
        diff = "Changes in this session:\n"
        diff += f"Files Created: {', '.join(self.files_created)}\n"
        diff += f"Files Modified: {', '.join(self.files_modified)}\n"
        return diff
