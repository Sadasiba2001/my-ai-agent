import time
from typing import Any

import ollama

from my_ai_agent.llm.exceptions import (
    LLMConnectionError,
    LLMError,
    LLMProviderUnavailableError,
    LLMTimeoutError,
)
from my_ai_agent.llm.models import LLMResult, ProviderProfile
from my_ai_agent.llm.providers.base import LLMProvider


class OllamaProvider(LLMProvider):
    def __init__(self, profile: ProviderProfile):
        super().__init__(profile)
        self.host = profile.host or "http://localhost:11434"
        self.timeout = profile.timeout or 20.0
        self.client = ollama.Client(host=self.host, timeout=self.timeout)

    def chat(
        self, messages: list[dict[str, Any]], tools: list[dict[str, Any]] | None = None
    ) -> LLMResult:
        start_time = time.perf_counter()
        try:
            response = self.client.chat(
                model=self.profile.model,
                messages=messages,
                tools=tools or [],
                options={
                    "temperature": 0.1,
                    "top_p": 0.9,
                },
            )
            elapsed_ms = (time.perf_counter() - start_time) * 1000

            msg = response.get("message", {})
            tool_calls = msg.get("tool_calls", [])

            return LLMResult(
                content=msg.get("content", "") or "",
                provider=self.profile.provider,
                model=self.profile.model,
                latency_ms=elapsed_ms,
                completed=True,
                fallback_used=False,
                tool_calls=tool_calls,
                raw_message=msg,
            )

        except (ollama.ResponseError, TimeoutError) as e:
            elapsed_ms = (time.perf_counter() - start_time) * 1000
            err_msg = str(e).lower()
            if "timeout" in err_msg or elapsed_ms >= (self.timeout * 1000):
                raise LLMTimeoutError(
                    f"Ollama call timed out after {self.timeout}s: {e}"
                ) from e
            raise LLMProviderUnavailableError(f"Ollama error: {e}") from e

        except Exception as e:
            err_msg = str(e).lower()
            if "timeout" in err_msg or "timed out" in err_msg:
                raise LLMTimeoutError(
                    f"Ollama call timed out after {self.timeout}s: {e}"
                ) from e
            if "connect" in err_msg or "refused" in err_msg:
                raise LLMConnectionError(
                    f"Failed to connect to Ollama at {self.host}: {e}"
                ) from e
            raise LLMError(f"Ollama unexpected error: {e}") from e
