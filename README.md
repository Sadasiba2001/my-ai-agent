# My AI Agent

A clean, testable, modular, and enterprise-grade Python AI Agent architecture featuring dynamic multi-provider routing, automated Ollama 20-second timeout failover, SQLite + FTS5 long-term memory, and sandboxed tool execution.

---

## 🌟 Key Features

- **Agent Engine**: Reasoning loop with typed state tracking and max-iteration safeguards (`src/my_ai_agent/agent/`).
- **LLM Router**: Multi-provider failover chain (NVIDIA MiniMax/GLM -> Ollama) with explicit exception handling and a **mandatory 20-second execution deadline for Ollama calls** (`src/my_ai_agent/llm/`).
- **Memory Subsystem**: SQLite + FTS5 long-term memory with keyword ranking, metadata tagging, policy-based context injection, and expiration filtering (`src/my_ai_agent/memory/`).
- **Tool Sandbox**: Built-in filesystem and Python execution tools returning structured `ToolResult` objects with path containment checks and 30s timeouts (`src/my_ai_agent/tools/`).
- **Modern Packaging**: Modern `pyproject.toml` configuration supporting `pip install -e .` and comprehensive test tooling (`pytest`, `ruff`, `mypy`).

---

## 🚀 Quick Start

### 1. Installation

```bash
# Clone the repository
git clone https://github.com/Sadasiba2001/my-ai-agent.git
cd my-ai-agent

# Install package in editable mode with development dependencies
pip install -e .[dev]
```

### 2. Environment Configuration

Copy `.env.example` to `.env` and set your credentials:

```bash
cp .env.example .env
```

Example `.env`:
```ini
ACTIVE_MODEL=minimax
ENABLE_AUTO_FALLBACK=true
FALLBACK_ORDER=minimax,glm,ollama
OLLAMA_HOST=http://localhost:11434
OLLAMA_MODEL=qwen3:8b
MINIMAX_API_KEY=nvapi-your-key-here
GLM_API_KEY=nvapi-your-key-here
```

### 3. Run the Agent

```bash
# Interactive CLI mode
python main.py

# Single prompt mode
my-ai-agent --prompt "List project files and explain main.py"
```

---

## 🧪 Running Tests & Quality Checks

Run the complete automated test suite:

```bash
pytest -q
```

Run static analysis:

```bash
ruff check .
```

Run static type checking:

```bash
mypy src/
```

---

## 🔒 Security Limitations

- **Python Execution Tool (`run_python`)**: Scripts are restricted to executing inside the `workspace/` directory with a 30-second execution timeout and stdout/stderr output caps (100KB). Subprocess isolation does not provide hypervisor/container sandboxing; privilege boundaries rely on process timeouts and workspace path checks.
- **Secrets Management**: Secrets are strictly read from `.env` or environment variables; API keys are never logged or committed to source control.
