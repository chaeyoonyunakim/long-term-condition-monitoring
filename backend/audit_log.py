"""Immutable audit trail for flag decisions.

Every medication-gap flag and CVD risk cluster assessment gets appended
here with its rationale. The module exposes no update or delete —
append and read only — and each entry's hash chains to the previous
entry's hash (genesis-block style), so any post-hoc tampering with the
in-memory list is detectable via verify_chain_integrity().
"""

from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone

from backend.models import AuditLogEntry

GENESIS_HASH = "0" * 64

_LOG: list[AuditLogEntry] = []


def _compute_hash(prev_hash: str, timestamp: str, patient_id: str, event_type: str, summary: str, rationale: list[str]) -> str:
    payload = json.dumps(
        {
            "prev_hash": prev_hash,
            "timestamp": timestamp,
            "patient_id": patient_id,
            "event_type": event_type,
            "summary": summary,
            "rationale": rationale,
        },
        sort_keys=True,
    )
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def record_event(patient_id: str, event_type: str, summary: str, rationale: list[str]) -> AuditLogEntry:
    """Append a new, immutable entry. This is the only way to add to the
    log — there is deliberately no corresponding update/delete function."""
    prev_hash = _LOG[-1].entry_hash if _LOG else GENESIS_HASH
    timestamp = datetime.now(timezone.utc)
    timestamp_iso = timestamp.isoformat()
    entry_hash = _compute_hash(prev_hash, timestamp_iso, patient_id, event_type, summary, rationale)

    entry = AuditLogEntry(
        sequence=len(_LOG),
        entry_hash=entry_hash,
        prev_hash=prev_hash,
        timestamp=timestamp,
        patient_id=patient_id,
        event_type=event_type,
        summary=summary,
        rationale=rationale,
    )
    _LOG.append(entry)
    return entry


def get_full_log() -> list[AuditLogEntry]:
    return list(_LOG)


def get_patient_log(patient_id: str) -> list[AuditLogEntry]:
    return [e for e in _LOG if e.patient_id == patient_id]


def verify_chain_integrity() -> bool:
    """Recomputes every hash from its stored fields and checks the chain
    links. Returns False if any entry was altered or reordered."""
    prev_hash = GENESIS_HASH
    for entry in _LOG:
        expected = _compute_hash(
            prev_hash, entry.timestamp.isoformat(), entry.patient_id, entry.event_type, entry.summary, entry.rationale
        )
        if entry.prev_hash != prev_hash or entry.entry_hash != expected:
            return False
        prev_hash = entry.entry_hash
    return True
