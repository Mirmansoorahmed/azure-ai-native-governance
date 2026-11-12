# Azure AI Native Governance — Architecture

> **Lab / portfolio project. SIMULATED Azure estate ("Nordlicht GmbH").**
> Synthetic data only. No live Azure tenant access, no real tenant,
> no production deployment. The user's Azure for Students subscription
> is live, but this lab does **not** call it.

![Architecture — one combined diagram: 6 layers + both data flows](architecture.png)

**One combined diagram (v1.0).** `architecture.png` contains the 6 layers
*and* both data flows (A Azure Policy evaluation, B agent tool call) in
a single picture. `dataflow.png` is an identical copy of the same
picture, so there are no two different diagrams.

Regenerate the single diagram: `python3 scripts/make_diagrams.py`

## The problem in one paragraph

Azure native applications govern **resources, identity, network and
model content** — but none of them decides an individual MCP tool
call. Azure Policy can deny a VM in eastus; Defender can flag an
unencrypted disk; Entra ID can require MFA; Key Vault can guard a
secret; content filters can block a jailbreak prompt. None of them
can say "this agent may read this storage account, but may not delete
this CRM account, and may only export with human approval". That
per-tool-call decision is the gap the Microsoft 365 Governance Agent
gateway fills — on the Azure side exactly as on the M365 side.

## Components

| Piece | Role | Where |
|---|---|---|
| FastAPI app | HTTP API, dashboard | `app/main.py` |
| Simulated Azure estate | Subscriptions, RGs, VMs, storage, Key Vaults, AI resources, users, policies, Defender | `app/connectors/azure.py`, `app/data.py` |
| Governance checks | 16 checks (Policy, Defender, Entra, Key Vault, Monitor, AI filters, residency, network, gap) | `app/checks.py` |
| Native capabilities | 10 services, each with explicit CAN / CANNOT lists | `app/data.py` NATIVE_CAPABILITIES |
| Comparison | 10 questions × 3 answers: Azure native vs Purview/Agent 365 vs gateway | `app/data.py` COMPARISON, `GET /comparison` |
| Gap | `native_decision_for_tool_call` is always `null` | `app/policy.py`, `GET /gap` |
| Policy engine | 8 rules, OPA first, Python fallback, engine always logged | `app/policy.py`, `app/opa_client.py`, `policies/*.rego` |
| Evidence | SHA-256 hash chain, CSV/JSON export for a GRC system of record | `app/evidence.py` |
| Issues | Open → In Progress → Verified → Closed | `app/models.py` Issue |
| Approvals | One-shot grants bound to exact arguments | `app/models.py` Approval |
| Classification | EU AI Act intake classifier (prohibited / high / limited / minimal) | `app/policy.py` `classify_use_case` |

## Request path — one agent tool call (two decisions)

```
Agent (Entra Agent ID identity, sponsor)
  → POST /agent/action {agent_id, tool, arguments}
  → Native decision: None — no Azure native application sees this call
  → Gateway decision: OPA (or Python fallback): allow / deny / needs_approval
  → needs_approval: create Approval, or reuse an approved one-shot grant
  → decision + reason + engine + native_decision logged as AgentAction row
  → (allow) tool would execute against the simulated estate
```

The gateway is the Policy Enforcement Point (PEP); OPA is the Policy
Decision Point (PDP). The caller enforces; OPA only decides. If OPA
is down, the Python engine decides and the response says so
(`engine: "python-fallback"`, with `opa_error`) — fail-closed is
preserved by the Python rules, which are deny-by-default.

## The law → rule pipeline

Same pipeline as the M365 project, applied to Azure resources:

1. **Law text → control objective.** EU AI Act Art. 5 "no social
   scoring" → control: "No use case may score people across
   unrelated data to decide treatment."
2. **Control objective → testable rule.** In Rego: `deny if
   eu_tier == "prohibited"`. In Azure Policy terms: "deny if the
   resource is in eastus".
3. **Rule → enforcement point.** ARM deployment, Terraform plan,
   agent gateway (`POST /agent/action`).
4. **Rule → evidence.** Every decision is logged with who / what /
   when / which rule version, hash-chained.
5. **Evidence → many frameworks.** One control, evidenced once,
   resolves obligations across ISO 42001, EU AI Act, GDPR and
   ISO 27001 (crosswalk in `app/data.py` CONTROLS).

## What Azure native does vs what the gateway does

| Question | Azure native | Purview / Agent 365 | Gateway (M365 project) |
|---|---|---|---|
| May this Azure resource exist here? | Azure Policy: Deny by region / SKU | Not applicable | Mirrors it (region + residency) |
| Is this storage / disk encrypted? | Policy + Defender: Audit/Deny | Purview labels (M365 content) | Checks the same estate |
| May this agent run at all? | Entra sign-in / Conditional Access | Agent 365 allow / block | Mirrors it |
| Which systems may it connect to? | NSG / Private Link / Firewall; RBAC | Power Platform DLP connector groups | Mirrors it |
| May this specific tool call happen, with these arguments, right now? | **No native application decides this** | **No per-tool MCP control** | **OPA decision per tool call** |
| Is the tool definition unchanged? | No hash pinning | Pin MCP versions (guidance) | SHA-256 pin check |
| Is a human approving this write? | No uniform gate | Copilot Studio workflow gates only | Uniform approval gate |
| What happened, in one audit trail? | Monitor / Sentinel (after the fact) | Purview audit log | One signed per-call log + hash chain |
| Does this satisfy the framework? | Partially — no single per-call record | Purview Compliance Manager (Microsoft scope) | Export to Archer/OneTrust |

## Trust boundaries

- The simulated estate is **outside** the trust boundary: its
  resource descriptions, regions and settings are checked, never
  trusted.
- The agent is authenticated (in the simulation: by agent_id + the
  registry) and then **not trusted** with a raw tool call.
- OPA is trusted for the decision; the gateway is trusted to enforce
  it and to log it. The approver is trusted to decide held calls.
- The lab approver flow has no auth token — approvals are decided
  via the API in the demo; a production version needs approver auth.

## What this design gives up

- A resource that is compliant on first sight is trusted until its
  configuration changes; a service that misbehaves while keeping a
  clean description is not stopped by Policy alone.
- The Python fallback is a second implementation of the Rego rules;
  the two can drift. The tests check the Python rules; the Rego
  files are kept short and mutually exclusive so OPA never returns
  two decisions for one input.
- This is a **simulated** estate. In a real tenant the connector
  layer (`app/connectors/azure.py`) would be replaced by Azure
  Resource Graph, Defender for Cloud, Microsoft Graph and Azure
  OpenAI management-plane calls — the governance logic above that
  layer would not change.
