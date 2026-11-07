# Reconstruction filter passives: FIR tap resistors, differential MFB R/C (per channel)

Datasheets:
- `datasheets/yageo-rt0603.pdf` (Yageo RT series thin film). RT0603 is 1/10 W, 75 V working /
  150 V overload, −55 to +155 °C. "B" means ±0.1 % and "D" means 25 ppm/°C; the ±0.1 %/±25 ppm
  range runs 1 Ω–1 MΩ (table 1).
- `datasheets/murata-grm2195c1h153.pdf` (GRM21 5C, C0G, 50 V).
- `datasheets/yageo-cc0603-npo.pdf` (CC0603 NPO, 50 V).

These are passive groups chosen for tolerance, tempco and dielectric. The filter maths is below.
The op-amp is in `F-opamp-sa5532.md`.

Lines from `show`:
- `C861295 RT0603BRD072K2L (YAGEO, 0603): extended, JLC stock 109760, lifecycle normal, checked 2026-11-07`
- `C861472 RT0603BRD07560RL (YAGEO, 0603): extended, JLC stock 9925, lifecycle normal, checked 2026-11-07`
- `C861551 RT0603BRD07750RL (YAGEO, 0603): extended, JLC stock 1260, lifecycle normal, checked 2026-11-07`
- `C728592 RT0603BRD073K9L (YAGEO, 0603): extended, JLC stock 17304, lifecycle normal, checked 2026-11-07`
- `C723637 RT0603BRD0720KL (YAGEO, 0603): extended, JLC stock 38143, lifecycle normal, checked 2026-11-07`
- `C97907 GRM2195C1H153JA01D (muRata, 0805): extended, JLC stock 17632, lifecycle normal, checked 2026-11-07`
- `C97908 GRM2195C1H822JA01D (muRata, 0805): extended, JLC stock 8750, lifecycle normal, checked 2026-11-07`
- `C62784 CC0603JRNPO9BN331 (YAGEO, 0603): extended, JLC stock 458353, lifecycle normal, checked 2026-11-07`

Note: the 3.83 kΩ value (RT0603BRD073K83L, C861384) has only 25 in stock. It was rejected, and
3.9 kΩ is used instead.

## Topology (one channel; the "+" side is fed by the Q outputs, the "−" side by the Q̄ outputs)

```
Q_k  ─ R_T 2.2k ─┐(k=0..3)                    Q̄_k ─ R_T 2.2k ─┐
                 P+ ─ R1 560 ─ X+ ─ R2 750 ─ IN+   P− ─ R1 560 ─ X− ─ R2 750 ─ IN−
                 │             │             │     │             │            │
                C0 15n        C1 8.2n      C2 330p C0 15n       C1 8.2n      C2 330p ─► OUT
                 │             ├ R3 3.9k─GND │     │             ├ R3 3.9k ─► OUT
                GND           GND           GND   GND           GND
                               └ R_INJ 20k ─ servo out           └ R_BAL 20k ─ GND
```

The inverting side is a standard MFB (R3 and C2 go to OUT). The non-inverting side is the mirror
image, with OUT replaced by GND. Superposition gives OUT = H_MFB(s)·(V_P+ − V_P−). That is a
differential 2nd-order low-pass, plus the passive real pole (R_T∥ and C0) on each side, so 3rd
order in total. The node equations are in `scratchpad/fcalc/sym.py`. Solving the denominator
against a 3rd-order Butterworth at 50 kHz with R0 = R1 = 560 Ω, R3 = 3.83 kΩ, R2 = 750 Ω gave
C0 = 14.83 nF, C1 = 8.72 nF, C2 = 310 pF. These were then snapped to E12 values.

## Chosen values and response (computed with the E-series values; script `chk2.py`)

| Ref | Value | Part | Why |
|---|---|---|---|
| R_T (×4 per side, ×8 per channel) | 2.2 kΩ 0.1 % 25 ppm | RT0603BRD072K2L | 4 ∥ = 550 Ω. FF Ron ≤ 33 Ω is ≤ 1.5 % of that |
| R_T option (single-tap) | 560 Ω 0.1 % | RT0603BRD07560RL | tap 0 only |
| R1 | 560 Ω 0.1 % | RT0603BRD07560RL | |
| R2 | 750 Ω 0.1 % | RT0603BRD07750RL | |
| R3 | 3.9 kΩ 0.1 % | RT0603BRD073K9L | gain = 3.9k/(550 + 560) = **3.51** |
| R_INJ, R_BAL | 20 kΩ 0.1 % | RT0603BRD0720KL | servo injection, balanced on both sides (`F-servo-opa2277.md`) |
| C0 | 15 nF C0G 50 V 5 % 0805 | GRM2195C1H153JA01D | |
| C1 | 8.2 nF C0G 50 V 5 % 0805 | GRM2195C1H822JA01D | |
| C2 | 330 pF C0G 50 V 5 % 0603 | CC0603JRNPO9BN331 | |

Output of the calculation:
```
chosen
   1000 Hz  -0.00 dB    20000 Hz  -0.06 dB    30000 Hz  -0.38 dB
  50000 Hz  -3.69 dB   100000 Hz -18.59 dB   200000 Hz -36.38 dB
 500000 Hz -60.20 dB  1000000 Hz -78.25 dB  3072000 Hz -107.49 dB
  -3 dB at 47.4 kHz; max -0.000 dB (no peaking)
Ctol 5%: |H(20k)| min -0.213 max 0.080 dB   (Monte Carlo, 2000 runs, R 0.1 %)
Ctol 2%: |H(20k)| min -0.121 max 0.001 dB
```
The in-band droop is −0.06 dB at 20 kHz nominal, and DSP EQ can flatten it. The phase at 20 kHz
is −49°, which is linear-phase-ish and doesn't matter for this application. The 4-tap boxcar
adds zeros at 1.536 and 3.072 MHz and −0.002 dB at 20 kHz.

## Tolerance and tempco

- **Resistor matching sets the CMRR.** The common-mode input is the 1.65 V DC average of Q/Q̄, plus
  +3V3_Q noise. The CM-to-DM conversion is ≈ gain × Σ(mismatch). With 0.1 % parts, the worst case
  is 0.4 %, so 1.65 V × 3.51 × 0.004 = 23 mV DC worst. The servo removes it. The AC CMRR is
  ≈ 46 dB worst, which is ample for 5 µV of supply noise. With 1 % thick-film parts this would be
  230 mV of offset and 26 dB of CMRR, which is why the parts are thin film.
- 25 ppm/K over the 30 K rise from room to cabinet air moves the gain by 0.08 % and keeps the
  mismatch ≤ 0.15 %. Negligible.
- C0G is ±30 ppm/K, with no voltage coefficient and no piezoelectric effect. X7R is forbidden in
  this filter: its voltage coefficient and microphonics would produce distortion. The DC bias on
  these caps is ≤ 1.65 V, well under the 50 V rating, and C0G has no DC-bias derating anyway.
- Effect of 5 % C on the response: f(−3 dB) moves by about ±5 %, and the 20 kHz gain by −0.21 to
  +0.08 dB (Monte Carlo above). L/R matching at 20 kHz is ≤ 0.3 dB worst case, which DSP can trim.

## Power

- R_T: ≤ (3.3 V − 1.3 V)²/2.2 kΩ = 1.8 mW. R1, R2: ≤ 1 mW. R3: (5.65 Vpk)²/2/3.9 kΩ = 4.1 mW.
  All are ≪ 100 mW (RT0603 rating). OK.
- R3 on the − side carries the full output swing. Voltage rating: 75 V for 0603 thin film. OK.

## Noise

R2 is the largest resistor noise source, because it is amplified by the rising noise gain (see
`F-overview.md`: 3.04 µV of the 7.22 µV total). Lowering R2 lowers the noise but raises C1 and C2.
At these values the op-amp en already dominates.

## Layout guidance

- Keep the C0 caps at the P nodes and put their ground vias directly into the analog ground.
  The P nodes carry the 6 MHz switching residue, so keep them compact and away from IN± and OUT.
- Lay out the + and − networks mirror-symmetric around the op-amp (CMRR at HF).
- C2 goes right at the op-amp inputs.

## Open questions

- None for phase 1. Phase 8 checks the real stopband with the SA5532 macromodel (MFB feedthrough
  above ~1 MHz depends on the op-amp's Zout).
