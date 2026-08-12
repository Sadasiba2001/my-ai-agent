import os

from agent.state import AgentState
from llm import chat_with_llm
from tools.definitions import TOOLS
from tools.registry import execute_tool


class AgentEngine:

    def __init__(self, max_iterations: int = 10):
        self.max_iterations = int(
            os.getenv("AGENT_MAX_ITERATIONS", str(max_iterations))
        )
        self.state = AgentState()

    def run(self, prompt: str) -> str:
        # Reset state for new user request
        self.state.reset(prompt)

        # ----------------------------------------------------
        # Fast, Action-Oriented System Instruction
        # ----------------------------------------------------
        system_instruction = (
            "You are an AI coding agent running on the user's computer.\n\n"
            "FAST EXECUTION DIRECTIVE:\n"
            "- Be direct, fast, and concise.\n"
            "- Do NOT generate long internal thinking, reasoning loops, or <think> blocks.\n"
            "- Immediately invoke the required tool for the task without preamble.\n\n"
            "AVAILABLE TOOLS:\n"
            "- list_files: inspect project directories.\n"
            "- read_file: read text files.\n"
            "- write_file: create or modify files inside workspace/.\n"
            "- run_python: execute Python files inside workspace/.\n\n"
            "PATH RULES:\n"
            "- list_files paths are relative to the project root.\n"
            "- read_file paths are relative to the project root.\n"
            "- write_file paths are relative to workspace/.\n"
            "- run_python paths are relative to workspace/.\n\n"
            "TASK RULES:\n"
            "Use tools when they are necessary.\n"
            "If the user asks you to find a file, use list_files.\n"
            "If the user asks you to read or explain a file, use read_file.\n"
            "If the user asks you to create or modify a file, use write_file.\n"
            "If the user asks you to run Python code, use run_python.\n\n"
            "VERIFICATION RULES:\n"
            "After creating or modifying code, run or inspect it when appropriate.\n"
            "Do not claim that code works unless you have evidence from a tool result.\n"
            "If execution produces an error, analyze the error and attempt to fix the problem.\n\n"
            "Continue using tools until the user's task is actually complete."
        )

        messages = [
            {"role": "system", "content": system_instruction},
            {"role": "user", "content": prompt},
        ]

        # ----------------------------------------------------
        # 4. LLM & Tool Execution Loop
        # ----------------------------------------------------
        for iteration in range(self.max_iterations):
            self.state.iteration = iteration + 1

            print(
                f"\n[Agent] Iteration "
                f"{self.state.iteration}/"
                f"{self.max_iterations}"
            )

            response = chat_with_llm(messages=messages, tools=TOOLS)

            message = response["message"]

            # ------------------------------------------------
            # Agent finished the task
            # ------------------------------------------------
            if not message.get("tool_calls"):
                self.state.completed = True
                print("[Agent] Final response received.")

                return message.get("content", "")

            # ------------------------------------------------
            # Agent wants to use one or more tools
            # ------------------------------------------------
            print("[Agent] Agent wants to use tool(s).")
            messages.append(message)

            for i, tool_call in enumerate(message["tool_calls"]):
                tool_name = tool_call["function"]["name"]
                arguments = tool_call["function"]["arguments"]

                self.state.tool_calls += 1

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

        return (
            "I stopped because the maximum number of "
            "agent iterations was reached."
        )