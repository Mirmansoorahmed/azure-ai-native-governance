import json

from app.database import SessionLocal
from app.evidence import compute_hash, verify_chain
from app.models import Evidence
from app.seed import seed


def test_hash_chain_valid_and_tamper_breaks():
    seed()
    db = SessionLocal()
    try:
        rows = []
        prev = "GENESIS"
        for i, code in enumerate(["A-01", "A-02", "A-03"]):
            ts = "2026-11-10T12:00:00+00:00"
            details = {"run_at": ts, "i": i}
            h = compute_hash(prev, code, "t", "Pass", ts, details)
            rows.append(Evidence(control_code=code, test_name="t", result="Pass", sha256=h, details=json.dumps(details)))
            prev = h
        assert verify_chain(rows)["valid"] is True
        rows[1].sha256 = "0" * 64
        assert verify_chain(rows)["valid"] is False
    finally:
        db.close()


def test_run_creates_evidence_and_issues():
    from fastapi.testclient import TestClient
    from app.main import app
    seed()
    c = TestClient(app)
    run = c.post("/tests/run").json()
    assert run["counts"]["Fail"] >= 3
    issues = c.get("/issues").json()
    assert len(issues) >= 3
    assert all(i["status"] == "Open" for i in issues)
