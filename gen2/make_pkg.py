# -*- coding: utf-8 -*-
"""Assembla il pacchetto di consegna rev 2.2 (sostituisce make_pkg.sh della rev 2.0).

uso (dalla cartella del progetto, dopo pipeline.py per entrambe le schede):
    python gen2/make_pkg.py
Crea x210ai_iso_adapter_kicad_rev2.2.zip; segnala i pezzi mancanti invece di fermarsi.
"""
import glob
import os
import shutil
import sys
import zipfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PKG = "x210ai_iso_adapter_rev2.2"
missing = []


def put(src_glob, dst_dir, rename=None):
    files = sorted(glob.glob(os.path.join(ROOT, src_glob)))
    if not files:
        missing.append(src_glob)
    for f in files:
        d = os.path.join(ROOT, "pkg", PKG, dst_dir)
        os.makedirs(d, exist_ok=True)
        if os.path.isdir(f):
            shutil.copytree(f, os.path.join(d, os.path.basename(f)), dirs_exist_ok=True)
        else:
            shutil.copy(f, os.path.join(d, rename or os.path.basename(f)))


def main():
    shutil.rmtree(os.path.join(ROOT, "pkg"), ignore_errors=True)
    for b in "AB":
        o = f"out_board{b}"
        for ext in ("kicad_pro", "kicad_sch", "kicad_pcb"):
            put(f"{o}/x210ai_board{b}.{ext}", f"board{b}")
        put(f"{o}/x210ai.pretty", f"board{b}")
        put(f"{o}/fp-lib-table", f"board{b}")
        put(f"{o}/drc.rpt", f"verifica/board{b}")
        put(f"{o}/erc.json", f"verifica/board{b}")
        put(f"{o}/parity.json", f"verifica/board{b}")
        put(f"produzione/board{b}/*.zip", f"produzione/board{b}")
        put(f"produzione/board{b}/*.csv", f"produzione/board{b}")
    put("produzione/*.csv", "produzione/bom_da_modello")
    for f in ("CABLE_SPEC.md", "REPORT_rev2.2.md", "LEGGIMI.md", "FIRMWARE.md", "VERIFICA.md",
              "x210ai_dima_boardA_1a1.pdf", "x210ai_dima_boardB_1a1.pdf"):
        put(f"doc/{f}", "documentazione")
    put("fw3/ThinkPad_RP2040_Keyboard", "firmware")
    put("fw3/out/ThinkPad_RP2040_Keyboard.ino.uf2", "firmware", "x210ai_rev2.2.uf2")
    put("spice2/*", "verifica/spice")
    put("emu2/run_fw2.js", "verifica/emulazione")
    put("emu2/make_cfg.py", "verifica/emulazione")
    put("gen2/*.py", "sorgenti/gen2")
    put("gen2/verifica/*.py", "sorgenti/gen2/verifica")
    put("gen2/lib/x210ai.pretty", "sorgenti/gen2/lib")
    put("riferimenti/T61/T61.brd", "sorgenti/riferimenti")
    zpath = os.path.join(ROOT, "x210ai_iso_adapter_kicad_rev2.2.zip")
    with zipfile.ZipFile(zpath, "w", zipfile.ZIP_DEFLATED) as z:
        base = os.path.join(ROOT, "pkg")
        for dp, _, fs in os.walk(base):
            for f in fs:
                p = os.path.join(dp, f)
                z.write(p, os.path.relpath(p, base))
    shutil.rmtree(os.path.join(ROOT, "pkg"))
    print("ok", zpath, round(os.path.getsize(zpath) / 1e6, 2), "MB")
    if missing:
        print("MANCANO (esegui prima pipeline.py per la scheda corrispondente):")
        for m in missing:
            print("  ", m)
        sys.exit(1)


if __name__ == "__main__":
    main()
