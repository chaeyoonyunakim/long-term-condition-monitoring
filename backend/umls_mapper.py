"""Drug name -> SNOMED/BNF/indication mapping.

Loads a pre-built JSON table (data/umls_medication_map.json) rather than
calling a live UMLS API, so lookups are instant and the demo has no
external dependency. This is the single source of truth for what a
medication *means* clinically — patient records only carry the drug
name and refill cadence.
"""

from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
UMLS_MAP_PATH = DATA_DIR / "umls_medication_map.json"


@lru_cache(maxsize=1)
def _load_map() -> dict[str, dict]:
    with open(UMLS_MAP_PATH, encoding="utf-8") as f:
        return json.load(f)


def get_medication_info(drug_name: str) -> dict:
    """Look up a drug by name (case-insensitive). Falls back to an
    'unmapped' record instead of raising, so an unrecognized drug in a
    patient file never breaks ingestion."""
    table = _load_map()
    entry = table.get(drug_name.strip().lower())
    if entry is None:
        return {
            "generic_name": drug_name,
            "bnf_code": None,
            "snomed": None,
            "drug_class": None,
            "indication": "Unmapped — not found in UMLS reference table",
            "cvd_relevant": False,
            "special_notes": None,
        }
    return entry
