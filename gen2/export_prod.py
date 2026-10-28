# -*- coding: utf-8 -*-
"""File di produzione: Gerber + forature (zip), BOM e CPL per JLCPCB, BOM completa con MPN.

uso: python export_prod.py --board A|B board.kicad_pcb out_dir      (senza --board: rev 2.0)
Richiede kicad-cli nel PATH (oppure la variabile KICAD_CLI con il percorso completo).
"""
import csv
import os
import re
import shutil
import subprocess
import sys
import zipfile

import pcbnew

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import boards  # noqa: E402

D = boards.load()
BOARD = getattr(D, "BOARD", "2.0")
CLI = os.environ.get("KICAD_CLI", "kicad-cli")
PREFIX = f"x210ai_rev{D.REV}" + ("" if BOARD == "2.0" else f"_board{BOARD}")

pcb, out = sys.argv[1:3]
os.makedirs(out, exist_ok=True)
gdir = os.path.join(out, "gerber")
if os.path.exists(gdir):
    shutil.rmtree(gdir)
os.makedirs(gdir)
LAYERS = "F.Cu,In1.Cu,In2.Cu,B.Cu,F.Paste,B.Paste,F.SilkS,B.SilkS,F.Mask,B.Mask,Edge.Cuts"
subprocess.run([CLI, "pcb", "export", "gerbers", "--layers", LAYERS, "--subtract-soldermask",
                "-o", gdir + "/", pcb], check=True, capture_output=True)
subprocess.run([CLI, "pcb", "export", "drill", "--format", "excellon", "--drill-origin", "absolute",
                "--excellon-units", "mm", "--generate-map", "--map-format", "gerberx2", "-o", gdir + "/", pcb],
               check=True, capture_output=True)
zpath = os.path.join(out, f"{PREFIX}_gerber_jlcpcb.zip")
with zipfile.ZipFile(zpath, "w", zipfile.ZIP_DEFLATED) as z:
    for f in sorted(os.listdir(gdir)):
        z.write(os.path.join(gdir, f), f)

# ---- correzioni di rotazione JLCPCB (tabella KiBot / JLCKicadTools) e convenzione lato bottom
ROT_DB = [(r"^QFN-", 270), (r"^SOT-23", 180), (r"^SOT-363", 180), (r"^Winbond_USON-8", 270)]


def jlc_rotation(fp):
    name = fp.GetFPID().GetLibItemName().wx_str() if hasattr(fp.GetFPID().GetLibItemName(), "wx_str") \
        else str(fp.GetFPID().GetLibItemName())
    corr = 0
    for rx, a in ROT_DB:
        if re.search(rx, name):
            corr = a
            break
    rot = fp.GetOrientationDegrees()
    if fp.IsFlipped():
        jlc = (180 - rot + corr) % 360       # JLCPCB: lato bottom visto da sotto (mirror_bottom)
    else:
        jlc = (rot + corr) % 360
    return name, rot, corr, round(jlc, 1) % 360


board = pcbnew.LoadBoard(pcb)
rows = []
for fp in board.GetFootprints():
    ref = fp.GetReference()
    c = D.BY_REF[ref]
    pos = fp.GetPosition()
    name, rot, corr, jlc = jlc_rotation(fp)
    value = c["value"]
    lcsc, mpn, mfr = D.PARTS.get(value, ("", "", ""))
    if ref == "J1" and hasattr(D, "J1_PARTS"):        # Board B: JLCPCB monta solo il ricettacolo (sopra)
        _, value, lcsc, mpn, mfr, _ = D.J1_PARTS[0]
    rows.append(dict(ref=ref, value=value, fp=name, x=pcbnew.ToMM(pos.x), y=-pcbnew.ToMM(pos.y),
                     layer="Bottom" if fp.IsFlipped() else "Top", rot=rot, corr=corr, jlc=jlc,
                     lcsc=lcsc, mpn=mpn, mfr=mfr, desc=c["desc"]))
rows.sort(key=lambda r: (r["ref"][0], int(re.sub(r"\D", "", r["ref"]) or 0)))


def assembled(r, with_j1):
    if r["ref"] in D.DNP or r["ref"] in D.NOT_ASSEMBLED:
        return False
    if r["ref"] == "J1" and not with_j1:
        return False
    return True


def write_set(suffix, with_j1):
    sel = [r for r in rows if assembled(r, with_j1)]
    groups = {}
    for r in sel:
        groups.setdefault((r["value"], r["fp"], r["lcsc"]), []).append(r["ref"])
    missing = [r["ref"] for r in sel if not r["lcsc"]]
    assert not missing, f"codice LCSC mancante per {missing}"
    with open(os.path.join(out, f"{PREFIX}_bom_jlcpcb_{suffix}.csv"), "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["Comment", "Designator", "Footprint", "LCSC Part #"])
        for (v, fpn, l), refs in groups.items():
            w.writerow([v, ",".join(refs), fpn, l])
    with open(os.path.join(out, f"{PREFIX}_cpl_jlcpcb_{suffix}.csv"), "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["Designator", "Mid X", "Mid Y", "Layer", "Rotation"])
        for r in sel:
            w.writerow([r["ref"], f"{r['x']:.4f}mm", f"{r['y']:.4f}mm", r["layer"], f"{r['jlc']:g}"])
    return len(sel)


n1 = write_set("solo_bottom", False)    # JLCPCB Economic: un lato solo, le parti sopra si saldano a mano
n2 = write_set("bottom_e_top", True)    # JLCPCB Standard: entrambi i lati
with open(os.path.join(out, f"{PREFIX}_cpl_rotazioni_applicate.csv"), "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["Designator", "Package", "Lato", "Rot KiCad", "Correzione", "Rot JLCPCB"])
    for r in rows:
        if assembled(r, True):
            w.writerow([r["ref"], r["fp"], r["layer"], f"{r['rot']:g}", r["corr"], f"{r['jlc']:g}"])
with open(os.path.join(out, f"{PREFIX}_bom_completa_mpn.csv"), "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["Designator", "Value", "Manufacturer", "MPN", "LCSC", "Footprint", "Side", "Assembly", "Note"])
    for r in rows:
        how = "DNP (saldare a mano)" if r["ref"] in D.DNP else ("no (solo rame)" if r["ref"] in D.NOT_ASSEMBLED
                                                                 else "si")
        w.writerow([r["ref"], r["value"], r["mfr"], r["mpn"], r["lcsc"], r["fp"], r["layer"], how, r["desc"]])
        if r["ref"] == "J1" and hasattr(D, "J1_PARTS"):
            s, v, l, m, mf, h = D.J1_PARTS[1]
            w.writerow(["J1", v, mf, m, l, r["fp"], s, h, r["desc"]])
print(f"gerber: {zpath} ({len(os.listdir(gdir))} file); BOM/CPL: {n1} componenti (solo bottom), "
      f"{n2} (bottom + J1)")
