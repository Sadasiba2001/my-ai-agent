import json
from typing import Any


def format_messages_for_openai(messages: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Format and sanitize messages to strictly conform to OpenAI API spec."""
    formatted: list[dict[str, Any]] = []
    pending_tool_ids: list[str] = []

    for msg in messages:
        role = msg.get("role")
        content = msg.get("content")

        if role == "assistant":
            tool_calls = msg.get("tool_calls")
            if tool_calls:
                formatted_tool_calls: list[dict[str, Any]] = []
                pending_tool_ids = []
                for i, tc in enumerate(tool_calls):
                    tc_id = tc.get("id") or f"call_{len(formatted)}_{i}"
                    pending_tool_ids.append(tc_id)

                    func_obj = tc.get("function", {})
                    func_name = func_obj.get("name", "")
                    func_args = func_obj.get("arguments", {})

                    if isinstance(func_args, (dict, list)):
                        func_args_str = json.dumps(func_args)
                    else:
                        func_args_str = str(func_args)

                    formatted_tool_calls.append(
                        {
                            "id": tc_id,
                            "type": "function",
                            "function": {
                                "name": func_name,
                                "arguments": func_args_str,
                            },
                        }
                    )

                formatted.append(
                    {
                        "role": "assistant",
                        "content": content or None,
                        "tool_calls": formatted_tool_calls,
                    }
                )
            else:
                formatted.append(
                    {
                        "role": "assistant",
                        "content": content or "",
                    }
                )

        elif role == "tool":
            tool_call_id = msg.get("tool_call_id")
            if not tool_call_id:
                if pending_tool_ids:
                    tool_call_id = pending_tool_ids.pop(0)
                else:
                    tool_call_id = "call_default"
            elif tool_call_id in pending_tool_ids:
                pending_tool_ids.remove(tool_call_id)

            formatted.append(
                {
                    "role": "tool",
                    "tool_call_id": tool_call_id,
                    "content": str(content or ""),
                }
            )
        else:
            formatted.append(
                {
                    "role": role,
                    "content": str(content or ""),
                }
            )

    return formatted


_format_messages_for_openai = format_messages_for_openai
