# -*- coding: utf-8 -*-
"""DRC con pcbnew (KiCad 7-10): python drc.py board.kicad_pcb report.rpt [N] [--nofill]
In alternativa: kicad-cli pcb drc --format json --output drc.json board.kicad_pcb"""
import collections
import os
import re
import sys

import pcbnew

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import boards  # noqa: E402

for _v in ("10", "9", "8", "7"):
    os.environ.setdefault(f"KICAD{_v}_FOOTPRINT_DIR", boards.kicad_share("footprints"))
pcb, rpt = sys.argv[1], sys.argv[2]
n = int(sys.argv[3]) if len(sys.argv) > 3 and sys.argv[3].isdigit() else 25
b = pcbnew.LoadBoard(pcb)
if "--nofill" not in sys.argv:
    pcbnew.ZONE_FILLER(b).Fill(b.Zones())
pcbnew.WriteDRCReport(b, rpt, pcbnew.EDA_UNITS_MILLIMETRES, True)
t = open(rpt).read()
for l in t.splitlines():
    if l.startswith("**"):
        print(l)
types = collections.Counter(re.findall(r"^\[(\w+)\]", t, re.M))
print(dict(types))
blocks = re.split(r"\n(?=\[)", t)
shown = 0
for bl in blocks:
    if bl.startswith("["):
        if shown < n:
            print(bl.strip()[:400])
            print("-")
        shown += 1
