import json
import re
from typing import Dict, Any, List, Optional, Generator
from ardan.ollama.client import OllamaClient
from ardan.ollama.prompts import EXECUTOR_SYSTEM, TOOL_FORMAT
from ardan.tools.file_tools import read_file, write_file, append_file, list_files, delete_file, search_and_replace, ToolResult
from ardan.tools.shell_tools import run_command, run_script, compile_c, compile_cpp, run_binary
from ardan.tools.code_tools import lint_python, format_python, search_in_files, investigate_codebase
from ardan.tools.web_tools import search_web, fetch_url
from ardan.tools.git_tools import git_init, git_commit, git_branch
from ardan.tools.test_tools import run_tests
from ardan.tools.docker_tools import docker_build, docker_run, generate_dockerfile, generate_docker_compose
from ardan.tools.deps_tools import scan_deps, auto_install_deps
from ardan.tools.diagram_tools import generate_ascii_diagram
from ardan.tools.mcp_tools import MCPManager
from ardan.agent.memory import Memory
from ardan.agent.messages import Message, GenerationConfig
from typing import Dict, Any, List, Optional, AsyncIterator

class Executor:
    def __init__(self, provider: Any, memory: Memory, mcp_manager: MCPManager = None):
        self.provider = provider
        self.memory = memory
        self.mcp_manager = mcp_manager or MCPManager()
        self.tools = {
            "read_file": read_file,
            "write_file": write_file,
            "append_file": append_file,
            "list_files": list_files,
            "delete_file": delete_file,
            "search_and_replace": search_and_replace,
            "run_command": run_command,
            "run_script": run_script,
            "compile_c": compile_c,
            "compile_cpp": compile_cpp,
            "run_binary": run_binary,
            "lint_python": lint_python,
            "format_python": format_python,
            "search_in_files": search_in_files,
            "investigate_codebase": investigate_codebase,
            "search_web": search_web,
            "fetch_url": fetch_url,
            "git_init": git_init,
            "git_commit": git_commit,
            "git_branch": git_branch,
            "run_tests": run_tests,
            "docker_build": docker_build,
            "docker_run": docker_run,
            "generate_dockerfile": generate_dockerfile,
            "generate_docker_compose": generate_docker_compose,
            "scan_deps": scan_deps,
            "auto_install_deps": auto_install_deps,
            "generate_ascii_diagram": generate_ascii_diagram
        }

    async def execute_step(self, step: Dict[str, Any], max_retries: int = 5) -> AsyncIterator[str]:
        # Construct message history for ReAct loop
        # Include summary of previous actions for context
        history_context = self.memory.get_full_context()
        context_prompt = f"\nPrevious Actions Context:\n{history_context}\n" if history_context else ""

        messages = [
            Message(role="system", content=f"{EXECUTOR_SYSTEM}\n{TOOL_FORMAT}"),
            Message(role="user", content=f"{context_prompt}Current Task: {step['description']}\nHint: {step.get('tool_hint', '')}")
        ]

        step_done = False
        steps_taken = 0
        final_summary = ""

        while not step_done and steps_taken < max_retries:
            response_full = ""
            config = GenerationConfig(stream=True)
            async for chunk in self.provider.generate(messages, config):
                 response_full += chunk
                 yield chunk # Yield tokens for UI streaming

            self.memory.add_step("EXECUTOR_REASONING", response_full)
            messages.append(Message(role="assistant", content=response_full))

            # Check for <tool> blocks
            tool_calls = re.findall(r"<tool>(.*?)</tool>", response_full, re.DOTALL)

            if tool_calls:
                 for tool_call_str in tool_calls:
                      try:
                           tool_call = json.loads(tool_call_str)
                           tool_name = tool_call.get("name")
                           tool_args = tool_call.get("args", {})

                           result = None
                           if tool_name in self.tools:
                                result = self.tools[tool_name](**tool_args)
                           elif self.mcp_manager and tool_name in self.mcp_manager.tools:
                                result = self.mcp_manager.call_tool(tool_name, tool_args)

                           if result:
                                result_str = f"Success: {result.success}\nOutput: {result.output}\nError: {result.error}"
                                self.memory.add_step("TOOL_RESULT", {"tool": tool_name, "args": tool_args, "result": result_str})
                                messages.append(Message(role="user", content=f"Observation from {tool_name}: {result_str}"))

                                # Record stats
                                if result.success:
                                     if tool_name == "write_file": self.memory.record_file_created(tool_args.get("path"))
                                     if tool_name in ["append_file", "search_and_replace"]: self.memory.record_file_modified(tool_args.get("path"))
                                     if tool_name in ["run_command", "run_script"]: self.memory.record_command_run(tool_args.get("command") or tool_args.get("script_content"))
                                else:
                                     self.memory.record_error(result.error)
                           else:
                                messages.append(Message(role="user", content=f"Error: Tool '{tool_name}' not found."))
                      except json.JSONDecodeError as e:
                           messages.append(Message(role="user", content=f"Error parsing tool call JSON: {str(e)}"))

            # Check for <finished> tag
            finished_match = re.search(r"<finished>(.*?)</finished>", response_full, re.DOTALL)
            if finished_match:
                 final_summary = finished_match.group(1)
                 step_done = True

            steps_taken += 1

        yield f"\n[Step Completed: {final_summary or 'Done'}]\n"

    async def run(self, task: str) -> AsyncIterator[str]:
        # Wrapper for running a single task string
        step = {"description": task, "tool_hint": ""}
        async for chunk in self.execute_step(step):
             yield chunk

    async def execute_parallel(self, steps: List[Dict[str, Any]]) -> AsyncIterator[str]:
        # In a real implementation, we'd use concurrent.futures
        # For this CLI, we yield sequentially but mark it as a parallel batch
        yield "[Starting Parallel Execution Batch]\n"
        for step in steps:
             async for chunk in self.execute_step(step):
                  yield chunk
