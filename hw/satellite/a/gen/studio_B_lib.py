"""studio_B_lib.py -- block B's project symbols and footprints (lib/studio_B.*).

Every pin number and land-pattern dimension below comes from the datasheet named in the comment
(design/datasheets/). Run on its own or from gen/iso_dcdc.py; it rewrites lib/studio_B.kicad_sym and
the footprints in lib/studio_B.pretty/.
"""
from __future__ import annotations

import uuid
from pathlib import Path

LIB = Path(__file__).resolve().parent.parent / "lib"


def _u():
    return str(uuid.uuid4())


def _f(v: float) -> str:
    s = f"{v:.4f}".rstrip("0").rstrip(".")
    return "0" if s in ("-0", "") else s


# ------------------------------------------------------------------ symbols

def _prop(name, value, x, y, hide=False, justify=None):
    j = f"\n\t\t\t\t(justify {justify})" if justify else ""
    h = "\n\t\t\t\t(hide yes)" if hide else ""
    return (f'\t\t(property "{name}" "{value}"\n\t\t\t(at {_f(x)} {_f(y)} 0)\n\t\t\t(effects\n'
            f'\t\t\t\t(font\n\t\t\t\t\t(size 1.27 1.27)\n\t\t\t\t){j}{h}\n\t\t\t)\n\t\t)\n')


def _pin(etype, num, name, x, y, angle, length=2.54, hide_name=False, hidden=False):
    h = "\t\t\t\t(hide yes)\n" if hidden else ""
    return (f'\t\t\t(pin {etype} line\n\t\t\t\t(at {_f(x)} {_f(y)} {angle})\n\t\t\t\t(length {_f(length)})\n{h}'
            f'\t\t\t\t(name "{name}"\n\t\t\t\t\t(effects\n\t\t\t\t\t\t(font\n\t\t\t\t\t\t\t(size 1.27 1.27)\n'
            f'\t\t\t\t\t\t)\n\t\t\t\t\t)\n\t\t\t\t)\n\t\t\t\t(number "{num}"\n\t\t\t\t\t(effects\n'
            f'\t\t\t\t\t\t(font\n\t\t\t\t\t\t\t(size 1.27 1.27)\n\t\t\t\t\t\t)\n\t\t\t\t\t)\n\t\t\t\t)\n\t\t\t)\n')


def _rect(x1, y1, x2, y2, fill="background"):
    return (f'\t\t\t(rectangle\n\t\t\t\t(start {_f(x1)} {_f(y1)})\n\t\t\t\t(end {_f(x2)} {_f(y2)})\n'
            f'\t\t\t\t(stroke\n\t\t\t\t\t(width 0.254)\n\t\t\t\t\t(type default)\n\t\t\t\t)\n'
            f'\t\t\t\t(fill\n\t\t\t\t\t(type {fill})\n\t\t\t\t)\n\t\t\t)\n')


def _poly(pts, width=0.254):
    xy = " ".join(f"(xy {_f(x)} {_f(y)})" for x, y in pts)
    return (f'\t\t\t(polyline\n\t\t\t\t(pts {xy})\n\t\t\t\t(stroke\n\t\t\t\t\t(width {_f(width)})\n'
            f'\t\t\t\t\t(type default)\n\t\t\t\t)\n\t\t\t\t(fill\n\t\t\t\t\t(type none)\n\t\t\t\t)\n\t\t\t)\n')


def _arc(s, m, e):
    return (f'\t\t\t(arc\n\t\t\t\t(start {_f(s[0])} {_f(s[1])})\n\t\t\t\t(mid {_f(m[0])} {_f(m[1])})\n'
            f'\t\t\t\t(end {_f(e[0])} {_f(e[1])})\n\t\t\t\t(stroke\n\t\t\t\t\t(width 0.254)\n'
            f'\t\t\t\t\t(type default)\n\t\t\t\t)\n\t\t\t\t(fill\n\t\t\t\t\t(type none)\n\t\t\t\t)\n\t\t\t)\n')


def _circle(c, r, fill="outline"):
    return (f'\t\t\t(circle\n\t\t\t\t(center {_f(c[0])} {_f(c[1])})\n\t\t\t\t(radius {_f(r)})\n'
            f'\t\t\t\t(stroke\n\t\t\t\t\t(width 0.254)\n\t\t\t\t\t(type default)\n\t\t\t\t)\n'
            f'\t\t\t\t(fill\n\t\t\t\t\t(type {fill})\n\t\t\t\t)\n\t\t\t)\n')


def _text(s, x, y):
    return (f'\t\t\t(text "{s}"\n\t\t\t\t(at {_f(x)} {_f(y)} 0)\n\t\t\t\t(effects\n\t\t\t\t\t(font\n'
            f'\t\t\t\t\t\t(size 1.27 1.27)\n\t\t\t\t\t)\n\t\t\t\t)\n\t\t\t)\n')


def _symbol(name, ref, value, fp, ds, descr, body, pins, ref_xy, val_xy, pin_names=True):
    pn = "" if pin_names else "\t\t(pin_names\n\t\t\t(hide yes)\n\t\t)\n"
    out = [f'\t(symbol "{name}"\n', pn,
           "\t\t(exclude_from_sim no)\n\t\t(in_bom yes)\n\t\t(on_board yes)\n",
           _prop("Reference", ref, *ref_xy, justify="left"),
           _prop("Value", value, *val_xy, justify="left"),
           _prop("Footprint", fp, 0, 0, hide=True),
           _prop("Datasheet", ds, 0, 0, hide=True),
           _prop("Description", descr, 0, 0, hide=True),
           f'\t\t(symbol "{name}_0_1"\n', body, "\t\t)\n",
           f'\t\t(symbol "{name}_1_1"\n', pins, "\t\t)\n",
           "\t\t(embedded_fonts no)\n\t)\n"]
    return "".join(out)


def sym_ncp4306():
    """NCP4306DADZZDASNT1G, TSOP-6 pin-out "D" (datasheets/ncp4306.pdf, Table 2 p.4):
    1 DRV, 2 GND, 3 CS, 4 MIN_TON, 5 MIN_TOFF, 6 VCC. CS (to the SR drain) is drawn on the right
    beside DRV, so both runs to the MOSFET leave the same side without crossing."""
    body = _rect(-10.16, 7.62, 10.16, -7.62)
    pins = (_pin("power_in", "6", "VCC", 0, 12.7, 270, 5.08)
            + _pin("passive", "4", "MIN_TON", -15.24, 0, 0, 5.08)
            + _pin("passive", "5", "MIN_TOFF", -15.24, -2.54, 0, 5.08)
            + _pin("input", "3", "CS", 15.24, 2.54, 180, 5.08)
            + _pin("output", "1", "DRV", 15.24, -2.54, 180, 5.08)
            + _pin("power_in", "2", "GND", 0, -12.7, 90, 5.08))
    return _symbol("NCP4306DADZZDA", "U", "NCP4306DADZZDA", "Package_TO_SOT_SMD:SOT-23-6",
                   "design/datasheets/ncp4306.pdf",
                   "Synchronous-rectifier controller, 10 V clamp, dV/dt, adjustable MIN_TON/TOFF, TSOP-6 pin-out D",
                   body, pins, (-10.16, 8.89), (-10.16, -8.89))


def _coil(x, y_top, y_bot, bulge):
    """Four half-turn arcs from y_top down to y_bot at x, bulging by `bulge` (+ right)."""
    out, n = "", 4
    step = (y_top - y_bot) / n
    for i in range(n):
        a, b = y_top - i * step, y_top - (i + 1) * step
        out += _arc((x, a), (x + bulge, (a + b) / 2), (x, b))
    return out


def sym_t1():
    """Würth 750343576 (datasheets/we-750343576.pdf p.1 schematic): five 4-turn windings,
    N1 2(dot)-4, N2 3(dot)-5, N5 1(dot)-6 (primary-side insulation), N3 7(dot)-10,
    N4 8(dot)-11 (secondary). No pin 9. Drawn for this design's 1:2 wiring: N5 at the top left,
    N1 upside down so its dot (2) sits next to N2's dot (3) -- the two starts join to VPRI between
    the windings and the two finishes (4, 5) at the outside join to the main FET drain without a
    crossing. Secondary N3 over N4 so 10 -> 8 is a short link."""
    body, pins = "", ""
    # (top pin, bottom pin, y top, y bottom, name, dot at top?)
    left = [("1", "6", 20.32, 12.7, "N5", True), ("4", "2", 5.08, -2.54, "N1", False),
            ("3", "5", -7.62, -15.24, "N2", True)]
    right = [("7", "10", 5.08, -2.54, "N3", True), ("8", "11", -7.62, -15.24, "N4", True)]
    for side, sgn in ((left, -1), (right, 1)):
        for tp, bp, yt, yb, nm, dot_top in side:
            body += _poly([(sgn * 5.08, yt), (sgn * 2.54, yt)]) + _poly([(sgn * 5.08, yb), (sgn * 2.54, yb)])
            body += _coil(sgn * 2.54, yt, yb, -sgn * 1.27)
            yd = yt - 1.27 if dot_top else yb + 1.27
            body += _circle((sgn * 4.064, yd), 0.381, "outline")
            body += _text(nm + " 4T", sgn * 6.35, (yt + yb) / 2)
            pins += (_pin("passive", tp, nm + ("_S" if dot_top else "_F"), sgn * 7.62, yt, 0 if sgn < 0 else 180)
                     + _pin("passive", bp, nm + ("_F" if dot_top else "_S"), sgn * 7.62, yb, 0 if sgn < 0 else 180))
    body += _poly([(-0.508, 22.86), (-0.508, -17.78)]) + _poly([(0.508, 22.86), (0.508, -17.78)])
    return _symbol("750343576", "T", "750343576", "studio_B:Wurth_750343576_ER19",
                   "design/datasheets/we-750343576.pdf",
                   "Würth WE-PoE++ transformer, 5 x 4 T, 100 uH (N1+N2), 2250 V DC N1,N2,N5 => N3,N4",
                   body, pins, (-7.62, 26.67), (-7.62, 24.13), pin_names=False)


def sym_ucc2897a():
    """UCC2897APWR, TSSOP-20 (datasheets/ucc2897a.pdf, Pin Functions p.4-5): 1 VIN, 2 NC, 3 RTDEL,
    4 RON, 5 ROFF, 6 VREF, 7 SYNC, 8 GND, 9 CS, 10 RSLOPE, 11 FB, 12 SS/SD, 13 PGND, 14 AUX,
    15 OUT, 16 PVDD, 17 VDD, 18 LINEUV, 19 LINEOV, 20 NC. Drawn by function: line inputs left,
    supplies top, drivers and CS right, the pins that take resistors/caps to GND on the bottom."""
    body = _rect(-25.4, 17.78, 25.4, -17.78)
    L, R, T, B = -30.48, 30.48, 22.86, -22.86
    pins = (_pin("passive", "1", "VIN", L, 12.7, 0, 5.08)
            + _pin("input", "18", "LINEUV", L, 5.08, 0, 5.08)
            + _pin("input", "7", "SYNC", L, 0, 0, 5.08)
            + _pin("input", "11", "FB", L, -5.08, 0, 5.08)
            + _pin("input", "19", "LINEOV", L, -10.16, 0, 5.08)
            + _pin("power_in", "17", "VDD", -12.7, T, 270, 5.08)
            + _pin("power_in", "16", "PVDD", -2.54, T, 270, 5.08)
            + _pin("power_out", "6", "VREF", 12.7, T, 270, 5.08)
            + _pin("output", "15", "OUT", R, 7.62, 180, 5.08)
            + _pin("output", "14", "AUX", R, 2.54, 180, 5.08)
            + _pin("input", "9", "CS", R, -7.62, 180, 5.08)
            + _pin("no_connect", "2", "NC", 25.4, -15.24, 180, 0, hidden=True)
            + _pin("no_connect", "20", "NC", 25.4, -12.7, 180, 0, hidden=True)
            + _pin("passive", "12", "SS/SD", -20.32, B, 90, 5.08)
            + _pin("passive", "3", "RTDEL", -12.7, B, 90, 5.08)
            + _pin("passive", "4", "RON", -5.08, B, 90, 5.08)
            + _pin("passive", "5", "ROFF", 2.54, B, 90, 5.08)
            + _pin("passive", "10", "RSLOPE", 10.16, B, 90, 5.08)
            + _pin("power_in", "8", "GND", 17.78, B, 90, 5.08)
            + _pin("power_in", "13", "PGND", 22.86, B, 90, 5.08))
    return _symbol("UCC2897A", "U", "UCC2897A", "Package_SO:TSSOP-20_4.4x6.5mm_P0.65mm",
                   "design/datasheets/ucc2897a.pdf",
                   "Active-clamp current-mode PWM controller, 110 V start-up, TSSOP-20 (PW)",
                   body, pins, (-25.4, 19.05), (-25.4, -19.05))


def write_symbols():
    text = ("(kicad_symbol_lib\n\t(version 20241209)\n\t(generator \"studio_B_lib.py\")\n"
            "\t(generator_version \"9.0\")\n" + sym_ncp4306() + sym_t1() + sym_ucc2897a() + ")\n")
    (LIB / "studio_B.kicad_sym").write_text(text, encoding="utf-8")


# ------------------------------------------------------------------ footprints

def _fp(name, descr, pads, body_w, body_h, attr="smd", extra="", silk_rect=True):
    hw, hh = body_w / 2, body_h / 2
    lines = ""
    for (x1, y1, x2, y2), layer, w in [((-hw, -hh, hw, -hh), "F.Fab", 0.1), ((hw, -hh, hw, hh), "F.Fab", 0.1),
                                       ((hw, hh, -hw, hh), "F.Fab", 0.1), ((-hw, hh, -hw, -hh), "F.Fab", 0.1)]:
        lines += (f'\t(fp_line\n\t\t(start {_f(x1)} {_f(y1)})\n\t\t(end {_f(x2)} {_f(y2)})\n\t\t(stroke\n'
                  f'\t\t\t(width {w})\n\t\t\t(type solid)\n\t\t)\n\t\t(layer "{layer}")\n\t\t(uuid "{_u()}")\n\t)\n')
    # courtyard: pads and body, +0.5 mm
    xs = [abs(p[1]) + p[3] / 2 for p in pads] + [hw]
    ys = [abs(p[2]) + p[4] / 2 for p in pads] + [hh]
    cx, cy = max(xs) + 0.5, max(ys) + 0.5
    lines += (f'\t(fp_rect\n\t\t(start {_f(-cx)} {_f(-cy)})\n\t\t(end {_f(cx)} {_f(cy)})\n\t\t(stroke\n'
              f'\t\t\t(width 0.05)\n\t\t\t(type solid)\n\t\t)\n\t\t(fill no)\n\t\t(layer "F.CrtYd")\n\t\t(uuid "{_u()}")\n\t)\n')
    # silk: body outline outside the pads, plus pin-1 dot
    sx, sy = hw + 0.15, hh + 0.15
    if silk_rect:
        lines += (f'\t(fp_rect\n\t\t(start {_f(-sx)} {_f(-sy)})\n\t\t(end {_f(sx)} {_f(sy)})\n\t\t(stroke\n'
                  f'\t\t\t(width 0.12)\n\t\t\t(type solid)\n\t\t)\n\t\t(fill no)\n\t\t(layer "F.SilkS")\n\t\t(uuid "{_u()}")\n\t)\n')
    pad_txt = ""
    for num, x, y, w, h in pads:
        pad_txt += (f'\t(pad "{num}" smd roundrect\n\t\t(at {_f(x)} {_f(y)})\n\t\t(size {_f(w)} {_f(h)})\n'
                    f'\t\t(layers "F.Cu" "F.Mask" "F.Paste")\n\t\t(roundrect_rratio 0.1)\n\t\t(uuid "{_u()}")\n\t)\n')
    text = (f'(footprint "{name}"\n\t(version 20241229)\n\t(generator "studio_B_lib.py")\n'
            f'\t(generator_version "9.0")\n\t(layer "F.Cu")\n\t(descr "{descr}")\n'
            f'\t(property "Reference" "REF**"\n\t\t(at 0 {_f(-cy - 1)} 0)\n\t\t(layer "F.SilkS")\n'
            f'\t\t(uuid "{_u()}")\n\t\t(effects\n\t\t\t(font\n\t\t\t\t(size 1 1)\n\t\t\t\t(thickness 0.15)\n\t\t\t)\n\t\t)\n\t)\n'
            f'\t(property "Value" "{name}"\n\t\t(at 0 {_f(cy + 1)} 0)\n\t\t(layer "F.Fab")\n'
            f'\t\t(uuid "{_u()}")\n\t\t(effects\n\t\t\t(font\n\t\t\t\t(size 1 1)\n\t\t\t\t(thickness 0.15)\n\t\t\t)\n\t\t)\n\t)\n'
            f'\t(attr {attr})\n' + lines + extra + pad_txt + "\t(embedded_fonts no)\n)\n")
    (LIB / "studio_B.pretty" / f"{name}.kicad_mod").write_text(text, encoding="utf-8")


def write_footprints():
    # Würth 750343576 "Recommended Land Pattern" (we-750343576.pdf p.1), TOP VIEW, KiCad y down.
    # Dimensions: 21.23 mm between the column centres (the arrow runs pad centre to pad centre),
    # pads 3.13 x 1.89 mm. Left column (primary) 1,2,3 / 4,5,6 at 2.8 mm pitch with 4.57 mm between
    # pads 3 and 4; right column (secondary) 11,10 / 8,7 with pads 10 and 8 at +-3.18 mm from the
    # centre line and 11 / 7 one 3.16 mm pitch further out (measured from the vector drawing; the
    # sheet does not dimension it). Pin 1 upper left, 6 lower left, 11 upper right, 7 lower right.
    # Phase 2 review B-M1: the first version copied the pad-side (mirrored) view; fixed here.
    xc = 21.23 / 2
    left = {"1": -7.885, "2": -5.085, "3": -2.285, "4": 2.285, "5": 5.085, "6": 7.885}
    right = {"11": -6.36, "10": -3.18, "8": 3.18, "7": 6.36}
    pads = [(n, -xc, y, 3.13, 1.89) for n, y in left.items()] + [(n, xc, y, 3.13, 1.89) for n, y in right.items()]
    hw, hh = 21.08 / 2, 23.37 / 2
    ln = lambda x1, y1, x2, y2, layer, wd: (f'\t(fp_line\n\t\t(start {_f(x1)} {_f(y1)})\n\t\t(end {_f(x2)} {_f(y2)})\n'
                                           f'\t\t(stroke\n\t\t\t(width {wd})\n\t\t\t(type solid)\n\t\t)\n'
                                           f'\t\t(layer "{layer}")\n\t\t(uuid "{_u()}")\n\t)\n')
    sx = xc - 3.13 / 2 - 0.3            # silk stops clear of the pad columns
    extra = (ln(-sx, -hh - 0.15, sx, -hh - 0.15, "F.SilkS", 0.12) + ln(-sx, hh + 0.15, sx, hh + 0.15, "F.SilkS", 0.12)
             # pin-1 marks: silk dot above pad 1, fab chamfer at the pin-1 corner, barrier line on fab
             + f'\t(fp_circle\n\t\t(center {_f(-xc)} -9.6)\n\t\t(end {_f(-xc + 0.35)} -9.6)\n\t\t(stroke\n'
               f'\t\t\t(width 0.12)\n\t\t\t(type solid)\n\t\t)\n\t\t(fill yes)\n\t\t(layer "F.SilkS")\n'
               f'\t\t(uuid "{_u()}")\n\t)\n'
             + ln(-hw, -hh + 2.0, -hw + 2.0, -hh, "F.Fab", 0.1)
             + ln(0, -hh, 0, hh, "F.Fab", 0.1))
    _fp("Wurth_750343576_ER19", "Wurth 750343576 WE-PoE++ ER19 SMD transformer, top-view land per datasheet p.1. "
        "Left column 1-6 primary, right column 7/8/10/11 secondary; pin 1 upper left",
        pads, 21.08, 23.37, extra=extra, silk_rect=False)
    # Sumida CDRH127/LD land pattern (sumida-cdrh127ldnp.pdf p.1, "Land pattern"): two pads, each
    # 5.4 mm wide x 2.9 mm deep, outer edges 12.8 mm apart (the 7.0 mm band is silk, not copper).
    # Drawn rotated 90 deg so pads 1/2 sit left/right: 2.9 x 5.4 at x = +-(12.8 - 2.9) / 2.
    xc = (12.8 - 2.9) / 2
    _fp("L_Sumida_CDRH127", "Sumida CDRH127/LD 12.3x12.3 mm power inductor, land per datasheet p.1",
        [("1", -xc, 0, 2.9, 5.4), ("2", xc, 0, 2.9, 5.4)], 12.3, 12.3)
    # SXN SM5845 (sxn-sm5845-221.pdf p.2 table): H 5.5 overall, I 2.15 pad length, J 1.7 pad
    # width, terminals D 2.0. PROVISIONAL reading of the table columns.
    _fp("L_SXN_SM5845", "SXN SM5845 5.8x5.2 mm unshielded inductor, land per datasheet p.2 (provisional)",
        [("1", -(5.5 / 2 - 2.15 / 2), 0, 2.15, 1.7), ("2", 5.5 / 2 - 2.15 / 2, 0, 2.15, 1.7)], 5.8, 5.2)


if __name__ == "__main__":
    write_symbols()
    write_footprints()
    print("lib/studio_B written")
