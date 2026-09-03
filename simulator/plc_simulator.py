"""
ProDiag AI V2
Industrial Factory PLC / Sensor Simulator

Features:
- 20 industrial machines
- Independent machine state machines
- Multiple simultaneous faults
- Progressive degradation
- Persistent machine breakdown
- MQTT telemetry publishing
- MQTT maintenance commands
- Repair -> Restart -> Healthy recovery
"""

import json
import random
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import paho.mqtt.client as mqtt


# ============================================================
# PROJECT PATH
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


# ============================================================
# PROJECT IMPORTS
# ============================================================

from backend.machine_config import MACHINES
from simulator.fault_profiles import (
    get_fault_profile,
    get_fault_stage,
)


# ============================================================
# MQTT CONFIGURATION
# ============================================================

MQTT_BROKER = "localhost"
MQTT_PORT = 1883

TELEMETRY_TOPIC = "prodiag/factory/{machine_id}/telemetry"
COMMAND_TOPIC = "prodiag/factory/+/command"


# ============================================================
# SIMULATION CONFIGURATION
# ============================================================

PUBLISH_INTERVAL = 1.0

# Healthy operating period
HEALTHY_TICKS_MIN = 15
HEALTHY_TICKS_MAX = 35

# Fault progression
DEGRADING_TICKS_MIN = 8
DEGRADING_TICKS_MAX = 14

WARNING_TICKS_MIN = 8
WARNING_TICKS_MAX = 14

CRITICAL_TICKS_MIN = 8
CRITICAL_TICKS_MAX = 15

# Maintenance
REPAIR_TICKS = 8

# Restart
RESTART_TICKS = 5

# ============================================================
# FLEET FAULT DISTRIBUTION
# ============================================================

TARGET_HEALTHY = 12
TARGET_DEGRADING = 3
TARGET_WARNING = 2
TARGET_CRITICAL = 2
TARGET_FAULTED = 1

# Small random variation around the target distribution
FAULT_START_PROBABILITY = 0.08


# ============================================================
# MACHINE STATE
# ============================================================

machine_states = {}


def create_machine_state(machine):
    """
    Create an independent state for each machine.

    Every machine has its own lifecycle, allowing several
    machines to fail independently at the same time.
    """

    return {
        "condition": "HEALTHY",
        "condition_ticks": random.randint(
            HEALTHY_TICKS_MIN,
            HEALTHY_TICKS_MAX,
        ),

        "fault_type": machine.get("fault_type"),
        "fault_stage": None,

        "maintenance_required": False,

        "repair_ticks": 0,
        "restart_ticks": 0,
    }


for machine in MACHINES:
    machine_states[machine["machine_id"]] = create_machine_state(
        machine
    )


# ============================================================
# UTILITY FUNCTIONS
# ============================================================

def random_from_range(value_range, default=0.0):
    """
    Generate a random number from a configured range.

    Supports both:

        (min, max)

    and:

        {"min": min, "max": max}

    This makes the simulator compatible with the current
    machine_config.py.
    """

    if value_range is None:
        return default

    # --------------------------------------------------------
    # Tuple / List
    # --------------------------------------------------------

    if isinstance(value_range, (tuple, list)):

        if len(value_range) >= 2:

            return random.uniform(
                value_range[0],
                value_range[1],
            )

        if len(value_range) == 1:
            return float(value_range[0])

        return default

    # --------------------------------------------------------
    # Dictionary
    # --------------------------------------------------------

    if isinstance(value_range, dict):

        minimum = value_range.get(
            "min",
            default,
        )

        maximum = value_range.get(
            "max",
            minimum,
        )

        return random.uniform(
            minimum,
            maximum,
        )

    # --------------------------------------------------------
    # Numeric value
    # --------------------------------------------------------

    if isinstance(value_range, (int, float)):
        return float(value_range)

    return default


def get_normal_value(
    normal_range,
    field_name,
    default=0.0,
):
    """
    Safely get a normal sensor value.
    """

    value_range = normal_range.get(
        field_name
    )

    return random_from_range(
        value_range,
        default,
    )


def clamp(value, minimum, maximum):
    """
    Keep a value within a specified range.
    """

    return max(
        minimum,
        min(
            maximum,
            value,
        ),
    )


def get_machine_topic(machine_id):
    """
    Build MQTT telemetry topic.
    """

    return TELEMETRY_TOPIC.format(
        machine_id=machine_id
    )


# ============================================================
# DEFAULT CURRENT GENERATION
# ============================================================

def generate_default_current(machine):
    """
    Generate a reasonable current value for machines that
    don't explicitly define a current sensor.

    Gearboxes are the main example in the current configuration.
    """

    machine_type = (
        machine.get("machine_type", "")
        .lower()
    )

    if "gearbox" in machine_type:
        return random.uniform(8.0, 14.0)

    if "fan" in machine_type:
        return random.uniform(6.0, 12.0)

    if "pump" in machine_type:
        return random.uniform(9.0, 16.0)

    if "compressor" in machine_type:
        return random.uniform(15.0, 20.0)

    if "conveyor" in machine_type:
        return random.uniform(7.0, 13.0)

    if "motor" in machine_type:
        return random.uniform(10.0, 17.0)

    return random.uniform(8.0, 15.0)


# ============================================================
# NORMAL MACHINE TELEMETRY
# ============================================================

def generate_normal_reading(machine):
    """
    Generate normal operating telemetry.

    The backend expects:

        temperature_c
        vibration_mm_s
        current_a
        rpm

    Therefore those fields are always published.

    If a machine does not have a physical current sensor,
    a simulated derived current value is provided for backend
    compatibility.
    """

    normal_range = machine.get(
        "normal_range",
        {},
    )

    # --------------------------------------------------------
    # Temperature
    # --------------------------------------------------------

    temperature_c = get_normal_value(
        normal_range,
        "temperature_c",
        default=45.0,
    )

    # --------------------------------------------------------
    # Vibration
    # --------------------------------------------------------

    vibration_mm_s = get_normal_value(
        normal_range,
        "vibration_mm_s",
        default=1.0,
    )

    # --------------------------------------------------------
    # RPM
    # --------------------------------------------------------

    rpm = get_normal_value(
        normal_range,
        "rpm",
        default=1500.0,
    )

    # --------------------------------------------------------
    # Current
    # --------------------------------------------------------

    if "current_a" in normal_range:

        current_a = get_normal_value(
            normal_range,
            "current_a",
            default=10.0,
        )

    else:

        current_a = generate_default_current(
            machine
        )

    # --------------------------------------------------------
    # Build telemetry
    # --------------------------------------------------------

    return {
        "machine_id": machine["machine_id"],
        "machine_name": machine["machine_name"],
        "machine_type": machine.get("machine_type"),

        "department": machine.get(
            "department"
        ),

        "production_line": machine.get(
            "production_line"
        ),

        "area": machine.get(
            "area"
        ),

        "location": machine.get(
            "location"
        ),

        "manufacturer": machine.get(
            "manufacturer"
        ),

        "model": machine.get(
            "model"
        ),

        "criticality": machine.get(
            "criticality"
        ),

        "production_impact": machine.get(
            "production_impact"
        ),

        "operating_hours": machine.get(
            "operating_hours"
        ),

        "timestamp": datetime.now(
            timezone.utc
        ).isoformat(),

        "temperature_c": round(
            temperature_c,
            2,
        ),

        "vibration_mm_s": round(
            vibration_mm_s,
            2,
        ),

        "current_a": round(
            current_a,
            2,
        ),

        "rpm": round(
            rpm,
            0,
        ),

        "status": "RUNNING",

        "condition": "HEALTHY",

        "fault_type": None,

        "fault_stage": None,

        "maintenance_required": False,
    }


# ============================================================
# APPLY FAULT PROFILE
# ============================================================

def apply_fault_progression(
    machine,
    stage,
):
    """
    Apply the configured fault profile to normal telemetry.
    """

    reading = generate_normal_reading(
        machine
    )

    fault_type = machine.get(
        "fault_type"
    )

    if not fault_type:
        return reading

    profile = get_fault_profile(
        fault_type
    )

    if profile is None:
        return reading

    stage_profile = get_fault_stage(
        fault_type,
        stage,
    )

    if stage_profile is None:
        return reading

    # --------------------------------------------------------
    # VIBRATION
    # --------------------------------------------------------

    vibration_multiplier = stage_profile.get(
        "vibration_multiplier",
        1.0,
    )

    reading["vibration_mm_s"] *= (
        vibration_multiplier
    )

    # Sensor noise
    reading["vibration_mm_s"] += random.uniform(
        -0.10,
        0.10,
    )

    # --------------------------------------------------------
    # TEMPERATURE
    # --------------------------------------------------------

    temperature_delta = stage_profile.get(
        "temperature_delta",
        0,
    )

    reading["temperature_c"] += (
        temperature_delta
    )

    reading["temperature_c"] += random.uniform(
        -0.5,
        0.5,
    )

    # --------------------------------------------------------
    # CURRENT
    # --------------------------------------------------------

    current_delta = stage_profile.get(
        "current_delta",
        0,
    )

    reading["current_a"] += (
        current_delta
    )

    reading["current_a"] += random.uniform(
        -0.2,
        0.2,
    )

    # --------------------------------------------------------
    # RPM
    # --------------------------------------------------------

    rpm_delta = stage_profile.get(
        "rpm_delta",
        0,
    )

    reading["rpm"] += rpm_delta

    # --------------------------------------------------------
    # Prevent impossible values
    # --------------------------------------------------------

    reading["temperature_c"] = round(
        max(
            0,
            reading["temperature_c"],
        ),
        2,
    )

    reading["vibration_mm_s"] = round(
        max(
            0,
            reading["vibration_mm_s"],
        ),
        2,
    )

    reading["current_a"] = round(
        max(
            0,
            reading["current_a"],
        ),
        2,
    )

    reading["rpm"] = round(
        max(
            0,
            reading["rpm"],
        ),
        0,
    )

    # --------------------------------------------------------
    # Fault metadata
    # --------------------------------------------------------

    reading["condition"] = stage

    reading["fault_type"] = fault_type

    reading["fault_stage"] = stage

    reading["status"] = "RUNNING"

    reading["maintenance_required"] = False

    return reading


# ============================================================
# FAULTED MACHINE
# ============================================================

def generate_faulted_reading(machine):
    """
    Generate telemetry for a machine that has physically
    broken down.

    FAULTED is persistent until maintenance is commanded.
    """

    reading = generate_normal_reading(
        machine
    )

    state = machine_states[
        machine["machine_id"]
    ]

    fault_type = (
        state.get("fault_type")
        or machine.get("fault_type")
    )

    # --------------------------------------------------------
    # Machine stopped
    # --------------------------------------------------------

    reading["status"] = "FAULT"

    reading["condition"] = "FAULTED"

    reading["fault_type"] = fault_type

    reading["fault_stage"] = "FAULTED"

    reading["maintenance_required"] = True

    # --------------------------------------------------------
    # Physical stopped condition
    # --------------------------------------------------------

    reading["rpm"] = 0

    reading["vibration_mm_s"] = round(
        random.uniform(
            0.05,
            0.25,
        ),
        2,
    )

    reading["current_a"] = round(
        random.uniform(
            0.0,
            0.5,
        ),
        2,
    )

    # Temperature remains elevated
    reading["temperature_c"] = round(
        max(
            35,
            reading["temperature_c"]
            - random.uniform(1, 4),
        ),
        2,
    )

    return reading


# ============================================================
# REPAIRING MACHINE
# ============================================================

def generate_repairing_reading(machine):
    """
    Generate telemetry while maintenance personnel are
    repairing the machine.
    """

    reading = generate_normal_reading(
        machine
    )

    state = machine_states[
        machine["machine_id"]
    ]

    reading["status"] = "MAINTENANCE"

    reading["condition"] = "REPAIRING"

    reading["fault_type"] = state.get(
        "fault_type"
    )

    reading["fault_stage"] = "REPAIRING"

    reading["maintenance_required"] = True

    # Machine remains stopped
    reading["rpm"] = 0

    reading["vibration_mm_s"] = round(
        random.uniform(
            0.05,
            0.20,
        ),
        2,
    )

    reading["current_a"] = round(
        random.uniform(
            0.0,
            0.5,
        ),
        2,
    )

    return reading


# ============================================================
# RESTART MACHINE
# ============================================================

def generate_restart_reading(machine):
    """
    Generate telemetry while a repaired machine is restarting.
    """

    reading = generate_normal_reading(
        machine
    )

    state = machine_states[
        machine["machine_id"]
    ]

    progress = (
        state["restart_ticks"]
        / max(
            1,
            RESTART_TICKS,
        )
    )

    progress = clamp(
        progress,
        0.0,
        1.0,
    )

    reading["status"] = "STARTING"

    reading["condition"] = "RESTART"

    reading["fault_type"] = None

    reading["fault_stage"] = "RESTART"

    reading["maintenance_required"] = False

    # Gradually increase RPM
    normal_rpm = reading["rpm"]

    reading["rpm"] = round(
        normal_rpm * progress,
        0,
    )

    # Startup load
    reading["temperature_c"] = round(
        reading["temperature_c"] + 2,
        2,
    )

    reading["current_a"] = round(
        reading["current_a"] + 2,
        2,
    )

    return reading

def get_fleet_counts():
    """
    Return the current number of machines in each condition.
    """

    counts = {
        "HEALTHY": 0,
        "DEGRADING": 0,
        "WARNING": 0,
        "CRITICAL": 0,
        "FAULTED": 0,
        "REPAIRING": 0,
        "RESTART": 0,
    }

    for state in machine_states.values():

        condition = state.get("condition")

        if condition in counts:
            counts[condition] += 1

    return counts
# ============================================================
# STATE TRANSITIONS
# ============================================================

def transition_machine(machine):
    """
    Progress one machine through the lifecycle while maintaining
    a realistic fleet distribution.

    Target active fleet:

        DEGRADING  -> ~3
        WARNING    -> ~2
        CRITICAL   -> ~2
        FAULTED    -> ~1

    When a severity level reaches its target capacity, machines
    remain at the previous stage until capacity becomes available.

    Lifecycle:

        HEALTHY
            ->
        DEGRADING
            ->
        WARNING
            ->
        CRITICAL
            ->
        FAULTED
            ->
        REPAIRING
            ->
        RESTART
            ->
        HEALTHY
    """

    machine_id = machine["machine_id"]

    state = machine_states[machine_id]

    condition = state["condition"]

    # ========================================================
    # CURRENT FLEET COUNTS
    # ========================================================

    counts = get_fleet_counts()

    # ========================================================
    # HEALTHY
    # ========================================================

    if condition == "HEALTHY":

        state["condition_ticks"] -= 1

        if state["condition_ticks"] <= 0:

            # --------------------------------------------------------
            # Start a new degradation only if DEGRADING has capacity
            # --------------------------------------------------------

            if counts["DEGRADING"] < TARGET_DEGRADING:

                if random.random() < FAULT_START_PROBABILITY:

                    state["condition"] = "DEGRADING"

                    state["fault_stage"] = "DEGRADING"

                    state["condition_ticks"] = random.randint(
                        DEGRADING_TICKS_MIN,
                        DEGRADING_TICKS_MAX,
                    )

                    print(
                        f"[{machine_id}] "
                        f"HEALTHY -> DEGRADING "
                        f"({machine.get('fault_type')})"
                    )

                else:

                    state["condition"] = "HEALTHY"

                    state["fault_stage"] = None

                    state["condition_ticks"] = random.randint(
                        HEALTHY_TICKS_MIN,
                        HEALTHY_TICKS_MAX,
                    )

            else:

                # DEGRADING is already full.
                # Keep this machine HEALTHY.

                state["condition"] = "HEALTHY"

                state["fault_stage"] = None

                state["condition_ticks"] = random.randint(
                    HEALTHY_TICKS_MIN,
                    HEALTHY_TICKS_MAX,
                )

    # ========================================================
    # DEGRADING
    # ========================================================

    elif condition == "DEGRADING":

        state["condition_ticks"] -= 1

        if state["condition_ticks"] <= 0:

            # -----------------------------------------------
            # Only allow progression if WARNING has capacity
            # -----------------------------------------------

            if counts["WARNING"] < TARGET_WARNING:

                state["condition"] = "WARNING"

                state["fault_stage"] = "WARNING"

                state["condition_ticks"] = random.randint(
                    WARNING_TICKS_MIN,
                    WARNING_TICKS_MAX,
                )

                print(
                    f"[{machine_id}] "
                    f"DEGRADING -> WARNING"
                )

            else:

                # WARNING is full.
                # Stay DEGRADING and check again later.

                state["condition_ticks"] = random.randint(
                    5,
                    10,
                )

    # ========================================================
    # WARNING
    # ========================================================

    elif condition == "WARNING":

        state["condition_ticks"] -= 1

        if state["condition_ticks"] <= 0:

            # -----------------------------------------------
            # Only allow progression if CRITICAL has capacity
            # -----------------------------------------------

            if counts["CRITICAL"] < TARGET_CRITICAL:

                state["condition"] = "CRITICAL"

                state["fault_stage"] = "CRITICAL"

                state["condition_ticks"] = random.randint(
                    CRITICAL_TICKS_MIN,
                    CRITICAL_TICKS_MAX,
                )

                print(
                    f"[{machine_id}] "
                    f"WARNING -> CRITICAL"
                )

            else:

                # CRITICAL is full.
                # Stay WARNING.

                state["condition_ticks"] = random.randint(
                    5,
                    10,
                )

    # ========================================================
    # CRITICAL
    # ========================================================

    elif condition == "CRITICAL":

        state["condition_ticks"] -= 1

        if state["condition_ticks"] <= 0:

            # -----------------------------------------------
            # Only allow breakdown if FAULTED capacity exists
            # -----------------------------------------------

            if counts["FAULTED"] < TARGET_FAULTED:

                state["condition"] = "FAULTED"

                state["fault_stage"] = "FAULTED"

                state["maintenance_required"] = True

                state["condition_ticks"] = 0

                print(
                    f"[{machine_id}] "
                    f"CRITICAL -> FAULTED "
                    f"!!! MACHINE BREAKDOWN !!!"
                )

            else:

                # -------------------------------------------
                # FAULTED limit reached.
                #
                # Machine remains CRITICAL.
                # -------------------------------------------

                state["condition_ticks"] = random.randint(
                    5,
                    10,
                )

    # ========================================================
    # FAULTED
    # ========================================================

    elif condition == "FAULTED":

        # ----------------------------------------------------
        # Persistent breakdown.
        #
        # NEVER automatically recover.
        # ----------------------------------------------------

        state["maintenance_required"] = True

    # ========================================================
    # REPAIRING
    # ========================================================

    elif condition == "REPAIRING":

        state["repair_ticks"] += 1

        if state["repair_ticks"] >= REPAIR_TICKS:

            state["condition"] = "RESTART"

            state["fault_stage"] = "RESTART"

            state["repair_ticks"] = 0

            state["restart_ticks"] = 0

            print(
                f"[{machine_id}] "
                f"REPAIRING -> RESTART"
            )

    # ========================================================
    # RESTART
    # ========================================================

    elif condition == "RESTART":

        state["restart_ticks"] += 1

        if state["restart_ticks"] >= RESTART_TICKS:

            state["condition"] = "HEALTHY"

            state["fault_stage"] = None

            state["fault_type"] = machine.get(
                "fault_type"
            )

            state["maintenance_required"] = False

            state["condition_ticks"] = random.randint(
                HEALTHY_TICKS_MIN,
                HEALTHY_TICKS_MAX,
            )

            state["restart_ticks"] = 0

            print(
                f"[{machine_id}] "
                f"RESTART -> HEALTHY"
            )

# ============================================================
# MACHINE TELEMETRY GENERATOR
# ============================================================

def generate_machine_data(machine):
    """
    Generate telemetry according to the machine's current
    condition.
    """

    machine_id = machine[
        "machine_id"
    ]

    state = machine_states[
        machine_id
    ]

    condition = state[
        "condition"
    ]

    # --------------------------------------------------------
    # HEALTHY
    # --------------------------------------------------------

    if condition == "HEALTHY":

        return generate_normal_reading(
            machine
        )

    # --------------------------------------------------------
    # DEGRADING
    # --------------------------------------------------------

    if condition == "DEGRADING":

        return apply_fault_progression(
            machine,
            "DEGRADING",
        )

    # --------------------------------------------------------
    # WARNING
    # --------------------------------------------------------

    if condition == "WARNING":

        return apply_fault_progression(
            machine,
            "WARNING",
        )

    # --------------------------------------------------------
    # CRITICAL
    # --------------------------------------------------------

    if condition == "CRITICAL":

        return apply_fault_progression(
            machine,
            "CRITICAL",
        )

    # --------------------------------------------------------
    # FAULTED
    # --------------------------------------------------------

    if condition == "FAULTED":

        return generate_faulted_reading(
            machine
        )

    # --------------------------------------------------------
    # REPAIRING
    # --------------------------------------------------------

    if condition == "REPAIRING":

        return generate_repairing_reading(
            machine
        )

    # --------------------------------------------------------
    # RESTART
    # --------------------------------------------------------

    if condition == "RESTART":

        return generate_restart_reading(
            machine
        )

    return generate_normal_reading(
        machine
    )


# ============================================================
# MQTT CONNECT CALLBACK
# ============================================================


def on_connect(
    client,
    userdata,
    flags,
    reason_code,
    properties,
):

    if reason_code == 0:

        print(
            "Connected to MQTT broker"
        )

        result = client.subscribe(
            COMMAND_TOPIC
        )

        if result[0] == mqtt.MQTT_ERR_SUCCESS:

            print(
                f"Subscribed to: "
                f"{COMMAND_TOPIC}"
            )

        else:

            print(
                "WARNING: Failed to subscribe "
                "to command topic"
            )

    else:

        print(
            f"MQTT connection failed. "
            f"Reason code: {reason_code}"
        )
# ============================================================
# MQTT MESSAGE CALLBACK
# ============================================================

def on_message(
    client,
    userdata,
    msg,
):
    """
    Process maintenance commands.

    Expected topic:

        prodiag/factory/MTR-01/command

    Expected payload:

        {
            "command": "repair"
        }
    """

    try:

        payload_text = msg.payload.decode(
            "utf-8"
        )

        payload = json.loads(
            payload_text
        )

        topic_parts = msg.topic.split("/")

        if len(topic_parts) < 4:

            print(
                f"[COMMAND] Invalid topic: "
                f"{msg.topic}"
            )

            return

        machine_id = topic_parts[2]

        command = payload.get(
            "command"
        )

        if machine_id not in machine_states:

            print(
                f"[COMMAND] Unknown machine: "
                f"{machine_id}"
            )

            return

        state = machine_states[
            machine_id
        ]

        # ====================================================
        # REPAIR
        # ====================================================

        if command == "repair":

            if state["condition"] == "FAULTED":

                state["condition"] = "REPAIRING"

                state["fault_stage"] = "REPAIRING"

                state["repair_ticks"] = 0

                state["maintenance_required"] = True

                print(
                    f"[{machine_id}] "
                    f"Maintenance command received: "
                    f"FAULTED -> REPAIRING"
                )

            else:

                print(
                    f"[{machine_id}] "
                    f"Repair ignored. "
                    f"Current state: "
                    f"{state['condition']}"
                )

        else:

            print(
                f"[COMMAND] Unknown command: "
                f"{command}"
            )

    except json.JSONDecodeError:

        print(
            f"[COMMAND] Invalid JSON: "
            f"{msg.payload}"
        )

    except Exception as exc:

        print(
            f"[COMMAND] Error: {exc}"
        )


# ============================================================
# MQTT CLIENT
# ============================================================

client = mqtt.Client(
    mqtt.CallbackAPIVersion.VERSION2
)

client.on_connect = on_connect
client.on_message = on_message


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":

    print("=" * 58)
    print(
        "ProDiag AI V2 - Industrial Factory Simulator"
    )
    print("=" * 58)

    print(
        f"Machines: {len(MACHINES)}"
    )

    print(
        "Multiple fault events: ENABLED"
    )

    print(
        "Persistent machine breakdown: ENABLED"
    )

    print(
        "Maintenance recovery: ENABLED"
    )

    # --------------------------------------------------------
    # Connect MQTT
    # --------------------------------------------------------

    try:

        client.connect(
            MQTT_BROKER,
            MQTT_PORT,
            60,
        )

    except Exception as exc:

        print(
            f"Unable to connect to MQTT broker: "
            f"{exc}"
        )

        sys.exit(1)

    # --------------------------------------------------------
    # Start MQTT background loop
    # --------------------------------------------------------

    client.loop_start()

    print(
        f"Publishing every "
        f"{PUBLISH_INTERVAL:.0f} second..."
    )

    print("=" * 58)

    # --------------------------------------------------------
    # Simulation loop
    # --------------------------------------------------------

    try:

        while True:

            for machine in MACHINES:

                # --------------------------------------------
                # Advance machine state
                # --------------------------------------------

                transition_machine(
                    machine
                )

                # --------------------------------------------
                # Generate telemetry
                # --------------------------------------------

                data = generate_machine_data(
                    machine
                )

                # --------------------------------------------
                # MQTT topic
                # --------------------------------------------

                topic = get_machine_topic(
                    machine["machine_id"]
                )

                # --------------------------------------------
                # Publish
                # --------------------------------------------

                client.publish(
                    topic,
                    json.dumps(data),
                    qos=0,
                    retain=False,
                )

            time.sleep(
                PUBLISH_INTERVAL
            )

    except KeyboardInterrupt:

        print()
        print(
            "Stopping ProDiag AI simulator..."
        )

    except Exception as exc:

        print()
        print(
            f"Simulator error: {exc}"
        )

        raise

    finally:

        client.loop_stop()

        client.disconnect()

        print(
            "Simulator stopped."
        )