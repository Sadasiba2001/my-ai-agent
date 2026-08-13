import os
from dataclasses import dataclass, field

from dotenv import load_dotenv

load_dotenv()


@dataclass(frozen=True)
class ModelProfile:
    key: str
    provider: str
    display_name: str
    model: str
    host: str | None = None
    base_url: str | None = None
    api_key: str | None = None
    timeout: float = 20.0


@dataclass(frozen=True)
class Settings:
    primary_model_key: str = field(
        default_factory=lambda: os.getenv("ACTIVE_MODEL", "minimax").lower().strip()
    )
    enable_auto_fallback: bool = field(
        default_factory=lambda: os.getenv("ENABLE_AUTO_FALLBACK", "true").lower().strip() in ("true", "1", "yes")
    )
    fallback_order: str = field(
        default_factory=lambda: os.getenv("FALLBACK_ORDER", "minimax,glm,ollama")
    )
    nvidia_api_key_default: str = field(
        default_factory=lambda: os.getenv("NVIDIA_API_KEY", "").strip()
    )
    agent_name: str = field(
        default_factory=lambda: os.getenv("AGENT_NAME", "MyAI-Agent")
    )
    agent_max_iterations: int = field(
        default_factory=lambda: int(os.getenv("AGENT_MAX_ITERATIONS", "10"))
    )
    agent_workspace: str = field(
        default_factory=lambda: os.getenv("AGENT_WORKSPACE", "workspace")
    )
    log_level: str = field(
        default_factory=lambda: os.getenv("LOG_LEVEL", "INFO")
    )


# Load default settings instance
settings = Settings()

PRIMARY_MODEL_KEY = settings.primary_model_key
ENABLE_AUTO_FALLBACK = settings.enable_auto_fallback
FALLBACK_KEYS = [k.strip().lower() for k in settings.fallback_order.split(",") if k.strip()]
NVIDIA_API_KEY_DEFAULT = settings.nvidia_api_key_default

MODEL_PROFILES: dict[str, dict[str, str]] = {
    "ollama": {
        "key": "ollama",
        "provider": "ollama",
        "display_name": "Ollama (Local)",
        "model": os.getenv("OLLAMA_MODEL") or "qwen3:8b",
        "host": os.getenv("OLLAMA_HOST") or "http://localhost:11434",
        "timeout": "20.0",
    },
    "minimax": {
        "key": "minimax",
        "provider": "nvidia",
        "display_name": "NVIDIA MiniMax M3",
        "model": os.getenv("MINIMAX_MODEL") or "minimaxai/minimax-m3",
        "base_url": os.getenv("MINIMAX_BASE_URL") or "https://integrate.api.nvidia.com/v1",
        "api_key": os.getenv("MINIMAX_API_KEY", "").strip() or NVIDIA_API_KEY_DEFAULT,
        "timeout": "30.0",
    },
    "glm": {
        "key": "glm",
        "provider": "nvidia",
        "display_name": "NVIDIA GLM-5.2",
        "model": os.getenv("GLM_MODEL") or "z-ai/glm-5.2",
        "base_url": os.getenv("GLM_BASE_URL") or "https://integrate.api.nvidia.com/v1",
        "api_key": os.getenv("GLM_API_KEY", "").strip() or NVIDIA_API_KEY_DEFAULT,
        "timeout": "30.0",
    },
    "laguna": {
        "key": "laguna",
        "provider": "nvidia",
        "display_name": "NVIDIA Laguna",
        "model": os.getenv("LAGUNA_MODEL") or "",
        "base_url": os.getenv("LAGUNA_BASE_URL") or "https://integrate.api.nvidia.com/v1",
        "api_key": os.getenv("LAGUNA_API_KEY", "").strip() or NVIDIA_API_KEY_DEFAULT,
        "timeout": "30.0",
    },
}

# Determine candidate router sequence
CANDIDATE_KEYS: list[str] = []
if PRIMARY_MODEL_KEY in MODEL_PROFILES:
    CANDIDATE_KEYS.append(PRIMARY_MODEL_KEY)

if ENABLE_AUTO_FALLBACK:
    for key in FALLBACK_KEYS:
        if key in MODEL_PROFILES and key not in CANDIDATE_KEYS:
            CANDIDATE_KEYS.append(key)
    for key in MODEL_PROFILES:
        if key not in CANDIDATE_KEYS:
            CANDIDATE_KEYS.append(key)

ACTIVE_MODEL_KEY = CANDIDATE_KEYS[0] if CANDIDATE_KEYS else "ollama"
profile = MODEL_PROFILES.get(ACTIVE_MODEL_KEY, MODEL_PROFILES["ollama"])
PROVIDER_TYPE = profile["provider"]
ACTIVE_MODEL_NAME = profile["model"]
DISPLAY_NAME = profile["display_name"]
