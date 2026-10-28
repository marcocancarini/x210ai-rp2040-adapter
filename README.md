# X210Ai RP2040 adapter (rev 2.2)

Controller USB con RP2040 per la tastiera del ThinkPad X210Ai (ISO italiana e JIS giapponese), su due schede:
**Board A** (RP2040, sotto il palmrest) e **Board B** (flessibile a scalino sul connettore tastiera BTB_R_CONN1),
collegate da un cavo eDP 40 pin. Dettagli in [`passaggio.md`](passaggio.md) e
[`doc/REPORT_rev2.2.md`](doc/REPORT_rev2.2.md).

## Checklist

Aggiornata al 28/10/2026 (versione `v2.2.0-rc1`). "Fatto" = verificato sul progetto, non su una scheda costruita.

### Fatto

**Progetto**
- [x] Architettura a due schede + cavo eDP (rev 2.2)
- [x] Modello dati separato: `gen2/design_boardA.py`, `gen2/design_boardB.py`, `gen2/edp_pinout.py`; script di `gen2/` con `--board A|B`
- [x] Firmware (hektopuss `970379d`) invariato: GPIO della Board A coincidenti con `x210ai_pins.h`, `fw3/out/*.uf2` valido
- [x] Emulazione firmware: 14/14 prove, 94/94 tasti (`emu2/`); simulazioni SPICE dei MOSFET EC e del TrackPoint (`spice2/`)
- [x] Impronte: `JAE_AA01B-S040VA1_T61` (44/44 piazzole come il Gerber T61; variante `_GND41` con le linguette a pin 41), `JAE_AA01B-P040_MB_Plug_Bottom`, `IPEX_20455-040E_90deg`
- [x] Specifica del cavo: [`doc/CABLE_SPEC.md`](doc/CABLE_SPEC.md)
- [x] Ambiente locale (Linux): KiCad 10.0.7, `.venv/` con shapely/gerbonara/cairosvg, Freerouting 1.9.0 + Java 21, ngspice 47, arduino-cli + arduino-pico 6.3.0, `emu2/node_modules`

**Schede**
- [x] Board B a L rovesciata a sandwich (39,7 × 15,4 mm): scartata, sopra la spina della tastiera non c'è spazio (non entra nemmeno una moneta da 5 centesimi, 1,67 mm)
- [x] Board B **a scalino** (29,1 × 28,8 mm): gradino alto con la spina J2 su BTB_R_CONN1, J4 verso il palmrest e Q2/Q3/R13/R14 sotto; scalino flessibile di 1,5 mm; gradino basso sulla scheda madre con il ricettacolo J1 della tastiera a 25° in senso orario. Ingombri dalla cornice di misura fotografata (`gen2/gen_dima_scala.py`), quadrato bianco come zona vietata; dima `doc/x210ai_dima_boardB_scalino_1a1.pdf` provata il 28/10/2026, legenda di tutti i componenti `doc/x210ai_dima_boardB_scalino_legenda.pdf`
- [x] Board B: PCB flessibile **4 strati** (poliimmide ~0,25 mm, In1 GND, via 0,4/0,2; a 2 strati le 30 linee J1 → J4 non si sbrogliano), irrigidimenti su User.1 (FR4 0,2 sopra J2 e sotto J4, poliimmide 0,1 sotto J1), zona di piega senza via. Uscite di J1 (ruotato di 25°) pre-instradate fino al gradino alto, poi Freerouting: ERC = 0, DRC = 0, 0 non connessi, schema = PCB; DFM: rame-bordo 0,25, ponte di maschera 0,2
- [x] Board A compattata a 28,9 × 16,4 mm (era 40 × 25): J4 sotto U1, TrackPoint in due colonne, via +3V3 dedicato per U1.48/49; dima provata sulla scheda madre il 28/10/2026
- [x] Sbroglio Freerouting di entrambe le schede (`-mp 100`): ERC = 0, DRC = 0, 0 non connessi, schema = PCB (`out_boardA/`, `out_boardB/`)
- [x] Isolamento foro-rame 0,2 mm rispettato alzando l'isolamento nel DSN (0,13 mm sulla Board B, 0,10 sulla Board A)
- [x] Controllo DFM: via 0,4/0,2 (A) e 0,3/0,15 (B, anello 0,075), pista minima 0,1, rame-bordo 0,25, ponte di maschera 0,2, via tutte coperte
- [x] KiCad 10: simboli nella libreria di progetto `x210ai.kicad_sym` + `sym-lib-table`, MOSFET da `Transistor_FET`, campi BOM nascosti in serigrafia, testo speculare sul lato B

**Produzione**
- [x] Produttore: JLCPCB per entrambe le schede (Board A rigida 4 strati 0,8 mm; Board B flessibile 4 strati con irrigidimenti)
- [x] Gerber, forature, BOM e CPL (un lato / due lati) per le due schede (`produzione/boardA/`, `produzione/boardB/`); controllo Gerber superato
- [x] Ricettacolo eDP C5160883 a magazzino LCSC (28/10/2026)
- [x] Spessori: Board B gradino alto ~2,0 mm (con irrigidimento), J4 innestato ~2,9 mm, gradino basso con spina e flat della tastiera ~2,9 mm; Board A ~3,1 mm su 4,0
- [x] Documenti rev 2.2: [`doc/LEGGIMI.md`](doc/LEGGIMI.md), [`doc/FIRMWARE.md`](doc/FIRMWARE.md), [`doc/VERIFICA.md`](doc/VERIFICA.md), [`doc/REPORT_rev2.2.md`](doc/REPORT_rev2.2.md)
- [x] Pacchetto `x210ai_iso_adapter_kicad_rev2.2.zip` (`gen2/make_pkg.py`)

### Da fare

**In sospeso (29/10/2026)**
- [ ] Board B: il flessibile a 4 strati con irrigidimenti costa troppo; da cercare una soluzione più economica (il progetto a scalino resta come riferimento: dima, ingombri misurati e legenda in `doc/`)
- [ ] Cavo: in attesa della risposta di LCSC Custom Cables (mail inviata il 29/10/2026)

**Prima di ordinare**
- [ ] Misurare col calibro la distanza tra le file della spina 2×22 del flat (oggi stimata 3,9 mm)
- [x] Cavo: tipo **1-N** (il cavo non si capovolge lungo il percorso), lunghezza **150 o 200 mm** (`doc/CABLE_SPEC.md`)
- [ ] Cavo: micro-coassiale I-PEX 20453 a 40 fili, nessun pin unito, barra di massa ai due capi. Preventivo chiesto a LCSC Custom Cables (`cable@lcsc.com`) per i tipi 1-N (progetto) e 1-1 (riserva), 150 o 200 mm, tratti piatti alle spine e fascio tondo nel mezzo, in opzione curva a 90°. Alternative: produttore su Alibaba (~11 $/pz) o I-PEX 81422-100B-02-D da DigiKey (200 mm). I cavi eDP generici per pannelli 4K non vanno bene
- [ ] Board B: confermare nel configuratore JLCPCB flex: 4 strati, spessore, componenti sui due lati, irrigidimenti (file User.1), via 0,4/0,2, piste 0,1 mm
- [ ] Board B: col Patafix, spazio sopra il gradino basso (ricettacolo + spina della tastiera, ~2,9 mm) e sopra J4 (~2,9 mm)

**Facoltativo**
- [ ] Rivedere in KiCad lo sbroglio automatico e ritoccarlo a mano dove serve; J4 della Board B resta a 0,45 mm dal flat arancione
- [ ] Serigrafia: testi 0,45-0,7 mm e linee 0,12 mm sotto i minimi consigliati (1,0 / 0,15 mm), possono risultare poco leggibili

**Costruzione e prova**
- [ ] Ordinare PCB, componenti e cavo
- [ ] Saldare a mano la Board B (spina JAE J2 sotto, non su LCSC); Kapton sulla scheda madre sotto il gradino basso
- [ ] Prova di continuità del cavo pin per pin (`doc/CABLE_SPEC.md`)
- [ ] Prove a scheda montata: matrice, TrackPoint, Fn+PgUp → ThinkLight, accensione, swap Fn/Ctrl, JIS, UF2
