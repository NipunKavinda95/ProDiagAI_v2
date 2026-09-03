MACHINE_PROFILES = {
    "MTR-01": {
        "degrading_fault": "Early signs of motor mechanical degradation",
        "warning_fault": "Probable motor bearing or alignment issue",
        "critical_fault": "Probable motor bearing degradation or lubrication failure",
        "degrading_actions": [
            "Continue monitoring vibration and temperature trends",
            "Inspect motor condition at the next planned maintenance opportunity",
            "Check for early bearing or alignment deterioration"
        ],
        "warning_actions": [
            "Inspect motor bearings and coupling",
            "Check shaft alignment and mounting condition",
            "Monitor vibration and temperature trend closely"
        ],
        "critical_actions": [
            "Stop or isolate the motor if vibration continues increasing",
            "Inspect bearings, lubrication and shaft alignment",
            "Check motor temperature and mechanical load immediately"
        ]
    },

    "PMP-02": {
        "degrading_fault": "Early signs of pump mechanical degradation",
        "warning_fault": "Probable pump cavitation or bearing condition",
        "critical_fault": "Probable pump bearing failure or severe cavitation",
        "degrading_actions": [
            "Monitor vibration and pump operating temperature",
            "Check suction and discharge conditions during planned inspection",
            "Inspect pump condition at the next maintenance opportunity"
        ],
        "warning_actions": [
            "Inspect pump bearings and coupling",
            "Check suction pressure and possible cavitation conditions",
            "Verify pump alignment and operating load"
        ],
        "critical_actions": [
            "Reduce load or stop the pump if vibration continues increasing",
            "Inspect bearings, coupling and pump alignment immediately",
            "Check for severe cavitation or abnormal operating conditions"
        ]
    },

    "CMP-03": {
        "degrading_fault": "Early signs of compressor operating degradation",
        "warning_fault": "Probable compressor overload",
        "critical_fault": "Probable compressor overload or overheating",
        "degrading_actions": [
            "Continue monitoring compressor temperature and current",
            "Review operating load and pressure conditions",
            "Inspect compressor condition during the next maintenance opportunity"
        ],
        "warning_actions": [
            "Inspect compressor operating load",
            "Check cooling and ventilation conditions",
            "Review current and temperature trends for continued increase"
        ],
        "critical_actions": [
            "Reduce compressor load or stop operation if temperature continues increasing",
            "Inspect cooling system and compressor load immediately",
            "Check electrical current and operating pressure conditions"
        ]
    },

    "CNV-04": {
        "degrading_fault": "Early signs of conveyor drive degradation",
        "warning_fault": "Probable conveyor belt alignment or drive resistance issue",
        "critical_fault": "Probable conveyor mechanical drive failure",
        "degrading_actions": [
            "Monitor vibration and conveyor speed trend",
            "Inspect belt tracking during the next maintenance opportunity",
            "Check conveyor drive and mounting condition"
        ],
        "warning_actions": [
            "Inspect belt alignment and tracking",
            "Check drive coupling, rollers and mounting condition",
            "Investigate increasing vibration or reduced conveyor speed"
        ],
        "critical_actions": [
            "Stop the conveyor if vibration or speed reduction continues",
            "Inspect belt, rollers, coupling and drive system immediately",
            "Check for mechanical obstruction or excessive resistance"
        ]
    },

    "FAN-05": {
        "degrading_fault": "Early signs of fan mechanical degradation",
        "warning_fault": "Probable fan imbalance or bearing condition",
        "critical_fault": "Probable fan bearing failure or severe imbalance",
        "degrading_actions": [
            "Continue monitoring fan vibration trend",
            "Inspect fan mounting and mechanical condition",
            "Check for early signs of imbalance during planned maintenance"
        ],
        "warning_actions": [
            "Inspect fan balance and mounting condition",
            "Check fan bearings and shaft alignment",
            "Monitor vibration trend for continued increase"
        ],
        "critical_actions": [
            "Stop the fan if vibration continues increasing",
            "Inspect bearings, shaft and fan balance immediately",
            "Check mounting bolts and mechanical integrity"
        ]
    },

    "GBX-06": {
        "degrading_fault": "Early signs of gearbox wear",
        "warning_fault": "Probable gearbox gear or bearing wear",
        "critical_fault": "Probable gearbox gear or bearing failure",
        "degrading_actions": [
            "Continue monitoring gearbox vibration and temperature",
            "Check lubrication condition during planned maintenance",
            "Monitor vibration trend for continued deterioration"
        ],
        "warning_actions": [
            "Inspect gearbox lubrication condition",
            "Check gears, bearings and shaft alignment",
            "Monitor vibration and temperature closely"
        ],
        "critical_actions": [
            "Reduce load or stop the gearbox if vibration continues increasing",
            "Inspect gears, bearings and lubrication immediately",
            "Check gearbox temperature and mechanical condition"
        ]
    }
}


def diagnose_fault(reading):
    machine_id = reading.get("machine_id", "")
    temperature = reading.get("temperature_c", 0)
    vibration = reading.get("vibration_mm_s", 0)
    current = reading.get("current_a", 0)
    rpm = reading.get("rpm", 0)
    health_status = reading.get("health_status", "HEALTHY")

    profile = MACHINE_PROFILES.get(machine_id)

    if profile is None:
        profile = {
            "degrading_fault": "Early signs of machine degradation",
            "warning_fault": "Abnormal machine operating condition",
            "critical_fault": "Severe machine health deterioration",
            "degrading_actions": [
                "Continue monitoring sensor trends",
                "Inspect machine at the next planned maintenance opportunity",
                "Review recent operating conditions"
            ],
            "warning_actions": [
                "Inspect machine condition",
                "Review abnormal sensor readings",
                "Continue monitoring the machine trend"
            ],
            "critical_actions": [
                "Stop or isolate the machine if the condition worsens",
                "Perform an immediate maintenance inspection",
                "Escalate the condition to maintenance personnel"
            ]
        }

    # ---------------------------------------------------------
    # CRITICAL
    # ---------------------------------------------------------
    if health_status == "CRITICAL":
        if machine_id == "MTR-01":
            fault = profile["critical_fault"]
            summary = (
                "High vibration and elevated thermal loading indicate "
                "a potentially severe motor mechanical condition."
            )
        elif machine_id == "PMP-02":
            fault = profile["critical_fault"]
            summary = (
                "Severe vibration or thermal stress indicates a potentially "
                "serious pump mechanical or hydraulic condition."
            )
        elif machine_id == "CMP-03":
            fault = profile["critical_fault"]
            summary = (
                "High operating load together with elevated temperature "
                "indicates a potentially severe compressor condition."
            )
        elif machine_id == "CNV-04":
            fault = profile["critical_fault"]
            summary = (
                "High vibration and reduced operating speed indicate "
                "a potentially severe conveyor drive problem."
            )
        elif machine_id == "FAN-05":
            fault = profile["critical_fault"]
            summary = (
                "Severe vibration indicates a potentially dangerous "
                "fan imbalance or bearing condition."
            )
        elif machine_id == "GBX-06":
            fault = profile["critical_fault"]
            summary = (
                "High vibration and temperature indicate potentially "
                "severe gearbox gear or bearing deterioration."
            )
        else:
            fault = profile["critical_fault"]
            summary = (
                "Multiple sensor indicators show severe machine health deterioration."
            )

        return {
            "condition": "CRITICAL",
            "probable_fault": fault,
            "confidence": 0.90,
            "recommended_actions": profile["critical_actions"],
            "estimated_time_to_failure": "4–24 hours if operation continues",
            "requires_escalation": True
        }

    # ---------------------------------------------------------
    # WARNING
    # ---------------------------------------------------------
    if health_status == "WARNING":
        if machine_id == "MTR-01" and current >= 19:
            confidence = 0.84
        elif machine_id == "PMP-02" and vibration >= 2.5:
            confidence = 0.82
        elif machine_id == "CMP-03" and current >= 19:
            confidence = 0.86
        elif machine_id == "CNV-04" and (vibration >= 2.5 or rpm < 900):
            confidence = 0.83
        elif machine_id == "FAN-05" and vibration >= 2.5:
            confidence = 0.82
        elif machine_id == "GBX-06" and (vibration >= 2.5 or temperature >= 60):
            confidence = 0.84
        else:
            confidence = 0.70

        return {
            "condition": "WARNING",
            "probable_fault": profile["warning_fault"],
            "confidence": confidence,
            "recommended_actions": profile["warning_actions"],
            "estimated_time_to_failure": "1–7 days depending on trend",
            "requires_escalation": False
        }

    # ---------------------------------------------------------
    # DEGRADING
    # ---------------------------------------------------------
    if health_status == "DEGRADING":
        return {
            "condition": "DEGRADING",
            "probable_fault": profile["degrading_fault"],
            "confidence": 0.68,
            "recommended_actions": profile["degrading_actions"],
            "estimated_time_to_failure": "7+ days",
            "requires_escalation": False
        }

    # ---------------------------------------------------------
    # HEALTHY
    # ---------------------------------------------------------
    return {
        "condition": "HEALTHY",
        "probable_fault": "No significant fault detected",
        "confidence": 0.95,
        "recommended_actions": [
            "Continue normal monitoring",
            "Follow the preventive-maintenance schedule"
        ],
        "estimated_time_to_failure": "No immediate failure risk detected",
        "requires_escalation": False
    }