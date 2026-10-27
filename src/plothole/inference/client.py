"""Satu pemanggil untuk semua provider (endpoint kompatibel OpenAI)."""
import os
import time

from openai import OpenAI


def make_client(mcfg: dict) -> OpenAI:
    key = os.getenv(mcfg["api_key_env"])
    if not key:
        raise RuntimeError(f"{mcfg['api_key_env']} kosong di .env")
    # timeout panjang karena prompt bisa ~50 ribu token; SDK sudah retry otomatis
    return OpenAI(api_key=key, base_url=mcfg.get("base_url"), timeout=600, max_retries=3)


def call_model(client, mcfg: dict, messages: list[dict]) -> dict:
    t0 = time.perf_counter()
    resp = client.chat.completions.create(
        model=mcfg["model_id"], messages=messages, **mcfg.get("params", {})
    )
    latency = time.perf_counter() - t0

    choice = resp.choices[0]
    usage = resp.usage
    details = getattr(usage, "completion_tokens_details", None)
    price = mcfg["price_per_mtok"]
    cost = (usage.prompt_tokens * price["input"] + usage.completion_tokens * price["output"]) / 1e6

    return {
        "model_returned": resp.model,          # versi yang BENAR-BENAR menjawab
        "content": choice.message.content,
        "reasoning_content": getattr(choice.message, "reasoning_content", None),
        "finish_reason": choice.finish_reason,  # "length" = output terpotong
        "prompt_tokens": usage.prompt_tokens,
        "completion_tokens": usage.completion_tokens,
        "reasoning_tokens": getattr(details, "reasoning_tokens", None) if details else None,
        "latency_s": round(latency, 2),
        "cost_usd": round(cost, 6),
    }