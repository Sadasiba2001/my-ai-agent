from agent.llm import chat_with_llm
from tools.definitions import TOOLS
from tools.registry import execute_tool


class AgentEngine:

    def __init__(self, max_iterations: int = 10):
        self.max_iterations = max_iterations

    def run(self, prompt: str) -> str:

        messages = [
            {
                "role": "system",
                "content": (
                    "You are an AI coding agent running on the user's "
                    "computer.\n\n"

                    "You can work with files and Python using tools.\n\n"

                    "Available tools:\n"
                    "- list_files: inspect project directories.\n"
                    "- read_file: read text files.\n"
                    "- write_file: create or modify files inside workspace/.\n"
                    "- run_python: execute Python files inside workspace/.\n\n"

                    "Complete the user's task using tools when necessary.\n"
                    "Do not merely explain what should be done.\n"
                    "Continue using tools until the task is complete."
                )
            },
            {
                "role": "user",
                "content": prompt
            }
        ]

        for iteration in range(self.max_iterations):

            print(
                f"\n[Agent] Iteration "
                f"{iteration + 1}/{self.max_iterations}"
            )

            response = chat_with_llm(
                messages=messages,
                tools=TOOLS
            )

            message = response["message"]

            # Qwen has finished
            if not message.get("tool_calls"):

                print("[Agent] Final response received.")

                return message.get("content", "")

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

        return (
            "I stopped because the maximum number of "
            "agent iterations was reached."
        )