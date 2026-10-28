# -*- coding: utf-8 -*-
"""Costruisce <progetto>.kicad_pcb dal modello dati della scheda scelta con l'API pcbnew (KiCad 7-10):
piazzamento, contorno, piano GND su In1, pre-instradamento (quarzo, fan-out QFN e masse).

uso:  python build_pcb.py --board A|B <out_dir>
      python build_pcb.py --board A|B --dsn <board.kicad_pcb> <out.dsn> [--in1-signal] [--protect NET1,NET2]
      (senza --board: rev 2.0)
"""
import json
import math
import os
import re
import shutil
import sys

import pcbnew
from shapely.geometry import Polygon

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import boards                # noqa: E402
import preroute as PR        # noqa: E402
import project               # noqa: E402

D = boards.load()
BOARD = getattr(D, "BOARD", "2.0")
HERE = os.path.dirname(os.path.abspath(__file__))
FANOUT_QFN = True
LIB = os.path.join(HERE, "lib", "x210ai.pretty")
MM = pcbnew.FromMM
VIA = getattr(D, "VIA", (0.4, 0.2))
PR.VIA_D, PR.VIA_DRILL = VIA

COMMENTS = {
    "2.0": ("4 strati: F.Cu / In1 GND / In2 segnali / B.Cu - spessore 0,8 mm (JLCPCB) o 0,6-0,4 mm (PCBWay)",
            "J1 sopra (tastiera), J2 sotto (BTB_R_CONN1 scheda madre), RP2040 sotto"),
    "A": ("4 strati: F.Cu / In1 GND / In2 segnali / B.Cu - 0,8 mm JLCPCB, ENIG, via 0,4/0,2",
          "RP2040 e componenti sotto; J4 (eDP verso la Board B) sopra"),
    "B": ("4 strati: F.Cu / In1 GND / In2 segnali / B.Cu - 0,4 mm PCBWay avanzato, ENIG, via 0,3/0,15",
          "J1 sandwich: ricettacolo sopra, spina sotto in BTB_R_CONN1; J4 eDP sopra; Q2/Q3 sotto"),
}
# scritte in serigrafia: (testo, x, y, lato, altezza) in coordinate del modello dati
SILK = {
    "2.0": [(f"X210Ai ISO/JIS rev {D.REV}", -13.2, -4.15, "F", 0.8), ("TASTIERA", -11.0, 4.6, "F", 0.7),
            ("BOOT", -25.4, -0.45, "F", 0.6), ("RST", -21.8, -0.45, "F", 0.6),
            ("CLK DIO GND 3V3", -23.3, -2.95, "F", 0.45)],
    "A": [(f"X210Ai Board A rev {D.REV}", 9.0, -11.3, "F", 0.8), ("BOOT", -16.4, -6.95, "F", 0.6),
          ("RST", -12.8, -6.95, "F", 0.6), ("CLK DIO GND 3V3", -14.3, -9.45, "F", 0.45),
          ("eDP -> Board B", 0.0, 11.4, "F", 0.7)],
    "B": [(f"X210Ai Board B rev {D.REV}", -27.0, 0.0, "B", 0.8), ("eDP -> Board A", -24.0, -3.6, "F", 0.6)],
}


def A(x, y):
    """coordinate relative (mm) -> assolute"""
    return (D.ORIGIN[0] + x, D.ORIGIN[1] + y)


def V(x, y):
    ax, ay = A(x, y)
    return pcbnew.VECTOR2I(MM(ax), MM(ay))


def load_fp(libid):
    lib, name = libid.split(":")
    path = LIB if lib == "x210ai" else os.path.join(boards.kicad_share("footprints"), lib + ".pretty")
    fp = pcbnew.FootprintLoad(path, name)
    assert fp is not None, f"impronta {libid} non trovata in {path}"
    fp.SetFPID(pcbnew.LIB_ID(lib, name))
    return fp


def outline_poly():
    r = D.CORNER_R
    pts = []
    corners = [(D.X1 - r, D.Y0 + r, -90), (D.X1 - r, D.Y1 - r, 0), (D.X0 + r, D.Y1 - r, 90), (D.X0 + r, D.Y0 + r, 180)]
    for cx, cy, a0 in corners:
        for i in range(9):
            a = math.radians(a0 + 90 * i / 8)
            pts.append(A(cx + r * math.cos(a), cy + r * math.sin(a)))
    return Polygon(pts)


def add_outline(board):
    r = D.CORNER_R
    segs = [((D.X0 + r, D.Y0), (D.X1 - r, D.Y0)), ((D.X1, D.Y0 + r), (D.X1, D.Y1 - r)),
            ((D.X1 - r, D.Y1), (D.X0 + r, D.Y1)), ((D.X0, D.Y1 - r), (D.X0, D.Y0 + r))]
    for a, b in segs:
        s = pcbnew.PCB_SHAPE(board)
        s.SetShape(pcbnew.SHAPE_T_SEGMENT)
        s.SetStart(V(*a))
        s.SetEnd(V(*b))
        s.SetLayer(pcbnew.Edge_Cuts)
        s.SetWidth(MM(0.05))
        board.Add(s)
    # archi: centro, punto iniziale, angolo
    arcs = [((D.X1 - r, D.Y0 + r), (D.X1 - r, D.Y0)), ((D.X1 - r, D.Y1 - r), (D.X1, D.Y1 - r)),
            ((D.X0 + r, D.Y1 - r), (D.X0 + r, D.Y1)), ((D.X0 + r, D.Y0 + r), (D.X0, D.Y0 + r))]
    for c, st in arcs:
        s = pcbnew.PCB_SHAPE(board)
        s.SetShape(pcbnew.SHAPE_T_ARC)
        s.SetCenter(V(*c))
        s.SetStart(V(*st))
        s.SetArcAngleAndEnd(pcbnew.EDA_ANGLE(90, pcbnew.DEGREES_T), True)
        s.SetLayer(pcbnew.Edge_Cuts)
        s.SetWidth(MM(0.05))
        board.Add(s)


def add_zone(board, layer, net="GND", inset=0.0, priority=0, name=""):
    z = pcbnew.ZONE(board)
    z.SetLayer(layer)
    z.SetNet(board.FindNet(net))
    ol = z.Outline()
    ol.NewOutline()
    for x, y in ((D.X0 + inset, D.Y0 + inset), (D.X1 - inset, D.Y0 + inset),
                 (D.X1 - inset, D.Y1 - inset), (D.X0 + inset, D.Y1 - inset)):
        ol.Append(MM(A(x, y)[0]), MM(A(x, y)[1]))
    z.SetMinThickness(MM(0.12))
    z.SetLocalClearance(MM(0.15))
    z.SetPadConnection(pcbnew.ZONE_CONNECTION_THERMAL)
    z.SetThermalReliefGap(MM(0.2))
    z.SetThermalReliefSpokeWidth(MM(0.2))
    z.SetIslandRemovalMode(pcbnew.ISLAND_REMOVAL_MODE_ALWAYS)
    z.SetAssignedPriority(priority)
    if name:
        z.SetZoneName(name)
    board.Add(z)
    return z


def pad_xy(board, ref, num):
    fp = board.FindFootprintByReference(ref)
    for p in fp.Pads():
        if p.GetNumber() == str(num) and p.GetAttribute() != pcbnew.PAD_ATTRIB_PTH:
            c = p.GetPosition()
            return (pcbnew.ToMM(c.x), pcbnew.ToMM(c.y))
    raise KeyError((ref, num))


def special_gnd(board):
    """masse di J1/J2 collegate con via dedicate (coordinate relative)"""
    vias = [(2.8, -3.85), (3.55, 0.65)]
    for x, y in vias:
        PR.add_via(board, "GND", *A(x, y))
    v31 = A(2.8, -3.85)
    v34 = A(3.55, 0.65)
    PR.add_track(board, "GND", [pad_xy(board, "J1", 31), v31], pcbnew.F_Cu, 0.2)
    PR.add_track(board, "GND", [pad_xy(board, "J2", 31), v31], pcbnew.B_Cu, 0.2)
    for ref, lay in (("J1", pcbnew.F_Cu), ("J2", pcbnew.B_Cu)):
        for n in (34, 36):
            x, y = pad_xy(board, ref, n)
            # dal bordo interno della piazzola verso la via centrale
            fp = board.FindFootprintByReference(ref)
            pad = [p for p in fp.Pads() if p.GetNumber() == str(n)][0]
            bb = pad.GetBoundingBox()
            yin = pcbnew.ToMM(bb.GetTop())
            PR.add_track(board, "GND", [(x, y), (x, yin), v34], lay, 0.2)
    # linguette di J1 (pad 41): una via 1 mm verso l'esterno
    fp = board.FindFootprintByReference("J1")
    for p in fp.Pads():
        if p.GetNumber() != "41":
            continue
        c = p.GetPosition()
        x, y = pcbnew.ToMM(c.x), pcbnew.ToMM(c.y)
        dx = 1.0 if x > D.ORIGIN[0] else -1.0
        PR.add_via(board, "GND", x + dx, y)
        PR.add_track(board, "GND", [(x, y), (x + dx, y)], pcbnew.F_Cu, 0.3)


def crystal_preroute(board):
    w = 0.15
    B = pcbnew.B_Cu
    xi, xo = pad_xy(board, "U1", 20), pad_xy(board, "U1", 21)
    y1, y3 = pad_xy(board, "Y1", 1), pad_xy(board, "Y1", 3)
    c13, c14 = pad_xy(board, "C13", 1), pad_xy(board, "C14", 1)
    r3a, r3b = pad_xy(board, "R3", 1), pad_xy(board, "R3", 2)
    tip = xi[0] + 0.5625
    PR.add_track(board, "XIN", [xi, (tip, xi[1]), (tip + 0.7, xi[1] - 0.7), y1], B, w)
    PR.add_track(board, "XIN", [c13, (c13[0] + 0.33, c13[1] + 0.4), y1], B, w)
    lane = xo[0] + 0.7125
    PR.add_track(board, "XOUT", [xo, (lane, xo[1]), (lane, r3a[1]), r3a], B, w)
    PR.add_track(board, "XOUT_R", [r3b, c14], B, w)
    PR.add_track(board, "XOUT_R", [c14, (c14[0], y3[1] + 0.6), y3], B, w)


def testen_to_ep(board):
    """TESTEN (pin 19) a massa con una pista diretta verso il pad centrale"""
    fp = board.FindFootprintByReference("U1")
    p19 = [p for p in fp.Pads() if p.GetNumber() == "19"][0]
    c = p19.GetPosition()
    cx, cy = pcbnew.ToMM(c.x), pcbnew.ToMM(c.y)
    o = fp.GetPosition()
    ox, oy = pcbnew.ToMM(o.x), pcbnew.ToMM(o.y)
    dx, dy = ox - cx, oy - cy
    d = math.hypot(dx, dy)
    # il pin e' sul lato: direzione perpendicolare al lato verso il centro
    if abs(dx) > abs(dy):
        end = (cx + math.copysign(3.4375 - 1.4, dx), cy)
    else:
        end = (cx, cy + math.copysign(3.4375 - 1.4, dy))
    PR.add_track(board, "GND", [(cx, cy), end], pcbnew.B_Cu, 0.15)
    return d


def build(out_dir, uuids=None):
    os.makedirs(out_dir, exist_ok=True)
    name = boards.project_name(D)
    pcb_path = os.path.join(out_dir, name + ".kicad_pcb")
    board = pcbnew.NewBoard(pcb_path)
    board.SetCopperLayerCount(4)
    ds = board.GetDesignSettings()
    ds.SetBoardThickness(MM(D.THICKNESS_MM))
    tb = board.GetTitleBlock()
    tb.SetTitle(D.TITLE)
    tb.SetRevision(D.REV)
    tb.SetDate(D.DATE)
    tb.SetCompany(D.COMPANY)
    tb.SetComment(0, COMMENTS[BOARD][0])
    tb.SetComment(1, COMMENTS[BOARD][1])

    nets = {}
    for n in D.NETS:
        ni = pcbnew.NETINFO_ITEM(board, n)
        board.Add(ni)
        nets[n] = ni

    for c in D.COMP:
        fp = load_fp(c["fp"])
        ref = c["ref"]
        fp.SetReference(ref)
        fp.SetValue(c["value"])
        lcsc, mpn, mfr = part_info(c)
        if lcsc:
            boards.kc_set_field(fp, "LCSC", lcsc)
        if mpn:
            boards.kc_set_field(fp, "MPN", mpn)
            boards.kc_set_field(fp, "Manufacturer", mfr)
        if ref in D.DNP:
            boards.kc_set_field(fp, "DNP", "DNP - saldare a mano")
        x, y, rot, side = D.PLACE[ref]
        fp.SetPosition(V(x, y))
        board.Add(fp)
        if side == "B":
            boards.kc_flip(fp)
        fp.SetOrientationDegrees(rot)
        attrs = fp.GetAttributes()
        if ref in D.DNP or ref in D.NOT_ASSEMBLED:
            attrs |= pcbnew.FP_EXCLUDE_FROM_BOM | pcbnew.FP_EXCLUDE_FROM_POS_FILES
        fp.SetAttributes(attrs)
        fp.SetPath(pcbnew.KIID_PATH("/" + D.sym_uuid(ref)))
        for p in fp.Pads():
            num = p.GetNumber()
            if not num:
                continue
            key = int(num) if num.isdigit() else num
            net = c["pins"].get(key)
            if net:
                p.SetNet(nets[net])
        # testi: riferimento piccolo, valore nascosto
        fp.Reference().SetTextSize(pcbnew.VECTOR2I(MM(0.6), MM(0.6)))
        fp.Reference().SetTextThickness(MM(0.1))
        fp.Reference().SetVisible(False)
        fp.Value().SetVisible(False)

    add_outline(board)
    add_zone(board, pcbnew.In1_Cu, "GND", 0.0, 0, "GND_In1")
    outline = outline_poly()
    if BOARD == "2.0":
        special_gnd(board)
    if "U1" in D.BY_REF:          # rev 2.0 e Board A: stesso gruppo RP2040 (posizioni relative identiche)
        crystal_preroute(board)
        testen_to_ep(board)
        if FANOUT_QFN:
            direct = {"+3V3", "+1V1", "GND", "XIN", "XOUT", "USB_DM_MCU", "USB_DP_MCU", "QSPI_SS", "QSPI_SCLK",
                      "QSPI_SD0", "QSPI_SD1", "QSPI_SD2", "QSPI_SD3"}
            qd, qs = PR.qfn_fanout(board, "U1", direct, outline)
            print(f"fan-out QFN: {len(qd)} via interne, piazzole lasciate al router: {qs}")
    skip = (lambda fp, p: (BOARD == "2.0" and fp.GetReference() in ("J1", "J2")) or
            (fp.GetReference() == "U1" and p.GetNumber() in ("57", "19")))
    done, failed = PR.gnd_fanout(board, outline, skip)
    print(f"fan-out GND: {len(done)} ok, falliti (li collega il router al piano In1): {failed}")
    add_silk(board)
    pcbnew.SaveBoard(pcb_path, board)
    pro = os.path.join(out_dir, name + ".kicad_pro")
    if not os.path.exists(pro):
        json.dump({"meta": {"filename": name + ".kicad_pro", "version": 1}}, open(pro, "w"))
    project.write(pro, VIA)
    # librerie locali
    dst = os.path.join(out_dir, "x210ai.pretty")
    if os.path.exists(dst):
        shutil.rmtree(dst)
    shutil.copytree(LIB, dst)
    open(os.path.join(out_dir, "fp-lib-table"), "w").write(
        '(fp_lib_table\n  (version 7)\n  (lib (name "x210ai")(type "KiCad")(uri "${KIPRJMOD}/x210ai.pretty")'
        '(options "")(descr "Footprint progetto X210Ai"))\n)\n')
    return pcb_path, failed


def add_silk(board):
    """scritte minime: titolo, rev, pin 1, lati"""
    def txt(s, x, y, layer, size=0.8, mirror=False, rot=0):
        t = pcbnew.PCB_TEXT(board)
        t.SetText(s)
        t.SetPosition(V(x, y))
        t.SetLayer(layer)
        t.SetTextSize(pcbnew.VECTOR2I(MM(size), MM(size)))
        t.SetTextThickness(MM(size * 0.15))
        t.SetMirrored(mirror)
        if rot:
            t.SetTextAngleDegrees(rot)
        board.Add(t)
    for s, x, y, side, size in SILK[BOARD]:
        txt(s, x, y, pcbnew.F_SilkS if side == "F" else pcbnew.B_SilkS, size, mirror=(side == "B"))


def part_info(c):
    """(LCSC, MPN, produttore); per J1 della Board B la parte montata sopra (il ricettacolo)"""
    if c["ref"] == "J1" and hasattr(D, "J1_PARTS"):
        _, _, lcsc, mpn, mfr, _ = D.J1_PARTS[0]
        return lcsc, mpn, mfr
    return D.PARTS.get(c["value"], ("", "", ""))


def protect_selected(t, nets):
    """protegge solo piste/via delle net indicate nella sezione wiring"""
    i = t.find("(wiring")
    if i < 0:
        return t
    out = [t[:i]]
    j = i
    while True:
        m = re.compile(r"\((wire|via)\b").search(t, j)
        if not m:
            break
        out.append(t[j:m.start()])
        depth, k = 0, m.start()
        while True:
            if t[k] == "(":
                depth += 1
            elif t[k] == ")":
                depth -= 1
                if depth == 0:
                    break
            k += 1
        blk = t[m.start():k + 1]
        n = re.search(r"\(net \"?([^\s)\"]+)\"?\)", blk)
        if n and n.group(1) in nets:
            blk = blk.replace("(type route)", "(type protect)")
        out.append(blk)
        j = k + 1
    out.append(t[j:])
    return "".join(out)


def cut_block(t, head):
    i = t.find(head)
    if i < 0:
        return t
    depth = 0
    for k in range(i, len(t)):
        if t[k] == "(":
            depth += 1
        elif t[k] == ")":
            depth -= 1
            if depth == 0:
                return t[:i] + t[k + 1:]
    return t


def export_dsn(pcb, dsn, protect_nets=None, in1_signal=False):
    board = pcbnew.LoadBoard(pcb)
    ok = pcbnew.ExportSpecctraDSN(board, dsn)
    assert ok, "export DSN fallito"
    t = open(dsn).read()
    # contorno di instradamento rientrato di 0,17 mm (rame lontano dal bordo)
    m = re.search(r'\(resolution um (\d+)\)', t)
    res = int(m.group(1)) if m else 10
    k = 1000  # (unit um): coordinate in micron
    ins = 0.17
    ch = 0.5
    x0, x1 = (D.ORIGIN[0] + D.X0 + ins), (D.ORIGIN[0] + D.X1 - ins)
    y0, y1 = -(D.ORIGIN[1] + D.Y0 + ins), -(D.ORIGIN[1] + D.Y1 - ins)
    pts = [(x0 + ch, y0), (x1 - ch, y0), (x1, y0 - ch), (x1, y1 + ch), (x1 - ch, y1), (x0 + ch, y1),
           (x0, y1 + ch), (x0, y0 - ch), (x0 + ch, y0)]
    poly = " ".join(f"{x * k:.0f} {y * k:.0f}" for x, y in pts)
    t, n = re.subn(r'\(boundary\s*\(path pcb 0[^)]*\)\s*\)', f'(boundary (path pcb 0 {poly}))', t, count=1)
    assert n == 1, "boundary non trovato"
    if not in1_signal:
        t = t.replace("(layer In1.Cu\n      (type signal)", "(layer In1.Cu\n      (type power)")
        t = re.sub(r'\(layer In1\.Cu\s*\(type signal\)', '(layer In1.Cu (type power)', t)
    else:
        # In1 diventa strato di segnale: niente piano GND per Freerouting (lo crea la zona KiCad dopo);
        # la net GND resta con un solo pin, cosi' non viene instradata ma le sue piste restano ostacoli.
        t = cut_block(t, "(plane GND")
        m = re.search(r"\(net GND\s*\(pins ([^)]*)\)", t)
        first = m.group(1).split()[0]
        t = t[:m.start(1)] + first + t[m.end(1):]
    if protect_nets is None:
        t = re.sub(r'\(type route\)', '(type protect)', t)
    else:
        t = protect_selected(t, protect_nets)
    open(dsn, "w").write(t)
    print("DSN ok:", dsn, "res", res)


if __name__ == "__main__":
    if sys.argv[1] == "--dsn":
        pn = None
        if "--protect" in sys.argv:
            pn = set(sys.argv[sys.argv.index("--protect") + 1].split(","))
        export_dsn(sys.argv[2], sys.argv[3], pn, "--in1-signal" in sys.argv)
    else:
        uu = None
        if "--uuids" in sys.argv:
            uu = json.load(open(sys.argv[sys.argv.index("--uuids") + 1]))
        path, failed = build(sys.argv[1], uu)
        print("salvato", path)
