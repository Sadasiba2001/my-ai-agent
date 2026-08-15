import pytest

from my_ai_agent.memory import (
    Memory,
    MemoryManager,
    MemoryType,
    SQLiteMemoryRepository,
)


def test_save_valid_memory(temp_dir):
    repo = SQLiteMemoryRepository(temp_dir / "test.db")
    memory = Memory(content="Python agent testing")
    saved = repo.save(memory)
    assert saved.id == memory.id
    assert saved.content == "Python agent testing"


def test_save_empty_memory_raises(temp_dir):
    repo = SQLiteMemoryRepository(temp_dir / "test.db")
    memory = Memory(content="   ")
    with pytest.raises(ValueError, match="content cannot be empty"):
        repo.save(memory)


def test_retrieve_existing_and_nonexistent(temp_dir):
    repo = SQLiteMemoryRepository(temp_dir / "test.db")
    memory = Memory(content="Retrieve me")
    repo.save(memory)

    retrieved = repo.get(memory.id)
    assert retrieved is not None
    assert retrieved.content == "Retrieve me"

    assert repo.get("nonexistent-id") is None


def test_delete_memory(temp_dir):
    repo = SQLiteMemoryRepository(temp_dir / "test.db")
    memory = Memory(content="Delete me")
    repo.save(memory)

    assert repo.delete(memory.id) is True
    assert repo.get(memory.id) is None
    assert repo.delete("nonexistent-id") is False


def test_search_memories(temp_dir):
    repo = SQLiteMemoryRepository(temp_dir / "test.db")
    repo.save(Memory(content="User likes dark mode theme"))
    repo.save(Memory(content="User prefers Python over Java"))
    repo.save(Memory(content="System initialized successfully"))

    results = repo.search("Python")
    assert len(results) == 1
    assert "Python" in results[0].content

    # Case insensitive partial search
    results_case = repo.search("python")
    assert len(results_case) == 1

    # No result search
    no_results = repo.search("Rust")
    assert len(no_results) == 0


def test_memory_metadata_and_expiration(temp_dir):
    manager = MemoryManager(db_path=temp_dir / "test.db")
    mem = manager.add_memory(
        content="Important fact",
        importance=0.9,
        confidence=0.95,
        memory_type=MemoryType.USER_PREFERENCE,
        tags=["ui", "pref"],
    )

    retrieved = manager.get_memory(mem.id)
    assert retrieved is not None
    assert retrieved.metadata.importance == 0.9
    assert retrieved.metadata.confidence == 0.95
    assert retrieved.type == MemoryType.USER_PREFERENCE
    assert "ui" in retrieved.metadata.tags


def test_memory_persistence(temp_dir):
    db_file = temp_dir / "persistent.db"

    # Save memory in one instance
    repo1 = SQLiteMemoryRepository(db_file)
    mem1 = Memory(content="Persistent memory item")
    repo1.save(mem1)

    # Re-open repository from same file (simulating app restart)
    repo2 = SQLiteMemoryRepository(db_file)
    retrieved = repo2.get(mem1.id)
    assert retrieved is not None
    assert retrieved.content == "Persistent memory item"
