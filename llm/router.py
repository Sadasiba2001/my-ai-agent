import json
import time

from config import (
    ACTIVE_MODEL_NAME,
    CANDIDATE_KEYS,
    DISPLAY_NAME,
    ENABLE_AUTO_FALLBACK,
    MODEL_PROFILES,
    profile,
)
from llm.providers import _execute_completion_with_profile
from tools import TOOLS, execute_tool


def chat_with_llm(messages: list, tools: list | None = None):
    """Send chat request with dynamic automatic model router fallback (minimax -> glm -> ollama)."""
    candidates = list(CANDIDATE_KEYS)
    last_exception = None

    for idx, key in enumerate(candidates):
        prof = MODEL_PROFILES[key]
        display_name = prof["display_name"]

        try:
            if idx > 0:
                print(
                    f"\n[Router Switch] Switching to fallback model: {display_name} ({prof['model']})..."
                )

            res = _execute_completion_with_profile(prof, messages, tools)
            return res

        except Exception as e:
            last_exception = e
            is_rate_limit = False
            status_code = getattr(e, "status_code", None)

            try:
                from openai import RateLimitError

                if isinstance(e, RateLimitError) or status_code == 429:
                    is_rate_limit = True
            except ImportError:
                pass

            error_type = "Rate limit (429)" if is_rate_limit else "Error / Missing Key"
            print(
                f"[Router Notice] '{display_name}' ({prof['model']}) encountered {error_type}."
            )

            if not ENABLE_AUTO_FALLBACK:
                raise e

            if idx < len(candidates) - 1:
                next_key = candidates[idx + 1]
                next_prof = MODEL_PROFILES[next_key]
                print(
                    f"[Router Failover] Automatically falling back to '{next_prof['display_name']}'..."
                )
                time.sleep(1)
            else:
                print(
                    f"[Router Error] All candidate models ({candidates}) in fallback order failed."
                )
                raise last_exception


def ask_llm(prompt: str) -> str:
    """Agent loop: handles system prompt, LLM reasoning, and tool execution."""
    print(f"\n[Agent] Primary Model: {DISPLAY_NAME} ({ACTIVE_MODEL_NAME})")
    print(f"[Agent] Router Fallback Chain: {' -> '.join(CANDIDATE_KEYS)}")
    print("[Agent] Thinking...")

    messages = [
        {
            "role": "system",
            "content": (
                "You are an AI agent running on the user's computer.\n\n"
                "You have tools for working with files and Python.\n\n"
                "Available capabilities:\n"
                "- list_files: inspect directories\n"
                "- read_file: read text files\n"
                "- write_file: create or modify files inside workspace/\n"
                "- run_python: execute Python scripts inside workspace/\n\n"
                "Use tools whenever they are needed to complete "
                "the user's request.\n\n"
                "After creating or modifying Python code, "
                "you can use run_python to test it.\n\n"
                "Continue using tools until the task is complete."
            ),
        },
        {
            "role": "user",
            "content": prompt,
        },
    ]

    while True:
        response = chat_with_llm(messages=messages, tools=TOOLS)
        message = response["message"]
        used_profile = response.get("profile_used", profile)
        used_provider = used_profile["provider"]

        # --------------------------------
        # No tool required
        # --------------------------------
        if not message.get("tool_calls"):
            print("[Agent] Final response received.")
            return message["content"]

        # --------------------------------
        # Tool requested
        # --------------------------------
        print(f"[Agent] {used_profile['display_name']} wants to use tool(s).")

        assistant_msg = {
            "role": "assistant",
            "content": message.get("content", ""),
        }

        if message.get("tool_calls"):
            if used_provider == "nvidia":
                assistant_msg["tool_calls"] = [
                    {
                        "id": tc.get("id") or f"call_{i}",
                        "type": "function",
                        "function": {
                            "name": tc["function"]["name"],
                            "arguments": json.dumps(tc["function"]["arguments"])
                            if isinstance(tc["function"]["arguments"], (dict, list))
                            else tc["function"]["arguments"],
                        },
                    }
                    for i, tc in enumerate(message["tool_calls"])
                ]
            else:
                assistant_msg["tool_calls"] = message["tool_calls"]

        messages.append(assistant_msg)

        for i, tool_call in enumerate(message["tool_calls"]):
            tool_name = tool_call["function"]["name"]
            arguments = tool_call["function"]["arguments"]

            print(f"[Tool] Executing: {tool_name}")
            print(f"[Tool] Arguments: {arguments}")

            result = execute_tool(tool_name, arguments)

            print("[Tool] Result:")
            print(result)

            tool_call_id = tool_call.get("id") or f"call_{i}"

            messages.append(
                {
                    "role": "tool",
                    "tool_call_id": tool_call_id,
                    "content": str(result),
                }
            )

        print("\n[Agent] Continuing...")
