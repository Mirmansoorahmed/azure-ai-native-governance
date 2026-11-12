#!/usr/bin/env python3
"""Azure AI Native Governance — architecture diagram v1.2.

TRUE project content only. Source of truth is the project's own code:
app/data.py and app/checks.py. Nothing in this picture is invented:
no Application Gateway, no Azure Firewall as a deployed resource,
no Azure Web App / Function App / Queue service, no Redis, Cosmos DB,
SQL Database, Blob or Azure AI Search as separate services, no VNet
topology, no Microsoft Foundry project box, no Foundry Agent Service
dependencies box, no DDoS Protection, no Application Insights.

What IS shown (all from data.py / checks.py):
- 6 agents, 10 native services (CAN/CANNOT), simulated estate
  "Nordlicht GmbH" (4 RGs, 6 VMs, 8 storage accounts, 3 Key Vaults,
  4 AI resources, 20 Entra users, 6 Policy assignments, Defender 62%),
- gateway: FastAPI app (local lab, NOT an Azure service), agent
  registry, OPA :8181 with 8 Rego policies + Python fallback,
  one-shot human-approval queue, SHA-256 hash-chained evidence,
  audit export JSON+CSV for Archer/OneTrust, 6 SQL audit queries,
- 16 checks AZ-01..AZ-16 (0 Pass, 8 Fail, 8 Partial, verified by
  running app.checks.run_all_checks()), 28 controls, 12 risks,
- demo: azure.storage.read -> allow; azure.vm.start ->
  needs_approval -> approved -> allow; shadow agent
  azure.keyvault.get_secret -> deny; social scoring -> deny
  (EU AI Act Art. 5); native decision in every case: none.

Design inspiration only (from the user's reference picture):
white background, thin blue lines, clean small line icons,
numbered green steps 1-5, generous white space.

Regenerate:
    cd ~/workspace/projects/azure-native-governance
    python3 scripts/make_foundry_style_diagram.py

Outputs:
    docs/architecture-foundry-style.svg
    docs/architecture-foundry-style.png  (4800 px wide)
"""
from __future__ import annotations

import cairosvg

OUT_SVG = "docs/architecture-foundry-style.svg"
OUT_PNG = "docs/architecture-foundry-style.png"

W, H = 2400, 2120
BLUE = "#0078D4"
DARK = "#0F2A44"
NAVY = "#1B3A5C"
TEAL = "#107C10"
AMBER = "#9D5D00"
AMBER_BG = "#FFF4D6"
AMBER_LINE = "#C77F0A"
LIGHT = "#EAF4FB"
LIGHT2 = "#F2F8FD"
GREY = "#5A6B7B"
RED = "#C42B1C"

E = []


def add(s: str) -> None:
    E.append(s)


def esc(t: str) -> str:
    return t.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def text(x, y, s, size=20, weight="normal", fill=DARK, anchor="start"):
    add(f'<text x="{x}" y="{y}" font-family="DejaVu Sans, sans-serif" '
        f'font-size="{size}" font-weight="{weight}" fill="{fill}" '
        f'text-anchor="{anchor}">{esc(s)}</text>')


def line(x1, y1, x2, y2, color=BLUE, w=2, dash=""):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    add(f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{color}" '
        f'stroke-width="{w}"{d} />')


def arrow(x1, y1, x2, y2, color=BLUE, w=2):
    add(f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{color}" '
        f'stroke-width="{w}" marker-end="url(#arr)" />')


def box(x, y, w, h, fill="#FFFFFF", stroke=BLUE, sw=1.5, dash="", rx=6):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    add(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" '
        f'fill="{fill}" stroke="{stroke}" stroke-width="{sw}"{d} />')


def step(n, x, y):
    add(f'<circle cx="{x}" cy="{y}" r="17" fill="{TEAL}" />')
    text(x, y + 6, str(n), size=20, weight="bold", fill="#FFFFFF", anchor="middle")


def icon(name, x, y, color=BLUE):
    s = 2.0
    p = f'<g stroke="{color}" stroke-width="{s}" fill="none" stroke-linecap="round" stroke-linejoin="round">'
    if name == "user":
        p += (f'<circle cx="{x+22}" cy="{y+15}" r="7" />'
              f'<path d="M {x+8} {y+38} C {x+8} {y+28}, {x+36} {y+28}, {x+36} {y+38}" />')
    elif name == "shield":
        p += (f'<path d="M {x+22} {y+5} L {x+37} {y+11} V {y+22} '
              f'C {x+37} {y+32}, {x+22} {y+39}, {x+22} {y+39} '
              f'C {x+22} {y+39}, {x+7} {y+32}, {x+7} {y+22} V {y+11} Z" />'
              f'<path d="M {x+16} {y+21} l 4 4 l 8 -9" />')
    elif name == "key":
        p += (f'<circle cx="{x+14}" cy="{y+16}" r="8" />'
              f'<line x1="{x+20}" y1="{y+22}" x2="{x+36}" y2="{y+38}" />'
              f'<line x1="{x+30}" y1="{y+32}" x2="{x+36}" y2="{y+26}" />')
    elif name == "db":
        p += (f'<ellipse cx="{x+22}" cy="{y+11}" rx="14" ry="5" />'
              f'<path d="M {x+8} {y+11} V {y+33} C {x+8} {y+36}, {x+36} {y+36}, {x+36} {y+33} V {y+11}" />'
              f'<path d="M {x+8} {y+22} C {x+8} {y+25}, {x+36} {y+25}, {x+36} {y+22}" />')
    elif name == "search":
        p += (f'<circle cx="{x+19}" cy="{y+19}" r="11" />'
              f'<line x1="{x+27}" y1="{y+27}" x2="{x+37}" y2="{y+37}" />')
    elif name == "spark":
        p += (f'<path d="M {x+22} {y+4} L {x+26} {y+18} L {x+40} {y+22} '
              f'L {x+26} {y+26} L {x+22} {y+40} L {x+18} {y+26} '
              f'L {x+4} {y+22} L {x+18} {y+18} Z" />')
    elif name == "bolt":
        p += f'<path d="M {x+25} {y+4} L {x+12} {y+24} H {x+21} L {x+18} {y+40} L {x+33} {y+19} H {x+23} Z" />'
    elif name == "monitor":
        p += (f'<rect x="{x+5}" y="{y+8}" width="34" height="24" rx="2" />'
              f'<line x1="{x+13}" y1="{y+26}" x2="{x+13}" y2="{y+18}" />'
              f'<line x1="{x+22}" y1="{y+26}" x2="{x+22}" y2="{y+13}" />'
              f'<line x1="{x+31}" y1="{y+26}" x2="{x+31}" y2="{y+21}" />'
              f'<line x1="{x+17}" y1="{y+37}" x2="{x+27}" y2="{y+37}" />')
    elif name == "lock":
        p += (f'<rect x="{x+9}" y="{y+19}" width="26" height="19" rx="2" />'
              f'<path d="M {x+14} {y+19} V {y+13} a 8 8 0 0 1 16 0 V {y+19}" />')
    elif name == "app":
        p += (f'<rect x="{x+6}" y="{y+6}" width="32" height="32" rx="4" />'
              f'<path d="M {x+6} {y+17} H {x+38}" />'
              f'<circle cx="{x+12}" cy="{y+11}" r="1.6" fill="{color}" />'
              f'<circle cx="{x+18}" cy="{y+11}" r="1.6" fill="{color}" />')
    elif name == "doc":
        p += (f'<path d="M {x+11} {y+5} H {x+28} L {x+36} {y+13} V {y+39} H {x+11} Z" />'
              f'<path d="M {x+28} {y+5} V {y+13} H {x+36}" />'
              f'<line x1="{x+16}" y1="{y+21}" x2="{x+31}" y2="{y+21}" />'
              f'<line x1="{x+16}" y1="{y+28}" x2="{x+31}" y2="{y+28}" />')
    p += '</g>'
    add(p)


def build():
    add(f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" '
        f'viewBox="0 0 {W} {H}">')
    add('<defs><marker id="arr" viewBox="0 0 10 10" refX="9" refY="5" '
        'markerWidth="7" markerHeight="7" orient="auto-start-reverse">'
        f'<path d="M 0 0 L 10 5 L 0 10 z" fill="{BLUE}" /></marker></defs>')
    add(f'<rect width="{W}" height="{H}" fill="#FFFFFF" />')

    # ---------- title ----------
    text(40, 52, "Azure AI Native Governance — Architecture (true project content, v1.2)",
         size=32, weight="bold", fill=NAVY)
    text(40, 88, "Version v1.2  •  10 November 2026  •  Status: Lab / portfolio  •  "
         "SIMULATED tenant: Nordlicht GmbH  •  Synthetic data only — no live Azure tenant access",
         size=18, fill=GREY)
    text(40, 112, "Source of truth: app/data.py + app/checks.py. Every box below is in that code — "
         "nothing invented, no service added from the reference picture.",
         size=16, fill=GREY)

    # ---------- ROW 1: agents | gateway | demo ----------
    # Agents (left)
    box(40, 130, 720, 280, fill="#FFFFFF", stroke=BLUE, sw=1.5)
    text(64, 162, "AGENTS — who asks to call a tool (6, from data.py)", size=19, weight="bold", fill=NAVY)
    agents = [
        ("finance-assistant", "active", "azure.storage.read, azure.openai.chat"),
        ("sales-assistant", "active", "azure.openai.chat, crm.send_email"),
        ("ops-agent", "active", "azure.vm.start / stop, azure.storage.read"),
        ("shadow-notes", "BLOCKED — no sponsor", "azure.keyvault.get_secret"),
        ("social-scoring-pilot", "BLOCKED — prohibited", "crm.score_customer"),
        ("hr-screening", "review — high-risk", "azure.openai.chat, hr.rank_applicant"),
    ]
    yy = 192
    for name, status, tools in agents:
        text(64, yy, name, size=16, weight="bold")
        text(64, yy + 0, "", size=16)
        text(300, yy, status, size=15, fill=RED if "BLOCKED" in status else GREY)
        yy += 20
        text(64, yy, "tools: " + tools, size=14, fill=GREY)
        yy += 16
    # Gateway (middle, amber)
    box(790, 130, 800, 280, fill=AMBER_BG, stroke=AMBER_LINE, sw=2)
    icon("app", 812, 148)
    text(872, 172, "GATEWAY — this project", size=19, weight="bold", fill=AMBER)
    text(872, 196, "FastAPI app — local lab, NOT an Azure service", size=15, weight="bold", fill=AMBER)
    gw = [
        "Agent registry: 6 agents, every agent has a sponsor (or is blocked)",
        "OPA server :8181  •  8 Rego policies  •  Python fallback",
        "One-shot human-approval queue (exact arguments, one use)",
        "Tool pinning: SHA-256 hash per tool — a changed tool is denied",
        "Evidence: SHA-256 hash chain  •  6 SQL audit queries",
        "Audit export: JSON + CSV for Archer / OneTrust (GRC record)",
    ]
    yy = 226
    for s in gw:
        text(812, yy, "•  " + s, size=15)
        yy += 24
    # Demo (right)
    box(1620, 130, 740, 280, fill="#FFFFFF", stroke=BLUE, sw=1.5)
    text(1644, 162, "DEMO — what the gateway decides (lab run)", size=19, weight="bold", fill=NAVY)
    demo = [
        ("azure.storage.read", "→  allow", TEAL),
        ("azure.vm.start", "→  needs_approval → approved → allow", AMBER),
        ("azure.keyvault.get_secret (shadow agent)", "→  deny", RED),
        ("social scoring (crm.score_customer)", "→  deny — EU AI Act Art. 5", RED),
    ]
    yy = 196
    for tool, res, col in demo:
        text(1644, yy, tool, size=16, weight="bold")
        text(1644, yy + 20, res, size=15, fill=col)
        yy += 44
    text(1644, yy + 4, "Native decision in every case: none", size=16, weight="bold", fill=RED)
    # arrows between row-1 boxes
    arrow(760, 270, 790, 270, w=2)
    arrow(1590, 270, 1620, 270, w=2)
    step(1, 40, 130)
    step(2, 790, 130)

    # ---------- ROW 2: simulated estate ----------
    text(40, 448, "SIMULATED ESTATE — Nordlicht GmbH (1 subscription, Azure for Students shape, SIMULATED)",
         size=20, weight="bold", fill=NAVY)
    box(40, 463, 2320, 440, fill=LIGHT2, stroke=BLUE, sw=1.5, dash="7 5")
    # 4 columns
    cols = [
        (64, "RESOURCE GROUPS (4)", "shield", [
            "rg-prod — germanywestcentral — 9 resources",
            "rg-ai — germanywestcentral — 6 resources",
            "rg-network — westeurope — 4 resources",
            "rg-test — eastus — 3 resources  ✕ OUTSIDE allowed",
            "Allowed regions: germanywestcentral, westeurope",
            "rg-test breaks the allowed-locations policy (AZ-01)",
        ]),
        (644, "VIRTUAL MACHINES (6)", "app", [
            "vm-web-01, vm-web-02 — encrypted, no public IP",
            "vm-app-01 — disk NOT encrypted, no JIT",
            "vm-db-01 — public IP, no backup, no JIT",
            "vm-test-01 — eastus, public IP, not encrypted",
            "vm-ai-01 — encrypted, JIT, backup on",
            "2 VMs with public IP  •  2 unencrypted disks",
        ]),
        (1224, "STORAGE ACCOUNTS (8)", "db", [
            "stnordlichtprod, stnordlichtlogs — private endpoint",
            "stnordlichtpub — PUBLIC blob  •  stnordlichtai",
            "stnordlichtold — PUBLIC blob, NOT encrypted, TLS 1.0",
            "stnordlichtbkp, stnordlichtdev, stnordlichtarc",
            "2 public blob  •  3 unencrypted  •  TLS < 1.2 on 2",
            "Private endpoint missing on 4 of 8 (AZ-13)",
        ]),
        (1804, "KEY VAULTS (3) + AI RESOURCES (4)", "key", [
            "kv-nordlicht-prod — RBAC, purge on, 0 expired",
            "kv-nordlicht-ai — no purge, 1 expired secret",
            "kv-nordlicht-old — no RBAC, 3 expired secrets",
            "aoai-nordlicht (gpt-4o, EU) — filters on",
            "aif-nordlicht (Foundry hub, gpt-4o, EU) — filters on",
            "acs-nordlicht (Content Safety, EU) — no logging",
            "aoai-test (gpt-4o-mini, US) — NO filter, NO logging",
        ]),
    ]
    for x, title, ic, lines in cols:
        box(x, 483, 532, 360, fill="#FFFFFF", stroke=BLUE, sw=1.5)
        icon(ic, x + 14, 496)
        text(x + 66, 522, title, size=17, weight="bold", fill=NAVY)
        yy = 556
        for ln in lines:
            text(x + 18, yy, ln, size=14.5, fill=DARK)
            yy += 26
        if "AI RESOURCES" in title:
            text(x + 18, yy + 2, "4 expired secrets total  •  20 Entra users, 3 without MFA",
                 size=14.5, weight="bold", fill=RED)
    text(64, 872, "6 Azure Policy assignments: Allowed locations (Deny)  •  Storage public blob (Deny)  •  Require encryption (Audit)  •  "
         "Minimum TLS 1.2 (Deny)  •  Key Vault purge protection (Audit)  •  Private endpoints for PaaS (Audit)",
         size=15, fill=GREY)
    text(64, 896, "Defender for Cloud: secure score 62 / 100  •  14 recommendations open, 5 high severity",
         size=15, fill=GREY)

    # ---------- ROW 3: 10 native services ----------
    text(40, 948, "10 NATIVE SERVICES — what each CAN and CANNOT decide (from data.py, NATIVE_CAPABILITIES)",
         size=20, weight="bold", fill=NAVY)
    services = [
        ("Azure Policy", "Deny / Audit a resource at creation", "shield"),
        ("Defender for Cloud", "Score the estate, flag, recommend", "shield"),
        ("Microsoft Entra ID", "MFA + Conditional Access, sign-in", "user"),
        ("Azure Key Vault", "RBAC on secrets, expiry, logs", "key"),
        ("Monitor / Sentinel", "Logs + alerts — after the fact", "monitor"),
        ("OpenAI content filters", "Block jailbreak / harmful content", "spark"),
        ("AI Foundry / Agent Service", "Run an agent with tools + model", "spark"),
        ("Network: NSG / Private Link", "Block a port, private endpoint", "lock"),
        ("Purview (M365 side)", "Labels, DLP, Copilot audit", "doc"),
        ("Agent 365 / Entra Agent ID", "Agent registry, identity, sponsor", "user"),
    ]
    sx, sy = 40, 963
    for i, (name, can, ic) in enumerate(services):
        x = sx + (i % 5) * 468
        y = sy + (i // 5) * 165
        box(x, y, 448, 150, fill="#FFFFFF", stroke=BLUE, sw=1.5)
        icon(ic, x + 12, y + 12)
        text(x + 64, y + 30, name, size=17, weight="bold", fill=NAVY)
        text(x + 16, y + 72, "CAN: " + can, size=14, fill=DARK)
        text(x + 16, y + 98, "CANNOT: decide one tool call", size=14, weight="bold", fill=RED)
        text(x + 16, y + 122, "CANNOT: check tool arguments", size=14, fill=RED)
    text(40, 1308, "Every one of the 10 admits it: no native application decides an individual MCP tool call, "
         "checks tool arguments, or approves one specific write.",
         size=16, weight="bold", fill=RED)

    # ---------- ROW 4: 16 checks ----------
    text(40, 1353, "16 CHECKS AZ-01 – AZ-16 (from app/checks.py — run live, 0 Pass, 8 Fail, 8 Partial)",
         size=20, weight="bold", fill=NAVY)
    box(40, 1368, 2320, 190, fill=LIGHT2, stroke=BLUE, sw=1.5)
    checks = [
        ("AZ-01", "allowed locations", "Fail"), ("AZ-02", "public blob deny", "Fail"),
        ("AZ-03", "encryption + TLS", "Fail"), ("AZ-04", "VM public IP / JIT", "Fail"),
        ("AZ-05", "Key Vault secrets", "Fail"), ("AZ-06", "Entra MFA", "Fail"),
        ("AZ-07", "Conditional Access", "Partial"), ("AZ-08", "Defender score 62%", "Partial"),
        ("AZ-09", "Monitor logging", "Partial"), ("AZ-10", "content filters", "Fail"),
        ("AZ-11", "AI residency EU", "Fail"), ("AZ-12", "AI logging Art. 12", "Partial"),
        ("AZ-13", "private endpoints", "Partial"), ("AZ-14", "Deny, not Audit-only", "Partial"),
        ("AZ-15", "AI literacy Art. 4", "Partial"), ("AZ-16", "per-tool-call GAP", "Partial*"),
    ]
    for i, (code, name, res) in enumerate(checks):
        x = 64 + (i % 8) * 288
        y = 1390 + (i // 8) * 62
        col = RED if res == "Fail" else AMBER
        box(x, y, 268, 52, fill="#FFFFFF", stroke=col, sw=2)
        text(x + 12, y + 22, code, size=16, weight="bold")
        text(x + 78, y + 22, name, size=14, fill=DARK)
        text(x + 12, y + 44, res, size=14, weight="bold", fill=col)
    text(64, 1536, "* AZ-16 is Partial BY DESIGN: it can only become Pass when a gateway like this one is in front of the tools.  "
         "28 controls (ISO 42001 + EU AI Act)  •  12 risks (R-01 – R-12).",
         size=15, fill=GREY)

    # ---------- ROW 5: evidence + steps ----------
    box(40, 1578, 1120, 200, fill="#FFFFFF", stroke=BLUE, sw=1.5, dash="7 5")
    text(64, 1612, "EVIDENCE & AUDIT — hash-chained, exportable", size=19, weight="bold", fill=NAVY)
    ev = [
        "Evidence register: one SHA-256 hash-chained row per check",
        "Issues workflow: Open → Verified → Closed (one Issue per Fail)",
        "Audit export: JSON + CSV for Archer / OneTrust (GRC record)",
        "KRI dashboard: 16 checks  •  12 risks  •  28 controls",
    ]
    yy = 1644
    for s in ev:
        text(64, yy, "•  " + s, size=15)
        yy += 28
    box(1180, 1578, 1180, 200, fill="#FFFFFF", stroke=BLUE, sw=1.5)
    text(1204, 1612, "NUMBERED STEPS", size=19, weight="bold", fill=NAVY)
    steps = [
        ("1", "An agent asks to call a tool (e.g. azure.vm.start)."),
        ("2", "Gateway checks identity + SHA-256 tool pin + agent allowlist."),
        ("3", "OPA decides per call: allow / deny / needs_approval (native: none)."),
        ("4", "Human approves the write in /approvals — one-shot, exact arguments."),
        ("5", "Decision logged as hash-chained evidence — exportable to Archer / OneTrust."),
    ]
    yy = 1644
    for n, s in steps:
        step(int(n), 1222, yy - 6)
        text(1252, yy, s, size=15)
        yy += 28

    # ---------- gap strip + footer ----------
    box(40, 1808, 2320, 64, fill=AMBER_BG, stroke=AMBER_LINE, sw=1.5)
    text(1200, 1848, "THE GAP — Azure native governs resources, identity, network and model content — "
         "NONE of them decides an individual MCP tool call. That is the gap the gateway fills.",
         size=19, weight="bold", fill=AMBER, anchor="middle")
    text(40, 1913, "What this picture does NOT show (deliberately): no Application Gateway, no Azure Firewall as a deployed resource, "
         "no Azure Web App / Function App / Queue service, no Redis, Cosmos DB, SQL Database, Blob or AI Search as separate services,",
         size=15, fill=GREY)
    text(40, 1937, "no VNet topology, no Microsoft Foundry project box, no Foundry Agent Service dependencies box — none of those are in "
         "app/data.py or app/checks.py. The gateway is a local-lab FastAPI app, not an Azure service.",
         size=15, fill=GREY)
    text(40, 1973, "Legend:   —  request / data flow      Amber box = gateway decision      Red = Fail / blocked      "
         "Green 1–5 = numbered steps",
         size=16, fill=GREY)
    text(40, 2003, "Regenerate: python3 scripts/make_foundry_style_diagram.py  •  Project: "
         "~/workspace/projects/azure-native-governance/  •  SIMULATED tenant: Nordlicht GmbH — no live Azure tenant access.",
         size=15, fill=GREY)
    text(40, 2063, "Azure native applications govern resources, identity, network and model content — "
         "none of them decides an individual MCP tool call.",
         size=16, fill=GREY)
    text(40, 2093, " ", size=16, fill=GREY)

    add("</svg>")
    return "".join(E)


if __name__ == "__main__":
    svg = build()
    with open(OUT_SVG, "w", encoding="utf-8") as f:
        f.write(svg)
    cairosvg.svg2png(url=OUT_SVG, write_to=OUT_PNG, output_width=4800)
    print(f"Wrote {OUT_SVG} and {OUT_PNG}")
