"""audio_out.py -- block F sheet 12: 4-tap 1-bit DAC, reconstruction filter, DC servo, headphone
class-AB stage, line driver, mute relays with DC/PoE-loss protection, output jacks.

Audits: design/parts/F-overview.md, F-dac-74lvc74.md, F-clk-buffer.md, F-filter-passives.md,
F-opamp-sa5532.md, F-servo-opa2277.md, F-hp-output-stage.md, F-mute-relay.md, F-esd.md, F-jacks.md.
Run from the repo root:  python3 hw/satellite/a/gen/audio_out.py

Layout (A2). Each channel is one horizontal band, signal flowing left to right:
    DAC_x0..3 (FPGA) -> 33R -> 74LVC74 taps -> 2.2k sums (P+ above, P- below)
    -> passive pole + differential MFB (SA5532) with the OPA2277 servo above it
    -> headphone class-AB stage;  filter output also runs along the band's bottom to the line relay.
L channel on top, R channel below. The shared parts (MCLK_Q buffer, supplies and decoupling) sit
in the band between them, and the relays, protection and jacks in the right-hand column.
"""
from __future__ import annotations

import hier
from f_parts import Placer

sch = hier.SubSheet("audio_out", paper="A2",
                    comments=["Block F. Audits: design/parts/F-*.md",
                              "DAC/filter: F-dac-74lvc74.md, F-filter-passives.md; HP: F-hp-output-stage.md"])
pl = Placer(sch, 1000)
W, J, T = sch.wire, sch.junction, sch.text


def glabel(name, at, rot=0, shape="input"):
    sch.label(name, at, rot=rot, kind="global_label", shape=shape)


def label(name, at, rot=0):
    sch.label(name, at, rot=rot)


def hR(key, x, y, top=False, **kw):
    if top:
        return pl.R(key, (x, y), horiz=True, ref_at=(x - 2.54, y - 5.08), value_at=(x - 2.54, y - 2.54), **kw)
    return pl.R(key, (x, y), horiz=True, ref_at=(x - 2.54, y - 2.54), value_at=(x - 2.54, y + 3.81), **kw)


def hC(key, x, y, top=False, **kw):
    if top:
        return pl.C(key, (x, y), horiz=True, ref_at=(x - 2.54, y - 6.35), value_at=(x - 2.54, y - 3.81), **kw)
    return pl.C(key, (x, y), horiz=True, ref_at=(x - 2.54, y - 3.81), value_at=(x - 2.54, y + 5.08), **kw)


def vR(key, x, y, left=False, **kw):
    if left:
        return pl.R(key, (x, y), ref_at=(x - 2.54, y - 1.27), value_at=(x - 2.54, y + 1.27), justify="right", **kw)
    return pl.R(key, (x, y), ref_at=(x + 2.54, y - 1.27), value_at=(x + 2.54, y + 1.27), **kw)


def vC(key, x, y, left=False, **kw):
    if left:
        return pl.C(key, (x, y), ref_at=(x - 2.54, y - 1.27), value_at=(x - 2.54, y + 1.27), justify="right", **kw)
    return pl.C(key, (x, y), ref_at=(x + 2.54, y - 1.27), value_at=(x + 2.54, y + 1.27), **kw)


def gnd_below(p, d=0.0):
    if d:
        W(p, (p[0], p[1] + d))
    pl.gnd((p[0], p[1] + d))


def pwr_above(net, p, d=0.0):
    if d:
        W(p, (p[0], p[1] - d))
    pl.pwr(net, (p[0], p[1] - d))


def pwr_below(net, p, d=2.54):
    """A negative rail drawn under a pin: wire down, then the (upward) -15V symbol."""
    W(p, (p[0], p[1] + d))
    pl.pwr(net, (p[0], p[1] + d))


# reference blocks: the two dual op-amps and the servo, shared by both channels
U_F = pl.ref("U")      # SA5532: filter/line driver, A = L, B = R
U_HP = pl.ref("U")     # SA5532: headphone drivers, A = L, B = R
U_SV = pl.ref("U")     # OPA2277: DC servos, A = L, B = R
U_CK = pl.ref("U")     # SN74LVC2G34 MCLK_Q buffer
U_FF = {"L": [pl.ref("U"), pl.ref("U")], "R": [pl.ref("U"), pl.ref("U")]}   # 74LVC74 per channel

# x columns shared by both bands
XU = [68.58, 114.3, 160.02, 205.74]           # the four flip-flop taps
X_P, X_R1, X_C1, X_RINJ, X_R3, X_R3D, X_R2, X_C2, X_DN = 236.22, 246.38, 254, 274.32, 281.94, 289.56, 299.72, 307.34, 322.58
X_OA = 337.82                                   # filter op-amp
X_FB = 350.52                                   # filter output / feedback vertical
X_SV = 330.2                                  # servo op-amp


def channel(ch: str, Yc: float, unit: int):
    """One audio channel band centred on Yc. unit: 1 for L (op-amp halves A), 2 for R (B)."""
    sfx = ch
    # ---------------------------------------------------------------- DAC taps
    sch.box((20.32, Yc - 33.02), (228.6, Yc + 33.02),
            f"{ch} 1-BIT DAC: 4-TAP FIR, 74LVC74 ON +3V3_Q, CLOCKED BY MCLK_FF (F-dac-74lvc74.md)")
    y_pp, y_pn = Yc - 20.32, Yc + 20.32
    first_q, first_qn = None, None
    for k, xu in enumerate(XU):
        pkg = U_FF[ch][k // 2]
        ff = pl.part("74xx:74HC74", "U", "74LVC74", (xu, Yc), unit=k % 2 + 1, ref=pkg,
                     ref_at=(xu - 12.7, Yc + 12.7), value_at=(xu - 12.7, Yc + 15.24))
        d, c, q, qn, s, r = (ff.pin(n) for n in (("2", "3", "5", "6", "4", "1") if k % 2 == 0
                                                  else ("12", "11", "9", "8", "10", "13")))
        rs = hR("33R", xu - 17.78, d[1], top=True, note="series R: place at the FPGA ball")
        W(rs.pin("2"), d)
        glabel(f"DAC_{sfx}{k}", rs.pin("1"), rot=180, shape="input")
        W(c, (c[0] - 2.54, c[1]), (c[0] - 2.54, c[1] + 7.62))
        label("MCLK_FF", (c[0] - 2.54, c[1] + 7.62), rot=180)
        pl.pwr("+3V3_Q", s)
        W(r, (r[0], r[1] + 2.54), (r[0] + 5.08, r[1] + 2.54))
        pl.pwr("+3V3_Q", (r[0] + 5.08, r[1] + 2.54))
        # Q -> 2.2k up to P+, Q_bar -> 2.2k down to P-
        xq, xqn = q[0] + 2.54, q[0] + 7.62
        rq = vR("2k2_tf", xq, Yc - 12.7, note=f"tap {k} Q")
        rqn = vR("2k2_tf", xqn, Yc + 12.7, note=f"tap {k} Q_bar")
        W(q, (xq, q[1]), rq.pin("2"))
        W(qn, (xqn, qn[1]), rqn.pin("1"))
        W(rq.pin("1"), (xq, y_pp))
        W(rqn.pin("2"), (xqn, y_pn))
        if first_q is None:
            first_q, first_qn = xq, xqn
        else:
            J((xq, y_pp)); J((xqn, y_pn))
    T("R_T 2.2k x 4 per side = 550 Ω; FIR zeros at 1.536 and 3.072 MHz", (25.4, Yc + 30.48))
    # ---------------------------------------------------------------- filter, + side (top)
    sch.box((231.14, Yc - 66.04), (355.6, Yc + 45.72),
            f"{ch} RECONSTRUCTION FILTER, 3rd-ORDER BUTTERWORTH 47 kHz, GAIN 3.51 (F-filter-passives.md)")
    W((first_q, y_pp), (X_P, y_pp))
    label(f"P{sfx}+", (first_q + 25.4, y_pp))
    c0p = vC("15n_c0g", X_P, y_pp + 3.81)
    gnd_below(c0p.pin("2"))
    r1p = hR("560R_tf", X_R1, y_pp, top=True)
    W((X_P, y_pp), r1p.pin("1")); J((X_P, y_pp))
    r2p = hR("750R_tf", X_R2, y_pp, top=True)
    W(r1p.pin("2"), (X_C1, y_pp), (X_RINJ, y_pp), (X_R3, y_pp), r2p.pin("1"))
    c1p = vC("8n2_c0g", X_C1, y_pp + 3.81)
    gnd_below(c1p.pin("2"))
    r3p = vR("3k9_tf", X_R3, y_pp + 3.81)
    gnd_below(r3p.pin("2"))
    rinj = vR("20k_tf", X_RINJ, Yc - 26.67, note="R_INJ: servo injection")
    W(rinj.pin("2"), (X_RINJ, y_pp))
    for x in (X_C1, X_RINJ, X_R3):
        J((x, y_pp))
    label(f"X{sfx}+", (X_R3 + 1.27, y_pp))
    c2p = vC("330p_c0g", X_C2, y_pp + 3.81)
    gnd_below(c2p.pin("2"))
    oa = pl.part("Amplifier_Operational:SA5532", "U", "SA5532", (X_OA, Yc), unit=unit, ref=U_F,
                 ref_at=(X_OA + 2.54, Yc - 6.35), value_at=(X_OA + 2.54, Yc + 6.35))
    pin_p, pin_n, pin_o = (oa.pin(n) for n in (("3", "2", "1") if unit == 1 else ("5", "6", "7")))
    W(r2p.pin("2"), (X_C2, y_pp), (X_DN, y_pp), (X_DN, pin_p[1]), pin_p)
    J((X_C2, y_pp))
    label(f"IN{sfx}+", (X_C2 + 2.54, y_pp))
    # - side (bottom)
    W((first_qn, y_pn), (X_P, y_pn))
    label(f"P{sfx}-", (first_qn + 25.4, y_pn))
    c0n = vC("15n_c0g", X_P, y_pn + 3.81)
    gnd_below(c0n.pin("2"))
    r1n = hR("560R_tf", X_R1, y_pn, top=True)
    W((X_P, y_pn), r1n.pin("1")); J((X_P, y_pn))
    r2n = hR("750R_tf", X_R2, y_pn, top=True)
    W(r1n.pin("2"), (X_C1, y_pn), (X_RINJ, y_pn), (X_R3D, y_pn), r2n.pin("1"))
    c1n = vC("8n2_c0g", X_C1, y_pn + 3.81)
    gnd_below(c1n.pin("2"))
    rbal = vR("20k_tf", X_RINJ, y_pn + 3.81, note="R_BAL: matches R_INJ")
    gnd_below(rbal.pin("2"))
    for x in (X_C1, X_RINJ, X_R3D):
        J((x, y_pn))
    label(f"X{sfx}-", (X_R3D + 1.27, y_pn))
    # R3- from X- to the output, C2- from IN- to the output, both along the bottom
    y_r3, y_c2 = Yc + 35.56, Yc + 27.94
    W((X_R3D, y_pn), (X_R3D, y_r3))
    r3n = hR("3k9_tf", 330.2, y_r3, note="R3-: feedback")
    W((X_R3D, y_r3), r3n.pin("1"))
    W(r2n.pin("2"), (X_C2, y_pn), (X_DN, y_pn), (X_DN, pin_n[1]), pin_n)
    W((X_C2, y_pn), (X_C2, y_c2))
    c2n = hC("330p_c0g", 330.2, y_c2, top=True)
    W((X_C2, y_c2), c2n.pin("1")); J((X_C2, y_pn))
    W(pin_o, (X_FB, pin_o[1]))
    W(c2n.pin("2"), (X_FB, y_c2)); W(r3n.pin("2"), (X_FB, y_r3))
    W((X_FB, pin_o[1]), (X_FB, y_c2), (X_FB, y_r3))
    J((X_FB, pin_o[1])); J((X_FB, y_c2))
    if ch == "L":      # FILT_L is also the loopback net to audio_in, so it is global everywhere
        glabel("FILT_L", (X_FB + 1.27, pin_o[1]), rot=90, shape="output")
    else:
        label(f"FILT_{sfx}", (X_FB + 1.27, pin_o[1]))
    # ---------------------------------------------------------------- DC servo (above the filter)
    sv = pl.part("Amplifier_Operational:OPA2277", "U", "OPA2277", (X_SV, Yc - 40.64), unit=unit, ref=U_SV,
                 mirror="x", ref_at=(X_SV + 2.54, Yc - 48.26), value_at=(X_SV + 7.62, Yc - 35.56))
    s_n, s_p, s_o = (sv.pin(n) for n in (("2", "3", "1") if unit == 1 else ("6", "5", "7")))
    rs_ = hR("1M_tf", 307.34, s_n[1], top=True, note="R_S: servo integrator")
    x_cs = 316.23
    W(rs_.pin("2"), (x_cs, s_n[1]), s_n)
    y_cs = Yc - 50.8
    cs = hC("100n_c0g", X_SV, y_cs, top=True, note="C_S: tau 0.1 s, f_HP 0.31 Hz")
    W((x_cs, s_n[1]), (x_cs, y_cs), cs.pin("1")); J((x_cs, s_n[1]))
    W(cs.pin("2"), (340.36, y_cs), (340.36, s_o[1]), s_o)
    gnd_below(s_p, 2.54)
    y_so = Yc - 30.48
    W((340.36, s_o[1]), (340.36, y_so), (X_RINJ, y_so), rinj.pin("1")); J((340.36, s_o[1]))
    label(f"SERVO_{sfx}", (292.1, y_so))
    W((X_FB, pin_o[1]), (X_FB, Yc - 55.88), (299.72, Yc - 55.88), (299.72, s_n[1]), rs_.pin("1"))
    T("DC servo, OPA2277: IN+ to GND directly\n(offset <= IB x 1M = 2.8 mV, F-servo-opa2277.md)",
      (236.22, Yc - 50.8))
    # ---------------------------------------------------------------- line driver build-out and clamp
    # the line branch runs left under the filter: clamp on the op-amp side, then R_BO
    y_lo = Yc + 53.34
    W((X_FB, y_r3), (X_FB, y_lo)); J((X_FB, y_r3))
    x_lc = X_FB - 15.24
    lcl = pl.part("studio_F:BAV99_NXP", "D", "BAV99", (x_lc, y_lo + 5.08), mirror="x",
                  ref_at=(x_lc - 3.81, y_lo + 15.24), value_at=(x_lc + 3.81, y_lo + 15.24))
    pl.pwr("+15V", lcl.pin("2")); pwr_below("-15V", lcl.pin("1"), 2.54)
    rbo = hR("100R_1206", x_lc - 15.24, y_lo, top=True, note="R_BO: line build-out, short-proof (F-opamp-sa5532.md)")
    W((X_FB, y_lo), (x_lc, y_lo), rbo.pin("2")); J((x_lc, y_lo))
    W(lcl.pin("3"), (x_lc, y_lo))
    W(rbo.pin("1"), (x_lc - 25.4, y_lo))
    label(f"LO_{sfx}", (x_lc - 25.4, y_lo), rot=180)
    T("LINE DRIVER: clamp + 100 Ω build-out -> line relay", (x_lc - 45.72, y_lo + 10.16))
    return dict(filt=(X_FB, pin_o[1]), r3_bottom=(X_FB, y_r3))


def hp_stage(ch: str, Yc: float, unit: int, filt):
    """Headphone driver: SA5532 + current-source-fed spreader + BCP56/BCP53 with limiter (F-hp-output-stage.md)."""
    sfx = ch
    sch.box((360.68, Yc - 43.18), (515.62, Yc + 63.5),
            f"{ch} HEADPHONE STAGE, GAIN 1.30, CLASS AB INSIDE THE LOOP (F-hp-output-stage.md)")
    # input stopper and op-amp
    r_in = hR("100R", 365.76, filt[1], top=True)
    W(filt, r_in.pin("1")); J(filt)
    hp = pl.part("Amplifier_Operational:SA5532", "U", "SA5532", (386.08, Yc + 2.54), unit=unit, ref=U_HP,
                 ref_at=(383.54, Yc - 6.35), value_at=(383.54, Yc - 3.81))
    h_p, h_n, h_o = (hp.pin(n) for n in (("3", "2", "1") if unit == 1 else ("5", "6", "7")))
    W(r_in.pin("2"), h_p)
    r_d = hR("1k_1206", 401.32, h_o[1], top=True, note="R_D: keeps the op-amp out of current limit in a short (M1)")
    W(h_o, r_d.pin("1"))
    # spreader BAV99 + R_SPR between N_T and N_B
    x_sp, y_nt, y_nb = 414.02, Yc - 5.08, Yc + 25.4
    sp = pl.part("studio_F:BAV99_NXP", "D", "BAV99", (x_sp, Yc + 2.54), rot=270,
                 ref_at=(x_sp + 3.81, Yc + 6.35), value_at=(x_sp + 3.81, Yc + 8.89), justify="left")
    W(r_d.pin("2"), sp.pin("3"))
    rspr = vR("10R", x_sp, Yc + 13.97, note="R_SPR: Iq trim 0-22 Ω, 10 Ω fitted")
    W(sp.pin("2"), rspr.pin("1"))
    W(rspr.pin("2"), (x_sp, y_nb))
    # current sources: Q_ST (BC857) on top, Q_SB (BC847) below, ~4 mA each
    x_cs = 426.72
    qst = pl.part("Transistor_BJT:BC857", "Q", "BC857", (424.18, Yc - 17.78), mirror="x",
                  ref_at=(428.22, Yc - 19.05), value_at=(428.22, Yc - 16.51))
    res = vR("180R", x_cs, Yc - 26.67)
    W(qst.pin("2"), res.pin("2"))
    pwr_above("+15V", res.pin("1"))
    W(qst.pin("3"), (x_cs, y_nt))
    drs = pl.part("studio_F:BAV99_NXP", "D", "BAV99", (x_sp, Yc - 25.4), rot=270,
                  ref_at=(x_sp + 3.81, Yc - 27.94), value_at=(x_sp + 3.81, Yc - 25.4), justify="left")
    pwr_above("+15V", drs.pin("1"))
    sch.no_connect(drs.pin("3"))
    W(drs.pin("2"), qst.pin("1"))
    rref = vR("15k", x_sp - 10.16, Yc - 13.97, left=True)
    W((x_sp - 10.16, Yc - 17.78), rref.pin("1")); W((x_sp - 10.16, Yc - 17.78), (x_sp, Yc - 17.78)); J((x_sp, Yc - 17.78))
    gnd_below(rref.pin("2"))
    qsb = pl.part("Transistor_BJT:BC847", "Q", "BC847", (424.18, Yc + 38.1),
                  ref_at=(428.22, Yc + 36.83), value_at=(428.22, Yc + 39.37))
    res2 = vR("180R", x_cs, Yc + 46.99)
    W(qsb.pin("2"), res2.pin("1"))
    pwr_below("-15V", res2.pin("2"))
    W(qsb.pin("3"), (x_cs, y_nb))
    drs2 = pl.part("studio_F:BAV99_NXP", "D", "BAV99", (x_sp, Yc + 45.72), rot=270,
                   ref_at=(x_sp + 3.81, Yc + 48.26), value_at=(x_sp + 3.81, Yc + 50.8), justify="left")
    sch.no_connect(drs2.pin("3"))
    pwr_below("-15V", drs2.pin("2"))
    W(drs2.pin("1"), qsb.pin("1"))
    rref2 = vR("15k", x_sp - 10.16, Yc + 41.91, left=True)
    W((x_sp - 10.16, Yc + 38.1), rref2.pin("1")); W((x_sp - 10.16, Yc + 38.1), (x_sp, Yc + 38.1)); J((x_sp, Yc + 38.1))
    gnd_below(rref2.pin("2"))
    T("Q_ST/Q_SB: (2 VF - VBE)/180 = 4 mA", (x_cs + 5.08, Yc - 31.75))
    # N_T / N_B rails of the spreader
    x_lim = 439.42
    W(sp.pin("1"), (x_cs, y_nt), (x_lim, y_nt))
    W((x_sp, y_nb), (x_cs, y_nb), (x_lim, y_nb))
    J((x_cs, y_nt)); J((x_cs, y_nb))
    label(f"NT_{sfx}", (x_sp + 1.27, y_nt)); label(f"NB_{sfx}", (x_sp + 1.27, y_nb))
    # base stoppers and output transistors
    rbn = hR("100R", 443.23, y_nt, top=True)
    rbp = hR("100R", 443.23, y_nb)
    qn = pl.part("Transistor_BJT:BCP56", "Q", "BCP56", (464.82, Yc - 5.08),
                 ref_at=(472.44, Yc - 7.62), value_at=(472.44, Yc - 5.08))
    qp = pl.part("Transistor_BJT:BCP53", "Q", "BCP53", (464.82, Yc + 25.4), mirror="x",
                 ref_at=(472.44, Yc + 30.48), value_at=(472.44, Yc + 33.02))
    x_dr = 454.66
    W(rbn.pin("2"), (x_dr, y_nt), qn.pin("1"))
    W(rbp.pin("2"), (x_dr, y_nb), qp.pin("1"))
    W(qn.pin("2"), (467.36, Yc - 12.7), (469.9, Yc - 12.7), qn.pin("4"))
    pwr_above("+15V", (467.36, Yc - 12.7))
    W(qp.pin("2"), (467.36, Yc + 33.02), (469.9, Yc + 33.02), qp.pin("4"))
    pwr_below("-15V", (467.36, Yc + 33.02), 5.08)
    T("BCP56/BCP53: ≥ 2 cm² copper per tab (hard rule)", (461.01, Yc - 21.59))
    # emitter resistors and OUT_INT
    y_oi = Yc + 10.16
    ren = vR("15R_tf", 467.36, Yc + 6.35)
    rep = vR("15R_tf", 467.36, Yc + 13.97)
    W(qn.pin("3"), ren.pin("1"))
    W(rep.pin("2"), qp.pin("3"))
    # reverse-protection diodes across each B-E (review M1)
    drn = pl.part("Device:D", "D", "1N4148WS", (x_dr, Yc - 1.27), rot=270,
                  ref_at=(x_dr + 1.27, Yc + 5.08), value_at=(x_dr + 1.27, Yc + 7.62))
    drp = pl.part("Device:D", "D", "1N4148WS", (x_dr, Yc + 21.59), rot=270,
                  ref_at=(x_dr + 1.27, Yc + 12.7), value_at=(x_dr + 1.27, Yc + 15.24))
    J((x_dr, y_nt)); J((x_dr, y_nb))
    W(drn.pin("2"), (467.36, Yc + 2.54)); J((467.36, Yc + 2.54))
    W(drp.pin("1"), (467.36, Yc + 17.78)); J((467.36, Yc + 17.78))
    # limiters
    qln = pl.part("Transistor_BJT:BC847", "Q", "BC847", (441.96, Yc + 2.54), mirror="y",
                  ref_at=(438.15, Yc + 1.27), value_at=(438.15, Yc + 3.81), justify="right")
    qlp = pl.part("Transistor_BJT:BC857", "Q", "BC857", (441.96, Yc + 17.78), rot=180,
                  ref_at=(438.15, Yc + 16.51), value_at=(438.15, Yc + 19.05), justify="right")
    W(qln.pin("3"), (x_lim, y_nt)); J((x_lim, y_nt))
    W(qln.pin("1"), drn.pin("2")); J(drn.pin("2"))
    W(qln.pin("2"), (x_lim, y_oi))
    W(qlp.pin("2"), (x_lim, y_oi))
    W(qlp.pin("3"), (x_lim, y_nb)); J((x_lim, y_nb))
    W(qlp.pin("1"), drp.pin("1")); J(drp.pin("1"))
    W((x_lim, y_oi), (467.36, y_oi)); J((x_lim, y_oi)); J((467.36, y_oi))
    label(f"OUT_INT_{sfx}", (444.5, y_oi))
    T("I_lim = VBE/R_E ≈ 43 mA", (428.22, Yc + 60.96))
    # Zobel, feedback tap, R_OUT
    x_z, x_fbt = 482.6, 495.3
    rz = vR("10R", x_z, Yc + 13.97)
    cz = vC("4n7_c0g", x_z, Yc + 21.59)
    W((467.36, y_oi), (x_z, y_oi), rz.pin("1")); W(rz.pin("2"), cz.pin("1"))
    gnd_below(cz.pin("2"))
    J((x_z, y_oi))
    rout = hR("4R7_0805", 502.92, y_oi, top=True, note="R_OUT: outside the loop")
    W((x_z, y_oi), (x_fbt, y_oi), rout.pin("1")); J((x_fbt, y_oi))
    # feedback network Rf || Cf, Rg
    x_fn, y_rf, y_cf, y_fbl = 373.38, Yc + 20.32, Yc + 27.94, Yc + 58.42
    W(h_n, (x_fn, h_n[1]), (x_fn, y_cf))
    rg = vR("3k3_tf", 368.3, y_rf + 3.81, left=True, note="Rg")
    W((x_fn, y_rf), (368.3, y_rf), rg.pin("1")); J((x_fn, y_rf))
    gnd_below(rg.pin("2"))
    rf = hR("1k_tf", 381, y_rf, top=True, note="Rf: gain 1.303")
    cf = hC("1n_c0g", 381, y_cf, note="Cf: 159 kHz")
    W((x_fn, y_rf), rf.pin("1")); W((x_fn, y_cf), cf.pin("1"))
    W(rf.pin("2"), (388.62, y_rf), (388.62, y_cf)); W(cf.pin("2"), (388.62, y_cf))
    W((388.62, y_cf), (388.62, y_fbl), (x_fbt, y_fbl), (x_fbt, y_oi))
    J((388.62, y_cf))
    # OUT_HP: rail clamp, then down to the relay
    x_oh = 510.54
    W(rout.pin("2"), (x_oh, y_oi))
    clp = pl.part("studio_F:BAV99_NXP", "D", "BAV99", (x_oh, y_oi + 5.08), mirror="x",
                  ref_at=(x_oh - 3.81, y_oi + 15.24), value_at=(x_oh + 3.81, y_oi + 15.24))
    W((x_oh, y_oi), clp.pin("3"))
    pl.pwr("+15V", clp.pin("2")); pwr_below("-15V", clp.pin("1"), 2.54)
    W((x_oh, y_oi), (x_oh, y_oi - 5.08)); J((x_oh, y_oi))
    label(f"HPA_{sfx}", (x_oh, y_oi - 5.08), rot=90)
    return (x_oh, y_oi)


# ======================================================================================== bands
YL, YR = 88.9, 304.8
L = channel("L", YL, 1)
R = channel("R", YR, 2)
hpL = hp_stage("L", YL, 1, L["filt"])
hpR = hp_stage("R", YR, 2, R["filt"])

# ======================================================================================== shared band
YM = 196.85                     # centre of the band between L and R

# ---- MCLK_Q buffer (F-clk-buffer.md)
sch.box((20.32, 160.02), (91.44, 234.95), "MCLK_Q BUFFER ON +3V3_Q (F-clk-buffer.md)")
T("VCXO branch, 33 Ω at the source (block E)", (22.86, 167.64))
yb1, yb2 = YM - 20.32, YM - 2.54
b1 = pl.part("74xGxx:74LVC2G34", "U", "LVC2G34", (53.34, yb1), unit=1, ref=U_CK,
             ref_at=(48.26, yb1 - 6.35), value_at=(48.26, yb1 - 3.81))
b2 = pl.part("74xGxx:74LVC2G34", "U", "LVC2G34", (53.34, yb2), unit=2, ref=U_CK,
             ref_at=(48.26, yb2 + 5.08), value_at=(48.26, yb2 + 7.62))
ym_in = (yb1 + yb2) / 2
glabel("MCLK_Q", (25.4, ym_in), rot=180, shape="input")
W((25.4, ym_in), (33.02, ym_in))
W((33.02, yb1), (33.02, yb2))
W((33.02, yb1), b1.pin("1")); W((33.02, yb2), b2.pin("3")); J((33.02, ym_in))
r_ff = hR("22R", 73.66, yb1, top=True, note="1Y: the 8 flip-flop clock inputs")
W(b1.pin("6"), r_ff.pin("1"))
W(r_ff.pin("2"), (81.28, yb1)); label("MCLK_FF", (81.28, yb1))
r_ad = hR("33R", 73.66, yb2, top=True, note="2Y: PCM1808 SCKI (audio_in)")
W(b2.pin("4"), r_ad.pin("1"))
W(r_ad.pin("2"), (81.28, yb2)); glabel("MCLK_ADC", (81.28, yb2), rot=0, shape="output")
bp = pl.part("74xGxx:74LVC2G34", "U", "LVC2G34", (60.96, YM + 20.32), unit=3, ref=U_CK,
             ref_at=(63.5, YM + 19.05), value_at=(63.5, YM + 21.59))
pwr_above("+3V3_Q", bp.pin("5"), 2.54)
gnd_below(bp.pin("2"))
cbk = vC("100n", 50.8, YM + 15.24, left=True, decouples=f"{U_CK}.5")
W((60.96, bp.pin("5")[1] - 2.54), (50.8, bp.pin("5")[1] - 2.54), cbk.pin("1")); J((60.96, bp.pin("5")[1] - 2.54))
gnd_below(cbk.pin("2"))
cbulk = vC("10u_1206", 27.94, YM + 20.32, note="+3V3_Q bulk at the entry point")
pwr_above("+3V3_Q", cbulk.pin("1"), 2.54); gnd_below(cbulk.pin("2"))

# ---- 74LVC74 supply pins with their 100 nF (F-dac-74lvc74.md)
sch.box((93.98, 160.02), (182.88, 234.95), "74LVC74 POWER UNITS, 100 nF AT PIN 14")
T("+3V3_Q SNS:\nKelvin to\nthis row", (135.89, 222.25))
pkgs = U_FF["L"] + U_FF["R"]
for (x, y), ref in zip(((119.38, YM - 12.7), (160.02, YM - 12.7), (119.38, YM + 21.59), (160.02, YM + 21.59)), pkgs):
    u3 = pl.part("74xx:74HC74", "U", "74LVC74", (x, y), unit=3, ref=ref,
                 ref_at=(x + 2.54, y - 1.27), value_at=(x + 2.54, y + 1.27))
    vcc = u3.pin("14")
    pwr_above("+3V3_Q", vcc, 3.81)
    cc = vC("100n", x - 7.62, vcc[1] + 1.27, left=True, decouples=f"{ref}.14")
    W((x, vcc[1] - 3.81), (x - 7.62, vcc[1] - 3.81), cc.pin("1")); J((x, vcc[1] - 3.81))
    gnd_below(cc.pin("2"))
    gnd_below(u3.pin("7"))

# ---- op-amp supply units: 100 nF + 10 uF per rail per package (F-opamp-sa5532.md, F-servo-opa2277.md)
sch.box((185.42, 160.02), (355.6, 234.95), "OP-AMP SUPPLIES: 100 nF + 10 µF PER RAIL AT EACH PACKAGE")
T("Power units (C) of the multi-unit symbols (74LVC74, SA5532, OPA2277); their logic and op-amp\nunits are in the bands. Each cap's Decouples field names its pin, so layout puts it at that package.", (187.96, 166.37))
for x, ref, lib, val in ((213.36, U_F, "Amplifier_Operational:SA5532", "SA5532"),
                         (269.24, U_HP, "Amplifier_Operational:SA5532", "SA5532"),
                         (325.12, U_SV, "Amplifier_Operational:OPA2277", "OPA2277")):
    up = pl.part(lib, "U", val, (x, YM), unit=3, ref=ref, ref_at=(x + 1.27, YM - 1.27), value_at=(x + 1.27, YM + 1.27))
    vp_, vn_ = up.pin("8"), up.pin("4")
    yp, yn = vp_[1] - 10.16, vn_[1] + 10.16
    W(vp_, (vp_[0], yp)); pl.pwr("+15V", (vp_[0], yp))
    W(vn_, (vn_[0], yn)); pl.pwr("-15V", (vn_[0], yn))
    ca = vC("100n", x - 10.16, yp + 5.08, left=True, decouples=f"{ref}.8")
    cb = vC("10u_1206", x + 7.62, yp + 5.08, decouples=f"{ref}.8")
    W((vp_[0], yp), (x - 10.16, yp), ca.pin("1")); W((vp_[0], yp), (x + 7.62, yp), cb.pin("1")); J((vp_[0], yp))
    gnd_below(ca.pin("2")); gnd_below(cb.pin("2"))
    cc_ = vC("100n", x - 10.16, yn + 5.08, left=True, decouples=f"{ref}.4")
    cd = vC("10u_1206", x + 7.62, yn + 5.08, decouples=f"{ref}.4")
    W((vn_[0], yn), (x - 10.16, yn), cc_.pin("1")); W((vn_[0], yn), (x + 7.62, yn), cd.pin("1")); J((vn_[0], yn))
    gnd_below(cc_.pin("2")); gnd_below(cd.pin("2"))

# ======================================================================================== relays and jacks
sch.box((360.68, 157.48), (579.12, 262.89), "OUTPUT RELAYS, DRIVERS, ESD, JACKS")
T("NMJ6HCD2: R-40\nwaiver, decisions.md", (474.98, 200.66))
T("Relays open when unpowered (F-mute-relay.md); ESD at every jack pin (F-esd.md)", (362.0, 260.35))
Y_DC, Y_PL = 248.92, 254.0       # /DC_TRIP and POE_LOSS_N buses under the drivers


def relay(xk, yk, en_label, com_labels):
    """HFD4 relay at (xk, yk) with its AO3400A driver below and the BAT54A gate OR to both buses."""
    k = pl.part("studio_F:HFD4", "K", "HFD4", (xk, yk), ref_at=(xk + 2.54, yk - 13.97), value_at=(xk + 2.54, yk - 16.51))
    for pin, name in zip(("3", "6"), com_labels):
        p = k.pin(pin)
        W(p, (p[0] - 5.08, p[1])); label(name, (p[0] - 5.08, p[1]), rot=180)
    for pin in ("2", "7"):
        sch.no_connect(k.pin(pin))
    pwr_above("+5V", k.pin("1"))
    xc = k.pin("8")[0]
    y_d = yk + 27.94
    W(k.pin("8"), (xc, y_d))
    dk = pl.part("Device:D", "D", "1N4148WS", (xc + 10.16, yk + 20.32), rot=270,
                 ref_at=(xc + 13.97, yk + 19.05), value_at=(xc + 13.97, yk + 21.59), note="flyback")
    pwr_above("+5V", dk.pin("1"))
    W(dk.pin("2"), (xc, dk.pin("2")[1])); J((xc, dk.pin("2")[1]))
    q = pl.part("Transistor_FET:AO3400A", "Q", "AO3400A", (xc - 2.54, y_d + 5.08),
                ref_at=(xc + 2.54, y_d + 3.81), value_at=(xc + 2.54, y_d + 6.35))
    gnd_below(q.pin("2"))
    g = q.pin("1")
    x_j = g[0] - 15.24
    rpd = vR("100k", g[0], g[1] + 3.81, left=True, note="gate pull-down: relay off by default")
    W(g, rpd.pin("1")); gnd_below(rpd.pin("2"))
    W(g, (x_j, g[1])); J(g)
    rg = hR("10k", x_j - 6.35, g[1], top=True, note="10k: lets the BAT54A override the FPGA")
    W((x_j, g[1]), rg.pin("2"))
    glabel(en_label, rg.pin("1"), rot=180, shape="input")
    da = pl.part("Diode:BAT54A", "D", "BAT54A", (x_j, Y_DC - 7.62), mirror="x",
                 ref_at=(x_j + 2.54, Y_DC - 13.97), value_at=(x_j + 2.54, Y_DC - 11.43))
    W((x_j, g[1]), da.pin("3")); J((x_j, g[1]))
    W(da.pin("1"), (da.pin("1")[0], Y_DC))
    W(da.pin("2"), (da.pin("2")[0], Y_PL))
    return k, (da.pin("1")[0], da.pin("2")[0])


k1, x1 = relay(408.94, 185.42, "HP_EN", ("HPA_L", "HPA_R"))
k2, x2 = relay(497.84, 185.42, "LO_EN", ("LO_L", "LO_R"))
x_bus0 = 381.0
W((x_bus0, Y_DC), (x1[0], Y_DC), (x2[0], Y_DC)); J((x1[0], Y_DC))
W((x_bus0, Y_PL), (x1[1], Y_PL), (x2[1], Y_PL)); J((x1[1], Y_PL))
glabel("HP_FAULT_N", (x_bus0, Y_DC), rot=180, shape="bidirectional")
glabel("POE_LOSS_N", (x_bus0, Y_PL), rot=180, shape="input")
T("/DC_TRIP (= HP_FAULT_N) or POE_LOSS_N low\npulls both gates to ≤ 0.37 V: relays open\nin hardware (F-mute-relay.md)",
  (515.62, 245.11))

# ---- headphone jack: ferrites, TVS, plug detect on SN (F-jacks.md, F-esd.md)
jh = pl.part("studio_F:NMJ6HCD2_F", "J", "NMJ6", (464.82, 180.34), ref_at=(464.82, 167.64), value_at=(464.82, 196.85))
sch.no_connect(jh.pin("TN")); sch.no_connect(jh.pin("RN"))
no1, no2 = k1.pin("4"), k1.pin("5")
y_t, y_r = 170.18, 198.12
xt = jh.pin("T")[0]
x_fb, x_tv = 429.26, 440.69
W(no1, (no1[0] + 2.54, no1[1]), (no1[0] + 2.54, y_t))
fbt = pl.part("Device:FerriteBead_Small", "FB", "FB600", (x_fb, y_t), rot=90, ref_at=(x_fb - 1.27, y_t - 6.35), value_at=(x_fb - 1.27, y_t - 3.81), justify="right")
W((no1[0] + 2.54, y_t), fbt.pin("1"))
tvt = pl.part("Device:D_TVS", "D", "PESD15", (x_tv, y_t + 3.81), rot=270, ref_at=(x_tv + 3.81, y_t + 2.54), value_at=(x_tv + 3.81, y_t + 5.08))
gnd_below(tvt.pin("2"))
W(fbt.pin("2"), (x_tv, y_t), (xt - 7.62, y_t), (xt - 7.62, jh.pin("T")[1]), jh.pin("T")); J((x_tv, y_t))
W((x_tv, y_t), tvt.pin("1"))
W(no2, (no2[0] + 2.54, no2[1]), (no2[0] + 2.54, y_r))
fbr = pl.part("Device:FerriteBead_Small", "FB", "FB600", (x_fb, y_r), rot=90, ref_at=(x_fb - 1.27, y_r - 6.35), value_at=(x_fb - 1.27, y_r - 3.81), justify="right")
W((no2[0] + 2.54, y_r), fbr.pin("1"))
tvr = pl.part("Device:D_TVS", "D", "PESD15", (x_tv, y_r + 3.81), rot=270, ref_at=(x_tv + 3.81, y_r + 2.54), value_at=(x_tv + 3.81, y_r + 5.08))
gnd_below(tvr.pin("2"))
W(fbr.pin("2"), (x_tv, y_r), (xt - 12.7, y_r), (xt - 12.7, jh.pin("R")[1]), jh.pin("R")); J((x_tv, y_r))
W((x_tv, y_r), tvr.pin("1"))
sp_, ss_ = jh.pin("SN"), jh.pin("S")
W(ss_, (ss_[0] - 2.54, ss_[1]), (ss_[0] - 2.54, ss_[1] + 5.08)); pl.gnd((ss_[0] - 2.54, ss_[1] + 5.08))
x_sn, y_hd = sp_[0] - 10.16, 223.52
W(sp_, (x_sn, sp_[1]), (x_sn, y_hd))
rhd = vR("47k", x_sn - 7.62, y_hd - 3.81, left=True, note="HP_DET pull-up: high = plug in (SN opens)")
pwr_above("+3V3", rhd.pin("1"))
W(rhd.pin("2"), (x_sn - 7.62, y_hd), (x_sn, y_hd))
tvd = pl.part("Device:D_TVS", "D", "PESD15", (x_sn, y_hd + 3.81), rot=270, ref_at=(x_sn - 3.81, y_hd + 2.54), value_at=(x_sn - 3.81, y_hd + 5.08), justify="right")
W((x_sn, y_hd), tvd.pin("1")); gnd_below(tvd.pin("2")); J((x_sn, y_hd))
W((x_sn, y_hd), (x_sn + 5.08, y_hd))
glabel("HP_DET", (x_sn + 5.08, y_hd), rot=0, shape="output")

# ---- line-out RCA jacks
for i, (no, name, yj) in enumerate(((k2.pin("4"), "L", 170.18), (k2.pin("5"), "R", 226.06))):
    xv = no[0] + 2.54 + 2.54 * i
    W(no, (xv, no[1]), (xv, yj))
    jr = pl.part("studio_F:RCJ-01", "J", "RCJ", (563.88, yj), ref_at=(563.88, yj - 5.08), value_at=(563.88, yj + 7.62))
    tv = pl.part("Device:D_TVS", "D", "PESD15", (520.7, yj + 3.81), rot=270, ref_at=(524.51, yj + 2.54), value_at=(524.51, yj + 5.08))
    rpd2 = vR("100k", 543.56, yj + 3.81, note="defines the jack when the relay is open")
    W((xv, yj), (520.7, yj), (543.56, yj), jr.pin("2")); J((520.7, yj)); J((543.56, yj))
    W((520.7, yj), tv.pin("1")); W((543.56, yj), rpd2.pin("1"))
    gnd_below(tv.pin("2")); gnd_below(rpd2.pin("2"))
    W(jr.pin("1"), (jr.pin("1")[0] - 2.54, jr.pin("1")[1]), (jr.pin("1")[0] - 2.54, yj + 7.62))
    pl.gnd((jr.pin("1")[0] - 2.54, yj + 7.62))
    T(f"LINE OUT {name} (RCA)", (548.64, yj - 7.62))

# ======================================================================================== DC detector (top right)
sch.box((518.16, 25.4), (588.01, 154.94), "DC DETECTOR: OPENS BOTH RELAYS (F-mute-relay.md)")
yd = [40.64, 50.8, 60.96, 71.12]
x_nd = 543.56
for y, name in zip(yd, ("HPA_L", "HPA_R", "FILT_L", "FILT_R")):
    rr = hR("47k", 533.4, y, top=True)
    W(rr.pin("1"), (525.78, y))
    if name == "FILT_L":
        glabel(name, (525.78, y), rot=180, shape="input")
    else:
        label(name, (525.78, y), rot=180)
    W(rr.pin("2"), (x_nd, y))
W((x_nd, yd[0]), (x_nd, 99.06))
for y in yd[1:]:
    J((x_nd, y))
label("N_DC", (x_nd, 81.28))
cdc = vC("10u_1206", 553.72, 90.17, note="non-polar X7R: tau 0.12 s with 4 x 47k")
W((x_nd, 86.36), (553.72, 86.36), cdc.pin("1")); J((x_nd, 86.36)); gnd_below(cdc.pin("2"))
rb1 = hR("10k", 551.18, 55.88, top=True)
W((x_nd, 55.88), rb1.pin("1")); J((x_nd, 55.88))
qdn = pl.part("Transistor_BJT:BC847", "Q", "BC847", (560.07, 55.88), ref_at=(565.15, 53.34), value_at=(565.15, 55.88))
W(rb1.pin("2"), qdn.pin("1")); gnd_below(qdn.pin("2"))
rb2 = hR("10k", 551.18, 99.06)
W((x_nd, 99.06), rb2.pin("1"))
qdp = pl.part("Transistor_BJT:BC847", "Q", "BC847", (560.07, 104.14), mirror="x", ref_at=(565.15, 106.68), value_at=(565.15, 109.22))
W(rb2.pin("2"), (562.61, 99.06), qdp.pin("2"))
W(qdp.pin("1"), (554.99, 104.14), (554.99, 106.68)); pl.gnd((554.99, 106.68))
x_tr = 572.77
W(qdn.pin("3"), (562.61, 45.72), (x_tr, 45.72), (x_tr, 119.38))
W(qdp.pin("3"), (562.61, 114.3), (x_tr, 114.3)); J((x_tr, 114.3))
rpu = vR("4k7", x_tr, 39.37, note="/DC_TRIP pull-up, read in hardware (re-review MINOR-3)")
W(rpu.pin("2"), (x_tr, 45.72)); J((x_tr, 45.72)); pwr_above("+3V3", rpu.pin("1"))
glabel("HP_FAULT_N", (x_tr, 119.38), rot=270, shape="output")
T("Trips at ±0.6 V on N_DC:\n2.4 V DC on one output,\n~30 ms incl. relay release.\nFILT_L is a global label: the\nsame net feeds the audio_in\nloopback. FILT_R is local.", (521.97, 127.0))

sch.save()
print("wrote", sch.file)
