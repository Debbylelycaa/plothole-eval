from plothole.preprocessing.clean import clean_screenplay, restore_line_breaks, word_count
from plothole.preprocessing.segment import assign_act, build_units, split_by_headings

PCFG = {
    "tokenizer": "o200k_base",
    "restore_lines_if_avg_line_over": 500,
    "restore_lines_space_gap": 4,
    "min_scene_headings": 3,
    "block_target_tokens": 50,
    "acts": [0.25, 0.50, 0.25],
}

NASKAH = (
    "JUDUL FILM\n\nFADE IN:\n\n"
    "INT. RUMAH - MALAM\nBudi masuk.\n\n"
    "12 EXT. JALAN - PAGI\nMobil lewat.\n\n"
    "INT./EXT. MOBIL - SIANG\nAni menyetir.\n\n"
    "EXT TAMAN - SORE\nBurung terbang.\n"
)


# ---------- cleaning ----------

def test_cleaning_tidak_mengubah_kata():
    raw = "      INT. RUMAH  -  MALAM\n\n\n\n\t  BUDI\n      Halo   semua.\xa0Apa kabar?  \n"
    clean = clean_screenplay(raw, PCFG)
    assert word_count(clean) == word_count(raw)
    assert clean == "INT. RUMAH - MALAM\n\nBUDI\nHalo semua. Apa kabar?"


def test_restore_line_breaks_untuk_naskah_satu_baris():
    satu_baris = "FADE IN:        INT. KAMAR - PAGI        Jam berbunyi.  Budi bangun." * 20
    hasil = restore_line_breaks(satu_baris, 500, 4)
    assert "\nINT. KAMAR - PAGI\n" in hasil
    assert "Jam berbunyi.  Budi bangun." in hasil  # 2 spasi biasa tidak dianggap batas baris


def test_restore_line_breaks_naskah_normal_tidak_diubah():
    normal = "INT. KAMAR - PAGI\n        Budi bangun.\n" * 50
    assert restore_line_breaks(normal, 500, 4) == normal


# ---------- segmentasi ----------

def test_heading_berbagai_format_terdeteksi():
    pieces = split_by_headings(NASKAH)
    headings = [p.split("\n", 1)[0] for p in pieces]
    assert headings == [
        "JUDUL FILM",                # pembuka ikut jadi unit
        "INT. RUMAH - MALAM",
        "12 EXT. JALAN - PAGI",      # bernomor
        "INT./EXT. MOBIL - SIANG",   # gabungan
        "EXT TAMAN - SORE",          # tanpa titik
    ]


def test_unit_menyusun_ulang_teks_persis():
    method, units = build_units(NASKAH, PCFG)
    assert method == "scene"
    rebuilt = "".join(NASKAH[u["start_char"]:u["end_char"]] for u in units)
    assert rebuilt == NASKAH


def test_naskah_tanpa_heading_pakai_blok():
    transkrip = "\n\n".join(f"Paragraf ke-{i}. Tokoh berbicara panjang lebar." for i in range(40))
    method, units = build_units(transkrip, PCFG)
    assert method == "block"
    assert len(units) > 1
    assert "".join(transkrip[u["start_char"]:u["end_char"]] for u in units) == transkrip


def test_posisi_dan_babak():
    _, units = build_units(NASKAH, PCFG)
    posisi = [u["rel_position"] for u in units]
    assert posisi == sorted(posisi) and 0 < posisi[0] and posisi[-1] < 1
    assert units[0]["act"] == 1 and units[-1]["act"] == 3


def test_assign_act_batas():
    acts = [0.25, 0.50, 0.25]
    assert [assign_act(p, acts) for p in (0.0, 0.24, 0.25, 0.74, 0.75, 1.0)] == [1, 1, 2, 2, 3, 3]