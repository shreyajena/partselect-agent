"""
LLM provider selector (DeepSeek or OpenAI).
Used by handlers to perform text generation with RAG context.
"""

from __future__ import annotations
from functools import lru_cache

from app.config import settings
from app.llm import deepseek, openai_client


@lru_cache(maxsize=1)
def _provider() -> str:
    """
    Returns: "deepseek" or "openai"
    Default: deepseek (as required by case study)
    """
    return (settings.llm_provider or "deepseek").lower()


@lru_cache(maxsize=1)
def get_chat_client():
    """
    Returns the correct client wrapper with .chat.completions.create().
    """
    if _provider() == "openai":
        return openai_client.openai_client
    return deepseek.deepseek_client


def get_default_model() -> str:
    """
    Returns model name per provider.
    Defaults:
      - DeepSeek:  deepseek-chat
      - OpenAI:    gpt-4o-mini
    """
    if _provider() == "openai":
        return settings.openai_model or "gpt-4o-mini"
    return settings.deepseek_model or "deepseek-chat"
