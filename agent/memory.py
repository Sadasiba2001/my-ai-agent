import os
import sqlite3
from datetime import datetime, timezone
from pathlib import Path


class MemoryManager:
    """Persistent memory subsystem backed by SQLite."""

    def __init__(self, db_path: str = "memory/agent_memory.db"):
        self.db_path = Path(db_path).resolve()
        self.initialize()

    def _get_connection(self) -> sqlite3.Connection:
        """Get a thread-safe connection to the SQLite database."""
        conn = sqlite3.connect(str(self.db_path), check_same_thread=False)
        conn.row_factory = sqlite3.Row
        return conn

    def initialize(self):
        """Create database directory and memory tables if they do not exist."""
        try:
            self.db_path.parent.mkdir(parents=True, exist_ok=True)
            with self._get_connection() as conn:
                conn.execute(
                    """
                    CREATE TABLE IF NOT EXISTS memories (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        content TEXT NOT NULL,
                        category TEXT NOT NULL,
                        scope TEXT NOT NULL DEFAULT 'global',
                        importance INTEGER NOT NULL DEFAULT 1,
                        source TEXT,
                        created_at TEXT NOT NULL,
                        updated_at TEXT NOT NULL
                    );
                    """
                )
                conn.commit()
        except Exception as e:
            print(f"[Memory Error] Database initialization failed: {e}")

    def _normalize_text(self, text: str) -> str:
        """Normalize text for deduplication checks."""
        return " ".join(text.strip().lower().split())

    def add_memory(
        self,
        content: str,
        category: str = "fact",
        scope: str = "global",
        importance: int = 1,
        source: str = "agent",
    ) -> dict:
        """Add a new memory or update an existing duplicate memory."""
        cleaned_content = content.strip()
        if not cleaned_content:
            return {}

        now = datetime.now(timezone.utc).isoformat()
        normalized_new = self._normalize_text(cleaned_content)

        try:
            with self._get_connection() as conn:
                # Check for existing duplicate memory
                cursor = conn.execute("SELECT * FROM memories")
                existing_rows = cursor.fetchall()

                for row in existing_rows:
                    if self._normalize_text(row["content"]) == normalized_new:
                        # Update existing memory with higher importance & fresh timestamp
                        new_importance = max(row["importance"], importance)
                        conn.execute(
                            """
                            UPDATE memories
                            SET content = ?, category = ?, scope = ?, importance = ?, source = ?, updated_at = ?
                            WHERE id = ?
                            """,
                            (
                                cleaned_content,
                                category,
                                scope,
                                new_importance,
                                source,
                                now,
                                row["id"],
                            ),
                        )
                        conn.commit()
                        return {
                            "id": row["id"],
                            "content": cleaned_content,
                            "category": category,
                            "scope": scope,
                            "importance": new_importance,
                            "source": source,
                            "created_at": row["created_at"],
                            "updated_at": now,
                            "action": "updated",
                        }

                # Insert new memory record
                cursor = conn.execute(
                    """
                    INSERT INTO memories (content, category, scope, importance, source, created_at, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        cleaned_content,
                        category,
                        scope,
                        importance,
                        source,
                        now,
                        now,
                    ),
                )
                conn.commit()
                new_id = cursor.lastrowid
                return {
                    "id": new_id,
                    "content": cleaned_content,
                    "category": category,
                    "scope": scope,
                    "importance": importance,
                    "source": source,
                    "created_at": now,
                    "updated_at": now,
                    "action": "created",
                }

        except Exception as e:
            print(f"[Memory Error] Failed to add memory: {e}")
            return {}

    def search_memory(self, query: str, limit: int = 5) -> list[dict]:
        """Search relevant memories using keyword matching."""
        if not query or not query.strip():
            return []

        cleaned_query = query.strip()
        keywords = [
            k for k in cleaned_query.lower().split() if len(k) > 2
        ]

        try:
            with self._get_connection() as conn:
                if not keywords:
                    pattern = f"%{cleaned_query}%"
                    cursor = conn.execute(
                        """
                        SELECT * FROM memories
                        WHERE content LIKE ? OR category LIKE ? OR scope LIKE ?
                        ORDER BY importance DESC, updated_at DESC
                        LIMIT ?
                        """,
                        (pattern, pattern, pattern, limit),
                    )
                else:
                    # Construct SQL clause for keyword matching
                    conditions = " OR ".join(["content LIKE ?"] * len(keywords))
                    params = [f"%{kw}%" for kw in keywords] + [limit]
                    cursor = conn.execute(
                        f"""
                        SELECT * FROM memories
                        WHERE {conditions}
                        ORDER BY importance DESC, updated_at DESC
                        LIMIT ?
                        """,
                        params,
                    )

                results = [dict(row) for row in cursor.fetchall()]
                return results
        except Exception as e:
            print(f"[Memory Error] Search memory failed: {e}")
            return []

    def get_memory(self, memory_id: int) -> dict | None:
        """Get a single memory by ID."""
        try:
            with self._get_connection() as conn:
                cursor = conn.execute(
                    "SELECT * FROM memories WHERE id = ?", (memory_id,)
                )
                row = cursor.fetchone()
                return dict(row) if row else None
        except Exception as e:
            print(f"[Memory Error] Get memory failed: {e}")
            return None

    def list_memories(
        self, scope: str | None = None, category: str | None = None
    ) -> list[dict]:
        """List all stored memories with optional filtering."""
        try:
            with self._get_connection() as conn:
                query = "SELECT * FROM memories WHERE 1=1"
                params = []

                if scope:
                    query += " AND scope = ?"
                    params.append(scope)

                if category:
                    query += " AND category = ?"
                    params.append(category)

                query += " ORDER BY importance DESC, updated_at DESC"
                cursor = conn.execute(query, params)
                return [dict(row) for row in cursor.fetchall()]
        except Exception as e:
            print(f"[Memory Error] List memories failed: {e}")
            return []

    def delete_memory(self, memory_id: int) -> bool:
        """Delete a memory by ID."""
        try:
            with self._get_connection() as conn:
                cursor = conn.execute(
                    "DELETE FROM memories WHERE id = ?", (memory_id,)
                )
                conn.commit()
                return cursor.rowcount > 0
        except Exception as e:
            print(f"[Memory Error] Delete memory failed: {e}")
            return False

    def delete_memory_by_content(self, content_query: str) -> list[dict]:
        """Search and delete memories matching a content string."""
        matching = self.search_memory(content_query, limit=10)
        deleted = []
        for mem in matching:
            if self.delete_memory(mem["id"]):
                deleted.append(mem)
        return deleted

    def update_memory(
        self, memory_id: int, content: str, importance: int | None = None
    ) -> bool:
        """Update existing memory content and timestamp."""
        now = datetime.now(timezone.utc).isoformat()
        try:
            with self._get_connection() as conn:
                if importance is not None:
                    cursor = conn.execute(
                        """
                        UPDATE memories
                        SET content = ?, importance = ?, updated_at = ?
                        WHERE id = ?
                        """,
                        (content.strip(), importance, now, memory_id),
                    )
                else:
                    cursor = conn.execute(
                        """
                        UPDATE memories
                        SET content = ?, updated_at = ?
                        WHERE id = ?
                        """,
                        (content.strip(), now, memory_id),
                    )
                conn.commit()
                return cursor.rowcount > 0
        except Exception as e:
            print(f"[Memory Error] Update memory failed: {e}")
            return False

    def clear_memory() -> bool:
        """Clear all stored memories."""
        try:
            with self._get_connection() as conn:
                conn.execute("DELETE FROM memories")
                conn.commit()
                return True
        except Exception as e:
            print(f"[Memory Error] Clear memory failed: {e}")
            return False

    def close(self):
        """Close connection placeholder."""
        pass
