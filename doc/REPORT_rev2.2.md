# X210Ai rev 2.2 – Report di avanzamento (27/10/2026)

Il progetto è **in fase di definizione**. Modello dati delle due schede, piedinatura del cavo, impronte dei
connettori, BOM e dime sono pronti e generati da script. **Schemi e PCB delle due schede non esistono
ancora**: per questo non ci sono Gerber né CPL da mandare a JLCPCB.

Legenda: ✅ raggiunto nel progetto · ⚠️ parziale o da verificare · ❌ non ancora fatto.
"Raggiunto nel progetto" significa verificato sul modello dati e sulla netlist, non su una scheda costruita.
DRC ed ERC non sono stati eseguiti, perché KiCad non è installato su questo PC.

## 1. Requisiti

| # | Requisito | Stato | Come è soddisfatto / cosa manca |
|---|---|---|---|
| R1 | Tastiera → USB con RP2040 (matrice → HID) | ✅ | Firmware hektopuss `970379d` invariato. I GPIO della Board A coincidono con `x210ai_pins.h` (8/8 define, controllo automatico); le 25 net della tastiera arrivano a un GPIO di U1 attraverso J4. Emulazione rev 2.0: 14/14 prove superate, con gli stessi GPIO |
| R2 | RP2040 integrato (QFN-56, flash, quarzo), montato da JLCPCB | ⚠️ | BOM della Board A completa: 36 componenti con codice LCSC (eDP **C5160883**). Manca il PCB sbrogliato (Gerber e CPL). Giacenza LCSC del C5160883 da controllare all'ordine |
| R3 | Zona sopra il connettore della scheda madre il più sottile possibile | ⚠️ | Board B da 0,4 mm; pila spina 1,5 + PCB 0,4 + ricettacolo 1,5 = 3,4 mm, più il flat circa 4,4 mm, su 5,0 mm disponibili. Le altezze vengono dai documenti, non da misure. La distanza tra le file della spina (3,9 mm) è una stima |
| R4 | TrackPoint sì, touchpad no | ✅ | Traslatori BSS138 (Q1, Q2a) e pull-up sulla Board A; DATA, CLK, RESET e 5 V passano nel cavo (pin A3-A8) |
| R5 | Nessun LED | ✅ | Nessun LED in BOM |
| R6 | Tasto di accensione diretto alla scheda madre, senza RP2040 | ✅ | Sulla Board B, J1 pin 19 ↔ pin 119 (spina); non passa dal cavo (verificato nella netlist) |
| R7 | Fn+PgUp → ThinkLight gestito dall'EC | ✅ | Q2b (Fn a massa) e Q3 (riga 24 ↔ colonna 5) sulla Board B, gate pilotati dalla Board A via cavo (pin A10-A11); pull-down R13/R14 sulla Board B. Circuito uguale alla rev 2.0 (SPICE `spice2/ec_switch.cir`) |
| R8 | Scambio Fn/Ctrl | ✅ | Firmware, salvato in flash, invariato |
| R9 | Windows e Linux | ✅ | Solo classi HID standard (firmware invariato) |
| R10 | Tastiera JIS (5 tasti in più) | ✅ | Firmware: apprendimento via seriale → International1-5, invariato |

## 2. Vincoli meccanici

| Vincolo | Stato | Valore |
|---|---|---|
| Board B: pila ≤ 5,0 mm | ⚠️ | circa 4,4 mm sulla carta (vedi R3) |
| Board B: componenti sotto ≤ 1,5 mm (accoppiamento JAE) | ✅ | SOT-363 e 0402, circa 1,1 mm al massimo |
| Board B: eDP sopra sotto il livello del flat | ✅ | 1,0 +0,1 mm innestato, contro 1,5 mm di J1 innestato |
| **Board B: ingombro in pianta** | ❌ | **45,3 × 8,7 mm**: esce di **8,8 mm** a sinistra rispetto alla rev 2.0 (stima iniziale 15 × 12 mm). Causa: il ricettacolo eDP 40 pin con la sua area libera (28,2 × 6,7 mm) e i 2,5 mm di margine richiesti tra J1 e J4. J4 è ruotato di 180° e spostato verso lo slot SIM in base alla foto della dima: bordo a circa 0,7 mm dallo slot SIM (stima ±0,5 mm), da riprovare con la dima nuova |
| Board A: altezza ≤ 4,0 mm (target) | ✅ | stima circa 3,0 mm: PCB 0,8 + componenti sotto 1,1 + eDP innestato 1,1 |
| Board A: ingombro in pianta | ⚠️ | 40 × 25 mm provvisori, da ridurre dopo lo sbroglio |
| Connettore J1 identico al progetto T61 | ✅ | `JAE_AA01B-S040VA1_T61`, convertito da `T61.brd`; 44/44 piazzole coincidono con il Gerber di produzione T61 |
| Spina sotto compatibile con la spina 2×22 del flat | ✅ | 40 pad più 4 pad d'angolo (MP) |

## 3. File per la produzione (JLCPCB)

| File | Board A | Board B | Note |
|---|---|---|---|
| BOM JLCPCB (`Comment, Designator, Footprint, LCSC Part #`) | ✅ | ✅ | `produzione/x210ai_rev2.2_board{A,B}_bom_jlcpcb.csv`; tutti i codici LCSC presenti |
| BOM completa con MPN | ✅ | ✅ | `produzione/x210ai_rev2.2_board{A,B}_bom_completa_mpn.csv` |
| Spina AA01B-P040VA1 | – | DNP | esclusa come richiesto: non è su LCSC, si salda a mano |
| Gerber + forature | ❌ | ❌ | manca il PCB: li produce `export_prod.py` dal `.kicad_pcb` sbrogliato |
| CPL (posizioni e rotazioni) | ❌ | ❌ | dipende dal PCB sbrogliato (`export_prod.py`) |
| Dima 1:1 | ✅ | ✅ | `doc/x210ai_dima_board{A,B}_1a1.pdf` (piazzamento provvisorio; righello 50 mm verificato nel PDF) |

Componenti non montati sulla Board A (solo rame): J3 (piazzole USB), JP1/JP2 (ponticelli), TP1-TP4.

**Board B a 0,4 mm** (aggiornato il 28/10/2026): JLCPCB fa il 4 strati a 0,4 mm, solo con finitura ENIG e
senza pannello (non fa invece il 4 strati a 0,6 mm). Le due schede si ordinano entrambe da JLCPCB.

## 4. Prossimi passi di PASSAGGIO.md

| Passo | Stato |
|---|---|
| Adattare `design2.py` per due PCB | ✅ `design_boardA.py`, `design_boardB.py`, `edp_pinout.py`; tutti gli script di `gen2/` accettano `--board A|B` |
| Footprint `IPEX_20455-040E_90deg` | ✅ dal land pattern del catalogo I-PEX (`riferimenti/I-PEX/`) |
| Footprint `JAE_AA01_sandwich` | ✅ ricettacolo identico alla T61 · ⚠️ distanza tra le file della spina da misurare |
| Schema e PCB Board A, sbroglio, DRC = 0 | ⚠️ schema generato (`out_boardA/`, collegamenti verificati sul modello); PCB, sbroglio e DRC da eseguire in locale con KiCad |
| Schema e PCB Board B, sbroglio, DRC = 0 | ⚠️ come la Board A (`out_boardB/`) |
| `CABLE_SPEC.md` | ✅ `doc/CABLE_SPEC.md` |
| Dima, Gerber, BOM, CPL | ⚠️ dime e BOM fatte; Gerber e CPL no |
| Aggiornare LEGGIMI, FIRMWARE, VERIFICA | ❌ sono ancora quelli della rev 2.0 |
| Zip finale | ⚠️ `gen2/make_pkg.py` pronto (sostituisce `make_pkg.sh`); da lanciare dopo le pipeline |

## 5. Script da eseguire in locale

**Già eseguiti qui, non serve KiCad** (si rifanno da `x210ai_rev2.2_lavoro/x210ai_rev2.2_lavoro`):

```
python gen2/gen_jae_t61_footprint.py riferimenti/T61/T61.brd gen2/lib/x210ai.pretty
python gen2/gen_edp_footprint.py gen2/lib/x210ai.pretty
python gen2/gen_sandwich_footprint.py gen2/lib/x210ai.pretty
python gen2/design_boardA.py
python gen2/design_boardB.py
python gen2/gen_bom_rev22.py produzione
python gen2/gen_dima_rev22.py A doc/x210ai_dima_boardA_1a1.pdf
python gen2/gen_dima_rev22.py B doc/x210ai_dima_boardB_1a1.pdf
```

**Da eseguire in locale con KiCad**: tutti gli script di `gen2/` sono adattati alla rev 2.2 (`--board A|B`)
e `gen2/pipeline.py` li esegue in ordine: schema, ERC, PCB, Freerouting, DRC, confronto schema/PCB,
Gerber, BOM e CPL. Istruzioni complete in **`doc/ESECUZIONE_LOCALE.md`**. In breve (PowerShell):

```
& "C:\Program Files\KiCad\10.0\bin\python.exe" -m pip install shapely matplotlib gerbonara
& "C:\Program Files\KiCad\10.0\bin\python.exe" gen2\pipeline.py --board A
& "C:\Program Files\KiCad\10.0\bin\python.exe" gen2\pipeline.py --board B
& "C:\Program Files\KiCad\10.0\bin\python.exe" gen2\make_pkg.py
```

Gli schemi delle due schede sono già generati (`out_boardA/`, `out_boardB/`) e verificati sul modello dati.
Il PCB è stato provato solo con un pcbnew simulato: l'API reale di KiCad 10 e Freerouting si provano al
primo giro in locale. Il firmware non va ricompilato: `fw3/out/*.uf2` è valido.

## 6. Riordino della cartella

Rimossi i file orfani, con copia di sicurezza in `Canca/_backup_file_rimossi_2026-10-27.zip` (32 file):

| Rimosso | Motivo |
|---|---|
| `logs/` | log di installazione, compilazione ed emulazione della rev 2.0 |
| `pcb_out3/` | tentativo di sbroglio intermedio della rev 2.0 |
| `dl_kibot/` | sorgenti KiBot scaricati come riferimento, non usati da nessuno script |
| `pcb_out4/` intermedi (`routed.kicad_pcb`, `x210ai.kicad_pcb`, `x210ai.kicad_pro`, `.dsn`, `.ses`, `drc0.rpt`) | resta il PCB finale della rev 2.0 (`routed_p.*`, `drc_final.rpt`, libreria), come riferimento visivo |
| `doc/x210ai_dima_1a1.pdf/.png` | dima della scheda rev 2.0, che non si costruisce più |
| `gen2/gen_dima_boardB.py` | sostituito da `gen_dima_rev22.py` (Board A e B) |
| `gen2/make_pkg.sh` | sostituito da `gen2/make_pkg.py` (rev 2.2, gira anche su Windows) |
| `__pycache__/` | file temporanei di Python |

Spostati dentro il progetto: i file T61 (da `Canca/` a `riferimenti/T61/`) e il catalogo I-PEX CABLINE-VS
(`riferimenti/I-PEX/`).

Tenuti perché servono: `fw3/` (firmware e `.elf` per l'emulazione), `emu2/`, `spice2/`, `sch/` (schema e
simboli rev 2.0), `pcb_out4/` (riferimento), `gen2/` (generatori), `doc/` (da aggiornare).

## 7. Decisioni aperte

1. **Ingombro della Board B** (45,3 × 8,7 mm): riprovare la dima nuova, soprattutto il margine verso lo slot SIM.
2. **Cavo 1-1 o 1-N**: dipende da come si guardano i due J4 (`gen2/edp_pinout.py`, oggi 1-N). Va deciso
   prima di ordinare la Board B.
3. **Lunghezza del cavo**: lo standard I-PEX parte da 100 mm, ne servono 40-60 (cavo su misura o piegato).
4. **Spina sotto**: misurare col calibro la distanza tra le file della spina 2×22 del flat.
5. **Board B a 0,4 mm**: JLCPCB (solo ENIG, niente pannello).
