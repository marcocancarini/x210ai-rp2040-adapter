# Misure dalla foto del 02/11/2026 (dima millimetrata)

Foto `PXL_20261102_114706251.jpg` (Pixel 9 Pro, 3072×4080, EXIF 2026-11-02 12:47) caricata su
GitHub il 02/11/2026: scheda madre X210Ai (51nb) con la **cornice di misura 1:1**
(`doc/x210ai_cornice_misura_1a1.pdf`, generata da `gen2/gen_dima_scala.py`) appoggiata sopra
BTB_R_CONN1, fotografata dall'alto.


> **Correzione 02/11/2026 (sera).** La rettifica qui sotto (crocini A/C/D → 24,07 px/mm) è **sbagliata**:
> nella foto la cornice è appoggiata **ruotata di 180°** (crocino A a destra, "lato vite (y+)" a
> sinistra, mentre la vite reale è a destra) e **non è centrata su BTB_R_CONN1** (il suo (0,0) cade
> ~23 mm e ~52 mm lontano dal connettore). Per questo la tabella "Elementi riconosciuti" e l'immagine
> rettificata (ora tolta) non valgono. Vedi la sezione **Correzione** in fondo.

## Rettifica (coordinate dima in mm) — NON VALIDA, vedi Correzione

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

(L'immagine rettificata `foto_20261102_rettificata_mm.jpg` era corrotta, a strisce ripetute, ed è stata tolta.)

## Elementi riconosciuti dal parsing della foto — NON VALIDI (rettifica sbagliata)

| Elemento | x (mm) | y (mm) | Dimensione |
|---|---|---|---|
| connettore FPC sinistro | −55,0..−33,4 | −26,0..−13,9 | 21,6 × 12,1 mm |
| connettore FPC centrale | −25,6..1,7 | −26,0..−13,9 | 27,3 × 12,1 mm |
| connettore FPC destro | 9,3..30,0 | −26,0..−14,0 | 20,7 × 12,1 mm |
| **slot SIM** (colonna verticale a sinistra) | −54,0..−42,0 | −12,5..4,3 | 12 × 16,8 mm |
| flat arancione | −37,35..−21,35 | 12,7..17,2 | 16 × 4,5 mm |
| vite | centro (−7,8, 19,1) | raggio 3,55 | — |
| linguetta vite | −13,1..−5,8 | 22,3..26,4 | 7,3 × 4,1 mm |
| connettore CN1 | −30,35..−21,6 | 17,25..23,5 | 8,75 × 6,25 mm |

Nota: il vecchio rettangolo "slot SIM" (x −50..−40, y −38,9..−26,9, dalla foto 19/10) era fuori dalla
finestra della cornice e non c'entra: lo slot SIM vero è la colonna a sinistra sopra. I nomi in
`gen2/gen_dima_giro.py` sono corretti di conseguenza.

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

## Board C (rev 2.3): scheda unica che aggira il quadrato bianco (senza cavo eDP)

Dime in `doc/x210ai_dima_boardC_1a1.pdf` (v1, portrait) e `doc/x210ai_dima_boardC_v2_1a1.pdf` (v2, tutti gli oggetti ruotati di 90° in senso antiorario nelle coordinate dima), generate da `gen2/gen_dima_giro.py` (Board C, forma C4,
pagina A4 portrait; scala 1:1 verificata, righello 50,09 mm).

Forma C4 (coordinate dima, origine = centro BTB_R_CONN1):

| Parte | Rettangolo | Dimensione |
|---|---|---|
| R1 base (copre BTB, J2 sotto a 0,0) | x −31,85..30, y −6,7..12,2 | 61,9 × 18,9 mm |
| R2 raccordo | x −39,5..−31,85, y −6,7..−3,3 | 7,65 × 3,4 mm |
| R3 braccio sinistro (tra slot SIM e quadrato) | x −39,5..−27,75, y −60..−3,3 | 11,75 × 56,7 mm |
| R4 componenti sopra il quadrato (lato opposto a BTB) | x −39,5..30, y −60..−40,7 | 69,5 × 19,3 mm |

Area 2936 mm²; BTB coperta al 100 %; distanza dal quadrato bianco 0,50 mm, dagli altri ostacoli
≥ 0,5 mm (FPC 0,50, slot SIM 0,50, flat 0,50, vite 3,35, CN1 5,05). Sopra BTB restano ~1,8 mm
(solo PCB sottile); in R4 (fuori dal quadrato in pianta) ~5 mm in verticale. Foto di riferimento:
`PXL_20261019_233538594.jpg` (19/10).

## Correzione (02/11/2026): parsing rifatto, nomi degli ingombri corretti — dima Board C v3.1

**Calibrazione nuova**, indipendente dalla cornice: origine = centro del corpo di BTB_R_CONN1,
scala dal lato corto del quadrato bianco (33 mm) e verifica sui bordi del quadrato e sulla staffa
metallica (errore ≤ 0,6 mm). In entrambe le foto: in alto = +x dima, a destra = +y dima.

| Foto | Scala | Origine (px) |
|---|---|---|
| `PXL_20261019_233538594.jpg` (2654 px) | 16,2 px/mm | (1725, 460) |
| `PXL_20261102_114706251.jpg` (3072 px) | 23,76 px/mm | (2337, 2130) |

**Ingombri** (coordinate dima, mm): le posizioni della v3 originale erano giuste, erano sbagliati i nomi.

| Nome corretto | x | y | Prima si chiamava |
|---|---|---|---|
| quadrato bianco (vietato) | −27,25..12 | −40,2..−7,2 | invariato |
| BTB_R_CONN1 | −7,8..7,8 | −3,45..3,45 | invariato |
| **slot SIM** (contatti dorati) | −45..−32,35 | −2,8..12,7 | "connettore FPC" |
| flat arancione (stretto, verticale) | −37,35..−21,35 | 12,7..17,2 | invariato |
| connettore CN1 (blocco nero) | −30,35..−21,6 | 17,25..23,5 | invariato |
| **connettore FPC (ZIF beige)** | −45,5..−34,2 | 18,2..25,2 | mancava (nuovo) |
| vite | centro (−7,8, 19,1), r 3,55 | | invariato |
| linguetta vite | −13,1..−5,8 | 22,3..26,4 | invariato |

Tolti: il vecchio "slot SIM" (x −50..−40, y −38,9..−26,9), che cadeva sulla **plastica del telaio**
(non sulla scheda madre), e i rettangoli aggiunti il 02/11 dalla rettifica sbagliata (slot SIM a
colonna, 3 "connettori FPC" in alto, di cui uno attraverso il quadrato bianco).

**Riferimenti** (non ostacoli PCB, grigio tratteggiato nella dima): bordo plastica telaio
x < −39,2 per y −47..−5,3 e x < −44 per y 4,8..30; staffa metallica sopra BTB x 11,15..15,55,
y −9,3..13,7 (è il "nastro alluminio" di `design_boardB.py`, in realtà una staffa).

**Forma v3 con gli ingombri corretti** (`gen2/gen_dima_giro.py --rot90ccw --v31`): area 2134 mm²,
BTB coperta; distanze: quadrato 0,50, slot SIM 0,50, flat 0,50, CN1 5,05, FPC ZIF 6,44, vite 3,35,
linguetta 10,10, staffa 2,15 mm. **Da verificare**: il bordo basso della U (x = −39,5) arriva sul
bordo della plastica del telaio (−39,2): sovrapposizione ~0,3 mm, dentro l'errore di misura.

Overlay di controllo (forma bianca + ingombri sulla foto): `verifica_v3_1_foto20261019.jpg`,
`verifica_v3_1_foto20261102.jpg`. Dima: `doc/x210ai_dima_boardC_v3_1_1a1.pdf` (stampa) e `.svg`
(stessa pagina A4 1:1, modificabile con Inkscape).

### v3.2 (02/11/2026, dopo la prova fisica della v3.1)

Correzioni misurate sulla scheda madre: la plastica del telaio entra ~2 mm più del previsto (bordo a
x = −37,5); il flat arancione occupa 2 mm in più verso −y (y 10,7..17,2); lo slot SIM si può coprire
dall'alto per 2 mm. Forma v3.2: R1 x −34,35..9, y −6,7..10,2 · R2 x −37..−31,85, y −6,7..−3,3 ·
R3 x −37..−27,75, y −60..−3,3 · R4 x −37..5, y −60..−40,7. Area 1867 mm²; distanze: quadrato 0,50,
flat 0,50, plastica 0,50, staffa 2,15, CN1 7,05, ZIF 8,00, vite 5,35 mm; slot SIM coperto per 2 mm
(voluto). Dima: `doc/x210ai_dima_boardC_v3_2_1a1.pdf` / `.svg`.
