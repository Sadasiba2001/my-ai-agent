# Architecture Overview — my-ai-agent

## Core Design Principles

The `my-ai-agent` codebase follows strict **separation of concerns** and **dependency inversion**:

```text
CLI / API
    ↓
AgentEngine
    ↓
AgentLoop
    ↓
┌──────────────┬──────────────┬──────────────┐
│              │              │
Memory       LLMRouter      ToolRegistry
│              │              │
Repository   Provider       Tool
               │
       ┌───────┴────────┐
       │                │
    Ollama       OpenAI-compatible
```

- **AgentEngine**: Orchestrates high-level workflow (memory lookup -> agent loop execution -> interaction recording).
- **AgentLoop**: Manages multi-turn iterative reasoning and tool call execution with safeguards (`max_iterations`).
- **LLMRouter**: Handles multi-provider model selection and dynamic failover (NVIDIA MiniMax / GLM -> Ollama). Enforces a **mandatory 20-second timeout on Ollama calls**.
- **MemoryManager**: Interacts with `SQLiteMemoryRepository` (using FTS5 full-text indexing) to store and retrieve long-term context independently.
- **ToolRegistry**: Manages tool registration, validation, execution, and OpenAI function schema generation for filesystem and Python execution tools.

---

## Directory Structure

```text
src/
└── my_ai_agent/
    ├── agent/
    │   ├── engine.py      # Top-level orchestrator
    │   ├── loop.py        # Multi-turn reasoning loop
    │   ├── state.py       # Typed agent state
    │   └── prompts.py     # Prompt assembly builder
    ├── llm/
    │   ├── router.py      # Multi-provider failover router
    │   ├── models.py      # LLMResult & LLMMessage models
    │   ├── exceptions.py  # Structured exceptions
    │   └── providers/
    │       ├── base.py    # LLMProvider abstract base class
    │       ├── ollama.py  # Ollama provider with 20s timeout
    │       └── openai_compatible.py # NVIDIA MiniMax / GLM provider
    ├── memory/
    │   ├── manager.py     # MemoryManager top-level facade
    │   ├── repository.py  # SQLite repository with FTS5
    │   ├── models.py      # Memory & metadata models
    │   ├── search.py      # Keyword + importance ranking
    │   └── policies.py    # Context formatting & expiration
    ├── tools/
    │   ├── base.py        # Tool ABC and ToolResult dataclass
    │   ├── registry.py    # ToolRegistry container
    │   ├── filesystem.py  # ListFilesTool, ReadFileTool, WriteFileTool
    │   └── python.py      # RunPythonTool with sandbox bounds
    ├── config/
    │   └── settings.py    # Typed Settings dataclass
    ├── cli/
    │   └── app.py         # CLI application
    └── utils/
        ├── logging.py     # Structured logging
        └── formatters.py  # OpenAI message sanitizers
```
