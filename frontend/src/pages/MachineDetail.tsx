import { useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import jsPDF from "jspdf";
import {
    CartesianGrid,
    Line,
    LineChart,
    ResponsiveContainer,
    Tooltip,
    XAxis,
    YAxis,
} from "recharts";

type MachineData = {
    machine_id: string;
    machine_name: string;
    timestamp: string;
    temperature_c: number;
    vibration_mm_s: number;
    current_a: number;
    rpm: number;
    status: string;
    health_score: number;
    health_status:
    | "HEALTHY"
    | "DEGRADING"
    | "WARNING"
    | "CRITICAL"
    | "FAULTED"
    | "REPAIRING"
    | "RESTART";
    risk_reasons: string[];
    condition?: string;
    fault_type?: string;
    ml_health_score?: number;
    ml_failure_probability?: number;
    ml_failure_within_1h?: boolean;
    ml_prediction_status?:
    | "HIGH_RISK"
    | "NORMAL"
    | "ALREADY_FAULTED"
    | "UNDER_MAINTENANCE"
    | "RESTARTING";
};

type TelemetryResponse = {
    count: number;
    machines: MachineData[];
};

type HistoryReading = {
    timestamp: string;
    temperature_c: number;
    vibration_mm_s: number;
    current_a: number;
    rpm: number;
    status: string;
    health_score: number;
    health_status: string;
    ml_health_score?: number;
    ml_failure_probability?: number;
    ml_failure_within_1h?: boolean;
};

type HistoryResponse = {
    machine_id: string;
    count: number;
    readings: HistoryReading[];
};

type AIDiagnosis = {
    diagnosis: string;
    probable_fault: string;
    confidence: number;
    evidence: string[];
    recommended_actions: string[];
    urgency: "LOW" | "MEDIUM" | "HIGH" | "CRITICAL";
    requires_escalation: boolean;
};

type AIDiagnosisResponse = {
    machine_id: string;
    machine_name: string;
    telemetry: MachineData;
    anomaly: {
        is_anomaly: boolean;
        anomaly_score: number;
        status: string;
        reasons: string[];
    };
    ai_diagnosis: AIDiagnosis;
};

function MachineDetail() {

    const { machineId } = useParams();
    const navigate = useNavigate();

    const [machine, setMachine] = useState<MachineData | null>(null);
    const mlHealthScoreColor =
        machine?.ml_health_score === undefined
            ? "#ffffff"
            : machine.ml_health_score >= 80
                ? "#7ee2a8"
                : machine.ml_health_score >= 60
                    ? "#f6c85f"
                    : machine.ml_health_score >= 40
                        ? "#ff9f43"
                        : "#ff6b6b";
    const [history, setHistory] = useState<HistoryReading[]>([]);

    const [aiDiagnosis, setAiDiagnosis] = useState<AIDiagnosis | null>(null);
    const [aiModalOpen, setAiModalOpen] = useState(false);
    const [aiLoading, setAiLoading] = useState(false);
    const [aiError, setAiError] = useState("");

    const [copilotQuestion, setCopilotQuestion] = useState("");
    const [copilotMessages, setCopilotMessages] = useState<
        {
            role: "user" | "assistant";
            content: string;
        }[]
    >([]);
    const [copilotLoading, setCopilotLoading] = useState(false);
    const [copilotError, setCopilotError] = useState("");

    const [error, setError] = useState("");

    const [workOrderLoading, setWorkOrderLoading] = useState(false);
    const [workOrderMessage, setWorkOrderMessage] = useState("");
    const [workOrderError, setWorkOrderError] = useState("");

    useEffect(() => {
        if (!machineId) return;

        const loadMachine = async () => {
            try {
                const response = await fetch(
                    "http://127.0.0.1:5000/api/telemetry"
                );

                if (!response.ok) {
                    throw new Error("Telemetry API is not available");
                }

                const data: TelemetryResponse = await response.json();

                const currentMachine = data.machines.find(
                    (item) => item.machine_id === machineId
                );

                if (!currentMachine) {
                    throw new Error(`Machine ${machineId} was not found`);
                }

                setMachine(currentMachine);
                setError("");
            } catch (err) {
                setError(
                    err instanceof Error ? err.message : "Unknown error"
                );
            }
        };

        loadMachine();

        const intervalId = setInterval(loadMachine, 1000);

        return () => clearInterval(intervalId);
    }, [machineId]);

    useEffect(() => {
        if (!machineId) return;

        const loadHistory = async () => {
            try {
                const response = await fetch(
                    `http://127.0.0.1:5000/api/machines/${machineId}/history?limit=40`
                );

                if (!response.ok) {
                    throw new Error("Machine history is not available");
                }

                const data: HistoryResponse = await response.json();

                setHistory(data.readings);
            } catch (err) {
                console.error(err);
            }
        };

        loadHistory();

        const intervalId = setInterval(loadHistory, 5000);

        return () => clearInterval(intervalId);
    }, [machineId]);

    const runAIDiagnosis = async () => {
        if (!machineId) return;

        setAiLoading(true);
        setAiError("");

        try {
            const response = await fetch(
                `http://127.0.0.1:5000/api/machines/${machineId}/ai-diagnosis`
            );

            if (!response.ok) {
                throw new Error("AI diagnosis is not available");
            }

            const data: AIDiagnosisResponse = await response.json();

            setAiDiagnosis(data.ai_diagnosis);
            setAiModalOpen(true);
        } catch (err) {
            setAiError(
                err instanceof Error ? err.message : "AI diagnosis failed"
            );
        } finally {
            setAiLoading(false);
        }
    };

    const askEngineerCopilot = async () => {
        if (!machineId || !copilotQuestion.trim()) return;

        const question = copilotQuestion.trim();

        setCopilotLoading(true);
        setCopilotError("");

        const userMessage = {
            role: "user" as const,
            content: question,
        };

        const updatedMessages = [
            ...copilotMessages,
            userMessage,
        ];

        setCopilotMessages(updatedMessages);
        setCopilotQuestion("");

        try {
            const response = await fetch(
                `http://127.0.0.1:5000/api/machines/${machineId}/ai-diagnosis/chat`,
                {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json",
                    },
                    body: JSON.stringify({
                        question,
                        conversation_history: copilotMessages,
                    }),
                }
            );

            if (!response.ok) {
                const errorData = await response.json().catch(() => null);

                throw new Error(
                    errorData?.error ||
                    "AI Maintenance Copilot is unavailable"
                );
            }

            const data = await response.json();

            const assistantResponse = data.response;

            const assistantText =
                assistantResponse?.summary ||
                assistantResponse?.diagnosis ||
                "The Copilot did not return a response.";

            setCopilotMessages([
                ...updatedMessages,
                {
                    role: "assistant",
                    content: assistantText,
                },
            ]);
        } catch (err) {
            setCopilotMessages(copilotMessages);

            setCopilotError(
                err instanceof Error
                    ? err.message
                    : "Engineer Copilot request failed"
            );
        } finally {
            setCopilotLoading(false);
        }
    };

    const createWorkOrder = async () => {
        if (!machine || !aiDiagnosis) return;

        setWorkOrderLoading(true);
        setWorkOrderMessage("");
        setWorkOrderError("");

        try {
            const response = await fetch(
                "http://127.0.0.1:5000/api/work-orders",
                {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json",
                    },
                    body: JSON.stringify({
                        machine_id: machine.machine_id,
                        machine_name: machine.machine_name,
                        title: `Maintenance Required — ${machine.fault_type
                            ? machine.fault_type.replace(/_/g, " ")
                            : "Machine Condition"
                            }`,
                        description: `Maintenance action required for ${machine.machine_name} based on the current machine condition and AI assessment.`,
                        priority:
                            aiDiagnosis.urgency === "CRITICAL"
                                ? "CRITICAL"
                                : aiDiagnosis.urgency === "HIGH"
                                    ? "HIGH"
                                    : "MEDIUM",
                        fault_type: machine.fault_type ?? null,
                        ai_diagnosis: aiDiagnosis.diagnosis,
                        ai_recommendation:
                            aiDiagnosis.recommended_actions.join("\n"),
                    }),
                }
            );

            if (!response.ok) {
                throw new Error("Could not create work order");
            }

            const data = await response.json();

            setWorkOrderMessage(
                `Work Order #${data.work_order_id} created successfully.`
            );
        } catch (err) {
            setWorkOrderError(
                err instanceof Error
                    ? err.message
                    : "Work order creation failed"
            );
        } finally {
            setWorkOrderLoading(false);
        }
    };

    // =========================================================
    // DOWNLOAD AI DIAGNOSTIC REPORT AS PDF
    // =========================================================
    const downloadPDFReport = () => {
        if (!machine || !aiDiagnosis) return;

        const doc = new jsPDF();

        const pageWidth = doc.internal.pageSize.getWidth();
        const pageHeight = doc.internal.pageSize.getHeight();

        const margin = 18;
        const contentWidth = pageWidth - margin * 2;

        let y = 20;

        const checkPage = (requiredHeight: number = 10) => {
            if (y + requiredHeight > pageHeight - 20) {
                doc.addPage();
                y = 20;
            }
        };

        const addWrappedText = (
            text: string,
            fontSize: number = 10,
            lineHeight: number = 6
        ) => {
            doc.setFontSize(fontSize);

            const lines = doc.splitTextToSize(
                text,
                contentWidth
            );

            lines.forEach((line: string) => {
                checkPage(lineHeight);
                doc.text(line, margin, y);
                y += lineHeight;
            });
        };

        const addSectionTitle = (title: string) => {
            checkPage(18);

            y += 5;

            doc.setFont("helvetica", "bold");
            doc.setFontSize(12);
            doc.text(title.toUpperCase(), margin, y);

            y += 8;

            doc.setFont("helvetica", "normal");
        };

        const addBulletList = (items: string[]) => {
            items.forEach((item) => {
                const lines = doc.splitTextToSize(
                    `- ${item}`,
                    contentWidth - 8
                );

                lines.forEach((line: string) => {
                    checkPage(6);

                    doc.setFont("helvetica", "normal");
                    doc.setFontSize(10);
                    doc.text(line, margin + 4, y);

                    y += 6;
                });

                y += 1;
            });
        };

        // ---------------------------------------------------------
        // REPORT HEADER
        // ---------------------------------------------------------

        doc.setFont("helvetica", "bold");
        doc.setFontSize(22);
        doc.text("ProDiag AI V2", margin, y);

        y += 8;

        doc.setFont("helvetica", "normal");
        doc.setFontSize(10);
        doc.text(
            "AI-Powered Industrial Predictive Maintenance Report",
            margin,
            y
        );

        y += 10;

        doc.setDrawColor(40, 82, 115);
        doc.line(
            margin,
            y,
            pageWidth - margin,
            y
        );

        y += 12;

        // ---------------------------------------------------------
        // MACHINE INFORMATION
        // ---------------------------------------------------------

        doc.setFont("helvetica", "bold");
        doc.setFontSize(16);
        doc.text(
            machine.machine_name,
            margin,
            y
        );

        y += 7;

        doc.setFont("helvetica", "normal");
        doc.setFontSize(10);

        doc.text(
            `Machine ID: ${machine.machine_id}`,
            margin,
            y
        );

        y += 6;

        doc.text(
            `Report generated: ${new Date().toLocaleString()}`,
            margin,
            y
        );

        y += 10;

        // ---------------------------------------------------------
        // MACHINE HEALTH
        // ---------------------------------------------------------

        addSectionTitle("Machine Health");

        doc.setFont("helvetica", "bold");
        doc.setFontSize(11);

        doc.text(
            `Health Score: ${machine.health_score} / 100`,
            margin,
            y
        );

        y += 7;

        doc.setFont("helvetica", "normal");
        doc.setFontSize(10);

        doc.text(
            `Health Status: ${machine.health_status}`,
            margin,
            y
        );

        y += 6;

        doc.text(
            `Machine Status: ${machine.status}`,
            margin,
            y
        );

        y += 6;

        if (machine.condition) {
            doc.text(
                `Condition: ${machine.condition}`,
                margin,
                y
            );

            y += 6;
        }

        if (machine.fault_type) {
            doc.text(
                `Fault Type: ${machine.fault_type.replace(
                    /_/g,
                    " "
                )}`,
                margin,
                y
            );

            y += 6;
        }

        // ---------------------------------------------------------
        // CURRENT SENSOR READINGS
        // ---------------------------------------------------------

        addSectionTitle("Current Sensor Readings");

        const sensorReadings = [
            `Temperature: ${machine.temperature_c} C`,
            `Vibration: ${machine.vibration_mm_s} mm/s`,
            `Current: ${machine.current_a} A`,
            `Rotational Speed: ${machine.rpm} RPM`,
        ];

        sensorReadings.forEach((reading) => {
            checkPage(7);

            doc.setFont("helvetica", "normal");
            doc.setFontSize(10);

            doc.text(
                reading,
                margin,
                y
            );

            y += 6;
        });

        // ---------------------------------------------------------
        // AI DIAGNOSIS
        // ---------------------------------------------------------

        addSectionTitle("AI Diagnostic Assessment");

        doc.setFont("helvetica", "bold");
        doc.setFontSize(11);

        addWrappedText(
            `Probable Fault: ${aiDiagnosis.probable_fault}`,
            11,
            6
        );

        doc.setFont("helvetica", "normal");

        addWrappedText(
            `Urgency: ${aiDiagnosis.urgency}`,
            10,
            6
        );

        addWrappedText(
            `Diagnostic Confidence: ${aiDiagnosis.confidence}%`,
            10,
            6
        );

        y += 3;

        addWrappedText(
            aiDiagnosis.diagnosis,
            10,
            6
        );

        // ---------------------------------------------------------
        // EVIDENCE
        // ---------------------------------------------------------

        addSectionTitle("Evidence");

        addBulletList(
            aiDiagnosis.evidence
        );

        // ---------------------------------------------------------
        // RECOMMENDED ACTIONS
        // ---------------------------------------------------------

        addSectionTitle("Recommended Actions");

        addBulletList(
            aiDiagnosis.recommended_actions
        );

        // ---------------------------------------------------------
        // ESCALATION
        // ---------------------------------------------------------

        addSectionTitle("Escalation");

        addWrappedText(
            aiDiagnosis.requires_escalation
                ? "Escalation recommended: involve a maintenance specialist or OEM."
                : "No escalation is currently recommended based on the AI assessment.",
            10,
            6
        );

        // ---------------------------------------------------------
        // FOOTER
        // ---------------------------------------------------------

        checkPage(25);

        y += 8;

        doc.setDrawColor(40, 82, 115);

        doc.line(
            margin,
            y,
            pageWidth - margin,
            y
        );

        y += 7;

        doc.setFont("helvetica", "normal");
        doc.setFontSize(8);

        doc.text(
            "ProDiag AI V2 - Predict before failure. Act before downtime.",
            margin,
            y
        );

        y += 5;

        doc.text(
            "AI-generated maintenance assessment. Verify critical decisions with qualified personnel.",
            margin,
            y
        );

        // ---------------------------------------------------------
        // SAVE PDF
        // ---------------------------------------------------------

        const safeMachineId =
            machine.machine_id.replace(
                /[^a-zA-Z0-9-_]/g,
                "_"
            );

        doc.save(
            `ProDiag_AI_Report_${safeMachineId}.pdf`
        );
    };

    const chartData = history.map((reading) => ({
        time: new Date(reading.timestamp).toLocaleTimeString([], {
            minute: "2-digit",
            second: "2-digit",
        }),
        health_score: reading.health_score,
    }));

    if (error) {
        return (
            <main>
                <p>Connection error: {error}</p>

                <button
                    type="button"
                    onClick={() => navigate("/")}
                >
                    Back to Fleet
                </button>
            </main>
        );
    }

    if (!machine) {
        return (
            <main>
                <p>Loading machine data...</p>
            </main>
        );
    }

    return (
        <main>
            <style>{`
                .ai-copilot-layout {
                    grid-template-columns: minmax(0, 1.1fr) minmax(0, 0.9fr);
                }

                .ai-copilot-chat-history {
                    scrollbar-width: thin;
                }

                @media (max-width: 900px) {
                    .ai-copilot-layout {
                        grid-template-columns: 1fr !important;
                    }

                    .ai-copilot-chat-column,
                    .ai-diagnosis-column {
                        min-height: auto !important;
                    }

                    .ai-copilot-chat-column {
                        min-height: 420px !important;
                    }
                }
            `}</style>

            <header
                className="machine-detail-header"
                style={{
                    display: "flex",
                    alignItems: "center",
                    justifyContent: "space-between",
                    gap: "24px",
                    marginBottom: "0",
                    paddingBottom: "18px",
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
                        Machine detail
                    </p>

                    <h1>
                        {machine.machine_name}
                    </h1>

                    <p>
                        Machine ID: {machine.machine_id}
                    </p>
                </div>

                <div
                    className={`health-badge ${machine.health_status.toLowerCase()}`}
                >
                    <span>
                        Health score
                    </span>

                    <strong>
                        {machine.health_score}
                    </strong>

                    <small>
                        / 100 · {machine.health_status}
                    </small>
                </div>

                <button
                    type="button"
                    onClick={() =>
                        navigate("/work-orders")
                    }
                    style={{
                        padding: "10px 16px",
                        borderRadius: "8px",
                        border: "1px solid #285273",
                        background: "transparent",
                        color: "#9ab3d0",
                        fontWeight: 600,
                        cursor: "pointer",
                    }}
                >
                    Work Orders →
                </button>
            </header>

            <section className="dashboard-grid machine-detail-grid">
                <article className="panel">
                    <p className="eyebrow">
                        Live sensor readings
                    </p>

                    <h2>
                        Operating condition
                    </h2>

                    <div className="metric-grid">
                        <div className="metric">
                            <span>
                                Temperature
                            </span>

                            <strong>
                                {machine.temperature_c} °C
                            </strong>
                        </div>

                        <div className="metric">
                            <span>
                                Vibration
                            </span>

                            <strong>
                                {machine.vibration_mm_s} mm/s
                            </strong>
                        </div>

                        <div className="metric">
                            <span>
                                Current
                            </span>

                            <strong>
                                {machine.current_a} A
                            </strong>
                        </div>

                        <div className="metric">
                            <span>
                                Speed
                            </span>

                            <strong>
                                {machine.rpm} RPM
                            </strong>
                        </div>
                    </div>

                    <p className="live-status">
                        <span className="live-dot" />

                        {machine.status} · Updated{" "}
                        {new Date(
                            machine.timestamp
                        ).toLocaleTimeString()}
                    </p>
                </article>

                <article className="panel predictive-panel">
                    <p className="eyebrow">
                        Predictive intelligence
                    </p>

                    <h2>
                        ML Risk Assessment
                    </h2>

                    <div className="metric-grid">
                        <div className="metric">
                            <span>
                                ML Health Score
                            </span>

                            <strong style={{ color: mlHealthScoreColor }}>
                                {machine.ml_health_score?.toFixed(2) ?? "—"}
                            </strong>

                            <small>
                                / 100
                            </small>
                        </div>

                        <div className="metric">
                            <span>
                                Failure Probability
                            </span>

                            <strong
                                style={{
                                    color:
                                        machine.health_status === "FAULTED"
                                            ? "#ff6b6b"
                                            : "#ffffff",
                                }}
                            >
                                {machine.ml_failure_probability !== undefined
                                    ? `${(
                                        machine.ml_failure_probability * 100
                                    ).toFixed(2)}%`
                                    : "—"}
                            </strong>
                        </div>
                    </div>

                    <div
                        style={{
                            marginTop: "20px",
                            padding: "14px 16px",
                            borderRadius: "10px",
                            border: "1px solid #285273",
                            background: "#10263b",
                        }}
                    >
                        <span
                            style={{
                                display: "block",
                                fontSize: "12px",
                                color: "#9ab3d0",
                                marginBottom: "6px",
                            }}
                        >
                            Prediction Status
                        </span>

                        <strong
                            style={{
                                fontSize: "16px",
                                color:
                                    machine.ml_prediction_status === "ALREADY_FAULTED"
                                        ? "#ff6b6b"
                                        : machine.ml_prediction_status === "UNDER_MAINTENANCE"
                                            ? "#f6c85f"
                                            : machine.ml_prediction_status === "RESTARTING"
                                                ? "#7ab8ff"
                                                : machine.ml_failure_within_1h
                                                    ? "#ff6b6b"
                                                    : "#7ee2a8",
                            }}
                        >
                            {machine.ml_prediction_status === "ALREADY_FAULTED"
                                ? "● MACHINE ALREADY FAULTED"
                                : machine.ml_prediction_status === "UNDER_MAINTENANCE"
                                    ? "● UNDER MAINTENANCE"
                                    : machine.ml_prediction_status === "RESTARTING"
                                        ? "● MACHINE RESTARTING"
                                        : machine.ml_failure_within_1h
                                            ? "⚠ HIGH FAILURE RISK"
                                            : "✓ NO FAILURE PREDICTED"}
                        </strong>
                    </div>

                    <p
                        style={{
                            marginTop: "14px",
                            fontSize: "12px",
                            color: "#7189a5",
                        }}
                    >
                        Prediction model: XGBoost · 10-second inference interval
                    </p>
                </article>

                <article
                    className="panel diagnosis-panel"
                    style={{
                        gridColumn: "1 / -1",
                    }}
                >
                    <p className="eyebrow">
                        AI maintenance copilot
                    </p>

                    <h2>
                        {aiDiagnosis
                            ? aiDiagnosis.probable_fault
                            : "AI maintenance intelligence"}
                    </h2>

                    <div
                        className="ai-copilot-layout"
                        style={{
                            display: "grid",
                            gridTemplateColumns:
                                "minmax(0, 1.1fr) minmax(0, 0.9fr)",
                            gap: "20px",
                            marginTop: "20px",
                            alignItems: "stretch",
                        }}
                    >
                        {/* =================================================
                            ENGINEER CHAT
                           ================================================= */}
                        <section
                            className="ai-copilot-column ai-copilot-chat-column"
                            style={{
                                display: "flex",
                                flexDirection: "column",
                                minWidth: 0,
                                minHeight: "460px",
                                padding: "20px",
                                borderRadius: "12px",
                                border: "1px solid #285273",
                                background: "#0b182a",
                            }}
                        >
                            <p className="eyebrow">
                                Engineer Chat
                            </p>

                            <h3
                                style={{
                                    marginBottom: "8px",
                                }}
                            >
                                Ask the Maintenance Copilot
                            </h3>

                            <p
                                style={{
                                    marginBottom: "16px",
                                    fontSize: "13px",
                                    color: "#7189a5",
                                }}
                            >
                                Ask questions about this machine,
                                its condition, possible faults,
                                inspection steps, or maintenance actions.
                            </p>

                            <div
                                className="copilot-chat-history"
                                style={{
                                    flex: 1,
                                    minHeight:
                                        copilotMessages.length > 0
                                            ? "180px"
                                            : "120px",
                                    maxHeight: "300px",
                                    overflowY: "auto",
                                    padding: "4px 8px 4px 4px",
                                    marginBottom: "16px",
                                    scrollbarGutter: "stable",
                                }}
                            >
                                {copilotMessages.length === 0 ? (
                                    <div
                                        style={{
                                            height: "100%",
                                            minHeight: "120px",
                                            display: "flex",
                                            alignItems: "center",
                                            justifyContent: "center",
                                            textAlign: "center",
                                            padding: "20px",
                                            borderRadius: "10px",
                                            border: "1px dashed #285273",
                                            color: "#7189a5",
                                            fontSize: "13px",
                                        }}
                                    >
                                        Start a conversation about the
                                        current machine condition.
                                    </div>
                                ) : (
                                    <div
                                        style={{
                                            display: "flex",
                                            flexDirection: "column",
                                            gap: "12px",
                                        }}
                                    >
                                        {copilotMessages.map(
                                            (message, index) => (
                                                <div
                                                    key={`${message.role}-${index}`}
                                                    style={{
                                                        alignSelf:
                                                            message.role ===
                                                                "user"
                                                                ? "flex-end"
                                                                : "flex-start",
                                                        width: "fit-content",
                                                        maxWidth: "88%",
                                                        padding: "12px 14px",
                                                        borderRadius: "10px",
                                                        border:
                                                            message.role ===
                                                                "user"
                                                                ? "1px solid #285273"
                                                                : "1px solid #1d3b57",
                                                        background:
                                                            message.role ===
                                                                "user"
                                                                ? "#10263b"
                                                                : "#071421",
                                                    }}
                                                >
                                                    <span
                                                        style={{
                                                            display: "block",
                                                            fontSize: "11px",
                                                            color: "#7189a5",
                                                            marginBottom: "5px",
                                                            fontWeight: 600,
                                                            textTransform:
                                                                "uppercase",
                                                        }}
                                                    >
                                                        {message.role ===
                                                            "user"
                                                            ? "Engineer"
                                                            : "AI Copilot"}
                                                    </span>

                                                    <p
                                                        style={{
                                                            margin: 0,
                                                            lineHeight: 1.5,
                                                            whiteSpace:
                                                                "pre-wrap",
                                                        }}
                                                    >
                                                        {message.content}
                                                    </p>
                                                </div>
                                            )
                                        )}
                                    </div>
                                )}
                            </div>

                            <div
                                style={{
                                    display: "flex",
                                    gap: "10px",
                                    alignItems: "flex-end",
                                }}
                            >
                                <textarea
                                    value={copilotQuestion}
                                    onChange={(event) =>
                                        setCopilotQuestion(
                                            event.target.value
                                        )
                                    }
                                    onKeyDown={(event) => {
                                        if (
                                            event.key === "Enter" &&
                                            !event.shiftKey
                                        ) {
                                            event.preventDefault();

                                            if (
                                                copilotQuestion.trim() &&
                                                !copilotLoading
                                            ) {
                                                askEngineerCopilot();
                                            }
                                        }
                                    }}
                                    placeholder="Ask the Copilot about this machine..."
                                    disabled={copilotLoading}
                                    rows={3}
                                    style={{
                                        flex: 1,
                                        resize: "none",
                                        minWidth: 0,
                                        minHeight: "72px",
                                        padding: "12px 14px",
                                        borderRadius: "10px",
                                        border: "1px solid #285273",
                                        background: "#071421",
                                        color: "#ffffff",
                                        fontFamily: "inherit",
                                        fontSize: "14px",
                                        outline: "none",
                                    }}
                                />

                                <button
                                    type="button"
                                    onClick={askEngineerCopilot}
                                    disabled={
                                        copilotLoading ||
                                        !copilotQuestion.trim()
                                    }
                                    style={{
                                        padding: "12px 18px",
                                        minHeight: "72px",
                                        borderRadius: "10px",
                                        border: "1px solid #52d5ff",
                                        background: "#10263b",
                                        color: "#ffffff",
                                        fontWeight: 600,
                                        cursor:
                                            copilotLoading ||
                                                !copilotQuestion.trim()
                                                ? "not-allowed"
                                                : "pointer",
                                        opacity:
                                            copilotLoading ||
                                                !copilotQuestion.trim()
                                                ? 0.5
                                                : 1,
                                        whiteSpace: "nowrap",
                                    }}
                                >
                                    {copilotLoading
                                        ? "Thinking..."
                                        : "Send"}
                                </button>
                            </div>

                            <p
                                style={{
                                    marginTop: "8px",
                                    fontSize: "11px",
                                    color: "#7189a5",
                                }}
                            >
                                Press Enter to send · Shift + Enter
                                for a new line
                            </p>

                            {copilotError && (
                                <p
                                    className="escalation-note"
                                    style={{
                                        marginTop: "12px",
                                    }}
                                >
                                    {copilotError}
                                </p>
                            )}
                        </section>

                        {/* =================================================
                            AI DIAGNOSIS
                           ================================================= */}
                        <section
                            className="ai-copilot-column ai-diagnosis-column"
                            style={{
                                minWidth: 0,
                                minHeight: "460px",
                                padding: "20px",
                                borderRadius: "12px",
                                border: "1px solid #285273",
                                background: "#10263b",
                            }}
                        >
                            <p className="eyebrow">
                                AI Diagnostic Assessment
                            </p>

                            {!aiDiagnosis && (
                                <>
                                    <h3
                                        style={{
                                            marginBottom: "10px",
                                        }}
                                    >
                                        AI diagnosis ready on demand
                                    </h3>

                                    <p className="diagnosis-summary">
                                        AI analysis will only run when
                                        you request it. Continuous
                                        monitoring does not call the
                                        AI automatically.
                                    </p>

                                    <button
                                        type="button"
                                        onClick={runAIDiagnosis}
                                        disabled={aiLoading}
                                        style={{
                                            marginTop: "18px",
                                            padding: "12px 18px",
                                            borderRadius: "10px",
                                            border: "1px solid #52d5ff",
                                            background: "#0b182a",
                                            color: "#ffffff",
                                            fontWeight: 600,
                                            cursor: aiLoading
                                                ? "wait"
                                                : "pointer",
                                        }}
                                    >
                                        {aiLoading
                                            ? "🤖 AI Diagnosing..."
                                            : "🤖 AI Diagnose"}
                                    </button>
                                </>
                            )}

                            {aiDiagnosis && (
                                <>
                                    <p
                                        className={`severity ${aiDiagnosis.urgency.toLowerCase()}`}
                                        style={{
                                            marginTop: "8px",
                                        }}
                                    >
                                        {aiDiagnosis.urgency} ·{" "}
                                        {aiDiagnosis.confidence}%
                                        confidence
                                    </p>

                                    <div
                                        style={{
                                            marginTop: "18px",
                                            padding: "16px",
                                            borderRadius: "10px",
                                            border: "1px solid #285273",
                                            background: "#0b182a",
                                        }}
                                    >
                                        <span
                                            style={{
                                                display: "block",
                                                fontSize: "11px",
                                                color: "#7189a5",
                                                marginBottom: "6px",
                                                textTransform:
                                                    "uppercase",
                                                fontWeight: 600,
                                            }}
                                        >
                                            Diagnosis
                                        </span>

                                        <p
                                            className="diagnosis-summary"
                                            style={{
                                                margin: 0,
                                            }}
                                        >
                                            {aiDiagnosis.diagnosis}
                                        </p>
                                    </div>

                                    <div
                                        style={{
                                            marginTop: "16px",
                                            padding: "16px",
                                            borderRadius: "10px",
                                            border: "1px solid #285273",
                                            background: "#0b182a",
                                        }}
                                    >
                                        <span
                                            style={{
                                                display: "block",
                                                fontSize: "11px",
                                                color: "#7189a5",
                                                marginBottom: "6px",
                                                textTransform:
                                                    "uppercase",
                                                fontWeight: 600,
                                            }}
                                        >
                                            Probable Fault
                                        </span>

                                        <strong>
                                            {aiDiagnosis.probable_fault}
                                        </strong>
                                    </div>

                                    <div
                                        style={{
                                            display: "flex",
                                            gap: "10px",
                                            flexWrap: "wrap",
                                            marginTop: "18px",
                                        }}
                                    >
                                        <button
                                            type="button"
                                            onClick={() =>
                                                setAiModalOpen(true)
                                            }
                                            style={{
                                                padding: "11px 16px",
                                                borderRadius: "9px",
                                                border:
                                                    "1px solid #52d5ff",
                                                background: "#0b182a",
                                                color: "#ffffff",
                                                fontWeight: 600,
                                                cursor: "pointer",
                                            }}
                                        >
                                            View Full AI Diagnostic Report
                                        </button>

                                        <button
                                            type="button"
                                            onClick={runAIDiagnosis}
                                            disabled={aiLoading}
                                            style={{
                                                padding: "10px 14px",
                                                borderRadius: "9px",
                                                border:
                                                    "1px solid #285273",
                                                background:
                                                    "transparent",
                                                color: "#9ab3d0",
                                                cursor: aiLoading
                                                    ? "wait"
                                                    : "pointer",
                                            }}
                                        >
                                            {aiLoading
                                                ? "Running..."
                                                : "Run Again"}
                                        </button>
                                    </div>
                                </>
                            )}

                            {aiError && (
                                <p
                                    className="escalation-note"
                                    style={{
                                        marginTop: "16px",
                                    }}
                                >
                                    {aiError}
                                </p>
                            )}
                        </section>
                    </div>
                </article>
            </section>

            <section className="trend-panel">
                <p className="eyebrow">
                    Condition trend
                </p>

                <h2>
                    Health score history
                </h2>

                <div
                    style={{
                        width: "100%",
                        height: 280,
                    }}
                >
                    <ResponsiveContainer>
                        <LineChart data={chartData}>
                            <CartesianGrid
                                stroke="#244866"
                                strokeDasharray="3 3"
                            />

                            <XAxis
                                dataKey="time"
                                stroke="#9ab3d0"
                                tick={{
                                    fontSize: 11,
                                }}
                            />

                            <YAxis
                                domain={[0, 100]}
                                stroke="#9ab3d0"
                                tick={{
                                    fontSize: 11,
                                }}
                            />

                            <Tooltip
                                contentStyle={{
                                    background: "#0b182a",
                                    border: "1px solid #285273",
                                    borderRadius: "10px",
                                }}
                            />

                            <Line
                                type="monotone"
                                dataKey="health_score"
                                stroke="#52d5ff"
                                strokeWidth={3}
                                dot={false}
                            />
                        </LineChart>
                    </ResponsiveContainer>
                </div>
            </section>

            {aiDiagnosis && aiModalOpen && (
                <div
                    style={{
                        position: "fixed",
                        inset: 0,
                        zIndex: 1000,
                        background: "rgba(2, 10, 20, 0.82)",
                        display: "flex",
                        alignItems: "center",
                        justifyContent: "center",
                        padding: "30px",
                        overflowY: "auto",
                    }}
                >
                    <div
                        style={{
                            width: "min(1050px, 100%)",
                            maxHeight: "90vh",
                            overflowY: "auto",
                            background: "#0b182a",
                            border: "1px solid #285273",
                            borderRadius: "18px",
                            boxShadow:
                                "0 25px 80px rgba(0, 0, 0, 0.55)",
                            padding: "30px",
                        }}
                    >
                        <div
                            style={{
                                display: "flex",
                                justifyContent:
                                    "space-between",
                                alignItems:
                                    "flex-start",
                                gap: "20px",
                                marginBottom: "24px",
                            }}
                        >
                            <div>
                                <p className="eyebrow">
                                    AI Diagnostic Copilot
                                </p>

                                <h2
                                    style={{
                                        marginBottom:
                                            "8px",
                                        fontSize: "28px",
                                    }}
                                >
                                    {machine.machine_name}
                                </h2>

                                <p>
                                    Machine ID:{" "}
                                    {machine.machine_id}
                                </p>
                            </div>

                            <button
                                type="button"
                                onClick={() =>
                                    setAiModalOpen(false)
                                }
                                style={{
                                    border:
                                        "1px solid #285273",
                                    background:
                                        "transparent",
                                    color: "#9ab3d0",
                                    borderRadius:
                                        "8px",
                                    padding:
                                        "8px 12px",
                                    cursor:
                                        "pointer",
                                    fontSize:
                                        "18px",
                                }}
                            >
                                ✕
                            </button>
                        </div>

                        <div
                            style={{
                                display: "flex",
                                alignItems:
                                    "center",
                                gap: "14px",
                                flexWrap: "wrap",
                                marginBottom:
                                    "20px",
                            }}
                        >
                            <p
                                className={`severity ${aiDiagnosis.urgency.toLowerCase()}`}
                                style={{
                                    margin: 0,
                                }}
                            >
                                {aiDiagnosis.urgency}
                            </p>

                            <strong>
                                {aiDiagnosis.confidence}%
                                Diagnostic Confidence
                            </strong>
                        </div>

                        <div
                            style={{
                                padding: "20px",
                                borderRadius:
                                    "12px",
                                border:
                                    "1px solid #285273",
                                background:
                                    "#10263b",
                                marginBottom:
                                    "24px",
                            }}
                        >
                            <p className="eyebrow">
                                Diagnosis
                            </p>

                            <h3
                                style={{
                                    marginBottom:
                                        "10px",
                                }}
                            >
                                {
                                    aiDiagnosis.probable_fault
                                }
                            </h3>

                            <p className="diagnosis-summary">
                                {
                                    aiDiagnosis.diagnosis
                                }
                            </p>
                        </div>

                        <div
                            style={{
                                display: "grid",
                                gridTemplateColumns:
                                    "repeat(auto-fit, minmax(320px, 1fr))",
                                gap: "20px",
                            }}
                        >
                            <section
                                style={{
                                    padding:
                                        "20px",
                                    borderRadius:
                                        "12px",
                                    background:
                                        "#10263b",
                                    border:
                                        "1px solid #285273",
                                }}
                            >
                                <p className="eyebrow">
                                    Evidence
                                </p>

                                <ul className="risk-list">
                                    {aiDiagnosis.evidence.map(
                                        (item) => (
                                            <li
                                                key={
                                                    item
                                                }
                                            >
                                                {item}
                                            </li>
                                        )
                                    )}
                                </ul>
                            </section>

                            <section
                                style={{
                                    padding:
                                        "20px",
                                    borderRadius:
                                        "12px",
                                    background:
                                        "#10263b",
                                    border:
                                        "1px solid #285273",
                                }}
                            >
                                <p className="eyebrow">
                                    Recommended Actions
                                </p>

                                <ul className="risk-list">
                                    {aiDiagnosis.recommended_actions.map(
                                        (
                                            action
                                        ) => (
                                            <li
                                                key={
                                                    action
                                                }
                                            >
                                                {action}
                                            </li>
                                        )
                                    )}
                                </ul>
                            </section>
                        </div>

                        {aiDiagnosis.requires_escalation && (
                            <p
                                className="escalation-note"
                                style={{
                                    marginTop:
                                        "20px",
                                }}
                            >
                                Escalation recommended:
                                involve a maintenance
                                specialist or OEM.
                            </p>
                        )}

                        <div
                            style={{
                                display: "flex",
                                gap: "12px",
                                flexWrap: "wrap",
                                marginTop: "26px",
                                paddingTop: "20px",
                                borderTop:
                                    "1px solid #1d3b57",
                            }}
                        >
                            <button
                                type="button"
                                onClick={
                                    createWorkOrder
                                }
                                disabled={
                                    workOrderLoading
                                }
                                style={{
                                    padding:
                                        "12px 18px",
                                    borderRadius:
                                        "10px",
                                    border:
                                        "1px solid #52d5ff",
                                    background:
                                        "#10263b",
                                    color:
                                        "#ffffff",
                                    fontWeight:
                                        600,
                                    cursor:
                                        workOrderLoading
                                            ? "wait"
                                            : "pointer",
                                }}
                            >
                                {workOrderLoading
                                    ? "Creating Work Order..."
                                    : "Create Work Order"}
                            </button>

                            <button
                                type="button"
                                onClick={
                                    downloadPDFReport
                                }
                                style={{
                                    padding:
                                        "12px 18px",
                                    borderRadius:
                                        "10px",
                                    border:
                                        "1px solid #52d5ff",
                                    background:
                                        "#10263b",
                                    color:
                                        "#ffffff",
                                    fontWeight:
                                        600,
                                    cursor:
                                        "pointer",
                                }}
                            >
                                📄 Download PDF Report
                            </button>

                            <button
                                type="button"
                                onClick={() =>
                                    setAiModalOpen(
                                        false
                                    )
                                }
                                style={{
                                    padding:
                                        "12px 18px",
                                    borderRadius:
                                        "10px",
                                    border:
                                        "1px solid #285273",
                                    background:
                                        "transparent",
                                    color:
                                        "#9ab3d0",
                                    fontWeight:
                                        600,
                                    cursor:
                                        "pointer",
                                }}
                            >
                                Close Report
                            </button>
                        </div>

                        {workOrderMessage && (
                            <p className="live-status">
                                ✓{" "}
                                {
                                    workOrderMessage
                                }
                            </p>
                        )}

                        {workOrderError && (
                            <p className="escalation-note">
                                {
                                    workOrderError
                                }
                            </p>
                        )}
                    </div>
                </div>
            )}
        </main>
    );
}

export default MachineDetail;