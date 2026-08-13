from dataclasses import dataclass, field
from typing import Any


@dataclass
class AgentState:
    task: str = ""
    iteration: int = 0
    tool_calls: int = 0
    completed: bool = False
    history: list[dict[str, Any]] = field(default_factory=list)

    def reset(self, task: str) -> None:
        self.task = task
        self.iteration = 0
        self.tool_calls = 0
        self.completed = False
        self.history.clear()
