import os
import subprocess
from .file_tools import ToolResult

def lint_python(path: str) -> ToolResult:
    try:
        # Check if ruff exists
        ruff_check = subprocess.run(["ruff", "--version"], capture_output=True, text=True)
        if ruff_check.returncode == 0:
            result = subprocess.run(["ruff", "check", path], capture_output=True, text=True)
            if result.returncode == 0:
                 return ToolResult(True, "No lint errors found by ruff.")
            else:
                 return ToolResult(False, result.stdout, result.stderr)
        else:
            # Fallback to py_compile
            import py_compile
            py_compile.compile(path, doraise=True)
            return ToolResult(True, "No syntax errors found by py_compile.")
    except Exception as e:
        return ToolResult(False, "", str(e))

def format_python(path: str) -> ToolResult:
    try:
        # Check if black exists
        black_check = subprocess.run(["black", "--version"], capture_output=True, text=True)
        if black_check.returncode == 0:
             result = subprocess.run(["black", path], capture_output=True, text=True)
             if result.returncode == 0:
                  return ToolResult(True, "File formatted successfully by black.")
             else:
                  return ToolResult(False, result.stdout, result.stderr)
        else:
             return ToolResult(False, "", "Black not installed.")
    except Exception as e:
        return ToolResult(False, "", str(e))

def search_in_files(directory: str, query: str) -> ToolResult:
    try:
        # Simple grep-like search using os.walk
        results = []
        for root, dirs, files in os.walk(directory):
            for file in files:
                file_path = os.path.join(root, file)
                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        for i, line in enumerate(f, 1):
                            if query in line:
                                results.append(f"{file_path}:{i}: {line.strip()}")
                except (UnicodeDecodeError, PermissionError):
                    continue

        if results:
            return ToolResult(True, "\n".join(results))
        else:
            return ToolResult(True, f"No matches for '{query}' found.")
    except Exception as e:
        return ToolResult(False, "", str(e))

def investigate_codebase(directory: str) -> ToolResult:
    """Analyze the codebase structure and key files."""
    try:
        structure = []
        for root, dirs, files in os.walk(directory):
            level = root.replace(directory, "").count(os.sep)
            indent = " " * 4 * level
            structure.append(f"{indent}{os.path.basename(root)}/")
            sub_indent = " " * 4 * (level + 1)
            for f in files[:10]: # Limit files shown
                 structure.append(f"{sub_indent}{f}")

        # Read a few important files if they exist
        important_files = ["README.md", "pyproject.toml", "requirements.txt", "package.json"]
        summaries = []
        for f_name in important_files:
             p = os.path.join(directory, f_name)
             if os.path.exists(p):
                  with open(p, "r") as f:
                       summaries.append(f"--- {f_name} ---\n{f.read()[:500]}...")

        output = "Codebase Structure:\n" + "\n".join(structure[:100])
        if summaries:
             output += "\n\nKey File Contents:\n" + "\n".join(summaries)

        return ToolResult(True, output)
    except Exception as e:
        return ToolResult(False, "", str(e))
