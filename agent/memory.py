"""Backward compatibility facade for agent.memory re-exporting memory package."""

from memory import MemoryManager

__all__ = ["MemoryManager"]
