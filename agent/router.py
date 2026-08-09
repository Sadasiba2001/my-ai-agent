"""Backward compatibility facade for agent.router re-exporting llm package."""

from llm.router import ask_llm, chat_with_llm

__all__ = ["ask_llm", "chat_with_llm"]
