# Memory Subsystem Documentation

## Overview

The memory subsystem in `my-ai-agent` provides long-term persistence, semantic full-text search, metadata tagging, and ranking for context injection into LLM prompts.

---

## Component Architecture

```text
MemoryManager
     ↓
┌─────────────────┬─────────────────┐
│                 │                 │
SQLiteRepository  MemorySearch      MemoryPolicies
(Persistence)     (Ranking)         (Expiration & Formatting)
```

### Models (`memory/models.py`)

- **`Memory`**: `id`, `content`, `type`, `source`, `metadata`.
- **`MemoryType`**: `SHORT_TERM`, `LONG_TERM`, `EPISODIC`, `FACTUAL`, `USER_PREFERENCE`.
- **`MemorySource`**: `USER_INPUT`, `AGENT_REFLECTION`, `TOOL_RESULT`, `SYSTEM`.
- **`MemoryMetadata`**: `confidence`, `importance`, `created_at`, `updated_at`, `expires_at`, `session_id`, `tags`.

---

## SQLite Database Schema

Memories are stored in SQLite (`data/memory.db`) with an optional FTS5 virtual table for full-text search:

```sql
CREATE TABLE IF NOT EXISTS memories (
    id TEXT PRIMARY KEY,
    content TEXT NOT NULL,
    type TEXT NOT NULL,
    source TEXT NOT NULL,
    metadata TEXT NOT NULL,
    created_at TEXT NOT NULL
);

CREATE VIRTUAL TABLE IF NOT EXISTS memories_fts USING fts5(
    id UNINDEXED,
    content
);
```

---

## Search & Ranking Algorithm

Search query results are retrieved via FTS5 match (or `LIKE` fallback), filtered for expiration, and ranked using:

$$\text{Score} = (1.5 \times \text{Keyword Match Count}) + \text{Importance Score}$$
