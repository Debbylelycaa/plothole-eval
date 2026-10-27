from plothole.preprocessing.clean import clean_screenplay, restore_line_breaks, word_count

PCFG = {
    "tokenizer": "o200k_base",
    "restore_lines_if_avg_line_over": 500,
    "restore_lines_space_gap": 4,
    "min_scene_headings": 3,
    "block_target_tokens": 50,
    "acts": [0.25, 0.50, 0.25],
}


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