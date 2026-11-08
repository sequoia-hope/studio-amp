"""io.py -- block G sheet: user I/O, debug and test points (references 1200-1299).

Run from the repo root: python3 hw/satellite/a/gen/io.py

Left column: USB-C, Qwiic, debug probe.  Middle: addressable LED output, knob header, FPGA JTAG.
Right: the remappable display header, its backlight switch, and test points.
Connectors are drawn with their pins facing down (rot 90/270) so ground drops straight to a
symbol and the signals fan out to the right without crossings.
Values come from design/parts/G-*.md.
"""
from __future__ import annotations

from cg_common import Sheet

S = Sheet("io", paper="A2")


def hR(key, left, below=False, **kw):
    """Horizontal resistor whose pin 1 is at `left`."""
    if below:
        kw.update(ref_at=(left[0] + 1.27, left[1] + 2.54), value_at=(left[0] + 1.27, left[1] + 4.318))
    return S.R(key, (left[0] + 3.81, left[1]), rot=90, **kw)


def vR(key, top, **kw):
    """Vertical resistor whose pin 1 is at `top`."""
    return S.R(key, (top[0], top[1] + 3.81), **kw)


def vR_gnd(key, top, **kw):
    r = vR(key, top, **kw)
    S.gnd((top[0], top[1] + 7.62))
    return r


def pullup(key, at, rail, **kw):
    """Resistor from a wire at `at` up to `rail`."""
    r = vR(key, (at[0], at[1] - 7.62), **kw)
    S.rail(rail, (at[0], at[1] - 7.62))
    return r


def esd(at):
    """PESD5V0S1BL (bidirectional, 35 pF) from a line at `at` down to GND, texts to the right."""
    d = S.part("Device:D_TVS", "D", "PESD5V0S1BL", (at[0], at[1] + 3.81), rot=90,
               ref_at=(at[0] + 2.54, at[1] + 3.048), value_at=(at[0] + 2.54, at[1] + 4.826), justify="left")
    S.gnd((at[0], at[1] + 7.62))
    return d


def tvs(key, at):
    """Unidirectional SMF TVS (drawn as a Zener), cathode on the rail at `at`, anode to GND."""
    d = S.part("Device:D_Zener", "D", key, (at[0], at[1] + 3.81), rot=270,
               ref_at=(at[0] + 2.54, at[1] + 3.048), value_at=(at[0] + 2.54, at[1] + 4.826), justify="left")
    S.gnd((at[0], at[1] + 7.62))
    return d


def jumper(at, bridged, rot=0, note=None, **kw):
    lib = "Jumper:SolderJumper_2_Bridged" if bridged else "Jumper:SolderJumper_2_Open"
    fp = ("Jumper:SolderJumper-2_P1.3mm_Bridged_RoundedPad1.0x1.5mm" if bridged
          else "Jumper:SolderJumper-2_P1.3mm_Open_RoundedPad1.0x1.5mm")
    f = {"Note": note} if note else None
    return S.part(lib, "JP", None, at, rot=rot, value="bridged" if bridged else "open", footprint=fp,
                  in_bom=False, fields=f, **kw)


def srv05(at, left, right, rail="+3V3"):
    """SRV05-4 with local labels on its I/O pins. left/right: (upper, lower) names, None = no connect."""
    e = S.part("Power_Protection:SRV05-4", "U", "SRV05-4", at,
               ref_at=(at[0] + 3.81, at[1] + 13.97), value_at=(at[0] + 3.81, at[1] + 15.748), justify="left")
    for (pu, pl), side in ((("1", "3"), -1), (("4", "6"), 1)):
        names = left if side < 0 else right
        for pn, nm in zip((pu, pl), names):
            pp = e.pin(pn)
            if nm is None:
                S.nc(pp)
            else:
                S.w(pp, (pp[0] + side * 2.54, pp[1]))
                S.label(nm, (pp[0] + side * 2.54, pp[1]), rot=180 if side < 0 else 0)
    S.rail(rail, e.pin("5"))
    S.gnd(e.pin("2"))
    return e


def switch(key, at, **kw):
    """TPS2553 in DBV (Qwiic) or DRV (LED, thermal pad); returns the part and its pins by function."""
    sym = "studio_G:TPS2553DRV" if key == "TPS2553DRV" else "studio_G:TPS2553"
    sw = S.part(sym, "U", key, at, **kw)
    n = (dict(IN="6", EN="4", OUT="1", FLT="3", GND="5", ILIM="2") if key == "TPS2553DRV"
         else dict(IN="1", EN="3", OUT="6", FLT="4", GND="2", ILIM="5"))
    return sw, {k: sw.pin(v) for k, v in n.items()}


# ===================================================================== USB-C
def usb():
    S.box((12.7, 15.24), (147.32, 110.49), "USB-C  USB 2.0 FS to the RP2350, sink only  (G-usb-c.md)")
    j = S.part("Connector:USB_C_Receptacle_USB2.0_16P", "J", "USB_C", (27.94, 63.5),
               ref_at=(15.24, 33.02), value_at=(15.24, 34.798), justify="left")
    vb, cc1, cc2 = j.pin("A4"), j.pin("A5"), j.pin("B5")
    dm1, dm2, dp1, dp2 = j.pin("A7"), j.pin("B7"), j.pin("A6"), j.pin("B6")
    gp, sh = j.pin("A1"), j.pin("S1")
    S.nc(j.pin("A8"))
    S.nc(j.pin("B8"))
    S.gnd(gp)
    # shell: 0R to GND fitted; 1M || 4n7 2 kV (DNP) is the isolated-shell option for EMC tests
    ysh = gp[1] + 10.16
    S.w(sh, (sh[0], ysh), (53.34, ysh))
    S.label("USB_SHIELD", (sh[0] + 2.54, ysh))
    vR_gnd("0R", (38.1, ysh), fields={"Note": "fit for shell to GND; remove to isolate"})
    vR_gnd("1M", (45.72, ysh), dnp=True, vtext="right", fields={"Note": "DNP: isolated-shell option"})
    S.C("4n7_2kV", (53.34, ysh + 3.81), dnp=True, vtext="right", fields={"Note": "DNP: isolated-shell option"})
    S.gnd((53.34, ysh + 7.62))
    S.text("Shell: 0R to GND fitted. Isolated option:\nremove the 0R, fit 1M || 4n7 2 kV (G-usb-c.md)",
           (68.58, 99.06))
    # VBUS -> VUSB: SMF5.0A at the connector, USBLC6 VBUS clamp, VUSB_DET divider
    y = vb[1]
    xd = 116.84
    S.w(vb, (xd, y))
    S.flag((50.8, y))
    tvs("SMF5.0A", (58.42, y))
    S.tp((66.04, y), "VUSB", keystone=False)
    S.rail("VUSB", (99.06, y))
    # D-/D+: both receptacle rows joined, through the USBLC6-2SC6 flow-through pins
    u = S.part("Power_Protection:USBLC6-2SC6", "U", "USBLC6-2SC6", (76.2, dm1[1]),
               ref_at=(80.01, dm1[1] - 8.89), value_at=(80.01, dm1[1] - 7.112), justify="left",
               footprint="Package_TO_SOT_SMD:SOT-23-6")
    io1l, io1r, io2l, io2r = u.pin("1"), u.pin("6"), u.pin("3"), u.pin("4")
    S.w(dm2, (45.72, dm2[1]), (45.72, dm1[1]))
    S.w(dm1, io1l)
    S.w(dp2, (48.26, dp2[1]), (48.26, dp1[1]))
    S.w(dp1, (60.96, dp1[1]), (60.96, io2l[1]), io2l)
    S.w(u.pin("5"), (u.pin("5")[0], y))
    S.gnd(u.pin("2"))
    for p, name in ((io1r, "USB_DM"), (io2r, "USB_DP")):
        S.w(p, (93.98, p[1]))
        S.glabel(name, (93.98, p[1]), shape="bidirectional")
    S.text("27R series at the RP2350 (block E)", (88.9, 71.12))
    # CC: one 5.1k per pin, never shared (Rd, sink)
    for p, name in ((cc1, "CC1"), (cc2, "CC2")):
        S.w(p, (p[0] + 2.54, p[1]))
        S.label(name, (p[0] + 2.54, p[1]))
    for x, name in ((55.88, "CC1"), (66.04, "CC2")):
        S.label(name, (x, 78.74))
        S.w((x, 78.74), (x, 81.28))
        vR_gnd("5.1k", (x, 81.28))
    # VUSB_DET: 15k / 22k -> 3.12 V at 5.25 V, 100n
    vR("15k", (xd, y))
    vR_gnd("22k", (xd, y + 7.62))
    S.w((xd, y + 7.62), (132.08, y + 7.62))
    S.cap_down("100n", 124.46, y + 7.62)
    S.glabel("VUSB_DET", (132.08, y + 7.62), shape="output")


# ===================================================================== Qwiic
def qwiic():
    S.box((12.7, 15.24), (147.32, 144.78), "QWIIC  TCA9617B repeater + TPS2553 switch, 155-207 mA  (G-qwiic.md)")
    j = S.part("Connector_Generic_MountingPin:Conn_01x04_MountingPin", "J", "JST_SH4", (25.4, 30.48), rot=90,
               ref_at=(35.56, 25.4), value_at=(35.56, 27.178), justify="left")
    p1, p2, p3, p4, mp = j.pin("1"), j.pin("2"), j.pin("3"), j.pin("4"), j.pin("MP")
    S.text("1 GND  2 +3V3  3 SDA  4 SCL (Qwiic)", (15.24, 20.32))
    S.gnd(p1)
    S.w(mp, (mp[0], mp[1] + 2.54))
    S.gnd((mp[0], mp[1] + 2.54))
    y_scl, y_sda, y_pwr = 45.72, 55.88, 71.12
    xt = 101.6
    t = S.part("studio_G:TCA9617B", "U", "TCA9617B", (xt, y_sda), mirror="y",
               ref_at=(104.14, y_sda + 15.24), value_at=(104.14, y_sda + 17.018), justify="left")
    sclb, sdab, scla, sdaa, en = t.pin("7"), t.pin("6"), t.pin("2"), t.pin("3"), t.pin("5")
    # B side: straight to J pins 3/4 (no series R, G-qwiic.md), 2.2k pull-ups to QWIIC_PU
    S.w(p4, (p4[0], y_scl), (86.36, y_scl), (86.36, sclb[1]), sclb)
    S.w(p3, (p3[0], y_sda), sdab)
    S.label("QWIIC_SCL", (35.56, y_scl))
    S.label("QWIIC_SDA", (35.56, y_sda))
    pullup("2.2k", (66.04, y_scl), "QWIIC_PU")
    pullup("2.2k", (76.2, y_sda), "QWIIC_PU")
    S.tp((48.26, y_scl), "SCLB", keystone=False)
    S.tp((55.88, y_sda), "SDAB", keystone=False)
    S.gnd(t.pin("4"))
    vcca, vccb = t.pin("1"), t.pin("8")
    yb = vcca[1] - 7.62
    S.w(vccb, (vccb[0], yb), (109.22, yb))
    S.w(vcca, (vcca[0], yb))
    S.rail("+3V3", (vccb[0], yb))
    S.cap_down("100n", 109.22, yb, dec=f"{t.ref}.1", vtext="right")
    # A side to the RP2350 I2C1; SCL lifts to its own lane so both 4.7k pull-ups hang clear
    S.w(scla, (116.84, scla[1]), (116.84, y_scl - 5.08), (129.54, y_scl - 5.08))
    S.glabel("I2C1_SCL", (129.54, y_scl - 5.08), shape="bidirectional")
    pullup("4.7k", (121.92, y_scl - 5.08), "+3V3")
    S.w(sdaa, (129.54, sdaa[1]))
    S.glabel("I2C1_SDA", (129.54, sdaa[1]), shape="bidirectional")
    pullup("4.7k", (124.46, sdaa[1]), "+3V3")
    S.text("A-side 4.7k: drop if block E\nfits I2C1 pull-ups", (106.68, 22.86))
    # EN: QWIIC_PWR_EN, 10k pull-down (beats the -25 uA internal pull-up)
    S.w(en, (129.54, en[1]))
    S.glabel("QWIIC_PWR_EN", (129.54, en[1]), shape="input")
    vR_gnd("10k", (124.46, en[1]), vtext="left")
    # power: +3V3 -> TPS2553 (RILIM 150k) -> QWIIC_3V3 -> J pin 2
    sw, P = switch("TPS2553", (76.2, 91.44), ref_at=(50.8, 80.01), value_at=(50.8, 81.788), justify="left")
    S.rail("+3V3", (50.8, P["IN"][1]))
    S.w((50.8, P["IN"][1]), P["IN"])
    S.cap_down("1u_50V_0603", 58.42, P["IN"][1], dec=f"{sw.ref}.1")
    S.w(P["EN"], (63.5, P["EN"][1]), (63.5, 106.68), (55.88, 106.68))
    S.glabel("QWIIC_PWR_EN", (55.88, 106.68), rot=180, shape="input")
    S.gnd(P["GND"])
    vR_gnd("150k", P["ILIM"], vtext="right")
    xo = P["OUT"][0] + 5.08
    S.w(p2, (p2[0], y_pwr), (xo, y_pwr), (xo, P["OUT"][1]), P["OUT"])
    S.rail("QWIIC_3V3", (38.1, y_pwr))
    S.tp((55.88, y_pwr), "QWIIC_3V3", keystone=False, rot=180)
    S.w((xo, P["OUT"][1]), (104.14, P["OUT"][1]))
    S.cap_down("10u_25V", 96.52, P["OUT"][1])
    vR_gnd("100k", (104.14, P["OUT"][1]))
    # supply of the B-side pull-ups: QWIIC_3V3 through a bridged jumper (cut to remove ours)
    jumper((66.04, y_pwr - 3.81), True, rot=90, note="cut to remove the on-board 2.2k B-side pull-ups",
           ref_at=(68.58, y_pwr - 4.572), value_at=(68.58, y_pwr - 2.794), justify="left")
    S.w((66.04, y_pwr - 7.62), (66.04, y_pwr - 10.16))
    S.rail("QWIIC_PU", (66.04, y_pwr - 10.16))
    S.flag((60.96, y_pwr - 10.16))
    S.w((60.96, y_pwr - 10.16), (66.04, y_pwr - 10.16))
    # FAULT -> QWIIC_FAULT_N, 10k to +3V3
    S.w(P["FLT"], (P["FLT"][0] + 2.54, P["FLT"][1]), (P["FLT"][0] + 2.54, 106.68), (129.54, 106.68))
    pullup("10k", (114.3, 106.68), "+3V3")
    S.glabel("QWIIC_FAULT_N", (129.54, 106.68), shape="output")
    # ESD on SDA/SCL: SRV05-4 (3 pF), rail QWIIC_3V3
    srv05((33.02, 124.46), (None, None), ("QWIIC_SCL", "QWIIC_SDA"), rail="QWIIC_3V3")
    S.text("No series R on SDA/SCL: a far-end low\nplus I*R must stay below VILB 0.4 V", (63.5, 124.46))


# ===================================================================== debug probe
def debug():
    S.box((12.7, 15.24), (147.32, 78.74), "DEBUG PROBE  JST SH 3-pin, Sequoia's convention  (G-debug-jtag.md)")
    for x0, title, lo, hi in ((22.86, "SWD:  1 SWCLK  2 GND  3 SWDIO", ("SWCLK", "output", "33R"),
                               ("SWDIO", "bidirectional", "33R")),
                              (86.36, "UART:  1 RX  2 GND  3 TX", ("UART0_RX", "output", "100R"),
                               ("UART0_TX", "input", "100R"))):
        j = S.part("Connector_Generic_MountingPin:Conn_01x03_MountingPin", "J", "JST_SH3", (x0, 27.94), rot=90,
                   ref_at=(x0 + 10.16, 22.86), value_at=(x0 + 10.16, 24.638), justify="left")
        p1, p2, p3, mp = j.pin("1"), j.pin("2"), j.pin("3"), j.pin("MP")
        S.gnd(p2)
        S.w(mp, (mp[0], mp[1] + 2.54))
        S.gnd((mp[0], mp[1] + 2.54))
        for p, (name, shape, rk), ly, xe in ((p3, hi, 43.18, x0 + 12.7), (p1, lo, 58.42, x0 + 17.78)):
            S.w(p, (p[0], ly), (x0 + 25.4, ly))
            esd((xe, ly))
            hR(rk, (x0 + 25.4, ly))
            S.w((x0 + 33.02, ly), (x0 + 38.1, ly))
            S.glabel(name, (x0 + 38.1, ly), shape=shape)
        S.text(title, (x0 - 7.62, 73.66))


# ===================================================================== LED output
def led():
    S.box((12.7, 15.24), (147.32, 134.62), "ADDRESSABLE LED OUTPUT  TPS2553 1.03-1.20 A, SN74LV1T125  (G-led-out.md)")
    y = 35.56
    sw, P = switch("TPS2553DRV", (40.64, y + 2.54), ref_at=(33.02, y - 6.35), value_at=(43.18, y - 6.35))
    S.rail("+5V_BUCK", (17.78, y))
    S.w((17.78, y), P["IN"])
    S.cap_down("1u_50V_0603", 22.86, y, dec=f"{sw.ref}.6", vtext="left")
    S.w(P["EN"], (27.94, P["EN"][1]), (27.94, 58.42), (22.86, 58.42))
    S.glabel("LED_EN", (22.86, 58.42), rot=180, shape="input")
    vR_gnd("100k", (27.94, 58.42), vtext="right")
    S.gnd(P["GND"])
    vR_gnd("23.2k", P["ILIM"], vtext="right")
    S.w(P["FLT"], (53.34, P["FLT"][1]), (53.34, 58.42), (66.04, 58.42))
    pullup("10k", (58.42, 58.42), "+3V3", vtext="right")
    S.glabel("LED_FAULT_N", (66.04, 58.42), shape="output")
    S.text("RILIM 23.2k: 1.03-1.20 A;\nfirmware caps it by PoE class", (50.8, 22.86))
    # +5V_LED -> 22u -> BLM31KN601 -> SMF6.0A -> J pin 1 (J at the top right, pins down)
    j = S.part("Connector_Generic:Conn_01x04", "J", "JST_PH4", (127.0, 20.32), rot=90,
               ref_at=(101.6, 20.32), value_at=(101.6, 22.098), justify="left")
    c1, c2, c3, c4 = j.pin("1"), j.pin("2"), j.pin("3"), j.pin("4")
    xf = 106.68
    S.w(P["OUT"], (xf - 2.54, y))
    S.cap_down("22u_25V", 66.04, y)
    S.rail("+5V_LED", (78.74, y))
    S.tp((91.44, y), "+5V_LED", rot=180)
    S.part("Device:FerriteBead_Small", "FB", "FB_600R_2A9", (xf, y), rot=90,
           ref_at=(xf - 3.81, y - 6.096), value_at=(xf - 3.81, y - 4.318), justify="left")
    S.w((xf + 2.54, y), (c1[0], y), c1)
    tvs("SMF6.0A", (114.3, y))
    S.label("LED_5V_OUT", (116.84, y))
    S.gnd(c2)
    # level shifters on +5V_LED (OE tied low), 47R + PESD to J pins 3 (D) and 4 (C)
    for pin, name, uy in ((c3, "LED_DATA", 81.28), (c4, "LED_CLK", 116.84)):
        u = S.part("74xGxx:74LVC1G125", "U", "SN74LV1T125", (66.04, uy),
                   ref_at=(68.58, uy + 7.62), value_at=(68.58, uy + 9.398), justify="left",
                   footprint="Package_TO_SOT_SMD:SOT-23-5")
        a, vcc, oe, yo, gp = u.pin("2"), u.pin("5"), u.pin("1"), u.pin("4"), u.pin("3")
        S.w(vcc, (vcc[0], vcc[1] - 2.54), (vcc[0] - 7.62, vcc[1] - 2.54))
        S.rail("+5V_LED", (vcc[0], vcc[1] - 2.54))
        S.cap_down("100n", vcc[0] - 7.62, vcc[1] - 2.54, dec=f"{u.ref}.5", vtext="left")
        S.w(oe, (oe[0], oe[1] - 2.54), (76.2, oe[1] - 2.54), (76.2, oe[1]))
        S.gnd((76.2, oe[1]))
        S.gnd(gp)
        S.w(a, (a[0] - 5.08, a[1]))
        S.glabel(name, (a[0] - 5.08, a[1]), rot=180, shape="input")
        hR("47R", yo)
        xn = yo[0] + 12.7
        S.w((yo[0] + 7.62, yo[1]), (pin[0], yo[1]), pin)
        esd((xn, yo[1]))
        S.tp((xn + 7.62, yo[1]), f"{name} 5V", keystone=False)
    S.text("J: 1 +5V  2 GND  3 D  4 C (R-19)", (101.6, 129.54))


# ===================================================================== knob header
def knob():
    S.box((12.7, 15.24), (147.32, 175.26), "KNOB / ENCODER HEADER  2x6 0.1 in, optional  (G-knob.md)")
    xh, yh = 40.64, 104.14
    j = S.part("Connector_Generic:Conn_02x06_Odd_Even", "J", "HDR_2x6", (xh, yh), rot=270,
               ref_at=(15.24, yh + 17.78), value_at=(15.24, yh + 19.558), justify="left")
    P = {n: j.pin(str(n)) for n in range(1, 13)}
    S.gnd(P[2])
    S.gnd(P[12])
    # pin 11: +3V3 through 47R (encoder pull-ups / indicator LEDs, <= 10 mA)
    y11 = P[11][1] - 2.54
    S.w(P[11], (P[11][0], y11), (P[11][0] - 2.54, y11))
    hR("47R", (P[11][0] - 10.16, y11), below=True)
    S.w((P[11][0] - 10.16, y11), (P[11][0] - 15.24, y11))
    S.rail("+3V3", (P[11][0] - 15.24, y11))
    # top row fans up (pin 1, rightmost, takes the nearest lane), bottom row fans down (pin 4 nearest)
    yt, yb = P[1][1], P[4][1]
    top = [(1, "KNOB_REF", yt - 7.62), (3, "KNOB1", yt - 20.32), (5, "KNOB3", yt - 33.02),
           (7, "ENC1_A", yt - 48.26), (9, "ENC2_A", yt - 63.5)]
    bot = [(4, "KNOB2", yb + 7.62), (6, "KNOB4", yb + 20.32), (8, "ENC1_B", yb + 35.56),
           (10, "ENC2_B", yb + 50.8)]
    xr = 73.66
    for n, name, ly in top + bot:
        p = P[n]
        if name == "KNOB_REF":
            S.w(p, (p[0], ly), (68.58, ly))
            S.label("KNOB_REF", (48.26, ly))
            S.cap_down("1u_50V_0603", 55.88, ly, vtext="right")
            hR("100R", (68.58, ly), below=True)
            S.w((76.2, ly), (81.28, ly))
            S.rail("ADC_AVDD", (81.28, ly))
            S.text("KNOB_REF: RP2350 ADC_AVDD (block E) through\n100R, so knob readings are ratiometric.\n"
                   "Pots 10-50k.", (88.9, ly + 3.81))
            continue
        S.w(p, (p[0], ly), (xr, ly))
        esd((66.04 if n in (3, 7, 4, 8) else 63.5, ly))
        hR("1k", (xr, ly))
        S.w((xr + 7.62, ly), (124.46, ly))
        if name.startswith("KNOB"):
            S.cap_down("100n", 101.6, ly, vtext="right")
        else:
            pullup("10k", (91.44, ly), "+3V3", vtext="right")
            S.cap_down("10n", 106.68, ly, vtext="right")
        S.glabel(name, (124.46, ly), shape="output")


# ===================================================================== JTAG
def jtag():
    S.box((12.7, 15.24), (147.32, 93.98), "FPGA JTAG  1x6 0.1 in, optional  (G-debug-jtag.md)")
    j = S.part("Connector_Generic:Conn_01x06", "J", "HDR_1x6", (30.48, 33.02), rot=90,
               ref_at=(43.18, 30.48), value_at=(43.18, 32.258), justify="left")
    P = {n: j.pin(str(n)) for n in range(1, 7)}
    S.text("1 +3V3  2 GND  3 TCK  4 TDO  5 TDI  6 TMS\n4.7k pulls are on block E's sheet (TN-02038)",
           (15.24, 20.32))
    S.w(P[1], (P[1][0], P[1][1] + 2.54), (P[1][0] - 5.08, P[1][1] + 2.54))
    S.rail("+3V3", (P[1][0] - 5.08, P[1][1] + 2.54))
    S.gnd(P[2])
    lines = [(6, "FPGA_TMS", 50.8, "output", "JT_TMS"), (5, "FPGA_TDI", 60.96, "output", "JT_TDI"),
             (4, "FPGA_TDO", 71.12, "input", "JT_TDO"), (3, "FPGA_TCK", 81.28, "output", "JT_TCK")]
    for n, name, ly, shape, loc in lines:
        p = P[n]
        S.w(p, (p[0], ly), (93.98, ly))
        S.label(loc, (55.88, ly))
        hR("33R", (93.98, ly))
        S.w((101.6, ly), (124.46, ly))
        S.glabel(name, (124.46, ly), shape=shape)
    srv05((114.3, 33.02), ("JT_TMS", "JT_TDI"), ("JT_TDO", "JT_TCK"))


# ===================================================================== display header
def display():
    S.box((12.7, 15.24), (284.48, 231.14), "DISPLAY HEADER  8-pin 0.1 in socket, every position remappable  (G-display.md)")
    fpga = {1: "DISP_AUX7", 2: "DISP_AUX8", 3: "DISP_SCL", 4: "DISP_SDA", 5: "DISP_RES", 6: "DISP_DC",
            7: "DISP_CS", 8: "DISP_BLK"}
    default = {1: "G", 2: "V", 8: "B"}
    rows = {k: 38.1 + (k - 1) * 22.86 for k in range(1, 9)}
    xc, yc = 22.86, round((rows[4] + rows[5]) / 2 / 2.54) * 2.54
    j = S.part("Connector_Generic:Conn_01x08", "J", "SOCK_1x8", (xc, yc), mirror="y",
               ref_at=(15.24, yc - 13.97), value_at=(15.24, yc - 12.192), justify="left")
    # staircase: pins 1-4 turn up (pin 1 nearest the header), pins 5-8 turn down (pin 8 nearest)
    xv = {1: 30.48, 2: 33.02, 3: 35.56, 4: 38.1, 8: 30.48, 7: 33.02, 6: 35.56, 5: 38.1}
    jv, jb, jg = 66.04, 88.9, 116.84
    for k in range(1, 9):
        p = j.pin(str(k))
        Y = rows[k]
        S.w(p, (xv[k], p[1]), (xv[k], Y), (233.68, Y))
        S.label(f"DISP_P{k}", (45.72, Y))
        for xj, kind, rail in ((jv, "V", "DISP_VCC"), (jb, "B", "DISP_BL_SW")):
            jumper((xj, Y - 3.81), default.get(k) == kind, rot=90,
                   ref_at=(xj + 2.54, Y - 4.572), value_at=(xj + 2.54, Y - 2.794), justify="left")
            S.rail(rail, (xj, Y - 7.62))
        jumper((jg, Y + 3.81), default.get(k) == "G", rot=90,
               ref_at=(jg + 2.54, Y + 3.048), value_at=(jg + 2.54, Y + 4.826), justify="left")
        S.gnd((jg, Y + 7.62))
        hR("47R", (233.68, Y))
        S.w((241.3, Y), (254.0, Y))
        S.glabel(fpga[k], (254.0, Y), shape="input")
    S.text("Each position: a jumper to DISP_VCC, DISP_BL_SW (switched backlight) or GND, else 47R to its FPGA pin.\n"
           "Defaults for GND, VCC, SCL, SDA, RES, DC, CS, BLK: JP to GND on 1, VCC on 2, BLK on 8\n"
           "bridged. An FPGA line whose position is jumpered must be constrained Hi-Z (block E).",
           (137.16, 22.86))
    # ESD: two SRV05-4 on the header-side nets, rail +3V3
    srv05((157.48, 213.36), ("DISP_P1", "DISP_P2"), ("DISP_P3", "DISP_P4"))
    srv05((215.9, 213.36), ("DISP_P5", "DISP_P6"), ("DISP_P7", "DISP_P8"))


def backlight():
    """DISP_VCC ferrite and the backlight high-side switch (AO3401A + 2N7002). Its output rail is
    DISP_BL_SW: DISP_BLK is already the FPGA line to header position 8 (E-pinmap.md)."""
    S.box((12.7, 15.24), (284.48, 66.04), "DISP_VCC AND BACKLIGHT SWITCH  (G-display.md)")
    y = 30.48
    S.rail("+3V3", (17.78, y))
    S.part("Device:FerriteBead_Small", "FB", "FB_220R", (35.56, y), rot=90,
           ref_at=(31.75, y - 6.096), value_at=(31.75, y - 4.318), justify="left")
    S.w((17.78, y), (33.02, y))
    S.cap_down("1u_50V_0603", 45.72, y)
    S.flag((53.34, y))
    S.rail("DISP_VCC", (66.04, y))
    S.tp((76.2, y), "DISP_VCC", keystone=False)
    # AO3401A (mirrored: source up on DISP_VCC, drain down to DISP_BL_SW), gate pulled to source by 100k
    q = S.part("Transistor_FET:AO3401A", "Q", "AO3401A", (104.14, y + 7.62), mirror="x",
               ref_at=(109.22, y + 6.35), value_at=(109.22, y + 8.128), justify="left")
    g_, d_, s_ = q.pin("1"), q.pin("3"), q.pin("2")
    S.w((38.1, y), (s_[0], y), s_)
    xg = 91.44
    S.w(g_, (xg, g_[1]))
    S.R("100k", (xg, y + 3.81), vtext="left")
    S.w((xg, y + 7.62), (xg, g_[1]))
    yb = d_[1] + 2.54
    S.w(d_, (d_[0], yb), (137.16, yb))
    S.flag((111.76, yb))
    S.rail("DISP_BL_SW", (127.0, yb))
    S.tp((137.16, yb), "DISP_BL_SW", keystone=False)
    # 2N7002 pulls the gate low; its gate from DISP_BL_PWM through 100R, 100k pull-down
    n = S.part("Transistor_FET:2N7002", "Q", "2N7002", (xg - 2.54, g_[1] + 15.24),
               ref_at=(xg + 1.27, g_[1] + 13.97), value_at=(xg + 1.27, g_[1] + 15.748), justify="left")
    ng, nd, ns = n.pin("1"), n.pin("3"), n.pin("2")
    S.w((xg, g_[1]), nd)
    S.gnd(ns)
    S.w(ng, (ng[0] - 2.54, ng[1]))
    hR("100R", (ng[0] - 10.16, ng[1]))
    vR_gnd("100k", (ng[0] - 2.54, ng[1]), vtext="right")
    S.w((ng[0] - 10.16, ng[1]), (ng[0] - 17.78, ng[1]))
    S.glabel("DISP_BL_PWM", (ng[0] - 17.78, ng[1]), rot=180, shape="input")
    S.text("PWM <= 2 kHz with the 100k gate pull-up\n(10k for faster PWM). Q off at power-up.", (165.1, 40.64))


# ===================================================================== test points
def testpoints():
    S.box((12.7, 15.24), (284.48, 45.72), "TEST POINTS  (R-80, G-testpoints.md)  rail pads sit at their rails")
    sigs = [("LED_EN", "input"), ("LED_FAULT_N", "output"), ("QWIIC_PWR_EN", "input"),
            ("QWIIC_FAULT_N", "output"), ("VDRV_EN", "input"), ("VDRV_PG", "input"), ("PTP_PPS", "input"),
            ("RUN", "bidirectional")]
    x = 30.48
    for name, shape in sigs:
        S.glabel(name, (x, 35.56), rot=180, shape=shape)
        S.w((x, 35.56), (x + 7.62, 35.56))
        S.tp((x + 7.62, 35.56), name, keystone=False)
        x += 27.94 if len(name) < 10 else 30.48
    for k, xg in enumerate((264.16, 274.32)):
        S.tp((xg, 35.56), "GND")
        S.gnd((xg, 35.56))


S.off = (0.0, 0.0)
usb()
S.off = (0.0, 101.6)
qwiic()
S.off = (0.0, 233.68)
debug()
S.off = (139.7, 0.0)
led()
S.off = (139.7, 124.46)
knob()
S.off = (139.7, 289.56)
jtag()
S.off = (289.56, 0.0)
display()
S.off = (289.56, 223.52)
backlight()
S.off = (289.56, 279.4)
testpoints()
S.off = (0.0, 0.0)
S.save()
print("wrote", S.sch.file.name)
