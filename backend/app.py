from flask import Flask, jsonify, request
from flask_cors import CORS

from database import (
    SensorReading,
    SessionLocal,
    initialize_database,
    save_sensor_reading,
)

from diagnosis_service import diagnose_fault

from services.mqtt_service import MQTTService
from services.anomaly_service import anomaly_service

from services.health_service import (
    calculate_health,
    enrich_reading,
)

# ============================================================
# APPLICATION CONFIGURATION
# ============================================================

app = Flask(__name__)
CORS(app)


# ============================================================
# DATABASE
# ============================================================

initialize_database()




# ============================================================
# MQTT READING PROCESSOR
# ============================================================
def process_mqtt_reading(data):
    try:
        enriched_reading = enrich_reading(data)

        anomaly_result = anomaly_service.detect(
            enriched_reading
        )

        enriched_reading["is_anomaly"] = (
            anomaly_result["is_anomaly"]
        )

        enriched_reading["anomaly_score"] = (
            anomaly_result["anomaly_score"]
        )

        enriched_reading["anomaly_status"] = (
            anomaly_result["status"]
        )

        enriched_reading["anomaly_reasons"] = (
            anomaly_result["reasons"]
        )

        save_sensor_reading(enriched_reading)

    except Exception as error:
        print(f"Could not process telemetry: {error}")

# ============================================================
# MQTT SERVICE
# ============================================================

mqtt_service = MQTTService(
    on_reading=process_mqtt_reading
)


# Start MQTT after service configuration
mqtt_service.start()


# ============================================================
# HEALTH CHECK
# ============================================================

@app.get("/api/health")
def health_check():

    return jsonify({
        "status": "ok",
        "service": "ProDiag AI V2 backend",
        "mqtt_connected": mqtt_service.connected,
    })


# ============================================================
# ALL LIVE TELEMETRY
# ============================================================

@app.get("/api/telemetry")
def get_all_telemetry():

    readings = (
        mqtt_service.get_all_latest()
    )

    enriched_readings = [
        enrich_reading(reading)
        for reading in readings.values()
    ]

    enriched_readings.sort(
        key=lambda reading: reading["machine_id"]
    )

    return jsonify({
        "count": len(enriched_readings),
        "machines": enriched_readings,
    })


# ============================================================
# LATEST TELEMETRY
# ============================================================

@app.get("/api/telemetry/latest")
def get_latest_telemetry():

    motor_reading = (
        mqtt_service.get_latest("MTR-01")
    )

    # Fallback to any available machine
    if motor_reading is None:

        all_readings = (
            mqtt_service.get_all_latest()
        )

        if all_readings:
            motor_reading = next(
                iter(all_readings.values())
            )

    if motor_reading is None:
        return jsonify({})

    return jsonify(
        enrich_reading(motor_reading)
    )


# ============================================================
# MACHINE SENSOR HISTORY
# ============================================================

@app.get("/api/machines/<machine_id>/history")
def get_machine_history(machine_id):

    limit = request.args.get(
        "limit",
        default=60,
        type=int,
    )

    limit = max(
        1,
        min(limit, 500),
    )

    with SessionLocal() as session:

        readings = (
            session.query(SensorReading)
            .filter(
                SensorReading.machine_id
                == machine_id
            )
            .order_by(
                SensorReading.id.desc()
            )
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
                "health_status": reading.health_status,
            }

            for reading in readings
        ],
    })


# ============================================================
# MACHINE AI DIAGNOSIS
# ============================================================

@app.get("/api/machines/<machine_id>/diagnosis")
def get_machine_diagnosis(machine_id):

    machine_reading = (
        mqtt_service.get_latest(machine_id)
    )

    if machine_reading is None:

        return jsonify({
            "error":
                f"No live telemetry found "
                f"for {machine_id}"
        }), 404

    enriched_reading = (
        enrich_reading(machine_reading)
    )

    diagnosis = diagnose_fault(
        enriched_reading
    )

    return jsonify({
        "machine_id": machine_id,
        "machine_name":
            enriched_reading["machine_name"],
        "telemetry":
            enriched_reading,
        "diagnosis":
            diagnosis,
    })


# ============================================================
# APPLICATION ENTRY POINT
# ============================================================

if __name__ == "__main__":

    app.run(
        debug=True,
        port=5000,
    )