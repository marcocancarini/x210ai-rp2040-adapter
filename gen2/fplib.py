# -*- coding: utf-8 -*-
"""Genera la libreria di footprint x210ai.pretty (formato KiCad 7).

uso: python3 fplib.py <rev13_pretty_dir> <kicad9_Package_SON.pretty> <out_dir>
"""
import os
import re
import sys
import uuid

KICAD7_FP = "/usr/share/kicad/footprints"
NS = uuid.UUID("6a3f1c2e-8b7d-4e0a-9c55-2f1e0d7b3a91")


def tid(*k):
    return str(uuid.uuid5(NS, "/".join(map(str, k))))


def line(x1, y1, x2, y2, layer, w, key):
    return (f'  (fp_line (start {x1:g} {y1:g}) (end {x2:g} {y2:g})\n'
            f'    (stroke (width {w:g}) (type solid)) (layer "{layer}") (tstamp {tid(key, x1, y1, x2, y2, layer)}))\n')


def rect(x1, y1, x2, y2, layer, w, key):
    return (line(x1, y1, x2, y1, layer, w, key) + line(x2, y1, x2, y2, layer, w, key) +
            line(x2, y2, x1, y2, layer, w, key) + line(x1, y2, x1, y1, layer, w, key))


def text(kind, txt, x, y, layer, size, key, hide=False, rot=0):
    r = f" {rot:g}" if rot else ""
    h = " hide" if hide else ""
    return (f'  (fp_text {kind} "{txt}" (at {x:g} {y:g}{r}) (layer "{layer}"){h}\n'
            f'      (effects (font (size {size:g} {size:g}) (thickness {size*0.15:.3f})))\n'
            f'    (tstamp {tid(key, kind, txt)})\n  )\n')


def header(name, descr, tags, attr="smd"):
    return (f'(footprint "{name}" (version 20221018) (generator pcbnew)\n  (layer "F.Cu")\n'
            f'  (descr "{descr}")\n  (tags "{tags}")\n  (attr {attr})\n')


def uson(src):
    """Winbond USON-8 3x2 (W25Q16JVUXIQ) - geometria dalla libreria KiCad 9, riscritta in formato 7"""
    t = open(src).read()
    pads = re.findall(r'\(pad "(\d*)" smd (\w+)\s*\(at ([-\d.]+) ([-\d.]+)\)\s*\(size ([\d.]+) ([\d.]+)\)'
                      r'(.*?)\(layers ([^)]*)\)', t, re.S)
    name = "Winbond_USON-8-1EP_3x2mm_P0.5mm_EP0.2x1.6mm"
    s = header(name, "Winbond USON-8 3x2 mm, passo 0,5 mm (W25Q16JVUXIQ). Geometria KiCad 9.0.7 "
               "(https://www.lcsc.com/datasheet/lcsc_datasheet_2205122030_Winbond-Elec-W25Q16JVUXIQ_C2843335.pdf)",
               "Winbond USON NoLead")
    s += text("reference", "REF**", 0, -1.95, "F.SilkS", 0.8, name)
    s += text("value", name, 0, 1.95, "F.Fab", 0.8, name)
    s += text("user", "${REFERENCE}", 0, 0, "F.Fab", 0.5, name + "u")
    s += line(-1.19, -1.135, 1.61, -1.135, "F.SilkS", 0.12, name)
    s += line(1.61, 1.135, -1.61, 1.135, "F.SilkS", 0.12, name)
    s += (f'  (fp_poly (pts (xy -1.48 -1.14) (xy -1.62 -1.33) (xy -1.34 -1.33) (xy -1.48 -1.14))\n'
          f'    (stroke (width 0.12) (type solid)) (fill solid) (layer "F.SilkS") (tstamp {tid(name, "poly")}))\n')
    # courtyard a croce come in KiCad 9
    cy = [(-2.13, -1.13, -1.75, -1.13), (-2.13, 1.13, -2.13, -1.13), (-1.75, -1.25, 1.75, -1.25),
          (-1.75, -1.13, -1.75, -1.25), (-1.75, 1.13, -2.13, 1.13), (-1.75, 1.25, -1.75, 1.13),
          (1.75, -1.25, 1.75, -1.13), (1.75, -1.13, 2.13, -1.13), (1.75, 1.13, 1.75, 1.25),
          (1.75, 1.25, -1.75, 1.25), (2.13, -1.13, 2.13, 1.13), (2.13, 1.13, 1.75, 1.13)]
    for a in cy:
        s += line(*a, "F.CrtYd", 0.05, name)
    s += rect(-1.5, -1.0, 1.5, 1.0, "F.Fab", 0.1, name + "fab")
    for num, shape, x, y, w, h, rest, layers in pads:
        layers = " ".join(f'"{l}"' for l in re.findall(r'"([^"]+)"', layers))
        extra = ""
        if shape == "roundrect":
            m = re.search(r'roundrect_rratio ([\d.]+)', t[t.find(f'(at {x} {y})'):][:400])
            extra += f" (roundrect_rratio {m.group(1) if m else 0.25})"
        if num == "9":
            extra += " (property pad_prop_heatsink) (zone_connect 2)"
        s += (f'  (pad "{num}" smd {shape} (at {x} {y}) (size {w} {h}) (layers {layers}){extra}'
              f' (tstamp {tid(name, "pad", num, x, y)}))\n')
    s += (f'  (model "${{KICAD7_3DMODEL_DIR}}/Package_SON.3dshapes/{name}.wrl"\n'
          f'    (offset (xyz 0 0 0)) (scale (xyz 1 1 1)) (rotate (xyz 0 0 0)))\n)\n')
    assert len(pads) == 10, len(pads)
    return name, s


def sot363_tight():
    import boards
    std = KICAD7_FP if os.path.isdir(KICAD7_FP) else boards.kicad_share("footprints")
    src = open(os.path.join(std, "Package_TO_SOT_SMD.pretty", "SOT-363_SC-70-6.kicad_mod")).read()
    s = src.replace('(footprint "SOT-363_SC-70-6"', '(footprint "SOT-363_SC-70-6_Tight"')
    s = s.replace('(descr "SOT-363, SC-70-6")',
                  '(descr "SOT-363, SC-70-6, courtyard ridotto a 2,9 x 2,5 mm per piazzamento fitto")')
    s = s.replace('(fp_text value "SOT-363_SC-70-6"', '(fp_text value "SOT-363_SC-70-6_Tight"')
    s, n = re.subn(r'\(start (-?)1\.6 (-?)1\.4\) \(end (-?)1\.6 (-?)1\.4\)',
                   lambda m: f'(start {m.group(1)}1.45 {m.group(2)}1.25) (end {m.group(3)}1.45 {m.group(4)}1.25)', s)
    assert n == 4, n
    return "SOT-363_SC-70-6_Tight", s


def usb_pads():
    name = "Pads_1x04_P1.60mm_Wire_Edge"
    s = header(name, "4 piazzole SMD per saldare i fili USB (5V, D-, D+, GND), passo 1,6 mm, al bordo scheda",
               "wire pads USB")
    s += text("reference", "REF**", 0, -3.8, "F.SilkS", 0.8, name, hide=True)
    s += text("value", name, 0, 3.8, "F.Fab", 0.8, name)
    labels = ["5V", "D-", "D+", "G"]
    for i, lab in enumerate(labels):
        y = (i - 1.5) * 1.6
        s += text("user", lab, 1.7, y, "F.SilkS", 0.7, name + lab)
        s += (f'  (pad "{i+1}" smd roundrect (at 0 {y:g}) (size 1.6 1.1) (layers "F.Cu" "F.Mask")'
              f' (roundrect_rratio 0.15) (tstamp {tid(name, "pad", i)}))\n')
    s += rect(-1.05, -3.2, 1.05, 3.2, "F.CrtYd", 0.05, name)
    s += ")\n"
    return name, s


def tp_pad():
    name = "TP_Pad_1.0x1.0mm"
    s = header(name, "test point quadrato 1,0 x 1,0 mm senza pasta", "test point pad")
    s += text("reference", "REF**", 0, -1.2, "F.SilkS", 0.8, name, hide=True)
    s += text("value", name, 0, 1.2, "F.Fab", 0.8, name)
    s += (f'  (pad "1" smd rect (at 0 0) (size 1 1) (layers "F.Cu" "F.Mask") (tstamp {tid(name, "pad")}))\n')
    s += rect(-0.7, -0.7, 0.7, 0.7, "F.CrtYd", 0.05, name)
    s += ")\n"
    return name, s


def main():
    rev13, son9, out = sys.argv[1:4]
    os.makedirs(out, exist_ok=True)
    for f in ("JAE_AA01B-S040VA1_KB_Receptacle.kicad_mod", "JAE_AA01B-P040_MB_Plug_Bottom.kicad_mod"):
        open(os.path.join(out, f), "w").write(open(os.path.join(rev13, f)).read())
    for name, s in (uson(os.path.join(son9, "Winbond_USON-8-1EP_3x2mm_P0.5mm_EP0.2x1.6mm.kicad_mod")),
                    sot363_tight(), usb_pads(), tp_pad()):
        open(os.path.join(out, name + ".kicad_mod"), "w").write(s)
    print("ok", sorted(os.listdir(out)))


if __name__ == "__main__":
    main()
