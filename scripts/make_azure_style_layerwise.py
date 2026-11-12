#!/usr/bin/env python3
"""Azure-style LAYERWISE architecture diagram for Azure AI Native Governance.

Regenerate:  python3 scripts/make_azure_style_layerwise.py
Output:       docs/architecture-azure-style-layerwise.png  (4000 x 2900 px)
Style: same Microsoft Azure reference-diagram style as
make_azure_style_diagram.py — light-blue/white, #0078D4, clean Azure
icons — but arranged layerwise, top to bottom, in 6 clearly labelled
layers like docs/architecture.png (v1.1), with a numbered 1-5 request
path down the layers and the 2 data flows condensed at the bottom.
All icons are vector pictograms drawn with matplotlib patches / DejaVu
glyphs — no emoji (they render as tofu on this VM).
"""
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Ellipse, Rectangle, FancyArrowPatch

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "docs" / "architecture-azure-style-layerwise.png"

AZURE = "#0078D4"
NAVY = "#0B2C5F"
DARK = "#1B3A5C"
LIGHT = "#DCEEF9"
LIGHT2 = "#EAF4FB"
MID = "#BFE0F2"
TEAL = "#0E7C7B"
AMBER = "#B45309"
AMBER_BG = "#FEF3C7"
RED = "#B42318"
GREY = "#475569"
WHITE = "white"

fig, ax = plt.subplots(figsize=(20, 29))
ax.set_xlim(0, 100)
ax.set_ylim(0, 145)
ax.axis("off")
fig.patch.set_facecolor("white")
ax.set_facecolor("white")


def box(x, y, w, h, face=WHITE, edge=AZURE, lw=1.6, r=0.7):
    p = FancyBboxPatch((x, y), w, h, boxstyle=f"round,pad=0,rounding_size={r}",
                       facecolor=face, edgecolor=edge, linewidth=lw)
    ax.add_patch(p)
    return p


def band(x, y, w, h, face, edge):
    box(x, y, w, h, face=face, edge=edge, lw=1.4, r=0.6)


def icon_disc(cx, cy, r, color, glyph, fs=13, tc="white"):
    # figsize (20, 29) with xlim 0-100, ylim 0-145: x-unit = y-unit = 0.2 in,
    # so no x-radius scaling (the 0.7 factor in the multi-region script
    # only applied to its 20x14 canvas)
    ax.add_patch(Ellipse((cx, cy), 2 * r, 2 * r, facecolor=color,
                         edgecolor="none", zorder=5))
    ax.text(cx, cy - 0.12, glyph, fontsize=fs, color=tc, ha="center",
            va="center", fontweight="bold", zorder=6)


def arrow(x1, y1, x2, y2, color=AZURE, lw=2.0, ms=14):
    ax.add_patch(FancyArrowPatch((x1, y1), (x2, y2), arrowstyle="-|>",
                                 mutation_scale=ms, linewidth=lw, color=color,
                                 shrinkA=0, shrinkB=0, zorder=4))


def db_icon(cx, cy, color=AZURE):
    ax.add_patch(Rectangle((cx - 1.0, cy - 1.2), 2.0, 2.0, facecolor=color,
                           edgecolor="none", zorder=5))
    ax.add_patch(Ellipse((cx, cy + 0.8), 2.0, 0.9, facecolor="#5EB0E5",
                         edgecolor="none", zorder=6))
    ax.add_patch(Ellipse((cx, cy - 1.2), 2.0, 0.9, facecolor=color,
                         edgecolor="none", zorder=6))


def cell(x, y, w, h, glyph, gcolor, title, sub, edge=AZURE, face=WHITE, gfs=13):
    """One content box: icon disc on the left, bold title + grey sub."""
    box(x, y, w, h, face=face, edge=edge, lw=1.5)
    icon_disc(x + 2.6, y + h / 2, 1.9, gcolor, glyph, fs=gfs)
    ax.text(x + 5.4, y + h / 2 + 1.1, title, fontsize=9.8, fontweight="bold",
            color=DARK, va="center")
    if sub:
        ax.text(x + 5.4, y + h / 2 - 1.6, sub, fontsize=8.6, color=GREY,
                va="center")


def layer(y, h, heading, face, edge):
    """Layer band; heading sits near the band top with clear space below
    it before the boxes start (boxes start 2.6 units below the top)."""
    band(2, y, 96, h, face, edge)
    ax.text(3.5, y + h - 1.6, heading, fontsize=11.5, fontweight="bold",
            color=NAVY if edge != AMBER else AMBER, va="center", ha="left")
    return y + h - 3.4  # top of the boxes inside the band


def path_step(cy, n, text):
    icon_disc(50, cy, 1.7, TEAL, str(n), fs=12)
    ax.text(52.4, cy, f"{n}  {text}", fontsize=9.8, color=TEAL, va="center")


# ---------------------------------------------------------------- title
box(1, 139.5, 98, 5.0, face=NAVY, edge=NAVY, lw=0, r=0.7)
ax.text(3, 142.0, "Azure AI Native Governance \u2014 Architecture  (Azure-style, layerwise)",
        fontsize=19, fontweight="bold", color="white", va="center", ha="left")
ax.text(97, 142.0, "Figure 1", fontsize=12, fontweight="bold",
        color="#BFD9F2", va="center", ha="right")
ax.text(50, 137.6, "Version v1.0  \u2022  10 November 2026  \u2022  Status: Lab / portfolio  \u2022  SIMULATED tenant: Nordlicht GmbH  \u2022  Synthetic data only \u2014 no live Azure tenant access",
        fontsize=9.5, color=GREY, va="center", ha="center")

# ------------------------------------------------- LAYER 1 — Experience
top = layer(124, 12.5, "LAYER 1 \u2014 Experience  \u2022  Users, Azure Portal, AI agents",
            LIGHT2, "#9CC8E4")
# 5 boxes in one row: narrower than the 4-box rows
bw, gap = 18.0, 1.25
exp = [
    ("User (Entra ID)", "MFA + Conditional Access", "\u25CF", AZURE),
    ("Azure Front Door", "Global entry point", "\u25B2", AZURE),
    ("Azure CDN", "Static content delivery", "\u2601", AZURE),
    ("Azure DNS", "DNS lookup", "DNS", AZURE),
    ("Internet", "User traffic", "\u2601", AZURE),
]
for i, (t, s, g, c) in enumerate(exp):
    x = 2.5 + i * (bw + gap)
    box(x, top - 6.8, bw, 6.8, face=WHITE, edge=AZURE, lw=1.5)
    icon_disc(x + 2.4, top - 3.4, 1.8, c, g, fs=9 if g == "DNS" else 12)
    ax.text(x + 4.9, top - 2.3, t, fontsize=9.2, fontweight="bold",
            color=DARK, va="center")
    ax.text(x + 4.9, top - 4.6, s, fontsize=8.2, color=GREY, va="center")
path_step(122.4, 1, "User asks an agent / opens the Portal")

# --------------------------------------- LAYER 2 — Azure native controls
top = layer(109.5, 12.5, "LAYER 2 \u2014 Azure native controls  \u2022  What Microsoft DOES govern",
            "#E6F4F3", TEAL)
bw = 22.9
ctrl = [
    ("Azure Policy", "Deny / Audit by region,\nSKU, encryption", "\u2696", TEAL),
    ("Defender for Cloud", "Secure score 62%\nrecommendations + alerts", "\u2713", TEAL),
    ("Entra ID", "MFA + Conditional Access\nAgent identity + sponsor", "K", TEAL),
    ("Azure OpenAI / AI Foundry", "Content filters\njailbreak + harmful content", "\u2605", TEAL),
]
for i, (t, s, g, c) in enumerate(ctrl):
    x = 3 + i * (bw + 1.1)
    cell(x, top - 6.8, bw, 6.8, g, c, t, s, edge=TEAL)
path_step(107.9, 2, "Azure native controls check the resource")

# ----------------------------------------- LAYER 3 — Simulated Azure estate
top = layer(84, 23.5, "LAYER 3 \u2014 Simulated Azure estate  \u2022  app/connectors/azure.py  (SIMULATED: Nordlicht GmbH)",
            LIGHT2, "#9CC8E4")
# Active region sub-box (top 104.6, clear of the band heading at ~105.9)
box(3, 95.8, 94, 8.8, face=LIGHT, edge="#9CC8E4", lw=1.3)
ax.text(4.5, 103.6, "Active region \u2014 Germany West Central", fontsize=10,
        fontweight="bold", color=NAVY, va="center")
# Web App
box(4.5, 96.8, 19, 5.6, face=MID, edge=AZURE, lw=1.3)
ax.text(14, 101.8, "App Service plan", fontsize=8.2, color=GREY,
        va="center", ha="center")
icon_disc(8.0, 99.4, 1.8, AZURE, "\u25CF", fs=11)
ax.text(10.6, 99.4, "Web App\nGovernance Agent (FastAPI)", fontsize=8.8,
        fontweight="bold", color=DARK, va="center")
# Queue
box(25.2, 97.6, 7.5, 4.0, face=WHITE, edge=AZURE, lw=1.3)
ax.text(29, 100.6, "Queue", fontsize=8.6, fontweight="bold", color=DARK,
        va="center", ha="center")
ax.text(29, 98.9, "approval", fontsize=8.0, color=GREY, va="center", ha="center")
# Function App
box(34.2, 96.8, 13.5, 5.6, face=MID, edge=AZURE, lw=1.3)
ax.text(41, 101.8, "Function App", fontsize=8.2, color=GREY, va="center", ha="center")
icon_disc(37.6, 99.4, 1.8, "#F2C811", "\u26A1", fs=12, tc=NAVY)
ax.text(40.0, 99.4, "Checks\nrunner", fontsize=8.8, fontweight="bold",
        color=DARK, va="center")
# Data group
box(49.2, 96.8, 31, 5.6, face=MID, edge=AZURE, lw=1.3)
db_icon(55.5, 100.0, color=AZURE)
ax.text(55.5, 97.8, "Redis cache", fontsize=8.6, fontweight="bold", color=DARK,
        va="center", ha="center")
db_icon(64.5, 100.0, color=NAVY)
ax.text(64.5, 97.8, "SQL Database", fontsize=8.6, fontweight="bold", color=DARK,
        va="center", ha="center")
icon_disc(73.5, 100.0, 1.8, NAVY, "\u25CB", fs=12)
ax.text(73.5, 97.8, "Cosmos DB", fontsize=8.6, fontweight="bold", color=DARK,
        va="center", ha="center")
# Blob / Search row inside Active
box(81.7, 96.8, 15.3, 5.6, face=WHITE, edge=AZURE, lw=1.3)
icon_disc(85.0, 99.6, 1.7, AZURE, "\u25A0", fs=11)
ax.text(87.4, 100.6, "Blob + Azure Search", fontsize=8.6, fontweight="bold",
        color=DARK, va="center")
ax.text(87.4, 98.6, "Reports + audit search", fontsize=8.0, color=GREY, va="center")
arrow(23.5, 99.6, 25.2, 99.6)
arrow(32.7, 99.6, 34.2, 99.6)
arrow(47.7, 99.6, 49.2, 99.6)
# Standby region sub-box
box(3, 85.2, 94, 9.0, face=LIGHT, edge="#9CC8E4", lw=1.3)
ax.text(4.5, 92.8, "Standby region \u2014 North Europe  (replicated)", fontsize=10,
        fontweight="bold", color=NAVY, va="center")
ax.text(4.5, 87.6, "Web App (replica)  \u2192  Queue (approval)  \u2192  Function App (checks runner)  \u2192  Redis / SQL / Cosmos (replicated)  \u2022  Blob + Azure Search + OPA decision \u2014 replicated",
        fontsize=9.2, color=DARK, va="center")
# geo-replication arrows: Active data group down to Standby
for x in (64.5, 73.5):
    arrow(x, 96.8, x, 94.2, color=TEAL, lw=2.2)
ax.text(78.5, 95.5, "geo-replication", fontsize=8.5, color=TEAL, va="center")
path_step(82.9, 3, "Gateway checks the simulated estate")

# -------------------------------------------- LAYER 4 — Policy-as-code
top = layer(69.5, 12.5, "LAYER 4 \u2014 Policy-as-code  \u2022  Rego + Python, identical decisions",
            "#E6F4F3", TEAL)
bw = 22.9
pol = [
    ("policies/*.rego", "8 rules", "</>", TEAL),
    ("OPA server :8181", "(via HTTP, or fallback)", "\u2699", TEAL),
    ("app/policy.py", "Python fallback", "</>", TEAL),
    ("app/opa_client.py", "engine: opa |\npython-fallback", "\u221E", TEAL),
]
for i, (t, s, g, c) in enumerate(pol):
    x = 3 + i * (bw + 1.1)
    cell(x, top - 6.8, bw, 6.8, g, c, t, s, edge=TEAL, gfs=10)
path_step(67.9, 4, "OPA / Python decides the call")

# ------------------------------------------- LAYER 5 — Evidence & audit
top = layer(55, 12.5, "LAYER 5 \u2014 Evidence & audit  \u2022  Hash-chained, exportable",
            LIGHT2, "#9CC8E4")
bw = 22.9
ev = [
    ("Evidence register", "SHA-256 chain", "\u221E", NAVY),
    ("Issues workflow", "Open \u2192 Verified \u2192 Closed", "\u26A0", NAVY),
    ("Audit export", "JSON + CSV for\nArcher / OneTrust", "\u2630", NAVY),
    ("KRI dashboard", "+ Power BI CSV", "\u258C", NAVY),
]
for i, (t, s, g, c) in enumerate(ev):
    x = 3 + i * (bw + 1.1)
    cell(x, top - 6.8, bw, 6.8, g, c, t, s, edge=AZURE, gfs=11)
path_step(53.4, 5, "Decision logged as hash-chained evidence")

# ------------------------- LAYER 6 — What Azure native does vs gateway
top = layer(40.5, 12.5, "LAYER 6 \u2014 What Azure native does vs what the gateway does",
            AMBER_BG, AMBER)
bw = 22.9
six = [
    ("Azure native CAN:", "Policy, Defender, Entra,\nKey Vault, content filters", "\u2713", AMBER),
    ("Azure native CANNOT:", "per-tool-call decision,\ntool pinning, approval", "\u2717", AMBER),
    ("Gateway (M365 project):", "OPA decision per tool call\n+ human approval", "\u2696", AMBER),
    ("GRC record (Archer / OneTrust):", "risk register\n+ evidence + audit", "\u2630", AMBER),
]
for i, (t, s, g, c) in enumerate(six):
    x = 3 + i * (bw + 1.1)
    cell(x, top - 6.8, bw, 6.8, g, c, t, s, edge=AMBER, gfs=11)

# ------------------------------------------------------------- DATA FLOWS
ax.text(3, 37.6, "DATA FLOWS \u2014 in the same picture", fontsize=12,
        fontweight="bold", color=NAVY, va="center")


def flow_row(y, label, color, steps, w):
    ax.text(3, y + 5.6, label, fontsize=10.5, fontweight="bold", color=color,
            va="center")
    for i, (t, s) in enumerate(steps):
        x = 3 + i * (w + 1.0)
        box(x, y - 1.2, w, 5.4, face=WHITE, edge=color, lw=1.5)
        icon_disc(x + 2.4, y + 1.5, 1.8, color, str(i + 1), fs=12)
        ax.text(x + 4.9, y + 2.4, t, fontsize=8.8, color=DARK, va="center")
        if s:
            ax.text(x + 4.9, y + 0.4, s, fontsize=8.2, color=GREY, va="center")
        if i < len(steps) - 1:
            arrow(x + w, y + 1.5, x + w + 1.0, y + 1.5, color=color, lw=1.8)


flow_a = [
    ("Azure resource", "VM / storage / AI\ncreated or changed"),
    ("Azure Policy", "allowed locations,\npublic blob, encryption"),
    ("Decision", "Deny / Audit\nAudit-only = report only"),
    ("Defender for Cloud", "secure score\nrecommendation"),
    ("Evidence", "hash-chained\n+ issue if Fail"),
]
flow_row(29.5, "A \u00b7 Azure Policy evaluation  (resource \u2192 policy \u2192 decision)",
         RED, flow_a, 18.4)

flow_b = [
    ("AI Agent", "ops-agent\ntool: azure.vm.start"),
    ("Azure native", "native_decision = None\nit never sees the call"),
    ("Gateway (M365 project)", "POST /agent/action\n(PEP)"),
    ("OPA server", "or Python fallback\n(PDP) \u2192 needs_approval"),
    ("Human approves", "or rejects\nin /approvals"),
    ("Tool call", "executed or blocked\n+ audit log"),
]
flow_row(20.5, "B \u00b7 Agent tool call  (Agent \u2192 Gateway \u2192 native: no decision \u2192 OPA \u2192 Decision)",
         TEAL, flow_b, 15.2)
ax.text(50, 17.6, "OPA decision:  allow \u2192 tool executes   \u2022   deny \u2192 blocked   \u2022   needs_approval \u2192 human approves in /approvals",
        fontsize=9.5, color=GREY, va="center", ha="center")

# ------------------------------------------------------------- gap strip
box(2, 10.0, 96, 6.0, face=AMBER_BG, edge=AMBER, lw=1.6)
ax.text(50, 14.6, "THE GAP \u2014 in one line", fontsize=11, fontweight="bold",
        color=AMBER, va="center", ha="center")
ax.text(50, 12.2, "Azure native applications govern resources, identity, network and model content \u2014 none of them decides an individual MCP tool call.  That is the gap the gateway fills.",
        fontsize=10.5, color=DARK, va="center", ha="center")

# ------------------------------------------------------------- legend/footer
ax.text(2, 7.6, "Legend:", fontsize=10, fontweight="bold", color=DARK, va="center")
ax.text(10, 7.6, "\u2192  request / data flow", fontsize=9.5, color=GREY, va="center")
ax.text(32, 7.6, "\u2192  geo-replication (teal)", fontsize=9.5, color=TEAL, va="center")
ax.text(58, 7.6, "Light-blue box = Azure region / estate", fontsize=9.5, color=GREY, va="center")
ax.text(84, 7.6, "Amber = gateway decision", fontsize=9.5, color=AMBER, va="center")
ax.text(50, 4.6, "Regenerate:  python3 scripts/make_azure_style_layerwise.py   \u2022   Project: ~/workspace/projects/azure-native-governance/",
        fontsize=9, color=GREY, va="center", ha="center")
ax.text(50, 1.8, "Azure native applications govern resources, identity, network and model content \u2014 none of them decides an individual MCP tool call.  That is the gap the gateway fills.",
        fontsize=10, style="italic", color=GREY, va="center", ha="center")

plt.tight_layout(pad=0.5)
plt.savefig(OUT, dpi=200)
print(f"Wrote {OUT}  {OUT.stat().st_size} bytes")
