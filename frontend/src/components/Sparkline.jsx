const WIDTH = 220;
const HEIGHT = 48;
const PADDING = 6;

export default function Sparkline({ points, color = "#2563eb", thresholdY }) {
  if (!points || points.length < 2) {
    return <div className="sparkline-empty">Not enough data</div>;
  }

  const values = points.map((p) => p.value);
  const min = Math.min(...values, thresholdY ?? Infinity);
  const max = Math.max(...values, thresholdY ?? -Infinity);
  const range = max - min || 1;

  const toX = (i) => PADDING + (i / (points.length - 1)) * (WIDTH - 2 * PADDING);
  const toY = (v) => HEIGHT - PADDING - ((v - min) / range) * (HEIGHT - 2 * PADDING);

  const path = points.map((p, i) => `${i === 0 ? "M" : "L"}${toX(i)},${toY(p.value)}`).join(" ");
  const last = points[points.length - 1];

  return (
    <svg width={WIDTH} height={HEIGHT} className="sparkline" role="img" aria-label="trend chart">
      {thresholdY !== undefined && (
        <line
          x1={PADDING}
          x2={WIDTH - PADDING}
          y1={toY(thresholdY)}
          y2={toY(thresholdY)}
          stroke="#dc2626"
          strokeDasharray="3,3"
          strokeWidth="1"
        />
      )}
      <path d={path} fill="none" stroke={color} strokeWidth="2" />
      <circle cx={toX(points.length - 1)} cy={toY(last.value)} r="3" fill={color} />
    </svg>
  );
}
