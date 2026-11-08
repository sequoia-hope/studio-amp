"""amp_sense.py -- block D sensing sheet (refs 600-699): VBUS ADC, current/NTC ADC, post-filter sense.

Values, MPNs and LCSC numbers from design/parts/D-vbus-adc.md, D-isense-adc.md, D-ntc.md and
D-postfilter-sense.md. Run from the repo root:
    python3 hw/satellite/a/gen/amp_sense.py

Layout (A3):
  top left    VBUS divider (/25.8) -> ADS7042 (feed-forward and the PoE-loss rule), AMP_ARM default
  top right   ADS7038-Q1: AIN0-3 INA241 outputs (100R/1n), AIN4-7 NTC pull-ups (10k/100n)
  bottom      post-filter sense, one ADS8353 per channel, each input buffered by an OPA836 follower
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from amp import C0402, C0603, R0402, R0603, R0805, P, Sheet  # noqa: E402

P.update({
    "rvt": ("27.4k 1%", R0805, "FRC0805F2742TS", "FOJAN", "C2930188"),
    "rvb": ("2.21k 1%", R0603, "FRC0603F2211TS", "FOJAN", "C2933171"),
    "c1n": ("1n C0G", C0402, "0402N102J500CT", "Walsin", "C237166"),
    "r10k": ("10k 1%", R0402, "0402WGF1002TCE", "UNI-ROYAL", "C25744"),
    "r20": ("20R 1%", R0402, "RC0402FR-0720RL", "YAGEO", "C138031"),
    "c10u": ("10u 10V X5R", C0603, "CL10A106KP8NNNC", "Samsung", "C19702"),
    "ads7042": ("ADS7042", "Package_SO:VSSOP-8_2.3x2mm_P0.5mm", "ADS7042IDCUR", "Texas Instruments", "C701641"),
    "ads7038": ("ADS7038-Q1", "Package_DFN_QFN:WQFN-16-1EP_3x3mm_P0.5mm_EP1.68x1.68mm", "ADS7038QRTERQ1",
                "Texas Instruments", "C2876384"),
    "ads8353": ("ADS8353", "Package_SO:TSSOP-16_4.4x5mm_P0.65mm", "ADS8353IPWR", "Texas Instruments", "C701691"),
    "opa836": ("OPA836", "Package_TO_SOT_SMD:SOT-23-6", "OPA836IDBVR", "Texas Instruments", "C111589"),
})
IC = {"ads7042": "Analog_ADC:ADS7042xDCU", "ads7038": "studio_D:ADS7038-Q1",
      "ads8353": "studio_D:ADS8353_PW", "opa836": "studio_D:OPA836_DBV"}


class Sense(Sheet):
    def __init__(self):
        super().__init__("amp_sense", "A3", [
            "Block D. Audits: D-vbus-adc.md, D-isense-adc.md, D-ntc.md, D-postfilter-sense.md",
            "+3V3_A (block C LDO): ADC and INA241 reference"])

    def ic(self, key, at, fields=None):
        return self.part(IC[key], key, at, fields=fields or "auto")

    def cap(self, key, x, ytop, dec=None, fields="auto"):
        """Vertical cap from (x, ytop) down to GND."""
        c = self.part("C", key, (x, ytop + 3.81), dec=dec, fields=fields)
        self.gnd(c.pin("2"))
        return c

    # ------------------------------------------------------------------ VBUS sense
    def vbus(self):
        s = self.sch
        s.box((20.32, 20.32), (190.5, 99.06), "VBUS SENSE, ADS7042 (FEED-FORWARD, POE-LOSS RULE)")
        u = self.ic("ads7042", (139.7, 63.5), fields=((147.32, 76.2), (147.32, 78.74)))
        ainp, ainm = u.pin("6"), u.pin("5")
        x = 40.64
        r1 = self.part("R", "rvt", (x, ainp[1] - 19.05))
        r2 = self.part("R", "rvt", (x, ainp[1] - 8.89))
        r3 = self.part("R", "rvb", (x, ainp[1] + 7.62))
        top = (x, r1.pin("1")[1] - 2.54)
        self.w(top, r1.pin("1"))
        self.pwr("VBUS", top)
        self.w(r1.pin("2"), r2.pin("1"))
        self.w(r2.pin("2"), (x, ainp[1]), r3.pin("1"))
        self.gnd(r3.pin("2"))
        self.w((x, ainp[1]), ainp)
        self.label("VBUS_DIV", (55.88, ainp[1]))
        # back-power clamp to 3V3_A, 1n C0G at the pin
        d = self.part("D", "bat46", (76.2, ainp[1] - 3.81), rot=270,
                      fields=((78.74, ainp[1] - 5.08), (78.74, ainp[1] - 2.54), "right"))
        self.w(d.pin("2"), (76.2, ainp[1]))
        self.w(d.pin("1"), (76.2, d.pin("1")[1] - 2.54))
        self.pwr("+3V3_A", (76.2, d.pin("1")[1] - 2.54))
        cf = self.cap("c1n", 106.68, ainp[1], dec=f"{u.ref}.6")
        self.w((106.68, ainp[1]), cf.pin("1"))
        self.w(ainm, (ainm[0] - 2.54, ainm[1]), (ainm[0] - 2.54, ainm[1] + 5.08))
        self.gnd((ainm[0] - 2.54, ainm[1] + 5.08))
        self.text("/25.8: 48 V -> 1.86 V, 55 V stop -> 2.13 V,\n82.4 V TVS clamp -> 3.19 V; LSB 20.8 mV.\n"
                  "RC pole 72 kHz (D-vbus-adc.md)", (25.4, ainp[1] + 20.32))
        self.text("BAT46WJ: the node goes into 3V3_A,\nnot the ADC, while VBUS outlives\nthe logic rails",
                  (63.5, ainp[1] - 25.4))
        self.text("AINM: Kelvin to the bottom of the divider", (101.6, ainp[1] + 19.05))
        # supplies: AVDD = 3V3_A (reference), DVDD = +3V3
        av, dv = u.pin("7"), u.pin("1")
        ya = av[1] - 12.7
        self.w(av, (av[0], ya))
        self.pwr("+3V3_A", (av[0], ya))
        self.w((av[0], ya + 2.54), (101.6, ya + 2.54))
        for xx, key in ((119.38, "c100n"), (101.6, "c1u")):
            self.cap(key, xx, ya + 2.54, dec=f"{u.ref}.7")
        yd = dv[1] - 7.62
        self.w(dv, (dv[0], yd), (167.64, yd))
        self.pwr("+3V3", (167.64, yd))
        self.cap("c100n", 154.94, yd, dec=f"{u.ref}.1")
        self.gnd(u.pin("8"))
        for pn, name, dirn in (("3", "VB_SDO", "out"), ("2", "VB_SCLK", "in"), ("4", "VB_CS_n", "in")):
            p = u.pin(pn)
            self.w(p, (172.72, p[1]))
            self.glabel(name, (172.72, p[1]), 0, dirn)
        self.text("576 kS/s, once per PWM period; SCLK <= 16 MHz", (137.16, 88.9))

    def arm(self):
        s = self.sch
        s.box((20.32, 106.68), (127.0, 149.86), "AMP_ARM DEFAULT")
        y = 119.38
        self.glabel("AMP_ARM", (33.02, y), 180, "in")
        r = self.part("R", "r10k", (55.88, y + 3.81))
        self.w((33.02, y), (55.88, y), r.pin("1"))
        self.gnd(r.pin("2"))
        self.text("10k pull-down: both fault latches held\nclear (bridges off) until the FPGA drives\n"
                  "AMP_ARM high (E-pinmap.md ball R1)", (63.5, y - 2.54))

    # ------------------------------------------------------------------ ADS7038: currents and NTCs
    def isense(self):
        s = self.sch
        s.box((200.66, 20.32), (398.78, 160.02), "CURRENT AND TEMPERATURE TELEMETRY, ADS7038-Q1")
        Yc = 88.9
        u = self.ic("ads7038", (332.74, Yc), fields=((337.82, Yc + 30.48), (337.82, Yc + 33.02), "left"))
        ur = u.ref
        xc = 304.8                          # filter caps: one column, beside the pins
        # AIN0-3: INA241 outputs, 100R + 1n C0G (kickback 0.8 LSB, D-isense-adc.md)
        rows = (Yc - 50.8, Yc - 38.1, Yc - 25.4, Yc - 12.7)
        jog = (317.5, 314.96, 312.42, None)
        for i, (name, pn) in enumerate((("ISNS_W_A", "15"), ("ISNS_W_B", "16"), ("ISNS_T_A", "1"),
                                        ("ISNS_T_B", "2"))):
            y, p = rows[i], u.pin(pn)
            self.glabel(name, (228.6, y), 180, "in")
            r = self.part("R", "r100", (264.16, y), rot=90)
            self.w((228.6, y), r.pin("1"))
            if jog[i]:
                self.w(r.pin("2"), (jog[i], y), (jog[i], p[1]), p)
            else:
                self.w(r.pin("2"), p)
            self.cap("c1n", xc, y, dec=f"{ur}.{pn}", fields="left")
        self.text("INA241A1: 1.65 V + 50 mV/A -> 16 mA/LSB,\nrange -32...+29 A", (226.06, 25.4))
        # AIN4-7: NTC dividers, 10k to 3V3_A, 100n at the pin
        rows = (Yc + 12.7, Yc + 25.4, Yc + 38.1, Yc + 50.8)
        jog = (None, 312.42, 314.96, 317.5)
        for i, (name, pn) in enumerate((("T_W_FET", "3"), ("T_W_IND", "4"), ("T_T_FET", "5"), ("T_T_IND", "6"))):
            y, p = rows[i], u.pin(pn)
            self.glabel(name, (228.6, y), 180, "in")
            r = self.part("R", "r10k", (279.4, y - 3.81), rot=90,
                          fields=((271.78, y - 5.08), (271.78, y - 2.54), "left"))
            self.w(r.pin("2"), (r.pin("2")[0], y))
            self.pwr("+3V3_A", r.pin("1"))
            if jog[i]:
                self.w((228.6, y), (jog[i], y), (jog[i], p[1]), p)
            else:
                self.w((228.6, y), p)
            self.cap("c100n", xc, y, dec=f"{ur}.{pn}", fields="left")
        self.text("NTC (NCP15XH103, on the power sheets) to GND;\n10k pull-up: 1.65 V at 25 C", (226.06, 154.94))
        # supplies
        av, dv = u.pin("7"), u.pin("10")
        ya = av[1] - 25.4
        self.w(av, (av[0], ya))
        self.pwr("+3V3_A", (av[0], ya))
        self.w((av[0], ya + 2.54), (342.9, ya + 2.54))
        self.cap("c1u", 342.9, ya + 2.54, dec=f"{ur}.7")
        yd = dv[1] - 7.62
        self.w(dv, (dv[0], yd), (363.22, yd))
        self.pwr("+3V3", (363.22, yd))
        self.cap("c1u", 353.06, yd, dec=f"{ur}.10")
        dc = u.pin("8")
        self.w(dc, (350.52, dc[1]))
        self.cap("c1u", 350.52, dc[1], dec=f"{ur}.8")
        g = u.pin("9")
        self.gnd(g)
        for pn, name, dirn in (("11", "IS_CS_n", "in"), ("13", "IS_SCLK", "in"), ("14", "IS_SDI", "in"),
                               ("12", "IS_SDO", "out")):
            p = u.pin(pn)
            self.w(p, (373.38, p[1]))
            self.glabel(name, (373.38, p[1]), 0, dirn)
        self.text("SCLK <= 60 MHz; ~240 kS/s per current channel,\nNTCs ~1 kS/s each", (340.36, 132.08))

    # ------------------------------------------------------------------ post-filter sense
    def buffer(self, name, Xo, Yo, dref, cap=True):
        """OPA836 follower: PF divider tap -> + ; OUT -> - ; 20R/1n to the ADC."""
        u = self.ic("opa836", (Xo, Yo), fields=((Xo + 12.7, Yo + 8.89), (Xo + 12.7, Yo + 11.43), "left"))
        ip, im, out, vsp, pd, vsn = (u.pin(n) for n in ("3", "4", "1", "6", "5", "2"))
        self.glabel(name, (Xo - 22.86, ip[1]), 180, "in")
        self.w((Xo - 22.86, ip[1]), ip)
        yr = Yo - 15.24
        self.w(vsp, (vsp[0], yr))
        self.w(pd, (pd[0], yr))
        self.w((vsp[0], yr), (Xo + 12.7, yr))
        self.pwr("+5V", (vsp[0], yr))
        self.cap("c100n", Xo + 12.7, yr, dec=f"{u.ref}.6")
        self.gnd((vsn[0], vsn[1] + 2.54))
        self.w(vsn, (vsn[0], vsn[1] + 2.54))
        yf = Yo + 13.97
        self.w(out, (Xo + 10.16, Yo), (Xo + 10.16, yf), (Xo - 10.16, yf), (Xo - 10.16, im[1]), im)
        r = self.part("R", "r20", (Xo + 19.05, Yo), rot=90)
        self.w((Xo + 10.16, Yo), r.pin("1"))
        self.w(r.pin("2"), (Xo + 27.94, Yo))
        if cap:
            c = self.cap("c1n", Xo + 27.94, Yo, dec=dref)
            self.w((Xo + 27.94, Yo), c.pin("1"))
        return (Xo + 27.94, Yo)

    def pfchan(self, ch, Xo, Yc):
        s = self.sch
        title = "WOOFER" if ch == "W" else "TWEETER"
        s.box((Xo - 33.02, Yc - 38.1), (Xo + 124.46, Yc + 48.26), f"POST-FILTER SENSE, {title}: OPA836 x 2 + ADS8353")
        Xc = Xo + 76.2
        u = self.ic("ads8353", (Xc, Yc), fields=((Xc + 12.7, Yc + 33.02), (Xc + 12.7, Yc + 35.56), "left"))
        ur = u.ref
        a = self.buffer(f"PF_{ch}_A", Xo, Yc - 10.16, f"{ur}.1")
        b = self.buffer(f"PF_{ch}_B", Xo, Yc + 25.4, f"{ur}.8", cap=False)
        pa, pb = u.pin("1"), u.pin("8")
        self.w(a, pa)
        xj = Xo + 35.56
        self.w(b, (xj, b[1]), (xj, pb[1]), pb)
        cb = self.cap("c1n", Xo + 50.8, pb[1], dec=f"{ur}.8", fields="left")
        self.w((Xo + 50.8, pb[1]), cb.pin("1"))
        for pn in ("2", "7"):
            p = u.pin(pn)
            self.w(p, (p[0] - 2.54, p[1]))
            self.gnd((p[0] - 2.54, p[1]))
        # references and grounds
        for pn, fl in (("3", "left"), ("6", "auto")):
            p = u.pin(pn)
            self.w(p, (p[0], p[1] + 2.54))
            self.cap("c10u", p[0], p[1] + 2.54, dec=f"{ur}.{pn}", fields=fl)
        g1, g0, g2 = u.pin("4"), u.pin("15"), u.pin("5")
        yg = g0[1] + 2.54
        self.w(g1, (g1[0], yg), (g2[0], yg), g2)
        self.w(g0, (g0[0], yg))
        self.gnd((g0[0], yg))
        # supplies: AVDD +5V, DVDD +3V3
        av, dv = u.pin("16"), u.pin("9")
        ya = av[1] - 12.7
        self.w(av, (av[0], ya), (Xc - 33.02, ya))
        self.pwr("+5V", (av[0], ya))
        self.cap("c100n", Xc - 17.78, ya, dec=f"{ur}.16")
        self.cap("c1u", Xc - 33.02, ya, dec=f"{ur}.16")
        yd = av[1] - 7.62
        self.w(dv, (dv[0], yd), (Xc + 17.78, yd))
        self.pwr("+3V3", (Xc + 17.78, yd))
        self.cap("c100n", Xc + 10.16, yd, dec=f"{ur}.9")
        names = (("11", "PF_CS_n", "in"), ("12", "PF_SCLK", "in"), ("10", "PF_SDI", "in"),
                 ("13", f"PF_SDO_{ch}A", "out"), ("14", f"PF_SDO_{ch}B", "out"))
        for pn, name, dirn in names:
            p = u.pin(pn)
            self.w(p, (Xc + 27.94, p[1]))
            self.glabel(name, (Xc + 27.94, p[1]), 0, dirn)
        self.text("A = OUT_A, B = OUT_B sampled together;\ngateware forms A - B. Range 0-5 V (2 x VREF)",
                  (Xc - 15.24, Yc + 43.18))

    def build(self):
        self.vbus()
        self.arm()
        self.isense()
        self.pfchan("W", 58.42, 200.66)
        self.pfchan("T", 261.62, 200.66)
        self.text("PF dividers (140k/10k 0.1%) sit on the power sheets; shared CS/SCLK/SDI, "
                  "one SDO per ADC channel (D-postfilter-sense.md). +5V load ~24 mA.", (25.4, 280.67))
        self.sch.save()
        self.save_labels()
        return self.sch


if __name__ == "__main__":
    a = Sense().build()
    print("wrote", a.file, "symbols", len({p.ref for p in a.parts if not p.ref.startswith("#")}))
