from datetime import datetime, timezone

from database import FaultEvent, SessionLocal


class FaultEventService:
    def __init__(self):
        self.previous_conditions = {}

    # ============================================================
    # PROCESS MACHINE CONDITION
    # ============================================================

    def process_condition_change(self, reading):
        machine_id = reading.get("machine_id")

        if not machine_id:
            return None

        current_condition = str(
            reading.get(
                "condition",
                "HEALTHY",
            )
        ).upper()

        previous_condition = self.previous_conditions.get(machine_id)

        # First reading for this machine.
        # Store the condition but do not create an event.
        if previous_condition is None:
            self.previous_conditions[machine_id] = current_condition
            return None

        # No state change.
        if previous_condition == current_condition:
            return None

        fault_type = reading.get("fault_type")

        reason = self._build_reason(
            previous_condition,
            current_condition,
            reading,
        )

        event = self._save_event(
            machine_id=machine_id,
            machine_name=reading.get(
                "machine_name",
                machine_id,
            ),
            previous_condition=previous_condition,
            new_condition=current_condition,
            fault_type=fault_type,
            reason=reason,
        )

        self.previous_conditions[machine_id] = current_condition

        print(
            f"[FAULT EVENT] "
            f"{machine_id} - "
            f"{previous_condition} -> "
            f"{current_condition}"
        )

        return event

    # ============================================================
    # BUILD EVENT REASON
    # ============================================================

    def _build_reason(
        self,
        previous_condition,
        new_condition,
        reading,
    ):
        if new_condition == "FAULTED":
            return "Machine breakdown detected"

        if new_condition == "CRITICAL":
            return "Critical machine condition detected"

        if new_condition == "WARNING":
            return "Machine condition requires attention"

        if new_condition == "DEGRADING":
            return "Machine degradation detected"

        if previous_condition == "FAULTED" and new_condition == "REPAIRING":
            return "Maintenance repair started"

        if previous_condition == "REPAIRING" and new_condition == "RESTART":
            return "Machine restart initiated"

        if previous_condition == "RESTART" and new_condition == "HEALTHY":
            return "Machine returned to healthy operation"

        return (
            f"Machine condition changed from "
            f"{previous_condition} to "
            f"{new_condition}"
        )

    # ============================================================
    # SAVE EVENT
    # ============================================================

    def _save_event(
        self,
        machine_id,
        machine_name,
        previous_condition,
        new_condition,
        fault_type,
        reason,
    ):
        timestamp = datetime.now(timezone.utc).isoformat()

        try:
            with SessionLocal() as session:
                event = FaultEvent(
                    machine_id=machine_id,
                    machine_name=machine_name,
                    previous_condition=previous_condition,
                    new_condition=new_condition,
                    fault_type=fault_type,
                    reason=reason,
                    timestamp=timestamp,
                )

                session.add(event)
                session.commit()
                session.refresh(event)

                return self._event_to_dict(event)

        except Exception as error:
            print(f"Could not save fault event: " f"{error}")
            return None

    # ============================================================
    # GET EVENT HISTORY
    # ============================================================

    def get_history(
        self,
        machine_id=None,
        limit=100,
    ):
        try:
            with SessionLocal() as session:
                query = session.query(FaultEvent)

                if machine_id:
                    query = query.filter(FaultEvent.machine_id == machine_id)

                events = query.order_by(FaultEvent.id.desc()).limit(limit).all()

                return [self._event_to_dict(event) for event in events]

        except Exception as error:
            print(f"Could not load fault events: " f"{error}")
            return []

    # ============================================================
    # CONVERT EVENT TO DICT
    # ============================================================

    def _event_to_dict(self, event):
        return {
            "event_id": event.id,
            "machine_id": event.machine_id,
            "machine_name": event.machine_name,
            "previous_condition": (event.previous_condition),
            "new_condition": event.new_condition,
            "fault_type": event.fault_type,
            "reason": event.reason,
            "timestamp": event.timestamp,
        }


fault_event_service = FaultEventService()
