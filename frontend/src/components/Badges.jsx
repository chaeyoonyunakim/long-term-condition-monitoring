export function ClusterBadge({ flagged }) {
  return flagged ? (
    <span className="tag tag-red">HIGH CVD RISK CLUSTER</span>
  ) : (
    <span className="tag tag-green">Stable</span>
  );
}

export function UrgencyBadge({ score }) {
  let tier = "tag-green";
  if (score >= 7) tier = "tag-red";
  else if (score >= 3) tier = "tag-amber";
  return <span className={`tag ${tier}`}>Urgency {score}/10</span>;
}

export function GapBadge({ flagged, days }) {
  if (!flagged) return null;
  return <span className="tag tag-red">{days}d refill gap</span>;
}

export function DecliningBadge({ flagged }) {
  if (!flagged) return null;
  return <span className="tag tag-amber">Declining adherence</span>;
}
