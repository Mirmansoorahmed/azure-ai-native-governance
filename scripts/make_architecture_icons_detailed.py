#!/usr/bin/env python3
"""Azure AI Native Governance — CLEAN DETAILED icon-only architecture diagram.

Detailed version of docs/architecture-icons.png: same icon-only look
(official Microsoft Azure Architecture Icons V25, large icons, transparent
perimeter boundaries with only a light dashed outline, white background),
plus clean details only:
- under each icon: service name + ONE short purpose line (max 5-6 words)
- on each flow arrow: ONE short data-flow label (max 4-5 words)
- one purpose line under the title
- one "one call, start to end" strip at the bottom (one line)

Content source of truth: app/data.py + app/checks.py only.
  Flow (5 steps): Agents -> Gateway -> OPA -> Human approval -> Evidence
  Native services (10, from NATIVE_CAPABILITIES): Azure Policy,
  Defender for Cloud, Entra ID, Key Vault, Monitor / Sentinel,
  OpenAI Filters (Azure OpenAI content filters), AI Foundry
  (Agent Service), Network (NSG / Private Link), Purview (M365 side),
  Agent 365 (M365 side).
  Agents: 6 in AGENTS, 3 active (finance-assistant, sales-assistant,
  ops-agent). Defender secure score: 62% (DEFENDER in data.py).
  Bottom strip: storage.read -> allow (allowlisted read);
  vm.start -> approval -> allow (write needs human approval);
  keyvault.get_secret -> deny (shadow-notes agent is blocked, not
  allowlisted) — see GAP examples in data.py.
No invented services (no App Gateway, Firewall, Web App, Function App,
Queue, Redis, Cosmos DB, SQL Database, Blob, Azure AI Search, VNet,
Foundry project box).
Review flags honoured: NO "SHA-256 tool pinning" claim (Gateway says
"identity + tool" only); NO "signed" evidence claim ("hash-chained"
only, per A-27 / checks.py); NO "EU data only" label — aoai-test is in
eastus (US), so no EU-residency claim anywhere in this diagram.
"""
import base64
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.dirname(HERE)
ICONS = "/tmp/azure-icons/Azure_Public_Service_Icons/Icons"
ICON_ZIP_URL = "https://arch-center.azureedge.net/icons/Azure_Public_Service_Icons_V25.zip"

ICON_FILES = {
    "agent": "ai + machine learning/038470523-icon-service-Foundry-Agent-Service.svg",
    "policy": "management + governance/10316-icon-service-Policy.svg",
    "defender": "security/10241-icon-service-Microsoft-Defender-for-Cloud.svg",
    "entra": "identity/10235-icon-service-Identity-Governance.svg",
    "keyvault": "security/10245-icon-service-Key-Vaults.svg",
    "monitor": "monitor/00001-icon-service-Monitor.svg",
    "openai": "ai + machine learning/03438-icon-service-Azure-OpenAI.svg",
    "foundry": "ai + machine learning/035746832-icon-service-AI-Foundry.svg",
    "nsg": "networking/10067-icon-service-Network-Security-Groups.svg",
    "purview": "identity/10229-icon-service-Azure-Information-Protection.svg",
    "agent365": "identity/10225-icon-service-Enterprise-Applications.svg",
}


def ensure_icons():
    """Re-download the V25 zip if the extracted icons are gone."""
    missing = [v for v in ICON_FILES.values()
               if not os.path.exists(os.path.join(ICONS, v))]
    if not missing:
        return
    os.makedirs("/tmp/azure-icons", exist_ok=True)
    zip_path = "/tmp/Azure_Public_Service_Icons_V25.zip"
    if not os.path.exists(zip_path):
        subprocess.run(["curl", "-sL", "-o", zip_path, ICON_ZIP_URL], check=True)
    subprocess.run(["unzip", "-q", "-o", zip_path, "-d", "/tmp/azure-icons"],
                   check=True)


def icon_uri(relpath):
    path = os.path.join(ICONS, relpath)
    with open(path, "rb") as f:
        return "data:image/svg+xml;base64," + base64.b64encode(f.read()).decode()


ensure_icons()
ICONS_B64 = {k: icon_uri(v) for k, v in ICON_FILES.items()}

NAVY = "#0F2A44"
GREY = "#44566B"         # purpose lines / subtitle
BLUE = "#0078D4"
ARROW_LBL = "#2F5D7A"    # flow-arrow labels
DASH = "#B9CBD9"          # very light dashed perimeter outline
FONT = "'Segoe UI', 'Helvetica Neue', Arial, 'Liberation Sans', sans-serif"

W, H = 4400, 1970


def esc(s):
    return (s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"))


def text(x, y, s, size=36, fill=NAVY, weight="bold", anchor="middle"):
    return (
        f'<text x="{x}" y="{y}" font-family="{FONT}" font-size="{size}" '
        f'fill="{fill}" font-weight="{weight}" text-anchor="{anchor}">{esc(s)}</text>'
    )


def img(name, x, y, size):
    return (f'<image href="{ICONS_B64[name]}" x="{x}" y="{y}" '
            f'width="{size}" height="{size}"/>')


def arrow(x1, y1, x2, y2, color=BLUE, sw=4):
    return (
        f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{color}" '
        f'stroke-width="{sw}"/><polygon points="{x2},{y2} {x2-22},{y2-11} '
        f'{x2-22},{y2+11}" fill="{color}"/>'
    )


def dashed_arrow_down(x, y1, y2, color="#5A6B7C", sw=3):
    return (
        f'<line x1="{x}" y1="{y1}" x2="{x}" y2="{y2}" stroke="{color}" '
        f'stroke-width="{sw}" stroke-dasharray="12 10"/>'
        f'<polygon points="{x},{y2} {x-11},{y2-22} {x+11},{y2-22}" fill="{color}"/>'
    )


def perimeter(x, y, w, h, rx=28):
    """Transparent group boundary: no fill, very light dashed outline only."""
    return (f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" '
            f'fill="none" stroke="{DASH}" stroke-width="2.5" '
            f'stroke-dasharray="16 12"/>')


def step_badge(cx, cy, n, r=32):
    return (
        f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="{BLUE}"/>'
        f'<text x="{cx}" y="{cy+11}" font-family="{FONT}" font-size="36" '
        f'fill="#FFFFFF" font-weight="bold" text-anchor="middle">{n}</text>'
    )


# --- Hand-drawn glyphs (our own code, not Azure services) -----------------
def shield(x, y, s):
    u = s / 170.0
    return (
        f'<path d="M {x+85*u:.0f} {y+8*u:.0f} L {x+148*u:.0f} {y+34*u:.0f} '
        f'L {x+148*u:.0f} {y+88*u:.0f} Q {x+148*u:.0f} {y+138*u:.0f} {x+85*u:.0f} {y+164*u:.0f} '
        f'Q {x+22*u:.0f} {y+138*u:.0f} {x+22*u:.0f} {y+88*u:.0f} '
        f'Q {x+22*u:.0f} {y+34*u:.0f} {x+85*u:.0f} {y+8*u:.0f} Z" '
        f'fill="none" stroke="{BLUE}" stroke-width="7" stroke-linejoin="round"/>'
        f'<path d="M {x+56*u:.0f} {y+88*u:.0f} L {x+78*u:.0f} {y+112*u:.0f} '
        f'L {x+118*u:.0f} {y+64*u:.0f}" fill="none" stroke="{BLUE}" '
        f'stroke-width="7" stroke-linecap="round" stroke-linejoin="round"/>'
    )


def scales(x, y, s):
    u = s / 170.0
    return (
        f'<line x1="{x+85*u:.0f}" y1="{y+18*u:.0f}" x2="{x+85*u:.0f}" y2="{y+140*u:.0f}" '
        f'stroke="{BLUE}" stroke-width="7" stroke-linecap="round"/>'
        f'<line x1="{x+28*u:.0f}" y1="{y+34*u:.0f}" x2="{x+142*u:.0f}" y2="{y+34*u:.0f}" '
        f'stroke="{BLUE}" stroke-width="7" stroke-linecap="round"/>'
        f'<line x1="{x+55*u:.0f}" y1="{y+152*u:.0f}" x2="{x+115*u:.0f}" y2="{y+152*u:.0f}" '
        f'stroke="{BLUE}" stroke-width="7" stroke-linecap="round"/>'
        f'<circle cx="{x+85*u:.0f}" cy="{y+18*u:.0f}" r="{9*u:.0f}" fill="{BLUE}"/>'
        f'<line x1="{x+28*u:.0f}" y1="{y+34*u:.0f}" x2="{x+14*u:.0f}" y2="{y+82*u:.0f}" '
        f'stroke="{BLUE}" stroke-width="5" stroke-linecap="round"/>'
        f'<line x1="{x+28*u:.0f}" y1="{y+34*u:.0f}" x2="{x+42*u:.0f}" y2="{y+82*u:.0f}" '
        f'stroke="{BLUE}" stroke-width="5" stroke-linecap="round"/>'
        f'<path d="M {x+8*u:.0f} {y+82*u:.0f} Q {x+28*u:.0f} {y+104*u:.0f} {x+48*u:.0f} {y+82*u:.0f}" '
        f'fill="none" stroke="{BLUE}" stroke-width="5" stroke-linecap="round"/>'
        f'<line x1="{x+142*u:.0f}" y1="{y+34*u:.0f}" x2="{x+128*u:.0f}" y2="{y+82*u:.0f}" '
        f'stroke="{BLUE}" stroke-width="5" stroke-linecap="round"/>'
        f'<line x1="{x+142*u:.0f}" y1="{y+34*u:.0f}" x2="{x+156*u:.0f}" y2="{y+82*u:.0f}" '
        f'stroke="{BLUE}" stroke-width="5" stroke-linecap="round"/>'
        f'<path d="M {x+122*u:.0f} {y+82*u:.0f} Q {x+142*u:.0f} {y+104*u:.0f} {x+162*u:.0f} {y+82*u:.0f}" '
        f'fill="none" stroke="{BLUE}" stroke-width="5" stroke-linecap="round"/>'
    )


def person_check(x, y, s):
    u = s / 170.0
    return (
        f'<circle cx="{x+68*u:.0f}" cy="{y+52*u:.0f}" r="{28*u:.0f}" fill="none" '
        f'stroke="{BLUE}" stroke-width="7"/>'
        f'<path d="M {x+22*u:.0f} {y+140*u:.0f} Q {x+22*u:.0f} {y+96*u:.0f} {x+68*u:.0f} {y+96*u:.0f} '
        f'Q {x+114*u:.0f} {y+96*u:.0f} {x+114*u:.0f} {y+140*u:.0f}" fill="none" '
        f'stroke="{BLUE}" stroke-width="7" stroke-linecap="round"/>'
        f'<path d="M {x+118*u:.0f} {y+128*u:.0f} L {x+134*u:.0f} {y+146*u:.0f} '
        f'L {x+162*u:.0f} {y+108*u:.0f}" fill="none" stroke="{BLUE}" '
        f'stroke-width="7" stroke-linecap="round" stroke-linejoin="round"/>'
    )


def evidence_doc(x, y, s):
    u = s / 170.0
    return (
        f'<path d="M {x+42*u:.0f} {y+12*u:.0f} L {x+108*u:.0f} {y+12*u:.0f} '
        f'L {x+132*u:.0f} {y+36*u:.0f} L {x+132*u:.0f} {y+152*u:.0f} '
        f'L {x+42*u:.0f} {y+152*u:.0f} Z" fill="none" stroke="{BLUE}" '
        f'stroke-width="7" stroke-linejoin="round"/>'
        f'<path d="M {x+108*u:.0f} {y+12*u:.0f} L {x+108*u:.0f} {y+36*u:.0f} '
        f'L {x+132*u:.0f} {y+36*u:.0f}" fill="none" stroke="{BLUE}" '
        f'stroke-width="5" stroke-linejoin="round"/>'
        f'<line x1="{x+58*u:.0f}" y1="{y+66*u:.0f}" x2="{x+116*u:.0f}" y2="{y+66*u:.0f}" '
        f'stroke="{BLUE}" stroke-width="6" stroke-linecap="round"/>'
        f'<line x1="{x+58*u:.0f}" y1="{y+92*u:.0f}" x2="{x+116*u:.0f}" y2="{y+92*u:.0f}" '
        f'stroke="{BLUE}" stroke-width="6" stroke-linecap="round"/>'
        f'<line x1="{x+58*u:.0f}" y1="{y+118*u:.0f}" x2="{x+96*u:.0f}" y2="{y+118*u:.0f}" '
        f'stroke="{BLUE}" stroke-width="6" stroke-linecap="round"/>'
        f'<path d="M {x+100*u:.0f} {y+140*u:.0f} L {x+112*u:.0f} {y+152*u:.0f} '
        f'L {x+132*u:.0f} {y+126*u:.0f}" fill="none" stroke="{BLUE}" '
        f'stroke-width="6" stroke-linecap="round" stroke-linejoin="round"/>'
    )


parts = []
parts.append(
    f'<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" '
    f'width="{W}" height="{H}" viewBox="0 0 {W} {H}">'
    f'<rect width="{W}" height="{H}" fill="#FFFFFF"/>'
)

# ---------- Title + one purpose line ----------
parts.append(text(2200, 105, "Azure AI Native Governance", 64, NAVY, "bold"))
parts.append(text(2200, 162, "Azure native governs resources. The gateway decides the tool call.",
                  34, GREY, "normal"))

# ---------- THE FLOW: 5 steps, left -> right ----------
# Grid: 5 cells, 680 wide, 170 gap, starting x=180 -> total 4080, centred.
CX0, CW, CGAP = 180, 680, 170
FLOW_Y, FLOW_H = 215, 460
parts.append(perimeter(140, FLOW_Y, 4120, FLOW_H))

flow = [
    ("icon", "agent", "Agents", "6 agents \u00b7 3 active"),
    ("draw", "shield", "Gateway", "checks identity + tool"),
    ("draw", "scales", "OPA", "allow / deny / approve"),
    ("draw", "person", "Human Approval", "one-shot \u00b7 exact args"),
    ("draw", "evidence", "Evidence", "hash-chained \u00b7 export to GRC"),
]
# Arrow labels, one per gap between steps (max 4-5 words each).
arrow_labels = [
    "asks to call a tool",
    "checks identity + tool",
    "allow / deny / approve",
    "approves the write",
]
DRAW = {"shield": shield, "scales": scales, "person": person_check,
        "evidence": evidence_doc}
for i, (kind, key, name, purpose) in enumerate(flow):
    cx = CX0 + i * (CW + CGAP) + CW // 2
    parts.append(step_badge(cx, 285, str(i + 1)))
    if kind == "icon":
        parts.append(img(key, cx - 80, 340, 160))
    else:
        parts.append(DRAW[key](cx - 80, 340, 160))
    parts.append(text(cx, 570, name, 37, NAVY, "bold"))
    parts.append(text(cx, 622, purpose, 29, GREY, "normal"))
    if i < 4:
        # Arrow at icon centre height; label centred in the wide gap
        # above the arrow — clear of both neighbouring icons.
        x1 = CX0 + (i + 1) * CW + i * CGAP + 12
        x2 = CX0 + (i + 1) * (CW + CGAP) - 14
        parts.append(arrow(x1, 420, x2, 420))
        parts.append(text((x1 + x2) // 2, 388, arrow_labels[i], 27,
                          ARROW_LBL, "normal"))

# Dashed link from OPA (step 3) down to the native services.
parts.append(dashed_arrow_down(2200, FLOW_Y + FLOW_H + 4, 820))

# ---------- NATIVE SERVICES: 10 icons, 2 rows of 5 ----------
NAT_Y, NAT_H = 830, 900
parts.append(perimeter(140, NAT_Y, 4120, NAT_H))

native = [
    ("policy", "Azure Policy", "blocks bad resources"),
    ("defender", "Defender for Cloud", "scores the estate \u00b7 62%"),
    ("entra", "Entra ID", "who may sign in"),
    ("keyvault", "Key Vault", "guards the secrets"),
    ("monitor", "Monitor / Sentinel", "sees it after it happened"),
    ("openai", "OpenAI Filters", "blocks harmful content"),
    ("foundry", "AI Foundry", "runs the agent + tools"),
    ("nsg", "Network", "blocks ports \u00b7 private paths"),
    ("purview", "Purview", "labels + DLP (M365)"),
    ("agent365", "Agent 365", "registry + sponsor"),
]
for i, (ic, name, purpose) in enumerate(native):
    col, row = i % 5, i // 5
    cx = CX0 + col * (CW + CGAP) + CW // 2
    top = 900 + row * 500
    parts.append(img(ic, cx - 70, top, 140))
    parts.append(text(cx, top + 205, name, 36, NAVY, "bold"))
    parts.append(text(cx, top + 255, purpose, 29, GREY, "normal"))

# Transparent dashed sub-group around the two M365-side services (row 2,
# columns 4-5): grouped by proximity only, no label, no fill.
parts.append(perimeter(CX0 + 3 * (CW + CGAP) - 20, 1380, 2 * CW + CGAP + 40, 310, rx=22))

# ---------- Bottom strip: one call, start to end (one line) ----------
STRIP_Y, STRIP_H = 1795, 120
parts.append(perimeter(140, STRIP_Y, 4120, STRIP_H, rx=22))
parts.append(text(
    2200, STRIP_Y + 72,
    "One call, start to end:   storage.read -> allow  \u00b7  "
    "vm.start -> approval -> allow  \u00b7  "
    "keyvault.get_secret -> deny (shadow agent)",
    32, NAVY, "normal"))

parts.append("</svg>")
svg = "\n".join(parts)

out_svg = os.path.join(PROJ, "docs", "architecture-icons-detailed.svg")
out_png = os.path.join(PROJ, "docs", "architecture-icons-detailed.png")
with open(out_svg, "w") as f:
    f.write(svg)

venv_python = "/tmp/cairovenv/bin/python"
exe = venv_python if os.path.exists(venv_python) else sys.executable
subprocess.run(
    [exe, "-m", "cairosvg", out_svg, "-o", out_png,
     "--output-width", "4400", "--output-height", str(H)],
    check=True,
)
print("wrote", out_svg)
print("wrote", out_png)
