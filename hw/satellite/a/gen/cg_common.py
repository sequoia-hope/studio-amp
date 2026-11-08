"""cg_common.py -- shared helpers for the block C (rails) and block G (io) generators.

Parts catalogue (values, footprints, MPN, manufacturer, LCSC) from the block C/G audits
(design/parts/C-*.md, G-*.md) and jlc_parts.py lookups of 2026-11-07/08.
"""
from __future__ import annotations

import hier

U = 1.27


def g(n: float) -> float:
    """n grid units (1.27 mm) -> mm, rounded so coordinates stay exact."""
    return round(n * U, 4)


# key -> (value text, footprint, MPN, manufacturer, LCSC)
R06 = "Resistor_SMD:R_0603_1608Metric"
R08 = "Resistor_SMD:R_0805_2012Metric"
R12 = "Resistor_SMD:R_1206_3216Metric"
C06 = "Capacitor_SMD:C_0603_1608Metric"
C08 = "Capacitor_SMD:C_0805_2012Metric"
C12 = "Capacitor_SMD:C_1206_3216Metric"
C1210 = "Capacitor_SMD:C_1210_3225Metric"
UNI = "UNI-ROYAL"
CAT = {
    # resistors, 1 % 0603 unless noted
    "0R_1206": ("0R 1206", R12, "1206W4F0000T5E", UNI, "C17888"),
    "0R": ("0R", R06, "0603WAF0000T5E", UNI, "C21189"),
    "1M_0805": ("1M 0805", R08, "0805W8F1004T5E", UNI, "C17514"),
    "330k_0805": ("330k 0805", R08, "0805W8F3303T5E", UNI, "C17629"),
    "390k_0805": ("390k 0805", R08, "0805W8F3903T5E", UNI, "C17656"),
    "191k_0805": ("191k 0805", R08, "0805W8F1913T5E", UNI, "C17511"),
    "124k_0805": ("124k 0805", R08, "0805W8F1243T5E", UNI, "C17440"),
    "931k": ("931k", R06, "0603WAF9313T5E", UNI, "C246847"),
    "715k": ("715k", R06, "0603WAF7153T5E", UNI, "C23237"),
    "150k": ("150k", R06, "0603WAF1503T5E", UNI, "C22807"),
    "137k": ("137k", R06, "0603WAF1373T5E", UNI, "C22872"),
    "118k": ("118k", R06, "0603WAF1183T5E", UNI, "C25806"),
    "113k": ("113k", R06, "0603WAF1133T5E", UNI, "C22862"),
    "100k": ("100k", R06, "0603WAF1003T5E", UNI, "C25803"),
    "100k_0.5": ("100k 0.5%", R06, "0603WAD1003T5E", UNI, "C423093"),
    "100k_0.1": ("100k 0.1%", R06, "RT0603BRD07100KL", "YAGEO", "C122538"),
    "84.5k": ("84.5k", R06, "0603WAF8452T5E", UNI, "C23118"),
    "68.1k": ("68.1k", R06, "0603WAF6812T5E", UNI, "C25976"),
    "64.9k": ("64.9k", R06, "0603WAF6492T5E", UNI, "C14891"),
    "56k": ("56k", R06, "0603WAF5602T5E", UNI, "C23206"),
    "52.3k": ("52.3k", R06, "0603WAF5232T5E", UNI, "C23198"),
    "47k": ("47k", R06, "0603WAF4702T5E", UNI, "C25819"),
    "46.4k": ("46.4k", R06, "0603WAF4642T5E", UNI, "C23059"),
    "32.4k": ("32.4k", R06, "0603WAF3242T5E", UNI, "C13187"),
    "31.6k_0.5": ("31.6k 0.5%", R06, "0603WAD3162T5E", UNI, "C423046"),
    "22k": ("22k", R06, "0603WAF2202T5E", UNI, "C31850"),
    "22k_0.1": ("22.0k 0.1%", R06, "RT0603BRD0722KL", "YAGEO", "C469656"),
    "16.7k_0.1": ("16.7k 0.1%", R06, "RT0603BRD0716K7L", "YAGEO", "C861155"),
    "15k": ("15k", R06, "0603WAF1502T5E", UNI, "C22809"),
    "10k": ("10k", R06, "0603WAF1002T5E", UNI, "C25804"),
    "9.76k": ("9.76k", R06, "0603WAF9761T5E", UNI, "C23128"),
    "5.36k": ("5.36k", R06, "0603WAF5361T5E", UNI, "C25973"),
    "5.1k": ("5.1k", R06, "0603WAF5101T5E", UNI, "C23186"),
    "4.7k": ("4.7k", R06, "0603WAF4701T5E", UNI, "C23162"),
    "23.2k": ("23.2k", R06, "0603WAF2322T5E", UNI, "C23346"),
    "2.2k": ("2.2k", R06, "0603WAF2201T5E", UNI, "C4190"),
    "2.7k": ("2.7k", R06, "0603WAF2701T5E", UNI, "C13167"),
    "1k": ("1k", R06, "0603WAF1001T5E", UNI, "C21190"),
    "100R": ("100R", R06, "0603WAF1000T5E", UNI, "C22775"),
    "100R_1206": ("100R 1206", R12, "1206W4F1000T5E", UNI, "C17901"),
    "1M": ("1M", R06, "0603WAF1004T5E", UNI, "C22935"),
    "47R": ("47R", R06, "0603WAF470JT5E", UNI, "C23182"),
    "33R": ("33R", R06, "0603WAF330JT5E", UNI, "C23140"),
    # capacitors
    "4u7_100V": ("4u7 100V", C1210, "FS32X475K101EGG", "PSA", "C381466"),
    "2u2_100V": ("2u2 100V", C1210, "CL32B225KCJSNNE", "Samsung", "C55151"),
    "1u_100V": ("1u 100V", C12, "CL31B105KCHNNNE", "Samsung", "C13832"),
    "100n_100V": ("100n 100V", C06, "0603B104K101NT", "FH", "C88219"),
    "22u_25V": ("22u 25V", C12, "CL31A226KAHNNNE", "Samsung", "C12891"),
    "47u_10V": ("47u 10V", C12, "CL31A476MPHNNNE", "Samsung", "C96123"),
    "22u_10V": ("22u 10V", C08, "CL21A226MPQNNNE", "Samsung", "C29277"),
    "10u_50V": ("10u 50V", C1210, "UMK325AB7106KM-P", "Taiyo Yuden", "C337485"),
    "10u_25V_1206": ("10u 25V", C12, "CL31B106KAHNNNE", "Samsung", "C14860"),
    "10u_25V": ("10u 25V", C08, "CL21A106KAYNNNE", "Samsung", "C15850"),
    "4u7_25V": ("4u7 25V", C08, "CL21A475KAQNNNE", "Samsung", "C1779"),
    "1u_50V": ("1u 50V", C08, "CL21B105KBFNNNE", "Samsung", "C28323"),
    "1u_50V_0603": ("1u 50V", C06, "CL10A105KB8NNNC", "Samsung", "C15849"),
    "220p_100V": ("220p C0G 100V", C06, "AC0603JRNPO0BN221", "YAGEO", "C2982813"),
    "4n7_2kV": ("4n7 2kV", C12, "1206B472K202NT", "FH", "C41017"),
    "10u_50V_1206": ("10u 50V", C12, "CL31B106KBHNNNE", "Samsung", "C89632"),
    "2u2_10V_0603": ("2u2 10V", C06, "CC0603KRX7R6BB225", "YAGEO", "C513691"),
    "22p": ("22p C0G", C06, "CL10C220JB8NNNC", "Samsung", "C1653"),
    "100n": ("100n", C06, "CC0603KRX7R9BB104", "YAGEO", "C14663"),
    "10n": ("10n", C06, "0603B103K500NT", "FH", "C57112"),
    "3n3": ("3n3", C06, "CL10B332KB8NNNC", "Samsung", "C1613"),
    "2n2": ("2n2", C06, "0603B222K500NT", "FH", "C1604"),
    "1n": ("1n", C06, "CL10B102KB8NNNC", "Samsung", "C1588"),
    "330p": ("330p C0G", C06, "CL10C331JB8NNNC", "Samsung", "C1664"),
    "6p8": ("6p8 C0G", C06, "0603CG6R8C500NT", "FH", "C1679"),
    # magnetics, ferrites
    "L47u_SRP1265A": ("47u SRP1265A", "studio_C:L_Bourns_SRP1265A", "SRP1265A-470M", "Bourns", "C840530"),
    "L47u_SRN6045": ("47u SRN6045TA", "Inductor_SMD:L_Bourns_SRN6045TA", "SRN6045TA-470M", "Bourns", "C5151734"),
    "L1u_SRP4020": ("1u SRP4020TA", "studio_C:L_Bourns_SRP4020TA", "SRP4020TA-1R0M", "Bourns", "C913245"),
    "L68u_coupled": ("68u 1:1 PSSCAQ7048M", "studio_C:L_PROD_PSSCAQ7048", "PSSCAQ7048M-680M", "PROD Tech", "C56266204"),
    "FB_220R": ("BLM18PG221", "Inductor_SMD:L_0603_1608Metric", "BLM18PG221SN1D", "Murata", "C80165"),
    "FB_600R_2A9": ("BLM31KN601", "Inductor_SMD:L_1206_3216Metric", "BLM31KN601SN1L", "Murata", "C668306"),
    # semiconductors
    "LM5013": ("LM5013", "Package_SO:TI_SO-PowerPAD-8", "LM5013DDAR", "TI", "C5383001"),
    "LM5017": ("LM5017", "Package_SO:TI_SO-PowerPAD-8", "LM5017MRX/NOPB", "TI", "C34355"),
    "TPS2116": ("TPS2116", "Package_TO_SOT_SMD:SOT-583-8", "TPS2116DRLR", "TI", "C3235557"),
    "TPS62A02A": ("TPS62A02A", "Package_TO_SOT_SMD:TSOT-23-6", "TPS62A02APDDCR", "TI", "C25687169"),
    "TPS7A94": ("TPS7A9401", "Package_SON:Texas_DSC0010J", "TPS7A9401DSCR", "TI", "C5220127"),
    "TPS7A2033": ("TPS7A2033P 3.3V", "Package_TO_SOT_SMD:SOT-23-5", "TPS7A2033PDBVR", "TI", "C2862740"),
    "TPS7A4901": ("TPS7A4901", "Package_SO:HVSSOP-8-1EP_3x3mm_P0.65mm_EP1.57x1.89mm", "TPS7A4901DGNR", "TI", "C16430"),
    "TPS7A3001": ("TPS7A3001", "Package_SO:HVSSOP-8-1EP_3x3mm_P0.65mm_EP1.57x1.89mm", "TPS7A3001DGNR", "TI", "C33835"),
    "TLV6703": ("TLV6703", "Package_TO_SOT_SMD:TSOT-23-6", "TLV6703DDCT", "TI", "C2877614"),
    "2N7002": ("2N7002", "Package_TO_SOT_SMD:SOT-23", "2N7002", "JSCJ", "C8545"),
    "AO3401A": ("AO3401A", "Package_TO_SOT_SMD:SOT-23", "AO3401A", "AOS", "C15127"),
    "SS5P10": ("SS5P10", "Package_TO_SOT_SMD:TO-277A", "SS5P10-M3/86A", "Vishay", "C46986"),
    "B1100": ("B1100", "Diode_SMD:D_SMA", "B1100-13-F", "Diodes Inc", "C110106"),
    "SMF5.0A": ("SMF5.0A", "Diode_SMD:D_SOD-123F", "SMF5.0A", "MDD", "C193402"),
    "SMF6.0A": ("SMF6.0A", "Diode_SMD:D_SOD-123F", "SMF6.0A", "MDD", "C123790"),
    "PESD5V0S1BL": ("PESD5V0S1BL", "Diode_SMD:D_SOD-882", "PESD5V0S1BL,315", "Nexperia", "C84374"),
    "SRV05-4": ("SRV05-4", "Package_TO_SOT_SMD:SOT-23-6", "SRV05-4.TCT", "Semtech", "C13612"),
    "USBLC6-2SC6": ("USBLC6-2SC6", "Package_TO_SOT_SMD:SOT-23-6", "USBLC6-2SC6", "ST", "C7519"),
    "TCA9617B": ("TCA9617B", "Package_SO:VSSOP-8_3x3mm_P0.65mm", "TCA9617BDGKR", "TI", "C527429"),
    "TPS2553": ("TPS2553", "Package_TO_SOT_SMD:SOT-23-6", "TPS2553DBVR", "TI", "C55266"),
    "TPS2553DRV": ("TPS2553", "Package_SON:WSON-6-1EP_2x2mm_P0.65mm_EP1x1.6mm", "TPS2553DRVR", "TI", "C138719"),
    "SN74LV1T125": ("SN74LV1T125", "Package_TO_SOT_SMD:SOT-23-5", "SN74LV1T125DBVR", "TI", "C473338"),
    # connectors, test points
    "USB_C": ("USB-C 16P TYPE-C-31-M-12", "Connector_USB:USB_C_Receptacle_HRO_TYPE-C-31-M-12", "TYPE-C-31-M-12", "HRO", "C165948"),
    "JST_SH4": ("Qwiic JST SH 4P", "Connector_JST:JST_SH_SM04B-SRSS-TB_1x04-1MP_P1.00mm_Horizontal", "SM04B-SRSS-TB(LF)(SN)", "JST", "C160404"),
    "JST_SH3": ("JST SH 3P", "Connector_JST:JST_SH_SM03B-SRSS-TB_1x03-1MP_P1.00mm_Horizontal", "1.0-3PWT", "FG", "C2763613"),
    "JST_PH4": ("JST PH 4P", "Connector_JST:JST_PH_B4B-PH-K_1x04_P2.00mm_Vertical", "B4B-PH-K-S(LF)(SN)", "JST", "C131334"),
    "SOCK_1x8": ("1x8 socket 2.54", "Connector_PinSocket_2.54mm:PinSocket_1x08_P2.54mm_Vertical", "2.54-1*8P", "BOOMELE", "C27438"),
    "HDR_2x6": ("2x6 header 2.54", "Connector_PinHeader_2.54mm:PinHeader_2x06_P2.54mm_Vertical", "PZ254V-12-12P", "XFCN", "C492423"),
    "HDR_1x6": ("1x6 header 2.54", "Connector_PinHeader_2.54mm:PinHeader_1x06_P2.54mm_Vertical", "PZ254V-11-06P", "XFCN", "C492405"),
    "TP_5015": ("TP Keystone 5015", "TestPoint:TestPoint_Keystone_5015_Micro_Mini", "5015", "Keystone", "C2906768"),
}


class Local:
    """A placed part whose pin() answers in the caller's local (offset) coordinates."""

    def __init__(self, part, off):
        self.part, self.off = part, off
        self.ref = part.ref

    def pin(self, key):
        x, y = self.part.pin(key)
        return (round(x - self.off[0], 4), round(y - self.off[1], 4))


class Sheet:
    """A SubSheet plus reference counters and part helpers. `off` translates every coordinate
    the helpers receive, so each block can be drawn in local coordinates and moved as a unit."""

    def __init__(self, name: str, paper: str = "A2"):
        self.off = (0.0, 0.0)
        self.sch = hier.SubSheet(name, paper=paper)
        self.base = self.sch.base
        self.n: dict[str, int] = {}

    def ref(self, prefix: str) -> str:
        self.n[prefix] = self.n.get(prefix, 0) + 1
        return f"{prefix}{self.base + self.n[prefix]}"

    def part(self, lib, prefix, key, at, rot=0, mirror=None, dec=None, dnp=False, value=None,
             fields=None, ref_at=None, value_at=None, in_bom=True, footprint=None, justify=None, ref=None,
             vtext=False, ref_rot=None):
        if key is not None:
            v, fp, mpn, mfr, lcsc = CAT[key]
            f = {"MPN": mpn, "Manufacturer": mfr, "LCSC": lcsc}
        else:
            v, fp, f = value, footprint, {}
        if value is not None:
            v = value
        if footprint is not None:
            fp = footprint
        if dec:
            f["Decouples"] = dec
        f.update(fields or {})
        dx, dy = self.off
        at = (at[0] + dx, at[1] + dy)
        if ref_at is not None:
            ref_at = (ref_at[0] + dx, ref_at[1] + dy)
        if value_at is not None:
            value_at = (value_at[0] + dx, value_at[1] + dy)
        x, y = at
        if dnp and vtext and rot == 0 and ref_at is None:
            # DNP: the red X covers the body, so both texts go clear of it, to the right
            ref_at, value_at, justify = (x + 3.81, y - 0.889), (x + 3.81, y + 0.889), "left"
        elif vtext and rot == 0 and ref_at is None:
            if vtext == "left":       # both texts on the left (right side is busy)
                ref_at, value_at, ref_rot, justify = (x - 4.318, y), (x - 2.54, y), 90, ""
            elif vtext == "right":    # both texts on the right
                ref_at, value_at, ref_rot, justify = (x + 2.54, y), (x + 4.318, y), 90, ""
            else:
                ref_at, value_at, ref_rot, justify = (x - 2.54, y), (x + 2.54, y), 90, ""
        if ref_at is None and value_at is None and rot in (90, 270):
            # horizontal two-pin part: both texts centred above the body
            ref_at, value_at, justify = (x, y - 4.064), (x, y - 2.286), ""
        if rot in (90, 180, 270) and ref_rot is None and (justify is None or justify in ("left", "right")) \
                and not lib.startswith("power:"):
            # the field angle follows the symbol: a rotated part shows its texts turned 180 deg,
            # which KiCad reads upright with the justification mirrored; swap so "left" means left
            justify = "left" if justify == "right" else "right"
        if ref_at is None and value_at is None:
            if rot in (90, 270):
                pass
            else:
                ref_at, value_at = (x + g(2), y - g(1)), (x + g(2), y + g(1))
        p = self.sch.symbol(lib, ref or self.ref(prefix), v, at, rot=rot, mirror=mirror, footprint=fp,
                            fields=f, dnp=dnp, ref_at=ref_at, value_at=value_at, in_bom=in_bom,
                            justify=justify, ref_rot=ref_rot)
        return Local(p, self.off)

    # passives: vertical (rot 0) has pin 1 at y-3.81 (top), pin 2 at y+3.81
    def R(self, key, at, rot=0, **kw):
        kw.setdefault("vtext", True)
        return self.part("Device:R", "R", key, at, rot, **kw)

    def C(self, key, at, rot=0, **kw):
        kw.setdefault("vtext", True)
        return self.part("Device:C", "C", key, at, rot, **kw)

    def _o(self, p):
        return (round(p[0] + self.off[0], 4), round(p[1] + self.off[1], 4))

    def gnd(self, at):
        return self.sch.power("power:GND", self._o(at))

    def rail(self, name, at):
        std = {"VBUS", "+5V", "+3V3", "+1V1", "+2V5", "+15V", "-15V"}
        if name in std:
            return self.sch.power(f"power:{name}", self._o(at))
        return self.sch.power("power:VCC", self._o(at), value=name)

    def flag(self, at):
        """PWR_FLAG on a net fed through a link, inductor or ferrite (ERC driver)."""
        return self.sch.power("power:PWR_FLAG", self._o(at))

    def cap_down(self, key, x, y, dec=None, **kw):
        """Capacitor hanging from a horizontal wire at (x, y) to a ground symbol below."""
        c = self.C(key, (x, y + g(3)), dec=dec, **kw)
        self.gnd((x, y + g(6)))
        return c

    def w(self, *pts):
        self.sch.wire(*[self._o(p) for p in pts])

    def label(self, name, at, rot=0):
        self.sch.label(name, self._o(at), rot=rot)

    def glabel(self, name, at, rot=0, shape="bidirectional"):
        self.sch.label(name, self._o(at), rot=rot, kind="global_label", shape=shape)

    def text(self, s, at, size=1.27):
        """Multi-line note whose first line sits at `at` (KiCad centres text on its anchor)."""
        n = s.count("\n")
        x, y = self._o(at)
        self.sch.text(s, (x, round(y + n * size * 0.8, 4)), size=size)

    def box(self, a, b, title):
        self.sch.box(self._o(a), self._o(b), title)

    def nc(self, at):
        self.sch.no_connect(self._o(at))

    def tp(self, at, net_hint=None, keystone=True, rot=0):
        """Test point: Keystone 5015 (BOM) or a bare 1.0 mm pad (PCB only). Pin at `at`;
        rot=180 hangs it below the wire (texts below too)."""
        sgn = -1 if rot == 0 else 1
        ra = (at[0] + g(1), at[1] + sgn * g(4))
        va = (at[0] + g(1), at[1] + sgn * g(4) + 1.778)
        if rot == 0:
            ra, va = (at[0] + g(1), at[1] - g(3) - 1.778), (at[0] + g(1), at[1] - g(3))
        if keystone:
            return self.part("Connector:TestPoint", "TP", "TP_5015", at, rot=rot,
                             value=f"TP {net_hint}" if net_hint else None, ref_at=ra, value_at=va, justify="left")
        return self.part("Connector:TestPoint", "TP", None, at, rot=rot, value=f"pad {net_hint}" if net_hint else "pad",
                         footprint="TestPoint:TestPoint_Pad_D1.0mm", in_bom=False, ref_at=ra, value_at=va,
                         justify="left")

    def save(self):
        self.sch.save()
