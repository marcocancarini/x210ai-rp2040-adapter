// x210ai_pins.h - generato da gen2/gen_fw_pins.py (scheda-ponte X210Ai rev 2.0, 2026-10-21)
// Non modificare a mano: i GPIO seguono il PCB.
#pragma once

// righe della matrice nell'ordine del firmware (pin connettore tastiera [32, 28, 20, 16, 12, 8, 4, 22, 26, 30, 18, 14, 10, 6, 2, 24])
#define X210_ROW_IO { 9, 11, 15, 17, 19, 21, 23, 14, 12, 10, 16, 18, 20, 22, 24, 13 }
// colonne (pin connettore [5, 9, 13, 17, 15, 11, 7, 3])
#define X210_COL_IO { 6, 4, 2, 0, 1, 3, 5, 7 }

#define X210_FN_PIN        8   // Fn, pin 1 del connettore (attivo basso)
#define X210_TP_DATA_PIN   29  // PS/2 data TrackPoint (via BSS138)
#define X210_TP_CLOCK_PIN  28  // PS/2 clock TrackPoint (via BSS138)
#define X210_TP_RESET_PIN  25  // reset TrackPoint, attivo alto (via BSS138)
#define X210_EC_FN_PIN     26  // gate Q2b: porta a massa il Fn della scheda madre
#define X210_EC_PGUP_PIN   27  // gate Q3: chiude riga 24 - colonna 5 (PgUp) verso l'EC
