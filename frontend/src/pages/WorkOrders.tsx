import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";

type WorkOrder = {
    work_order_id: number;
    machine_id: string;
    machine_name: string;

    status: string;
    priority: string;

    fault_type: string | null;
    fault_event_id: number | null;
    alert_id: number | null;

    title: string;
    description: string | null;

    ai_diagnosis: string | null;
    ai_recommendation: string | null;

    created_at: string;
    updated_at: string;
    completed_at: string | null;
};

type WorkOrdersResponse = {
    count: number;
    work_orders: WorkOrder[];
};

function WorkOrders() {
    const navigate = useNavigate();

    const [workOrders, setWorkOrders] = useState<WorkOrder[]>([]);
    const [error, setError] = useState("");

    useEffect(() => {
        const loadWorkOrders = async () => {
            try {
                const response = await fetch(
                    "http://127.0.0.1:5000/api/work-orders"
                );

                if (!response.ok) {
                    throw new Error("Work Orders API is not available");
                }

                const data: WorkOrdersResponse = await response.json();

                setWorkOrders(data.work_orders);
                setError("");
            } catch (err) {
                setError(
                    err instanceof Error ? err.message : "Unknown error"
                );
            }
        };

        loadWorkOrders();

        const intervalId = setInterval(loadWorkOrders, 5000);

        return () => clearInterval(intervalId);
    }, []);

    const getPriorityClass = (priority: string) => {
        return `work-order-priority ${priority.toLowerCase()}`;
    };

    const getStatusClass = (status: string) => {
        return `work-order-status ${status.toLowerCase()}`;
    };

    if (error) {
        return (
            <main>
                <button
                    type="button"
                    onClick={() => navigate("/")}
                >
                    ← Fleet Dashboard
                </button>

                <section className="panel">
                    <p className="eyebrow">Work Orders</p>
                    <h2>Unable to load work orders</h2>
                    <p>{error}</p>
                </section>
            </main>
        );
    }

    return (
        <main>
            <header
                style={{
                    display: "flex",
                    alignItems: "flex-start",
                    justifyContent: "space-between",
                    gap: "24px",
                    marginBottom: "28px",
                    paddingBottom: "22px",
                    borderBottom: "1px solid #1d3b57",
                }}
            >
                <div>
                    <button
                        type="button"
                        onClick={() => navigate("/")}
                        style={{
                            marginBottom: "16px",
                            background: "transparent",
                            border: "1px solid #285273",
                            color: "#9ab3d0",
                            padding: "8px 14px",
                            borderRadius: "8px",
                            cursor: "pointer",
                        }}
                    >
                        ← Fleet Dashboard
                    </button>

                    <p className="eyebrow">Maintenance execution</p>

                    <h1>Work Orders</h1>

                    <p>
                        {workOrders.length} work order
                        {workOrders.length !== 1 ? "s" : ""}
                    </p>
                </div>

                <div
                    style={{
                        color: "#7ee7c7",
                        fontSize: "0.85rem",
                        marginTop: "58px",
                    }}
                >
                    ● Maintenance Workflow
                </div>
            </header>

            {workOrders.length === 0 ? (
                <section className="panel">
                    <p className="eyebrow">No maintenance actions</p>

                    <h2>No work orders yet</h2>

                    <p>
                        Work orders will appear here after an engineer
                        reviews a maintenance recommendation and approves
                        the action.
                    </p>
                </section>
            ) : (
                <section
                    style={{
                        display: "grid",
                        gap: "16px",
                    }}
                >
                    {workOrders.map((workOrder) => (
                        <article
                            className="panel"
                            key={workOrder.work_order_id}
                        >
                            <div
                                style={{
                                    display: "flex",
                                    justifyContent: "space-between",
                                    alignItems: "flex-start",
                                    gap: "20px",
                                }}
                            >
                                <div>
                                    <p className="eyebrow">
                                        Work Order #{workOrder.work_order_id}
                                    </p>

                                    <h2>{workOrder.title}</h2>

                                    <p>
                                        {workOrder.machine_name} ·{" "}
                                        {workOrder.machine_id}
                                    </p>
                                </div>

                                <div
                                    style={{
                                        display: "flex",
                                        gap: "10px",
                                        flexWrap: "wrap",
                                        justifyContent: "flex-end",
                                    }}
                                >
                                    <span className={getPriorityClass(workOrder.priority)}>
                                        {workOrder.priority}
                                    </span>

                                    <span className={getStatusClass(workOrder.status)}>
                                        {workOrder.status}
                                    </span>
                                </div>
                            </div>

                            <div
                                style={{
                                    display: "grid",
                                    gridTemplateColumns:
                                        "repeat(auto-fit, minmax(180px, 1fr))",
                                    gap: "12px",
                                    marginTop: "20px",
                                }}
                            >
                                <div className="metric">
                                    <span>Fault Type</span>
                                    <strong>
                                        {workOrder.fault_type ?? "Not specified"}
                                    </strong>
                                </div>

                                <div className="metric">
                                    <span>Alert ID</span>
                                    <strong>
                                        {workOrder.alert_id ?? "—"}
                                    </strong>
                                </div>

                                <div className="metric">
                                    <span>Fault Event</span>
                                    <strong>
                                        {workOrder.fault_event_id ?? "—"}
                                    </strong>
                                </div>

                                <div className="metric">
                                    <span>Created</span>
                                    <strong>
                                        {new Date(
                                            workOrder.created_at
                                        ).toLocaleString()}
                                    </strong>
                                </div>
                            </div>

                            {workOrder.description && (
                                <div style={{ marginTop: "20px" }}>
                                    <p className="eyebrow">Description</p>

                                    <p>{workOrder.description}</p>
                                </div>
                            )}

                            {workOrder.ai_diagnosis && (
                                <div style={{ marginTop: "20px" }}>
                                    <p className="eyebrow">AI Diagnosis</p>

                                    <p>{workOrder.ai_diagnosis}</p>
                                </div>
                            )}

                            {workOrder.ai_recommendation && (
                                <div style={{ marginTop: "20px" }}>
                                    <p className="eyebrow">AI Recommendation</p>

                                    <p>{workOrder.ai_recommendation}</p>
                                </div>
                            )}

                            <div
                                style={{
                                    marginTop: "20px",
                                    display: "flex",
                                    justifyContent: "flex-end",
                                }}
                            >
                                <button
                                    type="button"
                                    onClick={() =>
                                        navigate(
                                            `/machines/${workOrder.machine_id}`
                                        )
                                    }
                                    style={{
                                        background: "transparent",
                                        border: "1px solid #285273",
                                        color: "#9ab3d0",
                                        padding: "9px 16px",
                                        borderRadius: "8px",
                                        cursor: "pointer",
                                    }}
                                >
                                    View Machine →
                                </button>
                            </div>
                        </article>
                    ))}
                </section>
            )}
        </main>
    );
}

export default WorkOrders;