"""Hash SHA-256 sebagai bukti bahwa data hasil scraping identik dari waktu ke waktu."""
import hashlib
from pathlib import Path

import pandas as pd

HASH_COLUMNS = ("screenplay_sha256", "gt_sha256")


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def update_checksums(results: list[dict], path: Path) -> None:
    new = pd.DataFrame(results)
    if path.exists():
        old = pd.read_csv(path, dtype=str).set_index("film_id")
        for r in results:
            if r["film_id"] in old.index:
                for col in HASH_COLUMNS:
                    if old.at[r["film_id"], col] != r[col]:
                        print(f"  [PERINGATAN] {r['film_id']}: {col} berbeda dari yang tercatat!")
        old = old.drop(index=[r["film_id"] for r in results], errors="ignore").reset_index()
        new = pd.concat([old, new])
    new.sort_values("film_id").to_csv(path, index=False)