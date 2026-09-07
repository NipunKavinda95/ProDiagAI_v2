from pathlib import Path
import json
import warnings

import joblib
import numpy as np
import pandas as pd

from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

from xgboost import XGBRegressor

warnings.filterwarnings("ignore")


PROJECT_ROOT = Path(__file__).resolve().parent.parent

DATA_PATH = PROJECT_ROOT / "ProDiag_AI_V2_synthetic_predictive_maintenance_dataset.csv"

MODEL_DIR = PROJECT_ROOT / "ml" / "models"
RESULT_DIR = PROJECT_ROOT / "ml" / "results"

MODEL_DIR.mkdir(parents=True, exist_ok=True)
RESULT_DIR.mkdir(parents=True, exist_ok=True)


TARGET = "health_score_target"

TEST_RATIO = 0.20


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


CATEGORICAL_FEATURES = ["equipment_type"]


def load_dataset():

    print("=" * 70)
    print("PRODIAG AI V2 - HEALTH SCORE REGRESSION EXPERIMENT")
    print("=" * 70)

    if not DATA_PATH.exists():

        raise FileNotFoundError(f"\nDataset not found:\n{DATA_PATH}")

    df = pd.read_csv(DATA_PATH)

    df["timestamp"] = pd.to_datetime(df["timestamp"], utc=True)

    df = df.sort_values(["timestamp", "machine_id"]).reset_index(drop=True)

    print(f"\nDataset: {DATA_PATH.name}")
    print(f"Rows: {len(df):,}")
    print(f"Columns: {len(df.columns)}")

    print("\nHealth Score target:")
    print(df[TARGET].describe())

    return df


def inspect_target(df):

    print("\n" + "-" * 70)
    print("HEALTH SCORE DATA QUALITY")
    print("-" * 70)

    missing = df[FEATURES + [TARGET]].isna().sum()

    missing = missing[missing > 0]

    if len(missing) == 0:

        print("\nNo missing values.")

    else:

        print("\nMissing values:")
        print(missing)

    print("\nHealth Score range:")

    print(f"Minimum: {df[TARGET].min():.4f}")

    print(f"Maximum: {df[TARGET].max():.4f}")

    print(f"Mean:    {df[TARGET].mean():.4f}")

    print(f"Median:  {df[TARGET].median():.4f}")


def split_time_based(df):

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
        f"Testing period: "
        f"{test_df['timestamp'].min()} → "
        f"{test_df['timestamp'].max()}"
    )

    return train_df, test_df


def create_preprocessor():

    numeric_pipeline = Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="median")),
            ("scaler", StandardScaler()),
        ]
    )

    categorical_pipeline = Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="most_frequent")),
            ("onehot", OneHotEncoder(handle_unknown="ignore")),
        ]
    )

    return ColumnTransformer(
        transformers=[
            ("numeric", numeric_pipeline, NUMERIC_FEATURES),
            ("categorical", categorical_pipeline, CATEGORICAL_FEATURES),
        ]
    )


def create_models():

    return {
        "Linear Regression": LinearRegression(),
        "Random Forest Regressor": RandomForestRegressor(
            n_estimators=300,
            max_depth=14,
            min_samples_leaf=3,
            random_state=42,
            n_jobs=-1,
        ),
        "XGBoost Regressor": XGBRegressor(
            n_estimators=300,
            max_depth=6,
            learning_rate=0.05,
            subsample=0.85,
            colsample_bytree=0.85,
            objective="reg:squarederror",
            eval_metric="rmse",
            random_state=42,
            n_jobs=-1,
        ),
    }


def evaluate_model(name, pipeline, X_test, y_test):

    predictions = pipeline.predict(X_test)

    predictions = np.clip(predictions, 0, 100)

    mae = mean_absolute_error(y_test, predictions)

    rmse = np.sqrt(mean_squared_error(y_test, predictions))

    r2 = r2_score(y_test, predictions)

    results = {
        "model": name,
        "mae": mae,
        "rmse": rmse,
        "r2": r2,
    }

    return results, predictions


def main():

    df = load_dataset()

    inspect_target(df)

    train_df, test_df = split_time_based(df)

    X_train = train_df[FEATURES]
    y_train = train_df[TARGET]

    X_test = test_df[FEATURES]
    y_test = test_df[TARGET]

    models = create_models()

    results = []

    predictions_by_model = {}

    print("\n" + "=" * 70)
    print("REGRESSION MODEL TRAINING")
    print("=" * 70)

    for name, model in models.items():

        print(f"\nTraining: {name}")

        preprocessor = create_preprocessor()

        pipeline = Pipeline(
            steps=[
                ("preprocessing", preprocessor),
                ("model", model),
            ]
        )

        pipeline.fit(X_train, y_train)

        metrics, predictions = evaluate_model(name, pipeline, X_test, y_test)

        results.append(metrics)

        predictions_by_model[name] = predictions

        safe_name = name.lower().replace(" ", "_")

        model_path = MODEL_DIR / f"{safe_name}.joblib"

        joblib.dump(pipeline, model_path)

        print(f"Saved model: " f"{model_path.name}")

        print(f"MAE  : {metrics['mae']:.4f}")

        print(f"RMSE : {metrics['rmse']:.4f}")

        print(f"R²   : {metrics['r2']:.4f}")

    results_df = pd.DataFrame(results)

    results_df = results_df.sort_values(
        ["mae", "rmse"], ascending=[True, True]
    ).reset_index(drop=True)

    comparison_path = RESULT_DIR / "health_score_model_comparison.csv"

    results_df.to_csv(comparison_path, index=False)

    best_model = results_df.iloc[0]

    summary = {
        "experiment": "Health Score Regression",
        "dataset": DATA_PATH.name,
        "target": TARGET,
        "target_range": "0-100",
        "split_method": "time_based",
        "test_ratio": TEST_RATIO,
        "models_compared": list(models.keys()),
        "selection_criteria": ["lowest MAE", "lowest RMSE", "highest R2"],
        "best_model": best_model["model"],
        "best_model_metrics": best_model.to_dict(),
        "all_results": results_df.to_dict(orient="records"),
    }

    summary_path = RESULT_DIR / "health_score_experiment_summary.json"

    with open(summary_path, "w", encoding="utf-8") as file:

        json.dump(summary, file, indent=4)

    print("\n" + "=" * 70)
    print("HEALTH SCORE MODEL COMPARISON")
    print("=" * 70)

    print(results_df.to_string(index=False, float_format=lambda x: f"{x:.4f}"))

    print("\n" + "=" * 70)
    print("BEST HEALTH SCORE MODEL")
    print("=" * 70)

    print(f"\nSelected model: " f"{best_model['model']}")

    print(f"MAE : {best_model['mae']:.4f}")

    print(f"RMSE: {best_model['rmse']:.4f}")

    print(f"R²  : {best_model['r2']:.4f}")

    print("\nSaved results:")

    print(f"  {comparison_path}")

    print(f"  {summary_path}")

    print("\n" + "=" * 70)
    print("HEALTH SCORE REGRESSION COMPLETED")
    print("=" * 70)


if __name__ == "__main__":
    main()
