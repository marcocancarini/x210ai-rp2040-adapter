# -*- coding: utf-8 -*-
"""Dima di prova in scala 1:1 (PDF A4): contorno della scheda-ponte, posizione del connettore,
ingombro dei componenti sul lato verso la scheda madre, righello di controllo.

uso: python3.12 gen_dima.py board.kicad_pcb out.pdf
"""
import os
import sys

import cairosvg
import pcbnew

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import boards  # noqa: E402

D = boards.load()
if getattr(D, "BOARD", "2.0") != "2.0":
    raise SystemExit("gen_dima.py disegna la scheda-ponte rev 2.0; per la rev 2.2: gen_dima_rev22.py A|B out.pdf")

pcb, out = sys.argv[1:3]
b = pcbnew.LoadBoard(pcb)
OX, OY = D.ORIGIN
mm = pcbnew.ToMM
HEIGHT = {"U1": 0.9, "U2": 0.55, "U3": 1.1, "Y1": 0.8, "Q1": 1.0, "Q2": 1.0, "Q3": 1.0}

svg = []


def add(s):
    svg.append(s)


def board_view(px, py, title):
    """disegna una copia della dima con origine (centro connettore) in (px, py) mm sulla pagina"""
    X = lambda x: px + x  # noqa: E731
    Y = lambda y: py + y  # noqa: E731
    r = D.CORNER_R
    add(f'<rect x="{X(D.X0):.3f}" y="{Y(D.Y0):.3f}" width="{D.X1 - D.X0:.3f}" height="{D.Y1 - D.Y0:.3f}" '
        f'rx="{r}" fill="#f4f4f4" stroke="#000" stroke-width="0.25"/>')
    # connettore (corpo J1 / BTB_R_CONN1)
    add(f'<rect x="{X(-6.9):.3f}" y="{Y(-2.5):.3f}" width="13.9" height="4.8" fill="none" stroke="#c00" '
        f'stroke-width="0.3"/>')
    add(f'<circle cx="{X(-4.7):.3f}" cy="{Y(-3.3):.3f}" r="0.35" fill="#c00"/>')
    add(f'<text x="{X(-4.2):.3f}" y="{Y(-3.0):.3f}" font-size="1.3" fill="#c00">pin 1</text>')
    add(f'<text x="{X(-6.4):.3f}" y="{Y(0.5):.3f}" font-size="1.4" fill="#c00">BTB_R_CONN1 / J1-J2</text>')
    # componenti sul lato scheda madre (tratteggiati)
    for fp in b.GetFootprints():
        if not fp.IsFlipped() or fp.GetReference() in ("J2",):
            continue
        bb = fp.GetBoundingBox(False, False)
        x0, y0 = mm(bb.GetLeft()) - OX, mm(bb.GetTop()) - OY
        w, h = mm(bb.GetWidth()), mm(bb.GetHeight())
        ref = fp.GetReference()
        col = "#1f5fbf" if ref in HEIGHT else "#7a9cc6"
        add(f'<rect x="{X(x0):.3f}" y="{Y(y0):.3f}" width="{w:.3f}" height="{h:.3f}" fill="none" stroke="{col}" '
            f'stroke-width="0.12" stroke-dasharray="0.6,0.4"/>')
        if ref in HEIGHT:
            add(f'<text x="{X(x0 + w / 2):.3f}" y="{Y(y0 + h / 2) + 0.4:.3f}" font-size="1.0" text-anchor="middle" '
                f'fill="{col}">{ref} {HEIGHT[ref]:g}</text>')
    # piazzole fili USB
    j3 = b.FindFootprintByReference("J3")
    for p in j3.Pads():
        c = p.GetPosition()
        add(f'<circle cx="{X(mm(c.x) - OX):.3f}" cy="{Y(mm(c.y) - OY):.3f}" r="0.5" fill="#2a2"/>')
    add(f'<text x="{X(D.X0) + 0.3:.3f}" y="{Y(D.Y1) + 2.4:.3f}" font-size="1.3">fili USB verso USB-CON1</text>')
    add(f'<text x="{X(D.X0):.3f}" y="{Y(D.Y0) - 1.2:.3f}" font-size="2.0" font-weight="bold">{title}</text>')
    add(f'<text x="{X(0):.3f}" y="{Y(D.Y0) - 4.6:.3f}" font-size="1.3" text-anchor="middle">'
        f'verso il quadrato bianco (non superare)</text>')
    add(f'<path d="M{X(0)} {Y(D.Y0) - 1.2} l0 -2.4 m-0.7 0.7 l0.7 -0.7 l0.7 0.7" stroke="#000" fill="none" '
        f'stroke-width="0.2"/>')
    add(f'<path d="M{X(0)} {Y(D.Y1) + 1.2} l0 2.0 m-0.7 -0.7 l0.7 0.7 l0.7 -0.7" stroke="#000" fill="none" '
        f'stroke-width="0.2"/>')
    add(f'<text x="{X(0):.3f}" y="{Y(D.Y1) + 4.6:.3f}" font-size="1.3" text-anchor="middle">'
        f'verso il foro della vite</text>')


W, H = 210, 297
add(f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}mm" height="{H}mm" viewBox="0 0 {W} {H}" '
    f'font-family="DejaVu Sans, sans-serif">')
add('<rect width="210" height="297" fill="#fff"/>')
add('<text x="15" y="20" font-size="5" font-weight="bold">X210Ai scheda-ponte rev 2.0 - dima 1:1</text>')
lines = ["Stampa al 100% (\"dimensioni effettive\", senza adattare alla pagina) e controlla il righello qui sotto.",
         "Vista dall'alto, scheda madre orientata come nella foto: connettore tastiera a destra,",
         "quadrato bianco sopra, foro della vite sotto. Il rettangolo rosso va sopra BTB_R_CONN1.",
         "I rettangoli blu tratteggiati sono i componenti rivolti verso la scheda madre (altezza in mm):",
         "in quella zona la scheda madre deve essere libera (spazio sotto la scheda: 1,5 mm).",
         "Ritaglia una copia lungo il contorno e appoggiala sulla scheda madre per controllare gli ingombri."]
for i, s in enumerate(lines):
    add(f'<text x="15" y="{29 + i * 5.2}" font-size="3.4">{s}</text>')
# righello 50 mm + quadrato 10 mm
add('<g stroke="#000" stroke-width="0.25">')
add('<line x1="15" y1="70" x2="65" y2="70"/>')
for i in range(0, 51):
    hgt = 3 if i % 10 == 0 else (2 if i % 5 == 0 else 1)
    add(f'<line x1="{15 + i}" y1="70" x2="{15 + i}" y2="{70 - hgt}"/>')
add('</g>')
for i in range(0, 51, 10):
    add(f'<text x="{15 + i}" y="74.5" font-size="2.6" text-anchor="middle">{i}</text>')
add('<text x="68" y="71" font-size="3">mm (deve misurare esattamente 50 mm)</text>')
add('<rect x="150" y="60" width="10" height="10" fill="none" stroke="#000" stroke-width="0.25"/>')
add('<text x="162" y="66" font-size="2.6">10 x 10 mm</text>')
board_view(50, 105, "Copia 1 (1:1)")
board_view(140, 105, "Copia 2 (1:1, da ritagliare)")
add('<g transform="translate(105 205) scale(3)">')
board_view(10.7, 0, "Ingrandimento 3:1 (NON in scala)")
add('</g>')
add('<text x="15" y="282" font-size="2.8">Contorno 36,5 x 10,6 mm; il connettore e\' a 29 mm dal bordo sinistro. '
    'Spessore: 1,5 mm sotto la scheda + PCB + 1,5 mm sopra.</text>')
add('</svg>')
cairosvg.svg2pdf(bytestring="\n".join(svg).encode(), write_to=out)
cairosvg.svg2png(bytestring="\n".join(svg).encode(), write_to=out.replace(".pdf", ".png"), output_width=1240)
print(out)
