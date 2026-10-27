"""Mengunduh halaman web dengan cache: halaman yang sudah ada di disk tidak diunduh ulang."""
import time
from pathlib import Path

import requests


def _download(url: str, scfg: dict) -> bytes:
    headers = {"User-Agent": scfg["user_agent"]}
    last_error = None
    for attempt in range(1, scfg["max_retries"] + 1):
        try:
            resp = requests.get(url, headers=headers, timeout=scfg["timeout_seconds"])
            resp.raise_for_status()
            return resp.content
        except requests.RequestException as e:
            last_error = e
            time.sleep(scfg["delay_seconds"] * attempt)  # jeda makin lama tiap gagal
    raise RuntimeError(f"Gagal mengunduh {url}: {last_error}")


def _decode(data: bytes) -> str:
    """
    Bytes -> teks dengan aturan yang sama di semua OS:
    - coba UTF-8, kalau gagal pakai cp1252 (encoding umum halaman lama)
    - semua akhir baris (\\r\\n atau \\r) diseragamkan menjadi \\n
    """
    try:
        text = data.decode("utf-8")
    except UnicodeDecodeError:
        text = data.decode("cp1252", errors="replace")
    return text.replace("\r\n", "\n").replace("\r", "\n")


def fetch_cached(url: str, cache_file: Path, scfg: dict) -> str:
    if not cache_file.exists():
        data = _download(url, scfg)
        cache_file.parent.mkdir(parents=True, exist_ok=True)
        cache_file.write_bytes(data)  # simpan apa adanya, tanpa konversi
        time.sleep(scfg["delay_seconds"])
    # Selalu dibaca dari cache, supaya run pertama dan run berikutnya
    # melewati jalur yang sama persis.
    return _decode(cache_file.read_bytes())