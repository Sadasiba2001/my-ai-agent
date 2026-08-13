import json
import time
from typing import Any

from openai import (
    APIError,
    APITimeoutError,
    AuthenticationError,
    OpenAI,
    RateLimitError,
)

from my_ai_agent.llm.exceptions import (
    LLMAuthenticationError,
    LLMConnectionError,
    LLMError,
    LLMRateLimitError,
    LLMTimeoutError,
)
from my_ai_agent.llm.models import LLMResult, ProviderProfile
from my_ai_agent.llm.providers.base import LLMProvider
from my_ai_agent.utils.formatters import format_messages_for_openai


class OpenAICompatibleProvider(LLMProvider):
    def __init__(self, profile: ProviderProfile):
        super().__init__(profile)
        if not profile.api_key or profile.api_key == "no-key-provided":
            raise LLMAuthenticationError(
                f"API Key for profile '{profile.key}' ({profile.display_name}) is missing!"
            )

        self.client = OpenAI(
            base_url=profile.base_url or "https://api.openai.com/v1",
            api_key=profile.api_key,
            timeout=profile.timeout,
        )

    def chat(
        self, messages: list[dict[str, Any]], tools: list[dict[str, Any]] | None = None
    ) -> LLMResult:
        start_time = time.perf_counter()
        try:
            formatted_messages = format_messages_for_openai(messages)
            response = self.client.chat.completions.create(
                model=self.profile.model,
                messages=formatted_messages,
                tools=tools or None,
                temperature=0.2,
                top_p=0.9,
            )
            elapsed_ms = (time.perf_counter() - start_time) * 1000

            choice = response.choices[0]
            msg = choice.message

            tool_calls_normalized = []
            if getattr(msg, "tool_calls", None):
                for tc in msg.tool_calls:
                    args = tc.function.arguments
                    if isinstance(args, str):
                        try:
                            args = json.loads(args)
                        except (json.JSONDecodeError, TypeError, ValueError):
                            args = {}
                    tool_calls_normalized.append(
                        {
                            "id": tc.id,
                            "type": "function",
                            "function": {
                                "name": tc.function.name,
                                "arguments": args,
                            },
                        }
                    )

            raw_msg_dict = {
                "role": "assistant",
                "content": msg.content or "",
                "tool_calls": tool_calls_normalized,
            }

            return LLMResult(
                content=msg.content or "",
                provider=self.profile.provider,
                model=self.profile.model,
                latency_ms=elapsed_ms,
                completed=True,
                fallback_used=False,
                tool_calls=tool_calls_normalized,
                raw_message=raw_msg_dict,
            )

        except APITimeoutError as e:
            raise LLMTimeoutError(f"Timeout calling {self.profile.display_name}: {e}") from e
        except RateLimitError as e:
            raise LLMRateLimitError(f"Rate limit exceeded on {self.profile.display_name}: {e}") from e
        except AuthenticationError as e:
            raise LLMAuthenticationError(f"Authentication failed on {self.profile.display_name}: {e}") from e
        except APIError as e:
            raise LLMError(f"API Error from {self.profile.display_name}: {e}") from e
        except Exception as e:
            raise LLMConnectionError(f"Connection error with {self.profile.display_name}: {e}") from e
