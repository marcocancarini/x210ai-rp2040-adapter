# Verifica – rev 2.0

Tutte le prove si rifanno con gli script in `verifica/` e `sorgenti/gen2/` (KiCad 7.0.11, ngspice 42,
rp2040js 1.1.1, arduino-pico 6.3.0). Risultati grezzi in `verifica/risultati/`.

## Requisiti

| Requisito | Come è soddisfatto | Stato |
|---|---|---|
| Tastiera ISO (e JIS) funzionante | L'RP2040 legge la matrice e invia codici HID; layout scelto dal sistema operativo | emulazione: 94/94 tasti |
| RP2040 saldato sulla scheda, niente Pico | QFN-56 + flash + quarzo sul PCB, montati da JLCPCB | BOM/CPL |
| Scheda il più sottile possibile | Ponte sul connettore: 3,8 mm (PCB 0,8) / 3,4 mm (PCB 0,4) dalla scheda madre al flat | vedi LEGGIMI |
| Solo TrackPoint, niente touchpad | PS/2 TrackPoint con traslatori; linee touchpad non collegate | SPICE + emulazione |
| LED facoltativi | Nessun LED | – |
| Accensione verso la scheda madre | J1-19 → J2-19 diretto | netlist |
| Fn+PgUp (ThinkLight) dall'EC | Q2b + Q3 emulano Fn+PgUp | SPICE + emulazione |
| Scambio Fn/Ctrl | Firmware, salvato in flash | emulazione |
| Windows e Linux | Solo classi HID standard (tastiera, consumer, system, radio, mouse) | emulazione USB |

@@RISULTATI@@
