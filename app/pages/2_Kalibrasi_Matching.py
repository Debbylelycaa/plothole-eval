"""Penilaian manusia: apakah prediksi dan GT membahas plot hole yang sama? (untuk kalibrasi)"""
from datetime import datetime

import pandas as pd
import streamlit as st

from plothole.config import load_config
from plothole.evaluation.calibration import load_match_labels, review_path, save_match_label

st.set_page_config(page_title="Kalibrasi Matching", layout="wide")
cfg = load_config()

st.title("Kalibrasi Matching")
st.caption(
    "Nilai apakah prediksi model dan entri GT membahas plot hole yang SAMA. "
    "Skor kemiripan dan nama model sengaja disembunyikan, dan urutan diacak, "
    "agar penilaian tidak terpengaruh. Aturan penilaian: lihat docs/annotation_codebook.md."
)

path = review_path(cfg)
if not path.exists():
    st.warning("Belum ada pasangan. Jalankan dulu: python -m plothole match-review")
    st.stop()

pairs = pd.read_csv(path, keep_default_na=False).sample(frac=1, random_state=0)  # urutan acak tetap
labels = load_match_labels(cfg)
done = {(r.pred_id, r.gt_id): r.same for r in labels.itertuples()}
n_done = sum((p.pred_id, p.gt_id) in done for p in pairs.itertuples())
st.progress(n_done / len(pairs), text=f"{n_done}/{len(pairs)} pasangan dinilai")

for n, p in enumerate(pairs.itertuples(), start=1):
    key = (p.pred_id, p.gt_id)
    current = done.get(key)
    with st.container(border=True):
        st.markdown(f"**Pasangan {n}** {'✅' if current else '⬜'}")
        col1, col2 = st.columns(2)
        col1.markdown("**Prediksi model**")
        col1.write(p.prediction)
        col2.markdown("**Ground truth**")
        col2.write(p.ground_truth)
        choice = st.radio(
            "Membahas plot hole yang sama?", ["yes", "no"],
            index=["yes", "no"].index(current) if current in ("yes", "no") else None,
            horizontal=True, key=f"{p.pred_id}::{p.gt_id}",
        )
        if choice and choice != current:
            save_match_label(cfg, {
                "pred_id": p.pred_id, "gt_id": p.gt_id, "same": choice,
                "labeled_at": datetime.now().isoformat(timespec="seconds"),
            })
            done[key] = choice