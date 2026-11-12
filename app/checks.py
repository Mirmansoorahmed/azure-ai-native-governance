"""16 Azure-native governance checks. Each check returns a dict with
control_code, test_name, result (Pass/Fail/Partial) and details. The
main app stores one hash-chained Evidence row per check and opens an
Issue on Fail.

Honesty rule (from Control Harness / M365 project): a check that did
not run, or produced no evidence, is at most Partial — never a Pass.
Check AZ-16 is the gap check: it is Partial BY DESIGN, because no
Azure native application can make the decision it tests.
"""
from .connectors.azure import SimulatedAzure
from .data import AGENTS, AI_RESOURCES, KEYVAULTS, POLICY_ASSIGNMENTS, STORAGE, USERS, VMS

AZURE = SimulatedAzure()


def _check(control, name, result, details):
    return {"control_code": control, "test_name": name, "result": result, "details": details}


def run_all_checks():
    s = AZURE.summary()
    out = []
    # AZ-01 allowed locations (A-01)
    out.append(_check("A-01", "azure_policy_allowed_locations",
                      "Fail" if s["regions_outside_allowed"] else "Pass",
                      {"regions_outside_allowed": s["regions_outside_allowed"], "allowed": ["germanywestcentral", "westeurope"]}))
    # AZ-02 public storage (A-02)
    out.append(_check("A-02", "storage_public_blob_deny",
                      "Fail" if s["storage_public"] else "Pass",
                      {"storage_public": s["storage_public"], "storage_total": s["storage_total"],
                       "public_accounts": [x["name"] for x in STORAGE if x["public_blob"]]}))
    # AZ-03 encryption + TLS (A-03)
    bad_tls = [x["name"] for x in STORAGE if x["tls_min"] < "1.2"]
    out.append(_check("A-03", "encryption_tls_minimum",
                      "Fail" if s["storage_unencrypted"] or bad_tls else "Pass",
                      {"storage_unencrypted": s["storage_unencrypted"], "tls_below_1_2": bad_tls,
                       "vms_unencrypted": s["vms_unencrypted"]}))
    # AZ-04 VM public IP / JIT (A-04)
    out.append(_check("A-04", "vm_public_ip_jit",
                      "Fail" if s["vms_public_ip"] >= 2 else "Partial" if s["vms_public_ip"] else "Pass",
                      {"vms_public_ip": s["vms_public_ip"], "public_vms": [v["name"] for v in VMS if v["public_ip"]],
                       "vms_no_jit": [v["name"] for v in VMS if not v["jit"]]}))
    # AZ-05 Key Vault secrets (A-05)
    out.append(_check("A-05", "keyvault_secrets_expiry_rbac",
                      "Fail" if s["secrets_expired"] >= 3 else "Partial" if s["secrets_expired"] else "Pass",
                      {"secrets_expired": s["secrets_expired"],
                       "vaults_no_purge": [k["name"] for k in KEYVAULTS if not k["purge_protection"]],
                       "vaults_no_rbac": [k["name"] for k in KEYVAULTS if not k["rbac"]]}))
    # AZ-06 MFA (A-06)
    out.append(_check("A-06", "entra_mfa",
                      "Fail" if s["users_no_mfa"] >= 3 else "Partial" if s["users_no_mfa"] else "Pass",
                      {"users_without_mfa": s["users_no_mfa"], "users": [u["user"] for u in USERS if not u["mfa"]]}))
    # AZ-07 Conditional Access (A-07)
    out.append(_check("A-07", "entra_conditional_access",
                      "Partial" if s["users_no_ca"] else "Pass",
                      {"users_not_ca_compliant": s["users_no_ca"], "users": [u["user"] for u in USERS if not u["ca_compliant"]]}))
    # AZ-08 Defender secure score (A-08)
    score = s["defender_secure_score_pct"]
    out.append(_check("A-08", "defender_secure_score",
                      "Pass" if score >= 80 else "Partial" if score >= 60 else "Fail",
                      {"secure_score_pct": score, "high_findings": s["defender_high_findings"],
                       "recommendations_open": AZURE.defender()["recommendations_open"]}))
    # AZ-09 Monitor / Sentinel logging (A-09)
    no_log = [a["name"] for a in AI_RESOURCES if not a["logging"]]
    out.append(_check("A-09", "monitor_sentinel_logging",
                      "Partial" if no_log else "Pass",
                      {"ai_resources_without_logging": no_log, "note": "Sentinel sees logs after the fact; it cannot decide before a call"}))
    # AZ-10 AI content filters (A-10)
    out.append(_check("A-10", "azure_openai_content_filters",
                      "Fail" if s["ai_no_filter"] else "Pass",
                      {"ai_no_filter": s["ai_no_filter"], "unfiltered": [a["name"] for a in AI_RESOURCES if not a["content_filter"]]}))
    # AZ-11 AI data residency (A-11)
    out.append(_check("A-11", "ai_data_residency_eu",
                      "Fail" if s["ai_outside_eu"] else "Pass",
                      {"ai_outside_eu": s["ai_outside_eu"], "outside": [a["name"] for a in AI_RESOURCES if a["data_residency"] != "EU"]}))
    # AZ-12 AI logging / Art. 12 (A-12)
    out.append(_check("A-12", "ai_logging_traceability",
                      "Partial" if no_log else "Pass",
                      {"ai_without_logging": no_log, "eu_ai_act": "Art. 12 logging"}))
    # AZ-13 private endpoints (A-13)
    no_pe = [x["name"] for x in STORAGE if not x["private_endpoint"]] + [k["name"] for k in KEYVAULTS if not k["private_endpoint"]]
    out.append(_check("A-13", "network_private_endpoints",
                      "Partial" if no_pe else "Pass",
                      {"resources_without_private_endpoint": no_pe, "count": len(no_pe)}))
    # AZ-14 policy effect Deny vs Audit-only (A-14)
    audit_only = [p["name"] for p in POLICY_ASSIGNMENTS if p["effect"] == "Audit"]
    out.append(_check("A-14", "policy_effect_deny_not_audit",
                      "Partial" if audit_only else "Pass",
                      {"audit_only_policies": audit_only, "note": "Audit-only policies report violations; they do not block them"}))
    # AZ-15 AI literacy Art. 4 (A-20)
    out.append(_check("A-20", "ai_literacy_training",
                      "Partial" if s["users_missing_ai_literacy"] else "Pass",
                      {"users_missing_ai_literacy": s["users_missing_ai_literacy"], "users_total": s["users_total"]}))
    # AZ-16 THE GAP — per-tool-call decision (A-16)
    out.append(_check("A-16", "per_tool_call_decision_gap",
                      "Partial",
                      {"native_decision": None,
                       "gateway_decision": "OPA allow / deny / needs_approval per tool call",
                       "gap": "No Azure native application decides an individual MCP tool call. "
                              "Azure Policy, Defender, Entra ID, Key Vault, Monitor/Sentinel and "
                              "content filters each govern a different layer — none sees the call itself. "
                              "This check is Partial by design; it can only become Pass when a gateway "
                              "like the M365 Governance Agent is in front of the tools.",
                       "agents": [a["agent_id"] for a in AGENTS]}))
    return out
