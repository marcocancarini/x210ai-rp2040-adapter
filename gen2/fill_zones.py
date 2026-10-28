# -*- coding: utf-8 -*-
"""Aggiunge le colate di massa sugli strati indicati e riempie tutte le zone.

uso: python fill_zones.py --board A|B in.kicad_pcb out.kicad_pcb [--pour F,B,In2]   (senza --board: rev 2.0)
"""
import os
import sys

import pcbnew

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import build_pcb as BP  # noqa: E402

pcb_in, pcb_out = sys.argv[1:3]
pour = []
if "--pour" in sys.argv:
    pour = sys.argv[sys.argv.index("--pour") + 1].split(",")
LAY = {"F": pcbnew.F_Cu, "B": pcbnew.B_Cu, "In2": pcbnew.In2_Cu}
board = pcbnew.LoadBoard(pcb_in)
have = {(z.GetLayer(), z.GetNetname()) for z in board.Zones()}
for p in pour:
    if (LAY[p], "GND") not in have:
        BP.add_zone(board, LAY[p], "GND", 0.0, 0, "GND_" + p)
pcbnew.ZONE_FILLER(board).Fill(board.Zones())
pcbnew.SaveBoard(pcb_out, board)
for z in board.Zones():
    print(board.GetLayerName(z.GetLayer()), z.GetNetname(), "area riempita mm2:",
          round(z.GetFilledArea() / 1e12, 1) if hasattr(z, "GetFilledArea") else "?")
