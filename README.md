# X210Ai RP2040 adapter (rev 2.2)

Controller USB con RP2040 per la tastiera del ThinkPad X210Ai (ISO italiana e JIS giapponese), su due schede:
**Board A** (RP2040, sotto il palmrest) e **Board B** (sandwich sul connettore tastiera BTB_R_CONN1),
collegate da un cavo eDP 40 pin. Dettagli in [`passaggio.md`](passaggio.md) e
[`doc/REPORT_rev2.2.md`](doc/REPORT_rev2.2.md).

## Checklist

Aggiornata al 28/10/2026. "Fatto" = verificato sul modello dati o sulla netlist, non su una scheda costruita.

### Fatto

- [x] Architettura a due schede + cavo eDP (rev 2.2)
- [x] Modello dati separato: `gen2/design_boardA.py`, `gen2/design_boardB.py`, `gen2/edp_pinout.py`; script di `gen2/` con `--board A|B`
- [x] Firmware (hektopuss `970379d`) invariato: GPIO della Board A coincidenti con `x210ai_pins.h`, `fw3/out/*.uf2` valido
- [x] Emulazione firmware: 14/14 prove, 94/94 tasti (`emu2/`)
- [x] Simulazioni SPICE dei MOSFET EC e del TrackPoint (`spice2/`)
- [x] Impronte: `JAE_AA01B-S040VA1_T61` (44/44 piazzole come il Gerber T61), `JAE_AA01_sandwich`, `IPEX_20455-040E_90deg`
- [x] Schemi generati e verificati sul modello: `out_boardA/`, `out_boardB/`
- [x] Specifica del cavo: [`doc/CABLE_SPEC.md`](doc/CABLE_SPEC.md)
- [x] BOM JLCPCB e BOM completa con MPN per le due schede (`produzione/`)
- [x] Ambiente locale (Linux): KiCad 10.0.7, `.venv/` con shapely/gerbonara/cairosvg, Freerouting 1.9.0 + Java 21, ngspice 47, arduino-cli + arduino-pico 6.3.0 (firmware ricompilato identico), `emu2/node_modules`
- [x] Dime 1:1 (piazzamento provvisorio): Board A, Board B attuale, Board B a L rovesciata (`doc/`)

### Da fare

**Board B: ingombro** (blocca tutto il resto della Board B)
- [ ] Provare sulla scheda madre la dima a L rovesciata `doc/x210ai_dima_boardB_L_1a1.pdf` (script `gen2/gen_dima_boardB_L.py`): slot SIM, vite, uscita del flat tastiera da J1, spazio a destra di J1
- [ ] Se va bene: portare il contorno a L in `design_boardB.py` (contorno a poligono) e rifare il piazzamento
- [ ] Rigenerare la dima Board B definitiva

**Decisioni aperte**
- [ ] Percorso reale del cavo eDP (con la L il cavo sale e va ripiegato verso la Board A) → cavo **1-1 o 1-N** (`gen2/edp_pinout.py`, oggi 1-N)
- [ ] Lunghezza del cavo: lo standard I-PEX parte da 100 mm, ne servono 40-60 (su misura o piegato)
- [ ] Misurare col calibro la distanza tra le file della spina 2×22 del flat (oggi stimata 3,9 mm)
- [ ] Board B 4 strati 0,4 mm: PCBWay oppure verifica nel configuratore JLCPCB

**PCB e produzione** (in locale: `.venv/bin/python gen2/pipeline.py --board A|B`, vedi [`doc/ESECUZIONE_LOCALE.md`](doc/ESECUZIONE_LOCALE.md))
- [ ] Board A: PCB, sbroglio, ERC = 0, DRC = 0, confronto schema/PCB
- [ ] Board A: ridurre l'ingombro (oggi 40 × 25 mm provvisori)
- [ ] Board B: PCB, sbroglio a mano, ERC = 0, DRC = 0
- [ ] Gerber, forature e CPL per le due schede (`gen2/export_prod.py`)
- [ ] Controllare la giacenza LCSC del ricettacolo eDP C5160883 all'ordine
- [ ] Altezza reale della pila Board B (oggi ~4,4 mm su 5,0 da documenti, non misurata)

**Documentazione e pacchetto**
- [ ] Aggiornare `doc/LEGGIMI.md`, `doc/FIRMWARE.md`, `doc/VERIFICA.md` (sono ancora della rev 2.0)
- [ ] Zip finale con `gen2/make_pkg.py`

**Costruzione e prova**
- [ ] Ordinare PCB, componenti e cavo
- [ ] Saldare a mano i connettori JAE della Board B; nastro Kapton sotto la Board B
- [ ] Prova di continuità del cavo pin per pin (`doc/CABLE_SPEC.md`)
- [ ] Prove a scheda montata: matrice, TrackPoint, Fn+PgUp → ThinkLight, accensione, swap Fn/Ctrl, JIS, UF2

## Struttura

| Cartella | Contenuto |
|---|---|
| `gen2/` | generatori Python (modello dati, impronte, schema, PCB, BOM, dime, export) |
| `out_boardA/`, `out_boardB/` | schemi KiCad generati |
| `produzione/` | BOM |
| `doc/` | report, specifica cavo, dime 1:1, istruzioni |
| `fw3/` | firmware RP2040 (fork di hektopuss/ThinkPad_RP2040_Keyboard, GPL-3.0) e binari |
| `emu2/`, `spice2/` | emulazione del firmware e simulazioni SPICE |
| `sch/`, `pcb_out4/` | schema e PCB della rev 2.0, solo come riferimento |
| `riferimenti/` | file di terzi usati dagli script ([`riferimenti/README.md`](riferimenti/README.md)) |
