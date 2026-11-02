# -*- coding: utf-8 -*-
"""Dima di prova 1:1 (PDF A4) per la scheda unica "a giro del quadrato bianco" (rev 2.3, senza cavo eDP).

Forma proposta (coordinate dima, mm; origine al centro di BTB_R_CONN1, x verso il palmrest = -x,
y verso la vite = +y, come in design_boardB.py). La scheda aggira il quadrato bianco passando
SOTTO (y > -7,2) e a SINISTRA (x < -27,25); a sinistra mette tutte le componenti del RP2040:

  R1 braccio dal connettore (scende in +y, copre BTB):  x -8 .. 8      y -3,95 .. 12,2
  R2 ponte sotto il quadrato:                          x -55 .. 8     y -6,7 .. -3,3
  R3 zona componenti RP2040 (sinistra del quadrato):   x -55 .. -27,75 y -26 .. -3,3
                                                       (27,25 x 22,7 mm, libera 100%)

Sopra BTB_R_CONN1 restano ~1,8 mm: lì solo PCB sottile, niente componenti. Il quadrato bianco
(rosso) e gli altri ostacoli (arancione) devono restare FUORI dal ritaglio.

uso: python3 gen_dima_giro.py [out.pdf]   (default ../doc/x210ai_dima_giro_1a1.pdf)
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
R1 = (-8.0, 8.0, -3.95, 12.2)       # braccio dal connettore (copre BTB_R_CONN1, scende in +y)
R2 = (-55.0, 8.0, -6.7, -3.3)       # ponte sotto il quadrato bianco
R3 = (-55.0, -27.75, -26.0, -3.3)   # braccio componenti RP2040, a sinistra del quadrato
FORMA = unary_union([box(R1[0], R1[2], R1[1], R1[3]), box(R2[0], R2[2], R2[1], R2[3]),
                     box(R3[0], R3[2], R3[1], R3[3])])

# ostacoli (come OSTACOLI in design_boardB.py)
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

    # forma della scheda: contorno esterno dell'unione, riempita chiara, bordo nero spesso = taglio
    ext = FORMA.exterior.coords
    ax.add_patch(Polygon([P(x, y) for x, y in ext], fc="0.95", ec="black", lw=1.6, zorder=2))
    ax.text(*P(0, 5), "R1: dal connettore\nBTB in giu' (16 x 16,2 mm)", fontsize=6, ha="center")
    ax.text(*P(-24, -5.0), "R2 ponte sotto il quadrato (63 x 3,4 mm)", fontsize=6, ha="center")
    ax.text(*P(-41.4, -15), "R3 componenti RP2040\n27,25 x 22,7 mm (libera 100%)", fontsize=6.5,
            ha="center", weight="bold")

    # zona sopra BTB_R_CONN1: solo PCB, niente componenti (restano ~1,8 mm)
    ax.add_patch(Rectangle(P(-8.3, -3.95), 16.6, 7.9, fc="none", ec="tab:blue", lw=0.8,
                           hatch="..", zorder=3))
    ax.text(*P(0, -5.8), "sopra BTB_R_CONN1: solo PCB 0,4-0,8 mm, niente componenti (~1,8 mm sopra)",
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
    ax.plot([18, 68], [282, 282], color="black", lw=0.8)
    for x in range(18, 69, 10):
        ax.plot([x, x], [281, 283], color="black", lw=0.5)
    ax.text(43, 287, "50 mm: controlla con il calibro dopo la stampa", fontsize=6, ha="center")

    legend = [
        "Dima di prova 1:1 - scheda unica \"a giro del quadrato bianco\" (rev 2.3, senza cavo eDP), coordinate dima mm",
        "Origine (0,0) = centro di BTB_R_CONN1, x verso il palmrest (-x), y verso la vite (+y).",
        "1. Stampa al 100% (senza 'adatta alla pagina') e controlla il righello da 50 mm col calibro.",
        "2. Ritaglia lungo il bordo nero spesso della forma a C (tieni il pezzo interno).",
        "3. Togli la tastiera. Appoggia il ritaglio sulla scheda madre con le frecce rosse puntate al centro",
        "   di BTB_R_CONN1 (connettore orizzontale, lato lungo parallelo all'asse x).",
        "4. Controlla che il ritaglio NON copra: quadrato bianco (rosso, vietato), FPC, flat arancione, CN1,",
        "   vite, linguetta (arancione). Deve coprire solo BTB_R_CONN1 (verde, spina J2 sotto a 0,0).",
        "5. R3 (a sinistra del quadrato) e' la zona per le componenti del RP2040; sopra BTB_R_CONN1",
        "   (tratteggio blu) solo PCB: devono restare ~1,8 mm, poi prova a rimontare la tastiera.",
    ]
    for i, s in enumerate(legend):
        ax.text(18, 16 + i * 4.6, s, fontsize=5.6 if i else 6.5, weight="bold" if i == 0 else "normal")
    ax.text(105, 10, "X210Ai - dima giro quadrato bianco, rev 2.3 (prova)", fontsize=8, ha="center", weight="bold")

    fig.savefig(out)
    print("ok", os.path.normpath(out))
    print(f"area forma {FORMA.area:.0f} mm2: R1 {R1}, R2 {R2}, R3 {R3}")

    # verifica automatica: la forma non deve toccare gli ostacoli (margine 0,3 mm) e deve coprire BTB
    for nome, t, d in OSTACOLI:
        o = box(d[0], d[2], d[1], d[3]) if t == "r" else Point(d[:2]).buffer(d[2], 32)
        if "BTB" in nome:
            print(f"  BTB_R_CONN1 coperta: {FORMA.contains(o)}")
        else:
            print(f"  distanza da {nome}: {FORMA.distance(o):.2f} mm")


if __name__ == "__main__":
    main()
