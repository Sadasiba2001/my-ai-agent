import logging
from typing import Any

from my_ai_agent.config import CANDIDATE_KEYS, ENABLE_AUTO_FALLBACK, MODEL_PROFILES
from my_ai_agent.llm.exceptions import LLMError
from my_ai_agent.llm.models import LLMResult, ProviderProfile
from my_ai_agent.llm.providers.base import LLMProvider
from my_ai_agent.llm.providers.ollama import OllamaProvider
from my_ai_agent.llm.providers.openai_compatible import OpenAICompatibleProvider

logger = logging.getLogger(__name__)


class LLMRouter:
    def __init__(
        self,
        candidate_keys: list[str] | None = None,
        profiles: dict[str, dict[str, Any]] | None = None,
        providers: dict[str, LLMProvider] | None = None,
        enable_fallback: bool = True,
    ):
        self.candidate_keys = candidate_keys or list(CANDIDATE_KEYS)
        self.profiles = profiles or MODEL_PROFILES
        self.enable_fallback = enable_fallback
        self.providers: dict[str, LLMProvider] = providers or {}

    def _get_provider(self, key: str) -> LLMProvider:
        if key in self.providers:
            return self.providers[key]

        prof_dict = self.profiles.get(key)
        if not prof_dict:
            raise KeyError(f"No configuration profile found for key '{key}'")

        prof = ProviderProfile(
            key=prof_dict["key"],
            provider=prof_dict["provider"],
            display_name=prof_dict["display_name"],
            model=prof_dict["model"],
            host=prof_dict.get("host"),
            base_url=prof_dict.get("base_url"),
            api_key=prof_dict.get("api_key"),
            timeout=float(prof_dict.get("timeout", 20.0)),
        )

        if prof.provider == "nvidia" or prof.provider == "openai":
            provider = OpenAICompatibleProvider(prof)
        else:
            provider = OllamaProvider(prof)

        self.providers[key] = provider
        return provider

    def chat(
        self, messages: list[dict[str, Any]], tools: list[dict[str, Any]] | None = None
    ) -> LLMResult:
        last_exception: Exception | None = None

        for idx, key in enumerate(self.candidate_keys):
            try:
                provider = self._get_provider(key)
                is_fallback = idx > 0
                if is_fallback:
                    logger.warning(
                        f"[Router Failover] Attempting fallback model '{provider.profile.display_name}' ({key})..."
                    )

                result = provider.chat(messages, tools=tools)
                result.fallback_used = is_fallback
                return result

            except Exception as e:
                last_exception = e
                prof_dict = self.profiles.get(key, {})
                display_name = prof_dict.get("display_name", key)

                logger.warning(
                    f"[Router Notice] Model '{display_name}' ({key}) failed: {e}"
                )

                if not self.enable_fallback:
                    raise

                if idx == len(self.candidate_keys) - 1:
                    logger.error(
                        f"[Router Error] All candidate models ({self.candidate_keys}) failed: {last_exception}"
                    )
                    raise LLMError(
                        f"All candidate models ({self.candidate_keys}) failed. Last error: {last_exception}"
                    ) from last_exception

        raise LLMError("No LLM candidate keys configured.")


_default_router = LLMRouter(enable_fallback=ENABLE_AUTO_FALLBACK)


def chat_with_llm(messages: list, tools: list | None = None) -> dict:
    """Legacy helper returning a dict for 100% backward compatibility."""
    res = _default_router.chat(messages, tools)
    return {
        "message": res.raw_message or {
            "role": "assistant",
            "content": res.content,
            "tool_calls": res.tool_calls,
        },
        "profile_used": {
            "provider": res.provider,
            "model": res.model,
        },
    }


def ask_llm(prompt: str) -> str:
    """Legacy shortcut asking LLM with single prompt string."""
    res = _default_router.chat([{"role": "user", "content": prompt}])
    return res.content
