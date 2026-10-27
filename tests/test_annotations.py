import json

import pytest

from plothole.annotations import cohen_kappa, load_annotations, save_annotation
from plothole.gt import load_gt
from plothole.scraping.checksums import sha256_text


@pytest.fixture
def cfg(tmp_path):
    film_dir = tmp_path / "film_x"
    film_dir.mkdir()
    entries = [
        {"gt_id": "film_x_gt01", "category": "Major Plot Hole", "description": "A tewas lalu muncul."},
        {"gt_id": "film_x_gt02", "category": "Minor Plot Hole", "description": "Aktor terlalu tua."},
    ]
    (film_dir / "gt_raw.json").write_text(json.dumps(entries), encoding="utf-8")
    return {
        "paths": {"manifest": tmp_path, "processed": tmp_path},
        "dataset": {"annotations_csv": "gt_annotations.csv", "gt_mode": "curated"},
    }


def record(gt_id, include, desc, ph_type="", exclude_code=""):
    return {
        "gt_id": gt_id, "film_id": "film_x", "desc_sha256": sha256_text(desc),
        "include": include, "exclude_code": exclude_code, "ph_type": ph_type,
        "setup_unit": "3" if include == "yes" else "", "violation_unit": "9" if include == "yes" else "",
        "notes": "", "annotated_at": "2026-10-27T20:00:00",
    }


def test_simpan_ulang_mengganti_baris_lama(cfg):
    save_annotation(cfg, record("film_x_gt01", "no", "A tewas lalu muncul.", exclude_code="E4"))
    save_annotation(cfg, record("film_x_gt01", "yes", "A tewas lalu muncul.", ph_type="T1"))
    df = load_annotations(cfg)
    assert len(df) == 1 and df.iloc[0]["include"] == "yes"


def test_curated_hanya_yes(cfg):
    save_annotation(cfg, record("film_x_gt01", "yes", "A tewas lalu muncul.", ph_type="T1"))
    save_annotation(cfg, record("film_x_gt02", "no", "Aktor terlalu tua.", exclude_code="E2"))
    gt = load_gt(cfg, "film_x")
    assert [g["gt_id"] for g in gt] == ["film_x_gt01"]
    assert gt[0]["violation_unit"] == "9"
    assert len(load_gt(cfg, "film_x", mode="raw")) == 2


def test_curated_tolak_kalau_deskripsi_berubah(cfg):
    save_annotation(cfg, record("film_x_gt01", "yes", "TEKS LAMA", ph_type="T1"))
    save_annotation(cfg, record("film_x_gt02", "no", "Aktor terlalu tua.", exclude_code="E2"))
    with pytest.raises(ValueError, match="berubah"):
        load_gt(cfg, "film_x")


def test_curated_tolak_kalau_belum_dianotasi(cfg):
    with pytest.raises(ValueError, match="belum dianotasi"):
        load_gt(cfg, "film_x")


def test_kappa():
    assert cohen_kappa(["y", "n", "y", "n"], ["y", "n", "y", "n"]) == 1.0
    # contoh buku teks: po = 0.7, pe = 0.5 -> kappa = 0.4
    a = ["y"] * 5 + ["n"] * 5
    b = ["y"] * 4 + ["n"] + ["y"] * 2 + ["n"] * 3
    assert cohen_kappa(a, b) == pytest.approx(0.4)