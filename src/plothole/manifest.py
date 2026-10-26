"""Membaca manifest film."""
import pandas as pd


def films_csv_path(cfg: dict):
    return cfg["paths"]["manifest"] / cfg["dataset"]["films_csv"]


def load_films(cfg: dict, include_excluded: bool = False) -> pd.DataFrame:
    # dtype=str: timestamp tetap teks; keep_default_na=False: sel kosong jadi "" bukan NaN
    df = pd.read_csv(films_csv_path(cfg), dtype=str, keep_default_na=False)
    if not include_excluded:
        df = df[df["status"] != "excluded"]
    return df