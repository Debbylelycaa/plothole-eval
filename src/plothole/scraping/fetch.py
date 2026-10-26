"""Mengunduh halaman web dengan cache: halaman yang sudah ada di disk tidak diunduh ulang."""
import time
from pathlib import Path

import requests


def fetch_cached(url: str, cache_file: Path, scfg: dict) -> str:
    if cache_file.exists():
        return cache_file.read_text(encoding="utf-8")

    headers = {"User-Agent": scfg["user_agent"]}
    last_error = None
    for attempt in range(1, scfg["max_retries"] + 1):
        try:
            resp = requests.get(url, headers=headers, timeout=scfg["timeout_seconds"])
            resp.raise_for_status()
            break
        except requests.RequestException as e:
            last_error = e
            time.sleep(scfg["delay_seconds"] * attempt)  # jeda makin lama tiap gagal
    else:
        raise RuntimeError(f"Gagal mengunduh {url}: {last_error}")

    cache_file.parent.mkdir(parents=True, exist_ok=True)
    cache_file.write_text(resp.text, encoding="utf-8")
    time.sleep(scfg["delay_seconds"])
    return resp.text