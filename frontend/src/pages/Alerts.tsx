import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";

type Alert = {
    alert_id: number;
    machine_id: string;
    machine_name: string;
    severity: string;
    condition: string;
    status: string;
    fault_type: string | null;
    reasons: string[];
    anomaly_score: number | null;
    created_at: string;
    last_seen: string;
};

type AlertsResponse = {
    active_alerts: Alert[];
    count: number;
};

function Alerts() {
    const navigate = useNavigate();

    const [alerts, setAlerts] = useState<Alert[]>([]);
    const [error, setError] = useState("");

    useEffect(() => {
        const loadAlerts = async () => {
            try {
                const response = await fetch(
                    "http://127.0.0.1:5000/api/alerts"
                );

                if (!response.ok) {
                    throw new Error("Alerts API is not available");
                }

                const data: AlertsResponse = await response.json();

                setAlerts(data.active_alerts);
                setError("");
            } catch (err) {
                setError(
                    err instanceof Error ? err.message : "Unknown error"
                );
            }
        };

        loadAlerts();

        const intervalId = setInterval(loadAlerts, 3000);

        return () => clearInterval(intervalId);
    }, []);

    if (error) {
        return (
            <main>
                <p>Connection error: {error}</p>

                <button type="button" onClick={() => navigate("/")}>
                    ← Fleet Dashboard
                </button>
            </main>
        );
    }

    return (
        <main>
            <header
                style={{
                    display: "flex",
                    alignItems: "center",
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

                    <p className="eyebrow">Maintenance monitoring</p>

                    <h1>Active Alerts</h1>

                    <p>
                        {alerts.length} active alert
                        {alerts.length !== 1 ? "s" : ""}
                    </p>
                </div>

                <div
                    style={{
                        textAlign: "right",
                        color: "#7ee7c7",
                        fontSize: "0.85rem",
                    }}
                >
                    ● Live Monitoring
                </div>
            </header>

            {alerts.length === 0 ? (
                <section className="panel">
                    <p className="eyebrow">System status</p>
                    <h2>No active alerts</h2>
                    <p>
                        All monitored machines are currently operating without
                        active maintenance alerts.
                    </p>
                </section>
            ) : (
                <section
                    style={{
                        display: "grid",
                        gap: "16px",
                    }}
                >
                    {alerts.map((alert) => (
                        <article
                            className="panel"
                            key={alert.alert_id}
                            style={{ cursor: "pointer" }}
                            onClick={() =>
                                navigate(`/machines/${alert.machine_id}`)
                            }
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
                                        Alert #{alert.alert_id}
                                    </p>

                                    <h2>{alert.machine_name}</h2>

                                    <p>
                                        Machine ID: {alert.machine_id}
                                    </p>
                                </div>

                                <span
                                    className={`health-badge ${alert.condition.toLowerCase()}`}
                                    style={{
                                        minWidth: "110px",
                                        textAlign: "center",
                                    }}
                                >
                                    <strong>{alert.severity}</strong>
                                </span>
                            </div>

                            <div
                                style={{
                                    display: "grid",
                                    gridTemplateColumns:
                                        "repeat(auto-fit, minmax(160px, 1fr))",
                                    gap: "12px",
                                    marginTop: "20px",
                                }}
                            >
                                <div className="metric">
                                    <span>Condition</span>
                                    <strong>{alert.condition}</strong>
                                </div>

                                <div className="metric">
                                    <span>Fault Type</span>
                                    <strong>
                                        {alert.fault_type ?? "Unknown"}
                                    </strong>
                                </div>

                                <div className="metric">
                                    <span>Status</span>
                                    <strong>{alert.status}</strong>
                                </div>

                                <div className="metric">
                                    <span>Anomaly Score</span>
                                    <strong>
                                        {alert.anomaly_score !== null
                                            ? alert.anomaly_score.toFixed(2)
                                            : "N/A"}
                                    </strong>
                                </div>
                            </div>

                            {alert.reasons.length > 0 && (
                                <>
                                    <p
                                        className="eyebrow"
                                        style={{ marginTop: "20px" }}
                                    >
                                        Alert reasons
                                    </p>

                                    <ul className="risk-list">
                                        {alert.reasons.map((reason) => (
                                            <li key={reason}>{reason}</li>
                                        ))}
                                    </ul>
                                </>
                            )}

                            <p className="live-status">
                                Created{" "}
                                {new Date(alert.created_at).toLocaleString()}
                                {" · "}
                                Last seen{" "}
                                {new Date(alert.last_seen).toLocaleString()}
                            </p>
                        </article>
                    ))}
                </section>
            )}
        </main>
    );
}

export default Alerts;