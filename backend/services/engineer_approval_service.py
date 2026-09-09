from datetime import datetime, timezone
from typing import Any, Dict

VALID_DECISIONS = {"approve", "reject"}


def process_engineer_approval(
    proposal: Dict[str, Any],
    decision: str,
    engineer_name: str,
    comment: str = "",
) -> Dict[str, Any]:
    """Process engineer approval or rejection of a work-order proposal."""

    if not isinstance(proposal, dict):
        raise ValueError("Proposal data must be an object.")

    if proposal.get("proposal_status") != "PENDING_ENGINEER_APPROVAL":
        raise ValueError("Only pending proposals can be approved or rejected.")

    if not isinstance(decision, str):
        raise ValueError("Approval decision is required.")

    decision = decision.strip().lower()

    if decision not in VALID_DECISIONS:
        raise ValueError("Decision must be 'approve' or 'reject'.")

    if not isinstance(engineer_name, str) or not engineer_name.strip():
        raise ValueError("Engineer name is required.")

    if not isinstance(comment, str):
        raise ValueError("Approval comment must be text.")

    approval_status = "APPROVED" if decision == "approve" else "REJECTED"

    return {
        "proposal_status": approval_status,
        "machine_id": proposal["machine_id"],
        "proposal_title": proposal.get("title"),
        "decision": decision,
        "engineer_name": engineer_name.strip(),
        "comment": comment.strip(),
        "approved_at": datetime.now(timezone.utc).isoformat(),
        "work_order_created": False,
        "requires_work_order_creation": decision == "approve",
        "source": "ProDiag Engineer Approval Service",
    }
