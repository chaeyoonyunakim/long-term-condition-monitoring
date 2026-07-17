"""Medication adherence inference.

Phase 1 scope: refill gap detection only (last refill date -> days
since last refill -> gap_flag if > 30 days). Compliance scoring and
trend detection land in Phase 2.
"""

from __future__ import annotations

from datetime import date

from backend.models import MedicationOrder, MedicationRefillStatus, RefillRecord

REFILL_GAP_THRESHOLD_DAYS = 30


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
    )
