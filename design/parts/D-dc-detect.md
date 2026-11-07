# DC-at-output detection (per channel): RC-filtered dividers + LMV393 window → fault latch (R-54: all four FETs off, no relay, ≤ 100 ms)

Datasheets: datasheets/lmv393.pdf (TI LMV331/LMV393/LMV339; read: all electrical tables, both supply columns); datasheets/uniroyal-0402wgf.pdf (0603 thick-film series, 75 V working); datasheets/cl10a225ko8.pdf (Samsung CL series MLCC).

| Ref (per channel) | Part | Qty/ch | Supplier (`show`, 2026-11-07) |
|---|---|---|---|
| U_DC | TI LMV393IDR dual comparator, open-drain, SOIC-8 | 1 | `C7984 LMV393IDR (TI, SOIC-8): extended, JLC stock 11884, lifecycle normal` |
| R_top | 2.2 MΩ 1 % 0603 (Uni-Royal 0603WAF2204T5E) | 4 | `C22938 0603WAF2204T5E` (preferred, 191k in stock, search 2026-11-07) |
| R_bot (plain nodes) | 100 kΩ 1 % 0603 (0603WAF1003T5E) | 2 | `C25803` (basic, 16.2 M in stock) |
| R_bot' (offset nodes) | 110 kΩ 1 % 0603 | 2 | Uni-Royal 0603WAF1103T5E (same family; LCSC number fixed in phase 2) |
| R_off | 1.21 MΩ 1 % 0603 | 2 | Uni-Royal 0603WAF1214T5E (same family) |
| C_f | 2.2 µF 16 V X5R 0603, CL10A225KO8NNNC | 4 | `C23630` (basic) |
| R_PU_DC | 10 kΩ pull-up on DC_n to +3V3 | 1 | C25744 |

Signal tap: the post-filter outputs OUT_P / OUT_N on the **bridge side** of the tweeter HPF cap (for the woofer, at the connector). That detects a DC fault of the bridge itself.

## Approach
Hardware net, independent of the FPGA and firmware: each output is divided by about 23 and low-pass filtered (τ ≈ 0.21 s). Two comparators test (OUT_P − OUT_N) > +6 V and (OUT_N − OUT_P) > +6 V after filtering. Their open-drain outputs form **DC_n** (to the FPGA, and through a BAT46WJ into the channel's FAULT_RAW_n, D-ocp-logic.md), which clears the latch, so EN goes low and all four FETs turn off.
On top of this, gateware runs a finer, faster detector on the I-sense ADC data: mean current over 50 ms above about 1 A → shutdown (block E, D-interfaces.md). The hardware path guarantees R-54 even if the gateware is wrong.
Why no relay works: with all four gates off, a single shorted FET cannot sustain DC. The loop through the shorted FET, the speaker and the other leg's FETs reverse-conducting returns to the same rail, with no driving voltage (checked for HS and LS shorts on either leg).

## Network (per output, two copies: a plain node and an offset node)
- **Plain node** (OUT_x_f): R_top 2.2 MΩ from OUT_x, R_bot 100 kΩ to GND, C_f 2.2 µF to GND. Gain = 100k/(2.2M + 100k) = 1/23.0 = 0.04348; R_th = 2.2M ∥ 100k = 95.65 kΩ; τ = 95.65 kΩ × 2.2 µF = 0.210 s.
- **Offset node** (OUT_x_f+): R_top 2.2 MΩ from OUT_x, R_bot' 110 kΩ to GND, R_off 1.21 MΩ to 3V3_A, C_f 2.2 µF. G_total = 1/2.2M + 1/110k + 1/1.21M = 10.372 µS → R_th = 96.41 kΩ (τ = 0.212 s, matched to the plain node). Gain = 96.41k/2.2M = 0.04382 (+0.8 % vs plain). Offset = 3.3 V × 96.41k/1.21M = **0.263 V = 6.0 V referred to the output**.
- Comparator A: IN− = OUT_P_f, IN+ = OUT_N_f+ → output released (OK) while OUT_P_f < OUT_N_f + 0.263 V, i.e. (P − N) < 6.0 V. Comparator B is the mirror image (N vs P).
- CM error from the 0.8 % gain mismatch at the BD idle CM of 24 V: 24 × (0.04382 − 0.04348) = 8 mV → 0.2 V of threshold shift. LMV393 VIO 7 mV max → ±0.16 V. Resistor 1 % → ±0.2 V. **Threshold 6.0 ± 0.6 V differential DC.**

## Ratings vs worst case
| Parameter | Rating | Worst case | OK |
|---|---|---|---|
| LMV393 VCC | 2.7–5.5 V | +3V3 | ✓ |
| LMV393 input range | abs: 0…VCC; VICR −0.1…2.0 V at 2.7 V (p.5), so ≈ −0.1…2.6 V at 3.3 V | plain node 0…48/23 = 2.09 V; offset node ≤ 2.09 × 1.008 + 0.263 = 2.37 V; TVS event 87 V → 3.8 V for ≪ τ, filtered | ✓ (normal); at a clamp event the RC filter keeps the node ≪ 3.3 V over a ms-scale transient |
| LMV393 VID | ±5.5 V | ≤ 2.4 V | ✓ |
| Output | open drain; VSAT 150 mV at 1.5 mA | 10 kΩ pull-up: 0.33 mA | ✓ |
| R_top 0603 voltage | 75 V working (Uni-Royal 0603) | 48 V (87 V transient) | ✓ (transient brief) |
| C_f voltage | 16 V | ≤ 2.4 V | ✓ |

## Calculations: trip time and AC rejection
Filtered differential = (V_DC/23)·(1 − e^(−t/τ)); trip when it reaches 0.263 V → t = −τ·ln(1 − 6.0/V_DC):
| DC at output (differential) | Trip time |
|---|---|
| 48 V (one leg stuck at a rail) | 0.21 × −ln(0.875) = **28 ms** |
| 24 V | **60 ms** |
| 18 V | 85 ms |
| 12 V | 146 ms (gateware detector covers this faster) |
| < 6 V | no hardware trip (woofer dissipation ≤ 6²/3.2 Ω = 11 W; the gateware detector trips at about 1 A) |
R-54 ≤ 100 ms is met in hardware for |DC| ≥ 17 V and by the gateware path for smaller DC.

AC rejection: a full-scale (48 V pk differential) sine at f gives a filtered peak of (48/23)/√(1 + (2πfτ)²): 20 Hz → **0.079 V** (30 % of threshold) ✓; 10 Hz → 0.16 V ✓; 5 Hz → 0.31 V ✗ (would trip). **Block E: subsonic high-pass in DSP on both channels at ≥ 15 Hz** (the woofer cannot use < 15 Hz anyway; tweeter content is HF).
Leakage: C_f X5R insulation ≥ 100 MΩ·µF/2.2 µF ≈ 45 MΩ → 44 nA at 2 V, against 20 µA divider current → 0.2 % ✓. LMV393 input bias is nA-level (p.5) ✓.
Supply: LMV393 ≤ 140 µA per package (both comparators) ✓.

## Fine print
- LMV393 inputs must not go below −0.1 V. OUT_x ≥ 0 V always, except for dead-time undershoot, which the LC filter removes.
- Propagation 0.5–1 µs (p.5/6): irrelevant here.

## Layout guidance
Dividers at the output-filter caps; the high-impedance filtered nodes are short and kept away from the switch nodes and inductors (they are 96 kΩ nodes). LMV393 near the channel's fault logic.

## Open questions
None. The network is ready for a phase 8 simulation check (trip times, AC rejection).
