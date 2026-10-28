# -*- coding: utf-8 -*-
"""Cornice di misura 1:1 (PDF A4) per fotografare la zona di BTB_R_CONN1 sulla scheda madre.

Le dime della Board B usano ostacoli (slot SIM, vite, quadrato bianco) ricavati da foto poco precise. Questa
cornice si ritaglia lungo il bordo esterno e la finestra interna, si appoggia sulla scheda madre con
BTB_R_CONN1 al centro degli assi "0" e si fotografa dall'alto: righelli e crocini agli angoli (A-D, a
coordinate note) permettono di raddrizzare la foto e misurare gli ostacoli nelle coordinate delle dime
(origine al centro di BTB_R_CONN1, x verso destra, y verso il basso, come in design_boardB.py).

uso: python3 gen_dima_scala.py [out.pdf]   (default ../doc/x210ai_cornice_misura_1a1.pdf)
Stampare al 100% (senza "adatta alla pagina") e controllare il righello da 50 mm.
"""
import os
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt                     # noqa: E402
from matplotlib.patches import Circle, Rectangle    # noqa: E402

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from gen_dima_rev22 import MM                       # noqa: E402

# ---------------------------------------------------------------- parametri (mm, coordinate delle dime)
WIN = (-55.0, 30.0, -26.0, 28.0)    # finestra da ritagliare: x0, x1, y0, y1 (slot SIM, vite, quadrato bianco)
FRAME = 14.0                        # larghezza della cornice attorno alla finestra
FID_IN = 6.0                        # crocini A-D: distanza dal bordo esterno


def main():
    out = sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                                             "..", "doc", "x210ai_cornice_misura_1a1.pdf")
    w, h = 210, 297
    fig = plt.figure(figsize=(w * MM, h * MM))
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, w)
    ax.set_ylim(h, 0)
    ax.axis("off")
    x0, x1, y0, y1 = WIN
    ox, oy = 105.0 - (x0 + x1) / 2, 150.0 - (y0 + y1) / 2     # pagina = coordinate dima + (ox, oy)
    X0, X1, Y0, Y1 = x0 - FRAME, x1 + FRAME, y0 - FRAME, y1 + FRAME

    def P(x, y):
        return ox + x, oy + y

    # bordo esterno e finestra (linee di taglio), cornice in grigio chiaro per vederla bene in foto
    ax.add_patch(Rectangle(P(X0, Y0), X1 - X0, Y1 - Y0, fc="0.93", ec="black", lw=0.8))
    ax.add_patch(Rectangle(P(x0, y0), x1 - x0, y1 - y0, fc="white", ec="black", lw=0.8, hatch="xx",
                           alpha=0.25))
    ax.text(*P((x0 + x1) / 2, (y0 + y1) / 2), "RITAGLIA\n(finestra)", fontsize=9, ha="center", va="center",
            color="0.6")

    # righelli sui quattro lati interni: tacche ogni mm, lunghe ogni 5, numeri ogni 10 (coordinate dima)
    for x in range(int(x0), int(x1) + 1):
        L = 3.0 if x % 10 == 0 else (2.0 if x % 5 == 0 else 1.2)
        for yb, s in ((y0, -1), (y1, 1)):
            ax.plot(*zip(P(x, yb), P(x, yb + s * L)), color="black", lw=0.6 if x == 0 else 0.25)
        if x % 10 == 0:
            ax.text(*P(x, y0 - 4.6), f"{x}", fontsize=4.5, ha="center", va="center",
                    weight="bold" if x == 0 else "normal")
            ax.text(*P(x, y1 + 4.6), f"{x}", fontsize=4.5, ha="center", va="center",
                    weight="bold" if x == 0 else "normal")
    for y in range(int(y0), int(y1) + 1):
        L = 3.0 if y % 10 == 0 else (2.0 if y % 5 == 0 else 1.2)
        for xb, s in ((x0, -1), (x1, 1)):
            ax.plot(*zip(P(xb, y), P(xb + s * L, y)), color="black", lw=0.6 if y == 0 else 0.25)
        if y % 10 == 0:
            ax.text(*P(x0 - 5.0, y), f"{y}", fontsize=4.5, ha="center", va="center",
                    weight="bold" if y == 0 else "normal")
            ax.text(*P(x1 + 5.0, y), f"{y}", fontsize=4.5, ha="center", va="center",
                    weight="bold" if y == 0 else "normal")
    # frecce sugli assi 0: il centro di BTB_R_CONN1 va all'incrocio delle due frecce
    for (xa, ya), (xb, yb) in (((0, y0 - 8.5), (0, y0 - 6.0)), ((0, y1 + 8.5), (0, y1 + 6.0)),
                               ((x0 - 9.5, 0), (x0 - 7.0, 0)), ((x1 + 9.5, 0), (x1 + 7.0, 0))):
        ax.annotate("", xy=P(xb, yb), xytext=P(xa, ya), arrowprops=dict(arrowstyle="-|>", lw=0.6,
                                                                        color="tab:red"))
    # crocini agli angoli, con un quadratino pieno per riconoscerli in foto
    fid = {"A": (X0 + FID_IN, Y0 + FID_IN), "B": (X1 - FID_IN, Y0 + FID_IN),
           "C": (X1 - FID_IN, Y1 - FID_IN), "D": (X0 + FID_IN, Y1 - FID_IN)}
    for k, (x, y) in fid.items():
        ax.add_patch(Circle(P(x, y), 2.2, fc="none", ec="black", lw=0.5))
        ax.plot(*zip(P(x - 3.2, y), P(x + 3.2, y)), color="black", lw=0.35)
        ax.plot(*zip(P(x, y - 3.2), P(x, y + 3.2)), color="black", lw=0.35)
        dx = 3.6 if x < 0 else -3.6
        ax.add_patch(Rectangle(P(x + dx - 0.9, y - 0.9), 1.8, 1.8, fc="black", ec="none"))
        ax.text(*P(x, y + (-4.3 if y > 0 else 4.3)), f"{k} ({x:g}, {y:g})", fontsize=3.8, ha="center",
                va="center")
    # orientamento
    ax.text(*P(x0 + 1, Y0 + 2.3), "slot SIM  <-", fontsize=4.5, ha="left", va="center", color="0.3")
    ax.text(*P(x1 - 1, Y0 + 2.3), "->  verso destra (x+)", fontsize=4.5, ha="right", va="center", color="0.3")
    ax.text(*P((x0 + x1) / 2, Y1 - 2.2), "lato vite (y+)", fontsize=4.5, ha="center", va="center", color="0.3")

    legend = ["Cornice di misura 1:1 per fotografare la zona di BTB_R_CONN1 (coordinate delle dime della Board B, mm)",
              "1. Stampa al 100% (senza 'adatta alla pagina') e controlla il righello da 50 mm col calibro.",
              "2. Ritaglia il bordo esterno e la finestra tratteggiata.",
              "3. Togli la tastiera. Appoggia la cornice sulla scheda madre con BTB_R_CONN1 orizzontale, lo slot SIM",
              "   a sinistra e la vite in basso, come nelle dime: il centro del connettore all'incrocio delle frecce rosse",
              "   (tacche 0), il lato lungo del connettore parallelo ai righelli in alto e in basso. Fissala con nastro.",
              "4. Fotografa dall'alto, perpendicolare, da 25-30 cm, senza flash e senza ombre: devono vedersi tutta la",
              "   cornice, i 4 crocini A-D e i bordi di slot SIM, foro della vite, quadrato bianco e componenti vicini.",
              "   Se puoi, fai anche una seconda foto un po' piu' vicina, sempre perpendicolare."]
    for i, s in enumerate(legend):
        ax.text(18, 20 + i * 4.6, s, fontsize=5.6 if i else 6.5, weight="bold" if i == 0 else "normal")
    ax.plot([18, 68], [282, 282], color="black", lw=0.8)
    for x in range(18, 69, 10):
        ax.plot([x, x], [281, 283], color="black", lw=0.5)
    ax.text(43, 287, "50 mm: controlla con il calibro dopo la stampa", fontsize=6, ha="center")
    fig.savefig(out)
    print("ok", os.path.normpath(out))
    print(f"cornice {X1 - X0:g} x {Y1 - Y0:g} mm, finestra {x1 - x0:g} x {y1 - y0:g} mm")
    for k, (x, y) in fid.items():
        print(f"  crocino {k}: ({x:g}, {y:g})")


if __name__ == "__main__":
    main()
