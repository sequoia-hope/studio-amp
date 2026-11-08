"""rails.py -- block C sheet: secondary rails and sequencing (references 300-399).

Run from the repo root: python3 hw/satellite/a/gen/rails.py

Power flows left to right, one row per VBUS-fed converter, VBUS on the left:
  row 1  LM5013 5 V buck -> TPS2116 source select -> 3V3 buck -> 1V1 buck -> 2V5 LDO
  row 2  LM5017 VDRV buck + TLV6703 good -> PG buffers -> 3V3_Q LDO -> 3V3_A LDO
  row 3  LM5017 +-15 V Fly-Buck -> TPS7A4901 / TPS7A3001 -> +5V_A
Values come from design/parts/C-*.md (the source of truth until this sheet exists).
"""
from __future__ import annotations

from cg_common import Sheet, g

S = Sheet("rails", paper="A2")


def hR(key, left, below=False, **kw):
    """Horizontal resistor whose left pin is at `left` (texts above, or below with below=True)."""
    if below:
        kw.update(ref_at=(left[0] + 3.81, left[1] + 2.54), value_at=(left[0] + 3.81, left[1] + 4.318), justify="")
    return S.R(key, (left[0] + 3.81, left[1]), rot=90, **kw)


def Lh(key, center):
    """Horizontal inductor with both texts centred above it."""
    return S.part("Device:L", "L", key, center, rot=90, ref_at=(center[0], center[1] - 5.334),
                  value_at=(center[0], center[1] - 3.556), justify="")


def hC(key, left, **kw):
    return S.C(key, (left[0] + 3.81, left[1]), rot=90, **kw)


def vR(key, top, **kw):
    """Vertical resistor whose top pin is at `top`."""
    return S.R(key, (top[0], top[1] + 3.81), **kw)


def vC(key, top, **kw):
    return S.C(key, (top[0], top[1] + 3.81), **kw)


def vR_gnd(key, top, **kw):
    r = vR(key, top, **kw)
    S.gnd((top[0], top[1] + 7.62))
    return r


def link(left, label):
    """0R 1206 bring-up isolation link (R-80), horizontal, left pin at `left`."""
    return hR("0R_1206", left, fields={"Note": f"bring-up link: {label}"})


def jumper(left, label, above=False, below=False):
    """Bridged solder jumper (cut to isolate), PCB only."""
    ry, vy = (-4.318, -2.54) if above else (2.54, 4.318) if below else (-2.54, 3.81)
    return S.part("Jumper:SolderJumper_2_Bridged", "JP", None, (left[0] + 3.81, left[1]),
                  value="bridged", fields={"Note": f"bring-up link: {label}"}, footprint="Jumper:SolderJumper-2_P1.3mm_Bridged_RoundedPad1.0x1.5mm",
                  in_bom=False, ref_at=(left[0] + 3.81, left[1] + ry), value_at=(left[0] + 3.81, left[1] + vy),
                  justify="")


def cap_bank(caps, y, dec):
    """VBUS input caps hanging from the input wire; texts on the right, starting below the wire.
    caps: (x, key, decouples?)."""
    for x, k, d in caps:
        S.C(k, (x, y + 3.81), dec=dec if d else None, ref_at=(x + 3.302, y + 5.588), value_at=(x + 5.08, y + 5.588),
            ref_rot=90, justify="", vtext=False)
        S.gnd((x, y + 7.62))


def vbus_in(y, label, flag_x):
    """VBUS power symbol, test point, 0R bring-up link, and the PWR_FLAG on the linked side."""
    S.rail("VBUS", (17.78, y))
    S.w((17.78, y), (27.94, y))
    S.tp((22.86, y), "VBUS", rot=180)
    link((27.94, y), label)
    S.w((35.56, y), (78.74, y))
    S.flag((flag_x, y))


# ===================================================================== row 1: 5 V buck
def five_volt():
    S.box((12.7, 20.32), (200.66, 88.9), "5 V BUCK  LM5013  ~213 kHz  (C-5v-buck.md)")
    y = 33.02                                         # VBUS rail into the buck
    vbus_in(y, "VBUS -> 5 V buck", 63.5)
    u = S.part("studio_C:LM5013", "U", "LM5013", (91.44, 53.34), ref_at=(83.82, 40.64), value_at=(90.17, 40.64))
    cap_bank(((43.18, "4u7_100V", True), (50.8, "4u7_100V", True), (58.42, "100n_100V", True)), y, f"{u.ref}.2")
    vin, en, ron = u.pin("2"), u.pin("3"), u.pin("4")
    bst, sw, fb, pg = u.pin("7"), u.pin("8"), u.pin("5"), u.pin("6")
    gp, ep = u.pin("1"), u.pin("9")
    S.w((78.74, y), (78.74, vin[1]), vin)
    # EN/UVLO divider 1M / 52.3k: on 30.2 V, off 28.2 V
    vR("1M_0805", (68.58, 38.1))
    S.w((68.58, y), (68.58, 38.1))
    S.w((68.58, 45.72), (68.58, en[1]), en)
    vR_gnd("52.3k", (68.58, en[1]))
    # RON 64.9k -> ~213 kHz
    S.w(ron, (76.2, ron[1]))
    vR_gnd("64.9k", (76.2, ron[1]))
    S.w(ep, gp, (gp[0], gp[1] + 2.54))
    S.gnd((gp[0], gp[1] + 2.54))
    # bootstrap 2n2 (datasheet window 1.5-2.5 nF)
    S.w(bst, (104.14, bst[1]))
    vC("2n2", (104.14, bst[1] - 7.62))
    S.w((104.14, bst[1] - 7.62), (109.22, bst[1] - 7.62), (109.22, sw[1]))
    # switch node, catch diode, inductor
    S.w(sw, (139.7, sw[1]))
    S.label("SW_5V", (124.46, sw[1]))
    d = S.part("studio_C:D_Schottky_TO277A", "D", "SS5P10", (134.62, sw[1] + 5.08), rot=90,
               ref_at=(138.43, sw[1] + 4.064), value_at=(138.43, sw[1] + 5.842))
    S.gnd(d.pin("1"))
    Lh("L47u_SRP1265A", (143.51, sw[1]))
    yo = sw[1]
    S.w((147.32, yo), (190.5, yo))
    for x in (152.4, 160.02, 167.64):
        S.cap_down("22u_25V", x, yo)
    S.tp((185.42, yo), "+5V_BUCK", rot=180)
    S.flag((177.8, yo))
    S.text("+5V_BUCK 5.04 V: 0.91 A design\n1.75 A with the LED port at its limit", (147.32, 27.94))
    # PGOOD -> PG_5V (divider 56k/100k at the TPS2116, C-5v-buck.md)
    S.label("PG_5V", pg)
    # feedback divider at FB (0.5 %): 100k / 31.6k -> 5.04 V with the Type 3 offset
    fx = 109.22
    S.w(fb, (fx, fb[1]), (fx, 68.58))
    S.label("FB_5V", (fx, 60.96))
    vR_gnd("31.6k_0.5", (fx, 68.58), vtext="left")
    hR("100k_0.5", (fx, 68.58))
    S.w((fx + 7.62, 68.58), (fx + 15.24, 68.58))
    S.rail("+5V_BUCK", (fx + 15.24, 68.58))
    # Type 3 ripple network (RA from SW, CA to VOUT, CB to FB), drawn beside the output caps;
    # in layout it sits at FB like the divider
    xn, yt = 165.1, 66.04
    S.label("SW_5V", (xn, yt))
    S.R("330k_0805", (xn, yt + 3.81), ref_at=(xn - 2.54, yt + 2.54), value_at=(xn - 2.54, yt + 4.318),
        justify="right", vtext=False)
    xy = yt + 7.62
    S.C("3n3", (xn + 3.81, xy), rot=90, ref_at=(xn + 10.16, xy - 0.508), value_at=(xn + 10.16, xy + 1.27),
        justify="left", vtext=False)
    S.rail("+5V_BUCK", (xn + 7.62, xy))
    S.C("330p", (xn, xy + 3.81), ref_at=(xn - 2.54, xy + 3.302), value_at=(xn - 2.54, xy + 5.08),
        justify="right", vtext=False)
    S.w((xn, xy + 7.62), (xn, xy + 10.16), (xn - 7.62, xy + 10.16))
    S.label("FB_5V", (xn - 7.62, xy + 10.16), rot=180)
    S.text("Hot loop C301-U301-D301 tight.\nFB parts at pin 5, away from SW.\nSW_5V: pad + GND spring site (io)",
           (15.24, 76.2))
    S.text("UVLO on 30.2 V / off 28.2 V", (38.1, 50.8))


# ===================================================================== row 1: TPS2116
def source_select():
    S.box((203.2, 20.32), (271.78, 88.9), "5 V SOURCE SELECT  TPS2116\nbuck has priority (C-5v-mux.md)")
    S.w((190.5, 50.8), (190.5, 45.72), (196.85, 45.72))
    S.rail("+5V_BUCK", (190.5, 50.8))
    link((196.85, 45.72), "+5V_BUCK -> mux")
    u = S.part("studio_C:TPS2116", "U", "TPS2116", (233.68, 58.42), ref_at=(213.36, 76.2), value_at=(213.36, 77.978))
    vin1, mode, pr1, vin2 = u.pin("3"), u.pin("5"), u.pin("4"), u.pin("6")
    vout, st, gp = u.pin("2"), u.pin("8"), u.pin("1")
    S.w((204.47, 45.72), (220.98, 45.72), (220.98, vin1[1]), vin1)
    S.w((220.98, vin1[1]), (220.98, mode[1]), mode)            # MODE = VIN1: priority mode
    S.cap_down("1u_50V_0603", 215.9, 45.72, dec=f"{u.ref}.3")
    S.flag((212.09, 45.72))
    # PG_5V divider 56k / 100k from +5V_BUCK; LM5013 PGOOD pulls the node low
    vR("56k", (208.28, 49.53))
    S.w((208.28, 45.72), (208.28, 49.53))
    S.w((208.28, 57.15), (208.28, pr1[1]), pr1)
    vR_gnd("100k", (208.28, pr1[1]))
    S.label("PG_5V", (210.82, pr1[1]))
    # VIN2 from USB, 4u7 at the pin
    S.w(vin2, (vin2[0], 35.56))
    S.rail("VUSB", (vin2[0], 35.56))
    S.w((vin2[0], 38.1), (226.06, 38.1))
    S.cap_down("4u7_25V", 226.06, 38.1, dec=f"{u.ref}.6")
    S.w(gp, (gp[0], gp[1] + 2.54), (gp[0] + 7.62, gp[1] + 2.54))
    S.gnd((gp[0], gp[1] + 2.54))
    S.flag((gp[0] + 7.62, gp[1] + 2.54))  # the project's one GND PWR_FLAG
    # output +5V, ~100 uF for reverse-current blocking (TPS2116 7.3.4)
    S.w(vout, (269.24, vout[1]))
    S.tp((248.92, vout[1]), "+5V")
    S.cap_down("47u_10V", 256.54, vout[1])
    S.cap_down("47u_10V", 264.16, vout[1])
    S.rail("+5V", (269.24, vout[1]))
    # ST: low when on USB power; pull-up required (7.3.3)
    S.w(st, (248.92, st[1]), (248.92, 81.28))
    hR("100k", (248.92, 81.28))
    S.w((256.54, 81.28), (261.62, 81.28))
    S.rail("+3V3", (261.62, 81.28))
    S.w((248.92, 81.28), (246.38, 81.28))
    S.label("PWR_FROM_POE", (246.38, 81.28), rot=180)


# ===================================================================== row 1: 3V3, 1V1
def buck(x0, name, out_rail, r_top, r_bot, n_cout, tie_en=True):
    """TPS62A02A buck: input link, caps, inductor, FB divider at the pin. x0: block left edge."""
    y = 53.34
    S.rail("+5V", (x0 + 5.08, y))
    S.w((x0 + 5.08, y), (x0 + 7.62, y))
    jumper((x0 + 7.62, y), f"+5V -> {name}", below=True)
    u = S.part("studio_C:TPS62A02A", "U", "TPS62A02A", (x0 + 45.72, y + 2.54),
               ref_at=(x0 + 38.1, y - 9.398), value_at=(x0 + 38.1, y - 7.62))
    vin, en, sw, fb, pg, gp = u.pin("4"), u.pin("1"), u.pin("3"), u.pin("6"), u.pin("5"), u.pin("2")
    S.w((x0 + 15.24, y), vin)
    S.flag((x0 + 20.32, y))
    S.cap_down("4u7_25V", x0 + 25.4, y, dec=f"{u.ref}.4")
    S.gnd(gp)
    if tie_en:
        S.w(en, (vin[0] - 2.54, en[1]), (vin[0] - 2.54, y))
    S.w(sw, (sw[0] + 6.35, sw[1]))
    Lh("L1u_SRP4020", (sw[0] + 10.16, sw[1]))
    xo = sw[0] + 13.97
    xc = [x0 + 93.98 + i * 7.62 for i in range(n_cout)]
    xe = xc[-1] + 5.08
    xt = xe + 5.08
    S.w((xo, y), (xt, y))
    for x in xc:
        S.cap_down("22u_10V", x, y)
    S.rail(out_rail, (xe, y))
    S.flag((x0 + 86.36, y))
    S.tp((xt, y), out_rail)
    # FB divider at the pin: R_top hangs from the output wire, R_bot to GND, node at FB
    fx = fb[0] + 7.62
    xr = x0 + 71.12
    yf = y + 10.16
    S.w(fb, (fx, fb[1]), (fx, yf))
    vR_gnd(r_bot, (fx, yf), vtext="right")
    vR(r_top, (xr, y), vtext="right")
    S.w((xr, y + 7.62), (xr, yf), (fx, yf))
    # feed-forward cap across R_top: footprint only (not needed in FPWM, C-3v3-1v1-bucks.md)
    xff = x0 + 78.74
    S.C("22p", (xff, y + 3.81), dnp=True, fields={"Note": "DNP: CFF option"})
    S.w((xff, y + 7.62), (xff, yf), (xr, yf))
    return u, en, pg


def logic_rails():
    S.box((274.32, 20.32), (391.16, 88.9), "3V3 BUCK  TPS62A02A  2.4 MHz FPWM")
    u3, en3, pg3 = buck(274.32, "3V3", "+3V3", "100k_0.1", "22k_0.1", 1)
    # PG_3V3 (100k pull-up) drives 1V1 EN and 2V5 EN_UV only; the FPGA reads PG_3V3_N (row 2)
    px = pg3[0] + 2.54
    S.w(pg3, (px, pg3[1]), (px, 78.74))
    hR("100k", (px - 7.62, 78.74))
    S.w((px - 7.62, 78.74), (px - 12.7, 78.74))
    S.rail("+3V3", (px - 12.7, 78.74))
    S.label("PG_3V3", (px + 12.7, 78.74))
    S.text("3V3 = 0.6 x (1 + 100k/22.0k) = 3.33 V\n0.1 %: ECP5 VCCIO max 3.465 V\n"
           "+3V3: 0.79 A design (2 A part)", (276.86, 27.94))

    S.box((393.7, 20.32), (518.16, 88.9), "1V1 BUCK  TPS62A02A  (ECP5 VCC)")
    u1, en1, pg1 = buck(393.7, "1V1", "+1V1", "84.5k", "100k", 2, tie_en=False)
    S.w((px, 78.74), (en1[0] - 5.08, 78.74), (en1[0] - 5.08, en1[1]), en1)
    S.nc(pg1)
    S.text("1V1 = 0.6 x (1 + 84.5k/100k) = 1.107 V\n+1V1: 0.40 A design; starts ~1 ms\nafter 3V3 (EN = PG_3V3)",
           (396.24, 27.94))


def ldo_2v5():
    S.box((444.5, 20.32), (576.58, 88.9), "2V5 LDO  TPS7A9401  (ECP5 VCCAUX, C-2v5-ldo.md)")
    y = 53.34
    S.rail("+3V3", (449.58, y))
    jumper((449.58, y), "+3V3 -> 2V5", below=True)
    u = S.part("studio_C:TPS7A94", "U", "TPS7A94", (490.22, y + 5.08), ref_at=(482.6, 41.91), value_at=(482.6, 43.688))
    inp, enuv, nr = u.pin("1"), u.pin("3"), u.pin("7")
    out, sns, pgp, fbpg = u.pin("10"), u.pin("8"), u.pin("4"), u.pin("5")
    gp, ep = u.pin("6"), u.pin("11")
    S.w((457.2, y), inp)
    S.flag((459.74, y))
    S.cap_down("10u_25V", 462.28, y, dec=f"{u.ref}.1")
    S.w(enuv, (474.98, enuv[1]))
    S.label("PG_3V3", (474.98, enuv[1]), rot=180)
    # NR/SS: R_NR 16.7k 0.1 % -> 2.505 V; C_NR 2.2 uF (above the 1 uF minimum) -> ~5 ms start
    S.w(nr, (477.52, nr[1]))
    vC("2u2_10V_0603", (477.52, nr[1]))
    S.gnd((477.52, nr[1] + 7.62))
    S.w((477.52, nr[1]), (469.9, nr[1]))
    vR_gnd("16.7k_0.1", (469.9, nr[1]))
    S.w(ep, gp, (gp[0], gp[1] + 2.54))
    S.gnd((gp[0], gp[1] + 2.54))
    S.w(out, (533.4, out[1]))
    S.w(sns, (sns[0] + 2.54, sns[1]), (sns[0] + 2.54, out[1]))
    S.cap_down("10u_25V", 515.62, out[1], dec=f"{u.ref}.10")
    S.rail("+2V5", (525.78, out[1]))
    S.tp((533.4, out[1]), "+2V5")
    # FB_PG 715k / 68.1k: PG trip 2.30 V, 60 % current limit (must not float)
    fx = 508.0
    S.w(fbpg, (fx, fbpg[1]))
    vR("715k", (fx, out[1]))
    vR_gnd("68.1k", (fx, fbpg[1]))
    S.nc(pgp)
    S.text("VOUT = 150 uA x 16.7k = 2.505 V, +2V5: 50 mA design\nEN_UV = PG_3V3: ~5 ms ramp, after 3V3 and 1V1\nSNS: Kelvin to the bead input",
           (444.5, 30.48))


# ===================================================================== LM5017 front end
def lm5017(y, link_label, ron_key, rfb_top, rr_key, out_name, en_label=None, uv_keys=None, sw_name="SW",
           flag_fb=True):
    """VBUS link, input caps, RON from VIN, UVLO, BST, VCC, FB divider and Type III network
    (Rr from SW, Cr to VOUT, Cac to FB). Returns (U, SW point)."""
    vbus_in(y, link_label, 60.96)
    u = S.part("studio_C:LM5017", "U", "LM5017", (91.44, y + 10.16),
               ref_at=(76.2, y + 27.94), value_at=(76.2, y + 29.718))
    # the 1u bulk sits furthest out; the 2u2 and 100n are the VIN decouplers
    cap_bank(((40.64, "1u_100V", False), (48.26, "2u2_100V", True), (55.88, "100n_100V", True)), y, f"{u.ref}.2")
    vin, ron, uvlo = u.pin("VIN"), u.pin("RON"), u.pin("UVLO")
    bst, sw, fb, vcc = u.pin("BST"), u.pin("SW"), u.pin("FB"), u.pin("VCC")
    rtn, pad9 = u.pin("RTN"), u.pin("RTNPAD")
    S.w((78.74, y), (78.74, vin[1]), vin)
    S.w(ron, (76.2, ron[1]))
    vR(ron_key, (76.2, y), vtext="left")                     # RON from VIN: sees VBUS, 0805
    if en_label:
        ye = uvlo[1] + 5.08
        S.w(uvlo, (64.77, uvlo[1]), (64.77, ye))
        vR_gnd("100k", (68.58, uvlo[1]), vtext="right")
        hR("10k", (57.15, ye), below=True)
        S.glabel(en_label, (57.15, ye), rot=180, shape="input")
    else:
        top, bot = uv_keys
        S.w(uvlo, (68.58, uvlo[1]))
        vR(top, (68.58, y), vtext="left")
        S.w((68.58, y + 7.62), (68.58, uvlo[1]))
        vR_gnd(bot, (68.58, uvlo[1]), vtext="left")
    S.w(pad9, rtn, (rtn[0], rtn[1] + 2.54))
    S.gnd((rtn[0], rtn[1] + 2.54))
    S.w(vcc, (104.14, vcc[1]))
    S.cap_down("1u_50V_0603", 104.14, vcc[1], dec=f"{u.ref}.6")
    S.w(bst, (104.14, bst[1]))
    vC("10n", (104.14, bst[1] - 7.62))
    S.w((104.14, bst[1] - 7.62), (109.22, bst[1] - 7.62), (109.22, sw[1]))
    S.label(sw_name, (116.84, sw[1]))
    fy = fb[1] + 22.86
    S.w(fb, (106.68, fb[1]), (106.68, fy))
    vR_gnd("10k", (106.68, fy), vtext="right")
    hR(rfb_top, (99.06, fy), below=True)
    S.w((99.06, fy), (93.98, fy))
    S.rail(out_name, (93.98, fy))
    hC("100n", (106.68, fy))
    S.w((114.3, sw[1]), (114.3, sw[1] + 5.08))
    vR(rr_key, (114.3, sw[1] + 5.08))
    S.w((114.3, sw[1] + 12.7), (114.3, fy))
    hC("1n", (114.3, fy))
    S.w((121.92, fy), (127.0, fy))
    S.rail(out_name, (127.0, fy))
    if flag_fb:                              # the output is fed through L: flag it here, clear of L
        S.w((127.0, fy), (137.16, fy))
        S.flag((137.16, fy))
    return u, sw


# ===================================================================== row 2: VDRV
def vdrv():
    y = 109.22
    S.box((12.7, 96.52), (200.66, 177.8), "GATE-DRIVE SUPPLY  VDRV 7.0 V  LM5017 + TLV6703  (C-vdrv-buck.md)")
    u, sw = lm5017(y, "VBUS -> VDRV", "191k_0805", "46.4k", "330k_0805", "VDRV", en_label="VDRV_EN",
                   sw_name="SW_VDRV")
    S.w(sw, (127.0, sw[1]))
    Lh("L47u_SRN6045", (130.81, sw[1]))
    yo = sw[1]
    S.w((134.62, yo), (185.42, yo))
    for x in (142.24, 149.86):
        S.cap_down("10u_25V_1206", x, yo)
    S.rail("VDRV", (157.48, yo))
    S.tp((165.1, yo), "VDRV")
    # TLV6703: good when VDRV >= 6.40 V (150k/10k); OUT pulled up from VDRV, 4.7k/2.7k
    tx = 175.26
    t = S.part("studio_C:TLV6703", "U", "TLV6703", (tx, yo + 27.94), ref_at=(tx + 2.54, yo + 13.97),
               value_at=(tx + 2.54, yo + 15.748))
    sense, out, vdd, gp = t.pin("3"), t.pin("1"), t.pin("5"), t.pin("2")
    S.w(vdd, (vdd[0], yo))
    S.cap_down("100n", tx - 5.08, yo, dec=f"{t.ref}.5")
    sx = tx - 12.7
    S.w(sense, (sx, sense[1]))
    vR("150k", (sx, yo))
    S.w((sx, yo + 7.62), (sx, sense[1]))
    vR_gnd("10k", (sx, sense[1]))
    S.gnd(gp)
    ox = tx + 10.16
    S.w(out, (ox, out[1]))
    vR("4.7k", (ox, yo))
    S.w((ox, yo + 7.62), (ox, out[1]))
    vR_gnd("2.7k", (ox, out[1]), vtext="right")
    S.w((ox, out[1]), (ox + 5.08, out[1]))
    S.glabel("VDRV_PG", (ox + 5.08, out[1]), shape="output")
    S.text("VDRV_EN low = off (100k pull-down).\nFirmware enables after FPGA DONE,\n"
           "PD_PG_N low and POE_LOSS_N high.\nVDRV 7.01-7.12 V typ (Type III offset)\n"
           "VDRV: 200 mA design (76 mA typ, block D)", (15.24, 160.02))


# ===================================================================== row 2: PG buffers
def pg_buffers():
    S.box((203.2, 96.52), (271.78, 177.8), "POWER-GOOD BUFFERS\nECP5 inputs never load PG nets")
    for yq, pgnet, outnet in ((124.46, "PG_5V", "PG_5V_N"), (154.94, "PG_3V3", "PG_3V3_N")):
        q = S.part("Transistor_FET:2N7002", "Q", "2N7002", (233.68, yq), ref_at=(238.76, yq - 1.27),
                   value_at=(238.76, yq + 1.27))
        gte, d, s_ = q.pin("1"), q.pin("3"), q.pin("2")
        S.w(gte, (220.98, gte[1]))
        S.label(pgnet, (220.98, gte[1]), rot=180)
        S.gnd(s_)
        S.w(d, (d[0], d[1] - 2.54), (246.38, d[1] - 2.54))
        vR("4.7k", (d[0], d[1] - 10.16))
        S.rail("+3V3", (d[0], d[1] - 10.16))
        S.glabel(outnet, (246.38, d[1] - 2.54), shape="output")
    S.text("Active low: low = rail good.\n>= 2.6 V vs the 150 uA ECP5\npull-down when not good", (205.74, 168.91))


# ===================================================================== row 2: 3V3_Q, 3V3_A
def ldo_3v3q():
    S.box((274.32, 96.52), (411.48, 177.8), "3V3_Q LDO  TPS7A9401  (DAC reclock, C-3v3q-ldo.md)")
    y = 116.84
    S.rail("+5V", (279.4, y))
    S.w((279.4, y), (281.94, y))
    jumper((281.94, y), "+5V -> 3V3_Q", above=True)  # texts above: the input cap sits right after it
    u = S.part("studio_C:TPS7A94", "U", "TPS7A94", (342.9, y + 5.08), ref_at=(335.28, y - 9.398),
               value_at=(335.28, y - 7.62))
    inp, enuv, nr = u.pin("1"), u.pin("3"), u.pin("7")
    out, sns, pgp, fbpg = u.pin("10"), u.pin("8"), u.pin("4"), u.pin("5")
    gp, ep = u.pin("6"), u.pin("11")
    S.w((289.56, y), inp)
    S.flag((299.72, y))
    S.cap_down("10u_25V", 292.1, y, dec=f"{u.ref}.1")
    # EN_UV from +15V: 47k / 10k (on at +15V >= 7.1 V, off < 6.1 V; block F request)
    ye = enuv[1] + 7.62
    S.w(enuv, (307.34, enuv[1]), (307.34, ye))
    hR("47k", (299.72, ye), below=True)
    S.rail("+15V", (299.72, ye))
    vR_gnd("10k", (312.42, enuv[1]), vtext="right")
    # NR/SS: R_NR 22.0k 0.1 % -> 3.30 V; C_NR 4u7 -> ~14 ms quiet start
    S.w(nr, (327.66, nr[1]))
    vC("4u7_25V", (327.66, nr[1]))
    S.gnd((327.66, nr[1] + 7.62))
    S.w((327.66, nr[1]), (320.04, nr[1]))
    vR_gnd("22k_0.1", (320.04, nr[1]))
    S.w(ep, gp, (gp[0], gp[1] + 2.54))
    S.gnd((gp[0], gp[1] + 2.54))
    S.w(out, (403.86, out[1]))
    S.w(sns, (sns[0] + 2.54, sns[1]), (sns[0] + 2.54, out[1]))
    S.cap_down("22u_10V", 368.3, out[1], dec=f"{u.ref}.10")
    S.cap_down("22u_10V", 375.92, out[1], dec=f"{u.ref}.10")
    S.rail("+3V3_Q", (393.7, out[1]))
    S.tp((403.86, out[1]), "+3V3_Q")
    # FB_PG 931k / 68.1k: PG at 2.93 V, ICL 60 %
    fx = 360.68
    S.w(fbpg, (fx, fbpg[1]))
    vR("931k", (fx, out[1]))
    vR_gnd("68.1k", (fx, fbpg[1]))
    # PG -> PG_3V3Q (100k to +3V3) -> FPGA B5
    S.w(pgp, (355.6, pgp[1]), (355.6, 149.86), (383.54, 149.86))
    vR("100k", (383.54, 142.24))
    S.rail("+3V3", (383.54, 142.24))
    S.w((383.54, 149.86), (391.16, 149.86))
    S.glabel("PG_3V3Q", (391.16, 149.86), shape="output")
    S.text("SNS: Kelvin trace to the 74LVC74 row (block F)\nCOUT ceramic, ESR <= 20 mOhm\n"
           "+3V3_Q: 35 mA design", (276.86, 162.56))


def ldo_3v3a():
    S.box((426.72, 96.52), (508.0, 165.1), "3V3_A LDO  TPS7A2033P\n(block D sense reference, C-3v3a-ldo.md)")
    y = 119.38
    S.rail("+5V", (434.34, y))
    jumper((434.34, y), "+5V -> 3V3_A", below=True)
    u = S.part("studio_C:TPS7A20", "U", "TPS7A2033", (469.9, y + 1.27), ref_at=(474.98, y - 9.398),
               value_at=(474.98, y - 7.62))
    inp, en, out, gp, nc = u.pin("1"), u.pin("3"), u.pin("5"), u.pin("2"), u.pin("4")
    S.w((441.96, y), inp)
    S.flag((444.5, y))
    S.cap_down("1u_50V_0603", 452.12, y, dec=f"{u.ref}.1")
    S.w(en, (457.2, en[1]), (457.2, y))
    S.gnd(gp)
    S.nc(nc)
    S.w(out, (495.3, out[1]))
    S.cap_down("4u7_25V", 482.6, out[1], dec=f"{u.ref}.5")
    S.rail("+3V3_A", (490.22, out[1]))
    S.tp((495.3, out[1]), "+3V3_A")
    S.text("Always on with +5V: block D's ADCs\nare powered whenever the FPGA\ndrives them. +3V3_A: 15 mA design",
           (429.26, 139.7))


# ===================================================================== row 3: Fly-Buck
def flybuck():
    y = 195.58
    S.box((12.7, 182.88), (200.66, 284.48), "+-15 V PRE-REGULATOR  LM5017 FLY-BUCK  (C-pm15-flybuck.md)")
    u, sw = lm5017(y, "VBUS -> Fly-Buck", "330k_0805", "137k", "390k_0805", "+18V_PRE",
                   uv_keys=("124k_0805", "5.36k"), sw_name="SW_AN", flag_fb=False)
    L = S.part("studio_C:L_Coupled_13_24", "L", "L68u_coupled", (137.16, sw[1] + 2.54), value="68u 1:1",
               ref_at=(132.08, sw[1] - 6.858), value_at=(132.08, sw[1] - 5.08))
    p1, p3, p2, p4 = L.pin("1"), L.pin("3"), L.pin("2"), L.pin("4")
    S.w(sw, (p1[0] - 2.54, sw[1]), (p1[0] - 2.54, p1[1]), p1)
    # primary (1 -> 3): +18V_PRE
    S.w(p3, (182.88, p3[1]))
    for x in (152.4, 160.02):
        S.cap_down("10u_50V", x, p3[1])
    S.rail("+18V_PRE", (172.72, p3[1]))
    S.flag((147.32, p3[1]))
    S.tp((182.88, p3[1]), "+18V_PRE", keystone=False)
    # secondary (2 -> 4): non-dot end 4 to GND; dot end 2 -> B1100 cathode; anode -> -18V_PRE
    S.w(p4, (p4[0] + 2.54, p4[1]), (p4[0] + 2.54, p4[1] + 2.54))
    S.gnd((p4[0] + 2.54, p4[1] + 2.54))
    yd = 236.22
    xk = p2[0] - 2.54
    S.w(p2, (xk, p2[1]), (xk, yd))
    S.part("Device:D_Schottky", "D", "B1100", (xk + 3.81, yd), ref_at=(xk + 1.27, yd - 5.588),
           value_at=(xk + 1.27, yd - 3.81))
    xa = xk + 7.62
    # RC snubber across D (C-pm15-flybuck.md), DNP: fit at bring-up if the leakage ringing needs it.
    # 100R 1206 (~0.27 W at 50 V, 498 kHz with 220p), 220p C0G 100 V
    S.R("100R_1206", (xk, yd + 3.81), dnp=True, ref_at=(xk - 3.81, yd + 2.921), value_at=(xk - 3.81, yd + 4.699),
        justify="right", vtext=False, fields={"Note": "DNP: snubber option"})
    S.w((xk, yd + 7.62), (xk, yd + 10.16))
    hC("220p_100V", (xk, yd + 10.16), dnp=True, ref_at=(xk + 3.81, yd + 14.224), value_at=(xk + 3.81, yd + 16.002),
       justify="", fields={"Note": "DNP: snubber option"})
    S.w((xa, yd + 10.16), (xa, yd))
    S.w((xa, yd), (185.42, yd))
    for x in (152.4, 160.02):
        S.cap_down("10u_50V", x, yd)
    vR_gnd("10k", (167.64, yd))
    S.rail("-18V_PRE", (175.26, yd))
    S.flag((144.78, yd))
    S.tp((185.42, yd), "-18V_PRE", keystone=False)
    S.text("Windings 1-3 primary, 2-4 secondary (dots at 1, 2).\nSecondary dot end -> D cathode, non-dot -> GND:\n"
           "rectified output is negative. 10k preload.\n+18V_PRE +18.4 V: 135 mA design (incl. +5V_A)\n"
           "-18V_PRE -17.8 V: 110 mA design", (113.03, 259.08))
    S.text("UVLO on 29.8 V / off 27.3 V (124k / 5.36k)", (15.24, 276.86))


# ===================================================================== row 3: LDOs
def ldo(x0, y, in_name, out_name, rtop, rbot, sym, key, ferrite=True, cin="10u_50V", cout="10u_50V", note=""):
    """TPS7A49/30: input ferrite + cap, EN = IN, NR 10n, divider with CFF 10n, COUT, test point."""
    if ferrite:
        S.rail(in_name, (x0 - 5.08, y))
        S.part("Device:FerriteBead_Small", "FB", "FB_220R", (x0 + 7.62, y), rot=90,
               ref_at=(x0 + 7.62, y - 6.096), value_at=(x0 + 7.62, y - 4.318), justify="")
        S.w((x0 - 5.08, y), (x0 + 5.08, y))
        xin = x0 + 12.7
        S.w((x0 + 10.16, y), (xin, y))
        S.flag((xin + 7.62, y))
    else:
        S.rail(in_name, (x0, y))
        xin = x0
    u = S.part(sym, "U", key, (xin + 25.4, y + 2.54), ref_at=(xin + 29.21, y + 13.97),
               value_at=(xin + 29.21, y + 15.748))
    inp, en, nr = u.pin("8"), u.pin("5"), u.pin("6")
    out, fb = u.pin("1"), u.pin("2")
    gp, ep = u.pin("4"), u.pin("9")
    S.w((xin, y), inp)
    S.cap_down(cin, xin + 2.54, y, dec=f"{u.ref}.8")
    S.w(en, (en[0] - 2.54, en[1]), (en[0] - 2.54, y))                 # EN tied to IN
    S.w(nr, (nr[0] - 5.08, nr[1]))
    S.cap_down("10n", nr[0] - 5.08, nr[1], vtext="right")
    S.w(ep, gp, (gp[0], gp[1] + 2.54))
    S.gnd((gp[0], gp[1] + 2.54))
    S.nc(u.pin("3"))
    S.nc(u.pin("7"))
    fx = out[0] + 5.08
    xt = out[0] + 35.56
    S.w(out, (xt, out[1]))
    vR(rtop, (fx, out[1]), vtext="right")
    cx = fx + 7.62
    S.w(fb, (fb[0] + 2.54, fb[1]), (fb[0] + 2.54, fb[1] + 5.08), (fx, fb[1] + 5.08))
    vR_gnd(rbot, (fx, fb[1] + 5.08), vtext="right")
    vC("10n", (cx, out[1]), vtext="right")
    S.w((cx, out[1] + 7.62), (cx, fb[1] + 5.08), (fx, fb[1] + 5.08))
    S.cap_down(cout, out[0] + 22.86, out[1], dec=f"{u.ref}.1")
    S.rail(out_name, (out[0] + 30.48, out[1]))
    S.tp((xt, out[1]), out_name, rot=180)
    if note:
        S.text(note, (x0, y + 27.94))
    return u


def analog_ldos():
    S.box((203.2, 182.88), (370.84, 284.48), "+15 V / -15 V LDOs  TPS7A4901 / TPS7A3001  (C-pm15-ldos.md)")
    ldo(215.9, 203.2, "+18V_PRE", "+15V", "113k", "9.76k", "studio_C:TPS7A4901", "TPS7A4901",
        note="+15V = 1.188 x (1 + 113k/9.76k) = 14.94 V\n120 mA design incl. +5V_A, 200 mA fault")
    ldo(215.9, 248.92, "-18V_PRE", "-15V", "118k", "10k", "studio_C:TPS7A3001", "TPS7A3001",
        note="-15V = -1.179 x (1 + 118k/10k) = -15.09 V\n110 mA design, 190 mA fault; DNC (7) open")
    S.box((373.38, 182.88), (469.9, 284.48), "+5V_A LDO  TPS7A4901\n(PCM1808 analog, mic bias)")
    ldo(381.0, 203.2, "+15V", "+5V_A", "32.4k", "10k", "studio_C:TPS7A4901", "TPS7A4901",
        ferrite=False, cin="10u_50V_1206", cout="10u_25V_1206",
        note="+5V_A = 1.188 x (1 + 32.4k/10k)\n= 5.04 V, <= 15 mA, 15 uVrms")


def notes():
    S.box((472.44, 182.88), (576.58, 233.68), "SEQUENCING  (C-sequencing.md)")
    S.text("VBUS >= 30.2 V: LM5013 -> +5V_BUCK -> PG_5V\n"
           "  -> TPS2116 selects the buck (else VUSB)\n"
           "+5V -> 3V3 -> PG_3V3 -> 1V1 (~1 ms), 2V5 (~5 ms)\n"
           "VBUS >= 29.8 V: Fly-Buck -> +-15 V (14 ms)\n"
           "  -> +5V_A; +15V >= 7.1 V enables 3V3_Q\n"
           "VDRV off until VDRV_EN (firmware, after\n"
           "  FPGA DONE, PD_PG_N low, POE_LOSS_N high)\n"
           "USB only: +5V, 3V3, 1V1, 2V5, 3V3_A\n\n"
           "Hold-up >= 34 ms after the VBUS < 40 V\n"
           "trip at 60 W on 6 mF (UVLO-off <= 30.2 V)\n\n"
           "R-80: 0R / bridged-jumper link at every\n"
           "converter input; test point on every rail;\n"
           "SW-node pads with GND springs on io sheet", (474.98, 193.04))


# rows are drawn in local coordinates and spread down the A2 page
S.off = (0.0, 5.08)
five_volt()
source_select()
logic_rails()
S.off = (0.0, 15.24)
vdrv()
pg_buffers()
ldo_3v3q()
S.off = (-27.94, 99.06)          # 2V5 LDO (from +3V3) ends row 2
ldo_2v5()
S.off = (0.0, 30.48)
flybuck()
analog_ldos()
S.off = (45.72, 116.84)          # 3V3_A (from +5V) ends row 3
ldo_3v3a()
S.off = (-459.74, 137.16)        # sequencing notes, row 4
notes()
S.off = (0.0, 0.0)
S.save()
print("wrote", S.sch.file.name, sum(1 for p in S.sch.parts if not p.ref.startswith("#")), "parts")
