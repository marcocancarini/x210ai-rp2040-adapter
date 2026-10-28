# Riferimenti

Solo i file che servono agli script o al progetto in corso.

| File | Perché serve | Fonte |
|---|---|---|
| `T61/T61.brd` | ingresso di `gen2/gen_jae_t61_footprint.py` (impronta JAE AA01B di J1) e di `gen2/make_pkg.py` | progetto T61 di thedalles77, <https://github.com/thedalles77/USB_Laptop_Keyboard_Controller> |
| `I-PEX/CATALOG_CABLINE-VS_E_202610R0.pdf` | land pattern di J4 (`IPEX_20455-040E_90deg`), ingombro della spina e codici dei cavi (`doc/CABLE_SPEC.md`) | catalogo I-PEX CABLINE-VS, <https://www.i-pex.com> |

Tolti dal repository il 28/10/2026, perché nessuno script li usa o le verifiche che li usavano sono chiuse:
sketch `.ino` e `keylist.txt` della T61, `T61.sch`, `T61_Teensy4p0.pdf` (schema citato in
`gen_sandwich_footprint.py`, p. 5) e lo zip dei Gerber T61 (usato per il controllo 44/44 piazzole di J1).
Si riscaricano dal repository di thedalles77.
