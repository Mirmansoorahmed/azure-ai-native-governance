"""Python policy engine — fallback for OPA / Rego.

Same rules exist as real Rego in policies/, one package per rule
(package azure_native.<name>). The governance question here is TWO
questions, kept separate on purpose:
  1. What does Azure native decide?  (native_decision)
  2. What does the gateway decide? (decision)
For a tool call, native_decision is always None — that IS the gap.
"""
from .data import AGENT_ALLOWLIST, ALLOWED_REGIONS, RECIPIENT_ALLOWLIST, TOOLS_REQUIRING_APPROVAL

OPA_PACKAGES = {
    "azure_policy_location": "location",
    "storage_public": "storage",
    "encryption": "encryption",
    "mfa": "mfa",
    "keyvault_expiry": "keyvault",
    "ai_content_filter": "content_filter",
    "network_private_endpoint": "network",
    "gateway_tool_call": "tool_call",
}


def native_decision_for_tool_call(tool, agent_id):
    """What Azure native applications decide about ONE tool call: nothing.
    They govern the resource, the identity, the network path and the
    model content — but they never see the tool call itself."""
    return {
        "native_decision": None,
        "native_reason": (
            f"No Azure native application decides the tool call '{tool}' for agent '{agent_id}'. "
            "Azure Policy governs the resource, Entra ID governs the sign-in, Key Vault governs "
            "the secret read, content filters govern the prompt — none of them sees this call."
        ),
    }


def evaluate_azure_policy_location(ctx):
    if ctx.get("region") not in ALLOWED_REGIONS:
        return {"decision": "deny", "reason": f"Region {ctx.get('region')} is outside the allowed EU regions (germanywestcentral / westeurope)"}
    return {"decision": "allow", "reason": f"Region {ctx.get('region')} is allowed"}


def evaluate_storage_public(ctx):
    if ctx.get("public_blob"):
        return {"decision": "deny", "reason": f"Storage {ctx.get('resource_id')} allows public blob access — Azure Policy 'deny public blob' applies"}
    return {"decision": "allow", "reason": "No public blob access"}


def evaluate_encryption(ctx):
    if not ctx.get("encryption"):
        return {"decision": "deny", "reason": f"Resource {ctx.get('resource_id')} is not encrypted at rest"}
    if ctx.get("tls_min") and ctx["tls_min"] < "1.2":
        return {"decision": "deny", "reason": f"TLS minimum {ctx.get('tls_min')} is below 1.2"}
    return {"decision": "allow", "reason": "Encryption at rest on, TLS >= 1.2"}


def evaluate_mfa(ctx):
    if not ctx.get("mfa_enabled"):
        return {"decision": "deny", "reason": f"User {ctx.get('user')} has no MFA"}
    if not ctx.get("ca_compliant"):
        return {"decision": "needs_approval", "reason": f"User {ctx.get('user')} is not Conditional Access compliant"}
    return {"decision": "allow", "reason": "MFA and Conditional Access satisfied"}


def evaluate_keyvault_expiry(ctx):
    if ctx.get("secrets_expired", 0) > 0:
        return {"decision": "deny", "reason": f"Key Vault {ctx.get('resource_id')} has {ctx['secrets_expired']} expired secret(s)"}
    if not ctx.get("purge_protection"):
        return {"decision": "needs_approval", "reason": "Purge protection is off — human review required"}
    if not ctx.get("rbac"):
        return {"decision": "needs_approval", "reason": "Key Vault still uses access policies, not RBAC"}
    return {"decision": "allow", "reason": "Key Vault: secrets current, RBAC on, purge protection on"}


def evaluate_ai_content_filter(ctx):
    if not ctx.get("content_filter"):
        return {"decision": "deny", "reason": f"AI resource {ctx.get('resource_id')} has no content filter — jailbreak / harmful output is unfiltered"}
    if not ctx.get("jailbreak_filter"):
        return {"decision": "needs_approval", "reason": "Jailbreak filter is off"}
    if not ctx.get("logging"):
        return {"decision": "needs_approval", "reason": "AI logging is off — no audit trail for this resource"}
    return {"decision": "allow", "reason": "Content + jailbreak filters on, logging on"}


def evaluate_network_private_endpoint(ctx):
    if not ctx.get("private_endpoint"):
        return {"decision": "needs_approval", "reason": f"Resource {ctx.get('resource_id')} has no private endpoint — reachable over the public network path"}
    return {"decision": "allow", "reason": "Private endpoint in place"}


def evaluate_gateway_tool_call(ctx):
    """The gateway decision for one tool call — the decision native
    applications never make. Deny-by-default, like the M365 project."""
    agent = ctx.get("agent_id", "unknown")
    tool = ctx.get("tool", "")
    tool_name = tool.split(".")[-1]
    native = native_decision_for_tool_call(tool, agent)
    if ctx.get("agent_status") == "blocked":
        return {**native, "decision": "deny", "reason": f"Agent {agent} is blocked"}
    if ctx.get("eu_tier") == "prohibited":
        return {**native, "decision": "deny", "reason": "EU AI Act Art. 5 prohibits this use case"}
    if ctx.get("tool_pinned") is False:
        return {**native, "decision": "deny", "reason": f"Tool {tool} failed the SHA-256 pin check (drift) — re-review required"}
    if ctx.get("from_untrusted_content"):
        return {**native, "decision": "needs_approval", "reason": "Tool arguments came from untrusted content (possible prompt injection)"}
    if tool_name in TOOLS_REQUIRING_APPROVAL or tool in TOOLS_REQUIRING_APPROVAL:
        return {**native, "decision": "needs_approval", "reason": f"Tool '{tool}' always requires human approval"}
    if tool in AGENT_ALLOWLIST.get(agent, []):
        return {**native, "decision": "allow", "reason": f"Tool '{tool}' is allowlisted for {agent}"}
    return {**native, "decision": "deny", "reason": f"Tool '{tool}' is not allowlisted for {agent}"}


_EVALUATORS = {
    "azure_policy_location": evaluate_azure_policy_location,
    "storage_public": evaluate_storage_public,
    "encryption": evaluate_encryption,
    "mfa": evaluate_mfa,
    "keyvault_expiry": evaluate_keyvault_expiry,
    "ai_content_filter": evaluate_ai_content_filter,
    "network_private_endpoint": evaluate_network_private_endpoint,
    "gateway_tool_call": evaluate_gateway_tool_call,
}


def evaluate(rule, context):
    fn = _EVALUATORS.get(rule)
    if fn is None:
        return {"decision": "deny", "reason": f"Unknown rule '{rule}'"}
    out = fn(context or {})
    out.setdefault("decision", "deny")
    out.setdefault("reason", "")
    return out


def classify_use_case(purpose, data_types, decision_about_people, workplace=False):
    p = (purpose or "").lower()
    if any(k in p for k in ("social scoring", "score people", "score customers", "emotion recognition")):
        return {"tier": "prohibited", "article": "Art. 5",
                "duties": ["Do not build or deploy. Block at intake and at runtime."],
                "reason": "EU AI Act Art. 5 prohibits social scoring and workplace emotion recognition."}
    if decision_about_people or any(k in p for k in ("screen", "recruit", "hire", "credit", "dismiss", "promote", "performance")):
        return {"tier": "high-risk", "article": "Arts. 9-15, 26",
                "duties": ["Risk management (Art. 9)", "Data governance (Art. 10)", "Logging (Art. 12)",
                           "Transparency (Art. 13)", "Human oversight (Art. 14)", "Works-council check (BetrVG s.87)"],
                "reason": "Decisions about people (employment, credit, access) are high-risk under Annex III."}
    if any(k in p for k in ("chatbot", "deepfake", "synthetic", "emotion")) or "personal data" in (data_types or ""):
        return {"tier": "limited", "article": "Art. 50",
                "duties": ["Transparency: tell users they are talking to AI", "Label AI-generated content"],
                "reason": "Limited-risk: transparency duties under Art. 50 apply."}
    return {"tier": "minimal", "article": "—",
            "duties": ["Voluntary codes of practice (Art. 95)"],
            "reason": "Minimal risk: no mandatory AI Act duties, voluntary good practice applies."}
