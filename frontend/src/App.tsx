import { useEffect, useState } from "react";
import {
  CartesianGrid,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis
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
  health_status: "HEALTHY" | "WARNING" | "CRITICAL";
  risk_reasons: string[];
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
};

type HistoryResponse = {
  machine_id: string;
  count: number;
  readings: HistoryReading[];
};

type Diagnosis = {
  fault_type: string;
  severity: "HEALTHY" | "WARNING" | "CRITICAL";
  confidence: number;
  summary: string;
  recommended_actions: string[];
  estimated_time_to_failure: string;
  escalation_required: boolean;
};

type DiagnosisResponse = {
  machine_id: string;
  machine_name: string;
  diagnosis: Diagnosis;
};

function App() {
  const [machines, setMachines] = useState<MachineData[]>([]);
  const [selectedMachineId, setSelectedMachineId] = useState("");
  const [history, setHistory] = useState<HistoryReading[]>([]);
  const [diagnosis, setDiagnosis] = useState<Diagnosis | null>(null);
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
        setSelectedMachineId((currentId) => {
          const machineStillExists = data.machines.some(
            (machine) => machine.machine_id === currentId
          );

          return machineStillExists
            ? currentId
            : data.machines[0]?.machine_id ?? "";
        });

        setError("");
      } catch (err) {
        setError(err instanceof Error ? err.message : "Unknown error");
      }
    };

    loadTelemetry();
    const intervalId = setInterval(loadTelemetry, 1000);

    return () => clearInterval(intervalId);
  }, []);

  useEffect(() => {
    if (!selectedMachineId) return;

    const loadHistory = async () => {
      try {
        const response = await fetch(
          `http://127.0.0.1:5000/api/machines/${selectedMachineId}/history?limit=40`
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
  }, [selectedMachineId]);

  useEffect(() => {
    if (!selectedMachineId) return;

    let active = true;

    const loadDiagnosis = async () => {
      try {
        const response = await fetch(
          `http://127.0.0.1:5000/api/machines/${selectedMachineId}/diagnosis`
        );

        if (!response.ok) {
          throw new Error("Diagnosis is not available");
        }

        const data: DiagnosisResponse = await response.json();

        if (active) {
          setDiagnosis(data.diagnosis);
        }
      } catch (err) {
        console.error(err);

        if (active) {
          setDiagnosis(null);
        }
      }
    };

    setDiagnosis(null);
    loadDiagnosis();

    const intervalId = setInterval(loadDiagnosis, 2000);

    return () => {
      active = false;
      clearInterval(intervalId);
    };
  }, [selectedMachineId]);

  const selectedMachine = machines.find(
    (machine) => machine.machine_id === selectedMachineId
  );

  const criticalCount = machines.filter(
    (machine) => machine.health_status === "CRITICAL"
  ).length;

  const warningCount = machines.filter(
    (machine) => machine.health_status === "WARNING"
  ).length;

  const healthyCount = machines.filter(
    (machine) => machine.health_status === "HEALTHY"
  ).length;

  const chartData = history.map((reading) => ({
    time: new Date(reading.timestamp).toLocaleTimeString([], {
      minute: "2-digit",
      second: "2-digit"
    }),
    health_score: reading.health_score
  }));

  if (error) {
    return <main><p>Connection error: {error}</p></main>;
  }

  if (!selectedMachine) {
    return <main><p>Waiting for live telemetry from all machines...</p></main>;
  }

  return (
    <main>
      <header className="app-header">
        <p className="eyebrow">Live industrial intelligence</p>
        <h1>ProDiag AI V2</h1>
        <p>Predictive Maintenance Copilot</p>
      </header>

      <section className="fleet-overview">
        <div>
          <p className="eyebrow">Fleet overview</p>
          <h2>{machines.length} connected machines</h2>
        </div>

        <div className="fleet-counts">
          <span className="critical-count">{criticalCount} Critical</span>
          <span className="warning-count">{warningCount} Warning</span>
          <span className="healthy-count">{healthyCount} Healthy</span>
        </div>
      </section>

      <section className="machine-grid">
        {machines.map((machine) => (
          <button
            className={`machine-card ${machine.health_status.toLowerCase()} ${machine.machine_id === selectedMachine.machine_id ? "selected" : ""
              }`}
            key={machine.machine_id}
            onClick={() => setSelectedMachineId(machine.machine_id)}
            type="button"
          >
            <div className="machine-card-top">
              <span>{machine.machine_id}</span>
              <strong>{machine.health_score}</strong>
            </div>

            <h3>{machine.machine_name}</h3>
            <p>{machine.health_status}</p>

            <small>
              {machine.risk_reasons[0] ?? "No active risk indicators"}
            </small>
          </button>
        ))}
      </section>

      <section className="selected-title">
        <div>
          <p className="eyebrow">Selected machine</p>
          <h2>{selectedMachine.machine_name}</h2>
          <p>Machine ID: {selectedMachine.machine_id}</p>
        </div>

        <div className={`health-badge ${selectedMachine.health_status.toLowerCase()}`}>
          <span>Health score</span>
          <strong>{selectedMachine.health_score}</strong>
          <small>/ 100 · {selectedMachine.health_status}</small>
        </div>
      </section>

      <section className="dashboard-grid">
        <article className="panel">
          <p className="eyebrow">Live sensor readings</p>
          <h2>Operating condition</h2>

          <div className="metric-grid">
            <div className="metric">
              <span>Temperature</span>
              <strong>{selectedMachine.temperature_c} °C</strong>
            </div>

            <div className="metric">
              <span>Vibration</span>
              <strong>{selectedMachine.vibration_mm_s} mm/s</strong>
            </div>

            <div className="metric">
              <span>Current</span>
              <strong>{selectedMachine.current_a} A</strong>
            </div>

            <div className="metric">
              <span>Speed</span>
              <strong>{selectedMachine.rpm} RPM</strong>
            </div>
          </div>

          <p className="live-status">
            <span className="live-dot" />
            {selectedMachine.status} · Updated{" "}
            {new Date(selectedMachine.timestamp).toLocaleTimeString()}
          </p>
        </article>

        <article className="panel diagnosis-panel">
          <p className="eyebrow">AI fault diagnosis</p>
          <h2>{diagnosis?.fault_type ?? "Analyzing machine condition..."}</h2>

          {diagnosis && (
            <>
              <p className={`severity ${diagnosis.severity.toLowerCase()}`}>
                {diagnosis.severity} · {Math.round(diagnosis.confidence * 100)}% confidence
              </p>

              <p className="diagnosis-summary">{diagnosis.summary}</p>

              <p className="eyebrow diagnosis-label">Recommended action</p>
              <ul className="risk-list">
                {diagnosis.recommended_actions.slice(0, 2).map((action) => (
                  <li key={action}>{action}</li>
                ))}
              </ul>

              <p className="failure-window">
                Estimated time to failure: {diagnosis.estimated_time_to_failure}
              </p>

              {diagnosis.escalation_required && (
                <p className="escalation-note">
                  Escalation recommended: involve a maintenance specialist or OEM.
                </p>
              )}
            </>
          )}
        </article>
      </section>

      <section className="trend-panel">
        <p className="eyebrow">Condition trend</p>
        <h2>Health score history</h2>

        <div style={{ width: "100%", height: 280 }}>
          <ResponsiveContainer>
            <LineChart data={chartData}>
              <CartesianGrid stroke="#244866" strokeDasharray="3 3" />
              <XAxis dataKey="time" stroke="#9ab3d0" tick={{ fontSize: 11 }} />
              <YAxis
                domain={[0, 100]}
                stroke="#9ab3d0"
                tick={{ fontSize: 11 }}
              />
              <Tooltip
                contentStyle={{
                  background: "#0b182a",
                  border: "1px solid #285273",
                  borderRadius: "10px"
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
    </main>
  );
}

export default App;