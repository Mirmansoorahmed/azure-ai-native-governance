"""Real OPA client. Tries a real Open Policy Agent server first, falls
back to the Python policy engine in app/policy.py, and ALWAYS says
which engine decided.

OPA contract: POST {OPA_URL}/v1/data/azure_native/{package}/decision
Body: {"input": {...}}  Response: {"result": {"decision": ..., "reason": ...}}
or a plain decision string. Run OPA with: opa run --server --addr
localhost:8181 policies/  (or docker compose up --build).
"""
import logging
import os

import httpx

from .policy import OPA_PACKAGES, evaluate

logger = logging.getLogger("azure_native.opa")
OPA_URL = os.environ.get("OPA_URL", "http://localhost:8181").rstrip("/")
OPA_ENABLED = os.environ.get("OPA_ENABLED", "true").lower() not in ("0", "false", "no")
OPA_TIMEOUT_S = float(os.environ.get("OPA_TIMEOUT_S", "2.0"))


def opa_available(timeout=1.0):
    if not OPA_ENABLED:
        return False
    try:
        with httpx.Client(timeout=timeout, trust_env=False) as client:
            r = client.get(f"{OPA_URL}/health")
            return r.status_code < 500
    except Exception:
        return False


def decide_via_opa(rule, context):
    package = OPA_PACKAGES.get(rule)
    if package is None:
        raise ValueError(f"Unknown rule '{rule}' for OPA")
    url = f"{OPA_URL}/v1/data/azure_native/{package}/decision"
    with httpx.Client(timeout=OPA_TIMEOUT_S, trust_env=False) as client:
        resp = client.post(url, json={"input": context})
        resp.raise_for_status()
        result = resp.json().get("result")
    if isinstance(result, dict):
        decision = result.get("decision", "deny")
        reason = result.get("reason", f"OPA decision for rule '{rule}'")
    elif isinstance(result, str) and result in ("allow", "deny", "needs_approval", "human_approval"):
        decision = "human_approval" if result == "human_approval" else result
        reason = f"OPA decision for rule '{rule}': {result}"
    elif isinstance(result, bool):
        decision = "allow" if result else "deny"
        reason = f"OPA decision for rule '{rule}'"
    else:
        raise ValueError(f"Unexpected OPA result for '{rule}': {result!r}")
    if decision == "human_approval":
        decision = "needs_approval"
    out = {"decision": decision, "reason": reason, "engine": "opa", "rule": rule, "opa_url": url}
    # Keep the native-decision field present even when OPA decides.
    if "native_decision" in context:
        out["native_decision"] = context.get("native_decision")
    return out


def decide(rule, context):
    if OPA_ENABLED:
        try:
            return decide_via_opa(rule, context)
        except Exception as exc:
            logger.warning("OPA unavailable for rule %s (%s); using Python fallback", rule, exc)
            result = evaluate(rule, context)
            result["engine"] = "python-fallback"
            result["rule"] = rule
            result["opa_error"] = str(exc)
            return result
    result = evaluate(rule, context)
    result["engine"] = "python-fallback"
    result["rule"] = rule
    result["opa_error"] = "OPA disabled (OPA_ENABLED=false)"
    return result
