import json
import re
import asyncio
from typing import Dict, Any, List, Optional, AsyncIterator
from ardan.agent.messages import Message, GenerationConfig
from ardan.providers.registry import failover_generate
from ardan.tools.file_tools import read_file, write_file, append_file, list_files, delete_file, search_and_replace, ToolResult
from ardan.tools.shell_tools import run_command, run_script, compile_c, compile_cpp, run_binary
from ardan.tools.code_tools import lint_python, format_python, search_in_files
from ardan.tools.git_tools import git_init, git_commit, git_branch, git_status, generate_commit_message
from ardan.tools.test_tools import run_tests, generate_tests_placeholder
from ardan.tools.docker_tools import docker_build, docker_run, generate_dockerfile, generate_compose
from ardan.tools.deps_tools import scan_imports, install_missing
from ardan.tools.diagram_tools import generate_architecture_diagram
from ardan.tools.web_tools import fetch_url, search_web
from ardan.ollama.prompts import EXECUTOR_SYSTEM, TOOL_FORMAT
from ardan.agent.memory import Memory

class Executor:
    def __init__(self, provider: Any, memory: Memory, settings: Any = None):
        self.provider = provider
        self.memory = memory
        self.settings = settings
        self.tools = {
            "read_file": read_file,
            "write_file": write_file,
            "append_file": append_file,
            "list_files": list_files,
            "delete_file": delete_file,
            "search_and_replace": search_and_replace,
            "run_command": run_command,
            "run_script": run_script,
            "lint_python": lint_python,
            "format_python": format_python,
            "search_in_files": search_in_files,
            "git_init": git_init,
            "git_commit": git_commit,
            "git_branch": git_branch,
            "git_status": git_status,
            "generate_commit_message": generate_commit_message,
            "run_tests": run_tests,
            "generate_tests": generate_tests_placeholder,
            "docker_build": docker_build,
            "docker_run": docker_run,
            "generate_dockerfile": generate_dockerfile,
            "generate_compose": generate_compose,
            "scan_deps": scan_imports,
            "auto_install_deps": install_missing,
            "generate_ascii_diagram": generate_architecture_diagram,
            "fetch_url": fetch_url,
            "search_web": search_web,
            "compile_c": compile_c,
            "compile_cpp": compile_cpp,
            "run_binary": run_binary
        }

    async def execute_step(self, step: Dict[str, Any], max_turns: int = 5) -> AsyncIterator[str]:
        messages = [
            Message(role="system", content=f"{EXECUTOR_SYSTEM}\n{TOOL_FORMAT}"),
            Message(role="user", content=f"Task: {step['description']}\nHint: {step.get('tool_hint', '')}")
        ]

        for turn in range(max_turns):
            response_full = ""
            async for chunk in failover_generate(messages, GenerationConfig(), self.provider, self.settings):
                response_full += chunk
                yield chunk

            self.memory.add_step("EXECUTOR_REASONING", response_full)
            messages.append(Message(role="assistant", content=response_full))

            # Tool matching
            tool_calls = re.findall(r"<tool>(.*?)</tool>", response_full, re.DOTALL)
            if not tool_calls:
                if "<finished>" in response_full:
                    break
                continue

            for tc_str in tool_calls:
                try:
                    tc = json.loads(tc_str)
                    name = tc.get("name")
                    args = tc.get("args", {})

                    if name in self.tools:
                        res: ToolResult = self.tools[name](**args)
                        res_str = f"Observation: {res.output}\nError: {res.error}"
                        self.memory.add_step("TOOL_RESULT", {"tool": name, "result": res_str})
                        messages.append(Message(role="user", content=res_str))

                        # Memory tracking
                        if res.success:
                            if name == "write_file": self.memory.files_created.append(args.get("path"))
                            if name in ["append_file", "search_and_replace"]: self.memory.record_modification(args.get("path"))
                            if name in ["run_command", "run_script"]: self.memory.commands_run.append(args.get("command") or "script")
                    else:
                        messages.append(Message(role="user", content=f"Error: Tool {name} not found."))
                except Exception as e:
                    messages.append(Message(role="user", content=f"Error parsing tool call: {str(e)}"))

    async def run_parallel(self, steps: List[Dict[str, Any]]) -> AsyncIterator[str]:
         """Run independent tasks in parallel and stream their outputs."""
         yield f"[Ardan] Initiating parallel execution for {len(steps)} independent tasks...\n"

         queue = asyncio.Queue()

         async def _worker(step):
              async for chunk in self.execute_step(step):
                   await queue.put(chunk)

         workers = [asyncio.create_task(_worker(s)) for s in steps]

         async def _monitor():
              await asyncio.gather(*workers)
              await queue.put(None) # Signal completion

         asyncio.create_task(_monitor())

         while True:
              chunk = await queue.get()
              if chunk is None: break
              yield chunk
