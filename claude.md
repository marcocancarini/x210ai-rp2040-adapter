Contesto progetto X210Ai Adapter Board (rev 2.2)
Obiettivo
Controller USB per tastiera ThinkPad X210Ai (ISO italiano + JIS giapponese) basato su RP2040.
Architettura rev 2.2 (DUE SCHEDE)
Board A (sotto palmrest, ~40x25 mm)

    Posizione: sotto il palmrest (spazio ~5 mm, target 4 mm)
    Componenti: RP2040 QFN-56, flash W25Q16, quarzo 12 MHz, LDO 3.3V, circuiti TrackPoint
    Connettore: eDP 90 gradi (I-PEX 20455-040E) verso Board B
    Alimentazione: USB 5V da USB-CON1 scheda madre
    PCB: 4 strati, 0.8 mm (JLCPCB), ENIG
    Assemblaggio: JLCPCB Standard (entrambi i lati)

Board B (sandwich sul connettore tastiera, ~15x12 mm)

    Posizione: incastonata su BTB_R_CONN1 scheda madre
    Componenti: solo 2 MOSFET BSS138DW (emulazione EC Fn/PgUp) + connettori
    Connettori:
        Sotto: spina JAE AA01B-P040VA1 (nel connettore madre)
        Sopra: ricettacolo JAE AA01B-S040VA1 (riceve flat tastiera)
        Lato: eDP 90 gradi (riceve cavo da Board A)
    PCB: 4 strati, 0.4 mm (JLCPCB, solo ENIG a questo spessore)
    Assemblaggio: a mano (connettori JAE saldati dall'utente)

Cavo eDP

    FPC 40 pin, passo 0.5 mm, lunghezza ~40-60 mm
    Spine eDP (I-PEX 20453-040E) a entrambe le estremità
    Collega Board A <-> Board B

Vincoli meccanici critici

    Spazio totale tastiera montata: 5.0 mm
    Spessore connettore tastiera + flat: 2.5 mm
    Spazio sotto palmrest: 5.0 mm (target 4.0 mm)
    Altezza totale Board B sandwich: 4.4 mm (rientra con margine)

Funzionalità firmware (invariato da rev 2.0)

    Swap Fn/Ctrl: SI (firmware, salvato in flash)
    Fn+PgUp -> ThinkLight: SI (MOSFET su Board B, pilotati da Board A via eDP)
    TrackPoint PS/2: SI (circuiti su Board A)
    JIS/ISO: SI (firmware)
    Modalita aereo, bootloader UF2, console seriale: SI

Pinout connettore tastiera (JAE AA01B, 40 pin, passo 0.5 mm)

    Pin 1: Fn (attivo basso)
    Pin 2,4,...,32 (pari): righe R2-R32 (16 righe)
    Pin 3,5,...,17 (dispari): colonne C3-C17 (8 colonne)
    Pin 19: tasto accensione (passaggio diretto, no RP2040)
    Pin 31,34,36: GND
    Pin 37: TrackPoint DATA (5V)
    Pin 38: TrackPoint 5V
    Pin 39: TrackPoint CLOCK (5V)
    Pin 40: TrackPoint RESET (5V, attivo alto)

Mappa GPIO RP2040 (invariata)
#define X210_ROW_IO { 9, 11, 15, 17, 19, 21, 23, 14, 12, 10, 16, 18, 20, 22, 24, 13 }
#define X210_COL_IO { 6, 4, 2, 0, 1, 3, 5, 7 }
#define X210_FN_PIN 8
#define X210_TP_DATA_PIN 29
#define X210_TP_CLOCK_PIN 28
#define X210_TP_RESET_PIN 25
#define X210_EC_FN_PIN 26      // -> Board B via eDP
#define X210_EC_PGUP_PIN 27    // -> Board B via eDP
Ambiente di lavoro

    KiCad: versione 10 (o >= 7)
    Python: 3.12+
    OS: Linux preferito (per kicad-cli e Python)
    Freerouting: 1.9.0 (Java, autorouting locale)
    ngspice: 42+ (simulazioni SPICE)

Strategia riduzione token

    NON leggere file .kicad_pcb o .kicad_sch interi (50-100 kB ciascuno)
    Usare script Python per estrarre solo ciò che serve (BOM, netlist, coordinate)
    Usare kicad-cli per report DRC/ERC in formato JSON
    Usare /clear quando si cambia sottocompito
    Usare /compact quando la sessione supera 20-30 messaggi
    Modello Sonnet per task routine, Opus per decisioni critiche

Comandi KiCad CLI utili
kicad-cli pcb drc board.kicad_pcb --format json --output drc.json
kicad-cli sch erc schematic.kicad_sch --format json --output erc.json
kicad-cli sch export netlist --format kicadxml schematic.kicad_sch --output netlist.xml
kicad-cli pcb export gerbers board.kicad_pcb --output gerber/
kicad-cli sch export bom schematic.kicad_sch --format csv --output bom.csv
Cosa riutilizzare dalla rev 2.0/2.1

    Firmware (fw3/): 100% riutilizzabile, nessuna modifica
    Emulatore (emu2/): riutilizzabile
    SPICE (spice2/): simulazioni MOSFET e TrackPoint ancora valide
    Script generatori (gen2/): da adattare per due PCB separati
    Libreria footprint (lib/x210ai.pretty/): da estendere con eDP 90 gradi e JAE sandwich
    PCB rev 2.0/2.1: non riutilizzabile (geometria completamente diversa)

Prossimi passi immediati

    Adattare design2.py -> design_boardA.py + design_boardB.py
    Creare footprint IPEX_20455-040E_90deg (eDP 90 gradi)
    Creare footprint JAE_AA01_sandwich (sovrapposizione spina + ricettacolo)
    Generare schema e PCB Board A
    Sbroglio Board A con Freerouting
    Generare schema e PCB Board B
    Sbroglio Board B a mano (piccolo e denso)
    Specifica cavo eDP (CABLE_SPEC.md)
    Export Gerber, BOM, CPL per produzione

Riferimenti

    Repository base firmware: hektopuss/ThinkPad_RP2040_Keyboard (commit 970379d)
    Repository T61 Teensy: thedalles77 (per riferimento pinout)
    Connettori JAE: serie AA01B (datasheet JAE)
    Connettori eDP: I-PEX 20454/20455 (datasheet I-PEX)

Note importanti

    I connettori JAE AA01 sono saldati a mano dall'utente (nessun problema di reperibilita LCSC)
    La Board B ha spessore 0.4 mm (JLCPCB, solo ENIG, niente pannello) per minimizzare ingombro verticale
    Il cavo eDP e un micro-coassiale I-PEX 20453 a 40 fili: standard I-PEX da DigiKey (~40 $, 100 mm) oppure su misura (LCSC Custom Cables, produttori su Alibaba ~11 $); i cavi eDP generici per pannelli non vanno bene (pin uniti o mancanti), vedi doc/CABLE_SPEC.md
    Lo swap Fn/Ctrl e firmware, funziona indipendentemente dall'architettura hardware
