"""mcu.py -- block E sheet "mcu": RP2350B with the Raspberry Pi reference regulator and decoupling,
W25Q128 boot flash, 12 MHz crystal, BOOTSEL and RUN, USB series resistors, the PIO link and SSPI
configuration pins to the FPGA, ILIM_SEL, IBUS_SENSE and the knob ADCs (references 700-799, A3).

Sources: design/parts/E-mcu-rp2350b.md, E-mcu-passives.md (Raspberry Pi RP2350B Minimal board values),
E-xtal-12mhz.md, E-flash-w25q128.md, E-pinmap.md (net per pin, read by e_pins.py), chips/rp2350.md.
Run from the repo root:  python3 hw/satellite/a/gen/mcu.py
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import e_pins  # noqa: E402
import hier  # noqa: E402
import lib_E  # noqa: E402
from e_parts import SHAPE, Drawer, fields  # noqa: E402
from kicad_write import symbol_pins  # noqa: E402

G = 2.54
sch = hier.SubSheet("mcu", paper="A3", comments=[
    "Block E. Audits: design/parts/E-mcu-rp2350b.md, E-mcu-passives.md, E-xtal-12mhz.md, E-flash-w25q128.md",
    "Regulator, decoupling, crystal and flash copied from the Raspberry Pi RP2350B Minimal board"])
d = Drawer(sch, 700)
PM = e_pins.rp_nets()
LIB_ID = "studio_E:RP2350B"
SYM = sch.libs.get(LIB_ID)
REF = d.ref("U")          # U701
UF = fields("RP2350B", "Raspberry Pi", "C42415655")
DECOR = lib_E.RP_DECOR


def T(s, at, size=1.27):
    sch.text(s, at, size=size)


def unit(u, at, rlab=None):
    return sch.symbol(LIB_ID, REF, "RP2350B", at, unit=u, footprint=lib_E.RP_FP, fields=UF,
                      ref_at=(at[0], at[1] - 10.16), value_at=(at[0], at[1] - 7.62), justify="")


# ---------------------------------------------------------------- power unit
PX, PY = 22.86, 55.88
pw = unit(4, (PX, PY))
pw_ref = (PX, PY + 22.86)
P = {n: pw.pin(n) for n in symbol_pins(SYM, 4)}
YR = P["61"][1] - 15.24          # rail height for every group


def up_to_rail(n):
    sch.wire(P[n], (P[n][0], YR))
    return P[n][0]


def flag(at):
    sch.power("power:PWR_FLAG", at)


# VREG_AVDD: +3V3 -> 33R -> VREG_AVDD, CFILT 4u7 (guide 2.1: 33 R / 4.7 uF, ~1 kHz)
x = up_to_rail("61")
d.rail("+3V3", (x - 15.24, YR))
r, a, b = d.series("33R", (x - 7.62, YR))
sch.wire((x - 15.24, YR), a)
sch.wire(b, (x + 5.08, YR))
d.cap_down("4u7", (x + 5.08, YR), decouples=f"{REF}.61")
sch.label("VREG_AVDD", (x + 1.27, YR))
flag((x + 12.7, YR))
sch.wire((x + 5.08, YR), (x + 12.7, YR))
# VREG_VIN: +3V3, CIN 4u7 (0402 small pads, as the reference)
x = up_to_rail("64")
d.rail("+3V3", (x - 7.62, YR))
sch.wire((x - 7.62, YR), (x + 5.08, YR))
d.cap_down("4u7s", (x + 5.08, YR), decouples=f"{REF}.64")
# VREG_LX -> L (polarity-marked; pad 2, the LX pad, on the right in the reference) -> DVDD_RP
x_lx = P["63"][0]
x_fb = P["65"][0]
yl = YR - 7.62
sch.wire(P["63"], (x_lx, yl))
L = sch.symbol("Device:L", d.ref("L"), "3.3u", ((x_lx + x_fb) / 2, yl), rot=270,
               footprint="studio_E:L_Abracon_AOTA-B201610S3R3_pol",
               fields=fields("AOTA-B201610S3R3-101-T", "Abracon", "C42411119",
                             Note="polarity marked: dot (pad 1) to DVDD_RP, pad 2 to VREG_LX, reference rotation"),
               ref_at=((x_lx + x_fb) / 2, yl - 4.83), value_at=((x_lx + x_fb) / 2, yl + 3.05), justify="")
assert L.pin("2")[0] < L.pin("1")[0], "L pin 2 (LX) must face VREG_LX"
sch.wire((x_lx, yl), L.pin("2"))
sch.wire(L.pin("1"), (x_fb, yl), (x_fb, YR))
# FB + DVDD x3 on the regulator output rail DVDD_RP (RP2350 internal 1.1 V, not the FPGA's +1V1)
up_to_rail("65")
last = x_fb
d.cap_down("4u7s", (x_fb + 5.08, YR), decouples=f"{REF}.65")      # COUT
for n in ("10", "32", "51"):
    xx = up_to_rail(n)
    d.cap_down("100n", (xx + 5.08, YR), decouples=f"{REF}.{n}")
    last = xx + 5.08
d.cap_down("4u7", (last + 10.16, YR), decouples=f"{REF}.51")      # second 4u7, DVDD opposite the regulator
last += 10.16
sch.wire((x_fb, YR), (last, YR))
sch.label("DVDD_RP", (x_fb + 1.27, YR))
flag((x_fb, yl))
# IOVDD x8, QSPI_IOVDD, USB_OTP_VDD on +3V3: 10u bulk + 100n per IOVDD; 68/69 share one 100n
io = ["5", "15", "24", "29", "41", "50", "60", "76", "69", "68"]
x0 = P[io[0]][0]
d.rail("+3V3", (x0 - 17.78, YR))
d.cap_down("10u", (x0 - 10.16, YR), decouples=f"{REF}.5")
for n in io:
    xx = up_to_rail(n)
    if n != "68":
        d.cap_down("100n", (xx + 5.08, YR), decouples=f"{REF}.{n}")
sch.wire((x0 - 17.78, YR), (P["69"][0] + 5.08, YR))
sch.wire((P["69"][0] + 5.08, YR), (P["68"][0], YR))
# ADC_AVDD: +3V3 -> 10R -> ADC_AVDD (4u7 + 100n at pin 59); also KNOB_REF's source on the io sheet
x = up_to_rail("59")
d.rail("+3V3", (x - 22.86, YR))
r, a, b = d.series("10R", (x - 15.24, YR))
sch.wire((x - 22.86, YR), a)
d.cap_down("4u7", (x - 7.62, YR), decouples=f"{REF}.59")
d.cap_down("100n", (x + 5.08, YR), decouples=f"{REF}.59")
sch.wire(b, (x + 12.7, YR))
d.rail("ADC_AVDD", (x + 12.7, YR))
flag((x + 25.4, YR))
sch.wire((x + 12.7, YR), (x + 25.4, YR))
# grounds
d.gnd(pw.pin("62"))
d.gnd(pw.pin("81"))
T("VREG_PGND (62) joins GND at ONE point,\ntwo adjacent vias (RP2350 6.3.8.1).", (pw.pin("62")[0] - 50.8, pw.pin("62")[1] + 2.54))
T("Core regulator, RP2350 6.3.8 / Minimal board: CIN, L and COUT on the chip's side; copy the reference corner\n"
  "(chips/rp2350.md). L: AOTA-B201610S3R3 3.3u, dot to DVDD_RP, reference rotation (orientation changes Vout).\n"
  "DVDD_RP is the RP2350's own 1.1 V (internal regulator); it is not the FPGA's +1V1.",
  (PX, 17.78))


# ---------------------------------------------------------------- GPIO units
def draw_gpio(u, at):
    part = unit(u, at)
    pins = symbol_pins(SYM, u)
    for n in pins:
        p = part.pin(n)
        side = "L" if p[0] < at[0] else "R"
        s = -1 if side == "L" else 1
        name, net, dr, note = PM[n]
        if net.startswith("SPARE"):
            sch.no_connect(p)
            continue
        dec = DECOR.get(net, {})
        X = lambda dx: (round(p[0] + s * dx, 4), p[1])
        cur, off = p, 5.08
        if dec.get("pd"):
            d.cap_down(dec["pd"], X(7.62))
            off = 12.7
        if dec.get("ser"):
            r, a, b = d.series(dec["ser"], X(10.16))
            near, far = (a, b) if s > 0 else (b, a)
            sch.wire(cur, near)
            cur, off = far, 20.32
        sch.wire(cur, X(off))
        d.glabel(net, X(off), side, SHAPE[dr])
    return part


g1 = draw_gpio(1, (210.82, 152.4))
g2 = draw_gpio(2, (320.04, 152.4))
T("PIO link to the ECP5 (E-link.md): 8-bit, 37.5 MHz,\n22R series at each driver is in the FPGA design rule;\n"
  "LINK_* tri-stated while the FPGA is configured.\nENC_*: encoder header on the io sheet (block G pulls).",
  (190.5, 205.74))
T("SSPI configuration (SPI1): FPGA_CCLK 33R at the RP2350,\npad set to 8 mA (1k pull-up at the FPGA).\n"
  "Reads <= 18.75 MHz, bitstream writes 37.5 MHz.\nIBUS_SENSE: 100n at the pin (B's 67k source, 24 Hz).\n"
  "ILIM_SEL0/1, VDRV_EN: reset Hi-Z, pulled down\nat blocks B and C (safe state).", (297.18, 205.74))


# ---------------------------------------------------------------- system unit
SX, SY = 78.74, 152.4
sy = unit(3, (SX, SY))
pin = sy.pin
# SWD -> debug header (io sheet; G fits the 33R)
for n, net, shp in (("33", "SWCLK", "input"), ("34", "SWDIO", "bidirectional")):
    sch.wire(pin(n), (pin(n)[0] - 5.08, pin(n)[1]))
    d.glabel(net, (pin(n)[0] - 5.08, pin(n)[1]), "L", shp)
# crystal: XIN direct, XOUT through 1k; 15p load caps (guide 4: ABM8-272-T3 with these exact values)
xin, xout = pin("30"), pin("31")
xc = xin[0] - 22.86
sch.wire(xin, (xc, xin[1]))
r, a, b = d.series("1k", (xout[0] - 7.62, xout[1]))
sch.wire(xout, b)
sch.wire(a, (xc, xout[1]))
Y = sch.symbol("Device:Crystal_GND24", d.ref("Y"), "12MHz", (xc, (xin[1] + xout[1]) / 2), rot=90,
               footprint="Crystal:Crystal_SMD_3225-4Pin_3.2x2.5mm",
               fields=fields("ABM8-272-T3", "Abracon", "C20625731"),
               ref_at=(xc + 12.7, (xin[1] + xout[1]) / 2 - 1.27),
               value_at=(xc + 12.7, (xin[1] + xout[1]) / 2 + 1.27), justify="")
top, bot = sorted([Y.pin("1"), Y.pin("3")], key=lambda p: p[1])
sch.wire((xc, xin[1]), top)
sch.wire(bot, (xc, xout[1]))
g = Y.pin("2")
gx = g[0]
if abs(gx - xc) > 0.01:          # case pins to GND
    sch.wire(g, (gx, g[1] + 5.08))
    d.gnd((gx, g[1] + 5.08))
for yy in (xin[1], xout[1]):
    sch.wire((xc, yy), (xc - 10.16, yy))
    d.cap_down("15p", (xc - 10.16, yy))
T("ABM8-272-T3 12 MHz with 15p + 15p and 1k\nat XOUT: Raspberry Pi's tuned network\n(guide 4); traces < 5 mm.",
  (xc - 22.86, xout[1] + 40.64))
# RUN: 10k pull-up, reset button to GND, to the debug header
run = pin("35")
j = (run[0] - 7.62, run[1])
d.pullup("10k", j, text_left=False)
sch.wire(run, (run[0] - 15.24, run[1]))
sw = sch.symbol("Switch:SW_Push", d.ref("SW"), "RUN", (run[0] - 15.24, run[1] + 5.08), rot=90,
                footprint="Button_Switch_SMD:SW_Push_1P1T_XKB_TS-1187A",
                fields=fields("TS-1187A-B-A-B", "XKB Connection", "C318884"),
                ref_at=(run[0] - 22.86, run[1] + 3.81), value_at=(run[0] - 22.86, run[1] + 6.35), justify="")
d.gnd(sw.pin("2") if sw.pin("2")[1] > sw.pin("1")[1] else sw.pin("1"))
sch.wire((run[0] - 15.24, run[1]), (run[0] - 22.86, run[1]))
d.glabel("RUN", (run[0] - 22.86, run[1]), "L", "bidirectional")
# QSPI flash, pins in the same order as the RP2350's: straight wires
ss = pin("75")
FX = ss[0] + 53.34
fl = sch.symbol("Memory_Flash:W25Q128JVS", d.ref("U"), "W25Q128JVSIQ", (FX, ss[1] + 7.62),
                footprint="Package_SO:SOIC-8_5.3x5.3mm_P1.27mm", fields=fields("W25Q128JVSIQ", "Winbond", "C97521"),
                ref_at=(FX + 10.16, ss[1] + 15.24), value_at=(FX + 10.16, ss[1] + 17.78))
for rp, fp in (("75", "1"), ("71", "6"), ("72", "5"), ("74", "2"), ("73", "3"), ("70", "7")):
    assert abs(pin(rp)[1] - fl.pin(fp)[1]) < 0.01, (rp, fp)
    sch.wire(pin(rp), fl.pin(fp))
# QSPI_SS: 10k pull-up position (DNP, as the reference) and 1k to the BOOTSEL button (guide 3.1)
d.pullup("10k", (ss[0] + 7.62, ss[1]), dnp=True, note="DNP as the reference (R1); footprint kept")
jb = (ss[0] + 20.32, ss[1])
rb = d.part("1k", (jb[0], jb[1] - 3.81))
bs = sch.symbol("Switch:SW_Push", d.ref("SW"), "BOOTSEL", (jb[0] + 7.62, jb[1] - 7.62),
                footprint="Button_Switch_SMD:SW_Push_1P1T_XKB_TS-1187A",
                fields=fields("TS-1187A-B-A-B", "XKB Connection", "C318884"),
                ref_at=(jb[0] + 7.62, jb[1] - 12.7), value_at=(jb[0] + 7.62, jb[1] - 10.16), justify="")
sch.wire((jb[0], jb[1] - 7.62), bs.pin("1"))
sch.wire(bs.pin("2"), (jb[0] + 17.78, jb[1] - 7.62))
d.gnd((jb[0] + 17.78, jb[1] - 7.62))
fv = fl.pin("8")
sch.wire(fv, (fv[0], fv[1] - 5.08))
d.rail("+3V3", (fv[0], fv[1] - 5.08))
sch.wire((fv[0], fv[1] - 5.08), (fv[0] + 12.7, fv[1] - 5.08))
d.cap_down("100n", (fv[0] + 12.7, fv[1] - 5.08), decouples=f"{fl.ref}.8")
d.gnd(fl.pin("4"))
T("Boot flash W25Q128JVSIQ (16 MB). QSPI <= 15 mm,\nnothing else between flash and RP2350.\n"
  "QSPI_SS: 10k pull-up footprint DNP (reference R1);\n1k to BOOTSEL (reference R6).", (FX - 2.54, ss[1] + 30.48))
# USB: 27R at the chip, D+/D- to the USB-C on the io sheet
for n, net in (("66", "USB_DM"), ("67", "USB_DP")):
    p = pin(n)
    r, a, b = d.series("27R", (p[0] + 10.16, p[1]))
    sch.wire(p, a)
    sch.wire(b, (p[0] + 20.32, p[1]))
    d.glabel(net, (p[0] + 20.32, p[1]), "R", "bidirectional")
T("USB 2.0 FS: 27R at the chip (guide 5.1);\nconnector and ESD on the io sheet.", (pin("67")[0] + 2.54, pin("67")[1] + 7.62))

sch.save()
print("wrote", sch.file)
