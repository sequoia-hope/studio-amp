# Block B — isolated active-clamp forward: converter design

Phase 1, block B (`iso_dcdc`). This file holds the converter-level design (operating points, stresses,
losses, efficiency, loop, protection). Each part has its own audit file; they quote the numbers from
here. Requirements: `design/intent.md` R-30..R-35, R-33a. Net names: `design/architecture.md`.

The loss arithmetic was done in a scratch script (not committed); every formula and input is
restated below so the reviewer can recompute it independently.

## Requirements this block must meet

| Item | Value | Source |
|---|---|---|
| Input `VPRI`–`RTN` | 42–57 V operating; PD UVLO 38.1 V rise / 32 V fall (TPS2373) | R-30, A→B |
| Output `VBUS` | 48 V ± 2 % static, ≤ 10 % sag in bursts | R-33 |
| Output power | 64.2 W at Class 8 (1.34 A), 45.8 W at Class 6 (0.95 A), 22.7 W at Type 2 (0.47 A) | R-33a |
| Efficiency | ≥ 92 % at full load (target) | R-33 |
| Isolation | 1500 Vrms 60 s primary↔secondary | R-32 |
| SR behaviour | no reverse conduction (diode emulation) | R-33 |
| Bulk | ≈ 5–7 mF, 63 V, 105 °C | R-33a |
| VBUS TVS | ≈ 56–58 V stand-off, clamp below the 100 V GaN rating | R-35 |

## Topology and transformer configuration

Active-clamp forward, low-side P-channel clamp (UCC2897A datasheet Fig. 24/29), peak-current mode,
secondary synchronous rectifiers in the return leg (both SR sources on secondary `GND`), each driven
by its own diode-emulating SR controller (NCP4306).

T1 = Würth 750343576 (WE-PoE++, the PMP20878 72 W ACF transformer, five 4-turn windings,
`B-transformer.md`). There is no 48 V-output forward transformer off the shelf, so the windings are
re-connected:

- primary = N1 ‖ N2 (4 T, two 6.5 mΩ windings in parallel)
- secondary = N3 + N4 in series (8 T)
- N5 (4 T, primary-side insulation) unused (or a sense winding, see `B-controller.md`)
- turns ratio n = Ns/Np = **2**; Lm = 100 µH/4 = **25 µH** (±20 %); Lleak ≈ 0.4 µH/4 ≈ 0.1 µH (est.)

## Switching frequency: 400 kHz

Chosen from three constraints:

1. **Volt-seconds.** The 4-turn primary halves the transformer's volt-second rating: 240 Vµs (N1+N2,
   8 T, bipolar) → **120 Vµs on 4 T**. Steady state V·t = (Vo + drops)/(n·fsw) = 48.8/(2·fsw).
   The UCC2897A has no line feed-forward of DMAX, so the worst case is DMAX at high line:
   57 V × 0.68/fsw. At 400 kHz: steady 61 Vµs (51 %), worst case **97 Vµs (81 %)**. At 250 kHz the
   worst case is 155 Vµs, over the rating (saturation). So fsw ≥ ~330 kHz.
2. **Core loss.** At 400 kHz the flux swing per turn equals PMP20878's at 200 kHz (122 Vµs on 8 T),
   the low end of Würth's 200–700 kHz application range. Loss falls with frequency at fixed
   volts (Steinmetz β > α), so higher is better for the core.
3. **Switching and gate loss** rise with fsw; 500 kHz gains ~0.2 W in the model but adds snubber
   and gate loss and makes the model's core term (the most uncertain) dominate the choice.

400 kHz also sits inside the amp's 400 kHz–1 MHz band; the amp fsw is tunable (R-53), so firmware
can avoid beat products. SYNC is left open (nothing crosses the barrier except feedback, R-32a).

## Operating points (400 kHz, Io = 1.34 A)

D = (Vo + Io·(R_SR + R_L)) / (n·(Vin − Ipri·Rds_main)); Vc = Vin/(1−D) (clamp/drain plateau);
ΔIm = Vin·D/(fsw·Lm); ΔIL = Vo·(1−D)/(Lo·fsw), Lo = 68 µH.

| Vin | D | Vc (main Vds plateau) | ΔIm p-p (Lm 25 µH) | ΔIL p-p | Primary peak |
|---|---|---|---|---|---|
| 41 V (PD min at 100 m, Class 8) | 0.590 | 100 V | 2.42 A | 0.72 A | 4.6 A |
| 42 V | 0.575 | 98.9 V | 2.42 A | 0.75 A | 4.64 A |
| 50 V | 0.483 | 96.7 V | 2.42 A | 0.91 A | 4.80 A |
| 57 V | 0.424 | 98.9 V | 2.42 A | 1.02 A | 4.90 A |

Vin·D is fixed by the output (24.4 V), so Vc stays near 97–100 V over the whole line range and the
magnetizing ripple is constant. Lm at −20 % gives ΔIm = 3.0 A p-p (+0.3 A on the peaks).

**DMAX = 0.68 nominal** (RON 48.7 k, ROFF 38.3 k, `B-controller.md`). Datasheet DMAX tolerance is
±4 points at 250 kHz; at 400 kHz assume ±5 → 0.63–0.73. Regulation needs D = 0.59 at 41 V; DMAX(min) would allow ≈ 38 V, but LINEUV stops the converter at
38.4 V (PD current limit, see start-up item 6).

## Stresses

| Device | Steady stress | With ringing (scaled from PMP20878 measurements) | Rating | Note |
|---|---|---|---|---|
| Main FET Vds | Vc ≈ 100 V | ≈ 120 V (PMP: 126.7 V peak at 38 V, Vc 105 V → +21 %) | 150 V | 80 % |
| Main FET, pathological DMAX at 57 V | 57/(1−0.73) = 211 V if the clamp fully follows | — | 150 V | only if D jumps to DMAX at high line; see note |
| Clamp P-FET Vds | −Vc ≈ −100 V | ≈ −120 V | −150 V | |
| Clamp cap | 100 V DC | | 250 V X7R | |
| Forward SR Vds (off-time) | n·Vin·D/(1−D) = 116 V at 42 V | ≈ 153 V (PMP Q13 +32 %) | 200 V | snubber required |
| Freewheel SR Vds (on-time) | n·Vin = 114 V at 57 V | ≈ 188 V (PMP Q15 +65 %) unsnubbed | 200 V | **snubber required; NCP4306 CS pin is 200 V abs max** |
| Output inductor | 114 V switch node | | wire insulation | |

Note on the DMAX case: the output sees a 6 mF bulk and a loop of a few kHz, so a load step moves
the error amp slowly and D does not jump to DMAX at high line; soft-start ramps D from zero; a short
is caught by the cycle-by-cycle limit, which shortens the pulse. The clamp cap (≈ 140 nF effective)
and Lm resonate with a quarter period of ≈ 3 µs, so Vc can follow D within a few cycles. This is the
same exposure TI accepted on PMP20878 (same FETs, same controller). **Bring-up check:** main-FET Vds
at 57 V with a step from 10 % to 100 % load. (LINEOV is used as the output OVP, `B-controller.md`.)

## Losses and efficiency (400 kHz, full Class 8 load, 48 V × 1.34 A = 64.3 W)

Model inputs: FDMS86200 Rds 18 mΩ max × 1.7 (hot); BSC500N20NS3 50 mΩ max × 1.6; Rcs 68 mΩ;
T1 windings 3.25 mΩ (pri, paralleled) and 21 mΩ (sec), × 1.4 hot × 2 AC factor; Lo DCR 89 mΩ × 1.3;
gate charges: main 40 nC, clamp 25 nC (ZVS, est.) at 13.5 V VDD (≈ 73 nC total), SR 13 nC each at the 10 V clamp; gate power
through the 85 %-efficient LM5019 bias bucks; main-FET turn-on Eoss ≈ 0.45 µJ at 50 V (it turns on at
≈ Vin: magnetizing energy brings Vds from Vc to Vin, but only leakage energy, ≈ 0.07 µJ, is left
below Vin); turn-off 3 ns effective overlap; SR body-diode conduction 2 × 40 ns per edge at 0.9 V;
two RC snubbers of 100 pF on the SRs (C·V² per cycle each); 0.15 W for feedback, CC sense, dividers.

Core loss (the dominant uncertainty): Würth gives no core data. Assumed Ae ≈ 60 mm² (consistent
with 240 Vµs at ±0.25 T on 8 T), Ve ≈ 2.4 cm³, generic MnZn Steinmetz at 100 °C:
P = 350 kW/m³ · (f/100 kHz)^1.4 · (Bpk/0.2 T)^2.6. Bpk = 126 mT at 400 kHz → ≈ 1.75 W.
The same model gives PMP20878's core ≈ 0.7 W, consistent with that design's measured 93.1 %
(TIDUDB0, 48 V in, 72 W out).

| Loss (W) at Vin | 42 V | 50 V | 57 V |
|---|---|---|---|
| Main FET conduction + switching | 0.55 | 0.58 | 0.61 |
| Current-sense resistor | 0.29 | 0.25 | 0.22 |
| Primary gate drive + UCC2897A at 13.5 V (via bias buck, 85 %) | 0.55 | 0.55 | 0.55 |
| Clamp FET (IRFR6215) conduction | 0.10 | 0.12 | 0.13 |
| T1 core (assumed, see above) | 1.75 | 1.75 | 1.75 |
| T1 windings | 0.10 | 0.09 | 0.08 |
| SR conduction + body diode | 0.22 | 0.23 | 0.23 |
| SR gate drive (via bias buck) | 0.16 | 0.16 | 0.16 |
| SR snubbers | 0.41 | 0.58 | 0.75 |
| Output inductor (DCR + core est.) | 0.28 | 0.32 | 0.34 |
| Feedback, CC sense, dividers | 0.15 | 0.15 | 0.15 |
| **Total** | **4.58** | **4.77** | **4.98** |
| **Efficiency** | **93.3 %** | **93.1 %** | **92.8 %** |

Sensitivity: with core loss doubled (3.5 W) the efficiency is 90.5–91.0 %. **Estimate: 90.5–93.3 %,
nominal ≈ 93 %.** The 92 % target is met if T1's core loss is ≤ ≈ 2.3 W; that has to be measured on
the bench (T1 temperature rise, input/output power). Snubber values are chosen at bring-up; the
model's 100 pF is pessimistic.

R-33a recomputed with the nominal 93 %: Class 8 converter output = (71.3 − 1.5) × 0.93 = 64.9 W
(R-33a assumed 64.2 W); Class 6 = 46.3 W. The ≈ 0.5 W of B's own bias is inside these numbers.
At 91 % the outputs are 63.5 W and 45.3 W, about 1 W below R-33a's line.

## Output current limit (constant-current loop) and the PSE

The PSE's budget, not the converter's ratings, sets the limit: bursts beyond Class power must come
from the bulk, not the cable (R-33a). The UCC2897A's cycle-by-cycle limit is ±10 % in threshold
and also depends on Lm, so it can only be a backstop. B therefore has a **secondary-side CC loop**
OR-ed into the same optocoupler as the voltage loop (`B-feedback.md`):

- IBUS shunt 27 mΩ (high side, between the converter output ceramics and the bulk node), INA281A4
  (gain 200, −4…110 V common mode), second TL431 as the current error amp.
- Three set-points selected by two FPGA/RP2350 GPIOs (`ILIM_SEL0`, `ILIM_SEL1`, secondary side, no
  barrier crossing): **0.470 A (Type 2, default at reset), 0.944 A (Class 6), 1.344 A (Class 8)**; the fourth
  GPIO state gives 0.87 A, so no state exceeds the Class 8 budget (`B-feedback.md`).
  Firmware raises the limit after reading `PD_TPL/TPH/BT` (block A) or LLDP.
- Start-up with the default 0.47 A: charging 6 mF to 48 V takes ≈ 0.6 s, with block C's ≈ 8 W
  logic load included ≈ 0.9 s. Acceptable (amp is muted until VBUS valid, R-34).
- Under CC, VBUS sags and output power falls with it, so the PD input stays under Class power.
- INA281 output is also `IBUS_SENSE` for telemetry (to an ADC, block D/E).

Primary backstop: Rcs = 68 mΩ; cycle-by-cycle at 0.43–0.53 V → 6.3–7.8 A primary peak, vs 5.3 A
needed at the 1.36 A CC limit with Lm −20 % (margin 1.19 at the low threshold). Hiccup at 0.75 V
(UCC2897A second threshold) for shorts. PD current limit (TPS2373-4, 2.2 A typ) is the last line.

## Soft-start, start-up sequence, shutdown

1. PSE powers the PD; TPS2373-4 charges its bulk (inrush 335 mA); PG low holds UCC2897A SS/SD at 0.
2. B's primary bias buck (LM5019, 13.5 V from VPRI, starts at VPRI–RTN ≈ 30 V during inrush) powers
   UCC2897A VDD directly and TPS2373 VC_IN; UCC2897A passes UVLO (12.7 V) but SS is held low by PG.
   TPS2373 VC_OUT is not used (TPS2373 §7.3.7: then VC_IN must be the PWM's bias supply).
3. After inrush + 81.5 ms, PG releases SS.
4. SS charges at 22 µA into 100 nF: 2.5→4.5 V in 9 ms (tSS = time to full current capability).
5. VBUS ramps in CC (0.47 A) to 48 V; SRs start as body diodes, then the NCP4306s take over when
   VSR (secondary LM5019 from VBUS) passes ≈ 10 V.
6. Line loss: LINEUV (40.4 V on / 38.4 V off) gives the UCC2897A soft-stop that discharges the clamp
   cap; the off level keeps the PD input ≤ 1.85 A at the Class 8 CC limit (`B-controller.md`).

## Loop compensation (starting values; to be confirmed in phase 8 simulation and on the bench)

Current-mode plant: ΔIout/ΔV_FB = 0.2 (internal FB divider, 4R:R) × n / Rcs = 0.2 × 2 / 0.068
= 5.9 A/V. Output Z at 1.5 kHz: 6 mF ‖ ESR(≈ 4 mΩ, 6 × KZN in parallel) → |Z| ≈ 18 mΩ, so
the plant gain at fc = 1.5 kHz is 0.106 (−19.5 dB). ESR zero ≈ 6.6 kHz.

Natural slope compensation: magnetizing upslope Vin/Lm = 1.68 A/µs at 42 V (109 mV/µs on Rcs)
already exceeds the reflected inductor downslope n·Vo/Lo = 1.41 A/µs (96 mV/µs), so m > 1 without
added ramp. RSLOPE = 180 k adds ≈ 0.5 more (UCC2897A eq. 28 with RF = 1 k, ton = 1.2 µs).

Voltage loop (TL431 type II, opto LED fed from VSR so there is no fast lane):
- divider 47.5 k / 2.61 k (0.1 %) → 47.9 V (low impedance so TL431 Iref adds ≤ 0.4 %);
- RLED 1.0 k, LTV-217-B CTR ≈ 1 at 1 mA, FB pull-up 4.99 k to VREF → mid-band opto gain 5;
- TL431 R1 = 84.5 k + C1 = 3.9 nF from cathode to REF: zero at 483 Hz, mid-band gain R1/Rtop = 1.78;
- total compensator gain 8.9 (+19 dB) at 1.5 kHz → fc ≈ 1.5 kHz;
- FB cap 6.8 nF to GND: pole at 4.7 kHz (cancels the ESR zero, filters the opto);
- 1 k across the LED keeps TL431 ≥ 1 mA.
Expected phase margin ≈ 55–65 °. Bulk ESR rises cold and with age, which moves the ESR zero down;
re-check at −10 °C equivalent ESR.

CC loop: TL431(CC) integrator 10 nF + 100 k zero; crossover ≈ 300 Hz (slow on purpose; the bulk
carries the transients).

## Light load and backfeed (R-33, R-35)

- NCP4306 turns each SR off at 0 mV Vds (true zero current), so inductor current never reverses:
  below Io ≈ ΔIL/2 (0.4–0.5 A) the converter runs DCM, and energy cannot flow from VBUS to the
  primary through the SRs.
- If the amp pumps VBUS above 48 V, the voltage loop drives FB below 2.5 V and the UCC2897A skips
  pulses on both OUT and AUX (datasheet 8.3.5): no power flows either way. Bulk absorbs, TVS clips
  spikes, firmware stops at 55 V (R-35).

## Open items

1. T1 core loss: no core data; measure at bring-up. A custom Würth winding of the same ER core
   with 8 T : 16 T would halve the flux and the core loss (≈ +1 % efficiency).
2. Snubber values (SR RC) tuned on the bench; footprints for RC on both SRs and RCD option on the
   freewheel SR.
3. MLCC DC-bias derating figures are assumptions (the maker datasheets carry none); confirm with
   Murata SimSurfing / Taiyo Yuden data before the gate.
4. Phase 8 simulation: SIMPLIS/LTspice of the power stage with the UCC2897A model, to confirm D,
   Vds peaks, loop crossover and the CC/CV hand-over.
