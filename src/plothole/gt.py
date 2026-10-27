"""Memuat ground truth untuk evaluasi: mentah (raw) atau hasil kurasi (curated)."""
import json

from plothole.annotations import load_annotations
from plothole.scraping.checksums import sha256_text


def load_gt_raw(cfg: dict, film_id: str) -> list[dict]:
    path = cfg["paths"]["processed"] / film_id / "gt_raw.json"
    return json.loads(path.read_text(encoding="utf-8"))


def load_gt(cfg: dict, film_id: str, mode: str | None = None) -> list[dict]:
    """
    mode 'raw'     -> semua entri hasil scraping
    mode 'curated' -> hanya entri include == 'yes', plus tipe dan posisinya
    Default mengikuti cfg['dataset']['gt_mode'].
    """
    mode = mode or cfg["dataset"]["gt_mode"]
    entries = load_gt_raw(cfg, film_id)
    if mode == "raw":
        return entries

    ann = load_annotations(cfg).set_index("gt_id")
    curated = []
    for e in entries:
        if e["gt_id"] not in ann.index:
            raise ValueError(f"{e['gt_id']} belum dianotasi.")
        a = ann.loc[e["gt_id"]]
        if a["desc_sha256"] != sha256_text(e["description"]):
            raise ValueError(f"{e['gt_id']}: deskripsi GT berubah sejak dianotasi, cek ulang.")
        if a["include"] == "yes":
            curated.append({
                **e,
                "ph_type": a["ph_type"],
                "setup_unit": a["setup_unit"],
                "violation_unit": a["violation_unit"],
            })
    return curated