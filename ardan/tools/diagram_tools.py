import os
from .file_tools import ToolResult


def generate_architecture_diagram(project_path: str) -> ToolResult:
    """Produces an ASCII architecture diagram."""
    try:
        # Simple analysis to build a diagram
        structure = os.listdir(project_path)
        diagram = "ARCHITECTURE DIAGRAM\n"
        diagram += "===================\n\n"
        diagram += f"Root: {os.path.basename(project_path)}\n"
        for item in structure:
            if os.path.isdir(os.path.join(project_path, item)) and not item.startswith(
                "."
            ):
                diagram += f"  ├── [{item}/]\n"
                subitems = os.listdir(os.path.join(project_path, item))[:3]
                for si in subitems:
                    diagram += f"  │   └── {si}\n"
            elif os.path.isfile(os.path.join(project_path, item)):
                diagram += f"  ├── {item}\n"

        with open(os.path.join(project_path, "ARCHITECTURE.md"), "w") as f:
            f.write(f"```text\n{diagram}\n```")

        return ToolResult(True, diagram, "")
    except Exception as e:
        return ToolResult(False, "", str(e))
