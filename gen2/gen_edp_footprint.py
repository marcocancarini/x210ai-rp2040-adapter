# -*- coding: utf-8 -*-
"""Genera l'impronta del ricettacolo eDP I-PEX CABLINE-VS 20455-0nnE (formato KiCad 7).

uso: python3 gen_edp_footprint.py <out_dir> [n_pin]      (default 40 -> IPEX_20455-040E_90deg.kicad_mod)

Quote dal catalogo I-PEX CABLINE-VS (rev. 202610R0), "Recommended footprint layout P/N 20455-0**E-##" e
"Receptacle assembly". Per 20/30/40/50 pin: A = 0,5 (n-1), B = A + 1,8, E = A + 4,8, G = A + 8,7, C = A + 6,75.
Origine al centro della fila di piazzole segnale; le piazzole sono verso -y, il corpo e il cavo verso +y.
"""
import os
import sys

from fplib import header, line, rect, text, tid

PITCH = 0.5
SIG = (0.25, 0.90)        # piazzola segnale (larghezza x lunghezza)
GBAR = (0.55, 0.90)       # piazzole della barra di massa, ai lati della fila
HOLD = (1.40, 1.90)       # piazzole delle linguette di fissaggio
HOLD_GAP = 1.42           # dal bordo inferiore delle piazzole segnale al bordo superiore delle linguette
TIP_IN_PAD = 0.32         # la piazzola sporge di 0,32 oltre la punta del piedino
BODY_FRONT = 0.55         # dalla punta del piedino al fronte del corpo
BODY_DEPTH = 3.95         # dalla punta del piedino al retro del corpo
MATED_DEPTH = 5.10        # dalla punta del piedino al retro della spina innestata
KEEPOUT_TOP = 0.55        # area libera oltre il bordo superiore delle piazzole
KEEPOUT_H = 6.70          # profondita' dell'area libera (nota 1: barra di sgancio della spina)
HEIGHT = 1.00             # altezza innestata +0,1


def edp(n=40):
    a = PITCH * (n - 1)
    b, e, g, c = a + 1.8, a + 4.8, a + 8.7, a + 6.75
    name = f"IPEX_20455-{n:03d}E_90deg"
    y_pad_top = -SIG[1] / 2
    y_tip = y_pad_top + TIP_IN_PAD
    y_front, y_rear, y_mated = y_tip + BODY_FRONT, y_tip + BODY_DEPTH, y_tip + MATED_DEPTH
    hold_y = SIG[1] / 2 + HOLD_GAP + HOLD[1] / 2
    hold_x = e / 2 + HOLD[0] / 2
    ko_y0 = y_pad_top - KEEPOUT_TOP
    ko_y1 = ko_y0 + KEEPOUT_H

    s = header(name, f"I-PEX CABLINE-VS 20455-{n:03d}E receptacle, {n} pin P0.5mm, accoppiamento orizzontale, "
                     f"altezza {HEIGHT:.2f} mm. Spina cavo 20453-{n:03d}T. Land pattern dal catalogo I-PEX "
                     f"CABLINE-VS 202610R0. Pad 41 = barra di massa e linguette di fissaggio.",
               "eDP CABLINE-VS I-PEX 20455 micro-coax 0.5mm")
    s += text("reference", "REF**", 0, ko_y0 - 0.8, "F.SilkS", 0.8, name)
    s += text("value", name, 0, ko_y1 + 0.8, "F.Fab", 0.8, name)
    s += text("user", "${REFERENCE}", 0, (y_front + y_rear) / 2, "F.Fab", 0.8, name + "u")
    s += text("user", "solo solder resist o GND sotto il connettore; nessun componente nel riquadro (barra di sgancio)",
              0, ko_y1 + 1.8, "Cmts.User", 0.5, name + "note")
    # serigrafia: retro del corpo tra le linguette e indicatore del pin 1
    xs = hold_x - HOLD[0] / 2 - 0.25
    s += line(-xs, y_rear + 0.15, xs, y_rear + 0.15, "F.SilkS", 0.12, name + "silk")
    s += (f'  (fp_circle (center {-a / 2:g} {ko_y0 + 0.2:g}) (end {-a / 2 + 0.12:g} {ko_y0 + 0.2:g})\n'
          f'    (stroke (width 0.12) (type solid)) (fill solid) (layer "F.SilkS") (tstamp {tid(name, "pin1")}))\n')
    # corpo, spina innestata, area libera
    s += rect(-c / 2, y_front, c / 2, y_rear, "F.Fab", 0.1, name + "body")
    s += rect(-(a + 3.06) / 2, y_rear, (a + 3.06) / 2, y_mated, "Dwgs.User", 0.1, name + "plug")
    s += rect(-g / 2, ko_y0, g / 2, ko_y1, "F.CrtYd", 0.05, name + "crt")
    # piazzole
    for i in range(n):
        x = -a / 2 + i * PITCH
        s += (f'  (pad "{i + 1}" smd rect (at {x:g} 0) (size {SIG[0]:g} {SIG[1]:g}) '
              f'(layers "F.Cu" "F.Paste" "F.Mask") (tstamp {tid(name, "pad", i + 1)}))\n')
    for k, (x, y, (w, h)) in enumerate([(-b / 2, 0, GBAR), (b / 2, 0, GBAR),
                                       (-hold_x, hold_y, HOLD), (hold_x, hold_y, HOLD)]):
        s += (f'  (pad "{n + 1}" smd rect (at {x:g} {y:g}) (size {w:g} {h:g}) '
              f'(layers "F.Cu" "F.Paste" "F.Mask") (tstamp {tid(name, "gnd", k)}))\n')
    s += ")\n"
    return name, s


def main():
    out = sys.argv[1]
    n = int(sys.argv[2]) if len(sys.argv) > 2 else 40
    assert n in (20, 30, 40, 50), n   # 20 pin: c'e' anche la variante "A20E" con impronta diversa
    os.makedirs(out, exist_ok=True)
    name, s = edp(n)
    open(os.path.join(out, name + ".kicad_mod"), "w").write(s)
    print("ok", name)


if __name__ == "__main__":
    main()
