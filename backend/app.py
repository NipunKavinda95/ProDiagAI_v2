import os

from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

from database import (
    Alert,
    FaultEvent,
    SensorReading,
    SessionLocal,
    initialize_database,
    save_sensor_reading,
)

from services.diagnosis_service import diagnose_fault

from services.mqtt_service import MQTTService
from services.anomaly_service import anomaly_service
from services.health_service import enrich_reading
from services.alert_service import alert_service
from services.fault_event_service import fault_event_service
from services.work_order_service import work_order_service
from services.ai_diagnosis_service import ai_diagnosis_service
from services.ml_prediction_service import ml_prediction_service
from services.rag_retrieval_service import retrieve_knowledge
from services.copilot_service import chat_with_engineer
from services.security_service import (
    validate_copilot_question,
    validate_conversation_history,
)
from services.engineer_approval_service import process_engineer_approval
from services.maintenance_agent_service import run_maintenance_agent
from services.factory_settings_service import (
    get_factory_settings,
    initialize_factory_settings,
    update_factory_settings,
)

app = Flask(__name__)

app.config["MAX_CONTENT_LENGTH"] = 1 * 1024 * 1024

limiter = Limiter(
    key_func=get_remote_address,
    app=app,
    default_limits=[],
)

allowed_origins = os.getenv("ALLOWED_ORIGINS", "").strip()

if allowed_origins:
    CORS(
        app,
        resources={
            r"/api/*": {
                "origins": [
                    origin.strip()
                    for origin in allowed_origins.split(",")
                    if origin.strip()
                ]
            }
        },
    )
else:
    CORS(
        app,
        resources={r"/api/*": {"origins": "http://localhost:5173"}},
    )

initialize_database()
initialize_factory_settings()

latest_processed_readings = {}


def process_mqtt_reading(data):
    try:

        # --------------------------------------------------------
        # ML PREDICTIONS
        # --------------------------------------------------------

        ml_prediction = None

        try:
            ml_prediction = ml_prediction_service.predict(data)

        except Exception as ml_error:
            print(f"[ML ERROR] {ml_error}")

        # --------------------------------------------------------
        # HEALTH ENRICHMENT
        # --------------------------------------------------------

        enriched_reading = enrich_reading(
            data,
            ml_prediction,
        )

        # --------------------------------------------------------
        # STORE ML PREDICTIONS
        # --------------------------------------------------------

        if ml_prediction is not None:
            enriched_reading["ml_failure_probability"] = ml_prediction[
                "failure_probability"
            ]
            enriched_reading["ml_failure_within_1h"] = ml_prediction[
                "failure_within_1h"
            ]
            enriched_reading["ml_failure_threshold"] = ml_prediction[
                "failure_threshold"
            ]
            enriched_reading["ml_health_score"] = ml_prediction["health_score"]
            enriched_reading["ml_prediction_status"] = ml_prediction.get(
                "prediction_status", "NORMAL"
            )
        # --------------------------------------------------------
        # FAULT EVENT TRACKING
        # --------------------------------------------------------

        fault_event_service.process_condition_change(enriched_reading)

        # --------------------------------------------------------
        # ANOMALY DETECTION
        # --------------------------------------------------------

        anomaly_result = anomaly_service.detect(enriched_reading)

        # --------------------------------------------------------
        # ALERT PROCESSING
        # --------------------------------------------------------

        if anomaly_result["is_anomaly"] or enriched_reading.get("condition") in [
            "WARNING",
            "CRITICAL",
            "FAULTED",
        ]:
            alert_service.process_anomaly(
                enriched_reading,
                {
                    **anomaly_result,
                    "is_anomaly": True,
                },
            )
        else:
            alert_service.process_anomaly(
                enriched_reading,
                anomaly_result,
            )

        # --------------------------------------------------------
        # STORE ANOMALY RESULTS
        # --------------------------------------------------------

        enriched_reading["is_anomaly"] = anomaly_result["is_anomaly"]

        enriched_reading["anomaly_score"] = anomaly_result["anomaly_score"]

        enriched_reading["anomaly_status"] = anomaly_result["status"]

        enriched_reading["anomaly_reasons"] = anomaly_result["reasons"]

        # --------------------------------------------------------
        # STORE LATEST READING
        # --------------------------------------------------------

        machine_id = enriched_reading["machine_id"]

        latest_processed_readings[machine_id] = enriched_reading

        save_sensor_reading(enriched_reading)

    except Exception as error:
        print(f"Could not process telemetry: {error}")


mqtt_service = MQTTService(on_reading=process_mqtt_reading)

mqtt_service.start()


@app.get("/api/health")
def health_check():
    return jsonify(
        {
            "status": "ok",
            "service": "ProDiag AI V2 backend",
            "mqtt_connected": mqtt_service.connected,
        }
    )


@app.get("/api/settings")
def get_settings():
    try:
        settings = get_factory_settings()

        if settings is None:
            return jsonify({"error": "Factory settings not found."}), 404

        return jsonify(settings)

    except Exception as error:
        print(f"Could not load factory settings: {error}")
        return jsonify({"error": "Could not load factory settings."}), 500


@app.put("/api/settings")
def save_settings():
    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify({"error": "Request body must be a JSON object."}), 400

    try:
        settings = update_factory_settings(data)

        if settings is None:
            return jsonify({"error": "Factory settings could not be saved."}), 500

        return jsonify(settings), 200

    except ValueError as error:
        return jsonify({"error": str(error)}), 400

    except Exception as error:
        print(f"Could not save factory settings: {error}")
        return jsonify({"error": "Could not save factory settings."}), 500


@app.get("/api/telemetry")
def get_all_telemetry():
    readings = list(latest_processed_readings.values())

    readings.sort(key=lambda reading: reading["machine_id"])

    return jsonify(
        {
            "count": len(readings),
            "machines": readings,
        }
    )


@app.get("/api/telemetry/latest")
def get_latest_telemetry():
    motor_reading = latest_processed_readings.get("MTR-01")

    if motor_reading is None and latest_processed_readings:
        motor_reading = next(iter(latest_processed_readings.values()))

    if motor_reading is None:
        return jsonify({})

    return jsonify(motor_reading)


@app.get("/api/machines/<machine_id>/history")
def get_machine_history(machine_id):
    limit = request.args.get(
        "limit",
        default=60,
        type=int,
    )

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

    return jsonify(
        {
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
                    "ml_health_score": reading.ml_health_score,
                    "ml_failure_probability": reading.ml_failure_probability,
                    "ml_failure_within_1h": reading.ml_failure_within_1h,
                }
                for reading in readings
            ],
        }
    )


@app.get("/api/machines/<machine_id>/diagnosis")
def get_machine_diagnosis(machine_id):
    machine_reading = latest_processed_readings.get(machine_id)

    if machine_reading is None:
        return (
            jsonify({"error": (f"No live telemetry found " f"for {machine_id}")}),
            404,
        )

    diagnosis = diagnose_fault(machine_reading)

    return jsonify(
        {
            "machine_id": machine_id,
            "machine_name": machine_reading["machine_name"],
            "telemetry": machine_reading,
            "diagnosis": diagnosis,
        }
    )


@app.get("/api/machines/<machine_id>/ai-diagnosis")
@limiter.limit("10 per minute")
def get_ai_machine_diagnosis(machine_id):
    machine_reading = latest_processed_readings.get(machine_id)

    if machine_reading is None:
        return (
            jsonify({"error": (f"No live telemetry found " f"for {machine_id}")}),
            404,
        )

    anomaly_result = {
        "is_anomaly": machine_reading.get(
            "is_anomaly",
            False,
        ),
        "anomaly_score": machine_reading.get(
            "anomaly_score",
            0.0,
        ),
        "status": machine_reading.get(
            "anomaly_status",
            "NORMAL",
        ),
        "reasons": machine_reading.get(
            "anomaly_reasons",
            [],
        ),
    }

    ai_diagnosis = ai_diagnosis_service.diagnose(
        machine_reading,
        anomaly_result,
    )

    return jsonify(
        {
            "machine_id": machine_id,
            "machine_name": machine_reading["machine_name"],
            "telemetry": machine_reading,
            "anomaly": anomaly_result,
            "ai_diagnosis": ai_diagnosis,
        }
    )


@app.post("/api/machines/<machine_id>/ai-diagnosis/chat")
@limiter.limit("20 per minute")
def chat_machine_diagnosis(machine_id):
    """
    Engineer chat with the AI Maintenance Copilot.

    AI is called only when the engineer explicitly
    sends a question.
    """

    machine_reading = latest_processed_readings.get(machine_id)

    if machine_reading is None:
        return (
            jsonify({"error": (f"No live telemetry found for {machine_id}")}),
            404,
        )

    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return (
            jsonify({"error": "Request body must be a JSON object."}),
            400,
        )

    try:
        question = validate_copilot_question(data.get("question"))

        conversation_history = validate_conversation_history(
            data.get("conversation_history", [])
        )

    except ValueError as error:
        return (
            jsonify({"error": str(error)}),
            400,
        )

    try:
        result = chat_with_engineer(
            machine=machine_reading,
            question=question,
            conversation_history=conversation_history,
            top_k=5,
        )

        return jsonify(
            {
                "machine_id": machine_id,
                "machine_name": machine_reading["machine_name"],
                "question": question,
                "response": result,
            }
        )

    except ValueError as error:
        return (
            jsonify({"error": str(error)}),
            400,
        )

    except Exception as error:
        print(f"[COPILOT CHAT ERROR] " f"{machine_id}: {error}")

        return (
            jsonify(
                {"error": ("AI Maintenance Copilot " "is temporarily unavailable.")}
            ),
            500,
        )


@app.get("/api/alerts")
def get_alerts():
    active_alerts = alert_service.get_active_alerts()

    return jsonify(
        {
            "active_alerts": active_alerts,
            "count": len(active_alerts),
        }
    )


@app.get("/api/alerts/history")
def get_alert_history():
    history = alert_service.get_alert_history()

    return jsonify(
        {
            "alerts": history,
            "count": len(history),
        }
    )


@app.get("/api/fault-events")
def get_fault_events():
    limit = request.args.get(
        "limit",
        default=100,
        type=int,
    )

    limit = max(1, min(limit, 500))

    events = fault_event_service.get_history(limit=limit)

    return jsonify(
        {
            "events": events,
            "count": len(events),
        }
    )


@app.get("/api/machines/<machine_id>/fault-events")
def get_machine_fault_events(machine_id):
    limit = request.args.get(
        "limit",
        default=100,
        type=int,
    )

    limit = max(1, min(limit, 500))

    events = fault_event_service.get_history(
        machine_id=machine_id,
        limit=limit,
    )

    return jsonify(
        {
            "machine_id": machine_id,
            "events": events,
            "count": len(events),
        }
    )


@app.post("/api/work-orders")
def create_work_order():
    data = request.get_json() or {}

    machine_id = data.get("machine_id")
    machine_name = data.get("machine_name")
    title = data.get("title")

    if not machine_id or not machine_name or not title:
        return (
            jsonify({"error": "machine_id, machine_name and title are required"}),
            400,
        )

    # Get the active alert for this machine
    alert_id = None

    active_alert = alert_service.get_machine_alert(machine_id)

    if active_alert:
        alert_id = active_alert.get("alert_id")

    # Get the latest fault event for this machine
    fault_event_id = None

    fault_events = fault_event_service.get_history(
        machine_id=machine_id,
        limit=1,
    )

    if fault_events:
        fault_event_id = fault_events[0].get("event_id")

    print(
        f"[WORK ORDER LINK] "
        f"{machine_id} -> "
        f"alert_id={alert_id}, "
        f"fault_event_id={fault_event_id}"
    )

    work_order = work_order_service.create_work_order(
        machine_id=machine_id,
        machine_name=machine_name,
        title=title,
        description=data.get("description"),
        priority=data.get("priority", "MEDIUM"),
        fault_type=data.get("fault_type"),
        fault_event_id=fault_event_id,
        alert_id=alert_id,
        ai_diagnosis=data.get("ai_diagnosis"),
        ai_recommendation=data.get("ai_recommendation"),
    )

    if work_order is None:
        return jsonify({"error": "Could not create work order"}), 500

    return jsonify(work_order), 201


@app.get("/api/work-orders")
def get_work_orders():
    machine_id = request.args.get("machine_id")
    status = request.args.get("status")

    work_orders = work_order_service.get_work_orders(
        machine_id=machine_id,
        status=status,
    )

    return jsonify(
        {
            "work_orders": work_orders,
            "count": len(work_orders),
        }
    )


@app.patch("/api/work-orders/<int:work_order_id>/status")
def update_work_order_status(work_order_id):
    data = request.get_json() or {}

    status = data.get("status")
    engineer_name = data.get("engineer_name")

    if not status:
        return jsonify({"error": "Status is required"}), 400

    # Completing a work order requires the engineer name so it is
    # persisted in the database and remains available after reload.
    if status == "COMPLETED" and not str(engineer_name or "").strip():
        return (
            jsonify(
                {"error": "engineer_name is required when completing a work order"}
            ),
            400,
        )

    work_order = work_order_service.update_status(
        work_order_id,
        status,
        engineer_name=str(engineer_name).strip() if engineer_name else None,
    )

    if work_order is None:
        return jsonify({"error": "Work order not found"}), 404

    return jsonify(work_order)


@app.post("/api/maintenance/agent")
def maintenance_agent():
    data = request.get_json() or {}

    machine = data.get("machine")
    request_text = data.get("request", "Create a maintenance plan")
    diagnosis = data.get("diagnosis")

    if not machine:
        return jsonify({"error": "machine is required"}), 400

    if not isinstance(machine, dict):
        return jsonify({"error": "machine must be an object"}), 400

    if not isinstance(request_text, str) or not request_text.strip():
        return jsonify({"error": "request must be text"}), 400

    try:
        result = run_maintenance_agent(
            machine=machine,
            request=request_text,
            diagnosis=diagnosis,
        )

        return jsonify(result), 200

    except ValueError as error:
        return jsonify({"error": str(error)}), 400

    except Exception as error:
        print(f"Maintenance Agent failed: {error}")
        return jsonify({"error": "Could not run Maintenance Agent"}), 500


@app.post("/api/maintenance/approve")
def approve_maintenance_proposal():
    data = request.get_json() or {}

    proposal = data.get("proposal")
    decision = data.get("decision")
    engineer_name = data.get("engineer_name")
    comment = data.get("comment", "")

    if not proposal:
        return jsonify({"error": "proposal is required"}), 400

    if not decision:
        return jsonify({"error": "decision is required"}), 400

    if not engineer_name:
        return jsonify({"error": "engineer_name is required"}), 400

    try:
        approval = process_engineer_approval(
            proposal=proposal,
            decision=decision,
            engineer_name=engineer_name,
            comment=comment,
        )

        work_order = None

        if approval["proposal_status"] == "APPROVED":
            machine_id = proposal.get("machine_id")

            # Link the current active alert to the Work Order.
            alert_id = None

            active_alert = alert_service.get_machine_alert(machine_id)

            if active_alert:
                alert_id = active_alert.get("alert_id")

            # Link the latest fault event to the Work Order.
            fault_event_id = None

            fault_events = fault_event_service.get_history(
                machine_id=machine_id,
                limit=1,
            )

            if fault_events:
                fault_event_id = fault_events[0].get("event_id")

            print(
                f"[AGENT WORK ORDER LINK] "
                f"{machine_id} -> "
                f"alert_id={alert_id}, "
                f"fault_event_id={fault_event_id}"
            )

            approved_proposal = {
                **proposal,
                "proposal_status": "APPROVED",
                "comment": comment,
                "alert_id": alert_id,
                "fault_event_id": fault_event_id,
                "engineer_name": engineer_name,
                "approved_at": approval["approved_at"],
            }

            work_order = work_order_service.create_from_approved_proposal(
                approved_proposal
            )

            if work_order is None:
                return (
                    jsonify(
                        {
                            "error": "Approval succeeded but work order creation failed.",
                            "approval": approval,
                        }
                    ),
                    500,
                )

        return (
            jsonify(
                {
                    "approval": approval,
                    "work_order": work_order,
                }
            ),
            200,
        )

    except ValueError as error:
        return jsonify({"error": str(error)}), 400

    except Exception as error:
        print(f"Maintenance approval failed: {error}")
        return jsonify({"error": "Could not process maintenance approval"}), 500


@app.route("/api/rag/search", methods=["GET"])
@limiter.limit("30 per minute")
def rag_search():
    query = request.args.get("q", "").strip()

    if not query:
        return jsonify({"error": "Query parameter 'q' is required."}), 400

    try:
        top_k = int(request.args.get("top_k", 5))

        top_k = max(1, min(top_k, 10))

        results = retrieve_knowledge(
            query=query,
            top_k=top_k,
        )

        return jsonify(
            {
                "query": query,
                "results": results,
                "count": len(results),
            }
        )

    except Exception as error:
        print(f"RAG search error: {error}")

        return jsonify({"error": "RAG retrieval failed."}), 500


@app.errorhandler(400)
def handle_bad_request(error):
    return jsonify({"error": "Bad request."}), 400


@app.errorhandler(404)
def handle_not_found(error):
    return jsonify({"error": "API endpoint not found."}), 404


@app.errorhandler(405)
def handle_method_not_allowed(error):
    return jsonify({"error": "HTTP method not allowed."}), 405


@app.errorhandler(413)
def handle_request_too_large(error):
    return jsonify({"error": "Request payload is too large."}), 413


@app.errorhandler(500)
def handle_internal_error(error):
    print(f"[INTERNAL SERVER ERROR] {error}")

    return jsonify({"error": "Internal server error."}), 500


if __name__ == "__main__":
    app.run(
        debug=True,
        use_reloader=False,
        port=5000,
    )
