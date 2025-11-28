"""
DeepSeek client wrapper (OpenAI-compatible API).
"""

from __future__ import annotations
from functools import lru_cache

from openai import OpenAI
from app.config import settings


@lru_cache(maxsize=1)
def _client() -> OpenAI:
    if not settings.deepseek_api_key:
        raise RuntimeError(
            "DeepSeek API key missing. Set INSTALILY_DEEPSEEK_API_KEY in .env"
        )
    return OpenAI(
        api_key=settings.deepseek_api_key,
        base_url="https://api.deepseek.com"
    )


class _CompletionsProxy:
    def create(self, *args, **kwargs):
        return _client().chat.completions.create(*args, **kwargs)


class _ChatProxy:
    def __init__(self):
        self.completions = _CompletionsProxy()


class _DeepSeekClient:
    def __init__(self):
        self.chat = _ChatProxy()


deepseek_client = _DeepSeekClient()
