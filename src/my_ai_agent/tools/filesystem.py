from pathlib import Path
from typing import Any, ClassVar

from my_ai_agent.tools.base import Tool, ToolResult

WORKSPACE = Path("workspace").resolve()

IGNORED_DIRECTORIES = {
    ".venv",
    "venv",
    "__pycache__",
    ".git",
    "node_modules",
    ".env",
    ".env.example",
    ".gitignore",
}


class ListFilesTool(Tool):
    name = "list_files"
    description = (
        "List files and directories. Use this tool whenever the user asks "
        "about files, folders, directories, or project contents."
    )
    parameters: ClassVar[dict[str, Any]] = {
        "type": "object",
        "properties": {
            "path": {
                "type": "string",
                "description": "Directory path to inspect. Use '.' for the current directory.",
            }
        },
        "required": ["path"],
    }

    def execute(self, arguments: dict[str, Any]) -> ToolResult:
        path_str = arguments.get("path", ".")
        target = Path(path_str).resolve()

        if not target.exists():
            return ToolResult(
                success=False,
                tool_name=self.name,
                error={"type": "FileNotFoundError", "message": f"Path does not exist: {path_str}"},
            )

        if not target.is_dir():
            return ToolResult(
                success=False,
                tool_name=self.name,
                error={"type": "NotADirectoryError", "message": f"Path is not a directory: {path_str}"},
            )

        items = []
        for item in target.rglob("*"):
            if any(ignored in item.parts for ignored in IGNORED_DIRECTORIES):
                continue
            relative = item.relative_to(target)
            if item.is_dir():
                items.append(f"[DIR]  {relative}")
            else:
                items.append(f"[FILE] {relative}")

        res_text = "\n".join(sorted(items)) if items else "Directory is empty."
        return ToolResult(success=True, tool_name=self.name, result=res_text)


class ReadFileTool(Tool):
    name = "read_file"
    description = (
        "Read the contents of a text file. Use this tool when the user asks "
        "to read, inspect, analyze, or explain a file."
    )
    parameters: ClassVar[dict[str, Any]] = {
        "type": "object",
        "properties": {
            "path": {
                "type": "string",
                "description": "Path of the text file to read.",
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

        target = Path(path_str)
        if not target.exists():
            return ToolResult(
                success=False,
                tool_name=self.name,
                error={"type": "FileNotFoundError", "message": f"File does not exist: {path_str}"},
            )

        if not target.is_file():
            return ToolResult(
                success=False,
                tool_name=self.name,
                error={"type": "IsADirectoryError", "message": f"Path is not a file: {path_str}"},
            )

        try:
            content = target.read_text(encoding="utf-8")
            return ToolResult(success=True, tool_name=self.name, result=content)
        except UnicodeDecodeError:
            return ToolResult(
                success=False,
                tool_name=self.name,
                error={"type": "UnicodeDecodeError", "message": f"Cannot read binary file: {path_str}"},
            )
        except OSError as e:
            return ToolResult(
                success=False,
                tool_name=self.name,
                error={"type": type(e).__name__, "message": str(e)},
            )


class WriteFileTool(Tool):
    name = "write_file"
    description = (
        "Create or overwrite a text file inside the workspace directory. "
        "Use this when the user asks you to create or write a file."
    )
    parameters: ClassVar[dict[str, Any]] = {
        "type": "object",
        "properties": {
            "path": {
                "type": "string",
                "description": "File path relative to workspace.",
            },
            "content": {
                "type": "string",
                "description": "Complete content to write into the file.",
            },
        },
        "required": ["path", "content"],
    }

    def execute(self, arguments: dict[str, Any]) -> ToolResult:
        path_str = arguments.get("path", "")
        content = arguments.get("content", "")

        if not path_str:
            return ToolResult(
                success=False,
                tool_name=self.name,
                error={"type": "ValueError", "message": "Missing 'path' argument."},
            )

        WORKSPACE.mkdir(parents=True, exist_ok=True)
        target = (WORKSPACE / path_str).resolve()

        if WORKSPACE not in target.parents and target != WORKSPACE:
            return ToolResult(
                success=False,
                tool_name=self.name,
                error={
                    "type": "PermissionError",
                    "message": "Permission denied. The agent can only write inside workspace/.",
                },
            )

        try:
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(content, encoding="utf-8")
            return ToolResult(
                success=True,
                tool_name=self.name,
                result=f"File successfully written: {target.name}",
            )
        except OSError as e:
            return ToolResult(
                success=False,
                tool_name=self.name,
                error={"type": type(e).__name__, "message": str(e)},
            )


def list_files(path: str = ".") -> str:
    return str(ListFilesTool().execute({"path": path}))


def read_file(path: str) -> str:
    return str(ReadFileTool().execute({"path": path}))


def write_file(path: str, content: str) -> str:
    return str(WriteFileTool().execute({"path": path, "content": content}))
