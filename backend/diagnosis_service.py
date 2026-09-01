def diagnose_fault(reading):
    temperature = reading.get("temperature_c", 0)
    vibration = reading.get("vibration_mm_s", 0)
    current = reading.get("current_a", 0)
    health_status = reading.get("health_status", "HEALTHY")

    if vibration >= 4.5 and temperature >= 70:
        return {
            "fault_type": "Probable bearing degradation or lubrication failure",
            "severity": "CRITICAL",
            "confidence": 0.92,
            "summary": (
                "High vibration together with high operating temperature "
                "strongly indicates bearing wear, lubrication failure, or shaft misalignment."
            ),
            "recommended_actions": [
                "Schedule an urgent inspection within the next maintenance window.",
                "Inspect bearing lubrication condition and contamination.",
                "Check shaft alignment and bearing housing temperature.",
                "Reduce load or stop the machine if vibration continues increasing."
            ],
            "estimated_time_to_failure": "4–24 hours if operation continues",
            "escalation_required": True
        }

    if current >= 22 and temperature >= 60:
        return {
            "fault_type": "Probable motor overload",
            "severity": "WARNING",
            "confidence": 0.84,
            "summary": (
                "High current and elevated temperature indicate possible "
                "mechanical resistance, overload, or electrical imbalance."
            ),
            "recommended_actions": [
                "Inspect mechanical load and driven equipment.",
                "Check motor terminals and phase balance.",
                "Review recent production-load changes."
            ],
            "estimated_time_to_failure": "1–3 days if load remains high",
            "escalation_required": False
        }

    if vibration >= 2.5:
        return {
            "fault_type": "Abnormal vibration condition",
            "severity": "WARNING",
            "confidence": 0.76,
            "summary": (
                "Vibration is above the expected operating range and should "
                "be inspected before it develops into a critical fault."
            ),
            "recommended_actions": [
                "Inspect mounting bolts and machine alignment.",
                "Check coupling condition and balance.",
                "Monitor vibration trend closely."
            ],
            "estimated_time_to_failure": "3–7 days",
            "escalation_required": False
        }

    return {
        "fault_type": "No active fault detected",
        "severity": "HEALTHY",
        "confidence": 0.95,
        "summary": "Sensor readings are within expected operating ranges.",
        "recommended_actions": [
            "Continue normal monitoring.",
            "Follow the preventive-maintenance schedule."
        ],
        "estimated_time_to_failure": "No immediate failure risk detected",
        "escalation_required": False
    }