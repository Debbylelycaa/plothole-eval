"""
Memotong naskah menjadi unit (scene atau blok) dan memberi label posisi & babak.

- Naskah dengan cukup scene heading -> dipotong per scene.
- Naskah tanpa heading (transkrip, format khusus) -> dipotong per blok ~N token
  di batas paragraf.
Setiap potongan adalah irisan persis dari teks: "".join(potongan) == teks.
"""
import re

from plothole.preprocessing.tokens import count_tokens

# Heading scene: opsional nomor scene di depan ("12", "12A"), lalu INT/EXT dan variannya.
# Contoh yang cocok: "INT. RUMAH", "EXT RUMAH", "12 INT. RUMAH", "INT./EXT. MOBIL", "I/E MOBIL"
HEADING = re.compile(
    r"^(?:\d+[A-Z]?\s+)?(?:INT\.?\s?/\s?EXT|EXT\.?\s?/\s?INT|I/E|INT|EXT)\b[.\s]",
    re.MULTILINE,
)


def split_by_headings(text: str) -> list[str]:
    starts = [m.start() for m in HEADING.finditer(text)]
    if not starts or starts[0] != 0:
        starts = [0] + starts  # bagian pembuka (judul, FADE IN) jadi unit pertama
    bounds = starts + [len(text)]
    return [text[a:b] for a, b in zip(bounds, bounds[1:]) if text[a:b].strip()]


def split_into_blocks(text: str, target_tokens: int, encoding: str) -> list[str]:
    # (?<=\n\n) = potong tepat SETELAH baris kosong, tanpa membuang karakter apa pun
    paragraphs = re.split(r"(?<=\n\n)", text)
    blocks, current, current_tokens = [], "", 0
    for p in paragraphs:
        n = count_tokens(p, encoding)
        if current and current_tokens + n > target_tokens:
            blocks.append(current)
            current, current_tokens = "", 0
        current += p
        current_tokens += n
    if current:
        blocks.append(current)
    return blocks


def assign_act(rel_position: float, proportions: list[float]) -> int:
    cumulative = 0.0
    for act, share in enumerate(proportions, start=1):
        cumulative += share
        if rel_position < cumulative:
            return act
    return len(proportions)


def build_units(text: str, pcfg: dict) -> tuple[str, list[dict]]:
    enc = pcfg["tokenizer"]
    if len(HEADING.findall(text)) >= pcfg["min_scene_headings"]:
        method, pieces = "scene", split_by_headings(text)
    else:
        method, pieces = "block", split_into_blocks(text, pcfg["block_target_tokens"], enc)

    units, char_pos, tok_pos = [], 0, 0
    for i, piece in enumerate(pieces, start=1):
        n_tok = count_tokens(piece, enc)
        units.append({
            "unit_id": i,
            "heading": piece.strip().split("\n", 1)[0][:80],
            "start_char": char_pos,
            "end_char": char_pos + len(piece),
            "start_token": tok_pos,
            "token_count": n_tok,
        })
        char_pos += len(piece)
        tok_pos += n_tok

    for u in units:
        mid = (u["start_token"] + u["token_count"] / 2) / tok_pos
        u["rel_position"] = round(mid, 4)
        u["act"] = assign_act(mid, pcfg["acts"])
    return method, units