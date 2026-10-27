"""Menjalankan grid model x strategi x film x run, dengan resume otomatis."""
import json
from datetime import datetime

import pandas as pd
from dotenv import load_dotenv

from plothole.config import PROJECT_ROOT
from plothole.inference.client import call_model, make_client
from plothole.inference.prompts import build_messages
from plothole.manifest import load_films
from plothole.preprocessing.tokens import count_tokens
from plothole.scraping.checksums import sha256_text

LOG_COLUMNS = [
    "experiment", "model", "model_id", "model_returned", "strategy", "film_id", "part", "run",
    "status", "finish_reason", "prompt_tokens", "completion_tokens", "reasoning_tokens",
    "latency_s", "cost_usd", "prompt_sha256", "started_at", "error",
]


def output_path(cfg, model, strategy, film_id, run, part):
    exp = cfg["experiment"]["name"]
    return cfg["paths"]["outputs"] / exp / model / strategy / film_id / f"run{run}_{part}.json"


def already_done(path) -> bool:
    return path.exists() and json.loads(path.read_text(encoding="utf-8"))["status"] == "ok"


def append_log(cfg, record: dict) -> None:
    """Log berisi angka saja (tanpa teks naskah/respons) -> aman di-commit."""
    path = cfg["paths"]["results"] / "runs_log.csv"
    row = pd.DataFrame([{c: record.get(c) for c in LOG_COLUMNS}])
    row.to_csv(path, mode="a", header=not path.exists(), index=False)


def run_grid(cfg, models=None, strategies=None, films=None, dry_run=False) -> list[dict]:
    load_dotenv(PROJECT_ROOT / ".env")
    exp = cfg["experiment"]
    enc = cfg["preprocessing"]["tokenizer"]
    film_ids = films or list(load_films(cfg)["film_id"])
    planned, done, failed = [], 0, 0

    for mcfg in cfg["models"]:
        if models and mcfg["name"] not in models:
            continue
        client = None if dry_run else make_client(mcfg)

        for strategy in strategies or exp["strategies"]:
            for film_id in film_ids:
                for part, messages in build_messages(cfg, strategy, film_id):
                    prompt_hash = sha256_text(json.dumps(messages, ensure_ascii=False))

                    for run in range(1, exp["repeats"] + 1):
                        path = output_path(cfg, mcfg["name"], strategy, film_id, run, part)
                        if already_done(path):
                            continue

                        if dry_run:
                            n_in = sum(count_tokens(m["content"], enc) for m in messages)
                            planned.append({
                                "model": mcfg["name"], "strategy": strategy, "calls": 1,
                                "est_input_tokens": n_in,
                                "est_input_cost_usd": n_in * mcfg["price_per_mtok"]["input"] / 1e6,
                            })
                            continue

                        record = {
                            "experiment": exp["name"], "model": mcfg["name"],
                            "model_id": mcfg["model_id"], "params": mcfg.get("params", {}),
                            "strategy": strategy, "film_id": film_id, "part": part, "run": run,
                            "prompt_sha256": prompt_hash,
                            "started_at": datetime.now().isoformat(timespec="seconds"),
                        }
                        try:
                            record.update(call_model(client, mcfg, messages))
                            record["status"] = "ok"
                            done += 1
                        except Exception as e:
                            record.update(status="error", error=f"{type(e).__name__}: {e}")
                            failed += 1

                        path.parent.mkdir(parents=True, exist_ok=True)
                        path.write_text(json.dumps(record, indent=2, ensure_ascii=False),
                                        encoding="utf-8", newline="\n")
                        append_log(cfg, record)

                        tag = "ok" if record["status"] == "ok" else "GAGAL"
                        detail = (f"{record['prompt_tokens']:,}+{record['completion_tokens']:,} tok | "
                                  f"{record['latency_s']}s | ${record['cost_usd']:.4f}"
                                  if tag == "ok" else record["error"][:120])
                        print(f"[{tag}] {mcfg['name']} | {strategy} | {film_id} | {part} | run{run} | {detail}")

    if not dry_run:
        print(f"\nSelesai: {done} sukses, {failed} gagal (yang sudah sukses sebelumnya dilewati).")
    return planned