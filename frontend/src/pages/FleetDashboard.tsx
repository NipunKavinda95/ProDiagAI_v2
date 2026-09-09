import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";

type MachineData = {
    machine_id: string;
    machine_name: string;
    timestamp: string;
    temperature_c: number;
    vibration_mm_s: number;
    current_a: number;
    rpm: number;
    status: string;
    condition: string;
    health_score: number;
    health_status:
    | "HEALTHY"
    | "DEGRADING"
    | "WARNING"
    | "CRITICAL"
    | "FAULTED";
    risk_reasons: string[];
};

type TelemetryResponse = {
    count: number;
    machines: MachineData[];
};

function getOperationalStatus(machine: MachineData) {
    const condition = (
        machine.condition ||
        machine.health_status ||
        "HEALTHY"
    ).toUpperCase();

    // Actual machine states always take priority.
    if (condition === "FAULT" || condition === "FAULTED") {
        return "FAULTED";
    }

    if (condition === "REPAIRING") {
        return "REPAIRING";
    }

    if (condition === "RESTART") {
        return "RESTART";
    }

    // For operating machines, the displayed status follows
    // the ML health score so score and status always agree.
    const score = Number(machine.health_score);

    if (score < 20) {
        return "FAULTED";
    }

    if (score < 40) {
        return "CRITICAL";
    }

    if (score < 60) {
        return "WARNING";
    }

    if (score < 80) {
        return "DEGRADING";
    }

    return "HEALTHY";
}

function FleetDashboard() {
    const navigate = useNavigate();

    const [machines, setMachines] = useState<MachineData[]>([]);
    const [error, setError] = useState("");

    useEffect(() => {
        const loadTelemetry = async () => {
            try {
                const response = await fetch("http://127.0.0.1:5000/api/telemetry");

                if (!response.ok) {
                    throw new Error("Telemetry API is not available");
                }

                const data: TelemetryResponse = await response.json();

                setMachines(data.machines);
                setError("");
            } catch (err) {
                setError(err instanceof Error ? err.message : "Unknown error");
            }
        };

        loadTelemetry();

        const intervalId = setInterval(loadTelemetry, 1000);

        return () => clearInterval(intervalId);
    }, []);

    const criticalCount = machines.filter(
        (machine) => getOperationalStatus(machine) === "CRITICAL"
    ).length;

    const faultedCount = machines.filter(
        (machine) => getOperationalStatus(machine) === "FAULTED"
    ).length;

    const warningCount = machines.filter(
        (machine) => getOperationalStatus(machine) === "WARNING"
    ).length;

    const degradingCount = machines.filter(
        (machine) => getOperationalStatus(machine) === "DEGRADING"
    ).length;

    const healthyCount = machines.filter(
        (machine) => getOperationalStatus(machine) === "HEALTHY"
    ).length;

    if (error) {
        return (
            <main>
                <p>Connection error: {error}</p>
            </main>
        );
    }

    if (machines.length === 0) {
        return (
            <main>
                <p>Waiting for live telemetry from all machines...</p>
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
                    <img
                        src="/logo.png"
                        alt="ProDiag AI"
                        style={{
                            display: "block",
                            width: "min(520px, 100%)",
                            height: "auto",
                        }}
                    />
                </div>

                <div
                    style={{
                        textAlign: "right",
                        whiteSpace: "nowrap",
                    }}
                >
                    <span
                        style={{
                            display: "inline-flex",
                            alignItems: "center",
                            gap: "8px",
                            color: "#7ee7c7",
                            fontSize: "0.78rem",
                            fontWeight: 600,
                            letterSpacing: "0.08em",
                            textTransform: "uppercase",
                        }}
                    >
                        <span
                            style={{
                                width: "8px",
                                height: "8px",
                                borderRadius: "50%",
                                background: "#35e29c",
                                boxShadow: "0 0 0 4px #35e29c24",
                            }}
                        />
                        System Online
                    </span>

                    <p
                        style={{
                            margin: "6px 0 0",
                            color: "#7895b0",
                            fontSize: "0.78rem",
                        }}
                    >
                        Industrial Asset Intelligence
                    </p>
                </div>
            </header>

            <section className="fleet-overview">
                <div>
                    <p className="eyebrow">Fleet overview</p>
                    <h2>{machines.length} connected machines</h2>
                </div>

                <div className="fleet-counts">
                    <span className="critical-count">{criticalCount} Critical</span>
                    <span className="faulted-count">{faultedCount} Faulted</span>
                    <span className="warning-count">{warningCount} Warning</span>
                    <span className="degrading-count">
                        {degradingCount} Degrading
                    </span>
                    <span className="healthy-count">{healthyCount} Healthy</span>
                </div>
            </section>

            <section className="machine-grid">
                {machines.map((machine) => (
                    <button
                        className={`machine-card ${getOperationalStatus(
                            machine
                        ).toLowerCase()}`}
                        key={machine.machine_id}
                        onClick={() => navigate(`/machines/${machine.machine_id}`)}
                        type="button"
                    >
                        <div className="machine-card-top">
                            <span>{machine.machine_id}</span>
                            <strong>{machine.health_score}</strong>
                        </div>

                        <h3>{machine.machine_name}</h3>

                        <p>{getOperationalStatus(machine)}</p>

                        <small>
                            {machine.risk_reasons[0] ?? "No active risk indicators"}
                        </small>
                    </button>
                ))}
            </section>
        </main>
    );
}

export default FleetDashboard;