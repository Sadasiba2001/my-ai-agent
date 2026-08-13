"""Backward compatibility facade for agent.config re-exporting config package."""

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
    "profile",
]
