#!/usr/bin/env python3
"""Azure AI Native Governance — COMPACT DETAILED icon-only diagram (v2).

Tighter, shorter version of docs/architecture-icons-detailed.png:
same icon-only look (official Microsoft Azure Architecture Icons V25,
large icons, transparent perimeter boundaries with only a light dashed
outline, white background), same grounded content, less white space
(4400 x 1700 instead of 4400 x 1970), plus a new "What our tool does"
box: the gateway's actual per-call parameters from the code and the
16 checks as short parameter chips (not a table).

Content source of truth: app/data.py + app/checks.py + app/main.py
+ app/policy.py. Nothing invented.
  Flow (5 steps): Agents -> Gateway -> OPA -> Human approval -> Evidence
  Native services (10, from NATIVE_CAPABILITIES): Azure Policy,
  Defender for Cloud, Entra ID, Key Vault, Monitor / Sentinel,
  OpenAI Filters (Azure OpenAI content filters), AI Foundry
  (Agent Service), Network (NSG / Private Link), Purview (M365 side),
  Agent 365 (M365 side).
  Agents: 6 in AGENTS, 3 active. Defender secure score: 62%.
  Per-call parameters (app/main.py agent_action + app/policy.py
  evaluate_gateway_tool_call):
    - agent identity + sponsor (AGENTS sponsor; Entra Agent ID)
    - tool name + tool arguments (payload "tool" + "arguments")
    - tool pin: identity + tool check (tool_pinned in the gateway ctx;
      a failed pin denies the call until re-review)
    - OPA decision: allow / deny / approve (needs_approval)
    - human approval: one-shot, exact args (an approval matches only
      the same agent + tool + exact arguments JSON)
    - evidence: hash-chained, export to GRC (app/evidence.py chain;
      /evidence/export.csv, /audit/export)
  16 checks (app/checks.py AZ-01..AZ-16, one chip each):
    AZ-01 region = EU only; AZ-02 public blob = deny;
    AZ-03 encryption + TLS 1.2; AZ-04 VM public IP / JIT;
    AZ-05 Key Vault expiry + RBAC; AZ-06 MFA = required;
    AZ-07 Conditional Access; AZ-08 Defender 62%;
    AZ-09 Monitor / Sentinel logging; AZ-10 content filters on;
    AZ-11 AI residency EU, 1 outside EU (aoai-test is in eastus, US);
    AZ-12 AI logging, Art. 12; AZ-13 private endpoints;
    AZ-14 Deny, not Audit-only; AZ-15 AI literacy, Art. 4;
    AZ-16 per-tool-call: gateway only (Partial by design — no Azure
    native application decides an individual tool call).
  Bottom strip: storage.read -> allow; vm.start -> approval -> allow;
  keyvault.get_secret -> deny (shadow agent) — see GAP in data.py.
Review flags honoured: NO "SHA-256 tool pinning" claim (gateway says
"tool pin (identity + tool check)" only); NO "signed" evidence claim
("hash-chained" only); NO "EU data only" label — the AZ-11 chip says
"AI residency EU, 1 outside EU" because aoai-test is in eastus (US).
No invented services, no GitHub / personal info.
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
CHIP_FILL = "#E8F1F8"    # very light blue chip fill
CHIP_STROKE = "#B9CBD9"
FONT = "'Segoe UI', 'Helvetica Neue', Arial, 'Liberation Sans', sans-serif"

W, H = 4400, 1700


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


def step_badge(cx, cy, n, r=30):
    return (
        f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="{BLUE}"/>'
        f'<text x="{cx}" y="{cy+11}" font-family="{FONT}" font-size="34" '
        f'fill="#FFFFFF" font-weight="bold" text-anchor="middle">{n}</text>'
    )


def chip(x, y, w, h, label):
    return (
        f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{h // 2}" '
        f'fill="{CHIP_FILL}" stroke="{CHIP_STROKE}" stroke-width="1.5"/>'
        + text(x + w // 2, y + h // 2 + 9, label, 25, NAVY, "normal")
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
parts.append(text(2200, 76, "Azure AI Native Governance", 58, NAVY, "bold"))
parts.append(text(2200, 124, "Azure native governs resources. The gateway decides the tool call.",
                  31, GREY, "normal"))

# ---------- THE FLOW: 5 steps, left -> right ----------
# Grid: 5 cells, 680 wide, 170 gap, starting x=180 -> total 4080, centred.
CX0, CW, CGAP = 180, 680, 170
FLOW_Y, FLOW_H = 152, 312
parts.append(perimeter(140, FLOW_Y, 4120, FLOW_H))

flow = [
    ("icon", "agent", "Agents", "6 agents \u00b7 3 active"),
    ("draw", "shield", "Gateway", "checks identity + tool"),
    ("draw", "scales", "OPA", "allow / deny / approve"),
    ("draw", "person", "Human Approval", "one-shot \u00b7 exact args"),
    ("draw", "evidence", "Evidence", "hash-chained \u00b7 export to GRC"),
]
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
    parts.append(step_badge(cx, 196, str(i + 1)))
    if kind == "icon":
        parts.append(img(key, cx - 59, 222, 118))
    else:
        parts.append(DRAW[key](cx - 59, 222, 118))
    parts.append(text(cx, 380, name, 35, NAVY, "bold"))
    parts.append(text(cx, 416, purpose, 28, GREY, "normal"))
    if i < 4:
        x1 = CX0 + (i + 1) * CW + i * CGAP + 12
        x2 = CX0 + (i + 1) * (CW + CGAP) - 14
        parts.append(arrow(x1, 281, x2, 281))
        parts.append(text((x1 + x2) // 2, 252, arrow_labels[i], 26,
                          ARROW_LBL, "normal"))

# Dashed link from OPA (step 3, cx 2220) down to the native services.
parts.append(dashed_arrow_down(2220, FLOW_Y + FLOW_H + 4, 500))

# ---------- NATIVE SERVICES: 10 icons, 2 rows of 5 ----------
NAT_Y, NAT_H = 506, 462
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
    top = 530 + row * 218
    parts.append(img(ic, cx - 56, top, 112))
    parts.append(text(cx, top + 150, name, 34, NAVY, "bold"))
    parts.append(text(cx, top + 186, purpose, 28, GREY, "normal"))

# Transparent dashed sub-group around the two M365-side services (row 2,
# columns 4-5): grouped by proximity only, no label, no fill.
parts.append(perimeter(CX0 + 3 * (CW + CGAP) - 20, 736, 2 * CW + CGAP + 40, 216, rx=22))

# ---------- WHAT OUR TOOL DOES: per-call parameters + 16 check chips -----
TOOL_Y, TOOL_H = 990, 500
parts.append(perimeter(140, TOOL_Y, 4120, TOOL_H))

parts.append(text(2200, 1044, "What our tool does \u2014 per call", 34, NAVY, "bold"))
parts.append(text(2200, 1102,
                  "Agent identity + sponsor  \u00b7  Tool name + arguments  \u00b7  "
                  "Tool pin (identity + tool check)", 30, NAVY, "normal"))
parts.append(text(2200, 1150,
                  "OPA: allow / deny / approve  \u00b7  Human approval: one-shot, exact args  "
                  "\u00b7  Evidence: hash-chained, export to GRC", 30, NAVY, "normal"))

parts.append(text(2200, 1216, "16 checks:", 27, GREY, "normal"))
CHIPS = [
    "region = EU only", "public blob = deny", "encryption + TLS 1.2",
    "VM public IP / JIT", "Key Vault expiry + RBAC", "MFA = required",
    "Conditional Access", "Defender 62%",
    "Monitor / Sentinel logging", "content filters on",
    "AI residency EU \u00b7 1 outside EU", "AI logging \u00b7 Art. 12",
    "private endpoints", "Deny, not Audit-only",
    "AI literacy \u00b7 Art. 4", "per-tool-call: gateway only",
]
CHIP_X0, CHIP_W, CHIP_GAP, CHIP_H = 200, 494, 18, 50
for i, label in enumerate(CHIPS):
    col, row = i % 8, i // 8
    x = CHIP_X0 + col * (CHIP_W + CHIP_GAP)
    y = 1236 + row * 62
    parts.append(chip(x, y, CHIP_W, CHIP_H, label))

# Thin divider, then the one-line takeaway.
parts.append(
    f'<line x1="700" y1="1396" x2="3700" y2="1396" stroke="{DASH}" '
    f'stroke-width="2"/>'
)
parts.append(text(2200, 1452,
                  "Native tells us what exists. Our tool decides what may run.",
                  32, NAVY, "bold"))

# ---------- Bottom strip: one call, start to end (one line) ----------
STRIP_Y, STRIP_H = 1512, 110
parts.append(perimeter(140, STRIP_Y, 4120, STRIP_H, rx=22))
parts.append(text(
    2200, STRIP_Y + 66,
    "One call, start to end:   storage.read -> allow  \u00b7  "
    "vm.start -> approval -> allow  \u00b7  "
    "keyvault.get_secret -> deny (shadow agent)",
    31, NAVY, "normal"))

parts.append("</svg>")
svg = "\n".join(parts)

out_svg = os.path.join(PROJ, "docs", "architecture-icons-detailed-v2.svg")
out_png = os.path.join(PROJ, "docs", "architecture-icons-detailed-v2.png")
with open(out_svg, "w") as f:
    f.write(svg)

subprocess.run(
    [sys.executable, "-m", "cairosvg", out_svg, "-o", out_png,
     "--output-width", "4400", "--output-height", str(H)],
    check=True,
)
print("wrote", out_svg)
print("wrote", out_png)
