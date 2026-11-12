"""Hash-chained evidence. Every test run creates one Evidence row; its
SHA-256 is computed over previous hash + control + test + result +
timestamp + details, so tampering with any row breaks the chain.
A clean scan is never a 'Pass' on its own: a test only becomes Pass
when the check actually ran AND produced evidence."""
import hashlib
import json
from datetime import datetime, timezone


def compute_hash(prev_hash, control_code, test_name, result, timestamp, details):
    payload = "|".join([prev_hash, control_code, test_name, result, timestamp,
                        json.dumps(details, sort_keys=True)])
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def verify_chain(rows):
    prev = "GENESIS"
    for row in rows:
        details = json.loads(row.details or "{}")
        ts = details.get("run_at")
        if ts is None:
            ts = row.created_at.isoformat() if isinstance(row.created_at, datetime) else str(row.created_at)
        expected = compute_hash(prev, row.control_code, row.test_name, row.result, ts, details)
        if expected != row.sha256:
            return {"valid": False, "broken_at_id": row.id, "checked": len(rows)}
        prev = row.sha256
    return {"valid": True, "checked": len(rows), "head": prev}


def utc_now_iso():
    return datetime.now(timezone.utc).isoformat()
