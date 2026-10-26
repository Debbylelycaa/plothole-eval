"""Mencari snapshot Wayback Machine dan membentuk URL arsipnya."""
import requests

API = "https://archive.org/wayback/available"


def find_snapshot(url: str, scfg: dict) -> str | None:
    """Mengembalikan timestamp snapshot terdekat ke scfg['wayback_target'], atau None."""
    params = {"url": url, "timestamp": scfg["wayback_target"]}
    resp = requests.get(API, params=params, timeout=scfg["timeout_seconds"])
    resp.raise_for_status()
    snap = resp.json().get("archived_snapshots", {}).get("closest")
    if snap and snap.get("available") and snap.get("status") == "200":
        return snap["timestamp"]
    return None


def raw_snapshot_url(original_url: str, timestamp: str) -> str:
    return f"https://web.archive.org/web/{timestamp}id_/{original_url}"