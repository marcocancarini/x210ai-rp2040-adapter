# -*- coding: utf-8 -*-
"""BOM per JLCPCB (formato "Comment, Designator, Footprint, LCSC Part #") e BOM completa con MPN, per la
Board A e la Board B della rev 2.2, dal solo modello dati (non serve KiCad).

uso: python3 gen_bom_rev22.py <out_dir>

La CPL (posizioni e rotazioni) NON si genera qui: dipende dal PCB sbrogliato; la produce export_prod.py.
"""
import csv
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import design_boardA as A  # noqa: E402
import design_boardB as B  # noqa: E402


def key(ref):
    return ref[0], int(re.sub(r"\D", "", ref) or 0)


def rows(D, board):
    out = []
    for c in sorted(D.COMP, key=lambda c: key(c["ref"])):
        side = "Top" if D.PLACE[c["ref"]][3] == "T" else "Bottom"
        fp = c["fp"].split(":")[1]
        if board == "B" and c["ref"] == "J1" and hasattr(D, "J1_PARTS"):
            for s, v, lcsc, mpn, mfr, how in D.J1_PARTS:
                out.append(dict(ref="J1", value=v, fp=fp, lcsc=lcsc, mpn=mpn, mfr=mfr, side=s, how=how,
                                desc=c["desc"]))
            continue
        lcsc, mpn, mfr = D.PARTS.get(c["value"], ("", "", ""))
        how = "DNP" if c["ref"] in D.DNP else ("no (solo rame)" if c["ref"] in D.NOT_ASSEMBLED else "si")
        out.append(dict(ref=c["ref"], value=c["value"], fp=fp, lcsc=lcsc, mpn=mpn, mfr=mfr, side=side, how=how,
                        desc=c["desc"]))
    return out


def write(out, board, rs):
    sel = [r for r in rs if r["how"] == "si"]
    missing = [r["ref"] for r in sel if not r["lcsc"]]
    assert not missing, f"Board {board}: codice LCSC mancante per {missing}"
    groups = {}
    for r in sel:
        groups.setdefault((r["value"], r["fp"], r["lcsc"]), []).append(r["ref"])
    p1 = os.path.join(out, f"x210ai_rev2.2_board{board}_bom_jlcpcb.csv")
    with open(p1, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["Comment", "Designator", "Footprint", "LCSC Part #"])
        for (v, fp, lcsc), refs in groups.items():
            w.writerow([v, ",".join(refs), fp, lcsc])
    p2 = os.path.join(out, f"x210ai_rev2.2_board{board}_bom_completa_mpn.csv")
    with open(p2, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["Designator", "Value", "Manufacturer", "MPN", "LCSC", "Footprint", "Side", "Assembly", "Note"])
        for r in rs:
            w.writerow([r["ref"], r["value"], r["mfr"], r["mpn"], r["lcsc"], r["fp"], r["side"], r["how"], r["desc"]])
    return len(sel), len(groups), [r["ref"] + " " + r["value"] for r in rs if r["how"] != "si"]


def main():
    out = sys.argv[1]
    os.makedirs(out, exist_ok=True)
    for board, D in (("A", A), ("B", B)):
        n, g, other = write(out, board, rows(D, board))
        print(f"Board {board}: {n} componenti montati da JLCPCB in {g} righe; non montati: {other}")


if __name__ == "__main__":
    main()
