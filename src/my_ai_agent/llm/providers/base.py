from abc import ABC, abstractmethod
from typing import Any

from my_ai_agent.llm.models import LLMResult, ProviderProfile


class LLMProvider(ABC):
    def __init__(self, profile: ProviderProfile):
        self.profile = profile

    @abstractmethod
    def chat(
        self, messages: list[dict[str, Any]], tools: list[dict[str, Any]] | None = None
    ) -> LLMResult:
        """Send chat messages to the LLM provider and return LLMResult."""
