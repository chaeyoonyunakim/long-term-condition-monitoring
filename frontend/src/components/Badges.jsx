export function ClusterBadge({ flagged }) {
  return flagged ? (
    <span className="badge badge-red">HIGH CVD RISK CLUSTER</span>
  ) : (
    <span className="badge badge-green">Stable</span>
  );
}

export function UrgencyBadge({ score }) {
  let tier = "badge-green";
  if (score >= 7) tier = "badge-red";
  else if (score >= 3) tier = "badge-amber";
  return <span className={`badge ${tier}`}>Urgency {score}/10</span>;
}

export function GapBadge({ flagged, days }) {
  if (!flagged) return null;
  return <span className="badge badge-red">{days}d refill gap</span>;
}

export function DecliningBadge({ flagged }) {
  if (!flagged) return null;
  return <span className="badge badge-amber">Declining adherence</span>;
}
