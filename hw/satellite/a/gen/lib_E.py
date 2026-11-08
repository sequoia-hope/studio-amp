"""lib_E.py -- block E project symbols and footprints (lib/studio_E.kicad_sym, lib/studio_E.pretty).

Run from the repo root:  python3 hw/satellite/a/gen/lib_E.py

Symbols
  LFE5U-25F-7BG256I  ECP5, caBGA-256, built from Lattice's pinout CSV
                     (design/datasheets/lattice-ECP5U-25-pinout.csv, column CABGA256). Every one of
                     the 256 balls is placed exactly once; the script checks that against the CSV.
                     Units by function: 1-6 the I/O banks 0, 1, 2, 3, 6, 7; 7 bank 8 + sysCONFIG +
                     JTAG; 8 core power (VCC, VCCAUX, GND); 9 I/O power (VCCIO0-8).
                     Pin side follows this design's net direction (E-pinmap.md): inputs left,
                     outputs and bidirectional right, spare balls at the bottom. Pins that carry a
                     series resistor or a pull get extra room so the parts sit at the pin.
  VCXO_3225          4-pad 3.2 x 2.5 mm VCXO / XO: 1 Vc (OE on the XO), 2 GND, 3 OUT, 4 VDD
                     (SX3V datasheet p.2 pin table; YXC YSO110TR p.3).
Footprints
  Lattice_caBGA-256_14x14mm_Layout16x16_P0.8mm   KiCad's BGA-256 0.8 mm 16x16 grid (ball names A1-T16,
                     no I/O rows) with Lattice's caBGA land: 0.40 mm NSMD pad, mask +0.075 mm (as KiCad's
                     Lattice_caBGA-381, same 0.45 mm ball and 0.8 mm pitch; E-fpga-ecp5.md fan-out).
  Oscillator_SMD_3225-4Pin_YXC_SX3V               one land for the SX3V VCXO and the YXC XOs: YXC's
                     recommended 1.3 x 1.2 mm pads at 2.1 x 1.9 mm centres, which contain SX3V's
                     1.2 x 0.95 mm pads at 2.2 x 1.75 mm (both datasheets' pad drawings).
"""
from __future__ import annotations

import math
import re
import sys
import uuid
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import e_pins  # noqa: E402

LIB = HERE.parent / "lib"
SYM = LIB / "studio_E.kicad_sym"
PRETTY = LIB / "studio_E.pretty"
KICAD_FP = Path("/usr/share/kicad/footprints")
G = 2.54
PL = 5.08     # I/O pin length: the ball number sits mid-pin, clear of a no-connect X at the end


def q(s):
    return '"' + str(s).replace('\\', '\\\\').replace('"', '\\"') + '"'


def f(v):
    s = f"{v:.4f}".rstrip("0").rstrip(".")
    return "0" if s in ("-0", "") else s


def up(v, step=G):
    return math.ceil(round(v / step, 6)) * step


def natkey(s):
    return [int(t) if t.isdigit() else t for t in re.split(r"(\d+)", s)]


def pin_line(et, x, y, ang, name, num, length=G, hide=False):
    h = " (hide yes)" if hide else ""
    return (f"\t\t\t(pin {et} line (at {f(x)} {f(y)} {ang}) (length {f(length)}){h}"
            f" (name {q(name)} (effects (font (size 1.27 1.27))))"
            f" (number {q(num)} (effects (font (size 1.27 1.27)))))")


def rect(x0, y0, x1, y1):
    return (f"\t\t\t(rectangle (start {f(x0)} {f(y0)}) (end {f(x1)} {f(y1)}) "
            "(stroke (width 0.254) (type default)) (fill (type background)))")


def stext(s, x, y, size=1.27, just=""):
    j = f" (justify {just})" if just else ""
    return f"\t\t\t(text {q(s)} (at {f(x)} {f(y)} 0) (effects (font (size {size} {size}) (bold yes)){j}))"


def header(name, ref, value, fp, ds, desc, kw, ref_y, val_y, extra=()):
    out = [f"\t(symbol {q(name)}", "\t\t(exclude_from_sim no)", "\t\t(in_bom yes)", "\t\t(on_board yes)"]

    def prop(k, v, x, y, hide=False, just=""):
        h_ = " (hide yes)" if hide else ""
        j = f" (justify {just})" if just else ""
        out.append(f"\t\t(property {q(k)} {q(v)} (at {f(x)} {f(y)} 0) (effects (font (size 1.27 1.27)){j}{h_}))")
    prop("Reference", ref, 0, ref_y)
    prop("Value", value, 0, val_y)
    prop("Footprint", fp, 0, 0, True)
    prop("Datasheet", ds, 0, 0, True)
    prop("Description", desc, 0, 0, True)
    prop("ki_keywords", kw, 0, 0, True)
    for k, v in extra:
        prop(k, v, 0, 0, True)
    return out


# ------------------------------------------------------------------ ECP5
ECP5 = "LFE5U-25F-7BG256I"
BGA_FP = "studio_E:Lattice_caBGA-256_14x14mm_Layout16x16_P0.8mm"

# half-heights each kind of pin needs above / below its wire for the parts drawn there (mm)
NEED = {"plain": (0.3, 0.3), "ser": (2.8, 1.1), "pu": (11.7, 0.3), "pd": (0.3, 11.7), "gnd": (0.3, 4.6)}


def pin_need(net):
    if net is None:
        return NEED["plain"]
    d = e_pins.FPGA_DECOR.get(net, {})
    a, b = NEED["plain"]
    for k in ("ser", "pu", "pd", "gnd"):
        if d.get(k):
            a, b = max(a, NEED[k][0]), max(b, NEED[k][1])
    if d.get("pu_far"):
        a = max(a, NEED["pu"][0])
    return a, b


def short_name(r):
    name = r["func"]
    if r["dual"]:
        name += "/" + "/".join(r["dual"].split("/")[:2])
    return name


def layout_side(items):
    """items: [(ball, name, net)] top to bottom -> [(ball, name, y)] with y going down from 0."""
    out, y, prev_below = [], 0.0, None
    for ball, name, net in items:
        above, below = pin_need(net)
        if prev_below is not None:
            y -= up(max(G, prev_below + above + 0.6))
        out.append((ball, name, y))
        prev_below = below
    return out


def bank_unit(unit, title, balls, nets, b):
    left, right, spare = [], [], []
    for ball in balls:
        if ball in nets:
            net, d = nets[ball][0], nets[ball][1]
            (left if d == "in" else right).append((ball, short_name(b[ball]), net))
        else:
            spare.append((ball, short_name(b[ball]), None))
    left.sort(key=lambda t: natkey(t[2]))
    right.sort(key=lambda t: natkey(t[2]))
    spare.sort(key=lambda t: natkey(t[1]))
    # spare balls fill the shorter side, after one empty row
    for s in spare:
        hl = -layout_side(left)[-1][2] if left else -G
        hr = -layout_side(right)[-1][2] if right else -G
        (left if hl <= hr else right).append(s)
    L, R = layout_side(left), layout_side(right)
    lw = max([len(n) for _, n, _ in L] + [4])
    rw = max([len(n) for _, n, _ in R] + [4])
    w = up((lw + rw) * 1.05 + 5.08, 2 * G)
    w = max(w, up(len(title) * 1.15 + 4, 2 * G))
    bottom = min([y for *_, y in L + R]) - G
    lines = [f"\t\t(symbol {q(f'{ECP5}_{unit}_1')}", rect(-w / 2, 5.08, w / 2, bottom),
             stext(title, 0, 2.54)]
    for ball, name, y in L:
        lines.append(pin_line("bidirectional", -w / 2 - PL, y, 0, name, ball, length=PL))
    for ball, name, y in R:
        lines.append(pin_line("bidirectional", w / 2 + PL, y, 180, name, ball, length=PL))
    lines.append("\t\t)")
    return lines, [x[0] for x in L + R]


CONFIG_TYPES = {"CCLK": "input", "PROGRAMN": "input", "INITN": "bidirectional", "DONE": "bidirectional",
                "CFG_0": "input", "CFG_1": "input", "CFG_2": "input",
                "TCK": "input", "TDI": "input", "TMS": "input", "TDO": "output"}


def config_unit(unit, b, nets):
    """bank 8 (sysCONFIG dual-purpose I/O) + dedicated config pins + JTAG (bank 40)."""
    balls = [k for k, r in b.items() if r["bank"] in ("8", "40") and not r["func"].startswith("VCC")]
    left, right = [], []
    for ball in balls:
        net, d = nets[ball][0], nets[ball][1]
        (left if d == "in" else right).append((ball, short_name(b[ball]), net))
    order = ["FPGA_CCLK", "FPGA_MOSI", "FPGA_SN", "FPGA_HOLDN", "FPGA_PROGRAMN",
             "FPGA_CFG0", "FPGA_CFG1", "FPGA_CFG2", "FPGA_TCK", "FPGA_TDI", "FPGA_TMS"]
    left.sort(key=lambda t: order.index(t[2]) if t[2] in order else 99)
    rorder = ["FPGA_MISO", "FPGA_INITN", "FPGA_DONE", "FPGA_TDO"]
    right.sort(key=lambda t: (rorder.index(t[2]) if t[2] in rorder else 99, natkey(t[2])))
    L, R = layout_side(left), layout_side(right)
    lw = max(len(n) for _, n, _ in L)
    rw = max(len(n) for _, n, _ in R)
    w = up((lw + rw) * 1.05 + 5.08, 2 * G)
    bottom = min(y for *_, y in L + R) - G
    lines = [f"\t\t(symbol {q(f'{ECP5}_{unit}_1')}", rect(-w / 2, 5.08, w / 2, bottom),
             stext("BANK 8 sysCONFIG + JTAG", 0, 2.54)]
    for ball, name, y in L:
        et = CONFIG_TYPES.get(b[ball]["func"], "bidirectional")
        lines.append(pin_line(et, -w / 2 - PL, y, 0, name, ball, length=PL))
    for ball, name, y in R:
        et = CONFIG_TYPES.get(b[ball]["func"], "bidirectional")
        lines.append(pin_line(et, w / 2 + PL, y, 180, name, ball, length=PL))
    lines.append("\t\t)")
    return lines, [x[0] for x in L + R]


# Top-pin layout of the power units. A group, left to right: its rail's power symbol, its bulk
# caps, then one pin per ball with its 100 nF 5.08 mm to the right of the pin (fpga.py draws them
# from these positions). LEAD = power symbol to first ball; GAP = last ball to next power symbol.
PITCH = 12.7
LEAD = {"VCC": 30.48, "VCCAUX": 25.4, "VCCIO": 15.24}
GAP = 15.24


def group_of(name):
    return "VCCIO" if name.startswith("VCCIO") else name


def power_unit(unit, title, groups, b, gnd=None):
    """groups: [(label, [balls])]. Returns lines, balls."""
    x = 2.54                      # first power symbol
    pins = []
    for label, balls in groups:
        x += LEAD[group_of(label)]
        for ball in sorted(balls, key=natkey):
            pins.append((ball, b[ball]["func"], x))
            x += PITCH
        x += GAP - PITCH
    if gnd:
        x = max(x, 5.08 * (len(gnd) + 1))
    w = up(x, 2 * G)
    h = 15.24
    tpos = (2.54, -h / 2, "left") if gnd else (w / 2, -h + 2.54, "")   # clear of the pin names
    lines = [f"\t\t(symbol {q(f'{ECP5}_{unit}_1')}", rect(0, 0, w, -h),
             stext(title, tpos[0], tpos[1], just=tpos[2])]
    for ball, name, px in pins:
        lines.append(pin_line("power_in", px, G, 270, name, ball))
    if gnd:     # one pin per GND ball along the bottom, each with its own ground symbol
        gx = up((w - 5.08 * (len(gnd) - 1)) / 2, 2 * G)
        for i, ball in enumerate(sorted(gnd, key=natkey)):
            lines.append(pin_line("power_in", gx + 5.08 * i, -h - G, 90, "GND", ball))
    lines.append("\t\t)")
    return lines, [p[0] for p in pins] + list(gnd or [])


def ecp5_symbol():
    b = e_pins.ecp5_balls()
    nets = e_pins.fpga_nets()
    funcs = {r["func"] for r in b.values()}
    assert not ({"NC", "RESERVED"} & funcs), "unexpected NC/RESERVED ball in CABGA256"
    for ball, (net, *_r) in nets.items():
        assert ball in b, ball
    units, placed = [], []
    titles = {"0": "BANK 0 (top)", "1": "BANK 1 (top)", "2": "BANK 2 (right)", "3": "BANK 3 (right)",
              "6": "BANK 6 (left)", "7": "BANK 7 (left)"}
    io = lambda bank: [k for k, r in b.items() if r["bank"] == bank and r["func"].startswith("P")
                       and r["func"] != "PROGRAMN"]
    for u, bank in enumerate(["0", "1", "2", "3", "6", "7"], 1):
        lines, bl = bank_unit(u, titles[bank], io(bank), nets, b)
        units += lines
        placed += bl
    lines, bl = config_unit(7, b, nets)
    units += lines
    placed += bl
    by = lambda fn: [k for k, r in b.items() if r["func"] == fn]
    lines, bl = power_unit(8, "CORE POWER", [("VCC", by("VCC")), ("VCCAUX", by("VCCAUX"))], b, gnd=by("GND"))
    units += lines
    placed += bl
    lines, bl = power_unit(9, "I/O POWER (all banks 3.3 V)",
                           [(f"VCCIO{n}", by(f"VCCIO{n}")) for n in "0123678"], b)
    units += lines
    placed += bl
    # every ball exactly once
    if sorted(placed) != sorted(b):
        missing = set(b) - set(placed)
        dup = {p for p in placed if placed.count(p) > 1}
        raise SystemExit(f"ECP5 symbol: missing {sorted(missing)}, duplicated {sorted(dup)}")
    # pin names agree with the CSV function of each ball
    for line in units:
        m = re.search(r'\(name "([^"]+)".*\(number "([A-T]\d+)"', line)
        if m and m.group(1).split("/")[0] != b[m.group(2)]["func"]:
            raise SystemExit(f"ball {m.group(2)}: name {m.group(1)} vs CSV {b[m.group(2)]['func']}")
    out = header(ECP5, "U", ECP5, BGA_FP,
                 "https://www.latticesemi.com/view_document?document_id=50461",
                 "ECP5 FPGA, 24K LUTs, 1.1 V core, caBGA-256 14x14 mm, speed -7, industrial",
                 "FPGA ECP5 Lattice", 10.16, -10.16)
    out.insert(1, "\t\t(pin_numbers (hide no))")
    out.append(f"\t\t(property \"ki_locked\" \"\" (at 0 0 0) (effects (font (size 1.27 1.27))))")
    out += units
    out.append("\t\t(embedded_fonts no)")
    out.append("\t)")
    return "\n".join(out), len(placed)


# ------------------------------------------------------------------ RP2350B
RP = "RP2350B"
RP_FP = "Package_DFN_QFN:QFN-80-1EP_10x10mm_P0.4mm_EP3.4x3.4mm"
# passives drawn at RP2350 pins (mcu.py); pin spacing follows them
RP_DECOR = {"FPGA_CCLK": {"ser": "33R"}, "IBUS_SENSE": {"pd": "100n"}}
# power unit, left to right: (pin numbers, gap before the first pin in mm). One pin per ball.
RP_POWER = [
    (["61"], 15.24),                      # VREG_AVDD: +3V3 -> 33R -> 4u7 (CFILT)
    (["64"], 30.48),                      # VREG_VIN: +3V3, CIN 4u7
    (["63"], 15.24),                      # VREG_LX -> L 3.3u
    (["65", "10", "32", "51"], 12.7),     # VREG_FB, DVDD x3 on the regulator output (DVDD_RP)
    (["5", "15", "24", "29", "41", "50", "60", "76", "69", "68"], 43.18),   # IOVDD x8, QSPI_IOVDD, USB_OTP_VDD
    (["59"], 30.48),                      # ADC_AVDD: +3V3 -> 10R -> 4u7 + 100n
]


def rp_symbol():
    """RP2350B QFN-80 in four units. Pin numbers, names and types are KiCad's MCU_RaspberryPi:RP2350B
    (checked here against design/parts/E-pinmap.md, which was taken from the RP2350 datasheet Fig. 3 /
    Tab. 2). Stacked passive IOVDD/DVDD pins become one power_in pin per ball."""
    import hier  # noqa: F401  (puts kicad_write on the path)
    from kicad_write import SymbolLib, symbol_pins
    src = symbol_pins(SymbolLib().get("MCU_RaspberryPi:RP2350B"), 1)
    pm = e_pins.rp_nets()
    for num, (name, *_r) in pm.items():
        if num in src and src[num]["name"].replace("~{", "").replace("}", "") != name:
            raise SystemExit(f"RP2350B pin {num}: KiCad {src[num]['name']} vs E-pinmap {name}")
    assert sorted(src, key=int) == [str(i) for i in range(1, 82)], "RP2350B: pins 1-81 expected"
    nm = lambda n: src[n]["name"]
    et = lambda n: "power_in" if src[n]["type"] == "passive" and nm(n) in ("IOVDD", "DVDD") else src[n]["type"]
    gpio = {n: int(re.match(r"GPIO(\d+)", nm(n)).group(1)) for n in src if nm(n).startswith("GPIO")}

    def need(net):
        dec = RP_DECOR.get(net, {})
        a, b_ = NEED["plain"]
        for k in ("ser", "pu", "pd"):
            if dec.get(k):
                a, b_ = max(a, NEED[k][0]), max(b_, NEED[k][1])
        return a, b_

    def lay(items):
        out, y, prev = [], 0.0, None
        for n, net in items:
            a, b_ = need(net)
            if prev is not None:
                y -= up(max(G, prev + a + 0.6))
            out.append((n, y))
            prev = b_
        return out

    units = []
    for u, (lo, hi, title) in enumerate([(0, 23, "GPIO0-23"), (24, 47, "GPIO24-47 / ADC")], 1):
        pins = [n for n, g in gpio.items() if lo <= g <= hi]
        left, right, spare = [], [], []
        for n in sorted(pins, key=lambda n: gpio[n]):
            net, d = pm[n][1], pm[n][2]
            if net.startswith("SPARE"):
                spare.append((n, None))
            elif d in ("in", "ain"):
                left.append((n, net))
            else:
                right.append((n, net))
        for s in spare:
            (left if len(left) <= len(right) else right).append(s)
        L, R = lay(left), lay(right)
        w = up((max(len(nm(n)) for n, _ in L + R) * 2) * 1.05 + 5.08, 2 * G)
        bottom = min(y for _, y in L + R) - G
        units += [f"\t\t(symbol {q(f'{RP}_{u}_1')}", rect(-w / 2, 5.08, w / 2, bottom), stext(title, 0, 2.54)]
        units += [pin_line(et(n), -w / 2 - PL, y, 0, nm(n), n, length=PL) for n, y in L]
        units += [pin_line(et(n), w / 2 + PL, y, 180, nm(n), n, length=PL) for n, y in R]
        units.append("\t\t)")
    # unit 3: system. Left: SWD, crystal, RUN. Right: QSPI in flash pin order, USB.
    sysL = [("33", 0), ("34", -2.54), ("30", -12.7), ("31", -30.48), ("35", -45.72)]
    sysR = [("75", 0), ("71", -2.54), ("72", -5.08), ("74", -7.62), ("73", -10.16), ("70", -12.7),
            ("66", -25.4), ("67", -30.48)]
    w = 30.48
    units += [f"\t\t(symbol {q(f'{RP}_3_1')}", rect(-w / 2, 5.08, w / 2, -48.26), stext("SYSTEM", 0, 2.54)]
    units += [pin_line(et(n), -w / 2 - G, y, 0, nm(n), n) for n, y in sysL]
    units += [pin_line(et(n), w / 2 + G, y, 180, nm(n), n) for n, y in sysR]
    units.append("\t\t)")
    # unit 4: power
    x, top = 0.0, []
    for nums, gap in RP_POWER:
        x += gap
        for i, n in enumerate(nums):
            if i:
                x += PITCH
            top.append((n, x))
    w = up(x + 12.7, 2 * G)
    h = 15.24
    units += [f"\t\t(symbol {q(f'{RP}_4_1')}", rect(0, 0, w, -h), stext("POWER", 2.54, -h / 2, just="left")]
    units += [pin_line(et(n), px, G, 270, nm(n), n) for n, px in top]
    gx = up(w / 2, 2 * G)
    units.append(pin_line("power_in", gx - 5.08, -h - G, 90, nm("62"), "62"))
    units.append(pin_line("power_in", gx + 5.08, -h - G, 90, nm("81"), "81"))
    units.append("\t\t)")
    placed = re.findall(r'\(number "(\d+)"', "\n".join(units))
    if sorted(placed, key=int) != sorted(src, key=int):
        raise SystemExit(f"RP2350B symbol: placed {len(placed)} pins, dup/missing "
                         f"{sorted(set(src) ^ set(placed))} {[p for p in placed if placed.count(p) > 1]}")
    out = header(RP, "U", RP, RP_FP, "design/datasheets/rp2350-lcsc.pdf",
                 "RP2350B dual Cortex-M33 / Hazard3 MCU, 48 GPIO, QFN-80 10x10 mm, internal 1.1 V regulator",
                 "RP2350 microcontroller", 10.16, -10.16)
    out.insert(1, "\t\t(pin_numbers (hide no))")
    out.append("\t\t(property \"ki_locked\" \"\" (at 0 0 0) (effects (font (size 1.27 1.27))))")
    out += units + ["\t\t(embedded_fonts no)", "\t)"]
    return "\n".join(out), len(placed)


# ------------------------------------------------------------------ LAN8720A
LAN = "LAN8720AI"
LAN_FP = "Package_DFN_QFN:QFN-24-1EP_4x4mm_P0.5mm_EP2.5x2.5mm"
# what ethernet.py draws at each pin (sets the pin spacing): kind per pin number
LAN_KIND = {"16": "pd", "8": "pu", "7": "pu", "11": "pu", "12": "pu", "15": "pd", "14": "pu",
            "5": "ser", "21": "pu", "20": "pu", "23": "pu", "22": "pu", "3": "ser", "2": "ser", "24": "pd"}
LAN_LEFT = ["8", "7", "11", "10", "17", "18", "16", "13", "12", "14", "15", "5", "4"]
LAN_RIGHT = ["21", "20", "23", "22", "3", "2", "24"]
LAN_TOP = [("6", -17.78), ("9", -5.08), ("19", 5.08), ("1", 17.78)]


def lan_symbol():
    """LAN8720A QFN-24: pin numbers, names and types from KiCad's Interface_Ethernet:LAN8720A
    (agree with the LAN8720A datasheet Tab 2-8 as read for E-phy-lan8720.md: XTAL1 5, VDDCR 6,
    VDDIO 9, VDD1A 19, VDD2A 1, RBIAS 24, LED1 3, LED2 2). Rearranged so each pull and series part
    has room at its pin; supplies on top in the order their filters are drawn."""
    import hier  # noqa: F401
    from kicad_write import SymbolLib, symbol_pins
    src = symbol_pins(SymbolLib().get("Interface_Ethernet:LAN8720A"), 1)
    assert sorted(src, key=int) == [str(i) for i in range(1, 26)]

    def lay(nums, y0):
        out, y, prev = [], y0, None
        for n in nums:
            a, b_ = NEED[LAN_KIND.get(n, "plain")]
            if prev is not None:
                y -= up(max(G, prev + a + 0.6))
            if n in ("13", "5", "3"):          # group gaps: management, clock / LEDs
                y -= 2 * G
            out.append((n, y))
            prev = b_
        return out
    L, R = lay(LAN_LEFT, 0.0), lay(LAN_RIGHT, -10.16)
    w = 45.72
    bottom = min(y for _, y in L + R) - G
    lines = [f"\t\t(symbol {q(LAN + '_1_1')}", rect(-w / 2, 5.08, w / 2, bottom)]
    lines += [pin_line(src[n]["type"], -w / 2 - G, y, 0, src[n]["name"], n) for n, y in L]
    lines += [pin_line(src[n]["type"], w / 2 + G, y, 180, src[n]["name"], n) for n, y in R]
    lines += [pin_line(src[n]["type"], x, 5.08 + G, 270, src[n]["name"], n) for n, x in LAN_TOP]
    lines.append(pin_line(src["25"]["type"], 0, bottom - G, 90, src["25"]["name"], "25"))
    lines.append("\t\t)")
    placed = re.findall(r'\(number "(\d+)"', "\n".join(lines))
    assert sorted(placed, key=int) == sorted(src, key=int), placed
    out = header(LAN, "U", LAN, LAN_FP, "design/datasheets/lan8720a.pdf",
                 "10/100 Ethernet PHY, RMII, HP Auto-MDIX, 24-QFN 4x4 mm, industrial", "Ethernet PHY RMII",
                 10.16, -10.16)
    out += lines + ["\t\t(embedded_fonts no)", "\t)"]
    return "\n".join(out)


def vcxo_symbol():
    name = "VCXO_3225"
    out = header(name, "Y", name, "studio_E:Oscillator_SMD_3225-4Pin_YXC_SX3V",
                 "design/datasheets/sx3v-vcxo.pdf",
                 "Voltage-controlled crystal oscillator, CMOS, 3.2x2.5 mm 4-pad (pin 1 Vc; OE on the "
                 "pin-compatible XO)", "VCXO oscillator", 13.97, -13.97)
    out += [f"\t\t(symbol {q(name + '_0_1')}", rect(-7.62, 7.62, 7.62, -7.62), "\t\t)",
            f"\t\t(symbol {q(name + '_1_1')}",
            pin_line("input", -10.16, 0, 0, "Vc", "1"),
            pin_line("power_in", 0, -10.16, 90, "GND", "2"),
            pin_line("output", 10.16, 0, 180, "OUT", "3"),
            pin_line("power_in", 0, 10.16, 270, "VDD", "4"),
            "\t\t)", "\t\t(embedded_fonts no)", "\t)"]
    return "\n".join(out)


def write_symbols():
    ecp5, n = ecp5_symbol()
    rp, nrp = rp_symbol()
    text = ("(kicad_symbol_lib\n\t(version 20241209)\n\t(generator \"studio_amp_lib_E\")\n"
            "\t(generator_version \"9.0\")\n" + ecp5 + "\n" + rp + "\n" + lan_symbol() + "\n" + vcxo_symbol()
            + "\n)\n")
    SYM.write_text(text)
    return n


# ------------------------------------------------------------------ footprints
def bga_footprint():
    src = KICAD_FP / "Package_BGA.pretty/BGA-256_14.0x14.0mm_Layout16x16_P0.8mm_Ball0.45mm_Pad0.32mm_NSMD.kicad_mod"
    t = src.read_text()
    name = "Lattice_caBGA-256_14x14mm_Layout16x16_P0.8mm"
    t = re.sub(r'^\(footprint "[^"]+"', f'(footprint "{name}"', t)
    t = re.sub(r'\(descr "[^"]*"\)',
               '(descr "Lattice caBGA-256 (ECP5 BG256), 14.0x14.0 mm, 16x16, 0.8 mm pitch, 0.45 mm ball. '
               'Land 0.40 mm NSMD, mask +0.075 mm as KiCad Lattice_caBGA-381 (same ball and pitch). '
               'Grid from KiCad BGA-256_14.0x14.0mm_Layout16x16_P0.8mm; package DS-02053 section 94")', t)
    t = t.replace("(size 0.32 0.32)", "(size 0.4 0.4)")
    t = re.sub(r"\(solder_mask_margin [0-9.]+\)", "(solder_mask_margin 0.075)", t)
    t = re.sub(r'\(model "[^"]*"', '(model "${KICAD9_3DMODEL_DIR}/Package_BGA.3dshapes/'
               'BGA-256_14.0x14.0mm_Layout16x16_P0.8mm_Ball0.45mm_Pad0.32mm_NSMD.step"', t)
    pads = re.findall(r'\(pad "([A-Z]+\d+)" smd circle\s+\(at ([-0-9.]+) ([-0-9.]+)\)\s+\(size ([0-9.]+)', t)
    names = {p[0] for p in pads}
    balls = set(e_pins.ecp5_balls())
    assert names == balls, f"BGA pads vs CSV balls differ: {sorted(names ^ balls)}"
    for nm, x, y, s in pads:          # A1 top-left, rows A..T down, columns 1..16 right, 0.8 mm
        r, c = e_pins.ROWS.index(nm[0]), int(nm[1:]) - 1
        assert abs(float(x) - (-6 + 0.8 * c)) < 1e-6 and abs(float(y) - (-6 + 0.8 * r)) < 1e-6, nm
        assert s == "0.4", nm
    (PRETTY / f"{name}.kicad_mod").write_text(t)
    return len(pads)


def osc_footprint():
    name = "Oscillator_SMD_3225-4Pin_YXC_SX3V"
    u = lambda: str(uuid.uuid4())
    pads = [("1", -1.05, 0.95), ("2", 1.05, 0.95), ("3", 1.05, -0.95), ("4", -1.05, -0.95)]
    L = [f'(footprint "{name}"', '\t(version 20241229)', '\t(generator "studio_amp_lib_E")',
         '\t(generator_version "9.0")', '\t(layer "F.Cu")',
         '\t(descr "3.2x2.5 mm 4-pad oscillator land shared by SCTF SX3V (VCXO, pads 1.2x0.95 on 2.2x1.75) '
         'and YXC YSO110TR OT2EL (XO, recommended 1.3x1.2 pads, 0.8/0.7 mm gaps). Pin 1 Vc/OE bottom left '
         '(top view), 2 GND, 3 OUT, 4 VDD")',
         '\t(tags "oscillator VCXO 3225")',
         f'\t(property "Reference" "REF**" (at 0 -2.4 0) (layer "F.SilkS") (uuid "{u()}") '
         '(effects (font (size 1 1) (thickness 0.15))))',
         f'\t(property "Value" "{name}" (at 0 2.5 0) (layer "F.Fab") (uuid "{u()}") '
         '(effects (font (size 1 1) (thickness 0.15))))',
         f'\t(property "Footprint" "" (at 0 0 0) (layer "F.Fab") (hide yes) (uuid "{u()}") '
         '(effects (font (size 1.27 1.27) (thickness 0.15))))',
         f'\t(property "Datasheet" "" (at 0 0 0) (layer "F.Fab") (hide yes) (uuid "{u()}") '
         '(effects (font (size 1.27 1.27) (thickness 0.15))))',
         f'\t(property "Description" "" (at 0 0 0) (layer "F.Fab") (hide yes) (uuid "{u()}") '
         '(effects (font (size 1.27 1.27) (thickness 0.15))))',
         '\t(attr smd)']

    def line(x0, y0, x1, y1, layer, w):
        L.append(f'\t(fp_line (start {f(x0)} {f(y0)}) (end {f(x1)} {f(y1)}) (stroke (width {w}) (type solid)) '
                 f'(layer "{layer}") (uuid "{u()}"))')
    # fab body 3.2 x 2.5 with a pin-1 chamfer
    for a, b_ in [((-1.6, -1.25), (1.6, -1.25)), ((1.6, -1.25), (1.6, 1.25)), ((1.6, 1.25), (-1.1, 1.25)),
                  ((-1.1, 1.25), (-1.6, 0.75)), ((-1.6, 0.75), (-1.6, -1.25))]:
        line(*a, *b_, "F.Fab", 0.1)
    # courtyard 0.25 mm around the pads/body
    cx, cy = 1.95, 1.8
    for a, b_ in [((-cx, -cy), (cx, -cy)), ((cx, -cy), (cx, cy)), ((cx, cy), (-cx, cy)), ((-cx, cy), (-cx, -cy))]:
        line(*a, *b_, "F.CrtYd", 0.05)
    # silk: short bars between the pads plus a pin-1 mark
    line(-0.25, -1.4, 0.25, -1.4, "F.SilkS", 0.12)
    line(-0.25, 1.4, 0.25, 1.4, "F.SilkS", 0.12)
    line(-1.85, 0.2, -1.85, 1.6, "F.SilkS", 0.12)
    L.append(f'\t(fp_text user "${{REFERENCE}}" (at 0 0 0) (layer "F.Fab") (uuid "{u()}") '
             '(effects (font (size 0.6 0.6) (thickness 0.09))))')
    for n, x, y in pads:
        L.append(f'\t(pad "{n}" smd roundrect (at {f(x)} {f(y)}) (size 1.3 1.2) (layers "F.Cu" "F.Mask" "F.Paste") '
                 f'(roundrect_rratio 0.2) (uuid "{u()}"))')
    # both parts' pads must lie inside these lands
    for n, x, y in pads:
        sx, sy = math.copysign(1.1, x), math.copysign(0.875, y)
        assert abs(sx - x) + 0.6 <= 0.65 + 1e-9 and abs(sy - y) + 0.475 <= 0.6 + 1e-9, n
    L.append('\t(embedded_fonts no)')
    L.append(")")
    (PRETTY / f"{name}.kicad_mod").write_text("\n".join(L) + "\n")


if __name__ == "__main__":
    n = write_symbols()
    pads = bga_footprint()
    osc_footprint()
    print(f"wrote {SYM.name}: {ECP5} with {n} balls (CSV: {len(e_pins.ecp5_balls())}), VCXO_3225; "
          f"BGA footprint {pads} pads; oscillator land")
