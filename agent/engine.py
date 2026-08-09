import os
import re

from agent.state import AgentState
from llm import chat_with_llm
from memory import MemoryManager
from tools.definitions import TOOLS
from tools.registry import execute_tool


class AgentEngine:

    def __init__(self, max_iterations: int = 10):
        self.max_iterations = int(
            os.getenv("AGENT_MAX_ITERATIONS", str(max_iterations))
        )
        self.state = AgentState()

        # Initialize Memory Subsystem
        db_path = os.getenv("MEMORY_DATABASE", "memory/agent_memory.db")
        self.memory = MemoryManager(db_path=db_path)

        # Disabled memory by default to keep model fast and focused
        self.memory_enabled = (
            os.getenv("MEMORY_ENABLED", "false").lower().strip()
            in ("true", "1", "yes")
        )
        self.retrieval_limit = int(os.getenv("MEMORY_RETRIEVAL_LIMIT", "5"))
        self.auto_save = (
            os.getenv("MEMORY_AUTO_SAVE", "false").lower().strip()
            in ("true", "1", "yes")
        )
        self.min_importance = int(os.getenv("MEMORY_MIN_IMPORTANCE", "3"))

    def _handle_explicit_memory_commands(self, prompt: str) -> str | None:
        """Check and execute explicit memory commands (remember, forget, list)."""
        lower_prompt = prompt.strip().lower()

        # ----------------------------------------------------
        # 1. List / Show memories
        # ----------------------------------------------------
        list_patterns = [
            "what do you remember",
            "show memories",
            "show my memories",
            "list memories",
            "list my memories",
            "view memories",
        ]
        if any(pat in lower_prompt for pat in list_patterns):
            memories = self.memory.list_memories()
            if not memories:
                return "I don't have any saved memories yet."

            lines = ["Here is what I remember:"]
            for i, mem in enumerate(memories, 1):
                lines.append(
                    f"{i}. [{mem['category'].upper()}] {mem['content']} "
                    f"(Scope: {mem['scope']}, Importance: {mem['importance']})"
                )
            return "\n".join(lines)

        # ----------------------------------------------------
        # 2. Explicit Forget
        # ----------------------------------------------------
        forget_match = re.match(
            r"^(?:please\s+)?forget(?:\s+that)?\s+(.+)$",
            prompt.strip(),
            re.IGNORECASE,
        )
        if forget_match:
            target_content = forget_match.group(1).strip()
            deleted = self.memory.delete_memory_by_content(target_content)

            if deleted:
                deleted_items = ", ".join([f'"{d["content"]}"' for d in deleted])
                print(f"[Memory] Deleted memory: {deleted_items}")
                return f"Memory forgotten: {deleted_items}"
            else:
                return f'I couldn\'t find any memory matching "{target_content}".'

        # ----------------------------------------------------
        # 3. Explicit Remember
        # ----------------------------------------------------
        remember_match = re.match(
            r"^(?:please\s+)?remember(?:\s+that)?\s+(.+)$",
            prompt.strip(),
            re.IGNORECASE,
        )
        if remember_match:
            content_to_save = remember_match.group(1).strip()

            category = "fact"
            lower_content = content_to_save.lower()
            if any(
                k in lower_content
                for k in ["prefer", "like", "love", "hate", "want"]
            ):
                category = "preference"
            elif any(
                k in lower_content for k in ["project", "repository", "app"]
            ):
                category = "project"
            elif any(
                k in lower_content
                for k in ["must", "should", "always", "never", "do not"]
            ):
                category = "instruction"

            result = self.memory.add_memory(
                content=content_to_save,
                category=category,
                scope="global",
                importance=4,
                source="user",
            )

            if result:
                action = result.get("action", "saved")
                print(f"[Memory] Memory {action}: {content_to_save}")
                return f'Memory saved: "{content_to_save}"'
            else:
                return "Failed to save memory due to an internal error."

        return None

    def run(self, prompt: str) -> str:
        # Reset state for new user request
        self.state.reset(prompt)

        # ----------------------------------------------------
        # 1. Handle explicit memory commands if enabled
        # ----------------------------------------------------
        if self.memory_enabled:
            explicit_response = self._handle_explicit_memory_commands(prompt)
            if explicit_response is not None:
                return explicit_response

        # ----------------------------------------------------
        # 2. Retrieve relevant long-term memories if enabled
        # ----------------------------------------------------
        memory_context = ""
        if self.memory_enabled:
            relevant_memories = self.memory.search_memory(
                query=prompt, limit=self.retrieval_limit
            )
            if relevant_memories:
                print(
                    f"[Memory] Retrieved {len(relevant_memories)} relevant memories."
                )
                mem_lines = []
                for i, m in enumerate(relevant_memories, 1):
                    mem_lines.append(f"{i}. {m['content']}")

                memory_context = (
                    "\n\nRELEVANT LONG-TERM MEMORIES:\n"
                    + "\n".join(mem_lines)
                )

        # ----------------------------------------------------
        # 3. Fast, Action-Oriented System Instruction
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
            f"{memory_context}"
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