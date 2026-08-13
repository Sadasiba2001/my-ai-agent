from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, ClassVar


@dataclass
class ToolResult:
    success: bool
    tool_name: str
    result: Any = None
    error: dict[str, str] | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "success": self.success,
            "tool": self.tool_name,
            "result": self.result,
            "error": self.error,
        }

    def __str__(self) -> str:
        if self.success:
            return str(self.result)
        err_msg = self.error.get("message", "Unknown error") if self.error else "Error"
        return f"Tool '{self.tool_name}' failed: {err_msg}"


class Tool(ABC):
    name: str
    description: str
    parameters: ClassVar[dict[str, Any]]

    @abstractmethod
    def execute(self, arguments: dict[str, Any]) -> ToolResult:
        """Execute tool logic with supplied arguments."""

    def to_schema(self) -> dict[str, Any]:
        """Return OpenAI function definition schema."""
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": self.parameters,
            },
        }
