"""Regenerate ONE combined architecture diagram (v1.1).

v1.1 fix: layer headings now sit cleanly above their boxes (larger
band + heading/box gap) and the Flow B outcome line sits cleanly
below its boxes (larger flow-row spacing).


Run (from the project root):  python3 scripts/make_diagrams.py
docs/architecture.png contains the 6 layers AND both data flows in one
balanced picture. docs/dataflow.png is an identical copy, so there are
no two different diagrams.

Icons are drawn vector pictograms (white on a coloured disc) plus
DejaVu glyphs verified to render (star, scales, gear, warning, check).
No colour emoji — they render as blank tofu boxes on this VM.
"""
from pathlib import Path
import shutil

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Circle, FancyArrowPatch, FancyBboxPatch, Polygon, Rectangle

OUT = Path(__file__).resolve().parent.parent / "docs"
OUT.mkdir(exist_ok=True)

NAVY = "#0b3d91"; NAVY_DARK = "#062a63"; NAVY_LIGHT = "#e8eefb"
TEAL = "#0e7c7b"; TEAL_LIGHT = "#e6f4f3"
AMBER = "#b45309"; AMBER_LIGHT = "#fef3e2"
RED = "#b42318"; RED_LIGHT = "#fdf0ee"
SLATE = "#475569"; INK = "#1e293b"; WHITE = "#ffffff"; GREY = "#cbd5e1"

FOOTER = "Azure native applications govern resources, identity, network and model content — none of them decides an individual MCP tool call. That is the gap the gateway fills."

LAYERS = [
    ("LAYER 1 — Experience  •  Users, Azure Portal, AI agents", NAVY, NAVY_LIGHT, [
        ("●", "User (Entra ID)\nMFA + Conditional Access"),
        ("✦", "Azure Portal\n+ Azure CLI / PowerShell"),
        ("◉", "Azure AI Foundry agents\nAgent Service runtime"),
        ("●●", "Copilot Studio agents\nDeclarative + custom-engine"),
    ]),
    ("LAYER 2 — Azure native controls  •  What Microsoft DOES govern", TEAL, TEAL_LIGHT, [
        ("⚖", "Azure Policy\nDeny / Audit by region,\nSKU, encryption"),
        ("✓", "Defender for Cloud\nSecure score 62%\nrecommendations + alerts"),
        ("K", "Entra ID\nMFA + Conditional Access\nAgent identity + sponsor"),
        ("K", "Key Vault\nRBAC, secret expiry\npurge protection"),
    ]),
    ("LAYER 3 — Simulated Azure estate  •  app/connectors/azure.py  (SIMULATED: Nordlicht GmbH)", NAVY, NAVY_LIGHT, [
        ("▣", "Subscriptions + RGs\n1 subscription, 4 RGs\n1 RG outside EU regions"),
        ("▣", "VMs + Storage\n6 VMs, 8 storage accounts\n2 public, 3 unencrypted"),
        ("K", "Key Vaults + AI\n3 vaults, 4 AI resources\n1 AI resource unfiltered"),
        ("◉", "Monitor / Sentinel\nAudit logs after the fact\nno pre-call decision"),
    ]),
    ("LAYER 4 — Policy-as-code  •  Rego + Python, identical decisions", TEAL, TEAL_LIGHT, [
        ("</>", "policies/*.rego\n8 rules"),
        ("⚙", "OPA server :8181\n(via HTTP, or fallback)"),
        ("</>", "app/policy.py\nPython fallback"),
        ("○○", "app/opa_client.py\nengine: opa |\npython-fallback"),
    ]),
    ("LAYER 5 — Evidence & audit  •  Hash-chained, exportable", NAVY, NAVY_LIGHT, [
        ("○○", "Evidence register\nSHA-256 chain"),
        ("⚠", "Issues workflow\nOpen → Verified → Closed"),
        ("▤", "Audit export\nJSON + CSV for\nArcher / OneTrust"),
        ("▮", "KRI dashboard\n+ Power BI CSV"),
    ]),
    ("LAYER 6 — What Azure native does vs what the gateway does", AMBER, AMBER_LIGHT, [
        ("✓", "Azure native CAN:\nPolicy, Defender, Entra,\nKey Vault, content filters"),
        ("✕", "Azure native CANNOT:\nper-tool-call decision,\ntool pinning, approval"),
        ("⚖", "Gateway (M365 project):\nOPA decision per tool call\n+ human approval"),
        ("▤", "GRC record (Archer /\nOneTrust): risk register\n+ evidence + audit"),
    ]),
]

FLOWS = [
    ("A · Azure Policy evaluation (resource → policy → decision)", RED, [
        ("1", "Azure resource\nVM / storage / AI\ncreated or changed"),
        ("2", "Azure Policy\nallowed locations,\npublic blob, encryption"),
        ("3", "Decision\nDeny / Audit\nAudit-only = report only"),
        ("4", "Defender for Cloud\nsecure score\nrecommendation"),
        ("5", "Evidence\nhash-chained\n+ issue if Fail"),
    ]),
    ("B · Agent tool call (Agent → Gateway → native: no decision → OPA → Decision)", TEAL, [
        ("1", "AI Agent\nops-agent\ntool: azure.vm.start"),
        ("2", "Azure native\nnative_decision = None\nit never sees the call"),
        ("3", "Gateway (M365 project)\nPOST /agent/action\n(PEP)"),
        ("4", "OPA server\nor Python fallback\n(PDP) → needs_approval"),
        ("5", "Human approves\nor rejects\nin /approvals"),
        ("6", "Tool call\nexecuted or blocked\n+ audit log"),
    ]),
]


def _box(ax, x, y, w, h, icon, text, edge, face=WHITE, fs=8.5):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.06,rounding_size=0.10",
                                facecolor=face, edgecolor=edge, linewidth=1.4))
    # icon disc on the left
    cx, cy = x + 0.42, y + h / 2
    ax.add_patch(Circle((cx, cy), 0.30, facecolor=edge, edgecolor=edge, zorder=3))
    ax.text(cx, cy, icon, ha="center", va="center", fontsize=11, color=WHITE, weight="bold", zorder=4)
    ax.text(x + 0.85, y + h / 2, text, ha="left", va="center", fontsize=fs, color=INK)


def _arrow(ax, x1, y1, x2, y2, color=NAVY):
    ax.add_patch(FancyArrowPatch((x1, y1), (x2, y2), arrowstyle="-|>", mutation_scale=12,
                                 color=color, linewidth=1.4, shrinkA=2, shrinkB=2))


def combined():
    # Taller canvas (17 units) so headings, boxes, flow rows and the
    # Flow B outcome line each have clear vertical space.
    fig, ax = plt.subplots(figsize=(16, 16))
    ax.set_xlim(0, 16); ax.set_ylim(0, 17); ax.axis("off")
    # title block
    ax.add_patch(FancyBboxPatch((0.3, 15.55), 15.4, 0.85, boxstyle="round,pad=0.05,rounding_size=0.12",
                                facecolor=NAVY_DARK, edgecolor=NAVY_DARK))
    ax.text(0.7, 15.98, "Azure AI Native Governance — Architecture", fontsize=17, weight="bold", color=WHITE, va="center")
    ax.text(15.35, 15.98, "Figure 1", fontsize=11, weight="bold", color="#bfdbfe", va="center", ha="right")
    ax.text(0.4, 15.25, "Version v1.1  •  10 November 2026  •  Status: Lab / portfolio  •  icons added",
            fontsize=9.5, color=SLATE, va="center")
    ax.text(15.6, 15.25, "SIMULATED tenant: Nordlicht GmbH", fontsize=9.5, color=SLATE, va="center", ha="right")
    ax.text(8, 14.95, "Synthetic data only  •  No live Azure tenant access  •  The user's Azure for Students subscription is live, but this lab does not call it",
            ha="center", fontsize=9, color=SLATE)
    y = 14.55
    for title, colour, band, boxes in LAYERS:
        # Band is 1.30 high; heading sits near its top, boxes start
        # 0.44 below the band top, so the heading is never touched
        # by a box top edge.
        ax.add_patch(Rectangle((0.3, y - 1.30), 15.4, 1.30, facecolor=band, edgecolor=GREY, linewidth=0.8))
        ax.text(0.45, y - 0.18, title, fontsize=10, weight="bold", color=colour, va="center")
        for i, (icon, txt) in enumerate(boxes):
            _box(ax, 0.45 + i * 3.90, y - 1.12, 3.70, 0.68, icon, txt, colour, fs=8.2)
        # numbered flow label between layers
        idx = LAYERS.index((title, colour, band, boxes))
        if idx < 5:
            ax.add_patch(Circle((8.0, y - 1.42), 0.16, facecolor=TEAL, edgecolor=TEAL, zorder=3))
            ax.text(8.0, y - 1.42, str(idx + 1), ha="center", va="center", fontsize=9, color=WHITE, weight="bold", zorder=4)
            labels = ["1  User asks an agent / opens the Portal", "2  Azure native controls check the resource",
                      "3  Gateway checks the simulated estate", "4  OPA / Python decides the call",
                      "5  Decision logged as hash-chained evidence"]
            ax.text(8.25, y - 1.42, labels[idx], fontsize=8.5, color=TEAL, va="center")
        y -= 1.55
    # flow strip
    y -= 0.05
    ax.text(0.4, y, "DATA FLOWS — in the same picture", fontsize=11, weight="bold", color=NAVY, va="center")
    y -= 0.35
    for title, colour, steps in FLOWS:
        ax.text(0.4, y, title, fontsize=10, weight="bold", color=colour, va="center")
        y -= 0.30
        for i, (num, step) in enumerate(steps):
            x = 0.4 + i * (15.2 / len(steps))
            w = 15.2 / len(steps) - 0.18
            _box(ax, x, y - 0.85, w, 0.85, num, step, colour, fs=7.8)
            if i + 1 < len(steps):
                _arrow(ax, x + w, y - 0.48, x + w + 0.18, y - 0.48, colour)
        # 1.25 gap after each flow row: the Flow B outcome line ends
        # up ~0.35 below the Flow B box bottoms, not touching them.
        y -= 1.25
    ax.text(8, y + 0.05, "OPA decision:  allow → tool executes   •   deny → blocked   •   needs_approval → human approves in /approvals",
            ha="center", fontsize=9, color=SLATE)
    y -= 0.35
    ax.text(0.4, y, "Legend:", fontsize=9, weight="bold", color=INK, va="center")
    ax.text(1.3, y, "▢  Azure native / experience", fontsize=9, color=SLATE, va="center")
    ax.text(5.6, y, "▢  This project (Azure AI Native Governance)", fontsize=9, color=SLATE, va="center")
    ax.text(10.2, y, "▢  Comparison / GRC record", fontsize=9, color=SLATE, va="center")
    ax.text(13.6, y, "┄  Tenant boundary", fontsize=9, color=SLATE, va="center")
    y -= 0.45
    ax.text(8, y, FOOTER, ha="center", fontsize=9, style="italic", color=SLATE, wrap=True)
    fig.tight_layout()
    fig.savefig(OUT / "architecture.png", dpi=200, bbox_inches="tight")
    plt.close(fig)
    shutil.copyfile(OUT / "architecture.png", OUT / "dataflow.png")
    print("wrote", OUT / "architecture.png", "and identical copy", OUT / "dataflow.png")


if __name__ == "__main__":
    combined()
