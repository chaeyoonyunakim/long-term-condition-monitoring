"""CVD risk cluster detection.

Aggregates five independent signals. 3 or more firing simultaneously is a
HIGH CVD RISK CLUSTER — the combination matters more than any single signal,
since each one in isolation is common and often benign in an aging
population, but concurrence points at an unmanaged crisis building.

Signals:
  1. Medication non-adherence — compliance <70% or a >30-day refill gap
  2. BP elevation             — latest systolic >140, or rising >=10mmHg
                                 since the earliest reading on file
  3. Weight gain               — >3kg gained within a trailing ~3-month window
  4. Lipid drift                — triglycerides >250, or LDL rising since
                                 the earliest lab on file
  5. Monitoring lapse           — no BP reading in >30 days (or none at all)
"""

from __future__ import annotations

from datetime import date, timedelta

from backend.models import BPReading, LabResult, MedicationRefillStatus, RiskClusterAssessment, RiskSignals, WeightRecord

COMPLIANCE_THRESHOLD = 70.0
BP_SYSTOLIC_THRESHOLD = 140
BP_RISE_THRESHOLD = 10
WEIGHT_GAIN_THRESHOLD_KG = 3.0
WEIGHT_GAIN_WINDOW_DAYS = 95  # ~3 months, with margin for quarterly-spaced readings
TRIGLYCERIDE_THRESHOLD = 250
MONITORING_LAPSE_DAYS = 30
CLUSTER_SIGNAL_THRESHOLD = 3


def detect_medication_nonadherence(medications: list[MedicationRefillStatus]) -> tuple[bool, list[str]]:
    reasons = []
    for m in medications:
        if m.gap_flag:
            reasons.append(f"{m.drug} refill gap of {m.days_since_last_refill} days (>{30})")
        elif m.compliance_score < COMPLIANCE_THRESHOLD:
            reasons.append(f"{m.drug} compliance {m.compliance_score}% (<{COMPLIANCE_THRESHOLD:.0f}%)")
    return bool(reasons), reasons


def detect_bp_elevation(bp_readings: list[BPReading]) -> tuple[bool, list[str]]:
    if not bp_readings:
        return False, []
    ordered = sorted(bp_readings, key=lambda r: r.date)
    latest = ordered[-1]
    earliest = ordered[0]
    reasons = []
    if latest.systolic > BP_SYSTOLIC_THRESHOLD:
        reasons.append(f"latest systolic {latest.systolic} mmHg on {latest.date} (>{BP_SYSTOLIC_THRESHOLD})")
    rise = latest.systolic - earliest.systolic
    if rise >= BP_RISE_THRESHOLD and latest.date != earliest.date:
        reasons.append(f"systolic rising {earliest.systolic}->{latest.systolic} mmHg since {earliest.date}")
    return bool(reasons), reasons


def detect_weight_gain(weight_history: list[WeightRecord]) -> tuple[bool, list[str]]:
    if len(weight_history) < 2:
        return False, []
    ordered = sorted(weight_history, key=lambda w: w.date)
    latest = ordered[-1]
    window_start = latest.date - timedelta(days=WEIGHT_GAIN_WINDOW_DAYS)
    candidates = [w for w in ordered if w.date >= window_start]
    if not candidates:
        return False, []
    baseline = min(candidates, key=lambda w: w.date)
    gain = round(latest.kg - baseline.kg, 1)
    if gain > WEIGHT_GAIN_THRESHOLD_KG:
        return True, [f"+{gain}kg since {baseline.date} ({baseline.kg}kg -> {latest.kg}kg)"]
    return False, []


def detect_lipid_drift(labs: list[LabResult]) -> tuple[bool, list[str]]:
    reasons = []
    trigs = sorted((l for l in labs if l.test.strip().lower() == "triglycerides"), key=lambda l: l.date)
    if trigs and trigs[-1].value > TRIGLYCERIDE_THRESHOLD:
        reasons.append(f"triglycerides {trigs[-1].value} {trigs[-1].unit} on {trigs[-1].date} (>{TRIGLYCERIDE_THRESHOLD})")

    ldls = sorted((l for l in labs if l.test.strip().lower() == "ldl"), key=lambda l: l.date)
    if len(ldls) >= 2 and ldls[-1].value > ldls[0].value:
        reasons.append(f"LDL rising {ldls[0].value}->{ldls[-1].value} {ldls[-1].unit} since {ldls[0].date}")

    return bool(reasons), reasons


def detect_monitoring_lapse(bp_readings: list[BPReading], reference_date: date) -> tuple[bool, list[str]]:
    if not bp_readings:
        return True, ["no BP readings on file"]
    latest_date = max(r.date for r in bp_readings)
    days_since = (reference_date - latest_date).days
    if days_since > MONITORING_LAPSE_DAYS:
        return True, [f"no BP reading in {days_since} days (last: {latest_date})"]
    return False, []


def _compute_urgency_score(
    signal_count: int,
    medications: list[MedicationRefillStatus],
    bp_readings: list[BPReading],
) -> int:
    score = signal_count * 2
    if any(m.days_since_last_refill is not None and m.days_since_last_refill > 40 for m in medications):
        score += 1
    if any(m.compliance_score < 50 for m in medications):
        score += 1
    if bp_readings and max(bp_readings, key=lambda r: r.date).systolic > 150:
        score += 1
    return min(score, 10)


def assess_risk_cluster(
    medications: list[MedicationRefillStatus],
    bp_readings: list[BPReading],
    weight_history: list[WeightRecord],
    labs: list[LabResult],
    reference_date: date,
) -> RiskClusterAssessment:
    nonadherence, r1 = detect_medication_nonadherence(medications)
    bp_elevation, r2 = detect_bp_elevation(bp_readings)
    weight_gain, r3 = detect_weight_gain(weight_history)
    lipid_drift, r4 = detect_lipid_drift(labs)
    monitoring_lapse, r5 = detect_monitoring_lapse(bp_readings, reference_date)

    signals = RiskSignals(
        medication_nonadherence=nonadherence,
        bp_elevation=bp_elevation,
        weight_gain=weight_gain,
        lipid_drift=lipid_drift,
        monitoring_lapse=monitoring_lapse,
    )
    signal_count = sum([nonadherence, bp_elevation, weight_gain, lipid_drift, monitoring_lapse])
    cluster_flag = signal_count >= CLUSTER_SIGNAL_THRESHOLD

    rationale = []
    for label, triggered, reasons in [
        ("Medication non-adherence", nonadherence, r1),
        ("BP elevation", bp_elevation, r2),
        ("Weight gain", weight_gain, r3),
        ("Lipid drift", lipid_drift, r4),
        ("Monitoring lapse", monitoring_lapse, r5),
    ]:
        if triggered:
            rationale.append(f"{label}: " + "; ".join(reasons))

    urgency_score = _compute_urgency_score(signal_count, medications, bp_readings)

    return RiskClusterAssessment(
        signals=signals,
        signal_count=signal_count,
        cluster_flag=cluster_flag,
        urgency_score=urgency_score,
        rationale=rationale,
    )
