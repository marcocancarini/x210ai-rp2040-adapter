## Firmware in emulazione (rp2040js)

`verifica/emulazione/run_fw2.js` carica `x210ai_rev2.0.uf2` in un RP2040 emulato e collega i GPIO come sul
PCB: matrice della tastiera, Fn, linee PS/2 con pull-up, uscite verso l'EC. Un host USB minimo enumera il
dispositivo (seriale + HID) e registra i report HID. Risultato: **14/14 prove superate**
(`verifica/risultati/emulazione_firmware.json`).

| Prova | Risultato |
|---|---|
| Enumerazione USB con interfaccia HID e seriale | ok |
| Nessun impulso verso l'EC all'accensione, nessun riavvio | ok |
| 94 tasti (tutti quelli della `Keylist` di hektopuss): posizione in matrice e report HID giusto (tasto, modificatore, consumer o system) | 94/94 |
| Fn+PgUp: un comando all'EC, Fn 44,6 ms prima, PgUp 100,4 ms, Fn 44,6 ms dopo; nessun PgUp al PC | ok |
| PgUp da solo: PageUp al PC, nessun evento EC | ok |
| Fn+F5: report "radio" 1 poi 0 | ok |
| Fn+Ctrl tenuti 2,5 s: scambio attivo, 4 comandi EC (ThinkLight lampeggia 2 volte) | ok |
| Con lo scambio: Fn fisico = Ctrl sinistro; Ctrl fisico + PgUp = ThinkLight | ok |
| Comando seriale `SWAP`: scambio spento | ok |
| `JIS`: posizione vuota appresa e inviata come International1 (0x87) | ok |
| Fn+ThinkVantage 1 s: nessun riavvio; tenuto: riavvio UF2 dopo 3,03 s | ok |

I tempi verso l'EC hanno la granularità del ciclo del firmware (~5 ms). Se l'EC del tuo X210Ai volesse un
tasto più lungo, basta cambiare `EC_PGUP_MS` in `ThinkPad_RP2040_Keyboard.ino`.

## SPICE (ngspice)

Modello BSS138 da datasheet (`verifica/spice/bss138.lib`). Misure in `verifica/spice/spice_misure.txt`.

**Interruttore verso l'EC** (`ec_switch.cir`, grafico `documentazione/sim_ec_switch.png`). L'EC scandisce
la riga 24 (bassa 100 µs ogni ms) e legge la colonna 5 con un pull-up interno (provato 47 kΩ e 10 kΩ, a 3,3
e 5 V):

| Condizione | Colonna 5 |
|---|---|
| gate spento, riga bassa | 3,30 V (isolata: i due MOSFET in serie bloccano anche i diodi interni) |
| gate acceso, riga bassa | 3,7 mV (17 mV con pull-up 10 kΩ; 5,6 mV a 5 V) |
| gate acceso, riga alta | 3,30 V |
| discesa / salita | 67 ns / 0,32 µs |
| Fn della scheda madre (Q2b acceso) | 0,09 mV |

All'accensione e allo spegnimento del gate la colonna ha un picco di qualche nanosecondo (fino a 4 V e giù
a 2,6 V) per la capacità gate-drain: troppo breve e debole per essere letto come tasto.

**TrackPoint** (circuiti uguali alla rev 1.3, rifatti girare): PS/2 clock e data passano tra 3,3 e 5 V con
livello basso 0,10-0,14 V, salita 0,4-1,1 µs; il reset resta alto (4,5 V) finché il firmware non lo rilascia
(0,07 V). **Matrice**: con pull-up interno 80 kΩ e 100 pF la colonna torna alta (3,27 V) prima della
lettura della riga successiva.
