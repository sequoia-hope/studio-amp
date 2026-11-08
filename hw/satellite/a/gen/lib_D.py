"""lib_D.py -- block D project symbols and footprints (lib/studio_D.kicad_sym, lib/studio_D.pretty).

Every pin number, pin type and land-pattern dimension comes from the datasheets in
design/datasheets/ (page references next to each part). Run from the repo root:
    python3 hw/satellite/a/gen/lib_D.py
"""
from __future__ import annotations

import uuid
from pathlib import Path

HERE = Path(__file__).resolve().parent
LIB = HERE.parent / "lib"
SYM = LIB / "studio_D.kicad_sym"
PRETTY = LIB / "studio_D.pretty"


def q(s):
    return '"' + str(s).replace('"', '\\"') + '"'


def f(v):
    s = f"{v:.4f}".rstrip("0").rstrip(".")
    return "0" if s in ("-0", "") else s


# ------------------------------------------------------------------ symbols
def box_symbol(name, ref, value, fp, desc, ds, pins, w, h, keywords=""):
    """pins: (number, name, etype, side, pos). side L/R pins at x=-w/2-2.54 / +w/2+2.54 with y=pos;
    T/B pins at y=+h/2+2.54 / -h/2-2.54 with x=pos. Library coordinates, y up."""
    out = [f"\t(symbol {q(name)}", "\t\t(exclude_from_sim no)", "\t\t(in_bom yes)", "\t\t(on_board yes)"]
    def prop(k, v, y, hide=False):
        h_ = " (hide yes)" if hide else ""
        out.append(f"\t\t(property {q(k)} {q(v)} (at 0 {f(y)} 0) (effects (font (size 1.27 1.27)){h_}))")
    prop("Reference", ref, h / 2 + 5.08)
    prop("Value", value, -h / 2 - 5.08)
    prop("Footprint", fp, 0, True)
    prop("Datasheet", ds, 0, True)
    prop("Description", desc, 0, True)
    if keywords:
        prop("ki_keywords", keywords, 0, True)
    out.append(f"\t\t(symbol {q(name + '_0_1')}")
    out.append(f"\t\t\t(rectangle (start {f(-w/2)} {f(h/2)}) (end {f(w/2)} {f(-h/2)}) "
               "(stroke (width 0.254) (type default)) (fill (type background)))")
    out.append("\t\t)")
    out.append(f"\t\t(symbol {q(name + '_1_1')}")
    for num, pname, et, side, pos in pins:
        hide = " (hide yes)" if et in ("no_connect", "passive_hidden") else ""
        et = "passive" if et == "passive_hidden" else et
        if side == "L":
            x, y, a = -w / 2 - 2.54, pos, 0
        elif side == "R":
            x, y, a = w / 2 + 2.54, pos, 180
        elif side == "T":
            x, y, a = pos, h / 2 + 2.54, 270
        else:
            x, y, a = pos, -h / 2 - 2.54, 90
        out.append(f"\t\t\t(pin {et} line (at {f(x)} {f(y)} {a}) (length 2.54){hide}"
                   f" (name {q(pname)} (effects (font (size 1.016 1.016))))"
                   f" (number {q(num)} (effects (font (size 1.016 1.016)))))")
    out.append("\t\t)")
    out.append("\t\t(embedded_fonts no)")
    out.append("\t)")
    return "\n".join(out)


def gan_symbol():
    """IGB070S10S1, PG-TSON-4 (datasheet p.1, p.13): 1 = gate, 2 = drain, 3 and 4 = source.
    Drawn like KiCad's Q_NMOS (enhancement); pin 4 stacked on pin 3."""
    name = "IGB070S10S1"
    L = [f"\t(symbol {q(name)}", "\t\t(pin_names (offset 0) (hide yes))", "\t\t(exclude_from_sim no)",
         "\t\t(in_bom yes)", "\t\t(on_board yes)"]
    def prop(k, v, x, y, hide=False, just=""):
        h_ = " (hide yes)" if hide else ""
        j = f" (justify {just})" if just else ""
        L.append(f"\t\t(property {q(k)} {q(v)} (at {f(x)} {f(y)} 0) (effects (font (size 1.27 1.27)){j}{h_}))")
    prop("Reference", "Q", 5.08, 1.27, just="left")
    prop("Value", name, 5.08, -1.27, just="left")
    prop("Footprint", "studio_D:IGB070S10S1_PG-TSON-4", 0, 0, True)
    prop("Datasheet", "design/datasheets/igb070s10s1.pdf", 0, 0, True)
    prop("Description", "CoolGaN 100 V G3, 7 mOhm, enhancement-mode GaN HEMT, PG-TSON-4 3.2x3.0 mm", 0, 0, True)
    g = [
        "(polyline (pts (xy 0.254 0) (xy -2.54 0)) (stroke (width 0) (type default)) (fill (type none)))",
        "(polyline (pts (xy 0.254 1.905) (xy 0.254 -1.905)) (stroke (width 0.254) (type default)) (fill (type none)))",
        "(polyline (pts (xy 0.762 -1.27) (xy 0.762 -2.286)) (stroke (width 0.254) (type default)) (fill (type none)))",
        "(polyline (pts (xy 0.762 0.508) (xy 0.762 -0.508)) (stroke (width 0.254) (type default)) (fill (type none)))",
        "(polyline (pts (xy 0.762 2.286) (xy 0.762 1.27)) (stroke (width 0.254) (type default)) (fill (type none)))",
        "(polyline (pts (xy 2.54 2.54) (xy 2.54 1.778)) (stroke (width 0) (type default)) (fill (type none)))",
        "(polyline (pts (xy 2.54 -2.54) (xy 2.54 0) (xy 0.762 0)) (stroke (width 0) (type default)) (fill (type none)))",
        "(polyline (pts (xy 0.762 -1.778) (xy 2.54 -1.778)) (stroke (width 0) (type default)) (fill (type none)))",
        "(polyline (pts (xy 0.762 1.778) (xy 2.54 1.778)) (stroke (width 0) (type default)) (fill (type none)))",
        "(polyline (pts (xy 1.016 0) (xy 2.032 0.381) (xy 2.032 -0.381) (xy 1.016 0)) (stroke (width 0) (type default)) (fill (type outline)))",
        "(circle (center 1.651 0) (radius 2.794) (stroke (width 0.254) (type default)) (fill (type none)))",
        "(text \"GaN\" (at -0.762 -2.032 0) (effects (font (size 0.762 0.762))))",
    ]
    L.append(f"\t\t(symbol {q(name + '_0_1')}")
    L += ["\t\t\t" + x for x in g]
    L.append("\t\t)")
    L.append(f"\t\t(symbol {q(name + '_1_1')}")
    L.append("\t\t\t(pin input line (at -5.08 0 0) (length 2.54) (name \"G\" (effects (font (size 1.27 1.27)))) (number \"1\" (effects (font (size 1.27 1.27)))))")
    L.append("\t\t\t(pin passive line (at 2.54 5.08 270) (length 2.54) (name \"D\" (effects (font (size 1.27 1.27)))) (number \"2\" (effects (font (size 1.27 1.27)))))")
    L.append("\t\t\t(pin passive line (at 2.54 -5.08 90) (length 2.54) (name \"S\" (effects (font (size 1.27 1.27)))) (number \"3\" (effects (font (size 1.27 1.27)))))")
    L.append("\t\t\t(pin passive line (at 2.54 -5.08 90) (length 2.54) (hide yes) (name \"S\" (effects (font (size 1.27 1.27)))) (number \"4\" (effects (font (size 1.27 1.27)))))")
    L.append("\t\t)")
    L.append("\t\t(embedded_fonts no)")
    L.append("\t)")
    return "\n".join(L)


SYMBOLS = [
    gan_symbol(),
    # LMG1210, WQFN-19 RVR (datasheet p.3 pin functions; §7.4 PWM mode). HS = 9, 13, 16, pad 21;
    # VSS = 3, 7, pad 20. NC 1, 11, 15. NC1 (14): leave open or tie to HS.
    box_symbol("LMG1210", "U", "LMG1210", "studio_D:Texas_RVR0019A_WQFN-19-2EP_4x3mm_P0.5mm",
               "200 V half-bridge GaN driver, PWM mode with adjustable dead time, WQFN-19 RVR",
               "design/datasheets/lmg1210.pdf", [
                   ("19", "PWM/LI", "input", "L", 7.62),
                   ("18", "EN/HI", "input", "L", -7.62),
                   ("2", "VIN", "power_in", "T", -7.62),
                   ("4", "VDD", "power_out", "T", -2.54),
                   ("17", "BST", "passive", "T", 2.54),
                   ("12", "HB", "passive", "T", 7.62),
                   ("10", "HO", "output", "R", 7.62),
                   ("9", "HS", "passive", "R", 0.0),
                   ("13", "HS", "passive_hidden", "R", 0.0),
                   ("16", "HS", "passive_hidden", "R", 0.0),
                   ("21", "HS", "passive_hidden", "R", 0.0),
                   ("14", "NC1", "passive", "R", -2.54),
                   ("8", "LO", "output", "R", -7.62),
                   ("5", "DHL", "passive", "B", -5.08),
                   ("6", "DLH", "passive", "B", 0.0),
                   ("3", "VSS", "power_in", "B", 5.08),
                   ("7", "VSS", "power_in", "B", 5.08),
                   ("20", "VSS", "power_in", "B", 5.08),
                   ("1", "NC", "no_connect", "B", -7.62),
                   ("11", "NC", "no_connect", "B", -7.62),
                   ("15", "NC", "no_connect", "B", -7.62),
               ], w=15.24, h=25.4),
    # INA241A1, DDF SOT-23-8 (datasheet p.3 Fig. 5-1, Table 5-1). NC (4) "Reserved. Connect to ground".
    box_symbol("INA241A1_DDF", "U", "INA241A1", "Package_TO_SOT_SMD:SOT-23-8",
               "-5 V to 110 V bidirectional current-sense amplifier, gain 10, SOT-23-8 DDF",
               "design/datasheets/ina241.pdf", [
                   ("8", "IN+", "input", "L", 2.54),
                   ("1", "IN-", "input", "L", -2.54),
                   ("5", "OUT", "output", "R", 0.0),
                   ("6", "VS", "power_in", "T", -2.54),
                   ("7", "REF1", "input", "T", 2.54),
                   ("2", "GND", "power_in", "B", -2.54),
                   ("4", "NC", "passive", "B", 0.0),
                   ("3", "REF2", "input", "B", 2.54),
               ], w=15.24, h=15.24),
    # TLV3502, DCN SOT-23-8 (datasheet p.3 pin table).
    box_symbol("TLV3502_DCN", "U", "TLV3502", "Package_TO_SOT_SMD:SOT-23-8",
               "Dual 4.5 ns rail-to-rail push-pull comparator, SOT-23-8 DCN",
               "design/datasheets/tlv3501.pdf", [
                   ("1", "+INA", "input", "L", 7.62),
                   ("2", "-INA", "input", "L", 5.08),
                   ("3", "+INB", "input", "L", -5.08),
                   ("4", "-INB", "input", "L", -7.62),
                   ("7", "OUTA", "output", "R", 5.08),
                   ("6", "OUTB", "output", "R", -5.08),
                   ("8", "V+", "power_in", "T", 0.0),
                   ("5", "V-", "power_in", "B", 0.0),
               ], w=10.16, h=20.32),
    # SN74LVC1G74, DCU VSSOP-8 (datasheet Fig. 5-1, pin functions).
    box_symbol("74LVC1G74_DCU", "U", "74LVC1G74", "Package_SO:VSSOP-8_2.3x2mm_P0.5mm",
               "Single D flip-flop with preset and clear, VSSOP-8 DCU",
               "design/datasheets/sn74lvc1g74.pdf", [
                   ("2", "D", "input", "L", 2.54),
                   ("1", "CLK", "input", "L", -2.54),
                   ("5", "Q", "output", "R", 2.54),
                   ("3", "~{Q}", "output", "R", -2.54),
                   ("8", "VCC", "power_in", "T", -2.54),
                   ("7", "~{PRE}", "input", "T", 2.54),
                   ("6", "~{CLR}", "input", "B", 2.54),
                   ("4", "GND", "power_in", "B", -2.54),
               ], w=15.24, h=15.24),
    # ADS7038-Q1, RTE WQFN-16 (datasheet p.4 pin functions); thermal pad to GND (17 here).
    box_symbol("ADS7038-Q1", "U", "ADS7038-Q1", "Package_DFN_QFN:WQFN-16-1EP_3x3mm_P0.5mm_EP1.68x1.68mm",
               "8-channel 12-bit 1 MSPS SAR ADC, SPI, WQFN-16 RTE",
               "design/datasheets/ads7038q1.pdf", [
                   ("15", "AIN0", "input", "L", 20.32),
                   ("16", "AIN1", "input", "L", 17.78),
                   ("1", "AIN2", "input", "L", 15.24),
                   ("2", "AIN3", "input", "L", 12.7),
                   ("3", "AIN4", "input", "L", -12.7),
                   ("4", "AIN5", "input", "L", -15.24),
                   ("5", "AIN6", "input", "L", -17.78),
                   ("6", "AIN7", "input", "L", -20.32),
                   ("11", "~{CS}", "input", "R", 5.08),
                   ("13", "SCLK", "input", "R", 2.54),
                   ("14", "SDI", "input", "R", 0.0),
                   ("12", "SDO", "output", "R", -2.54),
                   ("8", "DECAP", "passive", "R", -7.62),
                   ("7", "AVDD", "power_in", "T", -2.54),
                   ("10", "DVDD", "power_in", "T", 2.54),
                   ("9", "GND", "power_in", "B", 0.0),
                   ("17", "GND", "power_in", "B", 0.0),
               ], w=15.24, h=45.72),
    # ADS8353, PW TSSOP-16 (datasheet p.4 pin functions).
    box_symbol("ADS8353_PW", "U", "ADS8353", "Package_SO:TSSOP-16_4.4x5mm_P0.65mm",
               "Dual 16-bit 600 kSPS simultaneous-sampling SAR ADC, TSSOP-16",
               "design/datasheets/ads8353.pdf", [
                   ("1", "AINP_A", "input", "L", 10.16),
                   ("2", "AINM_A", "input", "L", 7.62),
                   ("8", "AINP_B", "input", "L", -2.54),
                   ("7", "AINM_B", "input", "L", -5.08),
                   ("11", "~{CS}", "input", "R", 5.08),
                   ("12", "SCLK", "input", "R", 2.54),
                   ("10", "SDI", "input", "R", 0.0),
                   ("13", "SDO_A", "output", "R", -2.54),
                   ("14", "SDO_B", "output", "R", -5.08),
                   ("16", "AVDD", "power_in", "T", -2.54),
                   ("9", "DVDD", "power_in", "T", 2.54),
                   ("3", "REFIO_A", "passive", "B", -10.16),
                   ("4", "REFGND_A", "power_in", "B", -2.54),
                   ("15", "GND", "power_in", "B", 0.0),
                   ("5", "REFGND_B", "power_in", "B", 2.54),
                   ("6", "REFIO_B", "passive", "B", 10.16),
               ], w=25.4, h=30.48),
    # OPA836, DBV SOT-23-6 (datasheet Fig. 6-4, Table 6-1): PD high = on.
    box_symbol("OPA836_DBV", "U", "OPA836", "Package_TO_SOT_SMD:SOT-23-6",
               "205 MHz rail-to-rail-output op amp with power-down, SOT-23-6",
               "design/datasheets/opa836.pdf", [
                   ("3", "+", "input", "L", 2.54),
                   ("4", "-", "input", "L", -2.54),
                   ("1", "OUT", "output", "R", 0.0),
                   ("6", "VS+", "power_in", "T", -2.54),
                   ("5", "PD", "input", "T", 2.54),
                   ("2", "VS-", "power_in", "B", -2.54),
               ], w=10.16, h=7.62),
]


def write_symbols():
    text = "(kicad_symbol_lib\n\t(version 20241209)\n\t(generator \"studio_amp_lib_D\")\n\t(generator_version \"9.0\")\n"
    text += "\n".join(SYMBOLS) + "\n)\n"
    SYM.write_text(text)


# ------------------------------------------------------------------ footprints
def fp_header(name, descr, smd=True, tags=""):
    return [f"(footprint {q(name)}", "\t(version 20241229)", "\t(generator \"studio_amp_lib_D\")",
            "\t(generator_version \"9.0\")", "\t(layer \"F.Cu\")", f"\t(descr {q(descr)})",
            f"\t(tags {q(tags)})",
            f"\t(attr {'smd' if smd else 'through_hole'})"]


def fp_text(kind, val, x, y, layer, size=1.0, hide=False):
    h_ = " (hide yes)" if hide else ""
    return (f"\t(property {q(kind)} {q(val)} (at {f(x)} {f(y)} 0) (layer {q(layer)}){h_} "
            f"(uuid {q(uuid.uuid4())}) (effects (font (size {f(size)} {f(size)}) (thickness 0.15))))")


def rect(x1, y1, x2, y2, layer, w=0.12):
    return (f"\t(fp_rect (start {f(x1)} {f(y1)}) (end {f(x2)} {f(y2)}) (stroke (width {f(w)}) (type solid)) "
            f"(fill no) (layer {q(layer)}) (uuid {q(uuid.uuid4())}))")


def line(x1, y1, x2, y2, layer, w=0.12):
    return (f"\t(fp_line (start {f(x1)} {f(y1)}) (end {f(x2)} {f(y2)}) (stroke (width {f(w)}) (type solid)) "
            f"(layer {q(layer)}) (uuid {q(uuid.uuid4())}))")


def smd(num, x, y, w, h, shape="roundrect", paste_ratio=None, rr=0.1):
    extra = f" (roundrect_rratio {f(rr)})" if shape == "roundrect" else ""
    pr = f" (solder_paste_margin_ratio {f(paste_ratio)})" if paste_ratio is not None else ""
    return (f"\t(pad {q(num)} smd {shape} (at {f(x)} {f(y)}) (size {f(w)} {f(h)}) "
            f"(layers \"F.Cu\" \"F.Paste\" \"F.Mask\"){extra}{pr} (uuid {q(uuid.uuid4())}))")


def tht(num, x, y, d, drill, shape="circle"):
    return (f"\t(pad {q(num)} thru_hole {shape} (at {f(x)} {f(y)}) (size {f(d)} {f(d)}) (drill {f(drill)}) "
            f"(layers \"*.Cu\" \"*.Mask\") (uuid {q(uuid.uuid4())}))")


def finish(lines, name, cy1, cy2, cx1, cx2, ref_y, val_y):
    out = lines[:8]
    out.append(fp_text("Reference", "REF**", 0, ref_y, "F.SilkS"))
    out.append(fp_text("Value", name, 0, val_y, "F.Fab"))
    out += lines[8:]
    out.append(rect(cx1, cy1, cx2, cy2, "F.CrtYd", 0.05))
    out.append("\t(embedded_fonts no)")
    out.append(")")
    (PRETTY / f"{name}.kicad_mod").write_text("\n".join(out) + "\n")


def fp_igb070():
    """IGB070S10S1 PG-TSON-4, footprint drawing Fig. 2 p.14 (top view, mm). Rows: top = pin 3 (source),
    middle = pin 2 (drain), bottom = pin 1 (gate, left) and pin 4 (source, right); outer edges at
    +/-1.505. The datasheet pads are solder-mask defined with notched edges; drawn here as their
    full copper rectangles (notches filled, same net) with paste reduced 15 %. Phase 6 reserves the
    IGC033S10S1 (PG-TSON-6, 3 x 5 mm) courtyard around each site (D-gan-fet.md)."""
    name = "IGB070S10S1_PG-TSON-4"
    L = fp_header(name, "Infineon PG-TSON-4 3.2x3.0 mm, IGB070S10S1 (datasheet Fig. 2 p.14)", tags="GaN TSON")
    L += [smd("3", 0, -1.2025, 3.2, 0.605, paste_ratio=-0.15, rr=0.05),
          smd("2", 0, 0, 3.2, 0.35, paste_ratio=-0.15, rr=0.05),
          smd("1", -1.175, 1.2025, 0.85, 0.605, paste_ratio=-0.15, rr=0.05),
          smd("4", 0.625, 1.2025, 1.95, 0.605, paste_ratio=-0.15, rr=0.05),
          rect(-1.6, -1.5, 1.6, 1.5, "F.Fab", 0.1),
          line(-1.75, 1.65, -1.75, 1.95, "F.SilkS"), line(-1.75, 1.95, -1.3, 1.95, "F.SilkS"),
          line(-1.75, -1.65, 1.75, -1.65, "F.SilkS")]
    finish(L, name, -2.0, 2.2, -2.0, 2.0, -2.6, 2.7)


def fp_rvr():
    """LMG1210 RVR0019A WQFN-19, TI land pattern example (datasheet p.24), top view, mm."""
    name = "Texas_RVR0019A_WQFN-19-2EP_4x3mm_P0.5mm"
    L = fp_header(name, "TI RVR0019A WQFN-19, 4x3 mm, two exposed pads (LMG1210 datasheet p.23-24)",
                  tags="WQFN LMG1210")
    pads = []
    for i, y in zip(range(1, 6), (-1.0, -0.5, 0.0, 0.5, 1.0)):
        pads.append(smd(str(i), -1.9, y, 0.6, 0.25, rr=0.2))
    for n, x in zip(range(6, 11), (-1.25, -0.75, -0.25, 0.75, 1.25)):
        pads.append(smd(str(n), x, 1.4, 0.25, 0.6, rr=0.2))
    for n, y in zip(range(11, 16), (1.0, 0.5, 0.0, -0.5, -1.0)):
        pads.append(smd(str(n), 1.9, y, 0.6, 0.25, rr=0.2))
    for n, x in zip(range(16, 20), (1.25, -0.25, -0.75, -1.25)):
        pads.append(smd(str(n), x, -1.4, 0.25, 0.6, rr=0.2))
    pads.append(smd("20", -0.75, 0, 1.2, 1.7, shape="rect", paste_ratio=-0.25))
    pads.append(smd("21", 0.975, 0, 0.75, 1.7, shape="rect", paste_ratio=-0.25))
    L += pads + [rect(-2.0, -1.5, 2.0, 1.5, "F.Fab", 0.1),
                 line(-2.15, -1.65, -1.6, -1.65, "F.SilkS"), line(-2.15, -1.65, -2.15, -1.3, "F.SilkS"),
                 line(2.15, 1.65, 1.6, 1.65, "F.SilkS"), line(2.15, 1.65, 2.15, 1.3, "F.SilkS")]
    finish(L, name, -2.0, 2.0, -2.5, 2.5, -2.6, 2.6)


def fp_ser2915():
    """Coilcraft SER2915H recommended land pattern (Doc 644-2, p.2), mm. Pad 3 is mechanical only
    (no net; the symbol has 2 pins)."""
    name = "Coilcraft_SER2915H"
    L = fp_header(name, "Coilcraft SER2915H shielded power inductor, 27.9x19.8 mm, 3-pad land pattern (Doc 644-2)",
                  tags="inductor ferrite")
    L += [smd("1", -5.075, 14.355, 5.33, 5.59, rr=0.05),
          smd("2", 5.075, 14.355, 5.33, 5.59, rr=0.05),
          smd("", 0, -7.72, 6.35, 5.28, rr=0.05),
          rect(-13.95, -9.9, 13.95, 9.9, "F.Fab", 0.1),
          rect(-14.1, -10.05, 14.1, 10.05, "F.SilkS")]
    finish(L, name, -10.9, 17.6, -14.5, 14.5, -11.6, 0)


def fp_connector():
    """MAX MX2EDGRC-5.08-02P right-angle closed header (CIXI MAIXU drawing), pins at 5.08 mm,
    PCB hole 1.70 mm; body 11.90 deep, pin row 3.28 mm from the body edge, length 5.08 + 6.56."""
    name = "MAX_MX2EDGRC-5.08-02P_1x02_P5.08mm_Horizontal"
    L = fp_header(name, "MAX (CIXI MAIXU) MX2EDGRC-5.08-02P pluggable header, 15 A, mates MX2EDGK-5.08-02P",
                  smd=False, tags="terminal block 5.08")
    L += [tht("1", 0, 0, 2.7, 1.7, shape="rect"), tht("2", 5.08, 0, 2.7, 1.7),
          rect(-3.28, -8.62, 8.36, 3.28, "F.Fab", 0.1),
          rect(-3.43, -8.77, 8.51, 3.43, "F.SilkS")]
    finish(L, name, -9.1, 3.9, -3.8, 8.9, -9.8, 4.6)


def fp_film():
    """TDK B32774D4226K, 2-pin, lead spacing 27.5 +/- 0.4 mm, lead 0.8 mm, body 22.0 x 31.5 mm max (b32774.pdf)."""
    name = "C_Rect_L31.5mm_W22.0mm_P27.50mm_B32774"
    L = fp_header(name, "TDK B32774D 2-pin MKP DC-link, 31.5 x 22.0 mm, 27.5 mm pitch", smd=False,
                  tags="film capacitor")
    L += [tht("1", 0, 0, 2.0, 1.2, shape="rect"), tht("2", 27.5, 0, 2.0, 1.2),
          rect(-2.0, -11.0, 29.5, 11.0, "F.Fab", 0.1),
          rect(-2.15, -11.15, 29.65, 11.15, "F.SilkS")]
    finish(L, name, -11.5, 11.5, -2.5, 30.0, -12.2, 12.2)


def fp_shunt():
    """2512 current-sense resistor with Kelvin sense pads (Yageo PA2512, 5 mOhm: L 6.35, W 3.18,
    terminal 1.19 mm, Fig. 3). Pads 1/4 carry current; 2/3 are sense pads at the inner edges,
    net-tied to 1/4 (KiCad net-tie groups)."""
    name = "R_2512_6332Metric_Kelvin_NetTie"
    L = fp_header(name, "2512 shunt, 4-terminal Kelvin land pattern (net-tie 1-2, 3-4)", tags="shunt kelvin")
    L.insert(7, "\t(net_tie_pad_groups \"1,2\" \"3,4\")")
    L += [smd("1", -3.1, 0, 1.6, 3.4, rr=0.1), smd("4", 3.1, 0, 1.6, 3.4, rr=0.1),
          smd("2", -2.1, 0.9, 0.5, 0.9, shape="rect"), smd("3", 2.1, 0.9, 0.5, 0.9, shape="rect"),
          rect(-3.175, -1.59, 3.175, 1.59, "F.Fab", 0.1),
          line(-1.6, -1.8, 1.6, -1.8, "F.SilkS"), line(-1.6, 1.8, 1.6, 1.8, "F.SilkS")]
    finish(L, name, -2.0, 2.0, -4.2, 4.2, -2.6, 2.6)


if __name__ == "__main__":
    PRETTY.mkdir(exist_ok=True)
    write_symbols()
    for fn in (fp_igb070, fp_rvr, fp_ser2915, fp_connector, fp_film, fp_shunt):
        fn()
    print("wrote", SYM, "and", len(list(PRETTY.glob('*.kicad_mod'))), "footprints")
