from plothole.evaluation.evidence import normalize, verify_quote
from plothole.evaluation.parse import extract_json, parse_predictions, to_unit

NASKAH = normalize("ALICE\nHe was found in the river\ntwo days after he left.\n\nLUCIUS\nI understand.")


def test_json_bersih():
    obj, fmt = extract_json('{"plot_holes": []}')
    assert fmt == "clean" and obj == {"plot_holes": []}


def test_json_dalam_markdown():
    obj, fmt = extract_json('Berikut hasilnya:\n```json\n{"plot_holes": [{"description": "x"}]}\n```')
    assert fmt == "extracted" and len(obj["plot_holes"]) == 1


def test_json_rusak():
    assert extract_json('{"plot_holes": [ {"description": "terpotong...')[1] == "broken"
    assert extract_json(None)[1] == "broken"


def test_unit_tidak_valid_jadi_none():
    assert to_unit("12", 30) == 12
    assert to_unit(None, 30) is None
    assert to_unit(99, 30) is None      # di luar rentang
    assert to_unit("unit 5", 30) is None


def test_parse_lewati_entri_tanpa_deskripsi():
    obj = {"plot_holes": [{"description": "  "}, {"description": "Kontradiksi", "violation_unit": 3}]}
    preds = parse_predictions(obj, n_units=10)
    assert len(preds) == 1 and preds[0]["violation_unit"] == 3 and preds[0]["setup_unit"] is None


def test_kutipan_lintas_baris_tetap_exact():
    assert verify_quote("found in the river two days", NASKAH, 90) == "exact"


def test_kutipan_typo_kecil_fuzzy():
    assert verify_quote("He was found in the rivr two days after he left", NASKAH, 90) == "fuzzy"


def test_kutipan_karangan_not_found():
    assert verify_quote("The spaceship landed on the roof at midnight", NASKAH, 90) == "not_found"
    assert verify_quote("", NASKAH, 90) == "empty"