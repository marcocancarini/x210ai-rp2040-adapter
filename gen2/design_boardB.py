# -*- coding: utf-8 -*-
"""X210Ai rev 2.2 - Board B (adattatore sandwich su BTB_R_CONN1): modello dati (PCB, schema, BOM).

Stessa interfaccia di design2.py. Sopra: ricettacolo JAE (riceve la spina della tastiera) e ricettacolo eDP
(cavo verso la Board A); sotto: spina JAE (in BTB_R_CONN1) e i MOSFET che emulano Fn+PgUp verso l'EC.
J1 usa l'impronta JAE_AA01_sandwich: pad 1-41 = ricettacolo sopra, pad 101-140 = spina sotto (pad 100+n
innestato nel pin n di BTB_R_CONN1).

Come nella rev 2.0 la matrice NON passa alla scheda madre: l'EC vede solo Fn (pin 1), riga 24 e colonna 5
(PgUp) attraverso Q2b/Q3, il tasto di accensione (pin 19, diretto) e le masse. Se la matrice passasse 1:1
l'EC e l'RP2040 scandirebbero insieme le stesse linee.

Coordinate in mm rispetto al centro di J1 (asse y verso il basso, come KiCad).
"""
import uuid as _uuid

import design2 as R20
import edp_pinout as E

BOARD = "B"
PROJECT = "x210ai_boardB"   # nome dei file KiCad (.kicad_pro/.kicad_sch/.kicad_pcb)
REV = "2.2"
DATE = "2026-10-27"
TITLE = "X210Ai - Board B (sandwich sul connettore tastiera)"
COMPANY = R20.COMPANY

ROOT_UUID = str(_uuid.uuid5(_uuid.NAMESPACE_URL, "x210ai/rev2.2/boardB"))
_NS = _uuid.UUID("9e4a2c71-6d0b-4b3f-8f25-7c1a5e3d9b02")


def uid(*k):
    return str(_uuid.uuid5(_NS, "/".join(map(str, k))))


def sym_uuid(ref, unit=1):
    return uid("sym", ref, unit)


# ---------------------------------------------------------------- footprint e parti
FP = {
    "R0402": R20.FP["R0402"],
    "SOT363": R20.FP["SOT363"],
    "JSANDWICH": "x210ai:JAE_AA01_sandwich",
    "EDP": "x210ai:IPEX_20455-040E_90deg",
}
J1_VALUE = "AA01B-S040VA1+AA01B-P040VA1"
PARTS = {
    "100k": R20.PARTS["100k"],
    "BSS138DW": R20.PARTS["BSS138DW"],
    "20455-040E-76": ("C5160883", "20455-040E-76", "I-PEX"),
}
# J1 sono due parti fisiche nella stessa impronta: (lato, valore, LCSC, MPN, produttore, montaggio)
J1_PARTS = [
    ("Top", "AA01B-S040VA1", "C2938571", "AA01B-S040VA1-R3000", "JAE", "si"),
    ("Bottom", "AA01B-P040VA1", "", "AA01B-P040VA1-R3000 (o spina 2x22 recuperata da un flat)", "JAE",
     "DNP - saldare a mano, non su LCSC"),
]

COMP = []   # dict(ref, value, fp, pins{pad:net}, desc)


def add(ref, value, fp, pins, desc=""):
    COMP.append(dict(ref=ref, value=value, fp=FP[fp], fpkey=fp, pins=pins, desc=desc))


def res(ref, val, a, b, desc=""):
    add(ref, val, "R0402", {1: a, 2: b}, desc)


J1_PINS = {p: R20.j1_net(p) for p in range(1, 41) if R20.j1_net(p)}          # lato tastiera (sopra)
J1_PINS.update({f"TAB{i}": "GND" for i in range(1, 5)})                       # linguette, come nella T61
J1_PINS.update({100 + p: n for p, n in R20.J2_NETS.items()})                  # lato scheda madre (sotto)

res("R13", "100k", "EC_FN_G", "GND", "pull-down gate Fn->EC")
res("R14", "100k", "EC_PGUP_G", "GND", "pull-down gate PgUp->EC")
add("Q2", "BSS138DW", "SOT363",
    {1: "GND", 2: "GND", 6: "GND", 4: "GND", 5: "EC_FN_G", 3: "MB_FN"},
    "meta' a non usata (a massa); b: Fn verso EC")
add("Q3", "BSS138DW", "SOT363",
    {1: "EC_PGUP_S", 2: "EC_PGUP_G", 6: "MB_R24", 4: "EC_PGUP_S", 5: "EC_PGUP_G", 3: "MB_C5"},
    "interruttore bidirezionale riga24-colonna5 (PgUp) verso EC")
add("J1", J1_VALUE, "JSANDWICH", J1_PINS, "ricettacolo tastiera (sopra) + spina verso BTB_R_CONN1 (sotto)")
add("J4", "20455-040E-76", "EDP", dict(E.EDP_B), f"ricettacolo eDP verso la Board A (cavo {E.CABLE})")

DNP = set()
NOT_ASSEMBLED = set()   # la spina di J1 (lato Bottom) e' DNP: vedi J1_PARTS
TOP_SIDE = {"J1", "J4"}

BY_REF = {c["ref"]: c for c in COMP}
NETS = sorted({n for c in COMP for n in c["pins"].values() if n})
POWER_NETS = ["GND", "VBUS"]

# ---------------------------------------------------------------- scheda
# PIAZZAMENTO PRELIMINARE. Il ricettacolo eDP 40 pin occupa 27,1 mm di piazzole e 28,2 x 6,7 mm di area
# libera (catalogo I-PEX): non sta nella stima "15 x 12 mm" ne' nell'ingombro della rev 2.0 (29 mm a sinistra
# del centro di J1). Qui e' a sinistra di J1, parallelo, ruotato di 180 gradi: pin 1 verso J1, cavo verso -y.
J1_J4_GAP = 2.5      # margine extra tra J1 e J4 (richiesto 2-3 mm), oltre ai rispettivi courtyard
# J4 ruotato di 180 gradi (cavo verso -y) e spostato verso +y. Limite misurato dalla foto della dima sulla
# scheda madre (27/10/2026, ~22 px/mm): lo slot SIM inizia a y ~ +5,0 per x < -33. Con le piazzole a y = +3,5
# il bordo della scheda e' a +4,3 (circa 0,7 mm dallo slot SIM: da ricontrollare con la dima).
EDP_Y = 3.5
X0, X1, Y0, Y1 = -35.3 - J1_J4_GAP, 7.5, -4.4, 4.3
CORNER_R = 0.6
ORIGIN = R20.ORIGIN
THICKNESS_MM = 0.4   # PCBWay 4 strati, lavorazione avanzata
VIA = (0.3, 0.15)    # diametro / foro (regole PCBWay avanzate)
ENVELOPE_REV20 = (-29.0, 7.5, -5.0, 5.6)   # ingombro verificato con la dima della rev 2.0
# ostacoli sulla scheda madre misurati dalla foto della dima (precisione ~0,5 mm): (nome, x0, x1, y0, y1)
OSTACOLI_FOTO = [("slot SIM", -45.0, -32.9, 5.0, 12.0), ("vite", -12.5, -4.8, 15.0, 20.7),
                 ("quadrato bianco", -27.3, 12.0, -20.0, -5.9)]

PLACE = {
    "J1": (0.0, 0.0, 0, "T"),
    "J4": (-21.35 - J1_J4_GAP, EDP_Y, 180, "T"),
    "Q2": (-10.0, 0.0, 0, "B"), "R13": (-8.3, 0.0, 90, "B"),
    "Q3": (-13.5, 0.0, 0, "B"), "R14": (-11.8, 0.0, 90, "B"),
}

assert set(PLACE) == set(BY_REF), set(PLACE) ^ set(BY_REF)
for r, (_, _, _, side) in PLACE.items():
    assert (side == "T") == (r in TOP_SIDE), r


def cable_check():
    """ogni pin del cavo deve avere la stessa net ai due capi"""
    import design_boardA as A
    a, b = A.BY_REF["J4"]["pins"], BY_REF["J4"]["pins"]
    bad = [(p, a[p], b[E.b_pin(p)]) for p in a if a[p] != b[E.b_pin(p)]]
    assert not bad, bad
    # tutte le net della tastiera di J1 (tranne accensione e masse) arrivano all'RP2040 attraverso il cavo
    kb = {n for p, n in J1_PINS.items() if isinstance(p, int) and p < 100} - {"PWR_SW", "GND"}
    assert kb <= set(b.values()), kb - set(b.values())
    return True


if __name__ == "__main__":
    print("Board B:", len(COMP), "componenti,", len(NETS), "net, cavo", E.CABLE)
    print("cavo coerente con la Board A:", cable_check())
    ex0, ex1, ey0, ey1 = ENVELOPE_REV20
    if X0 < ex0 or X1 > ex1 or Y0 < ey0 or Y1 > ey1:
        print(f"ATTENZIONE: contorno {X1 - X0:.1f} x {Y1 - Y0:.1f} mm fuori dall'ingombro rev 2.0 "
              f"(x {X0} < {ex0}): verificare con la dima")
