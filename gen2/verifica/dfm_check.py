"""Manufacturing (DFM) measurements on the delivered board, compared with JLCPCB multilayer limits.

usage: python3 dfm_check.py <board.kicad_pcb>  -> prints JSON
"""
import sys, json, math, itertools
import pcbnew
from pcbnew import ToMM
from shapely.geometry import Point, LineString, box, Polygon, MultiPolygon
from shapely.ops import unary_union

b = pcbnew.LoadBoard(sys.argv[1])
res = {}


def via_w(v):
    """diametro del via: KiCad 10 vuole lo strato (padstack), KiCad 7-9 no"""
    try:
        return ToMM(v.GetWidth(pcbnew.F_Cu))
    except TypeError:
        return ToMM(v.GetWidth())


# ---------------------------------------------------------------- board outline
edge = [d for d in b.GetDrawings() if d.GetLayer() == pcbnew.Edge_Cuts]
bb = b.GetBoardEdgesBoundingBox()
outline = None
ol = pcbnew.SHAPE_POLY_SET()
try:
    ok = b.GetBoardPolygonOutlines(ol, False)     # KiCad 10: aInferOutlineIfNecessary obbligatorio
except TypeError:
    ok = b.GetBoardPolygonOutlines(ol)            # KiCad 7-9
if ok:
    o = ol.Outline(0)
    outline = Polygon([(ToMM(o.CPoint(i).x), ToMM(o.CPoint(i).y)) for i in range(o.PointCount())])
res["board_mm"] = [round(outline.bounds[2] - outline.bounds[0], 3), round(outline.bounds[3] - outline.bounds[1], 3)]
res["thickness_mm"] = round(ToMM(b.GetDesignSettings().GetBoardThickness()), 3)
res["copper_layers"] = b.GetCopperLayerCount()

# ---------------------------------------------------------------- tracks / vias / holes
tracks = [t for t in b.GetTracks() if t.GetClass() == "PCB_TRACK"]
vias = [t for t in b.GetTracks() if t.GetClass() == "PCB_VIA"]
res["min_track_mm"] = round(min(ToMM(t.GetWidth()) for t in tracks), 3)
res["via_sizes"] = sorted({(round(via_w(v), 3), round(ToMM(v.GetDrillValue()), 3)) for v in vias})
res["min_via_annular_mm"] = round(min((via_w(v) - ToMM(v.GetDrillValue())) / 2 for v in vias), 3)
holes = [(ToMM(v.GetPosition().x), ToMM(v.GetPosition().y), ToMM(v.GetDrillValue()) / 2, "via") for v in vias]
pth_annular = []
smd_min = []
for fp in b.GetFootprints():
    for p in fp.Pads():
        if p.GetDrillSize().x > 0:
            holes.append((ToMM(p.GetPosition().x), ToMM(p.GetPosition().y), ToMM(p.GetDrillSize().x) / 2, fp.GetReference()))
            pth_annular.append(((ToMM(min(p.GetSize().x, p.GetSize().y)) - ToMM(p.GetDrillSize().x)) / 2, fp.GetReference()))
        else:
            smd_min.append((round(ToMM(min(p.GetSize().x, p.GetSize().y)), 3), fp.GetReference()))
res["min_drill_mm"] = round(min(h[2] * 2 for h in holes), 3)
res["min_pth_pad_annular_mm"] = [round(min(pth_annular)[0], 3), min(pth_annular)[1]] if pth_annular else None
res["min_smd_pad_dimension_mm"] = min(smd_min)
hh = min(((math.hypot(a[0] - c[0], a[1] - c[1]) - a[2] - c[2]), a[3], c[3]) for a, c in itertools.combinations(holes, 2))
res["min_hole_to_hole_edge_mm"] = [round(hh[0], 3), hh[1], hh[2]]
res["hole_count"] = len(holes)

# ---------------------------------------------------------------- copper to edge (all copper layers)
def pad_poly(p):
    bbp = p.GetBoundingBox()
    return box(ToMM(bbp.GetLeft()), ToMM(bbp.GetTop()), ToMM(bbp.GetRight()), ToMM(bbp.GetBottom()))
cu = []
for t in tracks:
    cu.append(LineString([(ToMM(t.GetStart().x), ToMM(t.GetStart().y)), (ToMM(t.GetEnd().x), ToMM(t.GetEnd().y))]).buffer(ToMM(t.GetWidth()) / 2))
for v in vias:
    cu.append(Point(ToMM(v.GetPosition().x), ToMM(v.GetPosition().y)).buffer(via_w(v) / 2))
for fp in b.GetFootprints():
    for p in fp.Pads():
        cu.append(pad_poly(p))
for z in b.Zones():
    if z.GetIsRuleArea():
        continue
    for layer in z.GetLayerSet().Seq():
        fpoly = z.GetFilledPolysList(layer)
        for i in range(fpoly.OutlineCount()):
            o = fpoly.Outline(i)
            pts = [(ToMM(o.CPoint(k).x), ToMM(o.CPoint(k).y)) for k in range(o.PointCount())]
            if len(pts) >= 3:
                cu.append(Polygon(pts))
edge_line = outline.exterior
res["min_copper_to_edge_mm"] = round(min(edge_line.distance(g) for g in cu), 3)

# ---------------------------------------------------------------- solder-mask webs (between different openings)
def mask_open(p, layer):
    if not p.IsOnLayer(layer):
        return None
    try:
        m = ToMM(p.GetSolderMaskExpansion(layer))     # KiCad 10
    except TypeError:
        m = ToMM(p.GetSolderMaskExpansion())          # KiCad 7-9
    return pad_poly(p).buffer(m, join_style=2)
for side, layer in (("top", pcbnew.F_Mask), ("bottom", pcbnew.B_Mask)):
    opens = [(fp.GetReference() + "." + p.GetNumber(), mask_open(p, layer)) for fp in b.GetFootprints() for p in fp.Pads()]
    opens = [(n, g) for n, g in opens if g is not None]
    best = (9, None, None)
    for (n1, g1), (n2, g2) in itertools.combinations(opens, 2):
        if n1.split(".")[0] == n2.split(".")[0] and n1.split(".")[1] == n2.split(".")[1]:
            continue
        d = g1.distance(g2)
        if 0 < d < best[0]:
            best = (round(d, 3), n1, n2)
    res["min_mask_web_%s_mm" % side] = list(best)

# ---------------------------------------------------------------- silkscreen
silk_lines, silk_texts = [], []
def add_item(it, ref):
    if it.GetLayer() not in (pcbnew.F_SilkS, pcbnew.B_SilkS):
        return
    cls = it.GetClass()
    if "TEXT" in cls or "FIELD" in cls:
        if hasattr(it, "IsVisible") and not it.IsVisible():
            return
        silk_texts.append((round(ToMM(it.GetTextHeight()), 3), round(ToMM(it.GetTextThickness()), 3), ref, it.GetText()))
    else:
        w = ToMM(it.GetWidth())
        if w > 0:
            silk_lines.append((round(w, 3), ref, cls))
for fp in b.GetFootprints():
    fields = list(fp.GetFields()) if hasattr(fp, "GetFields") else [fp.Reference(), fp.Value()]
    for it in list(fp.GraphicalItems()) + fields:
        add_item(it, fp.GetReference())
for d in b.GetDrawings():
    add_item(d, "board")
res["silk_line_widths_mm"] = sorted({w for w, _, _ in silk_lines})
res["silk_lines_below_0.15"] = sorted({r for w, r, _ in silk_lines if w < 0.15})
res["silk_text_heights_mm"] = sorted({h for h, _, _, _ in silk_texts})
res["silk_text_strokes_mm"] = sorted({t for _, t, _, _ in silk_texts})
res["silk_texts_below_1.0"] = len([1 for h, _, _, _ in silk_texts if h < 1.0])
res["silk_texts_total"] = len(silk_texts)
print(json.dumps(res, indent=1))
