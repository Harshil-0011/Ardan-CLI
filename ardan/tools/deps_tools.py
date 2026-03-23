import subprocess
import os
import re
from typing import List
from .file_tools import ToolResult

def scan_imports(directory: str) -> ToolResult:
    try:
        imports = set()
        for root, _, files in os.walk(directory):
            for file in files:
                if file.endswith(".py"):
                    with open(os.path.join(root, file), "r") as f:
                        content = f.read()
                        # Simple regex for imports
                        found = re.findall(r"^(?:import|from)\s+([a-zA-Z0-9_]+)", content, re.MULTILINE)
                        imports.update(found)
        return ToolResult(True, ", ".join(sorted(list(imports))), "")
    except Exception as e:
        return ToolResult(False, "", str(e))

def install_missing(packages: List[str]) -> ToolResult:
    try:
        subprocess.run(["pip", "install"] + packages, check=True, capture_output=True)
        return ToolResult(True, f"Installed: {', '.join(packages)}", "")
    except Exception as e:
        return ToolResult(False, "", str(e))
