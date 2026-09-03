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
"""

import json
import threading
from typing import Callable, Optional

import paho.mqtt.client as mqtt


# ============================================================
# MQTT CONFIGURATION
# ============================================================

BROKER = "localhost"
PORT = 1883

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
        broker: str = BROKER,
        port: int = PORT,
        telemetry_topic: str = TELEMETRY_TOPIC,
        on_reading: Optional[Callable[[dict], None]] = None,
    ):
        self.broker = broker
        self.port = port
        self.telemetry_topic = telemetry_topic
        self.on_reading = on_reading

        self.latest_sensor_data = {}
        self.data_lock = threading.Lock()

        self.client = mqtt.Client(
            mqtt.CallbackAPIVersion.VERSION2
        )

        self.client.on_connect = self._on_connect
        self.client.on_message = self._on_message

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

            result = client.subscribe(
                self.telemetry_topic
            )

            if result[0] == mqtt.MQTT_ERR_SUCCESS:
                print(
                    f"Subscribed to: "
                    f"{self.telemetry_topic}"
                )
            else:
                print(
                    "WARNING: Failed to subscribe "
                    "to telemetry topic"
                )

        else:
            self.connected = False

            print(
                f"MQTT connection failed. "
                f"Reason code: {reason_code}"
            )

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
            payload_text = message.payload.decode(
                "utf-8"
            )

            data = json.loads(payload_text)

            # ------------------------------------------------
            # Basic validation
            # ------------------------------------------------

            machine_id = data.get("machine_id")

            if not machine_id:
                print(
                    "MQTT telemetry ignored: "
                    "missing machine_id"
                )
                return

            # ------------------------------------------------
            # Store latest reading
            # ------------------------------------------------

            with self.data_lock:
                self.latest_sensor_data[
                    machine_id
                ] = data

            # ------------------------------------------------
            # Pass reading to backend processing
            # ------------------------------------------------

            if self.on_reading is not None:
                self.on_reading(data)

        except json.JSONDecodeError as error:
            print(
                f"Could not decode MQTT telemetry: "
                f"{error}"
            )

        except UnicodeDecodeError as error:
            print(
                f"Could not decode MQTT payload: "
                f"{error}"
            )

        except Exception as error:
            print(
                f"Could not process MQTT telemetry: "
                f"{error}"
            )

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
            return self.latest_sensor_data.get(
                machine_id
            )

    # ========================================================
    # GET ALL LATEST READINGS
    # ========================================================

    def get_all_latest(self):
        """
        Return the latest telemetry for all machines.
        """

        with self.data_lock:
            return dict(
                self.latest_sensor_data
            )