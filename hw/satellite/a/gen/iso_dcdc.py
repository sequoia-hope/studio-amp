"""iso_dcdc.py -- block B, sheet 3: isolated active-clamp forward converter, VPRI -> 48 V VBUS.

Run from the repo root:  python3 hw/satellite/a/gen/iso_dcdc.py
Design and every value: design/parts/B-*.md (B-converter-design.md is the overview).
A2 sheet, primary left of the dashed barrier at x = 279.4, secondary right of it:
  top left       VPRI input capacitors
  middle         UCC2897A; T1 primary (N1 || N2); main FET + Rcs; low-side P-FET active clamp;
                 N5 aux -> LINEOV output OVP
  bottom left    VB_PRI bias buck (LM5019)
  barrier        T1, Y2 capacitors, LTV-217 opto with the primary FB network
  top right      output inductor, ceramics, IBUS shunt, VBUS bulk, SMCJ51A; INA281
  middle right   forward and freewheel SR cells (BSC500 + NCP4306 + RC snubber + RCD-Z clamp)
  bottom right   opto LED drive, CV loop (TL431) and CC loop (TL431 + ILIM_SEL switches)
"""
from __future__ import annotations

import hier
import studio_B_lib
from b_common import B, lm5019_buck

BARRIER_X = 279.4


def build():
    studio_B_lib.write_symbols()
    studio_B_lib.write_footprints()
    sch = hier.SubSheet("iso_dcdc", paper="A2", comments=[
        "Block B. Audits: design/parts/B-*.md (overview B-converter-design.md)",
        "Active-clamp forward, 737.28 kHz synced, T1 1:2, VPRI 38.4-57 V -> VBUS 47.9 V"])
    b = B(sch)
    R, C, w, rtn, gnd, vcc = b.R, b.C, b.w, b.rtn, b.gnd, b.vcc

    # =================================================================== primary input caps
    yr = 50.8
    vcc((30.48, yr), "VPRI")
    w((30.48, yr), (86.36, yr))
    for ref, key, x, pol in (("C215", "47u100", 38.1, True), ("C211", "4u7_100", 50.8, False),
                             ("C212", "4u7_100", 60.96, False), ("C213", "4u7_100", 73.66, False),
                             ("C214", "100n100", 86.36, False)):
        c = C(ref, key, (x, 58.42), pol=pol, tf="v")
        w((x, yr), c.pin("1"))
        w(c.pin("2"), (x, 66.04))
    w((38.1, 66.04), (86.36, 66.04))
    rtn((60.96, 66.04))
    sch.text("VPRI from the PD (block A), 38.4-57 V, <= 1.85 A.\nC215 47u: LT4321 needs >= 10 uF; damps the cable.\n"
             "Layout: C211-C214 at T1 pins 2/3 and Q201's Rcs,\nthe 737 kHz pulse-current loop (1.34 A rms).\n"
             "B-primary-power.md", (25.4, 77.47))
    sch.box((20.32, 38.1), (101.6, 91.44), "PRIMARY INPUT CAPACITORS")

    # =================================================================== T1
    t1 = b.part("studio_B:750343576", "T201", "T1", (BARRIER_X, 101.6), tf="n",
                ref_at=(283.21, 73.66), value_at=(283.21, 76.2), justify="left")
    p1, p6, p4, p2, p3, p5 = (t1.pin(n) for n in "164235")
    # dots 2 + 3 (between the windings) -> VPRI; finishes 4 + 5 (outside) -> SW_PRI
    xv = 266.7
    w(p2, (xv, p2[1]), (xv, p3[1]), p3)
    vcc((xv, p2[1]), "VPRI")
    xs = 261.62
    w(p4, (xs, p4[1]), (xs, p5[1]))
    w(p5, (xs, p5[1]))
    b.lab("SW_PRI", (xs, 123.19), 0)
    # N5 aux (dot 1) -> D202 -> node A (47k to RTN) -> 470k -> LINEOV (filter at U201)
    d202 = b.part("Diode:BAV21", "D202", "BAV21W", (264.16, p1[1]), tf="n",
                  ref_at=(264.16, p1[1] - 5.08), value_at=(264.16, p1[1] - 2.54), justify="")
    w(d202.pin("2"), p1)
    w(p6, (269.24, p6[1]))
    rtn((269.24, p6[1]))
    w(d202.pin("1"), (254.0, p1[1]))
    r208 = R("R208", "47k", (254.0, 86.36), tf="l")
    w((254.0, p1[1]), r208.pin("1"))
    rtn(r208.pin("2"))
    r209 = R("R209", "470k", (243.84, p1[1]), rot=90)
    w(r209.pin("2"), (254.0, p1[1]))
    w(r209.pin("1"), (233.68, p1[1]))
    b.lab("LINEOV", (233.68, p1[1]), 180)
    sch.text("T1 wired 1:2: primary N1 || N2 = 4 T (Lm 25 uH),\nsecondary N3 + N4 in series (10-8) = 8 T.\n"
             "Dots = winding starts (B-transformer.md).\nLayout: N1 and N2 symmetric.", (185.42, 40.64))
    sch.text("N5 aux, 4 T: forward pulse ~ VPRI, averaged\n-> LINEOV: output OVP at VBUS ~ 53.3 V,\n"
             "independent of the opto (B-controller.md)", (185.42, 60.96))

    # =================================================================== main FET, Rcs
    q201 = b.part("Transistor_FET:BSC026N08NS5", "Q201", "FDMS86200", (259.08, 132.08), tf="n",
                  ref_at=(256.54, 114.3), value_at=(256.54, 116.84), justify="right")
    w((xs, p5[1]), q201.pin("5"))
    r216 = R("R216", "Rcs", (261.62, 147.32), tf="v")
    w(q201.pin("1"), r216.pin("1"))
    rtn(r216.pin("2"))
    gate = q201.pin("4")
    r214 = R("R214", "10k", (251.46, 139.7), tf="n", ref_at=(247.65, 141.0), value_at=(249.43, 141.0), ref_rot=90, justify="")
    w((251.46, gate[1]), r214.pin("1"))
    w(r214.pin("2"), r216.pin("1"))
    b.lab("CS_PRI", (256.54, r216.pin("1")[1]), 270)

    # =================================================================== UCC2897A
    u = b.part("studio_B:UCC2897A", "U201", "UCC2897A", (203.2, 139.7), tf="n",
               ref_at=(203.2, 137.16), value_at=(203.2, 139.7), justify="")
    pin = u.pin
    # OUT -> 2.2R -> gate (row y = OUT), 10k OUT -> PGND
    r213 = R("R213", "2R2", (243.84, gate[1]), rot=90, tf="ha")
    w(pin("15"), r213.pin("1"))
    w(r213.pin("2"), gate)
    r212 = R("R212", "10k", (236.22, 124.46), tf="vl")
    w((236.22, gate[1]), r212.pin("2"))
    w(r212.pin("1"), (236.22, 119.38), (241.3, 119.38))
    rtn((241.3, 119.38))
    # AUX -> 100n -> clamp gate; BAS316 (anode gate, cathode RTN) + 10k gate-source
    aux = pin("14")
    xa = 246.38
    c208 = C("C208", "100n", (xa, 162.56), tf="v")
    w(aux, (xa, aux[1]), c208.pin("1"))
    w(c208.pin("2"), (xa, 180.34))
    q202 = b.part("Transistor_FET:IRF9540N", "Q202", "IRFR6215", (251.46, 180.34), tf="n",
                  ref_at=(256.54, 187.96), value_at=(256.54, 190.5), justify="left")
    w((xa, 180.34), q202.pin("1"))
    rtn(q202.pin("3"))
    d201 = b.part("Diode:BAS316", "D201", "BAS316", (241.3, 186.69), rot=90, tf="v")
    r215 = R("R215", "10k", (233.68, 186.69), tf="vl")
    w((xa, 180.34), (233.68, 180.34))
    w((241.3, 180.34), d201.pin("2"))
    w((233.68, 180.34), r215.pin("1"))
    w(r215.pin("2"), (233.68, 195.58), (241.3, 195.58), d201.pin("1"))
    rtn((241.3, 195.58))
    # clamp caps: SW_PRI (right-hand lane) to the P-FET drain
    c209 = C("C209", "100n250", (254.0, 170.18), tf="v")
    c210 = C("C210", "100n250", (264.16, 170.18), tf="v")
    w(q202.pin("2"), c209.pin("2"))
    w(c209.pin("2"), c210.pin("2"))
    w(c209.pin("1"), c210.pin("1"), (271.78, c210.pin("1")[1]), (271.78, 125.73), (xs, 125.73))
    sch.text("Active clamp, P-FET low side:\nVc ~ 100 V on C209 || C210 (250 V X7R).\nB-primary-power.md",
             (231.14, 203.2))
    # CS: Kelvin from the Rcs pad; RF 1k + CF 82p at the pin
    cs = pin("9")
    r205 = R("R205", "1k", (241.3, 157.48), tf="v")
    w(cs, (241.3, cs[1]), r205.pin("1"))
    w(r205.pin("2"), (241.3, 163.83))
    b.lab("CS_PRI", (241.3, 163.83), 270)
    c204 = C("C204", "82p", (236.22, 152.4), tf="v")
    w((236.22, cs[1]), c204.pin("1"))
    rtn(c204.pin("2"))
    # supplies on top: VDD, PVDD (0R at the IC), VREF
    vdd, pvdd, vref = pin("17"), pin("16"), pin("6")
    vcc((vdd[0], 93.98), "VB_PRI")
    w((vdd[0], 93.98), vdd)
    c202 = C("C202", "1u", (182.88, 109.22), extra={"Decouples": "U201.17"}, tf="vl")
    w((vdd[0], 104.14), (182.88, 104.14), c202.pin("1"))
    rtn(c202.pin("2"))
    r220 = R("R220", "0R", (195.58, 99.06), rot=90)
    w((vdd[0], 99.06), r220.pin("1"))
    w(r220.pin("2"), (pvdd[0], 99.06), pvdd)
    b.flag((pvdd[0] + 0, 96.52))
    w((pvdd[0], 96.52), (pvdd[0], 99.06))
    c203 = C("C203", "10u", (205.74, 109.22), extra={"Decouples": "U201.16"}, tf="v")
    w((pvdd[0], 104.14), (205.74, 104.14), c203.pin("1"))
    rtn(c203.pin("2"))
    vcc((vref[0], 93.98), "VREF_ACF")
    w((vref[0], 93.98), vref)
    c201 = C("C201", "220n", (220.98, 109.22), extra={"Decouples": "U201.6"}, tf="v")
    w((vref[0], 104.14), (220.98, 104.14), c201.pin("1"))
    rtn(c201.pin("2"))
    # left: VIN (100k from VPRI; 0R to VDD DNP), LINEUV, SYNC, FB, LINEOV
    vin = pin("1")
    r218 = R("R218", "100k", (167.64, 119.38))
    w(vin, (167.64, vin[1]), r218.pin("2"))
    vcc(r218.pin("1"), "VPRI")
    r219 = R("R219", "0R", (154.94, 119.38), dnp=True, tf="l")
    w((167.64, vin[1]), (154.94, vin[1]), r219.pin("2"))
    vcc(r219.pin("1"), "VB_PRI")
    sch.text("VIN: 100k from VPRI (JFET start-up unused;\nVDD from VB_PRI). R219 DNP option.", (106.68, 99.06))
    luv = pin("18")
    r206 = R("R206", "73k2", (132.08, 127.0), tf="l")
    r207 = R("R207", "2k37", (132.08, 142.24), tf="l")
    w(luv, (132.08, luv[1]))
    w(r206.pin("2"), (132.08, luv[1]), r207.pin("1"))
    vcc(r206.pin("1"), "VPRI")
    rtn(r207.pin("2"))
    sch.text("LINEUV: on 40.4 V,\noff 38.4 V", (106.68, 152.4))
    b.glab("ACF_SYNC", pin("7"), 180, "input")
    b.lab("ACF_FB", pin("11"), 180)
    lov = pin("19")
    r210 = R("R210", "23k7", (167.64, 157.48), tf="v")
    c207 = C("C207", "47n", (157.48, 157.48), tf="vl")
    w(lov, (167.64, lov[1]), r210.pin("1"))
    w((167.64, lov[1]), (157.48, lov[1]), c207.pin("1"))
    w((157.48, lov[1]), (149.86, lov[1]))
    b.lab("LINEOV", (149.86, lov[1]), 180)
    w(c207.pin("2"), r210.pin("2"))
    rtn((162.56, r210.pin("2")[1]))
    sch.text("LINEOV: R209 470k from node A;\n23.7k || 47n averages (1 ms)", (106.68, 170.18))
    # bottom: SS/SD, timing resistors, GND + PGND on one RTN bus (net-tied at the IC)
    ybus = 179.07
    ss = pin("12")
    c205 = C("C205", "1u", (ss[0], 170.18), tf="v")
    w(ss, c205.pin("1"))
    w(c205.pin("2"), (ss[0], ybus))
    for ref, key, pn in (("R203", "4k53", "3"), ("R201", "31k6", "4"), ("R202", "14k3", "5"),
                         ("R204", "316k", "10")):
        p = pin(pn)
        rr = R(ref, key, (p[0], 170.18), tf="v")
        w(p, rr.pin("1"))
        w(rr.pin("2"), (p[0], ybus))
    w(pin("8"), (pin("8")[0], ybus))
    w(pin("13"), (pin("13")[0], ybus))
    w((ss[0], ybus), (pin("13")[0], ybus))
    rtn((pin("8")[0], ybus))
    sch.text("RDEL 4.53k = 50 ns. RON 31.6k / ROFF 14.3k:\nfree-run 656 kHz (590-708), synced to\n"
             "737.28 kHz, DMAX 0.68-0.715. RSLOPE 316k.\nCSS 1u: 60 ms soft start. PD_PG holds SS\n"
             "low during PD inrush; UCC_SS -> block A.\nGND (8) and PGND (13) meet only at the IC\n"
             "(datasheet 11.1). B-controller.md", (106.68, 182.88))
    # SS/SD: PD_PG holds it low through 1k during PD inrush; UCC_SS -> block A's PD_PG_N buffer
    w((ss[0], 165.1), (175.26, 165.1), (175.26, 173.99))
    r217 = R("R217", "1k", (175.26, 177.8), tf="l")
    b.glab("PD_PG", r217.pin("2"), 270, "input")
    w((175.26, 168.91), (162.56, 168.91))
    b.glab("UCC_SS", (162.56, 168.91), 180, "output")
    sch.box((101.6, 88.9), (276.86, 215.9), "UCC2897A CONTROLLER, PRIMARY STAGE")

    # =================================================================== VB_PRI bias buck (LM5019)
    lm5019_buck(b, 0, 0, dict(U="U202", L="L201", RON="R221", RFBT="R222", RFBB="R223", RUVT="R224",
                              RUVB="R225", RR="R226", CIN="C221", CIN2="C222", CVCC="C218", CBST="C219",
                              COUT="C220", CR="C216", CAC="C217"),
                dict(RON="267k", RFBT="107k", RUVT="237k", RR="200k", L="L330"), "VPRI", "VB_PRI", rtn,
                "VB_PRI BIAS BUCK (PRIMARY)",
                "VB_PRI 14.3 V (13.9-14.8), <= 85 mA: UCC2897A, block A's TPS2373\nVC_IN and isolator, "
                "the sync clock (iso_aux). Starts at VPRI 30.3 V.\n600 kHz (RON 267k); Type III ripple "
                "Rr 200k, Cr 1n, Cac 100n.\nB-bias.md")

    # =================================================================== barrier, Y caps, opto
    b.dashed((BARRIER_X, 27.94), (BARRIER_X, 340.36))
    sch.text("ISOLATION BARRIER  1500 Vrms (R-32)", (281.94, 30.48))
    sch.text("PRIMARY: VPRI_RTN", (250.19, 30.48))
    sch.text("SECONDARY: GND", (281.94, 35.56))
    c223 = C("C223", "Ycap", (BARRIER_X, 228.6), rot=90, tf="n", ref_at=(243.84, 224.79),
             value_at=(243.84, 227.33), justify="left")
    c224 = C("C224", "Ycap", (BARRIER_X, 241.3), rot=90, dnp=True, tf="n", ref_at=(243.84, 237.49),
             value_at=(243.84, 240.03), justify="left")
    w(c223.pin("1"), (271.78, 228.6), (271.78, 241.3), c224.pin("1"))
    w(c223.pin("2"), (287.02, 228.6), (287.02, 241.3), c224.pin("2"))
    rtn((271.78, 241.3))
    gnd((287.02, 241.3))
    sch.text("C223 Y2 2.2n at T1: interwinding\ndisplacement current. C224 DNP\n(EMI tuning). B-feedback.md",
             (231.14, 248.92))
    opto = b.part("Isolator:PC817", "U203", "LTV217", (BARRIER_X, 274.32), mirror="y", tf="n",
                  ref_at=(BARRIER_X, 265.43), value_at=(BARRIER_X, 267.97), justify="")
    oc, oe, oa, ok = opto.pin("4"), opto.pin("3"), opto.pin("1"), opto.pin("2")
    w(oc, (243.84, oc[1]))
    b.lab("ACF_FB", (243.84, oc[1]), 180)
    r211 = R("R211", "4k99", (259.08, 264.16), tf="l")
    w(r211.pin("2"), (259.08, oc[1]))
    vcc(r211.pin("1"), "VREF_ACF")
    c206 = C("C206", "6n8", (251.46, 276.86), tf="l")
    w((251.46, oc[1]), c206.pin("1"))
    w(oe, (266.7, oe[1]), (266.7, 284.48))
    w(c206.pin("2"), (251.46, 284.48), (266.7, 284.48))
    rtn((259.08, 284.48))
    sch.text("FB: 4.99k to VREF, 6.8n (pole 4.7 kHz).\nOpto gain CTR x 4.99k / 499R ~ 10.\n"
             "fc ~ 1 kHz, PM ~ 66 deg (B-feedback.md)", (215.9, 294.64))

    # =================================================================== secondary: T1 -> SRs
    p7, p10, p8, p11 = (t1.pin(n) for n in ("7", "10", "8", "11"))
    w(p10, (292.1, p10[1]), (292.1, p8[1]), p8)
    yo = 63.5
    xsl = 297.18
    w(p7, (xsl, p7[1]), (xsl, yo))
    b.lab("SW_SEC", (xsl + 2.54, p7[1]), 0)
    xlane = 396.24
    w((xsl, p7[1]), (xlane, p7[1]), (xlane, 175.26))
    l202 = b.part("Device:L", "L202", "Lout", (304.8, yo), rot=90, tf="h")
    w((xsl, yo), l202.pin("1"))

    def sr_cell(uref, qref, rton, rtoff, cvcc, csn, rsn, dcl, ccl, ztv, y0, title):
        n = b.part("studio_B:NCP4306DADZZDA", uref, "NCP4306", (320.04, y0), tf="n",
                   ref_at=(299.72, y0 + 19.05), value_at=(299.72, y0 + 21.59), justify="left")
        q = b.part("Transistor_FET:BSC026N08NS5", qref, "BSC500", (345.44, y0 + 2.54), tf="n",
                   ref_at=(347.98, y0 + 13.97), value_at=(347.98, y0 + 16.51), justify="")
        d = q.pin("5")
        w(n.pin("1"), q.pin("4"))
        csp = n.pin("3")
        w(csp, (csp[0], y0 - 12.7), (d[0], y0 - 12.7))
        vc = n.pin("6")
        vcc((vc[0], y0 - 22.86), "VSR")
        w((vc[0], y0 - 22.86), vc)
        cv = C(cvcc, "1u", (312.42, y0 - 17.78), extra={"Decouples": f"{uref}.6"}, tf="n",
               ref_at=(307.09, y0 - 17.78), value_at=(308.87, y0 - 17.78), ref_rot=90, justify="")
        w((vc[0], y0 - 21.59), (312.42, y0 - 21.59), cv.pin("1"))
        gnd(cv.pin("2"))
        ybs = y0 + 15.24
        r_off = R(rtoff, "2k", (302.26, y0 + 7.62), tf="v")
        w(n.pin("5"), (302.26, n.pin("5")[1]), r_off.pin("1"))
        r_on = R(rton, "750", (294.64, y0 + 7.62), tf="v")
        w(n.pin("4"), (294.64, n.pin("4")[1]), r_on.pin("1"))
        for p in (r_on.pin("2"), r_off.pin("2")):
            w(p, (p[0], ybs))
        w(n.pin("2"), (320.04, ybs))
        w((294.64, ybs), (320.04, ybs))
        gnd((320.04, ybs))
        gnd(q.pin("1"))
        # RC snubber and RCD-Z clamp off the drain
        tap = (d[0], y0 - 15.24)
        c_s = C(csn, "22p250", (360.68, y0 - 7.62), tf="v")
        w(tap, (360.68, tap[1]), c_s.pin("1"))
        r_s = R(rsn, "Rsnub", (360.68, y0 + 5.08), tf="vl")
        w(c_s.pin("2"), r_s.pin("1"))
        gnd(r_s.pin("2"))
        dc = b.part("Device:D", dcl, "US1G", (370.84, tap[1]), rot=180, tf="n",
                    ref_at=(370.84, tap[1] - 5.08), value_at=(370.84, tap[1] - 2.54), justify="")
        w((360.68, tap[1]), dc.pin("2"))
        k = dc.pin("1")
        c_c = C(ccl, "10n250", (378.46, y0 - 7.62), tf="v")
        w(k, (378.46, k[1]), c_c.pin("1"))
        gnd(c_c.pin("2"))
        z = b.part("Device:D_Zener", ztv, "SMBJ130A", (386.08, y0 - 7.62), rot=270, tf="v")
        w((378.46, k[1]), (386.08, k[1]), z.pin("1"))
        gnd(z.pin("2"))
        sch.box((289.56, y0 - 33.02), (393.7, y0 + 25.4), title)
        return n, q, d

    y1 = 147.32
    n1, q1, d1 = sr_cell("U204", "Q203", "R227", "R229", "C225", "C227", "R231", "D203", "C229", "D205", y1,
                         "FORWARD SR")
    w(p11, (d1[0], p11[1]), d1)
    b.lab("SR_FWD_D", (322.58, p11[1]), 0)
    # DRV_FWD (forward SR gate) -> iso_aux, ACF_PULSE buffer
    gx = 337.82
    w((gx, y1 + 2.54), (gx, y1 + 21.59))
    b.glab("DRV_FWD", (gx, y1 + 21.59), 0, "output")
    y2 = 210.82
    n2, q2, d2 = sr_cell("U205", "Q204", "R228", "R230", "C226", "C228", "R232", "D204", "C230", "D206", y2,
                         "FREEWHEEL SR")
    w((xlane, 175.26), (d2[0], 175.26), d2)
    sch.text("Both SRs: RC snubber 22p + 47R 2512; RCD-Z clamp (US1G, 10n, SMBJ130A) holds the\n"
             "drain and NCP4306 CS <= ~165 V (200 V abs max). MIN_TON 750R ~ 125 ns, MIN_TOFF 2k ~ 256 ns.\n"
             "Layout: NCP4306 GND Kelvin to its SR source pad, CS to the drain pad. B-sync-rect.md",
             (292.1, 241.3))

    # =================================================================== output filter -> VBUS
    w(l202.pin("2"), (312.42, yo))
    b.lab("VBUS_CONV", (312.42, yo), 0)
    w((312.42, yo), (410.21, yo))
    for i, x in enumerate([320.04, 330.2, 340.36, 353.06, 363.22, 375.92]):
        c = C(f"C{231 + i}", "4u7_100", (x, 71.12), tf="v")
        w((x, yo), c.pin("1"))
        gnd(c.pin("2"))
    r233 = R("R233", "Rsh", (414.02, yo), rot=90)
    w(r233.pin("2"), (424.18, yo))
    w((410.21, yo), r233.pin("1"))
    vcc((424.18, 55.88), "VBUS")
    w((424.18, 55.88), (424.18, yo), (518.16, yo))
    for i, x in enumerate([431.8, 444.5, 454.66, 467.36, 477.52, 490.22, 500.38]):
        c = C(f"C{241 + i}", "bulk", (x, 71.12), pol=True, dnp=(i == 6), tf="v")
        w((x, yo), c.pin("1"))
        gnd(c.pin("2"))
    d208 = b.part("Device:D_Zener", "D208", "SMCJ51A", (518.16, 71.12), rot=270, tf="v")
    w((518.16, yo), d208.pin("1"))
    gnd(d208.pin("2"))
    b.flag((523.24, yo))
    w((518.16, yo), (523.24, yo))
    sch.text("L202 68u: 0.35-0.55 A p-p, 1.65 A peak at CC.\nC231-C236 6 x 4.7u 100V ahead of the shunt "
             "keep 737 kHz ripple out of it. B-output.md", (299.72, 46.99))
    sch.text("VBUS 47.9 V +-1.5 %: 6 x 1000u 63V KZN (C247 DNP footprint).\n"
             "OVP: SMCJ51A + LINEOV 53.3 V + gateware 55 V (agreed with block D)", (421.64, 86.36))
    sch.box((294.64, 38.1), (528.32, 93.98), "OUTPUT FILTER, IBUS SHUNT 30 mR, VBUS BULK")

    # =================================================================== INA281, IBUS_SENSE
    ina = b.part("Amplifier_Current:INA281A4", "U206", "INA281A4", (414.02, 116.84), tf="n",
                 ref_at=(421.64, 129.54), value_at=(421.64, 132.08), justify="left")
    w(ina.pin("3"), (408.94, yo))
    w(ina.pin("4"), (419.10, yo))
    vp = ina.pin("5")
    vcc((401.32, 111.76), "VSR")
    w((401.32, 111.76), (401.32, vp[1]), vp)
    c238 = C("C238", "100n", (401.32, 127.0), extra={"Decouples": "U206.5"}, tf="n",
                ref_at=(397.76, 123.19), value_at=(399.54, 123.19), ref_rot=90, justify="")
    w((401.32, vp[1]), c238.pin("1"))
    gnd(c238.pin("2"))
    gnd(ina.pin("2"))
    out = ina.pin("1")
    r234 = R("R234", "100R", (429.26, out[1]), rot=90)
    w(out, r234.pin("1"))
    xf = 436.88
    w(r234.pin("2"), (xf, out[1]))
    c237 = C("C237", "470n", (xf, 124.46), tf="v")
    w((xf, out[1]), c237.pin("1"))
    gnd(c237.pin("2"))
    r235 = R("R235", "200k", (449.58, 124.46), tf="v")
    r236 = R("R236", "100k", (449.58, 139.7), tf="v")
    w((xf, out[1]), (449.58, out[1]), r235.pin("1"))
    w(r235.pin("2"), r236.pin("1"))
    gnd(r236.pin("2"))
    w((449.58, 132.08), (457.20, 132.08))
    b.glab("IBUS_SENSE", (457.20, 132.08), 0, "output")
    w((449.58, out[1]), (464.82, out[1]))
    b.lab("IBUS_F", (464.82, out[1]), 0)
    sch.text("INA281A4 200 V/V x 30 mR = 6.0 V/A;\n100R + 470n kills 737 kHz ripple.\n"
             "IBUS_SENSE 2.0 V/A, 67k source -> RP2350\nADC4 (block E fits 100 nF). B-feedback.md",
             (457.20, 142.24))
    sch.box((398.78, 99.06), (505.46, 157.48), "IBUS SENSE (INA281)")

    # =================================================================== opto LED, CV loop, CC loop
    # LED: VSR -> 499R -> anode; 1k across the LED keeps the TL431s >= 1 mA
    w(oa, (292.1, oa[1]), (292.1, 266.7))
    r247 = R("R247", "499", (292.1, 261.62), tf="n", ref_at=(294.13, 263.5), value_at=(295.91, 263.5), ref_rot=90, justify="")
    w(r247.pin("2"), (292.1, 266.7))
    vcc(r247.pin("1"), "VSR")
    r248 = R("R248", "1k", (302.26, 269.24), tf="v")
    w((292.1, 266.7), (302.26, 266.7), r248.pin("1"))
    yk = ok[1]
    w(r248.pin("2"), (302.26, yk))
    w(ok, (322.58, yk))
    b.lab("OPTO_K", (294.64, yk), 0)
    # CV: TL431 (mirror: REF right), 47.5k / 2.61k 0.1 %, 115k + 4.7n cathode -> REF
    u208 = b.part("Reference_Voltage:TL431DBZ", "U208", "TL431B", (322.58, yk + 7.62), rot=90, mirror="y",
                  tf="n", ref_at=(320.04, yk + 3.81), value_at=(320.04, yk + 6.35), justify="left")
    w((322.58, yk), u208.pin("1"))
    gnd(u208.pin("3"))
    ref8 = u208.pin("2")
    xcv = 337.82
    w(ref8, (xcv, ref8[1]))
    r244 = R("R244", "47k5_p", (xcv, ref8[1] - 7.62), tf="v")
    vcc(r244.pin("1"), "VBUS")
    w(r244.pin("2"), (xcv, ref8[1]))
    r245 = R("R245", "2k61_p", (xcv, ref8[1] + 10.16), tf="v")
    w((xcv, ref8[1]), r245.pin("1"))
    gnd(r245.pin("2"))
    ycomp = yk - 15.24
    w((322.58, yk), (322.58, ycomp))
    r246 = R("R246", "115k", (330.2, ycomp), rot=90)
    c240 = C("C240", "4n7", (345.44, ycomp), rot=90, tf="ha")
    w((322.58, ycomp), r246.pin("1"))
    w(r246.pin("2"), c240.pin("1"))
    w(c240.pin("2"), (350.52, ycomp), (350.52, ref8[1]), (xcv, ref8[1]))
    sch.text("CV: 2.495 V x (1 + 47.5k/2.61k) = 47.9 V.\nType II: 115k + 4.7n (zero 294 Hz).",
             (292.1, 304.8))
    # CC: OPTO_K -> BAS316 -> TL431 (CC) cathode; IBUS_F -> 4.99k -> CCREF -> 88.7k || switched 4.22k / 5.90k
    d207 = b.part("Diode:BAS316", "D207", "BAS316", (312.42, yk + 5.08), rot=90, tf="vl")
    w((312.42, yk), d207.pin("2"))
    ycc = 317.5
    w(d207.pin("1"), (312.42, ycc), (383.54, ycc))
    u207 = b.part("Reference_Voltage:TL431DBZ", "U207", "TL431B", (383.54, ycc + 2.54), rot=90, mirror="y",
                  tf="n", ref_at=(377.19, ycc + 5.08), value_at=(377.19, ycc + 7.62), justify="left")
    gnd(u207.pin("3"))
    ref7 = u207.pin("2")
    xn = 403.86
    w(ref7, (xn, ref7[1]))
    r237 = R("R237", "4k99", (xn, ref7[1] - 7.62), tf="v")
    w(r237.pin("2"), (xn, ref7[1]))
    w(r237.pin("1"), (xn, ref7[1] - 13.97), (408.94, ref7[1] - 13.97))
    b.lab("IBUS_F", (408.94, ref7[1] - 13.97), 0)
    r238 = R("R238", "88k7", (xn, ref7[1] + 7.62), tf="v")
    w((xn, ref7[1]), r238.pin("1"))
    gnd(r238.pin("2"))
    ycr = ycc - 10.16
    w((375.92, ycc), (375.92, ycr))
    r243 = R("R243", "100k", (381.0, ycr), rot=90)
    c239 = C("C239", "10n", (396.24, ycr), rot=90, tf="ha")
    w((375.92, ycr), r243.pin("1"))
    w(r243.pin("2"), c239.pin("1"))
    w(c239.pin("2"), (401.32, ycr), (401.32, ref7[1]))
    # ILIM_SEL switches
    ysel = ref7[1]
    w((xn, ysel), (444.5, ysel))
    r239 = R("R239", "4k22", (419.1, ysel + 7.62), tf="v")
    r240 = R("R240", "5k9", (444.5, ysel + 7.62), tf="v")
    w((419.1, ysel), r239.pin("1"))
    w((444.5, ysel), r240.pin("1"))
    q205 = b.part("Transistor_FET:AO3400A", "Q205", "AO3400A", (416.56, ysel + 20.32), tf="n",
                  ref_at=(421.64, ysel + 22.86), value_at=(421.64, ysel + 25.4), justify="left")
    q206 = b.part("Transistor_FET:AO3400A", "Q206", "AO3400A", (447.04, ysel + 20.32), mirror="y", tf="n",
                  ref_at=(441.96, ysel + 22.86), value_at=(441.96, ysel + 25.4), justify="right")
    w(r239.pin("2"), q205.pin("3"))
    w(r240.pin("2"), q206.pin("3"))
    gnd(q205.pin("2"))
    gnd(q206.pin("2"))
    g5, g6 = q205.pin("1"), q206.pin("1")
    w(g5, (401.32, g5[1]))
    b.glab("ILIM_SEL0", (401.32, g5[1]), 180, "input")
    w(g6, (462.28, g6[1]))
    b.glab("ILIM_SEL1", (462.28, g6[1]), 0, "input")
    r241 = R("R241", "100k", (408.94, g5[1] + 7.62), tf="vl")
    r242 = R("R242", "100k", (454.66, g6[1] + 7.62), tf="v")
    w((408.94, g5[1]), r241.pin("1"))
    w((454.66, g6[1]), r242.pin("1"))
    gnd(r241.pin("2"))
    gnd(r242.pin("2"))
    sch.text("CC limit (ILIM_SEL1:0, reset 00 via 100k):\n00 0.44 A, 01 0.94 A, 10 0.80 A, 11 1.30 A.\n"
             "Integrator 100k + 10n. B-feedback.md", (464.82, 312.42))
    sch.box((289.56, 248.92), (520.7, 375.92), "OPTO LED, CV LOOP (TL431) AND CC LOOP (TL431, ILIM_SEL)")
    return sch


if __name__ == "__main__":
    s = build()
    s.save()
    print("wrote", s.file)
