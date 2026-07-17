import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";
import { fetchPatient } from "../api";
import { ClusterBadge, DecliningBadge, GapBadge, UrgencyBadge } from "../components/Badges";
import Sparkline from "../components/Sparkline";

export default function PatientDetail() {
  const { patientId } = useParams();
  const [patient, setPatient] = useState(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    setPatient(null);
    fetchPatient(patientId).then(setPatient).catch((e) => setError(e.message));
  }, [patientId]);

  if (error) return <div className="error">Failed to load patient: {error}</div>;
  if (!patient) return <div className="loading">Loading patient…</div>;

  const { risk_assessment: risk } = patient;
  const bpPoints = [...patient.bp_readings]
    .sort((a, b) => a.date.localeCompare(b.date))
    .map((r) => ({ label: r.date, value: r.systolic }));
  const weightPoints = [...patient.weight_history]
    .sort((a, b) => a.date.localeCompare(b.date))
    .map((r) => ({ label: r.date, value: r.kg }));

  return (
    <div className="patient-detail">
      <Link to="/" className="back-link">
        ← Back to dashboard
      </Link>

      <header className="patient-header">
        <h1>
          {patient.name} <span className="patient-id">({patient.patient_id})</span>
        </h1>
        <p className="subtitle">
          Age {patient.age} · {patient.conditions.join(", ")}
        </p>
        <div className="badge-row">
          <ClusterBadge flagged={risk.cluster_flag} />
          <UrgencyBadge score={risk.urgency_score} />
        </div>
      </header>

      {risk.rationale.length > 0 && (
        <section className="risk-panel">
          <h2>Risk signals ({risk.signal_count}/5)</h2>
          <ul className="rationale-list">
            {risk.rationale.map((r, i) => (
              <li key={i}>{r}</li>
            ))}
          </ul>
        </section>
      )}

      <section>
        <h2>Medications</h2>
        <table className="med-table">
          <thead>
            <tr>
              <th>Drug</th>
              <th>Indication</th>
              <th>Last refill</th>
              <th>Days since</th>
              <th>Compliance</th>
              <th>Flags</th>
            </tr>
          </thead>
          <tbody>
            {patient.medications.map((m) => (
              <tr key={m.drug} className={m.gap_flag ? "row-flagged" : ""}>
                <td>
                  <strong>{m.drug}</strong>
                  {m.drug_class && <div className="drug-class">{m.drug_class}</div>}
                </td>
                <td>
                  {m.indication}
                  {m.special_notes && <div className="special-notes">{m.special_notes}</div>}
                </td>
                <td>{m.last_refill_date ?? "—"}</td>
                <td>{m.days_since_last_refill ?? "—"}</td>
                <td>{m.compliance_score}%</td>
                <td>
                  <GapBadge flagged={m.gap_flag} days={m.days_since_last_refill} />
                  <DecliningBadge flagged={m.declining_flag} />
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </section>

      <section className="vitals-section">
        <div className="vitals-card">
          <h2>Blood pressure (systolic)</h2>
          <Sparkline points={bpPoints} color="#dc2626" thresholdY={140} />
          <div className="vitals-footnote">
            Latest: {bpPoints.at(-1)?.value ?? "—"} mmHg on {bpPoints.at(-1)?.label ?? "—"}
          </div>
        </div>
        <div className="vitals-card">
          <h2>Weight</h2>
          <Sparkline points={weightPoints} color="#2563eb" />
          <div className="vitals-footnote">
            Latest: {weightPoints.at(-1)?.value ?? "—"} kg on {weightPoints.at(-1)?.label ?? "—"}
          </div>
        </div>
      </section>

      <section>
        <h2>Labs</h2>
        <table className="med-table">
          <thead>
            <tr>
              <th>Test</th>
              <th>Value</th>
              <th>Date</th>
            </tr>
          </thead>
          <tbody>
            {[...patient.labs]
              .sort((a, b) => b.date.localeCompare(a.date))
              .map((l, i) => (
                <tr key={i}>
                  <td>{l.test}</td>
                  <td>
                    {l.value} {l.unit}
                  </td>
                  <td>{l.date}</td>
                </tr>
              ))}
          </tbody>
        </table>
      </section>
    </div>
  );
}
