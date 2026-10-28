# -*- coding: utf-8 -*-
"""X210Ai rev 2.2 - Board B (adattatore a scalino su BTB_R_CONN1): modello dati (PCB, schema, BOM).

Stessa interfaccia di design2.py. PCB flessibile a 2 strati con irrigidimenti, su due livelli: il gradino alto
porta la spina J2 (sotto, in BTB_R_CONN1), il ricettacolo eDP J4 (cavo verso la Board A) e i MOSFET che emulano
Fn+PgUp verso l'EC; il gradino basso, appoggiato sulla scheda madre, porta il ricettacolo J1 della tastiera.

Come nella rev 2.0 la matrice NON passa alla scheda madre: l'EC vede solo Fn (pin 1), riga 24 e colonna 5
(PgUp) attraverso Q2b/Q3, il tasto di accensione (pin 19, diretto) e le masse. Se la matrice passasse 1:1
l'EC e l'RP2040 scandirebbero insieme le stesse linee.

Coordinate in mm rispetto al centro di J1 (asse y verso il basso, come KiCad).
"""
import math
import uuid as _uuid

from shapely.geometry import LineString, Point, Polygon, box
from shapely.ops import unary_union

import design2 as R20
import edp_pinout as E

BOARD = "B"
PROJECT = "x210ai_boardB"   # nome dei file KiCad (.kicad_pro/.kicad_sch/.kicad_pcb)
REV = "2.2"
DATE = "2026-10-28"
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
    "J1": "x210ai:JAE_AA01B-S040VA1_T61_GND41",           # ricettacolo della tastiera (T61; linguette = pin 41)
    "J2": R20.FP["J2"],                                   # spina verso BTB_R_CONN1 (sotto, gradino alto)
    "EDP": "x210ai:IPEX_20455-040E_90deg",
}
PARTS = {
    "100k": R20.PARTS["100k"],
    "BSS138DW": R20.PARTS["BSS138DW"],
    "AA01B-S040VA1": R20.PARTS["AA01B-S040VA1"],
    "AA01B-P040VA1": ("", "AA01B-P040VA1-R3000 (o spina 2x22 recuperata da un flat)", "JAE"),
    "20455-040E-76": ("C5160883", "20455-040E-76", "I-PEX"),
}

COMP = []   # dict(ref, value, fp, pins{pad:net}, desc)


def add(ref, value, fp, pins, desc=""):
    COMP.append(dict(ref=ref, value=value, fp=FP[fp], fpkey=fp, pins=pins, desc=desc))


def res(ref, val, a, b, desc=""):
    add(ref, val, "R0402", {1: a, 2: b}, desc)


J1_PINS = {p: R20.j1_net(p) for p in range(1, 41) if R20.j1_net(p)}          # tastiera
J1_PINS[41] = "GND"                                                          # linguette (4 piazzole "41")

res("R13", "100k", "EC_FN_G", "GND", "pull-down gate Fn->EC")
res("R14", "100k", "EC_PGUP_G", "GND", "pull-down gate PgUp->EC")
add("Q2", "BSS138DW", "SOT363",
    {1: "GND", 2: "GND", 6: "GND", 4: "GND", 5: "EC_FN_G", 3: "MB_FN"},
    "meta' a non usata (a massa); b: Fn verso EC")
add("Q3", "BSS138DW", "SOT363",
    {1: "EC_PGUP_S", 2: "EC_PGUP_G", 6: "MB_R24", 4: "EC_PGUP_S", 5: "EC_PGUP_G", 3: "MB_C5"},
    "interruttore bidirezionale riga24-colonna5 (PgUp) verso EC")
add("J1", "AA01B-S040VA1", "J1", J1_PINS, "ricettacolo tastiera (gradino basso, ruotato di 25 gradi)")
add("J2", "AA01B-P040VA1", "J2", dict(R20.J2_NETS), "spina verso BTB_R_CONN1 (sotto il gradino alto)")
add("J4", "20455-040E-76", "EDP", dict(E.EDP_B), f"ricettacolo eDP verso la Board A (cavo {E.CABLE})")

DNP = {"J2"}            # spina JAE non a magazzino LCSC: si salda a mano
NOT_ASSEMBLED = set()
TOP_SIDE = {"J1", "J4"}

BY_REF = {c["ref"]: c for c in COMP}
NETS = sorted({n for c in COMP for n in c["pins"].values() if n})
POWER_NETS = ["GND", "VBUS"]

# ---------------------------------------------------------------- scheda: variante a scalino (dima del 28/10/2026, OK)
# Sopra BTB_R_CONN1 la tastiera non ci sta a sandwich (meno di 1,67 mm sopra la sua spina). La Board B e' un PCB
# flessibile a 2 strati con irrigidimenti, su due livelli:
# - gradino alto: innestato su BTB_R_CONN1 con la spina J2 (sotto); J4 verso il palmrest, ruotato di 270 gradi
#   (piedini verso il connettore, cavo verso il palmrest); Q2, Q3, R13, R14 sotto, nel ponte tra J2 e J4;
# - scalino: tratto flessibile che scende di 1,5 mm (accoppiamento della spina) verso la vite (+y);
# - gradino basso: appoggiato sulla scheda madre, porta il ricettacolo J1 ruotato di 25 gradi in senso orario.
# Coordinate in mm dal centro di BTB_R_CONN1: x lungo il connettore (palmrest verso -x), y verso la vite.
# Ingombri dalla foto della cornice di misura (gen_dima_scala.py), seconda foto, +/-0,3 mm.
OSTACOLI = [   # (nome, "r" = rettangolo x0, x1, y0, y1 | "c" = cerchio cx, cy, raggio)
    ("BTB_R_CONN1", "r", (-7.8, 7.8, -3.45, 3.45)),
    ("connettore FPC", "r", (-45.0, -32.35, -2.8, 12.7)),       # continua oltre la finestra della cornice
    ("flat arancione", "r", (-37.35, -21.35, 12.7, 17.2)),
    ("vite", "c", (-7.8, 19.1, 3.55)),
    ("linguetta vite", "r", (-13.1, -5.8, 22.3, 26.4)),             # dalla prima foto
    ("connettore CN1", "r", (-30.35, -21.6, 17.25, 23.5)),          # dalla prima foto
    # quadrato bianco: zona vietata, sopra c'e' meno di 1 mm di spazio. Bordo verso il connettore e lato
    # sinistro misurati sulla serigrafia; il lato verso il palmrest (x = 12) dalle dime precedenti
    ("quadrato bianco", "r", (-27.25, 12.0, -29.7, -7.2)),
]
VIETATE = {"quadrato bianco"}
NASTRI = [          # non ingombri, solo riferimento
    ("nastro alluminio", (11.15, 15.55, -9.3, 13.7)),
    ("nastro", (8.85, 10.95, 3.7, 17.7)),
    ("nastro tessuto", (8.65, 28.65, -26.0, -9.3)),
]

J1_CRT = (-6.83, 6.92, -3.69, 3.48)   # courtyard di JAE_AA01B-S040VA1_T61 (x0, x1, y0, y1)
J2_CRT = (-6.62, 6.72, -2.92, 3.12)   # courtyard della spina montata sotto (come nella rev 2.0)
J4_CRT = (-14.1, 14.1, -1.0, 5.7)     # courtyard di IPEX_20455-040E_90deg (rot 0, cavo verso +y)
CAVO_W = 21.0        # larghezza del fascio micro-coassiale (40 x 0,5 mm + nastro)
EDGE = 0.3           # bordo scheda oltre i courtyard
ROT_KB = -25.0       # J1: 25 gradi in senso orario visto dall'alto (KiCad: antiorario +)
KB_DX = 0.0          # spostamento di J1 lungo BTB_R_CONN1 (0 = allineato)
STEP_H = 1.5         # dislivello dello scalino: accoppiamento JAE tra la spina e BTB_R_CONN1
FLEX_L = 2.7         # lunghezza in pianta del tratto flessibile (piega a S, raggio ~1,5 mm)
BAND_Y0, BAND_X1, Y_HI = -4.4, 7.5, 3.65   # fascia del gradino alto su BTB_R_CONN1 (come la dima rev 2.0)
J4_ROT = 270
J4_XMAX = -13.6      # bordo verso il connettore della zona di J4: 0,5 mm oltre la linguetta della vite
J4_X = J4_XMAX - EDGE + J4_CRT[2]     # rot 270: courtyard da J4_X - 5,7 a J4_X + 1,0 e da J4_Y - 14,1 a J4_Y + 14,1
J4_Y = 8.0           # 0,8 mm dentro il limite del quadrato bianco (-7,2 + 0,5)


def _rot(x, y, a):
    """rotazione KiCad (antioraria vista dall'alto, asse y verso il basso)"""
    r = math.radians(a)
    return x * math.cos(r) + y * math.sin(r), -x * math.sin(r) + y * math.cos(r)


EXT_X1, EXT_Y1 = -9.1, 14.0   # allargamento del gradino alto tra J4 e lo scalino (passaggio delle piste verso J4)
EXT2_X1, EXT2_Y1 = -11.85, 19.0   # ... e lungo gli ultimi piedini di J4, a 0,5 mm dall'anello della vite
_HIGH = unary_union([box(J4_XMAX - 0.01, BAND_Y0, BAND_X1, Y_HI),
                     box(J4_XMAX - 0.01, Y_HI - 0.01, EXT_X1, EXT_Y1),
                     box(J4_XMAX - 0.01, EXT_Y1 - 0.01, EXT2_X1, EXT2_Y1),
                     box(J4_X - J4_CRT[3] - EDGE, J4_Y - J4_CRT[1] - EDGE, J4_XMAX, J4_Y + J4_CRT[1] + EDGE)])
HIGH = list(_HIGH.exterior.coords)[:-1]
_c = [(J1_CRT[0] - EDGE, J1_CRT[2] - EDGE), (J1_CRT[1] + EDGE, J1_CRT[2] - EDGE),
      (J1_CRT[1] + EDGE, J1_CRT[3] + EDGE), (J1_CRT[0] - EDGE, J1_CRT[3] + EDGE)]
_r = [_rot(x, y, ROT_KB) for x, y in _c]
KB_X = KB_DX
KB_Y = Y_HI + FLEX_L - min(y for _, y in _r)          # il gradino basso parte a FLEX_L dal gradino alto
LOW = [(KB_X + x, KB_Y + y) for x, y in _r]
_top = sorted(LOW, key=lambda p: p[1])[:2]            # i due angoli del gradino basso verso BTB_R_CONN1
FLEX_X0 = max(-BAND_X1 + 1.0, min(p[0] for p in _top))          # lati del tratto flessibile ad almeno 1 mm
FLEX_X1 = min(BAND_X1 - 1.0, max(p[0] for p in _top) - 0.5)     # dagli spigoli del gradino alto


def _y_low(x):
    """bordo del gradino basso verso BTB_R_CONN1 alla coordinata x"""
    return min(y for _, y in Polygon(LOW).intersection(LineString([(x, -50), (x, 50)])).coords)


# tratto flessibile: dal bordo del gradino alto fino al bordo del gradino basso (0,5 mm dentro, senza scalini)
FLEX = [(FLEX_X0, Y_HI), (FLEX_X1, Y_HI), (FLEX_X1, _y_low(FLEX_X1) + 0.5), (FLEX_X0, _y_low(FLEX_X0) + 0.5)]
FLEX_DEV = math.hypot(FLEX_L, STEP_H) - FLEX_L        # lunghezza in piu' del tratto flessibile disteso
# zona di piega: niente via ne' componenti (tra il bordo del gradino alto e il bordo del gradino basso)
BEND = [(FLEX_X0, Y_HI), (FLEX_X1, Y_HI), (FLEX_X1, _y_low(FLEX_X1)), (FLEX_X0, _y_low(FLEX_X0))]
assert Polygon(LOW).distance(box(J4_XMAX, Y_HI, EXT_X1, EXT_Y1)) >= 1.0, "allargamento troppo vicino al gradino basso"
_shape = unary_union([_HIGH, Polygon(FLEX), Polygon(LOW)]).simplify(0.01)
OUTLINE = list(_shape.exterior.coords)[:-1]
X0, Y0, X1, Y1 = _shape.bounds                        # riquadro del contorno
CORNER_R = 0.3
ORIGIN = R20.ORIGIN
COPPER_LAYERS = 4    # JLCPCB flex 4 strati (poliimmide; a 2 strati J1-J4 non si sbroglia), irrigidimenti in STIFFENERS
THICKNESS_MM = 0.25   # flessibile 4 strati: da confermare nel configuratore JLCPCB
VIA = (0.4, 0.2)     # diametro / foro: valori prudenti per il flessibile
# irrigidimenti (disegnati su User.1 per il produttore): (nome, lato, materiale, spessore, poligono)
STIFFENERS = [
    ("gradino alto, sopra J2", "top", "FR4", 0.2, [(J4_XMAX, BAND_Y0), (BAND_X1, BAND_Y0), (BAND_X1, Y_HI),
                                                   (EXT_X1, Y_HI), (EXT_X1, EXT_Y1), (EXT2_X1, EXT_Y1),
                                                   (EXT2_X1, EXT2_Y1), (J4_XMAX, EXT2_Y1)]),
    ("sotto J4", "bottom", "FR4", 0.2,
     [(J4_X - J4_CRT[3] - EDGE, J4_Y - J4_CRT[1] - EDGE), (J4_XMAX, J4_Y - J4_CRT[1] - EDGE),
      (J4_XMAX, J4_Y + J4_CRT[1] + EDGE), (J4_X - J4_CRT[3] - EDGE, J4_Y + J4_CRT[1] + EDGE)]),
    ("gradino basso, sotto J1", "bottom", "poliimmide", 0.1, LOW),
]
# scritte in serigrafia (testo, x, y, lato, altezza)
SILK = [("X210Ai B", J4_X - 3.6, J4_Y + 11.0, "B", 0.6), (f"rev {REV}", J4_X - 3.6, J4_Y + 12.2, "B", 0.6)]
# variante a L (storica, dima gen_dima_boardB_L.py): ostacoli dalla prima foto e margine tra J1 e J4
OSTACOLI_FOTO = [("slot SIM", -45.0, -32.9, 5.0, 12.0), ("vite", -12.5, -4.8, 15.0, 20.7),
                 ("quadrato bianco", -27.3, 12.0, -20.0, -5.9)]
J1_J4_GAP = 2.5
BOT_Y0 = Y_HI

PLACE = {
    "J2": (0.0, 0.0, 0, "B"),
    "J1": (KB_X, KB_Y, ROT_KB, "T"),
    "J4": (J4_X, J4_Y, J4_ROT, "T"),
    # sotto, nel ponte tra la spina J2 e la zona di J4 (courtyard SOT-363 2,96 x 2,54, 0402 0,98 x 1,9)
    "Q3": (-11.6, -2.6, 0, "B"), "R14": (-8.3, -2.6, 90, "B"),
    "Q2": (-11.6, 1.2, 0, "B"), "R13": (-8.3, 1.2, 90, "B"),
}


def inside(x, y, poly=OUTLINE):
    """punto dentro il poligono (ray casting)"""
    n, ok = len(poly), False
    for i in range(n):
        (xa, ya), (xb, yb) = poly[i], poly[i - 1]
        if (ya > y) != (yb > y) and x < xa + (y - ya) * (xb - xa) / (yb - ya):
            ok = not ok
    return ok


def shape(tipo, d):
    return box(d[0], d[2], d[1], d[3]) if tipo == "r" else Point(d[0], d[1]).buffer(d[2])


def margini():
    """distanza minima (mm) di gradino alto e gradino basso dagli ingombri, e dal quadrato bianco"""
    m = {}
    for nome, poly in (("gradino alto", HIGH), ("gradino basso", LOW)):
        d = sorted((Polygon(poly).distance(shape(t, dd)), n) for n, t, dd in OSTACOLI if n != "BTB_R_CONN1")
        m[f"{nome} - {d[0][1]}"] = d[0][0]
    q = [shape(t, d) for n, t, d in OSTACOLI if n in VIETATE][0]
    m["gradino alto - quadrato bianco"] = Polygon(HIGH).distance(q)
    m["larghezza tratto flessibile"] = FLEX_X1 - FLEX_X0
    return m


assert set(PLACE) == set(BY_REF), set(PLACE) ^ set(BY_REF)
for r, (x, y, _, side) in PLACE.items():
    assert (side == "T") == (r in TOP_SIDE), r
    assert inside(x, y), r


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
    print(f"contorno a scalino {X1 - X0:.2f} x {Y1 - Y0:.2f} mm, {len(OUTLINE)} vertici; J1 a ({KB_X:.2f}, "
          f"{KB_Y:.2f}) rot {ROT_KB:g}; J4 a ({J4_X:.2f}, {J4_Y:.2f}) rot {J4_ROT}")
    for k, v in margini().items():
        print(f"  margine {k}: {v:.2f} mm")
