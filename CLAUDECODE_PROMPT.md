# HEALTH BRIDGE: CLAUDE CODE BUILD PROMPT
## eMed x OpenAI Hackathon (17–18 July 2026) — Solo Implementation

---

## CONTEXT

**Problem:** UK's 90+ population grows 20% by 2034; they're on 20+ years of lifelong CVD medications. Community pharmacies have no real-time visibility into medication adherence drift. Silent non-adherence (12–15% refill gap) goes undetected until hospital crisis.

**Solution:** Health Bridge is an ambient adherence monitoring + CVD risk cluster detection system. Flags medication non-adherence and cardiovascular risk escalation *before* crisis.

**See:** 
- `health_bridge_problem_context.md` (problem framing, data sources, regulatory context)
- `health_bridge_stats_one_pager.md` (quantified scale: 180K–240K missed CVD refills/year UK-wide)

**Hackathon Challenge:** eMed | "At-home chronic condition management powered by AI" | AI Engine, London, 17–18 July 2026

---

## TECH STACK

- **Backend:** FastAPI + Pydantic v2 (lightweight, no heavy dependencies)
- **LLM:** OpenAI GPT-4o (hackathon credits available) for risk narrative generation + UMLS grounding
- **Medical Grounding:** UMLS/LOINC/SNOMED CT (pre-loaded as JSON, not live API)
- **Adherence Logic:** Local heuristics (refill gap detection, BP trend, weight change, cluster detection) — *no LLM for flagging* (to avoid latency, cost, false positives)
- **Frontend:** React + Vercel (minimal, clinician dashboard only)
- **Deployment:** Render (backend) + Vercel (frontend)
- **Audit Log:** Immutable in-memory log (hash-based tracking for demo)

---

## MVP SCOPE (18-Hour Build)

### Phase 1: Data Ingestion & UMLS Mapping (Hours 1–4)
- Ingest mock patient dataset (5–10 patients with refill history, BP readings, weight, labs)
- Build UMLS/SNOMED medication mapper: map drug names to indication (e.g., "Atorvastatin" → statin → CVD → "kidney protection in CKD")
- Parse refill dates, calculate refill gaps (>30 days = RED FLAG)
- Output: Structured patient medication state object

### Phase 2: Adherence Inference Engine (Hours 4–8)
- **Refill gap detector:** Flag if last dispensing was >30 days ago
- **Compliance score:** (Expected refills in period) / (Actual refills) × 100
- **Trend detector:** If compliance declining >10% month-over-month, escalate
- **Output:** Adherence flag object per patient + trend slope

### Phase 3: CVD Risk Cluster Detector (Hours 8–12)
- Aggregate 3+ signals simultaneously:
  - Signal 1: Medication non-adherence (compliance <70% or refill gap >30 days)
  - Signal 2: BP elevation (systolic >140 or rising trend)
  - Signal 3: Weight gain (>3kg in 3 months)
  - Signal 4: Lipid drift (triglycerides >250 or LDL rising)
  - Signal 5: Monitoring lapse (no BP readings >30 days)
- 3+ signals = **HIGH CVD RISK CLUSTER** → urgent intervention
- Output: Risk cluster flag + urgency score (1–10)

### Phase 4: FastAPI Routes + Clinician Dashboard (Hours 12–16)
- `POST /ingest` — Load patient dataset
- `GET /patients` — List all patients with risk flags
- `GET /patients/{id}` — Detailed patient view: medication history, adherence, risk signals, audit trail
- `GET /dashboard` — Summary: "8 of 200 patients need attention this week"
- Simple React frontend: patient list + click-through detail view

### Phase 5: Demo Narrative + Audit Logging (Hours 16–18)
- Generate 5 demo patients (2 stable, 3 red flags) with synthetic but realistic patterns
- Implement immutable audit log: every flag decision logged with timestamp, rationale, no override capability
- Polish dashboard for live demo

---

## MOCK DATA SCHEMA (5 Patients)

```json
{
  "patients": [
    {
      "id": "P001",
      "name": "Ahmed",
      "age": 68,
      "conditions": ["Type 2 Diabetes", "Hypertension", "CKD Stage 3b"],
      "medications": [
        {
          "name": "Atorvastatin",
          "bnf_code": "2.12",
          "snomed": "55396009",
          "indication": "CVD prevention",
          "expected_refill_days": 30
        }
      ],
      "refill_history": [
        {"date": "2026-07-01", "drug": "Atorvastatin", "quantity": 30},
        {"date": "2026-06-01", "drug": "Atorvastatin", "quantity": 30},
        {"date": "2026-05-03", "drug": "Atorvastatin", "quantity": 30}
      ],
      "bp_readings": [
        {"date": "2026-07-15", "systolic": 135, "diastolic": 82},
        {"date": "2026-07-08", "systolic": 133, "diastolic": 80}
      ],
      "weight_history": [
        {"date": "2026-07-15", "kg": 82},
        {"date": "2026-05-15", "kg": 81}
      ],
      "labs": [
        {"date": "2026-06-15", "test": "triglycerides", "value": 145, "unit": "mg/dL"}
      ]
    },
    {
      "id": "P002",
      "name": "Priya",
      "age": 72,
      "conditions": ["CVD post-MI", "Hypertension", "Type 2 Diabetes"],
      "medications": [
        {"name": "Atorvastatin", "bnf_code": "2.12", "snomed": "55396009", "indication": "CVD prevention", "expected_refill_days": 30},
        {"name": "Lisinopril", "bnf_code": "2.5.1", "snomed": "36626009", "indication": "ACE inhibitor for cardiac protection", "expected_refill_days": 30}
      ],
      "refill_history": [
        {"date": "2026-05-20", "drug": "Atorvastatin", "quantity": 30},
        {"date": "2026-06-15", "drug": "Atorvastatin", "quantity": 30},
        {"date": "2026-04-10", "drug": "Lisinopril", "quantity": 30}
      ],
      "bp_readings": [
        {"date": "2026-07-15", "systolic": 151, "diastolic": 88},
        {"date": "2026-07-08", "systolic": 148, "diastolic": 86},
        {"date": "2026-06-30", "systolic": 144, "diastolic": 84}
      ],
      "weight_history": [
        {"date": "2026-07-15", "kg": 89},
        {"date": "2026-05-15", "kg": 83}
      ],
      "labs": [
        {"date": "2026-06-15", "test": "triglycerides", "value": 275, "unit": "mg/dL"},
        {"date": "2026-05-15", "test": "LDL", "value": 118, "unit": "mg/dL"}
      ]
    }
  ]
}
```

---

## DELIVERABLES (END OF 18 HOURS)

### Code (GitHub)
- `backend/app.py` — FastAPI server with adherence + cluster detection logic
- `backend/models.py` — Pydantic v2 data schemas
- `backend/adherence_engine.py` — Refill gap, compliance, trend detection
- `backend/cluster_detector.py` — CVD risk cluster aggregation logic
- `backend/umls_mapper.py` — Drug → indication mapping (JSON-based)
- `backend/audit_log.py` — Immutable audit trail
- `frontend/` — React dashboard (minimal, clinician-focused)
- `data/mock_patients.json` — 5 demo patients with realistic patterns
- `requirements.txt` — Dependencies (FastAPI, Pydantic, uvicorn, + minimal extras)
- `README.md` — Setup instructions, API docs, demo narrative

### Demo Ready
- Live clinician dashboard showing 5 patients
- Click patient → see medication history, adherence graph, risk flags, audit trail
- "Marcus: RED FLAG — ACE inhibitor refill gap 42 days, no BP readings 6 weeks, kidney protection at risk"
- "Priya: RED FLAG — Statin gap 38 days + BP 138→144→151 + Weight +6kg + Trig 275 = HIGH CVD RISK CLUSTER"

### Narrative
- One-slide problem statement (population aging + medication adherence gap)
- Five-minute walkthrough: demo patients, risk detection, pharmacy intervention model
- Judges see: real NHS problem + data-driven solution + implementable MVP

---

## STARTING PROMPT (For Claude Code)

> "Build Health Bridge MVP: ambient medication adherence monitoring + CVD risk cluster detection for eMed hackathon. 
>
> Start with Phase 1 (data ingestion + UMLS mapper): 
> - Load mock_patients.json (5 patients with refill history, BP, weight, labs)
> - Build UMLS medication mapper (Pydantic model linking drug name → SNOMED code → indication)
> - Parse refill dates; calculate refill gaps
> - Output structured patient medication state
>
> Tech stack: FastAPI + Pydantic v2, minimal dependencies.
> Keep code modular: adherence engine separate from cluster detector separate from audit log.
> No external UMLS API calls—use pre-loaded JSON mapping.
>
> First milestone: POST /ingest loads patients, GET /patients/{id} returns medication state + refill gaps."

---

## CHECKPOINT: After Phase 1 (Hour 4)

Before moving to Phase 2, verify:
- ✅ `mock_patients.json` loads without errors
- ✅ UMLS mapper correctly identifies "Atorvastatin" → CVD → "kidney protection" 
- ✅ Refill gaps calculated (e.g., Priya: 38-day gap on Atorvastatin, 52-day gap on Lisinopril)
- ✅ Pydantic models compile
- ✅ FastAPI `/patients` and `/patients/{id}` endpoints return structured data

If any fail, pause Phase 2 until resolved.

---

## SUCCESS CRITERIA (18-Hour Demo)

- [ ] FastAPI server runs locally without errors
- [ ] Dashboard loads 5 demo patients
- [ ] Red-flag patients (Marcus, Priya) correctly identified
- [ ] Audit log shows rationale for every flag (immutable, timestamped)
- [ ] Judges can click through patient detail, see medication history + risk signals
- [ ] Problem narrative ties to data: "180K–240K missed CVD refills annually; this system catches them before hospital"
- [ ] Code is clean, modular, deployable (Render + Vercel compatible)

---

## RUNNING LOCALLY (After Build)

```bash
cd backend
pip install -r requirements.txt
python -m uvicorn app:app --reload

# In another terminal:
cd frontend
npm install
npm start

# Visit http://localhost:3000 → see dashboard
```

---

## GO BUILD 🚀

This is a 18-hour solo sprint. Modular, achievable, data-driven. You've got the problem framed; now make the solution tangible.

**First Claude Code call:** "Start with Phase 1: data ingestion + UMLS mapper. Load mock_patients.json, build medication state model, calculate refill gaps."

Good luck! 🎯
