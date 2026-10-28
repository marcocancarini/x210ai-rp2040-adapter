# X210Ai rev 2.2 – Generare schema, PCB e file di produzione in locale

Tutti gli script sono in `gen2/` e funzionano per entrambe le schede con `--board A` o `--board B`;
senza `--board` rifanno la rev 2.0. `gen2/pipeline.py` esegue tutti i passi in ordine.

## 1. Cosa installare (una volta sola, Windows)

1. **KiCad 10** (o 9). Porta con sé il proprio Python con il modulo `pcbnew` e `kicad-cli`.
2. **Librerie Python** dentro il Python di KiCad (PowerShell):
   ```powershell
   & "C:\Program Files\KiCad\10.0\bin\python.exe" -m pip install shapely matplotlib gerbonara
   ```
3. **Freerouting 1.9.0**: scarica `freerouting-1.9.0.jar` dalla pagina delle release di Freerouting su
   GitHub e mettilo nella cartella del progetto, oppure indica dove si trova con `FREEROUTING_JAR`.
4. **Java**, nella versione richiesta dalla release di Freerouting (`java -version` deve funzionare).

`kicad-cli` viene cercato nel PATH e in `C:\Program Files\KiCad\*\bin`; se serve si indica con `KICAD_CLI`.
Le librerie di footprint di KiCad vengono cercate in `C:\Program Files\KiCad\*\share\kicad\footprints`
(oppure con `KICAD10_FOOTPRINT_DIR`).

## 2. Esecuzione

Dalla cartella del progetto (quella con `gen2/`, `doc/`, `sch/`), in PowerShell:

```powershell
$KPY = "C:\Program Files\KiCad\10.0\bin\python.exe"
$env:FREEROUTING_JAR = "$PWD\freerouting-1.9.0.jar"
& $KPY gen2\pipeline.py --board A
& $KPY gen2\pipeline.py --board B
& $KPY gen2\make_pkg.py
```

Si può ripartire da un passo (`--da route`) o eseguirne solo alcuni (`--solo sch,erc,netlist`).

| Passo | Cosa fa | Risultato |
|---|---|---|
| `sch` | schema dal modello dati (`gen_sch2.py`) | `out_boardX/x210ai_boardX.kicad_sch` |
| `erc` | ERC con `kicad-cli` | `out_boardX/erc.json` |
| `netlist` | netlist dello schema | `out_boardX/x210ai_boardX.xml` |
| `pcb` | PCB piazzato, piano GND su In1, pre-instradamento (`build_pcb.py`) | `x210ai_boardX.kicad_pcb`, `.kicad_pro`, copia in `stadi/01_piazzato` |
| `dsn` | file per Freerouting | `x210ai_boardX.dsn` |
| `route` | autorouting (Freerouting, 100 passate) | `x210ai_boardX.ses` |
| `ses` | importa piste e via nel PCB (`import_ses.py`) | PCB sbrogliato, copia in `stadi/02_sbrogliato` |
| `fill` | colate di massa sopra e sotto, riempimento zone | PCB finale |
| `drc` | DRC con `kicad-cli` | `drc.json`, `drc.rpt` (obiettivo: 0 errori) |
| `check` | schema ↔ PCB ↔ modello dati (`netlist_check.py`) | `parity.json` (obiettivo: `"errori": []`) |
| `prod` | Gerber e forature (zip), BOM e **CPL** JLCPCB, BOM con MPN | `produzione/boardX/` |
| `verify` | rilegge Gerber e CPL, misure DFM | a video |
| `dima` | dima 1:1 dal modello dati | `doc/x210ai_dima_boardX_1a1.pdf` |

Il progetto si apre in KiCad con `out_boardX/x210ai_boardX.kicad_pro`.

## 3. Già fatto senza KiCad

- Schemi di entrambe le schede (`out_boardA/`, `out_boardB/`). Lo stesso generatore rifà lo schema della
  rev 2.0 identico byte per byte all'originale, e i collegamenti degli schemi nuovi coincidono pin per pin
  con il modello dati.
- `build_pcb.py` provato con un pcbnew simulato: tutte le piazzole hanno la net giusta, i componenti stanno
  sul lato giusto, i campi LCSC sono corretti e le regole via della Board B (0,3/0,15) finiscono nel
  `.kicad_pro`.
- **Non provati**: l'API reale di KiCad 10 (export DSN, riempimento zone, DRC, Gerber) e Freerouting.

## 4. Cosa aspettarsi al primo giro

- **Piazzamento provvisorio**. Board A: gruppo RP2040 della rev 2.0, già sbrogliato, più J4. Board B: J1 e
  J4 con 2,5 mm di margine, J4 ruotato di 180° e spostato verso lo slot SIM. Se sposti componenti, cambia `PLACE` in `design_boardA.py` /
  `design_boardB.py` e rilancia da `pcb`; le modifiche fatte a mano in KiCad si perdono se rilanci `pcb`.
- **Differenze di API tra le versioni di KiCad**. Ribaltamento sul lato B e campi (LCSC, MPN) sono già
  gestiti per KiCad 7-10. Se un passo si ferma con `AttributeError`, il messaggio indica la funzione
  pcbnew da adattare.
- **Freerouting** potrebbe non completare tutte le net al primo colpo, soprattutto sulla Board B, che è
  piccola e densa. In quel caso: `drc.rpt` mostra le net non collegate, che si finiscono a mano in KiCad
  (`passaggio.md` prevede lo sbroglio manuale della Board B).
- **Rotazioni CPL**: per J1 e J4 (impronte del progetto) va controllata l'anteprima di JLCPCB, in
  particolare il pin 1.
- **Board B a 0,4 mm**: verificare se JLCPCB la fa; altrimenti PCBWay con gli stessi Gerber.

## 5. Script e scelta della scheda

| Script | `--board` | Note |
|---|---|---|
| `pipeline.py` | obbligatorio | esegue i passi qui sopra |
| `gen_sch2.py`, `build_pcb.py`, `fill_zones.py`, `netlist_check.py`, `export_prod.py`, `plot_nets.py` | A / B / (vuoto = 2.0) | |
| `gen_fw_pins.py` | A (o 2.0) | i GPIO non cambiano |
| `gen_dima_rev22.py`, `gen_bom_rev22.py`, `gen_*_footprint.py`, `design_board*.py` | – | non serve KiCad |
| `import_ses.py`, `drc.py`, `render.py`, `verifica/*.py` | – | valgono per qualunque PCB |
| `gen_dima.py`, `patch_fw.py`, `fplib.py`, `preroute.py`, `project.py` | – | rev 2.0 o moduli di supporto |
| `make_pkg.py` | – | pacchetto finale `x210ai_iso_adapter_kicad_rev2.2.zip` (sostituisce `make_pkg.sh`) |
