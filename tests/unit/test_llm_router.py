
import pytest

from my_ai_agent.llm import (
    LLMConnectionError,
    LLMError,
    LLMProvider,
    LLMResult,
    LLMRouter,
    LLMTimeoutError,
    ProviderProfile,
)


class MockProvider(LLMProvider):
    def __init__(
        self,
        profile: ProviderProfile,
        response: LLMResult | None = None,
        raise_exc: Exception | None = None,
    ):
        super().__init__(profile)
        self._response = response or LLMResult(
            content="Mock response",
            provider=profile.provider,
            model=profile.model,
            latency_ms=50.0,
        )
        self._raise_exc = raise_exc

    def chat(self, messages, tools=None):
        if self._raise_exc:
            raise self._raise_exc
        return self._response


def test_router_primary_success():
    prof1 = ProviderProfile(key="ollama", provider="ollama", display_name="Ollama", model="qwen3:8b")
    p1 = MockProvider(
        prof1,
        response=LLMResult(
            content="Hello from Ollama", provider="ollama", model="qwen3:8b", latency_ms=10.0
        ),
    )

    router = LLMRouter(candidate_keys=["ollama"], providers={"ollama": p1})
    res = router.chat([{"role": "user", "content": "Hi"}])

    assert res.content == "Hello from Ollama"
    assert res.provider == "ollama"
    assert res.fallback_used is False
    assert res.latency_ms == 10.0


def test_router_ollama_20s_timeout_fallback_to_minimax():
    prof_ollama = ProviderProfile(
        key="ollama", provider="ollama", display_name="Ollama", model="qwen3:8b", timeout=20.0
    )
    prof_minimax = ProviderProfile(
        key="minimax", provider="nvidia", display_name="MiniMax M3", model="minimax-m3"
    )

    p_ollama = MockProvider(prof_ollama, raise_exc=LLMTimeoutError("Ollama timed out after 20s"))
    p_minimax = MockProvider(
        prof_minimax,
        response=LLMResult(
            content="Fallback response", provider="nvidia", model="minimax-m3", latency_ms=120.0
        ),
    )

    router = LLMRouter(
        candidate_keys=["ollama", "minimax"],
        providers={"ollama": p_ollama, "minimax": p_minimax},
        enable_fallback=True,
    )

    res = router.chat([{"role": "user", "content": "Hi"}])

    assert res.content == "Fallback response"
    assert res.provider == "nvidia"
    assert res.fallback_used is True


def test_router_connection_error_fallback():
    prof1 = ProviderProfile(key="ollama", provider="ollama", display_name="Ollama", model="qwen3:8b")
    prof2 = ProviderProfile(key="glm", provider="nvidia", display_name="GLM-5.2", model="glm-5.2")

    p1 = MockProvider(prof1, raise_exc=LLMConnectionError("Failed to connect"))
    p2 = MockProvider(
        prof2,
        response=LLMResult(
            content="GLM response", provider="nvidia", model="glm-5.2", latency_ms=45.0
        ),
    )

    router = LLMRouter(
        candidate_keys=["ollama", "glm"],
        providers={"ollama": p1, "glm": p2},
        enable_fallback=True,
    )

    res = router.chat([{"role": "user", "content": "Test"}])
    assert res.content == "GLM response"
    assert res.fallback_used is True


def test_router_all_providers_fail():
    prof1 = ProviderProfile(key="ollama", provider="ollama", display_name="Ollama", model="qwen3:8b")
    prof2 = ProviderProfile(key="minimax", provider="nvidia", display_name="MiniMax", model="minimax-m3")

    p1 = MockProvider(prof1, raise_exc=LLMTimeoutError("Timeout"))
    p2 = MockProvider(prof2, raise_exc=LLMConnectionError("Connection ref"))

    router = LLMRouter(
        candidate_keys=["ollama", "minimax"],
        providers={"ollama": p1, "minimax": p2},
        enable_fallback=True,
    )

    with pytest.raises(LLMError, match="All candidate models"):
        router.chat([{"role": "user", "content": "Test"}])
