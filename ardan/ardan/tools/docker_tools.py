import subprocess
import os
from .file_tools import ToolResult

def docker_build(directory: str, tag: str) -> ToolResult:
    try:
        subprocess.run(["docker", "build", "-t", tag, "."], cwd=directory, check=True)
        return ToolResult(True, f"Docker image {tag} built.")
    except Exception as e:
        return ToolResult(False, "", str(e))

def docker_run(tag: str, port_mapping: str = "8080:80") -> ToolResult:
    try:
        subprocess.run(["docker", "run", "-d", "-p", port_mapping, tag], check=True)
        return ToolResult(True, f"Container {tag} running on port {port_mapping}")
    except Exception as e:
        return ToolResult(False, "", str(e))

def generate_dockerfile(directory: str, language: str = "python") -> ToolResult:
    """Generate a boilerplate Dockerfile."""
    docker_content = f"FROM {language}:3.11\nWORKDIR /app\nCOPY . .\nRUN pip install -r requirements.txt\nCMD [\"python\", \"main.py\"]"
    with open(os.path.join(directory, "Dockerfile"), "w") as f:
         f.write(docker_content)
    return ToolResult(True, "Dockerfile generated.")

def generate_docker_compose(directory: str) -> ToolResult:
    """Generate a simple docker-compose.yml file."""
    try:
        compose_content = "version: '3.8'\nservices:\n  app:\n    build: .\n    ports:\n      - '8080:80'"
        with open(os.path.join(directory, "docker-compose.yml"), "w") as f:
             f.write(compose_content)
        return ToolResult(True, "docker-compose.yml generated.")
    except Exception as e:
        return ToolResult(False, "", str(e))
