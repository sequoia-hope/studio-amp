# L (×4) — output filter inductor: Coilcraft SER2915H-103KL (10 µH ±10 %, ferrite)

> **fsw update 2026-11-07 (FPGA changed to ECP5, edge grid 1.453 ns = 688.128 Mb/s ODDRX2F, E-fpga-ecp5.md):** baseline fsw is now **448 kHz** (1536 grid steps; 448 kHz = 48 kHz × 28/3, audio-locked but not an integer multiple). 480 kHz is not on the grid. Option per build: 672 kHz (14 × 48 kHz, 1024 steps). Ripple at 448 kHz: 48 × 0.25/(10 µH × 448 kHz) = **2.68 A pp**; legitimate peak 12 + 1.34 = 13.3 A (trip 14.9 A unchanged).

Datasheet: datasheets/ser2915h.pdf (Coilcraft Doc 644-1/644-2, revised 09/04/26). Read: all (spec table, notes 1–7, dimensions and land pattern p.2).
MPN: SER2915H-103KL. Supplier: `C19276042 SER2915H-103KL (Coilcraft, SMD,27.9x19.8mm): extended, JLC stock 63, lifecycle normal, checked 2026-11-07`. Build need 4 × 5 + 2 = 22 ≤ 63 ✓.
Footprint: Coilcraft recommended land pattern (p.2): two terminal pads plus a **third pad "for mounting stability only"** (pad 3, no net; tie it to an unconnected copper island, not to a signal). Body 27.9 × 19.8 mm max, height 15.36 mm max (SER2915H). Weight 29.7 g.

Alternate (electrically equivalent, smaller, not footprint-compatible): Coilcraft **XAL1510-103MED**, `C3911782 XAL1510-103MED (Coilcraft, SMD,15.2x16.2mm): extended, JLC stock 191, lifecycle normal, checked 2026-11-07`; datasheets/xal1510.pdf (Doc 947, revised 05/04/26), read in full.

## Selection
| | SER2915H-103KL (chosen) | XAL1510-103ME | rejected |
|---|---|---|---|
| L | 10 µH ±10 % | 10 µH ±20 % | PA4342.103 (Pulse): Isat 12 A at −30 % < 15 A trip |
| Core | ferrite (gapped) | composite (powder) | FXL1360-100-M (cjiang): Isat 11.1/12.5 A < 15 A |
| L vs I | flat: −10 % at 18 A, −20 % at 21.5 A, −30 % at 23.4 A | soft: from p.2 graph, 9.2 µH at 12 A (−8 %), 8.9 µH at 15 A (−11 %), 8.6 µH at 18 A | FEXL1513A-100M, MDA1870-100M: powder cores; their datasheets publish no core-loss data at 480 kHz |
| DCR | 1.86 mΩ nom / 2.05 max | 6.80 / 9.00 mΩ | |
| Irms (20 °C / 40 °C rise) | 20 A / 30 A | 16 A / 22 A | |
| Ambient rating | −40…+85 °C with 40 °C rise; part max 125 °C | −40…+125 °C; part max 165 °C | |
| Size | 27.9 × 19.8 × 15.4 mm, 30 g | 15.2 × 16.2 × ~10 mm, 12–15 g | |

Chosen SER2915H for **inductance linearity** (R-51 open-loop THD: a flat L means the filter does not modulate with the signal current), **5× lower DCR**, and ferrite's low core loss at 480 kHz. Cost: board area. Four of them take about 22 cm², which phase 4 must accept. If the floorplan cannot, XAL1510-103 is the drop-in electrical alternative with a new footprint.

## Ratings vs worst case
| Parameter | Rating | Worst case | Margin |
|---|---|---|---|
| Isat (−10 %) | 18 A | 16 A: 15 A OCP trip plus 0.95 A overshoot during the ≤ 193 ns trip delay at 4.9 A/µs (output shorted to GND, 48 V across 9.8 µH) | 2 A; L is still ≥ 90 % at the trip point, so dI/dt stays bounded |
| Isat (−30 %) | 23.4 A | — | ≫ |
| Irms (20 °C rise) | 20 A | 6.0 A rms at the 144 W / 4 Ω burst; 3.5 A rms continuous (46 W / 4 Ω) | OK |
| Ambient | 85 °C with a 40 °C rise; part ≤ 125 °C | air 55 °C + self-heating < 5 °C + board 10–30 °C | OK |
| Voltage | not stated for SER2900 (ferrite, enamelled flat wire) | ≤ 48 V across the winding | standard for this class |

## Calculations
### Ripple and peak current (fsw 480 kHz, VBUS 48 V)
ΔI_pp = VBUS·D(1−D)/(L·fsw), at most at D = 0.5: 48 × 0.25 / (10 µH × 480 kHz) = **2.50 A pp** (±1.25 A).
With L at −10 % tolerance (9 µH): 2.78 A pp. At fsw 1 MHz: 1.20 A pp.
Peak at the firmware limit (12 A load peak): 12 + 1.39 = **13.4 A** < the 15 A trip ✓ (the trip does not chatter at full legitimate current).

### Copper loss (DCR 2.05 mΩ max × 1.3 for Cu at about +80 °C)
| Case | I_rms (load + ripple) | P_DCR |
|---|---|---|
| idle | 0.72 A | 1 mW |
| 46 W / 4 Ω | 3.47 A | 32 mW |
| 144 W / 4 Ω | 6.04 A | 97 mW |
AC (proximity) loss from the 2.5 A pp ripple at 480 kHz is not given in the datasheet.

### Core loss
**Not computable from the datasheet.** Coilcraft publishes core and winding loss only through its online calculator ("See www.coilcraft.com/coreloss"), which needs interactive use. Placeholder in the power budget: **0.2 W per inductor (0.8 W per board)** at 480 kHz, 2.5 A pp. Action: run the Coilcraft calculator for SER2915H-103 and XAL1510-103 at 480 kHz, 2.5 A pp ripple, 0 / 3.5 / 6 A DC, and replace the placeholder (open question 1).

### Filter values
See D-output-filter-caps.md: with 700 nF per side to GND, f0 = 60.2 kHz, Z0 = 7.56 Ω, Q = 0.53 (4 Ω) / 1.06 (8 Ω).

### Thermal
Self-heating at the continuous case ≈ 32 mW DCR + core placeholder 0.2 W. The 20 °C-rise rating is at 20 A, so self-heating is a few °C. An NTC next to each channel's inductor pair (D-ntc.md); firmware over-temperature limit 110 °C board, against the 125 °C part maximum.

## Fine print
- Note 5: Isat is "DC current at 25 °C"; "Click for temperature derating information". The temperature derating is published only on Coilcraft's web page, not in this PDF. Ferrite saturation current falls with temperature, and the size of the fall must be read from that page before phase 2 (open question 3). At 25 °C, the trip current (16 A) is below the −10 % point (18 A), and the −30 % point (23.4 A) leaves room for the hot case.
- Note 6: Irms "is for reference only … highly dependent on … pcb land pattern, trace size" → wide pours.
- Mechanical (R-41 vibration): 30 g part on a loudspeaker back panel. Solder all three pads (the third is mechanical) and add adhesive (a phase 4 note).
- Ferrite with an air gap: the gap's fringing field radiates. Keep the gap side away from sensitive analog (phase 6).

## Layout guidance
- Each leg: switch node (FET pair) → L → shunt (D-current-sense.md) → filter caps → output. The switch-node copper from the FETs to L must be **short and small in area** (dV/dt node, EMI).
- The inductor pairs of one channel are placed side by side with opposite winding direction if the orientation marking allows (CM/DM field cancellation, R-90).

## Open questions
1. Core and AC winding loss from the Coilcraft calculator (above). If it exceeds 0.4 W per part, re-check against XAL1510.
2. Phase 4 must confirm area for 4 × SER2915H. Otherwise switch to XAL1510-103MED (stock 191).
3. Isat temperature derating (Coilcraft web data) at 85 °C part temperature: confirm that L(16 A, 85 °C) ≥ 7 µH. If not, lower the trip to about 14 A (still above the 13.4 A legitimate peak).
