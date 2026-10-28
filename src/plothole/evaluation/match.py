"""Pencocokan prediksi dengan GT: satu-lawan-satu, optimal (algoritma Hungarian)."""
import numpy as np
from scipy.optimize import linear_sum_assignment


def assign(sim: np.ndarray, threshold: float) -> list[tuple[int, int, float]]:
    """
    Mengembalikan pasangan (indeks prediksi, indeks GT, skor) dengan skor >= threshold.

    Pasangan di bawah threshold dinolkan SEBELUM pencocokan, supaya algoritma
    hanya mengoptimalkan pasangan yang valid. Satu prediksi maksimal cocok dengan
    satu GT, dan sebaliknya.
    """
    if sim.size == 0:
        return []
    valid = np.where(sim >= threshold, sim, 0.0)
    rows, cols = linear_sum_assignment(-valid)  # Hungarian mencari MINIMUM, jadi skor dibalik
    return [(int(r), int(c), float(sim[r, c])) for r, c in zip(rows, cols) if sim[r, c] >= threshold]