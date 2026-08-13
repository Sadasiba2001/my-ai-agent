import logging

from my_ai_agent.agent.prompts import PromptBuilder
from my_ai_agent.agent.state import AgentState
from my_ai_agent.llm.router import LLMRouter, _default_router
from my_ai_agent.tools.registry import ToolRegistry, default_registry

logger = logging.getLogger(__name__)


class AgentLoop:
    def __init__(
        self,
        router: LLMRouter | None = None,
        registry: ToolRegistry | None = None,
        max_iterations: int = 10,
    ):
        self.router = router or _default_router
        self.registry = registry or default_registry
        self.max_iterations = max_iterations

    def run(
        self, prompt: str, state: AgentState, memory_context: str = ""
    ) -> str:
        state.reset(prompt)

        system_instruction = PromptBuilder.build_system_instruction(
            tools_schemas=self.registry.get_schemas(),
            memory_context=memory_context,
        )

        messages = [
            {"role": "system", "content": system_instruction},
            {"role": "user", "content": prompt},
        ]
        state.history = messages

        for iteration in range(self.max_iterations):
            state.iteration = iteration + 1
            logger.info(
                f"[AgentLoop] Iteration {state.iteration}/{self.max_iterations}"
            )

            llm_result = self.router.chat(
                messages=messages,
                tools=self.registry.get_schemas(),
            )

            tool_calls = llm_result.tool_calls
            assistant_content = llm_result.content

            if not tool_calls:
                state.completed = True
                logger.info("[AgentLoop] Final response received from LLM.")
                return assistant_content

            # Assistant requested tool calls
            logger.info(f"[AgentLoop] LLM requested {len(tool_calls)} tool call(s).")
            messages.append(
                {
                    "role": "assistant",
                    "content": assistant_content or "",
                    "tool_calls": tool_calls,
                }
            )

            for i, tool_call in enumerate(tool_calls):
                fn = tool_call.get("function", {})
                tool_name = fn.get("name", "")
                arguments = fn.get("arguments", {})

                state.tool_calls += 1
                logger.info(f"[Tool] Executing '{tool_name}' with args {arguments}")

                tool_res = self.registry.execute(tool_name, arguments)
                tool_call_id = tool_call.get("id") or f"call_{state.iteration}_{i}"

                messages.append(
                    {
                        "role": "tool",
                        "tool_call_id": tool_call_id,
                        "content": str(tool_res),
                    }
                )

        state.completed = False
        return (
            f"Agent stopped because maximum iteration limit ({self.max_iterations}) was reached."
        )
