"""Ekstraksi teks naskah dari halaman IMSDb."""
from bs4 import BeautifulSoup


def extract_screenplay(html: str) -> str:
    """Naskah ada di tag <pre> terpanjang (beberapa halaman punya lebih dari satu)."""
    pre_tags = BeautifulSoup(html, "lxml").find_all("pre")
    if not pre_tags:
        raise ValueError("Tidak ada tag <pre> di halaman IMSDb.")
    return max(pre_tags, key=lambda tag: len(tag.get_text())).get_text()