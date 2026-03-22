import json
import re
from typing import Dict, Any, List, Optional, Generator
from ardan.ollama.client import OllamaClient
from ardan.ollama.prompts import EXECUTOR_SYSTEM, TOOL_FORMAT
from ardan.tools.file_tools import read_file, write_file, append_file, list_files, delete_file, search_and_replace, ToolResult
from ardan.tools.shell_tools import run_command, run_script
from ardan.tools.code_tools import lint_python, format_python, search_in_files
from ardan.tools.web_tools import search_web
from ardan.agent.memory import Memory

class Executor:
    def __init__(self, client: OllamaClient, memory: Memory):
        self.client = client
        self.memory = memory
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
            "search_web": search_web
        }

    def execute_step(self, step: Dict[str, Any], max_retries: int = 5) -> Generator[str, None, None]:
        # Construct message history for ReAct loop
        messages = [
            {"role": "system", "content": f"{EXECUTOR_SYSTEM}\n{TOOL_FORMAT}"},
            {"role": "user", "content": f"Task: {step['description']}\nHint: {step.get('tool_hint', '')}"}
        ]

        step_done = False
        steps_taken = 0
        final_summary = ""

        while not step_done and steps_taken < max_retries:
            response_full = ""
            for chunk in self.client.chat(messages, stream=True):
                 response_full += chunk
                 yield chunk # Yield tokens for UI streaming

            self.memory.add_step("EXECUTOR_REASONING", response_full)
            messages.append({"role": "assistant", "content": response_full})

            # Check for <tool> blocks
            tool_calls = re.findall(r"<tool>(.*?)</tool>", response_full, re.DOTALL)

            if tool_calls:
                 for tool_call_str in tool_calls:
                      try:
                           tool_call = json.loads(tool_call_str)
                           tool_name = tool_call.get("name")
                           tool_args = tool_call.get("args", {})

                           if tool_name in self.tools:
                                result: ToolResult = self.tools[tool_name](**tool_args)
                                result_str = f"Success: {result.success}\nOutput: {result.output}\nError: {result.error}"
                                self.memory.add_step("TOOL_RESULT", {"tool": tool_name, "args": tool_args, "result": result_str})
                                messages.append({"role": "user", "content": f"Observation from {tool_name}: {result_str}"})

                                # Record stats
                                if result.success:
                                     if tool_name == "write_file": self.memory.record_file_created(tool_args.get("path"))
                                     if tool_name in ["append_file", "search_and_replace"]: self.memory.record_file_modified(tool_args.get("path"))
                                     if tool_name in ["run_command", "run_script"]: self.memory.record_command_run(tool_args.get("command") or tool_args.get("script_content"))
                                else:
                                     self.memory.record_error(result.error)
                           else:
                                messages.append({"role": "user", "content": f"Error: Tool '{tool_name}' not found."})
                      except json.JSONDecodeError as e:
                           messages.append({"role": "user", "content": f"Error parsing tool call JSON: {str(e)}"})

            # Check for <finished> tag
            finished_match = re.search(r"<finished>(.*?)</finished>", response_full, re.DOTALL)
            if finished_match:
                 final_summary = finished_match.group(1)
                 step_done = True

            steps_taken += 1

        yield f"\n[Step Completed: {final_summary or 'Done'}]\n"

    def run(self, task: str) -> Generator[str, None, None]:
        # Wrapper for running a single task string
        step = {"description": task, "tool_hint": ""}
        yield from self.execute_step(step)
