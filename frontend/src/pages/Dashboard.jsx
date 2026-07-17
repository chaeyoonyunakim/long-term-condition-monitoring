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

  const urgent = summary.patients_needing_attention > 0;

  return (
    <div className="dashboard">
      <h1>Patient overview</h1>
      <p className="page-lede">Weekly adherence and cardiovascular risk sweep across the caseload.</p>

      <div className={`care-card ${urgent ? "care-card--urgent" : "care-card--clear"}`}>
        <div className="care-card__body">
          <p className="care-card__heading">{summary.summary_message}</p>
        </div>
      </div>

      <div className="card-title">Caseload</div>
      <div className="table-wrap">
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
    </div>
  );
}
