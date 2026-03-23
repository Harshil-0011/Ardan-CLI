import subprocess
import os
from .file_tools import ToolResult


def docker_build(tag: str, cwd: str = ".") -> ToolResult:
    try:
        subprocess.run(
            ["docker", "build", "-t", tag, "."],
            cwd=cwd,
            check=True,
            capture_output=True,
        )
        return ToolResult(True, f"Built docker image: {tag}", "")
    except Exception as e:
        return ToolResult(False, "", str(e))


def docker_run(tag: str) -> ToolResult:
    try:
        subprocess.run(["docker", "run", "-d", tag], check=True, capture_output=True)
        return ToolResult(True, f"Started docker container: {tag}", "")
    except Exception as e:
        return ToolResult(False, "", str(e))


def generate_dockerfile(project_path: str) -> ToolResult:
    """Analyzes project and writes an optimal Dockerfile."""
    try:
        content = 'FROM python:3.11-slim\nWORKDIR /app\nCOPY requirements.txt .\nRUN pip install -r requirements.txt\nCOPY . .\nCMD ["python", "main.py"]'
        with open(os.path.join(project_path, "Dockerfile"), "w") as f:
            f.write(content)
        return ToolResult(True, "Dockerfile generated.", "")
    except Exception as e:
        return ToolResult(False, "", str(e))


def generate_compose(project_path: str) -> ToolResult:
    """Writes docker-compose.yml."""
    try:
        content = "version: '3.8'\nservices:\n  app:\n    build: .\n    ports:\n      - '8080:80'"
        with open(os.path.join(project_path, "docker-compose.yml"), "w") as f:
            f.write(content)
        return ToolResult(True, "docker-compose.yml generated.", "")
    except Exception as e:
        return ToolResult(False, "", str(e))
