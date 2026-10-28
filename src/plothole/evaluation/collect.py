"""Membaca semua output model, mem-parsing, dan memverifikasi kutipan."""
import json

import pandas as pd

from plothole.evaluation.evidence import normalize, verify_quote
from plothole.evaluation.parse import extract_json, parse_predictions
from plothole.inference.prompts import load_processed

KEY = ("model", "strategy", "film_id", "run", "part")


def collect_predictions(cfg: dict, films=None) -> tuple[list[dict], list[dict]]:
    """Mengembalikan (daftar prediksi, daftar statistik per panggilan). Hanya output status 'ok'."""
    root = cfg["paths"]["outputs"] / cfg["experiment"]["name"]
    threshold = cfg["evaluation"]["quote_fuzzy_threshold"]
    predictions, calls, screenplays = [], [], {}

    for path in sorted(root.glob("*/*/*/run*_*.json")):
        rec = json.loads(path.read_text(encoding="utf-8"))
        if rec["status"] != "ok" or (films and rec["film_id"] not in films):
            continue

        film_id = rec["film_id"]
        if film_id not in screenplays:  # naskah cukup dibaca sekali per film
            text, units = load_processed(cfg, film_id)
            screenplays[film_id] = (normalize(text), len(units))
        norm_text, n_units = screenplays[film_id]

        obj, fmt = extract_json(rec["content"])
        items = parse_predictions(obj, n_units)
        key = {k: rec[k] for k in KEY}
        calls.append({
            **key,
            "format": fmt,
            "has_analysis": isinstance(obj, dict) and bool(str(obj.get("analysis", "")).strip()),
            "finish_reason": rec["finish_reason"],
            "n_predictions": len(items),
        })
        for i, p in enumerate(items, start=1):
            predictions.append({
                **key,
                "pred_id": f"{rec['model']}|{rec['strategy']}|{film_id}|run{rec['run']}|{rec['part']}|{i}",
                **p,
                "evidence": verify_quote(p["evidence_quote"], norm_text, threshold),
            })
    return predictions, calls


def summarize(predictions: list[dict], calls: list[dict]) -> pd.DataFrame:
    """Statistik per model x strategi: kepatuhan format, kepatuhan CoT, verifikasi kutipan."""
    c = pd.DataFrame(calls)
    g = c.groupby(["model", "strategy"])
    summary = pd.DataFrame({
        "calls": g.size(),
        "format_clean": g["format"].apply(lambda s: (s == "clean").mean()),
        "format_extracted": g["format"].apply(lambda s: (s == "extracted").mean()),
        "format_broken": g["format"].apply(lambda s: (s == "broken").mean()),
        "truncated": g["finish_reason"].apply(lambda s: (s == "length").mean()),
        "analysis_rate": g["has_analysis"].mean(),
        "predictions": g["n_predictions"].sum(),
    })
    if predictions:
        p = pd.DataFrame(predictions)
        quotes = (p.groupby(["model", "strategy"])["evidence"]
                  .value_counts(normalize=True).unstack(fill_value=0))
        summary = summary.join(quotes.add_prefix("quote_"))
    # kolom quote_* sengaja dibiarkan kosong (NaN) jika model tidak menghasilkan prediksi:
    # "tidak ada kutipan untuk dinilai" berbeda dengan "0% kutipan valid"
    return summary.round(3).reset_index()