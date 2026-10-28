"""Mengubah respons mentah model menjadi daftar prediksi terstruktur."""
import json
import re

FENCE = re.compile(r"```(?:json)?\s*(.*?)```", re.S)


def extract_json(content: str | None) -> tuple[dict | None, str]:
    """
    Mengembalikan (objek JSON, status format):
    'clean'     = respons adalah JSON murni
    'extracted' = JSON terbungkus teks lain (mis. ```json ... ```), berhasil diambil
    'broken'    = tidak ada JSON yang bisa dibaca
    """
    if not content:
        return None, "broken"
    try:
        return json.loads(content), "clean"
    except json.JSONDecodeError:
        pass

    candidates = FENCE.findall(content)
    start, end = content.find("{"), content.rfind("}")
    if start != -1 and end > start:
        candidates.append(content[start:end + 1])
    for candidate in candidates:
        try:
            return json.loads(candidate), "extracted"
        except json.JSONDecodeError:
            continue
    return None, "broken"


def to_unit(value, n_units: int) -> int | None:
    """Nomor unit valid (1..n_units) atau None. Nilai aneh (teks, di luar rentang) -> None."""
    try:
        unit = int(value)
    except (TypeError, ValueError):
        return None
    return unit if 1 <= unit <= n_units else None


def parse_predictions(obj, n_units: int) -> list[dict]:
    items = obj.get("plot_holes", []) if isinstance(obj, dict) else []
    predictions = []
    for item in items:
        if not isinstance(item, dict) or not str(item.get("description", "")).strip():
            continue  # entri tanpa deskripsi diabaikan
        predictions.append({
            "description": str(item["description"]).strip(),
            "setup_unit": to_unit(item.get("setup_unit"), n_units),
            "violation_unit": to_unit(item.get("violation_unit"), n_units),
            "evidence_quote": str(item.get("evidence_quote") or "").strip(),
        })
    return predictions