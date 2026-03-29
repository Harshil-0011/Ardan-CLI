import subprocess
import os
import tempfile
import shlex
from .file_tools import ToolResult


def run_command(command: str, cwd: str = None, timeout: int = 60) -> ToolResult:
    """Execute a system command safely without using shell=True."""
    try:
        # Split the command into a list of arguments safely
        # Note: This prevents common shell injection vectors like ';' or '&&'
        # if the user tries to chain commands in a single argument.
        safe_args = shlex.split(command)

        process = subprocess.Popen(
            safe_args,
            shell=False,
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
    # Note: we pass arguments as separate elements to ensure safety
    return run_command(f"gcc -O3 {shlex.quote(src_path)} -o {shlex.quote(output_path)}")


def compile_cpp(src_path: str, output_path: str = "a.out") -> ToolResult:
    """Compile C++ source code using g++."""
    return run_command(f"g++ -O3 {shlex.quote(src_path)} -o {shlex.quote(output_path)}")


def run_binary(path: str, args: str = "") -> ToolResult:
    """Run a compiled binary."""
    # Ensure the path is prefixed with ./ if not present
    binary_path = path if path.startswith("./") or path.startswith("/") else f"./{path}"
    return run_command(f"{shlex.quote(binary_path)} {args}")
