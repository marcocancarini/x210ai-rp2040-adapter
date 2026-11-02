# -*- coding: utf-8 -*-
"""Esegue in ordine tutti i passi da schema a file di produzione per una scheda della rev 2.2.

uso (dalla cartella del progetto, con il Python di KiCad):
    python gen2/pipeline.py --board A                  tutti i passi
    python gen2/pipeline.py --board B --da route       riparte da un passo
    python gen2/pipeline.py --board A --solo sch,erc   solo alcuni passi

Passi: sch erc netlist pcb dsn route ses fill drc check prod verify dima
Uscite: out_boardA/ (progetto KiCad x210ai_boardA.*, report) e produzione/boardA/ (Gerber, BOM, CPL).

Programmi esterni:
  kicad-cli    nel PATH, oppure KICAD_CLI=<percorso>   (cercato anche in C:/Program Files/KiCad/*/bin)
  Freerouting  FREEROUTING_JAR=<percorso del .jar>     (default: freerouting-1.9.0.jar nella cartella del progetto)
  Java         java nel PATH, oppure JAVA=<percorso>
"""
import glob
import os
import re
import shutil
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
import boards  # noqa: E402

STEPS = ["sch", "erc", "netlist", "pcb", "dsn", "route", "ses", "fill", "drc", "check", "prod", "verify", "dima"]
NEEDS_PCBNEW = {"pcb", "dsn", "ses", "fill", "check", "prod", "verify"}


def kicad_cli():
    p = os.environ.get("KICAD_CLI") or shutil.which("kicad-cli")
    if not p:
        c = sorted(glob.glob("C:/Program Files/KiCad/*/bin/kicad-cli.exe"), reverse=True)
        p = c[0] if c else None
    if not p:
        raise SystemExit("kicad-cli non trovato: aggiungilo al PATH o imposta KICAD_CLI")
    return p


def run(cmd, ok_codes=(0,)):
    print("\n>>", " ".join(f'"{c}"' if " " in c else c for c in cmd), flush=True)
    r = subprocess.run(cmd, cwd=ROOT)
    if r.returncode not in ok_codes:
        raise SystemExit(f"passo fallito (codice {r.returncode})")


def main():
    argv = list(sys.argv)
    board = boards.pick(argv)
    if board == "2.0":
        raise SystemExit("indica la scheda: --board A, --board B oppure --board C")
    D = boards.load(["x", "--board", board])
    steps = STEPS
    if "--da" in argv:
        steps = STEPS[STEPS.index(argv[argv.index("--da") + 1]):]
    if "--solo" in argv:
        steps = [s for s in argv[argv.index("--solo") + 1].split(",")]
    bad = [s for s in steps if s not in STEPS]
    if bad:
        raise SystemExit(f"passi sconosciuti {bad}; validi: {STEPS}")
    if NEEDS_PCBNEW & set(steps):
        try:
            import pcbnew  # noqa: F401
        except ImportError:
            raise SystemExit("pcbnew non importabile: esegui con il Python di KiCad, ad es.\n"
                             '  "C:\\Program Files\\KiCad\\10.0\\bin\\python.exe" gen2\\pipeline.py --board '
                             f"{board}\n(prima: ... python.exe -m pip install shapely matplotlib gerbonara)")

    py = sys.executable
    name = boards.project_name(D)
    out = os.path.join("out_board" + board)
    prod = os.path.join("produzione", "board" + board)
    os.makedirs(os.path.join(ROOT, out, "stadi"), exist_ok=True)
    sch, pcb = os.path.join(out, name + ".kicad_sch"), os.path.join(out, name + ".kicad_pcb")
    xml, dsn, ses = (os.path.join(out, name + e) for e in (".xml", ".dsn", ".ses"))
    g = lambda s: os.path.join("gen2", s)  # noqa: E731
    b = ["--board", board]

    for s in steps:
        print(f"\n===== Board {board}: {s} =====", flush=True)
        if s == "sch":
            run([py, g("gen_sch2.py"), *b, os.path.join("sch", "x210ai.kicad_sch"), sch])
        elif s == "erc":
            run([kicad_cli(), "sch", "erc", "--format", "json", "--severity-all",
                 "--output", os.path.join(out, "erc.json"), sch])
        elif s == "netlist":
            run([kicad_cli(), "sch", "export", "netlist", "--format", "kicadxml", "--output", xml, sch])
        elif s == "pcb":
            run([py, g("build_pcb.py"), *b, out])
            shutil.copy(os.path.join(ROOT, pcb), os.path.join(ROOT, out, "stadi", "01_piazzato.kicad_pcb"))
        elif s == "dsn":
            run([py, g("build_pcb.py"), *b, "--dsn", pcb, dsn])
        elif s == "route":
            jar = os.environ.get("FREEROUTING_JAR", os.path.join(ROOT, "freerouting-1.9.0.jar"))
            if not os.path.exists(jar):
                raise SystemExit(f"Freerouting non trovato ({jar}): imposta FREEROUTING_JAR")
            extra = []
            if re.search(r"freerouting-([2-9])\.", os.path.basename(jar)):   # 2.x: senza finestra (Linux headless)
                extra = ["--gui.enabled=false"]
            run([os.environ.get("JAVA", "java"), "-jar", jar, "-de", dsn, "-do", ses, "-mp", os.environ.get("FREEROUTING_PASSES", "100"), *extra])
        elif s == "ses":
            run([py, g("import_ses.py"), pcb, ses, pcb])
            run([py, g("cleanup_pcb.py"), pcb, pcb])
            shutil.copy(os.path.join(ROOT, pcb), os.path.join(ROOT, out, "stadi", "02_sbrogliato.kicad_pcb"))
        elif s == "fill":
            run([py, g("fill_zones.py"), *b, pcb, pcb, "--pour", "F,B"])
        elif s == "drc":
            run([kicad_cli(), "pcb", "drc", "--format", "json", "--severity-all",
                 "--output", os.path.join(out, "drc.json"), pcb])
            run([kicad_cli(), "pcb", "drc", "--output", os.path.join(out, "drc.rpt"), pcb])
        elif s == "check":
            run([py, g("netlist_check.py"), *b, xml, pcb, os.path.join(out, "parity.json")])
        elif s == "prod":
            run([py, g("export_prod.py"), *b, pcb, prod])
        elif s == "verify":
            cpl = os.path.join(prod, f"x210ai_rev{D.REV}_board{board}_cpl_jlcpcb_bottom_e_top.csv")
            run([py, g(os.path.join("verifica", "gerber_check2.py")), os.path.join(prod, "gerber"), cpl])
            run([py, g(os.path.join("verifica", "dfm_check.py")), pcb])
        elif s == "dima":
            if board == "C":     # dima della forma v3.2 (contorno della Board C)
                run([py, g("gen_dima_giro.py"), "--rot90ccw", "--v32"])
            elif board == "B":     # Board B a scalino: dima e legenda di tutti i componenti
                run([py, g("gen_dima_boardB_scalino.py"), os.path.join("doc", "x210ai_dima_boardB_scalino_1a1.pdf")])
            else:
                run([py, g("gen_dima_rev22.py"), board, os.path.join("doc", f"x210ai_dima_board{board}_1a1.pdf")])
    print(f"\nfatto: {', '.join(steps)}. Progetto KiCad: {out}/{name}.kicad_pro")


if __name__ == "__main__":
    main()
