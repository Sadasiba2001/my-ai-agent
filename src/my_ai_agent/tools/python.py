import subprocess
import sys
from pathlib import Path
from typing import Any, ClassVar

from my_ai_agent.tools.base import Tool, ToolResult

WORKSPACE = Path("workspace").resolve()
MAX_OUTPUT_BYTES = 100 * 1024


class RunPythonTool(Tool):
    name = "run_python"
    description = (
        "Execute a Python script inside the workspace and return its output and errors. "
        "Use this tool when you need to test or execute a Python program."
    )
    parameters: ClassVar[dict[str, Any]] = {
        "type": "object",
        "properties": {
            "path": {
                "type": "string",
                "description": "Path of the Python script relative to workspace.",
            }
        },
        "required": ["path"],
    }

    def execute(self, arguments: dict[str, Any]) -> ToolResult:
        path_str = arguments.get("path", "")
        if not path_str:
            return ToolResult(
                success=False,
                tool_name=self.name,
                error={"type": "ValueError", "message": "Missing 'path' argument."},
            )

        path_str = path_str.removeprefix("workspace/").removeprefix("workspace\\")

        WORKSPACE.mkdir(parents=True, exist_ok=True)
        script = (WORKSPACE / path_str).resolve()

        if WORKSPACE not in script.parents:
            return ToolResult(
                success=False,
                tool_name=self.name,
                error={
                    "type": "PermissionError",
                    "message": "Permission denied. Python scripts can only be executed inside workspace/.",
                },
            )

        if not script.exists():
            return ToolResult(
                success=False,
                tool_name=self.name,
                error={"type": "FileNotFoundError", "message": f"Python file does not exist: {path_str}"},
            )

        if not script.is_file():
            return ToolResult(
                success=False,
                tool_name=self.name,
                error={"type": "IsADirectoryError", "message": f"Path is not a file: {path_str}"},
            )

        if script.suffix.lower() != ".py":
            return ToolResult(
                success=False,
                tool_name=self.name,
                error={"type": "ValueError", "message": "Only .py files can be executed."},
            )

        try:
            result = subprocess.run(
                [sys.executable, str(script)],
                cwd=WORKSPACE,
                capture_output=True,
                text=True,
                timeout=30,
                check=False,
            )

            stdout = result.stdout[:MAX_OUTPUT_BYTES] if result.stdout else ""
            stderr = result.stderr[:MAX_OUTPUT_BYTES] if result.stderr else ""

            output_lines = []
            if stdout:
                output_lines.append(f"STDOUT:\n{stdout}")
            if stderr:
                output_lines.append(f"STDERR:\n{stderr}")
            output_lines.append(f"EXIT CODE: {result.returncode}")

            res_str = "\n".join(output_lines)
            is_success = result.returncode == 0

            return ToolResult(
                success=is_success,
                tool_name=self.name,
                result=res_str,
                error=None if is_success else {"type": "ExecutionError", "message": stderr or "Non-zero exit code"},
            )

        except subprocess.TimeoutExpired:
            return ToolResult(
                success=False,
                tool_name=self.name,
                error={"type": "TimeoutError", "message": "Execution timed out after 30 seconds."},
            )
        except OSError as e:
            return ToolResult(
                success=False,
                tool_name=self.name,
                error={"type": type(e).__name__, "message": str(e)},
            )


def run_python(path: str) -> str:
    return str(RunPythonTool().execute({"path": path}))
