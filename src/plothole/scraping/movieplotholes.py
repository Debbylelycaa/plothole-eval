"""Ekstraksi daftar plot hole dari halaman arsip movieplotholes."""
import re

from bs4 import BeautifulSoup

PATTERN = re.compile(
    r"^(Major Plot Hole|Minor Plot Hole|Super Plot Hole|Unaddressed Issue|Plot Contrivance)\s*:\s*(.*)",
    re.IGNORECASE,
)

def parse_plot_holes(html: str, film_id: str) -> list[dict]:
    article = BeautifulSoup(html, "lxml").find("article")
    if article is None:
        raise ValueError("Tag <article> tidak ditemukan di halaman arsip.")

    entries, current = [], None
    for p in article.find_all("p"):
        text = re.sub(r"\s+", " ", p.get_text(" ", strip=True))
        if not text:
            continue
        match = PATTERN.match(text)
        if match:
            current = {
                "gt_id": f"{film_id}_gt{len(entries) + 1:02d}",
                "category": match.group(1).title(),
                "description": match.group(2).strip(),
            }
            entries.append(current)
        elif current is not None:
            current["description"] += "\n\n" + text  # paragraf lanjutan entri sebelumnya
    return entries