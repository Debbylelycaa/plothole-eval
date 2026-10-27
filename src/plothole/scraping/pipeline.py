"""Scraping satu film: naskah IMSDb + GT movieplotholes (via Wayback)."""
import json

from plothole.scraping.checksums import sha256_text
from plothole.scraping.fetch import fetch_cached
from plothole.scraping.imsdb import extract_screenplay
from plothole.scraping.movieplotholes import parse_plot_holes
from plothole.scraping.wayback import raw_snapshot_url


def scrape_film(row, cfg: dict) -> dict:
    fid, scfg = row["film_id"], cfg["scraping"]
    raw_dir = cfg["paths"]["raw"]
    out_dir = cfg["paths"]["processed"] / fid
    out_dir.mkdir(parents=True, exist_ok=True)

    html = fetch_cached(row["imsdb_url"], raw_dir / "imsdb" / f"{fid}.html", scfg)
    screenplay = extract_screenplay(html)
    (out_dir / "screenplay_raw.txt").write_text(screenplay, encoding="utf-8", newline="\n")

    snapshot = raw_snapshot_url(row["mph_url"], row["wayback_timestamp"])
    html = fetch_cached(snapshot, raw_dir / "mph" / f"{fid}.html", scfg)
    entries = parse_plot_holes(html, fid)
    gt_json = json.dumps(entries, indent=2, ensure_ascii=False)
    (out_dir / "gt_raw.json").write_text(gt_json, encoding="utf-8", newline="\n")

    return {
        "film_id": fid,
        "screenplay_chars": len(screenplay),
        "gt_count": len(entries),
        "screenplay_sha256": sha256_text(screenplay),
        "gt_sha256": sha256_text(gt_json),
    }