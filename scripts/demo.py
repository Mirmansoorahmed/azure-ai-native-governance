"""End-to-end demo (uses TestClient, no server needed).

Run:  python -m scripts.demo   (from the project root, venv active)
"""
from fastapi.testclient import TestClient

from app.main import app
from app.seed import seed


def main():
    seed()
    client = TestClient(app)
    print("== Azure AI Native Governance — demo (SIMULATED tenant: Nordlicht GmbH) ==")
    r = client.get("/dashboard/summary").json()
    print(f"resources={r['resources_total']} vms={r['vms_total']} storage={r['storage_total']} "
          f"keyvaults={r['keyvaults_total']} ai={r['ai_total']} users={r['users_total']} "
          f"defender_secure_score={r['defender_secure_score_pct']}%")
    print(f"storage_public={r['storage_public']} secrets_expired={r['secrets_expired']} "
          f"ai_no_filter={r['ai_no_filter']} ai_outside_eu={r['ai_outside_eu']} users_no_mfa={r['users_without_mfa']}")
    print("\n-- native capabilities: what Azure CAN and CANNOT decide --")
    for n in client.get("/native").json():
        print(f"  {n['service']}: CAN {len(n['can'])} things, CANNOT {len(n['cannot'])} things "
              f"(e.g. cannot: {n['cannot'][0]})")
    print("\n-- governance checks --")
    run = client.post("/tests/run").json()
    print(f"checks run: {run['checks_run']} — {run['counts']}")
    for c in run["checks"]:
        print(f"  {c['control_code']} {c['test_name']:38s} {c['result']}")
    print("\n-- evidence chain --")
    print("evidence chain valid:", client.get("/evidence/verify").json())
    print("\n-- agent tool calls: native decision vs gateway decision --")
    for agent, tool, args in [
        ("ops-agent", "azure.vm.start", {}),
        ("finance-assistant", "azure.storage.read", {}),
        ("ops-agent", "azure.keyvault.get_secret", {"secret": "prod-db-password"}),
        ("shadow-notes", "azure.keyvault.get_secret", {"secret": "prod-db-password"}),
        ("social-scoring-pilot", "crm.score_customer", {}),
        ("sales-assistant", "crm.delete_account", {"account": "ACME-001"}),
    ]:
        d = client.post("/agent/action", json={"agent_id": agent, "tool": tool, "arguments": args}).json()
        print(f"  {agent:22s} {tool:28s} -> gateway={d['decision']:15s} ({d['engine']}) native={d['native_decision']} — {d['reason'][:90]}")
    print("\n-- EU AI Act classification --")
    for purpose in ["Score customers across unrelated data to decide treatment",
                    "Screen job applicants and rank them for hiring"]:
        print(" ", purpose[:60], "->", client.post("/classification/classify",
              json={"purpose": purpose, "decision_about_people": True}).json()["tier"])
    print("\n-- approvals --")
    pending = [a for a in client.get("/approvals").json() if a["status"] == "pending"]
    print("  pending approvals:", len(pending))
    if pending:
        first = pending[0]
        print("  deciding first approval as approved:",
              client.post(f"/approvals/{first['approval_id']}/decide", json={"decision": "approved"}).json())
        retry = client.post("/agent/action", json={"agent_id": first["agent_id"], "tool": first["tool"], "arguments": {}}).json()
        print(f"  retry after approval -> {retry['decision']} ({retry['reason'][:80]})")
    print("\nsummary:", client.get("/dashboard/summary").json())
    print("\nDemo complete. Dashboard: http://127.0.0.1:8000  (uvicorn app.main:app --port 8000)")


if __name__ == "__main__":
    main()
