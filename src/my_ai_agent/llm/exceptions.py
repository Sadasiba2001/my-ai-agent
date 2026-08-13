"""LLM Subsystem Exceptions."""


class LLMError(Exception):
    """Base exception for all LLM errors."""


class LLMTimeoutError(LLMError):
    """Raised when an LLM provider call times out (e.g. 20-second Ollama limit)."""


class LLMConnectionError(LLMError):
    """Raised when connection to LLM host/endpoint fails."""


class LLMAuthenticationError(LLMError):
    """Raised when API key or auth token is invalid or missing."""


class LLMRateLimitError(LLMError):
    """Raised when provider returns HTTP 429 rate limit error."""


class LLMProviderUnavailableError(LLMError):
    """Raised when provider service is down or returns server error."""
