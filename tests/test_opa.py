"""OPA HTTP path proven against a fake OPA server speaking the same
contract (POST /v1/data/azure_native/<package>/decision). No real OPA
binary or Docker is needed for these tests."""
import json
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer

import app.opa_client as opa


class FakeOPA(BaseHTTPRequestHandler):
    def do_POST(self):
        length = int(self.headers.get("Content-Length", 0))
        body = json.loads(self.rfile.read(length) or b"{}")
        tool = body.get("input", {}).get("tool", "")
        decision = "allow" if tool == "azure.storage.read" else "deny"
        payload = json.dumps({"result": {"decision": decision, "reason": f"fake OPA: {decision}"}}).encode()
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)

    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-Length", "2")
        self.end_headers()
        self.wfile.write(b"{}")

    def log_message(self, *a):
        pass


def _server():
    srv = HTTPServer(("127.0.0.1", 0), FakeOPA)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    return srv


def test_opa_available_and_decide(monkeypatch):
    srv = _server()
    monkeypatch.setattr(opa, "OPA_URL", f"http://127.0.0.1:{srv.server_address[1]}")
    monkeypatch.setattr(opa, "OPA_ENABLED", True)
    assert opa.opa_available() is True
    r = opa.decide("gateway_tool_call", {"agent_id": "ops-agent", "tool": "azure.storage.read"})
    assert r["engine"] == "opa" and r["decision"] == "allow"
    r = opa.decide("gateway_tool_call", {"agent_id": "ops-agent", "tool": "crm.delete_account"})
    assert r["engine"] == "opa" and r["decision"] == "deny"
    srv.shutdown()


def test_opa_unavailable_falls_back(monkeypatch):
    monkeypatch.setattr(opa, "OPA_URL", "http://127.0.0.1:1")
    monkeypatch.setattr(opa, "OPA_ENABLED", True)
    r = opa.decide("azure_policy_location", {"region": "eastus"})
    assert r["engine"] == "python-fallback" and r["decision"] == "deny"
    assert "opa_error" in r
