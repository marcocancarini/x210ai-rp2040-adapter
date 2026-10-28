# -*- coding: utf-8 -*-
"""Dima 1:1 (PDF A4) della Board B in variante "L rovesciata" (prova meccanica, 28/10/2026).

La scheda attuale (design_boardB.py) ha J4 a sinistra di J1 e la parte bassa finisce sullo slot SIM.
Variante: dal blocco di J1 la scheda scende sul lato destro e torna verso sinistra con un braccio basso che
porta J4, parallelo a J1 ma piu' in basso e spostato a sinistra. J4 e' ruotato di 180 gradi: la spina e il
cavo escono verso l'alto (-y) e il cavo passa a sinistra di J1, nella zona lasciata libera.
Il circuito NON cambia: qui si prova solo l'ingombro. Le misure si regolano con i parametri qui sotto.

uso: python3 gen_dima_boardB_L.py [out.pdf]   (default ../doc/x210ai_dima_boardB_L_1a1.pdf)
Stampare al 100% (senza "adatta alla pagina") e controllare il righello da 50 mm.
"""
import os
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt                     # noqa: E402
from matplotlib.patches import Polygon, Rectangle   # noqa: E402

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import design_boardB as D                           # noqa: E402
from gen_dima_rev22 import MM, footprint, rot_pt    # noqa: E402

# ---------------------------------------------------------------- parametri (mm, origine = centro di J1)
J1_CRT = (-6.8, 6.9, -3.66, 3.45)   # courtyard di JAE_AA01_sandwich
J4_CRT = (-14.1, 14.1, -1.0, 5.7)   # courtyard di IPEX_20455-040E_90deg (rot 0, cavo verso +y)
J4_PLUG = 4.65                      # la spina innestata arriva a 5,1 mm dalla punta dei piedini (y = -0,45)
CAVO_W = 21.0                       # larghezza del fascio micro-coassiale (40 x 0,5 mm + nastro)
CAVO_J1 = 0.5                       # distanza minima tra il cavo e il courtyard di J1
J1_J4_GAP = D.J1_J4_GAP             # margine tra i courtyard di J1 e J4 (richiesto 2-3 mm)
EDGE = 0.3                          # bordo scheda oltre il courtyard di J4
TOP_X0, X1, Y0 = -7.5, D.X1, D.Y0   # braccio alto (J1): stesso bordo destro e superiore di oggi

# J4: il bordo destro del cavo resta a CAVO_J1 dal courtyard di J1, il courtyard di J4 sta J1_J4_GAP sotto J1
J4_X = J1_CRT[0] - CAVO_J1 - CAVO_W / 2
J4_Y = J1_CRT[3] + J1_J4_GAP + J4_CRT[3]
BOT_X0 = J4_X + J4_CRT[0] - EDGE                    # rot 180: x e y del courtyard si invertono
BOT_Y0 = J4_Y - J4_CRT[3] - EDGE
Y1 = J4_Y - J4_CRT[2] + EDGE
OUTLINE = [(TOP_X0, Y0), (X1, Y0), (X1, Y1), (BOT_X0, Y1), (BOT_X0, BOT_Y0), (TOP_X0, BOT_Y0)]
CAVO_Y0 = J4_Y - J4_PLUG            # da qui il cavo sale verso -y
PLACE = {"J1": (0.0, 0.0, 0), "J4": (J4_X, J4_Y, 180),
         # MOSFET e resistenze (lato sotto) nello spazio sotto J1, a destra di J4
         "Q3": (-1.0, 7.0, 0), "R14": (0.7, 7.0, 90), "Q2": (3.0, 7.0, 0), "R13": (4.7, 7.0, 90)}
BODY = {"Q2": (2.0, 1.25), "Q3": (2.0, 1.25), "R13": (1.0, 0.5), "R14": (1.0, 0.5)}


def margini():
    """distanze dagli ostacoli della foto (positivo = libero)"""
    ost = {n: (x0, x1, y0, y1) for n, x0, x1, y0, y1 in D.OSTACOLI_FOTO}
    sim, vite, quad = ost["slot SIM"], ost["vite"], ost["quadrato bianco"]
    m = {"slot SIM (in x)": BOT_X0 - sim[1] if Y1 > sim[2] else None,
         "vite (in y)": vite[2] - Y1,
         "quadrato bianco (in y)": Y0 - quad[3],
         "cavo - J1 (in x)": J1_CRT[0] - (J4_X + CAVO_W / 2)}
    return {k: v for k, v in m.items() if v is not None}


def disegna(ax, ox, oy, ostacoli):
    ax.add_patch(Polygon([(ox + x, oy + y) for x, y in OUTLINE], closed=True, fc="none", ec="black", lw=0.8))
    if ostacoli:
        ax.add_patch(Rectangle((ox + D.X0, oy + D.Y0), D.X1 - D.X0, D.Y1 - D.Y0, fc="none", ec="tab:red",
                               lw=0.5, ls=":"))
        for nome, x0, x1, y0, y1 in D.OSTACOLI_FOTO:
            ax.add_patch(Rectangle((ox + x0, oy + y0), x1 - x0, y1 - y0, fc="none", ec="dimgray", lw=0.3,
                                   hatch="////", alpha=0.6))
            ax.text(ox + (max(x0, BOT_X0 - 8) + min(x1, X1 + 8)) / 2, oy + (y0 + y1) / 2, nome, fontsize=4,
                    ha="center", va="center", color="dimgray")
    # spina innestata e fascio del cavo (non fanno parte della scheda: NON ritagliare)
    pw = 26.25
    ax.add_patch(Rectangle((ox + J4_X - pw / 2, oy + CAVO_Y0), pw, J4_PLUG + 0.45, fc="none", ec="tab:green",
                           lw=0.4, ls="-."))
    ax.add_patch(Rectangle((ox + J4_X - CAVO_W / 2, oy + CAVO_Y0 - 14), CAVO_W, 14, fc="tab:green", alpha=0.12,
                           ec="tab:green", lw=0.3))
    ax.annotate("", xy=(ox + J4_X, oy + CAVO_Y0 - 15), xytext=(ox + J4_X, oy + CAVO_Y0 - 4),
                arrowprops=dict(arrowstyle="->", lw=0.6, color="tab:green"))
    ax.text(ox + J4_X, oy + CAVO_Y0 - 8, f"cavo eDP {CAVO_W:g} mm", fontsize=4.5, color="tab:green",
            ha="center")
    for ref, col in (("J1", "tab:blue"), ("J4", "tab:green")):
        x, y, rot = PLACE[ref]
        footprint(ax, dict(J1="JAE_AA01_sandwich", J4="IPEX_20455-040E_90deg")[ref], ox + x, oy + y, col, rot)
        ax.text(ox + x, oy + y + (0 if ref == "J1" else 2.6), ref, fontsize=5, ha="center", va="center",
                color=col)
    px, py = rot_pt(-9.75, -1.0, 180)
    ax.text(ox + J4_X + px, oy + J4_Y + py, "1", fontsize=4, ha="center", va="center", color="tab:green")
    for ref, (bw, bh) in BODY.items():
        x, y, rot = PLACE[ref]
        if rot == 90:
            bw, bh = bh, bw
        ax.add_patch(Rectangle((ox + x - bw / 2, oy + y - bh / 2), bw, bh, ec="gray", lw=0.3, fc="none"))
        ax.text(ox + x, oy + y + 1.2, ref, fontsize=2.5, ha="center", va="center", color="dimgray")


def main():
    out = sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                                             "..", "doc", "x210ai_dima_boardB_L_1a1.pdf")
    w, h = 210, 297
    fig = plt.figure(figsize=(w * MM, h * MM))
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, w)
    ax.set_ylim(h, 0)
    ax.axis("off")
    ox = 105.0 - (BOT_X0 + X1) / 2
    disegna(ax, ox, 115.0, True)      # riferimento con gli ostacoli
    disegna(ax, ox, 200.0, False)     # copia da ritagliare

    m = margini()
    legend = [f"nero: contorno Board B a L rovesciata, {X1 - BOT_X0:.1f} x {Y1 - Y0:.1f} mm, vista dall'alto "
              f"(PROVA MECCANICA, circuito invariato)",
              "rosso puntinato: contorno attuale della Board B (design_boardB.py), per confronto",
              "tratteggio grigio: ostacoli misurati dalla foto (slot SIM, vite, quadrato bianco), +/-0,5 mm",
              "blu: J1 sandwich su BTB_R_CONN1;  verde: J4 ruotato 180 gradi, pin 1 a destra",
              "verde tratto-punto: spina innestata;  verde chiaro: fascio del cavo che sale a sinistra di J1",
              "margini: " + ";  ".join(f"{k} {v:.1f} mm" for k, v in m.items()),
              "Copia in basso: ritaglia SOLO il contorno nero, appoggia J1 sul connettore (pin 1 come in",
              "serigrafia). Per il cavo ritaglia una striscia di carta larga " f"{CAVO_W:g} mm e posala sulla zona verde."]
    ax.text(20, 22, f"X210Ai rev {D.REV} - dima 1:1 Board B, variante a L rovesciata", fontsize=8,
            weight="bold")
    for i, s in enumerate(legend + ["Stampa al 100% (senza 'adatta alla pagina')."]):
        ax.text(20, 29 + i * 4.6, s, fontsize=5.5)
    ax.text(20, 172, "da ritagliare:", fontsize=6, weight="bold")
    ax.plot([20, 70], [270, 270], color="black", lw=0.8)
    for x in range(20, 71, 10):
        ax.plot([x, x], [269, 271], color="black", lw=0.5)
    ax.text(45, 275, "50 mm: controlla con il calibro dopo la stampa", fontsize=6, ha="center")
    fig.savefig(out)
    print("ok", os.path.normpath(out))
    print(f"contorno {X1 - BOT_X0:.2f} x {Y1 - Y0:.2f} mm, J4 a ({J4_X:.2f}, {J4_Y:.2f}) rot 180")
    for k, v in m.items():
        print(f"  margine {k}: {v:.2f} mm")


if __name__ == "__main__":
    main()
