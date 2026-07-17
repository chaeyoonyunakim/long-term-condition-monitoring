"""Medication adherence inference.

- Refill gap detection: last refill date -> days since -> gap_flag if > 30 days.
- Compliance score: actual refills vs. expected refills over the observed
  history (a Proportion-of-Days-Covered-style ratio), 0-100.
- Trend detection: compares compliance over the most recent 60 days against
  the preceding 60 days. A rolling window (rather than a literal single
  calendar month) is used because monthly refill cadences only produce 0 or 1
  refill per month, which makes a true month-over-month ratio too coarse to
  be a meaningful signal — 60 days gives ~2 expected refills per window,
  enough resolution to detect a real decline while still fitting within a
  ~5-6 month observation history.
"""

from __future__ import annotations

from datetime import date, timedelta

from backend.models import MedicationOrder, MedicationRefillStatus, RefillRecord

REFILL_GAP_THRESHOLD_DAYS = 30
TREND_WINDOW_DAYS = 60
TREND_DECLINE_THRESHOLD = 10.0  # percentage points


def compute_refill_gap(
    drug: str,
    refill_history: list[RefillRecord],
    reference_date: date,
) -> tuple[date | None, int | None, int]:
    """Returns (last_refill_date, days_since_last_refill, refill_count)
    for a single drug, scanning the patient's full refill history."""
    drug_refills = sorted(
        (r for r in refill_history if r.drug.strip().lower() == drug.strip().lower()),
        key=lambda r: r.date,
    )
    if not drug_refills:
        return None, None, 0

    last_refill_date = drug_refills[-1].date
    days_since_last_refill = (reference_date - last_refill_date).days
    return last_refill_date, days_since_last_refill, len(drug_refills)


def _drug_refill_dates(drug: str, refill_history: list[RefillRecord]) -> list[date]:
    return sorted(r.date for r in refill_history if r.drug.strip().lower() == drug.strip().lower())


def compute_compliance_score(
    refill_dates: list[date],
    expected_refill_days: int,
    reference_date: date,
    window_start: date | None = None,
) -> float:
    """(actual refills / expected refills) x 100 over [window_start, reference_date],
    capped at 100. window_start defaults to the earliest refill on record."""
    if not refill_dates:
        return 0.0

    period_start = window_start if window_start is not None else refill_dates[0]
    in_window = [d for d in refill_dates if period_start <= d <= reference_date]
    period_days = (reference_date - period_start).days
    if period_days <= 0:
        return 100.0 if in_window else 0.0

    expected_refills = max(period_days / expected_refill_days, 1e-9)
    score = (len(in_window) / expected_refills) * 100
    return round(min(score, 100.0), 1)


def compute_trend(
    refill_dates: list[date],
    expected_refill_days: int,
    reference_date: date,
) -> tuple[float | None, bool]:
    """Compares compliance in the most recent TREND_WINDOW_DAYS window against
    the preceding one. Returns (trend_slope, declining_flag). trend_slope is
    None if the refill history doesn't reach back a full two windows."""
    earliest = min(refill_dates, default=None)
    two_windows_ago = reference_date - timedelta(days=2 * TREND_WINDOW_DAYS)
    if earliest is None or earliest > two_windows_ago:
        return None, False

    current_window_start = reference_date - timedelta(days=TREND_WINDOW_DAYS)
    prior_window_start = reference_date - timedelta(days=2 * TREND_WINDOW_DAYS)

    current_score = compute_compliance_score(
        refill_dates, expected_refill_days, reference_date, window_start=current_window_start
    )
    prior_score = compute_compliance_score(
        refill_dates,
        expected_refill_days,
        current_window_start,
        window_start=prior_window_start,
    )

    trend_slope = round(current_score - prior_score, 1)
    declining_flag = trend_slope <= -TREND_DECLINE_THRESHOLD
    return trend_slope, declining_flag


def build_medication_status(
    medication: MedicationOrder,
    refill_history: list[RefillRecord],
    med_info: dict,
    reference_date: date,
) -> MedicationRefillStatus:
    last_refill_date, days_since_last_refill, refill_count = compute_refill_gap(
        medication.name, refill_history, reference_date
    )
    gap_flag = days_since_last_refill is not None and days_since_last_refill > REFILL_GAP_THRESHOLD_DAYS

    refill_dates = _drug_refill_dates(medication.name, refill_history)
    compliance_score = compute_compliance_score(refill_dates, medication.expected_refill_days, reference_date)
    trend_slope, declining_flag = compute_trend(refill_dates, medication.expected_refill_days, reference_date)

    return MedicationRefillStatus(
        drug=medication.name,
        snomed=med_info.get("snomed"),
        bnf_code=med_info.get("bnf_code"),
        drug_class=med_info.get("drug_class"),
        indication=med_info.get("indication"),
        special_notes=med_info.get("special_notes"),
        expected_refill_days=medication.expected_refill_days,
        last_refill_date=last_refill_date,
        days_since_last_refill=days_since_last_refill,
        refill_count=refill_count,
        gap_flag=gap_flag,
        compliance_score=compliance_score,
        trend_slope=trend_slope,
        declining_flag=declining_flag,
    )


def summarize_patient_adherence(medications: list[MedicationRefillStatus]) -> tuple[float, bool]:
    """Returns (overall_compliance_score, adherence_declining) for a patient
    given their per-medication adherence statuses."""
    if not medications:
        return 0.0, False
    overall = round(sum(m.compliance_score for m in medications) / len(medications), 1)
    declining = any(m.declining_flag for m in medications)
    return overall, declining
