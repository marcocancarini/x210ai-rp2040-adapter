# -*- coding: utf-8 -*-
"""X210Ai rev 2.3 - Board C: scheda unica "a giro del quadrato bianco" (Board A + Board B integrate, senza
cavo eDP). Modello dati (PCB, schema, BOM, firmware) con la stessa interfaccia di design2.py.

Struttura come la rev 2.0 (design2.py): J1 (ricettacolo tastiera) SOPRA e J2 (spina in BTB_R_CONN1) SOTTO,
allineati uno sopra l'altro a (0, 0); stessa netlist della rev 2.0 (Q2b e Q3 per Fn+PgUp verso l'EC,
pin 19 diretto J1-J2), quindi il firmware non cambia.

Contorno = forma v3.2 della dima (gen_dima_giro.py --v32), coordinate dima = coordinate PCB: origine al centro
di BTB_R_CONN1, x lungo il connettore (palmrest = -x), y verso la vite (+y, verso il basso in KiCad), vista
dall'alto. La scheda gira intorno al quadrato bianco (x -27,25..12, y -40,2..-7,2):

  R1 braccio con J1/J2:      x -34,35 .. 9     y -6,7 .. 10,2   (scende 2 mm sopra lo slot SIM)
  R3 tratto sotto il quadrato: x -37 .. -27,75  y -60 .. -3,3
  R4 braccio componenti:     x -37 .. 5        y -60 .. -40,7  (dall'altra parte del quadrato rispetto a BTB)

Il gruppo RP2040 + TrackPoint (piazzamento della Board A, gia' provato) sta SOTTO, in R4: la scheda madre li'
e' coperta di Mylar, e sotto la scheda c'e' l'altezza della coppia J2 + BTB_R_CONN1 (~1,5 mm). Q2/Q3/R13/R14
(emulazione EC) restano sotto, accanto a J2, come nella Board B.
"""
import uuid as _uuid

import design2 as R20
import design_boardA as BA

BOARD = "C"
PROJECT = "x210ai_boardC"
REV = "2.3"
DATE = "2026-11-02"
TITLE = "X210Ai - Board C (scheda unica a giro del quadrato bianco)"
COMPANY = R20.COMPANY

ROOT_UUID = str(_uuid.uuid5(_uuid.NAMESPACE_URL, "x210ai/rev2.3/boardC"))
_NS = _uuid.UUID("8e3c1f52-6d0b-4a7e-b2c9-41f0a9d3e6c7")


def uid(*k):
    return str(_uuid.uuid5(_NS, "/".join(map(str, k))))


def sym_uuid(ref, unit=1):
    return uid("sym", ref, unit)


# ---------------------------------------------------------------- GPIO, parti, netlist: come la rev 2.0
SIGNAL_GPIO = R20.SIGNAL_GPIO
GPIO_SIGNAL = R20.GPIO_SIGNAL
FW_ROW_PINS = R20.FW_ROW_PINS
FW_COL_PINS = R20.FW_COL_PINS
ROW_IO = R20.ROW_IO
COL_IO = R20.COL_IO
gpio_pin = R20.gpio_pin
rp2040_pins = R20.rp2040_pins
FP = dict(R20.FP)
PARTS = dict(R20.PARTS)
COMP = [dict(c) for c in R20.COMP]
# Q2 della rev 2.0 aveva la meta' a (reset TrackPoint, gate a +3V3) e la meta' b (Fn verso l'EC) nello stesso
# SOT-363 accanto a J2: qui il +3V3 sta nel braccio lontano, a ~50 mm, e lo sbroglio non riusciva a portarlo.
# Le due meta' si separano come nelle Board A e B: Q2 = reset TrackPoint nel gruppo RP2040 (meta' b a massa),
# Q4 = Fn verso l'EC accanto a J2 (meta' a a massa). Stesse net e stessi GPIO: il firmware non cambia.
for c in COMP:
    if c["ref"] == "Q2":
        c.update(pins=dict(BA.BY_REF["Q2"]["pins"]), desc=BA.BY_REF["Q2"]["desc"])
COMP.append(dict(BA.BY_REF["Q2"], ref="Q4",
                 pins={1: "GND", 2: "GND", 6: "GND", 4: "GND", 5: "EC_FN_G", 3: "MB_FN"},
                 desc="meta' a non usata (a massa); b: Fn verso EC"))
# J2 (spina) e J1 (ricettacolo) JAE saldati a mano: nessuno dei due si fa montare da JLCPCB, cosi'
# l'assemblaggio e' su un solo lato (sotto)
DNP = set(R20.DNP) | {"J1"}
NOT_ASSEMBLED = set(R20.NOT_ASSEMBLED)
TOP_SIDE = set(R20.TOP_SIDE)             # J1 + ponticelli e test point (solo rame)
BY_REF = {c["ref"]: c for c in COMP}
NETS = sorted({n for c in COMP for n in c["pins"].values() if n})
POWER_NETS = R20.POWER_NETS

# ---------------------------------------------------------------- scheda
# rettangoli della forma v3.2 (x0, x1, y0, y1); R2 della dima (raccordo) e' contenuto in R3
RETT = {
    "R1": (-34.35, 9.0, -6.7, 10.2),
    "R3": (-37.0, -27.75, -60.0, -3.3),
    "R4": (-37.0, 5.0, -60.0, -40.7),
}
OUTLINE = [(-37.0, -60.0), (5.0, -60.0), (5.0, -40.7), (-27.75, -40.7), (-27.75, -6.7), (9.0, -6.7),
           (9.0, 10.2), (-34.35, 10.2), (-34.35, -3.3), (-37.0, -3.3)]
X0, X1 = min(p[0] for p in OUTLINE), max(p[0] for p in OUTLINE)
Y0, Y1 = min(p[1] for p in OUTLINE), max(p[1] for p in OUTLINE)
CORNER_R = 0.6
ORIGIN = R20.ORIGIN
# Spessore: sopra BTB_R_CONN1 restano ~1,8 mm (misura con le monete) e la pila J2 + PCB + J1 alza la spina della
# tastiera di (coppia JAE ~1,54 mm) + PCB: con 0,4 mm siamo a ~1,94 mm, circa 0,1-0,15 mm oltre la misura.
THICKNESS_MM = 0.4   # JLCPCB 4 strati 0,4 mm, ENIG
VIA = (0.4, 0.2)

# Gruppo RP2040 + TrackPoint della Board A traslato in blocco verso l'estremita' di R4 (x max) e centrato in
# altezza: restano ~4 mm liberi sopra e sotto il gruppo e ~15 mm a sinistra, dove arrivano da R3 i segnali di
# tastiera e TrackPoint (al primo tentativo, gruppo nell'angolo x min / y min, Freerouting si fermava a 20
# collegamenti mancanti). J3 (piazzole dei fili USB) resta sul bordo, nell'angolo x min / y min.
EDGE = 0.3
GRP = (-14.14, 13.3, -5.7, 4.75)         # courtyard del gruppo nelle coordinate della Board A (x0, x1, y0, y1)
TX = RETT["R4"][1] - EDGE - GRP[1]
TY = (RETT["R4"][2] + RETT["R4"][3]) / 2 - (GRP[2] + GRP[3]) / 2
PLACE = {r: (x + TX, y + TY, rot, side) for r, (x, y, rot, side) in BA.PLACE.items()
         if r != "J4"}
PLACE["J3"] = (RETT["R4"][0] + EDGE + 1.05, RETT["R4"][2] + EDGE + 3.2, 0, "B")   # courtyard 2,1 x 6,4
PLACE.update({
    "J1": (0.0, 0.0, 0, "T"), "J2": (0.0, 0.0, 0, "B"),
    # emulazione EC sotto, a sinistra di J2 (fuori dal corpo di BTB_R_CONN1, x > -7,8): come nella Board B,
    # 0,5 mm piu' in la' dal connettore
    "Q3": (-12.1, -2.6, 0, "B"), "R14": (-8.8, -2.6, 90, "B"),
    "Q4": (-12.1, 1.2, 0, "B"), "R13": (-8.8, 1.2, 90, "B"),
})

_jp1, _jp2, _tp1, _tp4 = PLACE["JP1"], PLACE["JP2"], PLACE["TP1"], PLACE["TP4"]
SILK = [(f"X210Ai Board C rev {REV}", -14.0, -44.0, "F", 0.8),
        ("RP2040 sotto (Mylar)", -14.0, -42.4, "F", 0.6),
        ("BOOT", _jp1[0], _jp1[1] + 1.15, "F", 0.5), ("RST", _jp2[0], _jp2[1] + 1.15, "F", 0.5),
        ("CLK DIO GND 3V3", (_tp1[0] + _tp4[0]) / 2, _tp1[1] + 1.15, "F", 0.45),
        ("TASTIERA", -20.0, 4.6, "F", 0.7)]

assert set(PLACE) == set(BY_REF), set(PLACE) ^ set(BY_REF)
for r, (_, _, _, side) in PLACE.items():
    assert (side == "T") == (r in TOP_SIDE), r


def inside(x, y, poly=OUTLINE):
    n, ok = len(poly), False
    for i in range(n):
        (xa, ya), (xb, yb) = poly[i], poly[i - 1]
        if (ya > y) != (yb > y) and x < xa + (y - ya) * (xb - xa) / (yb - ya):
            ok = not ok
    return ok


for r, (x, y, _, _) in PLACE.items():
    assert inside(x, y), r

if __name__ == "__main__":
    print("Board C:", len(COMP), "componenti,", len(NETS), "net; gruppo RP2040 traslato di", (round(TX, 2), round(TY, 3)))
    xs = [p[0] for r, p in PLACE.items() if r not in ("J1", "J2", "Q3", "Q4", "R13", "R14")]
    ys = [p[1] for r, p in PLACE.items() if r not in ("J1", "J2", "Q3", "Q4", "R13", "R14")]
    print(f"centri del gruppo: x {min(xs):.2f}..{max(xs):.2f}, y {min(ys):.2f}..{max(ys):.2f}")
