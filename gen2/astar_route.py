# -*- coding: utf-8 -*-
"""Router a griglia (A*) su un solo strato, per gli ultimi millimetri del fascio della Board C.

route(board, net, layer, start, goal, outline): cerca una pista larga w da start (punto, mm assoluti) fino a
toccare goal (geometria shapely della stessa net: via o piazzola), su una griglia di passo `grid`, tenendo
l'isolamento `clr` da tutto il rame di altre net sullo strato (piazzole, piste, via) e `edge` dal bordo.
Ritorna la lista dei vertici (gia' semplificata) o None se non trova un percorso.
"""
import heapq
import math

import numpy as np
import pcbnew
import shapely
from shapely.geometry import LineString, Point, box
from shapely.ops import unary_union


def _mm(v):
    return pcbnew.ToMM(v)


def obstacles(board, net, layer):
    """rame delle altre net sullo strato (geometrie shapely, mm assoluti)"""
    out = []
    for fp in board.GetFootprints():
        for p in fp.Pads():
            if p.GetNetname() == net and net:
                continue
            if not (p.IsOnLayer(layer) or p.GetAttribute() == pcbnew.PAD_ATTRIB_PTH):
                continue
            bb = p.GetBoundingBox()
            g = box(_mm(bb.GetLeft()), _mm(bb.GetTop()), _mm(bb.GetRight()), _mm(bb.GetBottom()))
            out.append(g)
    for t in board.GetTracks():
        if t.GetNetname() == net and net:
            continue
        if t.GetClass() == "PCB_VIA":
            s = t.GetStart()
            out.append(Point(_mm(s.x), _mm(s.y)).buffer(_mm(t.GetWidth(pcbnew.F_Cu)) / 2, 16))
        elif t.GetLayer() == layer:
            s, e = t.GetStart(), t.GetEnd()
            out.append(LineString([(_mm(s.x), _mm(s.y)), (_mm(e.x), _mm(e.y))]).buffer(_mm(t.GetWidth()) / 2, 8))
    return out


def route(board, net, layer, start, goal, outline, w=0.1, clr=0.1, edge=0.25, grid=0.05, margin=4.0,
          goal_point=None):
    sx, sy = start
    gb = goal.bounds
    x0, y0 = min(sx, gb[0]) - margin, min(sy, gb[1]) - margin
    x1, y1 = max(sx, gb[2]) + margin, max(sy, gb[3]) + margin
    ob = outline.bounds
    x0, y0, x1, y1 = max(x0, ob[0]), max(y0, ob[1]), min(x1, ob[2]), min(y1, ob[3])
    nx, ny = int((x1 - x0) / grid) + 1, int((y1 - y0) / grid) + 1
    xs = x0 + np.arange(nx) * grid
    ys = y0 + np.arange(ny) * grid
    X, Y = np.meshgrid(xs, ys)               # [iy, ix]
    win = box(x0, y0, x1, y1)
    inside = outline.buffer(-(edge + w / 2))
    free = shapely.contains_xy(inside, X, Y)
    obs = [g for g in obstacles(board, net, layer) if g.intersects(win.buffer(1.0))]
    if obs:
        blk = unary_union(obs).buffer(clr + w / 2, 8)
        free &= ~shapely.contains_xy(blk, X, Y)
    goal_cells = shapely.contains_xy(goal.buffer(w / 2 + 1e-6), X, Y)
    free |= goal_cells

    def cell(x, y):
        return int(round((y - y0) / grid)), int(round((x - x0) / grid))

    si, sj = cell(sx, sy)
    if not (0 <= si < ny and 0 <= sj < nx):
        return None
    free[si, sj] = True
    gc = goal.centroid
    gi, gj = cell(gc.x, gc.y)
    D8 = [(-1, 0, 1.0), (1, 0, 1.0), (0, -1, 1.0), (0, 1, 1.0),
          (-1, -1, 1.4142), (-1, 1, 1.4142), (1, -1, 1.4142), (1, 1, 1.4142)]

    def h(i, j):
        di, dj = abs(i - gi), abs(j - gj)
        return (di + dj) + (1.4142 - 2) * min(di, dj)

    best = {(si, sj, -1): 0.0}
    prev = {}
    pq = [(h(si, sj), 0.0, si, sj, -1)]
    end = None
    while pq:
        f, g, i, j, d = heapq.heappop(pq)
        if goal_cells[i, j]:
            end = (i, j, d)
            break
        if g > best.get((i, j, d), 1e18) + 1e-9:
            continue
        for k, (di, dj, c) in enumerate(D8):
            a, b = i + di, j + dj
            if not (0 <= a < ny and 0 <= b < nx) or not free[a, b]:
                continue
            ng = g + c + (0.0 if k == d or d < 0 else 0.5)      # penalita' sui cambi di direzione
            key = (a, b, k)
            if ng < best.get(key, 1e18) - 1e-9:
                best[key] = ng
                prev[key] = (i, j, d)
                heapq.heappush(pq, (ng + h(a, b), ng, a, b, k))
    if end is None:
        return None
    cells = [end]
    while cells[-1][:2] != (si, sj) or cells[-1][2] != -1:
        cells.append(prev[cells[-1]])
    cells.reverse()
    pts = [(x0 + j * grid, y0 + i * grid) for i, j, _ in cells]
    pts[0] = (sx, sy)
    # semplifica: tieni solo i vertici dove cambia direzione
    out = [pts[0]]
    for k in range(1, len(pts) - 1):
        (ax, ay), (bx, by), (cx, cy) = out[-1], pts[k], pts[k + 1]
        if abs((bx - ax) * (cy - by) - (by - ay) * (cx - bx)) > 1e-9:
            out.append(pts[k])
    out.append(pts[-1])
    if goal_point is not None:              # fino al centro della via / piazzola di arrivo
        out.append(tuple(goal_point))
    return out
