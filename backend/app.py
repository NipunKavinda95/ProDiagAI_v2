import json
import threading

import paho.mqtt.client as mqtt
from flask import Flask, jsonify, request
from flask_cors import CORS

from database import (
    SensorReading,
    SessionLocal,
    initialize_database,
    save_sensor_reading
)
from diagnosis_service import diagnose_fault

BROKER = "localhost"
PORT = 1883
TELEMETRY_TOPIC = "prodiag/factory/+/telemetry"

latest_sensor_data = {}
data_lock = threading.Lock()


def calculate_health(sensor_data):
    temperature = sensor_data.get("temperature_c", 0)
    vibration = sensor_data.get("vibration_mm_s", 0)
    current = sensor_data.get("current_a", 0)

    score = 100
    reasons = []

    if temperature >= 70:
        score -= 35
        reasons.append("High operating temperature")
    elif temperature >= 60:
        score -= 15
        reasons.append("Temperature above normal range")

    if vibration >= 4.5:
        score -= 40
        reasons.append("Critical vibration level")
    elif vibration >= 2.5:
        score -= 20
        reasons.append("Vibration above normal range")

    if current >= 22:
        score -= 20
        reasons.append("High motor current")

    score = max(score, 0)

    if score < 60:
        status = "CRITICAL"
    elif score < 85:
        status = "WARNING"
    else:
        status = "HEALTHY"

    return {
        "health_score": score,
        "health_status": status,
        "risk_reasons": reasons
    }


def enrich_reading(sensor_data):
    reading = sensor_data.copy()
    reading.update(calculate_health(sensor_data))
    return reading


def on_connect(client, userdata, flags, reason_code, properties):
    if reason_code == 0:
        print("Connected to MQTT broker")
        client.subscribe(TELEMETRY_TOPIC)
        print(f"Subscribed to: {TELEMETRY_TOPIC}")
    else:
        print(f"MQTT connection failed: {reason_code}")


def on_message(client, userdata, message):
    try:
        data = json.loads(message.payload.decode("utf-8"))
        enriched_reading = enrich_reading(data)

        save_sensor_reading(enriched_reading)

        with data_lock:
            latest_sensor_data[data["machine_id"]] = data

    except (json.JSONDecodeError, KeyError) as error:
        print(f"Could not process MQTT data: {error}")

    except Exception as error:
        print(f"Could not save sensor reading: {error}")


mqtt_client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
mqtt_client.on_connect = on_connect
mqtt_client.on_message = on_message
mqtt_client.connect(BROKER, PORT)
mqtt_client.loop_start()


app = Flask(__name__)
CORS(app)

initialize_database()


@app.get("/api/health")
def health_check():
    return jsonify({
        "status": "ok",
        "service": "ProDiag AI V2 backend"
    })


@app.get("/api/telemetry")
def get_all_telemetry():
    with data_lock:
        readings = [
            enrich_reading(reading)
            for reading in latest_sensor_data.values()
        ]

    readings.sort(key=lambda reading: reading["machine_id"])

    return jsonify({
        "count": len(readings),
        "machines": readings
    })


@app.get("/api/telemetry/latest")
def get_latest_telemetry():
    with data_lock:
        motor_reading = latest_sensor_data.get("MTR-01")

        if motor_reading is None and latest_sensor_data:
            motor_reading = next(iter(latest_sensor_data.values()))

    if motor_reading is None:
        return jsonify({})

    return jsonify(enrich_reading(motor_reading))


@app.get("/api/machines/<machine_id>/history")
def get_machine_history(machine_id):
    limit = request.args.get("limit", default=60, type=int)
    limit = max(1, min(limit, 500))

    with SessionLocal() as session:
        readings = (
            session.query(SensorReading)
            .filter(SensorReading.machine_id == machine_id)
            .order_by(SensorReading.id.desc())
            .limit(limit)
            .all()
        )

    readings.reverse()

    return jsonify({
        "machine_id": machine_id,
        "count": len(readings),
        "readings": [
            {
                "timestamp": reading.timestamp,
                "temperature_c": reading.temperature_c,
                "vibration_mm_s": reading.vibration_mm_s,
                "current_a": reading.current_a,
                "rpm": reading.rpm,
                "status": reading.status,
                "health_score": reading.health_score,
                "health_status": reading.health_status
            }
            for reading in readings
        ]
    })

@app.get("/api/machines/<machine_id>/diagnosis")
def get_machine_diagnosis(machine_id):
    with data_lock:
        machine_reading = latest_sensor_data.get(machine_id)

    if machine_reading is None:
        return jsonify({
            "error": f"No live telemetry found for {machine_id}"
        }), 404

    enriched_reading = enrich_reading(machine_reading)
    diagnosis = diagnose_fault(enriched_reading)

    return jsonify({
        "machine_id": machine_id,
        "machine_name": enriched_reading["machine_name"],
        "telemetry": enriched_reading,
        "diagnosis": diagnosis
    })

if __name__ == "__main__":
    app.run(debug=True, port=5000)