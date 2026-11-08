# HF ceramic decoupling across each half-bridge (VBUS–GND), ×4 half-bridges

> **HARD PLACEMENT RULE (second-pass review m-3, 2026-11-08): the commutation loop of each half-bridge (HS drain → LS source → the 2 × 100 nF 0603 → back) must be ≤ 1 nH, verified by phase 6 parasitic extraction** (≤ 1.5 nH only with a documented margin). The 1 nH target is load-bearing. Overshoot I·√(L/Coss) with IGB070 Coss 340 pF: 1 nH → 22 V at the 13 A legitimate peak (70 V) and 27 V at 16 A. 2 nH → 31 V at 13 A (**79 V, at Infineon's 80 V continuous guidance**) and 38 V at 16 A (86 V).
> **Insurance: an optional RC snubber footprint per half-bridge, DNP by default**, from the switch node to the LS source (GND), beside the LS FET: C_SN 470 pF 100 V C0G 0603 + R_SN 2.2 Ω 2512 (damping R ≈ √(L/Coss) = 1.7–2.4 Ω for 1–2 nH; C ≈ 1.4 × Coss). If fitted, the cost is C·V²·fsw = 470 pF × 48² × 576 kHz = **0.62 W per half-bridge** (2.5 W for four), dissipated in R_SN (2512, 1 W). So it is fitted only if bring-up shows ringing above ≈ 75 V, and the loss must then enter the budget. Part numbers are fixed in phase 2.

> **fsw update 2026-11-07 (FPGA changed to ECP5, edge grid 1.453 ns = 688.128 Mb/s ODDRX2F, E-fpga-ecp5.md):** baseline fsw is now **448 kHz** (1536 grid steps; 448 kHz = 48 kHz × 28/3, audio-locked but not an integer multiple). 480 kHz is not on the grid. Option per build: 672 kHz (14 × 48 kHz, 1024 steps). Ripple currents within ±5 % of the 480 kHz values; conclusions unchanged.

Datasheets: datasheets/hmk325b7225kn.pdf (Taiyo Yuden MSASH32NSB7225KTNA01 / HMK325B7225KN-T spec sheet with DC-bias, ESR and ripple-current curves, read off p.2); datasheets/hmk107b7104ka.pdf (HMK107B7104KAHT spec sheet). Read: all pages.

| Per half-bridge | Part | Supplier (`show`, 2026-11-07) |
|---|---|---|
| 2 × 2.2 µF 100 V X7R 1210 | Taiyo Yuden HMK325B7225KN-T | `C92775 HMK325B7225KN-T (Taiyo Yuden, 1210): extended, JLC stock 80056, lifecycle normal` |
| 2 × 100 nF 100 V X7R 0603 (closest to the FETs) | Taiyo Yuden HMK107B7104KAHT | `C268011 HMK107B7104KAHT (Taiyo Yuden, 0603): extended, JLC stock 249729, lifecycle normal` |

Per board: 8 × 2.2 µF + 8 × 100 nF. ×5 boards = 40 + 40; stock ≫.
The VBUS bulk electrolytics (≈ 5–7 mF) are block B's. This file covers only the ceramics that close each commutation loop.

## Ratings vs worst case
| Parameter | Rating | Worst case | Margin |
|---|---|---|---|
| Voltage | 100 V | 48 V nominal, 55 V firmware cut, 87 V TVS clamp (transient) | 1.8× at 55 V. The 2× MLCC guideline is not quite met at the firmware cut, but is met at nominal 48 V (2.1×). The 87 V clamp is a rare transient below the rating. Accepted. |
| Temperature | X7R −55…+125 °C | board ≤ 83 °C (no-panel case, D-gan-fet.md) | OK |

## Calculations
### DC-bias derating (HMK325B7225KN-T, p.2 "DC Bias Char.")
Read off the curve: −10 % at 10 V, −30 % at 30 V, **−52 % at 48 V**, −57 % at 55 V. Effective C per part ≈ 2.2 × 0.48 = **1.06 µF at 48 V**.
HMK107B7104KAHT (100 nF 0603 100 V X7R, p.2 "DC Bias Char."): −40 % at 20 V, **−65 % at 48 V** → 35 nF effective. Its SRF is ≈ 20–30 MHz (p.2 impedance curve), and it carries the ns-scale edge current.
Per half-bridge effective: 2 × 1.06 + 2 × 0.035 = **2.2 µF**; per channel (2 half-bridges, both on the same VBUS pour) 4.4 µF.

### Ripple current
Bridge input current per channel, HF component (rms about the switching-period mean), BTL BD sine, computed numerically (calc in the reviewer brief): **1.59 A rms at 46 W into 4 Ω** (continuous case), 2.85 A rms at 144 W into 4 Ω (burst), 1.22 A rms at 50 W into 8 Ω.
Shared over the channel's 4 × 2.2 µF (the 100 nF parts take the edges): ≈ 0.4 A rms each continuous, 0.71 A rms at the burst.
Ripple-current rating (p.2 "Ripple Current", self-heating): 100 kHz curve ≈ 1.3 A for ΔT 10 °C; 1 MHz curve ≈ 1.6 A for 10 °C; at 480 kHz roughly 1.5 A for 10 °C. At 0.4 A → ≈ 1 °C; at 0.71 A → ≈ 2.5 °C ✓.

### Bus ripple voltage across the ceramics
Worst case (ceramics alone supplying one full HS pulse): ΔQ = I_pk × t_on ≈ 8.5 A × 1 µs = 8.5 µC → ΔV = 8.5 µC / 4.4 µF = 1.9 V pp. The bulk electrolytics take over within about 100 ns (tens of nH of path inductance at ≤ 30 mm), so the expected HF bus ripple at the bridge is ≈ 0.5–1 V pp at 144 W, and less at the continuous level. Bus feedforward (D-vbus-adc.md) samples through a 75 kHz RC and does not see the 480 kHz component.
**Phase 4 requirement:** at least two VBUS bulk electrolytics within about 30 mm of each channel's bridge (block B to place, D-interfaces.md).

### Impedance at the edges
ESR of the 2.2 µF ≈ 7 mΩ at 1–3 MHz; SRF ≈ 3 MHz (p.2). The 100 nF 0603 (SRF ≈ 20–30 MHz) carries the ns-scale edge current; its ripple rating is ≈ 0.6 A for 10 °C at 1 MHz (p.2), well above its share. Each half-bridge's loop is closed by its own pair of 100 nF parts, placed between HS drain and LS source.

## Layout guidance
- The 2 × 100 nF 0603 bridge HS drain to LS source of the same leg, touching both FET pads, with the return path on L2 directly under (LMG1210 §8.3 do's #2/#3; motor-drive.md "ceramic decoupling directly across each half-bridge").
- The 2 × 2.2 µF 1210 within 5 mm, on the same pours.
- Via arrays per nets.csv current.

## Open questions
None.
