import { BrowserRouter, Link, Route, Routes } from "react-router-dom";
import "./App.css";
import Dashboard from "./pages/Dashboard";
import PatientDetail from "./pages/PatientDetail";

export default function App() {
  return (
    <BrowserRouter>
      <div className="app-shell">
        <header className="site-header">
          <div className="site-header__inner">
            <Link to="/" className="wordmark">
              Health Bridge
            </Link>
            <span className="site-header__tagline">Ambient adherence monitoring &amp; CVD risk cluster detection</span>
            <span className="prototype-badge">Prototype</span>
          </div>
        </header>

        <main className="site-main">
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/patients/:patientId" element={<PatientDetail />} />
          </Routes>
        </main>

        <footer className="site-footer">
          <p>Health Bridge — eMed × OpenAI Hackathon prototype, July 2026. Not an NHS product; not for clinical use.</p>
        </footer>
      </div>
    </BrowserRouter>
  );
}
