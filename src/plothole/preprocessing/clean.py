"""Membersihkan naskah. Hanya spasi/baris yang diubah; kata tidak pernah diubah."""
import re


def restore_line_breaks(text: str, min_avg_line: int, gap: int) -> str:
    """
    Beberapa halaman IMSDb tidak punya baris baru sama sekali (contoh: Training Day):
    seluruh naskah menjadi satu baris, dan batas baris aslinya hanya tersisa
    sebagai deretan spasi panjang. Deretan itu dikembalikan menjadi baris baru.
    Naskah dengan panjang baris normal tidak diubah.
    """
    avg_line = len(text) / (text.count("\n") + 1)
    if avg_line < min_avg_line:
        return text
    return re.sub(rf" {{{gap},}}", "\n", text)


def clean_screenplay(text: str, pcfg: dict) -> str:
    text = restore_line_breaks(
        text, pcfg["restore_lines_if_avg_line_over"], pcfg["restore_lines_space_gap"]
    )
    text = text.replace("\t", " ").replace("\xa0", " ")  # tab & non-breaking space -> spasi
    lines = [re.sub(r" {2,}", " ", line.strip()) for line in text.split("\n")]
    text = "\n".join(lines)
    text = re.sub(r"\n{3,}", "\n\n", text)  # maksimal satu baris kosong
    return text.strip()


def word_count(text: str) -> int:
    return len(text.split())