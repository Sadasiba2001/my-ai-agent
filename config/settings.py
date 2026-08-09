import os
from dotenv import load_dotenv

load_dotenv()

# Active Primary Model Choice: 'ollama' | 'minimax' | 'glm' | 'laguna'
PRIMARY_MODEL_KEY = os.getenv("ACTIVE_MODEL", "minimax").lower().strip()

# Fallback Settings
ENABLE_AUTO_FALLBACK = os.getenv("ENABLE_AUTO_FALLBACK", "true").lower().strip() in (
    "true",
    "1",
    "yes",
)

raw_fallback_order = os.getenv("FALLBACK_ORDER", "minimax,glm,ollama")
FALLBACK_KEYS = [k.strip().lower() for k in raw_fallback_order.split(",") if k.strip()]

# Shared fallback NVIDIA API key
NVIDIA_API_KEY_DEFAULT = os.getenv("NVIDIA_API_KEY", "").strip()

# Configured Model Profiles
MODEL_PROFILES = {
    "ollama": {
        "key": "ollama",
        "provider": "ollama",
        "display_name": "Ollama (Local)",
        "model": os.getenv("OLLAMA_MODEL") or "",
        "host": os.getenv("OLLAMA_HOST") or "",
    },
    "minimax": {
        "key": "minimax",
        "provider": "nvidia",
        "display_name": "NVIDIA MiniMax M3",
        "model": os.getenv("MINIMAX_MODEL") or "",
        "base_url": os.getenv("MINIMAX_BASE_URL") or "",
        "api_key": os.getenv("MINIMAX_API_KEY", "").strip() or NVIDIA_API_KEY_DEFAULT,
    },
    "glm": {
        "key": "glm",
        "provider": "nvidia",
        "display_name": "NVIDIA GLM-5.2",
        "model": os.getenv("GLM_MODEL") or "",
        "base_url": os.getenv("GLM_BASE_URL") or "",
        "api_key": os.getenv("GLM_API_KEY", "").strip() or NVIDIA_API_KEY_DEFAULT,
    },
    "laguna": {
        "key": "laguna",
        "provider": "nvidia",
        "display_name": "NVIDIA Laguna",
        "model": os.getenv("LAGUNA_MODEL") or "",
        "base_url": os.getenv("LAGUNA_BASE_URL") or "",
        "api_key": os.getenv("LAGUNA_API_KEY", "").strip() or NVIDIA_API_KEY_DEFAULT,
    },
}

# Determine candidate router sequence
CANDIDATE_KEYS = []
if PRIMARY_MODEL_KEY in MODEL_PROFILES:
    CANDIDATE_KEYS.append(PRIMARY_MODEL_KEY)

if ENABLE_AUTO_FALLBACK:
    for key in FALLBACK_KEYS:
        if key in MODEL_PROFILES and key not in CANDIDATE_KEYS:
            CANDIDATE_KEYS.append(key)
    for key in MODEL_PROFILES:
        if key not in CANDIDATE_KEYS:
            CANDIDATE_KEYS.append(key)

# Legacy / default profile selection
ACTIVE_MODEL_KEY = CANDIDATE_KEYS[0] if CANDIDATE_KEYS else "ollama"
profile = MODEL_PROFILES.get(ACTIVE_MODEL_KEY, MODEL_PROFILES["ollama"])
PROVIDER_TYPE = profile["provider"]
ACTIVE_MODEL_NAME = profile["model"]
DISPLAY_NAME = profile["display_name"]
