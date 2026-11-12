"""Azure AI Native Governance — Architecture v2.0 (brand new, from scratch).

Builds docs/architecture-v2.svg first (clean vector lines), then exports
docs/architecture-v2.png (4800 px wide) with cairosvg.

Source of truth: app/data.py + app/checks.py ONLY.
Design: simple, clean, professional — white background, thin blue lines,
small clean line icons, lots of white space, large readable labels.
NOT a dense slide. One clear 5-step flow, then agents + estate,
then the 10 native services, then checks, demo, and THE GAP.

Regenerate:  cd ~/workspace/projects/azure-native-governance
              python3 scripts/make_architecture_v2.py
"""
import html
import os
import subprocess
import sys

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DOCS = os.path.join(BASE, "docs")

W, H = 2400, 2680
NAVY = "#0b2a5b"
BLUE = "#0078d4"
TEAL = "#0f766e"
GREY = "#475569"
LIGHT = "#f1f5f9"
AMBER_BG = "#fffbeb"
AMBER_BD = "#b45309"
AMBER_TX = "#92400e"
RED = "#b91c1c"
GREEN = "#15803d"
GREEN_BG = "#dcfce7"


def esc(s):
    return html.escape(str(s))


def text(x, y, s, size=22, fill=NAVY, weight="normal", anchor="start", style=""):
    return (
        f'<text x="{x}" y="{y}" font-family="DejaVu Sans, Arial, sans-serif" '
        f'font-size="{size}" fill="{fill}" font-weight="{weight}" '
        f'text-anchor="{anchor}" {style}>{esc(s)}</text>'
    )


def box(x, y, w, h, fill="#ffffff", stroke=BLUE, sw=2, rx=14, dash=""):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    return (
        f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" '
        f'fill="{fill}" stroke="{stroke}" stroke-width="{sw}"{d}/>'
    )


def badge(cx, cy, n, r=26):
    return (
        f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="{GREEN}"/>'
        f'{text(cx, cy + 9, n, 26, "#ffffff", "bold", "middle")}'
    )


def arrow(x1, y1, x2, y2):
    return (
        f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{BLUE}" '
        f'stroke-width="3" marker-end="url(#arr)"/>'
    )


parts = []
parts.append(
    f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" '
    f'viewBox="0 0 {W} {H}">'
)
parts.append(
    '<defs><marker id="arr" markerWidth="12" markerHeight="12" refX="9" '
    'refY="4" orient="auto"><path d="M0,0 L10,4 L0,8 Z" fill="#0078d4"/>'
    '</marker></defs>'
)
parts.append(f'<rect width="{W}" height="{H}" fill="#ffffff"/>')

# ---- Title -----------------------------------------------------------------
parts.append(text(60, 78, "Azure AI Native Governance — Architecture v2.0", 46, NAVY, "bold"))
parts.append(text(60, 122, "One flow: an agent asks → the gateway decides → the decision is logged as evidence.", 24, GREY))
parts.append(text(60, 156, "SIMULATED tenant: Nordlicht GmbH  •  Synthetic data only  •  No live Azure tenant access", 22, GREY))
parts.append(text(2340, 78, "v2.0", 30, BLUE, "bold", "end"))
parts.append(f'<line x1="60" y1="180" x2="2340" y2="180" stroke="{BLUE}" stroke-width="2"/>')

# ---- 5-step flow ------------------------------------------------------------
parts.append(text(60, 232, "THE FLOW — 5 steps", 28, NAVY, "bold"))
flow = [
    ("1", "Agents ask", "An agent asks to call", "a tool, e.g. azure.vm.start"),
    ("2", "Gateway checks", "FastAPI app — local lab,", "NOT an Azure service"),
    ("3", "OPA decides", "allow / deny /", "needs_approval per tool call"),
    ("4", "Human approves", "One-shot, exact", "arguments — if needed"),
    ("5", "Evidence logged", "SHA-256 hash chain,", "exportable to Archer / OneTrust"),
]
fx, fy, fw, fh, gap = 60, 260, 424, 210, 26
for i, (n, title, l1, l2) in enumerate(flow):
    x = fx + i * (fw + gap)
    fill = AMBER_BG if i in (1, 2) else "#ffffff"
    stroke = AMBER_BD if i in (1, 2) else BLUE
    parts.append(box(x, fy, fw, fh, fill, stroke, 2.5))
    parts.append(badge(x + 34, fy + 36, n, 24))
    parts.append(text(x + 70, fy + 44, title, 26, NAVY, "bold"))
    parts.append(text(x + 30, fy + 100, l1, 21, GREY))
    parts.append(text(x + 30, fy + 132, l2, 21, GREY))
    if i == 1:
        parts.append(text(x + 30, fy + 168, "identity + SHA-256 tool pin", 19, GREY))
    if i == 2:
        parts.append(text(x + 30, fy + 168, "8 Rego policies • Python fallback", 19, GREY))
    if i < 4:
        parts.append(arrow(x + fw + 2, fy + fh // 2, x + fw + gap - 4, fy + fh // 2))
parts.append(text(60, 510, "Gateway = FastAPI app (local lab) + OPA server :8181 + human-approval queue.  Native decision at every step: none.", 22, GREY))

# ---- Agents + Estate (two big boxes) ---------------------------------------
y0 = 560
parts.append(text(60, y0 + 30, "WHO ASKS — 6 agents", 28, NAVY, "bold"))
parts.append(text(1230, y0 + 30, "WHAT IS GOVERNED — simulated estate", 28, NAVY, "bold"))
parts.append(box(60, y0 + 50, 1110, 400, "#ffffff", BLUE, 2))
parts.append(box(1230, y0 + 50, 1110, 400, "#f8fafc", BLUE, 2))
agents = [
    ("finance-assistant", "active", GREEN),
    ("sales-assistant", "active", GREEN),
    ("ops-agent", "active", GREEN),
    ("shadow-notes", "BLOCKED — no sponsor", RED),
    ("social-scoring-pilot", "BLOCKED — prohibited", RED),
    ("hr-screening", "review — high-risk", AMBER_TX),
]
for i, (name, status, col) in enumerate(agents):
    yy = y0 + 100 + i * 55
    parts.append(text(100, yy, name, 24, NAVY, "bold"))
    parts.append(text(560, yy, status, 22, col, "bold"))
    if i < 5:
        parts.append(f'<line x1="100" y1="{yy + 18}" x2="1130" y2="{yy + 18}" stroke="#e2e8f0" stroke-width="1"/>')
estate = [
    "1 subscription  •  4 resource groups  (rg-test in eastus — outside allowed regions)",
    "6 VMs  •  8 storage accounts  (2 public blob)  •  3 Key Vaults  (4 expired secrets)",
    "4 AI resources  (Azure OpenAI + AI Foundry hub + Content Safety + 1 unfiltered test)",
    "20 Entra users  (3 without MFA)  •  6 Azure Policy assignments",
    "Defender for Cloud: secure score 62%  •  AI data residency: EU only",
    "",
    "28 controls — ISO/IEC 42001 + EU AI Act  •  12 risks",
]
for i, line in enumerate(estate):
    if line:
        parts.append(text(1270, y0 + 100 + i * 52, line, 22, NAVY if i == 6 else GREY,
                          "bold" if i == 6 else "normal"))

# ---- Native services --------------------------------------------------------
y1 = 1080
parts.append(text(60, y1 + 30, "WHAT AZURE NATIVE DOES — 10 services, one CAN line each", 28, NAVY, "bold"))
parts.append(text(60, y1 + 62, "Every one of them admits the same thing, in red: it CANNOT decide one tool call.", 22, RED))
native = [
    ("Azure Policy", ["Deny a resource in a", "disallowed region"]),
    ("Defender for Cloud", ["Score the estate, flag risks"]),
    ("Microsoft Entra ID", ["Require MFA + Conditional Access"]),
    ("Azure Key Vault", ["RBAC on secrets, expire secrets"]),
    ("Monitor / Sentinel", ["Collect logs, alert", "after the fact"]),
    ("OpenAI content filters", ["Block jailbreak / harmful content"]),
    ("AI Foundry / Agent Service", ["Register + run an agent with tools"]),
    ("Network: NSG / Private Link", ["Block a port, force a", "private endpoint"]),
    ("Purview  (M365 side)", ["Block Copilot on labelled content"]),
    ("Agent 365  (M365 side)", ["Allow / block an agent,", "give it a sponsor"]),
]
nw, nh = 440, 190
for i, (name, can_lines) in enumerate(native):
    col, row = i % 5, i // 5
    x = 60 + col * (nw + 14)
    y = y1 + 85 + row * (nh + 14)
    parts.append(box(x, y, nw, nh, "#ffffff", BLUE, 2))
    parts.append(text(x + 22, y + 42, name, 23, NAVY, "bold"))
    for j, ln in enumerate(can_lines):
        parts.append(text(x + 22, y + 78 + j * 26, ("CAN: " if j == 0 else "") + ln, 19, GREY))
    parts.append(text(x + 22, y + 128, "CANNOT: decide one tool call", 20, RED, "bold"))

# ---- Checks -----------------------------------------------------------------
y2 = 1610
parts.append(text(60, y2 + 30, "16 CHECKS  AZ-01 – AZ-16  —  0 Pass,  8 Fail,  8 Partial", 28, NAVY, "bold"))
parts.append(text(60, y2 + 62, "AZ-16 is Partial BY DESIGN — it can only pass when a gateway like this one is in front of the tools.", 22, GREY))
checks = [
    ("AZ-01", "Fail"), ("AZ-02", "Fail"), ("AZ-03", "Fail"), ("AZ-04", "Fail"),
    ("AZ-05", "Fail"), ("AZ-06", "Fail"), ("AZ-07", "Partial"), ("AZ-08", "Partial"),
    ("AZ-09", "Partial"), ("AZ-10", "Fail"), ("AZ-11", "Fail"), ("AZ-12", "Partial"),
    ("AZ-13", "Partial"), ("AZ-14", "Partial"), ("AZ-15", "Partial"), ("AZ-16", "Partial*"),
]
cw, ch = 272, 78
for i, (code, res) in enumerate(checks):
    col, row = i % 8, i // 8
    x = 60 + col * (cw + 12)
    y = y2 + 85 + row * (ch + 12)
    colr = RED if res == "Fail" else AMBER_TX
    parts.append(box(x, y, cw, ch, "#ffffff", colr, 2))
    parts.append(text(x + 18, y + 32, code, 22, NAVY, "bold"))
    parts.append(text(x + 110, y + 32, res, 22, colr, "bold"))
    parts.append(text(x + 18, y + 60, "AZ-16: gap check" if code == "AZ-16" else "", 17, GREY))

# ---- Demo + Gap -------------------------------------------------------------
y3 = 1930
parts.append(box(60, y3, 1110, 300, "#ffffff", BLUE, 2))
parts.append(text(100, y3 + 48, "DEMO — what the gateway decides (lab run)", 26, NAVY, "bold"))
demo = [
    ("azure.storage.read", "allow", GREEN),
    ("azure.vm.start", "needs_approval → approved → allow", AMBER_TX),
    ("azure.keyvault.get_secret  (shadow agent)", "deny", RED),
    ("social scoring  (crm.score_customer)", "deny — EU AI Act Art. 5", RED),
]
for i, (call, res, col) in enumerate(demo):
    yy = y3 + 100 + i * 48
    parts.append(text(100, yy, call, 22, NAVY))
    parts.append(text(660, yy, "→ " + res, 20, col, "bold"))
parts.append(text(100, y3 + 272, "Native decision in every case: none", 22, RED, "bold"))

parts.append(box(1230, y3, 1110, 300, AMBER_BG, AMBER_BD, 2.5))
parts.append(text(1270, y3 + 48, "THE GAP — in one line", 26, AMBER_TX, "bold"))
parts.append(text(1270, y3 + 100, "Azure native governs resources, identity,", 23, NAVY))
parts.append(text(1270, y3 + 134, "network and model content —", 23, NAVY))
parts.append(text(1270, y3 + 168, "NONE of them decides an individual", 23, NAVY, "bold"))
parts.append(text(1270, y3 + 202, "MCP tool call. That is the gap", 23, NAVY, "bold"))
parts.append(text(1270, y3 + 236, "the gateway fills.", 23, NAVY, "bold"))
parts.append(text(1270, y3 + 272, "native_decision_for_tool_call: null", 20, RED, "bold"))

# ---- Footer -----------------------------------------------------------------
y4 = 2320
parts.append(f'<line x1="60" y1="{y4}" x2="2340" y2="{y4}" stroke="#cbd5e1" stroke-width="2"/>')
parts.append(text(60, y4 + 40, "Source of truth: app/data.py + app/checks.py. Every box above is in that code — nothing invented.", 21, GREY))
parts.append(text(60, y4 + 74, "Deliberately NOT shown: Application Gateway, Azure Firewall, Web App, Function App, Queue, Redis, Cosmos DB,", 21, GREY))
parts.append(text(60, y4 + 104, "SQL Database, Blob, Azure AI Search, VNet topology, Microsoft Foundry project box, Foundry Agent Service", 21, GREY))
parts.append(text(60, y4 + 134, "dependencies, DDoS Protection, Application Insights — none of those are in the project code.", 21, GREY))
parts.append(text(60, y4 + 178, "Legend:  → request / data flow     Green 1–5 = numbered steps     Amber box = gateway decision     Red = Fail / blocked", 20, GREY))
parts.append(text(60, y4 + 212, "Regenerate: python3 scripts/make_architecture_v2.py  •  Project: ~/workspace/projects/azure-native-governance/", 20, GREY))
parts.append(text(60, y4 + 246, "Azure native applications govern resources, identity, network and model content — none of them decides an individual MCP tool call.", 20, GREY, "normal", "", 'font-style="italic"'))
parts.append(text(60, y4 + 280, "10 November 2026  •  Lab / portfolio  •  pytest 30 passed", 20, GREY))
parts.append("</svg>")

svg = "\n".join(parts)
svg_path = os.path.join(DOCS, "architecture-v2.svg")
png_path = os.path.join(DOCS, "architecture-v2.png")
with open(svg_path, "w") as f:
    f.write(svg)

import cairosvg
cairosvg.svg2png(url=svg_path, write_to=png_path, output_width=4800)
print(f"Wrote {svg_path}")
print(f"Wrote {png_path} (4800 px wide)")
