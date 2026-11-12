# Azure AI Native Governance

**What Azure's native applications DO govern — and where the per-tool-call gateway gap remains. A companion to the Microsoft 365 Governance Agent.**

> **Lab / portfolio project. SIMULATED Azure estate ("Nordlicht GmbH").**
> All data is synthetic. There is **no live Azure tenant access** and
> no claim that this is Microsoft's tooling. The user's Azure for
> Students subscription is live, but this lab project does **not** call
> it — the estate below is invented, so no real tenant, cost, or
> customer data is ever claimed. It demonstrates, in working code, what
> Azure native governance actually decides — and what it cannot.

## The problem in one paragraph

Azure native applications govern **resources, identity, network and
model content** — Azure Policy denies a VM in the wrong region,
Defender for Cloud scores the estate, Entra ID requires MFA, Key
Vault guards secrets, content filters block a jailbreak prompt. But
**none of them decides an individual MCP tool call**. You cannot ask
Azure Policy "may this agent delete this account right now, with
these arguments?" — it never sees the call. That per-tool-call
decision is the gap the Microsoft 365 Governance Agent gateway fills
(see `../m365-governance-agent/`).

## What it does

- **Simulated Azure estate** — 1 subscription, 4 resource groups
  (1 outside the allowed EU regions), 6 VMs, 8 storage accounts,
  3 Key Vaults, 4 Azure OpenAI / AI Foundry resources, 20 Entra users,
  6 Azure Policy assignments, Defender for Cloud (secure score 62%).
- **16 governance checks** — Azure Policy (allowed locations, public
  storage, encryption), Defender, Entra MFA / Conditional Access,
  Key Vault (secret expiry, RBAC, purge protection), Monitor /
  Sentinel logging, Azure OpenAI content filters, AI data residency,
  private endpoints, AI literacy (Art. 4), and the gap check AZ-16.
- **CAN / CANNOT per native service** — 10 native applications, each
  with an explicit list of what it can decide and what it cannot
  (`GET /native`). Every one of them admits it cannot decide a tool call.
- **Comparison table** — same question, three answers: Azure native vs
  Purview / Agent 365 vs the gateway (`GET /comparison`, 10 rows).
- **The gap, as data** — `GET /gap`: `native_decision_for_tool_call`
  is always `null`; the gateway decision is an OPA allow / deny /
  needs_approval per call.
- **Gateway demo** — `POST /agent/action`: returns BOTH decisions side
  by side (native: none; gateway: OPA / Python fallback), with a
  one-shot human-approval queue (approve → retry → allow).
- **OPA / Rego policy-as-code** — 8 Rego policies, real OPA over HTTP
  first, Python fallback second; every decision carries
  `engine: "opa" | "python-fallback"`.
- **ISO/IEC 42001 + EU AI Act mapping** — 28 controls mapped to
  ISO/IEC 42001 (A.2–A.10), EU AI Act Arts. 4/5/9–15/26, GDPR and
  ISO 27001 Annex A; 12 risks.
- **Audit evidence** — SHA-256 hash-chained evidence, JSON + CSV
  export for a GRC system of record (Archer / OneTrust), 6 SQL queries.

## Measured results (lab run, 10 Nov 2026)

Run `python -m scripts.demo` — see [`REPORT.md`](REPORT.md) for the full record.

| Measure | Result |
|---|---|
| pytest | **30 passed, 0 failed** |
| Governance checks | 16 run — **0 Pass, 8 Fail, 8 Partial** |
| Evidence chain | valid, 16 rows checked |
| Defender secure score | 62% |
| Public storage accounts | 2 of 8 |
| Expired Key Vault secrets | 4 |
| AI resources without content filter | 1 of 4 (aoai-test, eastus) |
| Users without MFA | 3 of 20 |
| Gateway: `azure.storage.read` | allow — native: **no decision** |
| Gateway: `azure.vm.start` | needs_approval → approved → allow — native: **no decision** |
| Gateway: `azure.keyvault.get_secret` (shadow agent) | **deny** — native: **no decision** |
| Gateway: social-scoring agent | **deny** (EU AI Act Art. 5) — native: **no decision** |

## Quick start

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python -m app.seed
uvicorn app.main:app --reload --port 8000
# Dashboard: http://127.0.0.1:8000
python -m scripts.demo        # end-to-end demo (uses TestClient, no server needed)
```

With real OPA (requires Docker, or an `opa` binary):

```bash
docker compose up --build    # governance agent :8000, OPA :8181
# or: opa run --server --addr localhost:8181 policies/
#     OPA_URL=http://localhost:8181 uvicorn app.main:app --port 8000
```

## Key API endpoints

| Endpoint | What it does |
|---|---|
| `GET /` / `GET /dashboard` | KRI dashboard (HTML) |
| `GET /dashboard/summary` | KRIs as JSON |
| `GET /resources`, `/vms`, `/storage`, `/keyvaults`, `/ai`, `/users` | Simulated Azure estate |
| `GET /policies`, `/defender` | Policy assignments, Defender findings |
| `GET /native`, `GET /native/{service}` | CAN / CANNOT per native application |
| `GET /comparison` | Azure native vs Purview/Agent 365 vs gateway |
| `GET /gap` | The per-tool-call gap, as data |
| `POST /tests/run` | Run all 16 checks, write hash-chained evidence |
| `POST /agent/action` | One tool call: native decision (none) + gateway OPA decision |
| `POST /classification/classify` | EU AI Act tier for a use case |
| `GET /approvals`, `POST /approvals/{id}/decide` | Human approval queue |
| `GET /evidence`, `GET /evidence/verify`, `GET /evidence/export.csv` | Evidence register, tamper check, export |
| `GET /audit/export` | Audit pack (JSON: evidence, issues, gap, comparison) |
| `POST /policy/evaluate`, `GET /policy/engine` | Evaluate any rule, see which engine decided |

## Architecture

One combined diagram — 6 layers + both data flows in a single picture:

![Architecture — one combined diagram](docs/architecture.png)

Details: [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) — regenerate with
`python3 scripts/make_diagrams.py`.

## Azure native vs Purview/Agent 365 vs gateway — the headline

| Question | Azure native | Purview / Agent 365 | Gateway (M365 project) |
|---|---|---|---|
| May this Azure resource exist here? | Azure Policy: Deny by region / SKU | Not applicable | Mirrors it (region + residency) |
| Is this storage / disk encrypted? | Policy + Defender: Audit/Deny | Purview labels (M365 content) | Checks the same estate |
| May this agent run at all? | Entra sign-in / Conditional Access | Agent 365 allow / block | Mirrors it |
| May this specific tool call happen, with these arguments, right now? | **No — no native application decides this** | **No per-tool MCP control** | **OPA decision per tool call** |
| Is the tool definition unchanged? | No hash pinning | Pin MCP versions (guidance) | SHA-256 pin check |
| Is a human approving this write? | No uniform gate | Copilot Studio workflow gates only | Uniform approval gate |
| What happened, in one audit trail? | Monitor / Sentinel (after the fact) | Purview audit log | One signed per-call log + hash chain |

## Honest limitations

- **Simulated estate.** `app/connectors/azure.py` is the seam: in a
  real tenant it would be replaced by Azure Resource Graph queries,
  Defender for Cloud API calls, Microsoft Graph (Entra ID) reads and
  Azure OpenAI management-plane calls. The governance logic above
  that layer would not change.
- **OPA was not running in this VM** (no `opa` binary, no Docker), so
  the live demo ran on the Python fallback. The OPA HTTP path is
  proven by tests against a fake OPA server speaking the same contract
  (`tests/test_opa.py`); `docker-compose.yml` (OPA 1.9.0) is provided
  and verified by reading, not by running.
- The Python fallback is a second implementation of the Rego rules;
  the two can drift. Rego files are kept short and mutually exclusive
  so OPA never returns two decisions for one input.
- This project is **not** Microsoft's product, not PwC's stack, and
  not a claim of production experience. It is a personal lab /
  portfolio project with synthetic data, and a companion to the
  Microsoft 365 Governance Agent — it does not duplicate it.

## Project layout

```
app/                FastAPI app, models, policy, evidence, checks, seed
app/connectors/     Simulated Azure estate (ARM / Defender / Graph shapes)
policies/           8 Rego policies (package azure_native.*)
tests/              30 pytest tests (api, policy, checks, opa, evidence, gateway)
scripts/            demo.py, make_diagrams.py, run.sh, run_with_opa.sh
sql/                6 audit queries
docs/               ARCHITECTURE.md, diagrams
infra/              Dockerfile
docker-compose.yml  governance agent + OPA 1.9.0
```

## License

MIT. Synthetic data only.
