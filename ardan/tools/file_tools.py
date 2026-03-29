import os
import glob
from dataclasses import dataclass


@dataclass
class ToolResult:
    success: bool
    output: str
    error: str = ""


def _ensure_safe_path(path: str) -> str:
    """Ensure the path is within the workspace and prevent traversal."""
    if os.path.isabs(path) or ".." in path:
        raise ValueError(f"Access denied: {path} is outside the allowed workspace.")
    return path


def read_file(path: str) -> ToolResult:
    try:
        path = _ensure_safe_path(path)
        with open(path, "r", encoding="utf-8") as f:
            return ToolResult(True, f.read())
    except Exception as e:
        return ToolResult(False, "", str(e))


def write_file(path: str, content: str) -> ToolResult:
    try:
        path = _ensure_safe_path(path)
        dirname = os.path.dirname(path)
        if dirname:
            os.makedirs(dirname, exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
        return ToolResult(True, f"File written successfully to {path}")
    except Exception as e:
        return ToolResult(False, "", str(e))


def append_file(path: str, content: str) -> ToolResult:
    try:
        path = _ensure_safe_path(path)
        with open(path, "a", encoding="utf-8") as f:
            f.write(content)
        return ToolResult(True, f"Content appended to {path}")
    except Exception as e:
        return ToolResult(False, "", str(e))


def list_files(directory: str, pattern: str = "*") -> ToolResult:
    try:
        directory = _ensure_safe_path(directory)
        files = glob.glob(os.path.join(directory, pattern), recursive=True)
        # Simple tree view logic
        if not files:
            return ToolResult(True, "No files found.")

        output = []
        for file in sorted(files):
            output.append(file)
        return ToolResult(True, "\n".join(output))
    except Exception as e:
        return ToolResult(False, "", str(e))


def delete_file(path: str) -> ToolResult:
    try:
        path = _ensure_safe_path(path)
        if os.path.exists(path):
            os.remove(path)
            return ToolResult(True, f"File {path} deleted.")
        else:
            return ToolResult(False, "", f"File {path} does not exist.")
    except Exception as e:
        return ToolResult(False, "", str(e))


def search_and_replace(path: str, old: str, new: str) -> ToolResult:
    try:
        path = _ensure_safe_path(path)
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()

        if old not in content:
            return ToolResult(False, "", f"'{old}' not found in {path}")

        new_content = content.replace(old, new)
        with open(path, "w", encoding="utf-8") as f:
            f.write(new_content)
        return ToolResult(True, f"Successfully replaced '{old}' with '{new}' in {path}")
    except Exception as e:
        return ToolResult(False, "", str(e))
