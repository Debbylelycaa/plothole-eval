"""Command-line interface: python -m plothole <perintah>"""
import argparse
import os
from pathlib import Path

from dotenv import load_dotenv

from plothole.config import DEFAULT_CONFIG, PROJECT_ROOT, load_config

API_KEYS = ["OPENAI_API_KEY", "GEMINI_API_KEY", "GROQ_API_KEY"] 

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


def main() -> None:
    parser = argparse.ArgumentParser(prog="plothole")
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("info", help="cek konfigurasi dan setup")

    args = parser.parse_args()
    cfg = load_config(args.config)

    if args.command == "info":
        cmd_info(cfg)


if __name__ == "__main__":
    main()