X210Ai – Adattatore tastiera ISO/JIS con RP2040: report di passaggio (rev 2.2, 23/10/2026)
Questo documento è il manuale di handoff per riprendere il progetto in una nuova chat con Claude Code.
Contiene architettura, misure, vincoli, decisioni, schemi, PCB, firmware, produzione, e istruzioni
specifiche per l'uso efficiente con Claude Code + KiCad 10 CLI.
0. Come riprendere il progetto (ISTRUZIONI PER CLAUDE CODE)
0.1 Setup iniziale

    Allega lo zip del progetto (x210ai_rev2.2_lavoro.zip) alla nuova chat.
    Estrai in una cartella di lavoro locale (es. ~/projects/x210ai/).
    Verifica l'ambiente (sezione 7): KiCad 10, Python 3.12+, kicad-cli, Freerouting, ngspice.
    Leggi questo file (PASSAGGIO.md) come contesto principale.

0.2 Cosa riutilizzare dalla rev 2.0/2.1

    Firmware (fw3/): RIUTILIZZABILE al 100%. Nessuna modifica. Stesso RP2040, stessa logica, stessi GPIO.
    Script generatori (gen2/): DA ADATTARE. design2.py va diviso in design_boardA.py e design_boardB.py.
    Libreria footprint (lib/x210ai.pretty/): DA ESTENDERE. Mantenere i footprint esistenti, aggiungere IPEX_20455-040E_90deg e JAE_AA01_sandwich.
    PCB rev 2.0/2.1 (pcb_out4/, pcb_out5/): NON RIUTILIZZABILE. La geometria è completamente diversa. Serve come riferimento visivo, non come base.
    Emulatore (emu2/): RIUTILIZZABILE. Nessuna modifica.
    SPICE (spice2/): RIUTILIZZABILE. Le simulazioni dei MOSFET e del TrackPoint sono ancora valide.
    Documenti (doc/): DA AGGIORNARE. LEGGIMI.md, FIRMWARE.md, VERIFICA.md vanno aggiornati per la rev 2.2.

0.3 Strategia di riduzione token per Claude Code

    NON leggere file .kicad_pcb o .kicad_sch interi. Sono enormi (50-100 kB). Usa script Python per estrarre solo ciò che serve.
    Usa kicad-cli per report DRC/ERC in formato JSON.
    Usa /clear quando cambi sottocompito (es. da "disegno Board A" a "disegno Board B").
    Usa /compact quando la sessione si allunga oltre 20-30 messaggi.
    Scegli il modello in base al compito: Sonnet per script/export, Opus per decisioni critiche.
    Non far aprire a Claude Code i file di log di Freerouting (sono enormi). Usa solo il report finale.

0.4 Flusso di lavoro consigliato

    Fase 1: Design Board A (scheda principale sotto palmrest)
    Fase 2: Design Board B (adattatore sandwich sul connettore madre)
    Fase 3: Specifica cavo eDP
    Fase 4: Produzione e assemblaggio

1. Obiettivo e requisiti
ThinkPad X210Ai (scheda madre 51nb, telaio X200/X201). L'EC gestisce solo la tastiera ANSI. Con una tastiera ISO italiana non funzionano solo i tasti < > e ù. Si vuole anche la compatibilità con la tastiera giapponese JIS.
Requisiti dichiarati:

    R1: Convertire la tastiera in USB (base: thedalles77 T61 Teensy 4.0 e hektopuss/ThinkPad_RP2040_Keyboard) → RP2040 legge la matrice → tastiera HID USB
    R2: RP2040 integrato sul PCB (niente modulo Pico saldato), assemblato da JLCPCB → QFN-56 + flash + quarzo sulla Board A
    R3: Scheda più sottile possibile nella zona critica (sopra il connettore madre) → Board B sandwich 0,4 mm (JLCPCB), altezza totale ~4,4 mm
    R4: Touchpad non serve. TrackPoint sì → TrackPoint PS/2 via traslatori BSS138 sulla Board A
    R5: LED sacrificabili → nessun LED
    R6: Tasto di accensione verso la FPC 40 pin della scheda madre, senza passare dall'RP2040 → pin 19 diretto sulla Board B
    R7: Fn+PgUp = ThinkLight deve funzionare (gestito dall'EC) → EC emulato con 2 MOSFET (Q2b, Q3) sulla Board B, pilotati dalla Board A via eDP
    R8: Scambio Fn/Ctrl (il BIOS del X210Ai non ha l'opzione) → firmware sulla Board A, salvato in flash
    R9: Windows e Linux in dual boot → solo classi HID standard
    R10: Compatibilità JIS (5 tasti in più) → apprendimento via seriale → International1-5

2. Storia e logica delle decisioni

    rev 1.0-1.3 (consegnate prima). Scheda 46 × 26 mm, 4 strati, 0,8 mm, tutto sul lato TOP. Lo zip della rev 1.3 è tra i file del progetto: x210ai_iso_adapter_kicad_rev1.3.zip.
    Problema 1: Fn via USB. Se la tastiera passa tutta via USB, l'EC non vede più il tasto Fn. Soluzione: l'RP2040 "preme" Fn+PgUp verso l'EC con interruttori MOSFET sulle linee originali del connettore della scheda madre.
    Problema 2: ingombro verticale. Misure reali aggiornate (23/10/2026):
        Spazio totale disponibile tra scudi (tastiera montata): ~5,0 mm
        Spessore flat tastiera (solo cavo): 1,4 mm
        Spessore connettore tastiera + flat (dorso spina montata): 2,5 mm
        Spazio sotto il palmrest: ~5,0 mm (target 4,0 mm per margine di sicurezza)
    Soluzione scelta (rev 2.2): architettura a due schede collegate via cavo eDP.
        Board A (scheda principale): sotto il palmrest, dove c'è spazio abbondante (~4 mm target). Contiene RP2040, flash, quarzo, LDO, circuiti TrackPoint, connettore USB, e un connettore eDP 90° (I-PEX 20455 o equivalente).
        Board B (adattatore sandwich): incastonata direttamente sul connettore della scheda madre (BTB_R_CONN1). PCB sottilissimo (0,4 mm) con spina JAE sotto, ricettacolo JAE sopra, connettore eDP 90° di lato, e 2 MOSFET BSS138DW per l'emulazione EC.
        Cavo eDP: collega la Board A alla Board B. FPC standard a 40 pin, passo 0,5 mm, lunghezza ~40-60 mm.
    Swap Fn/Ctrl: ✅ funziona (è firmware, invariato dalla rev 2.0)
    Fn+PgUp → ThinkLight: ✅ funziona (MOSFET sulla Board B, pilotati dalla Board A via eDP)
    TrackPoint: ✅ funziona (circuiti sulla Board A)
    JIS/ISO: ✅ funziona (firmware, invariato)

3. Architettura dettagliata rev 2.2
Schema a blocchi:

                tastiera (spina AA01B-P040 sul flat)
                             │
                ┌────────────┴────────────┐
                │  Board B (sandwich)     │
                │  PCB 0,4 mm             │
                │  JAE spina (sotto)      │
                │  JAE ricettacolo (sopra)│
                │  eDP 90° (lato)         │
                │  MOSFET Q2b, Q3         │
                └────────────┬────────────┘
                             │  cavo eDP 40 pin 0,5 mm
                             │  (~40-60 mm)
                             │
     ┌───────────────────────┴───────────────────────┐
     │  Board A (sotto palmrest)                     │
     │  PCB 0,8 mm (JLCPCB)                          │
     │  RP2040 QFN-56, flash, quarzo, LDO            │
     │  TrackPoint PS/2 (traslatori BSS138)          │
     │  eDP 90° (lato, verso Board B)                │
     │  USB → USB-CON1 (scheda madre)                │
     └───────────────────────────────────────────────┘

3.1 Board A: Scheda principale (sotto palmrest)

    Posizione: sotto il palmrest, vicino al connettore della tastiera. Spazio disponibile: ~5 mm, target 4 mm.
    Componenti: RP2040 QFN-56, Flash W25Q16JVUXIQ, LDO XC6206P332MR, Quarzo 12 MHz, BSS138DW (TrackPoint), condensatori/resistori 0402, piazzole USB, connettore eDP 90° (I-PEX 20455-040E), jumper BOOT/RESET, pad di test.
    Dimensioni stimate: ~40 × 25 mm (da ottimizzare nel layout).
    Funzioni: Legge la matrice e il TrackPoint via eDP dalla Board B. Genera dispositivo USB composito. Pilota i MOSFET sulla Board B via eDP.

3.2 Board B: Adattatore sandwich (sul connettore madre)

    Posizione: incastonata direttamente sul connettore BTB_R_CONN1 della scheda madre.
    Componenti: Spina JAE AA01B-P040VA1 (sotto), ricettacolo JAE AA01B-S040VA1 (sopra), connettore eDP 90° (lato), 2x BSS138DW (Q2, Q3), resistori 100k (R13, R14).
    Dimensioni stimate: ~15 × 12 mm (minimo).
    Spessore PCB: 0,4 mm (JLCPCB, solo ENIG; inizialmente previsto PCBWay).
    Funzioni: Passaggio 1:1 dei segnali matrice e TrackPoint. Passaggio diretto pin 19 (accensione) e GND. Emulazione EC via MOSFET pilotati dalla Board A.

3.3 Cavo eDP

    Specifiche: FPC 40 pin, passo 0,5 mm, lunghezza ~40-60 mm, spine eDP (I-PEX 20453-040E) a entrambe le estremità, spessore ~0,2-0,3 mm.
    Segnali: Matrice (righe/colonne), Fn, TrackPoint (DATA, 5V, CLOCK, RESET), GND, Gate MOSFET (EC_FN_G, EC_PGUP_G). Il pin 19 (accensione) NON passa dal cavo, è diretto sulla Board B.

4. Misure e vincoli meccanici

    Spazio totale tra scudi (tastiera montata): ~5,0 mm
    Spessore flat tastiera (solo cavo): 1,4 mm
    Spessore connettore tastiera + flat (dorso spina): 2,5 mm
    Spazio sotto il palmrest: ~5,0 mm (target 4,0 mm)

Bilancio di spessore Board B (sandwich):

    Spina JAE (sotto): ~1,5 mm
    PCB Board B: 0,4 mm
    Ricettacolo JAE (sopra): ~1,5 mm
    Totale pila connettori: 3,4 mm
    Flat tastiera (parte che sporge sopra il ricettacolo): ~1,0 mm
    Altezza totale (scheda madre → dorso flat): 4,4 mm (rientra nei 5,0 mm con 0,6 mm di margine)

Vincoli di posizione: Non entrare nel quadrato bianco serigrafato, non scendere fino al foro della vite, attenzione allo slot SIM a sinistra. Applicare nastro Kapton sotto la Board B.
5. Schema elettrico e Firmware
Mappa GPIO RP2040 (invariata dalla rev 2.0):
#define X210_ROW_IO { 9, 11, 15, 17, 19, 21, 23, 14, 12, 10, 16, 18, 20, 22, 24, 13 }
#define X210_COL_IO { 6, 4, 2, 0, 1, 3, 5, 7 }
#define X210_FN_PIN 8
#define X210_TP_DATA_PIN 29
#define X210_TP_CLOCK_PIN 28
#define X210_TP_RESET_PIN 25
#define X210_EC_FN_PIN 26      // → Board B via eDP
#define X210_EC_PGUP_PIN 27    // → Board B via eDP
Firmware: Invariato dalla rev 2.0 (hektopuss/ThinkPad_RP2040_Keyboard, commit 970379d). Swap Fn/Ctrl, Fn+PgUp → ThinkLight, JIS, modalità aereo, bootloader UF2 funzionano esattamente come prima.
6. PCB e Produzione
Board A

    PCB: JLCPCB 4 strati, 0,8 mm, ENIG.
    Assemblaggio: JLCPCB Standard (entrambi i lati).
    Regole: pista/isolamento 0,1 mm, via 0,4/0,2 mm.

Board B

    PCB: JLCPCB 4 strati, 0,4 mm, ENIG (a 0,4 mm JLCPCB accetta solo ENIG; inizialmente previsto PCBWay).
    Assemblaggio: A mano (connettori JAE saldati dall'utente con pasta + aria calda).
    Regole: pista/isolamento 0,1 mm, via 0,3/0,15 mm.

Cavo eDP

    FPC 40 pin 0,5 mm, spine eDP alle estremità. Reperibile su AliExpress/Mouser (~5-10€) o custom.

7. Ambiente e comandi (Claude Code + KiCad 10)
Software necessario: KiCad 10, Python 3.12+, Freerouting 1.9.0, ngspice 42+, arduino-cli, kicad-cli.
Comandi KiCad CLI utili:
kicad-cli pcb drc board.kicad_pcb --format json --output drc.json
kicad-cli sch erc schematic.kicad_sch --format json --output erc.json
kicad-cli sch export netlist --format kicadxml schematic.kicad_sch --output netlist.xml
kicad-cli pcb export gerbers board.kicad_pcb --output gerber/
kicad-cli sch export bom schematic.kicad_sch --format csv --output bom.csv
Flusso di lavoro con Claude Code:

    Inizia una nuova chat e allega x210ai_rev2.2_lavoro.zip.
    Chiedi: "Riprendi il progetto dalla sezione 0 del PASSAGGIO.md".
    Fase 1: "Adatta design2.py per generare Board A e Board B separate".
    Fase 2: "Genera schema e PCB per Board A, poi sbroglio con Freerouting".
    Fase 3: "Genera schema e PCB per Board B, sbroglio a mano".
    Fase 4: "Scrivi specifiche cavo eDP in CABLE_SPEC.md".
    Fase 5: "Export Gerber, BOM, CPL per produzione".

8. Prossimi passi (in ordine)

    Adattare design2.py per gestire due PCB separati.
    Creare footprint IPEX_20455-040E_90deg per KiCad 10.
    Creare footprint JAE_AA01_sandwich per Board B.
    Generare schema e PCB Board A → Sbroglio → DRC 0 errori.
    Generare schema e PCB Board B → Sbroglio a mano → DRC 0 errori.
    Scrivere CABLE_SPEC.md.
    Rigenerare dima 1:1, export Gerber/BOM/CPL.
    Aggiornare LEGGIMI.md, FIRMWARE.md, VERIFICA.md.
    Assemblare zip finale con make_pkg.sh.

