from my_ai_agent.memory import MemoryManager, MemoryType


def test_sqlite_memory_search_ranking_and_context(temp_dir):
    manager = MemoryManager(db_path=temp_dir / "integration.db")

    manager.add_memory(
        content="User prefers Python for backend development",
        importance=0.8,
        memory_type=MemoryType.USER_PREFERENCE,
    )
    manager.add_memory(
        content="User uses dark mode UI theme in IDE",
        importance=0.4,
        memory_type=MemoryType.USER_PREFERENCE,
    )
    manager.add_memory(
        content="Project deadline is scheduled for next Friday",
        importance=0.9,
        memory_type=MemoryType.FACTUAL,
    )

    # Context query
    context = manager.get_context_for_prompt("Python backend")
    assert "User prefers Python for backend development" in context
    assert "Relevant Memories & Context:" in context

    # Delete memory verification
    all_memories = manager.search_memories("Python")
    assert len(all_memories) == 1
    mem_id = all_memories[0].id

    deleted = manager.delete_memory(mem_id)
    assert deleted is True
    assert len(manager.search_memories("Python")) == 0
