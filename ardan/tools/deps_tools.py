import subprocess
import os
from .file_tools import ToolResult

def scan_deps(directory: str) -> ToolResult:
    try:
        # Simple scan looking for common files like requirements.txt, etc.
        deps = []
        if os.path.exists(os.path.join(directory, "requirements.txt")):
             deps.append("Python requirements.txt")
        if os.path.exists(os.path.join(directory, "package.json")):
             deps.append("Node.js package.json")
        return ToolResult(True, f"Found dependencies for: {', '.join(deps)}")
    except Exception as e:
        return ToolResult(False, "", str(e))

def auto_install_deps(directory: str) -> ToolResult:
    try:
        if os.path.exists(os.path.join(directory, "requirements.txt")):
             subprocess.run(["pip", "install", "-r", "requirements.txt"], cwd=directory, check=True)
             return ToolResult(True, "Python dependencies installed.")
        elif os.path.exists(os.path.join(directory, "package.json")):
             subprocess.run(["npm", "install"], cwd=directory, check=True)
             return ToolResult(True, "Node.js dependencies installed.")
        return ToolResult(False, "", "No dependencies file found.")
    except Exception as e:
        return ToolResult(False, "", str(e))
