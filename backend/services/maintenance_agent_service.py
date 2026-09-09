from typing import Any, Dict

from services.maintenance_planning_service import (
    build_maintenance_plan,
)

from services.spare_parts_service import (
    get_spare_parts_recommendation,
)

from services.cost_estimation_service import (
    estimate_maintenance_cost,
)

from services.preventive_maintenance_service import (
    build_preventive_maintenance_plan,
)

from services.pm_scheduling_service import (
    schedule_preventive_maintenance,
)

from services.work_order_proposal_service import (
    build_work_order_proposal,
)


def select_capability(request: str) -> str:
    """Select the deterministic maintenance capability for an engineer request."""

    if not isinstance(request, str):
        raise ValueError("Agent request must be text.")

    request = request.strip().lower()

    if not request:
        raise ValueError("Agent request is required.")

    # ---------------------------------------------------------
    # Cost estimation
    # ---------------------------------------------------------
    cost_keywords = [
        "maintenance cost",
        "maintenance costs",
        "repair cost",
        "repair costs",
        "estimated cost",
        "estimate cost",
        "how much will",
        "cost estimate",
    ]

    if any(keyword in request for keyword in cost_keywords):
        return "cost_estimation"

    # ---------------------------------------------------------
    # Spare parts
    # ---------------------------------------------------------
    spare_parts_keywords = [
        "spare part",
        "spare parts",
        "replacement part",
        "replacement parts",
        "which part",
        "which parts",
        "what part",
        "what parts",
    ]

    if any(keyword in request for keyword in spare_parts_keywords):
        return "spare_parts"

    # ---------------------------------------------------------
    # PM scheduling
    # Check scheduling before general PM planning.
    # ---------------------------------------------------------
    scheduling_keywords = [
        "schedule maintenance",
        "maintenance schedule",
        "pm scheduling",
        "schedule pm",
        "when should maintenance",
        "when is maintenance due",
        "when is pm due",
        "next maintenance",
        "next pm",
    ]

    if any(keyword in request for keyword in scheduling_keywords):
        return "pm_scheduling"

    # ---------------------------------------------------------
    # Preventive maintenance planning
    # ---------------------------------------------------------
    pm_keywords = [
        "preventive maintenance",
        "preventative maintenance",
        "pm plan",
        "maintenance interval",
    ]

    if any(keyword in request for keyword in pm_keywords):
        return "preventive_maintenance"

    # ---------------------------------------------------------
    # Work-order proposal
    # ---------------------------------------------------------
    work_order_keywords = [
        "work order",
        "workorder",
        "create work order",
        "prepare work order",
        "propose work order",
        "work order proposal",
        "maintenance order",
    ]

    if any(keyword in request for keyword in work_order_keywords):
        return "work_order_proposal"

    # ---------------------------------------------------------
    # Default capability
    # ---------------------------------------------------------
    return "maintenance_planning"


def run_maintenance_agent(
    machine: Dict[str, Any],
    request: str = "Create a maintenance plan",
    diagnosis: Dict[str, Any] | None = None,
) -> Dict[str, Any]:
    """
    ProDiag Maintenance Agent.

    The agent selects a deterministic maintenance capability
    and executes the corresponding backend service.

    Workflow:
        AI/Agent recommends
            ↓
        Engineer reviews
            ↓
        Engineer approves
            ↓
        Work Order is created
    """

    if not isinstance(machine, dict):
        raise ValueError("Machine context must be an object.")

    if not machine.get("machine_id"):
        raise ValueError("Machine ID is required.")

    capability = select_capability(request)

    # =========================================================
    # 1. Maintenance Planning
    # =========================================================
    if capability == "maintenance_planning":
        result = build_maintenance_plan(
            machine=machine,
            diagnosis=diagnosis,
        )

        return {
            "agent": "ProDiag Maintenance Agent",
            "request": request,
            "capability": capability,
            "status": "completed",
            "result": result,
        }

    # =========================================================
    # 2. Spare Parts
    # =========================================================
    if capability == "spare_parts":
        result = get_spare_parts_recommendation(
            machine=machine,
        )

        return {
            "agent": "ProDiag Maintenance Agent",
            "request": request,
            "capability": capability,
            "status": "completed",
            "result": result,
        }

    # =========================================================
    # 3. Maintenance Cost
    # =========================================================
    if capability == "cost_estimation":
        spare_parts = get_spare_parts_recommendation(
            machine=machine,
        )

        result = estimate_maintenance_cost(
            machine=machine,
            spare_parts=spare_parts,
        )

        return {
            "agent": "ProDiag Maintenance Agent",
            "request": request,
            "capability": capability,
            "status": "completed",
            "result": result,
        }

    # =========================================================
    # 4. Preventive Maintenance
    # =========================================================
    if capability == "preventive_maintenance":
        result = build_preventive_maintenance_plan(
            machine=machine,
        )

        return {
            "agent": "ProDiag Maintenance Agent",
            "request": request,
            "capability": capability,
            "status": "completed",
            "result": result,
        }

    # =========================================================
    # 5. PM Scheduling
    # =========================================================
    if capability == "pm_scheduling":
        result = schedule_preventive_maintenance(
            machine=machine,
            last_maintenance_date=machine.get("last_maintenance_date"),
            reference_date=machine.get("reference_date"),
        )

        return {
            "agent": "ProDiag Maintenance Agent",
            "request": request,
            "capability": capability,
            "status": "completed",
            "machine_id": machine["machine_id"],
            "result": result,
        }

    # =========================================================
    # 6. Work-Order Proposal
    # =========================================================
    if capability == "work_order_proposal":

        # -----------------------------------------------------
        # Build maintenance plan
        # -----------------------------------------------------
        maintenance_plan = build_maintenance_plan(
            machine=machine,
            diagnosis=diagnosis,
        )

        # -----------------------------------------------------
        # Get deterministic spare-parts recommendation.
        #
        # The spare-parts catalog is the source of truth for:
        # - Part number
        # - Part name
        # - Part price
        # -----------------------------------------------------
        spare_parts = get_spare_parts_recommendation(
            machine=machine,
        )

        # -----------------------------------------------------
        # Calculate maintenance cost using the same parts.
        # -----------------------------------------------------
        cost_estimate = estimate_maintenance_cost(
            machine=machine,
            spare_parts=spare_parts,
        )

        # -----------------------------------------------------
        # Build the complete engineer approval proposal.
        #
        # IMPORTANT:
        # spare_parts MUST be passed here.
        #
        # This allows the approved proposal to carry:
        # - spare_parts
        # - parts_cost_usd
        # - cost_estimate
        #
        # into the Work Order creation flow.
        # -----------------------------------------------------
        result = build_work_order_proposal(
            machine=machine,
            maintenance_plan=maintenance_plan,
            diagnosis=diagnosis,
            cost_estimate=cost_estimate,
            spare_parts=spare_parts,
        )

        return {
            "agent": "ProDiag Maintenance Agent",
            "request": request,
            "capability": capability,
            "status": "completed",
            "result": result,
        }

    raise ValueError(f"Unsupported maintenance capability: {capability}")
