"""amp.py -- block D GaN BTL power stage: amp_woofer (W, refs 400-499) and amp_tweeter (T, 500-599).

One generator, parameterised by channel. Values, MPNs and LCSC numbers come from the block D audits
(design/parts/D-*.md). Run from the repo root:
    python3 hw/satellite/a/gen/amp.py          # writes both sheets and labels_amp_*.txt

Layout (A2), per leg (A top, B bottom):
  row 1, the power path left to right: PWM/EN inputs -> LMG1210 (VIN, VDD, bootstrap) -> gate R ->
         IGB070S10S1 pair -> VBUS HF decoupling (the <= 1 nH loop) -> switch node -> 10 uH -> Kelvin
         shunt -> C0G filter -> output node
  row 2, below: INA241 + OCP window under the shunt; output-short detector, DC-detect taps and the
         post-filter sense divider, fed from the output node by its local label
Common strip at the bottom: OCP and short-detector ladders, fault latch, DC comparator.
Output (Zobel, tweeter series HPF, connector) at the right between the legs.
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import hier  # noqa: E402

# ------------------------------------------------------------------ part data (from D-*.md audits)
R0402 = "Resistor_SMD:R_0402_1005Metric"
R0603 = "Resistor_SMD:R_0603_1608Metric"
R0805 = "Resistor_SMD:R_0805_2012Metric"
R2512 = "Resistor_SMD:R_2512_6332Metric"
C0402 = "Capacitor_SMD:C_0402_1005Metric"
C0603 = "Capacitor_SMD:C_0603_1608Metric"
C1206 = "Capacitor_SMD:C_1206_3216Metric"
C1210 = "Capacitor_SMD:C_1210_3225Metric"

P = {
    # key: (value, footprint, MPN, manufacturer, LCSC)  -- package is in the footprint field
    "drv": ("LMG1210", "studio_D:Texas_RVR0019A_WQFN-19-2EP_4x3mm_P0.5mm", "LMG1210RVRR", "Texas Instruments", "C2677136"),
    "gan": ("IGB070S10S1", "studio_D:IGB070S10S1_PG-TSON-4", "IGB070S10S1XTMA1", "Infineon", "C44179579"),
    "rg": ("2.2R 1%", R0402, "FRC0402F2R20TS", "FOJAN", "C2909330"),
    "rgsl": ("10k 1%", R0402, "0402WGF1002TCE", "UNI-ROYAL", "C25744"),
    "rgsh": ("100k 1%", R0402, "0402WGF1003TCE", "UNI-ROYAL", "C25741"),
    "rdt": ("20k 1%", R0402, "0402WGF2002TCE", "UNI-ROYAL", "C25765"),
    "c100n": ("100n 16V X7R", C0402, "CC0402KRX7R7BB104", "YAGEO", "C60474"),
    "c2u2": ("2.2u 16V X5R", C0603, "CL10A225KO8NNNC", "Samsung", "C23630"),
    "c1u": ("1u 25V X5R", C0603, "CL10A105KA8NNNC", "Samsung", "C5673"),
    "cbst": ("470n 25V X7R", C0603, "CL10B474KA8NNNC", "Samsung", "C1623"),
    "bat46": ("BAT46WJ", "Diode_SMD:D_SOD-323F", "BAT46WJ,115", "Nexperia", "C114696"),
    "r100": ("100R 1%", R0402, "RC0402FR-07100RL", "YAGEO", "C106232"),
    "r4k7": ("4.7k 1%", R0402, "0402WGF4701TCE", "UNI-ROYAL", "C25900"),
    "c10p": ("10p C0G", C0402, "0402N100J500CT", "Walsin", "C301961"),
    "chf2u2": ("2.2u 100V X7R", C1210, "HMK325B7225KN-T", "Taiyo Yuden", "C92775"),
    "chf100n": ("100n 100V X7R", C0603, "HMK107B7104KAHT", "Taiyo Yuden", "C268011"),
    "csn": ("470p 100V C0G", C0603, "CC0603JRNPO0BN471", "YAGEO", "C326973"),
    "rsn": ("2.2R 1W", R2512, "25121WJ022JT4E", "UNI-ROYAL", "C25480"),
    "tvs": ("SMBJ51A", "Diode_SMD:D_SMB", "SMBJ51A", "Littelfuse", "C1973217"),
    "ind": ("10u SER2915H", "studio_D:Coilcraft_SER2915H", "SER2915H-103KL", "Coilcraft", "C19276042"),
    "shunt": ("5m 1% 1W", "studio_D:R_2512_6332Metric_Kelvin_NetTie", "PA2512FKF070R005E", "YAGEO", "C723365"),
    "ina": ("INA241A1", "Package_TO_SOT_SMD:SOT-23-8", "INA241A1IDDFR", "Texas Instruments", "C19712054"),
    "tlv": ("TLV3502", "Package_TO_SOT_SMD:SOT-23-8", "TLV3502AIDCNR", "Texas Instruments", "C48618"),
    "cflt": ("100n 100V C0G", C1206, "GRM31C5C2A104JA01L", "Murata", "C405303"),
    "rzob": ("20R 1W", R2512, "25121WF200JT4E", "UNI-ROYAL", "C41950"),
    "cd": ("47p 100V C0G", C0603, "CC0603JRNPO0BN470", "YAGEO", "C327115"),
    "r1k": ("1k 1%", R0402, "0402WGF1001TCE", "UNI-ROYAL", "C11702"),
    "bat54s": ("BAT54S", "Package_TO_SOT_SMD:SOT-23", "BAT54S,215", "Nexperia", "C47546"),
    "r2k2": ("2.2k 1%", R0402, "0402WGF2201TCE", "UNI-ROYAL", "C25879"),
    "r9k09": ("9.09k 1%", R0402, "0402WGF9091TCE", "UNI-ROYAL", "C11549"),
    "r15k": ("15k 1%", R0402, "0402WGF1502TCE", "UNI-ROYAL", "C25756"),
    "r4k99": ("4.99k 1%", R0402, "0402WGF4991TCE", "UNI-ROYAL", "C25903"),
    "1g17": ("74LVC1G17", "Package_TO_SOT_SMD:SOT-23-5", "SN74LVC1G17DBVR", "Texas Instruments", "C7836"),
    "1g74": ("74LVC1G74", "Package_SO:VSSOP-8_2.3x2mm_P0.5mm", "SN74LVC1G74DCUR", "Texas Instruments", "C70285"),
    "lmv393": ("LMV393", "Package_SO:SOIC-8_3.9x4.9mm_P1.27mm", "LMV393IDR", "Texas Instruments", "C7984"),
    "r2m2": ("2.2M 1%", R0603, "0603WAF2204T5E", "UNI-ROYAL", "C22938"),
    "r82k": ("82k 1%", R0603, "0603WAF8202T5E", "UNI-ROYAL", "C23254"),
    "r88k7": ("88.7k 1%", R0603, "0603WAF8872T5E", "UNI-ROYAL", "C23258"),
    "r1m21": ("1.21M 1%", R0603, "0603WAF1214T5E", "UNI-ROYAL", "C422998"),
    "r140k": ("140k 0.1% 25ppm", R0603, "RT0603BRD07140KL", "YAGEO", "C861125"),
    "r10kp": ("10k 0.1%", R0603, "RT0603BRD0710KL", "YAGEO", "C95204"),
    "ntc": ("10k NTC B3380", R0402, "NCP15XH103F03RC", "Murata", "C77131"),
    "conn": ("MX2EDGRC-5.08-02P", "studio_D:MAX_MX2EDGRC-5.08-02P_1x02_P5.08mm_Horizontal",
             "MX2EDGRC-5.08-02P-GN01-Cu-A", "MAX (CIXI MAIXU)", "C5188019"),
    "chpf": ("22u 450V MKP", "studio_D:C_Rect_L31.5mm_W22.0mm_P27.50mm_B32774", "B32774D4226K", "TDK", "C531089"),
}

SYM = {
    "R": "Device:R", "C": "Device:C", "L": "Device:L", "D": "Device:D_Schottky", "TVS": "Device:D_Zener",
    "NTC": "Device:Thermistor_NTC", "SHUNT": "Device:R_Shunt", "J": "Connector_Generic:Conn_01x02",
    "drv": "studio_D:LMG1210", "gan": "studio_D:IGB070S10S1", "ina": "studio_D:INA241A1_DDF",
    "tlv": "studio_D:TLV3502_DCN", "1g74": "studio_D:74LVC1G74_DCU", "1g17": "74xGxx:74LVC1G17",
    "lmv393": "Comparator:LMV393", "bat54s": "studio_D:BAT54S",
}
PREFIX = {"R": "R", "C": "C", "L": "L", "D": "D", "TVS": "D", "NTC": "RT", "SHUNT": "R", "J": "J",
          "gan": "Q", "bat54s": "D"}


class Sheet:
    """Shared helpers for block D sheets (also used by amp_sense.py)."""

    def __init__(self, name, paper, comments):
        self.sch = hier.SubSheet(name, paper=paper, comments=comments)
        self.base = self.sch.base
        self.n: dict[str, int] = {}
        self.globals: dict[str, str] = {}

    def ref(self, prefix):
        self.n[prefix] = self.n.get(prefix, 0) + 1
        return f"{prefix}{self.base + self.n[prefix]}"

    def part(self, kind, key, at, rot=0, mirror=None, dnp=False, dec=None, unit=1, ref=None,
             fields="auto", lib=None, data=None):
        """fields: 'auto' (right of a vertical part, above/below a horizontal one), 'left', 'above'
        (both above/below, centred), or (ref_at, value_at)."""
        val, fp, mpn, mfr, lcsc = data or P[key]
        f = {"MPN": mpn, "Manufacturer": mfr, "LCSC": lcsc}
        if dec:
            f["Decouples"] = dec
        if dnp:
            f["Note"] = "DNP by default (block D audits)"
        r = ref or self.ref(PREFIX.get(kind, "U"))
        x, y = at
        two = kind in ("R", "C", "L", "NTC", "TVS", "D", "SHUNT")
        horiz = rot in (90, 270) if kind in ("R", "C", "L", "NTC", "SHUNT") else rot in (0, 180)
        ref_at = value_at = None
        just = None
        rr = None
        if isinstance(fields, tuple):
            ref_at, value_at = fields[0], fields[1]
            just = fields[2] if len(fields) > 2 else None
        elif two and (horiz or fields == "above"):
            dy = 3.81 if kind == "C" else 2.54
            ref_at, value_at, just = (x, y - dy), (x, y + dy), ""
        elif two and fields == "left":
            ref_at, value_at, just = (x - 2.54, y - 1.27), (x - 2.54, y + 1.27), "right"
        return self.sch.symbol(lib or SYM.get(kind, kind), r, val, at, rot=rot, mirror=mirror, footprint=fp,
                               fields=f, dnp=dnp, unit=unit, ref_at=ref_at, value_at=value_at, justify=just,
                               ref_rot=rr)

    def pwr(self, name, at):
        lib = {"GND": "power:GND", "+3V3": "power:+3V3", "+5V": "power:+5V", "VBUS": "power:VBUS"}.get(name, "power:VCC")
        self.sch.power(lib, at, value=None if lib != "power:VCC" else name)

    def gnd(self, at):
        self.pwr("GND", at)

    def w(self, *pts):
        self.sch.wire(*pts)

    def glabel(self, name, at, rot, direction):
        shape = {"in": "input", "out": "output", "bidir": "bidirectional", "passive": "passive"}[direction]
        self.sch.label(name, at, rot=rot, kind="global_label", shape=shape)
        self.globals[name] = direction

    def label(self, name, at, rot=0):
        self.sch.label(name, at, rot=rot)

    def text(self, s, at, size=1.0):
        self.sch.text(s, at, size=size)

    def save_labels(self):
        lab = Path(hier.HERE) / f"labels_{self.sch.name}.txt"
        lab.write_text("".join(f"{k} {v}\n" for k, v in sorted(self.globals.items())))


class Amp(Sheet):
    def __init__(self, ch: str):
        self.ch = ch
        name = "amp_woofer" if ch == "W" else "amp_tweeter"
        super().__init__(name, "A2", [
            "Block D. Audits: design/parts/D-*.md (IGB070S10S1, fsw 576 kHz, D-interfaces.md)",
            "gen/amp.py, both channels; the tweeter adds the 2 x 22 uF PP HPF caps"])

    # -- one half-bridge leg; Yd = y of the switch-node line
    def leg(self, leg: str, Yd: float):
        s, ch = self.sch, self.ch
        sfx = f"{ch}_{leg}"
        X = 101.6
        drv = self.part("drv", "drv", (X, Yd), fields=((X + 8.89, Yd + 11.43), (X + 8.89, Yd + 13.97)))
        dref = drv.ref
        self.text(f"LEG {leg}", (22.86, Yd - 45.72), size=2.0)

        # PWM input: 4.7k pull-down, 100R series, 10p DNP at the pin
        pwm = drv.pin("19")
        self.glabel(f"PWM_{sfx}", (27.94, pwm[1]), 180, "in")
        rpd = self.part("R", "r4k7", (40.64, pwm[1] + 3.81))
        self.w(rpd.pin("1"), (40.64, pwm[1]))
        self.gnd(rpd.pin("2"))
        rp = self.part("R", "r100", (58.42, pwm[1]), rot=90)
        self.w((27.94, pwm[1]), rp.pin("1"))
        self.w(rp.pin("2"), pwm)
        cp = self.part("C", "c10p", (73.66, pwm[1] + 3.81), dnp=True,
                       fields=((78.74, pwm[1] + 2.54), (78.74, pwm[1] + 5.08), "left"))
        self.w(cp.pin("1"), (73.66, pwm[1]))
        self.gnd(cp.pin("2"))
        # EN from the channel's fault latch
        en = drv.pin("18")
        self.label(f"EN_{ch}", (45.72, en[1]), 180)
        re_ = self.part("R", "r100", (58.42, en[1]), rot=90)
        self.w((45.72, en[1]), re_.pin("1"))
        self.w(re_.pin("2"), en)
        ce = self.part("C", "c10p", (73.66, en[1] + 3.81), dnp=True,
                       fields=((78.74, en[1] + 2.54), (78.74, en[1] + 5.08), "left"))
        self.w(ce.pin("1"), (73.66, en[1]))
        self.gnd(ce.pin("2"))
        self.text("PWM mode, high = HS on. 100R at the pins;\n4.7k pull-down; 10p DNP (ground bounce)", (22.86, Yd + 20.32))

        # dead-time resistors, drawn to the left; VSS
        for pn, yy in (("5", Yd + 20.32), ("6", Yd + 27.94)):
            pp = drv.pin(pn)
            r = self.part("R", "rdt", (85.09, yy), rot=90)
            self.w(pp, (pp[0], yy), r.pin("2"))
            self.w(r.pin("1"), (r.pin("1")[0] - 5.08, yy))
            self.gnd((r.pin("1")[0] - 5.08, yy))
        vss = drv.pin("3")
        self.w(vss, (vss[0], vss[1] + 5.08))
        self.gnd((vss[0], vss[1] + 5.08))
        self.text("DHL / DLH 20.0k: td 20 ns setting,\n~18 ns effective at the FETs", (40.64, Yd + 35.56))

        # VIN from VDRV with its bypass; VDD with 100n + 2 x 2.2u
        vin = drv.pin("2")
        vt = (vin[0], vin[1] - 7.62)
        self.w(vin, vt)
        self.pwr("VDRV", vt)
        cvin = self.part("C", "c1u", (88.9, vt[1] + 3.81), dec=f"{dref}.2", fields="left")
        self.w(vt, (88.9, vt[1]), cvin.pin("1"))
        self.gnd(cvin.pin("2"))
        vdd = drv.pin("4")
        vy = vdd[1] - 22.86
        self.w((66.04, vy), (vdd[0], vy), (116.84, vy))
        self.w(vdd, (vdd[0], vy))
        for x, key, fl in ((86.36, "c100n", "left"), (66.04, "c2u2", "left"), (116.84, "c2u2", "auto")):
            c = self.part("C", key, (x, vy + 3.81), dec=f"{dref}.4", fields=fl)
            self.w((x, vy), c.pin("1"))
            self.gnd(c.pin("2"))
        self.text("VDD 5 V (internal LDO): >= 5 x C_BST", (66.04, vy - 2.54))

        # bootstrap: BAT46WJ BST -> HB, 470n HB -> HS
        bst, hb, hs = drv.pin("17"), drv.pin("12"), drv.pin("9")
        dbst = self.part("D", "bat46", (bst[0] + 3.81, bst[1] - 10.16), rot=180,
                         fields=((bst[0] + 3.81, bst[1] - 15.24), (bst[0] + 3.81, bst[1] - 12.7), ""))
        self.w(bst, dbst.pin("2"))
        k = dbst.pin("1")
        hby = hb[1] - 5.08
        self.w(k, (k[0], hby))
        self.w(hb, (hb[0], hby), (124.46, hby))
        cb = self.part("C", "cbst", (124.46, hby + 3.81))
        self.w(cb.pin("2"), (124.46, hs[1]))
        self.label(f"HB_{sfx}", (114.3, hby))
        nc1 = drv.pin("14")
        self.w(nc1, (114.3, nc1[1]), (114.3, hs[1]))

        # gate drive and FETs
        ho, lo = drv.pin("10"), drv.pin("8")
        qh = self.part("gan", "gan", (172.72, ho[1]), fields=((177.8, ho[1] - 1.27), (177.8, ho[1] + 1.27)))
        ql = self.part("gan", "gan", (172.72, lo[1]), fields=((177.8, lo[1] - 1.27), (177.8, lo[1] + 1.27)))
        rgh = self.part("R", "rg", (137.16, ho[1]), rot=90)
        self.w(ho, rgh.pin("1"))
        self.w(rgh.pin("2"), qh.pin("1"))
        rgl = self.part("R", "rg", (137.16, lo[1]), rot=90)
        self.w(lo, rgl.pin("1"))
        self.w(rgl.pin("2"), ql.pin("1"))
        rgsh = self.part("R", "rgsh", (152.4, ho[1] + 3.81))
        self.w(rgsh.pin("2"), (152.4, hs[1]))
        rgsl = self.part("R", "rgsl", (152.4, lo[1] + 3.81))
        self.gnd(rgsl.pin("2"))
        sw = (175.26, hs[1])
        self.w(hs, sw)
        self.w(qh.pin("3"), sw)
        self.w(sw, ql.pin("2"))
        self.gnd(ql.pin("3"))
        self.text("2.2R on/off; pull-downs 100k (HS, fed from\nthe bootstrap) / 10k (LS)", (127.0, lo[1] + 17.78))

        # VBUS rail and HF decoupling: the commutation loop
        d = qh.pin("2")
        vb = d[1] - 12.7
        # drawn at the half-bridge: each sits across Q_H drain (VBUS) and Q_L source (GND)
        caps = [(167.64, "chf100n", "left"), (190.5, "chf100n", "auto"), (142.24, "chf2u2", "left"),
                (210.82, "chf2u2", "auto")]
        xr = 236.22 if leg == "A" else 210.82
        self.w(d, (d[0], vb))
        self.w((142.24, vb), (xr, vb))
        self.pwr("VBUS", (d[0], vb))
        for x, key, fl in caps:
            if x == 142.24:      # above the rail, clear of the bootstrap cap's text
                fl = ((140.97, vb - 5.08), (140.97, vb - 2.54), "right")
            c = self.part("C", key, (x, vb + 3.81), dec=f"{qh.ref}.2", fields=fl)
            self.w((x, vb), c.pin("1"))
            self.gnd(c.pin("2"))
        if leg == "A":
            tv = self.part("TVS", "tvs", (236.22, vb + 3.81), rot=270,
                           fields=((238.76, vb + 2.54), (238.76, vb + 5.08), "right"))
            self.w((236.22, vb), tv.pin("1"))
            self.gnd(tv.pin("2"))
        self.text(f"POWER LOOP <= 1 nH, verified by phase 6 extraction: {qh.ref} / {ql.ref} with the two\n"
                  "100n 0603 directly across the leg, return on L2" + (". SMBJ51A at the bridge (VBUS OV scheme)." if leg == "A" else "."),
                  (185.42, vb - 5.08))

        # switch node, snubber (DNP), inductor, NTC
        self.w(sw, (278.13, sw[1]))
        self.label(f"SW_{sfx}", (236.22, sw[1]))
        csn = self.part("C", "csn", (195.58, sw[1] + 3.81), dnp=True,
                        fields=((200.66, sw[1] + 2.54), (200.66, sw[1] + 5.08), "left"))
        self.w((195.58, sw[1]), csn.pin("1"))
        rsn = self.part("R", "rsn", (195.58, sw[1] + 11.43), dnp=True,
                        fields=((200.66, sw[1] + 10.16), (200.66, sw[1] + 12.7), "left"))
        self.gnd(rsn.pin("2"))
        self.text("RC snubber, DNP\n(0.62 W if fitted)", (200.66, sw[1] + 17.78))
        ntx = 220.98 if leg == "A" else 256.54
        nt = self.part("NTC", "ntc", (ntx, sw[1] + 11.43))
        self.w(nt.pin("1"), (ntx, sw[1] + 5.08), (ntx + 2.54, sw[1] + 5.08))
        self.glabel(f"T_{ch}_{'FET' if leg == 'A' else 'IND'}", (ntx + 2.54, sw[1] + 5.08), 0, "out")
        self.gnd(nt.pin("2"))
        L = self.part("L", "ind", (281.94, sw[1]), rot=90)

        # Kelvin shunt (pin 4 = inductor side), output node and C0G filter
        sh = self.part("SHUNT", "shunt", (307.34, sw[1]), rot=270)
        self.w(L.pin("2"), sh.pin("4"))
        out_end = 480.06
        self.w(sh.pin("1"), (out_end, sw[1]))
        self.label(f"OUT_{sfx}", (447.04, sw[1]))
        xs = [325.12, 342.9, 359.41, 377.19, 393.7, 411.48, 427.99]
        for x in xs:
            c = self.part("C", "cflt", (x, sw[1] + 3.81))
            self.w((x, sw[1]), c.pin("1"))
        self.w((xs[0], sw[1] + 7.62), (xs[-1], sw[1] + 7.62))
        self.gnd((xs[-1], sw[1] + 7.62))
        self.text("LC filter: 10 uH + 7 x 100n C0G to GND per side: f0 60 kHz, Q 0.53 / 1.06 at 4 / 8 ohm",
                  (316.23, sw[1] - 5.08))

        # row 2: INA241 (inputs right) and OCP window (inputs right, outputs left)
        ina = self.part("ina", "ina", (292.1, sw[1] + 40.64), mirror="y",
                        fields=((299.72, sw[1] + 54.61), (299.72, sw[1] + 57.15)))
        p3, p2 = sh.pin("3"), sh.pin("2")
        inp, inn = ina.pin("8"), ina.pin("1")
        self.w(p3, (p3[0], inp[1]), inp)
        self.w(p2, (p2[0], inn[1]), inn)
        self.text("Kelvin pair from the\nshunt inner pad edges", (299.72, sw[1] + 62.23))
        vs, rf1 = ina.pin("6"), ina.pin("7")
        self.w(rf1, vs)
        self.pwr("+3V3_A", vs)
        cia = self.part("C", "c100n", (276.86, rf1[1]), rot=90, dec=f"{ina.ref}.6",
                        fields=((276.86, rf1[1] - 5.08, ""), (276.86, rf1[1] - 2.54, "")))
        self.w(cia.pin("2"), rf1)
        self.gnd(cia.pin("1"))
        g, nc, rf2 = ina.pin("2"), ina.pin("4"), ina.pin("3")
        self.w(rf2, g)
        self.gnd(nc)
        vo = ina.pin("5")
        tl = self.part("tlv", "tlv", (264.16, vo[1] + 5.08), mirror="y",
                       fields=((243.84, vo[1] + 20.32), (243.84, vo[1] + 22.86)))
        self.w(vo, tl.pin("2"))
        j1 = 274.32
        self.w((j1, vo[1]), (j1, tl.pin("3")[1]), tl.pin("3"))
        self.w(vo, (vo[0], vo[1] + 22.86))
        self.glabel(f"ISNS_{sfx}", (vo[0], vo[1] + 22.86), 270, "out")
        self.label(f"VTH_HI_{ch}", tl.pin("1"), 0)
        self.label(f"VTH_LO_{ch}", tl.pin("4"), 0)
        vp = tl.pin("8")
        ct = self.part("C", "c100n", (vp[0] - 17.78, vp[1]), rot=90, dec=f"{tl.ref}.8",
                       fields=((vp[0] - 17.78, vp[1] - 5.08, ""), (vp[0] - 17.78, vp[1] - 2.54, "")))
        self.w(vp, (vp[0] - 7.62, vp[1]), ct.pin("2"))
        self.pwr("+3V3", (vp[0] - 7.62, vp[1]))
        self.gnd(ct.pin("1"))
        self.gnd(tl.pin("5"))
        anodes = []
        for pn in ("7", "6"):
            op = tl.pin(pn)
            dd = self.part("D", "bat46", (op[0] - 7.62, op[1]), rot=180)
            self.w(op, dd.pin("1"))
            anodes.append(dd.pin("2"))
        xa_ = anodes[0][0] - 2.54
        self.w(anodes[0], (xa_, anodes[0][1]), (xa_, anodes[1][1]), anodes[1])
        self.label(f"FAULT_RAW_{ch}", (xa_, anodes[0][1]), 180)
        s.box((226.06, sw[1] + 20.32), (320.04, sw[1] + 81.28), f"LEG {leg} CURRENT SENSE + OCP WINDOW")
        self.text("V = 1.65 V + 0.05 V/A (5 mR x 10).\nTrip at +/-14.9 A: VTH 2.40 / 0.90 V.\n"
                  "OK = high; a low on either pulls FAULT_RAW low.", (228.6, sw[1] + 71.12))

        # row 2: output-short detector, fed by the output node's label
        xd = 345.44
        self.w((xd, sw[1] + 27.94), (xd, sw[1] + 22.86), (347.98, sw[1] + 22.86))
        self.label(f"OUT_{sfx}", (347.98, sw[1] + 22.86), 0)
        cdd = self.part("C", "cd", (xd, sw[1] + 31.75))
        self.w((xd, sw[1] + 27.94), cdd.pin("1"))
        xn = cdd.pin("2")
        rd = self.part("R", "r1k", (xd, xn[1] + 3.81))
        self.label(f"VSDB_{ch}", rd.pin("2"), 270)
        cl = self.part("bat54s", "bat54s", (335.28, xn[1]), rot=90,
                       fields=((331.47, xn[1] - 1.27, "right"), (331.47, xn[1] + 1.27, "right")))
        self.w(cl.pin("3"), xn)
        self.pwr("+3V3_A", cl.pin("2"))
        self.gnd(cl.pin("1"))
        sd = self.part("tlv", "tlv", (386.08, xn[1] + 7.62),
                       fields=((391.16, xn[1] + 22.86), (391.16, xn[1] + 25.4)))
        jx2 = 358.14
        rs1 = self.part("R", "r1k", (363.22, sd.pin("2")[1]), rot=90)
        rs2 = self.part("R", "r1k", (363.22, sd.pin("3")[1]), rot=90)
        self.w(xn, (jx2, xn[1]), (jx2, sd.pin("2")[1]), rs1.pin("1"))
        self.w(rs1.pin("2"), sd.pin("2"))
        self.w((jx2, sd.pin("2")[1]), (jx2, sd.pin("3")[1]), rs2.pin("1"))
        self.w(rs2.pin("2"), sd.pin("3"))
        self.label(f"SDH_{ch}", sd.pin("1"), 180)
        self.label(f"SDL_{ch}", sd.pin("4"), 180)
        vp = sd.pin("8")
        self.pwr("+3V3", vp)
        csd = self.part("C", "c100n", (vp[0] - 12.7, vp[1]), rot=90, dec=f"{sd.ref}.8",
                        fields=((vp[0] - 12.7, vp[1] - 5.08, ""), (vp[0] - 12.7, vp[1] - 2.54, "")))
        self.w(vp, csd.pin("2"))
        self.gnd(csd.pin("1"))
        self.gnd(sd.pin("5"))
        anodes = []
        for pn in ("7", "6"):
            op = sd.pin(pn)
            dd = self.part("D", "bat46", (op[0] + 7.62, op[1]))
            self.w(op, dd.pin("1"))
            anodes.append(dd.pin("2"))
        xa_ = anodes[0][0] + 2.54
        self.w(anodes[0], (xa_, anodes[0][1]), (xa_, anodes[1][1]), anodes[1])
        self.label(f"FAULT_RAW_{ch}", (xa_, anodes[0][1]), 0)
        s.box((322.58, sw[1] + 15.24), (424.18, sw[1] + 81.28), f"LEG {leg} OUTPUT-SHORT DETECTOR")
        self.text("47p / 1k differentiator, BAT54S clamp: trips on a >= 1.5 V step\n"
                  "or > 21 V/us, ~51 ns to gates off (D-short-detect.md).\nA lead opening at >= 14 A also trips (benign).",
                  (325.12, sw[1] + 64.77))

        # row 2: DC-detect taps (plain /27.8 and offset +0.217 V) and post-filter sense divider
        for row, yy, rb, nm in (("P", sw[1] + 33.02, "r82k", f"DCP_{sfx}"), ("Q", sw[1] + 55.88, "r88k7", f"DCQ_{sfx}")):
            if row == "P":
                self.label(f"OUT_{sfx}", (436.88, yy), 180)
            else:
                self.w((436.88, sw[1] + 33.02), (436.88, yy))
            rt = self.part("R", "r2m2", (444.5, yy), rot=90)
            self.w((436.88, yy), rt.pin("1"))
            nx = 454.66
            self.w(rt.pin("2"), (nx, yy))
            rbt = self.part("R", rb, (nx, yy + 3.81))
            self.gnd(rbt.pin("2"))
            cf = self.part("C", "c2u2", (467.36, yy + 3.81))
            self.w((nx, yy), (467.36, yy), cf.pin("1"))
            self.gnd(cf.pin("2"))
            if row == "P":
                self.w((467.36, yy), (474.98, yy))
                self.label(nm, (474.98, yy), 0)
            else:
                ro = self.part("R", "r1m21", (477.52, yy), rot=90,
                               fields=((477.52, yy - 5.08, ""), (477.52, yy - 2.54, "")))
                self.w((467.36, yy), ro.pin("1"))
                self.w(ro.pin("2"), (487.68, yy))
                self.pwr("+3V3_A", (487.68, yy))
                self.w((nx, yy), (nx, yy - 7.62))
                self.label(nm, (nx, yy - 7.62), 180)
        s.box((426.72, sw[1] + 15.24), (492.76, sw[1] + 81.28), f"LEG {leg} DC-DETECT TAPS")
        self.text("/27.8, tau 0.17 s;\noffset node +0.217 V\n(= 6.0 V at the output)", (429.26, sw[1] + 71.12))
        self.w((500.38, sw[1] + 27.94), (500.38, sw[1] + 27.94))
        self.label(f"OUT_{sfx}", (500.38, sw[1] + 27.94), 90)
        rpt = self.part("R", "r140k", (500.38, sw[1] + 31.75))
        self.w((500.38, sw[1] + 27.94), rpt.pin("1"))
        nf = rpt.pin("2")
        rpb = self.part("R", "r10kp", (500.38, nf[1] + 3.81))
        self.gnd(rpb.pin("2"))
        self.w(nf, (508.0, nf[1]))
        self.glabel(f"PF_{sfx}", (508.0, nf[1]), 0, "out")
        self.text("Post-filter sense /15,\nthin film 0.1 %, to the\nADS8353 (amp_sense)", (497.84, sw[1] + 50.8))
        return sw[1], out_end

    # -- common strip: ladders, fault node, latch, DC comparator
    def common(self, Yc: float):
        s, ch = self.sch, self.ch
        s.box((20.32, Yc - 12.7), (401.32, Yc + 63.5), f"CHANNEL {ch}: THRESHOLDS, FAULT LATCH, DC DETECT")

        def ladder(x, keys, names, note):
            self.pwr("+3V3_A", (x, Yc))
            rs = [self.part("R", k, (x, Yc + 3.81 + 7.62 * i)) for i, k in enumerate(keys)]
            self.gnd(rs[-1].pin("2"))
            for i, nm in enumerate(names):
                node = rs[i].pin("2")
                dx = -12.7 if i == 0 else 12.7
                c = self.part("C", "c100n", (x + dx, node[1] + 3.81), fields="left" if dx < 0 else "auto")
                self.w(node, (x + dx, node[1]), c.pin("1"))
                self.gnd(c.pin("2"))
                self.label(nm, (x + dx, node[1]), 180 if dx < 0 else 0)
            self.text(note, (x - 15.24, Yc + 35.56))

        ladder(50.8, ("r9k09", "r15k", "r9k09"), (f"VTH_HI_{ch}", f"VTH_LO_{ch}"),
               "OCP thresholds 2.396 / 0.904 V\n(9.09k / 15k / 9.09k, ratiometric)")
        ladder(104.14, ("rdt", "rdt"), (f"VSDB_{ch}",), "Short-detector bias 1.65 V\n(2 x 20k)")
        ladder(152.4, ("r4k99", "r15k", "r4k99"), (f"SDH_{ch}", f"SDL_{ch}"),
               "Short-detector window\n2.64 / 0.66 V (4.99k / 15k / 4.99k)")

        # fault node (diode-AND of OK signals), 2.2k pull-up, Schmitt, latch
        xf = 228.6
        ny = Yc + 12.7
        self.label(f"FAULT_RAW_{ch}", (xf - 25.4, ny), 180)
        self.w((xf - 25.4, ny), (xf, ny))
        rpu = self.part("R", "r2k2", (xf - 5.08, ny - 3.81))
        self.pwr("+3V3", rpu.pin("1"))
        darm = self.part("D", "bat46", (xf - 15.24, ny + 7.62), rot=180)
        ka = darm.pin("1")
        self.w(ka, (ka[0] + 5.08, ka[1]))
        self.glabel("AMP_ARM", (ka[0] + 5.08, ka[1]), 0, "in")
        self.w(darm.pin("2"), (darm.pin("2")[0], ny))
        ddc = self.part("D", "bat46", (xf - 15.24, ny + 15.24), rot=180)
        kd = ddc.pin("1")
        self.w(kd, (kd[0] + 5.08, kd[1]))
        self.glabel(f"DC_{ch}_n", (kd[0] + 5.08, kd[1]), 0, "out")
        self.w(ddc.pin("2"), darm.pin("2"))
        g17 = self.part("1g17", "1g17", (xf + 17.78, ny), fields=((xf + 20.32, ny + 8.89), (xf + 20.32, ny + 11.43)))
        self.w((xf, ny), g17.pin("2"))
        self.pwr("+3V3", g17.pin("5"))
        self.gnd(g17.pin("3"))
        s.no_connect(g17.pin("1"))
        c17 = self.part("C", "c100n", (xf + 5.08, ny - 20.32), dec=f"{g17.ref}.5")
        self.pwr("+3V3", c17.pin("1"))
        self.gnd(c17.pin("2"))
        fo = g17.pin("4")
        ff = self.part("1g74", "1g74", (xf + 60.96, ny - 7.62), fields=((xf + 68.58, ny - 24.13), (xf + 68.58, ny - 21.59)))
        clr = ff.pin("6")
        xj = fo[0] + 7.62
        self.w(fo, (xj, fo[1]), (xj, clr[1] + 7.62), (clr[0], clr[1] + 7.62), clr)
        self.w((xj, clr[1] + 7.62), (xj, clr[1] + 15.24), (xj + 5.08, clr[1] + 15.24))
        self.glabel(f"FAULT_{ch}_n", (xj + 5.08, clr[1] + 15.24), 0, "out")
        dpin, cpin = ff.pin("2"), ff.pin("1")
        self.w(dpin, (dpin[0] - 12.7, dpin[1]))
        self.glabel(f"AMP_EN_{ch}", (dpin[0] - 12.7, dpin[1]), 180, "in")
        self.w(cpin, (cpin[0] - 7.62, cpin[1]))
        self.glabel(f"AMP_CLK_{ch}", (cpin[0] - 7.62, cpin[1]), 180, "in")
        v8, pre = ff.pin("8"), ff.pin("7")
        self.w(v8, pre)
        self.pwr("+3V3", v8)
        self.gnd(ff.pin("4"))
        s.no_connect(ff.pin("3"))
        cff = self.part("C", "c100n", (v8[0] - 22.86, v8[1] - 2.54), dec=f"{ff.ref}.8")
        self.pwr("+3V3", cff.pin("1"))
        self.gnd(cff.pin("2"))
        q = ff.pin("5")
        self.w(q, (q[0] + 7.62, q[1]))
        self.label(f"EN_{ch}", (q[0] + 7.62, q[1]), 0)
        self.text("Fault latch: any OK low (OCP x 4, output short x 4, DC, AMP_ARM low) pulls FAULT_RAW low;\n"
                  "Schmitt -> CLR -> Q (EN) low: both LMG1210 off in <= 216 ns (ramp) / ~51 ns (short).\n"
                  "The FPGA reads FAULT_n and re-arms with AMP_EN = 1 + an AMP_CLK edge. PRE tied high.",
                  (200.66, Yc + 38.1))

        # LMV393 DC comparator: A: P_f vs N_f+ ; B: N_f vs P_f+ ; open-drain wired, 4.7k pull-up
        xl = 340.36
        ua = self.part("lmv393", "lmv393", (xl, Yc + 2.54), unit=1, fields=((xl, Yc - 7.62), (xl, Yc - 5.08)))
        ub = self.part("lmv393", "lmv393", (xl, Yc + 22.86), unit=2, ref=ua.ref, fields=((xl, Yc + 31.75), (xl, Yc + 34.29)))
        uc = self.part("lmv393", "lmv393", (xl + 48.26, Yc + 33.02), unit=3, ref=ua.ref, fields=((xl + 53.34, Yc + 31.75), (xl + 53.34, Yc + 34.29)))
        self.label(f"DCQ_{ch}_B", ua.pin("3"), 180)
        self.label(f"DCP_{ch}_A", ua.pin("2"), 180)
        self.label(f"DCQ_{ch}_A", ub.pin("5"), 180)
        self.label(f"DCP_{ch}_B", ub.pin("6"), 180)
        oa, ob = ua.pin("1"), ub.pin("7")
        xo = oa[0] + 5.08
        self.w(oa, (xo, oa[1]), (xo, ob[1]), ob)
        self.w((xo, oa[1]), (xo + 15.24, oa[1]))
        rpd = self.part("R", "r4k7", (xo + 7.62, oa[1] - 3.81))
        self.pwr("+3V3", rpd.pin("1"))
        self.glabel(f"DC_{ch}_n", (xo + 15.24, oa[1]), 0, "out")
        self.pwr("+3V3", uc.pin("8"))
        self.gnd(uc.pin("4"))
        cl = self.part("C", "c100n", (xl + 33.02, Yc + 33.02), dec=f"{ua.ref}.8")
        self.pwr("+3V3", cl.pin("1"))
        self.gnd(cl.pin("2"))
        self.text("DC detect: trips at |DC| >= 6 V (23 ms at 48 V,\n50 ms at 24 V). Open-drain, 4.7k pull-up:\nDC_n to the FPGA and, by its diode, the fault node.",
                  (309.88, Yc + 45.72))

    # -- output: Zobel, tweeter HPF, connector
    def output(self, ya: float, yb: float, xend: float):
        ch = self.ch
        xz = 525.78
        rz1 = self.part("R", "rzob", (xz, ya + 13.97))
        rz2 = self.part("R", "rzob", (xz + 12.7, ya + 13.97))
        self.w((xz, ya), rz1.pin("1"))
        self.w(rz1.pin("1"), (xz + 12.7, rz1.pin("1")[1]), rz2.pin("1"))
        self.w(rz1.pin("2"), (xz + 12.7, rz1.pin("2")[1]), rz2.pin("2"))
        cz = self.part("C", "cflt", (xz, ya + 25.4))
        self.w(rz1.pin("2"), cz.pin("1"))
        self.w(cz.pin("2"), (xz, yb))
        self.text("ZOBEL 10R (2 x 20R 1 W)\n+ 100n C0G: open-load peak\n+23 dB; firmware limits\nit to <= 1 W",
                  (xz + 3.81, ya + 33.02))
        jy = round(((ya + yb) / 2) / 2.54) * 2.54
        j = self.part("J", "conn", (568.96, jy), fields=((558.8, jy - 7.62), (558.8, jy - 5.08), "left"))
        p1, p2 = j.pin("1"), j.pin("2")
        xa = 553.72
        if ch == "T":
            c1 = self.part("C", "chpf", (543.56, ya), rot=90)
            c2 = self.part("C", "chpf", (543.56, ya - 12.7), rot=90)
            self.w((xend, ya), c1.pin("1"))
            self.w(c1.pin("1"), (c1.pin("1")[0] - 2.54, ya), (c1.pin("1")[0] - 2.54, c2.pin("1")[1]), c2.pin("1"))
            self.w(c1.pin("2"), (c1.pin("2")[0] + 2.54, ya), (c1.pin("2")[0] + 2.54, c2.pin("2")[1]), c2.pin("2"))
            self.w(c1.pin("2"), (xa, ya))
            self.label("OUT_T_HPF", (xa, ya + 7.62), 270)
            self.text("PROTECTIVE HPF: 2 x 22u MKP in parallel\n= 44 uF: 904 / 603 / 452 Hz at 4 / 6 / 8 ohm;\nblocks DC if a leg fails short (R-54)",
                      (520.7, ya - 22.86))
        else:
            self.w((xend, ya), (xa, ya))
        self.w((xa, ya), (xa, p1[1]), p1)
        xb = xa + 5.08
        self.w((xend, yb), (xb, yb), (xb, p2[1]), p2)
        self.text("OUT+", (p1[0] + 8.89, p1[1]))
        self.text("OUT-", (p2[0] + 8.89, p2[1]))
        self.text(("WOOFER" if ch == "W" else "TWEETER") + " 4-8 ohm:\npin 1 OUT+ = leg A = speaker +\npin 2 OUT- = leg B = speaker -\n"
                  "15 A header MX2EDGRC-5.08;\nplug MX2EDGK-5.08-02P\n(C5187912) ships loose", (528.32, jy + 12.7))

    def build(self):
        ya, xend = self.leg("A", 66.04)
        yb, _ = self.leg("B", 198.12)
        self.common(299.72)
        self.output(ya, yb, xend)
        self.sch.save()
        self.save_labels()
        return self.sch


if __name__ == "__main__":
    for ch in ("W", "T"):
        a = Amp(ch).build()
        print("wrote", a.file, "symbols", len({p.ref for p in a.parts if not p.ref.startswith("#")}))
