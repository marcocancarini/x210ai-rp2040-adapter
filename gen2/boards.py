# -*- coding: utf-8 -*-
"""Scelta della scheda e compatibilita' KiCad per gli script di gen2.

Ogni script accetta "--board A" o "--board B" (rev 2.2) o "--board C" (rev 2.3) in qualunque punto della riga di comando, oppure la
variabile d'ambiente X210_BOARD; senza indicazioni usa la rev 2.0 (design2.py).
Le funzioni kc_* coprono le differenze dell'API pcbnew tra KiCad 7 e KiCad 9/10.
"""
import glob
import importlib
import os
import sys

MODULES = {"A": "design_boardA", "B": "design_boardB", "C": "design_boardC", "2.0": "design2"}


def pick(argv=None):
    """legge e toglie "--board X" da sys.argv; ritorna "A", "B" o "2.0" """
    argv = sys.argv if argv is None else argv
    name = os.environ.get("X210_BOARD", "2.0")
    if "--board" in argv:
        i = argv.index("--board")
        name = argv[i + 1]
        del argv[i:i + 2]
    name = name.upper().replace("BOARD", "").strip() if name.upper() != "2.0" else "2.0"
    if name not in MODULES:
        raise SystemExit(f"--board {name}: valori ammessi A, B, C, 2.0")
    os.environ["X210_BOARD"] = name          # cosi' gli script importati (build_pcb da fill_zones) lo ritrovano
    return name


def load(argv=None):
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    return importlib.import_module(MODULES[pick(argv)])


def project_name(D):
    return getattr(D, "PROJECT", "x210ai")


def kicad_share(sub):
    """cartella condivisa di KiCad (footprints, symbols): variabili KICADn_*_DIR, poi i percorsi tipici"""
    kind = {"footprints": "FOOTPRINT", "symbols": "SYMBOL"}[sub]
    for v in ("10", "9", "8", "7"):
        p = os.environ.get(f"KICAD{v}_{kind}_DIR")
        if p and os.path.isdir(p):
            return p
    cands = sorted(glob.glob(f"C:/Program Files/KiCad/*/share/kicad/{sub}"), reverse=True)
    cands += [f"/usr/share/kicad/{sub}", f"/usr/local/share/kicad/{sub}",
              f"/Applications/KiCad/KiCad.app/Contents/SharedSupport/{sub}"]
    for p in cands:
        if os.path.isdir(p):
            return p
    raise SystemExit(f"cartella KiCad '{sub}' non trovata: imposta KICAD10_{kind}_DIR")


# ---------------------------------------------------------------- compatibilita' pcbnew
def kc_flip(fp):
    """ribalta sul lato B sopra/sotto (KiCad 7-8: Flip(pos, False); KiCad 9+: FLIP_DIRECTION)"""
    import pcbnew
    d = getattr(pcbnew, "FLIP_DIRECTION_TOP_BOTTOM", None)
    if d is None:
        names = [n for n in dir(pcbnew) if "FLIP_DIRECTION" in n and "TOP_BOTTOM" in n]
        d = getattr(pcbnew, names[0]) if names else None
    if d is None:
        fp.Flip(fp.GetPosition(), False)
    else:
        fp.Flip(fp.GetPosition(), d)
    assert fp.IsFlipped(), fp.GetReference()


def kc_set_field(fp, name, value):
    if hasattr(fp, "SetField"):
        fp.SetField(name, value)
        # KiCad 8+ crea il campo visibile sulla serigrafia: e' un dato per la BOM, non va stampato
        for fld in fp.GetFields():
            if fld.GetName() == name:
                fld.SetVisible(False)
    else:
        fp.SetProperty(name, value)


def kc_get_field(fp, name):
    if hasattr(fp, "HasField"):
        get = getattr(fp, "GetFieldText", None) or fp.GetFieldShownText
        return get(name) if fp.HasField(name) else ""
    return fp.GetProperty(name) if fp.HasProperty(name) else ""
