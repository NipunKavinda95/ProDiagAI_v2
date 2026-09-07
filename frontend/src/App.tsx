import { Routes, Route, Navigate } from "react-router-dom";
import FleetDashboard from "./pages/FleetDashboard";
import MachineDetail from "./pages/MachineDetail";
import Alerts from "./pages/Alerts";
import WorkOrders from "./pages/WorkOrders";

function App() {
  return (
    <Routes>
      <Route path="/" element={<FleetDashboard />} />

      {/* Temporary routes — pages will be added next */}
      <Route
        path="/machines/:machineId"
        element={<MachineDetail />}
      />

      <Route
        path="/alerts"
        element={<Alerts />}
      />

      <Route
        path="/work-orders"
        element={<WorkOrders />}
      />

      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}

export default App;