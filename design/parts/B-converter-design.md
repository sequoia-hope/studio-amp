# Block B — isolated active-clamp forward: converter design

Phase 1, block B (`iso_dcdc`). This file holds the converter-level design (operating points, stresses,
losses, efficiency, loop, protection). Each part has its own audit file; they quote the numbers from
here. Requirements: `design/intent.md` R-30..R-35, R-33a. Net names: `design/architecture.md`.
Revised 2026-11-07 for the phase 1 review (`design/gates/review-phase1-B.md`); the responses are at
the end of `B-interfaces.md`.

The loss arithmetic was done in a scratch script (not committed); every formula and input is
restated below so the reviewer can recompute it independently.

## Requirements this block must meet

| Item | Value | Source |
|---|---|---|
| Input `VPRI`–`RTN` | 42–57 V operating; PD UVLO 38.1 V rise / 32 V fall (TPS2373); B runs 38.4–57 V (LINEUV) | R-30, A→B |
| Output `VBUS` | 48 V ± 2 % static, ≤ 10 % sag in bursts | R-33 |
| Output power | R-33a: 64.2 W at Class 8, 45.8 W at Class 6, 22.7 W at Type 2; B's CC limits (from the 91 % floor): 62.4 W / 45.3 W / 21.1 W | R-33a, m1 |
| Efficiency | ≥ 92 % target, verify at bring-up; 91 % acceptable (user, 2026-11-07) | R-33 |
| Isolation | 1500 Vrms 60 s primary↔secondary | R-32 |
| SR behaviour | no reverse conduction (diode emulation) | R-33 |
| Start-up | from Type 2 within PSE limits | R-30 |
| Bulk / VBUS OVP | ≈ 5–7 mF; VBUS overvoltage scheme agreed with block D (`B-output.md`) | R-33a, R-35 |

## Topology and transformer configuration

Active-clamp forward, low-side P-channel clamp (UCC2897A datasheet Fig. 24/29), peak-current mode,
secondary synchronous rectifiers in the return leg (both SR sources on secondary `GND`), each driven
by its own diode-emulating SR controller (NCP4306).

T1 = Würth 750343576 (WE-PoE++, the PMP20878 72 W ACF transformer, five 4-turn windings,
`B-transformer.md`). No 48 V-output forward transformer exists off the shelf, so the windings are
re-connected:

- primary = N1 ‖ N2 (4 T, two 6.5 mΩ windings in parallel)
- secondary = N3 + N4 in series (8 T)
- N5 (4 T, primary-side insulation) = sense winding for the output OVP (`B-controller.md`)
- turns ratio n = Ns/Np = **2**; Lm = 100 µH/4 = **25 µH** (±20 %); Lleak ≈ 0.4 µH/4 ≈ 0.1 µH (est.)

## Switching frequency: 737.28 kHz, crystal-synchronised (lead decision 2026-11-07)

History: 400 kHz (phase 1) → 620 kHz (review M3, volt-seconds) → **737.28 kHz** (lead decision: the
amp PWM is fixed at 576 kHz, and block E's beat check needs the converter inside **712–775 kHz across
all tolerances**). The UCC2897A's free-running oscillator is ±10 % over temperature (internal timing
capacitor), so the converter is **synchronised to a 7.3728 MHz crystal divided by 10** on the primary
(`B-sync-clock.md`). The frequency is then 737.28 kHz ± 40 ppm. If the clock fails, the controller
free-runs at 590–708 kHz and the converter keeps working (beat flagged by block E from `ACF_PULSE`).

1. **Volt-seconds (cold 120 Vµs on 4 T; ≈ 90 Vµs assumed hot until Würth answers):**
   - synced: worst 57 V × DMAX(max) 0.696/737 kHz = **54 Vµs → 45 % cold, ≈ 60 % hot** ✓;
   - clock failed: 57 × 0.75/590 kHz = 72 Vµs → 60 % cold, ≈ 80 % hot ✓;
   - steady state 24.4 V/737 kHz = 33 Vµs.
   The off-the-shelf part is now safe even if Würth's hot rating is as low as ≈ 72 Vµs (clock-failed
   case) or ≈ 60 Vµs (synced).
2. **Core loss**: Bpk 68 mT → ≈ 0.84 W (assumed Steinmetz, below).
3. **Switching, gate, snubber loss** rise ≈ 19 % from 620 kHz; net efficiency −0.2 % (table below).
4. **Limits**: T1 application range 200–700 kHz (Würth). **737 kHz is 5 % above Würth's typical
   range**; it is not a rating, but it is asked in the Würth email. UCC2897A ≤ 1 MHz, NCP4306 ≤ 1 MHz.
   Shortest SR conduction 0.41 µs against MIN_TON 125 ns ✓; shortest SR off-time 0.41 µs against
   MIN_TOFF 245 ns ✓ (`B-sync-rect.md`).

Beats with the 576 kHz amp: f − 576 = 161 kHz, 2·576 − f = 415 kHz, 3·576 − 2f = 253 kHz ✓.
Block C's 5 V buck (≈ 690 kHz): 47 kHz from 737.28 kHz. That is a supply-to-supply product on
separate rails; told to block C. In clock-failed mode the band 590–708 kHz can overlap it.

## Operating points (737 kHz, Io = 1.34 A)

D = (Vo + Io·(R_SR + R_L)) / (n·(Vin − Ipri·Rds_main)); Vc = Vin/(1−D);
ΔIm = Vin·D/(fsw·Lm); ΔIL = Vo·(1−D)/(Lo·fsw), Lo = 68 µH.

| Vin | D | Vc (main Vds plateau) | ΔIm p-p (Lm 25 µH) | ΔIL p-p | Primary peak |
|---|---|---|---|---|---|
| 37.6 V (LINEUV off, worst) | 0.655 (DMAX(min) 0.664 ✓) | 109 V | 1.32 A | 0.33 A | 3.68 A |
| 38.4 V (LINEUV off, nominal) | 0.640 | 107 V | 1.32 A | 0.35 A | 3.70 A |
| 42 V | 0.575 | 98.9 V | 1.32 A | 0.41 A | 3.75 A |
| 50 V | 0.484 | 96.9 V | 1.32 A | 0.50 A | 3.84 A |
| 57 V | 0.424 | 98.9 V | 1.32 A | 0.55 A | 3.89 A |

**DMAX in sync = 1 − tOFF/TSYNC = 0.680** (ROFF 14.3 k), 0.664–0.696 with ±5 % on tOFF; free-running
DMAX 0.715 (RON 31.6 k). A DMAX(min) part now covers the 37.6 V corner (0.655) without droop.

## Stresses (recomputed at the LINEUV-off corner, review M4)

| Device | Steady stress | With ringing | Protection | Rating |
|---|---|---|---|---|
| Main FET Vds | Vc 97–109 V | ≈ 130 V (+21 %, PMP: 126.7 V at Vc 105 V) | — | 150 V |
| Main FET at a 94 V input surge (block A's SMCJ58A) | Vc ≈ Vin²/(Vin − 24.4) = 127 V (peak-current mode cuts D within one cycle) | | — | 150 V |
| Clamp P-FET | −Vc | ≈ −130 V | — | −150 V |
| Clamp cap | 97–109 V DC | | | 250 V |
| Forward SR Vds = NCP4306 CS | n·Vin·D/(1−D) = **137 V at 38.4 V, 143 V at 37.6 V**; 84 V at 57 V | +22–32 % → 167–189 V unclamped | **RCD-Z clamp (US1G + 10 nF + SMBJ130A, VBR 144–159 V) → ≤ ≈ 165 V** | 200 V (≤ 83 %) |
| Freewheel SR Vds = NCP4306 CS | n·Vin = 114 V at 57 V | +65 % → 188 V unclamped | **same RCD-Z clamp → ≤ ≈ 165 V** | 200 V (≤ 83 %) |
| Main FET, DMAX at 57 V transient | 57/(1−0.696) = 188 V if the clamp fully follows | — | slow loop, 60 ms soft-start, CS limit | 150 V |

Note on the DMAX case: the output sees a 6 mF bulk and a loop of ≈ 1 kHz, so a load step moves the
error amp slowly and D does not jump to DMAX at high line. Soft-start ramps D from zero, and a short is
caught by the cycle-by-cycle limit. **Bring-up check:** main-FET Vds at 57 V with a 10 → 100 % load
step, plus the forced-DMAX test above.

## Losses and efficiency (737 kHz, full Class 8 load, 48 V × 1.34 A = 64.3 W)

Model inputs as before (FDMS86200 18 mΩ × 1.7; BSC500N20NS3 50 mΩ × 1.6; Rcs 68 mΩ; T1 3.25/21 mΩ
× 1.4 × 2 AC; Lo 120 mΩ × 1.3; gate 45 + 28 nC at 14.3 V and 2 × 13 nC at 10 V via 85 % bucks; Eoss
0.75 µJ at 50 V scaled Vin^1.5; 3 ns turn-off overlap; SR body diode 2 × 30 ns per edge; 22 pF RC
snubbers C·V²·f each + 0.1 W clamps; 0.15 W feedback/sense), plus 0.06 W for the sync clock.
Core: assumed Ae 60 mm², Ve 2.4 cm³, P = 350 kW/m³ · (f/100 kHz)^1.4 · (Bpk/0.2 T)^2.6;
Bpk 68 mT → 0.84 W.

| Loss (W) at Vin | 38.4 V | 50 V | 57 V |
|---|---|---|---|
| Main FET conduction + switching | 0.94 | 1.07 | 1.19 |
| Current-sense resistor | 0.32 | 0.24 | 0.21 |
| Primary gate drive + UCC2897A at 14.3 V (via bias buck) | 0.96 | 0.96 | 0.96 |
| Sync clock (LDO, oscillator, counter) | 0.06 | 0.06 | 0.06 |
| Clamp FET conduction | 0.03 | 0.04 | 0.04 |
| T1 core (assumed) | 0.84 | 0.84 | 0.84 |
| T1 windings | 0.11 | 0.08 | 0.07 |
| SR conduction + body diode | 0.25 | 0.25 | 0.25 |
| SR gate drive (via bias buck) | 0.32 | 0.32 | 0.32 |
| SR snubbers (22 pF) + RCD-Z clamps | 0.47 | 0.40 | 0.43 |
| Output inductor | 0.30 | 0.32 | 0.33 |
| Feedback, CC sense, dividers | 0.15 | 0.15 | 0.15 |
| **Total** | **4.75** | **4.73** | **4.86** |
| **Efficiency** | **93.1 %** | **93.1 %** | **93.0 %** |

Cost of 737 kHz against 620 kHz: ≈ +0.2 W, −0.3 % efficiency. Sensitivity: core loss doubled →
≈ 92.0 %; core loss and Eoss both +50 % → ≈ 91.8 %. **Estimate: 92–93.1 %**, against R-33's 92 %
target and 91 % floor ✓ (verify at bring-up).

R-33a: the Class 8 converter output is capped at 1.30 A × 48 V = 62.4 W (review m1), 1.8 W under
R-33a's 64.2 W line; in exchange the PD stays inside 71.3 W at the 91 % floor.

## Output current limit (constant-current loop) and the PSE

The PSE's budget, not the converter's ratings, sets the limit: bursts beyond Class power must come
from the bulk, not the cable (R-33a). The UCC2897A's cycle-by-cycle limit is ±10 % in threshold
and also depends on Lm, so it can only be a backstop. B therefore has a **secondary-side CC loop**,
OR-ed into the same optocoupler as the voltage loop (`B-feedback.md`):

- IBUS shunt 30 mΩ (high side, between the converter output ceramics and the bulk node), INA281A4
  (gain 200, −4…110 V common mode), RC-filtered, second TL431 as the current error amp.
- Set-points selected by two GPIOs (`ILIM_SEL0`, `ILIM_SEL1`, secondary side, no barrier crossing):
  **0.440 A (Type 2, default at reset), 0.943 A (Class 6), 1.30 A (Class 8)**, set from the 91 %
  efficiency floor (review m1). The fourth GPIO state gives 0.80 A, so no state exceeds the Class 8
  budget. Firmware raises the limit after reading `PD_TPL/TPH/BT` (block A) or LLDP.
- Under CC, VBUS sags and output power falls with it, so the PD input stays under Class power.
- The INA281 output, filtered, is also `IBUS_SENSE` for telemetry.

Primary backstop: Rcs = 68 mΩ; cycle-by-cycle at 0.43–0.53 V → 6.3–7.8 A primary peak, against
4.3 A needed at the 1.30 A CC limit with Lm −20 % at 737 kHz (margin 1.47 at the low threshold).
Hiccup at 0.75 V for shorts. The PD current limit (TPS2373-4, 2.2 A typ) is the last line.

## Soft-start, start-up sequence, shutdown (revised for review M5)

1. PSE powers the PD; TPS2373-4 charges its bulk (inrush 335 mA); PG low holds UCC2897A SS/SD at 0.
2. B's primary bias buck (LM5019, **14.3 V** from VPRI, starts at VPRI–RTN ≈ 30 V during inrush)
   powers UCC2897A VDD and TPS2373 VC_IN. UCC2897A passes UVLO (≤ 13.2 V) but SS is held low by PG.
3. After inrush + 81.5 ms, PG releases SS/SD.
4. **Soft-start 60 ms** (CSS 1.0 µF, ISS 34 µA; 2.5 → 4.5 V). The peak-current limit ramps
   linearly from 0 to its maximum over 60 ms. That ramp is what bounds the input current while VBUS
   is too low to power the secondary control.
5. Secondary control: the VSR buck (LM5019 from VBUS, 10 V) starts at **VBUS = 7.5 V** and tracks
   VBUS in dropout up to 10 V. From VBUS ≈ 7.5 V the TL431s, opto and INA281 work, so the **CC limit
   (0.44 A at reset) holds from VBUS ≈ 7.5 V** to 48 V.
6. Below 7.5 V nothing on the secondary regulates, and the output current is set only by the
   soft-start ramp: Iout(t) ≈ 2.4 A·t/60 ms (2.4 A ≈ secondary current at the minimum CS limit).
   VBUS on 6 mF reaches 7.5 V at t = √(2 · 60 ms · 6 mF · 7.5 V / 2.4 A) = 47 ms, with Iout = 1.9 A
   and Pout = 14 W. Input ≈ 14 W/0.75 (light-load efficiency, SR body diodes) = 19 W → **0.45 A at
   42 V, 0.37 A at 52 V**. This is under a Type 2 PSE's ≈ 0.6 A ICUT; Class 6/8 PSEs allow more.
   From 7.5 V on, CC caps the output at 0.44 A, so Pin ≤ 0.44 × 48/0.89 + 0.8 = 24.5 W < 25.5 W ✓.
   Worst corner: with the maximum CS threshold (Iout ramp to 3.0 A), VBUS reaches 7.5 V at 42 ms with
   2.1 A, 16 W out → 0.51 A in at 42 V. Still under 0.6 A; this is the case to measure.
7. SRs run as body diodes until VSR ≈ 6 V (NCP4306 UVLO 4 V; DRV held low below it), then the
   NCP4306s take over.
8. Line loss: LINEUV (40.4 V on / 38.4 V off) gives the UCC2897A soft-stop that discharges the clamp
   cap. The off level keeps the PD input ≤ 1.85 A at the Class 8 CC limit (`B-controller.md`).

**Bring-up test (added):** start-up from a Type 2 (802.3at, 30 W) PSE and from a Class 6 PSE, with
the input current logged against the PSE's ICUT/TCUT. Pass: no PSE disconnect over 20 cold starts,
and input current ≤ 0.6 A (Type 2) at every point.

## Loop compensation (redone for review M2; confirm in phase 8 simulation and on the bench)

**Plant.** UCC2897A: VCS(peak) ≈ (VFB − ≈ 2.5 V)/5 (internal 4R:R divider, datasheet block diagram),
so ΔIpri/ΔVFB = 0.2/Rcs = 2.94 A/V. With n = Ns/Np = 2 **the output current is the primary current
divided by n**: ΔIout/ΔVFB = 0.2/(Rcs·n) = **1.47 A/V**. (The old 5.9 A/V applied n the wrong way
round.) The slope ramp (m ≈ 1.7 including magnetizing) lowers it by a further ≈ 10–30 % (bench).
Output impedance: 6 mF ‖ (6 × KZN ESR ≈ 4 mΩ) → Zout(1 kHz) = 26.8 mΩ; ESR zero 6.6 kHz.
Plant at 1 kHz: 1.47 × 0.0268 = 0.039 (−28.1 dB), falling at −20 dB/dec.

**Compensator** (TL431 type II, the opto LED fed from VSR, no fast lane):
- divider 47.5 k / 2.61 k (0.1 %) → 47.9 V;
- **RLED 499 Ω**, LTV-217-B CTR ≈ 1, FB pull-up 4.99 k to VREF → opto gain CTR·RPU/RLED = 10;
- **TL431 R1 = 115 k + C1 = 4.7 nF** from cathode to REF: zero at 294 Hz; mid-band gain
  R1/Rtop = 2.42 (× 1.04 at 1 kHz from the zero);
- FB cap **6.8 nF** to GND: pole at 4.7 kHz. Opto pole ≈ 15 kHz (typical; not in the datasheet);
- 1 k across the LED keeps the TL431 at ≥ 1 mA. LED current: 0.5 mA of collector current at
  FB = 2.5 V needs 0.25–1 mA of LED current (CTR 2–0.5). The maximum, with the cathode at 2.5 V, is
  (10 − 1.1 − 2.5)/499 = 12.8 mA, under the LTV-217's 50 mA IF.
- Loop gain at 1 kHz: 0.039 × 10 × 2.42 × 1.04 = 0.98 → **fc ≈ 1.0 kHz**.
- Phase at fc: plant −90° + ESR zero +8.6°, compensator −90° (integrator) + zero +73.6°, FB pole
  −12°, opto pole −3.8° → −113.6° → **phase margin ≈ 66°**.
- Over CTR 0.5–2: fc 0.5–2 kHz, PM 56° (at 0.5 kHz) to 68° (at 2 kHz). Gain margin ≥ 15 dB (the
  FB/opto poles; beyond 20 kHz the plant has fallen another 26 dB).
- Cold bulk (ESR × 3 at −10 °C): the ESR zero moves to ≈ 2 kHz, fc rises ≈ 10 % and PM improves.

CC loop: TL431(CC) 100 k + 10 nF from cathode to REF (zero 160 Hz); INA281 output RC 1 k / 47 nF
(3.4 kHz). Crossover ≈ 200–300 Hz, slow on purpose because the bulk carries the transients. The CV
and CC paths drive the same LED through a diode OR; the hand-over is to be checked in the phase 8
simulation.

## Light load and backfeed (R-33, R-35)

- NCP4306 turns each SR off at 0 mV Vds (true zero current), so the inductor current does not
  reverse: below Io ≈ ΔIL/2 (0.17–0.28 A at 737 kHz) the converter runs DCM, and energy cannot flow
  from VBUS to the primary through the SRs. The only exception is the MIN_TON blanking. Set to
  ≈ 130 ns (RMIN_TON 0.75 k, review m4), it can hold the freewheel SR on while the inductor current
  reverses at Vo/Lo = 0.7 A/µs: ≤ 0.09 A peak, ≤ 6 nC per cycle (≈ 4.4 mA average at 737 kHz), and only in
  deep DCM. The dV/dt-detector variant ("D") stops turn-on on the DCM ring, so the SR is not
  re-triggered. Sustained backfeed to the primary, which R-33 forbids, cannot occur.
- If the amp pumps VBUS above 48 V, the voltage loop drives FB below 2.5 V and the UCC2897A skips
  pulses on both OUT and AUX (datasheet 8.3.5): no power flows either way. Bulk absorbs; the VBUS
  overvoltage scheme is in `B-output.md`.

## Open items

1. T1 core data (material, Ae, Bsat at 100 °C) and confirmation that 737 kHz is acceptable for
   the part (Würth's typical range ends at 700 kHz); questions in `B-transformer.md`. The volt-second
   margin is now comfortable (≤ 60 % hot synced). Measure core loss at bring-up.
2. SR snubbers: 22 pF RC plus RCD-Z clamps fitted on both SRs as the baseline (`B-sync-rect.md`);
   tune the RC on the bench.
3. MLCC DC-bias derating figures are assumptions (the maker datasheets carry none); confirm with
   Murata SimSurfing data before the gate.
4. Phase 8 simulation: SIMPLIS/LTspice of the power stage with the UCC2897A model, to confirm D,
   Vds peaks, loop crossover and the CC/CV hand-over.
