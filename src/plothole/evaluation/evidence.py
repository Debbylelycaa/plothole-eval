"""Verifikasi kutipan bukti: apakah kutipan model benar-benar ada di naskah?"""
import re

from rapidfuzz import fuzz


def normalize(text: str) -> str:
    """Semua whitespace (spasi, tab, baris baru) -> satu spasi; huruf kecil."""
    return re.sub(r"\s+", " ", text).strip().lower()


def verify_quote(quote: str, normalized_screenplay: str, fuzzy_threshold: int) -> str:
    """'exact' | 'fuzzy' | 'not_found' | 'empty'"""
    q = normalize(quote)
    if not q:
        return "empty"
    if q in normalized_screenplay:
        return "exact"
    if fuzz.partial_ratio(q, normalized_screenplay) >= fuzzy_threshold:
        return "fuzzy"
    return "not_found"