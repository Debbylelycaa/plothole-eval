"""
Penyimpanan anotasi GT + perhitungan kesepakatan (Cohen's kappa).

File CSV anotasi DI-COMMIT: isinya hanya ID, label, dan hash deskripsi,
bukan teks deskripsi (hak cipta movieplotholes).
"""
from pathlib import Path

import pandas as pd

COLUMNS = [
    "gt_id", "film_id", "desc_sha256", "include", "exclude_code", "ph_type",
    "setup_unit", "violation_unit", "notes", "annotated_at",
]

EXCLUDE_CODES = {
    "E1": "Realisme / pengetahuan di luar cerita",
    "E2": "Produksi, casting, akting, efek visual",
    "E3": "Tidak ada di versi naskah ini",
    "E4": "Opini / saran alternatif / nitpick",
    "E5": "Duplikat",
    "E6": "Dijelaskan atau disengaja di dalam cerita",
}

PH_TYPES = {
    "T1": "Kontradiksi fakta",
    "T2": "Pelanggaran aturan dunia",
    "T3": "Inkonsistensi waktu/urutan/lokasi",
    "T4": "Inkonsistensi motivasi/pengetahuan tokoh",
}


def annotations_path(cfg: dict, round_no: int = 1) -> Path:
    name = cfg["dataset"]["annotations_csv"]
    if round_no != 1:
        name = name.replace(".csv", f"_round{round_no}.csv")
    return cfg["paths"]["manifest"] / name


def load_annotations(cfg: dict, round_no: int = 1) -> pd.DataFrame:
    path = annotations_path(cfg, round_no)
    if not path.exists():
        return pd.DataFrame(columns=COLUMNS)
    return pd.read_csv(path, dtype=str, keep_default_na=False)


def save_annotation(cfg: dict, record: dict, round_no: int = 1) -> None:
    """Menyimpan satu anotasi. Kalau gt_id sudah ada, baris lamanya diganti."""
    df = load_annotations(cfg, round_no)
    df = df[df["gt_id"] != record["gt_id"]]
    df = pd.concat([df, pd.DataFrame([record])[COLUMNS]], ignore_index=True)
    df.sort_values("gt_id").to_csv(annotations_path(cfg, round_no), index=False)


def full_label(row) -> str:
    """Label lengkap: tipe untuk entri 'yes', kode eksklusi untuk entri 'no'."""
    return row["ph_type"] if row["include"] == "yes" else row["exclude_code"]


def cohen_kappa(a: list, b: list) -> float:
    """
    kappa = (po - pe) / (1 - pe)
    po = proporsi kesepakatan teramati
    pe = proporsi kesepakatan yang diharapkan terjadi kebetulan
    """
    n = len(a)
    po = sum(x == y for x, y in zip(a, b)) / n
    pe = sum((a.count(lab) / n) * (b.count(lab) / n) for lab in set(a) | set(b))
    return 1.0 if pe == 1 else (po - pe) / (1 - pe)