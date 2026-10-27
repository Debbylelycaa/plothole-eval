"""Command-line interface: python -m plothole <perintah>"""
import argparse
import os
from pathlib import Path

import pandas as pd
from dotenv import load_dotenv

from plothole.config import DEFAULT_CONFIG, PROJECT_ROOT, load_config
from plothole.manifest import films_csv_path, load_films
from plothole.preprocessing.pipeline import preprocess_film
from plothole.scraping.checksums import update_checksums
from plothole.scraping.pipeline import scrape_film
from plothole.scraping.wayback import find_snapshot, raw_snapshot_url

API_KEYS = ["OPENAI_API_KEY", "GEMINI_API_KEY", "GROQ_API_KEY"]  # disesuaikan di Fase 4


def cmd_info(cfg: dict) -> None:
    """Mengecek apakah setup sudah benar (config, folder, API key)."""
    exp = cfg["experiment"]
    print(f"Eksperimen : {exp['name']}")
    print(f"Strategi   : {', '.join(exp['strategies'])}")
    print(f"Mode GT    : {cfg['dataset']['gt_mode']}")

    print("\nFolder:")
    for name, path in cfg["paths"].items():
        status = "ok" if path.exists() else "TIDAK ADA"
        print(f"  [{status:^9}] {name:<10} {path}")

    load_dotenv(PROJECT_ROOT / ".env")
    print("\nAPI key (.env):")
    for key in API_KEYS:
        print(f"  [{'ada' if os.getenv(key) else 'kosong':^6}] {key}")


def cmd_find_snapshots(cfg: dict) -> None:
    """Mengisi wayback_timestamp yang masih kosong di films.csv."""
    films = load_films(cfg, include_excluded=True)
    for i, row in films.iterrows():
        if row["status"] == "excluded" or row["wayback_timestamp"] or not row["mph_url"]:
            continue
        ts = find_snapshot(row["mph_url"], cfg["scraping"])
        if ts:
            films.at[i, "wayback_timestamp"] = ts
            print(f"[ketemu]    {row['film_id']}: {raw_snapshot_url(row['mph_url'], ts)}")
        else:
            print(f"[tidak ada] {row['film_id']}")
    films.to_csv(films_csv_path(cfg), index=False)


def cmd_scrape(cfg: dict) -> None:
    """Mengunduh naskah + GT untuk semua film yang tidak excluded."""
    films = load_films(cfg)
    films = films[films["wayback_timestamp"] != ""]
    min_gt = cfg["dataset"]["min_gt_per_film"]

    results = []
    for _, row in films.iterrows():
        try:
            info = scrape_film(row, cfg)
            results.append(info)
            flag = "" if info["gt_count"] >= min_gt else f"   <-- GT < {min_gt}"
            print(f"[ok]    {info['film_id']}: {info['screenplay_chars']:,} karakter, "
                  f"{info['gt_count']} GT{flag}")
        except Exception as e:
            print(f"[GAGAL] {row['film_id']}: {e}")

    if results:  # kalau semua film gagal, jangan tulis checksums kosong
        update_checksums(results, cfg["paths"]["manifest"] / "checksums.csv")


def cmd_preprocess(cfg: dict) -> None:
    """Cleaning + segmentasi semua film, lalu simpan statistik dataset."""
    rows = []
    for film_id in load_films(cfg)["film_id"]:
        try:
            s = preprocess_film(film_id, cfg)
            rows.append(s)
            print(f"[ok]    {film_id}: {s['tokens']:,} token, {s['units']} unit ({s['segmentation']})")
        except Exception as e:
            print(f"[GAGAL] {film_id}: {e}")

    if rows:
        out = cfg["paths"]["results"] / "dataset_stats.csv"
        pd.DataFrame(rows).to_csv(out, index=False)
        print(f"\nStatistik dataset disimpan di {out}")


def main() -> None:
    parser = argparse.ArgumentParser(prog="plothole")
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("info", help="cek konfigurasi dan setup")
    sub.add_parser("find-snapshots", help="cari snapshot Wayback untuk film yang belum punya")
    sub.add_parser("scrape", help="unduh naskah + GT semua film")
    sub.add_parser("preprocess", help="cleaning + segmentasi + statistik dataset")

    args = parser.parse_args()
    cfg = load_config(args.config)

    if args.command == "info":
        cmd_info(cfg)
    elif args.command == "find-snapshots":
        cmd_find_snapshots(cfg)
    elif args.command == "scrape":
        cmd_scrape(cfg)
    elif args.command == "preprocess":
        cmd_preprocess(cfg)


if __name__ == "__main__":
    main()