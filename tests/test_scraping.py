import pytest

from plothole.scraping.checksums import sha256_text
from plothole.scraping.fetch import fetch_cached
from plothole.scraping.imsdb import MIN_CHARS, extract_screenplay
from plothole.scraping.movieplotholes import parse_plot_holes

MPH_HTML = """<html><body><article>
<p>Pengantar artikel.</p>
<p>Major Plot Hole: Tokoh A tewas di awal.</p>
<p>Namun ia muncul lagi di akhir.</p>
<p>minor plot hole: Jam di dinding berubah.</p>
</article></body></html>"""

NASKAH = "INT. RUMAH - MALAM\n" + "Dialog tokoh.\n" * (MIN_CHARS // 10)


def test_parse_plot_holes():
    entries = parse_plot_holes(MPH_HTML, "film_x")
    assert [e["gt_id"] for e in entries] == ["film_x_gt01", "film_x_gt02"]
    assert entries[1]["category"] == "Minor Plot Hole"
    assert "muncul lagi" in entries[0]["description"]   # paragraf lanjutan ikut
    assert "Pengantar" not in entries[0]["description"]  # teks sebelum entri pertama diabaikan


def test_extract_screenplay_ambil_pre_terpanjang():
    html = f"<pre>pendek</pre><pre>{NASKAH}</pre>"
    assert extract_screenplay(html).startswith("INT. RUMAH")


def test_extract_screenplay_tanpa_pre_pakai_scrtext():
    html = f'<table><tr><td class="scrtext">{NASKAH}<table><tr><td>Writers: X</td></tr></table></td></tr></table>'
    text = extract_screenplay(html)
    assert "INT. RUMAH" in text
    assert "Writers" not in text  # tabel info dibuang


def test_extract_screenplay_kosong_gagal():
    html = '<td class="scrtext"><pre></pre><table><tr><td>Writers: X</td></tr></table></td>'
    with pytest.raises(ValueError):
        extract_screenplay(html)


def test_hash_deterministik():
    assert sha256_text("abc") == sha256_text("abc") != sha256_text("abd")


def test_cache_akhir_baris_diseragamkan(tmp_path):
    # tmp_path = folder sementara yang dibuat pytest, otomatis dihapus
    cache = tmp_path / "halaman.html"
    cache.write_bytes(b"baris1\r\nbaris2\rbaris3\n")
    # cache sudah ada, jadi tidak ada download; scfg tidak dipakai
    assert fetch_cached("http://tidak-dipakai", cache, {}) == "baris1\nbaris2\nbaris3\n"
    
def test_plot_contrivance_jadi_entri_sendiri():
    html = """<article>
    <p>Super Plot Hole: Tongkat ular bisa mengendalikan orang.</p>
    <p>Plot contrivance: Jasmine lama sekali mengenali Aladdin.</p>
    </article>"""
    entries = parse_plot_holes(html, "film_x")
    assert len(entries) == 2
    assert entries[1]["category"] == "Plot Contrivance"
    assert "Jasmine" not in entries[0]["description"]