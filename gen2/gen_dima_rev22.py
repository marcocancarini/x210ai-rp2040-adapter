# -*- coding: utf-8 -*-
"""Dima 1:1 in PDF A4 della Board A o della Board B (rev 2.2), dal modello dati e dalle impronte della
libreria x210ai.pretty, senza KiCad. Il piazzamento e' quello PRELIMINARE dei file design_board*.py.

uso: python3 gen_dima_rev22.py A|B <out.pdf>
Stampare al 100% (senza "adatta alla pagina") e controllare il righello da 50 mm.
"""
import importlib
import math
import os
import re
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt                     # noqa: E402
from matplotlib.patches import Rectangle            # noqa: E402

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

LIB = os.path.join(os.path.dirname(os.path.abspath(__file__)), "lib", "x210ai.pretty")
PAD = re.compile(r'\(pad "\w+" smd \w+ \(at ([-\d.]+) ([-\d.]+)\) \(size ([\d.]+) ([\d.]+)\) \(layers "(\w)\.Cu"')
CRT = re.compile(r'\(fp_line \(start ([-\d.]+) ([-\d.]+)\) \(end ([-\d.]+) ([-\d.]+)\)\s*'
                 r'\(stroke \(width [\d.]+\) \(type \w+\)\) \(layer "F\.CrtYd"\)')
MM = 1 / 25.4
# ingombro del corpo (mm) per le impronte che non sono nella libreria del progetto
BODY = {"C0402": (1.0, 0.5), "R0402": (1.0, 0.5), "QFN56": (7.0, 7.0), "USON8": (3.0, 2.0), "SOT23": (2.9, 1.6),
        "SOT363": (2.0, 1.25), "XTAL": (3.2, 2.5), "SJ": (2.3, 1.5), "TP": (1.0, 1.0), "USB": (1.6, 5.9)}
LIBFP = {"JSANDWICH": ("JAE_AA01_sandwich", "tab:blue"), "EDP": ("IPEX_20455-040E_90deg", "tab:green")}


def rot_pt(x, y, rot):
    """rotazione KiCad (antioraria vista dall'alto, asse y verso il basso)"""
    a = math.radians(rot)
    return x * math.cos(a) + y * math.sin(a), -x * math.sin(a) + y * math.cos(a)


def footprint(ax, name, x0, y0, color, rot=0):
    assert rot in (0, 90, 180, 270), rot
    t = open(os.path.join(LIB, name + ".kicad_mod")).read()
    for x, y, w, h, side in PAD.findall(t):
        x, y, w, h = map(float, (x, y, w, h))
        x, y = rot_pt(x, y, rot)
        if rot in (90, 270):
            w, h = h, w
        ax.add_patch(Rectangle((x0 + x - w / 2, y0 + y - h / 2), w, h, fc=color if side == "F" else "none",
                               ec=color, lw=0.3, alpha=0.8))
    for x1, y1, x2, y2 in CRT.findall(t):
        (a1, b1), (a2, b2) = rot_pt(float(x1), float(y1), rot), rot_pt(float(x2), float(y2), rot)
        ax.plot([x0 + a1, x0 + a2], [y0 + b1, y0 + b2], color=color, lw=0.4, ls="--")


def main():
    board, out = sys.argv[1].upper(), sys.argv[2]
    D = importlib.import_module("design_board" + board)
    w, h = 210, 297
    fig = plt.figure(figsize=(w * MM, h * MM))
    ax = fig.add_axes([0, 0, 1, 1])
    ox, oy = 105.0 - (D.X0 + D.X1) / 2, 130.0       # centro della scheda a meta' pagina; y verso il basso
    ax.set_xlim(0, w)
    ax.set_ylim(h, 0)
    ax.axis("off")

    ax.add_patch(Rectangle((ox + D.X0, oy + D.Y0), D.X1 - D.X0, D.Y1 - D.Y0, fc="none", ec="black", lw=0.8))
    legend = [f"nero: contorno Board {board} {D.X1 - D.X0:.1f} x {D.Y1 - D.Y0:.1f} mm, vista dall'alto "
              f"(piazzamento PRELIMINARE)"]
    if board == "B":
        ex0, ex1, ey0, ey1 = D.ENVELOPE_REV20
        ax.add_patch(Rectangle((ox + ex0, oy + ey0), ex1 - ex0, ey1 - ey0, fc="none", ec="red", lw=0.5, ls=":"))
        for nome, x0, x1, y0, y1 in getattr(D, "OSTACOLI_FOTO", []):
            ax.add_patch(Rectangle((ox + x0, oy + y0), x1 - x0, y1 - y0, fc="none", ec="dimgray", lw=0.3,
                                   hatch="////", alpha=0.6))
            ax.text(ox + (max(x0, D.X0 - 8) + min(x1, D.X1 + 8)) / 2, oy + (y0 + y1) / 2, nome, fontsize=4,
                    ha="center", va="center", color="dimgray")
        legend += ["rosso puntinato: ingombro della rev 2.0 (29 mm a sinistra del centro del connettore)",
                   "tratteggio grigio: ostacoli misurati dalla foto (slot SIM, vite, quadrato bianco), +/-0,5 mm",
                   "blu: J1 sandwich centrato su BTB_R_CONN1 (pieno = sopra, vuoto = spina sotto)",
                   "Ritaglia il contorno nero e appoggialo con J1 sul connettore (pin 1 come in serigrafia)."]
    legend += ["verde: ricettacolo eDP 20455-040E, tratteggio = area libera 28,2 x 6,7 mm (barra di sgancio)",
               "grigio: altri componenti (pieno = sopra, vuoto = sotto)"]
    for c in D.COMP:
        ref = c["ref"]
        x, y, rot, side = D.PLACE[ref]
        if c["fpkey"] in LIBFP:
            name, col = LIBFP[c["fpkey"]]
            footprint(ax, name, ox + x, oy + y, col, rot)
            ty = y - 1.4 if rot == 0 else y + 1.6
            ax.text(ox + x, oy + ty, ref, fontsize=4, ha="center", va="center", color=col)
            if c["fpkey"] == "EDP":
                px, py = rot_pt(-9.75, -1.0, rot)
                ax.text(ox + x + px, oy + y + py, "1", fontsize=4, ha="center", va="center", color=col)
            continue
        bw, bh = BODY[c["fpkey"]]
        if rot in (90, 270):
            bw, bh = bh, bw
        ax.add_patch(Rectangle((ox + x - bw / 2, oy + y - bh / 2), bw, bh, ec="gray", lw=0.3,
                               fc="lightgray" if side == "T" else "none"))
        if bw * bh >= 2 or board == "B":
            ax.text(ox + x, oy + y + 0.2, ref, fontsize=2.5, ha="center", va="center", color="dimgray")
    jx, jy, jrot = D.PLACE["J4"][:3]
    dx, dy = rot_pt(0, 1, jrot)                    # il cavo esce verso +y dell'impronta
    sx, sy = jx + 5 * dx, jy + 5 * dy
    ex, ey = sx + 8 * dx, (D.Y1 + 8 if dy > 0 else D.Y0 - 8) if abs(dy) > 0.5 else sy
    ax.annotate("", xy=(ox + ex, oy + ey), xytext=(ox + sx, oy + sy),
                arrowprops=dict(arrowstyle="->", lw=0.6, color="tab:green"))
    ax.text(ox + ex + 1, oy + (ey + sy) / 2, "uscita cavo eDP", fontsize=5, color="tab:green")

    ax.plot([20, 70], [250, 250], color="black", lw=0.8)
    for x in range(20, 71, 10):
        ax.plot([x, x], [249, 251], color="black", lw=0.5)
    ax.text(45, 255, "50 mm: controlla con il calibro dopo la stampa", fontsize=6, ha="center")
    ax.text(20, 30, f"X210Ai rev {D.REV} - dima 1:1 Board {board}", fontsize=8, weight="bold")
    for i, s in enumerate(legend + ["Stampa al 100% (senza 'adatta alla pagina')."]):
        ax.text(20, 37 + i * 5.5, s, fontsize=6)
    fig.savefig(out)
    print("ok", out)


if __name__ == "__main__":
    main()
