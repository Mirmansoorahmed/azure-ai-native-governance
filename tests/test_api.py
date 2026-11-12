import json

from fastapi.testclient import TestClient

from app.main import app
from app.seed import seed


def client():
    seed()
    return TestClient(app)


def test_health():
    c = client()
    r = c.get("/health")
    assert r.status_code == 200 and r.json()["simulated"] is True


def test_dashboard_summary_counts():
    c = client()
    s = c.get("/dashboard/summary").json()
    assert s["vms_total"] == 6
    assert s["storage_total"] == 8
    assert s["keyvaults_total"] == 3
    assert s["ai_total"] == 4
    assert s["users_total"] == 20
    assert s["controls_total"] == 28
    assert s["risks_total"] == 12


def test_estate_endpoints():
    c = client()
    assert len(c.get("/vms").json()) == 6
    assert len(c.get("/storage").json()) == 8
    assert len(c.get("/keyvaults").json()) == 3
    assert len(c.get("/ai").json()) == 4
    assert len(c.get("/policies").json()) == 6
    assert c.get("/defender").json()["secure_score_pct"] == 62


def test_native_capabilities():
    c = client()
    native = c.get("/native").json()
    assert len(native) == 10
    for n in native:
        assert n["can"] and n["cannot"], n["service"]
        # every native service must admit it cannot decide a tool call
        assert any("tool call" in x.lower().replace("-", " ") for x in n["cannot"]), n["service"]


def test_comparison_and_gap():
    c = client()
    comp = c.get("/comparison").json()
    assert len(comp) == 10
    row = next(r for r in comp if "specific tool call" in r["question"])
    assert "NO" in row["azure_native"] and "NO" in row["purview_agent365"]
    assert "YES" in row["gateway"]
    gap = c.get("/gap").json()
    assert gap["native_decision_for_tool_call"] is None
    assert "OPA" in gap["gateway_decision_for_tool_call"]
    assert len(gap["examples"]) == 5


def test_run_checks_and_evidence():
    c = client()
    run = c.post("/tests/run").json()
    assert run["checks_run"] == 16
    assert sum(run["counts"].values()) == 16
    assert run["counts"]["Fail"] >= 3
    v = c.get("/evidence/verify").json()
    assert v["valid"] is True and v["checked"] == 16
    csv_text = c.get("/evidence/export.csv").text
    assert "control_code" in csv_text and "A-01" in csv_text


def test_dashboard_html():
    c = client()
    r = c.get("/")
    assert r.status_code == 200 and "Azure AI Native Governance" in r.text
    assert "SIMULATED" in r.text
