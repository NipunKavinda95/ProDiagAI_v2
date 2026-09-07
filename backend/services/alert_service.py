from datetime import datetime, timezone
import json

from database import Alert, SessionLocal


class AlertService:
    def __init__(self):
        self.active_alerts = {}
        self.alert_history = []
        self.next_alert_id = 1

        self._load_existing_alerts()

    # ============================================================
    # LOAD EXISTING ALERTS FROM DATABASE
    # ============================================================

    def _load_existing_alerts(self):
        try:
            with SessionLocal() as session:
                alerts = (
                    session.query(Alert)
                    .filter(Alert.status == "OPEN")
                    .order_by(Alert.id.asc())
                    .all()
                )

                for alert in alerts:
                    alert_data = self._db_to_dict(alert)

                    self.active_alerts[alert.machine_id] = alert_data

                    if alert.id >= self.next_alert_id:
                        self.next_alert_id = alert.id + 1

                latest_alert = session.query(Alert).order_by(Alert.id.desc()).first()

                if latest_alert and latest_alert.id >= self.next_alert_id:
                    self.next_alert_id = latest_alert.id + 1

        except Exception as error:
            print(f"Could not load alerts from database: {error}")

    # ============================================================
    # PROCESS ANOMALY
    # ============================================================

    def process_anomaly(self, reading, anomaly_result):
        machine_id = reading.get("machine_id")

        if not machine_id:
            return None

        condition = str(
            reading.get(
                "condition",
                "HEALTHY",
            )
        ).upper()

        is_anomaly = anomaly_result.get(
            "is_anomaly",
            False,
        )

        reasons = list(
            anomaly_result.get(
                "reasons",
                [],
            )
        )

        fault_type = reading.get("fault_type")

        # --------------------------------------------------------
        # ML FAILURE RISK
        # --------------------------------------------------------

        ml_failure_probability = reading.get("ml_failure_probability")

        ml_failure_within_1h = reading.get("ml_failure_within_1h")

        ml_failure_threshold = reading.get(
            "ml_failure_threshold",
            0.70,
        )

        ml_failure_risk = False

        try:
            if ml_failure_probability is not None:
                ml_failure_risk = float(ml_failure_probability) >= float(
                    ml_failure_threshold
                )
        except (TypeError, ValueError):
            ml_failure_risk = False

        if ml_failure_risk:
            ml_reason = "ML predicts high probability of failure " "within 1 hour"

            if ml_reason not in reasons:
                reasons.append(ml_reason)

        reasons = self._build_reasons(
            condition=condition,
            fault_type=fault_type,
            reasons=reasons,
        )

        should_alert = self._should_create_alert(
            condition=condition,
            is_anomaly=is_anomaly,
            reasons=reasons,
            ml_failure_risk=ml_failure_risk,
        )

        # ========================================================
        # ALERT REQUIRED
        # ========================================================

        if should_alert:
            severity = self._get_severity(condition)

            # ----------------------------------------------------
            # Existing alert for this machine
            # ----------------------------------------------------

            if machine_id in self.active_alerts:
                alert = self.active_alerts[machine_id]

                previous_condition = alert["condition"]
                previous_severity = alert["severity"]

                alert["severity"] = severity
                alert["condition"] = condition
                alert["fault_type"] = fault_type
                alert["reasons"] = reasons

                alert["anomaly_score"] = anomaly_result.get(
                    "anomaly_score",
                    0.0,
                )

                alert["ml_failure_probability"] = ml_failure_probability

                alert["ml_failure_within_1h"] = ml_failure_within_1h

                alert["last_seen"] = datetime.now(timezone.utc).isoformat()

                self._update_alert_in_database(alert)

                if previous_condition != condition or previous_severity != severity:
                    print(
                        f"[ALERT ESCALATED] "
                        f"{machine_id} - "
                        f"{previous_condition} -> "
                        f"{condition} - "
                        f"{previous_severity} -> "
                        f"{severity} - "
                        f"{reasons}"
                    )

                return alert

            # ----------------------------------------------------
            # Create new alert
            # ----------------------------------------------------

            now = datetime.now(timezone.utc).isoformat()

            alert = {
                "alert_id": self.next_alert_id,
                "machine_id": machine_id,
                "machine_name": reading.get(
                    "machine_name",
                    machine_id,
                ),
                "severity": severity,
                "status": "OPEN",
                "condition": condition,
                "fault_type": fault_type,
                "anomaly_score": anomaly_result.get(
                    "anomaly_score",
                    0.0,
                ),
                "ml_failure_probability": ml_failure_probability,
                "ml_failure_within_1h": ml_failure_within_1h,
                "reasons": reasons,
                "created_at": now,
                "last_seen": now,
                "resolved_at": None,
            }

            self.next_alert_id += 1

            self.active_alerts[machine_id] = alert

            self._save_alert_to_database(alert)

            print(
                f"[ALERT] "
                f"{machine_id} - "
                f"{severity} - "
                f"{condition} - "
                f"{reasons}"
            )

            return alert

        # ========================================================
        # NO ALERT REQUIRED
        # ========================================================

        if machine_id in self.active_alerts:
            alert = self.active_alerts.pop(machine_id)

            alert["status"] = "RESOLVED"
            alert["resolved_at"] = datetime.now(timezone.utc).isoformat()

            self._update_alert_in_database(alert)

            print(f"[ALERT RESOLVED] " f"{machine_id}")

            return alert

        return None

    # ============================================================
    # SAVE NEW ALERT
    # ============================================================

    def _save_alert_to_database(self, alert):
        try:
            with SessionLocal() as session:
                db_alert = Alert(
                    machine_id=alert["machine_id"],
                    machine_name=alert["machine_name"],
                    severity=alert["severity"],
                    condition=alert["condition"],
                    status=alert["status"],
                    fault_type=alert["fault_type"],
                    reasons=json.dumps(alert["reasons"]),
                    anomaly_score=alert["anomaly_score"],
                    # ------------------------------------------------
                    # ML PREDICTIONS
                    # ------------------------------------------------
                    ml_failure_probability=alert.get("ml_failure_probability"),
                    ml_failure_within_1h=alert.get("ml_failure_within_1h"),
                    created_at=alert["created_at"],
                    last_seen=alert["last_seen"],
                    resolved_at=alert.get("resolved_at"),
                )

                session.add(db_alert)
                session.commit()

                alert["alert_id"] = db_alert.id

                if db_alert.id >= self.next_alert_id:
                    self.next_alert_id = db_alert.id + 1

        except Exception as error:
            print(f"Could not save alert to database: " f"{error}")

    # ============================================================
    # UPDATE EXISTING ALERT
    # ============================================================

    def _update_alert_in_database(self, alert):
        try:
            with SessionLocal() as session:
                db_alert = (
                    session.query(Alert).filter(Alert.id == alert["alert_id"]).first()
                )

                if db_alert is None:
                    return

                db_alert.severity = alert["severity"]
                db_alert.condition = alert["condition"]
                db_alert.status = alert["status"]
                db_alert.fault_type = alert["fault_type"]
                db_alert.reasons = json.dumps(alert["reasons"])
                db_alert.anomaly_score = alert["anomaly_score"]

                # ------------------------------------------------
                # ML PREDICTIONS
                # ------------------------------------------------

                db_alert.ml_failure_probability = alert.get("ml_failure_probability")

                db_alert.ml_failure_within_1h = alert.get("ml_failure_within_1h")

                db_alert.last_seen = alert["last_seen"]
                db_alert.resolved_at = alert.get("resolved_at")

                session.commit()

        except Exception as error:
            print(f"Could not update alert in database: " f"{error}")

    # ============================================================
    # CONVERT DATABASE ALERT TO DICT
    # ============================================================

    def _db_to_dict(self, alert):
        try:
            reasons = json.loads(alert.reasons) if alert.reasons else []
        except (json.JSONDecodeError, TypeError):
            reasons = []

        return {
            "alert_id": alert.id,
            "machine_id": alert.machine_id,
            "machine_name": alert.machine_name,
            "severity": alert.severity,
            "status": alert.status,
            "condition": alert.condition,
            "fault_type": alert.fault_type,
            "anomaly_score": alert.anomaly_score,
            # ------------------------------------------------
            # ML PREDICTIONS
            # ------------------------------------------------
            "ml_failure_probability": (alert.ml_failure_probability),
            "ml_failure_within_1h": (alert.ml_failure_within_1h),
            "reasons": reasons,
            "created_at": alert.created_at,
            "last_seen": alert.last_seen,
            "resolved_at": alert.resolved_at,
        }

    # ============================================================
    # BUILD ALERT REASONS
    # ============================================================

    def _build_reasons(
        self,
        condition,
        fault_type,
        reasons,
    ):
        result = list(reasons)

        if condition == "FAULTED":
            message = "Machine breakdown detected"

            if message not in result:
                result.insert(0, message)

        elif condition == "CRITICAL":
            message = "Critical machine condition detected"

            if message not in result:
                result.insert(0, message)

        elif condition == "WARNING":
            if not result:
                result.insert(
                    0,
                    "Machine condition requires attention",
                )

        elif condition == "DEGRADING":
            if not result:
                result.insert(
                    0,
                    "Machine degradation detected",
                )

        if fault_type:
            fault_names = {
                "bearing_wear": "Bearing wear",
                "cavitation": "Cavitation",
                "overload": "Motor overload",
                "belt_misalignment": "Belt misalignment",
                "fan_imbalance": "Fan imbalance",
                "gear_wear": "Gear wear",
            }

            fault_name = fault_names.get(
                fault_type,
                fault_type.replace(
                    "_",
                    " ",
                ).title(),
            )

            fault_reason = f"Suspected fault: {fault_name}"

            if fault_reason not in result:
                result.append(fault_reason)

        return result

    # ============================================================
    # ALERT DECISION
    # ============================================================

    def _should_create_alert(
        self,
        condition,
        is_anomaly,
        reasons,
        ml_failure_risk=False,
    ):
        if condition in [
            "DEGRADING",
            "WARNING",
            "CRITICAL",
            "FAULTED",
        ]:
            return True

        engineering_reasons = [
            "Critical temperature level",
            "Critical vibration level",
            "Critical current level",
            "High operating temperature",
            "High motor current",
        ]

        if any(reason in engineering_reasons for reason in reasons):
            return True

        # --------------------------------------------------------
        # ML predictive failure risk
        # --------------------------------------------------------

        if ml_failure_risk:
            return True

        return False

    # ============================================================
    # SEVERITY
    # ============================================================

    def _get_severity(self, condition):
        if condition in [
            "FAULTED",
            "CRITICAL",
        ]:
            return "CRITICAL"

        if condition == "WARNING":
            return "WARNING"

        if condition == "DEGRADING":
            return "MEDIUM"

        return "LOW"

    # ============================================================
    # GETTERS
    # ============================================================

    def get_active_alerts(self):
        return list(self.active_alerts.values())

    def get_alert_history(self):
        try:
            with SessionLocal() as session:
                alerts = session.query(Alert).order_by(Alert.id.desc()).all()

                return [self._db_to_dict(alert) for alert in alerts]

        except Exception as error:
            print(f"Could not load alert history: " f"{error}")

            return []

    def get_machine_alert(self, machine_id):
        return self.active_alerts.get(machine_id)


alert_service = AlertService()
