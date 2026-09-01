import json
import random
import time
from datetime import datetime, timezone

import paho.mqtt.client as mqtt


BROKER = "localhost"
PORT = 1883
TOPIC_PREFIX = "prodiag/factory"

MACHINES = [
    {
        "id": "MTR-01",
        "topic": "motor-01",
        "name": "Mixer Drive Motor",
        "temperature": 42,
        "vibration": 1.2,
        "current": 15,
        "rpm": 1480
    },
    {
        "id": "PMP-02",
        "topic": "pump-02",
        "name": "Cooling Water Pump",
        "temperature": 38,
        "vibration": 0.9,
        "current": 12,
        "rpm": 1450
    },
    {
        "id": "CMP-03",
        "topic": "compressor-03",
        "name": "Air Compressor",
        "temperature": 55,
        "vibration": 1.5,
        "current": 18,
        "rpm": 2940
    },
    {
        "id": "CNV-04",
        "topic": "conveyor-04",
        "name": "Packaging Conveyor",
        "temperature": 35,
        "vibration": 0.8,
        "current": 9,
        "rpm": 920
    },
    {
        "id": "FAN-05",
        "topic": "fan-05",
        "name": "Extraction Fan",
        "temperature": 40,
        "vibration": 1.1,
        "current": 11,
        "rpm": 1460
    },
    {
        "id": "GBX-06",
        "topic": "gearbox-06",
        "name": "Conveyor Gearbox",
        "temperature": 48,
        "vibration": 1.7,
        "current": 13,
        "rpm": 980
    }
]

machine_states = {
    machine["id"]: {
        "fault_ticks_remaining": 0,
        "cooldown_ticks_remaining": random.randint(5, 25)
    }
    for machine in MACHINES
}


def normal_sensor_data(machine):
    return {
        "machine_id": machine["id"],
        "machine_name": machine["name"],
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "temperature_c": round(random.uniform(machine["temperature"] - 2, machine["temperature"] + 2), 1),
        "vibration_mm_s": round(random.uniform(machine["vibration"] - 0.2, machine["vibration"] + 0.2), 2),
        "current_a": round(random.uniform(machine["current"] - 1, machine["current"] + 1), 1),
        "rpm": round(random.uniform(machine["rpm"] - 25, machine["rpm"] + 25)),
        "status": "RUNNING"
    }


def fault_sensor_data(machine):
    return {
        "machine_id": machine["id"],
        "machine_name": machine["name"],
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "temperature_c": round(random.uniform(72, 78), 1),
        "vibration_mm_s": round(random.uniform(4.8, 5.8), 2),
        "current_a": round(random.uniform(22, 25), 1),
        "rpm": round(random.uniform(machine["rpm"] * 0.88, machine["rpm"] * 0.94)),
        "status": "FAULT"
    }


def generate_sensor_data(machine):
    state = machine_states[machine["id"]]

    if state["fault_ticks_remaining"] > 0:
        state["fault_ticks_remaining"] -= 1

        if state["fault_ticks_remaining"] == 0:
            state["cooldown_ticks_remaining"] = random.randint(12, 25)
            print(f"{machine['id']} fault event cleared.")

        return fault_sensor_data(machine)

    if state["cooldown_ticks_remaining"] > 0:
        state["cooldown_ticks_remaining"] -= 1

    elif random.random() < 0.08:
        state["fault_ticks_remaining"] = random.randint(12, 18)
        print(f"{machine['id']} random fault event started.")

    return normal_sensor_data(machine)


def on_connect(client, userdata, flags, reason_code, properties):
    if reason_code == 0:
        print("Connected to MQTT broker")


client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
client.on_connect = on_connect
client.connect(BROKER, PORT)
client.loop_start()

print("Six-machine PLC simulator started. Publishing every 1 second...")

try:
    while True:
        for machine in MACHINES:
            data = generate_sensor_data(machine)
            topic = f"{TOPIC_PREFIX}/{machine['topic']}/telemetry"
            client.publish(topic, json.dumps(data))

        print("Published telemetry for 6 machines")
        time.sleep(1)

except KeyboardInterrupt:
    print("\nPLC simulator stopped.")

finally:
    client.loop_stop()
    client.disconnect()