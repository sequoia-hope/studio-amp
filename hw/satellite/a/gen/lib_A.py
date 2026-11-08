"""lib_A.py -- block A (poe_in) project symbols and footprints.

Writes hw/satellite/a/lib/studio_A.kicad_sym and the footprints KiCad lacks in
hw/satellite/a/lib/studio_A.pretty. Every pin number and land is from the part's
datasheet in design/datasheets/ (cited per part below and in design/parts/A-*.md).
Run: python3 hw/satellite/a/gen/lib_A.py
"""
from __future__ import annotations

import re
from pathlib import Path

HERE = Path(__file__).resolve().parent
LIB = HERE.parent / "lib"
SYS = Path("/usr/share/kicad/symbols")


# ---------------------------------------------------------------- symbol text helpers

def _f(v: float) -> str:
    s = f"{v:.4f}".rstrip("0").rstrip(".")
    return "0" if s in ("-0", "") else s


def prop(name, value, x=0.0, y=0.0, hide=False, justify=None):
    j = f" (justify {justify})" if justify else ""
    h = " (hide yes)" if hide else ""
    return (f'\t\t(property "{name}" "{value}"\n\t\t\t(at {_f(x)} {_f(y)} 0)\n'
            f'\t\t\t(effects (font (size 1.27 1.27)){j}{h})\n\t\t)\n')


def pin(num, name, x, y, ang, etype="passive", length=2.54, hidden=False):
    h = "\n\t\t\t\t(hide yes)" if hidden else ""
    return (f'\t\t\t(pin {etype} line\n\t\t\t\t(at {_f(x)} {_f(y)} {ang})\n\t\t\t\t(length {_f(length)}){h}\n'
            f'\t\t\t\t(name "{name}" (effects (font (size 1.27 1.27))))\n'
            f'\t\t\t\t(number "{num}" (effects (font (size 1.27 1.27))))\n\t\t\t)\n')


def rect(x0, y0, x1, y1, fill="background"):
    return (f'\t\t\t(rectangle (start {_f(x0)} {_f(y0)}) (end {_f(x1)} {_f(y1)})\n'
            f'\t\t\t\t(stroke (width 0.254) (type default)) (fill (type {fill})))\n')


def line(pts, dash=False):
    p = " ".join(f"(xy {_f(x)} {_f(y)})" for x, y in pts)
    t = "dash" if dash else "default"
    return f'\t\t\t(polyline (pts {p}) (stroke (width 0.1524) (type {t})) (fill (type none)))\n'


def gtext(s, x, y, size=1.27):
    return f'\t\t\t(text "{s}" (at {_f(x)} {_f(y)} 0) (effects (font (size {size} {size}))))\n'


def symbol(name, ref, value, footprint, datasheet, descr, body, pins, ref_at, val_at, pin_names_offset=0.762):
    out = f'\t(symbol "{name}"\n\t\t(pin_names (offset {pin_names_offset}))\n\t\t(exclude_from_sim no)\n\t\t(in_bom yes)\n\t\t(on_board yes)\n'
    out += prop("Reference", ref, *ref_at, justify="left")
    out += prop("Value", value, *val_at, justify="left")
    out += prop("Footprint", footprint, hide=True)
    out += prop("Datasheet", datasheet, hide=True)
    out += prop("Description", descr, hide=True)
    out += f'\t\t(symbol "{name}_0_1"\n{body}\t\t)\n'
    out += f'\t\t(symbol "{name}_1_1"\n{pins}\t\t)\n'
    out += "\t\t(embedded_fonts no)\n\t)\n"
    return out


# ---------------------------------------------------------------- symbols

def tps2373():
    """TPS2373-4, TI SLUSCD1C p.4 (RGW VQFN-20). Exposed pad = pin 21, internally VSS (p.4)."""
    P = ""
    # top: power in / bias
    P += pin(1, "VDD", -7.62, 27.94, 270, "power_in")
    P += pin(14, "VC_OUT", 2.54, 27.94, 270, "power_out")
    P += pin(15, "VC_IN", 7.62, 27.94, 270, "power_in")
    # bottom: VSS (4, 5, EP 21 stacked) and the switched return RTN (11, 12)
    P += pin(4, "VSS", -7.62, -27.94, 90, "power_in")
    P += pin(5, "VSS", -7.62, -27.94, 90, "passive", hidden=True)
    P += pin(21, "VSS", -7.62, -27.94, 90, "passive", hidden=True)
    P += pin(11, "RTN", 7.62, -27.94, 90, "power_out")
    P += pin(12, "RTN", 7.62, -27.94, 90, "passive", hidden=True)
    # left: detection, classification, reference, MPS
    P += pin(2, "DEN", -15.24, 17.78, 0, "bidirectional")
    P += pin(3, "CLSA", -15.24, 10.16, 0, "output")
    P += pin(6, "CLSB", -15.24, 5.08, 0, "output")
    P += pin(7, "REF", -15.24, 0, 0, "output")
    P += pin(9, "MPS_DUTY", -15.24, -10.16, 0, "input")
    P += pin(20, "NC", -15.24, -17.78, 0, "no_connect")
    # right: status outputs and their controls
    P += pin(13, "PG", 15.24, 15.24, 180, "open_collector")
    P += pin(18, "~{TPH}", 15.24, 5.08, 180, "open_collector")
    P += pin(17, "~{TPL}", 15.24, 0, 180, "open_collector")
    P += pin(19, "~{BT}", 15.24, -5.08, 180, "open_collector")
    P += pin(8, "AMPS_CTL", 15.24, -10.16, 180, "output")
    P += pin(16, "UVLO_SEL", 15.24, -15.24, 180, "input")
    P += pin(10, "APD", 15.24, -20.32, 180, "input")
    body = rect(-12.7, 25.4, 12.7, -25.4)
    return symbol("TPS2373-4", "U", "TPS2373-4", "studio_A:TI_RGW0020B_VQFN-20-1EP_5x5mm_P0.65mm_EP2.2x2.2mm",
                  "design/datasheets/tps2373.pdf", "IEEE 802.3bt Type 4 PoE PD interface, 100 V hot-swap",
                  body, P, (-12.7, 30.48), (-12.7, -30.48))


def lt4321():
    """LT4321, Linear 4321f p.2 (UF16 4x4 QFN). Exposed pad 17 = OUTN."""
    P = ""
    P += pin(12, "OUTP", 0, 22.86, 270, "power_in")
    P += pin(9, "OUTN", 0, -22.86, 90, "power_in")
    P += pin(17, "OUTN", 0, -22.86, 90, "passive", hidden=True)
    P += pin(15, "IN12", -12.7, 15.24, 0, "input")
    P += pin(2, "IN36", -12.7, 12.7, 0, "input")
    P += pin(3, "IN45", -12.7, 7.62, 0, "input")
    P += pin(6, "IN78", -12.7, 5.08, 0, "input")
    P += pin(16, "TG12", 12.7, 17.78, 180, "output")
    P += pin(14, "BG12", 12.7, 15.24, 180, "output")
    P += pin(1, "TG36", 12.7, 12.7, 180, "output")
    P += pin(13, "BG36", 12.7, 10.16, 180, "output")
    P += pin(4, "TG45", 12.7, 5.08, 180, "output")
    P += pin(8, "BG45", 12.7, 2.54, 180, "output")
    P += pin(5, "TG78", 12.7, 0, 180, "output")
    P += pin(7, "BG78", 12.7, -2.54, 180, "output")
    P += pin(10, "~{EN}", 12.7, -12.7, 180, "input")
    P += pin(11, "EN", 12.7, -17.78, 180, "input")
    body = rect(-10.16, 20.32, 10.16, -20.32)
    return symbol("LT4321", "U", "LT4321", "Package_DFN_QFN:QFN-16-1EP_4x4mm_P0.65mm_EP2.15x2.15mm",
                  "design/datasheets/A-lt4321.pdf", "PoE dual ideal-diode bridge controller, 8 external N-FETs",
                  body, P, (-10.16, 25.4), (-10.16, -25.4))


def iso7740():
    """ISO7740DW, TI ZHCSF48F pin table p.7 (SOIC-16 DW). Pin 7 NC, EN2 pin 10."""
    P = ""
    P += pin(1, "VCC1", -5.08, 15.24, 270, "power_in")
    P += pin(16, "VCC2", 5.08, 15.24, 270, "power_in")
    P += pin(2, "GND1", -5.08, -15.24, 90, "power_in")
    P += pin(8, "GND1", -5.08, -15.24, 90, "passive", hidden=True)
    P += pin(9, "GND2", 5.08, -15.24, 90, "power_in")
    P += pin(15, "GND2", 5.08, -15.24, 90, "passive", hidden=True)
    P += pin(3, "INA", -12.7, 7.62, 0, "input")
    P += pin(4, "INB", -12.7, 5.08, 0, "input")
    P += pin(5, "INC", -12.7, 2.54, 0, "input")
    P += pin(6, "IND", -12.7, 0, 0, "input")
    P += pin(7, "NC", -12.7, -7.62, 0, "no_connect")
    P += pin(14, "OUTA", 12.7, 7.62, 180, "output")
    P += pin(13, "OUTB", 12.7, 5.08, 180, "output")
    P += pin(12, "OUTC", 12.7, 2.54, 180, "output")
    P += pin(11, "OUTD", 12.7, 0, 180, "output")
    P += pin(10, "EN2", 12.7, -7.62, 180, "input")
    body = rect(-10.16, 12.7, 10.16, -12.7) + line([(0, 12.7), (0, -12.7)], dash=True)
    return symbol("ISO7740DW", "U", "ISO7740DWR", "Package_SO:SOIC-16W_7.5x10.3mm_P1.27mm",
                  "design/datasheets/A-iso7740.pdf", "4-channel digital isolator, 5 kVrms, default-high outputs",
                  body, P, (-10.16, 17.78), (-10.16, -17.78))


def magjack():
    """LINK-PP LPJK6078AHNL, drawing LP23032002 rev A6 sheet 1 schematic. Pins 13-16 are the
    line-side centre taps (VC+/VC-), 1-12 PHY side, 17-20 LEDs, SH = shield tabs."""
    P = ""
    for num, name, y in ((13, "CT1-2", 33.02), (14, "CT3-6", 27.94), (15, "CT4-5", 22.86), (16, "CT7-8", 17.78),
                         (11, "MD1+", -5.08), (10, "MD1-", -7.62), (4, "MD2+", -10.16), (5, "MD2-", -12.7),
                         (12, "MDCT1", -20.32), (6, "MDCT2", -22.86)):
        P += pin(num, name, 15.24, y, 180)
    for num, name, y in ((3, "MD3+", -5.08), (2, "MD3-", -7.62), (1, "MDCT3", -10.16),
                         (8, "MD4+", -15.24), (9, "MD4-", -17.78), (7, "MDCT4", -20.32),
                         (18, "LEDY+", -25.4), (20, "LEDG+", -30.48), (17, "LEDY-", -33.02), (19, "LEDG-", -35.56)):
        P += pin(num, name, -15.24, y, 0)
    P += pin("SH", "SH", 0, -40.64, 90)
    body = (rect(-12.7, 38.1, 12.7, -38.1)
            + line([(-12.7, 7.62), (12.7, 7.62)], dash=True)
            + gtext("LINE SIDE (primary)", 0, 12.7) + gtext("PHY SIDE (secondary)", 0, 2.54)
            + gtext("4x 1CT:1CT,", -5.08, 27.94, 1.0) + gtext("Bob Smith", -5.08, 25.4, 1.0) + gtext("inside", -5.08, 22.86, 1.0))
    return symbol("LPJK6078AHNL", "J", "LPJK6078AHNL", "studio_A:LINKPP_LPJK6078AHNL_RJ45_PoE",
                  "design/datasheets/A-lpjk6078ahnl.pdf",
                  "RJ45 with 1000BASE-T PoE++ magnetics (1.0 A per CT), Bob Smith 4x75R/22nF + 1nF 2kV to shield",
                  body, P, (-12.7, 40.64), (-12.7, -43.18))


def psmn040():
    """PSMN040-100MSE (LFPAK33 / SOT1210): pins 1-3 S, 4 G, mounting base D (pad 5), datasheet p.2.
    Graphic and pin geometry copied from KiCad's PSMN5R2-60YL (same LFPAK pinning)."""
    t = (SYS / "Transistor_FET.kicad_sym").read_text()
    i = t.index('\t(symbol "PSMN5R2-60YL"')
    j = t.find('\n\t(symbol "', i + 10)
    s = t[i:j].rstrip() + "\n"
    s = s.replace("PSMN5R2-60YL", "PSMN040-100MSE")
    s = s.replace("Package_TO_SOT_SMD:LFPAK56", "Package_TO_SOT_SMD:LFPAK33")
    s = re.sub(r'"https://assets.nexperia.com/documents/data-sheet/[^"]*"', '"design/datasheets/A-psmn040-100mse.pdf"', s)
    s = re.sub(r'\(property "Description" "[^"]*"', '(property "Description" "100 V 36.6 mOhm N-MOSFET, LFPAK33"', s)
    s = s.replace('"LFPAK56*"', '"LFPAK33*"')
    return s


def main():
    syms = [tps2373(), lt4321(), iso7740(), magjack(), psmn040()]
    text = ('(kicad_symbol_lib\n\t(version 20241209)\n\t(generator "kicad_symbol_editor")\n'
            '\t(generator_version "9.0")\n' + "".join(syms) + ")\n")
    (LIB / "studio_A.kicad_sym").write_text(text)
    fp_tps2373()
    fp_magjack()
    print("wrote", LIB / "studio_A.kicad_sym", "and footprints")


# ---------------------------------------------------------------- footprints

def _pad(num, kind, shape, x, y, w, h, layers, drill=None, rr=None, extra=""):
    d = f" (drill {_f(drill)})" if drill else ""
    r = f" (roundrect_rratio {rr})" if rr else ""
    return (f'\t(pad "{num}" {kind} {shape} (at {_f(x)} {_f(y)}) (size {_f(w)} {_f(h)}){d} '
            f'(layers {layers}){r}{extra})\n')


def _fp(name, descr, attr, pads, graphics, ref_y, val_y):
    return (f'(footprint "{name}"\n\t(version 20241229)\n\t(generator "lib_A.py")\n\t(layer "F.Cu")\n'
            f'\t(descr "{descr}")\n'
            f'\t(property "Reference" "REF**" (at 0 {_f(ref_y)} 0) (layer "F.SilkS") (effects (font (size 1 1) (thickness 0.15))))\n'
            f'\t(property "Value" "{name}" (at 0 {_f(val_y)} 0) (layer "F.Fab") (effects (font (size 1 1) (thickness 0.15))))\n'
            f'\t(attr {attr})\n{graphics}{pads})\n')


def _rect_g(x0, y0, x1, y1, layer, w):
    return f'\t(fp_rect (start {_f(x0)} {_f(y0)}) (end {_f(x1)} {_f(y1)}) (stroke (width {w}) (type default)) (fill no) (layer "{layer}"))\n'


def fp_tps2373():
    """TI RGW0020B land pattern, TPS2373 datasheet p.41 (example board layout): 20 pads 0.75 x 0.31 on
    0.65 mm pitch, pad rows 4.65 mm apart (centres +-2.325), EP 2.2 x 2.2 (pad 21, VSS) with 9 vias
    of 0.2 mm on 0.85 mm pitch (p.37 "nine vias", p.41); stencil p.42: 4 x 0.98 mm windows on 0.59 mm
    offsets. Pin 1 top of the left row, numbering counter-clockwise (p.40)."""
    pads = ""
    c, pitch, L, W = 2.325, 0.65, 0.75, 0.31
    for i in range(5):
        y = -1.3 + i * pitch
        pads += _pad(1 + i, "smd", "roundrect", -c, y, L, W, '"F.Cu" "F.Mask" "F.Paste"', rr=0.25)
        pads += _pad(11 + i, "smd", "roundrect", c, -y, L, W, '"F.Cu" "F.Mask" "F.Paste"', rr=0.25)
        x = -1.3 + i * pitch
        pads += _pad(6 + i, "smd", "roundrect", x, c, W, L, '"F.Cu" "F.Mask" "F.Paste"', rr=0.25)
        pads += _pad(16 + i, "smd", "roundrect", -x, -c, W, L, '"F.Cu" "F.Mask" "F.Paste"', rr=0.25)
    pads += _pad(21, "smd", "rect", 0, 0, 2.2, 2.2, '"F.Cu" "F.Mask"')
    for sx in (-0.59, 0.59):
        for sy in (-0.59, 0.59):
            pads += _pad("", "smd", "roundrect", sx, sy, 0.98, 0.98, '"F.Paste"', rr=0.1)
    for vx in (-0.85, 0, 0.85):
        for vy in (-0.85, 0, 0.85):
            pads += _pad(21, "thru_hole", "circle", vx, vy, 0.45, 0.45, '"*.Cu"', drill=0.2)
    g = (_rect_g(-2.5, -2.5, 2.5, 2.5, "F.Fab", 0.1) + _rect_g(-3.0, -3.0, 3.0, 3.0, "F.CrtYd", 0.05)
         + '\t(fp_line (start -2.61 -2.61) (end -1.75 -2.61) (stroke (width 0.12) (type default)) (layer "F.SilkS"))\n'
         + '\t(fp_line (start -2.61 -2.61) (end -2.61 -1.75) (stroke (width 0.12) (type default)) (layer "F.SilkS"))\n'
         + '\t(fp_circle (center -3.0 -1.3) (end -2.85 -1.3) (stroke (width 0.3) (type default)) (fill yes) (layer "F.SilkS"))\n')
    name = "TI_RGW0020B_VQFN-20-1EP_5x5mm_P0.65mm_EP2.2x2.2mm"
    (LIB / "studio_A.pretty" / f"{name}.kicad_mod").write_text(
        _fp(name, "TI RGW0020B VQFN-20 5x5 mm, EP 2.2 mm (TPS2373 SLUSCD1C pp.40-42), 9 thermal vias",
            "smd", pads, g, -3.8, 3.8))


def fp_magjack():
    """LPJK6078AHNL, drawing LP23032002 sheet 2 'Suggested PCB Layout (Top View)'. Origin = midpoint
    of the two shield-tab holes (front of the jack, opening towards -x). Holes: 16 x 0.89 signal,
    4 x 1.03 LED, 2 x 3.20 posts (NPTH), 2 x 1.57 shield tabs.
      shield tabs  x 0,      y +-8.15 (16.30 apart)
      posts        x 3.18,   y +-6.35 (12.70 apart)
      pins 15/16   x 9.81 (3.18 + 6.63), pins 13/14 x 11.31 (+1.50); y +-5.59 (11.18 apart)
      pins 1-6     x 18.42,  y +5.075 (1) ... -5.075 (6), 2.03 pitch
      pins 7-12    x 20.96,  y +6.09 (7), 4.06, 2.03, -2.03, -4.06, -6.09 (12)
      LEDs         x 23.5,   20 at -6.09, 19 at -3.55, 18 at +3.55, 17 at +6.09 (12.18 / 2.54 dims)
    (Drawing y is up; KiCad y is down: pin 1 sits at +y, the bottom of the drawing.)"""
    pads = ""
    for i, n in enumerate((1, 2, 3, 4, 5, 6)):
        pads += _pad(n, "thru_hole", "rect" if n == 1 else "circle", 18.42, 5.075 - i * 2.03, 1.4, 1.4,
                     '"*.Cu" "*.Mask"', drill=0.89)
    for n, y in ((7, 6.09), (8, 4.06), (9, 2.03), (10, -2.03), (11, -4.06), (12, -6.09)):
        pads += _pad(n, "thru_hole", "circle", 20.96, y, 1.4, 1.4, '"*.Cu" "*.Mask"', drill=0.89)
    for n, x, y in ((16, 9.81, -5.59), (14, 11.31, -5.59), (15, 9.81, 5.59), (13, 11.31, 5.59)):
        pads += _pad(n, "thru_hole", "circle", x, y, 1.3, 1.3, '"*.Cu" "*.Mask"', drill=0.89)
    for n, y in ((20, -6.09), (19, -3.55), (18, 3.55), (17, 6.09)):
        pads += _pad(n, "thru_hole", "circle", 23.5, y, 1.6, 1.6, '"*.Cu" "*.Mask"', drill=1.03)
    for y in (-8.15, 8.15):
        pads += _pad("SH", "thru_hole", "circle", 0, y, 2.4, 2.4, '"*.Cu" "*.Mask"', drill=1.57)
    for y in (-6.35, 6.35):
        pads += _pad("", "np_thru_hole", "circle", 3.18, y, 3.2, 3.2, '"*.Cu" "*.Mask"', drill=3.2)
    g = (_rect_g(-2.0, -8.15, 24.5, 8.15, "F.Fab", 0.1)
         + _rect_g(-2.5, -9.6, 25.0, 9.6, "F.CrtYd", 0.05)
         + '\t(fp_text user "front: cable entry" (at -1.0 0 90) (layer "F.Fab") (effects (font (size 0.8 0.8) (thickness 0.12))))\n'
         + '\t(fp_text user "CHECK body outline vs LP23032002 sheet 2 side views (phase 4)" (at 11 10.5 0) (layer "Cmts.User") (effects (font (size 0.6 0.6) (thickness 0.1))))\n')
    name = "LINKPP_LPJK6078AHNL_RJ45_PoE"
    (LIB / "studio_A.pretty" / f"{name}.kicad_mod").write_text(
        _fp(name, "LINK-PP LPJK6078AHNL RJ45 PoE++ magjack, LP23032002 rev A6 suggested layout", "through_hole",
            pads, g, -10.5, 11.5))


if __name__ == "__main__":
    main()
