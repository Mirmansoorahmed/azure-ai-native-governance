#!/usr/bin/env python3
"""Azure AI Native Governance — Architecture v3.0 (minimal, draw.io-style).

Design: white background, thin lines, generous white space, official
Microsoft Azure Architecture Icons (V25, downloaded from Microsoft Learn:
https://learn.microsoft.com/en-us/azure/architecture/icons/ ->
https://arch-center.azureedge.net/icons/Azure_Public_Service_Icons_V25.zip).
Icons are embedded as base64 into the SVG; the SVG is the source, the PNG
is exported with cairosvg.

Content source of truth: app/data.py + app/checks.py only. Minimal text:
2-4 words per box + one short purpose line. No GitHub info, no personal info.
"""
import base64
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.dirname(HERE)
ICONS = "/tmp/azure-icons/Azure_Public_Service_Icons/Icons"

ICON_FILES = {
    "agent": "ai + machine learning/038470523-icon-service-Foundry-Agent-Service.svg",
    "policy": "management + governance/10316-icon-service-Policy.svg",
    "defender": "security/10241-icon-service-Microsoft-Defender-for-Cloud.svg",
    "entra": "identity/10235-icon-service-Identity-Governance.svg",
    "keyvault": "security/10245-icon-service-Key-Vaults.svg",
    "monitor": "monitor/00001-icon-service-Monitor.svg",
    "sentinel": "security/10248-icon-service-Azure-Sentinel.svg",
    "openai": "ai + machine learning/03438-icon-service-Azure-OpenAI.svg",
    "foundry": "ai + machine learning/035746832-icon-service-AI-Foundry.svg",
    "nsg": "networking/10067-icon-service-Network-Security-Groups.svg",
    "purview": "identity/10229-icon-service-Azure-Information-Protection.svg",
    "agent365": "identity/10225-icon-service-Enterprise-Applications.svg",
    "vm": "compute/10021-icon-service-Virtual-Machine.svg",
    "storage": "storage/10086-icon-service-Storage-Accounts.svg",
    "subscription": "general/10007-icon-service-Resource-Groups.svg",
}


def icon_uri(relpath):
    path = os.path.join(ICONS, relpath)
    with open(path, "rb") as f:
        return "data:image/svg+xml;base64," + base64.b64encode(f.read()).decode()


ICONS_B64 = {k: icon_uri(v) for k, v in ICON_FILES.items()}

NAVY = "#0F2A44"
BLUE = "#0078D4"
GREY = "#5A6B7C"
LIGHT = "#EAF2F8"
BORDER = "#C9D6E2"
RED = "#C50F1F"
GREEN = "#107C10"
AMBER_BG = "#FFF4D6"
AMBER_BD = "#D98E00"
FONT = "'Segoe UI', 'Helvetica Neue', Arial, sans-serif"

W, H = 2400, 1680


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def text(x, y, s, size=24, fill=NAVY, weight="normal", anchor="start", family=FONT):
    return (
        f'<text x="{x}" y="{y}" font-family="{family}" font-size="{size}" '
        f'fill="{fill}" font-weight="{weight}" text-anchor="{anchor}">{esc(s)}</text>'
    )


def box(x, y, w, h, fill="#FFFFFF", stroke=BORDER, rx=10, sw=1.5):
    return (
        f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" '
        f'fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>'
    )


def img(name, x, y, size=64):
    return f'<image href="{ICONS_B64[name]}" x="{x}" y="{y}" width="{size}" height="{size}"/>'


def arrow(x1, y1, x2, y2, color=BLUE, sw=2.5):
    return (
        f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{color}" '
        f'stroke-width="{sw}"/><polygon points="{x2},{y2} {x2-14},{y2-7} {x2-14},{y2+7}" '
        f'fill="{color}"/>'
    )


def step_badge(cx, cy, n, r=26):
    return (
        f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="{GREEN}"/>'
        f'<text x="{cx}" y="{cy+8}" font-family="{FONT}" font-size="28" fill="#FFFFFF" '
        f'font-weight="bold" text-anchor="middle">{n}</text>'
    )


parts = []
parts.append(
    f'<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" '
    f'width="{W}" height="{H}" viewBox="0 0 {W} {H}">'
    f'<rect width="{W}" height="{H}" fill="#FFFFFF"/>'
)

# ---------- Title: purpose of the architecture, one line ----------
parts.append(text(80, 78, "Azure AI Native Governance", 52, NAVY, "bold"))
parts.append(text(80, 128, "Every agent tool call gets one decision — before it runs.", 28, BLUE))
parts.append(text(80, 168, "Simulated tenant · Nordlicht GmbH · No live Azure access", 22, GREY))
parts.append(f'<line x1="80" y1="196" x2="2320" y2="196" stroke="{BORDER}" stroke-width="1.5"/>')

# ---------- THE FLOW: 4 steps, left -> right ----------
parts.append(text(80, 248, "THE FLOW", 26, NAVY, "bold"))
flow = [
    ("agent", "1 · Agent asks", "Calls a tool", "finance · sales · ops"),
    ("policy", "2 · Gateway checks", "Who? Which tool?", "identity + tool pin"),
    ("policy", "3 · OPA decides", "Allow · deny · approve", "8 Rego rules"),
    ("monitor", "4 · Evidence logged", "Signed · hash-chained", "export to GRC"),
]
# gateway step gets amber tint, others white; step 2 icon is a drawn shield (gateway is our code, not Azure)
fx, fy, fw, fh, gap = 80, 272, 520, 240, 40
for i, (ic, title, line1, line2) in enumerate(flow):
    x = fx + i * (fw + gap)
    fill = AMBER_BG if i in (1, 2) else "#FFFFFF"
    stroke = AMBER_BD if i in (1, 2) else BORDER
    parts.append(box(x, fy, fw, fh, fill, stroke, 12, 2))
    if i == 1:
        # hand-drawn shield = gateway is our own code, not an Azure service
        parts.append(
            f'<path d="M {x+52} {fy+36} L {x+92} {fy+52} L {x+92} {fy+88} '
            f'Q {x+92} {fy+118} {x+72} {fy+132} Q {x+52} {fy+118} {x+52} {fy+88} '
            f'Q {x+52} {fy+52} {x+52} {fy+36} Z" fill="none" stroke="{BLUE}" stroke-width="3"/>'
            f'<path d="M {x+62} {fy+86} L {x+70} {fy+96} L {x+84} {fy+74}" fill="none" '
            f'stroke="{BLUE}" stroke-width="3"/>'
        )
    else:
        parts.append(img(ic, x + 36, fy + 36, 72))
    parts.append(text(x + 128, fy + 66, title, 30, NAVY, "bold"))
    parts.append(text(x + 128, fy + 108, line1, 25, NAVY))
    parts.append(text(x + 128, fy + 148, line2, 23, GREY))
    parts.append(step_badge(x + 28, fy + 28, str(i + 1)))
    if i < 3:
        parts.append(arrow(x + fw + 4, fy + fh // 2, x + fw + gap - 6, fy + fh // 2))
parts.append(text(80, 556, "Gateway = FastAPI app (local lab, not an Azure service) + OPA :8181 + human approval.",
                  24, GREY))
parts.append(text(80, 592, "Native decision at every step: none.", 24, RED, "bold"))

# ---------- WHAT AZURE NATIVE DOES: 10 services, purpose + where it stops ----------
parts.append(text(80, 668, "WHAT AZURE NATIVE DOES — AND WHERE IT STOPS", 26, NAVY, "bold"))
parts.append(text(80, 702, "Each service has one job. None of them decides a single tool call.", 24, GREY))
# (icon, name, purpose, stops-at)
native = [
    ("policy", "Azure Policy", "Blocks bad resources", "stops at: the tool call"),
    ("defender", "Defender", "Scores the estate · 62%", "stops at: the tool call"),
    ("entra", "Entra ID", "Who may sign in", "stops at: the tool call"),
    ("keyvault", "Key Vault", "Guards the secrets", "stops at: the tool call"),
    ("monitor", "Monitor / Sentinel", "Sees it after it happened", "stops at: the tool call"),
    ("openai", "OpenAI filters", "Blocks harmful content", "stops at: the tool call"),
    ("foundry", "Foundry / Agent Service", "Runs the agent + tools", "stops at: the tool call"),
    ("nsg", "Network", "Blocks ports · private paths", "stops at: the tool call"),
    ("purview", "Purview", "Labels + DLP (M365)", "stops at: the tool call"),
    ("agent365", "Agent 365", "Agent registry + sponsor", "stops at: the tool call"),
]
cx0, cy0, cw, ch, cgx, cgy = 80, 730, 440, 150, 20, 20
for i, (ic, name, purpose, stops) in enumerate(native):
    x = cx0 + (i % 5) * (cw + cgx)
    y = cy0 + (i // 5) * (ch + cgy)
    parts.append(box(x, y, cw, ch, "#FFFFFF", BORDER, 10, 1.5))
    parts.append(img(ic, x + 22, y + 24, 56))
    parts.append(text(x + 96, y + 50, name, 26, NAVY, "bold"))
    parts.append(text(x + 96, y + 86, purpose, 23, GREY))
    parts.append(text(x + 96, y + 120, "x " + stops, 23, RED, "bold"))

# ---------- WHAT WE ADD (the gateway) ----------
gy = 1090
parts.append(box(80, gy, 1160, 210, AMBER_BG, AMBER_BD, 12, 2))
parts.append(text(116, gy + 52, "WHAT WE ADD — the gateway", 28, NAVY, "bold"))
parts.append(text(116, gy + 100, "One decision per tool call", 26, NAVY))
parts.append(text(116, gy + 142, "Tool pinning (SHA-256) · human approval for writes", 24, GREY))
parts.append(text(116, gy + 180, "16 checks · 0 pass · 8 fail · 8 partial", 24, GREY))

# ---------- DEMO: start -> end ----------
parts.append(box(1280, gy, 1040, 210, "#FFFFFF", BORDER, 12, 2))
parts.append(text(1316, gy + 52, "ONE CALL, START TO END", 28, NAVY, "bold"))
parts.append(text(1316, gy + 100, "storage.read  ->  allow", 26, GREEN, "bold"))
parts.append(text(1316, gy + 142, "vm.start  ->  approval  ->  allow", 26, NAVY))
parts.append(text(1316, gy + 180, "keyvault.get_secret  ->  deny", 26, RED, "bold"))

# ---------- THE ESTATE: one quiet strip ----------
ey = 1340
parts.append(text(80, ey + 40, "THE ESTATE (simulated)", 26, NAVY, "bold"))
estate = [
    ("subscription", "1 subscription"),
    ("vm", "6 VMs"),
    ("storage", "8 storage"),
    ("keyvault", "3 Key Vaults"),
    ("openai", "4 AI resources"),
    ("entra", "20 users"),
]
ex = 80
for ic, label in estate:
    parts.append(img(ic, ex, ey + 64, 48))
    parts.append(text(ex + 60, ey + 96, label, 24, NAVY))
    ex += 60 + len(label) * 13 + 70
parts.append(text(80, ey + 150, "4 resource groups · 6 Policy assignments · Defender 62% · EU data only",
                  24, GREY))

# ---------- THE GAP ----------
parts.append(box(80, 1530, 2240, 90, AMBER_BG, AMBER_BD, 12, 2))
parts.append(text(116, 1586, "THE GAP — Native stops at the tool call. The gateway decides it.",
                  28, NAVY, "bold"))
parts.append(text(80, 1662, "Icons: official Microsoft Azure Architecture Icons (V25, Microsoft Learn). "
                             "Source: app/data.py + app/checks.py.", 20, GREY))

parts.append("</svg>")
svg = "\n".join(parts)

out_svg = os.path.join(PROJ, "docs", "architecture-v3.svg")
out_png = os.path.join(PROJ, "docs", "architecture-v3.png")
with open(out_svg, "w") as f:
    f.write(svg)

venv_python = "/tmp/cairovenv/bin/python"
if os.path.exists(venv_python):
    subprocess.run(
        [venv_python, "-m", "cairosvg", out_svg, "-o", out_png,
         "--output-width", "4800", "--output-height", "3360"],
        check=True,
    )
else:
    subprocess.run(
        [sys.executable, "-m", "cairosvg", out_svg, "-o", out_png,
         "--output-width", "4800", "--output-height", "3360"],
        check=True,
    )
print("wrote", out_svg)
print("wrote", out_png)
