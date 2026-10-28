# -*- coding: utf-8 -*-
"""Genera lo schema KiCad (formato 7, KiCad 8-10 lo converte) dal modello dati della scheda scelta.

Simboli: libreria embedded presa da uno schema esistente (rev 2.0: sch/x210ai.kicad_sch, oppure rev 1.3),
Q_Dual dalla libreria KiCad se manca, e i simboli nuovi della rev 2.2 (J1 sandwich, J4 eDP) generati qui.
Ogni pin collegato riceve un tratto di filo e un'etichetta globale (o un simbolo di alimentazione);
i pin liberi ricevono il simbolo "non collegato".

uso: python gen_sch2.py --board A|B ../sch/x210ai.kicad_sch <out.kicad_sch>
     (senza --board: rev 2.0)
"""
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import boards  # noqa: E402

D = boards.load()
BOARD = getattr(D, "BOARD", "2.0")

G = 2.54


# ------------------------------------------------------------------ s-expr
def tokenize(s):
    return re.findall(r'"(?:[^"\\]|\\.)*"|\(|\)|[^\s()"]+', s)


def parse(tokens):
    stack = [[]]
    for t in tokens:
        if t == "(":
            stack.append([])
        elif t == ")":
            x = stack.pop()
            stack[-1].append(x)
        else:
            stack[-1].append(t)
    return stack[0]


def dump(n, ind=0):
    if not isinstance(n, list):
        return n
    if not any(isinstance(x, list) for x in n):
        return "(" + " ".join(n) + ")"
    sp = "  " * (ind + 1)
    head = []
    rest = []
    for x in n:
        if not rest and not isinstance(x, list):
            head.append(x)
        else:
            rest.append(x)
    return "(" + " ".join(head) + "".join("\n" + sp + dump(x, ind + 1) for x in rest) + ")"


def q(s):
    return '"' + s.replace('"', '\\"') + '"'


def unq(s):
    return s[1:-1] if s.startswith('"') else s


def child(n, name):
    for x in n:
        if isinstance(x, list) and x and x[0] == name:
            return x
    return None


def children(n, name):
    return [x for x in n if isinstance(x, list) and x and x[0] == name]


# ------------------------------------------------------------------ librerie
def lib_symbols(rev13_sch):
    t = open(rev13_sch).read()
    i = t.find("(lib_symbols")
    depth = 0
    for j in range(i, len(t)):
        if t[j] == "(":
            depth += 1
        elif t[j] == ")":
            depth -= 1
            if depth == 0:
                break
    blk = parse(tokenize(t[i:j + 1]))[0]
    syms = {unq(s[1]): s for s in children(blk, "symbol")}
    # Q_Dual_NMOS dalla libreria di KiCad 10 (Transistor_FET, prima in Device): pin identici alla copia della
    # rev 2.0, che si scarta perche' l'ERC la segnalerebbe come diversa dalla libreria
    QD = "Transistor_FET:Q_Dual_NMOS_S1G1D2S2G2D1"
    syms.pop("Device:Q_Dual_NMOS_S1G1D2S2G2D1", None)
    dev = open(os.path.join(boards.kicad_share("symbols"), "Transistor_FET.kicad_sym")).read()
    a = dev.find('(symbol "Q_Dual_NMOS_S1G1D2S2G2D1"')
    depth = 0
    for b in range(a, len(dev)):
        if dev[b] == "(":
            depth += 1
        elif dev[b] == ")":
            depth -= 1
            if depth == 0:
                break
    qd = parse(tokenize(dev[a:b + 1]))[0]
    qd[1] = q(QD)
    syms[QD] = qd
    # simboli della rev 2.0 cambiati nelle librerie di KiCad 10 (pin spostati o rinumerati): restano come
    # sono, ma nella libreria di progetto x210ai, come fa il "rescue" di KiCad, cosi' lo schema non cambia
    for k in RESCUE:
        s = syms.pop(k)
        s[1] = q("x210ai:" + k.split(":")[1])
        syms["x210ai:" + k.split(":")[1]] = s
    syms.update(new_symbols())
    return syms


def conn_symbol(lib_id, units, descr, footprint):
    """simbolo connettore: units = [(sinistra, destra)] liste di (numero, nome) dall'alto in basso"""
    base = lib_id.split(":")[1]

    def font(*extra):
        return ["effects", ["font", ["size", "1.27", "1.27"]]] + list(extra)

    rows = max(max(len(l), len(r)) for l, r in units)
    top = G * (rows // 2)
    s = ["symbol", q(lib_id), ["pin_names", ["offset", "1.016"]], ["in_bom", "yes"], ["on_board", "yes"],
         ["property", q("Reference"), q("J"), ["at", "0", f"{top + 2 * G:g}", "0"], font()],
         ["property", q("Value"), q(base), ["at", "0", f"{top - rows * G - G:g}", "0"], font()],
         ["property", q("Footprint"), q(footprint), ["at", "0", "0", "0"], font("hide")],
         ["property", q("Datasheet"), q(""), ["at", "0", "0", "0"], font("hide")],
         ["property", q("ki_description"), q(descr), ["at", "0", "0", "0"], font("hide")]]
    for u, (left, right) in enumerate(units, 1):
        sub = ["symbol", q(f"{base}_{u}_1"),
               ["rectangle", ["start", "-10.16", f"{top + G:g}"], ["end", "10.16", f"{top - rows * G:g}"],
                ["stroke", ["width", "0.254"], ["type", "default"]], ["fill", ["type", "background"]]]]
        for side, pins in ((-1, left), (1, right)):
            for k, (num, name) in enumerate(pins):
                sub.append(["pin", "passive", "line",
                            ["at", f"{side * 15.24:g}", f"{top - k * G:g}", "0" if side < 0 else "180"],
                            ["length", "5.08"], ["name", q(name), font()], ["number", q(num), font()]])
        s.append(sub)
    return s


def new_symbols():
    """J1 sandwich (unita' 1 = ricettacolo sopra, 2 = spina sotto) e J4 eDP 40 pin + massa"""
    rec_l = [(str(n), str(n)) for n in range(1, 41, 2)] + [("TAB1", "TAB"), ("TAB3", "TAB")]
    rec_r = [(str(n), str(n)) for n in range(2, 41, 2)] + [("TAB2", "TAB"), ("TAB4", "TAB")]
    plug_l = [(str(100 + n), f"MB{n}") for n in range(1, 41, 2)]
    plug_r = [(str(100 + n), f"MB{n}") for n in range(2, 41, 2)]
    edp_l = [(str(n), str(n)) for n in range(1, 21)] + [("41", "GND_BAR")]
    edp_r = [(str(n), str(n)) for n in range(21, 41)]
    return {
        "x210ai:X210Ai_KB_Sandwich": conn_symbol(
            "x210ai:X210Ai_KB_Sandwich", [(rec_l, rec_r), (plug_l, plug_r)],
            "Unita' 1: ricettacolo JAE AA01B-S040VA1 sopra (riceve la tastiera, pinout T61). Unita' 2: spina "
            "AA01B-P040VA1 sotto (pin 100+n = pin n di BTB_R_CONN1). Impronta unica JAE_AA01_sandwich.",
            "x210ai:JAE_AA01_sandwich"),
        "x210ai:IPEX_20455-040E": conn_symbol(
            "x210ai:IPEX_20455-040E", [(edp_l, edp_r)],
            "Ricettacolo eDP I-PEX CABLINE-VS 20455-040E, 40 pin passo 0,5 mm; 41 = barra di massa e linguette",
            "x210ai:IPEX_20455-040E_90deg"),
    }


def pins_of(sym):
    """{unit: [(numero, nome, x, y, angolo, tipo)]} - unit 0 = comune a tutte"""
    out = {}
    base = unq(sym[1]).split(":")[-1]
    for sub in children(sym, "symbol"):
        m = re.match(re.escape(base) + r"_(\d+)_(\d+)$", unq(sub[1]))
        if not m or m.group(2) not in ("0", "1"):
            continue
        u = int(m.group(1))
        for p in children(sub, "pin"):
            at = child(p, "at")
            num = unq(child(p, "number")[1])
            name = unq(child(p, "name")[1])
            out.setdefault(u, []).append((num, name, float(at[1]), float(at[2]), int(float(at[3])), p[1]))
    return out


RESCUE = ["MCU_RaspberryPi:RP2040", "Memory_Flash:W25Q32JVZP", "Device:Crystal_GND24", "Jumper:SolderJumper_2_Open"]
LIBID = {"C0402": "Device:C", "R0402": "Device:R", "QFN56": "x210ai:RP2040",
         "USON8": "x210ai:W25Q32JVZP", "SOT23": "Regulator_Linear:XC6206PxxxMR",
         "SOT363": "Transistor_FET:Q_Dual_NMOS_S1G1D2S2G2D1", "XTAL": "x210ai:Crystal_GND24",
         "J1": "x210ai:X210Ai_KB_Receptacle", "J2": "x210ai:X210Ai_MB_Plug",
         "USB": "Connector_Generic:Conn_01x04", "TP": "Connector:TestPoint", "SJ": "x210ai:SolderJumper_2_Open",
         "JSANDWICH": "x210ai:X210Ai_KB_Sandwich", "EDP": "x210ai:IPEX_20455-040E"}
POWER = {"GND": "power:GND", "+3V3": "power:+3V3", "VBUS": "power:VBUS", "+1V1": "power:+1V1"}

# ------------------------------------------------------------------ disposizione (mm, griglia 2,54)
# (ref, unita', x, y)
LAYOUT = [
    ("J1", 1, 63.5, 88.9), ("J2", 1, 63.5, 190.5), ("J3", 1, 30.48, 256.54),
    ("U1", 1, 228.6, 139.7),
    ("Y1", 1, 172.72, 210.82), ("C13", 1, 160.02, 228.6), ("C14", 1, 185.42, 228.6), ("R3", 1, 190.5, 205.74),
    ("U2", 1, 317.5, 116.84), ("C15", 1, 342.9, 93.98), ("R4", 1, 294.64, 93.98), ("JP1", 1, 294.64, 81.28),
    ("U3", 1, 330.2, 210.82), ("C16", 1, 309.88, 223.52), ("C17", 1, 350.52, 223.52),
    ("C1", 1, 160.02, 50.8), ("C2", 1, 172.72, 50.8), ("C3", 1, 185.42, 50.8), ("C4", 1, 198.12, 50.8),
    ("C5", 1, 210.82, 50.8), ("C6", 1, 223.52, 50.8), ("C9", 1, 236.22, 50.8), ("C10", 1, 248.92, 50.8),
    ("C11", 1, 261.62, 50.8), ("C7", 1, 279.4, 50.8), ("C8", 1, 292.1, 50.8), ("C12", 1, 304.8, 50.8),
    ("C18", 1, 135.89, 256.54),
    ("Q1", 1, 129.54, 41.91), ("Q1", 2, 129.54, 72.39), ("R7", 1, 114.3, 33.02), ("R8", 1, 142.24, 33.02),
    ("R9", 1, 114.3, 63.5), ("R10", 1, 142.24, 63.5),
    ("Q2", 1, 129.54, 102.87), ("R11", 1, 114.3, 93.98), ("R12", 1, 142.24, 93.98),
    ("Q2", 2, 129.54, 168.91), ("R13", 1, 114.3, 179.07),
    ("Q3", 1, 129.54, 201.93), ("Q3", 2, 129.54, 229.87), ("R14", 1, 114.3, 215.9),
    ("R1", 1, 66.04, 251.46), ("R2", 1, 81.28, 251.46),
    ("R5", 1, 368.3, 139.7), ("JP2", 1, 368.3, 154.94),
    ("TP1", 1, 387.35, 76.2), ("TP2", 1, 387.35, 88.9), ("TP3", 1, 387.35, 101.6), ("TP4", 1, 387.35, 114.3),
]

NOTES = [
    (20.32, 132.08, f"{D.TITLE} - rev {D.REV}", 2.0),
    (20.32, 137.16, "J1 sopra: tastiera. J2 sotto: BTB_R_CONN1 della scheda madre (solo pin 1, 5, 19, 24 e masse).", 1.5),
    (20.32, 140.97, "RP2040 legge tutta la matrice e il TrackPoint e li invia via USB (fili verso USB-CON1).", 1.5),
    (20.32, 144.78, "Q2b e Q3 emulano Fn+PgUp verso l'EC (ThinkLight). Pin 19 (accensione) passa diretto J1-J2.", 1.5),
    (101.6, 20.32, "TrackPoint PS/2: traslatori BSS138 3,3 V <-> 5 V", 1.5),
    (101.6, 152.4, "Verso EC: Fn (J2-1) a massa, interruttore riga 24 - colonna 5 (PgUp)", 1.5),
    (152.4, 40.64, "Disaccoppiamento", 1.5),
    (284.48, 71.12, "Flash QSPI 2 MB + BOOTSEL", 1.5),
    (302.26, 195.58, "LDO 3,3 V da VBUS", 1.5),
    (20.32, 241.3, "USB verso USB-CON1 (4 fili)", 1.5),
    (360.68, 66.04, "SWD e RESET", 1.5),
]
COMMENTS = ["Scheda-ponte 4 strati: J1 sopra (tastiera), J2 sotto (scheda madre), RP2040 sotto",
            "Firmware: hektopuss ThinkPad_RP2040_Keyboard + patch X210Ai (Fn+PgUp via EC, swap Fn/Ctrl, JIS)"]

if BOARD == "A":
    # gruppo RP2040 e TrackPoint come nella rev 2.0; J4 (eDP) al posto di J1/J2
    LAYOUT = [it for it in LAYOUT if it[0] not in ("J1", "J2", "Q3", "R13", "R14")] + [("J4", 1, 63.5, 88.9)]
    NOTES = [n for n in NOTES if not n[2].startswith(("J1 sopra", "Q2b", "Verso EC"))] + [
        (20.32, 137.16, "J4: cavo eDP 40 pin verso la Board B (tastiera, TrackPoint, gate EC). Vedi CABLE_SPEC.md", 1.5),
        (101.6, 152.4, "Q2b non usato (a massa). I gate EC_FN_G / EC_PGUP_G vanno alla Board B via J4", 1.5),
    ]
    COMMENTS = ["Board A 4 strati 0,8 mm (JLCPCB): RP2040, flash, LDO, traslatori TrackPoint, USB, J4 eDP",
                "Firmware invariato: hektopuss ThinkPad_RP2040_Keyboard + patch X210Ai (GPIO come la rev 2.0)"]
elif BOARD == "B":
    LAYOUT = [("J1", 1, 63.5, 88.9), ("J2", 1, 63.5, 177.8), ("J4", 1, 228.6, 127.0),
              ("Q2", 1, 147.32, 88.9), ("Q2", 2, 147.32, 152.4), ("R13", 1, 132.08, 162.56),
              ("Q3", 1, 147.32, 190.5), ("Q3", 2, 147.32, 218.44), ("R14", 1, 132.08, 204.47)]
    NOTES = [
        (20.32, 20.32, f"{D.TITLE} - rev {D.REV}", 2.0),
        (20.32, 25.4, "J1: ricettacolo della tastiera (gradino basso). J2: spina sotto il gradino alto, in BTB_R_CONN1.", 1.5),
        (20.32, 29.21, "Alla scheda madre passano solo Fn (J2-1), PgUp emulato (J2-5, J2-24), accensione (J1-19 / J2-19) e GND.", 1.5),
        (20.32, 33.02, f"J4: cavo eDP verso la Board A, tipo {D.E.CABLE}. Vedi CABLE_SPEC.md", 1.5),
        (119.38, 139.7, "Verso EC: Q2b porta a massa Fn, Q3 chiude riga 24 - colonna 5 (PgUp)", 1.5),
    ]
    COMMENTS = ["Board B flessibile 2 strati a scalino: J2 su BTB_R_CONN1, J1 tastiera, J4 eDP verso la Board A",
                "Nessun componente attivo: solo l'emulazione Fn+PgUp verso l'EC (Q2b, Q3)"]


def build(rev13, out):
    syms = lib_symbols(rev13)
    used_lib = set()
    items = []
    pwr_n = [0]

    def nid(*k):
        return D.uid(*k)

    def prop(name, val, x, y, hide=False, angle=0, justify=None):
        e = ["effects", ["font", ["size", "1.27", "1.27"]]]
        if justify:
            e.append(["justify", justify])
        if hide:
            e.append("hide")
        return ["property", q(name), q(val), ["at", f"{x:g}", f"{y:g}", str(angle)], e]

    def place_symbol(lib_id, ref, value, x, y, unit, rot=0, fields=None, uuid=None, pins=(), dnp=False,
                     ref_xy=None, val_xy=None, hide_ref=False, footprint=""):
        used_lib.add(lib_id)
        rx, ry = ref_xy or (x + 3.81, y - 2.54)
        vx, vy = val_xy or (x + 3.81, y + 2.54)
        s = ["symbol", ["lib_id", q(lib_id)], ["at", f"{x:g}", f"{y:g}", str(rot)], ["unit", str(unit)],
             ["in_bom", "yes" if not ref.startswith("#") else "yes"], ["on_board", "yes"],
             ["dnp", "yes" if dnp else "no"], ["uuid", q(uuid)],
             prop("Reference", ref, rx, ry, hide=hide_ref, justify="left"),
             prop("Value", value, vx, vy, justify="left"),
             prop("Footprint", footprint, x, y, hide=True),
             prop("Datasheet", "", x, y, hide=True)]
        for k, v in (fields or {}).items():
            s.append(prop(k, v, x, y, hide=True))
        for p in pins:
            s.append(["pin", q(p), ["uuid", q(nid("pin", uuid, p))]])
        s.append(["instances", ["project", q(boards.project_name(D)), ["path", q("/" + D.ROOT_UUID), ["reference", q(ref)],
                                                          ["unit", str(unit)]]]])
        items.append(s)

    def wire(x1, y1, x2, y2):
        items.append(["wire", ["pts", ["xy", f"{x1:g}", f"{y1:g}"], ["xy", f"{x2:g}", f"{y2:g}"]],
                      ["stroke", ["width", "0"], ["type", "default"]], ["uuid", q(nid("w", x1, y1, x2, y2))]])

    def glabel(name, x, y, ang):
        just = "left" if ang in (0, 90) else "right"
        items.append(["global_label", q(name), ["shape", "passive"], ["at", f"{x:g}", f"{y:g}", str(ang)],
                      ["fields_autoplaced"],
                      ["effects", ["font", ["size", "1.27", "1.27"]], ["justify", just]],
                      ["uuid", q(nid("gl", name, x, y))],
                      ["property", q("Intersheetrefs"), q("${INTERSHEET_REFS}"), ["at", f"{x:g}", f"{y:g}", "0"],
                       ["effects", ["font", ["size", "1.27", "1.27"]], "hide"]]])

    def power(net, x, y, ang_out):
        pwr_n[0] += 1
        ref = f"#PWR{pwr_n[0]:03d}"
        lib = POWER[net]
        if net == "GND":
            rot = {270: 0, 90: 180, 0: 90, 180: 270}[ang_out]
        else:
            rot = {90: 0, 270: 180, 180: 90, 0: 270}[ang_out]
        place_symbol(lib, ref, net, x, y, 1, rot, uuid=nid("pwr", ref), pins=["1"], hide_ref=True,
                     ref_xy=(x, y), val_xy=(x, y + (3.2 if net == "GND" else -3.2)))

    def noconn(x, y):
        items.append(["no_connect", ["at", f"{x:g}", f"{y:g}"], ["uuid", q(nid("nc", x, y))]])

    def text(s, x, y, size):
        items.append(["text", q(s), ["exclude_from_sim", "no"] if False else ["at", f"{x:g}", f"{y:g}", "0"],
                      ["effects", ["font", ["size", f"{size:g}", f"{size:g}"]], ["justify", "left", "bottom"]],
                      ["uuid", q(nid("txt", s))]])

    seen_pin = {}
    for ref, unit, x, y in LAYOUT:
        c = D.BY_REF[ref]
        lib_id = LIBID[c["fpkey"]]
        sym = syms[lib_id]
        pins = pins_of(sym)
        upins = pins.get(0, []) + pins.get(unit, [])
        lcsc, mpn, mfr = D.PARTS.get(c["value"], ("", "", ""))
        if ref == "J1" and hasattr(D, "J1_PARTS"):     # Board B: come build_pcb, la parte montata sopra
            _, _, lcsc, mpn, mfr, _ = D.J1_PARTS[0]
        fields = {}
        if lcsc:
            fields["LCSC"] = lcsc
        if mpn:
            fields["MPN"] = mpn
            fields["Manufacturer"] = mfr
        if ref in D.DNP:
            fields["Note"] = "DNP: non a magazzino LCSC, saldare a mano"
        if ref in D.NOT_ASSEMBLED:
            fields["Note"] = "solo rame (non assemblato)"
        bx = [p[2] for p in upins]
        top = min([-p[3] for p in upins] + [0])
        place_symbol(lib_id, ref, c["value"], x, y, unit, 0, fields, D.sym_uuid(ref, unit),
                     [p[0] for p in upins], dnp=(ref in D.DNP), footprint=c["fp"],
                     ref_xy=(x + max(bx + [0]) + 1.27, y + top - 1.27) if lib_id.startswith("x210ai") or
                     lib_id.endswith("RP2040") else None)
        for num, name, px, py, ang, typ in upins:
            key = int(num) if num.isdigit() else num
            net = c["pins"].get(key)
            seen_pin[(ref, num)] = net
            cx, cy = x + px, y - py
            # direzione verso l'esterno (opposta a quella del pin)
            odir = (ang + 180) % 360
            dx, dy = {0: (1, 0), 180: (-1, 0), 90: (0, -1), 270: (0, 1)}[odir]
            if net is None:
                noconn(cx, cy)
                continue
            ex, ey = cx + dx * G, cy + dy * G
            wire(cx, cy, ex, ey)
            if net in POWER:
                power(net, ex, ey, odir)
            else:
                glabel(net, ex, ey, odir)
    # bandierine di alimentazione (GND e VBUS arrivano dal connettore USB)
    for i, net in enumerate(("GND", "VBUS")):
        x, y = 30.48 + 15.24 * i, 284.48
        pwr_n[0] += 1
        place_symbol("power:PWR_FLAG", f"#FLG{i + 1:02d}", "PWR_FLAG", x, y, 1, 0, uuid=nid("flg", net), pins=["1"],
                     hide_ref=True, val_xy=(x, y - 3.81))
        wire(x, y, x, y + G)
        power(net, x, y + G, 270)
    for x, y, s, size in NOTES:
        text(s, x, y, size)

    # controllo: ogni pin del modello dati e' presente nello schema
    for c in D.COMP:
        for p, n in c["pins"].items():
            if (c["ref"], str(p)) not in seen_pin:
                raise SystemExit(f"pin {c['ref']}.{p} ({n}) non presente nel simbolo")

    lib = ["lib_symbols"] + [syms[k] for k in sorted(used_lib)]
    doc = ["kicad_sch", ["version", "20230121"], ["generator", "eeschema"], ["uuid", q(D.ROOT_UUID)],
           ["paper", q("A3")],
           ["title_block", ["title", q(D.TITLE)], ["date", q(D.DATE)], ["rev", q(D.REV)],
            ["company", q("Basato su thedalles77 (T61 Teensy 4.0) e hektopuss (ThinkPad_RP2040_Keyboard)")],
            ["comment", "1", q(COMMENTS[0])], ["comment", "2", q(COMMENTS[1])]],
           lib] + items + [["sheet_instances", ["path", q("/"), ["page", q("1")]]]]
    open(out, "w", newline="\n").write(dump(doc) + "\n")      # fine riga LF come KiCad, anche su Windows
    # libreria di progetto con i simboli x210ai usati, cosi' l'ERC li trova (sym-lib-table accanto allo schema)
    d = os.path.dirname(os.path.abspath(out))
    mine = [[s[0], q(unq(s[1]).split(":", 1)[1])] + s[2:] for k, s in sorted(syms.items())
            if k in used_lib and k.startswith("x210ai:")]
    lib_doc = ["kicad_symbol_lib", ["version", "20220914"], ["generator", "x210ai_gen_sch2"]] + mine
    open(os.path.join(d, "x210ai.kicad_sym"), "w", newline="\n").write(dump(lib_doc) + "\n")
    open(os.path.join(d, "sym-lib-table"), "w", newline="\n").write(
        '(sym_lib_table\n  (version 7)\n  (lib (name "x210ai")(type "KiCad")(uri "${KIPRJMOD}/x210ai.kicad_sym")'
        '(options "")(descr "Simboli progetto X210Ai"))\n)\n')
    print(f"schema: {len(items)} oggetti, simboli di libreria {len(used_lib)}")


if __name__ == "__main__":
    build(sys.argv[1], sys.argv[2])
