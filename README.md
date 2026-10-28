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
- [x] Dime 1:1 (piazzamento provvisorio): Board A, Board B a L rovesciata (`doc/`)
- [x] Board B a L rovesciata provata sulla scheda madre (28/10/2026) e portata nel modello: `OUTLINE` in `design_boardB.py` (39,7 × 15,4 mm, J4 ruotato di 180° sul braccio basso, Q2/Q3/R13/R14 sotto a destra), contorno, zone GND e confine di Freerouting a poligono in `build_pcb.py`, dima definitiva `doc/x210ai_dima_boardB_1a1.pdf`
- [x] Board B: PCB sbrogliato con Freerouting (0,13 mm di isolamento nel DSN per rispettare 0,2 mm foro-rame con i via 0,3/0,15), ERC = 0, DRC = 0, 0 non connessi, schema = PCB (`out_boardB/`)
- [x] Schemi: simbolo MOSFET da `Transistor_FET` (KiCad 10), libreria di simboli `x210ai.kicad_sym` + `sym-lib-table` accanto a ogni schema
- [x] Board B: controllo DFM sul PCB sbrogliato: via 0,3/0,15 (anello 0,075), pista minima 0,1, rame-bordo 0,25, ponte di maschera 0,2, 88 via tutti coperti, nessun via in piazzola
- [x] Board A compattata a 28,9 × 16,4 mm (era 40 × 25): J4 sotto U1, TrackPoint in due colonne; via +3V3 dedicato per U1.48/49 e piazzola 19 di U1 esclusa dalla zona
- [x] Board A: PCB sbrogliato con Freerouting, ERC = 0, DRC = 0, 0 non connessi, schema = PCB (`out_boardA/`)
- [x] Gerber, forature, BOM e CPL per le due schede (`produzione/boardA/`, `produzione/boardB/`); controllo Gerber e DFM superati
- [x] Campi LCSC/MPN/Manufacturer nascosti in serigrafia; testo "1" di J1 sul lato B speculare

### Da fare

**Decisioni aperte**
- [ ] Percorso reale del cavo eDP (con la L il cavo sale e va ripiegato verso la Board A) → cavo **1-1 o 1-N** (`gen2/edp_pinout.py`, oggi 1-N)
- [ ] Lunghezza del cavo: lo standard I-PEX parte da 100 mm, ne servono 40-60 (su misura o piegato)
- [ ] Misurare col calibro la distanza tra le file della spina 2×22 del flat (oggi stimata 3,9 mm)
- [x] Produttore: JLCPCB per entrambe le schede (Board A 0,8 mm; Board B 0,4 mm, a questo spessore solo ENIG e niente pannello; 0,6 mm a 4 strati non c'è)
- [ ] Board B: confermare nel configuratore JLCPCB via 0,3/0,15 (anello 0,075 mm) e piste 0,1 mm
- [ ] Cavo: micro-coassiale I-PEX 20453 a 40 fili, nessun pin unito, barra di massa ai due capi. Opzioni: preventivo LCSC Custom Cables (`cable@lcsc.com`) o produttore su Alibaba (~11 $/pz, lunghezza su misura), altrimenti I-PEX 82190-100B-02-D da DigiKey (~40 $, 100 mm). Su LCSC non c'è a catalogo; i cavi eDP generici per pannelli 4K non vanno bene
- [ ] Serigrafia: testi 0,45-0,7 mm e linee 0,12 mm sotto i minimi consigliati (1,0 / 0,15 mm), possono risultare poco leggibili
- [x] Dima Board A 28,9 × 16,4 mm provata sulla scheda madre (28/10/2026, `doc/x210ai_dima_boardA_1a1.pdf`)

**PCB e produzione** (in locale: `.venv/bin/python gen2/pipeline.py --board A|B`, vedi [`doc/ESECUZIONE_LOCALE.md`](doc/ESECUZIONE_LOCALE.md))
- [ ] Board A e Board B: rivedere in KiCad lo sbroglio automatico (Freerouting, `out_boardA/`, `out_boardB/`) e ritoccarlo a mano dove serve; tra i courtyard di J1 e J4 restano 0,5 mm (J4 risalito di 2 mm nella prova)
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
