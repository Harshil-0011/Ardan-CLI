import subprocess
import os
from .file_tools import ToolResult

def generate_test_file(path: str, code_content: str) -> ToolResult:
    """Auto-generate a unit test file for the given code."""
    try:
        # For this tool implementation, we create a boilerplate test
        # In a real build, the AI would generate the specific test cases.
        test_path = os.path.join(os.path.dirname(path), "test_" + os.path.basename(path))
        content = f"import pytest\n\ndef test_logic():\n    # Automatically generated test skeleton for {path}\n    assert True\n"
        with open(test_path, "w") as f:
             f.write(content)
        return ToolResult(True, f"Generated boilerplate test file at {test_path}")
    except Exception as e:
        return ToolResult(False, "", str(e))

def run_tests(directory: str) -> ToolResult:
    try:
        result = subprocess.run(["pytest", directory], capture_output=True, text=True)
        if result.returncode == 0:
             return ToolResult(True, result.stdout)
        else:
             return ToolResult(False, result.stdout, result.stderr)
    except Exception as e:
        return ToolResult(False, "", str(e))
