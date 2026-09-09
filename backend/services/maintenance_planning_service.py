from typing import Any, Dict, List


def _priority_from_condition(condition: str) -> str:
    condition = condition.upper()

    if condition in {"FAULTED", "CRITICAL"}:
        return "CRITICAL"

    if condition == "WARNING":
        return "HIGH"

    if condition == "DEGRADING":
        return "MEDIUM"

    return "LOW"


def build_maintenance_plan(
    machine: Dict[str, Any],
    diagnosis: Dict[str, Any] | None = None,
) -> Dict[str, Any]:
    """
    Build a structured maintenance plan from current machine context.

    This service is deterministic.
    The AI Agent will decide when to use this capability later.
    """

    condition = str(
        machine.get("condition") or machine.get("health_status") or "HEALTHY"
    ).upper()

    fault_type = str(machine.get("fault_type") or "unknown")

    priority = _priority_from_condition(condition)

    actions: List[str] = []

    if condition in {"CRITICAL", "FAULTED"}:
        actions.extend(
            [
                "Inspect the machine before further operation.",
                "Verify the reported fault condition.",
                "Perform required corrective maintenance.",
            ]
        )

    elif condition == "WARNING":
        actions.extend(
            [
                "Inspect the machine condition.",
                "Check the main wear and failure indicators.",
                "Schedule corrective maintenance if deterioration continues.",
            ]
        )

    elif condition == "DEGRADING":
        actions.extend(
            [
                "Inspect the machine for early degradation signs.",
                "Increase monitoring frequency.",
                "Plan maintenance before the condition reaches warning level.",
            ]
        )

    else:
        actions.extend(
            [
                "Continue normal condition monitoring.",
                "Perform scheduled preventive maintenance.",
            ]
        )

    if fault_type != "unknown":
        actions.insert(
            0,
            f"Inspect components associated with {fault_type}.",
        )

    if diagnosis:
        recommended_actions = diagnosis.get("recommended_actions", [])

        if isinstance(recommended_actions, list):
            for action in recommended_actions:
                if isinstance(action, str) and action.strip():
                    actions.append(action.strip())

    # Remove duplicate actions while preserving order.
    unique_actions = list(dict.fromkeys(actions))

    return {
        "machine_id": machine.get("machine_id"),
        "machine_name": machine.get("machine_name"),
        "condition": condition,
        "fault_type": fault_type,
        "priority": priority,
        "maintenance_required": condition != "HEALTHY",
        "actions": unique_actions,
        "source": "ProDiag Maintenance Planning Service",
    }
