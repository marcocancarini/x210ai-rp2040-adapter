# X210Ai rev 2.2 – Specifica del cavo eDP (Board A ↔ Board B)

Fonte della piedinatura: `gen2/edp_pinout.py` (questa tabella è generata da lì; se cambi il file, rigenera
la tabella). Quote dei connettori: catalogo I-PEX **CABLINE-VS** (rev. 202610R0).

## Connettori

| | Parte | Note |
|---|---|---|
| Sulle schede (J4 di A e J4 di B) | **I-PEX 20455-040E-76** (ricettacolo, 40 pin, passo 0,5 mm) | accoppiamento orizzontale, altezza innestata 1,00 +0,1 mm, impronta `x210ai:IPEX_20455-040E_90deg` |
| Sul cavo (due capi) | **I-PEX 20453-240T-03** (spina con barra di sgancio) | è la spina per **micro-coassiale**, non per FPC |

**Correzione rispetto a PASSAGGIO.md**: il 20453 non si monta su un FPC piatto. Il cavo è un fascio di 40
micro-coassiali (AWG 40-44), largo circa 20 mm. Se si vuole un FPC vero bisogna cambiare famiglia:
CABLINE-VSF ha la spina per FPC e usa la stessa impronta.

### Ingombro dell'impronta

| Voce | mm |
|---|---|
| Piazzole segnale | 0,25 × 0,90, passo 0,50, 19,50 tra il pin 1 e il pin 40 |
| Barra di massa (pad 41) | 0,55 × 0,90, a ±10,65 dal centro |
| Linguette di fissaggio (pad 41) | 1,40 × 1,90, a ±12,85, a 1,42 dal bordo inferiore delle piazzole |
| Area senza componenti (barra di sgancio) | **28,2 × 6,7** |
| Corpo | 26,25 × 3,4 (dalla punta dei piedini: 3,95) |
| Con la spina innestata | profondità 5,1 dalla punta dei piedini; il cavo esce da quel lato |

Sotto il connettore ci va solo solder resist o massa (nota 2 del catalogo): niente rame scoperto né via non
coperte.

## Tipo di cavo: "1-1" o "1-N"

I-PEX vende due cablaggi standard da 40 pin, con micro-coassiale AWG 40:

| Tipo | Collegamento | Lunghezza 100 mm | 200 mm | 300 mm |
|---|---|---|---|---|
| 1-1 | pin n → pin n | 82690-100B-01-D | 82691-100B-01-D | 82692-100B-01-D |
| 1-N | pin n → pin 41-n | 82190-100B-02-D | 81422-100B-02-D | 82290-100B-02-D |

- I due J4 sullo **stesso lato** delle schede, uno di fronte all'altro, con il cavo steso: serve il **1-N**.
- Un J4 sul lato opposto, oppure il cavo **piegato una volta** (la piega ribalta la spina): serve il **1-1**.

Oggi `edp_pinout.CABLE = "1-N"`. Cambia solo la numerazione dei pin di J4 sulla Board B. **Va deciso prima
di ordinare la Board B**, quando si conosce il percorso reale del cavo.

**Lunghezza**: lo standard I-PEX parte da 100 mm; PASSAGGIO.md chiede 40-60 mm. Ci sono due strade:
1. un cablaggio su misura (I-PEX o un fornitore di cavi eDP), indicando le spine 20453-240T-03, la
   lunghezza, il tipo 1-1 o 1-N, tutti i 40 conduttori collegati e la barra di massa ai due capi;
2. un cavo da 100 mm piegato. Attenzione: ogni piega ribalta la spina e cambia il tipo che serve.

I cavi eDP generici di AliExpress hanno spesso **pin non collegati o incrociati** (sono pensati per i
pannelli). Vanno bene solo se li verifichi con la procedura sotto.

## Piedinatura

| Pin A | Pin B (1-N) | Net | Pin A | Pin B (1-N) | Net |
|---|---|---|---|---|---|
| 1 | 40 | GND | 21 | 20 | GND |
| 2 | 39 | GND | 22 | 19 | KB_C17 |
| 3 | 38 | VBUS | 23 | 18 | KB_R16 |
| 4 | 37 | VBUS | 24 | 17 | KB_C15 |
| 5 | 36 | TP_RST_5V | 25 | 16 | KB_R14 |
| 6 | 35 | TP_DATA_5V | 26 | 15 | KB_C13 |
| 7 | 34 | GND | 27 | 14 | KB_R12 |
| 8 | 33 | TP_CLK_5V | 28 | 13 | KB_C11 |
| 9 | 32 | GND | 29 | 12 | KB_R10 |
| 10 | 31 | EC_PGUP_G | 30 | 11 | KB_C9 |
| 11 | 30 | EC_FN_G | 31 | 10 | GND |
| 12 | 29 | GND | 32 | 9 | KB_R8 |
| 13 | 28 | KB_R32 | 33 | 8 | KB_C7 |
| 14 | 27 | KB_R30 | 34 | 7 | KB_R6 |
| 15 | 26 | KB_R28 | 35 | 6 | KB_C5 |
| 16 | 25 | KB_R26 | 36 | 5 | KB_R4 |
| 17 | 24 | KB_R24 | 37 | 4 | KB_C3 |
| 18 | 23 | KB_R22 | 38 | 3 | KB_R2 |
| 19 | 22 | KB_R20 | 39 | 2 | KB_FN |
| 20 | 21 | KB_R18 | 40 | 1 | GND |

Barra di massa e linguette (pad 41) a GND su entrambe le schede. Con il cavo 1-1 il pin B è uguale al pin A.

Scelte:
- righe e colonne seguono l'ordine dei pin del connettore tastiera J1. Sulla Board B, J4 è ruotato di
  180° con il pin 1 verso J1: Fn è sul pin 2 della Board B (pin 39 della Board A), subito dopo
  la massa del pin 1, il più vicino a J1, così le piste J1 → J4 si annidano senza incroci;
- il clock PS/2 (pin A8) sta tra due masse;
- 5 V del TrackPoint su due pin (corrente di pochi mA; il catalogo dà 0,3 A per contatto con AWG 40);
- il **tasto di accensione (pin 19 di J1) non passa dal cavo**: va diretto da J1 a BTB_R_CONN1 sulla
  Board B;
- i gate EC_FN_G / EC_PGUP_G hanno il pull-down da 100 kΩ (R13, R14) sulla **Board B**: a cavo staccato o
  con la Board A spenta l'EC non vede tasti premuti.

## Requisiti elettrici

| Voce | Valore |
|---|---|
| Conduttori | 40, tutti collegati, schermi alla barra di massa ai due capi |
| Segnali | matrice e PS/2 lenti (scansione in kHz, PS/2 10-17 kHz): nessun vincolo di impedenza |
| Corrente | < 50 mA in totale (TrackPoint); 0,3 A per contatto ammessi |
| Resistenza del conduttore | < 2 Ω per filo (100 mm di AWG 40: circa 0,35 Ω) |

## Verifica prima del montaggio

1. Con il tester in continuità, misura **tutti i 40 pin**: ogni pin A deve suonare solo con il pin B della
   tabella (1-N o 1-1, secondo il cavo scelto). Basta un pin mancante o incrociato per scartare il cavo.
2. Controlla che nessun segnale sia in corto con la barra di massa.
3. A schede montate e **senza** la tastiera, misura tra J1-38 (Board B) e GND: deve esserci il 5 V della USB
   (cavo collegato, Board A alimentata).
4. Con la tastiera collegata, nel monitor seriale del firmware premi Fn e un tasto per riga: se una riga o
   una colonna manca, ricontrolla il cavo prima delle saldature.

## Da decidere

- [ ] Tipo di cavo 1-1 o 1-N (dal piazzamento reale delle due schede).
- [ ] Lunghezza: su misura (40-60 mm) o 100 mm standard piegato.
- [ ] **Ingombro della Board B**: il ricettacolo da 40 pin richiede 28,2 × 6,7 mm liberi, più della stima
  "15 × 12 mm". Nel piazzamento preliminare (`design_boardB.py`, con 2,5 mm di margine extra tra J1 e J4)
  la Board B misura 45,3 × 8,7 mm ed esce di 8,8 mm dall'ingombro della rev 2.0 (29 mm a sinistra del centro del connettore). Alternative: un
  connettore più piccolo (FPC ZIF a passo 0,3 mm con FPC su misura) o meno segnali sul cavo.
