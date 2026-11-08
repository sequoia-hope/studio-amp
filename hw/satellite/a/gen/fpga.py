"""fpga.py -- block E sheet "fpga": ECP5 LFE5U-25F-7BG256I, its decoupling, sysCONFIG straps,
JTAG pulls and every assigned ball as a labelled net (references 800-899, A2).

Sources: design/parts/E-pinmap.md (net per ball, read by e_pins.py), E-fpga-ecp5.md,
E-fpga-ecp5-passives.md (values), TN-02038 Tab 3.1 (decoupling), TN-02038 Tab 6.1-6.2 and
TN-02039 Tab 4.5 (config/JTAG pulls), DS-02012 section 3.6 (hot-socket series resistors).
Run from the repo root:  python3 hw/satellite/a/gen/fpga.py
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import e_pins  # noqa: E402
import hier  # noqa: E402
import lib_E  # noqa: E402
from e_parts import SHAPE, Drawer  # noqa: E402
from kicad_write import symbol_pins  # noqa: E402

G = 2.54
sch = hier.SubSheet("fpga", paper="A2", comments=[
    "Block E. Audits: design/parts/E-fpga-ecp5.md, E-fpga-ecp5-passives.md; nets: E-pinmap.md",
    "ECP5 LFE5U-25F-7BG256I, slave SPI from the RP2350 (CFGMDN 001). All VCCIO 3.3 V."])
d = Drawer(sch, 800)
NETS = e_pins.fpga_nets()
DECOR = e_pins.FPGA_DECOR
LIB_ID = "studio_E:LFE5U-25F-7BG256I"
FIELDS = {"MPN": "LFE5U-25F-7BG256I", "Manufacturer": "Lattice", "LCSC": "C1550762"}
FP = lib_E.BGA_FP
REF = d.ref("U")          # U801
SYM = sch.libs.get(LIB_ID)


def T(s, at, size=1.27):
    sch.text(s, at, size=size)


# ---------------------------------------------------------------- bank units
def side_offsets(unit):
    """Label distance from the pin end for each side, from what the side carries."""
    pins = symbol_pins(SYM, unit)
    off = {}
    for side in ("L", "R"):
        o = 5.08
        for ball, p in pins.items():
            if (p["x"] < 0) != (side == "L") or ball not in NETS:
                continue
            dec = DECOR.get(NETS[ball][0], {})
            if dec.get("pu") or dec.get("pd"):
                o = max(o, 15.24)
            if dec.get("ser"):
                o = max(o, 25.4)
            if dec.get("pu_far"):
                o = max(o, 30.48)
        off[side] = o
    return off


def draw_bank(unit, at):
    u = sch.symbol(LIB_ID, REF, "LFE5U-25F-7BG256I", at, unit=unit, footprint=FP, fields=FIELDS,
                   ref_at=(at[0], at[1] - 10.16), value_at=(at[0], at[1] - 7.62), justify="")
    off = side_offsets(unit)
    for ball in u.pins():
        p = u.pin(ball)
        side = "L" if p[0] < at[0] else "R"
        s = -1 if side == "L" else 1
        if ball not in NETS:
            sch.no_connect(p)
            continue
        net, dr, blk, note = NETS[ball]
        dec = DECOR.get(net, {})
        y = p[1]
        X = lambda dx: (round(p[0] + s * dx, 4), y)
        if dec.get("gnd"):
            sch.wire(p, X(5.08))
            d.gnd(X(5.08))
            continue
        cur = p
        if dec.get("pu"):
            d.pullup(dec["pu"], X(7.62), text_left=side == "L")
        if dec.get("pd"):
            d.pulldown(dec["pd"], X(7.62), text_left=side == "L")
        if dec.get("local"):
            sch.wire(p, X(7.62))
            continue
        if dec.get("ser"):
            r, a, b = d.series(dec["ser"], X(15.24))
            near, far = (a, b) if s > 0 else (b, a)
            sch.wire(cur, near)
            cur = far
        if dec.get("pu_far"):
            d.pullup(dec["pu_far"], X(22.86), text_left=side == "L")
        end = X(off[side])
        sch.wire(cur, end)
        if net == "CLK_AUX":
            sch.symbol("Connector:TestPoint", d.ref("TP"), "CLK_AUX", end, footprint="TestPoint:TestPoint_Pad_D1.0mm",
                       in_bom=False, ref_at=(end[0] - 2.54, end[1] - 3.81), value_at=(end[0] - 2.54, end[1] - 6.35),
                       justify="right")
            continue
        d.glabel(net, end, side, SHAPE[dr])
    return u


def bank_width(unit):
    pins = symbol_pins(SYM, unit)
    xs = [p["x"] for p in pins.values()]
    off = side_offsets(unit)
    def textw(side):
        names = [NETS[b][0] for b, p in pins.items() if b in NETS and (p["x"] < 0) == (side == "L")]
        return max([len(n) * 1.05 + 4 for n in names] + [0])
    left = -min(xs) + off["L"] + textw("L")
    right = max(xs) + off["R"] + textw("R")
    return left, right


POS = {}


def place_row(units, y, x0=20.32, gap=10.16):
    x = x0
    for unit in units:
        lw, rw = bank_width(unit)
        ux = round((x + lw) / G) * G
        draw_bank(unit, (ux, y))
        bottom = y - min(p["y"] for p in symbol_pins(SYM, unit).values()) + 2.54
        POS[unit] = (ux - lw, ux, ux + rw, bottom)
        x = ux + rw + gap


def note(unit, s, dy=3.81):
    """Multi-line text is centred on its anchor: put the block's top dy below the unit."""
    x0, ux, x1, bottom = POS[unit]
    n = s.count("\n") + 1
    T(s, (x0 + 2.54, round(bottom + dy + n * 1.016, 2)))


# ---------------------------------------------------------------- power units
def draw_power(unit, at, bulk):
    """bulk: group name -> list of cap keys (left of the group's first ball)."""
    u = sch.symbol(LIB_ID, REF, "LFE5U-25F-7BG256I", at, unit=unit, footprint=FP, fields=FIELDS,
                   ref_at=(at[0], at[1] + 22.86), value_at=(at[0], at[1] + 25.4), justify="left")
    pins = symbol_pins(SYM, unit)
    top = sorted(((b, p) for b, p in pins.items() if p["angle"] == 270), key=lambda t: t[1]["x"])
    groups = []
    for ball, p in top:
        name = p["name"]
        if not groups or groups[-1][0] != name:
            groups.append((name, []))
        groups[-1][1].append(ball)
    for name, balls in groups:
        pts = [u.pin(b) for b in balls]
        ytop = pts[0][1]
        yr = ytop - 15.24
        xf = pts[0][0]
        xps = xf - lib_E.LEAD[lib_E.group_of(name)]
        rail_start = xps
        if name == "VCCAUX":
            d.rail("+2V5", (xps, yr))
            fb = d.part("FB121", (xps + 7.62, yr), rot=90, justify="",
                        ref_at=(xps + 7.62, yr + 3.05), value_at=(xps + 7.62, yr + 5.59))
            sch.wire((xps, yr), fb.pin("1"))
            rail_start = fb.pin("2")[0]
            sch.label("VCCAUX", (rail_start + 1.27, yr))

            caps_x = [xps + 15.24]
        else:
            d.rail("+1V1" if name == "VCC" else "+3V3", (xps, yr))
            caps_x = [xps + 5.08 + 7.62 * i for i in range(len(bulk[name]))]
        for cx, key in zip(caps_x, bulk[name]):
            d.cap_down(key, (cx, yr), decouples=f"{REF}.{balls[0]}")
        last = xf
        for b_, p in zip(balls, pts):
            sch.wire(p, (p[0], yr))
            d.cap_down("100n", (p[0] + 5.08, yr), decouples=f"{REF}.{b_}")
            last = p[0] + 5.08
        if name == "VCCAUX":           # PWR_FLAG on the bead's output, past the last cap
            last += 7.62
            sch.power("power:PWR_FLAG", (last, yr))
        sch.wire((rail_start, yr), (last, yr))
    for b_, p in pins.items():
        if p["angle"] == 90:
            d.gnd(u.pin(b_))
    return u


# ---------------------------------------------------------------- the page
TOP = 48.26
draw_power(8, (20.32, TOP), {"VCC": ["10u", "10u", "10u"], "VCCAUX": ["10u"]})
draw_power(9, (195.58, TOP), {f"VCCIO{n}": ["22u" if n == "6" else "10u"] for n in "0123678"})
T("CORE: VCC +1V1 (1.045-1.155 V), 3 x 10u + 100n per ball; VCCAUX +2V5 through a 120 R bead, "
  "10u + 100n per ball (TN-02038 Tab 3.1).\n"
  "I/O: every VCCIO on +3V3 (max 3.465 V), 10u per bank (22u on bank 6, the PWM bank) + 100n per ball. "
  "Layout: 100n under the ball field between the dog-bone vias; bulk just outside the package.",
  (20.32, 17.78))

place_row([1, 2, 3, 4], 101.6)
place_row([6, 5, 7], 228.6, x0=20.32, gap=12.7)

note(1, "Status from always-powered parts (A, B, C):\n1k in series (hot socket, DS-02012 3.6).\n"
        "POE_LOSS_N: block B open drain, 4k7 pull-up\non the net (pre-config sweep, E-pinmap.md).\n"
        "ACF_PULSE: 4k7 series (B's 74LVC2G08).")
note(2, "RMII to the LAN8720A (ethernet sheet): REFCLK on\nPCLKT1_0 (C8). MODE straps (RXD0/1, CRS_DV),\n"
        "MDIO, nRST and nINT pulls sit at the PHY.\nLPF: PULLMODE=UP on A11, A12, B11.")
note(3, "Display, LED and Qwiic power (block G/C).\nAlways-driven inputs: 1k series,\n"
        "pair partners K15, D14, F14 left open.\nB15 (S0_IN) unused.")
note(4, "Audio (block F) and PIO link control (RP2350).\nMADC_DOUT, PDM_DAT: 330R; HP_FAULT_N, HP_DET: 1k;\n"
        "partners L15, P14, P12, K12 left open.\nLINK_CLK on PCLKT3_0 (M16).")
note(6, "CLK_AUX (K1, PCLKT7_0): spare clock input\non a test pad (external low-jitter clock option).\n"
        "DC_W_n / DC_T_n: 1k series, partners J2 / H2 open.")
note(5, "Power stage (block D). PWM_* from ODDRX2F at 589.824 Mb/s\n(PLL x12 from VCXO_CLK on P6, LLC_GPLL0T_IN; P5 open).\n"
        "FAULT_*: always driven, 330R, partners L2 / M2 open.\nT3 open: it pairs with PWM_T_B (R4).\n"
        "ADC chip selects: 4k7 pull-ups keep the ADCs\ndeselected through configuration.")
note(7, "sysCONFIG slave SPI from the RP2350 (SPI1, 37.5 MHz):\nCFGMDN[2:0] = 001: CFG0 4k7 up, CFG1/CFG2 to GND.\n"
        "CCLK 1k pull-up to VCCIO8 (TN-02038 Tab 6.2);\n33R series at the RP2350 (mcu sheet).\n"
        "PROGRAMN, INITN, DONE, SN, HOLDN: 4k7 up.\nJTAG: TDI, TMS, TDO 4k7 up, TCK 4k7 down\n"
        "(TN-02038 Tab 6.1); header on the io sheet.\nLINK_D0-7 / LINK_IRQ: PIO link (E-link.md).")

sch.save()
print("wrote", sch.file)
