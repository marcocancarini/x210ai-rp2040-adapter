# -*- coding: utf-8 -*-
"""Genera x210ai_pins.h dal modello dati: python gen_fw_pins.py [--board A] <sketch_dir>
(la Board A ha gli stessi GPIO della rev 2.0: cambia solo il commento in testa)"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import boards  # noqa: E402

D = boards.load()
assert hasattr(D, "SIGNAL_GPIO"), "il firmware gira sulla Board A: usa --board A"

out = os.path.join(sys.argv[1], "x210ai_pins.h")
G = D.SIGNAL_GPIO
txt = f"""// x210ai_pins.h - generato da gen2/gen_fw_pins.py (scheda-ponte X210Ai rev {D.REV}, {D.DATE})
// Non modificare a mano: i GPIO seguono il PCB.
#pragma once

// righe della matrice nell'ordine del firmware (pin connettore tastiera {D.FW_ROW_PINS})
#define X210_ROW_IO {{ {", ".join(map(str, D.ROW_IO))} }}
// colonne (pin connettore {D.FW_COL_PINS})
#define X210_COL_IO {{ {", ".join(map(str, D.COL_IO))} }}

#define X210_FN_PIN        {G["KB_FN"]}   // Fn, pin 1 del connettore (attivo basso)
#define X210_TP_DATA_PIN   {G["TP_DATA_3V3"]}  // PS/2 data TrackPoint (via BSS138)
#define X210_TP_CLOCK_PIN  {G["TP_CLK_3V3"]}  // PS/2 clock TrackPoint (via BSS138)
#define X210_TP_RESET_PIN  {G["TP_RST_3V3"]}  // reset TrackPoint, attivo alto (via BSS138)
#define X210_EC_FN_PIN     {G["EC_FN_G"]}  // gate Q2b: porta a massa il Fn della scheda madre
#define X210_EC_PGUP_PIN   {G["EC_PGUP_G"]}  // gate Q3: chiude riga 24 - colonna 5 (PgUp) verso l'EC
"""
open(out, "w").write(txt)
print(out)
