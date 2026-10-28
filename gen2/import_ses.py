# -*- coding: utf-8 -*-
"""Importa le piste e le via di una sessione Freerouting (.ses) mantenendo quelle gia' presenti.

uso: python3.12 import_ses.py in.kicad_pcb sessione.ses out.kicad_pcb
"""
import re
import sys

import pcbnew

MM = pcbnew.FromMM


def tokenize(s):
    return re.findall(r'\(|\)|"[^"]*"|[^\s()]+', s)


def parse(tokens):
    stack = [[]]
    for t in tokens:
        if t == "(":
            stack.append([])
        elif t == ")":
            x = stack.pop()
            stack[-1].append(x)
        else:
            stack[-1].append(t.strip('"'))
    return stack[0][0]


def find(node, name):
    for x in node:
        if isinstance(x, list) and x and x[0] == name:
            yield x


def main():
    pcb_in, ses, pcb_out = sys.argv[1:4]
    tree = parse(tokenize(open(ses).read()))
    routes = next(find(tree, "routes"))
    res = next(find(routes, "resolution"))
    unit, per = res[1], float(res[2])
    assert unit == "um", unit
    k = 1.0 / per / 1000.0          # unita' SES -> mm
    board = pcbnew.LoadBoard(pcb_in)
    layers = {board.GetLayerName(l): l for l in range(pcbnew.PCB_LAYER_ID_COUNT) if pcbnew.IsCopperLayer(l)}
    existing = set()
    vias = set()
    for t in board.GetTracks():
        if t.GetClass() == "PCB_VIA":
            p = t.GetPosition()
            vias.add((t.GetNetname(), round(pcbnew.ToMM(p.x), 3), round(pcbnew.ToMM(p.y), 3)))
        else:
            a, b = t.GetStart(), t.GetEnd()
            ka = (round(pcbnew.ToMM(a.x), 3), round(pcbnew.ToMM(a.y), 3))
            kb = (round(pcbnew.ToMM(b.x), 3), round(pcbnew.ToMM(b.y), 3))
            existing.add((t.GetNetname(), t.GetLayer(), min(ka, kb), max(ka, kb)))
    lib = next(find(routes, "library_out"), [])
    padstacks = {}
    for ps in find(lib, "padstack"):
        m = re.search(r"_(\d+):(\d+)_um", ps[1])
        if m:
            padstacks[ps[1]] = (int(m.group(1)) / 1000.0, int(m.group(2)) / 1000.0)
    net_out = next(find(routes, "network_out"))
    n_tr = n_via = n_dup = 0
    for net in find(net_out, "net"):
        name = net[1]
        ni = board.FindNet(name)
        if ni is None:
            raise SystemExit(f"net sconosciuta {name}")
        for w in find(net, "wire"):
            path = next(find(w, "path"))
            layer = layers[path[1]]
            width = float(path[2]) * k
            nums = [float(v) for v in path[3:] if not isinstance(v, list)]
            pts = [(nums[i] * k, -nums[i + 1] * k) for i in range(0, len(nums) - 1, 2)]
            for a, b in zip(pts[:-1], pts[1:]):
                ka = (round(a[0], 3), round(a[1], 3))
                kb = (round(b[0], 3), round(b[1], 3))
                key = (name, layer, min(ka, kb), max(ka, kb))
                if key in existing or ka == kb:
                    n_dup += 1
                    continue
                existing.add(key)
                t = pcbnew.PCB_TRACK(board)
                t.SetStart(pcbnew.VECTOR2I(MM(a[0]), MM(a[1])))
                t.SetEnd(pcbnew.VECTOR2I(MM(b[0]), MM(b[1])))
                t.SetWidth(MM(width))
                t.SetLayer(layer)
                t.SetNet(ni)
                board.Add(t)
                n_tr += 1
        for v in find(net, "via"):
            x, y = float(v[2]) * k, -float(v[3]) * k
            key = (name, round(x, 3), round(y, 3))
            if key in vias:
                n_dup += 1
                continue
            vias.add(key)
            d, drill = padstacks.get(v[1], (0.4, 0.2))
            via = pcbnew.PCB_VIA(board)
            via.SetPosition(pcbnew.VECTOR2I(MM(x), MM(y)))
            via.SetWidth(MM(d))
            via.SetDrill(MM(drill))
            via.SetViaType(pcbnew.VIATYPE_THROUGH)
            via.SetLayerPair(pcbnew.F_Cu, pcbnew.B_Cu)
            via.SetNet(ni)
            board.Add(via)
            n_via += 1
    pcbnew.SaveBoard(pcb_out, board)
    print(f"importate {n_tr} piste e {n_via} via ({n_dup} gia' presenti)")


if __name__ == "__main__":
    main()
