"""
OpenAI client proxy with the same interface used by DeepSeek wrapper.
"""

from __future__ import annotations

from functools import lru_cache

from openai import OpenAI

from app.config import settings


@lru_cache(maxsize=1)
def _client() -> OpenAI:
    if not settings.openai_api_key:
        raise RuntimeError("OpenAI API key not configured. Set INSTALILY_OPENAI_API_KEY in .env")
    return OpenAI(api_key=settings.openai_api_key)


class _CompletionsProxy:
    def create(self, *args, **kwargs):
        return _client().chat.completions.create(*args, **kwargs)


class _ChatProxy:
    def __init__(self):
        self.completions = _CompletionsProxy()


class _OpenAIClient:
    def __init__(self):
        self.chat = _ChatProxy()


openai_client = _OpenAIClient()

