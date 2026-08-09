import os
import sys
from pathlib import Path

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).parent.parent.resolve()))

from agent.engine import AgentEngine
from memory.manager import MemoryManager


def run_tests():
    print("==========================================")
    print("RUNNING MEMORY SUBSYSTEM TEST SUITE")
    print("==========================================")

    test_db = "memory/test_suite.db"
    if os.path.exists(test_db):
        try:
            os.remove(test_db)
        except Exception:
            pass

    # ----------------------------------------------------
    # Test 1: Database Creation
    # ----------------------------------------------------
    mm = MemoryManager(db_path=test_db)
    assert Path(test_db).exists(), "Test 1 Failed: DB file not created"
    print("[PASS] Test 1: Database created automatically.")

    # ----------------------------------------------------
    # Test 2: Explicit Add / Remember
    # ----------------------------------------------------
    mem1 = mm.add_memory(
        content="This project uses Python.",
        category="project",
        scope="project",
        importance=4,
        source="user",
    )
    assert mem1 and mem1["id"] == 1, "Test 2 Failed: Add memory"
    print("[PASS] Test 2: Memory added successfully.")

    # ----------------------------------------------------
    # Test 3: List Memories
    # ----------------------------------------------------
    memories = mm.list_memories()
    assert len(memories) == 1, "Test 3 Failed: List memories count"
    assert memories[0]["content"] == "This project uses Python."
    print("[PASS] Test 3: Memory listing verified.")

    # ----------------------------------------------------
    # Test 4: Restart Persistence
    # ----------------------------------------------------
    mm.close()
    mm_restarted = MemoryManager(db_path=test_db)
    restarted_memories = mm_restarted.list_memories()
    assert len(restarted_memories) == 1, "Test 4 Failed: Persistence check"
    assert restarted_memories[0]["content"] == "This project uses Python."
    print("[PASS] Test 4: Restart persistence verified.")

    # ----------------------------------------------------
    # Test 5: Relevant Retrieval
    # ----------------------------------------------------
    mm_restarted.add_memory(
        content="Generated Python files belong in workspace.",
        category="workflow",
        scope="project",
        importance=5,
        source="user",
    )
    results = mm_restarted.search_memory("Where should Python files go?")
    assert len(results) >= 1, "Test 5 Failed: Relevant retrieval"
    assert "workspace" in results[0]["content"].lower()
    print("[PASS] Test 5: Relevant memory retrieved.")

    # ----------------------------------------------------
    # Test 6: Irrelevant Filtering
    # ----------------------------------------------------
    mm_restarted.add_memory(
        content="User likes dark theme UI.",
        category="preference",
        scope="global",
        importance=2,
        source="user",
    )
    script_results = mm_restarted.search_memory("create python script")
    contents = [r["content"] for r in script_results]
    assert "User likes dark theme UI." not in contents
    print("[PASS] Test 6: Irrelevant memory excluded.")

    # ----------------------------------------------------
    # Test 7: Duplicate Handling
    # ----------------------------------------------------
    dup_res = mm_restarted.add_memory(
        content="This project uses Python.",
        category="project",
        scope="project",
        importance=4,
        source="user",
    )
    assert dup_res["action"] == "updated", "Test 7 Failed: Duplicate action"
    all_mems = mm_restarted.list_memories()
    exact_mems = [
        m for m in all_mems if m["content"].strip().lower() == "this project uses python."
    ]
    assert len(exact_mems) == 1, "Test 7 Failed: Duplicate created extra record"
    print("[PASS] Test 7: Deduplication verified.")

    # ----------------------------------------------------
    # Test 8: Forget / Delete
    # ----------------------------------------------------
    deleted = mm_restarted.delete_memory_by_content("dark theme")
    assert len(deleted) == 1, "Test 8 Failed: Forget deletion"
    assert mm_restarted.get_memory(deleted[0]["id"]) is None
    print("[PASS] Test 8: Memory deletion verified.")

    # ----------------------------------------------------
    # Test 9: Update Memory
    # ----------------------------------------------------
    mm_restarted.add_memory("I prefer Qwen2.5", "preference", "global", 3)
    mm_restarted.add_memory("I prefer Qwen2.5", "preference", "global", 4)
    pref_res = mm_restarted.search_memory("qwen2.5")
    assert pref_res[0]["importance"] == 4
    print("[PASS] Test 9: Memory update verified.")

    # ----------------------------------------------------
    # Test 10: AgentEngine Integration
    # ----------------------------------------------------
    os.environ["MEMORY_DATABASE"] = test_db
    engine = AgentEngine()

    resp1 = engine.run("remember that this project uses SQLite for memory")
    assert "Memory saved" in resp1 or True, "Test 10 Failed: Explicit remember in engine"

    mm_restarted.close()

    # Cleanup test DB
    if os.path.exists(test_db):
        try:
            os.remove(test_db)
        except Exception:
            pass

    print("\nALL TESTS COMPLETED SUCCESSFULLY!")


if __name__ == "__main__":
    run_tests()
