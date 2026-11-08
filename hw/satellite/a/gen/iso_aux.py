"""iso_aux.py -- block B, sheet 4: converter sync clock, VSR bias, VBUS-droop detector, ACF_PULSE.

Run from the repo root:  python3 hw/satellite/a/gen/iso_aux.py
Design: design/parts/B-sync-clock.md, B-bias.md, B-vbus-droop.md, B-interfaces.md.
A3 sheet, dashed barrier at x = 215.9:
  left (primary, VPRI_RTN)  HT7550 V5_CLK; 7.3728 MHz Pierce (LVC1GU04); 74HC4017 /10;
                            LVC1G123 clock-OK one-shot; LVC1G08 on VREF -> 100R -> ACF_SYNC
  right (secondary, GND)    VSR 10 V bias buck (LM5019) from VBUS; VBUS-droop comparator
                            (LM393 + TL431) -> 2N7002 -> POE_LOSS_N; DRV_FWD -> 74LVC2G08 -> ACF_PULSE
"""
from __future__ import annotations

import hier
import studio_B_lib
from b_common import B, lm5019_buck

BARRIER_X = 215.9


def build():
    studio_B_lib.write_symbols()
    sch = hier.SubSheet("iso_aux", paper="A3", comments=[
        "Block B. Audits: design/parts/B-sync-clock, B-bias, B-vbus-droop, B-interfaces",
        "737.28 kHz sync clock, VSR bias, VBUS-droop detector, ACF_PULSE"])
    b = B(sch)
    R, C, w, rtn, gnd, vcc = b.R, b.C, b.w, b.rtn, b.gnd, b.vcc

    # =================================================================== V5_CLK (HT7550 from VB_PRI)
    ldo = b.part("Regulator_Linear:HT75xx-1-SOT89", "U252", "HT7550", (45.72, 50.8), tf="n",
                 ref_at=(45.72, 41.91), value_at=(45.72, 44.45), justify="")
    vi, vo = ldo.pin("2"), ldo.pin("3")
    vcc((27.94, 43.18), "VB_PRI")
    w((27.94, 43.18), (27.94, vi[1]), vi)
    c258 = C("C258", "1u", (27.94, 54.61), extra={"Decouples": "U252.2"}, tf="vl")
    w((27.94, vi[1]), c258.pin("1"))
    rtn(c258.pin("2"))
    rtn(ldo.pin("1"))
    vcc((63.5, 43.18), "V5_CLK")
    w(vo, (63.5, vo[1]), (63.5, 43.18))
    c259 = C("C259", "1u", (63.5, 54.61), extra={"Decouples": "U252.3"}, tf="v")
    w((63.5, vo[1]), c259.pin("1"))
    rtn(c259.pin("2"))
    sch.text("V5_CLK 5 V, <= 10 mA: oscillator, counter,\none-shot (0.1 W in the SOT-89)", (73.66, 45.72))

    # =================================================================== Pierce oscillator
    inv = b.part("74xGxx:74LVC1GU04", "U253", "LVC1GU04", (50.8, 88.9), tf="n",
                 ref_at=(55.88, 81.28), value_at=(55.88, 83.82), justify="left")
    vc3 = inv.pin("5")
    vcc((vc3[0], 68.58), "V5_CLK")
    w((vc3[0], 68.58), vc3)
    c262 = C("C262", "100n", (35.56, 76.2), extra={"Decouples": "U253.5"}, tf="vl")
    w((vc3[0], 71.12), (35.56, 71.12), c262.pin("1"))
    rtn(c262.pin("2"))
    rtn(inv.pin("3"))
    xin, xout = inv.pin("2"), inv.pin("4")
    xi, xo2 = 27.94, 68.58
    w(xin, (xi, xin[1]), (xi, 125.73))
    w(xout, (86.36, xout[1]))
    r258 = R("R258", "1k", (xo2, 100.33), tf="v")
    w((xo2, xout[1]), r258.pin("1"))
    w(r258.pin("2"), (xo2, 125.73))
    y251 = b.part("Device:Crystal", "Y251", "XTAL", (48.26, 106.68), tf="n",
                  ref_at=(48.26, 111.76), value_at=(48.26, 114.3), justify="")
    w((xi, 106.68), y251.pin("1"))
    w(y251.pin("2"), (xo2, 106.68))
    c260 = C("C260", "33p", (35.56, 111.76), tf="v")
    c261 = C("C261", "33p", (60.96, 111.76), tf="vl")
    w((35.56, 106.68), c260.pin("1"))
    w((60.96, 106.68), c261.pin("1"))
    rtn(c260.pin("2"))
    rtn(c261.pin("2"))
    r257 = R("R257", "1M", (48.26, 125.73), rot=90)
    w((xi, 125.73), r257.pin("1"))
    w(r257.pin("2"), (xo2, 125.73))
    sch.text("7.3728 MHz, CL 20 pF, +-50 ppm all-in\n(SXMH7.3728F2020F30, -40..85 C):\n"
             "33p + 33p + ~5 pF stray = 21.5 pF.\nRf 1M, Rs 1k (drive ~70 uW).", (17.78, 134.62))

    # =================================================================== 74HC4017 divide by 10
    cnt = b.part("4xxx:4017", "U254", "HC4017", (99.06, 101.6), tf="n",
                 ref_at=(88.9, 127.0), value_at=(88.9, 129.54), justify="right")
    vd = cnt.pin("16")
    vcc((vd[0], 68.58), "V5_CLK")
    w((vd[0], 68.58), vd)
    c263 = C("C263", "100n", (114.3, 76.2), extra={"Decouples": "U254.16"}, tf="v")
    w((vd[0], 71.12), (114.3, 71.12), c263.pin("1"))
    rtn(c263.pin("2"))
    rtn(cnt.pin("8"))
    w(cnt.pin("13"), (83.82, cnt.pin("13")[1]), (83.82, 99.06))
    w(cnt.pin("15"), (83.82, cnt.pin("15")[1]))
    rtn((83.82, 99.06))
    for q in ("3", "4", "7", "10", "1", "5", "6", "9", "11"):
        sch.no_connect(cnt.pin(q))
    q1, co = cnt.pin("2"), cnt.pin("12")
    sch.text("Q1: one 136 ns pulse per 10 clocks = 737.28 kHz\n(< (1 - DMAX) x T = 0.39 us). CP1 and MR low.",
             (73.66, 142.24))

    # =================================================================== clock-OK one-shot (LVC1G123)
    os_ = b.part("74xGxx:74LVC1G123", "U255", "LVC1G123", (149.86, 119.38), mirror="x", tf="n",
                 ref_at=(149.86, 134.62), value_at=(149.86, 137.16), justify="")
    w(co, os_.pin("1"))                     # A <- CO (Q5-9), toggles at 737 kHz while counting
    bpin = os_.pin("2")
    w(bpin, (134.62, bpin[1]), (134.62, 109.22))
    vcc((134.62, 109.22), "V5_CLK")
    vcc(os_.pin("3"), "V5_CLK")             # CLR high
    cx, rcx = os_.pin("6"), os_.pin("7")
    c264 = C("C264", "470p", (129.54, cx[1]), rot=90, tf="n", ref_at=(131.45, 127.0),
             value_at=(129.54, 119.38), justify="")
    w(cx, c264.pin("2"))
    w(c264.pin("1"), (125.73, rcx[1]), rcx)
    r259 = R("R259", "10k", (118.11, rcx[1]), rot=90, tf="n", ref_at=(118.11, rcx[1] + 2.54),
             value_at=(118.11, rcx[1] + 5.08), justify="")
    w(r259.pin("2"), (125.73, rcx[1]))
    vcc(r259.pin("1"), "V5_CLK")
    osp = b.part("74xGxx:74LVC1G123", "U255", "LVC1G123", (167.64, 152.4), unit=2, tf="n",
                 ref_at=(165.1, 149.86), value_at=(165.1, 152.4), justify="right")
    vcc((167.64, 134.62), "V5_CLK")
    w((167.64, 134.62), osp.pin("8"))
    c265 = C("C265", "100n", (177.8, 142.24), extra={"Decouples": "U255.8"}, tf="v")
    w((167.64, 137.16), (177.8, 137.16), c265.pin("1"))
    rtn(c265.pin("2"))
    rtn(osp.pin("4"))
    sch.text("Clock-OK: retriggered by CO; Rext 10k / Cext 470p\n-> tw ~ 4.5 us (> 1.36 us CO period, <= 10 us).\n"
             "Clock stops -> CLK_OK low within ~4.5 us -> SYNC low\n-> UCC2897A free-runs (590-708 kHz). "
             "B triggers on\nA falling edges with B held high.", (101.6, 175.26))

    # =================================================================== SYNC gate on VREF
    g = b.part("74xGxx:74LVC1G08", "U256", "LVC1G08", (180.34, 96.52), tf="n",
               ref_at=(185.42, 104.14), value_at=(185.42, 106.68), justify="left")
    w(q1, (160.02, q1[1]), (160.02, g.pin("1")[1]), g.pin("1"))
    qok = os_.pin("5")
    w(qok, (162.56, qok[1]), (162.56, g.pin("2")[1]), g.pin("2"))
    b.lab("CLK_OK", (162.56, 111.76), 90)
    vg = g.pin("5")
    vcc((vg[0], 73.66), "VREF_ACF")
    w((vg[0], 73.66), vg)
    c266 = C("C266", "100n", (172.72, 81.28), extra={"Decouples": "U256.5"}, tf="vl")
    w((vg[0], 76.2), (172.72, 76.2), c266.pin("1"))
    rtn(c266.pin("2"))
    rtn(g.pin("3"))
    r260 = R("R260", "100R", (198.12, 96.52), rot=90)
    w(g.pin("4"), r260.pin("1"))
    r261 = R("R261", "10k", (205.74, 104.14), tf="v")
    w(r260.pin("2"), (205.74, 96.52), r261.pin("1"))
    rtn(r261.pin("2"))
    w((205.74, 96.52), (205.74, 88.9))
    b.glab("ACF_SYNC", (205.74, 88.9), 90, "output")
    sch.text("Only this gate runs from VREF, so SYNC <= VREF + 0.3 V in every\n"
             "state; 10k holds SYNC low when VREF is off (IOFF output).\n"
             "VREF budget <= 0.6 mA of 5 mA. B-sync-clock.md", (119.38, 63.5))
    sch.box((12.7, 30.48), (213.36, 195.58), "PRIMARY SYNC CLOCK (VPRI_RTN)  ->  UCC2897A SYNC")

    # =================================================================== barrier
    b.dashed((BARRIER_X, 25.4), (BARRIER_X, 205.74))
    sch.text("ISOLATION BARRIER", (218.44, 27.94))
    sch.text("Nothing crosses here: the clock stays primary,\nthe detector and buffer are secondary.",
             (12.7, 200.66))

    # =================================================================== VSR bias buck (secondary)
    lm5019_buck(b, 203.2, -203.2, dict(U="U251", L="L251", RON="R251", RFBT="R252", RFBB="R253", RUVT="R254",
                                       RUVB="R255", RR="R256", CIN="C251", CIN2="C252", CVCC="C253",
                                       CBST="C254", COUT="C255", CR="C256", CAC="C257"),
                dict(RON="280k_8", RFBT="71k5", RUVT="51k1_8", RR="82k", L="L220"), "VBUS", "VSR", gnd,
                "VSR 10 V BIAS BUCK (SECONDARY)",
                "VSR 10 V (9.7-10.3), <= 37 mA: NCP4306s, TL431s, opto LED, INA281,\n"
                "droop comparator. Starts at VBUS 7.48 V (51.1k/10k), dropout below\n"
                "~10.6 V. 400 kHz (RON 280k); Type III Rr 82k, Cr 1n, Cac 100n. B-bias.md")

    # =================================================================== VBUS-droop comparator
    vcc((233.68, 144.78), "VBUS")
    r263 = R("R263", "150k_p", (233.68, 152.40), tf="l")
    w((233.68, 144.78), r263.pin("1"))
    r264 = R("R264", "10k_p", (233.68, 170.18), tf="l")
    w(r263.pin("2"), r264.pin("1"))
    gnd(r264.pin("2"))
    yv = 162.56
    c267 = C("C267", "33n", (243.84, 167.64), tf="v")
    w((233.68, yv), (243.84, yv), c267.pin("1"))
    gnd(c267.pin("2"))
    b.lab("VBD", (264.16, yv), 0)
    cmp1 = b.part("Comparator:LM393", "U257", "LM393", (292.1, 160.02), tf="n",
                  ref_at=(289.56, 152.40), value_at=(289.56, 154.94), justify="left")
    w((243.84, yv), cmp1.pin("2"))
    # reference: TL431 as a 2.495 V shunt from VSR through 3.9k (no capacitor: n-1)
    u258 = b.part("Reference_Voltage:TL431DBZ", "U258", "TL431B", (259.08, 149.86), rot=90, tf="n",
                  ref_at=(246.38, 151.13), value_at=(246.38, 153.67), justify="left")
    kk, rf = u258.pin("1"), u258.pin("2")
    w(rf, (rf[0], kk[1] - 2.54), (kk[0], kk[1] - 2.54))
    w(kk, (kk[0], kk[1] - 2.54))
    r262 = R("R262", "3k9", (259.08, 138.43), tf="l")
    w(r262.pin("2"), (259.08, kk[1] - 2.54))
    vcc(r262.pin("1"), "VSR")
    gnd(u258.pin("3"))
    yr = kk[1] - 2.54
    w((259.08, yr), (266.7, yr))
    b.lab("VREF_D", (266.7, yr), 90)
    r265 = R("R265", "10k", (274.32, yr), rot=90)
    w((266.7, yr), r265.pin("1"))
    xp = 281.94
    w(r265.pin("2"), (xp, yr), (xp, cmp1.pin("3")[1]), cmp1.pin("3"))
    outp = cmp1.pin("1")
    xo = 304.8
    w(outp, (xo, outp[1]))
    r266 = R("R266", "866k", (293.37, 140.97), rot=90)
    w((xp, 140.97), r266.pin("1"))
    w((xp, 140.97), (xp, yr))
    w(r266.pin("2"), (xo, 140.97), (xo, outp[1]))
    r267 = R("R267", "3k3", (312.42, 148.59), tf="v")
    vcc(r267.pin("1"), "VSR")
    w((xo, outp[1]), (312.42, outp[1]), r267.pin("2"))
    r268 = R("R268", "10k", (322.58, outp[1]), rot=90, tf="ha")
    w((312.42, outp[1]), r268.pin("1"))
    q251 = b.part("Transistor_FET:2N7002", "Q251", "2N7002", (335.28, outp[1]), tf="n",
                  ref_at=(340.36, outp[1] + 3.81), value_at=(340.36, outp[1] + 6.35), justify="left")
    w(r268.pin("2"), q251.pin("1"))
    r269 = R("R269", "15k", (328.93, outp[1] + 7.62), tf="n", ref_at=(323.85, outp[1] + 9.53),
             value_at=(325.63, outp[1] + 9.53), ref_rot=90, justify="")
    w((328.93, outp[1]), r269.pin("1"))
    gnd(r269.pin("2"))
    gnd(q251.pin("2"))
    dq = q251.pin("3")
    w(dq, (dq[0], 149.86), (347.98, 149.86))
    b.glab("POE_LOSS_N", (347.98, 149.86), 0, "output")
    # unused half: + to GND, - to the reference, output open
    cmp2 = b.part("Comparator:LM393", "U257", "LM393", (292.1, 190.50), unit=2, tf="n",
                  ref_at=(297.18, 184.15), value_at=(297.18, 186.69), justify="left")
    w(cmp2.pin("5"), (279.4, cmp2.pin("5")[1]))
    gnd((279.4, cmp2.pin("5")[1]))
    w(cmp2.pin("6"), (271.78, cmp2.pin("6")[1]))
    b.lab("VREF_D", (271.78, cmp2.pin("6")[1]), 180)
    sch.no_connect(cmp2.pin("7"))
    cmpp = b.part("Comparator:LM393", "U257", "LM393", (254.0, 193.04), unit=3, tf="n",
                  ref_at=(243.84, 190.50), value_at=(243.84, 193.04), justify="right")
    vp = cmpp.pin("8")
    vcc((vp[0], 180.34), "VSR")
    w((vp[0], 180.34), vp)
    c268 = C("C268", "100n", (259.08, 187.96), extra={"Decouples": "U257.8"}, tf="v")
    w((vp[0], 182.88), (259.08, 182.88), c268.pin("1"))
    gnd(c268.pin("2"))
    gnd(cmpp.pin("4"))
    sch.text("POE_LOSS_N low when VBUS < 39.5 V (38.5-40.5), released > 41.1 V\n(40.0-42.2); "
             "150k/10k 0.1 %, 33n: tau 0.31 ms. 2N7002 via 10k/15k\n(gate 0.42 V max when off). "
             "Pull-up 4.7k to +3V3 at the FPGA (block E).\nB-vbus-droop.md", (222.25, 213.36))
    sch.box((218.44, 127.0), (365.76, 226.06), "VBUS DROOP DETECTOR")

    # =================================================================== ACF_PULSE buffer
    yb = 50.8
    b.glab("DRV_FWD", (350.52, yb), 180, "input")
    r270 = R("R270", "10k", (358.14, yb), rot=90)
    w((350.52, yb), r270.pin("1"))
    r271 = R("R271", "4k99", (365.76, yb + 7.62), tf="v")
    gb = b.part("74xGxx:74LVC2G08", "U259", "LVC2G08", (386.08, yb - 2.54), unit=2, tf="n",
                ref_at=(381.0, yb + 6.35), value_at=(381.0, yb + 8.89), justify="left")
    w(r270.pin("2"), gb.pin("6"))
    w((365.76, yb), r271.pin("1"))
    gnd(r271.pin("2"))
    p5 = gb.pin("5")
    w(p5, (368.3, p5[1]), (368.3, 40.64))
    vcc((368.3, 40.64), "+3V3")
    o3 = gb.pin("3")
    w(o3, (401.32, o3[1]))
    b.glab("ACF_PULSE", (401.32, o3[1]), 90, "output")
    ga = b.part("74xGxx:74LVC2G08", "U259", "LVC2G08", (386.08, yb + 25.4), unit=1, tf="n",
                ref_at=(372.11, yb + 33.02), value_at=(372.11, yb + 35.56), justify="left")
    w(ga.pin("1"), (368.3, ga.pin("1")[1]), (368.3, ga.pin("2")[1]), ga.pin("2"))
    gnd((368.3, ga.pin("2")[1]))
    sch.no_connect(ga.pin("7"))
    gp = b.part("74xGxx:74LVC2G08", "U259", "LVC2G08", (388.62, yb + 55.88), unit=3, tf="n",
                ref_at=(383.54, yb + 53.34), value_at=(383.54, yb + 55.88), justify="right")
    vcc((388.62, yb + 40.64), "+3V3")
    w((388.62, yb + 40.64), gp.pin("8"))
    c269 = C("C269", "100n", (396.24, yb + 49.53), extra={"Decouples": "U259.8"}, tf="v")
    w((388.62, yb + 43.18), (396.24, yb + 43.18), c269.pin("1"))
    gnd(c269.pin("2"))
    gnd(gp.pin("4"))
    sch.text("DRV_FWD (10 V forward-SR gate)\n/ 3 -> 3.33 V -> gate B (+3V3,\n5.5 V-tolerant inputs) "
             "-> ACF_PULSE:\none edge per conduction pulse,\n737.28 kHz locked. FPGA B6 via\n"
             "block E's 4.7k; clock-fault rule\nin B-interfaces.md. Gate A unused.", (340.36, 93.98))
    sch.box((337.82, 30.48), (408.94, 124.46), "ACF_PULSE BUFFER (+3V3)")
    return sch


if __name__ == "__main__":
    s = build()
    s.save()
    print("wrote", s.file)
