from my_ai_agent.config import CANDIDATE_KEYS, MODEL_PROFILES, Settings


def test_default_settings():
    s = Settings()
    assert isinstance(s.primary_model_key, str)
    assert isinstance(s.enable_auto_fallback, bool)
    assert isinstance(s.agent_max_iterations, int)


def test_environment_override(monkeypatch):
    monkeypatch.setenv("ACTIVE_MODEL", "ollama")
    monkeypatch.setenv("ENABLE_AUTO_FALLBACK", "false")
    monkeypatch.setenv("AGENT_MAX_ITERATIONS", "5")

    s = Settings()
    assert s.primary_model_key == "ollama"
    assert s.enable_auto_fallback is False
    assert s.agent_max_iterations == 5


def test_model_profiles_structure():
    assert "ollama" in MODEL_PROFILES
    assert "minimax" in MODEL_PROFILES
    assert "glm" in MODEL_PROFILES

    ollama_prof = MODEL_PROFILES["ollama"]
    assert ollama_prof["provider"] == "ollama"
    assert float(ollama_prof["timeout"]) == 20.0


def test_candidate_keys_sequence():
    assert len(CANDIDATE_KEYS) > 0
    assert "ollama" in CANDIDATE_KEYS or "minimax" in CANDIDATE_KEYS
