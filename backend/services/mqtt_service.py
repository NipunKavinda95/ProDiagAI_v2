"""
ProDiag AI V2
MQTT Telemetry Service

Responsibilities:
- Connect to the MQTT broker
- Subscribe to all machine telemetry
- Receive and validate telemetry
- Keep the latest reading for each machine
- Pass readings to the backend processing callback
- Start/stop the MQTT background loop

Supports:
- LOCAL MQTT broker
- HiveMQ Cloud over TLS
"""

import json
import os
import ssl
import threading
from pathlib import Path
from typing import Callable, Optional

import paho.mqtt.client as mqtt
from dotenv import load_dotenv

# ============================================================
# PROJECT / ENVIRONMENT CONFIGURATION
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent

# Load the common project-root .env file.
load_dotenv(PROJECT_ROOT / ".env")


# ============================================================
# MQTT CONFIGURATION
# ============================================================

MQTT_MODE = (
    os.getenv(
        "MQTT_MODE",
        "LOCAL",
    )
    .strip()
    .upper()
)

LOCAL_BROKER = os.getenv(
    "MQTT_LOCAL_BROKER",
    "localhost",
).strip()

LOCAL_PORT = int(
    os.getenv(
        "MQTT_LOCAL_PORT",
        "1883",
    )
)

CLOUD_BROKER = os.getenv(
    "MQTT_CLOUD_BROKER",
    "",
).strip()

CLOUD_PORT = int(
    os.getenv(
        "MQTT_CLOUD_PORT",
        "8883",
    )
)

MQTT_USERNAME = os.getenv(
    "MQTT_USERNAME",
    "",
)

MQTT_PASSWORD = os.getenv(
    "MQTT_PASSWORD",
    "",
)

TELEMETRY_TOPIC = "prodiag/factory/+/telemetry"


# ============================================================
# MQTT TELEMETRY SERVICE
# ============================================================


class MQTTService:
    """
    Handles MQTT telemetry ingestion for the ProDiag backend.

    The service itself does not contain health scoring,
    database logic, or AI logic.

    Those responsibilities remain outside this service and
    can be provided through the on_reading callback.
    """

    def __init__(
        self,
        broker: Optional[str] = None,
        port: Optional[int] = None,
        telemetry_topic: str = TELEMETRY_TOPIC,
        on_reading: Optional[Callable[[dict], None]] = None,
    ):
        self.telemetry_topic = telemetry_topic
        self.on_reading = on_reading

        self.latest_sensor_data = {}
        self.data_lock = threading.Lock()

        # --------------------------------------------------------
        # Resolve MQTT connection settings.
        #
        # Explicit broker/port arguments are still supported so
        # existing code that creates MQTTService(broker, port)
        # does not break.
        # --------------------------------------------------------

        if broker is not None:
            self.broker = broker
        elif MQTT_MODE == "CLOUD":
            self.broker = CLOUD_BROKER
        else:
            self.broker = LOCAL_BROKER

        if port is not None:
            self.port = port
        elif MQTT_MODE == "CLOUD":
            self.port = CLOUD_PORT
        else:
            self.port = LOCAL_PORT

        self.client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)

        self.client.on_connect = self._on_connect
        self.client.on_message = self._on_message

        # --------------------------------------------------------
        # HiveMQ Cloud authentication + TLS
        # --------------------------------------------------------

        if MQTT_MODE == "CLOUD":
            if not self.broker:
                raise RuntimeError(
                    "MQTT_CLOUD_BROKER is required when " "MQTT_MODE=CLOUD."
                )

            if not MQTT_USERNAME:
                raise RuntimeError("MQTT_USERNAME is required when " "MQTT_MODE=CLOUD.")

            if not MQTT_PASSWORD:
                raise RuntimeError("MQTT_PASSWORD is required when " "MQTT_MODE=CLOUD.")

            self.client.tls_set(cert_reqs=ssl.CERT_REQUIRED)

            self.client.username_pw_set(
                MQTT_USERNAME,
                MQTT_PASSWORD,
            )

            print("MQTT mode: CLOUD (HiveMQ Cloud)")
            print(f"MQTT broker: " f"{self.broker}:{self.port}")

        else:
            print("MQTT mode: LOCAL")
            print(f"MQTT broker: " f"{self.broker}:{self.port}")

        self.connected = False

    # ========================================================
    # MQTT CONNECT
    # ========================================================

    def _on_connect(
        self,
        client,
        userdata,
        flags,
        reason_code,
        properties,
    ):
        if reason_code == 0:
            self.connected = True

            print("Connected to MQTT broker")

            result = client.subscribe(self.telemetry_topic)

            if result[0] == mqtt.MQTT_ERR_SUCCESS:
                print(f"Subscribed to: " f"{self.telemetry_topic}")
            else:
                print("WARNING: Failed to subscribe " "to telemetry topic")

        else:
            self.connected = False

            print(f"MQTT connection failed. " f"Reason code: {reason_code}")

    # ========================================================
    # MQTT MESSAGE
    # ========================================================

    def _on_message(
        self,
        client,
        userdata,
        message,
    ):
        try:
            payload_text = message.payload.decode("utf-8")

            data = json.loads(payload_text)

            # ------------------------------------------------
            # Basic validation
            # ------------------------------------------------

            machine_id = data.get("machine_id")

            if not machine_id:
                print("MQTT telemetry ignored: " "missing machine_id")
                return

            # ------------------------------------------------
            # Store latest reading
            # ------------------------------------------------

            with self.data_lock:
                self.latest_sensor_data[machine_id] = data

            # ------------------------------------------------
            # Pass reading to backend processing
            # ------------------------------------------------

            if self.on_reading is not None:
                self.on_reading(data)

        except json.JSONDecodeError as error:
            print(f"Could not decode MQTT telemetry: " f"{error}")

        except UnicodeDecodeError as error:
            print(f"Could not decode MQTT payload: " f"{error}")

        except Exception as error:
            print(f"Could not process MQTT telemetry: " f"{error}")

    # ========================================================
    # START
    # ========================================================

    def start(self):
        """
        Connect to MQTT and start the background loop.
        """

        if self.connected:
            return

        self.client.connect(
            self.broker,
            self.port,
            60,
        )

        self.client.loop_start()

    # ========================================================
    # STOP
    # ========================================================

    def stop(self):
        """
        Stop the MQTT background loop and disconnect.
        """

        if not self.connected:
            return

        self.client.loop_stop()
        self.client.disconnect()

        self.connected = False

    # ========================================================
    # GET LATEST READING
    # ========================================================

    def get_latest(self, machine_id: str):
        """
        Return the latest telemetry for one machine.
        """

        with self.data_lock:
            return self.latest_sensor_data.get(machine_id)

    # ========================================================
    # GET ALL LATEST READINGS
    # ========================================================

    def get_all_latest(self):
        """
        Return the latest telemetry for all machines.
        """

        with self.data_lock:
            return dict(self.latest_sensor_data)
