# -*- coding: utf-8 -*-
"""Pre-instradamento: via di massa verso il piano In1 e collegamenti del quarzo.

Tutte le coordinate qui sono in mm assoluti della board (origine KiCad).
"""
import math

import pcbnew
from shapely.geometry import LineString, Point, box

MM = pcbnew.FromMM
CLR = 0.1            # isolamento minimo
VIA_D = 0.4
VIA_DRILL = 0.2
VIA_PITCH_MIN = 0.55  # interasse minimo tra via (foro-foro >= 0,35 mm)
EDGE_MIN = 0.3        # bordo via -> bordo scheda
GND_W = 0.2

LAYERS = {"F": pcbnew.F_Cu, "B": pcbnew.B_Cu, "In1": pcbnew.In1_Cu, "In2": pcbnew.In2_Cu}


def mm(v):
    return pcbnew.ToMM(v)


def vxy(x, y):
    return pcbnew.VECTOR2I(MM(x), MM(y))


def pad_geom(p):
    bb = p.GetBoundingBox()
    return box(mm(bb.GetLeft()), mm(bb.GetTop()), mm(bb.GetRight()), mm(bb.GetBottom()))


class Obstacles:
    """rame per strato: lista di (geometria, net)"""

    def __init__(self, board):
        self.board = board
        self.items = {k: [] for k in LAYERS}
        self.vias = []           # (x, y, net)
        for fp in board.GetFootprints():
            for p in fp.Pads():
                g = pad_geom(p)
                for k, l in LAYERS.items():
                    if p.IsOnLayer(l) and k != "In1":
                        self.items[k].append((g, p.GetNetname(), p))
                if p.GetAttribute() == pcbnew.PAD_ATTRIB_PTH:
                    c = p.GetPosition()
                    self.vias.append((mm(c.x), mm(c.y), p.GetNetname()))
        for t in board.GetTracks():
            self.add_item(t)

    def add_item(self, t):
        if t.GetClass() == "PCB_VIA":
            c = t.GetPosition()
            x, y = mm(c.x), mm(c.y)
            g = Point(x, y).buffer(mm(t.GetWidth()) / 2, 16)
            for k in ("F", "B", "In2"):
                self.items[k].append((g, t.GetNetname(), None))
            self.vias.append((x, y, t.GetNetname()))
        else:
            s, e = t.GetStart(), t.GetEnd()
            g = LineString([(mm(s.x), mm(s.y)), (mm(e.x), mm(e.y))]).buffer(mm(t.GetWidth()) / 2, 8)
            for k, l in LAYERS.items():
                if t.GetLayer() == l:
                    self.items[k].append((g, t.GetNetname(), None))

    def clear_point(self, x, y, net, r, layers, skip_pad=None):
        pt = Point(x, y)
        for k in layers:
            for g, n, p in self.items[k]:
                if p is not None and p is skip_pad:
                    continue
                d = g.distance(pt)
                if n != net or n == "":
                    if d < r + CLR - 1e-6:
                        return False
                elif p is not None and d < r + 0.05:   # niente via dentro le piazzole
                    return False
        return True

    def clear_seg(self, a, b, net, w, layer, own_pad=None):
        seg = LineString([a, b])
        for g, n, p in self.items[layer]:
            if p is not None and p is own_pad:
                continue
            if n != net or n == "":
                if g.distance(seg) < w / 2 + CLR - 1e-6:
                    return False
        return True

    def via_ok(self, x, y, net, outline):
        if not outline.contains(Point(x, y).buffer(VIA_D / 2 + EDGE_MIN)):
            return False
        for vx, vy, vn in self.vias:
            dd = math.hypot(vx - x, vy - y)
            if dd < VIA_PITCH_MIN - 1e-6 and not (vn == net and dd < 1e-3):
                return False
        return self.clear_point(x, y, net, VIA_D / 2, ("F", "B", "In2"))


def add_track(board, net, pts, layer, w):
    ni = board.FindNet(net)
    out = []
    for a, b in zip(pts[:-1], pts[1:]):
        t = pcbnew.PCB_TRACK(board)
        t.SetStart(vxy(*a))
        t.SetEnd(vxy(*b))
        t.SetLayer(layer)
        t.SetWidth(MM(w))
        t.SetNet(ni)
        board.Add(t)
        out.append(t)
    return out


def add_via(board, net, x, y):
    v = pcbnew.PCB_VIA(board)
    v.SetPosition(vxy(x, y))
    v.SetWidth(MM(VIA_D))
    v.SetDrill(MM(VIA_DRILL))
    v.SetViaType(pcbnew.VIATYPE_THROUGH)
    v.SetLayerPair(pcbnew.F_Cu, pcbnew.B_Cu)
    v.SetNet(board.FindNet(net))
    board.Add(v)
    return v


def place_via(board, obs, pad, outline, net="GND", w=GND_W, rmax=1.6):
    """cerca il punto piu' vicino alla piazzola dove mettere una via collegata con una pista corta"""
    layer_k = "F" if pad.IsOnLayer(pcbnew.F_Cu) else "B"
    layer = LAYERS[layer_k]
    c = pad.GetPosition()
    cx, cy = mm(c.x), mm(c.y)
    pg = pad_geom(pad)
    # 1) via esistente della stessa net a portata
    best = None
    for vx, vy, vn in obs.vias:
        if vn != net:
            continue
        d = math.hypot(vx - cx, vy - cy)
        if d < rmax and obs.clear_seg((cx, cy), (vx, vy), net, w, layer_k, own_pad=pad):
            if best is None or d < best[0]:
                best = (d, vx, vy, False)
    # 2) nuova via
    hw = max(pg.bounds[2] - pg.bounds[0], pg.bounds[3] - pg.bounds[1]) / 2
    r = 0.25
    while r <= rmax:
        for i in range(48):
            a = 2 * math.pi * i / 48
            x, y = cx + (hw + r) * math.cos(a), cy + (hw + r) * math.sin(a)
            if pg.distance(Point(x, y)) < VIA_D / 2 + 0.05:
                continue
            d = math.hypot(x - cx, y - cy)
            if best is not None and d >= best[0] - 0.15:
                continue
            if not obs.via_ok(x, y, net, outline):
                continue
            if not obs.clear_seg((cx, cy), (x, y), net, w, layer_k, own_pad=pad):
                continue
            best = (d, x, y, True)
        if best is not None and best[3]:
            break
        r += 0.05
    if best is None:
        return False
    _, x, y, new = best
    for t in add_track(board, net, [(cx, cy), (x, y)], layer, w):
        obs.add_item(t)
    if new:
        obs.add_item(add_via(board, net, x, y))
    return True


def gnd_fanout(board, outline, skip=lambda fp, pad: False):
    obs = Obstacles(board)
    done, failed = [], []
    pads = []
    for fp in board.GetFootprints():
        for p in fp.Pads():
            if p.GetNetname() != "GND" or p.GetAttribute() == pcbnew.PAD_ATTRIB_PTH:
                continue
            if skip(fp, p):
                continue
            pads.append((fp.GetReference(), p))
    # prima le piazzole piccole (piu' vincolate)
    pads.sort(key=lambda rp: mm(rp[1].GetBoundingBox().GetWidth()) * mm(rp[1].GetBoundingBox().GetHeight()))
    for ref, p in pads:
        (done if place_via(board, obs, p, outline) else failed).append(f"{ref}.{p.GetNumber()}")
    return done, failed


def qfn_fanout(board, ref, skip_nets, outline, w=0.1, d_rows=(2.55, 2.05), skip_side_pins=()):
    """via nell'anello interno del QFN (tra le piazzole e il pad centrale) con un tratto su B.Cu.
    Ritorna (fatti, saltati)."""
    fp = board.FindFootprintByReference(ref)
    obs = Obstacles(board)
    c = [p for p in fp.Pads() if p.GetNumber() == "57" and p.GetAttribute() != pcbnew.PAD_ATTRIB_PTH][0]
    cx, cy = mm(c.GetPosition().x), mm(c.GetPosition().y)
    done, skipped = [], []
    pads = [p for p in fp.Pads() if p.GetNumber().isdigit() and 1 <= int(p.GetNumber()) <= 56]
    pads.sort(key=lambda p: int(p.GetNumber()))
    lay = "B" if fp.IsFlipped() else "F"
    layer = LAYERS[lay]
    for p in pads:
        net = p.GetNetname()
        n = int(p.GetNumber())
        if not net or net in skip_nets or n in skip_side_pins:
            continue
        px, py = mm(p.GetPosition().x), mm(p.GetPosition().y)
        dx, dy = px - cx, py - cy
        if abs(dx) > abs(dy):
            ux, uy, along = (1 if dx > 0 else -1), 0, dy
        else:
            ux, uy, along = 0, (1 if dy > 0 else -1), dx
        if abs(along) > 2.25:          # piazzole d'angolo: niente via interna
            skipped.append(n)
            continue
        k = round((along + 2.6) / 0.4)
        order = d_rows if k % 2 == 0 else d_rows[::-1]
        placed = False
        for d in order:
            vx = cx + ux * d + (0 if ux else along)
            vy = cy + uy * d + (along if ux else 0)
            ok = all(math.hypot(vx - x, vy - y) >= VIA_PITCH_MIN - 1e-6 for x, y, _ in obs.vias)
            ok = ok and obs.clear_point(vx, vy, net, VIA_D / 2, ("F", "B", "In2"), skip_pad=p)
            if ok and obs.clear_seg((px, py), (vx, vy), net, w, lay, own_pad=p):
                for t in add_track(board, net, [(px, py), (vx, vy)], layer, w):
                    obs.add_item(t)
                obs.add_item(add_via(board, net, vx, vy))
                done.append(n)
                placed = True
                break
        if not placed:
            skipped.append(n)
    return done, skipped
