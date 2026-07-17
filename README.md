# Health Bridge

Ambient medication adherence monitoring + CVD risk cluster detection for community pharmacy.

Built for the eMed × OpenAI Hackathon, 17–18 July 2026 — challenge: *"At-home chronic condition management powered by AI."*

## Problem

The UK's 90+ population grows 20% by 2034; many are on 20+ years of lifelong CVD medications. Community pharmacies have no real-time visibility into adherence drift. Silent non-adherence (a 12–15% refill gap) goes undetected until a hospital crisis — an estimated 180,000–240,000 missed CVD refills per year UK-wide. See `docs/health_bridge_problem_context.md` and `docs/health_bridge_stats_one_pager.md` for the full framing.

Health Bridge flags non-adherence and cardiovascular risk escalation *before* crisis, using local heuristics (no LLM in the flagging path, to avoid latency, cost, and false positives) grounded in UMLS/SNOMED medication data.

## How it works

1. **Ingestion + UMLS mapping** (`backend/umls_mapper.py`) — drug names are resolved to SNOMED/BNF codes, drug class, and clinical indication from a pre-loaded JSON reference table (no live UMLS API call).
2. **Adherence inference** (`backend/adherence_engine.py`) — per medication: refill gap (>30 days = flagged), a compliance score (actual vs. expected refills), and a trend detector comparing the last 60 days of compliance against the prior 60 days (>10-point decline = flagged).
3. **CVD risk cluster detection** (`backend/cluster_detector.py`) — aggregates 5 independent signals (medication non-adherence, BP elevation, weight gain, lipid drift, monitoring lapse). 3+ concurrent signals = **HIGH CVD RISK CLUSTER**, with a 0–10 urgency score.
4. **Audit log** (`backend/audit_log.py`) — every flag decision is appended, with rationale, to an in-memory, hash-chained log. The module exposes no update/delete, and `verify_chain_integrity()` recomputes every hash to detect tampering.
5. **API + dashboard** (`backend/app.py`, `frontend/`) — FastAPI backend, a minimal React clinician dashboard on top.

## Demo patients

5 mock patients (`data/mock_patients.json`), evaluated against "today" = 2026-07-17:

| Patient | Status | Signals | Urgency | Why |
|---|---|---|---|---|
| **Priya** (72) | 🔴 HIGH CVD RISK CLUSTER | 4/5 | 10/10 | Statin gap 38 days + ACE inhibitor gap 52 days, BP rising 130→151 mmHg, weight +6kg in 3 months, triglycerides 275 mg/dL |
| **Marcus** (75) | 🔴 HIGH CVD RISK CLUSTER | 3/5 | 7/10 | ACE inhibitor refill gap 42 days, last BP reading 142 mmHg but none since — 6-week monitoring lapse, kidney protection at risk |
| **David** (80) | 🔴 HIGH CVD RISK CLUSTER | 3/5 | 6/10 | Statin compliance 54% (sporadic refills, no single gap >30 days), weight +4kg in 3 months, LDL rising 100→148 mg/dL — a cluster the raw refill-gap check alone would miss |
| **Ahmed** (68) | 🟢 Stable | 0/5 | 0/10 | Regular refills, stable BP/weight/labs |
| **Eleanor** (70) | 🟢 Stable | 0/5 | 0/10 | Regular refills, stable BP/weight |

## Running locally

**Backend:**

```bash
python -m venv .venv
source .venv/Scripts/activate   # Windows Git Bash; use .venv/bin/activate on macOS/Linux
pip install -r requirements.txt
python -m uvicorn backend.app:app --reload
```

Server runs at `http://localhost:8000`; interactive API docs at `http://localhost:8000/docs`. Patient data auto-loads from `data/mock_patients.json` on startup.

**Frontend:**

```bash
cd frontend
npm install
npm run dev
```

Visit `http://localhost:5173`. Set `VITE_API_BASE_URL` (defaults to `http://localhost:8000`) if the backend runs elsewhere.

## API

| Method | Path | Description |
|---|---|---|
| `POST` | `/ingest` | (Re)loads patient data into the in-memory store. Omit the body to reload `data/mock_patients.json`. |
| `GET` | `/patients` | All patients with full medication state, adherence, and risk assessment. |
| `GET` | `/patients/{id}` | Single patient detail. |
| `GET` | `/dashboard` | Summary (`"N of M patients need attention this week"`) plus patients sorted by urgency. |
| `GET` | `/audit-log` | Full hash-chained audit trail, with `chain_intact` integrity check. |
| `GET` | `/patients/{id}/audit-log` | Audit trail for one patient. |

## Deployment

- Backend: Render (FastAPI + uvicorn, `requirements.txt` has all dependencies).
- Frontend: Vercel (`frontend/`, set `VITE_API_BASE_URL` to the deployed backend URL as a build env var).

## Project layout

```
backend/
  app.py               FastAPI routes, in-memory patient store
  models.py             Pydantic v2 schemas
  umls_mapper.py         Drug -> SNOMED/BNF/indication lookup
  adherence_engine.py     Refill gap, compliance score, trend detection
  cluster_detector.py      5-signal CVD risk cluster aggregation
  audit_log.py              Immutable, hash-chained flag decision log
data/
  mock_patients.json      5 demo patients
  umls_medication_map.json Drug reference table
frontend/                React (Vite) clinician dashboard
docs/                    Problem framing and stats one-pager
```
