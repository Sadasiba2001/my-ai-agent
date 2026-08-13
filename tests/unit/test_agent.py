from my_ai_agent.agent import AgentEngine, PromptBuilder
from my_ai_agent.llm import LLMProvider, LLMResult, LLMRouter, ProviderProfile
from my_ai_agent.memory import MemoryManager


class MockLLMProvider(LLMProvider):
    def __init__(self, profile: ProviderProfile, responses: list[LLMResult]):
        super().__init__(profile)
        self.responses = responses
        self.call_count = 0

    def chat(self, messages, tools=None):
        if self.call_count < len(self.responses):
            res = self.responses[self.call_count]
            self.call_count += 1
            return res
        return LLMResult(content="Done", provider="mock", model="mock", latency_ms=1.0)


def test_agent_basic_request(temp_dir):
    prof = ProviderProfile(key="mock", provider="mock", display_name="Mock", model="mock")
    res1 = LLMResult(content="Hello! How can I help you?", provider="mock", model="mock", latency_ms=10.0)
    provider = MockLLMProvider(prof, [res1])

    router = LLMRouter(candidate_keys=["mock"], providers={"mock": provider})
    mem_manager = MemoryManager(db_path=temp_dir / "agent_mem.db")

    agent = AgentEngine(router=router, memory_manager=mem_manager)
    response = agent.run("Hello")

    assert response == "Hello! How can I help you?"
    assert agent.state.completed is True
    assert agent.state.iteration == 1


def test_agent_tool_execution_loop(temp_dir):
    prof = ProviderProfile(key="mock", provider="mock", display_name="Mock", model="mock")
    # Step 1: LLM calls list_files tool
    res1 = LLMResult(
        content="",
        provider="mock",
        model="mock",
        latency_ms=15.0,
        tool_calls=[
            {
                "id": "call_1",
                "function": {"name": "list_files", "arguments": {"path": "."}},
            }
        ],
    )
    # Step 2: LLM finishes task
    res2 = LLMResult(
        content="I listed the directory files.",
        provider="mock",
        model="mock",
        latency_ms=12.0,
    )

    provider = MockLLMProvider(prof, [res1, res2])
    router = LLMRouter(candidate_keys=["mock"], providers={"mock": provider})
    mem_manager = MemoryManager(db_path=temp_dir / "agent_mem2.db")

    agent = AgentEngine(router=router, memory_manager=mem_manager)
    response = agent.run("Show files")

    assert response == "I listed the directory files."
    assert agent.state.tool_calls == 1
    assert agent.state.iteration == 2


def test_agent_max_iterations_exceeded(temp_dir):
    prof = ProviderProfile(key="mock", provider="mock", display_name="Mock", model="mock")
    # Provider always requests another tool call
    res_loop = LLMResult(
        content="",
        provider="mock",
        model="mock",
        latency_ms=5.0,
        tool_calls=[
            {
                "id": "call_loop",
                "function": {"name": "list_files", "arguments": {"path": "."}},
            }
        ],
    )

    provider = MockLLMProvider(prof, [res_loop] * 10)
    router = LLMRouter(candidate_keys=["mock"], providers={"mock": provider})
    mem_manager = MemoryManager(db_path=temp_dir / "agent_mem3.db")

    agent = AgentEngine(max_iterations=3, router=router, memory_manager=mem_manager)
    response = agent.run("Loop forever")

    assert "maximum iteration limit (3)" in response
    assert agent.state.completed is False
    assert agent.state.iteration == 3


def test_prompt_builder_memory_context_assembly():
    prompt = PromptBuilder.build_system_instruction(
        memory_context="User prefers dark mode."
    )
    assert "User prefers dark mode." in prompt
    assert "FAST EXECUTION DIRECTIVE:" in prompt
