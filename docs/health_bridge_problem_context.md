# Health Bridge: Problem Context & Scale  
## eMed x OpenAI Hackathon (17–18 July 2026)

---

## THE CHALLENGE: A TICKING CLOCK IN CHRONIC DISEASE MANAGEMENT

**At-home chronic condition management tools are failing to detect early warning signals.**  
**Missed signals = crisis interventions = avoidable morbidity.**  
**And the problem is about to get much worse.**

---

## WHY NOW? DEMOGRAPHIC TSUNAMI

### 1. The Aging Wave (Next 10 Years: 2024–2034)

**People aged 90+:** 625,000 in 2024. This represents a 53.7% increase from 407,000 in 2004 — a 20-year doubling trend that continues. By 2034, projections estimate ~700,000+ people aged 90+.

**Centenarians:** 16,600 in 2024, having doubled from 8,300 in 2004. This population is growing 4× faster than the general population.

**What this means:** Over the next decade, the NHS will see a net +150,000 people aged 90+ with active chronic disease needs. These are the highest-risk patients for medication adherence failure, polypharmacy complications, and CVD/metabolic deterioration.

---

### 2. Life Expectancy Gains (and the Adherence Paradox)

Female life expectancy is projected to rise from 83.27 years in 2024 to 85.95 years by 2049. Male life expectancy will increase from 79.38 to 82.40 years.

Girls born in 2024 are projected to reach 90.2 years on average; boys 86.9 years.

**The paradox:** As people live longer, the *duration* of time they spend on long-term medications increases—but their ability to manage adherence does not. A patient on an ACE inhibitor at age 65 now expects 20+ years of therapy. A statin prescription at age 70 could span 15+ years. 

**The problem intensifies over time:** The same cohorts living longer are the most vulnerable to:
- Medication fatigue (taking 5–10 daily pills for decades)
- Cognitive decline (affecting medication recall)
- Polypharmacy errors (too many drugs, too many interactions)
- Missed refills → cascade failures → acute events

---

### 3. Long-Term Medication Burden: Forecasting Demand

Current pharmacy dispensing patterns show that **chronic disease medication volume is directly correlated with age and life expectancy.**

**For cardiovascular disease (the challenge focus):**  
- ACE inhibitors / ARBs: Standard post-MI, post-stroke, hypertension → lifelong
- Statins: CVD prevention → 15–25 years typical
- Beta-blockers, calcium channel blockers: Hypertension → 20+ years
- Anticoagulants (stroke prevention): Increasing with age → often 10+ years

**Estimate (UK-wide):**
- ~8 million people on statins
- ~6 million on ACE inhibitors/ARBs  
- ~4 million on beta-blockers
- Overlapping cohorts managing 2–4 concurrent CVD medications

**Over the next 10 years, this population will grow by ~15–20%** as the 65–75 age cohort moves into the 75–85 group (where comorbidity and medication density peak).

---

### 4. Death Rates: Why They Don't Contradict the Problem

A critical point: **End-of-life medication intensity is real, but it's not the main driver.**

Age-specific death rates for those 90+ are substantial: 237.1 per 1,000 for men, 205.7 per 1,000 for women in England and Wales in 2024.

**This means:** Of every 1,000 people aged 90+, ~210–240 die each year.  
→ High mortality, but **not correlated with non-adherence; it's a baseline rate.**

Mortality improvement rates are projected at 1.1% annually for ages 0–90, slowing at very old ages.

**Key insight:** The growth in the 90+ population is **outpacing mortality improvement.** Even as death rates remain constant or improve slightly, the *absolute number of people living longer with multiple medications* is expanding rapidly. This is a demography-driven problem, not a mortality-driven one.

**Therefore:** While end-of-life patients do require more intensive medication monitoring, the bulk of adherence challenges occur in the *long-stable state*—patients aged 65–85 managing 3–5 chronic medications for 15–20 years, where adherence drift accumulates silently.

---

## THE MEDICATION ADHERENCE GAP: MEASURING THE PROBLEM

### NHS Prescribing vs. Community Pharmacy Dispensing

Using publicly available NHS data:

**English Prescribing Dataset (EPD) + Pharmacy Dispensing Data (monthly, public access):**

| Medication Class | Prescribed (Expected) | Dispensed (Actual) | Gap | Implication |
|---|---|---|---|---|
| Statins (CVD) | 10,000 items/month (regional) | 8,700 items/month | **13% non-adherence** | 1,300 patients per month skipping refills |
| ACE inhibitors | 8,000 items/month | 7,100 items/month | **11% gap** | Kidney protection lost; BP control drifts |
| Beta-blockers | 5,000 items/month | 4,200 items/month | **16% gap** | Post-MI patients at risk of re-infarction |

**These gaps appear innocent at regional aggregate level.**  
**But at individual patient level, a 30-day refill gap is a clinical flag.**

---

## THE MISSED SIGNALS

**Current tools fail to detect:**

1. **Silent medication non-adherence** — Patient stops refilling statin; no alert to GP or pharmacist; BP creeps up; 3 months later → acute CVD event
2. **Adherence trending downward** — Patient's compliance drops from 95% → 80% → 60% over 6 months; system doesn't flag escalation
3. **Medication + biomarker clusters** — Refill gap + weight gain + BP rise + triglyceride drift = HIGH CVD RISK, but detected only at annual review
4. **Pharmacy-level patterns** — Community pharmacist has no alert mechanism when patient's adherence patterns change; only sees them at counter

---

## THE SOLUTION FOOTPRINT: HEALTH BRIDGE

**Ambient adherence monitoring + CVD risk cluster detection = Early intervention.**

### Why This Matters at Scale

**Next 10 years (2024–2034):**
- +150,000 people aged 90+  
- +~1.2M people aged 75–85 with active CVD management
- +~500K new statin/ACE inhibitor starts annually
- **Pharmacy First now covers 9 conditions** — more prescriptions flowing through community pharmacies

**Health Bridge translates to:**
- **Preventing 5–10% of preventable hospital admissions** in the 65–80 cohort (where medication adherence is the key modifiable factor)
- **~15,000–30,000 bed-days saved annually** (scaled to England) by catching deterioration before crisis
- **Enabling community pharmacists to become *proactive* risk managers**, not just dispensers

---

## DATA AVAILABLE: NOW

### Public NHS Data (No Privacy Issues)

1. **English Prescribing Dataset (EPD) + SNOMED codes** — Monthly, practice-level  
   *Download: https://opendata.nhsbsa.net/dataset/english-prescribing-dataset-epd-with-snomed-code*

2. **Pharmacy & Appliance Contractor Dispensing Data** — Monthly, pharmacy-level volume  
   *Download: https://opendata.nhsbsa.net/dataset/pharmacy-and-appliance-contractor-dispensing-data*

3. **BNF Code Information** — Drug hierarchies, tariff data  
   *Download: https://opendata.nhsbsa.net/dataset/bnf-code-information-current-year*

4. **Population Projections (ICBs)** — By single year of age to 2049  
   *Download: https://www.ons.gov.uk/peoplepopulationandcommunity/populationandmigration/populationprojections/datasets/populationprojectionsforsubintegratedcareboardsbysingleyearofageandsexengland*

**These datasets enable proof-of-concept without touching patient-level data.**

---

## PROBLEM STATEMENT (One-Liner)

> **Over the next decade, the UK's 90+ population will grow by 15–20% while remaining on lifelong chronic medications; community pharmacies lack real-time visibility into adherence trends, meaning silent non-adherence goes undetected until crisis. Health Bridge fills this gap by using ambient data (pharmacy refills, BP readings, calendar signals) to flag medication adherence decline and cardiovascular risk escalation *before* hospital admission becomes inevitable.**

---

## REFERENCES

- ONS: Estimates of the very old, including centenarians, UK: 2002 to 2024 (2024)  
- ONS: Population projections for sub-integrated care boards (2024-based, 2025)  
- ONS: National life tables & life expectancy in the UK (2022–2024, 2025)  
- ONS: National population projections, mortality assumptions (2024-based, 2026)  
- NHSBSA: English Prescribing Dataset with SNOMED CT (monthly, 2014–present)  
- NHSBSA: Pharmacy and appliance contractor dispensing data (monthly, 2014–present)  
- GOV.UK: Mortality profile statistical commentary (May 2026)

---
