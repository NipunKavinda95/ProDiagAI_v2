import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";

type SparePart = {
    part_id?: string;
    part_name?: string;
    equipment_type?: string;
    fault_type?: string;
    description?: string;
    estimated_cost_usd?: number;
    quantity?: number;
};

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
    spare_parts?: SparePart[];
    parts_cost_usd?: number | null;
    labour_cost_usd?: number | null;
    estimated_total_cost_usd?: number | null;
    approval_status?: string | null;
    engineer_name?: string | null;
    approval_comment?: string | null;
    approved_at?: string | null;
    created_at: string;
    updated_at: string;
    completed_at: string | null;
    completed_by?: string | null;
};

type WorkOrdersResponse = {
    count: number;
    work_orders: WorkOrder[];
};

function WorkOrders() {
    const navigate = useNavigate();

    const [workOrders, setWorkOrders] = useState<WorkOrder[]>([]);
    const [selectedWorkOrder, setSelectedWorkOrder] =
        useState<WorkOrder | null>(null);

    const [error, setError] = useState("");
    const [statusLoading, setStatusLoading] = useState(false);
    const [statusError, setStatusError] = useState("");

    const [completionEngineer, setCompletionEngineer] = useState("");

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

    useEffect(() => {
        loadWorkOrders();

        const intervalId = setInterval(loadWorkOrders, 5000);

        return () => clearInterval(intervalId);
    }, []);

    const getPriorityClass = (priority: string) =>
        `work-order-priority ${priority.toLowerCase()}`;

    const getStatusClass = (status: string) =>
        `work-order-status ${status.toLowerCase()}`;

    const formatDate = (value: string | null | undefined) => {
        if (!value) return "—";

        const date = new Date(value);

        if (Number.isNaN(date.getTime())) {
            return value;
        }

        return date.toLocaleString();
    };

    const formatMoney = (value: number | null | undefined) => {
        if (value === null || value === undefined) {
            return "—";
        }

        return `$${value.toFixed(2)}`;
    };

    const updateStatus = async (
        workOrder: WorkOrder,
        status: string,
        engineerName?: string
    ) => {
        setStatusLoading(true);
        setStatusError("");

        try {
            const response = await fetch(
                `http://127.0.0.1:5000/api/work-orders/${workOrder.work_order_id}/status`,
                {
                    method: "PATCH",
                    headers: {
                        "Content-Type": "application/json",
                    },
                    body: JSON.stringify({
                        status,
                        engineer_name:
                            engineerName?.trim() || null,
                    }),
                }
            );

            const data = await response.json();

            if (!response.ok) {
                throw new Error(
                    data.error || "Could not update work order"
                );
            }

            const updatedWorkOrder: WorkOrder = {
                ...data,
                completed_by:
                    data.completed_by ??
                    (status === "COMPLETED"
                        ? engineerName?.trim() || null
                        : workOrder.completed_by),
            };

            setWorkOrders((current) =>
                current.map((item) =>
                    item.work_order_id ===
                        updatedWorkOrder.work_order_id
                        ? updatedWorkOrder
                        : item
                )
            );

            setSelectedWorkOrder(updatedWorkOrder);

            if (status === "COMPLETED") {
                setCompletionEngineer("");
            }
        } catch (err) {
            setStatusError(
                err instanceof Error
                    ? err.message
                    : "Status update failed"
            );
        } finally {
            setStatusLoading(false);
        }
    };

    const openWorkOrder = (workOrder: WorkOrder) => {
        setSelectedWorkOrder(workOrder);
        setStatusError("");
        setCompletionEngineer(
            workOrder.completed_by ?? ""
        );
    };

    const closeWorkOrder = () => {
        setSelectedWorkOrder(null);
        setStatusError("");
        setCompletionEngineer("");
    };

    const startWork = () => {
        if (!selectedWorkOrder) return;

        updateStatus(
            selectedWorkOrder,
            "IN_PROGRESS"
        );
    };

    const completeWork = () => {
        if (!selectedWorkOrder) return;

        if (!completionEngineer.trim()) {
            setStatusError(
                "Please enter the engineer name before completing this work order."
            );
            return;
        }

        updateStatus(
            selectedWorkOrder,
            "COMPLETED",
            completionEngineer
        );
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

                    <p className="eyebrow">
                        Maintenance execution
                    </p>

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
                    <p className="eyebrow">
                        No maintenance actions
                    </p>

                    <h2>No work orders yet</h2>

                    <p>
                        Work orders will appear here after an
                        engineer reviews and approves a maintenance
                        proposal.
                    </p>
                </section>
            ) : (
                <section
                    style={{
                        display: "grid",
                        gap: "12px",
                    }}
                >
                    {workOrders.map((workOrder) => (
                        <article
                            className="panel"
                            key={workOrder.work_order_id}
                            onClick={() =>
                                openWorkOrder(workOrder)
                            }
                            style={{
                                cursor: "pointer",
                                padding: "18px 22px",
                            }}
                        >
                            <div
                                style={{
                                    display: "flex",
                                    justifyContent:
                                        "space-between",
                                    alignItems: "center",
                                    gap: "18px",
                                }}
                            >
                                <div style={{ minWidth: 0 }}>
                                    <p
                                        className="eyebrow"
                                        style={{
                                            marginBottom: "5px",
                                        }}
                                    >
                                        Work Order #
                                        {workOrder.work_order_id}
                                    </p>

                                    <h2
                                        style={{
                                            margin: "0 0 5px",
                                            fontSize: "1.15rem",
                                        }}
                                    >
                                        {workOrder.title}
                                    </h2>

                                    <p
                                        style={{
                                            margin: 0,
                                            color: "#9ab3d0",
                                        }}
                                    >
                                        {workOrder.machine_name} ·{" "}
                                        {workOrder.machine_id}
                                    </p>
                                </div>

                                <div
                                    style={{
                                        display: "flex",
                                        gap: "8px",
                                        flexWrap: "wrap",
                                    }}
                                >
                                    <span
                                        className={getPriorityClass(
                                            workOrder.priority
                                        )}
                                    >
                                        {workOrder.priority}
                                    </span>

                                    <span
                                        className={getStatusClass(
                                            workOrder.status
                                        )}
                                    >
                                        {workOrder.status}
                                    </span>
                                </div>
                            </div>

                            <div
                                style={{
                                    display: "flex",
                                    alignItems: "center",
                                    gap: "20px",
                                    flexWrap: "wrap",
                                    marginTop: "12px",
                                    fontSize: "0.85rem",
                                    color: "#8fa8c4",
                                }}
                            >
                                <span>
                                    Fault:{" "}
                                    <strong>
                                        {workOrder.fault_type ??
                                            "Not specified"}
                                    </strong>
                                </span>

                                <span>
                                    Alert:{" "}
                                    <strong>
                                        {workOrder.alert_id ?? "—"}
                                    </strong>
                                </span>

                                <span>
                                    Event:{" "}
                                    <strong>
                                        {workOrder.fault_event_id ??
                                            "—"}
                                    </strong>
                                </span>

                                <span>
                                    Created:{" "}
                                    <strong>
                                        {formatDate(
                                            workOrder.created_at
                                        )}
                                    </strong>
                                </span>

                                <span
                                    style={{
                                        marginLeft: "auto",
                                        color: "#58d7ff",
                                        fontWeight: 600,
                                    }}
                                >
                                    View Details →
                                </span>
                            </div>
                        </article>
                    ))}
                </section>
            )}

            {selectedWorkOrder && (
                <div
                    onClick={closeWorkOrder}
                    style={{
                        position: "fixed",
                        inset: 0,
                        zIndex: 1000,
                        background:
                            "rgba(2, 10, 20, 0.82)",
                        display: "flex",
                        alignItems: "center",
                        justifyContent: "center",
                        padding: "24px",
                    }}
                >
                    <section
                        className="panel"
                        onClick={(event) =>
                            event.stopPropagation()
                        }
                        style={{
                            width: "min(1100px, 100%)",
                            maxHeight: "92vh",
                            overflowY: "auto",
                            padding: "30px",
                        }}
                    >
                        <div
                            style={{
                                display: "flex",
                                justifyContent:
                                    "space-between",
                                gap: "20px",
                                alignItems: "flex-start",
                            }}
                        >
                            <div>
                                <p className="eyebrow">
                                    Work Order #
                                    {
                                        selectedWorkOrder.work_order_id
                                    }
                                </p>

                                <h1
                                    style={{
                                        fontSize: "2rem",
                                        marginBottom: "8px",
                                    }}
                                >
                                    {selectedWorkOrder.title}
                                </h1>

                                <p>
                                    {
                                        selectedWorkOrder.machine_name
                                    }{" "}
                                    ·{" "}
                                    {
                                        selectedWorkOrder.machine_id
                                    }
                                </p>
                            </div>

                            <div
                                style={{
                                    display: "flex",
                                    gap: "8px",
                                    flexWrap: "wrap",
                                }}
                            >
                                <span
                                    className={getPriorityClass(
                                        selectedWorkOrder.priority
                                    )}
                                >
                                    {selectedWorkOrder.priority}
                                </span>

                                <span
                                    className={getStatusClass(
                                        selectedWorkOrder.status
                                    )}
                                >
                                    {selectedWorkOrder.status}
                                </span>
                            </div>
                        </div>

                        <div
                            style={{
                                display: "grid",
                                gridTemplateColumns:
                                    "repeat(auto-fit, minmax(180px, 1fr))",
                                gap: "12px",
                                marginTop: "24px",
                            }}
                        >
                            <div className="metric">
                                <span>Fault Type</span>
                                <strong>
                                    {selectedWorkOrder.fault_type ??
                                        "Not specified"}
                                </strong>
                            </div>

                            <div className="metric">
                                <span>Alert ID</span>
                                <strong>
                                    {selectedWorkOrder.alert_id ??
                                        "—"}
                                </strong>
                            </div>

                            <div className="metric">
                                <span>Fault Event</span>
                                <strong>
                                    {
                                        selectedWorkOrder.fault_event_id ??
                                        "—"
                                    }
                                </strong>
                            </div>

                            <div className="metric">
                                <span>Created</span>
                                <strong>
                                    {formatDate(
                                        selectedWorkOrder.created_at
                                    )}
                                </strong>
                            </div>
                        </div>

                        {selectedWorkOrder.description && (
                            <div
                                style={{
                                    marginTop: "26px",
                                }}
                            >
                                <p className="eyebrow">
                                    Work Description
                                </p>

                                <p>
                                    {
                                        selectedWorkOrder.description
                                    }
                                </p>
                            </div>
                        )}

                        {selectedWorkOrder.ai_diagnosis && (
                            <div
                                style={{
                                    marginTop: "26px",
                                }}
                            >
                                <p className="eyebrow">
                                    AI Diagnosis
                                </p>

                                <p>
                                    {
                                        selectedWorkOrder.ai_diagnosis
                                    }
                                </p>
                            </div>
                        )}

                        {selectedWorkOrder.ai_recommendation && (
                            <div
                                style={{
                                    marginTop: "26px",
                                }}
                            >
                                <p className="eyebrow">
                                    Maintenance Actions
                                </p>

                                <div
                                    style={{
                                        display: "flex",
                                        flexDirection: "column",
                                        gap: "8px",
                                    }}
                                >
                                    {selectedWorkOrder.ai_recommendation
                                        .split("\n")
                                        .map((action) =>
                                            action.trim()
                                        )
                                        .filter(Boolean)
                                        .map(
                                            (
                                                action,
                                                index
                                            ) => (
                                                <div
                                                    key={`${selectedWorkOrder.work_order_id}-action-${index}`}
                                                    style={{
                                                        display: "flex",
                                                        alignItems:
                                                            "flex-start",
                                                        gap: "10px",
                                                        padding:
                                                            "9px 12px",
                                                        borderLeft:
                                                            "2px solid #58d7ff",
                                                        background:
                                                            "rgba(8, 25, 43, 0.55)",
                                                        borderRadius:
                                                            "6px",
                                                    }}
                                                >
                                                    <strong
                                                        style={{
                                                            color:
                                                                "#58d7ff",
                                                            minWidth:
                                                                "20px",
                                                        }}
                                                    >
                                                        {index + 1}.
                                                    </strong>

                                                    <span>
                                                        {action}
                                                    </span>
                                                </div>
                                            )
                                        )}
                                </div>
                            </div>
                        )}

                        {selectedWorkOrder.spare_parts &&
                            selectedWorkOrder.spare_parts.length > 0 && (
                                <div style={{ marginTop: "26px" }}>
                                    <p
                                        className="eyebrow"
                                        style={{ marginBottom: "12px" }}
                                    >
                                        Required Spare Parts
                                    </p>

                                    <div
                                        style={{
                                            overflowX: "auto",
                                            border: "1px solid #285273",
                                            borderRadius: "10px",
                                        }}
                                    >
                                        <table
                                            style={{
                                                width: "100%",
                                                minWidth: "650px",
                                                borderCollapse: "collapse",
                                            }}
                                        >
                                            <thead>
                                                <tr
                                                    style={{
                                                        background: "rgba(8, 25, 43, 0.85)",
                                                        color: "#9ab3d0",
                                                    }}
                                                >
                                                    {['Part No.', 'Spare Part', 'Qty', 'Unit Price', 'Total'].map((heading) => (
                                                        <th
                                                            key={heading}
                                                            style={{
                                                                textAlign: heading === 'Qty' ? 'center' : heading === 'Unit Price' || heading === 'Total' ? 'right' : 'left',
                                                                padding: "12px 14px",
                                                                fontSize: "0.78rem",
                                                                borderBottom: "1px solid #285273",
                                                            }}
                                                        >
                                                            {heading}
                                                        </th>
                                                    ))}
                                                </tr>
                                            </thead>

                                            <tbody>
                                                {selectedWorkOrder.spare_parts.map((part, index) => {
                                                    const quantity = part.quantity ?? 1;
                                                    const unitPrice = part.estimated_cost_usd ?? 0;
                                                    const lineTotal = quantity * unitPrice;

                                                    return (
                                                        <tr
                                                            key={part.part_id ?? index}
                                                            style={{
                                                                borderBottom: "1px solid rgba(40, 82, 115, 0.55)",
                                                            }}
                                                        >
                                                            <td
                                                                style={{
                                                                    padding: "13px 14px",
                                                                    color: "#58d7ff",
                                                                    fontWeight: 700,
                                                                    whiteSpace: "nowrap",
                                                                }}
                                                            >
                                                                {part.part_id ?? "—"}
                                                            </td>
                                                            <td style={{ padding: "13px 14px" }}>
                                                                <strong>{part.part_name ?? "Replacement Part"}</strong>
                                                                {part.description && (
                                                                    <span
                                                                        style={{
                                                                            display: "block",
                                                                            marginTop: "4px",
                                                                            color: "#8fa8c4",
                                                                            fontSize: "0.78rem",
                                                                        }}
                                                                    >
                                                                        {part.description}
                                                                    </span>
                                                                )}
                                                            </td>
                                                            <td
                                                                style={{
                                                                    padding: "13px 14px",
                                                                    textAlign: "center",
                                                                    fontWeight: 600,
                                                                }}
                                                            >
                                                                {quantity}
                                                            </td>
                                                            <td
                                                                style={{
                                                                    padding: "13px 14px",
                                                                    textAlign: "right",
                                                                }}
                                                            >
                                                                {formatMoney(unitPrice)}
                                                            </td>
                                                            <td
                                                                style={{
                                                                    padding: "13px 14px",
                                                                    textAlign: "right",
                                                                    color: "#7ee7c7",
                                                                    fontWeight: 700,
                                                                }}
                                                            >
                                                                {formatMoney(lineTotal)}
                                                            </td>
                                                        </tr>
                                                    );
                                                })}
                                            </tbody>

                                            <tfoot>
                                                <tr style={{ background: "rgba(8, 25, 43, 0.7)" }}>
                                                    <td
                                                        colSpan={2}
                                                        style={{
                                                            padding: "13px 14px",
                                                            fontWeight: 700,
                                                            color: "#d9e8f7",
                                                        }}
                                                    >
                                                        Parts Total
                                                    </td>
                                                    <td
                                                        style={{
                                                            padding: "13px 14px",
                                                            textAlign: "center",
                                                            fontWeight: 700,
                                                        }}
                                                    >
                                                        {selectedWorkOrder.spare_parts.reduce(
                                                            (total, part) => total + (part.quantity ?? 1),
                                                            0
                                                        )}
                                                    </td>
                                                    <td style={{ padding: "13px 14px" }} />
                                                    <td
                                                        style={{
                                                            padding: "13px 14px",
                                                            textAlign: "right",
                                                            color: "#7ee7c7",
                                                            fontWeight: 800,
                                                        }}
                                                    >
                                                        {formatMoney(selectedWorkOrder.parts_cost_usd)}
                                                    </td>
                                                </tr>
                                            </tfoot>
                                        </table>
                                    </div>
                                </div>
                            )}

                        <div
                            style={{
                                marginTop: "26px",
                            }}
                        >
                            <p className="eyebrow">
                                Maintenance Cost
                            </p>

                            <div
                                style={{
                                    display: "grid",
                                    gridTemplateColumns:
                                        "repeat(auto-fit, minmax(180px, 1fr))",
                                    gap: "12px",
                                }}
                            >
                                <div className="metric">
                                    <span>Parts</span>
                                    <strong>
                                        {formatMoney(
                                            selectedWorkOrder.parts_cost_usd
                                        )}
                                    </strong>
                                </div>

                                <div className="metric">
                                    <span>Labour</span>
                                    <strong>
                                        {formatMoney(
                                            selectedWorkOrder.labour_cost_usd
                                        )}
                                    </strong>
                                </div>

                                <div className="metric">
                                    <span>
                                        Estimated Total
                                    </span>
                                    <strong>
                                        {formatMoney(
                                            selectedWorkOrder.estimated_total_cost_usd
                                        )}
                                    </strong>
                                </div>
                            </div>
                        </div>

                        <div
                            style={{
                                marginTop: "26px",
                            }}
                        >
                            <p className="eyebrow">
                                Approval
                            </p>

                            <div
                                style={{
                                    display: "grid",
                                    gridTemplateColumns:
                                        "repeat(auto-fit, minmax(180px, 1fr))",
                                    gap: "12px",
                                }}
                            >
                                <div className="metric">
                                    <span>
                                        Approval Status
                                    </span>
                                    <strong>
                                        {
                                            selectedWorkOrder.approval_status ??
                                            "—"
                                        }
                                    </strong>
                                </div>

                                <div className="metric">
                                    <span>
                                        Approved By
                                    </span>
                                    <strong>
                                        {
                                            selectedWorkOrder.engineer_name ??
                                            "—"
                                        }
                                    </strong>
                                </div>

                                <div className="metric">
                                    <span>Approved</span>
                                    <strong>
                                        {formatDate(
                                            selectedWorkOrder.approved_at
                                        )}
                                    </strong>
                                </div>
                            </div>

                            {selectedWorkOrder.approval_comment && (
                                <p
                                    style={{
                                        marginTop: "12px",
                                    }}
                                >
                                    {
                                        selectedWorkOrder.approval_comment
                                    }
                                </p>
                            )}
                        </div>

                        <div
                            style={{
                                marginTop: "26px",
                            }}
                        >
                            <p className="eyebrow">
                                Work Order Timeline
                            </p>

                            <div
                                style={{
                                    display: "grid",
                                    gridTemplateColumns:
                                        "repeat(auto-fit, minmax(180px, 1fr))",
                                    gap: "12px",
                                }}
                            >
                                <div className="metric">
                                    <span>Created</span>
                                    <strong>
                                        {formatDate(
                                            selectedWorkOrder.created_at
                                        )}
                                    </strong>
                                </div>

                                <div className="metric">
                                    <span>
                                        Last Updated
                                    </span>
                                    <strong>
                                        {formatDate(
                                            selectedWorkOrder.updated_at
                                        )}
                                    </strong>
                                </div>

                                <div className="metric">
                                    <span>Completed At</span>
                                    <strong>
                                        {formatDate(
                                            selectedWorkOrder.completed_at
                                        )}
                                    </strong>
                                </div>

                                <div className="metric">
                                    <span>Completed By</span>
                                    <strong>
                                        {selectedWorkOrder.completed_by ??
                                            "—"}
                                    </strong>
                                </div>
                            </div>
                        </div>

                        {selectedWorkOrder.status ===
                            "IN_PROGRESS" && (
                                <div
                                    style={{
                                        marginTop: "26px",
                                        padding: "18px",
                                        border:
                                            "1px solid #285273",
                                        borderRadius: "10px",
                                        background:
                                            "rgba(8, 25, 43, 0.65)",
                                    }}
                                >
                                    <p className="eyebrow">
                                        Complete Work Order
                                    </p>

                                    <label
                                        htmlFor="completion-engineer"
                                        style={{
                                            display: "block",
                                            marginBottom: "8px",
                                            color: "#b8c7d8",
                                        }}
                                    >
                                        Engineer completing the
                                        maintenance
                                    </label>

                                    <input
                                        id="completion-engineer"
                                        type="text"
                                        value={completionEngineer}
                                        onChange={(event) =>
                                            setCompletionEngineer(
                                                event.target.value
                                            )
                                        }
                                        placeholder="Enter engineer name"
                                        disabled={statusLoading}
                                        style={{
                                            width: "100%",
                                            boxSizing:
                                                "border-box",
                                            padding: "11px 13px",
                                            border:
                                                "1px solid #285273",
                                            borderRadius: "8px",
                                            background:
                                                "rgba(3, 15, 28, 0.9)",
                                            color: "#e8f3ff",
                                            outline: "none",
                                            marginBottom: "12px",
                                        }}
                                    />

                                    <button
                                        type="button"
                                        disabled={
                                            statusLoading ||
                                            !completionEngineer.trim()
                                        }
                                        onClick={completeWork}
                                        style={{
                                            padding:
                                                "10px 16px",
                                            borderRadius: "8px",
                                            border:
                                                "1px solid #63e6a8",
                                            background:
                                                "rgba(30, 130, 90, 0.2)",
                                            color: "#63e6a8",
                                            cursor:
                                                statusLoading ||
                                                    !completionEngineer.trim()
                                                    ? "not-allowed"
                                                    : "pointer",
                                            fontWeight: 600,
                                            opacity:
                                                !completionEngineer.trim()
                                                    ? 0.5
                                                    : 1,
                                        }}
                                    >
                                        {statusLoading
                                            ? "Completing..."
                                            : "✓ Mark Completed"}
                                    </button>
                                </div>
                            )}

                        {statusError && (
                            <p
                                style={{
                                    marginTop: "18px",
                                    color: "#ff8f8f",
                                }}
                            >
                                {statusError}
                            </p>
                        )}

                        <div
                            style={{
                                display: "flex",
                                justifyContent:
                                    "space-between",
                                alignItems: "center",
                                gap: "12px",
                                flexWrap: "wrap",
                                marginTop: "30px",
                                paddingTop: "20px",
                                borderTop:
                                    "1px solid #1d3b57",
                            }}
                        >
                            <div
                                style={{
                                    display: "flex",
                                    gap: "8px",
                                    flexWrap: "wrap",
                                }}
                            >
                                {selectedWorkOrder.status ===
                                    "OPEN" && (
                                        <button
                                            type="button"
                                            disabled={
                                                statusLoading
                                            }
                                            onClick={startWork}
                                            style={{
                                                padding:
                                                    "10px 16px",
                                                borderRadius:
                                                    "8px",
                                                border:
                                                    "1px solid #58d7ff",
                                                background:
                                                    "rgba(25, 100, 130, 0.2)",
                                                color:
                                                    "#58d7ff",
                                                cursor:
                                                    "pointer",
                                                fontWeight: 600,
                                            }}
                                        >
                                            {statusLoading
                                                ? "Updating..."
                                                : "Start Work"}
                                        </button>
                                    )}
                            </div>

                            <div
                                style={{
                                    display: "flex",
                                    gap: "8px",
                                }}
                            >
                                <button
                                    type="button"
                                    onClick={() =>
                                        navigate(
                                            `/machines/${selectedWorkOrder.machine_id}`
                                        )
                                    }
                                    style={{
                                        padding:
                                            "10px 16px",
                                        borderRadius:
                                            "8px",
                                        border:
                                            "1px solid #285273",
                                        background:
                                            "rgba(18, 45, 70, 0.8)",
                                        color:
                                            "#9ed8ff",
                                        cursor:
                                            "pointer",
                                    }}
                                >
                                    View Machine →
                                </button>

                                <button
                                    type="button"
                                    onClick={closeWorkOrder}
                                    style={{
                                        padding:
                                            "10px 16px",
                                        borderRadius:
                                            "8px",
                                        border:
                                            "1px solid #46627d",
                                        background:
                                            "transparent",
                                        color:
                                            "#b8c7d8",
                                        cursor:
                                            "pointer",
                                    }}
                                >
                                    Close
                                </button>
                            </div>
                        </div>
                    </section>
                </div>
            )}
        </main>
    );
}

export default WorkOrders;