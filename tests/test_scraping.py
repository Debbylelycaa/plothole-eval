from plothole.scraping.checksums import sha256_text
from plothole.scraping.imsdb import extract_screenplay
from plothole.scraping.movieplotholes import parse_plot_holes

MPH_HTML = """<html><body><article>
<p>Pengantar artikel.</p>
<p>Major Plot Hole: Tokoh A tewas di awal.</p>
<p>Namun ia muncul lagi di akhir.</p>
<p>minor plot hole: Jam di dinding berubah.</p>
</article></body></html>"""


def test_parse_plot_holes():
    entries = parse_plot_holes(MPH_HTML, "film_x")
    assert [e["gt_id"] for e in entries] == ["film_x_gt01", "film_x_gt02"]
    assert entries[1]["category"] == "Minor Plot Hole"
    assert "muncul lagi" in entries[0]["description"]   # paragraf lanjutan ikut
    assert "Pengantar" not in entries[0]["description"]  # teks sebelum entri pertama diabaikan


def test_extract_screenplay_ambil_pre_terpanjang():
    html = "<pre>pendek</pre><pre>INT. RUMAH - MALAM\nIni naskah utuh.</pre>"
    assert extract_screenplay(html).startswith("INT. RUMAH")


def test_hash_deterministik():
    assert sha256_text("abc") == sha256_text("abc") != sha256_text("abd")