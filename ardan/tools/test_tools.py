import subprocess
from .file_tools import ToolResult


def run_tests(directory: str = ".") -> ToolResult:
    try:
        res = subprocess.run(["pytest", directory], capture_output=True, text=True)
        return ToolResult(res.returncode == 0, res.stdout, res.stderr)
    except Exception as e:
        return ToolResult(False, "", str(e))


def generate_tests_placeholder(file_path: str) -> ToolResult:
    """Agent should use the LLM to write unit tests for the given file."""
    # This tool is a signal for the agent to use its own reasoning
    # and write_file tool to create tests.
    return ToolResult(
        True, f"Agent instruction: analyze {file_path} and write unit tests for it.", ""
    )
