# -*- coding: utf-8 -*-
"""Confronta la netlist dello schema (kicad-cli, formato kicadxml) con le piazzole del PCB e con il modello dati.

uso: python netlist_check.py --board A|B schema.xml board.kicad_pcb out.json      (senza --board: rev 2.0)
"""
import json
import os
import sys
import xml.etree.ElementTree as ET

import pcbnew

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import boards  # noqa: E402

D = boards.load()

xml, pcb, out = sys.argv[1:4]
root = ET.parse(xml).getroot()
sch = {}          # (ref, pin) -> net
sch_comp = {}
for c in root.find("components"):
    ref = c.get("ref")
    sch_comp[ref] = {"value": c.findtext("value"), "footprint": c.findtext("footprint"),
                     "fields": {f.get("name"): f.text for f in (c.find("fields") if c.find("fields") is not None else [])}}
for n in root.find("nets"):
    name = n.get("name")
    for node in n.findall("node"):
        sch[(node.get("ref"), node.get("pin"))] = None if name.startswith("unconnected-") else name

board = pcbnew.LoadBoard(pcb)
pcbmap = {}
pcb_comp = {}
for fp in board.GetFootprints():
    ref = fp.GetReference()
    pcb_comp[ref] = {"value": fp.GetValue(), "footprint": fp.GetFPIDAsString(), "path": fp.GetPath().AsString(),
                     "lcsc": boards.kc_get_field(fp, "LCSC")}
    for p in fp.Pads():
        if not p.GetNumber():
            continue
        k = (ref, p.GetNumber())
        n = p.GetNetname() or None
        if k in pcbmap and pcbmap[k] != n:
            pcbmap[k] = "CONFLITTO"
        else:
            pcbmap[k] = n

model = {}
for c in D.COMP:
    for p, n in c["pins"].items():
        model[(c["ref"], str(p))] = n

err = []
for k, n in sch.items():
    if k not in pcbmap:
        err.append(f"pin {k} dello schema senza piazzola nel PCB")
    elif pcbmap[k] != n:
        err.append(f"{k}: schema {n} / PCB {pcbmap[k]}")
for k, n in pcbmap.items():
    if n and k not in sch:
        err.append(f"piazzola {k} ({n}) assente nello schema")
for k, n in model.items():
    if sch.get(k) != n:
        err.append(f"{k}: modello {n} / schema {sch.get(k)}")
for ref, c in sch_comp.items():
    pc = pcb_comp.get(ref)
    if not pc:
        err.append(f"{ref} manca nel PCB")
        continue
    if pc["footprint"] != c["footprint"]:
        err.append(f"{ref}: footprint schema {c['footprint']} / PCB {pc['footprint']}")
    if pc["value"] != c["value"]:
        err.append(f"{ref}: valore schema {c['value']} / PCB {pc['value']}")
    if pc["path"] != "/" + D.sym_uuid(ref):
        err.append(f"{ref}: path PCB {pc['path']} non collegato al simbolo")
    if (c["fields"].get("LCSC") or "") != pc["lcsc"]:
        err.append(f"{ref}: LCSC schema {c['fields'].get('LCSC')} / PCB {pc['lcsc']}")
for ref in pcb_comp:
    if ref not in sch_comp:
        err.append(f"{ref} manca nello schema")

nets_sch = {n for n in sch.values() if n}
res = {"componenti_schema": len(sch_comp), "componenti_pcb": len(pcb_comp), "pin_schema": len(sch),
       "net_schema": len(nets_sch), "net_pcb": len({n for n in pcbmap.values() if n}),
       "errori": err}
json.dump(res, open(out, "w"), indent=1, ensure_ascii=False)
print(json.dumps({k: v for k, v in res.items() if k != "errori"}), "errori:", len(err))
for e in err[:30]:
    print(" ", e)
