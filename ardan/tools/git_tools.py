import subprocess
from .file_tools import ToolResult


def git_init(path: str) -> ToolResult:
    try:
        subprocess.run(["git", "init"], cwd=path, check=True, capture_output=True)
        return ToolResult(True, f"Initialized git repo in {path}", "")
    except Exception as e:
        return ToolResult(False, "", str(e))


def git_commit(message: str, cwd: str = ".") -> ToolResult:
    try:
        subprocess.run(["git", "add", "."], cwd=cwd, check=True, capture_output=True)
        subprocess.run(
            ["git", "commit", "-m", message], cwd=cwd, check=True, capture_output=True
        )
        return ToolResult(True, f"Committed: {message}", "")
    except Exception as e:
        return ToolResult(False, "", str(e))


def git_branch(name: str, cwd: str = ".") -> ToolResult:
    try:
        subprocess.run(
            ["git", "checkout", "-b", name], cwd=cwd, check=True, capture_output=True
        )
        return ToolResult(True, f"Created and switched to branch {name}", "")
    except Exception as e:
        return ToolResult(False, "", str(e))


def git_status(cwd: str = ".") -> ToolResult:
    try:
        res = subprocess.run(
            ["git", "status"], cwd=cwd, check=True, capture_output=True, text=True
        )
        return ToolResult(True, res.stdout, "")
    except Exception as e:
        return ToolResult(False, "", str(e))


def generate_commit_message(cwd: str = ".") -> ToolResult:
    """Agent should use LLM to generate message from diff."""
    return ToolResult(
        True,
        "Agent instruction: run 'git diff', analyze it, and write a commit message.",
        "",
    )
