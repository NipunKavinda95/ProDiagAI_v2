import json
import os

from dotenv import load_dotenv
from openai import OpenAI

from services.security_service import validate_ai_diagnosis_response

load_dotenv()


class AIDiagnosisService:
    def __init__(self):
        api_key = os.getenv("OPENAI_API_KEY")

        if not api_key:
            raise RuntimeError("OPENAI_API_KEY is not configured")

        self.client = OpenAI(api_key=api_key)

        configured_model = os.getenv(
            "OPENAI_MODEL",
            "",
        ).strip()

        self.model = configured_model or "gpt-5.6-luna"

    def diagnose(self, reading, anomaly_result):
        machine_data = {
            "machine_id": reading.get("machine_id"),
            "machine_name": reading.get("machine_name"),
            "machine_type": reading.get("machine_type"),
            "department": reading.get("department"),
            "production_line": reading.get("production_line"),
            "condition": reading.get("condition"),
            "fault_type": reading.get("fault_type"),
            "temperature_c": reading.get("temperature_c"),
            "vibration_mm_s": reading.get("vibration_mm_s"),
            "current_a": reading.get("current_a"),
            "rpm": reading.get("rpm"),
            "health_score": reading.get("health_score"),
            "health_status": reading.get("health_status"),
            "anomaly_score": anomaly_result.get("anomaly_score"),
            "anomaly_status": anomaly_result.get("status"),
            "anomaly_reasons": anomaly_result.get(
                "reasons",
                [],
            ),
        }

        system_prompt = """
You are ProDiag AI, an industrial predictive
maintenance diagnostic assistant.

Analyze the supplied machine telemetry and
anomaly evidence.

Do not invent sensor values, machine facts,
maintenance history, or fault confirmation.

Distinguish between:

- observed evidence
- probable fault
- recommended maintenance action

A probable fault is a hypothesis, not a confirmed
failure unless the supplied evidence supports that
conclusion.

Use the machine condition, health score, sensor
values, anomaly evidence, and fault type when
available.

If evidence is insufficient, explicitly state that
the evidence is insufficient.

Recommendations must be practical maintenance
inspection or safety actions.

Do not recommend bypassing safety procedures.
"""

        user_prompt = "Analyze this machine data:\n\n" + json.dumps(
            machine_data,
            indent=2,
        )

        diagnosis_schema = {
            "type": "object",
            "additionalProperties": False,
            "properties": {
                "diagnosis": {"type": "string"},
                "probable_fault": {"type": "string"},
                "confidence": {
                    "type": "integer",
                    "minimum": 0,
                    "maximum": 100,
                },
                "evidence": {
                    "type": "array",
                    "items": {"type": "string"},
                },
                "recommended_actions": {
                    "type": "array",
                    "items": {"type": "string"},
                },
                "urgency": {
                    "type": "string",
                    "enum": [
                        "LOW",
                        "MEDIUM",
                        "HIGH",
                        "CRITICAL",
                    ],
                },
                "requires_escalation": {"type": "boolean"},
            },
            "required": [
                "diagnosis",
                "probable_fault",
                "confidence",
                "evidence",
                "recommended_actions",
                "urgency",
                "requires_escalation",
            ],
        }

        try:
            response = self.client.responses.create(
                model=self.model,
                instructions=system_prompt,
                input=user_prompt,
                text={
                    "format": {
                        "type": "json_schema",
                        "name": "maintenance_diagnosis",
                        "description": (
                            "Structured industrial " "maintenance diagnosis."
                        ),
                        "schema": diagnosis_schema,
                        "strict": True,
                    }
                },
            )

            output_text = (response.output_text or "").strip()

            if not output_text:
                raise ValueError("AI returned an empty diagnosis.")

            result = json.loads(output_text)
            result = validate_ai_diagnosis_response(result)
            return result

        except json.JSONDecodeError as error:
            print(f"[AI DIAGNOSIS JSON ERROR] " f"{error}")

            return {
                "diagnosis": ("AI returned an invalid " "diagnosis format."),
                "probable_fault": "Unknown",
                "confidence": 0,
                "evidence": [],
                "recommended_actions": [],
                "urgency": "LOW",
                "requires_escalation": False,
            }

        except Exception as error:
            print(f"[AI DIAGNOSIS ERROR] " f"{error}")

            return {
                "diagnosis": ("AI diagnosis temporarily " "unavailable."),
                "probable_fault": "Unknown",
                "confidence": 0,
                "evidence": [],
                "recommended_actions": [],
                "urgency": "LOW",
                "requires_escalation": False,
            }


ai_diagnosis_service = AIDiagnosisService()
