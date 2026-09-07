"""
ProDiag AI V2
ML Feature Service

Builds the feature set required by the trained ML models
from live telemetry readings.

Live telemetry may arrive every second, while the ML model
was trained on 10-second sampling intervals.
"""

from collections import defaultdict, deque
from datetime import datetime
from typing import Any, Dict, Optional

import pandas as pd


class MLFeatureService:
    """
    Maintains telemetry history for each machine and generates
    ML features at the same 10-second sampling interval used
    during model training.
    """

    HISTORY_SIZE = 10
    SAMPLING_INTERVAL_SECONDS = 10

    def __init__(self):
        self.history = defaultdict(
            lambda: {
                "temperature_c": deque(maxlen=self.HISTORY_SIZE),
                "vibration_mm_s": deque(maxlen=self.HISTORY_SIZE),
                "current_a": deque(maxlen=self.HISTORY_SIZE),
                "rpm": deque(maxlen=self.HISTORY_SIZE),
                "last_sample_timestamp": None,
            }
        )

    @staticmethod
    def _safe_float(
        value: Any,
        default: float = 0.0,
    ) -> float:

        try:
            if value is None:
                return default

            result = float(value)

            if pd.isna(result):
                return default

            return result

        except (TypeError, ValueError):
            return default

    @staticmethod
    def _parse_timestamp(value: Any) -> Optional[datetime]:
        try:
            if value is None:
                return None

            timestamp = pd.to_datetime(
                value,
                utc=True,
            )

            if pd.isna(timestamp):
                return None

            return timestamp.to_pydatetime()

        except (TypeError, ValueError):
            return None

    def _should_sample(
        self,
        machine_history: Dict[str, Any],
        timestamp: Optional[datetime],
    ) -> bool:
        """
        Determine whether this telemetry reading should become
        a new ML sample.
        """

        last_timestamp = machine_history["last_sample_timestamp"]

        # First reading for a machine.
        if last_timestamp is None:
            return True

        # If timestamp is unavailable, preserve existing behavior.
        if timestamp is None:
            return True

        elapsed = (timestamp - last_timestamp).total_seconds()

        return elapsed >= self.SAMPLING_INTERVAL_SECONDS

    def build_features(
        self,
        telemetry: Dict[str, Any],
    ) -> Optional[Dict[str, Any]]:

        machine_id = telemetry.get("machine_id")

        if not machine_id:
            raise ValueError("machine_id is required for ML feature generation")

        timestamp = self._parse_timestamp(telemetry.get("timestamp"))

        temperature = self._safe_float(telemetry.get("temperature_c"))

        vibration = self._safe_float(telemetry.get("vibration_mm_s"))

        current = self._safe_float(telemetry.get("current_a"))

        rpm = self._safe_float(telemetry.get("rpm"))

        load_factor = self._safe_float(telemetry.get("load_factor"))

        equipment_type = telemetry.get(
            "equipment_type",
            telemetry.get(
                "machine_type",
                "unknown",
            ),
        )

        machine_history = self.history[machine_id]

        # ----------------------------------------------------
        # Only generate a new ML sample every 10 seconds
        # ----------------------------------------------------

        if not self._should_sample(
            machine_history,
            timestamp,
        ):
            return None

        # ----------------------------------------------------
        # Calculate deltas against previous ML sample
        # ----------------------------------------------------

        previous_temperature = (
            machine_history["temperature_c"][-1]
            if machine_history["temperature_c"]
            else temperature
        )

        previous_vibration = (
            machine_history["vibration_mm_s"][-1]
            if machine_history["vibration_mm_s"]
            else vibration
        )

        previous_current = (
            machine_history["current_a"][-1]
            if machine_history["current_a"]
            else current
        )

        previous_rpm = machine_history["rpm"][-1] if machine_history["rpm"] else rpm

        temperature_delta = temperature - previous_temperature

        vibration_delta = vibration - previous_vibration

        current_delta = current - previous_current

        rpm_delta = rpm - previous_rpm

        # ----------------------------------------------------
        # Add current ML sample to history
        # ----------------------------------------------------

        machine_history["temperature_c"].append(temperature)

        machine_history["vibration_mm_s"].append(vibration)

        machine_history["current_a"].append(current)

        machine_history["rpm"].append(rpm)

        machine_history["last_sample_timestamp"] = timestamp

        # ----------------------------------------------------
        # Rolling means
        # ----------------------------------------------------

        temperature_rolling_mean = sum(machine_history["temperature_c"]) / len(
            machine_history["temperature_c"]
        )

        vibration_rolling_mean = sum(machine_history["vibration_mm_s"]) / len(
            machine_history["vibration_mm_s"]
        )

        current_rolling_mean = sum(machine_history["current_a"]) / len(
            machine_history["current_a"]
        )

        rpm_rolling_mean = sum(machine_history["rpm"]) / len(machine_history["rpm"])

        # ----------------------------------------------------
        # Return exact trained ML feature names
        # ----------------------------------------------------

        return {
            "temperature_c": temperature,
            "vibration_mm_s": vibration,
            "current_a": current,
            "rpm": rpm,
            "load_factor": load_factor,
            "temperature_c_delta": temperature_delta,
            "temperature_c_rolling_mean_10": (temperature_rolling_mean),
            "vibration_mm_s_delta": vibration_delta,
            "vibration_mm_s_rolling_mean_10": (vibration_rolling_mean),
            "current_a_delta": current_delta,
            "current_a_rolling_mean_10": (current_rolling_mean),
            "rpm_delta": rpm_delta,
            "rpm_rolling_mean_10": (rpm_rolling_mean),
            "equipment_type": equipment_type,
        }


# Shared feature service instance
ml_feature_service = MLFeatureService()
