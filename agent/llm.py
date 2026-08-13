"""LLM facade module re-exporting config, formatters, providers, and router functions for 100% backward compatibility."""

from config import (
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
from llm.providers import (
    _CLIENT_CACHE,
    _execute_completion_with_profile,
    _get_client_for_profile,
)
from llm.router import ask_llm, chat_with_llm
from utils.formatters import _format_messages_for_openai

__all__ = [
    "ACTIVE_MODEL_KEY",
    "ACTIVE_MODEL_NAME",
    "CANDIDATE_KEYS",
    "DISPLAY_NAME",
    "ENABLE_AUTO_FALLBACK",
    "FALLBACK_KEYS",
    "MODEL_PROFILES",
    "NVIDIA_API_KEY_DEFAULT",
    "PRIMARY_MODEL_KEY",
    "PROVIDER_TYPE",
    "_CLIENT_CACHE",
    "_execute_completion_with_profile",
    "_format_messages_for_openai",
    "_get_client_for_profile",
    "ask_llm",
    "chat_with_llm",
    "profile",
]
