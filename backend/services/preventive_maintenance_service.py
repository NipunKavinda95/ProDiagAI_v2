from typing import Any, Dict, List

PM_INTERVAL_DAYS = {
    "Motor": 30,
    "Pump": 30,
    "Gearbox": 60,
    "Fan": 30,
    "Conveyor": 30,
    "Compressor": 30,
}


def get_pm_interval(machine_type: str | None) -> int:
    """Return the default PM interval for an equipment type."""

    if not machine_type:
        return 30

    return PM_INTERVAL_DAYS.get(
        machine_type.strip().title(),
        30,
    )


def build_preventive_maintenance_plan(
    machine: Dict[str, Any],
) -> Dict[str, Any]:
    """
    Build a deterministic preventive-maintenance plan.

    This capability provides recommendations only.
    It does not schedule or create work orders.
    """

    if not isinstance(machine, dict):
        raise ValueError("Machine context must be an object.")

    machine_id = machine.get("machine_id")

    if not machine_id:
        raise ValueError("Machine ID is required.")

    machine_type = machine.get("machine_type") or "Unknown"
    condition = str(
        machine.get("condition") or machine.get("health_status") or "HEALTHY"
    ).upper()

    fault_type = machine.get("fault_type")

    interval_days = get_pm_interval(machine_type)

    actions: List[str] = [
        "Inspect machine condition.",
        "Check lubrication and visible wear.",
        "Verify abnormal vibration, temperature, and operating conditions.",
        "Record inspection findings in the maintenance history.",
    ]

    if fault_type:
        actions.insert(
            0,
            f"Inspect components associated with {fault_type}.",
        )

    if condition in {"WARNING", "CRITICAL", "FAULTED"}:
        actions.append(
            "Review corrective maintenance requirements before the next PM cycle."
        )

    return {
        "machine_id": machine_id,
        "machine_type": machine_type,
        "condition": condition,
        "fault_type": fault_type,
        "recommended_interval_days": interval_days,
        "actions": actions,
        "source": "ProDiag Preventive Maintenance Service",
    }
