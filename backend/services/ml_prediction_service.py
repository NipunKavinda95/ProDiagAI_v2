from pathlib import Path
from typing import Any, Dict

import joblib
import pandas as pd

from services.ml_feature_service import ml_feature_service


class MLPredictionService:
    FAILURE_THRESHOLD = 0.70

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

    def __init__(self):
        backend_dir = Path(__file__).resolve().parents[1]
        project_root = backend_dir.parent
        models_dir = project_root / "ml" / "models"

        self.failure_model_path = models_dir / "xgboost.joblib"
        self.health_model_path = models_dir / "xgboost_regressor.joblib"

        self.failure_model = self._load_model(self.failure_model_path)
        self.health_model = self._load_model(self.health_model_path)

        # Cache the latest ML prediction for each machine.
        # Live telemetry can arrive every second, while ML inference
        # is intentionally performed at the training cadence.
        self.last_predictions: Dict[str, Dict[str, Any]] = {}

        print("[ML] XGBoost failure model loaded")
        print("[ML] XGBoost health-score model loaded")

    @staticmethod
    def _load_model(path: Path):
        if not path.exists():
            raise FileNotFoundError(f"ML model not found: {path}")

        return joblib.load(path)

    def _prepare_features(self, telemetry):
        features = ml_feature_service.build_features(telemetry)

        # The feature service returns None when this telemetry
        # reading is between ML sampling intervals.
        if features is None:
            return None

        missing_features = [
            feature for feature in self.FEATURES if feature not in features
        ]

        if missing_features:
            raise ValueError(f"Missing ML features: {missing_features}")

        return pd.DataFrame(
            [[features[feature] for feature in self.FEATURES]],
            columns=self.FEATURES,
        )

    def predict(self, telemetry):
        machine_id = telemetry.get("machine_id")

        if not machine_id:
            raise ValueError("machine_id is required for ML prediction")

        features = self._prepare_features(telemetry)

        # No new ML sample yet.
        # Reuse the latest prediction instead of recalculating
        # from 1-second telemetry.
        if features is None:
            cached_prediction = self.last_predictions.get(machine_id)

            if cached_prediction is not None:
                return cached_prediction.copy()

            # Safety fallback. This should only occur if the very
            # first telemetry packet cannot produce ML features.
            return {
                "failure_probability": 0.0,
                "failure_within_1h": False,
                "failure_threshold": self.FAILURE_THRESHOLD,
                "health_score": 100.0,
            }

        # Run the trained models only on the new ML sample.
        failure_probability = float(self.failure_model.predict_proba(features)[0][1])

        failure_prediction = failure_probability >= self.FAILURE_THRESHOLD

        health_score = float(self.health_model.predict(features)[0])

        health_score = max(0.0, min(100.0, health_score))

        prediction = {
            "failure_probability": round(failure_probability, 4),
            "failure_within_1h": failure_prediction,
            "failure_threshold": self.FAILURE_THRESHOLD,
            "health_score": round(health_score, 2),
        }
        condition = str(
            telemetry.get("condition", telemetry.get("health_status", ""))
        ).upper()

        if condition == "FAULTED":
            prediction["prediction_status"] = "ALREADY_FAULTED"
        elif condition == "REPAIRING":
            prediction["prediction_status"] = "UNDER_MAINTENANCE"
        elif condition == "RESTART":
            prediction["prediction_status"] = "RESTARTING"
        else:
            prediction["prediction_status"] = (
                "HIGH_RISK" if failure_prediction else "NORMAL"
            )

        # Cache this machine's latest prediction.
        self.last_predictions[machine_id] = prediction.copy()

        return prediction


ml_prediction_service = MLPredictionService()
