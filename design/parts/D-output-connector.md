# J_WOOF, J_TWT — speaker outputs: 5.08 mm pluggable terminal block, MAX MX2EDGRC-5.08-02P header + MX2EDGK-5.08-02P plug (15 A)

Datasheets (manufacturer drawings, image PDFs, rendered and read): datasheets/max-2edgrc.pdf (CIXI MAIXU MX2EDGRC-5.08-XXP); datasheets/max-2edgk.pdf (MX2EDGK-5.08-XXP). Also read and rejected: datasheets/kangnex-2edgrc.pdf and kangnex-2edgk.pdf (10 A), datasheets/degson-15edgvc.pdf (8 A UL / 7 A IEC), datasheets/degson-2edgrc.pdf (15 A UL, but its 2EDGK plug has 0 stock), datasheets/degson-15edgk.pdf, datasheets/degson-2edgkd.pdf.

| Ref | Part | Supplier (`show`, 2026-11-07) |
|---|---|---|
| J_WOOF, J_TWT (board header, right-angle, closed) | MX2EDGRC-5.08-02P-GN01-Cu-A | `C5188019 MX2EDGRC-5.08-02P-GN01-Cu-A (MAX, Through Hole,Right Angle,P=5.08mm): extended, JLC stock 3266, lifecycle normal` |
| P_WOOF, P_TWT (mating screw plug, shipped loose) | MX2EDGK-5.08-02P-GN01-Cu-Y-A | `C5187912 MX2EDGK-5.08-02P-GN01-Cu-Y-A (MAX, P=5.08mm): extended, JLC stock 4097, lifecycle normal` |
Footprint (MX2EDGRC drawing): pins at 5.08 mm pitch, hole Ø1.70 mm → pad ≈ 2.7 mm; body 11.90 mm deep; pin row 3.28 mm from the body front edge; pins 1.0 mm square. Same pair from one maker, so the mating geometry is guaranteed (R-11 "5.08 mm-pitch 2-pin pluggable terminal block rated ≥ 15 A").

## Ratings vs worst case
| Parameter | Header rating | Plug rating | Our worst case | OK |
|---|---|---|---|---|
| Current | UL 300 V / **15 A**; IEC 320 V / **15 A** (overvoltage cat. III, pollution degree 2, 4 kV impulse) | UL 300 V / 15 A; IEC 320 V / 15 A | continuous 3.5 A rms (R-33a, 46 W into 4 Ω); burst 6.0 A rms at 144 W into 4 Ω (8.5 A pk); peak 12 A (firmware limit), 16 A OCP for < 1 µs | ✓ (continuous ≤ 23 %, burst ≤ 40 %) |
| Voltage | 300 V | 300 V | 48 V pk BTL | ✓ |
| Temperature | −40…+105 °C | −40…+105 °C | 55 °C air + I²R rise (tiny) | ✓ |
| Wire | — | 24–12 AWG (UL); 1.0–2.5 mm² (IEC); M2.5 screw, 0.4 N·m (3.5 lb·in); strip 7–8 mm | speaker wire 1.5–2.5 mm² (16–14 AWG) for 4 Ω at ≤ 0.5 m | ✓ |

Derating note: the 15 A rating is per pin at room temperature by UL/IEC test. Our continuous 3.5 A rms is under a quarter of it, so the ambient derating curve (not in this drawing) is not limiting.

## Silkscreen (LESSONS: connectors labelled with function, polarity and rating)
"WOOFER + −  4–8 Ω" and "TWEETER + −  4–8 Ω (HPF)", pin 1 = +.

## Layout guidance
Board edge, facing inward (R-60). Output pours from the filter caps / Zobel straight to the pins, ≥ 3 mm wide on two layers (nets.csv sets the width). Mechanical: through-hole, so solder both pins fully (R-41).

## Open questions
None.
