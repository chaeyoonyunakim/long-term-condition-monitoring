"""Health Bridge FastAPI server.

Phase 1: ingestion + UMLS-mapped, refill-gap-annotated patient state.
"""

from __future__ import annotations

import json
from contextlib import asynccontextmanager
from datetime import date
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from backend.adherence_engine import build_medication_status, summarize_patient_adherence
from backend.cluster_detector import assess_risk_cluster
from backend.models import DashboardSummary, PatientDataset, PatientMedicationState, PatientSummary
from backend.umls_mapper import get_medication_info

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
DEFAULT_DATASET_PATH = DATA_DIR / "mock_patients.json"


@asynccontextmanager
async def lifespan(app: FastAPI):
    _load_default_dataset()
    yield


app = FastAPI(title="Health Bridge", version="0.1.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory store: patient_id -> enriched PatientMedicationState
PATIENT_STORE: dict[str, PatientMedicationState] = {}


def _enrich_patient(raw, reference_date: date) -> PatientMedicationState:
    medications = [
        build_medication_status(
            medication=med,
            refill_history=raw.refill_history,
            med_info=get_medication_info(med.name),
            reference_date=reference_date,
        )
        for med in raw.medications
    ]
    overall_compliance_score, adherence_declining = summarize_patient_adherence(medications)
    risk_assessment = assess_risk_cluster(
        medications=medications,
        bp_readings=raw.bp_readings,
        weight_history=raw.weight_history,
        labs=raw.labs,
        reference_date=reference_date,
    )
    return PatientMedicationState(
        patient_id=raw.id,
        name=raw.name,
        age=raw.age,
        conditions=raw.conditions,
        medications=medications,
        bp_readings=raw.bp_readings,
        weight_history=raw.weight_history,
        labs=raw.labs,
        overall_compliance_score=overall_compliance_score,
        adherence_declining=adherence_declining,
        risk_assessment=risk_assessment,
    )


def _ingest_dataset(dataset: PatientDataset, reference_date: date | None = None) -> int:
    ref_date = reference_date or date.today()
    for raw in dataset.patients:
        PATIENT_STORE[raw.id] = _enrich_patient(raw, ref_date)
    return len(dataset.patients)


def _load_default_dataset() -> None:
    with open(DEFAULT_DATASET_PATH, encoding="utf-8") as f:
        raw_json = json.load(f)
    dataset = PatientDataset.model_validate(raw_json)
    _ingest_dataset(dataset)


@app.post("/ingest")
def ingest(dataset: PatientDataset | None = None) -> dict:
    """Load patient data into the in-memory store. Body is optional —
    omit it to (re)load the bundled data/mock_patients.json."""
    if dataset is None:
        with open(DEFAULT_DATASET_PATH, encoding="utf-8") as f:
            raw_json = json.load(f)
        dataset = PatientDataset.model_validate(raw_json)
    count = _ingest_dataset(dataset)
    return {"status": "ok", "patients_loaded": count}


@app.get("/patients")
def list_patients() -> list[PatientMedicationState]:
    return list(PATIENT_STORE.values())


@app.get("/patients/{patient_id}")
def get_patient(patient_id: str) -> PatientMedicationState:
    patient = PATIENT_STORE.get(patient_id)
    if patient is None:
        raise HTTPException(status_code=404, detail=f"Patient '{patient_id}' not found")
    return patient


@app.get("/dashboard")
def dashboard() -> DashboardSummary:
    patients = list(PATIENT_STORE.values())
    summaries = [
        PatientSummary(
            patient_id=p.patient_id,
            name=p.name,
            age=p.age,
            conditions=p.conditions,
            cluster_flag=p.risk_assessment.cluster_flag,
            signal_count=p.risk_assessment.signal_count,
            urgency_score=p.risk_assessment.urgency_score,
            overall_compliance_score=p.overall_compliance_score,
            top_rationale=p.risk_assessment.rationale[0] if p.risk_assessment.rationale else None,
        )
        for p in patients
    ]
    summaries.sort(key=lambda s: (-s.urgency_score, s.name))
    needing_attention = sum(1 for s in summaries if s.cluster_flag)

    return DashboardSummary(
        total_patients=len(summaries),
        patients_needing_attention=needing_attention,
        summary_message=f"{needing_attention} of {len(summaries)} patients need attention this week",
        patients=summaries,
    )
