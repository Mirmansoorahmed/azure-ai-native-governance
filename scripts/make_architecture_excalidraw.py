#!/usr/bin/env python3
"""Azure AI Native Governance — Excalidraw-style architecture diagram.

Style: hand-drawn Excalidraw look (rough strokes, Caveat handwriting,
pastel fills, white background), inspired by the user's reference
pictures (style only). Content: ONLY what app/data.py + app/checks.py define
(6 agents, 10 native services, simulated estate: 6 VMs, 8 storage,
3 Key Vaults, 4 AI resources, 20 users, 16 checks, 8 Rego policies,
28 controls, 12 risks). No invented services.

Outputs (same layout, two formats):
  docs/architecture-excalidraw.png       — rendered PNG (4800 x 3360)
  docs/architecture-excalidraw.excalidraw — real Excalidraw file, opens at excalidraw.com

Regenerate:  python3 scripts/make_architecture_excalidraw.py
"""
import json
import math
import os
import random

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager
from matplotlib.patches import Ellipse, FancyBboxPatch, Polygon

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
DOCS = os.path.join(ROOT, "docs")
FONT = os.path.join(DOCS, "fonts", "Caveat.ttf")
if os.path.exists(FONT):
    font_manager.fontManager.addfont(FONT)
CAVEAT = "Caveat"

# Excalidraw canvas (units) — PNG is 2x this size
W, H = 2400, 2040
INK = "#1e1e1e"
BLUE = "#a5d8ff"
LBLUE = "#d0ebff"
AMBER = "#ffe8a3"
PURPLE = "#e5dbff"
PINK = "#ffc9e3"
GREEN = "#b2f2bb"
GREY = "#495057"
RED = "#c92a2a"

rng = random.Random(7)

# ---------------------------------------------------------------- layout
# (kind, x, y, w, h, fill, title, sub)   sub may contain "\n"
BOXES = [
    ("round", 60, 150, 560, 150, "#f8f9fa", "Task: show what Azure", "native can + cannot do"),
    ("round", 1780, 150, 560, 150, "#f8f9fa", "Rule: one decision", "per tool call"),
    ("ellipse", 60, 360, 300, 260, BLUE, "Agents", "6 agents · 3 active"),
    ("round", 470, 360, 400, 260, AMBER, "Gateway", "FastAPI · local lab\nnot an Azure service"),
    ("diamond", 980, 360, 330, 260, "#fff3bf", "OPA decides", "allow · deny\napprove"),
    ("round", 1420, 360, 330, 260, LBLUE, "Human approves", "one-shot · exact args"),
    ("ellipse", 1860, 360, 420, 260, PURPLE, "Evidence", "hash-chained · export"),
    ("sticky", 470, 670, 400, 180, PINK, "why?", "native sees the resource,\nnever the call"),
    ("sticky", 1420, 670, 400, 180, PINK, "the gap", "no native app decides\none tool call"),
]
# native-services grid: (title, job) — each stops at the tool call
NATIVE = [
    ("Azure Policy", "blocks bad resources"),
    ("Defender", "scores the estate · 62%"),
    ("Entra ID", "who may sign in"),
    ("Key Vault", "guards the secrets"),
    ("Monitor / Sentinel", "sees it after it happened"),
    ("OpenAI filters", "blocks harmful content"),
    ("Foundry / Agent Service", "runs the agent + tools"),
    ("Network", "blocks ports · private paths"),
    ("Purview", "labels + DLP (M365)"),
    ("Agent 365", "registry + sponsor"),
]
GRID = (60, 900, 2280, 560)
ESTATE = (60, 1500, 2280, 140)
DEMO = (60, 1680, 1130, 170)
CHECKS = (1230, 1680, 1110, 170)
GAP = (60, 1890, 2280, 120)

ARROWS = [  # (x1, y1, x2, y2, label or "")
    (360, 490, 470, 490, ""),
    (870, 490, 980, 490, ""),
    (1310, 490, 1420, 490, ""),
    (1750, 490, 1860, 490, ""),
]

# ---------------------------------------------------------------- excalidraw
_el_id = [0]


def _eid():
    _el_id[0] += 1
    return f"el{_el_id[0]}"


def _base(x, y, w, h):
    return {"id": _eid(), "x": x, "y": y, "width": w, "height": h,
            "angle": 0, "strokeColor": INK, "backgroundColor": "transparent",
            "fillStyle": "solid", "strokeWidth": 2, "strokeStyle": "solid",
            "roughness": 1.5, "opacity": 100, "groupIds": [],
            "frameId": None, "roundness": {"type": 3},
            "seed": rng.randint(1, 100000), "version": 1,
            "versionNonce": rng.randint(1, 100000), "isDeleted": False,
            "boundElements": None, "updated": 1, "link": None, "locked": False}


def _text(x, y, s, size=32, bold=False):
    e = _base(x, y, len(s) * size * 0.55, size * 1.25)
    e.update({"type": "text", "fontSize": size, "fontFamily": 5,
              "text": s, "originalText": s, "lineHeight": 1.25,
              "textAlign": "left", "verticalAlign": "top",
              "containerId": None, "baseline": size,
              "strokeColor": INK, "backgroundColor": "transparent"})
    return e


def build_excalidraw():
    els = []
    els.append(_text(60, 30, "Azure AI Native Governance", 64))
    els.append(_text(60, 105, "Azure native governs resources. The gateway decides the tool call.", 34))
    for kind, x, y, w, h, fill, title, sub in BOXES:
        e = _base(x, y, w, h)
        e["backgroundColor"] = fill
        e["type"] = {"round": "rectangle", "ellipse": "ellipse",
                     "diamond": "diamond", "sticky": "rectangle"}[kind]
        if kind == "sticky":
            e["strokeStyle"] = "dashed"
        els.append(e)
        cx = x + w / 2
        ty = y + 100 if kind == "diamond" else y + 34
        els.append(_text(cx - len(title) * 9, ty, title, 36))
        for i, line in enumerate(sub.split("\n")):
            els.append(_text(cx - len(line) * 7, ty + 62 + i * 38, line, 28))
    # native-services grid container
    e = _base(*GRID[:2], GRID[2], GRID[3])
    e.update({"type": "rectangle", "strokeStyle": "dashed",
              "backgroundColor": "#f8f9fa", "roundness": {"type": 3}})
    els.append(e)
    els.append(_text(90, 920, "WHAT AZURE NATIVE DOES — AND WHERE IT STOPS", 32))
    for i, (title, job) in enumerate(NATIVE):
        gx = 90 + (i % 5) * 452
        gy = 970 + (i // 5) * 240
        e = _base(gx, gy, 430, 210)
        e.update({"type": "rectangle", "backgroundColor": "#ffffff"})
        els.append(e)
        els.append(_text(gx + 18, gy + 16, title, 30))
        els.append(_text(gx + 18, gy + 66, job, 26))
        els.append(_text(gx + 18, gy + 116, "x stops at: the tool call", 26))
    # estate + checks + demo + gap strips
    for (x, y, w, h), title, body in [
            (ESTATE, "THE ESTATE (simulated)",
             "1 subscription · 6 VMs · 8 storage · 3 Key Vaults · 4 AI resources\n"
             "20 users · 6 Policy assignments · Defender 62% · 1 AI resource outside EU"),
            (DEMO, "One call, start to end",
             "storage.read -> allow   ·   vm.start -> approval -> allow\n"
             "keyvault.get_secret -> deny (shadow agent)"),
            (CHECKS, "16 CHECKS — 0 pass · 8 fail · 8 partial",
             "AZ-16 partial by design\n28 controls · 12 risks · 8 Rego rules"),
            (GAP, "THE GAP",
             "Native stops at the tool call. The gateway decides it.")]:
        e = _base(x, y, w, h)
        e.update({"type": "rectangle", "backgroundColor": AMBER if (x, y) == GAP[:2] else "#ffffff"})
        els.append(e)
        els.append(_text(x + 20, y + 14, title, 32))
        for i, line in enumerate(body.split("\n")):
            els.append(_text(x + 20, y + 62 + i * 44, line, 28))
    for x1, y1, x2, y2, _ in ARROWS:
        e = _base(min(x1, x2), min(y1, y2), abs(x2 - x1), max(abs(y2 - y1), 1))
        e.update({"type": "arrow", "points": [[0, 0], [x2 - x1, y2 - y1]],
                  "lastCommittedPoint": None, "startBinding": None,
                  "endBinding": None, "startArrowhead": None,
                  "endArrowhead": "arrow", "backgroundColor": "transparent"})
        els.append(e)
    return {"type": "excalidraw", "version": 2,
            "source": "https://excalidraw.com",
            "elements": els, "appState": {"gridSize": None, "viewBackgroundColor": "#ffffff"},
            "files": {}}


# ---------------------------------------------------------------- png render
def _jitter(v, amt=4):
    return v + rng.uniform(-amt, amt)


def rough_rect(ax, x, y, w, h, fill, edge=INK, lw=2.2, r=18, dashed=False):
    for dx, dy, alpha in ((0, 0, 1.0), (2, -2, 0.35)):
        ax.add_patch(FancyBboxPatch((_jitter(x + dx), _jitter(y + dy)), w, h,
                     boxstyle=f"round,pad=0,rounding_size={r}",
                     facecolor=fill, edgecolor=edge, lw=lw, alpha=alpha,
                     linestyle=(0, (6, 4)) if dashed else "solid"))


def rough_ellipse(ax, x, y, w, h, fill, edge=INK, lw=2.2):
    for dx, dy, alpha in ((0, 0, 1.0), (2, -2, 0.35)):
        ax.add_patch(Ellipse((x + w / 2 + dx, y + h / 2 + dy), w, h,
                     facecolor=fill, edgecolor=edge, lw=lw, alpha=alpha))


def rough_diamond(ax, x, y, w, h, fill, edge=INK, lw=2.2):
    cx, cy = x + w / 2, y + h / 2
    pts = [(_jitter(cx), _jitter(y)), (_jitter(x + w), _jitter(cy)),
           (_jitter(cx), _jitter(y + h)), (_jitter(x), _jitter(cy))]
    ax.add_patch(Polygon(pts, closed=True, facecolor=fill, edgecolor=edge, lw=lw))


def rough_arrow(ax, x1, y1, x2, y2):
    n = 12
    xs, ys = [], []
    for i in range(n + 1):
        t = i / n
        xs.append(x1 + (x2 - x1) * t + rng.uniform(-2, 2))
        ys.append(y1 + (y2 - y1) * t + rng.uniform(-2, 2))
    ax.plot(xs, ys, color=INK, lw=2.2, solid_capstyle="round")
    ang = math.atan2(y2 - y1, x2 - x1)
    ah = 16
    ax.add_patch(Polygon([(x2, y2),
                          (x2 - ah * math.cos(ang - 0.45), y2 - ah * math.sin(ang - 0.45)),
                          (x2 - ah * math.cos(ang + 0.45), y2 - ah * math.sin(ang + 0.45))],
                         closed=True, facecolor=INK))


def txt(ax, x, y, s, size=26, weight="normal", color=INK, ha="left", va="top"):
    ax.text(x, y, s, fontfamily=CAVEAT, fontsize=size, color=color,
            ha=ha, va=va, weight=weight)


def render_png(path):
    fig, ax = plt.subplots(figsize=(24, 20.4), dpi=200)
    ax.set_xlim(0, W)
    ax.set_ylim(H, 0)
    ax.axis("off")
    fig.patch.set_facecolor("white")
    ax.set_facecolor("white")

    txt(ax, 60, 28, "Azure AI Native Governance", 58, weight="bold")
    txt(ax, 60, 108, "Azure native governs resources. The gateway decides the tool call.",
        34, color="#1971c2")
    for kind, x, y, w, h, fill, title, sub in BOXES:
        if kind == "ellipse":
            rough_ellipse(ax, x, y, w, h, fill)
        elif kind == "diamond":
            rough_diamond(ax, x, y, w, h, fill)
        else:
            rough_rect(ax, x, y, w, h, fill, dashed=(kind == "sticky"))
        cx = x + w / 2
        ty = y + 100 if kind == "diamond" else y + 34
        txt(ax, cx, ty, title, 34, weight="bold", ha="center")
        for i, line in enumerate(sub.split("\n")):
            sz = 22 if kind == "diamond" else 26
            txt(ax, cx, ty + 62 + i * 44, line, sz, ha="center", color=GREY)
    for x1, y1, x2, y2, _ in ARROWS:
        rough_arrow(ax, x1, y1, x2, y2)

    x, y, w, h = GRID
    rough_rect(ax, x, y, w, h, "#f8f9fa", dashed=True, r=24)
    txt(ax, x + 30, y + 18, "WHAT AZURE NATIVE DOES — AND WHERE IT STOPS", 30, weight="bold")
    for i, (title, job) in enumerate(NATIVE):
        gx = 90 + (i % 5) * 452
        gy = 970 + (i // 5) * 240
        rough_rect(ax, gx, gy, 430, 210, "#ffffff", r=14)
        txt(ax, gx + 18, gy + 16, title, 29, weight="bold")
        txt(ax, gx + 18, gy + 66, job, 25, color=GREY)
        txt(ax, gx + 18, gy + 118, "x stops at: the tool call", 25, color=RED)

    x, y, w, h = ESTATE
    rough_rect(ax, x, y, w, h, "#ffffff", r=14)
    txt(ax, x + 22, y + 14, "THE ESTATE (simulated)", 30, weight="bold")
    txt(ax, x + 22, y + 62,
        "1 subscription · 6 VMs · 8 storage · 3 Key Vaults · 4 AI resources", 26, color=GREY)
    txt(ax, x + 22, y + 100,
        "20 users · 6 Policy assignments · Defender 62% · 1 AI resource outside EU", 26, color=GREY)
    x, y, w, h = DEMO
    rough_rect(ax, x, y, w, h, "#ffffff", r=14)
    txt(ax, x + 22, y + 14, "One call, start to end", 30, weight="bold")
    txt(ax, x + 22, y + 64,
        "storage.read -> allow   ·   vm.start -> approval -> allow", 26, color=GREY)
    txt(ax, x + 22, y + 104,
        "keyvault.get_secret -> deny (shadow agent)", 26, color=GREY)
    x, y, w, h = CHECKS
    rough_rect(ax, x, y, w, h, "#ffffff", r=14)
    txt(ax, x + 22, y + 14, "16 CHECKS — 0 pass · 8 fail · 8 partial", 30, weight="bold")
    txt(ax, x + 22, y + 64, "AZ-16 partial by design", 26, color=GREY)
    txt(ax, x + 22, y + 104, "28 controls · 12 risks · 8 Rego rules", 26, color=GREY)
    x, y, w, h = GAP
    rough_rect(ax, x, y, w, h, AMBER, r=14)
    txt(ax, x + 22, y + 16, "THE GAP", 30, weight="bold")
    txt(ax, x + 22, y + 62,
        "Native stops at the tool call. The gateway decides it.", 28, color=GREY)
    plt.tight_layout(pad=0.3)
    fig.savefig(path, facecolor="white")
    plt.close(fig)


def main():
    ex = build_excalidraw()
    with open(os.path.join(DOCS, "architecture-excalidraw.excalidraw"), "w") as f:
        json.dump(ex, f, indent=2)
    render_png(os.path.join(DOCS, "architecture-excalidraw.png"))
    print("wrote", os.path.join(DOCS, "architecture-excalidraw.png"))
    print("wrote", os.path.join(DOCS, "architecture-excalidraw.excalidraw"))


if __name__ == "__main__":
    main()
