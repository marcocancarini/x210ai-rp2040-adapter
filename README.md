# X210Ai RP2040 adapter (rev 2.2)

Controller USB con RP2040 per la tastiera del ThinkPad X210Ai (ISO italiana e JIS giapponese), su due schede:
**Board A** (RP2040, sotto il palmrest) e **Board B** (sandwich sul connettore tastiera BTB_R_CONN1),
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
- [x] Impronte: `JAE_AA01B-S040VA1_T61` (44/44 piazzole come il Gerber T61), `JAE_AA01_sandwich`, `IPEX_20455-040E_90deg`
- [x] Specifica del cavo: [`doc/CABLE_SPEC.md`](doc/CABLE_SPEC.md)
- [x] Ambiente locale (Linux): KiCad 10.0.7, `.venv/` con shapely/gerbonara/cairosvg, Freerouting 1.9.0 + Java 21, ngspice 47, arduino-cli + arduino-pico 6.3.0, `emu2/node_modules`

**Schede**
- [x] Board B a L rovesciata, 39,7 × 15,4 mm (J4 ruotato di 180° sul braccio basso, Q2/Q3/R13/R14 sotto a destra); dima provata sulla scheda madre il 28/10/2026
- [x] Board A compattata a 28,9 × 16,4 mm (era 40 × 25): J4 sotto U1, TrackPoint in due colonne, via +3V3 dedicato per U1.48/49; dima provata sulla scheda madre il 28/10/2026
- [x] Sbroglio Freerouting di entrambe le schede (`-mp 100`): ERC = 0, DRC = 0, 0 non connessi, schema = PCB (`out_boardA/`, `out_boardB/`)
- [x] Isolamento foro-rame 0,2 mm rispettato alzando l'isolamento nel DSN (0,13 mm sulla Board B, 0,10 sulla Board A)
- [x] Controllo DFM: via 0,4/0,2 (A) e 0,3/0,15 (B, anello 0,075), pista minima 0,1, rame-bordo 0,25, ponte di maschera 0,2, via tutte coperte
- [x] KiCad 10: simboli nella libreria di progetto `x210ai.kicad_sym` + `sym-lib-table`, MOSFET da `Transistor_FET`, campi BOM nascosti in serigrafia, testo speculare sul lato B

**Produzione**
- [x] Produttore: JLCPCB per entrambe le schede (Board A 0,8 mm; Board B 0,4 mm, a questo spessore solo ENIG e niente pannello; 0,6 mm a 4 strati non c'è)
- [x] Gerber, forature, BOM e CPL (un lato / due lati) per le due schede (`produzione/boardA/`, `produzione/boardB/`); controllo Gerber superato
- [x] Ricettacolo eDP C5160883 a magazzino LCSC (28/10/2026)
- [x] Spessori: Board B ~4,4 mm su ~5,0 dalla scheda madre al dorso del flat; Board A ~3,1 mm su 4,0
- [x] Documenti rev 2.2: [`doc/LEGGIMI.md`](doc/LEGGIMI.md), [`doc/FIRMWARE.md`](doc/FIRMWARE.md), [`doc/VERIFICA.md`](doc/VERIFICA.md), [`doc/REPORT_rev2.2.md`](doc/REPORT_rev2.2.md)
- [x] Pacchetto `x210ai_iso_adapter_kicad_rev2.2.zip` (`gen2/make_pkg.py`)

### Da fare

**Prima di ordinare**
- [ ] Prova della moneta da 10 centesimi sul dorso della spina della tastiera (`doc/LEGGIMI.md`): altezza reale della pila della Board B
- [ ] Misurare col calibro la distanza tra le file della spina 2×22 del flat (oggi stimata 3,9 mm)
- [ ] Lunghezza del cavo con uno spago tra i due J4 e tipo: **1-N** con il cavo steso (impostato), **1-1** con una piega (`gen2/edp_pinout.py`, poi nuovo sbroglio della Board B)
- [ ] Cavo: micro-coassiale I-PEX 20453 a 40 fili, nessun pin unito, barra di massa ai due capi. Preventivo LCSC Custom Cables (`cable@lcsc.com`) o produttore su Alibaba (~11 $/pz); altrimenti I-PEX 82190-100B-02-D da DigiKey (~40 $, 100 mm). I cavi eDP generici per pannelli 4K non vanno bene
- [ ] Board B: confermare nel configuratore JLCPCB 4 strati 0,4 mm ENIG con via 0,3/0,15 e piste 0,1 mm

**Facoltativo**
- [ ] Rivedere in KiCad lo sbroglio automatico e ritoccarlo a mano dove serve; tra i courtyard di J1 e J4 della Board B restano 0,5 mm
- [ ] Serigrafia: testi 0,45-0,7 mm e linee 0,12 mm sotto i minimi consigliati (1,0 / 0,15 mm), possono risultare poco leggibili

**Costruzione e prova**
- [ ] Ordinare PCB, componenti e cavo
- [ ] Saldare a mano la Board B (spina JAE sotto, non su LCSC); Kapton sotto la Board B
- [ ] Prova di continuità del cavo pin per pin (`doc/CABLE_SPEC.md`)
- [ ] Prove a scheda montata: matrice, TrackPoint, Fn+PgUp → ThinkLight, accensione, swap Fn/Ctrl, JIS, UF2
