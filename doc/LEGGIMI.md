# X210Ai – scheda-ponte per tastiera ISO/JIS (rev 2.0)

Scheda da **36,5 × 10,6 mm**, 4 strati, che si infila tra la tastiera e il connettore tastiera della scheda
madre (BTB_R_CONN1):

* **J2** (sotto) è una spina come quella del flat della tastiera e si innesta in BTB_R_CONN1;
* **J1** (sopra) è un connettore come quello della scheda madre e riceve la spina della tastiera;
* l'**RP2040** (sotto, saldato sulla scheda, nessun modulo Pico) legge tutta la matrice e il TrackPoint e li
  manda al PC come tastiera + mouse USB, con 4 fili verso **USB-CON1**;
* alla scheda madre passano solo il **tasto di accensione** (pin 19, diretto, funziona anche a PC spento),
  le **masse** e il **Fn+PgUp emulato** (pin 1, 5, 24) che serve all'EC per accendere la **ThinkLight**.

La tastiera ISO (e la giapponese JIS) funziona quindi su Windows e su Linux senza driver: l'EC non vede più
la tastiera. Il tocco del firmware (scambio Fn/Ctrl, ThinkLight, modalità aereo, JIS) è descritto in
`FIRMWARE.md`; le verifiche in `VERIFICA.md`.

![scheda lato tastiera e lato scheda madre](documentazione/x210ai_render.png)

## Spessore

| Strato | mm |
|---|---|
| BTB_R_CONN1 + J2 innestati (altezza di accoppiamento serie JAE AA01) | 1,5 |
| PCB | 0,8 (JLCPCB) / 0,6 o 0,4 (PCBWay) |
| J1 + spina della tastiera innestati | 1,5 |
| **Totale dalla scheda madre al flat della tastiera** | **3,8 / 3,6 / 3,4** (oggi 1,5) |

Rispetto a oggi la spina della tastiera sale di **2,3 mm** con il PCB da 0,8 mm (2,1 mm con 0,6; 1,9 mm con
0,4). Il dorso della spina (flat e rinforzo) c'era già: non conta.

**Prova prima di ordinare.** Con la tastiera collegata normalmente, metti sul dorso della spina della
tastiera una pallina di Patafix, richiudi la tastiera premendola in sede, riaprila e misura lo spessore
schiacciato. Oppure fissa una moneta con un po' di nastro e richiudi: se la tastiera resta piatta e le viti
entrano senza forzare, quello spessore ci sta.

| Moneta | Spessore | Equivale a |
|---|---|---|
| 50 centesimi | 2,38 mm | PCB 0,8 mm con tolleranze sfavorevoli |
| 1 euro | 2,33 mm | PCB 0,8 mm |
| 20 centesimi | 2,14 mm | PCB 0,6 mm |
| 10 centesimi | 1,93 mm | PCB 0,4 mm |

Sotto la scheda restano 1,5 mm qualunque sia lo spessore del PCB; i componenti più alti (U3 SOT-23) sono
1,1 mm. La zona della scheda madre sotto il ponte deve essere libera: controllala con la dima
`documentazione/x210ai_dima_1a1.pdf` e metti un foglio di kapton sulla scheda madre.

## Contenuto

| File / cartella | Cosa contiene |
|---|---|
| `x210ai.kicad_pro`, `.kicad_sch`, `.kicad_pcb` | Progetto KiCad 7 (si apre anche con KiCad 8-10) |
| `x210ai.kicad_sym`, `x210ai.pretty/`, `sym-lib-table`, `fp-lib-table` | Librerie del progetto |
| `produzione/` | Gerber e forature, BOM e CPL per JLCPCB (due varianti), BOM completa con codici costruttore per PCBWay |
| `documentazione/` | Schema in PDF, render, dima 1:1, grafici delle simulazioni |
| `firmware/` | `x210ai_rev2.0.uf2` pronto, sorgente patchato (GPLv3) |
| `verifica/` | Risultati di DRC, confronto schema-PCB, emulazione del firmware, SPICE |
| `sorgenti/` | Gli script che generano schema, PCB, firmware e file di produzione |

### Aprire il progetto in KiCad 10

1. Usa una cartella nuova (o fai un backup): i file hanno gli stessi nomi della rev 1.x.
2. Apri `x210ai.kicad_pro`. Schema e PCB sono nel formato di KiCad 7: KiCad 10 li converte al primo
   salvataggio.
3. Nel PCB premi **B** (riempi zone) e lancia il **DRC**: con le regole incluse non ci sono errori.
   Le versioni più recenti possono mostrare qualche avviso in più (serigrafia), non bloccante.

## Come è fatta

| Blocco | Dettagli |
|---|---|
| MCU | RP2040 + flash W25Q16JV 2 MB (USON 2×3) + quarzo 12 MHz ABM8-272-T3, come il Raspberry Pi Pico |
| Alimentazione | 5 V dai fili USB → LDO XC6206 3,3 V; 1,1 V dal regolatore interno |
| Tastiera | J1 = JAE AA01B-S040VA1: 16 righe, 8 colonne e Fn sui GPIO |
| TrackPoint | 5 V dal pin 38; CLK, DATA e RESET attraverso traslatori BSS138 (Q1, Q2a) |
| EC | Q2b porta a massa il Fn della scheda madre (J2-1); Q3 è un interruttore bidirezionale tra riga 24 e colonna 5 (J2-24, J2-5), cioè il tasto PgUp. Gate con pull-down: a RP2040 spento è tutto aperto |
| Accensione | J1-19 → J2-19 direttamente |
| Strati | F.Cu (lato tastiera), In1 massa, In2 segnali, B.Cu (lato scheda madre); colate di massa su tutti gli strati |
| Servizio (lato tastiera) | ponticelli a saldare `BOOT` (JP1) e `RST` (JP2), pad `CLK`, `DIO`, `GND`, `3V3` |
| Fili USB (lato scheda madre) | piazzole `5V`, `D-`, `D+`, `G` sul bordo sinistro |

## Ordinare

Il progetto è a 4 strati: lo spessore si sceglie nell'ordine, i Gerber sono gli stessi.

### JLCPCB (0,8 mm)

**PCB**: carica `produzione/x210ai_rev2.0_gerber_jlcpcb.zip`; 4 strati, **0,8 mm**, finitura **ENIG**, via con
foro 0,2 mm / diametro 0,4 mm (piste e isolamenti minimi 0,1 mm), via coperte (tented), nessun controllo
d'impedenza.

**Assemblaggio**, due possibilità:

* **Economic** (più economico): un solo lato. Scegli il lato **Bottom** e carica
  `x210ai_bom_jlcpcb_solo_bottom.csv` + `x210ai_cpl_jlcpcb_solo_bottom.csv`. JLCPCB monta tutto tranne J1 e
  J2, che saldi tu.
* **Standard**: entrambi i lati. Carica `..._bottom_e_top.csv`: JLCPCB monta anche J1 (LCSC C2938571).
  Richiede una scheda di almeno 70 × 70 mm, quindi un pannello: scegli "Panel by JLCPCB" (ad esempio 2 × 6).

In entrambi i casi **J2 non è a magazzino LCSC** (vedi sotto) ed è segnata DNP.

Nell'anteprima di posizionamento controlla le rotazioni prima di confermare: per il lato bottom ho usato la
convenzione JLCPCB (angolo visto da sotto) con le correzioni della tabella di KiBot/JLCKicadTools
(`produzione/cpl_rotazioni_applicate.csv`). In particolare guarda il pallino del pin 1 di U1, U2, U3 e dei
tre Q, e che Y1 (quarzo) stia sulle sue 4 piazzole.

### PCBWay (0,6 o 0,4 mm)

PCBWay fa i 4 strati anche a 0,6 mm (standard) e 0,4 mm (lavorazione avanzata) e monta entrambi i lati.
Carica gli stessi Gerber, la CPL `..._bottom_e_top.csv` e la distinta `x210ai_bom_completa_mpn.csv`, che ha
costruttore e codice di ogni componente. PCBWay può anche procurarsi J2.

### J2 (JAE AA01B-P040VA1)

È la stessa spina del flat della tastiera X200/X201. Non è su LCSC: si trova da distributori di componenti
fuori produzione (es. come AA01B-P040VA1-R3000) o su Taobao/eBay. Un'alternativa è recuperarla da una tastiera
X200/X201 guasta. Si salda a mano (passo 0,5 mm, pasta e aria calda, o punta fine e molto flussante).

### Flash

Se la W25Q16JVUXIQ (C2843335) è esaurita, usa la **GD25Q16EEIGR** (C2986331): stesso contenitore USON 2×3,
stessa piedinatura, compatibile con il boot dell'RP2040.

## Montaggio

1. Salda J2 (e J1 se hai scelto l'assemblaggio Economic). Controlla con la lente che non ci siano ponti.
2. Collega i 4 fili alle piazzole `5V`, `D-`, `D+`, `G` (filo sottile, es. AWG 32-36; D- e D+ ritorti).
   La piedinatura di USB-CON1 sulla scheda madre va verificata con il tester prima di saldare.
3. Carica il firmware: la prima volta la scheda appare da sola come disco **RPI-RP2**; copia
   `firmware/x210ai_rev2.0.uf2`.
4. Metti il kapton sulla scheda madre nella zona della dima. Innesta J2 in BTB_R_CONN1 (pin 1 come in
   serigrafia), poi la spina della tastiera in J1.

## Da verificare prima di ordinare

1. **Spazio sopra la spina** (tabella "Spessore"): scegli lo spessore del PCB di conseguenza.
2. **Impronta di J2.** È ricavata, non presa da un disegno JAE (che non ho trovato). Misura col calibro la
   spina sul flat della tastiera: 20 piedini per fila a passo 0,5 mm, file di piazzole a **3,9 mm** tra i
   centri. Se è diversa dimmelo prima di ordinare.
3. **Orientamento.** J1 e J2 hanno il pin 1 dove ce l'ha BTB_R_CONN1 nella foto di hektopuss (pin dispari
   verso il quadrato bianco, pin 1 a sinistra guardando come nella tua foto). Controlla sulla scheda madre la
   serigrafia "1"/"39" accanto al connettore e confrontala con la dima.
4. **Ingombro**: il ponte si estende 29 mm a sinistra del centro del connettore, 5 mm verso il quadrato
   bianco e 5,6 mm verso la vite. Ritaglia la dima e appoggiala.
5. **USB-CON1**: piedinatura e presenza dei 5 V (anche in sospensione, se vuoi il risveglio da tastiera).

Licenze: hardware di questo progetto libero; firmware GPLv3 (hektopuss) con parti Apache 2.0 (Frank Adams).
