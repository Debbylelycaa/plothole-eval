"""Ekstraksi teks naskah dari halaman IMSDb."""
from bs4 import BeautifulSoup

# Naskah film utuh selalu jauh di atas ini (rata-rata 100-300 ribu karakter).
# Kalau hasil ekstraksi lebih pendek, hampir pasti halamannya kosong atau salah.
MIN_CHARS = 10_000


def extract_screenplay(html: str) -> str:
    """
    Mengambil teks naskah dari halaman IMSDb.

    Format halaman IMSDb tidak seragam:
    1. Sebagian besar naskah ada di dalam tag <pre> (ambil yang terpanjang).
    2. Sebagian lain langsung di <td class="scrtext"> tanpa <pre>.
    """
    soup = BeautifulSoup(html, "lxml")

    # Cara 1: tag <pre> terpanjang
    pre_tags = soup.find_all("pre")
    if pre_tags:
        text = max(pre_tags, key=lambda tag: len(tag.get_text())).get_text()
        if len(text.strip()) >= MIN_CHARS:
            return text

    # Cara 2: isi <td class="scrtext">, tanpa tabel info (penulis, genre) di bagian bawah
    td = soup.find("td", class_="scrtext")
    if td is not None:
        for table in td.find_all("table"):
            table.decompose()
        text = td.get_text()
        if len(text.strip()) >= MIN_CHARS:
            return text

    raise ValueError(f"Naskah tidak ditemukan atau lebih pendek dari {MIN_CHARS:,} karakter.")