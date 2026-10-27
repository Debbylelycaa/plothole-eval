import pytest

from plothole.config import load_config
from plothole.inference.prompts import build_messages, load_processed

CFG = load_config()
FILM = "the_village"
pytestmark = pytest.mark.skipif(
    not (CFG["paths"]["processed"] / FILM / "units.json").exists(),
    reason="data film belum ada (jalankan scrape + preprocess dulu)",
)


def test_zero_shot_satu_bagian_berisi_semua_unit():
    _, units = load_processed(CFG, FILM)
    [(part, messages)] = build_messages(CFG, "zero_shot", FILM)
    user = messages[1]["content"]
    assert part == "full"
    assert f"[UNIT 1]\n" in user and f"[UNIT {len(units)}]\n" in user
    assert "{screenplay}" not in user and "{n_units}" not in user


def test_cot_berbeda_dari_zero_shot():
    [(_, zs)] = build_messages(CFG, "zero_shot", FILM)
    [(_, cot)] = build_messages(CFG, "cot", FILM)
    assert '"analysis"' in cot[1]["content"] and '"analysis"' not in zs[1]["content"]
    assert zs[0] == cot[0]  # system prompt sama persis


def test_chunking_tiga_bagian_tanpa_tumpang_tindih():
    _, units = load_processed(CFG, FILM)
    parts = build_messages(CFG, "chunking", FILM)
    assert [p for p, _ in parts] == ["act1", "act2", "act3"]
    seen = [u["unit_id"] for u in units if f"[UNIT {u['unit_id']}]\n" in parts[0][1][1]["content"]]
    assert seen and all(u["act"] == 1 for u in units if u["unit_id"] in seen)
    total = sum(m[1]["content"].count("[UNIT ") for _, m in parts)
    assert total == len(units)  # setiap unit muncul tepat sekali di salah satu babak