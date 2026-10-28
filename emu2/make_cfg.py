# -*- coding: utf-8 -*-
"""Configurazione per l'emulatore: indirizzi dei simboli, GPIO, elenco tasti con codice atteso.

uso: python3 make_cfg.py <firmware.elf> <keycodes.h> <catena_tasti_dettaglio.json> <out.json>
"""
import glob
import json
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "gen2"))
import design2 as D  # noqa: E402

elf, kc_h, catena, out = sys.argv[1:5]

nm = glob.glob(os.path.join(HERE, "..", "tools", "arduino", "data", "packages", "rp2040", "tools", "pqt-gcc",
                            "*", "bin", "arm-none-eabi-nm"))[0]
syms = {}
for l in subprocess.run([nm, "-S", "-C", elf], capture_output=True, text=True).stdout.splitlines():
    p = l.split()
    if len(p) >= 4:
        syms[p[3]] = (int(p[0], 16), int(p[1], 16))
    elif len(p) == 3:
        syms[p[2]] = (int(p[0], 16), 0)
want = ["old_key", "KB", "SWAP_FN_CTRL", "EC", "jis_pos", "jis_learn", "TP", "_EEPROM_start", "tv_armed"]
S = {k: syms[k][0] for k in want if k in syms}
missing = [k for k in want if k not in syms]

# ---- valori dei codici tasto (keycodes.h, con riferimenti tra nomi)
defs = {}
for l in open(kc_h, encoding="utf-8", errors="ignore"):
    m = re.match(r"\s*#define\s+(\w+)\s+(.+?)\s*(//.*)?$", l.rstrip("\r\n"))
    if m:
        defs[m.group(1)] = m.group(2)


def val(name, depth=0):
    e = defs[name]
    e = re.sub(r"/\*.*?\*/", "", e)
    for tok in sorted(set(re.findall(r"[A-Za-z_]\w*", e)), key=len, reverse=True):
        if tok in defs:
            e = re.sub(r"\b%s\b" % tok, "(%d)" % val(tok, depth + 1), e)
    return int(eval(e, {}, {}))


cat = json.load(open(catena))
keys = []
for k in cat:
    name, rp, cp, _, _, r, c, code = k[:8]
    keys.append({"name": name, "rowPin": rp, "colPin": cp, "r": r, "c": c, "code": code,
                 "value": val(code) if code in defs else None,
                 "gr": D.SIGNAL_GPIO[f"KB_R{rp}"], "gc": D.SIGNAL_GPIO[f"KB_C{cp}"]})

used = {(k["r"], k["c"]) for k in keys}
empty = [(r, c) for r in range(16) for c in range(8) if (r, c) not in used]

G = D.SIGNAL_GPIO
cfg = {
    "symbols": S, "missing_symbols": missing,
    "rows": D.ROW_IO, "cols": D.COL_IO,
    "fn": G["KB_FN"], "tp_clk": G["TP_CLK_3V3"], "tp_data": G["TP_DATA_3V3"], "tp_rst": G["TP_RST_3V3"],
    "ec_fn": G["EC_FN_G"], "ec_pgup": G["EC_PGUP_G"],
    "keys": keys,
    "special": {"pgup": [24, 5], "lctrl": [30, 5], "thinkvantage": [16, 3], "f5": [6, 3], "esc": [22, 3]},
    "empty_positions": empty,
    "codes": {n: val(n) for n in ["KEY_INTERNATIONAL1", "KEY_PAGE_UP", "MODIFIERKEY_LEFT_CTRL", "KEY_F5",
                                  "KEY_THINKLIGHT", "KEY_THINK_VANTAGE", "KEY_ESC"]},
    "eeprom_flash_offset": (S["_EEPROM_start"] - 0x10000000) if "_EEPROM_start" in S else 0x200000 - 4096,
    "eeprom_preset": [0x5A, 0] + [0] * 6 + [0xFF] * 10,
    "signal_gpio": G,
}
json.dump(cfg, open(out, "w"), indent=1)
print(f"{len(keys)} tasti, {len(empty)} posizioni vuote, simboli {S}, mancanti {missing}")
