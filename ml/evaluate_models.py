from pathlib import Path
import json
import warnings

import joblib
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from sklearn.metrics import (
    accuracy_score,
    average_precision_score,
    classification_report,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
    roc_curve,
    precision_recall_curve,
)

warnings.filterwarnings("ignore")

PROJECT_ROOT = Path(__file__).resolve().parent.parent

DATA_PATH = PROJECT_ROOT / "ProDiag_AI_V2_synthetic_predictive_maintenance_dataset.csv"
MODEL_DIR = PROJECT_ROOT / "ml" / "models"
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


def load_test_data():
    print("=" * 70)
    print("PRODIAG AI V2 - MODEL EVALUATION")
    print("=" * 70)

    if not DATA_PATH.exists():
        raise FileNotFoundError(f"Dataset not found:\n{DATA_PATH}")

    df = pd.read_csv(DATA_PATH)

    df["timestamp"] = pd.to_datetime(df["timestamp"], utc=True)

    df = df.sort_values(["timestamp", "machine_id"]).reset_index(drop=True)

    unique_timestamps = df["timestamp"].sort_values().unique()

    split_index = int(len(unique_timestamps) * 0.80)

    split_timestamp = unique_timestamps[split_index]

    test_df = df[df["timestamp"] >= split_timestamp].copy()

    X_test = test_df[FEATURES]
    y_test = test_df[TARGET]

    print(f"\nTest rows: {len(test_df):,}")
    print(f"Test period: {test_df['timestamp'].min()} → {test_df['timestamp'].max()}")
    print(f"Failure samples: {int(y_test.sum()):,}")
    print(f"Normal samples: {int((y_test == 0).sum()):,}")

    return X_test, y_test


def evaluate_models(X_test, y_test):
    model_files = {
        "Logistic Regression": MODEL_DIR / "logistic_regression.joblib",
        "Random Forest": MODEL_DIR / "random_forest.joblib",
        "XGBoost": MODEL_DIR / "xgboost.joblib",
    }

    results = []

    roc_data = {}
    pr_data = {}
    confusion_matrices = {}

    print("\n" + "=" * 70)
    print("DETAILED MODEL EVALUATION")
    print("=" * 70)

    for name, model_path in model_files.items():

        if not model_path.exists():
            raise FileNotFoundError(f"Model not found:\n{model_path}")

        print(f"\nEvaluating: {name}")

        model = joblib.load(model_path)

        predictions = model.predict(X_test)

        probabilities = model.predict_proba(X_test)[:, 1]

        accuracy = accuracy_score(y_test, predictions)

        precision = precision_score(y_test, predictions, zero_division=0)

        recall = recall_score(y_test, predictions, zero_division=0)

        f1 = f1_score(y_test, predictions, zero_division=0)

        roc_auc = roc_auc_score(y_test, probabilities)

        pr_auc = average_precision_score(y_test, probabilities)

        matrix = confusion_matrix(y_test, predictions)

        report = classification_report(y_test, predictions, zero_division=0)

        results.append(
            {
                "model": name,
                "accuracy": accuracy,
                "precision": precision,
                "recall": recall,
                "f1": f1,
                "roc_auc": roc_auc,
                "pr_auc": pr_auc,
            }
        )

        confusion_matrices[name] = matrix.tolist()

        fpr, tpr, _ = roc_curve(y_test, probabilities)

        precision_curve, recall_curve, _ = precision_recall_curve(y_test, probabilities)

        roc_data[name] = {
            "fpr": fpr.tolist(),
            "tpr": tpr.tolist(),
            "auc": roc_auc,
        }

        pr_data[name] = {
            "precision": precision_curve.tolist(),
            "recall": recall_curve.tolist(),
            "auc": pr_auc,
        }

        print(f"Accuracy  : {accuracy:.4f}")
        print(f"Precision : {precision:.4f}")
        print(f"Recall    : {recall:.4f}")
        print(f"F1        : {f1:.4f}")
        print(f"ROC-AUC   : {roc_auc:.4f}")
        print(f"PR-AUC    : {pr_auc:.4f}")

        print("\nConfusion Matrix:")
        print(matrix)

        report_path = RESULT_DIR / (
            name.lower().replace(" ", "_") + "_classification_report.txt"
        )

        with open(report_path, "w", encoding="utf-8") as file:
            file.write(report)

    return (
        pd.DataFrame(results),
        roc_data,
        pr_data,
        confusion_matrices,
    )


def save_comparison(results_df):

    results_path = RESULT_DIR / "detailed_model_evaluation.csv"

    results_df = results_df.sort_values("f1", ascending=False)

    results_df.to_csv(results_path, index=False)

    print(f"\nSaved: {results_path}")

    return results_df


def create_confusion_matrix_plot(confusion_matrices):

    fig, axes = plt.subplots(1, 3, figsize=(15, 4))

    for ax, (name, matrix) in zip(axes, confusion_matrices.items()):

        matrix = np.array(matrix)

        ax.imshow(matrix)

        ax.set_title(name)

        ax.set_xlabel("Predicted")

        ax.set_ylabel("Actual")

        ax.set_xticks([0, 1])
        ax.set_yticks([0, 1])

        ax.set_xticklabels(["Normal", "Failure"])

        ax.set_yticklabels(["Normal", "Failure"])

        for i in range(2):
            for j in range(2):

                ax.text(j, i, matrix[i, j], ha="center", va="center")

    plt.tight_layout()

    path = RESULT_DIR / "confusion_matrices.png"

    plt.savefig(path, dpi=200, bbox_inches="tight")

    plt.close()

    print(f"Saved: {path}")


def create_roc_plot(roc_data):

    plt.figure(figsize=(8, 6))

    for name, data in roc_data.items():

        plt.plot(data["fpr"], data["tpr"], label=f"{name} (AUC={data['auc']:.4f})")

    plt.plot([0, 1], [0, 1], linestyle="--", label="Random classifier")

    plt.xlabel("False Positive Rate")

    plt.ylabel("True Positive Rate")

    plt.title("ProDiag AI V2 - ROC Curve Comparison")

    plt.legend()

    plt.grid(alpha=0.3)

    plt.tight_layout()

    path = RESULT_DIR / "roc_curve_comparison.png"

    plt.savefig(path, dpi=200, bbox_inches="tight")

    plt.close()

    print(f"Saved: {path}")


def create_pr_plot(pr_data):

    plt.figure(figsize=(8, 6))

    for name, data in pr_data.items():

        plt.plot(
            data["recall"], data["precision"], label=f"{name} (AP={data['auc']:.4f})"
        )

    plt.xlabel("Recall")

    plt.ylabel("Precision")

    plt.title("ProDiag AI V2 - Precision-Recall Comparison")

    plt.legend()

    plt.grid(alpha=0.3)

    plt.tight_layout()

    path = RESULT_DIR / "precision_recall_comparison.png"

    plt.savefig(path, dpi=200, bbox_inches="tight")

    plt.close()

    print(f"Saved: {path}")


def create_model_comparison_plot(results_df):

    metrics = [
        "precision",
        "recall",
        "f1",
        "roc_auc",
        "pr_auc",
    ]

    models = results_df["model"].tolist()

    x = np.arange(len(models))

    width = 0.15

    plt.figure(figsize=(12, 6))

    for index, metric in enumerate(metrics):

        values = results_df[metric].values

        plt.bar(x + index * width, values, width, label=metric.upper())

    plt.xticks(x + width * 2, models, rotation=15)

    plt.ylim(max(0, results_df[metrics].min().min() - 0.05), 1.01)

    plt.ylabel("Score")

    plt.title("ProDiag AI V2 - ML Model Comparison")

    plt.legend()

    plt.grid(axis="y", alpha=0.3)

    plt.tight_layout()

    path = RESULT_DIR / "model_comparison.png"

    plt.savefig(path, dpi=200, bbox_inches="tight")

    plt.close()

    print(f"Saved: {path}")


def save_evaluation_summary(results_df, confusion_matrices):

    best_model = results_df.iloc[0]

    summary = {
        "evaluation_type": "time_based_test_evaluation",
        "target": TARGET,
        "selection_metric": "f1",
        "best_model": best_model["model"],
        "best_model_metrics": best_model.to_dict(),
        "model_results": results_df.to_dict(orient="records"),
        "confusion_matrices": confusion_matrices,
    }

    path = RESULT_DIR / "evaluation_summary.json"

    with open(path, "w", encoding="utf-8") as file:

        json.dump(summary, file, indent=4)

    print(f"Saved: {path}")


def main():

    X_test, y_test = load_test_data()

    (
        results_df,
        roc_data,
        pr_data,
        confusion_matrices,
    ) = evaluate_models(X_test, y_test)

    results_df = save_comparison(results_df)

    create_confusion_matrix_plot(confusion_matrices)

    create_roc_plot(roc_data)

    create_pr_plot(pr_data)

    create_model_comparison_plot(results_df)

    save_evaluation_summary(results_df, confusion_matrices)

    print("\n" + "=" * 70)
    print("FINAL MODEL RANKING")
    print("=" * 70)

    print(
        results_df[
            [
                "model",
                "precision",
                "recall",
                "f1",
                "roc_auc",
                "pr_auc",
            ]
        ].to_string(index=False, float_format=lambda x: f"{x:.4f}")
    )

    print("\n" + "=" * 70)
    print("EVALUATION COMPLETED")
    print("=" * 70)


if __name__ == "__main__":
    main()
