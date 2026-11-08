"""lib_F.py -- block F project symbols and footprints (studio_F).

Writes hw/satellite/a/lib/studio_F.kicad_sym and studio_F.pretty/*.kicad_mod.
Every pin number and land comes from the datasheet named beside it
(design/datasheets/); see the part audits in design/parts/F-*.md.

    python3 hw/satellite/a/gen/lib_F.py
"""
from __future__ import annotations

import uuid
from pathlib import Path

LIB = Path(__file__).resolve().parents[1] / "lib"
U = lambda: str(uuid.uuid4())


# ------------------------------------------------------------------ symbols

def _font(hide=False, justify=None):
    j = f" (justify {justify})" if justify else ""
    h = " (hide yes)" if hide else ""
    return f"(effects (font (size 1.27 1.27)){j}{h})"


def _prop(name, value, x=0.0, y=0.0, hide=False, justify=None):
    return f'\t\t(property "{name}" "{value}" (at {x} {y} 0) {_font(hide, justify)})\n'


def _pin(num, name, x, y, ang, etype="passive", length=2.54, hide_name=False):
    return (f'\t\t\t(pin {etype} line (at {x} {y} {ang}) (length {length})'
            f' (name "{name}" (effects (font (size 1.27 1.27))))'
            f' (number "{num}" (effects (font (size 1.27 1.27)))))\n')


def symbol(name, ref, value, fp, ds, desc, body, pins, ref_at, val_at, hide_pin_names=False,
           hide_pin_numbers=False):
    s = f'\t(symbol "{name}"\n'
    if hide_pin_names:
        s += "\t\t(pin_names (hide yes))\n"
    if hide_pin_numbers:
        s += "\t\t(pin_numbers (hide yes))\n"
    s += "\t\t(exclude_from_sim no) (in_bom yes) (on_board yes)\n"
    s += _prop("Reference", ref, *ref_at)
    s += _prop("Value", value, *val_at)
    s += _prop("Footprint", fp, hide=True)
    s += _prop("Datasheet", ds, hide=True)
    s += _prop("Description", desc, hide=True)
    s += f'\t\t(symbol "{name}_0_1"\n{body}\t\t)\n'
    s += f'\t\t(symbol "{name}_1_1"\n' + "".join(_pin(*p) for p in pins) + "\t\t)\n"
    s += "\t\t(embedded_fonts no)\n\t)\n"
    return s


def rect(x1, y1, x2, y2, fill="background"):
    return (f"\t\t\t(rectangle (start {x1} {y1}) (end {x2} {y2}) (stroke (width 0.254) (type default))"
            f" (fill (type {fill})))\n")


def poly(*pts, w=0.254):
    p = " ".join(f"(xy {x} {y})" for x, y in pts)
    return f"\t\t\t(polyline (pts {p}) (stroke (width {w}) (type default)) (fill (type none)))\n"


def circ(x, y, r, fill="none"):
    return f"\t\t\t(circle (center {x} {y}) (radius {r}) (stroke (width 0.254) (type default)) (fill (type {fill})))\n"


def text(s, x, y):
    return f'\t\t\t(text "{s}" (at {x} {y} 0) (effects (font (size 1.27 1.27))))\n'


SYMS = []

# PCM1808 (pcm1808.pdf p.5 pin assignments). Analog inputs left; clock and serial port right (they
# go to the FPGA); supplies top; VREF, grounds and the mode straps along the bottom.
SYMS.append(symbol(
    "PCM1808", "U", "PCM1808", "Package_SO:TSSOP-14_4.4x5mm_P0.65mm", "design/datasheets/pcm1808.pdf",
    "Stereo 24-bit 96 kHz delta-sigma ADC, single-ended inputs, I2S/LJ",
    rect(-10.16, 12.7, 10.16, -12.7),
    [("13", "VINL", -12.7, 7.62, 0, "input"),
     ("14", "VINR", -12.7, -2.54, 0, "input"),
     ("6", "SCKI", 12.7, 7.62, 180, "input"),
     ("8", "BCK", 12.7, 2.54, 180, "bidirectional"),
     ("7", "LRCK", 12.7, 0, 180, "bidirectional"),
     ("9", "DOUT", 12.7, -5.08, 180, "output"),
     ("3", "VCC", -2.54, 15.24, 270, "power_in"),
     ("4", "VDD", 2.54, 15.24, 270, "power_in"),
     ("1", "VREF", -7.62, -15.24, 90, "passive"),
     ("2", "AGND", -5.08, -15.24, 90, "power_in"),
     ("5", "DGND", -2.54, -15.24, 90, "power_in"),
     ("10", "MD0", 2.54, -15.24, 90, "input"),
     ("11", "MD1", 5.08, -15.24, 90, "input"),
     ("12", "FMT", 7.62, -15.24, 90, "input")],
    (-10.16, 13.97), (2.54, 13.97)))

# T3902 (t3902.pdf p.10 table 9): CLK/SELECT in, DATA out, VDD top, GND bottom.
SYMS.append(symbol(
    "T3902", "MK", "T3902", "studio_F:TDK_T3902_LGA-5_3.5x2.65mm", "design/datasheets/t3902.pdf",
    "TDK InvenSense bottom-port PDM MEMS microphone",
    rect(-7.62, 5.08, 7.62, -5.08) + circ(4.445, 2.54, 0.635),
    [("4", "CLK", -10.16, 1.27, 0, "input"),
     ("2", "SELECT", -10.16, -1.27, 0, "input"),
     ("1", "DATA", 10.16, 0, 180, "tri_state"),
     ("5", "VDD", 0, 7.62, 270, "power_in"),
     ("3", "GND", 0, -7.62, 90, "power_in")],
    (-7.62, 6.35), (2.54, 6.35)))

# Hongfa HFD4 DPDT, single-side stable (hfd4.pdf p.70 wiring diagram, bottom view, de-energised):
# coil 1 (+) / 8 (-); pole 1: COM 3, NC 2, NO 4; pole 2: COM 6, NC 7, NO 5.
relay_body = (rect(-7.62, 10.16, 7.62, -10.16)
              + rect(-6.35, 2.54, -3.81, -2.54, fill="none")       # coil
              + poly((-6.35, 2.54), (-3.81, -2.54), w=0.1524)
              + poly((-5.08, 7.62), (-5.08, 2.54)) + poly((-5.08, -2.54), (-5.08, -7.62))
              # pole 1: COM at y=5.08 on the right edge region, NC y=7.62, NO y=2.54
              + poly((-1.27, 5.08), (3.81, 2.54)) + poly((3.81, 7.62), (5.08, 7.62))
              + poly((3.81, 2.54), (5.08, 2.54)) + poly((-1.27, 5.08), (-2.54, 5.08))
              # pole 2
              + poly((-1.27, -5.08), (3.81, -7.62)) + poly((3.81, -2.54), (5.08, -2.54))
              + poly((3.81, -7.62), (5.08, -7.62)) + poly((-1.27, -5.08), (-2.54, -5.08))
              + poly((0.0, 4.0), (0.0, -4.0), w=0.1524))
SYMS.append(symbol(
    "HFD4", "K", "HFD4/5-SR", "studio_F:Relay_DPDT_Hongfa_HFD4-S_SMD", "design/datasheets/hfd4.pdf",
    "Hongfa HFD4 DPDT signal relay, single-side stable, polarised coil (pin 1 +)",
    relay_body,
    [("1", "+", -5.08, 12.7, 270, "passive"),
     ("8", "-", -5.08, -12.7, 90, "passive"),
     ("3", "COM1", -10.16, 5.08, 0, "passive"),
     ("6", "COM2", -10.16, -5.08, 0, "passive"),
     ("2", "NC1", 10.16, 7.62, 180, "passive"),
     ("4", "NO1", 10.16, 2.54, 180, "passive"),
     ("5", "NO2", 10.16, -2.54, 180, "passive"),
     ("7", "NC2", 10.16, -7.62, 180, "passive")],
    (-7.62, 11.43), (7.62, 11.43), hide_pin_names=True))

# CUI RCJ-01x RCA jack (rcj-014.pdf p.2): pin 2 = centre contact, pin 1 = shell (3 pads).
SYMS.append(symbol(
    "RCJ-01", "J", "RCJ-014", "studio_F:RCA_CUI_RCJ-01_Horizontal", "design/datasheets/rcj-014.pdf",
    "CUI RCJ-01 right-angle RCA jack (pin 2 centre, pin 1 shell)",
    rect(0.0, 2.54, 5.08, -3.81) + circ(2.54, -0.635, 1.27) + circ(2.54, -0.635, 0.381, fill="outline"),
    [("2", "T", -2.54, 0.0, 0, "passive"),
     ("1", "S", -2.54, -2.54, 0, "passive")],
    (0.0, 3.81), (0.0, -5.08)))

# Neutrik NMJ6HCD2 with the pins ordered for this sheet (nmj6hcd2.pdf drawing: T, R, S and the
# normals TN, RN, SN). Pin names match KiCad's Jack_6.35mm_Neutrik_NMJ6HCD2_Horizontal pads.
SYMS.append(symbol(
    "NMJ6HCD2_F", "J", "NMJ6HCD2", "Connector_Audio:Jack_6.35mm_Neutrik_NMJ6HCD2_Horizontal",
    "design/datasheets/nmj6hcd2.pdf", "Neutrik 1/4 in stereo jack, switched (normals TN, RN, SN)",
    rect(0.0, 10.16, 10.16, -15.24) + rect(2.54, 3.81, 7.62, -8.89, fill="none") + text("TRS", 5.08, 6.35),
    [("TN", "TN", -2.54, 7.62, 0), ("RN", "RN", -2.54, 5.08, 0), ("T", "T", -2.54, 0.0, 0),
     ("R", "R", -2.54, -5.08, 0), ("SN", "SN", -2.54, -10.16, 0), ("S", "S", -2.54, -12.7, 0)],
    (0.0, 11.43), (0.0, -16.51), hide_pin_numbers=True))

# Nexperia BAV99 with pins named after the datasheet (bav99.pdf Table 2: 1 = A1, 2 = K2, 3 = K1/A2).
SYMS.append(symbol(
    "BAV99_NXP", "D", "BAV99", "Package_TO_SOT_SMD:SOT-23", "design/datasheets/bav99.pdf",
    "Series switching-diode pair: pin 1 anode end, pin 2 cathode end, pin 3 midpoint",
    (poly((-3.81, 1.27), (-1.27, 0), (-3.81, -1.27), (-3.81, 1.27)) + poly((-1.27, 1.27), (-1.27, -1.27))
     + poly((1.27, 1.27), (3.81, 0), (1.27, -1.27), (1.27, 1.27)) + poly((3.81, 1.27), (3.81, -1.27))
     + poly((-5.08, 0), (5.08, 0), w=0) + poly((0, 0), (0, -2.54), w=0) + circ(0, 0, 0.254, fill="outline")),
    [("1", "A1", -7.62, 0, 0), ("2", "K2", 7.62, 0, 180), ("3", "K1A2", 0, -5.08, 90)],
    (0, 3.81), (0, 2.03), hide_pin_names=True))


# Nexperia BAT54S, same series-pair pinout as BAV99 (bat54s.pdf Table 2: 1 = A1, 2 = K2, 3 = K1/A2).
SYMS.append(symbol(
    "BAT54S_NXP", "D", "BAT54S", "Package_TO_SOT_SMD:SOT-23", "design/datasheets/bat54s.pdf",
    "Series Schottky pair: pin 1 anode end, pin 2 cathode end, pin 3 midpoint",
    (poly((-3.81, 1.27), (-1.27, 0), (-3.81, -1.27), (-3.81, 1.27))
     + poly((-0.762, 1.27), (-1.27, 1.27), (-1.27, -1.27), (-1.778, -1.27))
     + poly((1.27, 1.27), (3.81, 0), (1.27, -1.27), (1.27, 1.27))
     + poly((4.318, 1.27), (3.81, 1.27), (3.81, -1.27), (3.302, -1.27))
     + poly((-5.08, 0), (5.08, 0), w=0) + poly((0, 0), (0, -2.54), w=0) + circ(0, 0, 0.254, fill="outline")),
    [("1", "A1", -7.62, 0, 0), ("2", "K2", 7.62, 0, 180), ("3", "K1A2", 0, -5.08, 90)],
    (0, 3.81), (0, 2.03), hide_pin_names=True))


def write_symbols():
    out = '(kicad_symbol_lib\n\t(version 20241209)\n\t(generator "kicad_symbol_editor")\n\t(generator_version "9.0")\n'
    out += "".join(SYMS) + ")\n"
    (LIB / "studio_F.kicad_sym").write_text(out)


# ------------------------------------------------------------------ footprints

def fp_head(name, descr, tags, attr="smd"):
    return (f'(footprint "{name}"\n\t(version 20241229)\n\t(generator "pcbnew")\n\t(generator_version "9.0")\n'
            f'\t(layer "F.Cu")\n\t(descr "{descr}")\n\t(tags "{tags}")\n'
            f'\t(property "Reference" "REF**" (at 0 -4 0) (layer "F.SilkS") (uuid "{U()}")'
            f' (effects (font (size 1 1) (thickness 0.15))))\n'
            f'\t(property "Value" "{name}" (at 0 4 0) (layer "F.Fab") (uuid "{U()}")'
            f' (effects (font (size 1 1) (thickness 0.15))))\n'
            f'\t(attr {attr})\n')


def line(x1, y1, x2, y2, layer, w=0.12):
    return (f'\t(fp_line (start {x1} {y1}) (end {x2} {y2}) (stroke (width {w}) (type solid))'
            f' (layer "{layer}") (uuid "{U()}"))\n')


def box(x1, y1, x2, y2, layer, w=0.12):
    return (line(x1, y1, x2, y1, layer, w) + line(x2, y1, x2, y2, layer, w)
            + line(x2, y2, x1, y2, layer, w) + line(x1, y2, x1, y1, layer, w))


def smd(num, x, y, w, h, shape="roundrect"):
    rr = " (roundrect_rratio 0.25)" if shape == "roundrect" else ""
    return (f'\t(pad "{num}" smd {shape} (at {x} {y}) (size {w} {h}) (layers "F.Cu" "F.Paste" "F.Mask")'
            f'{rr} (uuid "{U()}"))\n')


def tht(num, x, y, drill, dia):
    return (f'\t(pad "{num}" thru_hole circle (at {x} {y}) (size {dia} {dia}) (drill {drill})'
            f' (layers "*.Cu" "*.Mask") (uuid "{U()}"))\n')


def write_fp(name, body):
    (LIB / "studio_F.pretty" / f"{name}.kicad_mod").write_text(body + ")\n")


def footprints():
    # --- Hongfa HFD4 standard SMT (S): hfd4.pdf p.70 "PCB layout (bottom view)": pads 0.8 x 2.15,
    # columns 3.2 / 2.2 / 2.2, pad centres 6.35 apart across the rows. Mirrored here to a TOP view:
    # pin 1 at +x, top row pins 1-4, bottom row pins 8-5 (pin 8 under pin 1). Body 10 x 6.5.
    xs = {1: 3.8, 2: 0.6, 3: -1.6, 4: -3.8}
    b = fp_head("Relay_DPDT_Hongfa_HFD4-S_SMD",
                "Hongfa HFD4 standard SMT (HFD4/x-S, -SR), 10x6.5 mm, hfd4.pdf p.70 PCB layout mirrored to top view",
                "relay DPDT signal Hongfa HFD4 SMD")
    for n, x in xs.items():
        b += smd(n, x, -3.175, 0.8, 2.15)
        b += smd(9 - n, x, 3.175, 0.8, 2.15)
    b += box(-5.0, -3.25, 5.0, 3.25, "F.Fab", 0.1)
    b += box(-5.11, -1.85, 5.11, 1.85, "F.SilkS")          # body edge between the pad rows
    b += line(5.11, -1.85, 5.11, -2.6, "F.SilkS")           # pin-1 end marker
    b += box(-5.5, -4.5, 5.5, 4.5, "F.CrtYd", 0.05)
    write_fp("Relay_DPDT_Hongfa_HFD4-S_SMD", b)

    # --- CUI RCJ-01 RCA jack: rcj-014.pdf p.2 recommended PCB layout (top view):
    # pin 1 (shell) Ø2.6 at (-5,0), (+5,0), (0,-4.5); pin 2 (centre) Ø1.7 at (0,0).
    # Body front 0.7 beyond the top shell pin; 10.6 wide, 14.5 deep (toward +y here is the plug side).
    b = fp_head("RCA_CUI_RCJ-01_Horizontal",
                "CUI RCJ-01 series right-angle RCA jack, rcj-014.pdf p.2 recommended layout", "RCA phono jack CUI RCJ-01",
                attr="through_hole")
    b += tht(1, -5.0, 0.0, 2.6, 3.6) + tht(1, 5.0, 0.0, 2.6, 3.6) + tht(1, 0.0, -4.5, 2.6, 3.6)
    b += tht(2, 0.0, 0.0, 1.7, 2.6)
    b += box(-5.3, -5.2, 5.3, 9.3, "F.Fab", 0.1)
    b += line(-5.41, 2.0, -5.41, 9.41, "F.SilkS") + line(5.41, 2.0, 5.41, 9.41, "F.SilkS")
    b += line(-5.41, 9.41, 5.41, 9.41, "F.SilkS")
    b += box(-6.0, -6.0, 6.0, 9.8, "F.CrtYd", 0.05)
    write_fp("RCA_CUI_RCJ-01_Horizontal", b)

    # --- TDK T3902 LGA-5: t3902.pdf p.18 Fig.14 land pattern, p.20 bottom view, p.10 top-view pinout.
    # Top view, origin at package centre: pins 1/2 one row, 5/4 the other; ring (pin 3) with the
    # sound hole on the opposite end. Pads 0.522 x 0.725; columns 0.822 apart, rows 1.675 apart,
    # ring centre 1.252 from the inner column, ring Ø1.625 / Ø1.025, sound hole Ø0.8 NPTH (0.5-1.0 rec.).
    b = fp_head("TDK_T3902_LGA-5_3.5x2.65mm",
                "TDK InvenSense T3902 bottom-port PDM MEMS mic, LGA_CAV 3.5x2.65 mm, t3902.pdf Fig.14/16",
                "MEMS microphone PDM bottom port")
    for n, x, y in [(1, 1.364, -0.8375), (2, 0.542, -0.8375), (4, 0.542, 0.8375), (5, 1.364, 0.8375)]:
        b += smd(n, x, y, 0.522, 0.725, shape="rect")
    rc, rm, wr = -0.71, (1.625 + 1.025) / 4, (1.625 - 1.025) / 2      # ring centre x, mid radius, width
    b += (f'\t(pad "3" smd custom (at {rc + rm} 0) (size {wr} {wr}) (layers "F.Cu" "F.Paste" "F.Mask")'
          f' (options (clearance outline) (anchor circle))'
          f' (primitives (gr_circle (center {-rm} 0) (end {-rm + rm} 0) (width {wr}) (fill no)))'
          f' (uuid "{U()}"))\n')
    b += (f'\t(pad "" np_thru_hole circle (at {rc} 0) (size 0.8 0.8) (drill 0.8) (layers "*.Cu" "*.Mask")'
          f' (uuid "{U()}"))\n')
    b += box(-1.75, -1.325, 1.75, 1.325, "F.Fab", 0.1)
    b += line(-1.86, -1.44, 1.86, -1.44, "F.SilkS") + line(-1.86, 1.44, 1.86, 1.44, "F.SilkS")
    b += line(1.86, -1.44, 2.2, -1.44, "F.SilkS")                     # pin-1 corner tick
    b += box(-2.0, -1.6, 2.0, 1.6, "F.CrtYd", 0.05)
    b += f'\t(fp_text user "sound port" (at {rc} 2.2 0) (layer "F.Fab") (uuid "{U()}") (effects (font (size 0.5 0.5) (thickness 0.08))))\n'
    write_fp("TDK_T3902_LGA-5_3.5x2.65mm", b)


if __name__ == "__main__":
    (LIB / "studio_F.pretty").mkdir(exist_ok=True)
    write_symbols()
    footprints()
    print("wrote", LIB / "studio_F.kicad_sym", "and", len(list((LIB / "studio_F.pretty").glob("*.kicad_mod"))), "footprints")
