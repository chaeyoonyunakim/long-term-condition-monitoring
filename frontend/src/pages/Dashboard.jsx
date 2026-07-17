import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { fetchDashboard } from "../api";
import { ClusterBadge, UrgencyBadge } from "../components/Badges";

export default function Dashboard() {
  const [summary, setSummary] = useState(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchDashboard().then(setSummary).catch((e) => setError(e.message));
  }, []);

  if (error) return <div className="error">Failed to load dashboard: {error}</div>;
  if (!summary) return <div className="loading">Loading dashboard…</div>;

  return (
    <div className="dashboard">
      <header className="dashboard-header">
        <h1>Health Bridge</h1>
        <p className="subtitle">Ambient adherence monitoring &amp; CVD risk cluster detection</p>
      </header>

      <div className={`summary-banner ${summary.patients_needing_attention > 0 ? "urgent" : "clear"}`}>
        {summary.summary_message}
      </div>

      <table className="patient-table">
        <thead>
          <tr>
            <th>Patient</th>
            <th>Age</th>
            <th>Conditions</th>
            <th>Status</th>
            <th>Urgency</th>
            <th>Compliance</th>
          </tr>
        </thead>
        <tbody>
          {summary.patients.map((p) => (
            <tr key={p.patient_id} className={p.cluster_flag ? "row-flagged" : ""}>
              <td>
                <Link to={`/patients/${p.patient_id}`} className="patient-link">
                  {p.name}
                </Link>
              </td>
              <td>{p.age}</td>
              <td className="conditions-cell">{p.conditions.join(", ")}</td>
              <td>
                <ClusterBadge flagged={p.cluster_flag} />
              </td>
              <td>
                <UrgencyBadge score={p.urgency_score} />
              </td>
              <td>{p.overall_compliance_score}%</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
