from typing import Any, Dict, List, Optional


def _extract_spare_parts(
    spare_parts: Any,
) -> tuple[List[Dict[str, Any]], Optional[float]]:
    """
    Normalize spare-parts data coming from the Spare Parts Service.

    Supported formats:

    1. Direct list:
       [
           {
               "part_id": "BRG-6205",
               "estimated_cost_usd": 35.0,
               "quantity": 1
           }
       ]

    2. Recommendation dictionary:
       {
           "parts": [...],
           "parts_cost_usd": 60.0
       }

    3. Older recommendation dictionary:
       {
           "parts": [...],
           "total_parts_cost_usd": 60.0
       }

    The catalog remains the source of truth.
    """

    if isinstance(spare_parts, list):
        parts = [part for part in spare_parts if isinstance(part, dict)]

        return parts, None

    if isinstance(spare_parts, dict):
        parts = spare_parts.get("parts", [])

        if not isinstance(parts, list):
            parts = []

        parts = [part for part in parts if isinstance(part, dict)]

        authoritative_cost = spare_parts.get("parts_cost_usd")

        if authoritative_cost is None:
            authoritative_cost = spare_parts.get("total_parts_cost_usd")

        try:
            if authoritative_cost is not None:
                authoritative_cost = float(authoritative_cost)
        except (
            TypeError,
            ValueError,
        ):
            authoritative_cost = None

        return parts, authoritative_cost

    return [], None


def _calculate_parts_cost(
    parts: List[Dict[str, Any]],
) -> float:
    """
    Calculate spare-parts cost from catalog prices.

    Quantity defaults to 1.
    """

    total = 0.0

    for part in parts:
        try:
            unit_cost = float(
                part.get(
                    "estimated_cost_usd",
                    0,
                )
                or 0
            )

            quantity = float(
                part.get(
                    "quantity",
                    1,
                )
                or 1
            )

            total += unit_cost * quantity

        except (
            TypeError,
            ValueError,
        ):
            continue

    return round(total, 2)


def build_work_order_proposal(
    machine: Dict[str, Any],
    maintenance_plan: Optional[Dict[str, Any]] = None,
    diagnosis: Optional[Dict[str, Any]] = None,
    cost_estimate: Optional[Dict[str, Any]] = None,
    spare_parts: Any = None,
) -> Dict[str, Any]:
    """
    Build a complete maintenance work-order proposal
    for engineer approval.

    Flow:

        Spare Parts Catalog
                ↓
        Maintenance Agent
                ↓
        Work Order Proposal
                ↓
        Engineer Approval
                ↓
        Work Order
    """

    if not isinstance(machine, dict):
        raise ValueError("Machine data must be an object.")

    machine_id = machine.get("machine_id")

    if not machine_id:
        raise ValueError("Machine ID is required.")

    condition = str(
        machine.get("condition") or machine.get("health_status") or "HEALTHY"
    ).upper()

    fault_type = machine.get("fault_type")

    priority_map = {
        "FAULTED": "CRITICAL",
        "CRITICAL": "CRITICAL",
        "WARNING": "HIGH",
        "DEGRADING": "MEDIUM",
        "HEALTHY": "LOW",
    }

    priority = priority_map.get(
        condition,
        "MEDIUM",
    )

    # =========================================================
    # Maintenance Actions
    # =========================================================

    actions: List[str] = []

    if isinstance(
        maintenance_plan,
        dict,
    ):
        plan_actions = maintenance_plan.get(
            "actions",
            [],
        )

        if isinstance(
            plan_actions,
            list,
        ):
            actions.extend(
                action
                for action in plan_actions
                if isinstance(
                    action,
                    str,
                )
                and action.strip()
            )

    if isinstance(
        diagnosis,
        dict,
    ):
        diagnosis_actions = diagnosis.get(
            "recommended_actions",
            [],
        )

        if isinstance(
            diagnosis_actions,
            list,
        ):
            actions.extend(
                action
                for action in diagnosis_actions
                if isinstance(
                    action,
                    str,
                )
                and action.strip()
            )

    # Remove duplicates while preserving order.
    actions = list(dict.fromkeys(actions))

    # =========================================================
    # Spare Parts
    # =========================================================

    parts, catalog_parts_cost = _extract_spare_parts(spare_parts)

    calculated_parts_cost = _calculate_parts_cost(parts)

    # Prefer the authoritative cost returned
    # by the Spare Parts Service.
    #
    # If it is not available, calculate from
    # the actual catalog part prices.
    if catalog_parts_cost is not None:
        parts_cost = round(
            catalog_parts_cost,
            2,
        )
    else:
        parts_cost = calculated_parts_cost

    # =========================================================
    # Cost Estimate
    # =========================================================

    if not isinstance(
        cost_estimate,
        dict,
    ):
        cost_estimate = {}

    labour_cost = cost_estimate.get("labour_cost_usd")

    estimated_total = cost_estimate.get("estimated_total_cost_usd")

    # If the cost service did not provide a total,
    # calculate it safely from parts + labour.
    if estimated_total is None:

        try:
            labour_value = float(labour_cost or 0)
        except (
            TypeError,
            ValueError,
        ):
            labour_value = 0.0

        estimated_total = round(
            parts_cost + labour_value,
            2,
        )

        cost_estimate = {
            **cost_estimate,
            "parts_cost_usd": parts_cost,
            "labour_cost_usd": labour_value,
            "estimated_total_cost_usd": (estimated_total),
        }

    else:

        try:
            estimated_total = float(estimated_total)
        except (
            TypeError,
            ValueError,
        ):
            estimated_total = round(
                parts_cost,
                2,
            )

    # =========================================================
    # Final Proposal
    # =========================================================

    return {
        "proposal_status": ("PENDING_ENGINEER_APPROVAL"),
        "machine_id": machine_id,
        "machine_name": machine.get("machine_name"),
        "machine_type": machine.get("machine_type"),
        "condition": condition,
        "fault_type": fault_type,
        "priority": priority,
        "title": (
            f"Maintenance required - " f"{machine_id}"
            if fault_type is None
            else f"Maintenance - " f"{fault_type} - " f"{machine_id}"
        ),
        # =====================================================
        # Diagnosis
        # =====================================================
        "ai_diagnosis": (
            diagnosis.get("diagnosis")
            if isinstance(
                diagnosis,
                dict,
            )
            else None
        ),
        "probable_fault": (
            diagnosis.get("probable_fault")
            if isinstance(
                diagnosis,
                dict,
            )
            else fault_type
        ),
        # =====================================================
        # Maintenance
        # =====================================================
        "recommended_actions": actions,
        # =====================================================
        # Spare Parts
        # =====================================================
        "spare_parts": parts,
        "parts_found": bool(parts),
        "parts_count": len(parts),
        "parts_cost_usd": round(
            parts_cost,
            2,
        ),
        # =====================================================
        # Cost
        # =====================================================
        "cost_estimate": {
            **cost_estimate,
            "parts_cost_usd": round(
                parts_cost,
                2,
            ),
            "estimated_total_cost_usd": (
                round(
                    estimated_total,
                    2,
                )
            ),
        },
        # =====================================================
        # Approval
        # =====================================================
        "requires_engineer_approval": True,
        "auto_create_work_order": False,
        "source": ("ProDiag Maintenance Agent"),
    }
