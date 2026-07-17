"""Pydantic v2 schemas for Health Bridge.

Two layers:
  - Raw models mirror the shape of data/mock_patients.json (input).
  - Enriched models are produced by umls_mapper + adherence_engine and
    are what the API actually serves.
"""

from __future__ import annotations

from datetime import date

from pydantic import BaseModel, Field


# --- Raw input models (as they appear in mock_patients.json) ---


class MedicationOrder(BaseModel):
    name: str
    expected_refill_days: int


class RefillRecord(BaseModel):
    date: date
    drug: str
    quantity: int


class BPReading(BaseModel):
    date: date
    systolic: int
    diastolic: int


class WeightRecord(BaseModel):
    date: date
    kg: float


class LabResult(BaseModel):
    date: date
    test: str
    value: float
    unit: str


class PatientRaw(BaseModel):
    id: str
    name: str
    age: int
    conditions: list[str]
    medications: list[MedicationOrder]
    refill_history: list[RefillRecord]
    bp_readings: list[BPReading]
    weight_history: list[WeightRecord]
    labs: list[LabResult]


class PatientDataset(BaseModel):
    patients: list[PatientRaw]


# --- Enriched models (UMLS-mapped + refill-gap-calculated) ---


class MedicationRefillStatus(BaseModel):
    drug: str
    snomed: str | None = None
    bnf_code: str | None = None
    drug_class: str | None = None
    indication: str | None = None
    special_notes: str | None = None
    expected_refill_days: int
    last_refill_date: date | None = None
    days_since_last_refill: int | None = None
    refill_count: int
    gap_flag: bool = Field(
        description="True if days_since_last_refill exceeds the 30-day adherence threshold"
    )
    compliance_score: float = Field(
        description="Actual vs. expected refills over the observed history, 0-100"
    )
    trend_slope: float | None = Field(
        default=None,
        description=(
            "Percentage-point change in compliance score between the prior and "
            "current 90-day windows. Negative = declining adherence. None if the "
            "refill history doesn't span two full windows yet."
        ),
    )
    declining_flag: bool = Field(
        default=False,
        description="True if trend_slope indicates a >10 point compliance decline",
    )


class PatientMedicationState(BaseModel):
    patient_id: str
    name: str
    age: int
    conditions: list[str]
    medications: list[MedicationRefillStatus]
    bp_readings: list[BPReading]
    weight_history: list[WeightRecord]
    labs: list[LabResult]
    overall_compliance_score: float = Field(
        description="Average compliance score across all medications"
    )
    adherence_declining: bool = Field(
        default=False,
        description="True if any medication shows a declining adherence trend",
    )
