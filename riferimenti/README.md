# Riferimenti

Solo i file che servono agli script o al progetto in corso.

| File | Perché serve | Fonte |
|---|---|---|
| `T61/T61.brd` | ingresso di `gen2/gen_jae_t61_footprint.py` (impronta JAE AA01B di J1) e di `gen2/make_pkg.py` | progetto T61 di thedalles77, <https://github.com/thedalles77/USB_Laptop_Keyboard_Controller> |
| `I-PEX/CATALOG_CABLINE-VS_E_202610R0.pdf` | land pattern di J4 (`IPEX_20455-040E_90deg`), ingombro della spina e codici dei cavi (`doc/CABLE_SPEC.md`) | catalogo I-PEX CABLINE-VS, <https://www.i-pex.com> |
| `misure/PXL_20261102_114706251.jpg` | foto della scheda madre con la cornice di misura 1:1 (`doc/x210ai_cornice_misura_1a1.pdf`), 02/11/2026 | caricata su GitHub il 02/11/2026 (commit `9b0ff75`) |
| `misure/PXL_20261019_233538594.jpg` | foto ravvicinata della zona BTB_R_CONN1 del 19/10/2026 (la "seconda foto" da cui vengono gli `OSTACOLI` di `gen2/design_boardB.py`) | caricata il 02/11/2026 |
| `misure/verifica_v3_1_foto20261019.jpg`, `misure/verifica_v3_1_foto20261102.jpg` | overlay di controllo: forma Board C v3.1 e ingombri (nomi corretti) sulle due foto | derivate dalle foto, calibrazione su BTB_R_CONN1 + quadrato bianco |
| `misure/MISURE_foto_20261102.md` | report: calibrazione, ostacoli misurati (con correzione dei nomi del 02/11), ingombri e zona libera per la scheda "a giro del quadrato bianco" | — |

Tolti dal repository il 28/10/2026, perché nessuno script li usa o le verifiche che li usavano sono chiuse:
sketch `.ino` e `keylist.txt` della T61, `T61.sch`, `T61_Teensy4p0.pdf` (schema citato in
`gen_sandwich_footprint.py`, p. 5) e lo zip dei Gerber T61 (usato per il controllo 44/44 piazzole di J1).
Si riscaricano dal repository di thedalles77.
