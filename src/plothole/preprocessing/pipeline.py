"""Preprocessing satu film: cleaning -> segmentasi -> simpan + statistik."""
import json

from plothole.preprocessing.clean import clean_screenplay, word_count
from plothole.preprocessing.segment import build_units


def preprocess_film(film_id: str, cfg: dict) -> dict:
    pcfg = cfg["preprocessing"]
    film_dir = cfg["paths"]["processed"] / film_id

    raw = (film_dir / "screenplay_raw.txt").read_text(encoding="utf-8")
    clean = clean_screenplay(raw, pcfg)
    if word_count(raw) != word_count(clean):
        raise ValueError(
            f"Cleaning mengubah jumlah kata ({word_count(raw)} -> {word_count(clean)})."
        )

    method, units = build_units(clean, pcfg)
    (film_dir / "screenplay_clean.txt").write_text(clean, encoding="utf-8", newline="\n")
    units_json = json.dumps({"method": method, "units": units}, indent=2, ensure_ascii=False)
    (film_dir / "units.json").write_text(units_json, encoding="utf-8", newline="\n")

    n_acts = len(pcfg["acts"])
    act_tokens = {
        f"act{a}_tokens": sum(u["token_count"] for u in units if u["act"] == a)
        for a in range(1, n_acts + 1)
    }
    gt_raw = json.loads((film_dir / "gt_raw.json").read_text(encoding="utf-8"))

    return {
        "film_id": film_id,
        "chars_raw": len(raw),
        "chars_clean": len(clean),
        "words": word_count(clean),
        "tokens": sum(u["token_count"] for u in units),
        "segmentation": method,
        "units": len(units),
        **act_tokens,
        "gt_raw": len(gt_raw),
    }