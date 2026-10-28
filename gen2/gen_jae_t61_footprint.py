# -*- coding: utf-8 -*-
"""Converte in KiCad (formato 7) il footprint WM6787_AA01B del progetto T61 di thedalles77 (T61.brd, Eagle 9),
identico per quote e piedinatura: pad 1-40 (P$1-P$40 in Eagle) e TAB1-TAB4 (linguette, a GND nella T61).

uso: python3 gen_jae_t61_footprint.py riferimenti/T61/T61.brd gen2/lib/x210ai.pretty

Stessa origine del package Eagle (non centrata: fila pin a x -4.7..4.8); y Eagle verso l'alto -> y KiCad
verso il basso. Il risultato e' JAE_AA01B-S040VA1_T61.kicad_mod.
"""
import os
import sys
import xml.etree.ElementTree as ET

from fplib import header, line, rect, text, tid

PKG = "WM6787_AA01B"
NAME = "JAE_AA01B-S040VA1_T61"
SILK, DOCU = "21", "51"        # tPlace, tDocu


def f(v):
    return f"{round(float(v), 4):g}"


def package(brd):
    for p in ET.parse(brd).getroot().iter("package"):
        if p.get("name") == PKG:
            return p
    raise SystemExit(f"{PKG} non trovato in {brd}")


def pads(p):
    """[(nome KiCad, x, y, larghezza, altezza)] con y gia' invertita e rotazione applicata"""
    out = []
    for s in p.iter("smd"):
        assert s.get("layer") == "1", s.attrib            # tutto sul lato Top
        dx, dy = float(s.get("dx")), float(s.get("dy"))
        rot = s.get("rot", "R0")
        assert rot in ("R0", "R90", "R180", "R270"), rot
        w, h = (dy, dx) if rot in ("R90", "R270") else (dx, dy)
        name = s.get("name").replace("P$", "")
        out.append((name, float(s.get("x")), -float(s.get("y")), w, h))
    return out


def main():
    brd, lib = sys.argv[1:3]
    p = package(brd)
    pl = pads(p)
    names = [n for n, *_ in pl]
    assert sorted(names) == sorted([str(i) for i in range(1, 41)] + [f"TAB{i}" for i in range(1, 5)]), names

    s = header(NAME, "JAE AA01B-S040VA1 (connettore tastiera della scheda madre X200/X201/X210Ai/T61), 2x20 "
                     "P0.5mm. Copia esatta del package WM6787_AA01B di thedalles77 (T61.brd, progetto T61 "
                     "Teensy 4.0): pad 1-40 = P$1-P$40, TAB1-TAB4 = linguette (GND).",
               "ThinkPad keyboard connector AA01B 40 pin 0.5mm T61 thedalles77")
    s += text("reference", "REF**", 0, -4.4, "F.SilkS", 0.8, NAME)
    s += text("value", NAME, 0, 4.3, "F.Fab", 0.8, NAME)
    s += text("user", "${REFERENCE}", 0, 0, "F.Fab", 0.6, NAME + "u")
    for t in p.iter("text"):
        if t.get("layer") == SILK:                         # numeri dei pin d'angolo: 1, 39, 2, 40
            s += text("user", t.text, float(t.get("x")) + 0.3, -float(t.get("y")) - 0.3, "F.SilkS",
                      float(t.get("size")), NAME + "t" + t.text)
    for w in p.iter("wire"):
        if w.get("layer") == DOCU:
            s += line(float(w.get("x1")), -float(w.get("y1")), float(w.get("x2")), -float(w.get("y2")),
                      "F.Fab", 0.1, NAME + "fab")
    x0 = min(x - w / 2 for _, x, _, w, _ in pl) - 0.25
    x1 = max(x + w / 2 for _, x, _, w, _ in pl) + 0.25
    y0 = min(y - h / 2 for _, _, y, _, h in pl) - 0.25
    y1 = max(y + h / 2 for _, _, y, _, h in pl) + 0.25
    s += rect(round(x0, 2), round(y0, 2), round(x1, 2), round(y1, 2), "F.CrtYd", 0.05, NAME + "crt")
    for n, x, y, w, h in pl:
        s += (f'  (pad "{n}" smd rect (at {f(x)} {f(y)}) (size {f(w)} {f(h)}) (layers "F.Cu" "F.Paste" "F.Mask")'
              f' (tstamp {tid(NAME, "pad", n)}))\n')
    s += ")\n"
    open(os.path.join(lib, NAME + ".kicad_mod"), "w").write(s)
    print("ok", NAME, len(pl), "pad")


if __name__ == "__main__":
    main()
