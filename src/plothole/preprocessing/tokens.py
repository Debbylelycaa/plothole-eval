"""Estimasi jumlah token. Token sebenarnya per model dicatat dari respons API (Fase 4)."""
from functools import lru_cache

import tiktoken


@lru_cache(maxsize=None)
def _encoder(name: str):
    # lru_cache: encoder cukup dimuat sekali, lalu dipakai ulang
    return tiktoken.get_encoding(name)


def count_tokens(text: str, encoding: str) -> int:
    return len(_encoder(encoding).encode(text))