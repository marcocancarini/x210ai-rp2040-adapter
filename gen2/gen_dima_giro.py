# -*- coding: utf-8 -*-
"""Dima di prova 1:1 (PDF A4) per la Board C (rev 2.3): scheda unica "a giro del quadrato bianco",
integrazione di Board A + Board B senza cavo eDP.

Forma C4 (coordinate dima, mm; origine al centro di BTB_R_CONN1, x verso il palmrest = -x,
y verso la vite = +y, come in design_boardB.py). La scheda aggira il quadrato bianco passant
SOTTO (y > -7,2) e a SINISTRA (x < -27,25, tra slot SIM e quadrato); sopra il quadrato (lato
opposto a BTB) mette le componenti del RP2040:

  R1 base (copre BTB, scende in +y):   x -31,85 .. 30    y -6,7 .. 12,2     (61,9 x 18,9 mm)
  R2 raccordo verso sinistra:          x -39,5 .. -31,85 y -6,7 .. -3,3     (7,65 x 3,4 mm)
  R3 braccio sinistro:                 x -39,5 .. -27,75 y -60 .. -3,3      (11,75 x 56,7 mm)
  R4 componenti SOPRA il quadrato:     x -39,5 .. 30     y -60 .. -40,7     (69,5 x 19,3 mm)

Sopra BTB_R_CONN1 restano ~1,8 mm: lì solo PCB sottile, niente componenti. Il quadrato bianco
(rosso) e gli altri ostacoli (arancione) devono restare FUORI dal ritaglio.

uso: python3 gen_dima_giro.py [--rot90ccw] [out.pdf]
  default: out ../doc/x210ai_dima_boardC_1a1.pdf, pagina A4 portrait
  --rot90ccw: pagina ruotata di 90 gradi in senso antiorario (A4 landscape 297x210)

Stampare al 100% (senza "adatta alla pagina") e controllare il righello da 50 mm.
"""
import os
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt                     # noqa: E402
from matplotlib.patches import Circle, Polygon, Rectangle  # noqa: E402
from shapely.geometry import box, Point               # noqa: E402
from shapely.ops import unary_union                   # noqa: E402

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from gen_dima_rev22 import MM                       # noqa: E402

# ---------------------------------------------------------------- forma della scheda (mm, coordinate dima)
RETT = [
    (-31.85, 30.0, -6.7, 12.2),     # R1 base (copre BTB_R_CONN1)
    (-39.5, -31.85, -6.7, -3.3),    # R2 raccordo
    (-39.5, -27.75, -60.0, -3.3),   # R3 braccio sinistro (tra slot SIM e quadrato)
    (-39.5, 30.0, -60.0, -40.7),    # R4 componenti sopra il quadrato
]
FORMA = unary_union([box(r[0], r[2], r[1], r[3]) for r in RETT])

# ostacoli (come OSTACOLI in design_boardB.py)
OSTACOLI = [
    ("quadrato bianco VIETATO (<1 mm sopra), 39,3 x 33 mm", "r", (-27.25, 12.0, -40.2, -7.2)),
    ("BTB_R_CONN1 (spina J2 sotto, a 0,0)", "r", (-7.8, 7.8, -3.45, 3.45)),
    ("connettore FPC", "r", (-45.0, -32.35, -2.8, 12.7)),
    ("flat arancione", "r", (-37.35, -21.35, 12.7, 17.2)),
    ("vite", "c", (-7.8, 19.1, 3.55)),
    ("linguetta vite", "r", (-13.1, -5.8, 22.3, 26.4)),
    ("connettore CN1", "r", (-30.35, -21.6, 17.25, 23.5)),
    ("slot SIM", "r", (-50.0, -40.0, -38.9, -26.9)),
]


def main():
    args = sys.argv[1:]
    ccw = "--rot90ccw" in args
    pos = [a for a in args if not a.startswith("--")]
    out = pos[0] if pos else os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "doc",
                                          "x210ai_dima_boardC_1a1.pdf")
    if ccw:
        # pagina A4 landscape (297x210), tutto ruotato di 90 gradi in senso antiorario:
        # coordinata dima (x,y) -> pagina (ox - y, oy + x)
        w, h = 297, 210
        ox, oy = 100.0, 75.0

        def P(x, y):
            return ox - y, oy + x
    else:
        w, h = 210, 297
        ox, oy = 105.0, 160.0

        def P(x, y):
            return ox + x, oy + y

    fig = plt.figure(figsize=(w * MM, h * MM))
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, w)
    ax.set_ylim(h, 0)
    ax.axis("off")

    # griglia 10 mm con numeri sugli assi
    for x in range(-70, 46, 10):
        ax.plot(*zip(P(x, -65), P(x, 65)), color="0.85", lw=0.4, zorder=0)
        if x % 20 == 0:
            ax.text(*P(x, -67), f"{x}", fontsize=5, ha="center", color="0.5")
    for y in range(-65, 66, 10):
        ax.plot(*zip(P(-70, y), P(45, y)), color="0.85", lw=0.4, zorder=0)
        if y % 20 == 0:
            ax.text(*P(-72, y), f"{y}", fontsize=5, va="center", color="0.5")
    ax.plot(*zip(P(-70, 0), P(45, 0)), color="0.6", lw=0.5, zorder=0)
    ax.plot(*zip(P(0, -65), P(0, 65)), color="0.6", lw=0.5, zorder=0)

    # forma della scheda: contorno esterno, riempita chiara, bordo nero spesso = taglio
    ext = FORMA.exterior.coords
    ax.add_patch(Polygon([P(x, y) for x, y in ext], fc="0.95", ec="black", lw=1.6, zorder=2))
    for k, r in enumerate(RETT):
        cx, cy = (r[0] + r[1]) / 2, (r[2] + r[3]) / 2
        ax.text(*P(cx, cy), f"R{k+1} {r[1]-r[0]:g}x{r[3]-r[2]:g}", fontsize=6, ha="center", va="center")

    # zona sopra BTB_R_CONN1: solo PCB, niente componenti (~1,8 mm sopra)
    ax.add_patch(Rectangle(P(-8.3, -3.95), 16.6, 7.9, fc="none", ec="tab:blue", lw=0.8,
                           hatch="..", zorder=3))
    ax.text(*P(0, -5.8), "sopra BTB_R_CONN1: solo PCB 0,4-0,8 mm (~1,8 mm sopra)",
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
            ax.text(*P(x0 + 0.5, y0 - 2.0 if "VIETATO" in nome else y1 + 2.0), nome, fontsize=5,
                    color=col, ha="left")
        else:
            cx, cy, r = d
            ax.add_patch(Circle(P(cx, cy), r, fc="none", ec="darkorange", lw=0.9, zorder=3))
            ax.text(*P(cx, cy + r + 2.0), nome, fontsize=5, color="darkorange", ha="center")

    # frecce rosse verso l'origine (centro BTB_R_CONN1)
    for (xa, ya), (xb, yb) in (((0, -36), (0, -30)), ((0, 34), (0, 28)),
                               ((-52, 0), (-46, 0)), ((36, 0), (30, 0))):
        ax.annotate("", xy=P(xb, yb), xytext=P(xa, ya),
                    arrowprops=dict(arrowstyle="-|>", lw=0.8, color="tab:red"))
    ax.text(*P(0, -38), "centro BTB_R_CONN1 qui (0,0)", fontsize=6, ha="center", color="tab:red")

    # righello di controllo 50 mm
    if ccw:
        ry = h - 12
        ax.plot([210, 260], [ry, ry], color="black", lw=0.8)
        for x in range(210, 261, 10):
            ax.plot([x, x], [ry - 1, ry + 1], color="black", lw=0.5)
        ax.text(235, ry - 5, "50 mm: controlla con il calibro", fontsize=6, ha="center")
    else:
        ax.plot([18, 68], [288, 288], color="black", lw=0.8)
        for x in range(18, 69, 10):
            ax.plot([x, x], [287, 289], color="black", lw=0.5)
        ax.text(43, 293, "50 mm: controlla con il calibro dopo la stampa", fontsize=6, ha="center")

    legend = [
        "Dima di prova 1:1 - Board C (rev 2.3, forma C4): scheda unica a giro del quadrato bianco, coordinate dima mm",
        "Origine (0,0) = centro di BTB_R_CONN1, x verso il palmrest (-x), y verso la vite (+y).",
        "1. Stampa al 100% (senza 'adatta alla pagina') e controlla il righello da 50 mm col calibro.",
        "2. Ritaglia lungo il bordo nero spesso (tieni il pezzo interno).",
        "3. Togli la tastiera. Appoggia il ritaglio con le frecce rosse puntate al centro di BTB_R_CONN1.",
        "4. Il ritaglio NON deve coprire: quadrato bianco (rosso, vietato), FPC, flat, CN1, vite,",
        "   linguetta, slot SIM (arancione). Deve coprire solo BTB_R_CONN1 (verde, J2 sotto a 0,0).",
        "5. Sopra BTB_R_CONN1 (tratteggio blu) solo PCB: restano ~1,8 mm; poi prova a rimontare la tastiera.",
    ]
    if ccw:
        for i, s in enumerate(legend):
            ax.text(180, 14 + i * 4.6, s, fontsize=5.2 if i else 6.2, weight="bold" if i == 0 else "normal")
        ax.text(180, 8, "X210Ai - dima Board C (forma C4, ruotata 90 deg antiorario)",
                fontsize=7, weight="bold")
    else:
        for i, s in enumerate(legend):
            ax.text(18, 14 + i * 4.6, s, fontsize=5.6 if i else 6.5, weight="bold" if i == 0 else "normal")
        ax.text(105, 8, "X210Ai - dima Board C (forma C4), rev 2.3 (prova)", fontsize=8,
                ha="center", weight="bold")

    fig.savefig(out)
    print("ok", os.path.normpath(out))
    print(f"area forma {FORMA.area:.0f} mm2")
    for nome, t, d in OSTACOLI:
        o = box(d[0], d[2], d[1], d[3]) if t == "r" else Point(d[:2]).buffer(d[2], 32)
        if "BTB" in nome:
            print(f"  BTB_R_CONN1 coperta: {FORMA.contains(o)}")
        else:
            print(f"  distanza da {nome}: {FORMA.distance(o):.2f} mm")


if __name__ == "__main__":
    main()
