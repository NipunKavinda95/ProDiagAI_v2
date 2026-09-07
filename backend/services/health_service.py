"""
ProDiag AI V2
Health Service

Responsibilities:
- Provide ML-based machine health score
- Determine health status
- Explain health risks
- Enrich telemetry readings with health information

Note:
Machine operational condition is NOT determined here.
The condition state machine remains responsible for:
HEALTHY → DEGRADING → WARNING → CRITICAL → FAULTED → REPAIRING → RESTART → HEALTHY
"""


def calculate_health(
    sensor_data,
    ml_prediction=None,
):
    """
    Calculate machine health information.

    The continuous health score comes from the trained
    XGBoost health-score model.

    Operational machine condition is intentionally NOT
    determined here.
    """

    # --------------------------------------------------------
    # ML health score
    # --------------------------------------------------------

    if ml_prediction is not None:
        health_score = float(
            ml_prediction.get(
                "health_score",
                100.0,
            )
        )

    else:
        # Safe fallback if ML prediction is temporarily
        # unavailable.
        health_score = 100.0

    # Keep score strictly inside 0-100.
    health_score = max(
        0.0,
        min(100.0, health_score),
    )

    # --------------------------------------------------------
    # Health status
    # --------------------------------------------------------
    #
    # This is a presentation/risk classification of the
    # continuous ML health score.
    #
    # It does NOT replace machine operational condition.
    #

    if health_score < 20:
        status = "FAULT"

    elif health_score < 40:
        status = "CRITICAL"

    elif health_score < 60:
        status = "WARNING"

    elif health_score < 80:
        status = "DEGRADING"

    else:
        status = "HEALTHY"

    # --------------------------------------------------------
    # Risk explanations
    # --------------------------------------------------------

    reasons = []

    temperature = sensor_data.get(
        "temperature_c",
        0,
    )

    vibration = sensor_data.get(
        "vibration_mm_s",
        0,
    )

    current = sensor_data.get(
        "current_a",
        0,
    )

    if temperature >= 70:
        reasons.append("High operating temperature")

    elif temperature >= 60:
        reasons.append("Temperature above normal range")

    if vibration >= 4.5:
        reasons.append("Critical vibration level")

    elif vibration >= 2.5:
        reasons.append("Vibration above normal range")

    if current >= 22:
        reasons.append("High motor current")

    return {
        "health_score": round(
            health_score,
            2,
        ),
        "health_status": status,
        "risk_reasons": reasons,
    }


def enrich_reading(
    sensor_data,
    ml_prediction=None,
):
    """
    Add ML-based health information to a telemetry reading
    without modifying the original dictionary.
    """

    reading = sensor_data.copy()

    reading.update(
        calculate_health(
            sensor_data,
            ml_prediction,
        )
    )

    return reading
