import { useEffect, useMemo, useState } from "react";
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

type FactorySettings = {
    company_name: string;
    plant_name: string;
    location: string;
    contact_person: string;
    contact_detail: string;
};

type MachineDepartment = "ALL" | "PRODUCTION" | "UTILITIES";

type MachineCategory =
    | "ALL"
    | "MOTORS"
    | "PUMPS"
    | "GEARBOXES"
    | "FANS"
    | "CONVEYORS"
    | "COMPRESSORS";

function getMachineCategory(machineId: string): Exclude<MachineCategory, "ALL"> {
    const prefix = machineId.toUpperCase().split("-")[0];

    switch (prefix) {
        case "MTR":
            return "MOTORS";
        case "PMP":
            return "PUMPS";
        case "GBX":
            return "GEARBOXES";
        case "FAN":
            return "FANS";
        case "CNV":
            return "CONVEYORS";
        case "CMP":
            return "COMPRESSORS";
        default:
            return "MOTORS";
    }
}

const DEPARTMENT_LABELS: Record<MachineDepartment, string> = {
    ALL: "All Departments",
    PRODUCTION: "Production",
    UTILITIES: "Utilities",
};

function getMachineDepartment(machineId: string): Exclude<MachineDepartment, "ALL"> {
    const prefix = machineId.toUpperCase().split("-")[0];

    // Current simulator telemetry does not expose a department field,
    // so the demo fleet uses an equipment-based department mapping.
    switch (prefix) {
        case "PMP":
        case "FAN":
        case "CMP":
            return "UTILITIES";
        case "MTR":
        case "GBX":
        case "CNV":
        default:
            return "PRODUCTION";
    }
}

const CATEGORY_LABELS: Record<MachineCategory, string> = {
    ALL: "All Assets",
    MOTORS: "Motors",
    PUMPS: "Pumps",
    GEARBOXES: "Gearboxes",
    FANS: "Fans",
    CONVEYORS: "Conveyors",
    COMPRESSORS: "Compressors",
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
    const [factorySettings, setFactorySettings] = useState<FactorySettings | null>(null);
    const [selectedCategory, setSelectedCategory] = useState<MachineCategory>("ALL");
    const [selectedDepartment, setSelectedDepartment] = useState<MachineDepartment>("ALL");
    const [error, setError] = useState("");
    const API_BASE = import.meta.env.VITE_API_URL || "http://127.0.0.1:5000";

    useEffect(() => {
        const loadFactorySettings = async () => {
            try {
                const response = await fetch(`${API_BASE}/api/settings`);

                if (!response.ok) {
                    throw new Error("Factory settings are not available");
                }

                const data: FactorySettings = await response.json();
                setFactorySettings(data);
            } catch (err) {
                console.error("Could not load factory settings:", err);
            }
        };

        loadFactorySettings();
    }, []);

    useEffect(() => {
        const loadTelemetry = async () => {
            try {
                const response = await fetch(`${API_BASE}/api/telemetry`);

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

    const filteredMachines = useMemo(() => {
        return machines.filter((machine) => {
            const categoryMatches =
                selectedCategory === "ALL" ||
                getMachineCategory(machine.machine_id) === selectedCategory;

            const departmentMatches =
                selectedDepartment === "ALL" ||
                getMachineDepartment(machine.machine_id) === selectedDepartment;

            return categoryMatches && departmentMatches;
        });
    }, [machines, selectedCategory, selectedDepartment]);

    // Filter counts are intentionally dependent on the other filter.
    // This keeps the UI truthful: selecting Motors, for example, makes
    // the Department row show only the departments that contain Motors.
    const departmentCounts = useMemo(() => {
        const counts: Record<MachineDepartment, number> = {
            ALL: 0,
            PRODUCTION: 0,
            UTILITIES: 0,
        };

        machines.forEach((machine) => {
            const categoryMatches =
                selectedCategory === "ALL" ||
                getMachineCategory(machine.machine_id) === selectedCategory;

            if (!categoryMatches) return;

            const department = getMachineDepartment(machine.machine_id);
            counts.ALL += 1;
            counts[department] += 1;
        });

        return counts;
    }, [machines, selectedCategory]);

    const categoryCounts = useMemo(() => {
        const counts: Record<MachineCategory, number> = {
            ALL: 0,
            MOTORS: 0,
            PUMPS: 0,
            GEARBOXES: 0,
            FANS: 0,
            CONVEYORS: 0,
            COMPRESSORS: 0,
        };

        machines.forEach((machine) => {
            const departmentMatches =
                selectedDepartment === "ALL" ||
                getMachineDepartment(machine.machine_id) === selectedDepartment;

            if (!departmentMatches) return;

            const category = getMachineCategory(machine.machine_id);
            counts.ALL += 1;
            counts[category] += 1;
        });

        return counts;
    }, [machines, selectedDepartment]);

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
        <>
            <style>{`
                .fleet-dashboard-category-button:hover {
                    border-color: #35dfff !important;
                    color: #ecfcff !important;
                    background: #103650 !important;
                    transform: translateY(-1px);
                }
                .fleet-overview {
                    min-width: 0;
                }
                .fleet-counts {
                    min-width: 0;
                }
                @media (max-width: 860px) {
                    .fleet-dashboard-header {
                        grid-template-columns: 1fr !important;
                    }
                    .fleet-overview {
                        align-items: flex-start !important;
                    }
                    .fleet-counts {
                        justify-content: flex-start !important;
                    }
                }
            `}</style>
            <main>
                <header
                    className="fleet-dashboard-header"
                    style={{
                        display: "grid",
                        gridTemplateColumns: "minmax(0, 1.25fr) minmax(320px, 0.75fr)",
                        alignItems: "center",
                        gap: "28px",
                        marginBottom: "28px",
                        padding: "4px 0 24px",
                        borderBottom: "1px solid #1d3b57",
                        fontFamily: "Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, \"Segoe UI\", sans-serif",
                    }}
                >
                    <div style={{ minWidth: 0, display: "flex", alignItems: "center" }}>
                        <img
                            src="/logo.png"
                            alt="ProDiag AI"
                            style={{
                                display: "block",
                                width: "min(530px, 100%)",
                                maxHeight: "150px",
                                objectFit: "contain",
                                objectPosition: "left center",
                            }}
                        />
                    </div>

                    {factorySettings && (
                        <div
                            style={{
                                minWidth: 0,
                                padding: "18px 20px",
                                border: "1px solid #214866",
                                borderRadius: "18px",
                                background: "linear-gradient(145deg, rgba(12,35,57,.94), rgba(7,24,41,.9))",
                                boxShadow: "0 16px 38px rgba(0,0,0,.15)",
                            }}
                        >
                            <div
                                style={{
                                    display: "flex",
                                    alignItems: "center",
                                    justifyContent: "space-between",
                                    gap: "12px",
                                    marginBottom: "14px",
                                }}
                            >
                                <span
                                    style={{
                                        color: "#45dfff",
                                        fontSize: "0.68rem",
                                        fontWeight: 800,
                                        letterSpacing: "0.16em",
                                        textTransform: "uppercase",
                                    }}
                                >
                                    Plant Identity
                                </span>
                                <span
                                    style={{
                                        display: "inline-flex",
                                        alignItems: "center",
                                        gap: "7px",
                                        padding: "5px 9px",
                                        border: "1px solid #1c6650",
                                        borderRadius: "999px",
                                        color: "#78efc2",
                                        background: "#0b382d",
                                        fontSize: "0.65rem",
                                        fontWeight: 800,
                                        letterSpacing: "0.08em",
                                        textTransform: "uppercase",
                                    }}
                                >
                                    <span style={{ width: 6, height: 6, borderRadius: "50%", background: "#35e29c", boxShadow: "0 0 0 3px #35e29c20" }} />
                                    Online
                                </span>
                            </div>

                            <div style={{ minWidth: 0 }}>
                                <div
                                    style={{
                                        color: "#f4f9ff",
                                        fontSize: "1.15rem",
                                        lineHeight: 1.25,
                                        fontWeight: 800,
                                        letterSpacing: "-0.025em",
                                        overflowWrap: "anywhere",
                                    }}
                                >
                                    {factorySettings.company_name}
                                </div>
                                <div
                                    style={{
                                        marginTop: "5px",
                                        color: "#9fc1df",
                                        fontSize: "0.9rem",
                                        fontWeight: 600,
                                    }}
                                >
                                    {factorySettings.plant_name}
                                </div>
                                <div
                                    style={{
                                        marginTop: "4px",
                                        color: "#6f9bc2",
                                        fontSize: "0.78rem",
                                        fontWeight: 500,
                                    }}
                                >
                                    {factorySettings.location}
                                </div>
                            </div>
                        </div>
                    )}
                </header>

                <section
                    className="fleet-overview"
                    style={{
                        overflow: "hidden",
                        fontFamily: "Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, \"Segoe UI\", sans-serif",
                    }}
                >
                    <div style={{ minWidth: 0 }}>
                        <p className="eyebrow">Fleet overview</p>
                        <h2 style={{ fontSize: "clamp(1.35rem, 2.5vw, 1.75rem)", fontWeight: 800, letterSpacing: "-0.025em" }}>
                            {machines.length} connected machines
                        </h2>
                    </div>

                    <div className="fleet-counts" style={{ minWidth: 0, justifyContent: "flex-end" }}>
                        <span className="critical-count">{criticalCount} Critical</span>
                        <span className="faulted-count">{faultedCount} Faulted</span>
                        <span className="warning-count">{warningCount} Warning</span>
                        <span className="degrading-count">
                            {degradingCount} Degrading
                        </span>
                        <span className="healthy-count">{healthyCount} Healthy</span>
                    </div>
                </section>

                <section
                    style={{
                        marginTop: "24px",
                        padding: "20px",
                        border: "1px solid #1d3b57",
                        borderRadius: "16px",
                        background: "rgba(8, 27, 45, 0.72)",
                    }}
                >
                    <div
                        style={{
                            display: "flex",
                            flexWrap: "wrap",
                            alignItems: "center",
                            justifyContent: "space-between",
                            gap: "12px",
                            marginBottom: "14px",
                        }}
                    >
                        <div>
                            <p className="eyebrow" style={{ marginBottom: "4px" }}>
                                Asset categories
                            </p>
                            <span style={{ color: "#7895b0", fontSize: "0.82rem" }}>
                                Filter the live fleet by equipment type
                            </span>
                        </div>

                        <span style={{ color: "#7ee7c7", fontSize: "0.8rem", fontWeight: 700 }}>
                            {filteredMachines.length} shown
                        </span>
                    </div>

                    <div
                        style={{
                            display: "flex",
                            flexWrap: "wrap",
                            gap: "8px",
                        }}
                    >
                        {(Object.keys(CATEGORY_LABELS) as MachineCategory[]).map((category) => {
                            const active = selectedCategory === category;

                            return (
                                <button
                                    key={category}
                                    type="button"
                                    className="fleet-dashboard-category-button"
                                    onClick={() => setSelectedCategory(category)}
                                    style={{
                                        border: `1px solid ${active ? "#32d9ff" : "#244763"}`,
                                        background: active ? "#103a55" : "#091e31",
                                        color: active ? "#e8fbff" : "#91abc3",
                                        borderRadius: "999px",
                                        padding: "8px 13px",
                                        fontSize: "0.78rem",
                                        fontWeight: 700,
                                        cursor: "pointer",
                                        transition: "all 0.2s ease",
                                    }}
                                >
                                    {CATEGORY_LABELS[category]}
                                    <span style={{ marginLeft: "7px", opacity: 0.72 }}>
                                        {categoryCounts[category]}
                                    </span>
                                </button>
                            );
                        })}
                    </div>

                    <div
                        style={{
                            marginTop: "18px",
                            paddingTop: "16px",
                            borderTop: "1px solid rgba(29, 59, 87, 0.75)",
                        }}
                    >
                        <div
                            style={{
                                display: "flex",
                                flexWrap: "wrap",
                                alignItems: "center",
                                justifyContent: "space-between",
                                gap: "10px",
                                marginBottom: "10px",
                            }}
                        >
                            <div>
                                <div
                                    style={{
                                        color: "#45dfff",
                                        fontSize: "0.66rem",
                                        fontWeight: 800,
                                        letterSpacing: "0.15em",
                                        textTransform: "uppercase",
                                    }}
                                >
                                    Departments
                                </div>
                                <span style={{ color: "#7895b0", fontSize: "0.78rem" }}>
                                    Filter by operational area
                                </span>
                            </div>
                        </div>

                        <div
                            style={{
                                display: "flex",
                                flexWrap: "wrap",
                                gap: "8px",
                            }}
                        >
                            {(Object.keys(DEPARTMENT_LABELS) as MachineDepartment[]).map((department) => {
                                const active = selectedDepartment === department;

                                return (
                                    <button
                                        key={department}
                                        type="button"
                                        className="fleet-dashboard-category-button"
                                        onClick={() => setSelectedDepartment(department)}
                                        style={{
                                            border: `1px solid ${active ? "#35dfff" : "#244763"}`,
                                            background: active ? "#103a55" : "#091e31",
                                            color: active ? "#e8fbff" : "#91abc3",
                                            borderRadius: "999px",
                                            padding: "7px 12px",
                                            fontSize: "0.76rem",
                                            fontWeight: 700,
                                            cursor: "pointer",
                                            transition: "all 0.2s ease",
                                        }}
                                    >
                                        {DEPARTMENT_LABELS[department]}
                                        <span style={{ marginLeft: "7px", opacity: 0.72 }}>
                                            {departmentCounts[department]}
                                        </span>
                                    </button>
                                );
                            })}
                        </div>
                    </div>
                </section>

                <section
                    className="machine-grid"
                    style={{
                        marginTop: "28px",
                    }}
                >
                    {filteredMachines.map((machine) => (
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

                {filteredMachines.length === 0 && (
                    <section
                        style={{
                            marginTop: "20px",
                            padding: "42px 24px",
                            textAlign: "center",
                            border: "1px solid #1d3b57",
                            borderRadius: "16px",
                            color: "#7895b0",
                        }}
                    >
                        No machines match the selected asset category and department filters.
                    </section>
                )}
            </main>
        </>
    );
}

export default FleetDashboard;