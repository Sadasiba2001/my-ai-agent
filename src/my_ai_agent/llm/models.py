from dataclasses import dataclass, field
from typing import Any


@dataclass
class LLMMessage:
    role: str
    content: str | None = None
    tool_calls: list[dict[str, Any]] | None = None
    tool_call_id: str | None = None


@dataclass
class LLMResult:
    content: str
    provider: str
    model: str
    latency_ms: float
    completed: bool = True
    fallback_used: bool = False
    tool_calls: list[dict[str, Any]] = field(default_factory=list)
    raw_message: dict[str, Any] = field(default_factory=dict)


@dataclass
class ProviderProfile:
    key: str
    provider: str
    display_name: str
    model: str
    host: str | None = None
    base_url: str | None = None
    api_key: str | None = None
    timeout: float = 20.0
