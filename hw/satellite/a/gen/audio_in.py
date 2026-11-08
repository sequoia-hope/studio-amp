"""audio_in.py -- block F sheet 13: measurement-mic input (R-15) and on-board MEMS mic (R-16).

Audits: design/parts/F-mic-adc-pcm1808.md, F-opamp-sa5532.md, F-esd.md, F-jacks.md, F-mems-t3902.md.
Run from the repo root:  python3 hw/satellite/a/gen/audio_in.py

Layout (A3, signal flow left to right):
  top band     jack + ESD + plug-in power -> preamp (SA5532 A) -> film coupling + clamp -> PCM1808
  lower left   op-amp supply unit and its decoupling
  lower middle optional loopback of line-out L (SA5532 B buffer) into PCM1808 VINR
  lower right  T3902 MEMS microphone
"""
from __future__ import annotations

import hier
from f_parts import Placer

sch = hier.SubSheet("audio_in", comments=["Block F. Audits: design/parts/F-*.md",
                                          "Mic chain: F-mic-adc-pcm1808.md; MEMS mic: F-mems-t3902.md"])
pl = Placer(sch, 1100)
U_OA = pl.ref("U")                    # SA5532: preamp (A), loopback buffer (B), supply (C)
W, J, T = sch.wire, sch.junction, sch.text


def glabel(name, at, rot=0, shape="input"):
    sch.label(name, at, rot=rot, kind="global_label", shape=shape)


def hR(key, x, y, top=False, **kw):
    """Horizontal resistor centred at (x, y), reference above, value below (or both above)."""
    if top:
        return pl.R(key, (x, y), horiz=True, ref_at=(x - 2.54, y - 5.08), value_at=(x - 2.54, y - 2.54), **kw)
    return pl.R(key, (x, y), horiz=True, ref_at=(x - 2.54, y - 2.54), value_at=(x - 2.54, y + 3.81), **kw)


def hC(key, x, y, **kw):
    return pl.C(key, (x, y), horiz=True, ref_at=(x - 2.54, y - 3.81), value_at=(x - 2.54, y + 5.08), **kw)


def vR(key, x, y, **kw):
    return pl.R(key, (x, y), ref_at=(x + 2.54, y - 1.27), value_at=(x + 2.54, y + 1.27), **kw)


def vC(key, x, y, left=False, **kw):
    if left:
        return pl.C(key, (x, y), ref_at=(x - 2.54, y - 1.27), value_at=(x - 2.54, y + 1.27), justify="right", **kw)
    return pl.C(key, (x, y), ref_at=(x + 2.54, y - 1.27), value_at=(x + 2.54, y + 1.27), **kw)


Y = 76.2          # the main signal row (mic tip -> preamp -> ADC VINL)

# =====================================================================================
# 1. EXT MIC JACK, ESD and plug-in power (F-jacks.md, F-esd.md, F-mic-adc-pcm1808.md)
# =====================================================================================
sch.box((20.32, 38.1), (134.62, 152.4), "EXT MIC JACK, ESD AND PLUG-IN POWER (R-15)")
jm = pl.part("Connector_Audio:AudioJack3", "J", "SJ1", (30.48, Y + 2.54), mirror="x",
             ref_at=(25.4, Y - 6.35), value_at=(25.4, Y - 3.81))
tip, ring, slv = jm.pin("T"), jm.pin("R"), jm.pin("S")
assert abs(tip[1] - Y) < 0.01
T("3.5 mm TRS, CUI SJ1-3523N\nT = mic signal + bias\nR = bias only, S = GND", (22.86, Y + 33.02))
W(slv, (40.64, slv[1]), (40.64, Y + 25.4))
pl.gnd((40.64, Y + 25.4))
# ring: TVS to ground, then R_RING to the bias node
x_rt, x_rr, y_nb = 48.26, 68.58, 127.0
W(ring, (x_rr, ring[1]))
d_r = pl.part("Device:D_TVS", "D", "PESD15", (x_rt, ring[1] + 8.89), rot=270,
              ref_at=(x_rt + 3.81, ring[1] + 7.62), value_at=(x_rt + 3.81, ring[1] + 10.16))
W((x_rt, ring[1]), d_r.pin("1")); J((x_rt, ring[1]))
pl.gnd(d_r.pin("2"))
r_ring = vR("2k2", x_rr, 104.14, note="R_RING")
W((x_rr, ring[1]), r_ring.pin("1"))
# tip: TVS, R_BIAS
x_tt, x_rb = 81.28, 99.06
d_t = pl.part("Device:D_TVS", "D", "PESD15", (x_tt, Y + 11.43), rot=270,
              ref_at=(x_tt + 3.81, Y + 10.16), value_at=(x_tt + 3.81, Y + 12.7))
pl.gnd(d_t.pin("2"))
r_bias = vR("2k2", x_rb, 104.14, note="R_BIAS")
# bias node N_B: Al reservoir and R_F up to +5V_A
x_cnb, x_rf = 109.22, 121.92
c_nb = vC("47u_al", x_cnb, y_nb + 7.62, polar=True, note="Al electrolytic, not ceramic: no piezo pick-up (review M2)")
pl.gnd(c_nb.pin("2"))
r_f = vR("2k2", x_rf, y_nb - 10.16, note="R_F")
pl.pwr("+5V_A", r_f.pin("1"))
W(r_ring.pin("2"), (x_rr, y_nb), (x_rb, y_nb), (x_cnb, y_nb), (x_rf, y_nb), r_f.pin("2"))
W(r_bias.pin("2"), (x_rb, y_nb))
W((x_cnb, y_nb), c_nb.pin("1"))
J((x_rb, y_nb)); J((x_cnb, y_nb))
sch.label("MIC_BIAS", (111.76, y_nb))
T("Plug-in power: 5.0 V open circuit through 4.4 kΩ,\n2.8-3.7 V at a 0.3-0.5 mA electret\n(R-15 deviation, F-overview.md).\nR_F with 47 µF: 1.5 Hz filter on +5V_A.",
  (25.4, 140.97))
# tip line
x_cin = 129.54
c_in = hC("1u_film", x_cin, Y, note="PET film: no piezo pick-up (review M2)")
W(tip, (x_tt, Y), (x_rb, Y), c_in.pin("1"))
W((x_tt, Y), d_t.pin("1")); W((x_rb, Y), r_bias.pin("1"))
J((x_tt, Y)); J((x_rb, Y))
sch.label("MIC_TIP", (43.18, Y))

# =====================================================================================
# 2. PREAMP: SA5532 half A, +12 dB (F-mic-adc-pcm1808.md, F-opamp-sa5532.md)
# =====================================================================================
sch.box((139.7, 38.1), (243.84, 152.4), "MIC PREAMP, +12 dB (SA5532 A)")
r_s = hR("470R", 147.32, Y)
W(c_in.pin("2"), r_s.pin("1"))
x_cl = 162.56                                         # clamp node, BAV99 hangs below
d_cl = pl.part("studio_F:BAV99_NXP", "D", "BAV99", (x_cl, Y + 7.62), mirror="x",
               ref_at=(x_cl - 10.16, Y + 12.7), value_at=(x_cl + 1.27, Y + 12.7))
W((x_cl, Y), d_cl.pin("3"))
pl.pwr("+15V", d_cl.pin("2"))
pl.pwr("-15V", d_cl.pin("1"))
x_b = 177.8
r_b = vR("470k", x_b, Y + 10.16)
pl.gnd(r_b.pin("2"))
ua = pl.part("Amplifier_Operational:SA5532", "U", "SA5532", (205.74, Y + 2.54), unit=1, ref=U_OA,
             ref_at=(203.2, Y - 5.08), value_at=(203.2, Y - 2.54))
W(r_s.pin("2"), (x_cl, Y), (x_b, Y), ua.pin("3"))
W((x_b, Y), r_b.pin("1"))
J((x_cl, Y)); J((x_b, Y))
sch.label("MIC_PRE_IN", (182.88, Y))
# feedback: Rg to ground, Rf || Cf from out to -IN
nin, out = ua.pin("2"), ua.pin("1")
x_g, yfb = 190.5, Y + 17.78
x_o = out[0] + 7.62
W(nin, (x_g, nin[1]), (x_g, yfb))
r_g = vR("1k", x_g, yfb + 7.62, note="Rg")
W((x_g, yfb), r_g.pin("1")); pl.gnd(r_g.pin("2"))
r_fb = hR("3k", 205.74, yfb, note="Rf")
c_fb = pl.C("1n_c0g", (205.74, yfb + 10.16), horiz=True, ref_at=(207.01, yfb + 6.35), value_at=(203.2, yfb + 15.24),
            note="Cf: 53 kHz pole")
W((x_g, yfb), r_fb.pin("1"))
W((r_fb.pin("1")[0] - 2.54, yfb), (r_fb.pin("1")[0] - 2.54, yfb + 10.16), c_fb.pin("1"))
W(c_fb.pin("2"), (x_o, yfb + 10.16), (x_o, yfb))
W(r_fb.pin("2"), (x_o, yfb), (x_o, out[1]))
W(out, (x_o, out[1]))
J((x_g, yfb)); J((r_fb.pin("1")[0] - 2.54, yfb)); J((x_o, yfb)); J((x_o, out[1]))
T("Gain 1 + 3k/1k = 4.0 (+12 dB): clips at 110 dB SPL\nwith a -28 dBV/Pa capsule. Line level plugged in\nby mistake swings ±5.7 V, inside the input range.",
  (172.72, 116.84))

# =====================================================================================
# 3. ADC: PCM1808, film coupling, Schottky clamp (F-mic-adc-pcm1808.md)
# =====================================================================================
sch.box((248.92, 30.48), (403.86, 152.4), "MIC ADC: PCM1808, I2S SLAVE, SCKI = 512 fs")
x_c2 = 259.08
c_adc = hC("1u_film", x_c2, Y, note="PET film coupling (review M2); 2.65 Hz with 60 kΩ")
W((x_o, out[1]), (233.68, out[1]), (233.68, Y), c_adc.pin("1"))
sch.label("MIC_PRE", (236.22, Y))
r_a = hR("2k2", 274.32, Y, note="R_A: limits clamp current to 5.7 mA")
W(c_adc.pin("2"), r_a.pin("1"))
x_j = 287.02                                          # clamp junction, BAT54S hangs below
d_s = pl.part("studio_F:BAT54S_NXP", "D", "BAT54S", (x_j, Y + 7.62), mirror="x",
              ref_at=(x_j - 10.16, Y + 12.7), value_at=(x_j + 1.27, Y + 12.7))
W((x_j, Y), d_s.pin("3"))
pl.gnd(d_s.pin("1"))
pl.pwr("+5V_A", d_s.pin("2"))
r_bb = hR("1k", 299.72, Y, top=True, note="R_B: datasheet 1 kΩ / 1 nF at the pin")
W(r_a.pin("2"), (x_j, Y), r_bb.pin("1")); J((x_j, Y))
u = pl.part("studio_F:PCM1808", "U", "PCM1808", (345.44, Y + 7.62), ref_at=(335.28, Y - 8.89),
            value_at=(345.44, Y - 8.89))
x_cp = 313.69
c_pin = vC("1n_c0g", x_cp, Y + 5.08, decouples=None)
W(r_bb.pin("2"), (x_cp, Y), u.pin("13"))
W((x_cp, Y), c_pin.pin("1")); J((x_cp, Y))
pl.gnd(c_pin.pin("2"))
sch.label("ADC_VINL", (318.77, Y))
# supplies: VCC (+5V_A) and VDD (+3V3), each 100 nF + 10 uF at the pin
vcc, vdd = u.pin("3"), u.pin("4")
y_vcc, y_vdd = 50.8, 43.18
W(vcc, (vcc[0], y_vcc), (322.58, y_vcc), (309.88, y_vcc))
pl.pwr("+5V_A", (337.82, y_vcc))
c_a1 = vC("100n", 322.58, y_vcc + 5.08, decouples=f"{u.ref}.3")
c_a2 = vC("10u_0805", 309.88, y_vcc + 5.08, left=True, decouples=f"{u.ref}.3")
W((322.58, y_vcc), c_a1.pin("1")); W((309.88, y_vcc), c_a2.pin("1"))
J((322.58, y_vcc)); J((337.82, y_vcc))
pl.gnd(c_a1.pin("2")); pl.gnd(c_a2.pin("2"))
W(vdd, (vdd[0], y_vdd), (363.22, y_vdd), (378.46, y_vdd))
pl.pwr("+3V3", (vdd[0], y_vdd))
c_d1 = vC("100n", 363.22, y_vdd + 5.08, decouples=f"{u.ref}.4")
c_d2 = vC("10u_0805", 378.46, y_vdd + 5.08, decouples=f"{u.ref}.4")
W((363.22, y_vdd), c_d1.pin("1")); W((378.46, y_vdd), c_d2.pin("1"))
J((363.22, y_vdd))
pl.gnd(c_d1.pin("2")); pl.gnd(c_d2.pin("2"))
# bottom: VREF caps, grounds and straps (slave mode MD1 = MD0 = L, I2S FMT = L)
vref = u.pin("1")
y_b = vref[1] + 15.24
W(vref, (vref[0], y_b), (350.52, y_b), (365.76, y_b))
c_r1 = vC("100n", 350.52, y_b + 5.08, decouples=f"{u.ref}.1")
c_r2 = vC("10u_al", 365.76, y_b + 5.08, polar=True, decouples=f"{u.ref}.1")
W((350.52, y_b), c_r1.pin("1")); W((365.76, y_b), c_r2.pin("1")); J((350.52, y_b))
pl.gnd(c_r1.pin("2")); pl.gnd(c_r2.pin("2"))
sch.label("ADC_VREF", (340.36, y_b))
y_g = vref[1] + 5.08
gp = [u.pin(n) for n in ("2", "5", "10", "11", "12")]
for p in gp:
    W(p, (p[0], y_g))
W(gp[0], (gp[0][0], y_g)); W((gp[0][0], y_g), (gp[-1][0], y_g))
for p in gp[1:-1]:
    J((p[0], y_g))
W((gp[2][0], y_g), (gp[2][0], y_g + 2.54)); pl.gnd((gp[2][0], y_g + 2.54))
T("MD1 = MD0 = L: slave, SCKI auto-detect\nFMT = L: I2S 24-bit", (312.42, 137.16))
# FPGA side: SCKI from the MCLK_Q buffer (audio_out), I2S to the ECP5 (E-pinmap.md)
x_lab = 381.0
for pin, name, shape in (("6", "MCLK_ADC", "input"), ("8", "MADC_BCK", "input"),
                         ("7", "MADC_LRCK", "input"), ("9", "MADC_DOUT", "output")):
    p = u.pin(pin)
    W(p, (x_lab, p[1]))
    glabel(name, (x_lab, p[1]), rot=0, shape=shape)
T("ECP5 P13 / R14 / L16 (E-pinmap.md);\n330 Ω series on DOUT at block E.\nMCLK_ADC: SN74LVC2G34 2Y via 33 Ω (audio_out).",
  (358.14, 96.52))

# =====================================================================================
# 4. SA5532 supply unit (U1101C) with decoupling at its pins
# =====================================================================================
sch.box((20.32, 160.02), (134.62, 254.0), "SA5532 SUPPLY (U1101)")
upw = pl.part("Amplifier_Operational:SA5532", "U", "SA5532", (78.74, 205.74), unit=3, ref=U_OA,
              ref_at=(81.28, 204.47), value_at=(81.28, 207.01))
vp, vn = upw.pin("8"), upw.pin("4")
y_p, y_n = vp[1] - 7.62, vn[1] + 7.62
W(vp, (vp[0], y_p), (60.96, y_p), (40.64, y_p))
pl.pwr("+15V", (vp[0], y_p))
c1 = vC("100n", 60.96, y_p + 6.35, left=True, decouples=f"{U_OA}.8")
c2 = vC("10u_1206", 40.64, y_p + 6.35, left=True, decouples=f"{U_OA}.8")
W((60.96, y_p), c1.pin("1")); W((40.64, y_p), c2.pin("1")); J((60.96, y_p))
pl.gnd(c1.pin("2")); pl.gnd(c2.pin("2"))
W(vn, (vn[0], y_n), (91.44, y_n), (111.76, y_n))
pl.pwr("-15V", (vn[0], y_n))
c3 = vC("100n", 91.44, y_n + 6.35, decouples=f"{U_OA}.4")
c4 = vC("10u_1206", 111.76, y_n + 6.35, decouples=f"{U_OA}.4")
W((91.44, y_n), c3.pin("1")); W((111.76, y_n), c4.pin("1")); J((91.44, y_n))
pl.gnd(c3.pin("2")); pl.gnd(c4.pin("2"))
T("100 nF + 10 µF per rail within 3 mm of pins 8 and 4\n(F-opamp-sa5532.md)", (25.4, 248.92))

# =====================================================================================
# 5. Optional loopback: line-out L into VINR (DNP by default; F-mic-adc-pcm1808.md)
# =====================================================================================
sch.box((139.7, 160.02), (325.12, 254.0), "LOOPBACK: LINE-OUT L (FILT_L) -> PCM1808 VINR (OPTIONAL, R_LA AND C_LB DNP)")
YL = 195.58
glabel("FILT_L", (147.32, YL), rot=180, shape="input")
r_la = hR("10k", 158.75, YL, dnp=True, note="DNP: fit for latency/level loopback")
W((147.32, YL), r_la.pin("1"))
x_d = 172.72
r_lb = vR("2k2", x_d, YL + 7.62, note="divider 10k/2.2k: 4 Vrms -> 0.72 Vrms")
W(r_la.pin("2"), (x_d, YL)); W((x_d, YL), r_lb.pin("1"))
pl.gnd(r_lb.pin("2"))
ub = pl.part("Amplifier_Operational:SA5532", "U", "SA5532", (195.58, YL + 2.54), unit=2, ref=U_OA,
             ref_at=(193.04, YL - 5.08), value_at=(193.04, YL - 2.54))
W((x_d, YL), ub.pin("5")); J((x_d, YL))
o2, n2 = ub.pin("7"), ub.pin("6")
x_o2 = o2[0] + 5.08
W(o2, (x_o2, o2[1]), (x_o2, n2[1] + 7.62), (n2[0] - 2.54, n2[1] + 7.62), (n2[0] - 2.54, n2[1]), n2)
J((x_o2, o2[1]))
c_lb = hC("1u_film", 222.25, o2[1], dnp=True, note="DNP with R_LA")
W((x_o2, o2[1]), c_lb.pin("1"))
r_a2 = hR("2k2", 237.49, o2[1])
W(c_lb.pin("2"), r_a2.pin("1"))
x_j2 = 250.19
d_s2 = pl.part("studio_F:BAT54S_NXP", "D", "BAT54S", (x_j2, o2[1] + 7.62), mirror="x",
               ref_at=(x_j2 - 10.16, o2[1] + 12.7), value_at=(x_j2 + 1.27, o2[1] + 12.7))
W((x_j2, o2[1]), d_s2.pin("3"))
pl.gnd(d_s2.pin("1")); pl.pwr("+5V_A", d_s2.pin("2"))
r_b2 = hR("1k", 262.89, o2[1], top=True)
W(r_a2.pin("2"), (x_j2, o2[1]), r_b2.pin("1")); J((x_j2, o2[1]))
x_v = 309.88
vinr = u.pin("14")
x_cp2 = 280.67
c_pin2 = vC("1n_c0g", x_cp2, o2[1] + 5.08)
W(r_b2.pin("2"), (x_cp2, o2[1]), (x_v, o2[1]), (x_v, vinr[1]), vinr)
W((x_cp2, o2[1]), c_pin2.pin("1")); J((x_cp2, o2[1]))
pl.gnd(c_pin2.pin("2"))
sch.label("ADC_VINR", (284.48, o2[1]))
T("Not fitted: R_LA and C_LB. With them, VINR records line-out L\nfor latency and level calibration (room correction).", (144.78, 241.3))

# =====================================================================================
# 6. MEMS PDM microphone (F-mems-t3902.md)
# =====================================================================================
sch.box((330.2, 160.02), (403.86, 254.0), "ON-BOARD MEMS MIC (R-16)")
mk = pl.part("studio_F:T3902", "MK", "T3902", (370.84, 210.82), ref_at=(381.0, 217.17), value_at=(381.0, 219.71))
clk, sel, dat, vdd2, gnd2 = mk.pin("4"), mk.pin("2"), mk.pin("1"), mk.pin("5"), mk.pin("3")
glabel("PDM_CLK", (342.9, clk[1]), rot=180, shape="input")
W((342.9, clk[1]), clk)
W(sel, (355.6, sel[1]), (355.6, sel[1] + 7.62)); pl.gnd((355.6, sel[1] + 7.62))
T("SELECT = GND: data on the right\nchannel (after CLK falls)", (335.28, 236.22))
W(dat, (391.16, dat[1])); glabel("PDM_DAT", (391.16, dat[1]), rot=0, shape="output")
pl.gnd(gnd2)
y_mv = vdd2[1] - 7.62
r_mv = hR("10R", 383.54, y_mv)
W(vdd2, (vdd2[0], y_mv), r_mv.pin("1"))
pl.pwr("+3V3", r_mv.pin("2"))
sch.power("power:PWR_FLAG", (360.68, y_mv))
c_mv = vC("100n", 350.52, y_mv + 5.08, decouples=f"{mk.ref}.5")
W((vdd2[0], y_mv), (350.52, y_mv), c_mv.pin("1")); J((vdd2[0], y_mv))
pl.gnd(c_mv.pin("2"))
T("Bottom port: Ø0.8 mm PCB hole, vent to the back panel\n(phase 4). No pull on DATA. Clock 3.072 MHz.", (335.28, 246.38))

sch.save()
print("wrote", sch.file)
