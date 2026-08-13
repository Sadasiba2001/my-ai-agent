import os

from my_ai_agent.agent.loop import AgentLoop
from my_ai_agent.agent.state import AgentState
from my_ai_agent.llm.router import LLMRouter, _default_router
from my_ai_agent.memory.manager import MemoryManager
from my_ai_agent.tools.registry import ToolRegistry, default_registry


class AgentEngine:
    def __init__(
        self,
        max_iterations: int | None = None,
        router: LLMRouter | None = None,
        registry: ToolRegistry | None = None,
        memory_manager: MemoryManager | None = None,
    ):
        if max_iterations is not None:
            self.max_iterations = max_iterations
        else:
            self.max_iterations = int(os.getenv("AGENT_MAX_ITERATIONS", "10"))

        self.router = router or _default_router
        self.registry = registry or default_registry
        self.memory_manager = memory_manager or MemoryManager()
        self.state = AgentState()
        self.loop = AgentLoop(
            router=self.router,
            registry=self.registry,
            max_iterations=self.max_iterations,
        )

    def run(self, prompt: str) -> str:
        memory_context = self.memory_manager.get_context_for_prompt(prompt, limit=5)

        response = self.loop.run(
            prompt=prompt,
            state=self.state,
            memory_context=memory_context,
        )

        if prompt.strip():
            self.memory_manager.add_memory(
                content=f"User requested: {prompt}",
                importance=0.5,
            )

        return response
