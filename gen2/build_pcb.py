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
    "2.0": ("4 strati: F.Cu / In1 GND / In2 segnali / B.Cu - spessore 0,8 mm o 0,4 mm (JLCPCB)",
            "J1 sopra (tastiera), J2 sotto (BTB_R_CONN1 scheda madre), RP2040 sotto"),
    "A": ("4 strati: F.Cu / In1 GND / In2 segnali / B.Cu - 0,8 mm JLCPCB, ENIG, via 0,4/0,2",
          "RP2040 e componenti sotto; J4 (eDP verso la Board B) sopra"),
    "B": ("Flessibile 4 strati (poliimmide ~0,25 mm, In1 GND) con irrigidimenti su User.1 - JLCPCB flex, via 0,4/0,2",
          "A scalino: J2 sotto in BTB_R_CONN1 e J4 sul gradino alto; J1 (tastiera) sul gradino basso a 25 gradi"),
    "C": ("4 strati: F.Cu / In1 GND / In2 segnali / B.Cu - 0,4 mm JLCPCB, ENIG, via 0,4/0,2",
          "J1 sopra e J2 sotto allineati su BTB_R_CONN1; RP2040 sotto nel braccio lontano (Mylar sulla madre)"),
}
# scritte in serigrafia: (testo, x, y, lato, altezza) in coordinate del modello dati (Board A: D.SILK)
SILK = {
    "2.0": [(f"X210Ai ISO/JIS rev {D.REV}", -13.2, -4.15, "F", 0.8), ("TASTIERA", -11.0, 4.6, "F", 0.7),
            ("BOOT", -25.4, -0.45, "F", 0.6), ("RST", -21.8, -0.45, "F", 0.6),
            ("CLK DIO GND 3V3", -23.3, -2.95, "F", 0.45)],
    "B": [(f"X210Ai Board B rev {D.REV}", -17.8, 6.2, "B", 0.8), ("eDP -> Board A", -17.8, 8.2, "B", 0.6)],
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


def outline_pts():
    """vertici del contorno (coordinate relative): OUTLINE del modello dati, altrimenti il rettangolo X0..Y1"""
    return getattr(D, "OUTLINE", [(D.X0, D.Y0), (D.X1, D.Y0), (D.X1, D.Y1), (D.X0, D.Y1)])


def fillets():
    """per ogni vertice (lati con angolo qualsiasi): tangenza in entrata, punto medio dell'arco, tangenza in uscita
    e centro dell'arco di raggio CORNER_R"""
    r, pts, out = D.CORNER_R, outline_pts(), []
    for i, (px, py) in enumerate(pts):
        (ax, ay), (bx, by) = pts[i - 1], pts[(i + 1) % len(pts)]
        u = ((ax - px) / math.hypot(ax - px, ay - py), (ay - py) / math.hypot(ax - px, ay - py))
        v = ((bx - px) / math.hypot(bx - px, by - py), (by - py) / math.hypot(bx - px, by - py))
        th = math.acos(max(-1.0, min(1.0, u[0] * v[0] + u[1] * v[1])))    # angolo tra i due lati
        d = r / math.tan(th / 2)                                            # distanza dei punti di tangenza
        t1, t2 = (px + u[0] * d, py + u[1] * d), (px + v[0] * d, py + v[1] * d)
        w = (u[0] + v[0], u[1] + v[1])
        wl = math.hypot(*w)
        w = (w[0] / wl, w[1] / wl)                                          # bisettrice, verso l'interno dell'angolo
        h = r / math.sin(th / 2)
        cx, cy = px + w[0] * h, py + w[1] * h
        out.append((t1, (cx - w[0] * r, cy - w[1] * r), t2, (cx, cy)))
    return out


def outline_poly():
    pts = []
    for t1, _, t2, (cx, cy) in fillets():
        a0, a1 = math.atan2(t1[1] - cy, t1[0] - cx), math.atan2(t2[1] - cy, t2[0] - cx)
        da = (a1 - a0 + math.pi) % (2 * math.pi) - math.pi
        for i in range(9):
            a = a0 + da * i / 8
            pts.append(A(cx + D.CORNER_R * math.cos(a), cy + D.CORNER_R * math.sin(a)))
    return Polygon(pts)


def add_outline(board):
    f = fillets()
    for i, (t1, mid, t2, _) in enumerate(f):
        s = pcbnew.PCB_SHAPE(board)
        s.SetShape(pcbnew.SHAPE_T_ARC)
        s.SetArcGeometry(V(*t1), V(*mid), V(*t2))
        s.SetLayer(pcbnew.Edge_Cuts)
        s.SetWidth(MM(0.05))
        board.Add(s)
        s = pcbnew.PCB_SHAPE(board)
        s.SetShape(pcbnew.SHAPE_T_SEGMENT)
        s.SetStart(V(*t2))
        s.SetEnd(V(*f[(i + 1) % len(f)][0]))
        s.SetLayer(pcbnew.Edge_Cuts)
        s.SetWidth(MM(0.05))
        board.Add(s)


def add_zone(board, layer, net="GND", inset=0.0, priority=0, name=""):
    z = pcbnew.ZONE(board)
    z.SetLayer(layer)
    z.SetNet(board.FindNet(net))
    ol = z.Outline()
    ol.NewOutline()
    poly = Polygon(outline_pts()).buffer(-inset, join_style=2) if inset else Polygon(outline_pts())
    for x, y in list(poly.exterior.coords)[:-1]:
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


def j1_fanout(board):
    """Board B: Freerouting non si aggancia ai piedini di J1 ruotato di 25 gradi e fatica nel tratto inclinato.
    Ogni piedino con una net riceve una pista fino al gradino alto: la fila rivolta allo scalino sopra (F.Cu),
    l'altra fila con un via sotto il corpo del connettore (due profondita' alternate) e poi sotto (B.Cu). Le
    piste escono dal gradino basso nella direzione del connettore, poi salgono dritte attraverso lo scalino e si
    fermano 0,35 mm dentro il gradino alto; da li' instrada Freerouting"""
    fp = board.FindFootprintByReference("J1")
    f = fp.GetPosition()
    fx, fy = pcbnew.ToMM(f.x), pcbnew.ToMM(f.y)
    ox, oy = A(0, 0)
    y_end = oy + D.Y_HI - 0.35
    n = 0
    for p in fp.Pads():
        num, net = p.GetNumber(), p.GetNetname()
        if not net or not num.isdigit() or int(num) > 40:
            continue
        c = p.GetPosition()
        gx, gy = pcbnew.ToMM(c.x) - fx, pcbnew.ToMM(c.y) - fy
        lx, ly = D._rot(gx, gy, -D.ROT_KB)                       # coordinate nell'impronta
        ex, ey = D._rot(lx, D.J1_CRT[2], D.ROT_KB)               # uscita sul lato verso lo scalino
        edge, top = (fx + ex, fy + ey), (fx + ex, y_end)
        if ly < 0:                                               # fila verso lo scalino: tutto sopra
            PR.add_track(board, net, [(fx + gx, fy + gy), edge, top], pcbnew.F_Cu, 0.1)
        else:                                                    # altra fila: via sotto il corpo, poi sotto
            half = pcbnew.ToMM(p.GetSize(pcbnew.F_Cu).y) / 2
            k = round((lx + 4.7) / 0.5)
            vx, vy = D._rot(lx, ly - half - (0.4 if k % 2 == 0 else 1.2), D.ROT_KB)
            via = (fx + vx, fy + vy)
            PR.add_track(board, net, [(fx + gx, fy + gy), via], pcbnew.F_Cu, 0.1)
            PR.add_via(board, net, *via)
            PR.add_track(board, net, [via, edge, top], pcbnew.B_Cu, 0.1)
        n += 1
    print(f"pre-instradamento J1: {n} piedini fino al gradino alto")


def add_keepout(board, pts, name):
    """area senza via (zona di piega del flessibile): le piste possono passare"""
    z = pcbnew.ZONE(board)
    z.SetIsRuleArea(True)
    z.SetDoNotAllowVias(True)
    z.SetDoNotAllowTracks(False)
    z.SetDoNotAllowPads(True)
    z.SetDoNotAllowZoneFills(False)
    z.SetDoNotAllowFootprints(True)
    z.SetLayerSet(pcbnew.LSET.AllCuMask())
    ol = z.Outline()
    ol.NewOutline()
    for x, y in pts:
        ol.Append(MM(A(x, y)[0]), MM(A(x, y)[1]))
    z.SetZoneName(name)
    board.Add(z)


def add_stiffeners(board):
    """irrigidimenti del flessibile su User.1: contorno, materiale, spessore e lato"""
    for nome, lato, mat, sp, pts in D.STIFFENERS:
        for i, p in enumerate(pts):
            s = pcbnew.PCB_SHAPE(board)
            s.SetShape(pcbnew.SHAPE_T_SEGMENT)
            s.SetStart(V(*p))
            s.SetEnd(V(*pts[(i + 1) % len(pts)]))
            s.SetLayer(pcbnew.User_1)
            s.SetWidth(MM(0.1))
            board.Add(s)
        t = pcbnew.PCB_TEXT(board)
        t.SetText(f"{mat} {sp:g} mm ({lato})")
        cx = sum(x for x, _ in pts) / len(pts)
        cy = sum(y for _, y in pts) / len(pts)
        t.SetPosition(V(cx, cy))
        t.SetLayer(pcbnew.User_1)
        t.SetTextSize(pcbnew.VECTOR2I(MM(0.6), MM(0.6)))
        t.SetTextThickness(MM(0.08))
        board.Add(t)


def pad_xy(board, ref, num):
    fp = board.FindFootprintByReference(ref)
    for p in fp.Pads():
        if p.GetNumber() == str(num) and p.GetAttribute() != pcbnew.PAD_ATTRIB_PTH:
            c = p.GetPosition()
            return (pcbnew.ToMM(c.x), pcbnew.ToMM(c.y))
    raise KeyError((ref, num))


def special_gnd(board):
    """masse di J1/J2 (rev 2.0 e Board C) collegate con via dedicate (coordinate relative)"""
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
    # gia' collegato al pad centrale: niente raggi verso la zona GND (tra le piazzole vicine ne entra uno solo)
    p19.SetLocalZoneConnection(pcbnew.ZONE_CONNECTION_NONE)
    return d


def vdd_48_49(board):
    """IOVDD 48 e 49 unite su B.Cu e portate a una via interna sull'anello del fan-out (2,55 mm dal centro),
    come nello sbroglio della rev 2.0: lasciate al router, nella Board A restavano isolate dal resto del +3V3"""
    fp = board.FindFootprintByReference("U1")
    pad = {p.GetNumber(): p for p in fp.Pads() if p.GetAttribute() != pcbnew.PAD_ATTRIB_PTH}
    c = pad["57"].GetPosition()
    cx, cy = pcbnew.ToMM(c.x), pcbnew.ToMM(c.y)
    (x48, y48), (x49, y49) = [(pcbnew.ToMM(pad[n].GetPosition().x), pcbnew.ToMM(pad[n].GetPosition().y))
                              for n in ("48", "49")]
    assert pad["48"].GetNetname() == pad["49"].GetNetname() == "+3V3"
    if abs(x49 - cx) > abs(y49 - cy):      # lato verticale: si rientra in x
        via = (cx + math.copysign(2.55, x49 - cx), y49)
    else:
        via = (x49, cy + math.copysign(2.55, y49 - cy))
    PR.add_track(board, "+3V3", [(x48, y48), (x49, y49), via], pcbnew.B_Cu, 0.2)
    PR.add_via(board, "+3V3", *via)


def build(out_dir, uuids=None):
    os.makedirs(out_dir, exist_ok=True)
    name = boards.project_name(D)
    pcb_path = os.path.join(out_dir, name + ".kicad_pcb")
    board = pcbnew.NewBoard(pcb_path)
    board.SetCopperLayerCount(getattr(D, "COPPER_LAYERS", 4))
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
    four = getattr(D, "COPPER_LAYERS", 4) == 4
    if four:
        add_zone(board, pcbnew.In1_Cu, "GND", 0.0, 0, "GND_In1")
    if hasattr(D, "BEND"):
        add_keepout(board, D.BEND, "piega")
    if hasattr(D, "STIFFENERS"):
        add_stiffeners(board)
    outline = outline_poly()
    if BOARD in ("2.0", "C"):      # J1 sopra e J2 sotto allineati: masse con via dedicate
        special_gnd(board)
    if BOARD == "B" and getattr(D, "ROT_KB", 0) % 90:
        j1_fanout(board)
    if "U1" in D.BY_REF:          # rev 2.0 e Board A: stesso gruppo RP2040 (posizioni relative identiche)
        crystal_preroute(board)
        testen_to_ep(board)
        vdd_48_49(board)
        if FANOUT_QFN:
            direct = {"+3V3", "+1V1", "GND", "XIN", "XOUT", "USB_DM_MCU", "USB_DP_MCU", "QSPI_SS", "QSPI_SCLK",
                      "QSPI_SD0", "QSPI_SD1", "QSPI_SD2", "QSPI_SD3"}
            qd, qs = PR.qfn_fanout(board, "U1", direct, outline)
            print(f"fan-out QFN: {len(qd)} via interne, piazzole lasciate al router: {qs}")
    skip = (lambda fp, p: (BOARD in ("2.0", "C") and fp.GetReference() in ("J1", "J2")) or
            (fp.GetReference() == "U1" and p.GetNumber() in ("57", "19")))
    failed = []
    if four:                       # via di massa verso il piano In1 (a 2 strati la massa la instrada il router)
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
    for s, x, y, side, size in getattr(D, "SILK", None) or SILK[BOARD]:
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
    # spigoli smussati di ch (cap_style/join_style 3 = bevel); y del DSN verso l'alto
    shape = Polygon(outline_pts()).buffer(-ins - ch, join_style=2).buffer(ch, join_style=3)
    pts = [(D.ORIGIN[0] + x, -(D.ORIGIN[1] + y)) for x, y in shape.exterior.coords]
    poly = " ".join(f"{x * k:.0f} {y * k:.0f}" for x, y in pts)
    t, n = re.subn(r'\(boundary\s*\(path pcb 0[^)]*\)\s*\)', f'(boundary (path pcb 0 {poly}))', t, count=1)
    assert n == 1, "boundary non trovato"
    if getattr(D, "COPPER_LAYERS", 4) == 2:
        # a 2 strati la massa la collegano le colate F/B dopo lo sbroglio: GND resta con un solo pin, cosi'
        # Freerouting non la instrada e lascia lo spazio alle altre net
        m = re.search(r"\(net GND\s*\(pins ([^)]*)\)", t)
        t = t[:m.start(1)] + m.group(1).split()[0] + t[m.end(1):]
    elif not in1_signal:
        t = t.replace("(layer In1.Cu\n      (type signal)", "(layer In1.Cu\n      (type power)")
        t = re.sub(r'\(layer In1\.Cu\s*\(type signal\)', '(layer In1.Cu (type power)', t)
    else:
        # In1 diventa strato di segnale: niente piano GND per Freerouting (lo crea la zona KiCad dopo);
        # la net GND resta con un solo pin, cosi' non viene instradata ma le sue piste restano ostacoli.
        t = cut_block(t, "(plane GND")
        m = re.search(r"\(net GND\s*\(pins ([^)]*)\)", t)
        first = m.group(1).split()[0]
        t = t[:m.start(1)] + first + t[m.end(1):]
    # Freerouting conosce solo l'isolamento rame-rame: lo si alza quanto basta perche' il rame resti a
    # min_hole_clearance dal foro dei via (via 0,3/0,15 della Board B: 0,2 - 0,075 -> 0,13 mm)
    need = math.ceil((project.RULES["min_hole_clearance"] - VIA[1] / 2) * 100 - 1e-9) * 10 * k / 1000
    t = re.sub(r'\(clearance (\d+(?:\.\d+)?)\)', lambda m: f"(clearance {max(float(m.group(1)), need):g})", t)
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
