# -*- coding: utf-8 -*-
"""X210Ai rev 2.0 - scheda-ponte tutto-in-uno: modello dati unico (PCB, schema, BOM, firmware).

Coordinate in mm rispetto al centro di J1/J2 (asse y verso il basso, come KiCad).
Lato "T" = sopra (verso la tastiera), "B" = sotto (verso la scheda madre).
"""
import uuid as _uuid

REV = "2.0"
DATE = "2026-10-21"
TITLE = "X210Ai - scheda-ponte tastiera ISO/JIS (RP2040 integrato)"
COMPANY = "Progetto X210Ai ISO adapter"

ROOT_UUID = "854c47c9-edf5-41e6-af1e-1a0fd690f4e1"
_NS = _uuid.UUID("3f6c2b0e-2a8f-4a59-9d6e-2d1a0b7c0e20")


def uid(*k):
    return str(_uuid.uuid5(_NS, "/".join(map(str, k))))


def sym_uuid(ref, unit=1):
    return uid("sym", ref, unit)


# ---------------------------------------------------------------- GPIO
SIGNAL_GPIO = {
    "KB_C17": 0, "KB_C15": 1, "KB_C13": 2, "KB_C11": 3, "KB_C9": 4, "KB_C7": 5, "KB_C5": 6, "KB_C3": 7,
    "KB_FN": 8,
    "KB_R32": 9, "KB_R30": 10, "KB_R28": 11, "KB_R26": 12, "KB_R24": 13, "KB_R22": 14, "KB_R20": 15,
    "KB_R18": 16, "KB_R16": 17,
    # lato inferiore del QFN: righe vicine al connettore, poi TrackPoint/EC (ordine planare)
    "KB_R14": 18, "KB_R12": 19, "KB_R10": 20, "KB_R8": 21, "KB_R6": 22, "KB_R4": 23, "KB_R2": 24,
    "TP_RST_3V3": 25, "EC_FN_G": 26, "EC_PGUP_G": 27, "TP_CLK_3V3": 28, "TP_DATA_3V3": 29,
}
GPIO_SIGNAL = {g: s for s, g in SIGNAL_GPIO.items()}

# ordine righe/colonne della matrice nel firmware hektopuss (pin del connettore tastiera)
FW_ROW_PINS = [32, 28, 20, 16, 12, 8, 4, 22, 26, 30, 18, 14, 10, 6, 2, 24]
FW_COL_PINS = [5, 9, 13, 17, 15, 11, 7, 3]
ROW_IO = [SIGNAL_GPIO[f"KB_R{p}"] for p in FW_ROW_PINS]
COL_IO = [SIGNAL_GPIO[f"KB_C{p}"] for p in FW_COL_PINS]


def gpio_pin(g):
    """numero di pin del package QFN-56 per GPIOg"""
    if g <= 7:
        return 2 + g
    if g <= 15:
        return 11 + (g - 8)
    if g <= 21:
        return 27 + (g - 16)
    return 34 + (g - 22)


RP_PWR = {1: "+3V3", 10: "+3V3", 22: "+3V3", 33: "+3V3", 42: "+3V3", 49: "+3V3",
          43: "+3V3", 44: "+3V3", 48: "+3V3",
          23: "+1V1", 50: "+1V1", 45: "+1V1",
          57: "GND", 19: "GND"}
RP_OTHER = {20: "XIN", 21: "XOUT", 24: "SWCLK", 25: "SWDIO", 26: "RUN",
            46: "USB_DM_MCU", 47: "USB_DP_MCU",
            51: "QSPI_SD3", 52: "QSPI_SCLK", 53: "QSPI_SD0", 54: "QSPI_SD2", 55: "QSPI_SD1", 56: "QSPI_SS"}


def rp2040_pins():
    p = dict(RP_PWR)
    p.update(RP_OTHER)
    for g in range(30):
        p[gpio_pin(g)] = GPIO_SIGNAL[g]
    assert len(p) == 57, len(p)
    return p


# ---------------------------------------------------------------- connettori
J1_FIXED = {1: "KB_FN", 19: "PWR_SW", 31: "GND", 34: "GND", 36: "GND", 41: "GND",
            37: "TP_DATA_5V", 38: "VBUS", 39: "TP_CLK_5V", 40: "TP_RST_5V"}
J1_NC = [21, 23, 25, 27, 29, 33, 35]


def j1_net(p):
    if p in J1_FIXED:
        return J1_FIXED[p]
    if p % 2 == 0 and p <= 32:
        return f"KB_R{p}"
    if p % 2 == 1 and 3 <= p <= 17:
        return f"KB_C{p}"
    return None


# J2 = spina sotto la scheda, innestata in BTB_R_CONN1 della scheda madre
J2_NETS = {1: "MB_FN", 5: "MB_C5", 24: "MB_R24", 19: "PWR_SW", 31: "GND", 34: "GND", 36: "GND"}

# ---------------------------------------------------------------- footprint
FP = {
    "C0402": "Capacitor_SMD:C_0402_1005Metric",
    "R0402": "Resistor_SMD:R_0402_1005Metric",
    "QFN56": "Package_DFN_QFN:QFN-56-1EP_7x7mm_P0.4mm_EP3.2x3.2mm_ThermalVias",
    "USON8": "x210ai:Winbond_USON-8-1EP_3x2mm_P0.5mm_EP0.2x1.6mm",
    "SOT23": "Package_TO_SOT_SMD:SOT-23-3",
    "SOT363": "x210ai:SOT-363_SC-70-6_Tight",
    "XTAL": "Crystal:Crystal_SMD_3225-4Pin_3.2x2.5mm",
    "J1": "x210ai:JAE_AA01B-S040VA1_KB_Receptacle",
    "J2": "x210ai:JAE_AA01B-P040_MB_Plug_Bottom",
    "USB": "x210ai:Pads_1x04_P1.60mm_Wire_Edge",
    "TP": "x210ai:TP_Pad_1.0x1.0mm",
    "SJ": "Jumper:SolderJumper-2_P1.3mm_Open_RoundedPad1.0x1.5mm",
}

# valore -> (LCSC, MPN, produttore)
PARTS = {
    "100nF": ("C1525", "CL05B104KO5NNNC", "Samsung"),
    "1uF": ("C52923", "CL05A105KA5NQNC", "Samsung"),
    "15pF": ("C1548", "CL05C150JB5NNNC", "Samsung"),
    "10uF": ("C15525", "CL05A106MQ5NUNC", "Samsung"),
    "27R": ("C25100", "0402WGF270JTCE", "UNI-ROYAL"),
    "1k": ("C11702", "0402WGF1001TCE", "UNI-ROYAL"),
    "10k": ("C25744", "0402WGF1002TCE", "UNI-ROYAL"),
    "4.7k": ("C25900", "0402WGF4701TCE", "UNI-ROYAL"),
    "100k": ("C25741", "0402WGF1003TCE", "UNI-ROYAL"),
    "RP2040": ("C2040", "RP2040", "Raspberry Pi"),
    "W25Q16JVUXIQ": ("C2843335", "W25Q16JVUXIQ", "Winbond"),
    "XC6206P332MR": ("C5446", "XC6206P332MR-G", "Torex"),
    "12MHz": ("C20625731", "ABM8-272-T3", "Abracon"),
    "BSS138DW": ("C154900", "BSS138DW-7-F", "Diodes Inc."),
    "AA01B-S040VA1": ("C2938571", "AA01B-S040VA1-R3000", "JAE"),
    "AA01B-P040VA1": ("", "AA01B-P040VA1-R3000", "JAE"),
}

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
res("R13", "100k", "EC_FN_G", "GND", "pull-down gate Fn->EC")
res("R14", "100k", "EC_PGUP_G", "GND", "pull-down gate PgUp->EC")

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
    {1: "TP_RST_3V3", 2: "+3V3", 6: "TP_RST_5V", 4: "GND", 5: "EC_FN_G", 3: "MB_FN"},
    "traslatore reset TrackPoint (a), Fn verso EC (b)")
add("Q3", "BSS138DW", "SOT363",
    {1: "EC_PGUP_S", 2: "EC_PGUP_G", 6: "MB_R24", 4: "EC_PGUP_S", 5: "EC_PGUP_G", 3: "MB_C5"},
    "interruttore bidirezionale riga24-colonna5 (PgUp) verso EC")
add("J1", "AA01B-S040VA1", "J1",
    {p: j1_net(p) for p in list(range(1, 41)) + [41] if j1_net(p)}, "connettore tastiera (sopra)")
add("J2", "AA01B-P040VA1", "J2", dict(J2_NETS), "spina verso BTB_R_CONN1 (sotto)")
add("J3", "USB", "USB", {1: "VBUS", 2: "USB_DM", 3: "USB_DP", 4: "GND"}, "fili verso USB-CON1")
add("JP1", "BOOT", "SJ", {1: "BOOTSEL_N", 2: "GND"}, "ponticello BOOTSEL")
add("JP2", "RESET", "SJ", {1: "RUN", 2: "GND"}, "ponticello RESET")
add("TP1", "SWCLK", "TP", {1: "SWCLK"}, "test point SWD")
add("TP2", "SWDIO", "TP", {1: "SWDIO"}, "test point SWD")
add("TP3", "GND", "TP", {1: "GND"}, "test point")
add("TP4", "+3V3", "TP", {1: "+3V3"}, "test point")

DNP = {"J2"}                         # non montato da JLCPCB (non a magazzino LCSC)
NOT_ASSEMBLED = {"J3", "JP1", "JP2", "TP1", "TP2", "TP3", "TP4"}   # solo rame
TOP_SIDE = {"J1", "JP1", "JP2", "TP1", "TP2", "TP3", "TP4"}

BY_REF = {c["ref"]: c for c in COMP}
NETS = sorted({n for c in COMP for n in c["pins"].values() if n})
POWER_NETS = ["GND", "+3V3", "VBUS", "+1V1"]

# ---------------------------------------------------------------- scheda
X0, X1, Y0, Y1 = -29.0, 7.5, -5.0, 5.6
CORNER_R = 0.6
ORIGIN = (100.0, 100.0)
THICKNESS_MM = 0.8   # JLCPCB 4 strati: 0,4 / 0,8 mm e oltre (0,6 mm non disponibile)

# ref: (x, y, rot, lato)
PLACE = {
    "J1": (0, 0, 0, "T"), "J2": (0, 0, 0, "B"),
    "U1": (-15.45, 0.3, 270, "B"),
    "Y1": (-9.2, -0.4, 0, "B"), "C13": (-10.35, -2.6, 0, "B"), "R3": (-10.35, 1.95, 0, "B"),
    "C14": (-8.0, 1.95, 0, "B"), "C3": (-10.35, 2.95, 0, "B"), "C7": (-8.0, 2.95, 0, "B"),
    "R5": (-10.35, 3.95, 0, "B"),
    "C1": (-18.05, -4.4, 0, "B"), "C2": (-14.45, -4.4, 0, "B"), "C5": (-18.05, 5.0, 0, "B"),
    "C4": (-14.45, 5.0, 0, "B"),
    "U2": (-22.15, -0.95, 0, "B"), "C15": (-21.15, -2.75, 0, "B"), "R4": (-23.15, -2.75, 0, "B"),
    "C8": (-20.65, 0.85, 0, "B"), "C9": (-20.65, 1.85, 0, "B"), "C12": (-20.65, 2.85, 0, "B"),
    "C10": (-20.65, 3.85, 0, "B"), "C6": (-22.65, 0.85, 0, "B"), "C11": (-22.65, 2.85, 0, "B"),
    "R1": (-24.65, 0.83, 0, "B"), "R2": (-24.65, 1.8, 0, "B"), "J3": (-27.9, -1.6, 0, "B"),
    "U3": (-26.85, 4.0, 0, "B"), "C16": (-23.85, 3.95, 0, "B"), "C17": (-23.85, 4.95, 0, "B"),
    "R7": (-8.0, 3.95, 0, "B"), "R9": (-10.35, 4.95, 0, "B"), "R11": (-8.0, 4.95, 0, "B"),
    "C18": (5.8, -4.4, 0, "B"), "R8": (1.2, -4.35, 0, "B"), "R10": (3.9, -4.35, 180, "B"),
    "Q2": (-5.55, 4.37, 0, "B"), "R13": (-3.6, 4.37, 90, "B"), "Q3": (-1.6, 4.37, 0, "B"),
    "R14": (0.4, 4.37, 90, "B"), "R12": (2.0, 4.37, 90, "B"), "Q1": (5.4, 4.37, 0, "B"),
    "TP1": (-25.4, -4.1, 0, "T"), "TP2": (-24.0, -4.1, 0, "T"), "TP3": (-22.6, -4.1, 0, "T"),
    "TP4": (-21.2, -4.1, 0, "T"), "JP1": (-25.4, -1.6, 0, "T"), "JP2": (-21.8, -1.6, 0, "T"),
}

assert set(PLACE) == set(BY_REF), set(PLACE) ^ set(BY_REF)
for r, (_, _, _, side) in PLACE.items():
    assert (side == "T") == (r in TOP_SIDE), r

if __name__ == "__main__":
    print(len(COMP), "componenti,", len(NETS), "net")
    print("Row_IO", ROW_IO)
    print("Col_IO", COL_IO)
