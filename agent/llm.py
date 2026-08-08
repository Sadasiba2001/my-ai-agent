import os
import ollama
from dotenv import load_dotenv

from tools.filesystem import list_files

load_dotenv()

MODEL = os.getenv("OLLAMA_MODEL", "")
OLLAMA_HOST = os.getenv("OLLAMA_HOST", "")

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "list_files",
            "description": (
                "List files and directories. "
                "Use this tool whenever the user asks "
                "about files, folders, directories, "
                "or project contents."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": (
                            "Directory path to inspect. "
                            "Use '.' for the current directory."
                        )
                    }
                },
                "required": ["path"]
            }
        }
    }
]


def execute_tool(tool_name: str, arguments: dict) -> str:

    print(f"[Tool] Executing: {tool_name}")
    print(f"[Tool] Arguments: {arguments}")

    if tool_name == "list_files":
        return list_files(arguments.get("path", "."))

    return f"Unknown tool: {tool_name}"


def ask_llm(prompt: str) -> str:

    print("\n[Agent] Thinking...")

    messages = [
        {
            "role": "system",
            "content": (
                "You are an AI agent running on the user's computer. "
                "You have access to tools. "
                "When the user asks about files or directories, "
                "use the appropriate tool."
            )
        },
        {
            "role": "user",
            "content": prompt
        }
    ]

    # First request
    response = ollama.chat(
        model=MODEL,
        messages=messages,
        tools=TOOLS
    )

    message = response["message"]

    # No tool required
    if not message.get("tool_calls"):
        print("[Agent] Response received.")
        return message["content"]

    # Tool requested
    print("[Agent] Qwen wants to use a tool.")

    messages.append(message)

    # Execute every requested tool
    for tool_call in message["tool_calls"]:

        tool_name = tool_call["function"]["name"]
        arguments = tool_call["function"]["arguments"]

        result = execute_tool(
            tool_name,
            arguments
        )

        print("[Tool] Result:")
        print(result)

        messages.append(
            {
                "role": "tool",
                "content": result
            }
        )

    # Send tool result back to Qwen
    print("\n[Agent] Sending tool result back to Qwen...")

    final_response = ollama.chat(
        model=MODEL,
        messages=messages,
        tools=TOOLS
    )

    print("[Agent] Final response received.")

    return final_response["message"]["content"]