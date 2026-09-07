from pathlib import Path
import warnings

import joblib
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import shap

warnings.filterwarnings("ignore")

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

SAMPLE_SIZE = 3000


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

    print(f"Test rows available: {len(X_test):,}")

    if len(X_test) > SAMPLE_SIZE:
        X_test = X_test.sample(n=SAMPLE_SIZE, random_state=42)

    print(f"SHAP samples used: {len(X_test):,}")

    return X_test


def transform_features(pipeline, X):

    preprocessor = pipeline.named_steps["preprocessing"]

    X_transformed = preprocessor.transform(X)

    feature_names = preprocessor.get_feature_names_out()

    if hasattr(X_transformed, "toarray"):
        X_transformed = X_transformed.toarray()

    X_transformed = pd.DataFrame(X_transformed, columns=feature_names, index=X.index)

    return X_transformed


def create_summary_plot(shap_values, X_transformed):

    print("\nCreating SHAP summary plot...")

    plt.figure(figsize=(11, 8))

    shap.summary_plot(shap_values, X_transformed, show=False, max_display=15)

    plt.title("ProDiag AI V2 - XGBoost SHAP Feature Impact")

    plt.tight_layout()

    path = RESULT_DIR / "xgboost_shap_summary.png"

    plt.savefig(path, dpi=200, bbox_inches="tight")

    plt.close()

    print(f"Saved: {path}")


def create_bar_plot(shap_values, X_transformed):

    print("\nCreating SHAP importance plot...")

    mean_abs_shap = np.abs(shap_values).mean(axis=0)

    importance_df = pd.DataFrame(
        {"feature": X_transformed.columns, "mean_abs_shap": mean_abs_shap}
    )

    importance_df = importance_df.sort_values(
        "mean_abs_shap", ascending=False
    ).reset_index(drop=True)

    importance_df["importance_percent"] = (
        importance_df["mean_abs_shap"] / importance_df["mean_abs_shap"].sum() * 100
    )

    csv_path = RESULT_DIR / "xgboost_shap_importance.csv"

    importance_df.to_csv(csv_path, index=False)

    top_features = importance_df.head(15)

    plt.figure(figsize=(10, 7))

    plt.barh(top_features["feature"][::-1], top_features["mean_abs_shap"][::-1])

    plt.xlabel("Mean Absolute SHAP Value")

    plt.ylabel("Feature")

    plt.title("ProDiag AI V2 - SHAP Feature Importance")

    plt.tight_layout()

    figure_path = RESULT_DIR / "xgboost_shap_importance.png"

    plt.savefig(figure_path, dpi=200, bbox_inches="tight")

    plt.close()

    print(f"Saved: {csv_path}")
    print(f"Saved: {figure_path}")

    return importance_df


def save_top_features(importance_df):

    path = RESULT_DIR / "xgboost_shap_top_features.txt"

    top_features = importance_df.head(15)

    with open(path, "w", encoding="utf-8") as file:

        file.write("PRODIAG AI V2 - SHAP TOP FEATURES\n")

        file.write("=" * 60 + "\n\n")

        for index, row in top_features.iterrows():

            file.write(
                f"{index + 1:2d}. "
                f"{row['feature']} - "
                f"{row['importance_percent']:.2f}%\n"
            )

    print(f"Saved: {path}")


def main():

    print("=" * 70)
    print("PRODIAG AI V2 - SHAP EXPLAINABILITY")
    print("=" * 70)

    if not MODEL_PATH.exists():
        raise FileNotFoundError(f"XGBoost model not found:\n{MODEL_PATH}")

    if not DATA_PATH.exists():
        raise FileNotFoundError(f"Dataset not found:\n{DATA_PATH}")

    print("\nLoading XGBoost pipeline...")

    pipeline = joblib.load(MODEL_PATH)

    model = pipeline.named_steps["model"]

    print("Model loaded successfully.")

    X_test = load_test_data()

    print("\nTransforming features...")

    X_transformed = transform_features(pipeline, X_test)

    print(f"Transformed feature count: " f"{X_transformed.shape[1]}")

    print("\nCreating SHAP TreeExplainer...")

    explainer = shap.TreeExplainer(model)

    print("Calculating SHAP values...")

    shap_values = explainer.shap_values(X_transformed)

    if isinstance(shap_values, list):
        shap_values = shap_values[-1]

    shap_values = np.asarray(shap_values)

    print(f"SHAP matrix shape: " f"{shap_values.shape}")

    create_summary_plot(shap_values, X_transformed)

    importance_df = create_bar_plot(shap_values, X_transformed)

    save_top_features(importance_df)

    print("\n" + "=" * 70)
    print("TOP SHAP FEATURES")
    print("=" * 70)

    for index, row in importance_df.head(15).iterrows():

        print(
            f"{index + 1:2d}. "
            f"{row['feature']:<50} "
            f"{row['importance_percent']:.2f}%"
        )

    print("\n" + "=" * 70)
    print("SHAP ANALYSIS COMPLETED")
    print("=" * 70)


if __name__ == "__main__":
    main()
