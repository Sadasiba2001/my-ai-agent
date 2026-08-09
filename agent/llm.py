import os

import ollama
from dotenv import load_dotenv

from tools.registry import execute_tool


load_dotenv()


MODEL = os.getenv("OLLAMA_MODEL", "qwen3:8b")
OLLAMA_HOST = os.getenv(
    "OLLAMA_HOST",
    "http://localhost:11434"
)


ollama_client = ollama.Client(
    host=OLLAMA_HOST
)


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
    },
    {
        "type": "function",
        "function": {
            "name": "read_file",
            "description": (
                "Read the contents of a text file. "
                "Use this tool when the user asks "
                "to read, inspect, analyze, or explain "
                "a file."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": (
                            "Path of the text file to read."
                        )
                    }
                },
                "required": ["path"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "write_file",
            "description": (
                "Create or overwrite a text file inside "
                "the workspace directory. "
                "Use this when the user asks you to create "
                "or write a file."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": (
                            "File path relative to workspace."
                        )
                    },
                    "content": {
                        "type": "string",
                        "description": (
                            "Complete content to write into the file."
                        )
                    }
                },
                "required": [
                    "path",
                    "content"
                ]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "run_python",
            "description": (
                "Execute a Python script inside the workspace "
                "and return its output and errors. "
                "Use this tool when you need to test or execute "
                "a Python program."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": (
                            "Path of the Python script relative "
                            "to workspace."
                        )
                    }
                },
                "required": ["path"]
            }
        }
    }
]


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

        response = ollama_client.chat(
            model=MODEL,
            messages=messages,
            tools=TOOLS
        )

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