import subprocess
import sys
from pathlib import Path


WORKSPACE = Path("workspace").resolve()


def run_python(path: str) -> str:
    """
    Execute a Python script inside workspace/.
    
    The path must be relative to workspace/.
    Example:
        hello.py
        scripts/test.py
    """

    if path.startswith("workspace/"):
        path = path[len("workspace/"):]

    if path.startswith("workspace\\"):
        path = path[len("workspace\\"):]

    script = (WORKSPACE / path).resolve()

    if WORKSPACE not in script.parents:
        return (
            "Permission denied. "
            "Python scripts can only be executed "
            "inside workspace/."
        )

    if not script.exists():
        return f"Python file does not exist: {path}"

    if not script.is_file():
        return f"Path is not a file: {path}"

    if script.suffix.lower() != ".py":
        return "Only .py files can be executed."

    try:

        result = subprocess.run(
            [sys.executable, str(script)],
            cwd=WORKSPACE,
            capture_output=True,
            text=True,
            timeout=30,
        )

        output = []

        if result.stdout:
            output.append(
                f"STDOUT:\n{result.stdout}"
            )

        if result.stderr:
            output.append(
                f"STDERR:\n{result.stderr}"
            )

        output.append(
            f"EXIT CODE: {result.returncode}"
        )

        return "\n".join(output)

    except subprocess.TimeoutExpired:
        return "Execution timed out after 30 seconds."

    except Exception as e:
        return f"Python execution error: {e}"