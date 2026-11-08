"""ethernet.py -- block E sheet "ethernet": LAN8720AI PHY with straps and MDI terminations, the 50 MHz
RMII reference clock, and the 24.576 MHz audio/PWM VCXO with its tune filter and the shared XO land
(references 900-999, A3).

Sources: design/parts/E-phy-lan8720.md, E-phy-passives.md, E-clk-rmii-50mhz.md, E-clk-audio-vcxo.md,
E-fpga-ecp5-passives.md (MODE strap pull-ups), A-poe-magjack.md (J101 pin map, block A's net names).
Run from the repo root:  python3 hw/satellite/a/gen/ethernet.py
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import hier  # noqa: E402
import lib_E  # noqa: E402
from e_parts import Drawer, fields  # noqa: E402

G = 2.54
sch = hier.SubSheet("ethernet", paper="A3", comments=[
    "Block E. Audits: design/parts/E-phy-lan8720.md, E-phy-passives.md, E-clk-rmii-50mhz.md, E-clk-audio-vcxo.md",
    "LAN8720AI in REF_CLK-in mode (nINTSEL = 1), MODE 111, PHYAD 0"])
d = Drawer(sch, 900)


def T(s, at, size=1.27):
    sch.text(s, at, size=size)


def flag(at):
    sch.power("power:PWR_FLAG", at)


# ---------------------------------------------------------------- PHY
OX, OY = 215.9, 101.6
phy = sch.symbol("studio_E:LAN8720AI", d.ref("U"), "LAN8720AI", (OX, OY), footprint=lib_E.LAN_FP,
                 fields=fields("LAN8720AI-CP-TR", "Microchip", "C17146"),
                 ref_at=(OX + 5.08, OY + 116.84), value_at=(OX + 5.08, OY + 119.38))
U = phy.ref
pin = phy.pin

# left side: RMII and management to the FPGA (bank 1), with the straps at the pins
LEFT = {  # pin: (net, label shape seen from this sheet, pull, value)
    "8": ("RMII_RXD0", "output", "pu", "4k7"), "7": ("RMII_RXD1", "output", "pu", "4k7"),
    "11": ("RMII_CRSDV", "output", "pu", "4k7"), "17": ("RMII_TXD0", "input", None, None),
    "18": ("RMII_TXD1", "input", None, None), "16": ("RMII_TXEN", "input", "pd", "10k"),
    "13": ("PHY_MDC", "input", None, None), "12": ("PHY_MDIO", "bidirectional", "pu", "1k5"),
    "14": ("PHY_NINT", "output", "pu", "10k"), "15": ("PHY_NRST", "input", "pd", "10k"),
}
for n, (net, shape, pull, val) in LEFT.items():
    p = pin(n)
    j = (p[0] - 7.62, p[1])
    if pull == "pu":
        d.pullup(val, j, text_left=True)
    elif pull == "pd":
        d.pulldown(val, j, text_left=True)
    end = (p[0] - 20.32, p[1])
    sch.wire(p, end)
    d.glabel(net, end, "L", shape)
# RXER/PHYAD0: unconnected in RMII (PHYAD0 = 0 by the internal pull-down), test pad only
p = pin("10")
sch.wire(p, (p[0] - 12.7, p[1]))
sch.symbol("Connector:TestPoint", d.ref("TP"), "RXER", (p[0] - 12.7, p[1]), rot=90,
           footprint="TestPoint:TestPoint_Pad_D1.0mm", in_bom=False,
           ref_at=(p[0] - 17.78, p[1] - 1.27), value_at=(p[0] - 17.78, p[1] + 1.27), justify="")
sch.no_connect(pin("4"))                       # XTAL2: open with an external clock (Tab 2-5)
T("Straps (sampled at nRST release):\nMODE[2:0] = 111 (all capable, auto-neg):\n"
  "4k7 pull-ups beat the ECP5's 150 uA\npre-config pull-down (review MAJOR-2);\n"
  "gateware: PULLMODE=UP, nRST released\n>= 25 ms after the rails.\nPHYAD0 = 0 (RXER internal pull-down).",
  (20.32, 132.08))
T("nRST 10k down: PHY held in reset\nuntil the FPGA design releases it.\nMDIO 1k5 up (tau 30 ns).",
  (20.32, 160.02))

# right side: MDI with 49.9R terminations to the analog island (Fig 7-5), LEDs, RBIAS
for n, net in (("21", "ETH_TXP"), ("20", "ETH_TXN"), ("23", "ETH_RXP"), ("22", "ETH_RXN")):
    p = pin(n)
    j = (p[0] + 7.62, p[1])
    d.pullup("49R9", j, rail="ETH_AVDD")
    sch.wire(p, (p[0] + 15.24, p[1]))
    d.glabel(net, (p[0] + 15.24, p[1]), "R", "bidirectional")
for n, net, shape in (("3", "ETH_LED_G_A", "output"), ("2", "ETH_LED_Y_K", "input")):
    p = pin(n)
    r, a, b = d.series("270R", (p[0] + 10.16, p[1]))
    sch.wire(p, a)
    sch.wire(b, (p[0] + 20.32, p[1]))
    d.glabel(net, (p[0] + 20.32, p[1]), "R", shape)
p = pin("24")
d.pulldown("12k1", (p[0] + 7.62, p[1]))
sch.wire(p, (p[0] + 7.62, p[1]))
# CBYPASS at each pair's 49.9R junction (Fig 7-5)
for n in ("20", "22"):
    p = pin(n)
    x, y = p[0] + 33.02, p[1] - 10.16
    d.rail("ETH_AVDD", (x, y))
    d.cap_down("100n", (x, y))
T("49R9 + 100n at the MDI pins, symmetric per pair;\npairs 100 R differential, no vias, over solid GND.\n"
  "J101 (poe_in): TX -> 11/10, RX -> 4/5.", (pin("21")[0] + 45.72, pin("21")[1] + 2.54))
T("LED1 (link, active high) -> green 20/19;\nLED2 (100M, active low) <- yellow 18/17 from VDD2A.\n"
  "Straps: REGOFF = 0 (internal 1.2 V on),\nnINTSEL = 1 (REF_CLK in). RBIAS 12k1 1%.",
  (pin("24")[0] + 45.72, pin("3")[1]))
d.gnd(pin("25"))

# top: VDDCR (internal 1.2 V core regulator out), VDDIO, VDD1A / VDD2A (analog island)
top = phy.pin("6")[1]
y1, y2 = top - 15.24, top - 30.48
x = pin("6")[0]
sch.wire(pin("6"), (x, y1), (x - 45.72, y1))
d.cap_down("1u", (x - 25.4, y1), decouples=f"{U}.6")
d.cap_down("470p", (x - 35.56, y1), decouples=f"{U}.6")
flag((x - 45.72, y1))
sch.label("VDDCR", (x - 22.86, y1))
x = pin("9")[0]
sch.wire(pin("9"), (x, y2), (x - 27.94, y2))
d.cap_down("100n", (x - 5.08, y2), decouples=f"{U}.9", text_left=True)
d.cap_down("4u7_0603", (x - 20.32, y2), decouples=f"{U}.9", text_left=True)
d.rail("+3V3", (x - 27.94, y2))
xa, xb = pin("19")[0], pin("1")[0]
sch.wire(pin("19"), (xa, y1))
sch.wire(pin("1"), (xb, y1))
d.cap_down("100n", (xa + 5.08, y1), decouples=f"{U}.19")
d.cap_down("100n", (xb + 5.08, y1), decouples=f"{U}.1")
d.cap_down("4u7_0603", (xb + 15.24, y1), decouples=f"{U}.1")
xr = xb + 22.86
d.rail("ETH_AVDD", (xr, y1))
flag((xb + 10.16, y1))
fb = d.part("FB221", (xr + 15.24, y1), rot=90, justify="",
            ref_at=(xr + 15.24, y1 + 3.05), value_at=(xr + 15.24, y1 + 5.59))
sch.wire((xa, y1), fb.pin("1") if fb.pin("1")[0] < fb.pin("2")[0] else fb.pin("2"))
far = max(fb.pin("1"), fb.pin("2"))
sch.wire(far, (far[0] + 5.08, y1))
d.rail("+3V3", (far[0] + 5.08, y1))
# the magjack's PHY-side centre taps (J101 12, 6) and the yellow LED anode (18) are ETH_AVDD too:
# block A puts ETH_AVDD power symbols on those pins. Their two bypass caps go at J101.
xc = xr + 2.54
for i, pinj in enumerate(("12", "6")):
    x = xc + 7.62 + 12.7 * i
    d.rail("ETH_AVDD", (x, y1 - 22.86))
    d.cap_down("100n", (x, y1 - 22.86))
T("CT bypass, place at\nJ101 pins 12 and 6", (xc + 2.54, y1 - 33.02))
T("ETH_AVDD: analog 3.3 V island (VDD1A, VDD2A, 4 x 49R9,\nmagnetics centre taps, yellow LED anode) behind a\n"
  "BLM18PG221 (<= 130 mA, 13 mV). VDDCR: internal 1.2 V\nregulator output, 1u || 470p at pin 6 (Tab 2-7).",
  (xc + 38.1, y1 - 22.86))

# ---------------------------------------------------------------- 50 MHz RMII reference clock
xt1 = pin("5")
XO = (xt1[0] - 55.88, xt1[1])
xo = sch.symbol("Oscillator:ASE-xxxMHz", d.ref("Y"), "50MHz", XO,
                footprint="studio_E:Oscillator_SMD_3225-4Pin_YXC_SX3V",
                fields=fields("OT2EL4C4JI-111OLP-50M", "YXC", "C5203552"),
                ref_at=(XO[0] + 2.54, XO[1] + 10.16), value_at=(XO[0] + 2.54, XO[1] + 12.7))
vdd, en, out = xo.pin("4"), xo.pin("1"), xo.pin("3")
yv = vdd[1] - 5.08
sch.wire(vdd, (vdd[0], yv))
sch.wire(en, (en[0] - 2.54, en[1]), (en[0] - 2.54, yv), (vdd[0] + 7.62, yv))
d.rail("+3V3", (en[0] - 2.54, yv))
d.cap_down("100n", (vdd[0] + 7.62, yv), decouples=f"{xo.ref}.4")
d.gnd(xo.pin("2"))
node = (out[0] + 5.08, out[1])
sch.wire(out, node)
r, a, b = d.series("33R", (node[0] + 10.16, node[1]))
sch.wire(node, a)
sch.wire(b, xt1)
sch.wire(node, (node[0], node[1] + 10.16))
r, a, b = d.series("33R", (node[0] + 10.16, node[1] + 10.16))
sch.wire((node[0], node[1] + 10.16), a)
sch.wire(b, (node[0] + 22.86, node[1] + 10.16))
d.glabel("RMII_REFCLK", (node[0] + 22.86, node[1] + 10.16), "R", "output")
T("RMII REFERENCE CLOCK: 50 MHz +-50 ppm CMOS XO, OE tied high.\nTwo point-to-point branches, 33R each at the XO:\n"
  "PHY XTAL1 and ECP5 C8 (PCLKT1_0), <= 25 mm,\nmatched +-5 mm, over solid GND.", (XO[0] - 7.62, XO[1] + 22.86))

# ---------------------------------------------------------------- 24.576 MHz VCXO
VX, VY = 109.22, 81.28
vc = sch.symbol("studio_E:VCXO_3225", d.ref("Y"), "24.576MHz VCXO", (VX, VY),
                footprint="studio_E:Oscillator_SMD_3225-4Pin_YXC_SX3V",
                fields=fields("SX3V24.576B20100F30TNN", "SCTF", "C5179997",
                              Note="alternative on the same land: YXC OT2EL4C4JI-111OLP-24.576M (C5203547), "
                                   "fit R(0R) to VDD, remove the series 0R"),
                ref_at=(VX + 5.08, VY + 12.7), value_at=(VX + 5.08, VY + 15.24))
vin, vout, vvdd = vc.pin("1"), vc.pin("3"), vc.pin("4")
d.gnd(vc.pin("2"))
# tune: VCXO_TUNE (ECP5 N4, delta-sigma) -> 100k -> 1u -> 100k -> 1u -> 0R -> Vc  (2 poles at 1.59 Hz)
x0 = 35.56
d.glabel("VCXO_TUNE", (x0, VY), "L", "input")
r1, a1, b1 = d.series("100k", (x0 + 10.16, VY))
sch.wire((x0, VY), a1)
n1 = (x0 + 17.78, VY)
sch.wire(b1, n1)
d.cap_down("1u", n1)
r2, a2, b2 = d.series("100k", (x0 + 25.4, VY))
sch.wire(n1, a2)
n2 = (x0 + 33.02, VY)
sch.wire(b2, n2)
d.cap_down("1u", n2)
r3, a3, b3 = d.series("0R", (x0 + 40.64, VY))
sch.wire(n2, a3)
n3 = (x0 + 50.8, VY)
sch.wire(b3, n3, vin)
# shared land: XO's pin 1 is OE -> 0R to VDD (DNP with the VCXO fitted)
yr = VY - 20.32
rx = d.part("0R", (n3[0], VY - 7.62), dnp=True, note="fit only with the fixed XO (C5203547); then remove R(0R) in the tune path",
            ref_at=(n3[0] - 3.81, VY - 8.89), value_at=(n3[0] - 3.81, VY - 6.35), justify="right")
sch.wire(n3, rx.pin("2"))
sch.wire(rx.pin("1"), (n3[0], yr))
sch.wire(vvdd, (vvdd[0], yr))
sch.wire((n3[0], yr), (vvdd[0] + 30.48, yr))
d.cap_down("100n", (vvdd[0] + 7.62, yr), decouples=f"{vc.ref}.4")
d.cap_down("4u7_0603", (vvdd[0] + 17.78, yr), decouples=f"{vc.ref}.4")
fv = d.part("FB221", (vvdd[0] + 38.1, yr), rot=90, justify="",
            ref_at=(vvdd[0] + 38.1, yr - 5.59), value_at=(vvdd[0] + 38.1, yr - 3.05))
lo = min(fv.pin("1"), fv.pin("2"))
hi = max(fv.pin("1"), fv.pin("2"))
sch.wire((vvdd[0] + 30.48, yr), lo)
sch.wire(hi, (hi[0] + 5.08, yr))
d.rail("+3V3", (hi[0] + 5.08, yr))
sch.label("VCXO_VDD", (vvdd[0] + 1.27, yr))
flag((vvdd[0] + 25.4, yr))
# outputs: FPGA PLL input direct (no R: fastest edge, review MINOR-4); block F's buffer via 33R
node = (vout[0] + 7.62, vout[1])
sch.wire(vout, node, (node[0] + 15.24, node[1]))
d.glabel("VCXO_CLK", (node[0] + 15.24, node[1]), "R", "output")
sch.wire(node, (node[0], node[1] + 10.16))
r, a, b = d.series("33R", (node[0] + 10.16, node[1] + 10.16))
sch.wire((node[0], node[1] + 10.16), a)
sch.wire(b, (node[0] + 22.86, node[1] + 10.16))
d.glabel("MCLK_Q", (node[0] + 22.86, node[1] + 10.16), "R", "output")
T("Tune: 1-bit delta-sigma from ECP5 N4, 2 x (100k, 1u): 1.59 Hz poles,\n> 16 bits below 2 Hz; firmware clamps Vc to 0.3-3.0 V.\n"
  "Fixed-XO fallback on the same land: fit the 0R to VDD, remove the series 0R.", (x0 - 5.08, VY + 20.32))
T("VCXO_CLK -> ECP5 P6 (LLC_GPLL0T_IN), shortest branch, no R.\nMCLK_Q -> block F's SN74LVC2G34 (MCLK_Q).\n"
  "VCXO within 10 mm of P6, RC filter beside Vc,\nnothing switching under the 1u caps.", (x0 - 5.08, VY + 33.02))
sch.box((x0 - 22.86, yr - 12.7), (node[0] + 50.8, VY + 43.18), "AUDIO / PWM MASTER CLOCK, 24.576 MHz VCXO")

sch.save()
print("wrote", sch.file)
