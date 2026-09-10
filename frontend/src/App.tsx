import { useState } from "react";
import { Routes, Route, Navigate, useLocation, useNavigate } from "react-router-dom";

import FleetDashboard from "./pages/FleetDashboard";
import MachineDetail from "./pages/MachineDetail";
import Alerts from "./pages/Alerts";
import WorkOrders from "./pages/WorkOrders";
import Settings from "./pages/Settings";

function App() {
  const navigate = useNavigate();
  const location = useLocation();
  const [menuOpen, setMenuOpen] = useState(false);

  const menuItems = [
    {
      label: "Fleet Dashboard",
      icon: "▦",
      path: "/",
    },
    {
      label: "Active Alerts",
      icon: "⚠",
      path: "/alerts",
    },
    {
      label: "Work Orders",
      icon: "✓",
      path: "/work-orders",
    },
    {
      label: "Settings",
      icon: "⚙",
      path: "/settings",
    },
  ];

  const handleNavigation = (path: string) => {
    navigate(path);
    setMenuOpen(false);
  };

  return (
    <>
      <Routes>
        <Route path="/" element={<FleetDashboard />} />

        <Route
          path="/machines/:machineId"
          element={<MachineDetail />}
        />

        <Route path="/alerts" element={<Alerts />} />

        <Route path="/work-orders" element={<WorkOrders />} />

        <Route path="/settings" element={<Settings />} />

        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>

      {/* Floating Menu Button */}
      {!menuOpen && (
        <button
          type="button"
          onClick={() => setMenuOpen(true)}
          aria-label="Open navigation menu"
          style={{
            position: "fixed",
            right: "24px",
            bottom: "24px",
            zIndex: 1000,
            width: "58px",
            height: "58px",
            borderRadius: "18px",
            border: "1px solid rgba(88, 215, 255, 0.5)",
            background:
              "linear-gradient(145deg, #123252, #08192c)",
            color: "#58d7ff",
            fontSize: "24px",
            fontWeight: 700,
            cursor: "pointer",
            boxShadow:
              "0 12px 35px rgba(0,0,0,0.45), 0 0 22px rgba(88,215,255,0.12)",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
          }}
        >
          ☰
        </button>
      )}

      {/* Dark Overlay */}
      {menuOpen && (
        <div
          onClick={() => setMenuOpen(false)}
          style={{
            position: "fixed",
            inset: 0,
            zIndex: 1100,
            background: "rgba(2, 10, 20, 0.65)",
            backdropFilter: "blur(4px)",
          }}
        />
      )}

      {/* Right Side Panel */}
      <aside
        style={{
          position: "fixed",
          top: 0,
          right: 0,
          zIndex: 1200,
          width: "min(340px, 88vw)",
          height: "100vh",
          background:
            "linear-gradient(180deg, #0b1d32 0%, #071321 100%)",
          borderLeft: "1px solid rgba(88, 215, 255, 0.25)",
          boxShadow: "-20px 0 50px rgba(0,0,0,0.5)",
          transform: menuOpen
            ? "translateX(0)"
            : "translateX(105%)",
          transition: "transform 0.25s ease",
          display: "flex",
          flexDirection: "column",
          overflowY: "auto",
        }}
      >
        {/* Header */}
        <div
          style={{
            padding: "28px 24px 22px",
            borderBottom:
              "1px solid rgba(255,255,255,0.08)",
          }}
        >
          <div
            style={{
              display: "flex",
              alignItems: "flex-start",
              justifyContent: "space-between",
              gap: "16px",
            }}
          >
            <div>
              <div
                style={{
                  color: "#58d7ff",
                  fontSize: "12px",
                  fontWeight: 800,
                  letterSpacing: "2px",
                  textTransform: "uppercase",
                }}
              >
                ProDiag AI
              </div>

              <div
                style={{
                  marginTop: "5px",
                  color: "#ffffff",
                  fontSize: "21px",
                  fontWeight: 700,
                }}
              >
                Control Center
              </div>

              <div
                style={{
                  marginTop: "6px",
                  color: "#7895ad",
                  fontSize: "12px",
                }}
              >
                Industrial Maintenance Intelligence
              </div>
            </div>

            <button
              type="button"
              onClick={() => setMenuOpen(false)}
              aria-label="Close navigation menu"
              style={{
                width: "38px",
                height: "38px",
                borderRadius: "12px",
                border: "1px solid rgba(255,255,255,0.12)",
                background: "rgba(255,255,255,0.05)",
                color: "#b9d4e8",
                fontSize: "22px",
                cursor: "pointer",
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
              }}
            >
              ×
            </button>
          </div>
        </div>

        {/* Navigation */}
        <div
          style={{
            padding: "24px 16px",
            flex: 1,
          }}
        >
          <div
            style={{
              color: "#6f8da5",
              fontSize: "10px",
              fontWeight: 800,
              letterSpacing: "1.8px",
              textTransform: "uppercase",
              padding: "0 10px 10px",
            }}
          >
            Navigation
          </div>

          {menuItems.map((item) => {
            const isActive =
              item.path === "/"
                ? location.pathname === "/"
                : location.pathname.startsWith(item.path);

            return (
              <button
                key={item.path}
                type="button"
                onClick={() =>
                  handleNavigation(item.path)
                }
                style={{
                  width: "100%",
                  display: "flex",
                  alignItems: "center",
                  gap: "14px",
                  padding: "14px",
                  marginBottom: "8px",
                  borderRadius: "14px",
                  border: isActive
                    ? "1px solid rgba(88,215,255,0.28)"
                    : "1px solid transparent",
                  background: isActive
                    ? "linear-gradient(90deg, rgba(30,105,145,0.35), rgba(30,105,145,0.08))"
                    : "transparent",
                  color: isActive
                    ? "#ffffff"
                    : "#9bb3c7",
                  cursor: "pointer",
                  textAlign: "left",
                }}
              >
                <span
                  style={{
                    width: "38px",
                    height: "38px",
                    borderRadius: "11px",
                    display: "flex",
                    alignItems: "center",
                    justifyContent: "center",
                    background: isActive
                      ? "rgba(88,215,255,0.14)"
                      : "rgba(255,255,255,0.04)",
                    color: isActive
                      ? "#58d7ff"
                      : "#7895ad",
                    fontSize: "18px",
                    fontWeight: 700,
                    flexShrink: 0,
                  }}
                >
                  {item.icon}
                </span>

                <span
                  style={{
                    fontSize: "14px",
                    fontWeight: isActive
                      ? 700
                      : 500,
                  }}
                >
                  {item.label}
                </span>

                {isActive && (
                  <span
                    style={{
                      marginLeft: "auto",
                      width: "7px",
                      height: "7px",
                      borderRadius: "50%",
                      background: "#58d7ff",
                      boxShadow:
                        "0 0 10px rgba(88,215,255,0.8)",
                    }}
                  />
                )}
              </button>
            );
          })}

          {/* System Status */}
          <div
            style={{
              marginTop: "30px",
              padding: "18px",
              borderRadius: "16px",
              border: "1px solid rgba(88,215,255,0.12)",
              background: "rgba(255,255,255,0.025)",
            }}
          >
            <div
              style={{
                color: "#58d7ff",
                fontSize: "10px",
                fontWeight: 800,
                letterSpacing: "1.5px",
                textTransform: "uppercase",
                marginBottom: "10px",
              }}
            >
              System Status
            </div>

            <div
              style={{
                display: "flex",
                alignItems: "center",
                gap: "9px",
                color: "#78e6b5",
                fontSize: "13px",
                fontWeight: 600,
              }}
            >
              <span
                style={{
                  width: "8px",
                  height: "8px",
                  borderRadius: "50%",
                  background: "#2ee6a6",
                  boxShadow:
                    "0 0 10px rgba(46,230,166,0.7)",
                }}
              />

              System Online
            </div>

            <div
              style={{
                marginTop: "8px",
                color: "#718ba1",
                fontSize: "11px",
                lineHeight: 1.5,
              }}
            >
              MQTT Telemetry and Predictive Maintenance
              Services are Active.
            </div>
          </div>
        </div>

        {/* Footer */}
        <div
          style={{
            padding: "18px 24px 24px",
            borderTop:
              "1px solid rgba(255,255,255,0.07)",
            color: "#607b91",
            fontSize: "10px",
            lineHeight: 1.5,
          }}
        >
          <div
            style={{
              color: "#8da7bb",
              fontWeight: 700,
              marginBottom: "3px",
            }}
          >
            ProDiag AI V2
          </div>

          Agentic Predictive Maintenance Copilot
        </div>
      </aside>
    </>
  );
}

export default App;