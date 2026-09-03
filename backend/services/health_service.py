"""
ProDiag AI V2
Health Service

Responsibilities:
- Calculate machine health score
- Determine health status
- Explain health risks
- Enrich telemetry readings with health information
"""


def calculate_health(sensor_data):
    """
    Calculate a simple 0-100 health score from sensor readings.
    """

    temperature = sensor_data.get("temperature_c", 0)
    vibration = sensor_data.get("vibration_mm_s", 0)
    current = sensor_data.get("current_a", 0)

    score = 100
    reasons = []

    # Temperature
    if temperature >= 70:
        score -= 35
        reasons.append("High operating temperature")

    elif temperature >= 60:
        score -= 15
        reasons.append("Temperature above normal range")

    # Vibration
    if vibration >= 4.5:
        score -= 40
        reasons.append("Critical vibration level")

    elif vibration >= 2.5:
        score -= 20
        reasons.append("Vibration above normal range")

    # Current
    if current >= 22:
        score -= 20
        reasons.append("High motor current")

    score = max(score, 0)

    # Health status
    if score < 60:
        status = "CRITICAL"

    elif score < 85:
        status = "WARNING"

    else:
        status = "HEALTHY"

    return {
        "health_score": score,
        "health_status": status,
        "risk_reasons": reasons,
    }


def enrich_reading(sensor_data):
    """
    Add health information to a telemetry reading
    without modifying the original dictionary.
    """

    reading = sensor_data.copy()

    reading.update(
        calculate_health(sensor_data)
    )

    return reading