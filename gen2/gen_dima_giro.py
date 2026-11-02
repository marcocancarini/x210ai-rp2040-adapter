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
  default: out ../doc/x210ai_dima_boardC_1a1.pdf (v1, A4 portrait)
  --v32: v3.2 = v3.1 con fondo alzato (plastica telaio), invasione SIM 2 mm, flat +2 mm, braccio sx -4 mm
  --v31: v3.1 = forma v3 con ingombri dai nomi corretti (02/11) + riferimenti, PDF + SVG modificabile
  --rot90ccw: v2 - tutti gli oggetti (board, quadrato vietato, connettori, riferimenti) ruotati
              di 90 gradi in senso antiorario nelle coordinate dima; out ../doc/x210ai_dima_boardC_v2_1a1.pdf

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
# v3: taglia la parte superiore dei due lati della U (in v2) fino a 3 mm sotto la parte
# superiore del quadrato bianco: in coordinate dima.originali x = 12 - 3 = 9
RETT_V3 = [
    (-31.85, 9.0, -6.7, 12.2),      # R1 tagliata a x = 9
    (-39.5, -31.85, -6.7, -3.3),    # R2 invariato
    (-39.5, -27.75, -60.0, -3.3),   # R3 invariato
    (-39.5, 9.0, -60.0, -40.7),     # R4 tagliata a x = 9
]
# v4 = v3 + modifiche: invade lo spazio dello slot SIM di 2,2 mm (R3 x min -39,5 -> -42,2),
# parte bassa della U tagliata di 2 mm (R1 y max 12,2 -> 10,2),
# parte sinistra della U allargata di 7 mm (R4 y min -60 -> -67)
# v3.2 = v3.1 + modifiche (02/11/2026, prova sulla scheda madre):
#  - la plastica del telaio entra ~2 mm nella parte bassa della U: bordo plastica corretto a
#    x = -37,5, fondo della scheda (R2, R3, R4) da x -39,5 a -37,0 (0,5 mm di margine);
#  - lo slot SIM si puo' invadere dall'alto di 2 mm: R1 scende da x -31,85 a -34,35;
#  - il flat arancione occupa 2 mm in piu' verso sinistra (y min 12,7 -> 10,7): R1 ristretta a y 10,2;
#  - braccio sinistro della U (R4) accorciato in alto di 4 mm: x max 9 -> 5.
RETT_V32 = [
    (-34.35, 9.0, -6.7, 10.2),      # R1: invade lo slot SIM di 2 mm, ristretta verso il flat
    (-37.0, -31.85, -6.7, -3.3),    # R2: fondo alzato di 2,5 mm (plastica telaio)
    (-37.0, -27.75, -60.0, -3.3),   # R3: fondo alzato di 2,5 mm
    (-37.0, 5.0, -60.0, -40.7),     # R4: fondo alzato di 2,5 mm, alto tagliato di 4 mm
]
SIM_INVADIBILE = 2.0   # mm dello slot SIM (dal lato x = -32,35) che la scheda puo' coprire
RETT_V4 = [
    (-31.85, 9.0, -6.7, 10.2),      # R1: tagliata 2 mm in basso
    (-39.5, -31.85, -6.7, -3.3),    # R2 invariato
    (-42.2, -27.75, -60.0, -3.3),   # R3: invade lo slot SIM di 2,2 mm (bordo SIM a x=-40)
    (-39.5, 9.0, -67.0, -40.7),     # R4: allargata di 7 mm in alto
]
# FORMA viene calcolata in main() dopo aver scelto RETT (v1/v2/v3)

# ostacoli: posizioni come nella v3 originale (OSTACOLI di design_boardB.py, foto 19/10), nomi
# corretti il 02/11/2026 rifacendo il parsing delle foto con calibrazione su BTB_R_CONN1 + bordi del
# quadrato bianco (vedi riferimenti/misure/MISURE_foto_20261102.md, sezione "Correzione"):
#  - il rettangolo che si chiamava "connettore FPC" e' lo SLOT SIM (contatti dorati);
#  - il vero connettore FPC e' lo ZIF beige a destra del flat arancione (prima mancava);
#  - il vecchio "slot SIM" (x -50..-40, y -38,9..-26,9) era sulla plastica del telaio: tolto;
#  - tolti anche i rettangoli aggiunti il 02/11 (slot SIM a colonna e 3 "FPC" in alto): venivano da
#    una rettifica sbagliata (cornice ruotata di 180 gradi e non centrata su BTB nella foto).
OSTACOLI = [
    ("quadrato bianco VIETATO (<1 mm sopra), 39,3 x 33 mm", "r", (-27.25, 12.0, -40.2, -7.2)),
    ("BTB_R_CONN1 (spina J2 sotto, a 0,0)", "r", (-7.8, 7.8, -3.45, 3.45)),
    ("slot SIM", "r", (-45.0, -32.35, -2.8, 12.7)),
    ("flat arancione", "r", (-37.35, -21.35, 10.7, 17.2)),          # 02/11: +2 mm verso -y (prova fisica)
    ("connettore CN1", "r", (-30.35, -21.6, 17.25, 23.5)),
    ("connettore FPC (ZIF)", "r", (-45.5, -34.2, 18.2, 25.2)),
    ("vite", "c", (-7.8, 19.1, 3.55)),
    ("linguetta vite", "r", (-13.1, -5.8, 22.3, 26.4)),
]
# riferimenti (grigio tratteggiato): non sono ostacoli sul PCB ma aiutano ad allineare la dima e
# segnano dove finisce il piano libero; misurati sulle foto 19/10 e 02/11 (+-0,6 mm)
RIFERIMENTI = [
    ("plastica telaio (bordo)", (-60.0, -37.5, -47.0, -5.3)),       # 02/11: entra 2 mm piu' del misurato in foto
    ("plastica telaio (bordo)", (-60.0, -44.0, 4.8, 30.0)),
    ("staffa metallica", (11.15, 15.55, -9.3, 13.7)),
]
# posizione delle etichette nelle dime ruotate (v2+), coordinate dima: (x, y, rotazione testo)
# per non sovrapporle; chi non e' qui usa la posizione di default
ETICHETTE_CCW = {
    "slot SIM": (-38.7, 5.0, 0),
    "flat arancione": (-29.35, 13.95, 90),
    "connettore CN1": (-26.0, 24.5, 0),
    "connettore FPC (ZIF)": (-47.5, 18.2, 0),
    "BTB_R_CONN1 (spina J2 sotto, a 0,0)": (17.8, 0.0, 0),
    "vite": (-12.0, 19.1, 0),
}

def main():
    args = sys.argv[1:]
    ccw = "--rot90ccw" in args
    v3 = "--v3" in args
    v4 = "--v4" in args
    v32 = "--v32" in args
    v31 = "--v31" in args or v32
    v3 = v3 or v31
    pos = [a for a in args if not a.startswith("--")]
    if pos:
        out = pos[0]
    else:
        nome = ("x210ai_dima_boardC_v3_2_1a1.pdf" if v32 else "x210ai_dima_boardC_v3_1_1a1.pdf" if v31 else "x210ai_dima_boardC_v4_1a1.pdf" if v4 else "x210ai_dima_boardC_v3_1a1.pdf" if v3
                else "x210ai_dima_boardC_v2_1a1.pdf" if ccw else "x210ai_dima_boardC_1a1.pdf")
        out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "doc", nome)
    rett = RETT_V32 if v32 else RETT_V4 if v4 else (RETT_V3 if v3 else RETT)
    FORMA = unary_union([box(r[0], r[2], r[1], r[3]) for r in rett])
    # v2 (--rot90ccw): ruota di 90 gradi in senso ANTIORARIO tutti gli oggetti in coordinate
    # dima (board, quadrato vietato, connettori, riferimenti): (x,y) -> (y,-x). Pagina sempre A4
    # portrait: la rotazione e' nel sistema dima (y in giu'), non della pagina.
    w, h = 210, 297
    ox, oy = 105.0, 150.0

    def R(x, y):
        return (y, -x) if ccw else (x, y)

    def P(x, y):
        x, y = R(x, y)
        return ox + x, oy + y

    def rect(x0, x1, y0, y1, **kw):
        # rettangolo in coordinate dima: ruota TUTTI e 4 i vertici (width/height si scambiano)
        pts = [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]
        ax.add_patch(Polygon([P(*pt) for pt in pts], **kw))

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
    for k, r in enumerate(rett):
        cx, cy = (r[0] + r[1]) / 2, (r[2] + r[3]) / 2
        ax.text(*P(cx, cy), f"R{k+1} {r[1]-r[0]:g}x{r[3]-r[2]:g}", fontsize=6, ha="center", va="center")

    # zona sopra BTB_R_CONN1: solo PCB, niente componenti (~1,8 mm sopra)
    rect(-8.3, 8.3, -3.95, 3.95, fc="none", ec="tab:blue", lw=0.8, hatch="..", zorder=3)
    ax.text(*P(23 if ccw else 0, 0 if ccw else -5.8), "sopra BTB_R_CONN1: solo PCB 0,4-0,8 mm (~1,8 mm sopra)",
            fontsize=5.5, ha="center", color="tab:blue")

    # spina J2 a (0,0)
    rect(-6.62, 6.72, -2.92, 3.12, fc="none", ec="green", lw=1.0, zorder=4)
    ax.text(*P(0, 0), "J2", fontsize=6, ha="center", va="center", color="green", weight="bold", zorder=5)

    # riferimenti (non ostacoli): grigio tratteggiato
    for nome, (x0, x1, y0, y1) in RIFERIMENTI:
        rect(x0, x1, y0, y1, fc="none", ec="0.55", lw=0.7, ls="--", zorder=1)
        ax.text(*P((x0 + x1) / 2, (y0 + y1) / 2), "rif. " + nome, fontsize=4.5, color="0.45",
                ha="center", va="center", rotation=(90 if y1 - y0 < 6 else 0) if ccw else 90, zorder=1)

    if v32:   # fascia dello slot SIM che la scheda puo' coprire (dall'alto)
        x1s = -32.35
        rect(x1s - SIM_INVADIBILE, x1s, -2.8, 12.7, fc="none", ec="darkorange", lw=0.5, hatch="////", zorder=3)

    # ostacoli
    for nome, t, d in OSTACOLI:
        if t == "r":
            x0, x1, y0, y1 = d
            col = "red" if "VIETATO" in nome else ("green" if "BTB" in nome else "darkorange")
            lw = 1.6 if "VIETATO" in nome else 0.9
            rect(x0, x1, y0, y1, fc="none", ec=col, lw=lw, zorder=3)
            if ccw and nome in ETICHETTE_CCW:
                lx, ly, rot = ETICHETTE_CCW[nome]
                ax.text(*P(lx, ly), nome, fontsize=5, color=col, ha="center", va="center", rotation=rot,
                        zorder=5)
            else:
                ax.text(*P(x0 + 0.5, y0 - 2.0 if "VIETATO" in nome else y1 + 2.0), nome, fontsize=5,
                        color=col, ha="left")
        else:
            cx, cy, r = d
            ax.add_patch(Circle(P(cx, cy), r, fc="none", ec="darkorange", lw=0.9, zorder=3))
            lx, ly, _ = ETICHETTE_CCW[nome] if ccw and nome in ETICHETTE_CCW else (cx, cy + r + 2.0, 0)
            ax.text(*P(lx, ly), nome, fontsize=5, color="darkorange", ha="center", va="center")

    # frecce rosse verso l'origine (centro BTB_R_CONN1)
    for (xa, ya), (xb, yb) in (((0, -36), (0, -30)), ((0, 34), (0, 28)),
                               ((-52, 0), (-46, 0)), ((36, 0), (30, 0))):
        ax.annotate("", xy=P(xb, yb), xytext=P(xa, ya),
                    arrowprops=dict(arrowstyle="-|>", lw=0.8, color="tab:red"))
    ax.text(*P(38, 0) if ccw else P(0, -38), "centro BTB_R_CONN1 qui (0,0)", fontsize=6, ha="center", color="tab:red")

    # righello di controllo 50 mm
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
    if v32:
        legend.append("7. v3.2: fascia arancione tratteggiata = 2 mm di slot SIM che la scheda puo' coprire dall'alto.")
    if v31:
        legend.insert(len(legend) - (1 if v32 else 0), "6. Grigio tratteggiato = riferimenti (bordo plastica telaio, staffa metallica): non ostacoli PCB,"
                      " servono per allineare; " + ("il fondo della U sta 0,5 mm dentro la plastica." if v32
                      else "il bordo basso della U tocca la plastica (~0,3 mm, da verificare)."))
    for i, s in enumerate(legend):
        ax.text(18, 14 + i * 4.6, s, fontsize=5.6 if i else 6.5, weight="bold" if i == 0 else "normal")
    ver = "v3.2" if v32 else "v3.1" if v31 else "v4" if v4 else "v3" if v3 else "v2" if ccw else "v1"
    titolo = f"X210Ai - dima Board C {ver} (forma C4" + (", ruotata 90 gradi antiorario" if ccw else "") \
        + "), rev 2.3" + (" - plastica, SIM, flat, braccio sx corretti" if v32
                                 else " - ingombri con nomi corretti 02/11" if v31 else "")
    ax.text(105, 8, titolo, fontsize=8, ha="center", weight="bold")

    fig.savefig(out)
    print("ok", os.path.normpath(out))
    if v31:   # versione modificabile (Inkscape): stessa pagina A4 1:1
        fig.savefig(out[:-4] + ".svg")
        print("ok", os.path.normpath(out[:-4] + ".svg"))
    print(f"area forma {FORMA.area:.0f} mm2, rettangoli {rett}")
    for nome, t, d in OSTACOLI:
        o = box(d[0], d[2], d[1], d[3]) if t == "r" else Point(d[:2]).buffer(d[2], 32)
        if "BTB" in nome:
            print(f"  BTB_R_CONN1 coperta: {FORMA.contains(o)}")
        else:
            sov = FORMA.intersection(o).area
            print(f"  distanza da {nome}: {FORMA.distance(o):.2f} mm"
                  + (f"  SOVRAPPOSIZIONE {sov:.1f} mm2" if sov > 0.01 else ""))
    for nome, d in RIFERIMENTI:
        o = box(d[0], d[2], d[1], d[3])
        sov = FORMA.intersection(o)
        print(f"  rif. {nome}: distanza {FORMA.distance(o):.2f} mm, sovrapposizione {sov.area:.1f} mm2"
              + (f" (bordo x {sov.bounds[0]:.1f}..{sov.bounds[2]:.1f})" if sov.area else ""))


if __name__ == "__main__":
    main()
