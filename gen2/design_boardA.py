# -*- coding: utf-8 -*-
"""X210Ai rev 2.2 - Board A (scheda principale sotto il palmrest): modello dati (PCB, schema, BOM, firmware).

Stessa interfaccia di design2.py, cosi' i generatori di gen2/ possono usarlo al posto di design2.
GPIO, componenti e piazzamento del gruppo RP2040 sono quelli della rev 2.0 (design2): il firmware non cambia.
Rispetto alla rev 2.0 mancano J1, J2, Q3, R13, R14 (sulla Board B) e c'e' J4, il ricettacolo eDP verso la
Board B. Q2 tiene solo la meta' "a" (reset TrackPoint): la meta' "b" (Fn verso l'EC) e' ora sulla Board B.

Coordinate in mm rispetto al centro della scheda (asse y verso il basso, come KiCad).
Lato "T" = sopra, "B" = sotto.
"""
import uuid as _uuid

import design2 as R20
import edp_pinout as E

BOARD = "A"
PROJECT = "x210ai_boardA"   # nome dei file KiCad (.kicad_pro/.kicad_sch/.kicad_pcb)
REV = "2.2"
DATE = "2026-10-28"
TITLE = "X210Ai - Board A (RP2040, sotto il palmrest)"
COMPANY = R20.COMPANY

ROOT_UUID = str(_uuid.uuid5(_uuid.NAMESPACE_URL, "x210ai/rev2.2/boardA"))
_NS = _uuid.UUID("5b1d7e0a-3c42-4f8e-9a61-0e2b9d4c7a11")


def uid(*k):
    return str(_uuid.uuid5(_NS, "/".join(map(str, k))))


def sym_uuid(ref, unit=1):
    return uid("sym", ref, unit)


# ---------------------------------------------------------------- GPIO (invariati dalla rev 2.0)
SIGNAL_GPIO = R20.SIGNAL_GPIO
GPIO_SIGNAL = R20.GPIO_SIGNAL
FW_ROW_PINS = R20.FW_ROW_PINS
FW_COL_PINS = R20.FW_COL_PINS
ROW_IO = R20.ROW_IO
COL_IO = R20.COL_IO
gpio_pin = R20.gpio_pin
rp2040_pins = R20.rp2040_pins

# ---------------------------------------------------------------- footprint e parti
FP = dict(R20.FP)
for k in ("J1", "J2"):
    del FP[k]
FP["EDP"] = "x210ai:IPEX_20455-040E_90deg"

PARTS = {k: v for k, v in R20.PARTS.items() if not k.startswith("AA01B")}
# LCSC C5160883 = I-PEX 20455-040E-76 (verificato su lcsc.com il 2026-10-27; giacenza da controllare all'ordine)
PARTS["20455-040E-76"] = ("C5160883", "20455-040E-76", "I-PEX")

COMP = []   # dict(ref, value, fp, pins{pad:net}, desc)


def add(ref, value, fp, pins, desc=""):
    COMP.append(dict(ref=ref, value=value, fp=FP[fp], fpkey=fp, pins=pins, desc=desc))


def cap(ref, val, net, desc=""):
    add(ref, val, "C0402", {1: net, 2: "GND"}, desc)


def res(ref, val, a, b, desc=""):
    add(ref, val, "R0402", {1: a, 2: b}, desc)


for r in ("C1", "C2", "C3", "C4", "C5", "C6", "C9", "C10"):
    cap(r, "100nF", "+3V3", "disaccoppiamento IOVDD/USB_VDD/ADC")
cap("C7", "100nF", "+1V1", "disaccoppiamento DVDD")
cap("C8", "100nF", "+1V1", "disaccoppiamento DVDD")
cap("C11", "1uF", "+3V3", "VREG_VIN")
cap("C12", "1uF", "+1V1", "VREG_VOUT")
cap("C13", "15pF", "XIN", "carico quarzo")
cap("C14", "15pF", "XOUT_R", "carico quarzo")
cap("C15", "100nF", "+3V3", "disaccoppiamento flash")
cap("C16", "10uF", "VBUS", "ingresso regolatore")
cap("C17", "10uF", "+3V3", "uscita regolatore")
cap("C18", "100nF", "VBUS", "alimentazione TrackPoint")

res("R1", "27R", "USB_DM", "USB_DM_MCU", "serie USB D-")
res("R2", "27R", "USB_DP", "USB_DP_MCU", "serie USB D+")
res("R3", "1k", "XOUT", "XOUT_R", "serie quarzo")
res("R4", "1k", "QSPI_SS", "BOOTSEL_N", "BOOTSEL")
res("R5", "10k", "RUN", "+3V3", "pull-up RUN")
res("R7", "4.7k", "TP_CLK_3V3", "+3V3", "pull-up PS/2 clock lato 3,3 V")
res("R8", "4.7k", "TP_CLK_5V", "VBUS", "pull-up PS/2 clock lato 5 V")
res("R9", "4.7k", "TP_DATA_3V3", "+3V3", "pull-up PS/2 data lato 3,3 V")
res("R10", "4.7k", "TP_DATA_5V", "VBUS", "pull-up PS/2 data lato 5 V")
res("R11", "10k", "TP_RST_3V3", "+3V3", "pull-up reset TrackPoint lato 3,3 V")
res("R12", "10k", "TP_RST_5V", "VBUS", "pull-up reset TrackPoint lato 5 V")
# R13/R14 (pull-down dei gate EC) sono sulla Board B, vicino ai MOSFET: a cavo staccato i gate restano a massa

add("U1", "RP2040", "QFN56", rp2040_pins(), "microcontrollore")
add("U2", "W25Q16JVUXIQ", "USON8",
    {1: "QSPI_SS", 2: "QSPI_SD1", 3: "QSPI_SD2", 4: "GND", 5: "QSPI_SD0", 6: "QSPI_SCLK", 7: "QSPI_SD3", 8: "+3V3"},
    "flash 2 MB (pad 9 lasciato libero)")
add("U3", "XC6206P332MR", "SOT23", {1: "GND", 2: "+3V3", 3: "VBUS"}, "LDO 3,3 V")
add("Y1", "12MHz", "XTAL", {1: "XIN", 2: "GND", 3: "XOUT_R", 4: "GND"}, "quarzo 12 MHz")
add("Q1", "BSS138DW", "SOT363",
    {1: "TP_CLK_3V3", 2: "+3V3", 6: "TP_CLK_5V", 4: "TP_DATA_3V3", 5: "+3V3", 3: "TP_DATA_5V"},
    "traslatori PS/2 clock (a) e data (b)")
add("Q2", "BSS138DW", "SOT363",
    {1: "TP_RST_3V3", 2: "+3V3", 6: "TP_RST_5V", 4: "GND", 5: "GND", 3: "GND"},
    "traslatore reset TrackPoint (a); meta' b non usata, a massa")
add("J3", "USB", "USB", {1: "VBUS", 2: "USB_DM", 3: "USB_DP", 4: "GND"}, "fili verso USB-CON1")
add("J4", "20455-040E-76", "EDP", dict(E.EDP_A), "ricettacolo eDP verso la Board B")
add("JP1", "BOOT", "SJ", {1: "BOOTSEL_N", 2: "GND"}, "ponticello BOOTSEL")
add("JP2", "RESET", "SJ", {1: "RUN", 2: "GND"}, "ponticello RESET")
add("TP1", "SWCLK", "TP", {1: "SWCLK"}, "test point SWD")
add("TP2", "SWDIO", "TP", {1: "SWDIO"}, "test point SWD")
add("TP3", "GND", "TP", {1: "GND"}, "test point")
add("TP4", "+3V3", "TP", {1: "+3V3"}, "test point")

DNP = set()
NOT_ASSEMBLED = {"J3", "JP1", "JP2", "TP1", "TP2", "TP3", "TP4"}   # solo rame
TOP_SIDE = {"J4", "JP1", "JP2", "TP1", "TP2", "TP3", "TP4"}

BY_REF = {c["ref"]: c for c in COMP}
NETS = sorted({n for c in COMP for n in c["pins"].values() if n})
POWER_NETS = R20.POWER_NETS

# ---------------------------------------------------------------- scheda
# Ingombro ridotto (28/10/2026): J4 e' l'unico componente sopra insieme ai ponticelli e ai test point, quindi
# il resto sta sotto, nella stessa area di J4. La larghezza la decide J4 (courtyard 28,3 mm).
J4_CRT = (-14.14, 14.14, -1.05, 5.75)   # courtyard di IPEX_20455-040E_90deg (rot 0, cavo verso +y)
EDGE = 0.3                               # bordo scheda oltre i courtyard
X0, X1 = J4_CRT[0] - EDGE, J4_CRT[1] + EDGE
Y0 = -6.0
CORNER_R = 0.6
ORIGIN = R20.ORIGIN
THICKNESS_MM = 0.8   # JLCPCB 4 strati, ENIG
VIA = (0.4, 0.2)     # diametro / foro

# Gruppo RP2040 della rev 2.0 (gia' sbrogliato, fan-out della QFN e quarzo) traslato in blocco di DX, DY:
# J3 sul bordo sinistro, il bordo alto dei courtyard (C1, y = -4,91 nelle coordinate rev 2.0) sul bordo
# superiore. La fila di piazzole di J4 (alta 0,9 mm, sopra) non puo' passare sopra U1: la piazzola centrale
# ha via termici passanti e intorno c'e' il fan-out. Sta quindi sotto il courtyard di U1 (y = 4,47 nelle
# coordinate rev 2.0); ponticelli e test point (sopra, fino a y = -0,31) restano lontani da J4.
CORE_X0, CORE_Y0, U1_Y1 = -29.0, -4.91, 4.47        # coordinate rev 2.0
DX, DY = X0 + EDGE - CORE_X0, Y0 + EDGE - CORE_Y0
J4_Y = U1_Y1 + DY + 0.25 + 0.45
Y1 = J4_Y + J4_CRT[3] + EDGE
TRACKPOINT = {"Q2", "Q1", "R8", "R10", "R12", "C18"}
PLACE = {r: (x + DX, y + DY, rot, side) for r, (x, y, rot, side) in R20.PLACE.items()
         if r in BY_REF and r not in TRACKPOINT}
PLACE["C13"] = (PLACE["C13"][0], PLACE["C13"][1] - 0.15, 0, "B")   # rev 2.0: courtyard sovrapposto a Y1
PLACE["J4"] = (0.0, J4_Y, 0, "T")
# TrackPoint a destra del gruppo, in due colonne: SOT-363 (courtyard 3,0 x 2,6) e 0402 (1,94 x 1,04)
_qx, _rx = -5.3 + DX, -2.6 + DX      # colonne a destra del bordo del gruppo (x = -7,03 nelle coordinate rev 2.0)
PLACE.update({"Q2": (_qx, -3.2 + DY, 0, "B"), "Q1": (_qx, -0.4 + DY, 0, "B"),
              "R8": (_rx, -4.4 + DY, 0, "B"), "R10": (_rx, -3.25 + DY, 0, "B"),
              "R12": (_rx, -2.1 + DY, 0, "B"), "C18": (_rx, -0.95 + DY, 0, "B")})
# scritte in serigrafia (testo, x, y, lato, altezza), legate ai componenti
_jp1, _jp2, _tp1, _tp4 = PLACE["JP1"], PLACE["JP2"], PLACE["TP1"], PLACE["TP4"]
# lato sopra libero a destra dei test point e sopra J4 (x 0..14, y fino a ~3): titolo e verso del cavo
SILK = [(f"X210Ai Board A rev {REV}", 7.0, Y0 + 1.5, "F", 0.7),
        ("BOOT", _jp1[0], _jp1[1] + 1.15, "F", 0.5), ("RST", _jp2[0], _jp2[1] + 1.15, "F", 0.5),
        ("CLK DIO GND 3V3", (_tp1[0] + _tp4[0]) / 2, _tp1[1] + 1.15, "F", 0.45),
        ("eDP -> Board B", 7.0, Y0 + 3.0, "F", 0.6)]

assert set(PLACE) == set(BY_REF), set(PLACE) ^ set(BY_REF)
for r, (_, _, _, side) in PLACE.items():
    assert (side == "T") == (r in TOP_SIDE), r
for r, (x, y, _, _) in PLACE.items():
    assert X0 < x < X1 and Y0 < y < Y1, r

if __name__ == "__main__":
    print("Board A:", len(COMP), "componenti,", len(NETS), "net")
    print(f"contorno {X1 - X0:.2f} x {Y1 - Y0:.2f} mm, J4 a (0, {J4_Y:.2f}), gruppo RP2040 traslato di "
          f"({DX:.2f}, {DY:.2f})")
    print("Row_IO", ROW_IO)
    print("Col_IO", COL_IO)
    pads = {}
    for c in COMP:
        for n in c["pins"].values():
            pads[n] = pads.get(n, 0) + 1
    print("net con un solo pad:", sorted(n for n, k in pads.items() if k == 1))
