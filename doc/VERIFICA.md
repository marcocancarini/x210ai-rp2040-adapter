# Verifica – rev 2.2

Tutte le prove si rifanno con `gen2/pipeline.py --board A|B` (KiCad 10.0.7, Freerouting 1.9.0) e con gli
script in `gen2/verifica/`, `emu2/` e `spice2/`. Risultati grezzi in `verifica/boardA/` e `verifica/boardB/`
del pacchetto (`drc.rpt`, `erc.json`, `parity.json`). "Verificato" = sul progetto, non su una scheda costruita.

## Requisiti

| Requisito | Come è soddisfatto | Prova |
|---|---|---|
| Tastiera ISO (e JIS) funzionante | L'RP2040 della Board A legge la matrice attraverso il cavo eDP e invia codici HID | emulazione: 94/94 tasti, 14/14 prove |
| RP2040 saldato sulla scheda, niente Pico | QFN-56 + flash + quarzo sulla Board A, montati da JLCPCB | BOM/CPL, baricentri nelle piazzole |
| Zona sopra il connettore madre sottile | Board B a scalino: sopra BTB_R_CONN1 solo il gradino alto (~2,0 mm); la tastiera si innesta sul gradino basso (~2,9 mm) | dima provata; spazio sopra il gradino basso da misurare col Patafix |
| Board A sotto il palmrest ≤ 4,0 mm | componenti sotto ~1,2 + PCB 0,8 + J4 innestato 1,1 = ~3,1 mm | cataloghi |
| Solo TrackPoint, niente touchpad | PS/2 con traslatori BSS138 sulla Board A; 5 V, CLK, DATA, RESET nel cavo | SPICE + emulazione |
| Nessun LED | nessun LED in BOM | BOM |
| Accensione verso la scheda madre | J1-19 → J2-19, sulla Board B, fuori dal cavo | netlist |
| Fn+PgUp (ThinkLight) dall'EC | Q2b + Q3 sulla Board B, gate dal cavo con pull-down R13/R14 | SPICE + emulazione |
| Scambio Fn/Ctrl, Windows e Linux | firmware invariato, solo classi HID standard | emulazione |

## Schede

| Controllo | Board A | Board B |
|---|---|---|
| Ingombro | 28,9 × 16,4 mm | 29,1 × 28,8 mm (a scalino, dislivello 1,5 mm) |
| Strati / spessore | 4 / 0,8 mm rigida | 4 / ~0,25 mm flessibile con irrigidimenti |
| ERC | 0 | 0 |
| DRC (errori / non connessi) | 0 / 0 | 0 / 0 |
| Schema = PCB | 43 componenti, 54 net, 0 errori | 7 componenti, 37 net, 0 errori |
| Via | 0,4/0,2 (anello 0,1) | 0,4/0,2 (anello 0,1), nessuna nella zona di piega |
| Pista minima | 0,1 mm | 0,1 mm |
| Rame–bordo | 0,25 mm | 0,25 mm |
| Ponte di maschera minimo | 0,2 mm | 0,2 mm |
| Foro–foro minimo | 0,30 mm | 0,31 mm |
| Fori | 113 da 0,2 mm | 85 da 0,2 mm |
| Gerber (contorno, strati) | 28,93 × 16,48 mm, 4 strati | 29,08 × 28,85 mm, 4 strati + irrigidimenti (User.1) |
| Dima 1:1 provata sulla scheda madre | sì (28/10/2026) | sì (28/10/2026) |

Isolamento foro–rame: la regola di KiCad è 0,2 mm; per rispettarla Freerouting lavora con un isolamento
alzato nel DSN (0,10 mm su entrambe). Sulla Board B le uscite di J1, ruotato di 25°, sono
pre-instradate fino al gradino alto (Freerouting non si aggancia a piazzole ruotate di angoli qualsiasi).

## Limiti noti

- Serigrafia: testi da 0,45 a 0,7 mm e linee da 0,12 mm, sotto i minimi consigliati da JLCPCB (1,0 / 0,15):
  possono risultare poco leggibili, non bloccano l'ordine.
- Sbroglio automatico: elettricamente completo, da rivedere a mano in KiCad dove serve.
- Altezze della pila della Board B prese dai documenti, non misurate.
- Distanza tra le file della spina 2×22 del flat stimata (3,9 mm), da misurare col calibro.
