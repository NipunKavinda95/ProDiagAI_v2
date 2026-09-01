import json

import paho.mqtt.client as mqtt
from flask import Flask, jsonify
from flask_cors import CORS


BROKER = "localhost"
PORT = 1883
TOPIC = "prodiag/factory/motor-01/telemetry"

latest_sensor_data = {}


def on_connect(client, userdata, flags, reason_code, properties):
    if reason_code == 0:
        print("Connected to MQTT broker")
        client.subscribe(TOPIC)
        print(f"Subscribed to: {TOPIC}")
    else:
        print(f"MQTT connection failed: {reason_code}")


def on_message(client, userdata, message):
    global latest_sensor_data

    latest_sensor_data = json.loads(message.payload.decode("utf-8"))
    print("Received MQTT data:", latest_sensor_data)


mqtt_client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
mqtt_client.on_connect = on_connect
mqtt_client.on_message = on_message
mqtt_client.connect(BROKER, PORT)
mqtt_client.loop_start()


app = Flask(__name__)
CORS(app)


@app.get("/api/health")
def health_check():
    return jsonify({
        "status": "ok",
        "service": "ProDiag AI V2 backend"
    })


@app.get("/api/telemetry/latest")
def get_latest_telemetry():
    return jsonify(latest_sensor_data)


if __name__ == "__main__":
    app.run(debug=True, port=5000)