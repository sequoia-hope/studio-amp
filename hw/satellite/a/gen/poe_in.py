"""poe_in.py -- block A sheet: RJ45 magjack, two ideal-diode bridges (LT4321 + 8 N-FETs),
input TVS, TPS2373-4 PD, CBULK, and the ISO7740 status isolator.

Audits (source of every value): design/parts/A-*.md.
Run from the repo root: python3 hw/satellite/a/gen/poe_in.py

Layout (A2, signal flow left to right, VPRI rail along the top, primary negative nets below):
  x  10-92   J101 magjack; secondary island below its barrier line (PHY pairs, LEDs, shield network)
  x  96-220  four FET columns (one per centre tap; the two pair sets drawn apart), VPD_N rail below
  x 240-340  LT4321 and its enable network (zener, 1 M, BSS123 hot-swap gate)
  x 340-475  TVS + C_PD, TPS2373-4 with class/detection/REF parts, bias caps, PG (CBULK is on iso_dcdc)
  x 360-530  isolator section below the PD: 78L05, pull-ups, 2N7002 PG buffer, ISO7740 (barrier)
"""
from __future__ import annotations

import hier
from kicad_write import S, Sym, new_uuid

sch = hier.SubSheet("poe_in", paper="A2", comments=[
    "Block A. Audits: design/parts/A-*.md (values, calculations, datasheet pages)",
    "Primary = VPRI / VPD_N / VPRI_RTN; secondary = GND. Barrier R-32: 1500 Vrms (dashed)"])

R0603, R0805, R1206 = ("Resistor_SMD:R_0603_1608Metric", "Resistor_SMD:R_0805_2012Metric",
                       "Resistor_SMD:R_1206_3216Metric")
C0603, C0805, C1206 = ("Capacitor_SMD:C_0603_1608Metric", "Capacitor_SMD:C_0805_2012Metric",
                       "Capacitor_SMD:C_1206_3216Metric")
GROUND_NETS = ("GND", "VPD_N", "VPRI_RTN")


def f(mpn, mfr, lcsc, **extra):
    d = {"MPN": mpn, "Manufacturer": mfr, "LCSC": lcsc}
    d.update(extra)
    return d


def _set_justify(p, j):
    for prop in p.node:
        if isinstance(prop, list) and prop and str(prop[0]) == "property" and prop[1] in ("Reference", "Value"):
            for e in prop:
                if isinstance(e, list) and str(e[0]) == "effects":
                    e[:] = [x for x in e if not (isinstance(x, list) and str(x[0]) == "justify")]
                    e.append([Sym("justify"), Sym(j)])


def part(lib, ref, value, at, fp, fields, rot=0, mirror=None, ref_at=None, value_at=None, dnp=False, left=False,
         just=None):
    """left=True: text ends at ref_at (right-justified) on an unrotated, unmirrored symbol.
    just=...: the justification written to the file, for rotated/mirrored symbols, where KiCad flips it
    on screen (a 270-degree part or a mirror-y part shows "left" as right-justified)."""
    p = sch.symbol(lib, ref, value, at, rot=rot, mirror=mirror, footprint=fp, fields=fields,
                   ref_at=ref_at, value_at=value_at, dnp=dnp)
    if just:
        _set_justify(p, just)
    elif left:
        _set_justify(p, "right")
    return p


def res(ref, value, at, fp, fields, rot=0, left=False, dnp=False):
    """Vertical (rot 0) or horizontal (rot 90) resistor; fields right of it, or left if asked."""
    x, y = at
    if rot == 90:
        return part("Device:R", ref, value, at, fp, fields, rot=90,
                    ref_at=(x - 3.81, y - 4.57), value_at=(x - 3.81, y - 2.03), dnp=dnp)
    if left:
        return part("Device:R", ref, value, at, fp, fields, ref_at=(x - 2.54, y - 1.27),
                    value_at=(x - 2.54, y + 1.27), dnp=dnp, left=True)
    return part("Device:R", ref, value, at, fp, fields, ref_at=(x + 2.54, y - 1.27), value_at=(x + 2.54, y + 1.27),
                dnp=dnp)


def cap(ref, value, at, fp, fields, lib="Device:C", left=False):
    x, y = at
    if left:
        return part(lib, ref, value, at, fp, fields, ref_at=(x - 2.54, y - 1.27), value_at=(x - 2.54, y + 1.27),
                    left=True)
    return part(lib, ref, value, at, fp, fields, ref_at=(x + 2.54, y - 1.27), value_at=(x + 2.54, y + 1.27))


def pwr(name, at):
    if name in GROUND_NETS:
        p = sch.power("power:GND", at, value=None if name == "GND" else name)
        for prop in p.node:   # ground-type value text below the symbol, not on top of the part
            if isinstance(prop, list) and prop and str(prop[0]) == "property" and prop[1] == "Value":
                for e in prop:
                    if isinstance(e, list) and str(e[0]) == "at":
                        e[1:3] = [at[0], at[1] + 4.45]
        return p
    if name == "+3V3":
        return sch.power("power:+3V3", at)
    return sch.power("power:VCC", at, value=name)


def flag(at):
    sch.symbol("power:PWR_FLAG", f"#FLG{len(sch.parts):03d}", "PWR_FLAG", at, ref_at=at,
               value_at=(at[0], at[1] - 3.81), in_bom=False, on_board=False, justify="")


W = sch.wire
VPRI_Y = 40.64        # VPRI rail
OUTN_Y = 104.14       # VPD_N rail under the FET columns

sch.text("PoE++ input, block A (references 100-199).  VPRI = bridge output = TPS2373 VDD;  VPD_N = bridge "
         "OUTN = TPS2373 VSS;  VPRI_RTN = TPS2373 RTN (after the hot-swap) = block B's primary return.",
         (12.7, 25.4), size=1.778)

# ================================================================ J101 magjack
J1 = part("studio_A:LPJK6078AHNL", "J101", "LPJK6078AHNL", (50.8, 104.14), "studio_A:LINKPP_LPJK6078AHNL_RJ45_PoE",
          f("LPJK6078AHNL", "LINK-PP", "C49274795"), ref_at=(38.1, 63.5), value_at=(45.72, 63.5))
for pn, net in (("13", "POE_CT12"), ("14", "POE_CT36"), ("15", "POE_CT45"), ("16", "POE_CT78")):
    x, y = J1.pin(pn)
    W((x, y), (x + 7.62, y))
    sch.label(net, (x + 7.62, y))
for pn, net in (("11", "ETH_TXP"), ("10", "ETH_TXN"), ("4", "ETH_RXP"), ("5", "ETH_RXN")):
    x, y = J1.pin(pn)
    W((x, y), (x + 10.16, y))
    sch.label(net, (x + 10.16, y), kind="global_label", shape="bidirectional")
# PHY-side centre taps and the yellow LED anode: the PHY's filtered analog 3.3 V (block E's ETH_AVDD;
# CT bypass caps are on the ethernet sheet, placed at J101 pins 12 and 6)
(c1x, c1y), (c2x, c2y) = J1.pin("12"), J1.pin("6")
W((c1x, c1y), (c1x + 5.08, c1y), (c1x + 5.08, c2y), (c2x, c2y))
pwr("ETH_AVDD", (c1x + 5.08, c1y))
for pn in ("3", "2", "1", "8", "9", "7"):
    sch.no_connect(J1.pin(pn))
x, y = J1.pin("18")
W((x, y), (x - 5.08, y))
pwr("ETH_AVDD", (x - 5.08, y))
for pn, net, shape in (("20", "ETH_LED_G_A", "input"), ("17", "ETH_LED_Y_K", "output")):
    x, y = J1.pin(pn)
    W((x, y), (x - 7.62, y))
    sch.label(net, (x - 7.62, y), rot=180, kind="global_label", shape=shape)
x, y = J1.pin("19")
W((x, y), (x - 5.08, y), (x - 5.08, y + 5.08))
pwr("GND", (x - 5.08, y + 5.08))

# ---- shield network (secondary)
sx, sy = J1.pin("SH")
W((sx, sy), (sx, 152.4))
C101 = cap("C101", "1n 2kV X7R 1206", (sx, 156.21), C1206, f("1206B102K202NT", "FH", "C9196"), left=True)
W((sx, 152.4), C101.pin("1"))
pwr("GND", C101.pin("2"))
W((sx, 149.86), (66.04, 149.86))
r_sh = [res("R101", "2.0M 1% 1206", (66.04, 153.67), R1206, f("FRC1206F2004TS", "FOJAN", "C2907380")),
        res("R102", "2.0M 1% 1206", (66.04, 161.29), R1206, f("FRC1206F2004TS", "FOJAN", "C2907380")),
        res("R103", "2.0M 1% 1206", (66.04, 168.91), R1206, f("FRC1206F2004TS", "FOJAN", "C2907380")),
        res("R104", "2.0M 1% 1206", (66.04, 176.53), R1206, f("FRC1206F2004TS", "FOJAN", "C2907380")),
        res("R105", "2.0M 1% 1206", (66.04, 184.15), R1206, f("FRC1206F2004TS", "FOJAN", "C2907380"))]
W((66.04, 149.86), r_sh[0].pin("1"))
pwr("GND", r_sh[-1].pin("2"))
sch.text("SHIELD -> GND: C101 1 nF 2 kV || R101-R105 (10 Mohm).\n"
         "R-32 hipot: <= 1.2 kVpk on J101's internal 1 nF,\n<= 1.23 kVpk on C101. AC hipot only.\n"
         "ESD +-8 kV: 1.33 kV peak, 267 V per resistor.\nA-shield-network.md", (12.7, 203.2))
sch.text("MD3/MD4 windings unused (100BASE-TX\nuses pairs 1-2 and 3-6); their line-side\n"
         "CTs still carry power (CT4-5, CT7-8).", (12.7, 224.79))
sch.box((10.16, 96.52), (91.44, 236.22), "SECONDARY (GND)")
sch.text("Isolation barrier (R-32, 1500 Vrms):\nthis box edge, through J101", (12.7, 189.23))

# ================================================================ FET bridges
cols = [  # FET x, centre-tap net, gate nets, refs (pair set A: CT12/CT36, pair set B: CT45/CT78)
    (101.6, "POE_CT12", "TG12", "BG12", "Q101", "Q102"),
    (134.62, "POE_CT36", "TG36", "BG36", "Q103", "Q104"),
    (180.34, "POE_CT45", "TG45", "BG45", "Q105", "Q106"),
    (213.36, "POE_CT78", "TG78", "BG78", "Q107", "Q108"),
]
FET = f("PSMN040-100MSEX", "Nexperia", "C458214")
for x, ct, tg, bg, rhs, rls in cols:
    hs = part("studio_A:PSMN040-100MSE", rhs, "PSMN040", (x, 53.34), "Package_TO_SOT_SMD:LFPAK33", FET,
              ref_at=(x + 5.08, 52.07), value_at=(x + 5.08, 54.61))
    ls = part("studio_A:PSMN040-100MSE", rls, "PSMN040", (x, 78.74), "Package_TO_SOT_SMD:LFPAK33", FET,
              ref_at=(x + 5.08, 77.47), value_at=(x + 5.08, 80.01))
    d = hs.pin("5")
    W(d, (d[0], VPRI_Y))
    W(hs.pin("1"), ls.pin("5"))
    sch.label(ct, (d[0], 66.04))
    W(ls.pin("1"), (ls.pin("1")[0], OUTN_Y))
    sch.label(tg, hs.pin("4"), rot=180)
    sch.label(bg, ls.pin("4"), rot=180)
W((cols[0][0] + 2.54, OUTN_Y), (cols[-1][0] + 2.54, OUTN_Y))
pwr("VPD_N", (cols[-1][0] + 2.54, OUTN_Y))
flag((157.48, OUTN_Y))
flag((157.48, VPRI_Y))
sch.box((93.98, 33.02), (226.06, 109.22), None)
sch.text("PAIR SET A (pins 1-2 / 3-6)", (99.06, 36.83), size=1.524)
sch.text("PAIR SET B (pins 4-5 / 7-8)", (177.8, 36.83), size=1.524)
sch.text("Two ideal-diode bridges. High-side FET: drain VPRI, source CT; low-side: drain CT, source VPD_N.\n"
         "PSMN040-100MSE: 25-57 mV drop at 0.865 A per pair set, 0.20 W for all eight hot (A-bridge-lt4321.md).\n"
         "Layout: each pair set's 4 FETs round its two CT pins; TG/BG traces short to U101.", (96.52, 113.03))

# ================================================================ LT4321
U101 = part("studio_A:LT4321", "U101", "LT4321IUF", (254.0, 71.12),
            "Package_DFN_QFN:QFN-16-1EP_4x4mm_P0.65mm_EP2.15x2.15mm",
            f("LT4321IUF#TRPBF", "Analog Devices", "C580183"), ref_at=(243.84, 46.99), value_at=(256.54, 46.99))
for pn, net in (("15", "POE_CT12"), ("2", "POE_CT36"), ("3", "POE_CT45"), ("6", "POE_CT78")):
    sch.label(net, U101.pin(pn), rot=180)
for pn, net in (("16", "TG12"), ("14", "BG12"), ("1", "TG36"), ("13", "BG36"),
                ("4", "TG45"), ("8", "BG45"), ("5", "TG78"), ("7", "BG78")):
    sch.label(net, U101.pin(pn))
op = U101.pin("12")
W(op, (op[0], VPRI_Y))
pwr("VPD_N", U101.pin("9"))

# ~EN tied to OUTP (LT4321 p.5); EN network (A-bridge-lt4321.md calc 3)
nx, ny = U101.pin("10")
W((nx, ny), (279.4, ny), (279.4, VPRI_Y))
ex, ey = U101.pin("11")
W((ex, ey), (304.8, ey))
R107 = res("R107", "1M 1% 0603", (274.32, ey + 7.62), R0603, f("0603WAF1004T5E", "UNI-ROYAL", "C22935"), left=True)
W((274.32, ey), R107.pin("1"))
pwr("VPD_N", R107.pin("2"))
Q109 = part("Transistor_FET:BSS123", "Q109", "BSS123", (292.1, ey + 12.7), "Package_TO_SOT_SMD:SOT-23",
            f("BSS123,215", "Nexperia", "C78962"), mirror="y", ref_at=(287.02, ey + 11.43),
            value_at=(287.02, ey + 13.97), just="left")
W(Q109.pin("3"), (Q109.pin("3")[0], ey))
pwr("VPD_N", Q109.pin("2"))
gx, gy = Q109.pin("1")
W((gx, gy), (325.12, gy))
D102 = part("Device:D_Zener", "D102", "BZT52C10", (304.8, gy + 3.81), "Diode_SMD:D_SOD-123",
            f("BZT52C10", "MDD", "C173431"), rot=270, ref_at=(307.34, gy + 2.54), value_at=(307.34, gy + 5.08), just="right")
W((304.8, gy), D102.pin("1"))
pwr("VPD_N", D102.pin("2"))
C102 = cap("C102", "1n 50V X7R", (320.04, gy + 3.81), C0603, f("CL10B102KB8NNNC", "Samsung", "C1588"))
W((320.04, gy), C102.pin("1"))
pwr("VPD_N", C102.pin("2"))
R108 = res("R108", "2.2M 1% 0805", (328.93, gy), R0805, f("0805W8F2204T5E", "UNI-ROYAL", "C26113"), rot=90)
W(R108.pin("2"), (337.82, gy), (337.82, gy + 2.54))
pwr("VPRI_RTN", (337.82, gy + 2.54))
R106 = res("R106", "100k 1% 0603", (308.61, ey), R0603, f("0603WAF1003T5E", "UNI-ROYAL", "C25803"), rot=90)
D101 = part("Device:D_Zener", "D101", "BZT52C27", (320.04, ey - 7.62), "Diode_SMD:D_SOD-123",
            f("BZT52C27", "MDD", "C173421"), rot=270, ref_at=(317.5, ey - 8.89), value_at=(317.5, ey - 6.35),
            just="left")
W(R106.pin("2"), (320.04, ey), D101.pin("2"))
W(D101.pin("1"), (320.04, VPRI_Y))
sch.text("LT4321 enable (A-bridge-lt4321.md calc 3): on for VPRI >= 32.8 V (D101, R106),\n"
         "held off below 21 V (R107). Q109 pulls EN low whenever the TPS2373 hot-swap is\n"
         "open (RTN-VSS > 2.8 V), so the bridges run only with CBULK connected (LT4321 p.7).\n"
         "R108 2.2 M keeps the detection signature at 24.4-24.9 k.", (241.3, 120.65))

# ================================================================ TVS and C_PD
D103 = part("Device:D_Zener", "D103", "SMCJ58A TVS", (342.9, 55.88), "Diode_SMD:D_SMC",
            f("SMCJ58A-13-F", "Diodes Inc", "C135180"), rot=270, ref_at=(340.36, 54.61), value_at=(340.36, 57.15),
            just="left")
W(D103.pin("1"), (342.9, VPRI_Y))
pwr("VPD_N", D103.pin("2"))
C103 = cap("C103", "100n 100V X7R 0805", (358.14, 55.88), C0805,
           f("CL21B104KCFNNNE", "Samsung", "C28233", Decouples="U102.1"))
W(C103.pin("1"), (358.14, VPRI_Y))
pwr("VPD_N", C103.pin("2"))
sch.text("D103: <= 93.6 V at 16 A\n(abs max 100 V).\nC103 = C_PD, the only cap\non VDD-VSS (0.05-0.12 uF).\n"
         "Place both at U101.", (330.2, 73.66))

# ================================================================ TPS2373-4
U102 = part("studio_A:TPS2373-4", "U102", "TPS2373-4", (396.24, 96.52),
            "studio_A:TI_RGW0020B_VQFN-20-1EP_5x5mm_P0.65mm_EP2.2x2.2mm",
            f("TPS2373-4RGWR", "Texas Instruments", "C470963"), ref_at=(383.54, 66.04), value_at=(383.54, 63.5),
            left=True)
vx, vy = U102.pin("1")
W((vx, vy), (vx, VPRI_Y))
R109 = res("R109", "24.9k 1% 0603", (375.92, 48.26), R0603, f("0603WAF2492T5E", "UNI-ROYAL", "C25962"), left=True)
W(R109.pin("1"), (375.92, VPRI_Y))
dx, dy = U102.pin("2")
W(R109.pin("2"), (375.92, dy), (dx, dy))
# CLSA / CLSB / REF to VSS: a staircase onto one VPD_N bus, so no wire crosses a resistor
BUS_Y = 121.92
for pn, ref, val, mpn, mfr, lcsc, fp, rx_, drop in (
        ("3", "R110", "63.4R 1% 0805", "FRC0805F63R4TS", "FOJAN", "C5159721", R0805, 353.06, 8.89),
        ("6", "R111", "90.9R 1% 0805", "FRC0805F90R9TS", "FOJAN", "C3000584", R0805, 363.22, 11.43),
        ("7", "R112", "49.9k 1% 0603", "0603WAF4992T5E", "UNI-ROYAL", "C23184", R0603, 373.38, 13.97)):
    px, py = U102.pin(pn)
    r = res(ref, val, (rx_, py + drop), fp, f(mpn, mfr, lcsc), left=True)
    W((px, py), (rx_, py), r.pin("1"))
    W(r.pin("2"), (rx_, BUS_Y))
W((353.06, BUS_Y), (373.38, BUS_Y))
pwr("VPD_N", (353.06, BUS_Y))
# AMPS_CTL: R113 DNP (auto-MPS off, R-30)
px, py = U102.pin("8")
R113 = res("R113", "1.3k DNP", (424.18, py + 3.81), R1206, f("FRC1206F1301TS", "FOJAN", "C2933592"),
           left=True, dnp=True)
W((px, py), R113.pin("1"))
pwr("VPD_N", R113.pin("2"))
for pn in ("9", "20", "16"):
    sch.no_connect(U102.pin(pn))
pwr("VPD_N", U102.pin("4"))
rtx, rty = U102.pin("11")
pwr("VPRI_RTN", (rtx, rty))
ax, ay = U102.pin("10")
W((ax, ay), (ax + 5.08, ay))
pwr("VPRI_RTN", (ax + 5.08, ay))
sch.text("Class 8: CLSA 63.4R, CLSB 90.9R (TPS2373 Table 1). RDEN 24.9k\n"
         "(trim to 24.3k if the signature reads high). AMPS_CTL: R113 DNP,\n"
         "auto-MPS off (R-30). MPS_DUTY, UVLO_SEL open; APD to RTN.\n"
         "A-pd-tps2373.md, A-pd-passives.md", (340.36, 137.16))
# bias: VC_OUT unused (1 uF to RTN only); VC_IN = VB_PRI from block B
ox, oy = U102.pin("14")
W((ox, oy), (ox, 50.8), (429.26, 50.8))
C104 = cap("C104", "1u 50V X7R 0805", (429.26, 54.61), C0805,
           f("CL21B105KBFNNNE", "Samsung", "C28323", Decouples="U102.14"))
pwr("VPRI_RTN", C104.pin("2"))
ix, iy = U102.pin("15")
W((ix, iy), (ix, 60.96), (416.56, 60.96))
pwr("VB_PRI", (ix, 60.96))
C105 = cap("C105", "100n 50V X7R", (416.56, 64.77), C0603,
           f("CC0603KRX7R9BB104", "YAGEO", "C14663", Decouples="U102.15"))
pwr("VPRI_RTN", C105.pin("2"))
sch.text("VC_OUT unused (1 uF only). VC_IN = VB_PRI,\n14.3 V from block B (TPS2373 7.3.7).", (434.34, 64.77))
gx_, gy_ = U102.pin("13")
W((gx_, gy_), (414.02, gy_))
sch.label("PD_PG", (414.02, gy_), kind="global_label", shape="output")

# ================================================================ CBULK and the VPRI rail
VPRI_END = 474.98
W((cols[0][0] + 2.54, VPRI_Y), (VPRI_END, VPRI_Y))
pwr("VPRI", (VPRI_END, VPRI_Y))
sch.text("CBULK (61 uF) is drawn on iso_dcdc: block B's C215 47 uF 100 V Al\n"
         "+ C211-C213 3 x 4.7 uF at T1 (>= 10 uF for U101, <= 120 uF; inrush 12.7 ms).", (403.86, 29.21))
sch.text("VPRI, VPRI_RTN, VB_PRI: block B (iso_dcdc)", (477.52, 43.18))

# ================================================================ status pull-ups, PG buffer, isolator
VISO = "VISO_P5V"
U103 = part("studio_A:ISO7740DW", "U103", "ISO7740DWR", (497.84, 180.34), "Package_SO:SOIC-16W_7.5x10.3mm_P1.27mm",
            f("ISO7740DWR", "Texas Instruments", "C529547"), ref_at=(486.41, 199.39), value_at=(486.41, 201.93),
            left=True)
# each status row turns down at its own x (top row first), so nothing crosses
for pn, iso_pin, vx_, ref in (("18", "5", 431.8, "R114"),     # TPH -> INC
                              ("17", "4", 449.58, "R115"),    # TPL -> INB
                              ("19", "3", 467.36, "R116")):   # BT  -> INA
    px, py = U102.pin(pn)
    tx, ty = U103.pin(iso_pin)
    W((px, py), (vx_, py), (vx_, ty), (tx, ty))
    r = res(ref, "10k 1% 0603", (vx_, py - 3.81), R0603, f("0603WAF1002T5E", "UNI-ROYAL", "C25804"))
    pwr(VISO, r.pin("1"))
Q110 = part("Transistor_FET:2N7002", "Q110", "2N7002", (421.64, 185.42), "Package_TO_SOT_SMD:SOT-23",
            f("2N7002", "JSCJ", "C8545"), ref_at=(426.72, 189.23), value_at=(426.72, 191.77))
sch.label("UCC_SS", Q110.pin("1"), rot=180, kind="global_label", shape="input")
qd = Q110.pin("3")
W(qd, U103.pin("6"))
R117 = res("R117", "10k 1% 0603", (qd[0], qd[1] - 3.81), R0603, f("0603WAF1002T5E", "UNI-ROYAL", "C25804"),
           left=True)
pwr(VISO, R117.pin("1"))
pwr("VPRI_RTN", Q110.pin("2"))
sch.text("PD_PG_N LOW = SS/SD above the 2N7002 threshold (1-2.5 V):\n"
         "PD out of inrush and UCC2897A running. UCC_SS is block B's\n"
         "SS/SD node after its 1 k from PD_PG; the gate draws <= 80 nA.", (393.7, 210.82))
U104 = part("Regulator_Linear:L78L05_SOT89", "U104", "78L05", (391.16, 157.48), "Package_TO_SOT_SMD:SOT-89-3",
            f("78L05G-AB3-R", "UTC", "C71136"), ref_at=(387.35, 149.86), value_at=(387.35, 152.4))
ux, uy = U104.pin("3")
W((ux, uy), (375.92, uy))
pwr("VB_PRI", (375.92, uy))
C107 = cap("C107", "330n 50V X7R 0805", (378.46, uy + 3.81), C0805,
           f("0805B334K500NT", "FH", "C1740", Decouples="U104.3"), left=True)
pwr("VPRI_RTN", C107.pin("2"))
pwr("VPRI_RTN", U104.pin("2"))
oxx, oyy = U104.pin("1")
W((oxx, oyy), (403.86, oyy))
C108 = cap("C108", "100n 50V X7R", (403.86, oyy + 3.81), C0603,
           f("CC0603KRX7R9BB104", "YAGEO", "C14663", Decouples="U104.1"))
pwr("VPRI_RTN", C108.pin("2"))
pwr(VISO, (403.86, oyy))
sch.text("U104 78L05: SOT-89 O-G-I pinout is the -AB3-R order only.\n"
         "VISO_P5V (primary): <= 15.3 mA, 177 mW at VB_PRI 14.8 V.", (322.58, 172.72))
# ISO7740 supplies: VCC1 primary (VISO_P5V, RTN), VCC2 secondary (+3V3, GND)
c1x, c1y = U103.pin("1")
W((c1x, c1y), (c1x, 157.48), (482.6, 157.48))
pwr(VISO, (c1x, 157.48))
C109 = cap("C109", "100n 50V X7R", (482.6, 161.29), C0603,
           f("CC0603KRX7R9BB104", "YAGEO", "C14663", Decouples="U103.1"), left=True)
pwr("VPRI_RTN", C109.pin("2"))
pwr("VPRI_RTN", U103.pin("2"))
c2x, c2y = U103.pin("16")
W((c2x, c2y), (c2x, 157.48), (530.86, 157.48))
pwr("+3V3", (c2x, 157.48))
C110 = cap("C110", "100n 50V X7R", (510.54, 161.29), C0603,
           f("CC0603KRX7R9BB104", "YAGEO", "C14663", Decouples="U103.16"))
W((510.54, 157.48), C110.pin("1"))
pwr("GND", C110.pin("2"))
pwr("GND", U103.pin("9"))
sch.no_connect(U103.pin("7"))
enx, eny = U103.pin("10")
W((enx, eny), (530.86, eny), (530.86, 157.48))
for pn, net in (("14", "PD_BT_N"), ("13", "PD_TPL_N"), ("12", "PD_TPH_N"), ("11", "PD_PG_N")):
    sch.label(net, U103.pin(pn), kind="global_label", shape="output")
sch.box((497.84, 144.78), (551.18, 218.44), "SECONDARY (GND, +3V3)")
sch.text("All four active LOW. ISO7740 (no F suffix)\nreads HIGH while the primary is unpowered.\n"
         "TPH/TPL/BT valid 20-28 ms after PG releases.\nTruth table: A-pd-tps2373.md", (500.38, 207.01))
sch.items.append(S("polyline", S("pts", S("xy", 497.84, 144.78), S("xy", 497.84, 218.44)),
                   S("stroke", S("width", 0.3), S("type", Sym("dash"))), S("uuid", new_uuid())))

if __name__ == "__main__":
    sch.save()
    print("wrote", sch.file)
