# Riferimenti

Solo i file che servono agli script o al progetto in corso.

| File | Perché serve | Fonte |
|---|---|---|
| `T61/T61.brd` | ingresso di `gen2/gen_jae_t61_footprint.py` (impronta JAE AA01B di J1) e di `gen2/make_pkg.py` | progetto T61 di thedalles77, <https://github.com/thedalles77/USB_Laptop_Keyboard_Controller> |
| `I-PEX/CATALOG_CABLINE-VS_E_202610R0.pdf` | land pattern di J4 (`IPEX_20455-040E_90deg`), ingombro della spina e codici dei cavi (`doc/CABLE_SPEC.md`) | catalogo I-PEX CABLINE-VS, <https://www.i-pex.com> |
| `misure/PXL_20261102_114706251.jpg` | foto della scheda madre con la cornice di misura 1:1 (`doc/x210ai_cornice_misura_1a1.pdf`), 02/11/2026 | caricata su GitHub il 02/11/2026 (commit `9b0ff75`) |
| `misure/foto_20261102_rettificata_mm.jpg` | stessa foto rettificata in coordinate dima (mm, origine al centro di BTB_R_CONN1), griglia 10 mm e ostacoli disegnati | derivata da `PXL_20261102_114706251.jpg` (croccini A/C/D, scala 24,07 px/mm) |
| `misure/MISURE_foto_20261102.md` | report: omografia, ostacoli misurati, ingombri e zona libera per la scheda "a giro del quadrato bianco" | — |

Tolti dal repository il 28/10/2026, perché nessuno script li usa o le verifiche che li usavano sono chiuse:
sketch `.ino` e `keylist.txt` della T61, `T61.sch`, `T61_Teensy4p0.pdf` (schema citato in
`gen_sandwich_footprint.py`, p. 5) e lo zip dei Gerber T61 (usato per il controllo 44/44 piazzole di J1).
Si riscaricano dal repository di thedalles77.
