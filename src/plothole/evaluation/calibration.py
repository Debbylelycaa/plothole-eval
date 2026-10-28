"""Kalibrasi threshold matching: pasangan untuk dinilai manusia dan penyimpanan labelnya."""
import pandas as pd

from plothole.evaluation.collect import collect_predictions
from plothole.evaluation.similarity import similarity_matrix
from plothole.gt import load_gt

LABEL_COLUMNS = ["pred_id", "gt_id", "same", "labeled_at"]


def review_path(cfg: dict):
    # berisi teks prediksi + GT -> disimpan lokal, TIDAK di-commit
    return cfg["paths"]["outputs"] / cfg["experiment"]["name"] / "match_review.csv"


def labels_path(cfg: dict):
    # hanya ID + label -> DI-COMMIT
    return cfg["paths"]["manifest"] / "match_labels.csv"


def load_match_labels(cfg: dict) -> pd.DataFrame:
    path = labels_path(cfg)
    if not path.exists():
        return pd.DataFrame(columns=LABEL_COLUMNS)
    return pd.read_csv(path, dtype=str, keep_default_na=False)


def save_match_label(cfg: dict, record: dict) -> None:
    df = load_match_labels(cfg)
    df = df[~((df["pred_id"] == record["pred_id"]) & (df["gt_id"] == record["gt_id"]))]
    df = pd.concat([df, pd.DataFrame([record])[LABEL_COLUMNS]], ignore_index=True)
    df.sort_values(["pred_id", "gt_id"]).to_csv(labels_path(cfg), index=False)


def build_review_pairs(cfg: dict, films: list[str]) -> pd.DataFrame:
    """Untuk tiap prediksi: GT paling mirip. Untuk tiap GT: prediksi paling mirip."""
    predictions, _ = collect_predictions(cfg, films=films)
    model_name = cfg["evaluation"]["embedding_model"]
    rows = []
    for film_id in films:
        gt = load_gt(cfg, film_id, mode="raw")
        preds = [p for p in predictions if p["film_id"] == film_id]
        if not preds or not gt:
            continue
        sim = similarity_matrix([p["description"] for p in preds],
                                [g["description"] for g in gt], model_name)
        pairs = {}
        for i in range(len(preds)):
            j = int(sim[i].argmax())
            pairs[(i, j)] = sim[i, j]
        for j in range(len(gt)):
            i = int(sim[:, j].argmax())
            pairs[(i, j)] = sim[i, j]
        for (i, j), score in pairs.items():
            rows.append({
                "pred_id": preds[i]["pred_id"],
                "gt_id": gt[j]["gt_id"],
                "similarity": round(float(score), 4),
                "prediction": preds[i]["description"],
                "ground_truth": gt[j]["description"],
            })
    return pd.DataFrame(rows)