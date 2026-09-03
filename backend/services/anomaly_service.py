"""
ProDiag AI V2
Anomaly Detection Service

Responsibilities:
- Learn normal sensor behaviour for each machine
- Detect unusual sensor combinations using Isolation Forest
- Apply engineering safety rules
- Return an explainable anomaly result
"""

from collections import defaultdict, deque

import numpy as np
from sklearn.ensemble import IsolationForest


class AnomalyService:
    def __init__(
        self,
        window_size=60,
        min_samples=20,
        contamination=0.05,
    ):
        self.window_size = window_size
        self.min_samples = min_samples
        self.contamination = contamination

        self.machine_history = defaultdict(
            lambda: deque(maxlen=self.window_size)
        )

        self.models = {}

    def _extract_features(self, reading):
        return [
            float(reading.get("temperature_c", 0)),
            float(reading.get("vibration_mm_s", 0)),
            float(reading.get("current_a", 0)),
            float(reading.get("rpm", 0)),
        ]

    def _train_model(self, machine_id):
        history = self.machine_history[machine_id]

        if len(history) < self.min_samples:
            return None

        X = np.array(history)

        model = IsolationForest(
            n_estimators=100,
            contamination=self.contamination,
            random_state=42,
        )

        model.fit(X)

        self.models[machine_id] = model

        return model

    def _engineering_anomaly(self, reading):
        """
        Detect obvious dangerous operating conditions
        using engineering thresholds.
        """

        temperature = float(
            reading.get("temperature_c", 0)
        )

        vibration = float(
            reading.get("vibration_mm_s", 0)
        )

        current = float(
            reading.get("current_a", 0)
        )

        reasons = []

        if temperature >= 70:
            reasons.append(
                "Critical temperature level"
            )

        if vibration >= 4.5:
            reasons.append(
                "Critical vibration level"
            )

        if current >= 22:
            reasons.append(
                "Critical current level"
            )

        return reasons

    def detect(self, reading):
        """
        Analyze one telemetry reading.
        """

        machine_id = reading.get("machine_id")

        if not machine_id:
            return {
                "is_anomaly": False,
                "anomaly_score": 0.0,
                "status": "INSUFFICIENT_DATA",
                "samples_used": 0,
                "reasons": [],
            }

        features = self._extract_features(reading)

        history = self.machine_history[machine_id]

        history.append(features)

        samples_used = len(history)

        # Engineering rules are checked first.
        engineering_reasons = self._engineering_anomaly(
            reading
        )

        # Learn normal behaviour first.
        if samples_used < self.min_samples:
            if engineering_reasons:
                return {
                    "is_anomaly": True,
                    "anomaly_score": 1.0,
                    "status": "ANOMALY",
                    "samples_used": samples_used,
                    "reasons": engineering_reasons,
                }

            return {
                "is_anomaly": False,
                "anomaly_score": 0.0,
                "status": "LEARNING",
                "samples_used": samples_used,
                "reasons": [],
            }

        model = self.models.get(machine_id)

        if model is None:
            model = self._train_model(machine_id)

        if model is None:
            return {
                "is_anomaly": False,
                "anomaly_score": 0.0,
                "status": "LEARNING",
                "samples_used": samples_used,
                "reasons": [],
            }

        X_current = np.array([features])

        prediction = model.predict(X_current)[0]

        raw_score = model.decision_function(
            X_current
        )[0]

        ml_anomaly = prediction == -1

        anomaly_score = max(
            0.0,
            min(
                1.0,
                0.5 - float(raw_score),
            ),
        )

        # Combine ML detection with engineering rules.
        is_anomaly = (
            ml_anomaly
            or bool(engineering_reasons)
        )

        reasons = list(engineering_reasons)

        if ml_anomaly:
            reasons.append(
                "Unusual sensor pattern detected by ML model"
            )

        return {
            "is_anomaly": bool(is_anomaly),
            "anomaly_score": round(
                anomaly_score,
                4,
            ),
            "status": (
                "ANOMALY"
                if is_anomaly
                else "NORMAL"
            ),
            "samples_used": samples_used,
            "reasons": reasons,
        }


# Shared service instance
anomaly_service = AnomalyService()