"""Halaman anotasi GT: label include/exclude, tipe, dan posisi unit di naskah."""
import json
from datetime import datetime

import streamlit as st

from plothole.annotations import EXCLUDE_CODES, PH_TYPES, load_annotations, save_annotation
from plothole.config import load_config
from plothole.gt import load_gt_raw
from plothole.manifest import load_films
from plothole.scraping.checksums import sha256_text

st.set_page_config(page_title="Anotasi GT", layout="wide")
cfg = load_config()


@st.cache_data
def load_screenplay(film_id: str):
    film_dir = cfg["paths"]["processed"] / film_id
    text = (film_dir / "screenplay_clean.txt").read_text(encoding="utf-8")
    units = json.loads((film_dir / "units.json").read_text(encoding="utf-8"))["units"]
    return text, units


# ---------- sidebar: pilih putaran & film ----------
st.sidebar.header("Pengaturan")
round_no = st.sidebar.radio(
    "Putaran anotasi", [1, 2],
    help="Putaran 2 = uji konsistensi. Jawaban putaran 1 tidak ditampilkan.",
)
film_id = st.sidebar.selectbox("Film", load_films(cfg)["film_id"])

entries = load_gt_raw(cfg, film_id)
ann = load_annotations(cfg, round_no).set_index("gt_id")
text, units = load_screenplay(film_id)

done = sum(e["gt_id"] in ann.index for e in entries)
st.sidebar.progress(done / len(entries), text=f"{done}/{len(entries)} entri teranotasi")

# ---------- sidebar: alat bantu mencari posisi ----------
with st.sidebar.expander("🔎 Cari kata di naskah"):
    query = st.text_input("Kata kunci (nama tokoh, benda, tempat)")
    if query:
        q = query.lower()
        hits = [u for u in units if q in text[u["start_char"]:u["end_char"]].lower()]
        st.caption(f"{len(hits)} unit cocok")
        for u in hits[:30]:
            seg = text[u["start_char"]:u["end_char"]]
            i = seg.lower().find(q)
            st.markdown(f"**Unit {u['unit_id']}** · {u['heading']}  \n…{seg[max(0, i - 80):i + 150]}…")

with st.sidebar.expander("📖 Baca satu unit"):
    unit_no = st.number_input("Nomor unit", min_value=1, max_value=len(units), value=1)
    u = units[unit_no - 1]
    st.caption(f"{u['heading']} · posisi {u['rel_position']:.0%} · babak {u['act']}")
    st.text(text[u["start_char"]:u["end_char"]])

# ---------- konten utama ----------
st.title("Anotasi Ground Truth")
st.caption(f"Putaran {round_no} · {film_id} · {len(units)} unit · lihat docs/annotation_codebook.md")

gt_id = st.selectbox(
    "Entri GT", [e["gt_id"] for e in entries],
    format_func=lambda g: f"{'✅' if g in ann.index else '⬜'} {g}",
)
entry = next(e for e in entries if e["gt_id"] == gt_id)
prev = ann.loc[gt_id].to_dict() if gt_id in ann.index else {}

st.subheader(entry["category"])
st.write(entry["description"])
st.divider()


def index_of(options, value):
    return options.index(value) if value in options else None


with st.form(f"form_{round_no}_{gt_id}"):
    include = st.radio(
        "Layak dipakai sebagai GT?", ["yes", "no"],
        index=index_of(["yes", "no"], prev.get("include")), horizontal=True,
    )
    col1, col2 = st.columns(2)
    type_opts = [""] + list(PH_TYPES)
    ph_type = col1.selectbox(
        "Tipe (jika yes)", type_opts, index=index_of(type_opts, prev.get("ph_type", "")),
        format_func=lambda c: f"{c} – {PH_TYPES[c]}" if c else "—",
    )
    code_opts = [""] + list(EXCLUDE_CODES)
    exclude_code = col2.selectbox(
        "Kode eksklusi (jika no)", code_opts, index=index_of(code_opts, prev.get("exclude_code", "")),
        format_func=lambda c: f"{c} – {EXCLUDE_CODES[c]}" if c else "—",
    )

    setup_unit = violation_unit = ""
    if round_no == 1:  # posisi cukup diisi sekali, di putaran 1
        col3, col4 = st.columns(2)
        setup_unit = col3.text_input("setup_unit (opsional)", prev.get("setup_unit", ""))
        violation_unit = col4.text_input("violation_unit", prev.get("violation_unit", ""))

    notes = st.text_area("Catatan", prev.get("notes", ""))
    submitted = st.form_submit_button("Simpan", type="primary")

if submitted:
    errors = []
    if include is None:
        errors.append("Pilih yes atau no.")
    if include == "yes" and not ph_type:
        errors.append("Entri 'yes' wajib punya tipe.")
    if include == "no" and not exclude_code:
        errors.append("Entri 'no' wajib punya kode eksklusi.")
    for name, val in (("setup_unit", setup_unit), ("violation_unit", violation_unit)):
        if val and not (val.isdigit() and 1 <= int(val) <= len(units)):
            errors.append(f"{name} harus nomor unit 1–{len(units)}.")

    if errors:
        for err in errors:
            st.error(err)
    else:
        is_yes = include == "yes"
        save_annotation(cfg, {
            "gt_id": gt_id,
            "film_id": film_id,
            "desc_sha256": sha256_text(entry["description"]),
            "include": include,
            "exclude_code": "" if is_yes else exclude_code,
            "ph_type": ph_type if is_yes else "",
            "setup_unit": setup_unit if is_yes else "",
            "violation_unit": violation_unit if is_yes else "",
            "notes": notes,
            "annotated_at": datetime.now().isoformat(timespec="seconds"),
        }, round_no)
        st.rerun()