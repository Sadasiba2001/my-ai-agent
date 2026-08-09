"""LLM facade module re-exporting config, formatters, providers, and router functions for 100% backward compatibility."""

from agent.config import (
    ACTIVE_MODEL_KEY,
    ACTIVE_MODEL_NAME,
    CANDIDATE_KEYS,
    DISPLAY_NAME,
    ENABLE_AUTO_FALLBACK,
    FALLBACK_KEYS,
    MODEL_PROFILES,
    NVIDIA_API_KEY_DEFAULT,
    PRIMARY_MODEL_KEY,
    PROVIDER_TYPE,
    profile,
)
from agent.formatter import _format_messages_for_openai
from agent.providers import (
    _CLIENT_CACHE,
    _execute_completion_with_profile,
    _get_client_for_profile,
)
from agent.router import ask_llm, chat_with_llm

__all__ = [
    "PRIMARY_MODEL_KEY",
    "ENABLE_AUTO_FALLBACK",
    "FALLBACK_KEYS",
    "NVIDIA_API_KEY_DEFAULT",
    "MODEL_PROFILES",
    "CANDIDATE_KEYS",
    "ACTIVE_MODEL_KEY",
    "profile",
    "PROVIDER_TYPE",
    "ACTIVE_MODEL_NAME",
    "DISPLAY_NAME",
    "_CLIENT_CACHE",
    "_get_client_for_profile",
    "_format_messages_for_openai",
    "_execute_completion_with_profile",
    "chat_with_llm",
    "ask_llm",
]
