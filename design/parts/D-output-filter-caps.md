# Output LC filter capacitors and Zobel (per channel: 2 × 700 nF to GND + 10 Ω / 100 nF Zobel)

> **fsw update (block E review, ECP5 −7I grid now 1.695 ns, PLL ×12): baseline fsw = 576 kHz (12 × 48 kHz, 1024 steps); 768 kHz option; 448/512/672 kHz only with E's ×14 bring-up option.** CM ripple 2.08/(8 × 576 kHz × 700 nF) = **0.65 V pp**; attenuation at 2·fsw = 1.152 MHz ≈ −51 dB. f0, Q, Zobel unchanged.

> **fsw update 2026-11-07 (FPGA changed to ECP5, edge grid 1.453 ns = 688.128 Mb/s ODDRX2F, E-fpga-ecp5.md):** baseline fsw is now **448 kHz** (1536 grid steps; 448 kHz = 48 kHz × 28/3, audio-locked but not an integer multiple). 480 kHz is not on the grid. Option per build: 672 kHz (14 × 48 kHz, 1024 steps). CM ripple on each output: 2.68/(8 × 448 kHz × 700 nF) = **1.07 V pp**; differential attenuation at 2·fsw = 896 kHz ≈ −47 dB. f0, Q, Zobel unchanged.

Datasheets: datasheets/grm31c5c2a104.pdf (Murata GRM31C5C2A104JA01_ spec, 1206 C0G 0.1 µF DC100V); datasheets/uniroyal-2512.pdf (Uni-Royal thick-film chip resistor series, incl. 2512 1 W). Read: ratings, dimensions, test methods.

| Function | Part | Qty / channel | Supplier (`show`, 2026-11-07) |
|---|---|---|---|
| Filter cap, each output leg to GND: 7 × 100 nF = 700 nF | Murata GRM31C5C2A104JA01L, 100 nF ±5 % 100 V **C0G** 1206 (T = 1.6 mm) | 14 | `C405303 GRM31C5C2A104JA01L (muRata, 1206): extended, JLC stock 9116, lifecycle normal` |
| Zobel capacitor (across the output, differential) | same GRM31C5C2A104JA01L | 1 | same |
| Zobel resistor 10 Ω: 2 × 20 Ω 1 W 2512 in parallel | Uni-Royal 25121WF200JT4E: 2512, 1 W, F = ±1 %, "200J" = 200 × 10⁻¹ = 20.0 Ω (part-code key, datasheet §2.3–2.4); working voltage 200 V; full power to 70 °C ambient, derated linearly above (§9) | 2 | `C41950 25121WF200JT4E (UNI-ROYAL, 2512): extended, JLC stock 100880, lifecycle normal` |

Per board (2 channels): 30 × GRM31C5C2A104, 4 × 2512. ×5 boards = 150 + 10 % = 165 ≤ 9116 ✓.

## Dielectric choice
**C0G, not X7R or film.** X7R at 24 V DC (the BD idle common-mode level) loses about 50–60 % of its capacitance (cf. the HMK325 curve in D-bridge-decoupling.md), and its capacitance varies *with the audio voltage*. That is a nonlinear filter element, and it adds THD at high frequencies (R-51). X7R is also piezoelectric (audible singing). C0G has no DC-bias or voltage coefficient. SMD film (Panasonic ECWU, WIMA SMD, KEMET LDE) has 0 stock on every LCSC listing checked (`jlc_parts.py search` 2026-11-07). Through-hole MKP would add 4 hand-placed parts per channel. Paralleling 7 × 1206 C0G also gives low ESL and spreads the ripple current.

## Ratings vs worst case
| Parameter | Rating | Worst case | Margin |
|---|---|---|---|
| Voltage (each cap, leg to GND) | 100 V DC | 0–48 V (BD: each output swings between 0 and VBUS) + ≈ 1 V ripple; 55 V firmware cut | 1.8× at 55 V; C0G has no derating. OK |
| Temperature | C0G −55…+125 °C | ≤ 83 °C | OK |
| Ripple current | (not specified; C0G ESR ≈ mΩ) | CM switching ripple 2.5 A pp triangle = 0.72 A rms per side → 0.10 A per cap; audio reactive current at full-scale 20 kHz: 1.49 A rms per side → 0.21 A per cap | negligible self-heating |

## Calculations
### Filter (BTL, BD, symmetric; each leg: L = 10 µH in series, C = 700 nF to GND)
Differential view: 2L = 20 µH in series; the two 700 nF caps in series = 350 nF across the load.
- f0 = 1/(2π√(L·C_side)) = 1/(2π√(10 µH × 700 nF)) = **60.2 kHz**
- Z0 = √(2L/(C_side/2)) = √(20 µH/350 nF) = **7.56 Ω**
- Q = R_load/Z0: **0.53 at 4 Ω**, **1.06 at 8 Ω**, 2.1 at 16 Ω; open load is limited only by the Zobel (below).
- Response (computed with DCR 2.4 mΩ + shunt 5 mΩ per leg): at 20 kHz: −1.51 dB (3.2 Ω), −0.77 dB (4 Ω), +0.49 dB (8 Ω), +0.87 dB (16 Ω). Peak +1.6 dB at 45 kHz in 8 Ω. R-51 says frequency response is "don't care, corrected in DSP"; the 20 kHz spread across loads is ±1.2 dB.
- Attenuation at the BD differential ripple frequency 2·fsw = 960 kHz: **−48 dB**. Common-mode attenuation at fsw (each leg's own LC): also second-order, from 60 kHz.
- Common-mode ripple voltage on each output (idle, worst): ΔV_pp = ΔI_pp/(8·fsw·C) = 2.5 A/(8 × 480 kHz × 700 nF) = **0.93 V pp** at 480 kHz. Inside the cabinet on short speaker leads this is acceptable. R-90 needs common-mode control: a CM choke option is noted for D-interfaces.md as a later variant, not this spin.
- Why 700 nF: Q ≈ 1 into 8 Ω (maximally flat to 20 kHz on the nominal load) and Q ≈ 0.5 into 4 Ω, f0 three times above 20 kHz. It is also the value TI recommends for BD filters with 10 µH (cross-check only; the numbers above stand alone).

### Zobel (10 Ω + 100 nF across the two outputs)
Open load (tweeter disconnected, or the HPF cap's high impedance in the tweeter's stopband): without the Zobel the filter peaks at **+46 dB at 60 kHz**, driven by the noise shaper's out-of-band energy. With 10 Ω + 100 nF: open-load peak **+23 dB at 54 kHz**; other loads change ≤ 0.3 dB at 20 kHz. Larger Zobels (6.8 Ω/220 nF → +16 dB; 4.7 Ω/470 nF → +11 dB) dissipate 5.8 W / 17.5 W at full-scale 20 kHz, too much.
- Zobel dissipation: full-scale (48 V pk diff) sine at 20 kHz: I = 33.9 V / |10 Ω + 1/(j2π·20 kHz·100 nF)| = 33.9/80.2 = 0.42 A → **1.79 W**; at 10 kHz 0.45 W. Music at full scale above 10 kHz is rare; firmware must still limit sustained HF output (block E: an HF power limiter on each channel, ≤ 2 W in the Zobel). The resistor: 2 × 20 Ω 1 W 2512 in parallel = 10 Ω, 2 W at ≤ 70 °C. The board can reach 83 °C (no-panel case), where the linear derating to 155 °C leaves 2 W × (155 − 83)/(155 − 70) = 1.7 W. The 1.79 W at 20 kHz full scale is therefore over that limit, so **firmware must limit Zobel power to ≤ 1 W** (≈ 20 kHz at −2.5 dBFS sustained). Voltage: 33.9 V rms ≪ 200 V ✓.
- Resistor pulse: inductive kick at OCP shutdown is absorbed by the bridge (GaN reverse conduction to VBUS), not the Zobel.

### Noise shaper interaction (for block E)
The noise shaper puts quantisation energy above 20 kHz. The LC filter's f0 (60 kHz) and its Q in each load define how much of that reaches the speaker and the Zobel. E's noise-shaper analysis should use the H(f) curves in this file. Saved numbers: calc script in the reviewer brief.

## Fine print
- Murata GRM31C5C2A104: thickness 1.6 ± 0.2 mm (1206, "C" thickness code). The phase 6 placement needs that height.
- C0G 100 nF 1206 parts are thick and cost more than X7R. Only C0G meets the linearity need.

## Layout guidance
- Caps on the output side of each shunt: inductor → shunt → caps → output connector, so the shunt measures inductor current (D-current-sense.md).
- Spread the 7 caps of each leg along the output trace, with their GND ends on a solid GND pour that returns to the bridge's LS-source / GND region (keeps the CM ripple current local).
- Zobel at the output connector, across OUT+ and OUT−.

## Open questions
None.
