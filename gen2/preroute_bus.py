# -*- coding: utf-8 -*-
"""Pre-instradamento del fascio J1 -> gruppo RP2040 della Board C.

Sopra la Board C (F.Cu) ci sono solo J1 e le piazzole di test/ponticelli: il fascio dei segnali della
tastiera e del TrackPoint corre li', senza via intermedi. Freerouting da solo si incastrava sul percorso
lungo a U (circa 30 segnali da J1, attorno al quadrato bianco, fino al gruppo RP2040); qui lo si disegna in
modo deterministico e Freerouting fa solo gli ultimi millimetri (fine del fascio -> via del fan-out del QFN).

Percorso di ogni segnale su F.Cu (coordinate del modello dati, mm):
  piazzola di J1 -> uscita dritta (fila verso il quadrato: -y; fila verso la vite: +y) fino alla sua quota
  -> verso -x nel braccio R1 fino alla sua corsia -> giu' (-y) nel tratto R3 sotto il quadrato
  -> verso +x in R4 alla sua quota -> fine "a scala": verso il suo pin, ma 0,45 mm prima della fine della
  pista sopra, cosi' sotto ogni fine resta posto per il via di discesa.
Le quote e le corsie sono ordinate in modo che le piste non si incrocino (chi gira prima sta all'esterno).

D.BUS["inner"]: segnali portati invece su In2 (via subito fuori da J1), con percorso proprio: servono per
quelli che su F.Cu finirebbero nelle corsie piu' basse ma vanno all'estremita' lontana del gruppo.
"""
import pcbnew

import preroute as PR


def _stack(start, sign, pins, wide, gap=0.1, w0=0.1):
    """centri delle piste impilate da start verso sign (+1/-1): pitch = mezze larghezze + gap"""
    out, cur, prev_w = {}, start, None
    for p in pins:
        w = wide.get(p, w0)
        if prev_w is not None:
            cur += sign * (prev_w / 2 + gap + w / 2)
        out[p] = cur
        prev_w = w
    return out


def _target_x(board, net, ox, oy, y_far=-20.0):
    """x (coordinate del modello) della piazzola piu' a -x della net nella zona del gruppo"""
    xs = []
    for fp in board.GetFootprints():
        for p in fp.Pads():
            if p.GetNetname() == net:
                c = p.GetPosition()
                x, y = pcbnew.ToMM(c.x) - ox, pcbnew.ToMM(c.y) - oy
                if y < y_far:
                    xs.append(x)
    return min(xs)


def bus_preroute(board, D, pad_xy):
    B = D.BUS
    ox, oy = D.ORIGIN
    wide = B.get("wide", {})
    odd, even = B["odd"], B["even"]
    j1 = D.BY_REF["J1"]["pins"]

    def A(pts):
        return [(ox + x, oy + y) for x, y in pts]

    # ---- F.Cu
    y_out = _stack(B["odd_y0"], -1, odd, wide)
    y_out.update(_stack(B["even_y0"], +1, even, wide))
    order = list(reversed(odd)) + even
    x_lane = _stack(B["lane_x0"], -1, order, wide)
    y_turn = _stack(B["turn_y0"], -1, order, wide)
    done, x_prev, ends = [], None, {}
    for p in order:
        px, py = pad_xy(board, "J1", p)
        px, py = px - ox, py - oy
        x_end = _target_x(board, j1[p], ox, oy) - B.get("end_back", 0.3)
        if x_prev is not None:
            x_end = min(x_end, x_prev - B["end_step"])
        x_end = max(x_end, B["x_end_min"])
        x_end = min(x_end, B.get("x_end_max", x_end))
        x_prev = x_end
        pts = [(px, py), (px, y_out[p]), (x_lane[p], y_out[p]), (x_lane[p], y_turn[p]), (x_end, y_turn[p])]
        PR.add_track(board, j1[p], A(pts), pcbnew.F_Cu, wide.get(p, 0.1))
        done.append(j1[p])
        ends[j1[p]] = (A(pts)[-1], pcbnew.F_Cu, wide.get(p, 0.1), y_turn[p])
    # ---- In2: via subito fuori da J1, poi percorso proprio
    for p, d in B.get("inner", {}).items():
        px, py = pad_xy(board, "J1", p)
        px, py = px - ox, py - oy
        w = wide.get(p, 0.1)
        vx, vy = px, d["via_y"]
        PR.add_track(board, j1[p], A([(px, py), (vx, vy)]), pcbnew.F_Cu, w)
        PR.add_via(board, j1[p], ox + vx, oy + vy)
        pts = [(vx, vy), (vx, d["y_band"]), (d["x_lane"], d["y_band"]), (d["x_lane"], d["y_turn"]),
               (d["x_end"], d["y_turn"])]
        PR.add_track(board, j1[p], A(pts), pcbnew.In2_Cu, w)
        done.append(j1[p])
        ends[j1[p]] = (A(pts)[-1], pcbnew.In2_Cu, w, d["y_turn"])
    # ---- B.Cu: gate EC da Q3/Q4 + R13/R14 (accanto a J2) verso U1, percorsi del modello dati
    for net, d in B.get("bottom", {}).items():
        PR.add_track(board, net, A(d["path"]), pcbnew.B_Cu, 0.1)
        done.append(net)
        ends[net] = (A(d["path"])[-1], pcbnew.B_Cu, 0.1, d["path"][-1][1])
    return done, ends


def _far_items(board, net, oy, y_far):
    vias, pads = [], []
    for t in board.GetTracks():
        if t.GetClass() == "PCB_VIA" and t.GetNetname() == net:
            s = t.GetStart()
            if pcbnew.ToMM(s.y) - oy < y_far:
                vias.append((pcbnew.ToMM(s.x), pcbnew.ToMM(s.y)))
    for fp in board.GetFootprints():
        for p in fp.Pads():
            if p.GetNetname() == net:
                c = p.GetPosition()
                if pcbnew.ToMM(c.y) - oy < y_far:
                    pads.append(p)
    return vias, pads


def last_mile(board, D, outline, ends, y_far=-40.0, skip_layers=()):
    """ultimo tratto: dalla fine del fascio fino a una via della stessa net nel gruppo (F.Cu, In2) o fino alla
    piazzola (B.Cu), con il router a griglia; dove manca una via la si crea accanto a una piazzola"""
    import astar_route as AR
    from shapely.geometry import Point, box
    ox, oy = D.ORIGIN
    ok, ko = [], []
    # prima le piste piu' vicine al gruppo (quota piu' a -y)
    for net, (end, layer, w, _) in sorted(ends.items(), key=lambda kv: kv[1][3]):
        if layer in skip_layers:
            continue
        vias, pads = _far_items(board, net, oy, y_far)
        if layer == pcbnew.B_Cu:
            pads.sort(key=lambda p: (pcbnew.ToMM(p.GetPosition().x) - end[0]) ** 2 +
                      (pcbnew.ToMM(p.GetPosition().y) - end[1]) ** 2)
            goals = []
            for p in pads:
                bb = p.GetBoundingBox()
                g = box(pcbnew.ToMM(bb.GetLeft()), pcbnew.ToMM(bb.GetTop()),
                        pcbnew.ToMM(bb.GetRight()), pcbnew.ToMM(bb.GetBottom()))
                c = p.GetPosition()
                goals.append((g, (pcbnew.ToMM(c.x), pcbnew.ToMM(c.y))))
        else:
            if not vias:
                obs = PR.Obstacles(board)
                for p in sorted(pads, key=lambda p: (pcbnew.ToMM(p.GetPosition().x) - end[0]) ** 2 +
                                (pcbnew.ToMM(p.GetPosition().y) - end[1]) ** 2):
                    if PR.place_via(board, obs, p, outline, net=net, w=0.1):
                        break
                vias, _ = _far_items(board, net, oy, y_far)
            vias.sort(key=lambda v: (v[0] - end[0]) ** 2 + (v[1] - end[1]) ** 2)
            goals = [(Point(v).buffer(PR.VIA_D / 2, 16), v) for v in vias]
        path = None
        for g, gp in goals[:3]:
            path = AR.route(board, net, layer, end, g, outline, w=w, goal_point=gp)
            if path:
                break
        if path:
            PR.add_track(board, net, path, layer, w)
            ok.append(net)
        else:
            ko.append(net)
    return ok, ko
