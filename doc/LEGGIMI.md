# X210Ai – adattatore USB con RP2040 per tastiera ISO/JIS (rev 2.2)

Due schede collegate da un cavo eDP a 40 fili:

* **Board A** (28,9 × 16,4 mm, rigida 4 strati 0,8 mm) sta sotto il palmrest: RP2040 (QFN-56 saldato, niente Pico), flash,
  quarzo, LDO 3,3 V, traslatori del TrackPoint, piazzole per i 4 fili verso **USB-CON1** e il ricettacolo
  eDP **J4**;
* **Board B** (29,1 × 28,8 mm, flessibile 4 strati con irrigidimenti) è **a scalino**: il gradino alto si
  innesta sul connettore tastiera della scheda madre (BTB_R_CONN1) con la spina **J2** e porta **J4** (cavo
  verso la Board A) e Q2/Q3 (emulano Fn+PgUp verso l'EC); un tratto flessibile scende di 1,5 mm sul gradino
  basso, appoggiato sulla scheda madre, che porta il ricettacolo **J1** della tastiera, ruotato di 25 gradi.

Alla scheda madre passano solo il **tasto di accensione** (diretto, funziona anche a PC spento), le
**masse** e il **Fn+PgUp emulato** per la **ThinkLight**. La tastiera ISO (e la JIS) funziona su Windows e
Linux senza driver. Firmware in `FIRMWARE.md`, verifiche in `VERIFICA.md`, cavo in `CABLE_SPEC.md`.

## Spessore

**Board B** (altezze dalla scheda madre). Sopra BTB_R_CONN1 la spina della tastiera non può salire: non ci
sta nemmeno una moneta da 5 centesimi (1,67 mm). Per questo la Board B è a scalino e la tastiera si innesta
accanto al connettore.

| Punto | mm |
|---|---|
| Gradino alto: accoppiamento spina J2 / BTB_R_CONN1 + flessibile 0,25 + irrigidimento FR4 0,2 sopra | ~2,0 |
| J4 con la spina del cavo innestata (1,1 sopra il flessibile) | ~2,9 |
| Gradino basso: irrigidimento 0,1 + flessibile 0,25 + J1 con la spina della tastiera (1,5) + dorso del flat (~1,0) | ~2,9 (+ Kapton) |

Sotto il gradino alto restano 1,5 mm: Q2/Q3 (SOT-363) arrivano a ~1,1 mm. Il quadrato bianco della scheda
madre è zona vietata (sopra meno di 1 mm): la Board B ne resta fuori di 0,8 mm.

**Board A**: componenti sotto ~1,2 mm (U3 SOT-23) + PCB 0,8 + J4 con la spina del cavo 1,1 = **~3,1 mm**
(obiettivo 4,0, spazio ~5,0). I fili USB vanno fatti uscire di piatto, senza accavallarli sulla scheda.

## Contenuto

| Cartella | Cosa contiene |
|---|---|
| `boardA/`, `boardB/` | Progetti KiCad 10 (`.kicad_pro`, `.kicad_sch`, `.kicad_pcb`) con le librerie del progetto |
| `produzione/boardA/`, `produzione/boardB/` | Gerber e forature (zip), BOM e CPL JLCPCB (un lato e due lati), BOM completa con MPN, rotazioni CPL applicate |
| `documentazione/` | Questo file, `FIRMWARE.md`, `VERIFICA.md`, `CABLE_SPEC.md`, report, dime 1:1 delle due schede, legenda dei componenti |
| `firmware/` | `x210ai_rev2.2.uf2` pronto, sorgente patchato (GPLv3) |
| `verifica/` | DRC, ERC e confronto schema-PCB delle due schede, SPICE, emulazione del firmware |
| `sorgenti/` | Gli script che generano schemi, PCB, firmware e file di produzione |

Apri `boardA/x210ai_boardA.kicad_pro` o `boardB/x210ai_boardB.kicad_pro` con KiCad 10. Le zone sono già
riempite; il DRC dà 0 errori e 0 non connessi.

## Come è fatta

| Blocco | Dettagli |
|---|---|
| MCU (Board A) | RP2040 + flash W25Q16JV 2 MB (USON 2×3) + quarzo 12 MHz, come il Raspberry Pi Pico |
| Alimentazione (Board A) | 5 V dai fili USB → LDO XC6206 3,3 V; 1,1 V dal regolatore interno |
| Cavo eDP | 40 pin: 16 righe, 8 colonne, Fn, TrackPoint (5 V, CLK, DATA, RESET), 2 gate EC, masse. Piedinatura in `CABLE_SPEC.md` |
| TrackPoint | traslatori BSS138 (Q1, Q2a) e pull-up sulla Board A |
| EC (Board B) | Q2b porta a massa il Fn della scheda madre; Q3 collega riga 24 e colonna 5 (PgUp). Pull-down da 100 kΩ (R13, R14): a cavo staccato o Board A spenta è tutto aperto |
| Accensione (Board B) | J1-19 → J2-19, diretto, non passa dal cavo |
| Strati | F.Cu, In1 massa, In2 segnali, B.Cu su entrambe (Board B flessibile). Colate di massa |
| Servizio (Board A, sopra) | ponticelli a saldare `BOOT` (JP1) e `RST` (JP2), pad `CLK`, `DIO`, `GND`, `3V3` |
| Fili USB (Board A, sotto) | J3: pad 1 = 5 V, 2 = D-, 3 = D+, 4 = GND, sul bordo |

## Ordinare (JLCPCB)

### Board A – 4 strati, 0,8 mm, ENIG

**PCB**: `produzione/boardA/x210ai_rev2.2_boardA_gerber_jlcpcb.zip`; 4 strati, **0,8 mm**, **ENIG**, via
0,4/0,2 coperte, piste e isolamenti minimi 0,1 mm, nessun controllo d'impedenza.

**Assemblaggio**, due possibilità:

* **Economic**, un lato: lato **Bottom**, `..._bom_jlcpcb_solo_bottom.csv` + `..._cpl_jlcpcb_solo_bottom.csv`.
  JLCPCB monta tutto tranne J4 (sopra), che saldi tu (40 pin passo 0,5 mm, con linguette di fissaggio).
* **Standard**, due lati: `..._bottom_e_top.csv`, JLCPCB monta anche J4 (C5160883). Se il configuratore chiede
  una dimensione minima, scegli "Panel by JLCPCB".

Nell'anteprima controlla le rotazioni prima di confermare (correzioni in `..._cpl_rotazioni_applicate.csv`),
in particolare il pin 1 di U1, U2, U3, Q1, Q2 e che Y1 stia sulle sue 4 piazzole.

### Board B – flessibile 4 strati con irrigidimenti

**PCB**: `produzione/boardB/x210ai_rev2.2_boardB_gerber_jlcpcb.zip`, servizio **Flex PCB** di JLCPCB: **4 strati**
(a 2 strati le linee tra J1 e J4 non si sbrogliano), poliimmide, spessore ~0,25 mm da confermare, via **0,4/0,2**, piste e isolamenti minimi 0,1 mm. Gli **irrigidimenti** sono
disegnati sullo strato User.1 (file `...-User_1.gbr` nello zip) e vanno indicati nell'ordine:

| Dove | Lato | Materiale |
|---|---|---|
| Gradino alto, sopra la spina J2 e l'allargamento | sopra | FR4 0,2 mm |
| Sotto J4 | sotto | FR4 0,2 mm |
| Gradino basso, sotto J1 | sotto | poliimmide 0,1 mm |

Nella zona dello scalino (tra il gradino alto e il gradino basso) non ci sono via né componenti: è la parte
che si piega a S di 1,5 mm (raggio ~1,5 mm).

**Componenti**: si saldano a mano. Da LCSC, insieme all'ordine: J1 ricettacolo AA01B-S040VA1 (C2938571),
J4 20455-040E-76 (C5160883), 2 × BSS138DW (C154900), 2 × 100 kΩ 0402 (C25741). La distinta completa è
`..._bom_completa_mpn.csv`.

**Spina J2 (JAE AA01B-P040VA1)**: è la stessa spina del flat della tastiera X200/X201 e non è su LCSC. Si
trova da distributori di componenti fuori produzione (AA01B-P040VA1-R3000), su Taobao/eBay, oppure si
recupera da una tastiera X200/X201 guasta.

### Cavo

Micro-coassiale con spina **I-PEX 20453-240T-03** ai due capi, **40 fili tutti collegati, nessun pin unito**,
barra di massa ai due capi, cablaggio 1-N (pin n → pin 41−n). Lunghezza 150 o 200 mm; standard: I-PEX
81422-100B-02-D (200 mm, DigiKey). Su misura: LCSC Custom Cables o produttori di cavi eDP. I cavi eDP generici per pannelli non vanno
bene. Dettagli e prova di continuità in `CABLE_SPEC.md`.

### Flash

Se la W25Q16JVUXIQ (C2843335) è esaurita, usa la **GD25Q16EEIGR** (C2986331): stesso contenitore, stessa
piedinatura, compatibile con il boot dell'RP2040.

## Montaggio

1. **Board B**: salda Q2, Q3, R13, R14 e la spina J2 sotto il gradino alto, J4 sopra, il ricettacolo J1 sul
   gradino basso. Controlla con la lente che non ci siano ponti (passo 0,5 mm: pasta e aria calda, o punta
   fine e flussante). Piega lo scalino a S solo dopo le saldature.
2. **Board A**: se hai scelto l'assemblaggio Economic, salda J4. Collega i 4 fili a J3 (filo sottile,
   AWG 32-36; D- e D+ ritorti). La piedinatura di USB-CON1 sulla scheda madre va verificata col tester.
3. **Cavo**: prova di continuità pin per pin (`CABLE_SPEC.md`) prima di collegarlo.
4. Carica il firmware: la prima volta la Board A appare da sola come disco **RPI-RP2**; copia
   `firmware/x210ai_rev2.2.uf2`.
5. Metti il Kapton sulla scheda madre sotto il gradino basso. Innesta J2 in BTB_R_CONN1 (pin 1 come in
   serigrafia), la spina della tastiera in J1, il cavo nei due J4; fissa la Board A sotto il palmrest
   (Kapton o biadesivo sottile).

## Da verificare prima di ordinare

1. **Spazio sopra il gradino basso e sopra J4** (col Patafix): circa 2,9 mm dalla scheda madre.
2. **Spina J2**: l'impronta è ricavata, non presa da un disegno JAE. Misura col calibro la spina sul
   flat della tastiera: 20 piedini per fila a passo 0,5 mm, file a **3,9 mm** tra i centri.
3. **Cavo**: 150 o 200 mm, 1-N; il percorso non deve capovolgere il cavo (`CABLE_SPEC.md`).
4. **USB-CON1**: piedinatura e presenza dei 5 V (anche in sospensione, se vuoi il risveglio da tastiera).

Le dime 1:1 delle due schede (`documentazione/`) sono già state provate sulla scheda madre; per la Board B
c'è anche la legenda di tutti i componenti delle due schede e degli ingombri della scheda madre.

Licenze: hardware di questo progetto libero; firmware GPLv3 (hektopuss) con parti Apache 2.0 (Frank Adams).
