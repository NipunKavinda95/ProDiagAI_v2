from pathlib import Path
import json
import warnings

import joblib
import numpy as np
import pandas as pd

from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    average_precision_score,
    classification_report,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
)
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.ensemble import RandomForestClassifier

from xgboost import XGBClassifier

warnings.filterwarnings("ignore")


# ============================================================
# PATHS
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent

DATA_PATH = PROJECT_ROOT / "ProDiag_AI_V2_synthetic_predictive_maintenance_dataset.csv"

MODEL_DIR = PROJECT_ROOT / "ml" / "models"
RESULT_DIR = PROJECT_ROOT / "ml" / "results"

MODEL_DIR.mkdir(parents=True, exist_ok=True)
RESULT_DIR.mkdir(parents=True, exist_ok=True)


# ============================================================
# CONFIGURATION
# ============================================================

TARGET = "failure_within_1h"

TEST_RATIO = 0.20


# Features available to the ML model.
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


# ============================================================
# LOAD DATA
# ============================================================


def load_dataset():
    print("=" * 70)
    print("PRODIAG AI V2 - ML FAILURE PREDICTION EXPERIMENT")
    print("=" * 70)

    if not DATA_PATH.exists():
        raise FileNotFoundError(
            f"\nDataset not found:\n{DATA_PATH}\n\n"
            "Place the CSV dataset in the ProDiag AI V2 project root."
        )

    df = pd.read_csv(DATA_PATH)

    print(f"\nDataset: {DATA_PATH.name}")
    print(f"Rows: {len(df):,}")
    print(f"Columns: {len(df.columns)}")

    # Convert timestamp and sort chronologically.
    df["timestamp"] = pd.to_datetime(df["timestamp"], utc=True)

    df = df.sort_values(["timestamp", "machine_id"]).reset_index(drop=True)

    return df


# ============================================================
# DATA QUALITY
# ============================================================


def inspect_dataset(df):
    print("\n" + "-" * 70)
    print("DATA QUALITY")
    print("-" * 70)

    print("\nMissing values:")
    missing = df[FEATURES + [TARGET]].isna().sum()

    missing = missing[missing > 0]

    if len(missing) == 0:
        print("No missing values.")
    else:
        print(missing)

    print("\nTarget distribution:")

    target_counts = df[TARGET].value_counts().sort_index()

    print(target_counts)

    failure_rate = df[TARGET].mean()

    print(f"\nFailure samples: {int(df[TARGET].sum()):,}")

    print(f"Non-failure samples: " f"{int((df[TARGET] == 0).sum()):,}")

    print(f"Failure rate: {failure_rate:.2%}")


# ============================================================
# TIME-BASED SPLIT
# ============================================================


def split_time_based(df):
    """
    Important:
    We deliberately DO NOT use random train/test splitting.

    Earlier observations -> training
    Later observations  -> testing

    This better represents real predictive-maintenance deployment.
    """

    unique_timestamps = df["timestamp"].sort_values().unique()

    split_index = int(len(unique_timestamps) * (1 - TEST_RATIO))

    split_timestamp = unique_timestamps[split_index]

    train_df = df[df["timestamp"] < split_timestamp].copy()

    test_df = df[df["timestamp"] >= split_timestamp].copy()

    print("\n" + "-" * 70)
    print("TIME-BASED TRAIN / TEST SPLIT")
    print("-" * 70)

    print(f"\nSplit timestamp: {split_timestamp}")

    print(f"Training rows: {len(train_df):,}")

    print(f"Testing rows:  {len(test_df):,}")

    print(
        f"Training period: "
        f"{train_df['timestamp'].min()} → "
        f"{train_df['timestamp'].max()}"
    )

    print(
        f"Testing period:  "
        f"{test_df['timestamp'].min()} → "
        f"{test_df['timestamp'].max()}"
    )

    return train_df, test_df


# ============================================================
# PREPROCESSING
# ============================================================

NUMERIC_FEATURES = [
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
]

CATEGORICAL_FEATURES = [
    "equipment_type",
]


def create_preprocessor():

    numeric_pipeline = Pipeline(
        steps=[
            (
                "imputer",
                SimpleImputer(strategy="median"),
            ),
            (
                "scaler",
                StandardScaler(),
            ),
        ]
    )

    categorical_pipeline = Pipeline(
        steps=[
            (
                "imputer",
                SimpleImputer(strategy="most_frequent"),
            ),
            (
                "onehot",
                OneHotEncoder(handle_unknown="ignore"),
            ),
        ]
    )

    return ColumnTransformer(
        transformers=[
            (
                "numeric",
                numeric_pipeline,
                NUMERIC_FEATURES,
            ),
            (
                "categorical",
                categorical_pipeline,
                CATEGORICAL_FEATURES,
            ),
        ]
    )


# ============================================================
# MODEL DEFINITIONS
# ============================================================


def create_models():

    return {
        "Logistic Regression": LogisticRegression(
            max_iter=2000,
            class_weight="balanced",
            random_state=42,
        ),
        "Random Forest": RandomForestClassifier(
            n_estimators=300,
            max_depth=14,
            min_samples_leaf=3,
            class_weight="balanced",
            random_state=42,
            n_jobs=-1,
        ),
        "XGBoost": XGBClassifier(
            n_estimators=300,
            max_depth=6,
            learning_rate=0.05,
            subsample=0.85,
            colsample_bytree=0.85,
            objective="binary:logistic",
            eval_metric="logloss",
            random_state=42,
            n_jobs=-1,
        ),
    }


# ============================================================
# EVALUATION
# ============================================================


def evaluate_model(
    name,
    pipeline,
    X_test,
    y_test,
):

    predictions = pipeline.predict(X_test)

    probabilities = pipeline.predict_proba(X_test)[:, 1]

    metrics = {
        "model": name,
        "accuracy": accuracy_score(
            y_test,
            predictions,
        ),
        "precision": precision_score(
            y_test,
            predictions,
            zero_division=0,
        ),
        "recall": recall_score(
            y_test,
            predictions,
            zero_division=0,
        ),
        "f1": f1_score(
            y_test,
            predictions,
            zero_division=0,
        ),
        "roc_auc": roc_auc_score(
            y_test,
            probabilities,
        ),
        "pr_auc": average_precision_score(
            y_test,
            probabilities,
        ),
    }

    matrix = confusion_matrix(
        y_test,
        predictions,
    )

    report = classification_report(
        y_test,
        predictions,
        zero_division=0,
    )

    return metrics, matrix, report


# ============================================================
# MAIN EXPERIMENT
# ============================================================


def main():

    df = load_dataset()

    inspect_dataset(df)

    train_df, test_df = split_time_based(df)

    X_train = train_df[FEATURES]
    y_train = train_df[TARGET]

    X_test = test_df[FEATURES]
    y_test = test_df[TARGET]

    models = create_models()

    all_results = []
    detailed_results = {}

    print("\n" + "=" * 70)
    print("MODEL TRAINING")
    print("=" * 70)

    for name, model in models.items():

        print(f"\nTraining: {name}")

        preprocessor = create_preprocessor()

        pipeline = Pipeline(
            steps=[
                (
                    "preprocessing",
                    preprocessor,
                ),
                (
                    "model",
                    model,
                ),
            ]
        )

        pipeline.fit(
            X_train,
            y_train,
        )

        metrics, matrix, report = evaluate_model(
            name,
            pipeline,
            X_test,
            y_test,
        )

        all_results.append(metrics)

        detailed_results[name] = {
            "metrics": metrics,
            "confusion_matrix": matrix.tolist(),
            "classification_report": report,
        }

        # Save each trained model.
        safe_name = name.lower().replace(" ", "_")

        model_path = MODEL_DIR / f"{safe_name}.joblib"

        joblib.dump(
            pipeline,
            model_path,
        )

        print(f"Saved model: {model_path.name}")

        print(f"Precision : {metrics['precision']:.4f}")
        print(f"Recall    : {metrics['recall']:.4f}")
        print(f"F1        : {metrics['f1']:.4f}")
        print(f"ROC-AUC   : {metrics['roc_auc']:.4f}")
        print(f"PR-AUC    : {metrics['pr_auc']:.4f}")

    # ========================================================
    # MODEL COMPARISON
    # ========================================================

    results_df = pd.DataFrame(all_results)

    results_df = results_df.sort_values(
        "f1",
        ascending=False,
    ).reset_index(drop=True)

    comparison_path = RESULT_DIR / "model_comparison.csv"

    results_df.to_csv(
        comparison_path,
        index=False,
    )

    # Best model based primarily on F1.
    best_model = results_df.iloc[0]

    best_model_name = best_model["model"]

    experiment_summary = {
        "dataset": DATA_PATH.name,
        "target": TARGET,
        "features": FEATURES,
        "split_method": "time_based",
        "test_ratio": TEST_RATIO,
        "models_compared": list(models.keys()),
        "selection_metric": "f1",
        "best_model": best_model_name,
        "best_model_metrics": best_model.to_dict(),
        "all_results": detailed_results,
    }

    summary_path = RESULT_DIR / "ml_experiment_summary.json"

    with open(
        summary_path,
        "w",
        encoding="utf-8",
    ) as file:
        json.dump(
            experiment_summary,
            file,
            indent=4,
            default=str,
        )

    # ========================================================
    # FINAL OUTPUT
    # ========================================================

    print("\n" + "=" * 70)
    print("MODEL COMPARISON")
    print("=" * 70)

    display_columns = [
        "model",
        "precision",
        "recall",
        "f1",
        "roc_auc",
        "pr_auc",
        "accuracy",
    ]

    print(
        results_df[display_columns].to_string(
            index=False,
            float_format=lambda x: f"{x:.4f}",
        )
    )

    print("\n" + "=" * 70)
    print("BEST MODEL")
    print("=" * 70)

    print(f"\nSelected model: {best_model_name}")

    print(f"F1:       {best_model['f1']:.4f}")

    print(f"Recall:   {best_model['recall']:.4f}")

    print(f"Precision: {best_model['precision']:.4f}")

    print(f"ROC-AUC:  {best_model['roc_auc']:.4f}")

    print(f"PR-AUC:   {best_model['pr_auc']:.4f}")

    print("\nSaved results:")
    print(f"  {comparison_path}")
    print(f"  {summary_path}")

    print("\nML experiment completed successfully.")


if __name__ == "__main__":
    main()
