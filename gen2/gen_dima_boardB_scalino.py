# -*- coding: utf-8 -*-
"""Dima 1:1 (PDF A4) della Board B in variante "a scalino" (prova meccanica, 28/10/2026).

Sopra BTB_R_CONN1 la tastiera non ci sta: con la Board B a sandwich la sua spina salirebbe di 1,9 mm e non
c'e' spazio nemmeno per una moneta da 5 centesimi (1,67 mm). Variante: la Board B si divide in due livelli.
- Gradino alto: innestato su BTB_R_CONN1 con la sola spina (lato sotto) e J4 (eDP) accanto, dalla parte
  opposta al ricettacolo della tastiera, con il cavo che esce allontanandosi dal connettore.
- Scalino: un tratto flessibile scende di 1,5 mm (l'altezza di accoppiamento della spina) fino alla scheda
  madre, sul lato lungo di BTB_R_CONN1 verso la vite.
- Gradino basso: appoggiato sulla scheda madre (con Kapton), porta il ricettacolo della tastiera accanto a
  BTB_R_CONN1, ruotato di 25 gradi in senso orario.

Il disegno e' orientato come la scheda madre vista dall'alto con il palmrest in basso: "su" = lontano dal
palmrest, BTB_R_CONN1 e J4 verticali, ricettacolo della tastiera a destra. I calcoli usano le coordinate di
design_boardB.py (x lungo BTB_R_CONN1 verso la parte opposta al palmrest, y verso la vite): nel disegno x
diventa "su" e y "destra" (rotazione di 90 gradi in senso antiorario).

Ingombri dalla foto della cornice di misura (gen_dima_scala.py) del 28/10/2026, seconda foto, raddrizzata con
3 crocini e 2 tacche dei righelli (scarto < 0,35 mm). I nastri (tessuto nero, alluminio) non sono ingombri:
sono disegnati solo come riferimento. La linguetta della vite viene dalla prima foto (fuori dalla finestra).
Il circuito NON cambia: qui si prova solo l'ingombro.

uso: python3 gen_dima_boardB_scalino.py [out.pdf]   (default ../doc/x210ai_dima_boardB_scalino_1a1.pdf)
Stampare al 100% (senza "adatta alla pagina") e controllare il righello da 50 mm.
"""
import math
import os
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt                     # noqa: E402
from matplotlib.patches import Circle, Polygon      # noqa: E402
from shapely.geometry import Point, Polygon as SPoly, box    # noqa: E402
from shapely.ops import unary_union                 # noqa: E402

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import design_boardB as D                           # noqa: E402
from gen_dima_rev22 import LIB, MM, PAD, footprint, rot_pt   # noqa: E402

VIEW = 90           # rotazione del disegno rispetto alle coordinate di design_boardB.py (KiCad: antiorario +)

# geometria e ingombri: dal modello dati della Board B (stessa forma del PCB)
from design_boardB import (OSTACOLI, VIETATE, NASTRI, shape, ROT_KB, STEP_H, FLEX_L, J1_CRT, J4_CRT,  # noqa: E402
                           CAVO_W, J4_ROT, J4_X, J4_Y, HIGH, KB_X, KB_Y, LOW, FLEX_X0, FLEX_X1, FLEX,
                           FLEX_DEV, Y_HI, BAND_X1 as X1, margini)
J4_PLUG = 4.65      # la spina del cavo innestata arriva a 5,1 mm dalla punta dei piedini


def rot(pts, a):
    return [rot_pt(x, y, a) for x, y in pts]


def disegna(ax, ox, oy, ostacoli, distesa=False):
    def T(x, y, dy=0.0):
        """coordinate di design_boardB.py -> pagina (vista con il palmrest in basso)"""
        u, v = rot_pt(x, y + dy, VIEW)
        return ox + u, oy + v

    def poly(pts, dy=0.0, **kw):
        ax.add_patch(Polygon([T(x, y, dy) for x, y in pts], closed=True, **kw))

    def rect(d, **kw):
        poly([(d[0], d[2]), (d[1], d[2]), (d[1], d[3]), (d[0], d[3])], **kw)

    dy = FLEX_DEV if distesa else 0.0          # copia da ritagliare: lo scalino disteso e' un po' piu' lungo
    if ostacoli:
        for nome, d in NASTRI:
            rect(d, fc="none", ec="silver", lw=0.3, ls=":")
            ax.text(*T((d[0] + d[1]) / 2, (d[2] + d[3]) / 2), nome + "\n(non ingombro)", fontsize=2.8,
                    ha="center", va="center", color="silver")
        for nome, tipo, d in OSTACOLI:
            col = "tab:blue" if nome == "BTB_R_CONN1" else ("tab:red" if nome in VIETATE else "dimgray")
            hatch = None if col == "tab:blue" else ("xx" if nome in VIETATE else "////")
            if tipo == "r":
                rect(d, fc="none", ec=col, lw=0.3, hatch=hatch, alpha=0.6)
                tx, ty = (d[0] + d[1]) / 2, (d[2] + d[3]) / 2
            else:
                ax.add_patch(Circle(T(d[0], d[1]), d[2], fc="none", ec=col, lw=0.3, hatch=hatch, alpha=0.6))
                tx, ty = d[0], d[1]
            if nome in VIETATE:
                ax.text(*T(tx, ty), nome + "\nZONA VIETATA\n(sopra < 1 mm)", fontsize=4, ha="center", va="center",
                        color="tab:red")
            elif nome != "BTB_R_CONN1":
                ax.text(*T(tx, ty), nome, fontsize=3.2, ha="center", va="center", color="dimgray")
        # spina del cavo innestata e fascio che si allontana dal connettore (non fanno parte della scheda)
        pw, cx = 26.25, J4_X - J4_PLUG
        rect((cx, J4_X + 0.45, J4_Y - pw / 2, J4_Y + pw / 2), fc="none", ec="tab:green", lw=0.4, ls="-.")
        rect((cx - 12, cx, J4_Y - CAVO_W / 2, J4_Y + CAVO_W / 2), fc="tab:green", alpha=0.12, ec="tab:green",
             lw=0.3)
        ax.text(*T(cx - 7, J4_Y), "cavo eDP verso la Board A", fontsize=4.5, color="tab:green", ha="center",
                va="center")
    poly(HIGH, fc="none", ec="black", lw=0.8)
    poly([(x, y + (dy if y > Y_HI else 0)) for x, y in FLEX], fc="tab:orange", alpha=0.2, ec="black", lw=0.8)
    poly(LOW, dy, fc="none", ec="black", lw=0.8)
    for yf in (Y_HI, Y_HI + FLEX_L + dy):           # linee di piega dello scalino (a S)
        ax.plot(*zip(T(FLEX_X0 - 1.5, yf), T(FLEX_X1 + 1.5, yf)), color="tab:orange", lw=0.5, ls="--")
    ax.text(*T(X1 + 1.5, Y_HI + (FLEX_L + dy) / 2), f"scalino\n{STEP_H:g} mm", fontsize=3.5, ha="center",
            va="bottom", color="tab:orange")
    t = open(os.path.join(LIB, "JAE_AA01_sandwich.kicad_mod")).read()
    for x, y, w, h, s in PAD.findall(t):
        x, y, w, h = map(float, (x, y, w, h))
        c = [(x - w / 2, y - h / 2), (x + w / 2, y - h / 2), (x + w / 2, y + h / 2), (x - w / 2, y + h / 2)]
        if s == "B":    # spina sotto, su BTB_R_CONN1
            poly(c, fc="none", ec="tab:blue", lw=0.2)
        else:           # ricettacolo della tastiera, sul gradino basso
            poly([(KB_X + p, KB_Y + q) for p, q in rot(c, ROT_KB)], dy, fc="tab:purple", ec="tab:purple", lw=0.2,
                 alpha=0.8)
    ax.text(*T(0, 0), "spina\nsotto", fontsize=3.5, ha="center", va="center", color="tab:blue")
    footprint(ax, "IPEX_20455-040E_90deg", *T(J4_X, J4_Y), "tab:green", (J4_ROT + VIEW) % 360)
    ax.text(*T(J4_X - 2.6, J4_Y), "J4", fontsize=5, ha="center", va="center", color="tab:green")
    px, py = rot_pt(-9.75, -1.0, J4_ROT)
    ax.text(*T(J4_X + px, J4_Y + py), "1", fontsize=4, ha="center", va="center", color="tab:green")
    px, py = rot_pt(-4.7, -3.8, ROT_KB)
    ax.text(*T(KB_X + px, KB_Y + py, dy), "1", fontsize=4, ha="center", va="center", color="tab:purple")
    ax.text(*T(KB_X, KB_Y, dy), "ricettacolo\ntastiera", fontsize=3.5, ha="center", va="center",
            color="tab:purple")


def _pagina(d, tipo="r"):
    """ingombro nelle coordinate del disegno: (destra da, a), (su da, a) in mm dal centro di BTB_R_CONN1"""
    if tipo == "c":
        return (d[1] - d[2], d[1] + d[2]), (d[0] - d[2], d[0] + d[2])
    return (d[2], d[3]), (d[0], d[1])


def _bbox(pts):
    xs, ys = [p[0] for p in pts], [p[1] for p in pts]
    return (min(xs), max(xs), min(ys), max(ys))


def _bom(board):
    """righe della BOM completa (produzione/boardX/..._bom_completa_mpn.csv)"""
    import csv
    p = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "produzione", f"board{board}",
                     f"x210ai_rev{D.REV}_board{board}_bom_completa_mpn.csv")
    return list(csv.DictReader(open(p, encoding="utf-8")))


def _pkg(fp):
    for k, v in (("C_0402", "0402"), ("R_0402", "0402"), ("SOT-363", "SOT-363"), ("SOT-23-3", "SOT-23"),
                 ("QFN-56", "QFN-56 7x7"), ("Winbond_USON-8", "USON-8 3x2"), ("Crystal_SMD_3225", "3225"),
                 ("SolderJumper", "ponticello"), ("Pads_1x04", "4 piazzole"), ("TP_Pad", "piazzola 1 mm"),
                 ("IPEX_20455", "I-PEX 20455"), ("JAE_AA01", "JAE AA01")):
        if fp.startswith(k):
            return v
    return fp


def legenda(out):
    """PDF A4 con la legenda di tutto: elementi della dima, scheda madre, componenti della Board A e della Board B"""
    import design_boardA as A
    pos = lambda r: f"{r[0]:+.1f} / {r[1]:+.1f}"              # noqa: E731
    sezioni = []

    # 1. elementi della dima (Board B a scalino)
    cols = [(10, "Elemento"), (38, "Nel disegno"), (70, "Cos'e'"), (138, "Destra da / a"), (156, "Su da / a"),
            (174, "Note")]
    r = []
    kb = _bbox([(KB_X + x, KB_Y + y) for x, y in rot([(J1_CRT[0], J1_CRT[2]), (J1_CRT[1], J1_CRT[2]),
                                                       (J1_CRT[1], J1_CRT[3]), (J1_CRT[0], J1_CRT[3])], ROT_KB)])
    for nome, col, cosa, dd, nota in [
        ("Gradino alto", "contorno nero", "PCB sulla spina in BTB_R_CONN1 (0,4 mm o flessibile)", _bbox(HIGH),
         "1,5 mm sopra la scheda madre"),
        ("Spina J1 (sotto)", "blu, piazzole vuote", "JAE AA01B-P040VA1 in BTB_R_CONN1",
         (J1_CRT[0], J1_CRT[1], J1_CRT[2], J1_CRT[3]), "a mano, non su LCSC"),
        ("J4", "verde, piazzole", "ricettacolo eDP I-PEX 20455-040E-76, piedini verso il connettore",
         (J4_X - J4_CRT[3], J4_X - J4_CRT[2], J4_Y - J4_CRT[1], J4_Y + J4_CRT[1]), "~3,0 mm dalla sch. madre"),
        ("Spina e cavo eDP", "verde tratteggio / chiaro", "spina I-PEX 20453 + 40 micro-coassiali verso la Board A",
         (J4_X - J4_PLUG - 12, J4_X + 0.45, J4_Y - 13.1, J4_Y + 13.1), "verso il palmrest"),
        ("Scalino", "arancio, tratteggio", f"tratto flessibile: scende di {STEP_H:g} mm in {FLEX_L:g} mm", _bbox(FLEX),
         "piega a S, raggio ~1,5 mm"),
        ("Gradino basso", "contorno nero ruotato", "PCB appoggiato sulla scheda madre (Kapton sotto)", _bbox(LOW), ""),
        ("Ricettacolo tastiera", "viola", f"JAE AA01B-S040VA1 (C2938571), {abs(ROT_KB):g} gradi orario", kb,
         "~2,9 mm con spina e flat"),
        ('Numero "1"', "verde / viola", "pin 1 di J4 e del ricettacolo della tastiera", None, ""),
    ]:
        p = _pagina(dd) if dd else None
        r.append((nome, col, cosa, pos(p[0]) if p else "", pos(p[1]) if p else "", nota))
    sezioni.append(("DIMA - Board B a scalino (mm dal centro di BTB_R_CONN1; destra = verso la vite, su = lontano "
                    "dal palmrest)", cols, r))

    # 2. scheda madre
    note = {"BTB_R_CONN1": "origine delle misure", "connettore FPC": "continua oltre la cornice",
            "flat arancione": "flat inserito in CN1", "vite": "foro con anello, vite del palmrest",
            "linguetta vite": "dalla prima foto", "connettore CN1": "dalla prima foto",
            "quadrato bianco": "sopra meno di 1 mm"}
    cosa = {"BTB_R_CONN1": "connettore tastiera della scheda madre", "quadrato bianco": "ZONA VIETATA"}
    r = []
    for nome, tipo, d in OSTACOLI:
        col = "blu" if nome == "BTB_R_CONN1" else ("rosso, quadrettato" if nome in VIETATE else "grigio, tratteggio")
        p = _pagina(d, tipo)
        r.append((nome, col, cosa.get(nome, "ingombro"), pos(p[0]), pos(p[1]), note.get(nome, "")))
    for nome, d in NASTRI:
        p = _pagina(d)
        r.append((nome, "grigio chiaro, puntinato", "nastro: NON e' un ingombro", pos(p[0]), pos(p[1]), ""))
    sezioni.append(("SCHEDA MADRE (foto della cornice di misura del 28/10/2026, +/-0,3 mm)", cols, r))

    # 3-4. componenti delle due schede
    cols = [(10, "Rif."), (21, "Valore"), (42, "Funzione"), (100, "Produttore / MPN"), (143, "LCSC"),
            (155, "Package"), (172, "Lato"), (188, "x / y")]
    for board, titolo in (("A", f"BOARD A - {A.X1 - A.X0:.1f} x {A.Y1 - A.Y0:.1f} mm, 4 strati 0,8 mm, sotto il "
                                "palmrest (x / y in mm dal centro della dima della Board A, y verso il basso)"),
                          ("B", "BOARD B - variante a scalino, 4 strati 0,4 mm o flessibile (posizioni: vedi dima; "
                                "Q2, Q3, R13, R14 sotto il gradino alto, da piazzare)")):
        place = A.PLACE if board == "A" else {}
        r = []
        for b in _bom(board):
            ref = b["Designator"]
            pl = place.get(ref)
            lato = {"Top": "sopra", "Bottom": "sotto"}.get(b["Side"], b["Side"])
            mont = "" if b["Assembly"] == "si" else (" (rame)" if b["Assembly"].startswith("no") else " (mano)")
            mpn = (b["Manufacturer"] + " " + b["MPN"]).strip()
            funz = b["Note"]
            if ref == "J1":
                funz = "ricettacolo tastiera (sopra)" if b["Side"] == "Top" else "spina verso BTB_R_CONN1 (sotto)"
            r.append((ref, b["Value"], funz[:56], mpn[:40], b["LCSC"], _pkg(b["Footprint"]), lato + mont,
                      f"{pl[0] - (A.X0 + A.X1) / 2:+.1f} / {pl[1] - (A.Y0 + A.Y1) / 2:+.1f}" if pl else ""))
        sezioni.append((titolo, cols, r))

    righe = sum(len(s[2]) for s in sezioni)
    w, h = 210, 297
    fig = plt.figure(figsize=(w * MM, h * MM))
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, w)
    ax.set_ylim(h, 0)
    ax.axis("off")
    ax.text(10, 11, f"X210Ai rev {D.REV} - legenda: dima Board B a scalino, scheda madre, Board A e Board B",
            fontsize=8.5, weight="bold")
    passo = min(3.3, (h - 30 - len(sezioni) * 9) / righe)       # tutto in una pagina
    fs = passo * 1.55
    y = 18
    for titolo, cols, r in sezioni:
        y += 2
        ax.text(10, y, titolo, fontsize=fs + 0.6, weight="bold", color="0.2")
        y += passo + 0.6
        for x, s in cols:
            ax.text(x, y, s, fontsize=fs, weight="bold")
        ax.plot([10, 200], [y + 0.8, y + 0.8], color="black", lw=0.3)
        y += passo + 0.3
        for row in r:
            for (x, _), s in zip(cols, row):
                ax.text(x, y, s, fontsize=fs, weight="bold" if x == cols[0][0] else "normal",
                        color="tab:red" if "VIETATA" in row[2] else "black")
            y += passo
    y += 2
    for i, s in enumerate(["Altezze dalla scheda madre: spina in BTB_R_CONN1 1,5 mm; gradino alto 1,9 mm; J4 innestato "
                           "~3,0 mm; gradino basso 0,4 mm; ricettacolo con spina e flat ~2,9 mm.",
                           "Margini: " + ";  ".join(f"{k} {v:.1f} mm" for k, v in margini().items())]):
        ax.text(10, y + i * (passo + 0.4), s, fontsize=fs)
    fig.savefig(out)
    print("ok", os.path.normpath(out), f"({righe} righe, carattere {fs:.1f} pt)")


def main():
    out = sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                                             "..", "doc", "x210ai_dima_boardB_scalino_1a1.pdf")
    w, h = 210, 297
    fig = plt.figure(figsize=(w * MM, h * MM))
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, w)
    ax.set_ylim(h, 0)
    ax.axis("off")
    disegna(ax, 98.0, 128.0, True)
    disegna(ax, 98.0, 225.0, False, distesa=True)

    m = margini()
    hx = [x for x, _ in HIGH]
    hy = [y for _, y in HIGH]
    legend = ["PROVA MECCANICA, circuito invariato. Ingombri dalla seconda foto della cornice di misura (28/10).",
              "Orientamento: scheda madre vista dall'alto con il palmrest in BASSO; BTB_R_CONN1 e J4 verticali.",
              f"nero: gradino alto ({max(hy) - min(hy):.1f} x {max(hx) - min(hx):.1f} mm) sulla spina in BTB_R_CONN1 (blu), "
              "J4 in basso (verso il palmrest);",
              f"arancio: scalino flessibile, scende di {STEP_H:g} mm in {FLEX_L:g} mm (piega a S tra le linee tratteggiate);",
              f"viola: ricettacolo della tastiera sul gradino basso, a destra, appoggiato sulla scheda madre, "
              f"{abs(ROT_KB):g} gradi in senso orario;",
              "verde: J4 eDP e spina/fascio del cavo;  grigio: ingombri;  rosso: zona vietata;  puntinato: nastri",
              "Legenda completa dei componenti: x210ai_dima_boardB_scalino_legenda.pdf",
              "margini: " + ";  ".join(f"{k} {v:.1f} mm" for k, v in m.items()),
              "Copia in basso: ritaglia il contorno nero (scalino compreso), piega a Z sulle linee arancio in modo che",
              f"il gradino basso scenda di {STEP_H:g} mm, appoggia la parte alta su BTB_R_CONN1 (pin 1 come in serigrafia)",
              "e controlla: niente sopra il quadrato bianco, gradino basso libero accanto alla vite, spina della tastiera",
              "che arriva sul ricettacolo viola,",
              "spazio sopra il gradino basso per spina + flat (circa 2,9 mm dalla scheda madre), spazio sopra J4",
              "(circa 3,0 mm dalla scheda madre) e strada libera per il cavo eDP."]
    ax.text(15, 16, f"X210Ai rev {D.REV} - dima 1:1 Board B, variante a scalino (palmrest in basso)", fontsize=8,
            weight="bold")
    for i, s in enumerate(legend + ["Stampa al 100% (senza 'adatta alla pagina')."]):
        ax.text(15, 23 + i * 4.1, s, fontsize=5.1)
    ax.text(15, 180, "da ritagliare (scalino disteso):", fontsize=6, weight="bold")
    ax.text(105, 286, "palmrest (in basso)", fontsize=6, ha="center", color="0.4")
    ax.plot([15, 65], [280, 280], color="black", lw=0.8)
    for x in range(15, 66, 10):
        ax.plot([x, x], [279, 281], color="black", lw=0.5)
    ax.text(40, 285, "50 mm: controlla con il calibro", fontsize=6, ha="center")
    fig.savefig(out)
    print("ok", os.path.normpath(out))
    legenda(out.replace("_1a1.pdf", "_legenda.pdf") if out.endswith("_1a1.pdf") else out[:-4] + "_legenda.pdf")
    print(f"gradino alto {max(hy) - min(hy):.1f} x {max(hx) - min(hx):.1f} mm (larghezza x altezza nel disegno); "
          f"ricettacolo tastiera a {KB_Y:.2f} mm a destra del centro di BTB_R_CONN1, rot {ROT_KB:g}")
    for k, v in m.items():
        print(f"  {k}: {v:.2f} mm")


if __name__ == "__main__":
    main()
