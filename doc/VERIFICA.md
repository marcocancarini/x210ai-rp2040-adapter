# Verifica – rev 2.2

Tutte le prove si rifanno con `gen2/pipeline.py --board A|B` (KiCad 10.0.7, Freerouting 1.9.0) e con gli
script in `gen2/verifica/`, `emu2/` e `spice2/`. Risultati grezzi in `verifica/boardA/` e `verifica/boardB/`
del pacchetto (`drc.rpt`, `erc.json`, `parity.json`). "Verificato" = sul progetto, non su una scheda costruita.

## Requisiti

| Requisito | Come è soddisfatto | Prova |
|---|---|---|
| Tastiera ISO (e JIS) funzionante | L'RP2040 della Board A legge la matrice attraverso il cavo eDP e invia codici HID | emulazione: 94/94 tasti, 14/14 prove |
| RP2040 saldato sulla scheda, niente Pico | QFN-56 + flash + quarzo sulla Board A, montati da JLCPCB | BOM/CPL, baricentri nelle piazzole |
| Zona sopra il connettore madre sottile | Board B 0,4 mm: ~4,4 mm dalla scheda madre al dorso del flat, su ~5,0 | da misurare (prova della moneta, LEGGIMI) |
| Board A sotto il palmrest ≤ 4,0 mm | componenti sotto ~1,2 + PCB 0,8 + J4 innestato 1,1 = ~3,1 mm | cataloghi |
| Solo TrackPoint, niente touchpad | PS/2 con traslatori BSS138 sulla Board A; 5 V, CLK, DATA, RESET nel cavo | SPICE + emulazione |
| Nessun LED | nessun LED in BOM | BOM |
| Accensione verso la scheda madre | J1-19 → pin 119 della spina, sulla Board B, fuori dal cavo | netlist |
| Fn+PgUp (ThinkLight) dall'EC | Q2b + Q3 sulla Board B, gate dal cavo con pull-down R13/R14 | SPICE + emulazione |
| Scambio Fn/Ctrl, Windows e Linux | firmware invariato, solo classi HID standard | emulazione |

## Schede

| Controllo | Board A | Board B |
|---|---|---|
| Ingombro | 28,9 × 16,4 mm | 39,7 × 15,4 mm (L rovesciata) |
| Strati / spessore | 4 / 0,8 mm | 4 / 0,4 mm (JLCPCB: solo ENIG) |
| ERC | 0 | 0 |
| DRC (errori / non connessi) | 0 / 0 | 0 / 0 |
| Schema = PCB | 43 componenti, 54 net, 0 errori | 6 componenti, 37 net, 0 errori |
| Via | 0,4/0,2 (anello 0,1) | 0,3/0,15 (anello 0,075), tutti coperti |
| Pista minima | 0,1 mm | 0,1 mm |
| Rame–bordo | 0,25 mm | 0,25 mm |
| Ponte di maschera minimo | 0,2 mm | 0,2 mm |
| Foro–foro minimo | 0,30 mm | – |
| Fori | 113 da 0,2 mm | 88 da 0,15 mm |
| Gerber (contorno, strati) | 28,93 × 16,48 mm, 4 strati | 39,75 × 15,40 mm, 4 strati |
| Dima 1:1 provata sulla scheda madre | sì (28/10/2026) | sì (28/10/2026) |

Isolamento foro–rame: la regola di KiCad è 0,2 mm; per rispettarla Freerouting lavora con un isolamento
alzato nel DSN (0,13 mm sulla Board B, 0,10 mm sulla Board A).

## Limiti noti

- Serigrafia: testi da 0,45 a 0,7 mm e linee da 0,12 mm, sotto i minimi consigliati da JLCPCB (1,0 / 0,15):
  possono risultare poco leggibili, non bloccano l'ordine.
- Sbroglio automatico: elettricamente completo, da rivedere a mano in KiCad dove serve.
- Altezze della pila della Board B prese dai documenti, non misurate.
- Distanza tra le file della spina 2×22 del flat stimata (3,9 mm), da misurare col calibro.
