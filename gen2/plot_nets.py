# -*- coding: utf-8 -*-
"""Disegno di dettaglio (matplotlib):
python plot_nets.py [--board A|B] board out.png "xmin,xmax,ymin,ymax" ["NET1,NET2"]
coordinate del modello dati (origine D.ORIGIN)."""
import os
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.patches import Circle, Rectangle  # noqa: E402
import pcbnew  # noqa: E402

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import boards  # noqa: E402

D = boards.load()

pcb, out, win = sys.argv[1:4]
hl = set(sys.argv[4].split(",")) if len(sys.argv) > 4 and sys.argv[4] else set()
x0, x1, y0, y1 = map(float, win.split(","))
b = pcbnew.LoadBoard(pcb)
OX, OY = D.ORIGIN
mm = pcbnew.ToMM
fig, ax = plt.subplots(figsize=(max(8, (x1 - x0) * 1.1), max(4, (y1 - y0) * 1.1)))
COL = {pcbnew.F_Cu: "#d62728", pcbnew.In2_Cu: "#2ca02c", pcbnew.B_Cu: "#1f77b4", pcbnew.In1_Cu: "#9467bd"}
for fp in b.GetFootprints():
    for p in fp.Pads():
        bb = p.GetBoundingBox()
        x, y = mm(bb.GetLeft()) - OX, mm(bb.GetTop()) - OY
        w, h = mm(bb.GetWidth()), mm(bb.GetHeight())
        if x > x1 or x + w < x0 or y > y1 or y + h < y0:
            continue
        lay = pcbnew.F_Cu if p.IsOnLayer(pcbnew.F_Cu) and not p.IsOnLayer(pcbnew.B_Cu) else pcbnew.B_Cu
        if p.GetAttribute() == pcbnew.PAD_ATTRIB_PTH:
            lay = None
        ec = "k" if p.GetNetname() in hl else "none"
        ax.add_patch(Rectangle((x, y), w, h, fc=COL.get(lay, "#888") if lay else "#888", alpha=0.35, ec=ec, lw=1.5))
        if w * h > 0.05:
            ax.text(x + w / 2, y + h / 2, f"{fp.GetReference()}.{p.GetNumber()}", fontsize=4, ha="center", va="center")
for t in b.GetTracks():
    if t.GetClass() == "PCB_VIA":
        c = t.GetPosition()
        x, y = mm(c.x) - OX, mm(c.y) - OY
        if x0 <= x <= x1 and y0 <= y <= y1:
            ax.add_patch(Circle((x, y), mm(t.GetWidth()) / 2, fc="#ff7f0e" if t.GetNetname() != "GND" else "#555",
                                ec="k" if t.GetNetname() in hl else "none", alpha=0.8))
        continue
    s, e = t.GetStart(), t.GetEnd()
    xs = [mm(s.x) - OX, mm(e.x) - OX]
    ys = [mm(s.y) - OY, mm(e.y) - OY]
    if max(xs) < x0 or min(xs) > x1 or max(ys) < y0 or min(ys) > y1:
        continue
    lw = mm(t.GetWidth()) * 72 * fig.get_size_inches()[0] / (x1 - x0) / 1.0
    ax.plot(xs, ys, color=COL.get(t.GetLayer(), "k"), lw=max(lw, 0.5), alpha=0.9 if t.GetNetname() in hl else 0.5,
            solid_capstyle="round")
ax.set_xlim(x0, x1)
ax.set_ylim(y1, y0)
ax.set_aspect("equal")
ax.grid(True, lw=0.2)
ax.set_title(f"{os.path.basename(pcb)}  rosso=F  verde=In2  blu=B  arancio=via segnale  grigio=via GND")
plt.tight_layout()
plt.savefig(out, dpi=110)
print(out)
