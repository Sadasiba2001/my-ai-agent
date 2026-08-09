import os

import ollama
from dotenv import load_dotenv

from tools import TOOLS, execute_tool

load_dotenv()


MODEL = os.getenv("OLLAMA_MODEL") or "qwen3:8b"
OLLAMA_HOST = os.getenv("OLLAMA_HOST") or "http://localhost:11434"


ollama_client = ollama.Client(
    host=OLLAMA_HOST
)


def chat_with_llm(messages: list, tools: list | None = None):
    return ollama_client.chat(
        model=MODEL,
        messages=messages,
        tools=tools or []
    )


def ask_llm(prompt: str) -> str:
    print("\n[Agent] Thinking...")

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
            )
        },
        {
            "role": "user",
            "content": prompt
        }
    ]

    while True:
        response = chat_with_llm(messages=messages, tools=TOOLS)
        message = response["message"]

        # --------------------------------
        # No tool required
        # --------------------------------
        if not message.get("tool_calls"):
            print("[Agent] Final response received.")
            return message["content"]

        # --------------------------------
        # Tool requested
        # --------------------------------
        print("[Agent] Qwen wants to use a tool.")
        messages.append(message)

        for tool_call in message["tool_calls"]:
            tool_name = tool_call["function"]["name"]
            arguments = tool_call["function"]["arguments"]

            print(f"[Tool] Executing: {tool_name}")
            print(f"[Tool] Arguments: {arguments}")

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

        print("\n[Agent] Continuing...")