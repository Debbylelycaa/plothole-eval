import numpy as np

from plothole.evaluation.match import assign


def test_satu_lawan_satu_dan_threshold():
    sim = np.array([
        [0.9, 0.2],
        [0.8, 0.3],   # prediksi kedua juga mirip GT 0, tapi GT 0 sudah diambil prediksi pertama
    ])
    pairs = assign(sim, threshold=0.5)
    assert [(r, c) for r, c, _ in pairs] == [(0, 0)]   # (1,1) di bawah threshold -> tidak cocok


def test_pasangan_di_bawah_threshold_tidak_memboroskan_gt():
    sim = np.array([
        [0.90, 0.55],
        [0.52, 0.45],
    ])
    # Tanpa dinolkan dulu: Hungarian memilih (0,0)+(1,1)=1.35, lalu (1,1) dibuang -> hanya 1 cocok.
    # Dengan dinolkan dulu: (0,1)+(1,0) = 1.07 adalah kombinasi valid terbaik -> 2 cocok.
    pairs = assign(sim, threshold=0.5)
    assert sorted((r, c) for r, c, _ in pairs) == [(0, 1), (1, 0)]


def test_kosong():
    assert assign(np.zeros((0, 3)), 0.5) == []