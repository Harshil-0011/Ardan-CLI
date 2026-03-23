import subprocess
import os
import tempfile
from .file_tools import ToolResult


def run_command(command: str, cwd: str = None, timeout: int = 60) -> ToolResult:
    try:
        process = subprocess.Popen(
            command,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            cwd=cwd,
        )
        stdout, stderr = process.communicate(timeout=timeout)
        if process.returncode == 0:
            return ToolResult(True, stdout)
        else:
            return ToolResult(
                False,
                stdout,
                stderr or f"Process exited with code {process.returncode}",
            )
    except subprocess.TimeoutExpired:
        return ToolResult(False, "", "Command timed out.")
    except Exception as e:
        return ToolResult(False, "", str(e))


def run_script(script_content: str, language: str = "bash") -> ToolResult:
    try:
        suffix = ".sh" if language == "bash" else f".{language}"
        with tempfile.NamedTemporaryFile(
            mode="w", delete=False, suffix=suffix
        ) as tmp_file:
            tmp_file.write(script_content)
            tmp_file_path = tmp_file.name

        os.chmod(tmp_file_path, 0o755)

        if language == "bash":
            command = f"bash {tmp_file_path}"
        elif language == "python":
            command = f"python3 {tmp_file_path}"
        else:
            command = f"{language} {tmp_file_path}"

        result = run_command(command)

        if os.path.exists(tmp_file_path):
            os.remove(tmp_file_path)

        return result
    except Exception as e:
        return ToolResult(False, "", str(e))


def compile_c(src_path: str, output_path: str = "a.out") -> ToolResult:
    """Compile C source code using gcc."""
    return run_command(f"gcc -O3 {src_path} -o {output_path}")


def compile_cpp(src_path: str, output_path: str = "a.out") -> ToolResult:
    """Compile C++ source code using g++."""
    return run_command(f"g++ -O3 {src_path} -o {output_path}")


def run_binary(path: str, args: str = "") -> ToolResult:
    """Run a compiled binary."""
    return run_command(f"./{path} {args}")
