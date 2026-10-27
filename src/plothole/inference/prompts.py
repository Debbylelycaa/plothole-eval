"""Menyusun pesan (messages) untuk setiap strategi prompting."""
import json


def load_processed(cfg: dict, film_id: str) -> tuple[str, list[dict]]:
    film_dir = cfg["paths"]["processed"] / film_id
    text = (film_dir / "screenplay_clean.txt").read_text(encoding="utf-8")
    units = json.loads((film_dir / "units.json").read_text(encoding="utf-8"))["units"]
    return text, units


def format_units(text: str, units: list[dict]) -> str:
    """Naskah dengan penanda [UNIT n] di awal setiap unit."""
    return "\n\n".join(
        f"[UNIT {u['unit_id']}]\n{text[u['start_char']:u['end_char']].strip()}" for u in units
    )


def fill(template: str, **values) -> str:
    for key, value in values.items():
        template = template.replace("{" + key + "}", str(value))
    return template


def load_template(cfg: dict, name: str) -> str:
    return (cfg["paths"]["prompts"] / f"{name}.txt").read_text(encoding="utf-8")


def build_messages(cfg: dict, strategy: str, film_id: str) -> list[tuple[str, list[dict]]]:
    """
    Mengembalikan daftar (part, messages).
    zero_shot / cot -> 1 bagian ("full"); chunking -> 1 bagian per babak ("act1", "act2", ...).
    """
    text, units = load_processed(cfg, film_id)
    system = {"role": "system", "content": load_template(cfg, "system")}

    if strategy in ("zero_shot", "cot"):
        user = fill(load_template(cfg, strategy),
                    screenplay=format_units(text, units), n_units=len(units))
        return [("full", [system, {"role": "user", "content": user}])]

    if strategy == "chunking":
        n_acts = len(cfg["preprocessing"]["acts"])
        parts = []
        for act in range(1, n_acts + 1):
            act_units = [u for u in units if u["act"] == act]
            user = fill(load_template(cfg, "chunking"),
                        screenplay=format_units(text, act_units),
                        n_units=len(act_units), part=act, n_parts=n_acts)
            parts.append((f"act{act}", [system, {"role": "user", "content": user}]))
        return parts

    raise ValueError(f"Strategi tidak dikenal: {strategy}")