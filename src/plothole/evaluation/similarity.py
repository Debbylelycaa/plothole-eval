"""Kemiripan makna antar-deskripsi plot hole: sentence embedding + cosine similarity."""
from functools import lru_cache

import numpy as np


@lru_cache(maxsize=None)
def _load_model(name: str):
    # import di dalam fungsi: library ini berat, jadi hanya dimuat saat benar-benar dipakai
    from sentence_transformers import SentenceTransformer
    return SentenceTransformer(name)


def embed(texts: list[str], model_name: str) -> np.ndarray:
    # normalize_embeddings=True -> perkalian titik (dot product) = cosine similarity
    return _load_model(model_name).encode(list(texts), normalize_embeddings=True,
                                          show_progress_bar=False)


def similarity_matrix(pred_texts: list[str], gt_texts: list[str], model_name: str) -> np.ndarray:
    """Baris = prediksi, kolom = GT, isi = cosine similarity."""
    if not pred_texts or not gt_texts:
        return np.zeros((len(pred_texts), len(gt_texts)))
    return embed(pred_texts, model_name) @ embed(gt_texts, model_name).T