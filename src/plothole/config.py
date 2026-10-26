"""Memuat konfigurasi eksperimen. Semua path dihitung dari root project."""
from pathlib import Path

import yaml

# config.py -> plothole -> src -> ROOT  (up 3 level)
PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_CONFIG = PROJECT_ROOT / "configs" / "experiment.yaml"


def load_config(path: Path = DEFAULT_CONFIG) -> dict:
    with open(path, encoding="utf-8") as f:
        cfg = yaml.safe_load(f)
    cfg["paths"] = {name: PROJECT_ROOT / rel for name, rel in cfg["paths"].items()}
    return cfg