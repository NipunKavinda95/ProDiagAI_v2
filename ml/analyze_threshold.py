from pathlib import Path
import joblib
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    confusion_matrix,
)

PROJECT_ROOT = Path(__file__).resolve().parent.parent

MODEL_PATH = PROJECT_ROOT / "ml" / "models" / "xgboost.joblib"
DATA_PATH = PROJECT_ROOT / "ProDiag_AI_V2_synthetic_predictive_maintenance_dataset.csv"
RESULT_DIR = PROJECT_ROOT / "ml" / "results"

RESULT_DIR.mkdir(parents=True, exist_ok=True)

TARGET = "failure_within_1h"

FEATURES = [
    "temperature_c",
    "vibration_mm_s",
    "current_a",
    "rpm",
    "load_factor",
    "temperature_c_delta",
    "vibration_mm_s_delta",
    "current_a_delta",
    "rpm_delta",
    "temperature_c_rolling_mean_10",
    "vibration_mm_s_rolling_mean_10",
    "current_a_rolling_mean_10",
    "rpm_rolling_mean_10",
    "equipment_type",
]

THRESHOLDS = [
    0.20,
    0.30,
    0.40,
    0.50,
    0.60,
    0.70,
    0.80,
]


def load_test_data():

    print("\nLoading dataset...")

    df = pd.read_csv(DATA_PATH)

    df["timestamp"] = pd.to_datetime(df["timestamp"], utc=True)

    df = df.sort_values(["timestamp", "machine_id"]).reset_index(drop=True)

    unique_timestamps = df["timestamp"].sort_values().unique()

    split_index = int(len(unique_timestamps) * 0.80)

    split_timestamp = unique_timestamps[split_index]

    test_df = df[df["timestamp"] >= split_timestamp].copy()

    X_test = test_df[FEATURES]

    y_test = test_df[TARGET]

    print(f"Test rows: {len(test_df):,}")

    return X_test, y_test


def evaluate_thresholds(probabilities, y_test):

    results = []

    print("\n" + "=" * 70)
    print("THRESHOLD ANALYSIS")
    print("=" * 70)

    for threshold in THRESHOLDS:

        predictions = (probabilities >= threshold).astype(int)

        tn, fp, fn, tp = confusion_matrix(y_test, predictions).ravel()

        accuracy = accuracy_score(y_test, predictions)

        precision = precision_score(y_test, predictions, zero_division=0)

        recall = recall_score(y_test, predictions, zero_division=0)

        f1 = f1_score(y_test, predictions, zero_division=0)

        results.append(
            {
                "threshold": threshold,
                "accuracy": accuracy,
                "precision": precision,
                "recall": recall,
                "f1": f1,
                "true_negatives": tn,
                "false_positives": fp,
                "false_negatives": fn,
                "true_positives": tp,
            }
        )

    results_df = pd.DataFrame(results)

    print(results_df.to_string(index=False, float_format=lambda x: f"{x:.4f}"))

    return results_df


def save_results(results_df):

    path = RESULT_DIR / "xgboost_threshold_analysis.csv"

    results_df.to_csv(path, index=False)

    print(f"\nSaved: {path}")


def create_threshold_plot(results_df):

    plt.figure(figsize=(10, 6))

    plt.plot(
        results_df["threshold"], results_df["precision"], marker="o", label="Precision"
    )

    plt.plot(results_df["threshold"], results_df["recall"], marker="o", label="Recall")

    plt.plot(results_df["threshold"], results_df["f1"], marker="o", label="F1")

    plt.xlabel("Classification Threshold")

    plt.ylabel("Score")

    plt.title("ProDiag AI V2 - XGBoost Threshold Analysis")

    plt.xticks(THRESHOLDS)

    plt.ylim(0.85, 1.01)

    plt.legend()

    plt.grid(alpha=0.3)

    plt.tight_layout()

    path = RESULT_DIR / "xgboost_threshold_analysis.png"

    plt.savefig(path, dpi=200, bbox_inches="tight")

    plt.close()

    print(f"Saved: {path}")


def save_error_analysis(results_df):

    best_row = results_df.loc[results_df["f1"].idxmax()]

    path = RESULT_DIR / "xgboost_error_analysis.txt"

    with open(path, "w", encoding="utf-8") as file:

        file.write("PRODIAG AI V2 - XGBOOST ERROR ANALYSIS\n")

        file.write("=" * 60 + "\n\n")

        file.write(f"Best F1 threshold: " f"{best_row['threshold']:.2f}\n\n")

        file.write(f"Precision: " f"{best_row['precision']:.4f}\n")

        file.write(f"Recall: " f"{best_row['recall']:.4f}\n")

        file.write(f"F1: " f"{best_row['f1']:.4f}\n\n")

        file.write(f"True Negatives: " f"{int(best_row['true_negatives'])}\n")

        file.write(f"False Positives: " f"{int(best_row['false_positives'])}\n")

        file.write(f"False Negatives: " f"{int(best_row['false_negatives'])}\n")

        file.write(f"True Positives: " f"{int(best_row['true_positives'])}\n")

    print(f"Saved: {path}")


def main():

    print("=" * 70)
    print("PRODIAG AI V2 - XGBOOST THRESHOLD & ERROR ANALYSIS")
    print("=" * 70)

    if not MODEL_PATH.exists():
        raise FileNotFoundError(f"XGBoost model not found:\n{MODEL_PATH}")

    if not DATA_PATH.exists():
        raise FileNotFoundError(f"Dataset not found:\n{DATA_PATH}")

    print("\nLoading XGBoost model...")

    model = joblib.load(MODEL_PATH)

    print("Model loaded successfully.")

    X_test, y_test = load_test_data()

    print("\nGenerating failure probabilities...")

    probabilities = model.predict_proba(X_test)[:, 1]

    print(
        f"Probability range: "
        f"{probabilities.min():.4f} → "
        f"{probabilities.max():.4f}"
    )

    results_df = evaluate_thresholds(probabilities, y_test)

    save_results(results_df)

    create_threshold_plot(results_df)

    save_error_analysis(results_df)

    print("\n" + "=" * 70)
    print("THRESHOLD ANALYSIS COMPLETED")
    print("=" * 70)


if __name__ == "__main__":
    main()
