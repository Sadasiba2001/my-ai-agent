from typing import Any

from my_ai_agent.tools.base import Tool, ToolResult
from my_ai_agent.tools.filesystem import ListFilesTool, ReadFileTool, WriteFileTool
from my_ai_agent.tools.python import RunPythonTool


class ToolRegistry:
    def __init__(self):
        self._tools: dict[str, Tool] = {}
        self.register(ListFilesTool())
        self.register(ReadFileTool())
        self.register(WriteFileTool())
        self.register(RunPythonTool())

    def register(self, tool: Tool) -> None:
        if tool.name in self._tools:
            raise ValueError(f"Tool with name '{tool.name}' is already registered.")
        self._tools[tool.name] = tool

    def get_tool(self, name: str) -> Tool | None:
        return self._tools.get(name)

    def execute(self, tool_name: str, arguments: dict[str, Any]) -> ToolResult:
        tool = self.get_tool(tool_name)
        if not tool:
            return ToolResult(
                success=False,
                tool_name=tool_name,
                error={"type": "KeyError", "message": f"Unknown tool: '{tool_name}'"},
            )
        try:
            return tool.execute(arguments)
        except (TypeError, ValueError, KeyError, RuntimeError, OSError) as e:
            return ToolResult(
                success=False,
                tool_name=tool_name,
                error={"type": type(e).__name__, "message": str(e)},
            )

    def get_schemas(self) -> list[dict[str, Any]]:
        return [tool.to_schema() for tool in self._tools.values()]


default_registry = ToolRegistry()
TOOL_FUNCTIONS = default_registry._tools
TOOLS = default_registry.get_schemas()


def execute_tool(tool_name: str, arguments: dict) -> str:
    res = default_registry.execute(tool_name, arguments)
    return str(res)
