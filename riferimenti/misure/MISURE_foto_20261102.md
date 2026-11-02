# Misure dalla foto del 02/11/2026 (dima millimetrata)

Foto `PXL_20261102_114706251.jpg` (Pixel 9 Pro, 3072×4080, EXIF 2026-11-02 12:47) caricata su
GitHub il 02/11/2026: scheda madre X210Ai (51nb) con la **cornice di misura 1:1**
(`doc/x210ai_cornice_misura_1a1.pdf`, generata da `gen2/gen_dima_scala.py`) appoggiata sopra
BTB_R_CONN1, fotografata dall'alto.

## Rettifica (coordinate dima in mm)

Sistema di coordinate delle dime (`gen2/design_boardB.py`): origine al **centro di BTB_R_CONN1**,
x lungo il connettore (verso il palmrest = −x), y verso la vite (+y). La cornice ha i crocini:

| Crocino | Coordinate dima (mm) | Posizione in foto (px) |
|---|---|---|
| A | (−63, −34) | (1903, 1160) |
| B | (38, −34) | non visibile/rilevato |
| C | (38, 36) | (326, 3654) |
| D | (−63, 36) | (224, 1218) |

Omografia (affine) da A, C, D: **scala 24,07 px/mm**, rotazione della foto ≈ 88° rispetto alla
dima. Da OCR sui righelli letta anche la serigrafia `BTB_R_CONN1` e le scritte della cornice
(`slot SIM <-`, `lato vite (y+)`).

Immagine rettificata in coordinate dima (40 px/mm), con griglia 10 mm e ostacoli disegnati:
[`foto_20261102_rettificata_mm.jpg`](foto_20261102_rettificata_mm.jpg) (ridotta a 20 px/mm).

## Ostacoli misurati (confronto con `OSTACOLI` in `gen2/design_boardB.py`)

| Ostacolo | Da questa foto (mm) | Stima in `design_boardB.py` (mm) |
|---|---|---|
| Quadrato bianco (zona vietata, < 1 mm sopra) | x ≈ −27..+12 (lato 39,3 mm) nella finestra; lato alto non visibile (coperto dalla cornice sopra y = −26) | calibro 02/11: **x −27,25..12,0 · y −40,2..−7,2 → 39,25 × 33 mm** |
| BTB_R_CONN1 (origine) | centro (0,0), corpo ≈ 15,6 × 6,9 mm | x −7,8..7,8 · y −3,45..3,45 |
| Connettore FPC, flat arancione, CN1, vite, linguetta | come stima (±0,3 mm) | vedi `OSTACOLI` |

Finestra della cornice: x −55..30, y −26..28 (85 × 54 mm).

## Ingombri: zona libera per una scheda "a giro del quadrato bianco"

Zona libera = finestra − ostacoli (BTB_R_CONN1 escluso, ci si innesta la spina J2):
area totale **3460 mm²**.

| Zona | Rettangolo | Libero |
|---|---|---|
| **Destra del quadrato bianco** | x 12..30, y −26..28 → **18 × 54 mm** | **100 % (972 mm²)** |
| Sotto il quadrato | x −55..30, y −7,2..28 → 85 × 35,2 mm | 87 % (2600 mm²; dentro: vite, linguetta, CN1, flat, FPC) |
| Sinistra del quadrato | x −55..−27,25, y −26..28 → 27,8 × 54 mm | 83 % (1238 mm²; dentro: FPC, CN1, flat) |
| Sopra (y −26..−7,2) | 85 × 18,8 mm | 54 %: qui c'è il quadrato bianco vietato |

Altezze verticali (misure al calibro/monete, vedi conversazione): sopra il quadrato bianco < 1 mm
(vietato); sopra BTB_R_CONN1 con connettore innestato (2,1 mm) restano ~1,8 mm (moneta 5 centesimi
entra, 10 no) → ~3,9 mm totali dal piano scheda madre; **fuori dal quadrato bianco e fuori dal
connettore lo spazio tra i piani è ~5,0 mm**.

## Conclusione

Una scheda rigida che si innesta su BTB_R_CONN1 e **gira attorno al quadrato bianco** (senza starci
sopra) ha in pianta: un braccio destro libero di 18 × 54 mm, una base sotto di 85 × 35 mm (all'87 %)
e un braccio sinistro di 27,8 × 54 mm (all'83 %). In verticale fuori dal quadrato bianco ci sono
~5,0 mm, quindi una scheda rigida (0,8–1,6 mm) con componenti ci sta; sopra il connettore BTB_R_CONN1
restano ~1,8 mm (solo la spina J2, come nel progetto a scalino).

## Variante rev 2.3: scheda unica che aggira il quadrato bianco (senza cavo eDP)

Tre versioni di dima in `doc/` (generate da `gen2/gen_dima_giro.py --forma L|C|C2`, scala 1:1 verificata):

| Versione | File | Forma | Area |
|---|---|---|---|
| L | `x210ai_dima_giro_L_1a1.pdf` | base sotto il quadrato + braccio destro | 1500 mm² |
| C | `x210ai_dima_giro_C_1a1.pdf` | giù da BTB, ponte sotto, componenti a **sinistra** del quadrato (R3 27,25 × 22,7 mm, libera 100 %) | 988 mm² |
| C2 | `x210ai_dima_giro_C2_1a1.pdf` | giù da BTB, ponte sotto, risale a **destra** del quadrato, componenti **sopra** il quadrato (R4 57,75 × 19,3 mm, lato opposto a BTB) | 2087 mm² |
| C3 | `x210ai_dima_giro_C3_1a1.pdf` | ↓ da BTB, ponte sotto, risale a **sinistra** del quadrato (tra slot SIM e quadrato, R3 larga 11,75 mm), componenti **sopra** il quadrato (R4 69,5 × 19,3 mm, lato opposto a BTB) | 2150 mm² |
| **C4** | `x210ai_dima_giro_C4_1a1.pdf` | **ingrossata**: base piena 61,9 × 18,9 mm sotto il quadrato (R1, copre BTB), piccolo raccordo 7,65 × 3,4 mm verso sinistra, braccio sinistro 11,75 mm, componenti **sopra** il quadrato (R4 69,5 × 19,3 mm) | 2936 mm² |

Tutte: BTB_R_CONN1 coperta al 100 % (spina J2 sotto a 0,0, sopra restano ~1,8 mm → solo PCB sottile),
distanza dal quadrato bianco 0,50 mm, dagli altri ostacoli ≥ 0,5 mm. Foto di riferimento:
`PXL_20261019_233538594.jpg` (19/10).
