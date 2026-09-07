from pathlib import Path
import json

import joblib
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from sklearn.metrics import (
    mean_absolute_error,
    mean_squared_error,
    r2_score,
)

# ============================================================
# PATHS
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent

DATASET_PATH = BASE_DIR / "ProDiag_AI_V2_synthetic_predictive_maintenance_dataset.csv"

MODEL_DIR = BASE_DIR / "ml" / "models"
RESULTS_DIR = BASE_DIR / "ml" / "results"

RESULTS_DIR.mkdir(parents=True, exist_ok=True)


# ============================================================
# CONFIGURATION
# ============================================================

TARGET = "health_score_target"

TEST_SIZE = 0.20


# These are the EXACT feature names stored in the dataset
# and expected by the trained pipelines.

FEATURES = [
    "temperature_c",
    "vibration_mm_s",
    "current_a",
    "rpm",
    "load_factor",
    "temperature_c_delta",
    "temperature_c_rolling_mean_10",
    "vibration_mm_s_delta",
    "vibration_mm_s_rolling_mean_10",
    "current_a_delta",
    "current_a_rolling_mean_10",
    "rpm_delta",
    "rpm_rolling_mean_10",
    "equipment_type",
]


# ============================================================
# LOAD DATASET
# ============================================================

print("=" * 70)
print("ProDiag AI V2 - Health Score Regression Evaluation")
print("=" * 70)

print("\n[1/6] Loading dataset...")

df = pd.read_csv(DATASET_PATH)

print(f"Dataset rows: {len(df):,}")
print(f"Dataset columns: {len(df.columns)}")


# ============================================================
# VALIDATE FEATURES
# ============================================================

print("\n[2/6] Validating feature columns...")

missing_features = [feature for feature in FEATURES if feature not in df.columns]

if missing_features:

    print("\nERROR: Missing required features:")

    for feature in missing_features:
        print(f"  - {feature}")

    raise ValueError(
        "Dataset does not contain the exact features " "used by the trained models."
    )


print("All required features found.")


# ============================================================
# PREPARE DATA
# ============================================================

X = df[FEATURES].copy()

y = df[TARGET].copy()


# ============================================================
# TIME-BASED TEST SPLIT
# ============================================================

print("\n[3/6] Creating test split...")

# The dataset is already generated in chronological order.
# Do NOT sort by machine_id here because that would destroy
# the global temporal ordering.

split_index = int(len(df) * (1 - TEST_SIZE))

X_train = X.iloc[:split_index].copy()
X_test = X.iloc[split_index:].copy()

y_train = y.iloc[:split_index].copy()
y_test = y.iloc[split_index:].copy()


print(f"Training samples: {len(X_train):,}")

print(f"Test samples:     {len(X_test):,}")

print(f"Training target mean: " f"{y_train.mean():.4f}")

print(f"Test target mean: " f"{y_test.mean():.4f}")


# ============================================================
# LOAD TRAINED MODELS
# ============================================================

print("\n[4/6] Loading trained regression models...")

model_paths = {
    "Linear Regression": MODEL_DIR / "linear_regression.joblib",
    "Random Forest": MODEL_DIR / "random_forest_regressor.joblib",
    "XGBoost": MODEL_DIR / "xgboost_regressor.joblib",
}


models = {}

for name, path in model_paths.items():

    if not path.exists():

        raise FileNotFoundError(f"Model file not found: {path}")

    models[name] = joblib.load(path)

    print(f"Loaded: {name}")


# ============================================================
# EVALUATION
# ============================================================

print("\n[5/6] Evaluating models...")

results = []

predictions = {}


for name, model in models.items():

    print(f"\nEvaluating {name}...")

    # The saved model is a complete sklearn Pipeline.
    # Pass the raw dataframe columns directly.
    y_pred = model.predict(X_test)

    # Keep health score within valid range.
    y_pred = np.clip(
        y_pred,
        0,
        100,
    )

    predictions[name] = y_pred

    # --------------------------------------------------------
    # Core metrics
    # --------------------------------------------------------

    mae = mean_absolute_error(
        y_test,
        y_pred,
    )

    rmse = np.sqrt(
        mean_squared_error(
            y_test,
            y_pred,
        )
    )

    r2 = r2_score(
        y_test,
        y_pred,
    )

    # --------------------------------------------------------
    # Error analysis
    # --------------------------------------------------------

    errors = y_pred - y_test.to_numpy()

    absolute_errors = np.abs(errors)

    mean_error = np.mean(errors)

    median_absolute_error = np.median(absolute_errors)

    max_absolute_error = np.max(absolute_errors)

    # --------------------------------------------------------
    # Store results
    # --------------------------------------------------------

    results.append(
        {
            "model": name,
            "MAE": mae,
            "RMSE": rmse,
            "R2": r2,
            "Mean_Error": mean_error,
            "Median_Absolute_Error": median_absolute_error,
            "Max_Absolute_Error": max_absolute_error,
        }
    )

    # --------------------------------------------------------
    # Terminal output
    # --------------------------------------------------------

    print(f"MAE:                   {mae:.4f}")

    print(f"RMSE:                  {rmse:.4f}")

    print(f"R²:                    {r2:.4f}")

    print(f"Mean Error:            " f"{mean_error:.4f}")

    print(f"Median Absolute Error: " f"{median_absolute_error:.4f}")

    print(f"Max Absolute Error:    " f"{max_absolute_error:.4f}")


# ============================================================
# RESULTS DATAFRAME
# ============================================================

results_df = pd.DataFrame(results)


# Primary metric:
# MAE = average health-score prediction error.
#
# Secondary metrics:
# RMSE and R².

results_df = results_df.sort_values(
    by=[
        "MAE",
        "RMSE",
    ],
    ascending=[
        True,
        True,
    ],
).reset_index(drop=True)


# ============================================================
# SAVE DETAILED RESULTS
# ============================================================

comparison_path = RESULTS_DIR / "health_score_detailed_evaluation.csv"

results_df.to_csv(
    comparison_path,
    index=False,
)


# ============================================================
# PRINT MODEL RANKING
# ============================================================

print("\n" + "=" * 70)
print("HEALTH SCORE MODEL RANKING")
print("=" * 70)

print(
    results_df[
        [
            "model",
            "MAE",
            "RMSE",
            "R2",
        ]
    ].to_string(index=False)
)


best_model_name = results_df.iloc[0]["model"]


print(f"\nBest model by MAE: " f"{best_model_name}")


# ============================================================
# SAVE PREDICTIONS
# ============================================================

prediction_df = pd.DataFrame(
    {
        "timestamp": df.iloc[split_index:]["timestamp"].values,
        "machine_id": df.iloc[split_index:]["machine_id"].values,
        "actual_health_score": y_test.to_numpy(),
    }
)


for name, y_pred in predictions.items():

    safe_name = name.lower().replace(" ", "_")

    prediction_df[f"{safe_name}_prediction"] = y_pred


prediction_path = RESULTS_DIR / "health_score_predictions.csv"

prediction_df.to_csv(
    prediction_path,
    index=False,
)


# ============================================================
# PLOT 1 — PREDICTED VS ACTUAL
# ============================================================

plt.figure(figsize=(9, 7))

for name, y_pred in predictions.items():

    plt.scatter(
        y_test,
        y_pred,
        alpha=0.18,
        s=12,
        label=name,
    )


plt.plot(
    [0, 100],
    [0, 100],
    linestyle="--",
    linewidth=2,
    label="Perfect Prediction",
)


plt.xlabel("Actual Health Score")

plt.ylabel("Predicted Health Score")

plt.title("Health Score — Predicted vs Actual")

plt.xlim(
    0,
    100,
)

plt.ylim(
    0,
    100,
)

plt.legend()

plt.grid(alpha=0.25)

plt.tight_layout()


path = RESULTS_DIR / "health_score_predicted_vs_actual.png"

plt.savefig(
    path,
    dpi=200,
    bbox_inches="tight",
)

plt.close()


# ============================================================
# PLOT 2 — RESIDUAL DISTRIBUTION
# ============================================================

plt.figure(figsize=(9, 6))

for name, y_pred in predictions.items():

    residuals = y_pred - y_test.to_numpy()

    plt.hist(
        residuals,
        bins=60,
        alpha=0.35,
        label=name,
    )


plt.axvline(
    0,
    linestyle="--",
    linewidth=2,
)


plt.xlabel("Prediction Error")

plt.ylabel("Frequency")

plt.title("Health Score — Residual Distribution")

plt.legend()

plt.grid(alpha=0.25)

plt.tight_layout()


path = RESULTS_DIR / "health_score_residual_distribution.png"

plt.savefig(
    path,
    dpi=200,
    bbox_inches="tight",
)

plt.close()


# ============================================================
# PLOT 3 — MAE
# ============================================================

plt.figure(figsize=(9, 6))

plt.bar(
    results_df["model"],
    results_df["MAE"],
)

plt.ylabel("MAE")

plt.title("Health Score Model Comparison — MAE")

plt.grid(
    axis="y",
    alpha=0.25,
)

plt.tight_layout()


path = RESULTS_DIR / "health_score_mae_comparison.png"

plt.savefig(
    path,
    dpi=200,
    bbox_inches="tight",
)

plt.close()


# ============================================================
# PLOT 4 — RMSE
# ============================================================

plt.figure(figsize=(9, 6))

plt.bar(
    results_df["model"],
    results_df["RMSE"],
)

plt.ylabel("RMSE")

plt.title("Health Score Model Comparison — RMSE")

plt.grid(
    axis="y",
    alpha=0.25,
)

plt.tight_layout()


path = RESULTS_DIR / "health_score_rmse_comparison.png"

plt.savefig(
    path,
    dpi=200,
    bbox_inches="tight",
)

plt.close()


# ============================================================
# PLOT 5 — R²
# ============================================================

plt.figure(figsize=(9, 6))

plt.bar(
    results_df["model"],
    results_df["R2"],
)

plt.ylabel("R²")

plt.title("Health Score Model Comparison — R²")

plt.grid(
    axis="y",
    alpha=0.25,
)

plt.tight_layout()


path = RESULTS_DIR / "health_score_r2_comparison.png"

plt.savefig(
    path,
    dpi=200,
    bbox_inches="tight",
)

plt.close()


# ============================================================
# PLOT 6 — BEST MODEL ERROR
# ============================================================

best_predictions = predictions[best_model_name]

best_errors = best_predictions - y_test.to_numpy()


plt.figure(figsize=(12, 6))

plt.plot(
    best_errors,
    linewidth=0.8,
)

plt.axhline(
    0,
    linestyle="--",
    linewidth=1.5,
)


plt.xlabel("Test Sample")

plt.ylabel("Prediction Error")

plt.title(f"Health Score Prediction Error — " f"{best_model_name}")

plt.grid(alpha=0.25)

plt.tight_layout()


path = RESULTS_DIR / "health_score_best_model_error.png"

plt.savefig(
    path,
    dpi=200,
    bbox_inches="tight",
)

plt.close()


# ============================================================
# JSON SUMMARY
# ============================================================

summary = {
    "target": TARGET,
    "dataset_rows": int(len(df)),
    "training_samples": int(len(X_train)),
    "test_samples": int(len(X_test)),
    "test_size": TEST_SIZE,
    "validation_method": "time_based_split",
    "selection_metric": "MAE",
    "best_model": best_model_name,
    "models": {},
}


for _, row in results_df.iterrows():

    summary["models"][row["model"]] = {
        "MAE": float(row["MAE"]),
        "RMSE": float(row["RMSE"]),
        "R2": float(row["R2"]),
        "Mean_Error": float(row["Mean_Error"]),
        "Median_Absolute_Error": float(row["Median_Absolute_Error"]),
        "Max_Absolute_Error": float(row["Max_Absolute_Error"]),
    }


summary_path = RESULTS_DIR / "health_score_detailed_evaluation.json"


with open(
    summary_path,
    "w",
    encoding="utf-8",
) as f:

    json.dump(
        summary,
        f,
        indent=2,
    )


# ============================================================
# COMPLETE
# ============================================================

print("\n" + "=" * 70)
print("HEALTH SCORE EVALUATION COMPLETE")
print("=" * 70)

print(f"\nSelected model by MAE: " f"{best_model_name}")

print("\nEvaluation files saved to:")

print(RESULTS_DIR)
