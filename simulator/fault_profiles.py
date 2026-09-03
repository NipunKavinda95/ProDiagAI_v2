"""
ProDiag AI V2
Industrial Fault Profiles

Defines realistic sensor behaviour for different machine fault types.
The simulator uses these profiles to progressively inject faults.
"""


FAULT_PROFILES = {

    # =========================================================
    # MOTOR — BEARING WEAR
    # =========================================================

    "bearing_wear": {
        "name": "Bearing Wear",

        "description": (
            "Progressive bearing deterioration causing increasing "
            "vibration, temperature and motor current."
        ),

        "progression": {
            "DEGRADING": {
                "vibration_multiplier": 1.35,
                "temperature_delta": 5,
                "current_delta": 1.5,
                "rpm_delta": -15,
            },

            "WARNING": {
                "vibration_multiplier": 2.0,
                "temperature_delta": 12,
                "current_delta": 3.5,
                "rpm_delta": -40,
            },

            "CRITICAL": {
                "vibration_multiplier": 3.2,
                "temperature_delta": 25,
                "current_delta": 7,
                "rpm_delta": -80,
            },

            "FAULTED": {
                "vibration_multiplier": 3.8,
                "temperature_delta": 30,
                "current_delta": 9,
                "rpm_delta": -120,
            },
        },

        "failure_message": (
            "Motor stopped due to severe bearing degradation."
        ),
    },


    # =========================================================
    # PUMP — CAVITATION
    # =========================================================

    "cavitation": {
        "name": "Pump Cavitation",

        "description": (
            "Hydraulic instability producing fluctuating vibration "
            "followed by increased temperature and operating stress."
        ),

        "progression": {
            "DEGRADING": {
                "vibration_multiplier": 1.6,
                "temperature_delta": 2,
                "current_delta": 0.5,
                "rpm_delta": -5,
            },

            "WARNING": {
                "vibration_multiplier": 2.4,
                "temperature_delta": 8,
                "current_delta": 1.5,
                "rpm_delta": -20,
            },

            "CRITICAL": {
                "vibration_multiplier": 3.5,
                "temperature_delta": 18,
                "current_delta": 4,
                "rpm_delta": -50,
            },

            "FAULTED": {
                "vibration_multiplier": 4.0,
                "temperature_delta": 22,
                "current_delta": 5,
                "rpm_delta": -100,
            },
        },

        "failure_message": (
            "Pump stopped due to severe cavitation and hydraulic instability."
        ),
    },


    # =========================================================
    # COMPRESSOR — OVERLOAD
    # =========================================================

    "overload": {
        "name": "Compressor Overload",

        "description": (
            "Increasing operating load causes motor current and "
            "compressor temperature to rise progressively."
        ),

        "progression": {
            "DEGRADING": {
                "vibration_multiplier": 1.1,
                "temperature_delta": 4,
                "current_delta": 1.5,
                "rpm_delta": -10,
            },

            "WARNING": {
                "vibration_multiplier": 1.35,
                "temperature_delta": 10,
                "current_delta": 3.5,
                "rpm_delta": -35,
            },

            "CRITICAL": {
                "vibration_multiplier": 1.6,
                "temperature_delta": 20,
                "current_delta": 7,
                "rpm_delta": -70,
            },

            "FAULTED": {
                "vibration_multiplier": 1.8,
                "temperature_delta": 28,
                "current_delta": 10,
                "rpm_delta": -120,
            },
        },

        "failure_message": (
            "Compressor stopped after reaching severe overload conditions."
        ),
    },


    # =========================================================
    # CONVEYOR — BELT MISALIGNMENT
    # =========================================================

    "belt_misalignment": {
        "name": "Belt Misalignment",

        "description": (
            "Progressive belt tracking problems increase vibration "
            "while reducing conveyor speed."
        ),

        "progression": {
            "DEGRADING": {
                "vibration_multiplier": 1.5,
                "temperature_delta": 2,
                "current_delta": 0.5,
                "rpm_delta": -25,
            },

            "WARNING": {
                "vibration_multiplier": 2.3,
                "temperature_delta": 6,
                "current_delta": 1.5,
                "rpm_delta": -60,
            },

            "CRITICAL": {
                "vibration_multiplier": 3.3,
                "temperature_delta": 12,
                "current_delta": 3,
                "rpm_delta": -110,
            },

            "FAULTED": {
                "vibration_multiplier": 3.8,
                "temperature_delta": 18,
                "current_delta": 4,
                "rpm_delta": -180,
            },
        },

        "failure_message": (
            "Conveyor stopped due to severe belt misalignment."
        ),
    },


    # =========================================================
    # FAN — IMBALANCE
    # =========================================================

    "fan_imbalance": {
        "name": "Fan Imbalance",

        "description": (
            "Rotating imbalance causes progressively increasing "
            "vibration and mechanical stress."
        ),

        "progression": {
            "DEGRADING": {
                "vibration_multiplier": 1.45,
                "temperature_delta": 2,
                "current_delta": 0.5,
                "rpm_delta": -5,
            },

            "WARNING": {
                "vibration_multiplier": 2.2,
                "temperature_delta": 6,
                "current_delta": 1.5,
                "rpm_delta": -20,
            },

            "CRITICAL": {
                "vibration_multiplier": 3.3,
                "temperature_delta": 14,
                "current_delta": 3,
                "rpm_delta": -50,
            },

            "FAULTED": {
                "vibration_multiplier": 4.0,
                "temperature_delta": 20,
                "current_delta": 4,
                "rpm_delta": -100,
            },
        },

        "failure_message": (
            "Fan stopped due to severe mechanical imbalance."
        ),
    },


    # =========================================================
    # GEARBOX — GEAR WEAR
    # =========================================================

    "gear_wear": {
        "name": "Gear Wear",

        "description": (
            "Progressive gear and bearing wear produces increasing "
            "vibration followed by rising gearbox temperature."
        ),

        "progression": {
            "DEGRADING": {
                "vibration_multiplier": 1.3,
                "temperature_delta": 4,
                "current_delta": 0.5,
                "rpm_delta": -10,
            },

            "WARNING": {
                "vibration_multiplier": 2.0,
                "temperature_delta": 10,
                "current_delta": 1.5,
                "rpm_delta": -25,
            },

            "CRITICAL": {
                "vibration_multiplier": 3.2,
                "temperature_delta": 22,
                "current_delta": 3,
                "rpm_delta": -60,
            },

            "FAULTED": {
                "vibration_multiplier": 3.8,
                "temperature_delta": 28,
                "current_delta": 4,
                "rpm_delta": -120,
            },
        },

        "failure_message": (
            "Gearbox stopped due to severe gear or bearing deterioration."
        ),
    },
}


def get_fault_profile(fault_type):
    """
    Return the fault profile for a given fault type.
    """
    return FAULT_PROFILES.get(fault_type)


def get_fault_stage(fault_type, stage):
    """
    Return the sensor progression settings for a specific
    fault type and machine health stage.
    """
    profile = get_fault_profile(fault_type)

    if profile is None:
        return None

    return profile["progression"].get(stage)


def get_fault_name(fault_type):
    """
    Return the human-readable fault name.
    """
    profile = get_fault_profile(fault_type)

    if profile is None:
        return "Unknown Fault"

    return profile["name"]