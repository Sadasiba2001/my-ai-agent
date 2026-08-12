import json
import ollama
from openai import OpenAI

from utils.formatters import _format_messages_for_openai


# Client Cache for lazy initialization
_CLIENT_CACHE = {}


def _get_client_for_profile(prof: dict):
    """Retrieve or initialize client for a model profile."""
    key = prof["key"]
    if key in _CLIENT_CACHE:
        return _CLIENT_CACHE[key]

    provider = prof["provider"]
    if provider == "nvidia":
        

        client = OpenAI(
            base_url=prof["base_url"],
            api_key=prof["api_key"] or "no-key-provided",
        )
    else:
        client = ollama.Client(host=prof["host"])

    _CLIENT_CACHE[key] = client
    return client


def _execute_completion_with_profile(
    prof: dict, messages: list, tools: list | None = None
):
    """Execute completion attempt on a specific model profile."""
    provider = prof["provider"]
    model_name = prof["model"]
    display_name = prof["display_name"]

    if provider == "nvidia":
        api_key = prof["api_key"]
        if not api_key or api_key == "no-key-provided":
            raise ValueError(
                f"API Key for '{prof['key']}' ({display_name}) is missing in .env!"
            )

        client = _get_client_for_profile(prof)
        formatted_messages = _format_messages_for_openai(messages)

        response = client.chat.completions.create(
            model=model_name,
            messages=formatted_messages,
            tools=tools or None,
            temperature=0.2,
            top_p=0.9,
        )

        choice = response.choices[0]
        msg = choice.message

        tool_calls_normalized = []
        if getattr(msg, "tool_calls", None):
            for tc in msg.tool_calls:
                args = tc.function.arguments
                if isinstance(args, str):
                    try:
                        args = json.loads(args)
                    except Exception:
                        args = {}
                tool_calls_normalized.append(
                    {
                        "id": tc.id,
                        "function": {
                            "name": tc.function.name,
                            "arguments": args,
                        },
                    }
                )

        return {
            "message": {
                "role": "assistant",
                "content": msg.content or "",
                "tool_calls": tool_calls_normalized,
            },
            "profile_used": prof,
        }
    else:
        # Ollama provider with optimized speed options
        client = _get_client_for_profile(prof)
        response = client.chat(
            model=model_name,
            messages=messages,
            tools=tools or [],
            options={
                "temperature": 0.1,  # Low temperature for fast, direct action
                "top_p": 0.9,
            },
        )
        return {
            "message": response["message"],
            "profile_used": prof,
        }
