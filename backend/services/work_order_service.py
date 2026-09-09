import json
from datetime import datetime, timezone

from database import SessionLocal, WorkOrder


class WorkOrderService:
    def create_work_order(
        self,
        machine_id,
        machine_name,
        title,
        description=None,
        priority="MEDIUM",
        fault_type=None,
        fault_event_id=None,
        alert_id=None,
        ai_diagnosis=None,
        ai_recommendation=None,
        spare_parts=None,
        parts_cost_usd=None,
        labour_cost_usd=None,
        estimated_total_cost_usd=None,
        approval_status=None,
        engineer_name=None,
        approval_comment=None,
        approved_at=None,
    ):
        now = datetime.now(timezone.utc).isoformat()

        try:
            if isinstance(ai_diagnosis, list):
                ai_diagnosis = "\n".join(str(item) for item in ai_diagnosis)

            if isinstance(ai_recommendation, list):
                ai_recommendation = "\n".join(str(item) for item in ai_recommendation)

            spare_parts_json = None

            if spare_parts is not None:
                spare_parts_json = json.dumps(spare_parts)

            with SessionLocal() as session:
                work_order = WorkOrder(
                    machine_id=machine_id,
                    machine_name=machine_name,
                    status="OPEN",
                    priority=priority,
                    fault_type=fault_type,
                    fault_event_id=fault_event_id,
                    alert_id=alert_id,
                    title=title,
                    description=description,
                    ai_diagnosis=ai_diagnosis,
                    ai_recommendation=ai_recommendation,
                    spare_parts=spare_parts_json,
                    parts_cost_usd=parts_cost_usd,
                    labour_cost_usd=labour_cost_usd,
                    estimated_total_cost_usd=estimated_total_cost_usd,
                    approval_status=approval_status,
                    engineer_name=engineer_name,
                    approval_comment=approval_comment,
                    approved_at=approved_at,
                    created_at=now,
                    updated_at=now,
                )

                session.add(work_order)
                session.commit()
                session.refresh(work_order)

                return self._to_dict(work_order)

        except Exception as error:
            print(f"Could not create work order: {error}")
            return None

    def create_from_approved_proposal(self, proposal):
        """
        Create a Work Order only from an approved maintenance proposal.

        All proposal data is carried into the Work Order:
        - spare parts
        - parts cost
        - labour cost
        - estimated total cost
        - approval information
        - diagnosis
        - recommended actions
        """

        if not isinstance(proposal, dict):
            raise ValueError("Proposal data must be an object.")

        if proposal.get("proposal_status") != "APPROVED":
            raise ValueError("Only approved proposals can create work orders.")

        machine_id = proposal.get("machine_id")

        if not machine_id:
            raise ValueError("Machine ID is required.")

        recommended_actions = proposal.get("recommended_actions")

        if isinstance(recommended_actions, list):
            recommended_actions = "\n".join(
                str(action) for action in recommended_actions
            )

        cost_estimate = proposal.get("cost_estimate") or {}

        spare_parts = proposal.get("spare_parts")

        # Use the proposal's parts cost when available.
        # Otherwise calculate it from the spare-parts list.
        parts_cost_usd = proposal.get("parts_cost_usd")

        if parts_cost_usd is None:
            if isinstance(spare_parts, list):
                parts_cost_usd = sum(
                    float(part.get("estimated_cost_usd", 0) or 0)
                    * float(part.get("quantity", 1) or 1)
                    for part in spare_parts
                    if isinstance(part, dict)
                )
            else:
                parts_cost_usd = 0.0

        labour_cost_usd = cost_estimate.get("labour_cost_usd")

        estimated_total_cost_usd = cost_estimate.get("estimated_total_cost_usd")

        return self.create_work_order(
            machine_id=machine_id,
            machine_name=proposal.get("machine_name"),
            title=(proposal.get("title") or proposal.get("proposal_title")),
            description=proposal.get("comment"),
            priority=proposal.get("priority", "MEDIUM"),
            fault_type=proposal.get("fault_type"),
            fault_event_id=proposal.get("fault_event_id"),
            alert_id=proposal.get("alert_id"),
            ai_diagnosis=proposal.get("ai_diagnosis"),
            ai_recommendation=recommended_actions,
            spare_parts=spare_parts,
            parts_cost_usd=parts_cost_usd,
            labour_cost_usd=labour_cost_usd,
            estimated_total_cost_usd=(estimated_total_cost_usd),
            approval_status="APPROVED",
            engineer_name=proposal.get("engineer_name"),
            approval_comment=proposal.get("comment"),
            approved_at=proposal.get("approved_at"),
        )

    def get_work_orders(
        self,
        machine_id=None,
        status=None,
    ):
        try:
            with SessionLocal() as session:
                query = session.query(WorkOrder)

                if machine_id:
                    query = query.filter(WorkOrder.machine_id == machine_id)

                if status:
                    query = query.filter(WorkOrder.status == status)

                work_orders = query.order_by(WorkOrder.id.desc()).all()

                return [self._to_dict(work_order) for work_order in work_orders]

        except Exception as error:
            print(f"Could not load work orders: {error}")
            return []

    def get_work_order(
        self,
        work_order_id,
    ):
        try:
            with SessionLocal() as session:
                work_order = (
                    session.query(WorkOrder)
                    .filter(WorkOrder.id == work_order_id)
                    .first()
                )

                if not work_order:
                    return None

                return self._to_dict(work_order)

        except Exception as error:
            print(f"Could not load work order: {error}")
            return None

    def update_status(
        self,
        work_order_id,
        status,
        engineer_name=None,
    ):
        now = datetime.now(timezone.utc).isoformat()

        try:
            with SessionLocal() as session:
                work_order = (
                    session.query(WorkOrder)
                    .filter(WorkOrder.id == work_order_id)
                    .first()
                )

                if not work_order:
                    return None

                work_order.status = status
                work_order.updated_at = now

                if engineer_name and status == "COMPLETED":
                    work_order.completed_by = engineer_name

                if status == "COMPLETED":
                    work_order.completed_at = now

                session.commit()
                session.refresh(work_order)

                return self._to_dict(work_order)

        except Exception as error:
            print(f"Could not update work order: {error}")
            return None

    def _to_dict(self, work_order):
        spare_parts = []

        if work_order.spare_parts:
            try:
                spare_parts = json.loads(work_order.spare_parts)
            except (
                TypeError,
                json.JSONDecodeError,
            ):
                spare_parts = []

        return {
            "work_order_id": work_order.id,
            "machine_id": work_order.machine_id,
            "machine_name": work_order.machine_name,
            "status": work_order.status,
            "priority": work_order.priority,
            "fault_type": work_order.fault_type,
            "fault_event_id": work_order.fault_event_id,
            "alert_id": work_order.alert_id,
            "title": work_order.title,
            "description": work_order.description,
            "ai_diagnosis": work_order.ai_diagnosis,
            "ai_recommendation": (work_order.ai_recommendation),
            "spare_parts": spare_parts,
            "parts_cost_usd": (work_order.parts_cost_usd),
            "labour_cost_usd": (work_order.labour_cost_usd),
            "estimated_total_cost_usd": (work_order.estimated_total_cost_usd),
            "approval_status": (work_order.approval_status),
            "engineer_name": (work_order.engineer_name),
            "approval_comment": (work_order.approval_comment),
            "approved_at": (work_order.approved_at),
            "created_at": (work_order.created_at),
            "updated_at": (work_order.updated_at),
            "completed_at": (work_order.completed_at),
            "completed_by": getattr(
                work_order,
                "completed_by",
                None,
            ),
        }


work_order_service = WorkOrderService()
