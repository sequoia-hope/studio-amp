"""f_parts.py -- block F part catalogue and drawing helpers shared by audio_out.py and audio_in.py.

Every entry is (value, footprint, MPN, manufacturer, LCSC) taken from the audits in
design/parts/F-*.md. The schematic becomes the source of truth once drawn.
"""
from __future__ import annotations

R0603 = "Resistor_SMD:R_0603_1608Metric"
R0805 = "Resistor_SMD:R_0805_2012Metric"
R1206 = "Resistor_SMD:R_1206_3216Metric"
C0603 = "Capacitor_SMD:C_0603_1608Metric"
C0805 = "Capacitor_SMD:C_0805_2012Metric"
C1206 = "Capacitor_SMD:C_1206_3216Metric"

P = {
    # --- resistors, thick film 1 % (basic)
    "10R":    ("10", R0603, "0603WAF100JT5E", "UNI-ROYAL", "C22859"),
    "22R":    ("22", R0603, "0603WAF220JT5E", "UNI-ROYAL", "C23345"),
    "33R":    ("33", R0603, "0603WAF330JT5E", "UNI-ROYAL", "C23140"),
    "100R":   ("100", R0603, "0603WAF1000T5E", "UNI-ROYAL", "C22775"),
    "180R":   ("180", R0603, "0603WAF1800T5E", "UNI-ROYAL", "C22828"),
    "470R":   ("470", R0603, "0603WAF4700T5E", "UNI-ROYAL", "C23179"),
    "1k":     ("1k", R0603, "0603WAF1001T5E", "UNI-ROYAL", "C21190"),
    "2k2":    ("2.2k", R0603, "0603WAF2201T5E", "UNI-ROYAL", "C4190"),
    "3k":     ("3k", R0603, "0603WAF3001T5E", "UNI-ROYAL", "C4211"),
    "4k7":    ("4.7k", R0603, "0603WAF4701T5E", "UNI-ROYAL", "C23162"),
    "10k":    ("10k", R0603, "0603WAF1002T5E", "UNI-ROYAL", "C25804"),
    "15k":    ("15k", R0603, "0603WAF1502T5E", "UNI-ROYAL", "C22809"),
    "47k":    ("47k", R0603, "0603WAF4702T5E", "UNI-ROYAL", "C25819"),
    "100k":   ("100k", R0603, "0603WAF1003T5E", "UNI-ROYAL", "C25803"),
    "470k":   ("470k", R0603, "0603WAF4703T5E", "UNI-ROYAL", "C23178"),
    "0R":     ("0", R0603, "0603WAF0000T5E", "UNI-ROYAL", "C21189"),
    "4R7_0805": ("4.7", R0805, "FRC0805J4R7 TS", "FOJAN", "C2907327"),
    "100R_1206": ("100 0.25W", R1206, "1206W4F1000T5E", "UNI-ROYAL", "C17901"),
    "1k_1206": ("1k 0.25W", R1206, "1206W4F1001T5E", "UNI-ROYAL", "C4410"),
    "2k2_1206": ("2.2k 0.25W", R1206, "1206W4F2201T5E", "UNI-ROYAL", "C17948"),
    # --- thin film 0.1 % 25 ppm (Yageo RT0603)
    "15R_tf":  ("15 0.1%", R0603, "RT0603BRD0715RL", "YAGEO", "C705727"),
    "560R_tf": ("560 0.1%", R0603, "RT0603BRD07560RL", "YAGEO", "C861472"),
    "750R_tf": ("750 0.1%", R0603, "RT0603BRD07750RL", "YAGEO", "C861551"),
    "1k_tf":   ("1k 0.1%", R0603, "RT0603BRD071KL", "YAGEO", "C110776"),
    "2k2_tf":  ("2.2k 0.1%", R0603, "RT0603BRD072K2L", "YAGEO", "C861295"),
    "3k3_tf":  ("3.3k 0.1%", R0603, "RT0603BRD073K3L", "YAGEO", "C309653"),
    "3k9_tf":  ("3.9k 0.1%", R0603, "RT0603BRD073K9L", "YAGEO", "C728592"),
    "20k_tf":  ("20k 0.1%", R0603, "RT0603BRD0720KL", "YAGEO", "C723637"),
    "100k_tf": ("100k 0.1%", R0603, "RT0603BRD07100KL", "YAGEO", "C122538"),
    "1M_tf":   ("1M 0.1%", R0603, "RT0603BRD071ML", "YAGEO", "C326730"),
    # --- capacitors
    "100n":    ("100n 50V X7R", C0603, "CC0603KRX7R9BB104", "YAGEO", "C14663"),
    "10u_0805": ("10u 25V X5R", C0805, "CL21A106KAYNNNE", "Samsung", "C15850"),
    "10u_1206": ("10u 25V X7R", C1206, "CC1206KKX7R8BB106", "YAGEO", "C70462"),
    "330p_c0g": ("330p C0G", C0603, "CC0603JRNPO9BN331", "YAGEO", "C62784"),
    "1n_c0g":  ("1n C0G", C0603, "CC0603JRNPO9BN102", "YAGEO", "C106246"),
    "4n7_c0g": ("4.7n C0G", C0603, "CC0603JRNPO9BN472", "YAGEO", "C576818"),
    "8n2_c0g": ("8.2n C0G", C0805, "GRM2195C1H822JA01D", "Murata", "C97908"),
    "15n_c0g": ("15n C0G", C0805, "GRM2195C1H153JA01D", "Murata", "C97907"),
    "100n_c0g": ("100n C0G", C1206, "GRM31C5C1H104JA01L", "Murata", "C97946"),
    "1u_film": ("1u 63V PET film", "Capacitor_THT:C_Rect_L7.2mm_W5.0mm_P5.00mm",
                "MKS2C041001F00JSSD", "WIMA", "C92673"),
    "47u_al":  ("47u 16V Al", "Capacitor_SMD:CP_Elec_5x5.4", "RST47UF16V034", "KNSCHA", "C4747957"),
    "10u_al":  ("10u 16V Al", "Capacitor_SMD:CP_Elec_4x5.4", "RST10UF16V013", "KNSCHA", "C4747968"),
    # --- semiconductors
    "SA5532":  ("SA5532A", "Package_SO:SOIC-8_3.9x4.9mm_P1.27mm", "SA5532ADR", "TI", "C83716"),
    "OPA2277": ("OPA2277UA", "Package_SO:SOIC-8_3.9x4.9mm_P1.27mm", "OPA2277UA/2K5", "TI", "C24460"),
    "74LVC74": ("74LVC74A", "Package_SO:TSSOP-14_4.4x5mm_P0.65mm", "74LVC74APW,118", "Nexperia", "C6100"),
    "LVC2G34": ("74LVC2G34", "Package_TO_SOT_SMD:SOT-23-6", "SN74LVC2G34DBVR", "TI", "C347589"),
    "PCM1808": ("PCM1808", "Package_SO:TSSOP-14_4.4x5mm_P0.65mm", "PCM1808PWR", "TI", "C55513"),
    "T3902":   ("T3902", "studio_F:TDK_T3902_LGA-5_3.5x2.65mm", "MMICT390200012", "TDK InvenSense", "C3171752"),
    "BCP56":   ("BCP56-16", "Package_TO_SOT_SMD:SOT-223-3_TabPin2", "BCP56-16,115", "Nexperia", "C92221"),
    "BCP53":   ("BCP53-16", "Package_TO_SOT_SMD:SOT-223-3_TabPin2", "BCP53-16,115", "Nexperia", "C85085"),
    "BC847":   ("BC847B", "Package_TO_SOT_SMD:SOT-23", "BC847B,215", "Nexperia", "C57668"),
    "BC857":   ("BC857B", "Package_TO_SOT_SMD:SOT-23", "BC857B,215", "Nexperia", "C59205"),
    "AO3400A": ("AO3400A", "Package_TO_SOT_SMD:SOT-23", "AO3400A", "AOS", "C20917"),
    "BAV99":   ("BAV99", "Package_TO_SOT_SMD:SOT-23", "BAV99,215", "Nexperia", "C2500"),
    "BAT54S":  ("BAT54S", "Package_TO_SOT_SMD:SOT-23", "BAT54S,215", "Nexperia", "C47546"),
    "BAT54C":  ("BAT54C", "Package_TO_SOT_SMD:SOT-23", "BAT54C,215", "Nexperia", "C37704"),
    "BAT54A":  ("BAT54A", "Package_TO_SOT_SMD:SOT-23", "BAT54A,215", "Nexperia", "C130910"),
    "1N4148WS": ("1N4148WS", "Diode_SMD:D_SOD-323", "1N4148WS", "JSCJ", "C2128"),
    "PESD15":  ("PESD15VL1BA", "Diode_SMD:D_SOD-323", "PESD15VL1BA,115", "Nexperia", "C85378"),
    "FB600":   ("600R@100MHz", "Inductor_SMD:L_0603_1608Metric", "BLM18AG601SN1D", "Murata", "C19330"),
    "HFD4":    ("HFD4/5-SR", "studio_F:Relay_DPDT_Hongfa_HFD4-S_SMD", "HFD4/5-SR", "HONGFA", "C64399"),
    "NMJ6":    ("NMJ6HCD2", "Connector_Audio:Jack_6.35mm_Neutrik_NMJ6HCD2_Horizontal", "NMJ6HCD2", "Neutrik", "C368502"),
    "RCJ":     ("RCJ-014", "studio_F:RCA_CUI_RCJ-01_Horizontal", "RCJ-014", "CUI Devices", "C4991844"),
    "SJ1":     ("SJ1-3523N", "Connector_Audio:Jack_3.5mm_CUI_SJ1-3523N_Horizontal", "SJ1-3523N", "CUI Devices", "C20182914"),
}


class Placer:
    """Thin layer over SubSheet: references from the sheet's range, catalogue fields, and a few
    two-terminal helpers. Coordinates stay explicit at every call site."""

    def __init__(self, sch, base: int):
        self.sch = sch
        self.n = {}
        self.base = base

    def ref(self, prefix: str) -> str:
        self.n[prefix] = self.n.get(prefix, 0) + 1
        return f"{prefix}{self.base + self.n[prefix]}"

    def part(self, lib_id, prefix, key, at, rot=0, mirror=None, unit=1, ref=None, value=None,
             decouples=None, dnp=False, note=None, ref_at=None, value_at=None, justify=None):
        val, fp, mpn, mfr, lcsc = P[key]
        fields = {"MPN": mpn, "Manufacturer": mfr, "LCSC": lcsc}
        if decouples:
            fields["Decouples"] = decouples
        if note:
            fields["Note"] = note
        ref = ref or self.ref(prefix)
        if rot in (180, 270):
            # KiCad turns field text with the symbol: at 180/270 the justification reads mirrored,
            # so ask for the opposite side to get the text where the call site wants it.
            j = justify or "left"
            justify = {"left": "right", "right": "left"}.get(j, j)
        return self.sch.symbol(lib_id, ref, value or val, at, rot=rot, mirror=mirror, unit=unit,
                               footprint=fp, fields=fields, dnp=dnp, ref_at=ref_at, value_at=value_at,
                               justify=justify)

    # Two-terminal parts. Horizontal: pin 1 left, pin 2 right. Vertical: pin 1 top, pin 2 bottom.
    def R(self, key, at, horiz=False, **kw):
        if horiz:
            kw.setdefault("ref_at", (at[0] - 2.54, at[1] - 2.54))
            kw.setdefault("value_at", (at[0] - 2.54, at[1] + 3.3))
        return self.part("Device:R", "R", key, at, rot=90 if horiz else 0, **kw)

    def C(self, key, at, horiz=False, polar=False, **kw):
        lib = "Device:C_Polarized" if polar else "Device:C"
        if horiz:
            kw.setdefault("ref_at", (at[0] - 2.54, at[1] - 2.54))
            kw.setdefault("value_at", (at[0] - 2.54, at[1] + 3.3))
        return self.part(lib, "C", key, at, rot=90 if horiz else 0, **kw)

    def gnd(self, at):
        return self.sch.power("power:GND", at)

    def pwr(self, net, at):
        std = {"+15V": "power:+15V", "+3V3": "power:+3V3", "+5V": "power:+5V"}
        if net == "-15V":
            # value text under the symbol: above it would sit on the part the rail feeds
            self.sch._pwr += 1
            return self.sch.symbol("power:-15V", f"#PWR{self.sch._pwr:02d}", "-15V", at,
                                   ref_at=at, value_at=(at[0], at[1] + 3.81), in_bom=False, on_board=False, justify="")
        if net in std:
            return self.sch.power(std[net], at)
        return self.sch.power("power:VCC", at, value=net)
