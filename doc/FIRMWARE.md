# Firmware – rev 2.2

Il firmware è quello di [hektopuss/ThinkPad_RP2040_Keyboard](https://github.com/hektopuss/ThinkPad_RP2040_Keyboard)
(commit `970379d`, GPLv3) con una patch per l'adattatore. Il firmware è lo stesso della rev 2.0: i GPIO della Board A coincidono
con quelli della scheda-ponte rev 2.0 (controllo automatico su `x210ai_pins.h`). La patch è applicata da
`sorgenti/gen2/patch_fw.py`, che sostituisce solo testo esatto del file originale: se hektopuss aggiorna il
repository, lo script si ferma invece di produrre un file sbagliato.

`firmware/x210ai_rev2.2.uf2` (identico al file della rev 2.0) è già compilato (core arduino-pico 6.3.0, scheda "Raspberry Pi Pico", 71 kB):
basta copiarlo sul disco **RPI-RP2**.
SHA-256: `bf325f9a294858f8f08f89307a970341929446da00dd066ff3580920e6f4c984`

## Cosa cambia rispetto all'originale

| Funzione | Come funziona |
|---|---|
| **Fn+PgUp = ThinkLight** | La ThinkLight la accende l'EC della scheda madre, che non vede più la tastiera. Il firmware gli "preme" Fn+PgUp: sulla Board B Q2b porta a massa il Fn della scheda madre, Q3 collega riga 24 e colonna 5 (PgUp); i gate arrivano dalla Board A nel cavo eDP (EC_FN_G, EC_PGUP_G). Sequenza: Fn 40 ms, PgUp 100 ms, Fn ancora 40 ms, pausa 150 ms. Fino a 4 comandi in coda. |
| **Scambio Fn / Ctrl** | Tieni premuti insieme **Fn e Ctrl sinistro per 2 s**: i due tasti si scambiano. La ThinkLight lampeggia due volte come conferma. Lo stesso gesto (gli stessi due tasti fisici) torna indietro. L'impostazione resta salvata in flash. Con lo scambio attivo, anche **Ctrl+PgUp** (cioè il nuovo Fn) accende la ThinkLight. |
| **Fn+F5 = modalità aereo** | Invia il tasto HID "Wireless Radio Button": Windows attiva/disattiva la modalità aereo, Linux lo riceve come `KEY_RFKILL` (GNOME/KDE fanno lo stesso). Prima era Win+A, valido solo su Windows. |
| **Fn+ThinkVantage = bootloader** | Va tenuto **3 s**: prima bastava sfiorarlo per riavviare in modalità UF2. |
| **Tastiera giapponese (JIS)** | I 5 tasti in più (ろ, かな, ¥, 変換, 無変換) cadono in posizioni vuote della matrice. Il comando seriale `JIS` le impara (vedi sotto) e le invia come International1-5, che Windows e Linux con layout giapponese riconoscono. |
| **Risveglio dalla sospensione** | Un tasto qualsiasi chiede al PC di svegliarsi (USB remote wakeup). Funziona se USB-CON1 resta alimentata in sospensione e il sistema lo permette; il tasto di accensione funziona comunque, perché passa diretto alla scheda madre. |
| **Niente LED** | Il GPIO25 (LED del Pico) qui è una riga della matrice. |
| **GPIO** | Seguono il PCB della Board A: sono in `x210ai_pins.h`, generato dal modello del progetto. |

La tastiera ISO italiana funziona già con le mappe di hektopuss (che usa una tastiera tedesca ISO): `< >`
è `KEY_NON_US_BS` e `ù` arriva come il tasto a sinistra di Invio. Il layout lo sceglie il sistema
operativo: imposta **Italiano** (o **Giapponese** per la JIS).

### Scorciatoie (invariate, da hektopuss)

| Fn + | Effetto | Fn + | Effetto |
|---|---|---|---|
| Home / End | luminosità + / − | F2 | Win+L (blocca) |
| ← → ↑ ↓ | brano prec. / succ. / stop / play | F4 | sospensione |
| PgUp | ThinkLight (EC) | F7 | Win+P (schermi) |
| PgDn | (nessuna) | F8 / F9 / F10 / F11 | TrackPoint on/off, reset, init, errore |
| Spazio | zoom | F12 | ibernazione |
| Esc | console di debug on/off | Win | disattiva/riattiva il tasto Win |
| Bloc Scorr | Bloc Num | Bloc Maiusc | disattiva/riattiva Bloc Maiusc |

Volume e muto sono tasti diretti (senza Fn) e funzionano su entrambi i sistemi. Fn+Muto non fa nulla,
come nel firmware originale (il confronto con `KEY_MUTE` non scatta mai).

## Console seriale

La scheda si presenta anche come porta seriale USB (qualsiasi velocità): Monitor seriale dell'IDE Arduino,
PuTTY su Windows, `screen /dev/ttyACM0` su Linux. Comandi (Invio per confermare):

| Comando | Effetto |
|---|---|
| `HELP`, `STAT` | aiuto, stato (anche scambio Fn/Ctrl e tasti JIS appresi) |
| `SWAP` | scambia Fn e Ctrl (salvato) |
| `LIGHT` | manda un comando ThinkLight all'EC |
| `JIS` | apprendimento dei tasti giapponesi |
| `JISX` | cancella i tasti giapponesi appresi |
| `BOOT` | riavvio nel bootloader UF2 |
| `DON` / `DOFF`, `TPI`, `TPR`, `TPE`, `TPER` | debug e TrackPoint, come nell'originale |

**Apprendimento JIS:** scrivi `JIS`. La console chiede i tasti uno alla volta, in quest'ordine:
1. ろ (accanto a Shift destro);
2. かな / カタカナ;
3. ¥ (accanto a Backspace);
4. 変換 (a destra della barra);
5. 無変換 (a sinistra della barra).

Premi il tasto richiesto. Esc salta quello che la tastiera non ha. Alla fine le posizioni vengono salvate.
Una tastiera ISO non ne ha bisogno.

Le impostazioni (scambio e tasti JIS) stanno nell'ultimo settore della flash (EEPROM emulata). Restano
anche quando aggiorni il firmware copiando un nuovo `.uf2`.

## GPIO

| Segnale | GPIO |
|---|---|
| Colonne C17, C15, C13, C11, C9, C7, C5, C3 | 0-7 |
| Fn (pin 1) | 8 |
| Righe R32, R30, R28, R26, R24, R22, R20, R18, R16 | 9-17 |
| Righe R14, R12, R10, R8, R6, R4, R2 | 18-24 |
| TrackPoint reset / clock / data | 25 / 28 / 29 |
| EC: Fn (gate Q2b) / PgUp (gate Q3) | 26 / 27 |

L'ordine segue il giro dei pin del QFN. Righe, colonne, Fn, TrackPoint e gate EC passano dal cavo eDP: la
piedinatura del cavo è in `CABLE_SPEC.md`.

## Caricare

* **Prima volta**: l'RP2040 con la flash vuota si presenta da solo come disco **RPI-RP2**: copia il `.uf2`.
* **Aggiornamenti**: Fn+ThinkVantage tenuti 3 s, oppure il comando `BOOT`, oppure doppio reset (cortocircuita
  due volte di fila il ponticello **RST**, JP2). Emergenza: tieni chiuso **BOOT** (JP1) durante il reset.
* **SWD** (facoltativo): pad `CLK`, `DIO`, `GND`, `3V3` sul lato superiore della Board A, accanto a J4.

## Compilare

1. Arduino IDE 2.x, URL aggiuntivo del gestore schede:
   `https://github.com/earlephilhower/arduino-pico/releases/download/global/package_rp2040_index.json`
2. Installa "Raspberry Pi Pico/RP2040/RP2350" (provato con la 6.3.0).
3. Apri `firmware/ThinkPad_RP2040_Keyboard/ThinkPad_RP2040_Keyboard.ino` (cartella già patchata).
4. Scheda **Raspberry Pi Pico**, USB stack **Pico SDK**, Flash Size **2MB (no FS)**: la EEPROM emulata usa
   l'ultimo settore.

Da riga di comando:
`arduino-cli compile -b rp2040:rp2040:rpipico --output-dir out ThinkPad_RP2040_Keyboard`

Licenza: GPLv3 (hektopuss), con parti Apache 2.0 di Frank Adams (thedalles77).
