# -*- coding: utf-8 -*-
"""Regole di progetto e classi di net nel file .kicad_pro (KiCad 7 lo riscrive con i default al salvataggio)."""
import json

RULES = {
    "min_clearance": 0.1,
    "min_track_width": 0.1,
    "min_via_diameter": 0.35,
    "min_via_annular_width": 0.075,
    "min_through_hole_diameter": 0.2,
    "min_hole_to_hole": 0.25,
    "min_hole_clearance": 0.2,
    "min_copper_edge_clearance": 0.25,
    "min_silk_clearance": 0.0,
    "min_text_height": 0.6,
    "min_text_thickness": 0.08,
    "min_microvia_diameter": 0.2,
    "min_microvia_drill": 0.1,
    "solder_mask_clearance": 0.0,
    "solder_mask_min_width": 0.0,
    "use_height_for_length_calcs": True,
    "allow_blind_buried_vias": False,
    "allow_microvias": False,
}

NETCLASSES = [
    {"name": "Default", "clearance": 0.1, "track_width": 0.1, "via_diameter": 0.4, "via_drill": 0.2,
     "microvia_diameter": 0.3, "microvia_drill": 0.1, "diff_pair_gap": 0.15, "diff_pair_width": 0.15,
     "diff_pair_via_gap": 0.25, "bus_width": 12, "line_style": 0, "pcb_color": "rgba(0, 0, 0, 0.000)",
     "schematic_color": "rgba(0, 0, 0, 0.000)", "wire_width": 6, "priority": 2147483647},
    {"name": "Power", "clearance": 0.1, "track_width": 0.2, "via_diameter": 0.4, "via_drill": 0.2,
     "microvia_diameter": 0.3, "microvia_drill": 0.1, "diff_pair_gap": 0.15, "diff_pair_width": 0.15,
     "diff_pair_via_gap": 0.25, "bus_width": 12, "line_style": 0, "pcb_color": "rgba(0, 0, 0, 0.000)",
     "schematic_color": "rgba(0, 0, 0, 0.000)", "wire_width": 6, "priority": 0},
]
POWER_PATTERNS = ["GND", "+3V3", "VBUS", "+1V1"]

IGNORE = ["silk_edge_clearance", "silk_overlap", "silk_over_copper", "text_height", "text_thickness",
          "lib_footprint_mismatch"]


def write(pro_path, via=(0.4, 0.2)):
    """via = (diametro, foro) della classe di default: 0,4/0,2 JLCPCB; 0,3/0,15 Board B (JLCPCB 0,4 mm)"""
    d = json.load(open(pro_path))
    ds = d.setdefault("board", {}).setdefault("design_settings", {})
    rules = dict(RULES)
    rules["min_via_diameter"] = min(RULES["min_via_diameter"], via[0])
    rules["min_through_hole_diameter"] = min(RULES["min_through_hole_diameter"], via[1])
    ds.setdefault("rules", {}).update(rules)
    ds["track_widths"] = [0.0, 0.1, 0.15, 0.2, 0.3]
    ds["via_dimensions"] = [{"diameter": 0.0, "drill": 0.0}, {"diameter": via[0], "drill": via[1]},
                            {"diameter": 0.5, "drill": 0.25}]
    for c in NETCLASSES:
        c["via_diameter"], c["via_drill"] = via
    sev = ds.setdefault("rule_severities", {})
    for k in IGNORE:
        sev[k] = "ignore"
    ns = d.setdefault("net_settings", {})
    ns["classes"] = NETCLASSES
    ns["netclass_patterns"] = [{"netclass": "Power", "pattern": p} for p in POWER_PATTERNS]
    ns.setdefault("meta", {})["version"] = 3
    json.dump(d, open(pro_path, "w"), indent=2)


if __name__ == "__main__":
    import sys
    write(sys.argv[1])
