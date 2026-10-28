# -*- coding: utf-8 -*-
"""Rilegge Gerber, forature e CPL: contorno, strati, fori e baricentri sulle aperture di pasta (lato giusto).

uso: python3 gerber_check2.py <cartella gerber> <cpl.csv>
"""
import csv
import glob
import os
import sys

from gerbonara import ExcellonFile, GerberFile
from gerbonara.utils import MM

d, cpl = sys.argv[1], sys.argv[2]


def load(pat):
    f = glob.glob(os.path.join(d, pat))
    return GerberFile.open(f[0]) if f else None


edge = load("*Edge_Cuts*")
(ex0, ey0), (ex1, ey1) = edge.bounding_box(unit=MM)
print("contorno: %.2f x %.2f mm (incluso lo spessore della linea)" % (ex1 - ex0, ey1 - ey0))
cu = sorted(os.path.basename(c) for c in glob.glob(os.path.join(d, "*_Cu.*")))
print("strati di rame: %d %s" % (len(cu), cu))
nh, sizes = 0, {}
for f in glob.glob(os.path.join(d, "*.drl")):
    ex = ExcellonFile.open(f)
    for o in ex.drills():
        nh += 1
        dia = round(o.unit.convert_to(MM, o.tool.diameter), 3)
        sizes[dia] = sizes.get(dia, 0) + 1
print("fori: %d, per diametro (mm): %s" % (nh, dict(sorted(sizes.items()))))
paste = {}
for side, pat in (("Top", "*F_Paste*"), ("Bottom", "*B_Paste*")):
    g = load(pat)
    pads = []
    for o in g.objects if g else []:
        (a, b) = o.bounding_box(unit=MM)
        pads.append((a[0], a[1], b[0], b[1]))
    paste[side] = pads
    print(f"aperture di pasta {side}: {len(pads)}")
WIN = {"J1": (7.5, 3.5), "U1": (4.2, 4.2), "U2": (2.2, 1.4), "Y1": (1.8, 1.5)}
bad = []
rows = list(csv.DictReader(open(cpl)))
for r in rows:
    ref = r["Designator"]
    x = float(r["Mid X"].replace("mm", ""))
    y = float(r["Mid Y"].replace("mm", ""))
    pads = paste[r["Layer"]]
    wx, wy = WIN.get(ref, (1.6, 1.6))
    sel = [p for p in pads if abs((p[0] + p[2]) / 2 - x) <= wx and abs((p[1] + p[3]) / 2 - y) <= wy]
    if ref not in WIN:
        sel.sort(key=lambda p: ((p[0] + p[2]) / 2 - x) ** 2 + ((p[1] + p[3]) / 2 - y) ** 2)
        sel = sel[:{"Q": 6, "U": 3}.get(ref[0], 2)]
    if not sel:
        bad.append((ref, "nessuna apertura"))
        continue
    cx = (min(p[0] for p in sel) + max(p[2] for p in sel)) / 2
    cy = (min(p[1] for p in sel) + max(p[3] for p in sel)) / 2
    err = ((cx - x) ** 2 + (cy - y) ** 2) ** 0.5
    if err > 0.2:
        bad.append((ref, round(err, 3)))
print(f"baricentri CPL controllati: {len(rows)}, fuori dalle piazzole: {bad if bad else 'nessuno'}")
