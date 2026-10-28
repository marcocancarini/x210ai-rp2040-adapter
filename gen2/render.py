# -*- coding: utf-8 -*-
"""Render PNG dei lati della scheda: python3 render.py board.kicad_pcb prefisso scala [top,bottom,inner,all]"""
import os
import subprocess
import sys

import cairosvg

pcb, prefix = sys.argv[1], sys.argv[2]
scale = float(sys.argv[3]) if len(sys.argv) > 3 else 20
which = (sys.argv[4] if len(sys.argv) > 4 else "top,bottom").split(",")
SETS = {
    "top": ("F.Cu,F.Paste,F.SilkS,F.Mask,Edge.Cuts,F.Fab", False),
    "bottom": ("B.Cu,B.Paste,B.SilkS,B.Mask,Edge.Cuts,B.Fab", True),
    "inner": ("In1.Cu,In2.Cu,Edge.Cuts", False),
    "in2": ("In2.Cu,Edge.Cuts", False),
    "all": ("F.Cu,In2.Cu,B.Cu,Edge.Cuts", False),
}
for w in which:
    layers, mirror = SETS[w]
    svg = f"{prefix}_{w}.svg"
    cmd = ["kicad-cli", "pcb", "export", "svg", "--layers", layers, "--page-size-mode", "2",
           "--exclude-drawing-sheet", "-o", svg, pcb]
    if mirror:
        cmd.insert(4, "--mirror")
    subprocess.run(cmd, check=True, capture_output=True)
    import re
    t = open(svg).read()
    m = re.search(r'width="([\d.]+)mm" height="([\d.]+)mm"', t)
    wmm = float(m.group(1)) if m else 40
    cairosvg.svg2png(url=svg, write_to=f"{prefix}_{w}.png", output_width=int(wmm * scale), background_color="white")
    print(f"{prefix}_{w}.png")
