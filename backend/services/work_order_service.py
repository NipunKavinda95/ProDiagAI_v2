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
    ):
        now = datetime.now(timezone.utc).isoformat()

        try:
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

    def get_work_order(self, work_order_id):
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

                if status == "COMPLETED":
                    work_order.completed_at = now

                session.commit()
                session.refresh(work_order)

                return self._to_dict(work_order)

        except Exception as error:
            print(f"Could not update work order: {error}")
            return None

    def _to_dict(self, work_order):
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
            "ai_recommendation": work_order.ai_recommendation,
            "created_at": work_order.created_at,
            "updated_at": work_order.updated_at,
            "completed_at": work_order.completed_at,
        }


work_order_service = WorkOrderService()
