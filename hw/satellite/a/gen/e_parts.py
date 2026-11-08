"""e_parts.py -- block E parts catalogue and drawing helpers for mcu.py, fpga.py and ethernet.py.

Values, MPNs and LCSC numbers come from block E's audits (design/parts/E-*.md); every LCSC line
was checked with jlc_parts.py show on 2026-11-07 (quoted in those audits).
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import hier  # noqa: E402,F401

G = 2.54
UNI = "UNI-ROYAL"
SEC = "Samsung Electro-Mechanics"
FH = "FH (Guangdong Fenghua Advanced Tech)"
R04, R06 = "Resistor_SMD:R_0402_1005Metric", "Resistor_SMD:R_0603_1608Metric"
C04, C06, C08 = "Capacitor_SMD:C_0402_1005Metric", "Capacitor_SMD:C_0603_1608Metric", "Capacitor_SMD:C_0805_2012Metric"
L06 = "Inductor_SMD:L_0603_1608Metric"

# key -> (lib_id, value, footprint, MPN, manufacturer, LCSC)
CAT = {
    "0R": ("Device:R", "0R", R04, "0402WGF0000TCE", UNI, "C17168"),
    "10R": ("Device:R", "10R", R04, "0402WGF100JTCE", UNI, "C25077"),
    "22R": ("Device:R", "22R", R04, "0402WGF220JTCE", UNI, "C25092"),
    "27R": ("Device:R", "27R", R04, "0402WGF270JTCE", UNI, "C25100"),
    "33R": ("Device:R", "33R", R04, "0402WGF330JTCE", UNI, "C25105"),
    "270R": ("Device:R", "270R", R04, "0402WGF2700TCE", UNI, "C25099"),
    "330R": ("Device:R", "330R", R04, "0402WGF3300TCE", UNI, "C25104"),
    "1k": ("Device:R", "1k", R04, "0402WGF1001TCE", UNI, "C11702"),
    "1k5": ("Device:R", "1k5", R04, "0402WGF1501TCE", UNI, "C25867"),
    "4k7": ("Device:R", "4k7", R04, "0402WGF4701TCE", UNI, "C25900"),
    "10k": ("Device:R", "10k", R04, "0402WGF1002TCE", UNI, "C25744"),
    "12k1": ("Device:R", "12k1 1%", R04, "0402WGF1212TCE", UNI, "C25852"),
    "100k": ("Device:R", "100k", R04, "0402WGF1003TCE", UNI, "C25741"),
    "49R9": ("Device:R", "49R9 1%", R06, "0603WAF499JT5E", UNI, "C23185"),
    "100n": ("Device:C", "100n", C04, "CL05B104KO5NNNC", SEC, "C1525"),
    "10n": ("Device:C", "10n", C04, "CL05B103KB5NNNC", SEC, "C15195"),
    "470p": ("Device:C", "470p", C04, "0402B471K500NT", FH, "C1537"),
    "15p": ("Device:C", "15p", C04, "0402CG150J500NT", FH, "C1548"),
    "1u": ("Device:C", "1u", C04, "CL05A105KA5NQNC", SEC, "C52923"),
    "4u7": ("Device:C", "4u7", C04, "CL05A475MP5NRNC", SEC, "C23733"),
    "4u7s": ("Device:C", "4u7", "studio_E:C_0402_1005Metric_RPi_SmallPads", "CL05A475MP5NRNC", SEC, "C23733"),
    "4u7_0603": ("Device:C", "4u7", C06, "CL10A475KO8NNNC", SEC, "C19666"),
    "10u": ("Device:C", "10u", C06, "CL10A106KP8NNNC", SEC, "C19702"),
    "22u": ("Device:C", "22u", C08, "CL21A226MAQNNNE", SEC, "C45783"),
    "FB221": ("Device:FerriteBead", "BLM18PG221", L06, "BLM18PG221SN1D", "Murata", "C80165"),
    "FB121": ("Device:FerriteBead", "BLM18PG121", L06, "BLM18PG121SN1D", "Murata", "C14709"),
}


class Refs:
    """References per type within the sheet's range: R701, R702, ... C701, ..."""
    def __init__(self, base: int):
        self.base, self.n = base, {}

    def __call__(self, kind: str) -> str:
        self.n[kind] = self.n.get(kind, 0) + 1
        return f"{kind}{self.base + self.n[kind]}"


def fields(mpn, mfr, lcsc, **extra):
    d = {"MPN": mpn, "Manufacturer": mfr, "LCSC": lcsc}
    d.update({k: v for k, v in extra.items() if v})
    return d


class Drawer:
    """Thin layer over hier.SubSheet for the passives block E uses everywhere."""

    def __init__(self, sch, base):
        self.sch = sch
        self.ref = Refs(base)

    def part(self, key, at, rot=0, decouples=None, dnp=False, ref_at=None, value_at=None,
             ref_rot=None, justify=None, note=None):
        lib, value, fp, mpn, mfr, lcsc = CAT[key]
        kind = {"Device:R": "R", "Device:C": "C", "Device:FerriteBead": "FB"}[lib]
        f = fields(mpn, mfr, lcsc, Decouples=decouples, Note=note)
        return self.sch.symbol(lib, self.ref(kind), value, at, rot=rot, footprint=fp, fields=f, dnp=dnp,
                               ref_at=ref_at, value_at=value_at, ref_rot=ref_rot, justify=justify)

    # -- vertical parts hanging off a horizontal wire at point p
    def pullup(self, key, p, rail="+3V3", text_left=False, dnp=False, note=None):
        """Resistor from p straight up to a rail symbol. Returns the part."""
        x, y = p[0], p[1] - 3.81
        kw = dict(ref_at=(x - 2.54, y - 1.27), value_at=(x - 2.54, y + 1.27), justify="right") if text_left else {}
        r = self.part(key, (x, y), dnp=dnp, note=note, **kw)
        self.rail(rail, (p[0], p[1] - 7.62))
        return r

    def pulldown(self, key, p, text_left=False):
        x, y = p[0], p[1] + 3.81
        kw = dict(ref_at=(x - 2.54, y - 1.27), value_at=(x - 2.54, y + 1.27), justify="right") if text_left else {}
        r = self.part(key, (x, y), **kw)
        self.gnd((p[0], p[1] + 7.62))
        return r

    def cap_down(self, key, p, decouples=None, dnp=False, text_left=False):
        """Capacitor from p down to GND."""
        x, y = p[0], p[1] + 3.81
        kw = dict(ref_at=(x - 2.54, y - 1.27), value_at=(x - 2.54, y + 1.27), justify="right") if text_left else {}
        c = self.part(key, (x, y), decouples=decouples, dnp=dnp, **kw)
        self.gnd((p[0], p[1] + 7.62))
        return c

    def series(self, key, center, dnp=False):
        """Horizontal resistor centred at center: reference left of centre, value right, one line
        above the body (centred text, so KiCad's justification flip on rotated symbols can't
        move it). Returns (part, pin-1 point, pin-2 point)."""
        x, y = center
        r = self.part(key, (x, y), rot=90, dnp=dnp, justify="",
                      ref_at=(x - 2.54, y - 2.29), value_at=(x + 2.79, y - 2.29))
        return r, r.pin("1"), r.pin("2")

    def gnd(self, p):
        return self.sch.power("power:GND", p)

    def rail(self, name, p):
        std = ("+3V3", "+2V5", "+1V1", "+5V")
        return self.sch.power(f"power:{name}" if name in std else "power:VCC", p,
                              value=None if name in std else name)

    def glabel(self, name, p, side, shape):
        """side 'L': text runs left of p; 'R': right."""
        self.sch.label(name, p, rot=180 if side == "L" else 0, kind="global_label", shape=shape)


def _justify(part, field, j):
    from kicad_write import Sym, children
    for pr in children(part.node, "property"):
        if pr[1] == field:
            eff = next(c for c in pr[3:] if isinstance(c, list) and c and str(c[0]) == "effects")
            for c in list(eff):
                if isinstance(c, list) and c and str(c[0]) == "justify":
                    eff.remove(c)
            eff.append([Sym("justify"), Sym(j)])


SHAPE = {"in": "input", "out": "output", "io": "bidirectional", "od out": "output", "ain": "input"}
