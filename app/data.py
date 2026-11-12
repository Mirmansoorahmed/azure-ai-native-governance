"""Simulated Azure estate — "Nordlicht GmbH" (SIMULATED, synthetic data only).
No live Azure tenant access. The user's Azure for Students subscription is
live, but this lab project does NOT call it: all resources below are
invented, so no real tenant, cost, or customer data is ever claimed.

Estate shape mirrors what Azure Resource Graph / Defender for Cloud /
Entra ID would return in a real tenant; app/connectors/azure.py is the
seam where real ARM / Graph / Defender API calls would go.
"""
import json

TENANT_NAME = "Nordlicht GmbH (SIMULATED)"
SUBSCRIPTION = {
    "id": "sub-simulated-0001",
    "name": "Nordlicht GmbH — Azure (SIMULATED)",
    "type": "Azure for Students (simulated shape)",
    "regions_allowed": ["germanywestcentral", "westeurope"],
    "credit_note": "Lab copy only — simulated subscription, NOT a real subscription ID. No live calls are made.",
}
ALLOWED_REGIONS = ["germanywestcentral", "westeurope"]
ALLOWED_REGIONS_DISPLAY = ["Germany West Central", "West Europe"]

RESOURCE_GROUPS = [
    {"id": "rg-prod", "name": "rg-prod", "region": "germanywestcentral", "resources": 9},
    {"id": "rg-ai", "name": "rg-ai", "region": "germanywestcentral", "resources": 6},
    {"id": "rg-network", "name": "rg-network", "region": "westeurope", "resources": 4},
    {"id": "rg-test", "name": "rg-test", "region": "eastus", "resources": 3},  # outside allowed regions
]

VMS = [
    {"id": "vm-web-01", "name": "vm-web-01", "rg": "rg-prod", "region": "germanywestcentral", "disk_encrypted": True, "public_ip": False, "backup": True, "jit": True, "image": "Ubuntu 24.04 LTS"},
    {"id": "vm-web-02", "name": "vm-web-02", "rg": "rg-prod", "region": "germanywestcentral", "disk_encrypted": True, "public_ip": False, "backup": True, "jit": True, "image": "Ubuntu 24.04 LTS"},
    {"id": "vm-app-01", "name": "vm-app-01", "rg": "rg-prod", "region": "germanywestcentral", "disk_encrypted": False, "public_ip": False, "backup": True, "jit": False, "image": "Ubuntu 22.04 LTS"},
    {"id": "vm-db-01", "name": "vm-db-01", "rg": "rg-prod", "region": "germanywestcentral", "disk_encrypted": True, "public_ip": True, "backup": False, "jit": False, "image": "Windows Server 2022"},
    {"id": "vm-test-01", "name": "vm-test-01", "rg": "rg-test", "region": "eastus", "disk_encrypted": False, "public_ip": True, "backup": False, "jit": False, "image": "Ubuntu 20.04 LTS"},
    {"id": "vm-ai-01", "name": "vm-ai-01", "rg": "rg-ai", "region": "germanywestcentral", "disk_encrypted": True, "public_ip": False, "backup": True, "jit": True, "image": "Ubuntu 24.04 LTS"},
]

STORAGE = [
    {"id": "stnordlichtprod", "name": "stnordlichtprod", "rg": "rg-prod", "region": "germanywestcentral", "public_blob": False, "encryption": True, "tls_min": "1.2", "private_endpoint": True},
    {"id": "stnordlichtlogs", "name": "stnordlichtlogs", "rg": "rg-prod", "region": "germanywestcentral", "public_blob": False, "encryption": True, "tls_min": "1.2", "private_endpoint": True},
    {"id": "stnordlichtpub", "name": "stnordlichtpub", "rg": "rg-prod", "region": "germanywestcentral", "public_blob": True, "encryption": True, "tls_min": "1.2", "private_endpoint": False},
    {"id": "stnordlichtai", "name": "stnordlichtai", "rg": "rg-ai", "region": "germanywestcentral", "public_blob": False, "encryption": True, "tls_min": "1.2", "private_endpoint": True},
    {"id": "stnordlichtold", "name": "stnordlichtold", "rg": "rg-test", "region": "eastus", "public_blob": True, "encryption": False, "tls_min": "1.0", "private_endpoint": False},
    {"id": "stnordlichtbkp", "name": "stnordlichtbkp", "rg": "rg-prod", "region": "westeurope", "public_blob": False, "encryption": True, "tls_min": "1.2", "private_endpoint": False},
    {"id": "stnordlichtdev", "name": "stnordlichtdev", "rg": "rg-test", "region": "germanywestcentral", "public_blob": False, "encryption": True, "tls_min": "1.0", "private_endpoint": False},
    {"id": "stnordlichtarc", "name": "stnordlichtarc", "rg": "rg-prod", "region": "germanywestcentral", "public_blob": False, "encryption": True, "tls_min": "1.2", "private_endpoint": True},
]

KEYVAULTS = [
    {"id": "kv-nordlicht-prod", "name": "kv-nordlicht-prod", "rg": "rg-prod", "region": "germanywestcentral", "rbac": True, "purge_protection": True, "secrets_expired": 0, "secrets_total": 12, "private_endpoint": True},
    {"id": "kv-nordlicht-ai", "name": "kv-nordlicht-ai", "rg": "rg-ai", "region": "germanywestcentral", "rbac": True, "purge_protection": False, "secrets_expired": 1, "secrets_total": 6, "private_endpoint": True},
    {"id": "kv-nordlicht-old", "name": "kv-nordlicht-old", "rg": "rg-test", "region": "eastus", "rbac": False, "purge_protection": False, "secrets_expired": 3, "secrets_total": 5, "private_endpoint": False},
]

AI_RESOURCES = [
    {"id": "aoai-nordlicht", "name": "aoai-nordlicht", "kind": "Azure OpenAI", "rg": "rg-ai", "region": "germanywestcentral", "content_filter": True, "jailbreak_filter": True, "logging": True, "model": "gpt-4o", "data_residency": "EU"},
    {"id": "aif-nordlicht", "name": "aif-nordlicht", "kind": "Azure AI Foundry hub", "rg": "rg-ai", "region": "germanywestcentral", "content_filter": True, "jailbreak_filter": True, "logging": True, "model": "gpt-4o", "data_residency": "EU"},
    {"id": "acs-nordlicht", "name": "acs-nordlicht", "kind": "Azure AI Content Safety", "rg": "rg-ai", "region": "westeurope", "content_filter": True, "jailbreak_filter": True, "logging": False, "model": "content-safety", "data_residency": "EU"},
    {"id": "aoai-test", "name": "aoai-test", "kind": "Azure OpenAI (test)", "rg": "rg-test", "region": "eastus", "content_filter": False, "jailbreak_filter": False, "logging": False, "model": "gpt-4o-mini", "data_residency": "US"},
]

USERS = [
    {"user": "lena.vogel@nordlicht.example", "mfa": True, "ca_compliant": True, "ai_literacy": True, "role": "AI Governance"},
    {"user": "jonas.berg@nordlicht.example", "mfa": True, "ca_compliant": True, "ai_literacy": True, "role": "Cloud Engineer"},
    {"user": "mira.hoff@nordlicht.example", "mfa": True, "ca_compliant": True, "ai_literacy": False, "role": "Data Analyst"},
    {"user": "admin@nordlicht.example", "mfa": True, "ca_compliant": True, "ai_literacy": True, "role": "Global Admin"},
    {"user": "test.user@nordlicht.example", "mfa": False, "ca_compliant": False, "ai_literacy": False, "role": "Test"},
    {"user": "guest@nordlicht.example", "mfa": False, "ca_compliant": False, "ai_literacy": False, "role": "Guest"},
    {"user": "sara.k@nordlicht.example", "mfa": True, "ca_compliant": True, "ai_literacy": True, "role": "Security"},
    {"user": "omar.h@nordlicht.example", "mfa": True, "ca_compliant": False, "ai_literacy": True, "role": "Developer"},
    {"user": "anna.l@nordlicht.example", "mfa": True, "ca_compliant": True, "ai_literacy": False, "role": "HR"},
    {"user": "peter.m@nordlicht.example", "mfa": True, "ca_compliant": True, "ai_literacy": True, "role": "Finance"},
    {"user": "julia.r@nordlicht.example", "mfa": False, "ca_compliant": True, "ai_literacy": True, "role": "Marketing"},
    {"user": "karim.s@nordlicht.example", "mfa": True, "ca_compliant": True, "ai_literacy": True, "role": "Developer"},
    {"user": "emma.w@nordlicht.example", "mfa": True, "ca_compliant": True, "ai_literacy": False, "role": "Support"},
    {"user": "david.k@nordlicht.example", "mfa": True, "ca_compliant": True, "ai_literacy": True, "role": "Auditor"},
    {"user": "nina.b@nordlicht.example", "mfa": True, "ca_compliant": True, "ai_literacy": True, "role": "Legal"},
    {"user": "tomas.z@nordlicht.example", "mfa": True, "ca_compliant": True, "ai_literacy": True, "role": "DevOps"},
    {"user": "lea.f@nordlicht.example", "mfa": True, "ca_compliant": True, "ai_literacy": False, "role": "Intern"},
    {"user": "max.g@nordlicht.example", "mfa": True, "ca_compliant": True, "ai_literacy": True, "role": "Developer"},
    {"user": "sofia.d@nordlicht.example", "mfa": True, "ca_compliant": True, "ai_literacy": True, "role": "Product"},
    {"user": "lukas.p@nordlicht.example", "mfa": True, "ca_compliant": True, "ai_literacy": True, "role": "IT Support"},
]

POLICY_ASSIGNMENTS = [
    {"id": "pol-allowed-locations", "name": "Allowed locations", "effect": "Deny", "scope": "subscription", "compliant": 21, "non_compliant": 3},
    {"id": "pol-deny-public-storage", "name": "Storage accounts should not allow public blob access", "effect": "Deny", "scope": "subscription", "compliant": 6, "non_compliant": 2},
    {"id": "pol-require-encryption", "name": "Require encryption (storage + disks)", "effect": "Audit", "scope": "subscription", "compliant": 11, "non_compliant": 3},
    {"id": "pol-require-tls12", "name": "Minimum TLS 1.2 for storage", "effect": "Deny", "scope": "rg-prod", "compliant": 5, "non_compliant": 2},
    {"id": "pol-keyvault-purge", "name": "Key Vault purge protection", "effect": "Audit", "scope": "subscription", "compliant": 1, "non_compliant": 2},
    {"id": "pol-private-endpoint", "name": "Private endpoints for PaaS", "effect": "Audit", "scope": "rg-prod", "compliant": 4, "non_compliant": 4},
]

DEFENDER = {
    "secure_score_pct": 62,
    "secure_score_max": 100,
    "recommendations_open": 14,
    "recommendations_high": 5,
    "findings": [
        {"id": "df-01", "title": "Machines should have disk encryption enabled", "severity": "High", "resource": "vm-app-01"},
        {"id": "df-02", "title": "Storage accounts should not allow public blob access", "severity": "High", "resource": "stnordlichtpub"},
        {"id": "df-03", "title": "Key Vault secrets should have an expiry date", "severity": "Medium", "resource": "kv-nordlicht-old"},
        {"id": "df-04", "title": "MFA should be enabled for all users", "severity": "High", "resource": "Entra ID"},
        {"id": "df-05", "title": "VMs should not have public IP addresses", "severity": "Medium", "resource": "vm-db-01"},
        {"id": "df-06", "title": "Private endpoints should be used for PaaS", "severity": "Medium", "resource": "stnordlichtbkp"},
        {"id": "df-07", "title": "Azure OpenAI should have content filtering enabled", "severity": "High", "resource": "aoai-test"},
        {"id": "df-08", "title": "Audit logging should be enabled for AI resources", "severity": "Medium", "resource": "acs-nordlicht"},
    ],
}

# Agents that would call Azure / MCP tools — same agents as the M365 project,
# so the gap demo is directly comparable.
AGENTS = [
    {"agent_id": "finance-assistant", "name": "Finance Assistant", "status": "active", "sponsor": "peter.m@nordlicht.example", "tools": ["azure.storage.read", "azure.openai.chat", "finance.read_report"], "eu_tier": "limited"},
    {"agent_id": "sales-assistant", "name": "Sales Assistant", "status": "active", "sponsor": "sara.k@nordlicht.example", "tools": ["azure.openai.chat", "crm.send_email"], "eu_tier": "limited"},
    {"agent_id": "ops-agent", "name": "Ops Agent", "status": "active", "sponsor": "tomas.z@nordlicht.example", "tools": ["azure.vm.start", "azure.vm.stop", "azure.storage.read"], "eu_tier": "minimal"},
    {"agent_id": "shadow-notes", "name": "Shadow Notes Agent", "status": "blocked", "sponsor": None, "tools": ["azure.keyvault.get_secret", "notes.export_all"], "eu_tier": "minimal"},
    {"agent_id": "social-scoring-pilot", "name": "Social Scoring Pilot", "status": "blocked", "sponsor": None, "tools": ["crm.score_customer"], "eu_tier": "prohibited"},
    {"agent_id": "hr-screening", "name": "HR Screening Agent", "status": "review", "sponsor": "anna.l@nordlicht.example", "tools": ["azure.openai.chat", "hr.rank_applicant"], "eu_tier": "high-risk"},
]

AGENT_ALLOWLIST = {
    "finance-assistant": ["azure.storage.read", "azure.openai.chat", "finance.read_report"],
    "sales-assistant": ["azure.openai.chat", "crm.send_email"],
    "ops-agent": ["azure.vm.start", "azure.vm.stop", "azure.storage.read"],
    "hr-screening": ["azure.openai.chat", "hr.rank_applicant"],
}
TOOLS_REQUIRING_APPROVAL = ["azure.vm.start", "azure.vm.stop", "azure.keyvault.get_secret", "crm.send_email", "hr.rank_applicant"]
RECIPIENT_ALLOWLIST = ["lena.vogel@nordlicht.example", "jonas.berg@nordlicht.example", "mira.hoff@nordlicht.example"]

RISKS = [
    {"code": "R-01", "title": "Resources deployed outside allowed EU regions", "likelihood": 3, "impact": 4, "category": "Data residency", "frameworks": "ISO 42001 A.5; EU AI Act Art. 26; GDPR", "description": "A resource group in eastus breaks the EU data-boundary decision and the allowed-locations policy."},
    {"code": "R-02", "title": "Public storage exposes data at AI speed", "likelihood": 4, "impact": 5, "category": "Data protection", "frameworks": "ISO 42001 A.6; ISO 27001 A.8; GDPR Art. 32", "description": "Public blob access makes data retrievable by anyone — and by any Copilot/agent that can reach it."},
    {"code": "R-03", "title": "Unencrypted disks / storage", "likelihood": 3, "impact": 4, "category": "Data protection", "frameworks": "ISO 42001 A.6; ISO 27001 A.8", "description": "Data at rest without encryption fails Azure Policy and ISO 27001 Annex A controls."},
    {"code": "R-04", "title": "VMs exposed to the internet", "likelihood": 4, "impact": 4, "category": "Network security", "frameworks": "ISO 42001 A.6; ISO 27001 A.8; NIS2", "description": "Public IPs without just-in-time access widen the attack surface for the whole estate."},
    {"code": "R-05", "title": "Secrets without expiry / RBAC in Key Vault", "likelihood": 3, "impact": 5, "category": "Identity & secrets", "frameworks": "ISO 42001 A.6; ISO 27001 A.8", "description": "Expired or over-shared secrets can be used by an agent long after they should have been rotated."},
    {"code": "R-06", "title": "Identity without MFA / Conditional Access", "likelihood": 4, "impact": 5, "category": "Identity", "frameworks": "ISO 42001 A.6; ISO 27001 A.5; NIS2", "description": "3 of 20 users have no MFA; a compromised identity can drive Azure and agent actions."},
    {"code": "R-07", "title": "AI model without content filters or logging", "likelihood": 3, "impact": 4, "category": "AI safety", "frameworks": "ISO 42001 A.7/A.8; EU AI Act Arts. 9, 12, 15", "description": "The test Azure OpenAI resource has no jailbreak filter and no logging — harmful output and prompt injection go unseen."},
    {"code": "R-08", "title": "AI data processed outside the EU", "likelihood": 2, "impact": 5, "category": "Data residency", "frameworks": "ISO 42001 A.5; EU AI Act; GDPR", "description": "aoai-test runs in eastus (US) with no documented approval — EU Data Boundary decision is broken."},
    {"code": "R-09", "title": "No audit trail for agent / AI actions", "likelihood": 3, "impact": 4, "category": "Audit & accountability", "frameworks": "ISO 42001 A.8/A.9; EU AI Act Art. 12", "description": "AI resources without logging cannot prove what a model or agent did, when, or for whom."},
    {"code": "R-10", "title": "Per-tool-call decisions are invisible to native controls", "likelihood": 5, "impact": 4, "category": "Agent governance (GAP)", "frameworks": "ISO 42001 A.7; EU AI Act Arts. 9, 14", "description": "No Azure native application decides an individual MCP tool call. This is the gap the M365 Governance Agent gateway fills."},
    {"code": "R-11", "title": "Policy in Audit mode only — no enforcement", "likelihood": 3, "impact": 3, "category": "Governance", "frameworks": "ISO 42001 A.5/A.9", "description": "Encryption and purge-protection policies are Audit-only: violations are reported, not blocked."},
    {"code": "R-12", "title": "No private endpoints on PaaS data stores", "likelihood": 3, "impact": 3, "category": "Network security", "frameworks": "ISO 42001 A.6; ISO 27001 A.8", "description": "Storage and Key Vault without private endpoints are reachable over the public network path."},
]

CONTROLS = [
    {"code": "A-01", "title": "Azure Policy: allowed locations (EU only)", "risk_code": "R-01", "frameworks": "ISO 42001 A.5; EU AI Act Art. 26; GDPR", "owner": "Cloud Governance", "description": "Deny policy: resources may only be created in germanywestcentral / westeurope."},
    {"code": "A-02", "title": "Azure Policy: deny public blob access", "risk_code": "R-02", "frameworks": "ISO 42001 A.6; ISO 27001 A.8.2", "owner": "Cloud Governance", "description": "Deny policy: storage accounts must not allow public blob access."},
    {"code": "A-03", "title": "Encryption at rest + TLS 1.2 minimum", "risk_code": "R-03", "frameworks": "ISO 42001 A.6; ISO 27001 A.8.24", "owner": "Cloud Engineering", "description": "Storage encryption on, disks encrypted, TLS >= 1.2."},
    {"code": "A-04", "title": "VMs: no public IP without JIT access", "risk_code": "R-04", "frameworks": "ISO 42001 A.6; ISO 27001 A.8.20", "owner": "Cloud Engineering", "description": "Public IPs only with just-in-time VM access; otherwise denied."},
    {"code": "A-05", "title": "Key Vault: secrets expire, RBAC, purge protection", "risk_code": "R-05", "frameworks": "ISO 42001 A.6; ISO 27001 A.8.2", "owner": "Identity & Secrets", "description": "Every secret has an expiry, RBAC replaces access policies, purge protection on."},
    {"code": "A-06", "title": "Entra ID: MFA for all users", "risk_code": "R-06", "frameworks": "ISO 42001 A.6; ISO 27001 A.5.17", "owner": "Identity", "description": "MFA enforced; no user without MFA in production scope."},
    {"code": "A-07", "title": "Entra ID: Conditional Access compliance", "risk_code": "R-06", "frameworks": "ISO 42001 A.6; ISO 27001 A.5.15", "owner": "Identity", "description": "Conditional Access policies cover all users, incl. guests."},
    {"code": "A-08", "title": "Defender for Cloud: secure score >= 80%", "risk_code": "R-04", "frameworks": "ISO 42001 A.8; ISO 27001 A.8.16", "owner": "Security Operations", "description": "Secure score tracked; high-severity recommendations remediated."},
    {"code": "A-09", "title": "Azure Monitor / Sentinel: audit logging on", "risk_code": "R-09", "frameworks": "ISO 42001 A.8; EU AI Act Art. 12", "owner": "Security Operations", "description": "Diagnostic settings + Sentinel cover all AI and PaaS resources."},
    {"code": "A-10", "title": "Azure OpenAI: content + jailbreak filters on", "risk_code": "R-07", "frameworks": "ISO 42001 A.7/A.8; EU AI Act Art. 15", "owner": "AI Governance", "description": "Content filters and jailbreak detection enabled on every Azure OpenAI deployment."},
    {"code": "A-11", "title": "AI data residency: EU only, documented exceptions", "risk_code": "R-08", "frameworks": "ISO 42001 A.5; EU AI Act; GDPR", "owner": "AI Governance", "description": "AI processing stays in the EU Data Boundary unless a documented exception exists."},
    {"code": "A-12", "title": "AI logging and traceability (Art. 12)", "risk_code": "R-09", "frameworks": "ISO 42001 A.8; EU AI Act Art. 12", "owner": "AI Governance", "description": "Every AI interaction is logged with who / what / when / which model."},
    {"code": "A-13", "title": "Network: private endpoints for PaaS", "risk_code": "R-12", "frameworks": "ISO 42001 A.6; ISO 27001 A.8.20", "owner": "Network", "description": "Storage, Key Vault and AI resources reachable only via private endpoints."},
    {"code": "A-14", "title": "Policy effect: Deny, not Audit-only, for critical rules", "risk_code": "R-11", "frameworks": "ISO 42001 A.5/A.9", "owner": "Cloud Governance", "description": "Critical policies (encryption, purge protection) must Deny, not merely Audit."},
    {"code": "A-15", "title": "Agent registry: every agent has a sponsor", "risk_code": "R-10", "frameworks": "ISO 42001 A.5; EU AI Act Art. 26", "owner": "AI Governance", "description": "No ownerless agent may call Azure or MCP tools (mirrors Entra Agent ID)."},
    {"code": "A-16", "title": "Per-tool-call decision (GAP — gateway only)", "risk_code": "R-10", "frameworks": "ISO 42001 A.7; EU AI Act Arts. 9, 14", "owner": "AI Governance", "description": "Each individual tool call gets an OPA decision (allow / deny / needs_approval). No Azure native application does this."},
    {"code": "A-17", "title": "Tool pinning: SHA-256 hash per tool (GAP — gateway only)", "risk_code": "R-10", "frameworks": "ISO 42001 A.7; EU AI Act Art. 9", "owner": "AI Governance", "description": "A changed tool definition is denied until re-reviewed. Native controls pin versions only as guidance."},
    {"code": "A-18", "title": "Uniform human approval for agent writes (GAP — gateway only)", "risk_code": "R-10", "frameworks": "ISO 42001 A.7; EU AI Act Art. 14", "owner": "AI Governance", "description": "One approval gate for every agent write, whatever the builder. Native approval exists only inside Copilot Studio flows."},
    {"code": "A-19", "title": "EU AI Act classification at intake", "risk_code": "R-07", "frameworks": "ISO 42001 A.4; EU AI Act Arts. 4, 5, 9-15", "owner": "AI Governance", "description": "Every AI use case is classified prohibited / high-risk / limited / minimal before it is built."},
    {"code": "A-20", "title": "AI literacy (Art. 4) for all users", "risk_code": "R-07", "frameworks": "ISO 42001 A.4; EU AI Act Art. 4", "owner": "AI Governance", "description": "All users who use AI complete AI-literacy training."},
    {"code": "A-21", "title": "Works-council check for employee-monitoring AI", "risk_code": "R-07", "frameworks": "ISO 42001 A.5; BetrVG s.87(1) No. 6; EU AI Act Art. 26(7)", "owner": "Legal / AI Governance", "description": "AI that logs employee prompts or scores staff needs a works agreement before rollout."},
    {"code": "A-22", "title": "Backup and recovery for VMs and data", "risk_code": "R-04", "frameworks": "ISO 42001 A.6; ISO 27001 A.8.13", "owner": "Cloud Engineering", "description": "Backup enabled and tested for production VMs and storage."},
    {"code": "A-23", "title": "Secrets rotation (Key Vault)", "risk_code": "R-05", "frameworks": "ISO 42001 A.6; ISO 27001 A.8.2", "owner": "Identity & Secrets", "description": "Secrets are rotated before expiry; expired secrets are removed."},
    {"code": "A-24", "title": "Defender recommendations: high severity closed", "risk_code": "R-04", "frameworks": "ISO 42001 A.8; ISO 27001 A.8.16", "owner": "Security Operations", "description": "All high-severity Defender recommendations have an owner and a due date."},
    {"code": "A-25", "title": "AI model inventory and versioning", "risk_code": "R-09", "frameworks": "ISO 42001 A.8; EU AI Act Art. 12", "owner": "AI Governance", "description": "Every deployed model is inventoried with version, purpose and owner."},
    {"code": "A-26", "title": "Cost and credit guardrails (Azure for Students)", "risk_code": "R-11", "frameworks": "ISO 42001 A.5", "owner": "Cloud Governance", "description": "Spending alerts and budgets prevent runaway cost on the student subscription."},
    {"code": "A-27", "title": "Evidence: one hash-chained log per check", "risk_code": "R-09", "frameworks": "ISO 42001 A.8/A.9; EU AI Act Art. 12", "owner": "AI Governance", "description": "Every check writes hash-chained evidence exportable to a GRC system of record."},
    {"code": "A-28", "title": "Third-party / marketplace services register", "risk_code": "R-10", "frameworks": "ISO 42001 A.5; EU AI Act Art. 28 (DORA-style)", "owner": "Cloud Governance", "description": "Every third-party Azure service is registered with owner and risk rating."},
]

# --- What each native application CAN and CANNOT decide -------------------
NATIVE_CAPABILITIES = [
    {"service": "Azure Policy", "layer": "Azure resources (ARM)", "governs": "Resource creation and configuration",
     "can": ["Deny a VM/storage in a disallowed region", "Deny public blob access at creation", "Require tags, SKUs, encryption settings", "Audit non-compliant resources"],
     "cannot": ["Decide an individual MCP tool call", "See a prompt, a tool argument, or a recipient", "Approve a single agent write", "Pin a tool definition by hash"],
     "enforcement": "ARM deployment / evaluation (Deny, Audit, AuditIfNotExists)", "evidence": "Policy compliance states, Resource Graph"},
    {"service": "Microsoft Defender for Cloud", "layer": "Azure workloads", "governs": "Posture, vulnerabilities, threats",
     "can": ["Score the estate (secure score)", "Flag unencrypted disks, public IPs, missing MFA", "Detect threats and recommend fixes"],
     "cannot": ["Block a single tool call in real time", "Decide allow/deny per agent action", "Approve a write", "Know what an agent intended to do"],
     "enforcement": "Recommendations + alerts (no inline blocking of agent calls)", "evidence": "Secure score, recommendations, alerts"},
    {"service": "Microsoft Entra ID", "layer": "Identity", "governs": "Who may sign in, and under what conditions",
     "can": ["Require MFA and Conditional Access", "Block a sign-in from a risky location", "Give an agent an identity (Entra Agent ID) + sponsor"],
     "cannot": ["Decide an individual tool call for a signed-in agent", "Check tool arguments or recipients", "Approve one specific write", "Pin a tool"],
     "enforcement": "Token issuance / refresh (Conditional Access)", "evidence": "Sign-in logs, audit logs"},
    {"service": "Azure Key Vault", "layer": "Secrets / keys / certificates", "governs": "Who may read a secret",
     "can": ["RBAC: who may read / write a secret", "Expire secrets, purge protection", "Log every secret access"],
     "cannot": ["Decide the tool call that uses the secret it just read", "Check what the agent does with the secret afterwards", "Approve the downstream tool call"],
     "enforcement": "Data-plane RBAC at secret-read time", "evidence": "Key Vault diagnostic logs"},
    {"service": "Azure Monitor / Microsoft Sentinel", "layer": "Logs / SIEM", "governs": "What happened, and alerting on it",
     "can": ["Collect logs from Azure + AI resources", "Alert on anomalies, correlate incidents", "Retain logs for audit"],
     "cannot": ["Decide before a tool call happens", "Block a call (it sees it after the fact)", "Approve a write"],
     "enforcement": "After-the-fact detection and response (SOAR)", "evidence": "Log Analytics, Sentinel incidents"},
    {"service": "Azure OpenAI / AI Foundry content filters", "layer": "Model input / output", "governs": "Harmful content in prompts and responses",
     "can": ["Block jailbreak / hate / sexual / violent content", "Filter a prompt or a response", "Log content-filter triggers"],
     "cannot": ["Decide a tool call (read vs delete vs export)", "Check a recipient, an amount, or a file path in tool arguments", "Require human approval for a write", "Pin a tool definition"],
     "enforcement": "Model call time (prompt/response filtering)", "evidence": "Content-filter logs (where enabled)"},
    {"service": "Azure AI Foundry / Agent Service", "layer": "AI agents (Azure-hosted)", "governs": "Agent runtime, tools, threads",
     "can": ["Register an agent and its tools", "Run an agent with a model + tools", "Apply content filters to its calls"],
     "cannot": ["Give a per-tool-call OPA decision with arguments + session history", "Enforce one uniform approval gate across builders", "Hash-pin a tool definition"],
     "enforcement": "Agent runtime (tool execution)", "evidence": "Agent run logs, threads"},
    {"service": "Network — NSG / Private Link / Firewall", "layer": "Network", "governs": "Which network paths exist",
     "can": ["Block a port / IP range", "Force PaaS traffic over a private endpoint", "Inspect traffic at the firewall"],
     "cannot": ["Decide whether a permitted network call is a safe tool call", "Read tool arguments", "Approve a write"],
     "enforcement": "Network packet / connection level", "evidence": "NSG flow logs, Firewall logs"},
    {"service": "Microsoft Purview (M365 side)", "layer": "M365 data", "governs": "Labels, DLP, retention, audit of Copilot data",
     "can": ["Block Copilot from processing labelled content", "Retain and eDiscover Copilot interactions", "Report oversharing (DSPM)"],
     "cannot": ["Decide an individual MCP tool call", "Block a whole MCP server per tool", "Approve one agent write"],
     "enforcement": "DLP / label enforcement at the M365 service", "evidence": "Purview audit log, DSPM reports"},
    {"service": "Agent 365 / Entra Agent ID (M365 side)", "layer": "Agents (M365)", "governs": "Agent inventory, identity, sponsor",
     "can": ["Allow / block / deploy an agent", "Give it an identity and a human sponsor", "Apply Conditional Access to agents"],
     "cannot": ["Decide an individual tool call", "Check tool arguments", "Require approval per write"],
     "enforcement": "Registry + identity (allow/block at agent level)", "evidence": "Agent 365 registry, Entra logs"},
]

# --- Comparison: same question, three answers ------------------------------
COMPARISON = [
    {"question": "Which agent is this, who is accountable?",
     "azure_native": "Entra ID: identity + sponsor (Entra Agent ID)",
     "purview_agent365": "Entra Agent ID + Agent 365 registry",
     "gateway": "Mirrors it (registry, sponsor, blueprint) — same as M365 project"},
    {"question": "May this Azure resource exist here at all?",
     "azure_native": "Azure Policy: Deny by region / SKU / setting",
     "purview_agent365": "Not applicable (M365 data, not ARM resources)",
     "gateway": "Mirrors it for AI resources (region + residency checks)"},
    {"question": "Is this storage / disk encrypted, is this secret expired?",
     "azure_native": "Azure Policy + Defender for Cloud: Audit/Deny + recommendations",
     "purview_agent365": "Purview labels / DLP (M365 content, not Azure disks)",
     "gateway": "Checks the same estate and writes hash-chained evidence"},
    {"question": "May this agent run at all?",
     "azure_native": "Entra ID sign-in / Conditional Access; Foundry agent runtime",
     "purview_agent365": "Agent 365 allow / block / deploy",
     "gateway": "Mirrors it (active / review / blocked)"},
    {"question": "Which systems may it connect to?",
     "azure_native": "NSG / Private Link / Firewall (network paths); RBAC (data plane)",
     "purview_agent365": "Power Platform DLP connector groups",
     "gateway": "Mirrors it (Business / Non-business / Blocked)"},
    {"question": "May this specific tool call happen, with these arguments, right now?",
     "azure_native": "NO — no native application decides this",
     "purview_agent365": "NO — no per-tool MCP control",
     "gateway": "YES — OPA decision per tool call (allow / deny / needs_approval)"},
    {"question": "Is the tool definition unchanged?",
     "azure_native": "No hash pinning; version pinning is guidance only",
     "purview_agent365": "Pin MCP versions (guidance)",
     "gateway": "SHA-256 pin check in the gateway"},
    {"question": "Is a human approving this write?",
     "azure_native": "No uniform gate; approval only inside a specific workflow",
     "purview_agent365": "Copilot Studio workflow gates (inside flows only)",
     "gateway": "Uniform approval gate for every write tool"},
    {"question": "What happened, in one audit trail?",
     "azure_native": "Monitor / Sentinel logs + Defender alerts (after the fact)",
     "purview_agent365": "Purview audit log + Entra logs + Defender",
     "gateway": "One signed per-call decision log + hash-chained evidence"},
    {"question": "Does this satisfy the framework (ISO 42001 / EU AI Act)?",
     "azure_native": "Partially — controls exist, but no single per-call decision record",
     "purview_agent365": "Purview Compliance Manager (Microsoft scope only)",
     "gateway": "Export to Archer / OneTrust (GRC system of record)"},
]

# The gap, stated as a testable claim.
GAP = {
    "headline": "Azure native applications govern resources, identity, network and model content — none of them decides an individual MCP tool call.",
    "native_decision_for_tool_call": None,
    "gateway_decision_for_tool_call": "OPA allow / deny / needs_approval, per call, with arguments, session history and a hash-pinned tool definition.",
    "examples": [
        {"tool": "azure.storage.read", "native": "RBAC allows the read if the identity has the role — no check of why, or what happens next.", "gateway": "allow — read is allowlisted for this agent."},
        {"tool": "azure.keyvault.get_secret", "native": "Key Vault RBAC allows the read; it cannot stop the agent using the secret to exfiltrate data.", "gateway": "needs_approval — secrets always require human approval."},
        {"tool": "azure.vm.start", "native": "Azure Policy allows the VM to exist; it cannot approve starting it right now.", "gateway": "needs_approval — starting a VM is a write."},
        {"tool": "crm.delete_account", "native": "No Azure native application sees this MCP tool call at all.", "gateway": "deny — delete is not allowlisted for this agent."},
        {"tool": "azure.openai.chat (jailbreak prompt)", "native": "Content filter can block the harmful prompt — but cannot decide the tool call that follows it.", "gateway": "needs_approval — arguments came from untrusted content."},
    ],
}
