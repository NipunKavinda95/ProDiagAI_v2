import json
import random
import time
from datetime import datetime, timezone

import paho.mqtt.client as mqtt


BROKER = "localhost"
PORT = 1883
TOPIC = "prodiag/factory/motor-01/telemetry"


def generate_sensor_data():
    return {
        "machine_id": "MTR-01",
        "machine_name": "Mixer Drive Motor",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "temperature_c": round(random.uniform(40, 44), 1),
        "vibration_mm_s": round(random.uniform(0.9, 1.5), 2),
        "current_a": round(random.uniform(14, 16), 1),
        "rpm": round(random.uniform(1450, 1500)),
        "status": "RUNNING"
    }


client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
client.connect(BROKER, PORT)
client.loop_start()

print("PLC simulator started. Publishing every 1 second...")

try:
    while True:
        data = generate_sensor_data()
        client.publish(TOPIC, json.dumps(data))
        print(data)
        time.sleep(1)

except KeyboardInterrupt:
    print("\nPLC simulator stopped.")

finally:
    client.loop_stop()
    client.disconnect()