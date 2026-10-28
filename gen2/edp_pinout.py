# -*- coding: utf-8 -*-
"""X210Ai rev 2.2 - piedinatura del cavo eDP (I-PEX CABLINE-VS 40 pin) tra Board A e Board B.

EDP_A e' la piedinatura del connettore J4 della Board A; quella della Board B si ricava dal tipo di cavo.
I-PEX vende due cablaggi standard (catalogo CABLINE-VS, pagina "Standard Harness"):
  "1-1": pin n -> pin n        (es. 82690-100B-01-D, 40 pin, 100 mm)
  "1-N": pin n -> pin 41-n     (es. 82190-100B-02-D, 40 pin, 100 mm)
Con i due ricettacoli sullo stesso lato delle schede, uno di fronte all'altro e il cavo steso senza pieghe
serve il "1-N". Se una scheda monta J4 sull'altro lato o il cavo viene piegato una volta (la piega ribalta la
spina) serve il "1-1". DA DECIDERE con il piazzamento reale, prima di ordinare la Board B.
"""

CABLE = "1-N"

# pin -> net sul connettore della Board A. Ordine delle righe/colonne = ordine dei pin di J1 (connettore
# tastiera), cosi' sulla Board B le piste da J1 a J4 sono annidate e non si incrociano. Con J4 della Board B
# ruotato di 180 gradi (pin 1 verso J1) e cavo 1-N, Fn sta sul pin 39 della Board A = pin 2 della Board B,
# subito dopo la massa del pin 1, il pin di J4 piu' vicino a J1.
EDP_A = {
    1: "GND", 2: "GND",
    3: "VBUS", 4: "VBUS",               # 5 V del TrackPoint (dalla USB della Board A)
    5: "TP_RST_5V", 6: "TP_DATA_5V",
    7: "GND",
    8: "TP_CLK_5V",                     # clock PS/2 tra due masse
    9: "GND",
    10: "EC_PGUP_G", 11: "EC_FN_G",
    12: "GND",
    13: "KB_R32", 14: "KB_R30", 15: "KB_R28", 16: "KB_R26", 17: "KB_R24", 18: "KB_R22", 19: "KB_R20",
    20: "KB_R18",
    21: "GND",
    22: "KB_C17", 23: "KB_R16", 24: "KB_C15", 25: "KB_R14", 26: "KB_C13", 27: "KB_R12", 28: "KB_C11",
    29: "KB_R10", 30: "KB_C9",
    31: "GND",
    32: "KB_R8", 33: "KB_C7", 34: "KB_R6", 35: "KB_C5", 36: "KB_R4", 37: "KB_C3", 38: "KB_R2", 39: "KB_FN",
    40: "GND",
    41: "GND",                          # barra di massa e linguette di fissaggio del ricettacolo
}


def b_pin(a_pin):
    """pin della Board B collegato al pin a_pin della Board A"""
    if a_pin == 41 or CABLE == "1-1":
        return a_pin
    assert CABLE == "1-N", CABLE
    return 41 - a_pin


EDP_B = {b_pin(p): n for p, n in EDP_A.items()}

assert sorted(EDP_A) == list(range(1, 42))
assert sorted(EDP_B) == list(range(1, 42))
SIGNALS = sorted({n for n in EDP_A.values() if n != "GND"})
assert len(SIGNALS) == 31, len(SIGNALS)   # 16 righe + 8 colonne + Fn + 3 TrackPoint + 5 V + 2 gate EC

if __name__ == "__main__":
    print("cavo", CABLE)
    for p in range(1, 41):
        print(f"A{p:<3} -> B{b_pin(p):<3} {EDP_A[p]}")
