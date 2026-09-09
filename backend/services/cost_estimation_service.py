from typing import Any, Dict, List

LABOUR_RATES_USD_PER_HOUR = {
    "LOW": 30.0,
    "MEDIUM": 40.0,
    "HIGH": 50.0,
    "CRITICAL": 60.0,
}


LABOUR_HOURS = {
    "LOW": 1.0,
    "MEDIUM": 2.0,
    "HIGH": 3.0,
    "CRITICAL": 4.0,
}


def _calculate_parts_cost(parts: List[Dict[str, Any]]) -> float:
    """Calculate total cost using catalog part prices."""

    total = 0.0

    for part in parts:
        try:
            total += float(part.get("estimated_cost_usd", 0))
        except (TypeError, ValueError):
            continue

    return round(total, 2)


def estimate_maintenance_cost(
    machine: Dict[str, Any],
    spare_parts: Dict[str, Any] | None = None,
) -> Dict[str, Any]:
    """
    Estimate maintenance cost from catalog parts and
    deterministic labour assumptions.
    """

    if not isinstance(machine, dict):
        raise ValueError("Machine context must be an object.")

    machine_id = machine.get("machine_id")

    if not machine_id:
        raise ValueError("Machine ID is required.")

    condition = str(
        machine.get("condition") or machine.get("health_status") or "HEALTHY"
    ).upper()

    if condition not in LABOUR_RATES_USD_PER_HOUR:
        condition = "LOW"

    parts = []

    if isinstance(spare_parts, dict):
        candidate_parts = spare_parts.get("parts", [])

        if isinstance(candidate_parts, list):
            parts = [part for part in candidate_parts if isinstance(part, dict)]

    parts_cost = _calculate_parts_cost(parts)

    labour_rate = LABOUR_RATES_USD_PER_HOUR[condition]
    labour_hours = LABOUR_HOURS[condition]
    labour_cost = round(labour_rate * labour_hours, 2)

    total_cost = round(parts_cost + labour_cost, 2)

    return {
        "machine_id": machine_id,
        "condition": condition,
        "parts_count": len(parts),
        "parts_cost_usd": parts_cost,
        "labour_rate_usd_per_hour": labour_rate,
        "estimated_labour_hours": labour_hours,
        "labour_cost_usd": labour_cost,
        "estimated_total_cost_usd": total_cost,
        "currency": "USD",
        "source": "ProDiag Cost Estimation Service",
    }
