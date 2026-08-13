from typing import Any


class PromptBuilder:
    @staticmethod
    def build_system_instruction(
        tools_schemas: list[dict[str, Any]] | None = None,
        memory_context: str | None = None,
    ) -> str:
        instructions = [
            "You are an AI coding agent running on the user's computer.",
            "",
            "FAST EXECUTION DIRECTIVE:",
            "- Be direct, fast, and concise.",
            "- Do NOT generate long internal thinking, reasoning loops, or <think> blocks.",
            "- Immediately invoke the required tool for the task without preamble.",
            "",
            "PATH RULES:",
            "- list_files paths are relative to the project root.",
            "- read_file paths are relative to the project root.",
            "- write_file paths are relative to workspace/.",
            "- run_python paths are relative to workspace/.",
            "",
            "TASK RULES:",
            "Use tools when they are necessary to inspect, write, or execute code.",
            "After creating or modifying code, run or inspect it when appropriate.",
            "Do not claim that code works unless you have evidence from a tool result.",
            "Continue using tools until the user's task is complete.",
        ]

        if memory_context and memory_context.strip():
            instructions.extend(
                [
                    "",
                    "MEMORY CONTEXT:",
                    memory_context.strip(),
                ]
            )

        return "\n".join(instructions)
