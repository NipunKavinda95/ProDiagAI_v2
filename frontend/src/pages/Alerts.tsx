import { useEffect, useMemo, useState } from "react";
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

type AlertFilter =
    | "ALL"
    | "CRITICAL"
    | "FAULTED"
    | "WARNING"
    | "DEGRADING";

function Alerts() {
    const navigate = useNavigate();

    const [alerts, setAlerts] = useState<Alert[]>([]);
    const [error, setError] = useState("");
    const [filter, setFilter] = useState<AlertFilter>("ALL");
    const API_BASE = import.meta.env.VITE_API_URL || "http://127.0.0.1:5000";

    useEffect(() => {
        const loadAlerts = async () => {
            try {
                const response = await fetch(
                    `${API_BASE}/api/alerts`
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

    const counts = useMemo(() => {
        return {
            critical: alerts.filter(
                (alert) => alert.condition.toUpperCase() === "CRITICAL"
            ).length,

            faulted: alerts.filter(
                (alert) => alert.condition.toUpperCase() === "FAULTED"
            ).length,

            warning: alerts.filter(
                (alert) => alert.condition.toUpperCase() === "WARNING"
            ).length,

            degrading: alerts.filter(
                (alert) => alert.condition.toUpperCase() === "DEGRADING"
            ).length,
        };
    }, [alerts]);

    const filteredAlerts = useMemo(() => {
        if (filter === "ALL") {
            return alerts;
        }

        return alerts.filter(
            (alert) => alert.condition.toUpperCase() === filter
        );
    }, [alerts, filter]);

    const getSeverityMeta = (alert: Alert) => {
        const condition = alert.condition.toUpperCase();

        if (condition === "CRITICAL") {
            return {
                label: "CRITICAL",
                color: "#ff7b8b",
                background: "rgba(255, 72, 94, 0.10)",
                border: "rgba(255, 72, 94, 0.30)",
                glow: "rgba(255, 72, 94, 0.18)",
            };
        }

        if (condition === "FAULTED") {
            return {
                label: "FAULTED",
                color: "#ff6b7a",
                background: "rgba(239, 68, 68, 0.10)",
                border: "rgba(239, 68, 68, 0.30)",
                glow: "rgba(239, 68, 68, 0.16)",
            };
        }

        if (condition === "WARNING") {
            return {
                label: "WARNING",
                color: "#ffc857",
                background: "rgba(255, 190, 60, 0.10)",
                border: "rgba(255, 190, 60, 0.30)",
                glow: "rgba(255, 190, 60, 0.14)",
            };
        }

        return {
            label: "DEGRADING",
            color: "#63c8ff",
            background: "rgba(74, 177, 255, 0.10)",
            border: "rgba(74, 177, 255, 0.28)",
            glow: "rgba(74, 177, 255, 0.14)",
        };
    };

    const formatDate = (value: string) => {
        const date = new Date(value);

        if (Number.isNaN(date.getTime())) {
            return value;
        }

        return date.toLocaleString();
    };

    const formatRelativeTime = (value: string) => {
        const date = new Date(value);

        if (Number.isNaN(date.getTime())) {
            return "";
        }

        const diffSeconds = Math.max(
            0,
            Math.floor((Date.now() - date.getTime()) / 1000)
        );

        if (diffSeconds < 60) {
            return `${diffSeconds}s ago`;
        }

        const minutes = Math.floor(diffSeconds / 60);

        if (minutes < 60) {
            return `${minutes}m ago`;
        }

        const hours = Math.floor(minutes / 60);

        if (hours < 24) {
            return `${hours}h ago`;
        }

        return `${Math.floor(hours / 24)}d ago`;
    };

    const getAnomalyPercentage = (score: number | null) => {
        if (score === null || Number.isNaN(score)) {
            return 0;
        }

        const normalized = Math.abs(score);

        return Math.min(100, Math.max(0, normalized * 100));
    };

    if (error) {
        return (
            <main>
                <button
                    type="button"
                    onClick={() => navigate("/")}
                    style={{
                        marginBottom: "20px",
                        background: "transparent",
                        border: "1px solid #285273",
                        color: "#9ab3d0",
                        padding: "9px 15px",
                        borderRadius: "9px",
                        cursor: "pointer",
                    }}
                >
                    ← Fleet Dashboard
                </button>

                <section
                    className="panel"
                    style={{
                        padding: "36px",
                        border: "1px solid rgba(255,90,110,0.25)",
                    }}
                >
                    <p className="eyebrow">Monitoring error</p>

                    <h2
                        style={{
                            marginBottom: "10px",
                        }}
                    >
                        Unable to load alerts
                    </h2>

                    <p>{error}</p>
                </section>
            </main>
        );
    }

    return (
        <main>
            {/* PAGE HEADER */}
            <header
                style={{
                    display: "flex",
                    alignItems: "flex-end",
                    justifyContent: "space-between",
                    gap: "24px",
                    marginBottom: "28px",
                    paddingBottom: "24px",
                    borderBottom: "1px solid #1d3b57",
                }}
            >
                <div>
                    <button
                        type="button"
                        onClick={() => navigate("/")}
                        style={{
                            marginBottom: "18px",
                            background: "rgba(255,255,255,0.025)",
                            border: "1px solid #285273",
                            color: "#9ab3d0",
                            padding: "8px 14px",
                            borderRadius: "9px",
                            cursor: "pointer",
                        }}
                    >
                        ← Fleet Dashboard
                    </button>

                    <p className="eyebrow">Maintenance monitoring</p>

                    <h1
                        style={{
                            marginBottom: "8px",
                        }}
                    >
                        Active Alerts
                    </h1>

                    <p
                        style={{
                            color: "#7895ad",
                            maxWidth: "620px",
                            lineHeight: 1.6,
                            margin: 0,
                        }}
                    >
                        Real-time maintenance events requiring engineering
                        attention across the monitored fleet.
                    </p>
                </div>

                <div
                    style={{
                        minWidth: "170px",
                        padding: "14px 16px",
                        borderRadius: "14px",
                        border: "1px solid rgba(46,230,166,0.20)",
                        background: "rgba(46,230,166,0.045)",
                        textAlign: "right",
                    }}
                >
                    <div
                        style={{
                            display: "flex",
                            alignItems: "center",
                            justifyContent: "flex-end",
                            gap: "8px",
                            color: "#65e5b1",
                            fontSize: "12px",
                            fontWeight: 800,
                            letterSpacing: "1px",
                            textTransform: "uppercase",
                        }}
                    >
                        <span
                            style={{
                                width: "8px",
                                height: "8px",
                                borderRadius: "50%",
                                background: "#2ee6a6",
                                boxShadow:
                                    "0 0 12px rgba(46,230,166,0.75)",
                            }}
                        />

                        Live Monitoring
                    </div>

                    <div
                        style={{
                            marginTop: "7px",
                            color: "#6e879c",
                            fontSize: "11px",
                        }}
                    >
                        Auto-refreshing every 3s
                    </div>
                </div>
            </header>

            {/* SUMMARY CARDS */}
            <section
                style={{
                    display: "grid",
                    gridTemplateColumns:
                        "repeat(auto-fit, minmax(180px, 1fr))",
                    gap: "14px",
                    marginBottom: "26px",
                }}
            >
                <button
                    type="button"
                    onClick={() => setFilter("CRITICAL")}
                    style={{
                        textAlign: "left",
                        padding: "18px",
                        borderRadius: "16px",
                        border:
                            filter === "CRITICAL"
                                ? "1px solid rgba(255,72,94,0.42)"
                                : "1px solid rgba(255,72,94,0.18)",
                        background:
                            filter === "CRITICAL"
                                ? "rgba(255,72,94,0.11)"
                                : "rgba(255,72,94,0.045)",
                        color: "#ffffff",
                        cursor: "pointer",
                    }}
                >
                    <div
                        style={{
                            color: "#ff7b8b",
                            fontSize: "10px",
                            fontWeight: 800,
                            letterSpacing: "1.5px",
                        }}
                    >
                        CRITICAL
                    </div>

                    <div
                        style={{
                            marginTop: "7px",
                            fontSize: "30px",
                            fontWeight: 800,
                        }}
                    >
                        {counts.critical}
                    </div>

                    <div
                        style={{
                            marginTop: "3px",
                            color: "#7895ad",
                            fontSize: "11px",
                        }}
                    >
                        High failure risk
                    </div>
                </button>

                <button
                    type="button"
                    onClick={() => setFilter("FAULTED")}
                    style={{
                        textAlign: "left",
                        padding: "18px",
                        borderRadius: "16px",
                        border:
                            filter === "FAULTED"
                                ? "1px solid rgba(239,68,68,0.42)"
                                : "1px solid rgba(239,68,68,0.18)",
                        background:
                            filter === "FAULTED"
                                ? "rgba(239,68,68,0.11)"
                                : "rgba(239,68,68,0.045)",
                        color: "#ffffff",
                        cursor: "pointer",
                    }}
                >
                    <div
                        style={{
                            color: "#ff6b7a",
                            fontSize: "10px",
                            fontWeight: 800,
                            letterSpacing: "1.5px",
                        }}
                    >
                        FAULTED
                    </div>

                    <div
                        style={{
                            marginTop: "7px",
                            fontSize: "30px",
                            fontWeight: 800,
                        }}
                    >
                        {counts.faulted}
                    </div>

                    <div
                        style={{
                            marginTop: "3px",
                            color: "#7895ad",
                            fontSize: "11px",
                        }}
                    >
                        Machine stopped
                    </div>
                </button>

                <button
                    type="button"
                    onClick={() => setFilter("WARNING")}
                    style={{
                        textAlign: "left",
                        padding: "18px",
                        borderRadius: "16px",
                        border:
                            filter === "WARNING"
                                ? "1px solid rgba(255,190,60,0.42)"
                                : "1px solid rgba(255,190,60,0.18)",
                        background:
                            filter === "WARNING"
                                ? "rgba(255,190,60,0.11)"
                                : "rgba(255,190,60,0.045)",
                        color: "#ffffff",
                        cursor: "pointer",
                    }}
                >
                    <div
                        style={{
                            color: "#ffc857",
                            fontSize: "10px",
                            fontWeight: 800,
                            letterSpacing: "1.5px",
                        }}
                    >
                        WARNING
                    </div>

                    <div
                        style={{
                            marginTop: "7px",
                            fontSize: "30px",
                            fontWeight: 800,
                        }}
                    >
                        {counts.warning}
                    </div>

                    <div
                        style={{
                            marginTop: "3px",
                            color: "#7895ad",
                            fontSize: "11px",
                        }}
                    >
                        Requires attention
                    </div>
                </button>

                <button
                    type="button"
                    onClick={() => setFilter("DEGRADING")}
                    style={{
                        textAlign: "left",
                        padding: "18px",
                        borderRadius: "16px",
                        border:
                            filter === "DEGRADING"
                                ? "1px solid rgba(74,177,255,0.42)"
                                : "1px solid rgba(74,177,255,0.18)",
                        background:
                            filter === "DEGRADING"
                                ? "rgba(74,177,255,0.11)"
                                : "rgba(74,177,255,0.045)",
                        color: "#ffffff",
                        cursor: "pointer",
                    }}
                >
                    <div
                        style={{
                            color: "#63c8ff",
                            fontSize: "10px",
                            fontWeight: 800,
                            letterSpacing: "1.5px",
                        }}
                    >
                        DEGRADING
                    </div>

                    <div
                        style={{
                            marginTop: "7px",
                            fontSize: "30px",
                            fontWeight: 800,
                        }}
                    >
                        {counts.degrading}
                    </div>

                    <div
                        style={{
                            marginTop: "3px",
                            color: "#7895ad",
                            fontSize: "11px",
                        }}
                    >
                        Early degradation
                    </div>
                </button>
            </section>

            {/* ALERT TOOLBAR */}
            <section
                style={{
                    display: "flex",
                    alignItems: "center",
                    justifyContent: "space-between",
                    gap: "16px",
                    flexWrap: "wrap",
                    marginBottom: "16px",
                }}
            >
                <div>
                    <p
                        className="eyebrow"
                        style={{ marginBottom: "4px" }}
                    >
                        Alert stream
                    </p>

                    <div
                        style={{
                            color: "#9bb3c7",
                            fontSize: "13px",
                        }}
                    >
                        Showing{" "}
                        <strong style={{ color: "#ffffff" }}>
                            {filteredAlerts.length}
                        </strong>{" "}
                        of{" "}
                        <strong style={{ color: "#ffffff" }}>
                            {alerts.length}
                        </strong>{" "}
                        active alerts
                    </div>
                </div>

                <button
                    type="button"
                    onClick={() => setFilter("ALL")}
                    style={{
                        padding: "9px 14px",
                        borderRadius: "9px",
                        border:
                            filter === "ALL"
                                ? "1px solid rgba(88,215,255,0.35)"
                                : "1px solid #285273",
                        background:
                            filter === "ALL"
                                ? "rgba(88,215,255,0.10)"
                                : "rgba(255,255,255,0.025)",
                        color:
                            filter === "ALL"
                                ? "#58d7ff"
                                : "#9ab3d0",
                        cursor: "pointer",
                        fontSize: "12px",
                        fontWeight: 700,
                    }}
                >
                    SHOW ALL
                </button>
            </section>

            {/* ALERT LIST */}
            {filteredAlerts.length === 0 ? (
                <section
                    className="panel"
                    style={{
                        padding: "50px 30px",
                        textAlign: "center",
                        border: "1px solid rgba(46,230,166,0.18)",
                        background:
                            "linear-gradient(145deg, rgba(46,230,166,0.055), rgba(255,255,255,0.015))",
                    }}
                >
                    <div
                        style={{
                            width: "58px",
                            height: "58px",
                            margin: "0 auto 18px",
                            borderRadius: "18px",
                            display: "flex",
                            alignItems: "center",
                            justifyContent: "center",
                            background: "rgba(46,230,166,0.10)",
                            border: "1px solid rgba(46,230,166,0.20)",
                            color: "#2ee6a6",
                            fontSize: "25px",
                        }}
                    >
                        ✓
                    </div>

                    <p className="eyebrow">System status</p>

                    <h2
                        style={{
                            marginBottom: "8px",
                        }}
                    >
                        No alerts in this view
                    </h2>

                    <p
                        style={{
                            maxWidth: "500px",
                            margin: "0 auto",
                            color: "#7895ad",
                            lineHeight: 1.6,
                        }}
                    >
                        {filter === "ALL"
                            ? "All monitored machines are currently operating without active maintenance alerts."
                            : `There are currently no ${filter.toLowerCase()} alerts in the active alert stream.`}
                    </p>
                </section>
            ) : (
                <section
                    style={{
                        display: "grid",
                        gap: "14px",
                    }}
                >
                    {filteredAlerts.map((alert) => {
                        const meta = getSeverityMeta(alert);

                        const anomalyPercentage =
                            getAnomalyPercentage(alert.anomaly_score);

                        return (
                            <article
                                className="panel"
                                key={alert.alert_id}
                                style={{
                                    position: "relative",
                                    overflow: "hidden",
                                    padding: "22px",
                                    cursor: "pointer",
                                    border: `1px solid ${meta.border}`,
                                    background: `linear-gradient(145deg, ${meta.background}, rgba(8,20,34,0.72))`,
                                    boxShadow: `0 12px 30px rgba(0,0,0,0.14), 0 0 30px ${meta.glow}`,
                                }}
                                onClick={() =>
                                    navigate(
                                        `/machines/${alert.machine_id}`
                                    )
                                }
                            >
                                {/* Severity accent */}
                                <div
                                    style={{
                                        position: "absolute",
                                        left: 0,
                                        top: 0,
                                        bottom: 0,
                                        width: "4px",
                                        background: meta.color,
                                        boxShadow: `0 0 16px ${meta.glow}`,
                                    }}
                                />

                                {/* TOP ROW */}
                                <div
                                    style={{
                                        display: "flex",
                                        alignItems: "flex-start",
                                        justifyContent:
                                            "space-between",
                                        gap: "18px",
                                    }}
                                >
                                    <div
                                        style={{
                                            minWidth: 0,
                                        }}
                                    >
                                        <div
                                            style={{
                                                display: "flex",
                                                alignItems: "center",
                                                gap: "10px",
                                                flexWrap: "wrap",
                                                marginBottom: "10px",
                                            }}
                                        >
                                            <span
                                                style={{
                                                    display: "inline-flex",
                                                    alignItems: "center",
                                                    gap: "7px",
                                                    padding:
                                                        "6px 10px",
                                                    borderRadius:
                                                        "999px",
                                                    background:
                                                        meta.background,
                                                    border: `1px solid ${meta.border}`,
                                                    color: meta.color,
                                                    fontSize: "10px",
                                                    fontWeight: 800,
                                                    letterSpacing:
                                                        "1.2px",
                                                }}
                                            >
                                                <span
                                                    style={{
                                                        width: "6px",
                                                        height: "6px",
                                                        borderRadius:
                                                            "50%",
                                                        background:
                                                            meta.color,
                                                        boxShadow: `0 0 8px ${meta.color}`,
                                                    }}
                                                />

                                                {meta.label}
                                            </span>

                                            <span
                                                style={{
                                                    color: "#617c94",
                                                    fontSize: "10px",
                                                    fontWeight: 600,
                                                }}
                                            >
                                                ALERT #{alert.alert_id}
                                            </span>
                                        </div>

                                        <h2
                                            style={{
                                                margin: 0,
                                                fontSize: "20px",
                                                lineHeight: 1.25,
                                            }}
                                        >
                                            {alert.machine_name}
                                        </h2>

                                        <div
                                            style={{
                                                display: "flex",
                                                alignItems: "center",
                                                gap: "8px",
                                                marginTop: "7px",
                                                color: "#7895ad",
                                                fontSize: "12px",
                                            }}
                                        >
                                            <span
                                                style={{
                                                    color: "#58d7ff",
                                                    fontWeight: 700,
                                                }}
                                            >
                                                {alert.machine_id}
                                            </span>

                                            <span>•</span>

                                            <span>
                                                {alert.fault_type ??
                                                    "Unknown fault"}
                                            </span>
                                        </div>
                                    </div>

                                    <div
                                        style={{
                                            flexShrink: 0,
                                            textAlign: "right",
                                        }}
                                    >
                                        <div
                                            style={{
                                                color: meta.color,
                                                fontSize: "13px",
                                                fontWeight: 800,
                                            }}
                                        >
                                            {formatRelativeTime(
                                                alert.last_seen
                                            )}
                                        </div>

                                        <div
                                            style={{
                                                marginTop: "5px",
                                                color: "#607a90",
                                                fontSize: "10px",
                                            }}
                                        >
                                            Last seen
                                        </div>
                                    </div>
                                </div>

                                {/* METRICS */}
                                <div
                                    style={{
                                        display: "grid",
                                        gridTemplateColumns:
                                            "repeat(auto-fit, minmax(145px, 1fr))",
                                        gap: "10px",
                                        marginTop: "20px",
                                    }}
                                >
                                    <div
                                        style={{
                                            padding: "13px",
                                            borderRadius: "12px",
                                            background:
                                                "rgba(255,255,255,0.025)",
                                            border: "1px solid rgba(255,255,255,0.055)",
                                        }}
                                    >
                                        <div
                                            style={{
                                                color: "#607a90",
                                                fontSize: "9px",
                                                fontWeight: 800,
                                                letterSpacing: "1.1px",
                                                textTransform:
                                                    "uppercase",
                                            }}
                                        >
                                            Condition
                                        </div>

                                        <div
                                            style={{
                                                marginTop: "6px",
                                                color: meta.color,
                                                fontSize: "13px",
                                                fontWeight: 800,
                                            }}
                                        >
                                            {alert.condition}
                                        </div>
                                    </div>

                                    <div
                                        style={{
                                            padding: "13px",
                                            borderRadius: "12px",
                                            background:
                                                "rgba(255,255,255,0.025)",
                                            border: "1px solid rgba(255,255,255,0.055)",
                                        }}
                                    >
                                        <div
                                            style={{
                                                color: "#607a90",
                                                fontSize: "9px",
                                                fontWeight: 800,
                                                letterSpacing: "1.1px",
                                                textTransform:
                                                    "uppercase",
                                            }}
                                        >
                                            Status
                                        </div>

                                        <div
                                            style={{
                                                marginTop: "6px",
                                                color: "#d5e3ef",
                                                fontSize: "13px",
                                                fontWeight: 700,
                                            }}
                                        >
                                            {alert.status}
                                        </div>
                                    </div>

                                    <div
                                        style={{
                                            padding: "13px",
                                            borderRadius: "12px",
                                            background:
                                                "rgba(255,255,255,0.025)",
                                            border: "1px solid rgba(255,255,255,0.055)",
                                        }}
                                    >
                                        <div
                                            style={{
                                                color: "#607a90",
                                                fontSize: "9px",
                                                fontWeight: 800,
                                                letterSpacing: "1.1px",
                                                textTransform:
                                                    "uppercase",
                                            }}
                                        >
                                            Anomaly Score
                                        </div>

                                        <div
                                            style={{
                                                marginTop: "6px",
                                                color: "#ffffff",
                                                fontSize: "13px",
                                                fontWeight: 800,
                                            }}
                                        >
                                            {alert.anomaly_score !==
                                                null
                                                ? alert.anomaly_score.toFixed(
                                                    2
                                                )
                                                : "N/A"}
                                        </div>
                                    </div>

                                    <div
                                        style={{
                                            padding: "13px",
                                            borderRadius: "12px",
                                            background:
                                                "rgba(255,255,255,0.025)",
                                            border: "1px solid rgba(255,255,255,0.055)",
                                        }}
                                    >
                                        <div
                                            style={{
                                                color: "#607a90",
                                                fontSize: "9px",
                                                fontWeight: 800,
                                                letterSpacing: "1.1px",
                                                textTransform:
                                                    "uppercase",
                                            }}
                                        >
                                            Created
                                        </div>

                                        <div
                                            style={{
                                                marginTop: "6px",
                                                color: "#d5e3ef",
                                                fontSize: "11px",
                                                fontWeight: 600,
                                            }}
                                        >
                                            {formatRelativeTime(
                                                alert.created_at
                                            )}
                                        </div>
                                    </div>
                                </div>

                                {/* ANOMALY BAR */}
                                {alert.anomaly_score !== null && (
                                    <div
                                        style={{
                                            marginTop: "18px",
                                        }}
                                    >
                                        <div
                                            style={{
                                                display: "flex",
                                                alignItems: "center",
                                                justifyContent:
                                                    "space-between",
                                                marginBottom: "7px",
                                            }}
                                        >
                                            <span
                                                style={{
                                                    color: "#6e879c",
                                                    fontSize: "10px",
                                                    fontWeight: 700,
                                                    letterSpacing:
                                                        "0.8px",
                                                    textTransform:
                                                        "uppercase",
                                                }}
                                            >
                                                Anomaly intensity
                                            </span>

                                            <span
                                                style={{
                                                    color: meta.color,
                                                    fontSize: "10px",
                                                    fontWeight: 800,
                                                }}
                                            >
                                                {anomalyPercentage.toFixed(
                                                    0
                                                )}
                                                %
                                            </span>
                                        </div>

                                        <div
                                            style={{
                                                width: "100%",
                                                height: "5px",
                                                borderRadius:
                                                    "999px",
                                                background:
                                                    "rgba(255,255,255,0.07)",
                                                overflow: "hidden",
                                            }}
                                        >
                                            <div
                                                style={{
                                                    width: `${anomalyPercentage}%`,
                                                    height: "100%",
                                                    borderRadius:
                                                        "999px",
                                                    background:
                                                        meta.color,
                                                    boxShadow: `0 0 12px ${meta.glow}`,
                                                    transition:
                                                        "width 0.3s ease",
                                                }}
                                            />
                                        </div>
                                    </div>
                                )}

                                {/* REASONS */}
                                {alert.reasons.length > 0 && (
                                    <div
                                        style={{
                                            marginTop: "18px",
                                            paddingTop: "17px",
                                            borderTop:
                                                "1px solid rgba(255,255,255,0.06)",
                                        }}
                                    >
                                        <div
                                            style={{
                                                color: "#718ba1",
                                                fontSize: "9px",
                                                fontWeight: 800,
                                                letterSpacing:
                                                    "1.2px",
                                                textTransform:
                                                    "uppercase",
                                                marginBottom:
                                                    "9px",
                                            }}
                                        >
                                            Detection reasons
                                        </div>

                                        <div
                                            style={{
                                                display: "flex",
                                                flexWrap: "wrap",
                                                gap: "7px",
                                            }}
                                        >
                                            {alert.reasons.map(
                                                (reason) => (
                                                    <span
                                                        key={reason}
                                                        style={{
                                                            padding:
                                                                "6px 9px",
                                                            borderRadius:
                                                                "8px",
                                                            background:
                                                                "rgba(255,255,255,0.035)",
                                                            border: "1px solid rgba(255,255,255,0.065)",
                                                            color: "#a7bdcf",
                                                            fontSize:
                                                                "10px",
                                                        }}
                                                    >
                                                        {reason}
                                                    </span>
                                                )
                                            )}
                                        </div>
                                    </div>
                                )}

                                {/* FOOTER */}
                                <div
                                    style={{
                                        display: "flex",
                                        alignItems: "center",
                                        justifyContent:
                                            "space-between",
                                        gap: "16px",
                                        flexWrap: "wrap",
                                        marginTop: "18px",
                                        paddingTop: "15px",
                                        borderTop:
                                            "1px solid rgba(255,255,255,0.06)",
                                    }}
                                >
                                    <div
                                        style={{
                                            color: "#5f788e",
                                            fontSize: "10px",
                                        }}
                                    >
                                        Last updated{" "}
                                        {formatDate(alert.last_seen)}
                                    </div>

                                    <button
                                        type="button"
                                        onClick={(event) => {
                                            event.stopPropagation();

                                            navigate(
                                                `/machines/${alert.machine_id}`
                                            );
                                        }}
                                        style={{
                                            padding: "8px 12px",
                                            borderRadius: "8px",
                                            border: `1px solid ${meta.border}`,
                                            background:
                                                meta.background,
                                            color: meta.color,
                                            fontSize: "10px",
                                            fontWeight: 800,
                                            letterSpacing: "0.8px",
                                            cursor: "pointer",
                                        }}
                                    >
                                        VIEW MACHINE →
                                    </button>
                                </div>
                            </article>
                        );
                    })}
                </section>
            )}
        </main>
    );
}

export default Alerts;