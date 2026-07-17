import { BrowserRouter, Route, Routes } from "react-router-dom";
import "./App.css";
import Dashboard from "./pages/Dashboard";
import PatientDetail from "./pages/PatientDetail";

export default function App() {
  return (
    <BrowserRouter>
      <div className="app-shell">
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/patients/:patientId" element={<PatientDetail />} />
        </Routes>
      </div>
    </BrowserRouter>
  );
}
