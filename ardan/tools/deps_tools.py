import subprocess
import os
import re
from typing import List
from .file_tools import ToolResult

def scan_imports(directory: str) -> ToolResult:
    """
    Optimized scan of Python files to find unique top-level imports.
    Uses 'ast' for precision and skips common non-library files.
    """
    try:
        import ast
        imports = set()
        # Exclude directories that don't contain source code to speed up walk
        exclude_dirs = {'.git', '__pycache__', 'node_modules', 'venv', '.venv', 'dist', 'build'}

        for root, dirs, files in os.walk(directory):
            # Prune directories in-place for faster traversal
            dirs[:] = [d for d in dirs if d not in exclude_dirs]

            for file in files:
                if file.endswith(".py"):
                    file_path = os.path.join(root, file)
                    try:
                        with open(file_path, "r", encoding="utf-8") as f:
                            # Performance boost: Use ast.parse on the file content
                            # but skip files larger than 1MB to avoid memory issues
                            if os.path.getsize(file_path) > 1024 * 1024:
                                continue

                            tree = ast.parse(f.read(), filename=file_path)
                            for node in ast.walk(tree):
                                if isinstance(node, ast.Import):
                                    for name in node.names:
                                        imports.add(name.name.split('.')[0])
                                elif isinstance(node, ast.ImportFrom):
                                    if node.module:
                                        imports.add(node.module.split('.')[0])
                    except (UnicodeDecodeError, SyntaxError):
                        continue
        return ToolResult(True, ", ".join(sorted(list(imports))), "")
    except Exception as e:
        return ToolResult(False, "", str(e))

def install_missing(packages: List[str]) -> ToolResult:
    try:
        subprocess.run(["pip", "install"] + packages, check=True, capture_output=True)
        return ToolResult(True, f"Installed: {', '.join(packages)}", "")
    except Exception as e:
        return ToolResult(False, "", str(e))
