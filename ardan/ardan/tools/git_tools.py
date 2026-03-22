import os
import subprocess
from .file_tools import ToolResult

def git_init(directory: str) -> ToolResult:
    try:
        subprocess.run(["git", "init"], cwd=directory, check=True)
        return ToolResult(True, f"Git repository initialized in {directory}")
    except Exception as e:
        return ToolResult(False, "", str(e))

def git_commit(directory: str, message: str) -> ToolResult:
    try:
        subprocess.run(["git", "add", "."], cwd=directory, check=True)
        subprocess.run(["git", "commit", "-m", message], cwd=directory, check=True)
        return ToolResult(True, f"Committed with message: {message}")
    except Exception as e:
        return ToolResult(False, "", str(e))

def git_branch(directory: str, name: str) -> ToolResult:
    try:
        subprocess.run(["git", "checkout", "-b", name], cwd=directory, check=True)
        return ToolResult(True, f"Switched to new branch: {name}")
    except Exception as e:
        return ToolResult(False, "", str(e))
