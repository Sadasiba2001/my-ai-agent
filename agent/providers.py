"""Backward compatibility facade for agent.providers re-exporting llm package."""

from llm.providers import (
    _CLIENT_CACHE,
    _execute_completion_with_profile,
    _get_client_for_profile,
)

__all__ = [
    "_CLIENT_CACHE",
    "_get_client_for_profile",
    "_execute_completion_with_profile",
]
