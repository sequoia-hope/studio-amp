"""lib_cg.py -- build lib/studio_C.* and lib/studio_G.* (blocks C and G) from the datasheets.

Run from the repo root: python3 hw/satellite/a/gen/lib_cg.py

Every pin number and type below is taken from the datasheet named in the comment
(design/datasheets/), as recorded in the block C/G audits (design/parts/C-*.md, G-*.md).
Pins are arranged by function: inputs/control left, outputs right, supply top,
ground bottom. Stacked pins (same name, same point) are used for multi-pin nets
(TPS2116 VOUT 2/7, TPS7A94 IN 1/2 and OUT 9/10, exposed pads).
"""
from __future__ import annotations

from pathlib import Path

LIB = Path(__file__).resolve().parent.parent / "lib"
P = 2.54


def q(s):
    return '"' + str(s).replace('"', '\\"') + '"'


def fmt(v):
    s = f"{v:.4f}".rstrip("0").rstrip(".")
    return "0" if s in ("-0", "") else s


def pin(name, num, typ, x, y, ang, hide_name=False):
    eff = "(effects (font (size 1.27 1.27)))"
    return (f'\t\t\t(pin {typ} line (at {fmt(x)} {fmt(y)} {ang}) (length 2.54)\n'
            f'\t\t\t\t(name {q(name)} {eff})\n\t\t\t\t(number {q(num)} {eff})\n\t\t\t)\n')


def symbol(name, ref, value, footprint, desc, w, h, pins, graphics="", datasheet="", pin_names=True):
    """pins: list of (name, number, type, side, offset) where side is L/R/T/B and offset is the
    position along that side in mm (y for L/R, x for T/B), library coordinates (y up)."""
    out = [f'\t(symbol {q(name)}\n\t\t(pin_names (offset 1.016){"" if pin_names else " (hide yes)"})\n'
           f'\t\t(exclude_from_sim no)\n\t\t(in_bom yes)\n\t\t(on_board yes)\n']
    props = [("Reference", ref, (-w, h + 1.27), False), ("Value", value, (-w, -h - 1.27), False),
             ("Footprint", footprint, (0, 0), True), ("Datasheet", datasheet, (0, 0), True),
             ("Description", desc, (0, 0), True)]
    for k, v, (x, y), hide in props:
        out.append(f'\t\t(property {q(k)} {q(v)} (at {fmt(x)} {fmt(y)} 0)\n\t\t\t(effects (font (size 1.27 1.27))'
                   f'{" (justify left)" if not hide else ""}{" (hide yes)" if hide else ""})\n\t\t)\n')
    out.append(f'\t\t(symbol {q(name + "_0_1")}\n')
    if w and h:
        out.append(f'\t\t\t(rectangle (start {fmt(-w)} {fmt(h)}) (end {fmt(w)} {fmt(-h)})\n'
                   f'\t\t\t\t(stroke (width 0.254) (type default)) (fill (type background)))\n')
    out.append(graphics)
    out.append('\t\t)\n')
    out.append(f'\t\t(symbol {q(name + "_1_1")}\n')
    for nm, num, typ, side, off in pins:
        if side == "L":
            out.append(pin(nm, num, typ, -w - P, off, 0))
        elif side == "R":
            out.append(pin(nm, num, typ, w + P, off, 180))
        elif side == "T":
            out.append(pin(nm, num, typ, off, h + P, 270))
        else:
            out.append(pin(nm, num, typ, off, -h - P, 90))
    out.append('\t\t)\n\t)\n')
    return "".join(out)


def library(symbols):
    return ('(kicad_symbol_lib\n\t(version 20241209)\n\t(generator "studio_lib_cg")\n\t(generator_version "9.0")\n'
            + "".join(symbols) + ')\n')


# ------------------------------------------------------------------ block C symbols

def coupled_inductor():
    """Two windings 1->3 and 2->4, dots at 1 and 2 (PSSCAQ7048M / SRF0703 'dual inductor' layout:
    the series land joins pads 1+4 and the parallel land joins 1+2 / 3+4, so the windings are 1-3
    and 2-4; Bourns SRF0703 schematic N1 = 1-3, N2 = 2-4, dot = terminal 1)."""
    g = []
    for y in (2.54, -2.54):
        for i in range(4):
            x0 = -2.54 + i * 1.27
            g.append(f'\t\t\t(arc (start {fmt(x0)} {fmt(y)}) (mid {fmt(x0 + 0.635)} {fmt(y + 0.635 if y > 0 else y - 0.635)}) '
                     f'(end {fmt(x0 + 1.27)} {fmt(y)})\n\t\t\t\t(stroke (width 0.254) (type default)) (fill (type none)))\n')
    for y in (1.016, -1.016):
        g.append(f'\t\t\t(polyline (pts (xy -2.54 {fmt(y)}) (xy 2.54 {fmt(y)}))\n'
                 f'\t\t\t\t(stroke (width 0.254) (type default)) (fill (type none)))\n')
    for y in (4.064, -1.016 - 0.508):
        pass
    # dots at the winding starts (pins 1 and 2, left end)
    for y in (3.81, -1.27):
        g.append(f'\t\t\t(circle (center -3.302 {fmt(y)}) (radius 0.3048)\n'
                 f'\t\t\t\t(stroke (width 0) (type default)) (fill (type outline)))\n')
    pins = [("1", "1", "passive", "L", 2.54), ("3", "3", "passive", "R", 2.54),
            ("2", "2", "passive", "L", -2.54), ("4", "4", "passive", "R", -2.54)]
    s = symbol("L_Coupled_13_24", "L", "L_Coupled", "studio_C:L_PROD_PSSCAQ7048",
               "Coupled inductor, 1:1, windings 1-3 and 2-4, dots at 1 and 2", 0, 0, [], "".join(g))
    # body-less symbol: place the pins by hand at the coil ends
    s = s.replace('\t\t(symbol "L_Coupled_13_24_1_1"\n\t\t)\n',
                  '\t\t(symbol "L_Coupled_13_24_1_1"\n'
                  + pin("1", "1", "passive", -5.08, 2.54, 0) + pin("3", "3", "passive", 5.08, 2.54, 180)
                  + pin("2", "2", "passive", -5.08, -2.54, 0) + pin("4", "4", "passive", 5.08, -2.54, 180)
                  + '\t\t)\n')
    s = s.replace('(pin_names (offset 1.016))', '(pin_names (offset 1.016) (hide yes))\n\t\t(pin_numbers (hide yes))')
    return s


def block_c():
    syms = []
    # LM5013 (datasheets/lm5013.pdf Table 6-1): 1 GND, 2 VIN, 3 EN/UVLO, 4 RON, 5 FB, 6 PGOOD,
    # 7 BST, 8 SW, EP no internal connection (tie to GND).
    syms.append(symbol("LM5013", "U", "LM5013", "Package_SO:TI_SO-PowerPAD-8",
                       "100 V 3.5 A non-synchronous COT buck, SO PowerPAD-8 (DDA)", 7.62, 10.16, [
                           ("VIN", "2", "power_in", "L", 5.08), ("EN/UVLO", "3", "input", "L", 0),
                           ("RON", "4", "passive", "L", -5.08),
                           ("BST", "7", "passive", "R", 5.08), ("SW", "8", "power_out", "R", 2.54),
                           ("FB", "5", "input", "R", -2.54), ("PGOOD", "6", "open_collector", "R", -5.08),
                           ("GND", "1", "power_in", "B", -2.54), ("EP", "9", "passive", "B", 0)]))
    # TPS2116 DRL (datasheets/tps2116.pdf Table 5-1): 1 GND, 2/7 VOUT, 3 VIN1, 4 PR1, 5 MODE,
    # 6 VIN2, 8 ST. KiCad's TPS2116DRL omits pin 7.
    syms.append(symbol("TPS2116", "U", "TPS2116", "Package_TO_SOT_SMD:SOT-583-8",
                       "1.6-5.5 V 2.5 A priority power mux, SOT-583 (DRL)", 10.16, 10.16, [
                           ("VIN1", "3", "power_in", "L", 5.08), ("MODE", "5", "input", "L", 2.54),
                           ("PR1", "4", "input", "L", -2.54), ("VIN2", "6", "power_in", "T", 0),
                           ("VOUT", "2", "power_out", "R", 5.08), ("VOUT", "7", "passive", "R", 5.08),
                           ("ST", "8", "open_collector", "R", -5.08),
                           ("GND", "1", "power_in", "B", 0)]))
    # LM5017 DDA (datasheets/lm5017.pdf pin functions): 1 RTN, 2 VIN, 3 UVLO, 4 RON, 5 FB, 6 VCC,
    # 7 BST, 8 SW, EP (9) RTN. Same layout as KiCad's LM5017MR, whose pin 3 is misspelt "ULVO".
    syms.append(symbol("LM5017", "U", "LM5017", "Package_SO:TI_SO-PowerPAD-8",
                       "100 V 600 mA constant-on-time synchronous buck, SO PowerPAD-8 (DDA)", 7.62, 10.16, [
                           ("VIN", "2", "power_in", "L", 5.08), ("RON", "4", "input", "L", 2.54),
                           ("UVLO", "3", "input", "L", -2.54),
                           ("BST", "7", "input", "R", 5.08), ("SW", "8", "output", "R", 2.54),
                           ("FB", "5", "input", "R", -2.54), ("VCC", "6", "output", "R", -7.62),
                           ("RTN", "1", "power_in", "B", -2.54), ("RTNPAD", "9", "power_in", "B", 0)]))
    # TPS62A02A PDDC (datasheets/tps62a02a.pdf Table 5-1, SOT23-6): 1 EN, 2 GND, 3 SW, 4 VIN,
    # 5 PG, 6 FB. Thin SOT-23-6 (review): TSOT-23-6.
    syms.append(symbol("TPS62A02A", "U", "TPS62A02A", "Package_TO_SOT_SMD:TSOT-23-6",
                       "2 A 2.4 MHz forced-PWM buck with power good, TSOT-23-6 (DDC)", 5.08, 7.62, [
                           ("VIN", "4", "power_in", "L", 2.54), ("EN", "1", "input", "L", -2.54),
                           ("SW", "3", "power_out", "R", 2.54), ("FB", "6", "input", "R", 0),
                           ("PG", "5", "open_collector", "R", -2.54),
                           ("GND", "2", "power_in", "B", 0)]))
    # TPS7A94 DSC (datasheets/tps7a94.pdf pin diagram): 1-2 IN, 3 EN_UV, 4 PG, 5 FB_PG, 6 GND,
    # 7 NR/SS, 8 SNS, 9-10 OUT, thermal pad (11) to GND.
    syms.append(symbol("TPS7A94", "U", "TPS7A9401", "Package_SON:Texas_DSC0010J",
                       "1 A ultra-low-noise LDO, VOUT = 150 uA x R(NR/SS), WSON-10 (DSC)", 7.62, 10.16, [
                           ("IN", "1", "power_in", "L", 5.08), ("IN", "2", "passive", "L", 5.08),
                           ("EN_UV", "3", "input", "L", 0), ("NR/SS", "7", "passive", "L", -5.08),
                           ("OUT", "10", "power_out", "R", 5.08), ("OUT", "9", "passive", "R", 5.08),
                           ("SNS", "8", "input", "R", 2.54), ("FB_PG", "5", "input", "R", -2.54),
                           ("PG", "4", "open_collector", "R", -5.08),
                           ("GND", "6", "power_in", "B", -2.54), ("EP", "11", "passive", "B", 0)]))
    # TPS7A49 / TPS7A30 DGN (datasheets/tps7a49.pdf, tps7a30.pdf pin tables): 1 OUT, 2 FB, 3 NC,
    # 4 GND, 5 EN, 6 NR/SS, 7 DNC, 8 IN, PowerPAD (9) to GND.
    for nm, desc in (("TPS7A4901", "+36 V 150 mA ultra-low-noise positive LDO, adjustable, HVSSOP-8 (DGN)"),
                     ("TPS7A3001", "-36 V 200 mA ultra-low-noise negative LDO, adjustable, HVSSOP-8 (DGN)")):
        syms.append(symbol(nm, "U", nm, "Package_SO:HVSSOP-8-1EP_3x3mm_P0.65mm_EP1.57x1.89mm", desc, 7.62, 7.62, [
            ("IN", "8", "power_in", "L", 2.54), ("EN", "5", "input", "L", 0), ("NR/SS", "6", "passive", "L", -2.54),
            ("OUT", "1", "power_out", "R", 2.54), ("FB", "2", "input", "R", 0),
            ("NC", "3", "no_connect", "T", -2.54), ("DNC", "7", "no_connect", "T", 2.54),
            ("GND", "4", "power_in", "B", -2.54), ("EP", "9", "passive", "B", 0)]))
    # TPS7A20xxP DBV (datasheets/tps7a20.pdf pin functions, SOT-23): 1 IN, 2 GND, 3 EN, 4 N/C, 5 OUT.
    syms.append(symbol("TPS7A20", "U", "TPS7A2033P", "Package_TO_SOT_SMD:SOT-23-5",
                       "300 mA low-noise fixed LDO with active discharge, SOT-23-5 (DBV)", 5.08, 5.08, [
                           ("IN", "1", "power_in", "L", 1.27), ("EN", "3", "input", "L", -1.27),
                           ("OUT", "5", "power_out", "R", 1.27), ("NC", "4", "no_connect", "T", 0),
                           ("GND", "2", "power_in", "B", 0)]))
    # TLV6703 DDC (datasheets/tlv6703.pdf pin functions): 1 OUT, 2/4/6 GND, 3 SENSE, 5 VDD.
    syms.append(symbol("TLV6703", "U", "TLV6703", "Package_TO_SOT_SMD:TSOT-23-6",
                       "18 V comparator with 400 mV reference, open-drain, TSOT-23-6 (DDC)", 7.62, 7.62, [
                           ("SENSE", "3", "input", "L", 0), ("OUT", "1", "open_collector", "R", 0),
                           ("VDD", "5", "power_in", "T", 0),
                           ("GND", "2", "power_in", "B", 0), ("GND", "4", "passive", "B", 0),
                           ("GND", "6", "passive", "B", 0)]))
    # SS5P10 TO-277A (datasheets/vishay-ss5p10.pdf: pins 1, 2 anode, tab cathode K):
    # KiCad TO-277A pads 1, 2 and 3 (tab).
    g = ('\t\t\t(polyline (pts (xy -1.27 1.27) (xy -1.27 -1.27) (xy 1.27 0) (xy -1.27 1.27))\n'
         '\t\t\t\t(stroke (width 0.254) (type default)) (fill (type none)))\n'
         '\t\t\t(polyline (pts (xy 1.778 1.016) (xy 1.27 1.27) (xy 1.27 -1.27) (xy 0.762 -1.016))\n'
         '\t\t\t\t(stroke (width 0.254) (type default)) (fill (type none)))\n'
         '\t\t\t(polyline (pts (xy -2.54 0) (xy 2.54 0))\n\t\t\t\t(stroke (width 0) (type default)) (fill (type none)))\n')
    s = symbol("D_Schottky_TO277A", "D", "SS5P10", "Package_TO_SOT_SMD:TO-277A",
               "Schottky diode, TO-277A: pins 1, 2 anode, tab (3) cathode", 0, 0, [], g)
    s = s.replace('\t\t(symbol "D_Schottky_TO277A_1_1"\n\t\t)\n',
                  '\t\t(symbol "D_Schottky_TO277A_1_1"\n'
                  + pin("A", "1", "passive", -5.08, 0, 0) + pin("A", "2", "passive", -5.08, 0, 0)
                  + pin("K", "3", "passive", 5.08, 0, 180) + '\t\t)\n')
    s = s.replace('(pin_names (offset 1.016))', '(pin_names (offset 1.016) (hide yes))\n\t\t(pin_numbers (hide yes))')
    syms.append(s)
    syms.append(coupled_inductor())
    return syms


# ------------------------------------------------------------------ block G symbols

def block_g():
    syms = []
    # TCA9617B DGK (datasheets/tca9617b.pdf pin table): 1 VCCA, 2 SCLA, 3 SDAA, 4 GND, 5 EN,
    # 6 SDAB, 7 SCLB, 8 VCCB.
    syms.append(symbol("TCA9617B", "U", "TCA9617B", "Package_SO:VSSOP-8_3x3mm_P0.65mm",
                       "Level-translating FM+ I2C repeater, VSSOP-8 (DGK)", 7.62, 10.16, [
                           ("SCLA", "2", "bidirectional", "L", 2.54), ("SDAA", "3", "bidirectional", "L", 0),
                           ("EN", "5", "input", "L", -2.54),
                           ("SCLB", "7", "bidirectional", "R", 2.54), ("SDAB", "6", "bidirectional", "R", 0),
                           ("VCCA", "1", "power_in", "T", -2.54), ("VCCB", "8", "power_in", "T", 2.54),
                           ("GND", "4", "power_in", "B", 0)]))
    # TPS2553 DBV (datasheets/tps2553.pdf pin table, DBV column): 1 IN, 2 GND, 3 EN (active high),
    # 4 FAULT (active low, open drain), 5 ILIM, 6 OUT.
    syms.append(symbol("TPS2553", "U", "TPS2553", "Package_TO_SOT_SMD:SOT-23-6",
                       "Adjustable current-limited power switch, active-high EN, SOT-23-6 (DBV)", 7.62, 10.16, [
                           ("IN", "1", "power_in", "L", 2.54), ("EN", "3", "input", "L", -2.54),
                           ("OUT", "6", "power_out", "R", 2.54), ("~{FAULT}", "4", "open_collector", "R", -2.54),
                           ("GND", "2", "power_in", "B", -2.54), ("ILIM", "5", "passive", "B", 2.54)]))
    # TPS2553 DRV (same pin table, DRV column): 1 OUT, 2 ILIM, 3 FAULT, 4 EN, 5 GND, 6 IN; the
    # thermal pad (p. 32, 1.0 x 1.6 mm) is soldered to GND: pad 7 stacked on GND. 2x2 mm SON,
    # P0.65 (p. 31) = KiCad WSON-6-1EP_2x2mm_P0.65mm_EP1x1.6mm.
    syms.append(symbol("TPS2553DRV", "U", "TPS2553", "Package_SON:WSON-6-1EP_2x2mm_P0.65mm_EP1x1.6mm",
                       "Adjustable current-limited power switch, active-high EN, SON-6 2x2 (DRV)", 7.62, 10.16, [
                           ("IN", "6", "power_in", "L", 2.54), ("EN", "4", "input", "L", -2.54),
                           ("OUT", "1", "power_out", "R", 2.54), ("~{FAULT}", "3", "open_collector", "R", -2.54),
                           ("GND", "5", "power_in", "B", -2.54), ("GND", "7", "passive", "B", -2.54),
                           ("ILIM", "2", "passive", "B", 2.54)]))
    # Connectors drawn by function (the footprint keeps the physical pad numbers):
    # LED output, JST PH 4 (R-19 order 1 +5V, 2 GND, 3 D, 4 C)
    syms.append(symbol("Conn_LED_PH4", "J", "JST PH 4P", "Connector_JST:JST_PH_B4B-PH-K_1x04_P2.00mm_Vertical",
                       "Addressable-LED output connector, pins by function", 5.08, 3.81, [
                           ("+5V", "1", "passive", "L", 2.54), ("D", "3", "passive", "L", 0),
                           ("C", "4", "passive", "L", -2.54), ("GND", "2", "passive", "B", 0)]))
    # Knob / encoder 2x6 header (G-knob.md pin table); +3V3 (11) on top, GND (2, 12) at the bottom
    syms.append(symbol("Conn_Knob_2x6", "J", "2x6 header 2.54",
                       "Connector_PinHeader_2.54mm:PinHeader_2x06_P2.54mm_Vertical",
                       "Knob / encoder header, pins by function", 7.62, 17.78, [
                           ("KNOB_REF", "1", "passive", "R", 10.16), ("KNOB1", "3", "passive", "R", 7.62),
                           ("KNOB2", "4", "passive", "R", 5.08), ("KNOB3", "5", "passive", "R", 2.54),
                           ("KNOB4", "6", "passive", "R", 0), ("ENC1_A", "7", "passive", "R", -2.54),
                           ("ENC1_B", "8", "passive", "R", -5.08), ("ENC2_A", "9", "passive", "R", -7.62),
                           ("ENC2_B", "10", "passive", "R", -10.16), ("+3V3", "11", "passive", "T", 0),
                           ("GND", "2", "passive", "B", -2.54), ("GND", "12", "passive", "B", 2.54)]))
    return syms


# ------------------------------------------------------------------ footprints

def fp_two_pad(name, descr, pad_w, pad_h, cx, body_w, body_h, tags):
    """Two-terminal SMD power inductor: pads 1 (left) and 2 (right) at x = -cx / +cx."""
    crt_w, crt_h = max(body_w, 2 * cx + pad_w) / 2 + 0.25, max(body_h, pad_h) / 2 + 0.25
    return f'''(footprint "{name}"
	(version 20241229)
	(generator "studio_lib_cg")
	(layer "F.Cu")
	(descr "{descr}")
	(tags "{tags}")
	(attr smd)
	(property "Reference" "REF**" (at 0 {fmt(-body_h / 2 - 1.5)} 0) (layer "F.SilkS") (effects (font (size 1 1) (thickness 0.15))))
	(property "Value" "{name}" (at 0 {fmt(body_h / 2 + 1.5)} 0) (layer "F.Fab") (effects (font (size 1 1) (thickness 0.15))))
	(fp_rect (start {fmt(-body_w / 2)} {fmt(-body_h / 2)}) (end {fmt(body_w / 2)} {fmt(body_h / 2)}) (stroke (width 0.1) (type solid)) (fill no) (layer "F.Fab"))
	(fp_rect (start {fmt(-crt_w)} {fmt(-crt_h)}) (end {fmt(crt_w)} {fmt(crt_h)}) (stroke (width 0.05) (type solid)) (fill no) (layer "F.CrtYd"))
	(fp_line (start {fmt(-body_w / 2 - 0.12)} {fmt(-body_h / 2 - 0.12)}) (end {fmt(body_w / 2 + 0.12)} {fmt(-body_h / 2 - 0.12)}) (stroke (width 0.12) (type solid)) (layer "F.SilkS"))
	(fp_line (start {fmt(-body_w / 2 - 0.12)} {fmt(body_h / 2 + 0.12)}) (end {fmt(body_w / 2 + 0.12)} {fmt(body_h / 2 + 0.12)}) (stroke (width 0.12) (type solid)) (layer "F.SilkS"))
	(pad "1" smd rect (at {fmt(-cx)} 0) (size {fmt(pad_w)} {fmt(pad_h)}) (layers "F.Cu" "F.Paste" "F.Mask"))
	(pad "2" smd rect (at {fmt(cx)} 0) (size {fmt(pad_w)} {fmt(pad_h)}) (layers "F.Cu" "F.Paste" "F.Mask"))
)
'''


def fp_coupled():
    """PROD PSSCAQ7048M / Bourns SRF0703 'dual inductor' land (datasheets/prod-psscaq7048m.pdf p.4,
    bourns-srf0703.pdf 'Recommended Layout'): four 1.4 x 3.0 mm pads, column pitch 1.8 mm,
    row pitch 4.9 mm (7.9 mm outer). Pads 1 2 on top, 4 3 below; body 7.6 x 7.6 mm."""
    pads = [("1", -0.9, -2.45), ("2", 0.9, -2.45), ("3", 0.9, 2.45), ("4", -0.9, 2.45)]
    body = 7.6
    p = "".join(f'\t(pad "{n}" smd rect (at {fmt(x)} {fmt(y)}) (size 1.4 3) (layers "F.Cu" "F.Paste" "F.Mask"))\n'
                for n, x, y in pads)
    return f'''(footprint "L_PROD_PSSCAQ7048"
	(version 20241229)
	(generator "studio_lib_cg")
	(layer "F.Cu")
	(descr "Coupled inductor 7.6x7.6 mm, PROD Tech PSSCAQ7048M / Bourns SRF0703 dual-inductor land (pads 1.4x3.0, 1.8 x 4.9 mm pitch); windings 1-3 and 2-4")
	(tags "coupled inductor dual inductor PSSCAQ7048 SRF0703")
	(attr smd)
	(property "Reference" "REF**" (at 0 -5 0) (layer "F.SilkS") (effects (font (size 1 1) (thickness 0.15))))
	(property "Value" "L_PROD_PSSCAQ7048" (at 0 5 0) (layer "F.Fab") (effects (font (size 1 1) (thickness 0.15))))
	(fp_rect (start -3.8 -3.8) (end 3.8 3.8) (stroke (width 0.1) (type solid)) (fill no) (layer "F.Fab"))
	(fp_rect (start -4.05 -4.2) (end 4.05 4.2) (stroke (width 0.05) (type solid)) (fill no) (layer "F.CrtYd"))
	(fp_rect (start -3.92 -3.92) (end 3.92 3.92) (stroke (width 0.12) (type solid)) (fill no) (layer "F.SilkS"))
	(fp_circle (center -2.6 -4.4) (end -2.45 -4.4) (stroke (width 0.3) (type solid)) (fill yes) (layer "F.SilkS"))
{p})
'''


def main():
    (LIB / "studio_C.kicad_sym").write_text(library(block_c()), encoding="utf-8")
    (LIB / "studio_G.kicad_sym").write_text(library(block_g()), encoding="utf-8")
    pc = LIB / "studio_C.pretty"
    # Bourns SRP1265A (datasheets/bourns-srp1265a.pdf 'Recommended Layout'): 14.2 mm outer, 8.0 mm
    # inner, 5.0 mm tall -> pads 3.1 x 5.0 at +-5.55 mm; body 13.5 x 12.5 mm.
    (pc / "L_Bourns_SRP1265A.kicad_mod").write_text(fp_two_pad(
        "L_Bourns_SRP1265A", "Bourns SRP1265A shielded power inductor 13.5x12.5 mm (datasheet recommended layout: 14.2 outer, 8.0 inner, 5.0 tall)",
        3.1, 5.0, 5.55, 13.5, 12.5, "inductor Bourns SRP1265A"))
    # Bourns SRP4020TA (datasheets/bourns-srp4020ta.pdf 'Recommended Layout'): 5.2 outer, 2.2 inner,
    # 2.4 tall -> pads 1.5 x 2.4 at +-1.85 mm; body 4.45 x 4.06 mm.
    (pc / "L_Bourns_SRP4020TA.kicad_mod").write_text(fp_two_pad(
        "L_Bourns_SRP4020TA", "Bourns SRP4020TA shielded power inductor 4.45x4.06 mm (datasheet recommended layout: 5.2 outer, 2.2 inner, 2.4 tall)",
        1.5, 2.4, 1.85, 4.45, 4.06, "inductor Bourns SRP4020TA"))
    (pc / "L_PROD_PSSCAQ7048.kicad_mod").write_text(fp_coupled(), encoding="utf-8")
    print("wrote studio_C / studio_G symbols and footprints")


if __name__ == "__main__":
    main()
