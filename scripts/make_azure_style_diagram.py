#!/usr/bin/env python3
"""Azure-style multi-region architecture diagram for Azure AI Native Governance.

Regenerate:  python3 scripts/make_azure_style_diagram.py
Output:       docs/architecture-azure-style.png  (4000 x 2800 px)
Style: Microsoft Azure reference-diagram style — light-blue region boxes
(Active on top, Standby below), entry on the left, data services on the
right, blue flow arrows, geo-replication between regions.
All icons are vector pictograms drawn with matplotlib patches / DejaVu
glyphs — no emoji (they render as tofu on this VM).
"""
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Circle, Ellipse, Rectangle, FancyArrowPatch

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "docs" / "architecture-azure-style.png"

AZURE = "#0078D4"
NAVY = "#0B2C5F"
DARK = "#1B3A5C"
LIGHT = "#DCEEF9"
LIGHT2 = "#EAF4FB"
MID = "#BFE0F2"
TEAL = "#0E7C7B"
AMBER = "#B45309"
AMBER_BG = "#FEF3C7"
GREY = "#475569"
WHITE = "white"

fig, ax = plt.subplots(figsize=(20, 14))
ax.set_xlim(0, 100)
ax.set_ylim(0, 100)
ax.axis("off")
fig.patch.set_facecolor("white")
ax.set_facecolor("white")


def box(x, y, w, h, face=WHITE, edge=AZURE, lw=1.6, r=0.7):
    p = FancyBboxPatch((x, y), w, h, boxstyle=f"round,pad=0,rounding_size={r}",
                       facecolor=face, edgecolor=edge, linewidth=lw)
    ax.add_patch(p)
    return p


def region(x, y, w, h, label):
    box(x, y, w, h, face=LIGHT2, edge="#9CC8E4", lw=1.4, r=0.8)
    ax.text(x + 1.2, y + h - 2.2, label, fontsize=13, fontweight="bold",
            color=NAVY, va="center", ha="left")


def icon_disc(cx, cy, r, color, glyph, fs=15, tc="white"):
    # x-unit is 0.20 inch, y-unit is 0.14 inch, so scale x-radius by 0.7
    ax.add_patch(Ellipse((cx, cy), 2 * r * 0.7, 2 * r, facecolor=color, edgecolor="none", zorder=5))
    ax.text(cx, cy - 0.15, glyph, fontsize=fs, color=tc, ha="center",
            va="center", fontweight="bold", zorder=6)


def label(x, y, title, sub, tc=DARK, ts=10.5, ss=8.8, align="left"):
    ax.text(x, y, title, fontsize=ts, fontweight="bold", color=tc,
            va="center", ha=align)
    if sub:
        ax.text(x, y - 2.6, sub, fontsize=ss, color=GREY, va="center", ha=align)


def arrow(x1, y1, x2, y2, color=AZURE, lw=2.0, style="-|>", ms=14):
    ax.add_patch(FancyArrowPatch((x1, y1), (x2, y2), arrowstyle=style,
                                 mutation_scale=ms, linewidth=lw, color=color,
                                 shrinkA=0, shrinkB=0, zorder=4))


def db_icon(cx, cy, color=AZURE):
    # cylinder: body + top ellipse
    ax.add_patch(Rectangle((cx - 1.12, cy - 1.4), 2.24, 2.4, facecolor=color,
                           edgecolor="none", zorder=5))
    ax.add_patch(Ellipse((cx, cy + 1.0), 2.24, 1.1, facecolor="#5EB0E5",
                         edgecolor="none", zorder=6))
    ax.add_patch(Ellipse((cx, cy - 1.4), 2.24, 1.1, facecolor=color,
                         edgecolor="none", zorder=6))


# ---------------------------------------------------------------- title
box(1, 94.5, 98, 5.0, face=NAVY, edge=NAVY, lw=0, r=0.7)
ax.text(3, 97.0, "Azure AI Native Governance \u2014 Architecture  (Azure-style, multi-region)",
        fontsize=19, fontweight="bold", color="white", va="center", ha="left")
ax.text(97, 97.0, "Figure 1", fontsize=12, fontweight="bold",
        color="#BFD9F2", va="center", ha="right")
ax.text(50, 92.6, "Version v1.0  \u2022  10 November 2026  \u2022  Status: Lab / portfolio  \u2022  SIMULATED tenant: Nordlicht GmbH  \u2022  Synthetic data only \u2014 no live Azure tenant access",
        fontsize=9.5, color=GREY, va="center", ha="center")

# ------------------------------------------------------- control plane
ax.text(2, 90.4, "CONTROL PLANE \u2014 what Azure native governs", fontsize=11,
        fontweight="bold", color=NAVY, va="center", ha="left")
controls = [
    ("Azure Policy", "Deny / Audit by region,\nSKU, encryption", "\u2696", TEAL),
    ("Defender for Cloud", "Secure score 62%\nrecommendations + alerts", "\u2713", TEAL),
    ("Key Vault", "RBAC, secret expiry\npurge protection", "K", TEAL),
    ("Azure OpenAI / AI Foundry", "Content filters\njailbreak + harmful content", "\u2605", TEAL),
    ("Gateway (this project)", "OPA decision per tool call\n+ human approval", "\u2696", AMBER),
]
cw, gap = 18.6, 1.2
for i, (t, s, g, c) in enumerate(controls):
    x = 2 + i * (cw + gap)
    face = AMBER_BG if i == 4 else WHITE
    edge = AMBER if i == 4 else TEAL
    box(x, 82.6, cw, 6.6, face=face, edge=edge, lw=1.6)
    icon_disc(x + 2.4, 85.9, 1.9, c, g, fs=13)
    ax.text(x + 5.0, 87.2, t, fontsize=10, fontweight="bold", color=DARK, va="center")
    ax.text(x + 5.0, 84.9, s, fontsize=8.4, color=GREY, va="center")
ax.text(50, 80.9, "Native controls govern resources, identity, network and model content \u2014 NONE of them decides a per-MCP tool call.  That decision is the gateway.",
        fontsize=10, fontweight="bold", color=AMBER, va="center", ha="center")

# ------------------------------------------------------------- left entry
ax.text(2, 77.6, "ENTRY", fontsize=11, fontweight="bold", color=NAVY, va="center")
entry = [
    (74.0, "User  (Entra ID)", "MFA + Conditional Access", "\u25CF", AZURE),
    (67.0, "Internet", "", "\u2601", AZURE),
    (60.0, "Azure DNS", "DNS lookup", "DNS", AZURE),
    (53.0, "Azure Front Door", "Global entry point", "\u25B2", AZURE),
    (46.0, "Azure CDN", "Static content delivery", "\u2601", AZURE),
]
for cy, t, s, g, c in entry:
    box(2, cy - 3.0, 17, 6.0, face=WHITE, edge=AZURE, lw=1.6)
    icon_disc(5.0, cy, 1.9, c, g, fs=10 if g == "DNS" else 13)
    ax.text(7.6, cy + (0.9 if s else 0), t, fontsize=10.5, fontweight="bold",
            color=DARK, va="center")
    if s:
        ax.text(7.6, cy - 1.5, s, fontsize=8.4, color=GREY, va="center")
# entry arrows: user -> internet -> dns -> front door, and cdn -> front door
arrow(10.5, 71.0, 10.5, 70.0)
arrow(10.5, 64.0, 10.5, 63.0)
arrow(10.5, 57.0, 10.5, 56.0)
# front door -> active region (right), and -> standby region via the gap
# between the entry column (ends x=19) and the regions (start x=23),
# so the line never crosses the CDN box
arrow(19.0, 53.0, 21.0, 53.0)
arrow(21.0, 53.0, 21.0, 38.0)
arrow(21.0, 38.0, 23.0, 38.0)
ax.text(22.3, 45.5, "to Standby", fontsize=8.5, color=AZURE, ha="center",
        rotation=90, va="center")

# ---------------------------------------------------------- region helper
def draw_region(y0, label, sub_label, standby=False):
    """Region box y0..y0+20, x 23..98. Returns dict of key x-centres."""
    region(23, y0, 75, 20, label)
    ax.text(96.5, y0 + 17.8, sub_label, fontsize=9, color=GREY,
            va="center", ha="right")
    # --- compute row (app) y  y0+10.5 .. y0+17, data row y0+1.5 .. y0+9
    # App Service plan box (Web App)
    box(24.5, y0 + 10.5, 17, 6.5, face=MID, edge=AZURE, lw=1.4)
    ax.text(33, y0 + 16.2, "App Service plan", fontsize=8.8, color=GREY,
            va="center", ha="center")
    icon_disc(28.5, y0 + 13.4, 2.0, AZURE, "\u25CF", fs=12)
    ax.text(31.2, y0 + 13.4, "Web App\nGovernance Agent\n(FastAPI)", fontsize=9.2,
            fontweight="bold", color=DARK, va="center")
    # Queue
    box(43.5, y0 + 12.0, 7, 3.6, face=WHITE, edge=AZURE, lw=1.4)
    ax.text(47, y0 + 14.6, "Queue", fontsize=8.8, fontweight="bold",
            color=DARK, va="center", ha="center")
    ax.text(47, y0 + 13.0, "approval", fontsize=8.2, color=GREY,
            va="center", ha="center")
    # Function App
    box(52.5, y0 + 10.5, 13, 6.5, face=MID, edge=AZURE, lw=1.4)
    ax.text(59, y0 + 16.2, "Function App", fontsize=8.8, color=GREY,
            va="center", ha="center")
    icon_disc(56.2, y0 + 13.4, 1.9, "#F2C811", "\u26A1", fs=13, tc=NAVY)
    ax.text(58.6, y0 + 13.4, "Checks\nrunner", fontsize=9.2, fontweight="bold",
            color=DARK, va="center")
    # Data group box
    box(67.5, y0 + 10.5, 29, 6.5, face=MID, edge=AZURE, lw=1.4)
    # Redis
    db_icon(72.5, y0 + 13.8, color=AZURE)
    ax.text(72.5, y0 + 11.4, "Redis cache", fontsize=8.8, fontweight="bold",
            color=DARK, va="center", ha="center")
    # SQL
    db_icon(81.5, y0 + 13.8, color=NAVY)
    ax.text(81.5, y0 + 11.4, "SQL Database", fontsize=8.8, fontweight="bold",
            color=DARK, va="center", ha="center")
    ax.text(81.5, y0 + 10.9 - 1.2, "", fontsize=8, color=GREY, va="center", ha="center")
    # Cosmos
    icon_disc(90.5, y0 + 13.8, 2.0, NAVY, "\u25CB", fs=13)
    ax.text(90.5, y0 + 11.4, "Cosmos DB", fontsize=8.8, fontweight="bold",
            color=DARK, va="center", ha="center")
    # --- data row: SQL detail / Cosmos detail / Blob+Search
    # (detail captions moved into the data labels above; nothing here,
    # so the lower row of boxes is not overlapped)
    # Blob / static + Azure Search (bottom row of region)
    box(24.5, y0 + 1.8, 17, 6.0, face=WHITE, edge=AZURE, lw=1.4)
    icon_disc(28.5, y0 + 4.8, 1.9, AZURE, "\u25A0", fs=12)
    ax.text(31.2, y0 + 5.6, "Blob", fontsize=9.2, fontweight="bold", color=DARK, va="center")
    ax.text(31.2, y0 + 3.6, "Reports + static content", fontsize=8.4, color=GREY, va="center")
    box(67.5, y0 + 1.8, 14, 6.0, face=WHITE, edge=AZURE, lw=1.4)
    icon_disc(71.5, y0 + 4.8, 1.9, AZURE, "Q", fs=12)
    ax.text(74.2, y0 + 5.6, "Azure Search", fontsize=9.2, fontweight="bold",
            color=DARK, va="center")
    ax.text(74.2, y0 + 3.6, "Audit search", fontsize=8.4, color=GREY, va="center")
    # OPA decision box (bottom right of region)
    box(83.5, y0 + 1.8, 13, 6.0, face=AMBER_BG, edge=AMBER, lw=1.4)
    ax.text(90, y0 + 5.6, "OPA decision", fontsize=9.2, fontweight="bold",
            color=AMBER, va="center", ha="center")
    ax.text(90, y0 + 3.6, "allow / deny /\nneeds_approval", fontsize=8.4,
            color=GREY, va="center", ha="center")
    # arrows inside region: web -> queue -> function -> data
    arrow(41.5, y0 + 13.8, 43.5, y0 + 13.8)
    arrow(50.5, y0 + 13.8, 52.5, y0 + 13.8)
    arrow(65.5, y0 + 13.8, 67.5, y0 + 13.8)
    return {"sql_x": 81.5, "cosmos_x": 90.5, "blob_x": 33.0, "search_x": 74.5}


active = draw_region(58, "Active region", "Germany West Central", standby=False)
standby = draw_region(30, "Standby region", "North Europe  (replicated)", standby=True)

# geo-replication arrows on the right side, active -> standby
for x in (81.5, 90.5):
    arrow(x, 58.0, x, 50.0, color=TEAL, lw=2.2)
    ax.text(x + 1.0, 54.0, "geo-replication", fontsize=8.5, color=TEAL,
            va="center", ha="left", rotation=90)
# blob replication (left side of data area)
arrow(33.0, 58.0, 33.0, 50.0, color=TEAL, lw=2.2)

# ------------------------------------------------------------- flow note
ax.text(50, 26.5, "Request flow:  User \u2192 Entra ID \u2192 Azure Front Door \u2192 Web App (Governance Agent) \u2192 Queue \u2192 Function App (checks) \u2192 SQL / Cosmos / Redis",
        fontsize=10.5, fontweight="bold", color=NAVY, va="center", ha="center")
ax.text(50, 23.5, "Gateway demo (lab, 10 Nov 2026):  azure.storage.read \u2192 allow  \u2022  azure.vm.start \u2192 needs_approval \u2192 approved \u2192 allow  \u2022  shadow agent azure.keyvault.get_secret \u2192 deny  \u2022  social scoring \u2192 deny (EU AI Act Art. 5)  \u2022  native decision in every case: none",
        fontsize=9.5, color=DARK, va="center", ha="center")

# ------------------------------------------------------------- gap strip
box(2, 14.5, 96, 6.5, face=AMBER_BG, edge=AMBER, lw=1.6)
ax.text(50, 19.2, "THE GAP \u2014 in one line", fontsize=11, fontweight="bold",
        color=AMBER, va="center", ha="center")
ax.text(50, 16.6, "Azure native applications govern resources, identity, network and model content \u2014 none of them decides an individual MCP tool call.  That is the gap the gateway fills.",
        fontsize=10.5, color=DARK, va="center", ha="center")

# ------------------------------------------------------------- legend/footer
ax.text(2, 11.5, "Legend:", fontsize=10, fontweight="bold", color=DARK, va="center")
ax.text(10, 11.5, "\u2192  request / data flow", fontsize=9.5, color=GREY, va="center")
ax.text(32, 11.5, "\u2192  geo-replication (teal)", fontsize=9.5, color=TEAL, va="center")
ax.text(58, 11.5, "Light-blue box = Azure region", fontsize=9.5, color=GREY, va="center")
ax.text(84, 11.5, "Amber = gateway decision", fontsize=9.5, color=AMBER, va="center")
ax.text(50, 8.5, "Regenerate:  python3 scripts/make_azure_style_diagram.py   \u2022   Project: ~/workspace/projects/azure-native-governance/",
        fontsize=9, color=GREY, va="center", ha="center")
ax.text(50, 5.5, "Azure native applications govern resources, identity, network and model content \u2014 none of them decides an individual MCP tool call.  That is the gap the gateway fills.",
        fontsize=10, style="italic", color=GREY, va="center", ha="center")

plt.tight_layout(pad=0.5)
plt.savefig(OUT, dpi=200)
print(f"Wrote {OUT}  {OUT.stat().st_size} bytes")
