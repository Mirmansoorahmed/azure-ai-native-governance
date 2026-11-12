from fastapi.testclient import TestClient

from app.main import app
from app.seed import seed


def client():
    seed()
    return TestClient(app)


def test_gateway_allow_and_native_none():
    c = client()
    r = c.post("/agent/action", json={"agent_id": "ops-agent", "tool": "azure.storage.read", "arguments": {}}).json()
    assert r["decision"] == "allow"
    assert r["native_decision"] is None
    assert "No Azure native" in r["native_reason"]


def test_gateway_needs_approval_then_allow():
    c = client()
    r = c.post("/agent/action", json={"agent_id": "ops-agent", "tool": "azure.vm.start", "arguments": {}}).json()
    assert r["decision"] == "needs_approval"
    assert r["approval_id"]
    d = c.post(f"/approvals/{r['approval_id']}/decide", json={"decision": "approved"}).json()
    assert d["status"] == "approved"
    r2 = c.post("/agent/action", json={"agent_id": "ops-agent", "tool": "azure.vm.start", "arguments": {}}).json()
    assert r2["decision"] == "allow"


def test_gateway_denies_blocked_and_prohibited():
    c = client()
    r = c.post("/agent/action", json={"agent_id": "shadow-notes", "tool": "azure.keyvault.get_secret", "arguments": {}}).json()
    assert r["decision"] == "deny"
    r = c.post("/agent/action", json={"agent_id": "social-scoring-pilot", "tool": "crm.score_customer", "arguments": {}}).json()
    assert r["decision"] == "deny"
    r = c.post("/agent/action", json={"agent_id": "sales-assistant", "tool": "crm.delete_account", "arguments": {}}).json()
    assert r["decision"] == "deny"


def test_approval_decide_validation():
    c = client()
    r = c.post("/agent/action", json={"agent_id": "ops-agent", "tool": "azure.vm.start", "arguments": {}}).json()
    bad = c.post(f"/approvals/{r['approval_id']}/decide", json={"decision": "maybe"})
    assert bad.status_code == 400
    missing = c.post("/approvals/apr_doesnotexist/decide", json={"decision": "approved"})
    assert missing.status_code == 404


def test_classification_endpoint():
    c = client()
    r = c.post("/classification/classify", json={"purpose": "Score customers", "decision_about_people": True}).json()
    assert r["tier"] == "prohibited"
