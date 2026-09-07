from pathlib import Path

import joblib
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

PROJECT_ROOT = Path(__file__).resolve().parent.parent

MODEL_PATH = PROJECT_ROOT / "ml" / "models" / "xgboost.joblib"
DATA_PATH = PROJECT_ROOT / "ProDiag_AI_V2_synthetic_predictive_maintenance_dataset.csv"
RESULT_DIR = PROJECT_ROOT / "ml" / "results"

RESULT_DIR.mkdir(parents=True, exist_ok=True)


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


def main():

    print("=" * 70)
    print("PRODIAG AI V2 - XGBOOST FEATURE IMPORTANCE")
    print("=" * 70)

    if not MODEL_PATH.exists():
        raise FileNotFoundError(f"XGBoost model not found:\n{MODEL_PATH}")

    if not DATA_PATH.exists():
        raise FileNotFoundError(f"Dataset not found:\n{DATA_PATH}")

    print("\nLoading XGBoost model...")

    pipeline = joblib.load(MODEL_PATH)

    model = pipeline.named_steps["model"]
    preprocessor = pipeline.named_steps["preprocessing"]

    print("Model loaded successfully.")

    feature_names = preprocessor.get_feature_names_out()

    importances = model.feature_importances_

    importance_df = pd.DataFrame(
        {
            "feature": feature_names,
            "importance": importances,
        }
    )

    importance_df = importance_df.sort_values(
        "importance", ascending=False
    ).reset_index(drop=True)

    importance_df["importance_percent"] = importance_df["importance"] * 100

    print("\n" + "-" * 70)
    print("FEATURE IMPORTANCE RANKING")
    print("-" * 70)

    print(
        importance_df[["feature", "importance_percent"]].to_string(
            index=False, float_format=lambda x: f"{x:.4f}"
        )
    )

    csv_path = RESULT_DIR / "xgboost_feature_importance.csv"

    importance_df.to_csv(csv_path, index=False)

    print(f"\nSaved: {csv_path}")

    top_n = min(15, len(importance_df))

    top_features = importance_df.head(top_n)

    plt.figure(figsize=(10, 7))

    plt.barh(top_features["feature"][::-1], top_features["importance_percent"][::-1])

    plt.xlabel("Importance (%)")

    plt.ylabel("Feature")

    plt.title("ProDiag AI V2 - XGBoost Feature Importance")

    plt.tight_layout()

    figure_path = RESULT_DIR / "xgboost_feature_importance.png"

    plt.savefig(figure_path, dpi=200, bbox_inches="tight")

    plt.close()

    print(f"Saved: {figure_path}")

    print("\n" + "=" * 70)
    print("TOP FEATURES")
    print("=" * 70)

    for index, row in top_features.iterrows():

        print(
            f"{index + 1:2d}. "
            f"{row['feature']:<45} "
            f"{row['importance_percent']:.2f}%"
        )

    print("\n" + "=" * 70)
    print("FEATURE IMPORTANCE ANALYSIS COMPLETED")
    print("=" * 70)


if __name__ == "__main__":
    main()
