"""FastAPI app — Azure AI Native Governance.

Endpoints mirror the M365 Governance Agent project so the two can be
compared side by side. All estate data is SIMULATED (see app/data.py).
"""
import csv
import io
import json
import secrets
from datetime import datetime, timezone

from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse, JSONResponse, PlainTextResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from .checks import run_all_checks
from .connectors.azure import SimulatedAzure
from .data import (
    AGENTS, AI_RESOURCES, COMPARISON, CONTROLS, DEFENDER, GAP, KEYVAULTS,
    NATIVE_CAPABILITIES, POLICY_ASSIGNMENTS, RISKS, STORAGE, SUBSCRIPTION,
    USERS, VMS,
)
from .database import Base, SessionLocal, engine, get_db
from .evidence import compute_hash, utc_now_iso, verify_chain
from .models import AgentAction, Approval, AzureResource, Control, Evidence, Issue, Risk
from .opa_client import decide, opa_available
from .policy import classify_use_case, evaluate, native_decision_for_tool_call

Base.metadata.create_all(bind=engine)
app = FastAPI(title="Azure AI Native Governance", version="1.0.0")
templates = Jinja2Templates(directory="app/templates")
AZURE = SimulatedAzure()


def _summary(db):
    s = AZURE.summary()
    ev = db.query(Evidence).count()
    return {
        "tenant": "SIMULATED Nordlicht GmbH (Azure)",
        "subscription": SUBSCRIPTION["name"],
        "risks_total": db.query(Risk).count(),
        "controls_total": db.query(Control).count(),
        "resources_total": db.query(AzureResource).count(),
        "vms_total": s["vms_total"],
        "vms_public_ip": s["vms_public_ip"],
        "storage_total": s["storage_total"],
        "storage_public": s["storage_public"],
        "keyvaults_total": s["keyvaults_total"],
        "secrets_expired": s["secrets_expired"],
        "ai_total": s["ai_total"],
        "ai_no_filter": s["ai_no_filter"],
        "ai_outside_eu": s["ai_outside_eu"],
        "users_total": s["users_total"],
        "users_without_mfa": s["users_no_mfa"],
        "users_missing_ai_literacy": s["users_missing_ai_literacy"],
        "defender_secure_score_pct": s["defender_secure_score_pct"],
        "agents_total": len(AGENTS),
        "evidence_total": ev,
        "open_issues": db.query(Issue).filter(Issue.status != "Closed").count(),
        "gap": GAP["headline"],
    }


@app.get("/", response_class=HTMLResponse)
def dashboard(request: Request, db: Session = Depends(get_db)):
    # Render directly (not via Starlette TemplateResponse): the installed
    # Jinja2 version fails to cache a template when the context contains
    # plain dicts — "unhashable type: 'dict'" (same fix as the M365 project).
    from jinja2 import Environment, FileSystemLoader
    env = Environment(loader=FileSystemLoader("app/templates"))
    html = env.get_template("dashboard.html").render({"summary": _summary(db)})
    return HTMLResponse(content=html)


@app.get("/dashboard", response_class=HTMLResponse)
def dashboard2(request: Request, db: Session = Depends(get_db)):
    return dashboard(request, db)


@app.get("/dashboard/summary")
def dashboard_summary(db: Session = Depends(get_db)):
    return _summary(db)


@app.get("/subscription")
def subscription():
    return SUBSCRIPTION


@app.get("/resources")
def resources(db: Session = Depends(get_db)):
    rows = db.query(AzureResource).all()
    return [{"resource_id": r.resource_id, "name": r.name, "kind": r.kind, "resource_group": r.resource_group,
             "region": r.region, "status": r.status, "owner": r.owner, "details": json.loads(r.details or "{}")} for r in rows]


@app.get("/vms")
def vms():
    return VMS


@app.get("/storage")
def storage():
    return STORAGE


@app.get("/keyvaults")
def keyvaults():
    return KEYVAULTS


@app.get("/ai")
def ai_resources():
    return AI_RESOURCES


@app.get("/users")
def users():
    return USERS


@app.get("/policies")
def policies():
    return POLICY_ASSIGNMENTS


@app.get("/defender")
def defender():
    return DEFENDER


@app.get("/agents")
def agents():
    return AGENTS


@app.get("/native")
def native_capabilities():
    """What each Azure native application CAN and CANNOT decide."""
    return NATIVE_CAPABILITIES


@app.get("/native/{service}")
def native_one(service: str):
    for n in NATIVE_CAPABILITIES:
        if service.lower() in n["service"].lower():
            return n
    raise HTTPException(404, "native service not found")


@app.get("/comparison")
def comparison():
    """Same question — Azure native vs Purview/Agent 365 vs gateway."""
    return COMPARISON


@app.get("/gap")
def gap():
    """The per-tool-call gap, stated as data."""
    return GAP


@app.get("/risks")
def risks(db: Session = Depends(get_db)):
    return [{"code": r.code, "title": r.title, "likelihood": r.likelihood, "impact": r.impact,
             "inherent_score": r.inherent_score, "category": r.category, "frameworks": r.frameworks} for r in db.query(Risk).all()]


@app.get("/controls")
def controls(db: Session = Depends(get_db)):
    return [{"code": c.code, "title": c.title, "risk_code": c.risk_code, "frameworks": c.frameworks,
             "owner": c.owner} for c in db.query(Control).all()]


@app.post("/tests/run")
def run_tests(db: Session = Depends(get_db)):
    checks = run_all_checks()
    prev = db.query(Evidence).order_by(Evidence.id.desc()).first()
    prev_hash = prev.sha256 if prev else "GENESIS"
    created = []
    for ch in checks:
        ts = utc_now_iso()
        details = dict(ch["details"]); details["run_at"] = ts
        h = compute_hash(prev_hash, ch["control_code"], ch["test_name"], ch["result"], ts, details)
        row = Evidence(control_code=ch["control_code"], test_name=ch["test_name"], result=ch["result"],
                       sha256=h, details=json.dumps(details))
        db.add(row); db.flush(); prev_hash = h; created.append(ch)
        if ch["result"] == "Fail":
            existing = db.query(Issue).filter(Issue.control_code == ch["control_code"], Issue.status != "Closed").first()
            if not existing:
                ctrl = db.query(Control).filter(Control.code == ch["control_code"]).first()
                db.add(Issue(title=f"{ch['test_name']} failed", control_code=ch["control_code"],
                             owner=ctrl.owner if ctrl else "AI Governance", severity="High"))
    db.commit()
    counts = {"Pass": 0, "Fail": 0, "Partial": 0}
    for ch in created:
        counts[ch["result"]] += 1
    return {"checks_run": len(created), "counts": counts, "checks": created}


@app.get("/evidence")
def evidence(db: Session = Depends(get_db)):
    rows = db.query(Evidence).order_by(Evidence.id).all()
    return [{"id": r.id, "control_code": r.control_code, "test_name": r.test_name, "result": r.result,
             "sha256": r.sha256[:16] + "…"} for r in rows]


@app.get("/evidence/verify")
def evidence_verify(db: Session = Depends(get_db)):
    rows = db.query(Evidence).order_by(Evidence.id).all()
    return verify_chain(rows)


@app.get("/evidence/export.csv", response_class=PlainTextResponse)
def evidence_csv(db: Session = Depends(get_db)):
    rows = db.query(Evidence).order_by(Evidence.id).all()
    buf = io.StringIO(); w = csv.writer(buf)
    w.writerow(["id", "control_code", "test_name", "result", "sha256"])
    for r in rows:
        w.writerow([r.id, r.control_code, r.test_name, r.result, r.sha256])
    return buf.getvalue()


@app.get("/issues")
def issues(db: Session = Depends(get_db)):
    return [{"id": i.id, "title": i.title, "control_code": i.control_code, "status": i.status,
             "owner": i.owner, "severity": i.severity} for i in db.query(Issue).all()]


@app.post("/agent/action")
def agent_action(payload: dict, db: Session = Depends(get_db)):
    """One tool call, two decisions: what native decides (nothing) and
    what the gateway decides (OPA / Python fallback)."""
    agent_id = payload.get("agent_id", "unknown")
    tool = payload.get("tool", "")
    agent = next((a for a in AGENTS if a["agent_id"] == agent_id), None)
    ctx = {
        "agent_id": agent_id, "tool": tool,
        "agent_status": agent["status"] if agent else "blocked",
        "eu_tier": agent["eu_tier"] if agent else "minimal",
        "tool_pinned": payload.get("tool_pinned", True),
        "from_untrusted_content": payload.get("from_untrusted_content", False),
    }
    native = native_decision_for_tool_call(tool, agent_id)
    result = decide("gateway_tool_call", ctx)
    decision = result["decision"]
    approval_id = None
    if decision == "needs_approval":
        grant = db.query(Approval).filter(
            Approval.agent_id == agent_id, Approval.tool == tool,
            Approval.arguments == json.dumps(payload.get("arguments", {}), sort_keys=True),
            Approval.status == "approved").first()
        if grant:
            decision = "allow"
            result["reason"] = f"human approved {grant.approval_id}"
            approval_id = grant.approval_id
        else:
            approval_id = "apr_" + secrets.token_hex(6)
            db.add(Approval(approval_id=approval_id, agent_id=agent_id, tool=tool,
                            arguments=json.dumps(payload.get("arguments", {}), sort_keys=True),
                            reason=result["reason"]))
            db.commit()
    db.add(AgentAction(agent_id=agent_id, tool=tool, decision=decision, reason=result["reason"],
                       engine=result.get("engine", "python-fallback"),
                       native_decision=None, approval_id=approval_id))
    db.commit()
    return {"agent_id": agent_id, "tool": tool, "decision": decision,
            "reason": result["reason"], "engine": result.get("engine", "python-fallback"),
            "native_decision": native["native_decision"], "native_reason": native["native_reason"],
            "approval_id": approval_id, "gap": GAP["headline"]}


@app.get("/approvals")
def approvals(db: Session = Depends(get_db)):
    return [{"approval_id": a.approval_id, "agent_id": a.agent_id, "tool": a.tool,
             "status": a.status, "reason": a.reason} for a in db.query(Approval).all()]


@app.post("/approvals/{approval_id}/decide")
def decide_approval(approval_id: str, payload: dict, db: Session = Depends(get_db)):
    ap = db.query(Approval).filter(Approval.approval_id == approval_id).first()
    if not ap:
        raise HTTPException(404, "approval not found")
    decision = payload.get("decision", "")
    if decision not in ("approved", "denied"):
        raise HTTPException(400, "decision must be 'approved' or 'denied'")
    ap.status = decision; ap.decided_by = payload.get("decided_by", "human-approver")
    db.commit()
    return {"approval_id": approval_id, "status": ap.status}


@app.post("/classification/classify")
def classify(payload: dict):
    return classify_use_case(payload.get("purpose", ""), payload.get("data_types", ""),
                             payload.get("decision_about_people", False), payload.get("workplace", False))


@app.post("/policy/evaluate")
def policy_evaluate(payload: dict):
    rule = payload.get("rule", "")
    context = payload.get("context", {})
    return decide(rule, context)


@app.get("/policy/engine")
def policy_engine():
    return {"opa_available": opa_available(), "opa_url": "http://localhost:8181"}


@app.get("/audit/export")
def audit_export(db: Session = Depends(get_db)):
    return {"tenant": "SIMULATED Nordlicht GmbH (Azure)", "summary": _summary(db),
            "evidence": [{"control_code": r.control_code, "test_name": r.test_name, "result": r.result} for r in db.query(Evidence).all()],
            "issues": [{"title": i.title, "control_code": i.control_code, "status": i.status} for i in db.query(Issue).all()],
            "gap": GAP, "comparison": COMPARISON}


@app.get("/health")
def health():
    return {"status": "ok", "project": "azure-native-governance", "simulated": True}
