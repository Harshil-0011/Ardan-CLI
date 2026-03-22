import os
from .file_tools import ToolResult

def generate_ascii_diagram(directory: str) -> ToolResult:
    """Analyze the directory and generate a simple ASCII architecture diagram."""
    try:
        # Simple analysis of top-level directories
        structure = os.listdir(directory)
        dirs = [d for d in structure if os.path.isdir(os.path.join(directory, d))]
        files = [f for f in structure if os.path.isfile(os.path.join(directory, f))]

        diagram = "Architecture Diagram:\n"
        diagram += "+-------------------+\n"
        diagram += "|    User Request   |\n"
        diagram += "+---------+---------+\n"
        diagram += "          |\n"
        diagram += "          v\n"
        diagram += "+---------+---------+\n"
        diagram += "|   Ardan Agent     |\n"
        diagram += "+---------+---------+\n"
        diagram += "          |\n"
        diagram += "          v\n"

        for d in dirs[:5]:
             diagram += f"+------- {d}/ -------+\n"

        for f in files[:5]:
             diagram += f"| {f}\n"

        return ToolResult(True, diagram)
    except Exception as e:
        return ToolResult(False, "", str(e))
