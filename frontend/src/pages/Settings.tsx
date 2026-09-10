import { useEffect, useState } from "react";
import type { CSSProperties, FormEvent } from "react";

type FactorySettings = {
    companyName: string;
    plantName: string;
    location: string;
    contactPerson: string;
    contactDetail: string;
};

type ApiFactorySettings = {
    company_name?: string;
    plant_name?: string;
    location?: string;
    contact_person?: string | null;
    contact_detail?: string | null;
};

const API_BASE = "http://127.0.0.1:5000";

const DEFAULT_SETTINGS: FactorySettings = {
    companyName: "Manufactory Industrial LLC",
    plantName: "Dubai Manufacturing Plant",
    location: "Dubai, UAE",
    contactPerson: "Maintenance Manager",
    contactDetail: "+971 50 000 0000",
};

function fromApi(data: ApiFactorySettings): FactorySettings {
    return {
        companyName: data.company_name?.trim() || DEFAULT_SETTINGS.companyName,
        plantName: data.plant_name?.trim() || DEFAULT_SETTINGS.plantName,
        location: data.location?.trim() || DEFAULT_SETTINGS.location,
        contactPerson: data.contact_person?.trim() || "",
        contactDetail: data.contact_detail?.trim() || "",
    };
}

function toApi(settings: FactorySettings) {
    return {
        company_name: settings.companyName.trim(),
        plant_name: settings.plantName.trim(),
        location: settings.location.trim(),
        contact_person: settings.contactPerson.trim(),
        contact_detail: settings.contactDetail.trim(),
    };
}

function Settings() {
    const [settings, setSettings] = useState<FactorySettings>(DEFAULT_SETTINGS);
    const [loading, setLoading] = useState(true);
    const [saving, setSaving] = useState(false);
    const [saved, setSaved] = useState(false);
    const [error, setError] = useState("");

    useEffect(() => {
        let active = true;

        const loadSettings = async () => {
            try {
                setLoading(true);
                setError("");

                const response = await fetch(`${API_BASE}/api/settings`);

                if (!response.ok) {
                    throw new Error(`HTTP ${response.status}`);
                }

                const data = (await response.json()) as ApiFactorySettings;

                if (active) {
                    setSettings(fromApi(data));
                }
            } catch (loadError) {
                console.error("Unable to load factory settings:", loadError);
                if (active) {
                    setError(
                        "Could not connect to the settings service. Showing the default plant profile."
                    );
                }
            } finally {
                if (active) {
                    setLoading(false);
                }
            }
        };

        void loadSettings();

        return () => {
            active = false;
        };
    }, []);

    const updateField = (field: keyof FactorySettings, value: string) => {
        setSettings((current) => ({ ...current, [field]: value }));
        setSaved(false);
        setError("");
    };

    const handleSubmit = async (event: FormEvent<HTMLFormElement>) => {
        event.preventDefault();

        if (!settings.companyName.trim()) {
            setError("Company name is required.");
            return;
        }

        if (!settings.plantName.trim()) {
            setError("Plant name is required.");
            return;
        }

        if (!settings.location.trim()) {
            setError("Location is required.");
            return;
        }

        try {
            setSaving(true);
            setSaved(false);
            setError("");

            const response = await fetch(`${API_BASE}/api/settings`, {
                method: "PUT",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(toApi(settings)),
            });

            const data = (await response.json().catch(() => ({}))) as
                | ApiFactorySettings
                | { error?: string };

            if (!response.ok) {
                throw new Error(
                    "error" in data && data.error
                        ? data.error
                        : `HTTP ${response.status}`
                );
            }

            setSettings(fromApi(data as ApiFactorySettings));
            setSaved(true);
        } catch (saveError) {
            console.error("Unable to save factory settings:", saveError);
            setError(
                saveError instanceof Error
                    ? saveError.message
                    : "Could not save factory settings."
            );
        } finally {
            setSaving(false);
        }
    };

    const inputStyle: CSSProperties = {
        width: "100%",
        boxSizing: "border-box",
        border: "1px solid #244965",
        borderRadius: "12px",
        background: "#081a2d",
        color: "#f4f8fc",
        padding: "14px 15px",
        fontSize: "0.95rem",
        outline: "none",
    };

    const labelStyle: CSSProperties = {
        display: "block",
        color: "#a9bfd3",
        fontSize: "0.8rem",
        fontWeight: 600,
    };

    return (
        <main style={{ minHeight: "100%", paddingBottom: "80px" }}>
            <header
                style={{
                    display: "flex",
                    justifyContent: "space-between",
                    alignItems: "flex-end",
                    gap: "24px",
                    paddingBottom: "24px",
                    marginBottom: "28px",
                    borderBottom: "1px solid #1d3b57",
                }}
            >
                <div>
                    <p
                        style={{
                            margin: "0 0 8px",
                            color: "#4fdcff",
                            fontSize: "0.72rem",
                            fontWeight: 700,
                            letterSpacing: "0.16em",
                            textTransform: "uppercase",
                        }}
                    >
                        System Configuration
                    </p>
                    <h1
                        style={{
                            margin: 0,
                            color: "#f5f8fc",
                            fontSize: "clamp(1.8rem, 3vw, 2.4rem)",
                            lineHeight: 1.1,
                        }}
                    >
                        Factory Settings
                    </h1>
                    <p
                        style={{
                            margin: "10px 0 0",
                            maxWidth: "680px",
                            color: "#7895b0",
                            fontSize: "0.92rem",
                            lineHeight: 1.6,
                        }}
                    >
                        Configure the company and plant identity displayed across the
                        ProDiag AI monitoring system.
                    </p>
                </div>

                <div
                    style={{
                        display: "inline-flex",
                        alignItems: "center",
                        gap: "9px",
                        padding: "9px 13px",
                        border: "1px solid #21445f",
                        borderRadius: "999px",
                        background: "#0a2035",
                        color: "#7ee7c7",
                        fontSize: "0.74rem",
                        fontWeight: 700,
                        letterSpacing: "0.08em",
                        whiteSpace: "nowrap",
                    }}
                >
                    <span
                        style={{
                            width: "7px",
                            height: "7px",
                            borderRadius: "50%",
                            background: "#35e29c",
                            boxShadow: "0 0 0 4px #35e29c24",
                        }}
                    />
                    PLANT PROFILE
                </div>
            </header>

            {error && (
                <div
                    role="alert"
                    style={{
                        marginBottom: "20px",
                        padding: "13px 16px",
                        border: "1px solid #7b3c48",
                        borderRadius: "12px",
                        background: "#321b27",
                        color: "#ffb7c2",
                        fontSize: "0.82rem",
                        lineHeight: 1.5,
                    }}
                >
                    {error}
                </div>
            )}

            <section
                style={{
                    display: "grid",
                    gridTemplateColumns: "minmax(0, 1.45fr) minmax(280px, 0.55fr)",
                    gap: "22px",
                    alignItems: "start",
                }}
            >
                <form
                    onSubmit={handleSubmit}
                    style={{
                        padding: "26px",
                        border: "1px solid #234965",
                        borderRadius: "18px",
                        background: "linear-gradient(145deg, #0b2138 0%, #091a2d 100%)",
                        boxShadow: "0 18px 45px #00000024",
                        opacity: loading ? 0.7 : 1,
                    }}
                >
                    <div style={{ marginBottom: "24px" }}>
                        <p
                            style={{
                                margin: "0 0 7px",
                                color: "#4fdcff",
                                fontSize: "0.7rem",
                                fontWeight: 700,
                                letterSpacing: "0.14em",
                                textTransform: "uppercase",
                            }}
                        >
                            Factory Profile
                        </p>
                        <h2 style={{ margin: 0, color: "#f5f8fc", fontSize: "1.25rem" }}>
                            Company & Plant Details
                        </h2>
                    </div>

                    <div
                        style={{
                            display: "grid",
                            gridTemplateColumns: "repeat(2, minmax(0, 1fr))",
                            gap: "20px",
                        }}
                    >
                        <label style={labelStyle}>
                            Company Name
                            <input
                                value={settings.companyName}
                                onChange={(event) => updateField("companyName", event.target.value)}
                                placeholder="Company name"
                                style={{ ...inputStyle, marginTop: "8px" }}
                                disabled={loading || saving}
                            />
                        </label>

                        <label style={labelStyle}>
                            Plant Name
                            <input
                                value={settings.plantName}
                                onChange={(event) => updateField("plantName", event.target.value)}
                                placeholder="Plant name"
                                style={{ ...inputStyle, marginTop: "8px" }}
                                disabled={loading || saving}
                            />
                        </label>

                        <label style={labelStyle}>
                            Location
                            <input
                                value={settings.location}
                                onChange={(event) => updateField("location", event.target.value)}
                                placeholder="City, country"
                                style={{ ...inputStyle, marginTop: "8px" }}
                                disabled={loading || saving}
                            />
                        </label>

                        <label style={labelStyle}>
                            Contact Person
                            <input
                                value={settings.contactPerson}
                                onChange={(event) => updateField("contactPerson", event.target.value)}
                                placeholder="Maintenance contact"
                                style={{ ...inputStyle, marginTop: "8px" }}
                                disabled={loading || saving}
                            />
                        </label>

                        <label style={{ ...labelStyle, gridColumn: "1 / -1" }}>
                            Contact Detail
                            <input
                                value={settings.contactDetail}
                                onChange={(event) => updateField("contactDetail", event.target.value)}
                                placeholder="Phone or contact detail"
                                style={{ ...inputStyle, marginTop: "8px" }}
                                disabled={loading || saving}
                            />
                        </label>
                    </div>

                    <div
                        style={{
                            display: "flex",
                            alignItems: "center",
                            justifyContent: "flex-end",
                            gap: "14px",
                            marginTop: "28px",
                            paddingTop: "22px",
                            borderTop: "1px solid #173650",
                        }}
                    >
                        {loading && (
                            <span style={{ color: "#7895b0", fontSize: "0.82rem" }}>
                                Loading plant profile…
                            </span>
                        )}
                        {saved && !loading && (
                            <span style={{ color: "#7ee7c7", fontSize: "0.82rem", fontWeight: 600 }}>
                                ✓ Settings saved to database
                            </span>
                        )}
                        <button
                            type="submit"
                            disabled={loading || saving}
                            style={{
                                border: "1px solid #35c9f5",
                                borderRadius: "11px",
                                background: saving ? "#24556e" : "linear-gradient(135deg, #0d9fd0, #1474a4)",
                                color: "#ffffff",
                                padding: "12px 22px",
                                fontSize: "0.86rem",
                                fontWeight: 700,
                                cursor: loading || saving ? "not-allowed" : "pointer",
                                boxShadow: "0 8px 24px #009ed52b",
                            }}
                        >
                            {saving ? "Saving…" : "Save Changes"}
                        </button>
                    </div>
                </form>

                <aside
                    style={{
                        padding: "24px",
                        border: "1px solid #234965",
                        borderRadius: "18px",
                        background: "#0a1d31",
                    }}
                >
                    <p
                        style={{
                            margin: "0 0 8px",
                            color: "#4fdcff",
                            fontSize: "0.7rem",
                            fontWeight: 700,
                            letterSpacing: "0.14em",
                            textTransform: "uppercase",
                        }}
                    >
                        Live Preview
                    </p>
                    <h2 style={{ margin: "0 0 22px", color: "#f5f8fc", fontSize: "1.12rem" }}>
                        Plant Identity
                    </h2>

                    <div
                        style={{
                            padding: "18px",
                            border: "1px solid #1e405c",
                            borderRadius: "14px",
                            background: "#08182a",
                        }}
                    >
                        <div style={{ display: "flex", alignItems: "flex-start", gap: "14px" }}>
                            <div
                                style={{
                                    width: "42px",
                                    height: "42px",
                                    flex: "0 0 42px",
                                    display: "grid",
                                    placeItems: "center",
                                    border: "1px solid #24607d",
                                    borderRadius: "11px",
                                    background: "#0c2941",
                                    color: "#4fdcff",
                                    fontSize: "0.7rem",
                                    fontWeight: 800,
                                }}
                            >
                                PA
                            </div>
                            <div style={{ minWidth: 0 }}>
                                <strong style={{ display: "block", color: "#f5f8fc", fontSize: "0.98rem", lineHeight: 1.35 }}>
                                    {settings.companyName || "Company Name"}
                                </strong>
                                <span style={{ display: "block", marginTop: "4px", color: "#b7cadb", fontSize: "0.85rem" }}>
                                    {settings.plantName || "Plant Name"}
                                </span>
                                <span style={{ display: "block", marginTop: "5px", color: "#718ea8", fontSize: "0.76rem" }}>
                                    {settings.location || "Location"}
                                </span>
                            </div>
                        </div>
                    </div>

                    <div style={{ marginTop: "20px", paddingTop: "18px", borderTop: "1px solid #173650" }}>
                        <p style={{ margin: "0 0 7px", color: "#708da7", fontSize: "0.72rem", textTransform: "uppercase", letterSpacing: "0.08em" }}>
                            Maintenance Contact
                        </p>
                        <strong style={{ display: "block", color: "#dce8f2", fontSize: "0.86rem" }}>
                            {settings.contactPerson || "Contact Person"}
                        </strong>
                        <span style={{ display: "block", marginTop: "4px", color: "#7895b0", fontSize: "0.78rem" }}>
                            {settings.contactDetail || "Contact Detail"}
                        </span>
                    </div>
                </aside>
            </section>

            <p style={{ margin: "18px 2px 0", color: "#58738b", fontSize: "0.76rem", lineHeight: 1.5 }}>
                Factory identity is stored in the ProDiag AI backend database. Changes are available to the dashboard and other system views after they load the settings API.
            </p>
        </main>
    );
}

export default Settings;
