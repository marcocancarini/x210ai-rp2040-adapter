# -*- coding: utf-8 -*-
"""Genera JAE_AA01_sandwich: ricettacolo AA01B-S040VA1 sopra + spina AA01B-P040VA1 sotto in un'unica impronta.

uso: python3 gen_sandwich_footprint.py <x210ai.pretty>

Parte dalle due impronte gia' nella libreria (le stesse della rev 2.0, dove J1 e J2 erano piazzati
concentrici): il ricettacolo resta com'e' (pad 1-41, F.Cu); la spina viene ribaltata sopra/sotto come faceva
build_pcb.py (Flip con aFlipLeftRight=False: y -> -y) e i suoi pad diventano 101-140 su B.Cu.
Pad 100+n della spina = pin n di BTB_R_CONN1 sulla scheda madre.
"""
import os
import re
import sys

from fplib import header, text, tid

REC = "JAE_AA01B-S040VA1_T61"     # da gen_jae_t61_footprint.py: identico al progetto T61 (pad 1-40, TAB1-4)
PLUG = "JAE_AA01B-P040_MB_Plug_Bottom"
NAME = "JAE_AA01_sandwich"
STACK = "pila: spina 1,5 + PCB 0,4 + ricettacolo 1,5 = 3,4 mm (+ spina tastiera)"

PAD = re.compile(r'\(pad "(\w+)" smd (\w+) \(at ([-\d.]+) ([-\d.]+)\) \(size ([\d.]+) ([\d.]+)\)')
LINE = re.compile(r'\(fp_line \(start ([-\d.]+) ([-\d.]+)\) \(end ([-\d.]+) ([-\d.]+)\)\s*'
                  r'\(stroke \(width ([\d.]+)\) \(type \w+\)\) \(layer "([^"]+)"\)')
CIRCLE = re.compile(r'\(fp_circle \(center ([-\d.]+) ([-\d.]+)\) \(end ([-\d.]+) ([-\d.]+)\)\s*'
                    r'\(stroke \(width ([\d.]+)\) \(type \w+\)\) \(fill (\w+)\) \(layer "([^"]+)"\)')


def f(v):
    return f"{round(float(v), 4):g}"


def items(t, flip, key):
    """pad, linee e cerchi di un'impronta; con flip passa al lato B (y -> -y, F.* -> B.*, pad 100+n)"""
    sy = -1 if flip else 1
    lay = (lambda s: s.replace("F.", "B.")) if flip else (lambda s: s)
    out = []
    for x1, y1, x2, y2, w, layer in LINE.findall(t):
        out.append(f'  (fp_line (start {f(x1)} {f(sy * float(y1))}) (end {f(x2)} {f(sy * float(y2))})\n'
                   f'    (stroke (width {w}) (type solid)) (layer "{lay(layer)}") '
                   f'(tstamp {tid(NAME, key, "l", x1, y1, x2, y2, layer)}))\n')
    for cx, cy, ex, ey, w, fill, layer in CIRCLE.findall(t):
        out.append(f'  (fp_circle (center {f(cx)} {f(sy * float(cy))}) (end {f(ex)} {f(sy * float(ey))})\n'
                   f'    (stroke (width {w}) (type solid)) (fill {fill}) (layer "{lay(layer)}") '
                   f'(tstamp {tid(NAME, key, "c", cx, cy)}))\n')
    pads = PAD.findall(t)
    for num, shape, x, y, w, h in pads:
        n = int(num) + 100 if flip else num
        layers = '"B.Cu" "B.Paste" "B.Mask"' if flip else '"F.Cu" "F.Paste" "F.Mask"'
        out.append(f'  (pad "{n}" smd {shape} (at {f(x)} {f(sy * float(y))}) (size {w} {h}) (layers {layers})'
                   f' (tstamp {tid(NAME, key, "p", num, x, y)}))\n')
    return out, pads


def main():
    lib = sys.argv[1]
    rec = open(os.path.join(lib, REC + ".kicad_mod")).read()
    plug = open(os.path.join(lib, PLUG + ".kicad_mod")).read()
    top, rp = items(rec, False, "rec")
    bot, pp = items(plug, True, "plug")
    assert len(rp) == 44 and len(pp) == 40, (len(rp), len(pp))
    # la spina sul flat della tastiera ha 2x22 piedini: i 4 d'angolo non hanno contatto nel ricettacolo da 40
    # (thedalles77, T61_Teensy4p0.pdf p. 5). Pad "MP" senza net, cosi' ci sta sia la spina 40 sia la 44.
    xs = sorted({float(x) for _, _, x, _, _, _ in pp})
    for num, shape, x, y, w, h in pp:
        if int(num) in (1, 2, 39, 40):
            xe = float(x) + (-0.5 if int(num) <= 2 else 0.5)
            assert xe < xs[0] or xe > xs[-1], xe
            bot.append(f'  (pad "MP" smd {shape} (at {f(xe)} {f(-float(y))}) (size {w} {h}) '
                       f'(layers "B.Cu" "B.Paste" "B.Mask") (tstamp {tid(NAME, "corner", num)}))\n')
    # i pin n di ricettacolo e spina devono stare sulla stessa colonna (x) e dallo stesso lato (segno di y)
    rx = {int(n): (float(x), float(y)) for n, _, x, y, _, _ in rp if n.isdigit()}
    for n, _, x, y, _, _ in pp:
        n, x, y = int(n), float(x), -float(y)
        assert abs(rx[n][0] - x) < 0.01 and (rx[n][1] > 0) == (y > 0), (n, rx[n], (x, y))

    s = header(NAME, "JAE AA01B-S040VA1 (sopra, riceve la spina della tastiera) + AA01B-P040VA1 (sotto, si innesta "
                     "in BTB_R_CONN1) concentrici. Pad 1-40 e TAB1-TAB4 ricettacolo (= WM6787_AA01B di thedalles77, "
                     "T61.brd), pad 101-140 spina (100+n = pin n), pad MP = 4 piedini d'angolo della spina 2x22 "
                     "del flat. Distanza tra le file della spina da VERIFICARE con il calibro. " + STACK,
               "ThinkPad X210Ai keyboard AA01B sandwich stacked 0.5mm")
    s += text("reference", "REF**", 0, -4.4, "F.SilkS", 0.8, NAME)
    s += text("value", NAME, 0, 4.3, "F.Fab", 0.8, NAME)
    s += text("user", "${REFERENCE}", 0, 0, "F.Fab", 0.6, NAME + "u")
    s += "".join(re.findall(r'  \(fp_text user "(?:1|2|39|40)".*?\n  \)\n', rec, re.S))   # numeri come nella T61
    s += text("user", "1", -3.9, -4.0, "B.SilkS", 1.0, NAME + "1B")
    s += text("user", STACK, 0, 5.2, "Cmts.User", 0.5, NAME + "stack")
    s += (f'  (fp_circle (center -5 -3.4) (end -4.85 -3.4)\n'
          f'    (stroke (width 0.15) (type solid)) (fill solid) (layer "B.SilkS") (tstamp {tid(NAME, "pin1B")}))\n')
    s += "".join(top) + "".join(bot) + ")\n"
    open(os.path.join(lib, NAME + ".kicad_mod"), "w").write(s)
    print("ok", NAME, len(rp), "pad sopra,", len(pp) + 4, "pad sotto (4 MP)")


if __name__ == "__main__":
    main()
