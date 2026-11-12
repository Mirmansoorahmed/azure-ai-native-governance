# Azure AI Native Governance — Report

**Date:** 10 November 2026 (lab run, Europe/Berlin)
**Author:** Mir Mansoor Ahmed — personal lab / portfolio project
**Tenant:** SIMULATED "Nordlicht GmbH" (Azure) — all data synthetic, no live
Azure tenant access, no production deployment. The user's Azure for
Students subscription is live, but this lab does **not** call it.

Companion project to the **Microsoft 365 Governance Agent**
(`../m365-governance-agent/`). It does not duplicate it: that project
governs Copilot / agents in Microsoft 365; this one shows what Azure's
native applications govern on the Azure side — and where the same
per-tool-call gap remains.

## 1. Why this project exists

The user asked: do Azure's native applications not do this work? The
answer, checked service by service, is: they do a lot of governance
work, but **none of them decides an individual MCP tool call**.

- **Azure Policy** denies a VM in the wrong region or a public
  storage account — at resource creation / evaluation time.
- **Defender for Cloud** scores the estate and flags unencrypted
  disks, public IPs and missing MFA — as recommendations, after
  the fact.
- **Entra ID** requires MFA and Conditional Access — at token
  issuance, not at the next tool call.
- **Key Vault** guards who may read a secret — it cannot stop the
  agent using the secret afterwards.
- **Monitor / Sentinel** log and alert — after the call happened.
- **Azure OpenAI content filters** block a jailbreak prompt — they
  cannot decide the tool call that follows it.
- **Azure AI Foundry / Agent Service** runs an agent and its tools —
  it gives no per-tool OPA decision with arguments and session history.

## 2. The core argument

- **Azure native governs resources, identity, network and model
  content.** That is real governance, and it is what most Azure
  jobs ask for (see §3).
- **The gap is per-tool-call policy.** No native application sees
  the call itself: `azure.storage.read` vs `azure.keyvault.get_secret`
  vs `crm.delete_account` are all the same to Azure Policy, Defender
  and Entra ID — either the identity has the role, or it does not.
  There is no "read yes, delete no, export only with human approval".
- **Archer records the risk; OPA decides the call; the gateway
  enforces it.** The M365 Governance Agent gateway is the missing
  layer on both sides: it sits in front of the tools, takes an OPA
  decision per call, and writes one signed decision log.

## 3. What was built

| Area | Contents |
|---|---|
| App | FastAPI + SQLite (SQLAlchemy), Jinja2 dashboard, 25+ endpoints |
| Estate (simulated) | 1 subscription, 4 resource groups, 6 VMs, 8 storage accounts, 3 Key Vaults, 4 AI resources, 20 users, 6 policy assignments, Defender secure score 62% |
| Checks | 16 Azure-native governance checks (`app/checks.py`) |
| Native capabilities | 10 services, each with explicit CAN / CANNOT lists (`GET /native`) |
| Comparison | 10 questions × 3 answers: Azure native vs Purview/Agent 365 vs gateway (`GET /comparison`) |
| Gap | `GET /gap`: `native_decision_for_tool_call` is always `null`; gateway decision is OPA allow / deny / needs_approval |
| Policies | 8 Rego policies (`policies/*.rego`), 8 Python rules (`app/policy.py`) |
| Gateway demo | `POST /agent/action` — returns native decision (none) AND gateway decision side by side |
| Evidence | SHA-256 hash chain (`app/evidence.py`), `/evidence/verify`, CSV/JSON export |
| SQL | 6 audit queries (`sql/`) |
| Diagrams | One combined architecture picture, v1.0, with icons (`docs/architecture.png`, regenerable via `scripts/make_diagrams.py`) |
| Tests | 30 pytest tests across 6 files |
| Docs | README, REPORT, ARCHITECTURE |

## 4. Measured results — lab run, 10 Nov 2026

Method: `python -m scripts.demo` (TestClient, in-VM, no OPA server
running, so the Python fallback decided; engine logged per decision).
Seed: `python -m app.seed`.

### 4.1 Tests

```
30 passed, 0 failed in 12.59s
```

### 4.2 Checks (16 run)

```
0 Pass, 8 Fail, 8 Partial
```

| Check | Result | Why |
|---|---|---|
| A-01 allowed locations | Fail | rg-test is in eastus, outside the EU regions |
| A-02 public storage | Fail | 2 of 8 storage accounts allow public blob access |
| A-03 encryption / TLS | Fail | 1 storage account unencrypted, 2 VMs unencrypted, TLS 1.0 present |
| A-04 VM public IP / JIT | Fail | 2 VMs have public IPs, 3 without JIT |
| A-05 Key Vault secrets | Fail | 4 expired secrets across 3 vaults |
| A-06 MFA | Fail | 3 of 20 users without MFA |
| A-07 Conditional Access | Partial | 4 users not CA-compliant |
| A-08 Defender secure score | Partial | 62% (target 80%) |
| A-09 Monitor / Sentinel logging | Partial | 1 AI resource without logging |
| A-10 AI content filters | Fail | aoai-test has no content filter |
| A-11 AI data residency | Fail | aoai-test runs in eastus (US) |
| A-12 AI logging / Art. 12 | Partial | 1 AI resource without logging |
| A-13 private endpoints | Partial | 7 resources without a private endpoint |
| A-14 policy effect Deny | Partial | 3 policies are Audit-only |
| A-20 AI literacy | Partial | 6 of 20 users missing AI literacy |
| A-16 per-tool-call gap | Partial (by design) | Native decision is `null`; only a gateway can pass this check |

0 Pass is honest, not a bug: the simulated estate was built
deliberately non-compliant so the checks have something to find —
the same approach as the M365 project (which had 5 Pass, 4 Fail,
7 Partial on a less broken tenant).

### 4.3 Gateway demo (native vs gateway, per tool call)

| Agent | Tool | Native decision | Gateway decision |
|---|---|---|---|
| ops-agent | `azure.vm.start` | None | needs_approval → approved → allow |
| finance-assistant | `azure.storage.read` | None | allow |
| ops-agent | `azure.keyvault.get_secret` | None | needs_approval |
| shadow-notes | `azure.keyvault.get_secret` | None | **deny** (agent blocked) |
| social-scoring-pilot | `crm.score_customer` | None | **deny** (EU AI Act Art. 5) |
| sales-assistant | `crm.delete_account` | None | **deny** (not allowlisted) |

Evidence chain: valid, 16 rows checked. EU AI Act classification:
social scoring → prohibited; screening job applicants → high-risk.

### 4.4 Native capabilities (summary)

| Service | CAN (count) | CANNOT — the gap in one line |
|---|---|---|
| Azure Policy | 4 | Decide an individual MCP tool call |
| Defender for Cloud | 3 | Block a single tool call in real time |
| Entra ID | 3 | Decide an individual tool call for a signed-in agent |
| Key Vault | 3 | Decide the tool call that uses the secret |
| Monitor / Sentinel | 3 | Decide before a tool call happens |
| Azure OpenAI content filters | 3 | Decide a tool call (read vs delete vs export) |
| AI Foundry / Agent Service | 3 | Give a per-tool-call OPA decision |
| Network (NSG / Private Link) | 3 | Decide whether a permitted call is a safe tool call |
| Purview (M365 side) | 3 | Decide an individual MCP tool call |
| Agent 365 / Entra Agent ID | 3 | Decide an individual tool call |

## 5. How this maps to jobs

Azure governance jobs (Cloud Engineer, Azure Security Engineer,
Cloud Governance Lead, in Germany/EU) ask for: Azure Policy and
Resource Graph, Defender for Cloud and secure score, Entra ID /
Conditional Access / PIM, Key Vault, Monitor / Sentinel, network
(private endpoints, NSG, Firewall), cost guardrails, and frameworks
(ISO 27001, ISO 42001, EU AI Act, NIS2, DORA). This project
implements each of those as a working check, and adds the one thing
the job descriptions do not name but the agent era needs: a
per-tool-call decision record.

Certifications this maps to: **AZ-104** (Azure Administrator),
**AZ-500** (Azure Security Engineer), **SC-100** (Cybersecurity
Architect), **AI-102** (Azure AI Engineer). None of these exams
covers a per-tool-call gateway — that is the portfolio differentiator.

## 6. Honest limitations

- **Simulated estate.** `app/connectors/azure.py` is the seam: in a
  real tenant it would be replaced by Azure Resource Graph queries,
  Defender for Cloud API calls, Microsoft Graph (Entra ID) reads and
  Azure OpenAI management-plane calls. The governance logic above
  that layer would not change.
- **OPA was not running in this VM** (no `opa` binary, no Docker), so
  the live demo ran on the Python fallback. The OPA HTTP path is
  proven by tests against a fake OPA server speaking the same
  contract (`tests/test_opa.py`); `docker-compose.yml` (OPA 1.9.0)
  is provided and verified by reading, not by running.
- The Python fallback is a second implementation of the Rego rules;
  the two can drift. Rego files are kept short and mutually exclusive.
- The 0 Pass / 8 Fail check result reflects the deliberately
  non-compliant simulated estate, not a real tenant's posture.
- This project is **not** Microsoft's product, not PwC's stack, and
  not a claim of production experience. It is a personal lab /
  portfolio project with synthetic data.
