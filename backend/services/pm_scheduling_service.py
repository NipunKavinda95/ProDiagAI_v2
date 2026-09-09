from datetime import date, timedelta
from typing import Any, Dict, Optional

from services.preventive_maintenance_service import (
    build_preventive_maintenance_plan,
)


def schedule_preventive_maintenance(
    machine: Dict[str, Any],
    last_maintenance_date: Optional[str] = None,
    reference_date: Optional[str] = None,
) -> Dict[str, Any]:
    """Calculate the recommended PM schedule for a machine."""

    if not isinstance(machine, dict):
        raise ValueError("Machine data must be an object.")

    machine_id = machine.get("machine_id")
    if not machine_id:
        raise ValueError("Machine ID is required.")

    pm_plan = build_preventive_maintenance_plan(machine)
    interval_days = pm_plan["recommended_interval_days"]

    if reference_date:
        try:
            ref_date = date.fromisoformat(reference_date)
        except ValueError as exc:
            raise ValueError("Reference date must use YYYY-MM-DD format.") from exc
    else:
        ref_date = date.today()

    if last_maintenance_date:
        try:
            last_date = date.fromisoformat(last_maintenance_date)
        except ValueError as exc:
            raise ValueError(
                "Last maintenance date must use YYYY-MM-DD format."
            ) from exc

        next_date = last_date + timedelta(days=interval_days)
        days_until_due = (next_date - ref_date).days

        status = "DUE" if days_until_due <= 0 else "SCHEDULED"
    else:
        last_date = None
        next_date = ref_date
        days_until_due = 0
        status = "INITIAL_SCHEDULE"

    return {
        "machine_id": machine_id,
        "machine_type": pm_plan["machine_type"],
        "condition": pm_plan["condition"],
        "fault_type": pm_plan["fault_type"],
        "last_maintenance_date": (last_date.isoformat() if last_date else None),
        "next_maintenance_date": next_date.isoformat(),
        "days_until_due": days_until_due,
        "recommended_interval_days": interval_days,
        "schedule_status": status,
        "actions": pm_plan["actions"],
        "source": "ProDiag PM Scheduling Service",
    }
