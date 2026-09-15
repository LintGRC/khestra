import { Route, Routes, Navigate } from "react-router-dom";
import Layout from "./Layout";
import { aigovernanceRouteElements } from "./routeElements";

export default function App() {
  return (
    <Routes>
      <Route element={<Layout />}>
        {aigovernanceRouteElements}
      </Route>
      <Route path="*" element={<Navigate to="/dashboard" replace />} />
    </Routes>
  );
}
