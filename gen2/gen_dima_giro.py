# -*- coding: utf-8 -*-
"""Dima di prova 1:1 (PDF A4) per la scheda "a giro del quadrato bianco" (variante senza cavo eDP).

Forma proposta (coordinate dima, mm; origine al centro di BTB_R_CONN1, x verso il palmrest = -x,
y verso la vite = +y, come in design_boardB.py):

  base sotto il quadrato bianco:  x -31,5 .. 30,0   y -6,7 .. 12,2   (61,5 x 18,9 mm)
  braccio destro del quadrato:    x  12,5 .. 30,0   y -26,0 .. -6,7  (17,5 x 19,3 mm)

La base copre BTB_R_CONN1 (la spina J2 va sotto, a (0,0)): sopra il connettore restano ~1,8 mm,
quindi lì solo PCB sottile, niente componenti (zona tratteggiata). Il quadrato bianco (rosso) e gli
altri ostacoli (arancione) devono restare FUORI dal ritaglio.

uso: python3 gen_dima_giro.py [out.pdf]   (default ../doc/x210ai_dima_giro_1a1.pdf)
Stampare al 100% (senza "adatta alla pagina") e controllare il righello da 50 mm.
"""
import os
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt                     # noqa: E402
from matplotlib.patches import Circle, Polygon, Rectangle  # noqa: E402

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from gen_dima_rev22 import MM                       # noqa: E402

# ---------------------------------------------------------------- forma della scheda (mm, coordinate dima)
BASE = (-31.5, 30.0, -6.7, 12.2)      # x0, x1, y0, y1  (sotto il quadrato bianco)
BRACCIO = (12.5, 30.0, -26.0, -6.7)   # braccio destro (zona libera 18 x 54)
FORMA = [(-31.5, -6.7), (12.5, -6.7), (12.5, -26.0), (30.0, -26.0),
         (30.0, 12.2), (-31.5, 12.2)]     # poligono a L: base y -6,7..12,2 + braccio destro y -26..-6,7

# ostacoli (come OSTACOLI in design_boardB.py), più margine 0,5 mm dove serve
OSTACOLI = [
    ("quadrato bianco VIETATO (<1 mm sopra), 39,3 x 33 mm", "r", (-27.25, 12.0, -40.2, -7.2)),
    ("BTB_R_CONN1 (spina J2 sotto, a 0,0)", "r", (-7.8, 7.8, -3.45, 3.45)),
    ("connettore FPC", "r", (-45.0, -32.35, -2.8, 12.7)),
    ("flat arancione", "r", (-37.35, -21.35, 12.7, 17.2)),
    ("vite", "c", (-7.8, 19.1, 3.55)),
    ("linguetta vite", "r", (-13.1, -5.8, 22.3, 26.4)),
    ("connettore CN1", "r", (-30.35, -21.6, 17.25, 23.5)),
]


def main():
    out = sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                                             "..", "doc", "x210ai_dima_giro_1a1.pdf")
    w, h = 210, 297
    fig = plt.figure(figsize=(w * MM, h * MM))
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, w)
    ax.set_ylim(h, 0)
    ax.axis("off")
    ox, oy = 105.0, 150.0          # origine dima (0,0) al centro pagina

    def P(x, y):
        return ox + x, oy + y

    # griglia 10 mm con numeri sugli assi
    for x in range(-70, 46, 10):
        ax.plot(*zip(P(x, -45), P(x, 40)), color="0.85", lw=0.4, zorder=0)
        if x % 20 == 0:
            ax.text(*P(x, -47), f"{x}", fontsize=5, ha="center", color="0.5")
    for y in range(-45, 41, 10):
        ax.plot(*zip(P(-70, y), P(45, y)), color="0.85", lw=0.4, zorder=0)
        if y % 20 == 0:
            ax.text(*P(-72, y), f"{y}", fontsize=5, va="center", color="0.5")
    ax.plot(*zip(P(-70, 0), P(45, 0)), color="0.6", lw=0.5, zorder=0)
    ax.plot(*zip(P(0, -45), P(0, 40)), color="0.6", lw=0.5, zorder=0)

    # forma della scheda: riempita chiara, bordo nero spesso = linea di taglio
    ax.add_patch(Polygon([P(x, y) for x, y in FORMA], fc="0.95", ec="black", lw=1.6, zorder=2))
    bx0, bx1, by0, by1 = BASE
    ax.text(*P((bx0 + bx1) / 2, (by0 + by1) / 2 - 3), "BASE  61,5 x 18,9 mm", fontsize=7,
            ha="center", weight="bold")
    ax.text(*P((BRACCIO[0] + BRACCIO[1]) / 2, (BRACCIO[2] + BRACCIO[3]) / 2),
            "BRACCIO DESTRO\n17,5 x 19,3 mm\n(zona libera 100%)", fontsize=6, ha="center", va="center")

    # zona sopra BTB_R_CONN1: solo PCB, niente componenti (restano ~1,8 mm)
    ax.add_patch(Rectangle(P(-8.3, -3.95), 16.6, 7.9, fc="none", ec="tab:blue", lw=0.8,
                           hatch="..", zorder=3))
    ax.text(*P(0, -5.6), "sopra BTB_R_CONN1: solo PCB 0,4-0,8 mm, niente componenti (~1,8 mm sopra)",
            fontsize=5.5, ha="center", color="tab:blue")

    # spina J2 a (0,0)
    ax.add_patch(Rectangle(P(-6.62, -2.92), 13.34, 6.04, fc="none", ec="green", lw=1.0, zorder=4))
    ax.text(*P(0, 0), "J2", fontsize=6, ha="center", va="center", color="green", weight="bold", zorder=5)

    # ostacoli
    for nome, t, d in OSTACOLI:
        if t == "r":
            x0, x1, y0, y1 = d
            col = "red" if "VIETATO" in nome else ("green" if "BTB" in nome else "darkorange")
            lw = 1.6 if "VIETATO" in nome else 0.9
            ax.add_patch(Rectangle(P(x0, y0), x1 - x0, y1 - y0, fc="none", ec=col, lw=lw, zorder=3))
            ax.text(*P(x0 + 0.5, y1 + 2.0 if "VIETATO" not in nome else y0 - 2.0), nome, fontsize=5,
                    color=col, ha="left")
        else:
            cx, cy, r = d
            col = "darkorange"
            ax.add_patch(Circle(P(cx, cy), r, fc="none", ec=col, lw=0.9, zorder=3))
            ax.text(*P(cx, cy + r + 2.0), nome, fontsize=5, color=col, ha="center")

    # frecce rosse verso l'origine (centro BTB_R_CONN1)
    for (xa, ya), (xb, yb) in (((0, -36), (0, -30)), ((0, 34), (0, 28)),
                               ((-52, 0), (-46, 0)), ((36, 0), (30, 0))):
        ax.annotate("", xy=P(xb, yb), xytext=P(xa, ya),
                    arrowprops=dict(arrowstyle="-|>", lw=0.8, color="tab:red"))
    ax.text(*P(0, -38), "centro BTB_R_CONN1 qui (0,0)", fontsize=6, ha="center", color="tab:red")

    # righello di controllo 50 mm
    ax.plot([18, 68], [282, 282], color="black", lw=0.8)
    for x in range(18, 69, 10):
        ax.plot([x, x], [281, 283], color="black", lw=0.5)
    ax.text(43, 287, "50 mm: controlla con il calibro dopo la stampa", fontsize=6, ha="center")

    legend = [
        "Dima di prova 1:1 - scheda \"a giro del quadrato bianco\" (variante senza cavo eDP), coordinate dima mm",
        "Origine (0,0) = centro di BTB_R_CONN1, x verso il palmrest (-x), y verso la vite (+y).",
        "1. Stampa al 100% (senza 'adatta alla pagina') e controlla il righello da 50 mm col calibro.",
        "2. Ritaglia lungo il bordo nero spesso della forma a L (tieni il pezzo interno).",
        "3. Togli la tastiera. Appoggia il ritaglio sulla scheda madre con le frecce rosse puntate al centro",
        "   di BTB_R_CONN1 (connettore orizzontale, lato lungo parallelo all'asse x).",
        "4. Controlla che il ritaglio NON copra: quadrato bianco (rosso, vietato), FPC, flat arancione, CN1,",
        "   vite, linguetta (arancione). Deve coprire solo BTB_R_CONN1 (verde, spina J2 sotto a 0,0).",
        "5. Prova a rimontare la tastiera: sopra BTB_R_CONN1 (tratteggio blu) devono restare ~1,8 mm.",
    ]
    for i, s in enumerate(legend):
        ax.text(18, 18 + i * 4.6, s, fontsize=5.6 if i else 6.5, weight="bold" if i == 0 else "normal")
    ax.text(105, 12, "X210Ai - dima giro quadrato bianco, rev 2.3 (prova)", fontsize=8, ha="center", weight="bold")

    fig.savefig(out)
    print("ok", os.path.normpath(out))
    print(f"base {BASE[1]-BASE[0]:g} x {BASE[3]-BASE[2]:g} mm, braccio "
          f"{BRACCIO[1]-BRACCIO[0]:g} x {BRACCIO[3]-BRACCIO[2]:g} mm")

    # verifica automatica: la forma non deve toccare gli ostacoli (margine 0,3 mm) e deve coprire BTB
    from shapely.geometry import Polygon as SPoly, box, Point
    forma = SPoly([(x, y) for x, y in FORMA])
    for nome, t, d in OSTACOLI:
        o = box(*d) if t == "r" else Point(d[:2]).buffer(d[2], 32)
        if "BTB" in nome:
            print(f"  BTB_R_CONN1 coperta: {forma.contains(o)}")
        else:
            print(f"  distanza da {nome}: {forma.distance(o):.2f} mm")


if __name__ == "__main__":
    main()
