# Block D — interfaces to the other blocks, and proposed changes to the architecture

Block D: two identical BTL GaN channels (woofer `amp_woofer`, tweeter `amp_tweeter`) plus `vbus_sense`. Per channel: 2 × LMG1210 (PWM mode), 4 × IGB070S10S1 (user decision 2026-11-08; IGC033S10S1 is the documented fallback, different land pattern), 2 × SER2915H-103KL + 5 mΩ/INA241A1 sense, TLV3502 window OCP, diode-AND + 74LVC1G17 + 74LVC1G74 fault latch, LMV393 DC detect, 14 × 100 nF C0G filter caps, Zobel 10 Ω/100 nF, 2 × NTC, SMBJ51A. The tweeter channel adds a 2 × 22 µF polypropylene series HPF cap. Shared: ADS7042 (VBUS), ADS7038-Q1 (4 × I, 4 × NTC), 2 × ADS8353 + 4 × OPA836 (post-filter sense; fitted on all prototypes per user decision E).

## Baseline operating point
- **fsw = 576 kHz = 12 × 48 kHz** (block E review: ECP5 −7I grid at PLL ×12, ECLK 294.912 MHz, **1.695 ns steps, 1024 per period**). R-53 range ✓. Option 768 kHz. Idle FET loss, both channels: **IGB070S10S1 1.80 W at 576 kHz** (0.89 W at 448, 3.34 W at 768); IGC033 fallback 6.02 W.
- **BD modulation, both legs of a channel switching at fsw; dead-time setting 20 ns** (LMG1210 resistors 20.0 kΩ; **≈ 18 ns effective with IGB070 edges, 14–24 ns spread**; ≈ 15 ns with the IGC033 fallback). *[changed 2026-11-08]*
- **Duty clamp 8–92 %** per leg (M ≤ 0.84 → 40.3 V pk: 101 W into 8 Ω, R-50 ✓; 10.1 A pk into 4 Ω), for bootstrap refresh (D-bootstrap.md, review M1). *[changed: was 3–97 %, M ≤ 0.94]*
- **OCP, two regimes, same latch:** hard short at a terminal → dV/dt detector, **≈ 48 ns** from the short, peak ≤ 13.3 A (D-short-detect.md); ramp overcurrent → INA241 window **14.9 ± 0.7 A, ≈ 216 ns** threshold to gates off, peak ≤ 16.7 A (D-current-sense.md). DC detect in hardware (|DC| ≥ 6 V; 23 ms at 48 V, 50 ms at 24 V). *[changed 2026-11-08: 50/218 → 48/216 ns]*

## D ↔ E: FPGA signals (3.3 V LVCMOS)

| # | Signal | Dir (FPGA) | Per | Notes |
|---|---|---|---|---|
| 1–4 | `PWM_W_A`, `PWM_W_B`, `PWM_T_A`, `PWM_T_B` | out | leg | LMG1210 PWM input (high = HS on). **Must be on DDR/OSER-capable pins with PLL-derived clock**, matched routing. 100 Ω series R at the driver. |
| 5–6 | `AMP_EN_W`, `AMP_EN_T` | out | channel | D input of the channel's fault latch (74LVC1G74). |
| 7–8 | `AMP_CLK_W`, `AMP_CLK_T` | out | channel | Latch clock: rising edge loads AMP_EN into Q = the LMG1210 EN of both drivers. Ignored while FAULT is low. |
| 9–10 | `FAULT_W_n`, `FAULT_T_n` | in | channel | Low = OCP, DC or not-armed (after the Schmitt). Gates are already off in hardware when this is low. |
| 11–12 | `DC_W_n`, `DC_T_n` | in | channel | Low = hardware DC detector tripped (distinguishes DC from OCP). Open-drain with a **4.7 kΩ** pull-up (≥ 2.6 V against the unconfigured ECP5's 150 µA pull-down). |
| 13 | `AMP_ARM` | out | shared | High = allow either latch to be set. A 10 kΩ pull-down holds both bridges off until the FPGA is configured. |
| 14–16 | `VB_CS_n`, `VB_SCLK`, `VB_SDO` | out/out/in | — | ADS7042 VBUS ADC, SCLK ≤ 16 MHz, sampled once per PWM period (576 kS/s) on CS falling. E: VB_CS_n now on ball P4. |
| 17–20 | `IS_CS_n`, `IS_SCLK`, `IS_SDI`, `IS_SDO` | out/out/out/in | — | ADS7038-Q1 (I-sense ×4, NTC ×4), SCLK ≤ 60 MHz, 1 MSPS. |
| 21–27 | `PF_CS_n`, `PF_SCLK`, `PF_SDI`, `PF_SDO_WA`, `PF_SDO_WB`, `PF_SDO_TA`, `PF_SDO_TB` | out×3 / in×4 | — | Optional-population 2 × ADS8353 (shared CS/SCLK/SDI). **Pins must be reserved even when the ADCs are not fitted** (R-51 "without a respin"). |

**Pin count: 20 required + 7 reserved for the optional sense = 27.** Reductions E may take: share SCLK between the ADS7042 and ADS7038 (both run ≤ 16 MHz; −1); drop `DC_x_n` and infer DC from FAULT + I-sense data (−2). Floor: 17 + 7.
This replaces architecture.md's "8 PWM lines … 2 OC trip lines": **4 PWM** (LMG1210 PWM mode) plus the latch/fault set above.

**Agreed with block E (2026-11-07):** E-pinmap.md (ECP5 bank 6/7) now carries all 27 signals of this table, including the 7 reserved. Series resistors: 330 Ω on FAULT_x_n, 1 kΩ on DC_x_n. E adds 4.7 kΩ pull-ups on the three ADC CS lines. NTCs confirmed on ADS7038 AIN4–7; RP2350 ADC4–7 are spare. VDRV good reaches the FPGA over the RP2350 link; that is acceptable because the hardware latch keeps the bridge off independently. *(Superseded: fsw is 576 kHz; see "fsw locked" below.)* fsw at the time: E sizes the noise shaper for 448 kHz, with 512 kHz as the fallback if R-51 is not met (its first-order estimate: 448 kHz is ≈ 5 dB worse than 512 kHz at order 5). The noise-shaper simulation with this LC filter is still open in block E.

### Gateware requirements arising from block D (for block E)
1. **Start-up:** VDRV good → wait ≥ 200 µs (LMG1210 tSTLS 150 µs max) → AMP_ARM high → AMP_EN = 1 + clock → hold PWM low ≥ 50 µs (bootstrap charge, BTL output 0 V) → start at 50 % duty (BD idle). Mute until VBUS, VDRV and FPGA config are valid (R-34). **Ramp the duty from 0 % to 50 % (BD idle) over ≥ 1 ms rather than stepping it** (second-pass m-5: a step reaches 0.42 V of the short detector's 1 V threshold, and ramping avoids a pop).
2. **Fault handling:** FAULT_x_n low → gates are already off. The FPGA logs it and stops that channel's PWM. Re-arm (AMP_CLK with AMP_EN = 1) only after FAULT_x_n is high again, and then cycle-by-cycle or with back-off policy (R-54). DC fault: stay off until power cycle or user action.
3. **Duty clamp 8–92 %** (hardware safety: bootstrap refresh) → minimum leg pulse ≥ 139 ns at 576 kHz.
4. **Dead-time compensation** (needed for R-51 open-loop THD): uncompensated, ≈ 18 ns effective dead time at 576 kHz gives ≈ 1.5 % H3 at 50 W into 8 Ω. Shift each hard-switched edge by the per-board calibrated effective td (spread ≈ 14–24 ns), using the current sign from the I-sense ADC; calibrate with the post-filter sense (fitted on all prototypes).
5. **Bus feedforward** from the ADS7042 (≥ 480 kS/s, PWM-synchronous). Account for the 72 kHz RC pole and the ±2 % divider gain (calibrate).
6. **Software DC detector** on the I-sense data: |mean current| over 50 ms > ≈ 1 A → shut down (finer and faster than the hardware net).
7. **Subsonic high-pass ≥ 15 Hz on both channels** (otherwise full-scale content below about 5 Hz trips the hardware DC detector).
8. **HF power limiter:** Zobel dissipation ≤ 1 W (full-scale sine > 15 kHz must be limited).
9. **Thermal:** NTC FET region derate 95 °C / shut down 110 °C; inductor region derate 100 °C / shut down 115 °C (use B25/100 = 3455 K above 85 °C).
10. **Auto-idle (recommended):** after N s of digital silence, ramp to 50 % duty, then disable (AMP_EN = 0). Saves ≈ 3.4 W at 576 kHz (IGB070; ≈ 7.7 W with the IGC033 fallback). Wake within ≤ 10 ms with the start-up sequence (pop-free in BD).
11. **Noise shaper:** use the LC response in D-output-filter-caps.md (f0 60 kHz, Q 0.53/1.06 at 4/8 Ω, open-load peak +23 dB at 54 kHz with the Zobel).

## C → D: supplies

| Rail | Voltage | Load from block D | Notes |
|---|---|---|---|
| **VDRV** | **7.0 V ± 5 %** (C: 6.85–7.16 V worst case ✓) | **IGB070S10S1: 48 mA at 576 kHz** (39 at 448, 57 at 768, 78 at 1 MHz); IGC033 fallback 76 mA at 576 kHz → **spec ≤ 150 mA kept** | 4 × LMG1210 VIN. 0.34 W at VDRV (≈ 0.40 W from VBUS). VDRV_PG to RP2350 GPIO33. *[changed 2026-11-08: 76 → 48 mA]* |
| **3V3_A** (agreed with block C: its own TPS7A2033PDBVR LDO from +5V, C-3v3a-ldo.md; always on with +5V, including USB-only power; **placed in block D's sensing region**, C's output caps + D's local decoupling) | 3.3 V ± 1.5 %, 7 µV rms | **≤ 15 mA** (4 × INA241 12.8 mA, threshold ladders 0.2, NTCs 0.7, ADC AVDDs 0.9) | **Ratiometric reference** for current sense, OCP thresholds and both ADCs. VBUS feedforward accuracy depends on its stability (absolute). Not shared with 3V3_Q, so sense currents cannot modulate the DAC reference. |
| +3V3 | 3.3 V | **≤ 85 mA** (TLV3502 ×16 comparators: 8 OCP + 8 short-detect, 51 typ / 80 max; logic, LMV393, ADC DVDD, pull-ups) *[changed: was ≤ 45 mA]* | |
| +5V | 5 V | **≈ 24 mA** (post-filter sense now fitted on all prototypes; user decision E) | 2 × ADS8353 AVDD + 4 × OPA836 |

## B ↔ D: VBUS
- **VBUS load (amp side), IGB070S10S1, 576 kHz, 20 ns setting, both channels switching:** idle **≈ 3.4 W** (FETs 1.80 W + inductor core placeholder 1.6 W + divider 0.04 W) plus gate drive ≈ 0.40 W through C's VDRV buck → **≈ 3.8 W of VBUS power at zero signal (≈ 80 mA)**. At 46 W into 4 Ω (one channel, the other idle): losses ≈ 2.29 + 0.90 + 1.6 + 0.1 + 0.40 = 5.3 W → efficiency ≈ **90 %** (R-33a assumes 90 % ✓; better if the inductor core loss is below the 0.4 W/part placeholder). IGC033 fallback: ≈ 8.3 W idle, ≈ 84 %. *[changed 2026-11-08: was 8.3 W / 84 % with IGC033]*
- **Audio-frequency bus current per channel (bulk ripple, BTL sine):** mean P/VBUS with a 2f component of equal amplitude → 46 W/4 Ω: 0.96 A mean, **0.68 A rms at 2f**; 144 W/4 Ω: 3.0 A mean, **2.1 A rms at 2f** (40 Hz–40 kHz). Both channels: B sizes the bulk ripple rating for ≈ 2.2 A rms continuous (R-33a level) and 4.2 A rms in bursts. The 480 kHz component (1.6–2.9 A rms per channel) is carried by D's ceramics (D-bridge-decoupling.md), not B's bulk.
- **Placement:** at least two of B's bulk electrolytics within about 30 mm of each channel's bridge (phase 4).
- **VBUS overvoltage scheme: AGREED with block B 2026-11-07** (same wording in B-interfaces.md / B-output.md; details and energy budget in D-vbus-tvs.md). 63 V (KZN bulk, no published surge rating) is the absolute VBUS limit.
  1. **Energy:** ≤ 12.4 mJ can return to VBUS from the amp (4 inductors at 16 A, 5 µs of regen at the stop, filter caps) → ΔV ≈ 0.04 V on 6 mF at 55 V.
  2. **Gateware stop** at VBUS ≥ **55 V** (block D ADS7042, < 5 µs); restart < **52 V**.
  3. **Converter output OVP (block B):** UCC2897A LINEOV fed from the averaged N5 forward voltage (≈ VBUS/2), works without the opto. Trips at ≈ 53.3 V (51.2–55.4 V), then hiccups; covers a feedback failure (D → DMAX). ACF load dump (≤ 1.34 A current-limited step) overshoots by ≈ 24 mV.
  4. **TVS, fast spikes only:** **SMBJ51A** at each bridge (block D, Littelfuse C1973217) and **SMCJ51A** at the bulk (block B, MDD C408371, VC 82.4 V at 18.2 A). VBR 56.7–62.7 V: no conduction at the 55 V stop, onset ≤ 63 V; VC 82.4 V + ≈ 10 V overshoot = 92 V < 100 V GaN.
  - Ratings at 82.4 V: LM5013/LM5017 100 V, GaN 100 V, ceramics 100 V, ADS7042 divider 3.19 V ✓.
  - Residual risk (recorded by B): a feedback failure while Vin is 38.4–41.9 V with the converter in DCM could pass 56.7 V, and the SMCJ51A could then fail short.
- Backfeed: OCP shutdown returns ≤ 5.1 mJ of inductor energy into VBUS (ΔV ≈ 21 mV on 5 mF). Sustained regen is handled per R-35 (firmware stop at 55 V; B's SRs do not conduct backwards).

## D → G / mechanical / phase 4
- Output connectors: 2 × MAX MX2EDGRC-5.08-02P (15 A), with silk "WOOFER + − 4–8 Ω", "TWEETER + − 4–8 Ω (HPF)".
- **Large parts for the floorplan:** 4 × SER2915H inductors 27.9 × 19.8 × 15.4 mm (≈ 22 cm²; alternative XAL1510 15.2 × 16.2 mm), 2 × TDK B32774D4226K 22 µF PP boxes (22 × 36.5 × 31.5 mm each, 27.5 mm pitch; user decision B) instead of 1 × MEB 33 µF box 32 × 28 × 14 mm (THT, 27.5 mm pitch), 8 × GaN 3.2 × 3.0 mm, 4 × LMG1210, plus the thermal pad / aluminium path to the back panel under the bridges (R-61; analysis assumes ≤ 4 °C/W per channel region, and still meets Tj ≤ 125 °C at 15 °C/W).
- 4-layer minimum, power return on L2 under each bridge (LMG1210 do's).

## Proposed changes to architecture (for the lead / user)
1. *(Superseded by "GaN back to IGB070S10S1 at 576 kHz (user decision 2026-11-08)" below: the part is IGB070S10S1, IGC033S10S1 is the fallback.)* **GaN FET: Infineon IGC033S10S1 (user decision 2026-11-07; the earlier recommendation was IGB070S10S1, kept as the rejected alternative in D-gan-fet.md), not the Innoscience INN100 parts.** [Original reasoning for IGB070 follows.] Reason: Qoss dominates loss at 12 A. Idle FET loss is 2.0 W for both channels vs 4.8–5.1 W for the 3 mΩ Innoscience/IGC033 parts, and LCSC reports no lifecycle for any Innoscience part (C55014508's LCSC page is "Part not found"; no datasheet exists for INN100EA035A-C). **Stock is 80 against a build need of 44: buy early.** Fallback: IGC033S10S1 (985 in stock, different footprint, +3 W idle). → architecture.md block diagram text "4× INN100 GaN" becomes "4× IGB070S10S1".
2. **LMG1210 in PWM mode: 4 PWM lines instead of 8**, plus the latched-fault interface above (FPGA pins: 20 + 7 reserved).
3. **R-35 TVS stand-off 51 V (SMBJ51A at each bridge, SMCJ51A at the bulk; VBR 56.7–62.7 V, VC 82.4 V), not 56–58 V or the 54 V first proposed: see the VBUS overvoltage scheme above.** SMBJ58A clamps at 93.6 V, which plus switching overshoot exceeds the 100 V GaN rating. A local TVS at each bridge (block D), plus B's.
4. **Power-stage NTCs (4) go to block D's ADS7038 (read by the FPGA)**, not to the RP2350 ADC. This frees RP2350 ADC inputs for the knobs and puts over-temperature next to the bridge enable.
5. **New quiet rail 3V3_A ≤ 15 mA** for block D's ratiometric sensing: agreed with C as a dedicated TPS7A2033 from +5V.
6. **VDRV = 7.0 V ± 5 %, ≤ 150 mA** (IGC033S10S1; R-33a "Gate drive" row: 0.43 W at 448 kHz, 0.89 W at 1 MHz, at VDRV).
7. **Idle power:** ≈ 3.8 W of VBUS power at zero signal (IGB070S10S1, 576 kHz, incl. gate drive and the 1.6 W inductor placeholder). Recommend auto-idle and noting it in R-33a.
8. **fsw baseline 576 kHz** (ECP5 ×12 grid); 768 kHz option; 448 kHz only on E's ×14 option.

## User decisions (2026-11-07)
- **A.** GaN = **IGC033S10S1** (985 in stock). D audits reworked (D-gan-fet.md, D-lmg1210.md, D-bootstrap.md, D-driver-passives.md); IGB070S10S1 kept as the rejected alternative.
- **B.** Tweeter HPF = **2 × 22 µF polypropylene TDK B32774D4226K (44 µF)** (D-tweeter-hpf.md).
- **C.** TVS: 54 V accepted in principle, then revised to **51 V** so that onset stays ≤ the 63 V bulk rating; one VBUS overvoltage scheme with block B (above).
- **D.** Inductor SER2915H vs XAL1510: deferred to the phase 4 floorplan; both stay audited.
- **E.** Post-filter sense **fitted on all 5 prototypes**.


## Review response (phase 1 review, design/gates/review-phase1-D.md, 2026-11-07)
**Numbers in this file that changed** (C and E depend on them): dead-time setting 16 → **20 ns** (≈ 15 ns effective); duty clamp 3–97 % → **8–92 %** (E: gateware item 3); OCP → **two regimes** (≈ 50 ns hard short / ≈ 218 ns, 14.9 A ramp); **+3V3 load ≤ 45 → ≤ 85 mA** (C); idle VBUS power 5.2 → **≈ 6.2 W**, efficiency at 46 W/4 Ω 89 → **≈ 87 %** (lead: R-33a); VDRV 62 → **61 mA** at 448 kHz (≤ 150 mA spec unchanged); DC-detect trip 28 → 23 ms at 48 V. FPGA pins unchanged (the short detector feeds the existing FAULT_x_n).

| Finding | Response |
|---|---|
| **M1** bootstrap refresh at the 3 % clamp | **Fixed.** Duty clamp widened to 8–92 % (LO ≥ 153 ns → 0.107 A, BAT46WJ VF 0.54/0.64 V) and HS gate pull-down 10 k → 100 kΩ (Q 17.4 → 16.4 nC). Equilibrium HB−HS **≥ 4.03 V** worst case (≥ 3.80 V ROC, ≥ 0.38 V above UVLO). R-50: M_max 0.84 → 101 W into 8 Ω ✓. Bring-up item added (scope HB−HS at 20 Hz full scale). D-bootstrap.md, D-lmg1210.md, D-driver-passives.md. Diode kept (a lower-VF 100 V Schottky was not needed). |
| **M2** INA241 1 µs CM hold | **Fixed with a second detector.** New D-short-detect.md: 47 pF/1 kΩ differentiator per output node + TLV3502 window → the same fault latch; trips on any node step ≥ 1 V or slew > 21 V/µs, ≈ 50 ns from the short, peak ≤ 13.7 A. Two regimes written in D-current-sense.md; residual (sub-1 V CM step triggering the hold) ≤ ≈ 21 A, bench item to measure the hold threshold. Inductor hot check at 16.7/21 A in D-output-inductor.md (Coilcraft derating pending). **Proposed R-54 wording:** "a short at an output terminal turns all four FETs of that channel off within ≤ 100 ns of the short; a gradually rising overcurrent trips at 15 A ± 1 A with ≤ 250 ns from threshold to all gates off; peak device current ≤ 17 A in both cases." |
| m1 effective dead time | Fixed: effective ≈ 15 ns stated; setting raised to 20 ns (20.0 kΩ, the characterised point) so the ZVS window is back to ≈ 15 ns; loss tables recomputed (D-gan-fet.md). |
| m2 typical IOH in the model | Fixed: t_sw 11 ns at IOH min; tables recomputed; panel path stated as required at every fsw for 144 W (Tj 124 °C without it at 448 kHz). |
| m3 overshoot ≈ 10 V | Fixed: 21 V at 16 A / 1 nH; clamp case 103 V on the 120 V pulsed rating, stated and accepted; phase 6 loop target ≤ 1 nH (D-gan-fet.md, D-vbus-tvs.md). |
| m4 LMV393 VICR | Fixed: R_bot 82.0 k / R_bot' 88.7 k → max node 2.21 V ≤ 2.5 V (D-dc-detect.md). |
| m5 overdrive build-up | Fixed: +20 ns → ramp regime ≈ 218 ns (D-current-sense.md, D-ocp-logic.md); hard shorts use the new 50 ns path. |
| m6 core-loss placeholder | Placeholder raised to 0.4 W/part (budget above); the Coilcraft calculator run is an action for the lead/user (interactive tool), recorded in D-output-inductor.md. |
| m7 VBST max | Fixed: 5.24 V stated (0.01 V under the 5.25 V ROC, 0.26 V under 5.5 V) (D-bootstrap.md). |
| m8 inductor stock | Noted: order/reserve SER2915H-103KL early (D-output-inductor.md). |
| n1 Gowin pull-up text | Fixed (ECP5 pull-down default) in D-driver-passives.md. |
| n2 C's VDRV table | Not a block D file: C-interfaces.md should carry 61–127 mA, ≤ 150 mA (lead/C to update). |
| n3 D_VCL leakage | Noted in D-vbus-adc.md (≈ 1.2 LSB, calibrated). |
| n4 1 kΩ bootstrap path | Noted in D-bootstrap.md (≈ 0.1 nC/cycle). |
| n5 shunt ESL | Noted in D-current-sense.md (open question 3). |
| n6 TVS between VWM and VBR | Noted in D-vbus-tvs.md. |
| n7 gateware safety items | Duty clamp value updated (item 3); E to update E-interfaces.md to 8–92 %. |
| IGB070 leftovers in D-lmg1210 / D-driver-passives | Fixed: both files rewritten for IGC033S10S1; IGB070 now appears only as the rejected alternative in D-gan-fet.md. |

## fsw choice on the ×12 grid (1.695 ns, 589.824 Mb/s): 576 kHz (2026-11-07, lead request; agreed with block E)
Candidates are frequencies that divide the grid exactly. IGC033S10S1, 20 ns dead-time setting (≈ 15 ns effective), t_sw 11 ns, L 10 µH, C 700 nF/side. Tj = 4 °C/W panel path / 15 °C/W no panel. Noise = in-band shaper noise relative to 576 kHz at order L = 5, using E's scaling Δ²/OSR^(2L+1) with Δ = 1/N and OSR = fsw/48 kHz. Beat = |fsw − f_B| with block B's converter 400 kHz ± 6 % (376–424 kHz, B-interfaces.md).

| fsw | N (steps) | 48 kHz-locked | Idle FET loss, both ch | 46 W/4 Ω per ch (Tj) | 144 W/4 Ω per ch (Tj) | Ripple / CM ripple | Carrier atten. at 2·fsw | Noise vs 576 k | Beat with B | R-53 (400 k–1 M) |
|---|---|---|---|---|---|---|---|---|---|---|
| 384 kHz | 1536 | 8× | **3.08 W** | 2.14 W (70/96 °C) | 3.02 W (76/115 °C) | 3.12 A pp / 1.45 V pp | −44 dB | **+15.8 dB** | **0 Hz possible (384 ∈ 376–424)** ✗ | ✗ below floor |
| 512 kHz | 1152 | no (10.67×) | 5.02 W | 3.00 W (75/111 °C) | 4.02 W (82/133 °C) | 2.34 / 0.82 | −49 dB | +4.6 dB | 88–136 kHz ✗ (< 100 kHz) | ✓ |
| **576 kHz** | **1024** | **12×** | **6.02 W** | **3.43 W (78/119 °C)** | **4.52 W (85/141 °C)** | **2.08 / 0.65** | **−51 dB** | **0 dB** | **152–200 kHz ✓** | ✓ |
| 768 kHz | 768 | 16× | 9.04 W | 4.74 W (86/141 °C) | 6.03 W (95/167 °C) | 1.56 / 0.36 | −56 dB | −11.2 dB | 344–392 kHz ✓ (but 768 vs B's 2nd harmonic 752–848: 0–80 kHz ✗) | ✓ |

**Choice: 576 kHz.**
- It is the only candidate that meets the beat rule with B (> 100 kHz) and R-53, and that is 48 kHz-locked. So whether audio-locking is strictly required (the 512 kHz question) does not matter here: 512 kHz fails the beat rule anyway.
- 384 kHz would save ≈ 2.9 W of idle loss, but it lands inside B's 376–424 kHz band (a beat down to DC, unless B were synchronised across the isolation barrier: B's SYNC pin is on the primary, which would need an isolator channel, and B's transformer is designed for 400 kHz). It is also 15.8 dB worse in shaper noise and below R-53's floor.
- Residual beat at 576 kHz: 2·fsw (the BD differential ripple at 1152 kHz) against B's 3rd harmonic (1128–1272 kHz) can come within 0–144 kHz. Both are low-amplitude harmonics; noted for the phase 8 EMI/SI review.
- Costs at 576 kHz:
  - idle ≈ 8.3 W of VBUS power (FETs 6.02 + inductor placeholder 1.6 + gate drive 0.63 + divider);
  - ≈ 84 % efficiency at 46 W/4 Ω;
  - R-61 panel path mandatory (Tj 119 °C without it at 46 W/4 Ω).
- Mitigations (user decision): gateware auto-idle; XAL1510-682MED 6.8 µH → idle FET 4.69 W.
- **Block E confirmed 576 kHz (N = 1024)** and supplied its noise-shaper estimate (E-interfaces.md, "PWM fsw choice and noise-shaper estimate"). Ideal in-band quantisation noise at the speaker, NTF (1 − z⁻¹)^L, 20 Hz–20 kHz: at 576 kHz, **L = 4: 3.8 µV (1.5 µV A); L = 5: 0.75 µV (0.29 µV A)**. That is far below R-51's ≤ 150 µV A open-loop and ≤ 60 µV closed-loop, so edge quantisation does not limit R-51 at 576 kHz. 384 kHz is 15.7 dB worse (consistent with the scaling above). E recommends L = 5. The fsw choice is therefore loss vs the beat with block B, as tabled.


## GaN back to IGB070S10S1 at 576 kHz (user decision 2026-11-08)
- **Part:** IGB070S10S1 (C44179579). **Order early: 44 needed (40 + 10 % attrition) against 80 in stock.** Fallback IGC033S10S1 (C41381300, 985) needs a **different land pattern** (PG-TSON-6 3 × 5 mm vs PG-TSON-4 3.2 × 3.0 mm). Phase 6 reserves the 3 × 5 mm courtyard at each FET site. All other block D parts (driver passives, bootstrap, sense, filter) suit both FETs unchanged.
- **Numbers that changed** (C and E informed):

  | Item | IGC033 (2026-11-07) | **IGB070 (2026-11-08)** |
  |---|---|---|
  | Idle FET loss, both channels, 576 kHz | 6.02 W | **1.80 W** |
  | Idle VBUS power incl. inductors and gate drive | ≈ 8.3 W | **≈ 3.8 W** |
  | 46 W/4 Ω loss per channel; Tj panel/no panel | 3.43 W; 78/119 °C | **2.29 W; 72/100 °C** |
  | 144 W/4 Ω loss per channel; Tj | 4.52 W; 85/141 °C | **3.74 W; 83/129 °C** (panel path still required) |
  | Efficiency at 46 W/4 Ω | ≈ 84 % | **≈ 90 %** |
  | VDRV load | 76 mA | **48 mA** (spec ≤ 150 mA unchanged) |
  | Effective dead time | ≈ 15 ns | **≈ 18 ns (14–24)** |
  | OCP: hard short / ramp | 50 / 218 ns | **48 / 216 ns** |
  | Bootstrap HB−HS min / max | 3.97 / 5.24 V | **4.09 / 5.32 V** (max is 0.07 V over the LMG1210 ROC, 0.18 V under abs max; accepted, D-bootstrap.md) |
  | Switching overshoot at 16 A, 1 nH | 21 V | **27 V** (clamp case 109 V on the 120 V pulsed rating) |
- **Unchanged:** FPGA pins and gateware items (duty clamp 8–92 %, start-up, compensation, limiters); +3V3 ≤ 85 mA; 3V3_A ≤ 15 mA; +5V ≈ 24 mA; the VBUS overvoltage scheme.

## fsw reopened: block B's converter moved to 620 kHz ± 10 % (2026-11-08, from block E; pending B)
576 kHz now lies inside B's 558–682 kHz band, so the beat can reach 0 Hz. E's options are in E-interfaces.md ("PWM fsw vs block B's new 620 kHz converter"). Block D's figures for the two candidates, with **IGB070S10S1** (E's "9 W" for 768 kHz was the IGC033 figure):

| | 576 kHz (needs B at ≈ 712–775 kHz ± 5 %, E's option 1) | 768 kHz (fallback if B stays at 620 kHz ± 5 %) |
|---|---|---|
| Idle FET loss, both channels | 1.80 W | **3.34 W** |
| Idle VBUS power (incl. 1.6 W inductor placeholder, gate drive) | ≈ 3.8 W | ≈ 5.5 W |
| 46 W/4 Ω per channel; Tj panel / no panel | 2.29 W; 72/100 °C | 3.10 W; 77/114 °C |
| 144 W/4 Ω per channel; Tj | 3.74 W; 83/129 °C | 4.83 W; 90/149 °C (panel path required) |
| Efficiency at 46 W/4 Ω | ≈ 90 % | ≈ 87 % |
| VDRV load | 48 mA | 57 mA |
| Bootstrap HB−HS min (8–92 % clamp) | 4.09 V (LO ≥ 113 ns) | 4.03 V (LO ≥ 78 ns, 0.12 A) ✓ |
| Inductor ripple / CM ripple | 2.08 A pp / 0.65 V pp | 1.56 A pp / 0.36 V pp |
| Shaper noise (E) | reference | −11 dB |

**Block D preference: E's option 1** (B moves to ≈ 740 kHz ± 5 %, amp stays at 576 kHz), worth ≈ 1.5 W of idle and ≈ 3 points of efficiency. 768 kHz is acceptable as the fallback, since no block D part changes. Decision pending B's answer.

## fsw locked: 576 kHz (2026-11-08, lead decision; block B confirmed)
Block B's converter is crystal-synchronised at **737.28 kHz ± 40 ppm** (7.3728 MHz ÷ 10 into the UCC2897A SYNC pin). Low-order products with 576 kHz are 161, 253 and 415 kHz, all ≥ 100 kHz ✓. **Baseline: fsw = 576 kHz with IGB070S10S1**; figures as in the "GaN back to IGB070S10S1" section: idle FET loss 1.80 W, idle VBUS power ≈ 3.8 W, ≈ 90 % at 46 W/4 Ω, VDRV 48 mA.
Fault mode: if B's sync clock fails, the converter free-runs at 590–708 kHz, so the beat with 576 kHz can fall to 14 kHz. E detects this from ACF_PULSE. Block D suggests that gateware, on that flag, either moves the amp to 768 kHz (beat ≥ 60 kHz against 708 kHz; acceptable as a degraded mode, idle 3.34 W) or mutes. **E has chosen: when ACF_PULSE is outside 737.28 kHz ± 0.5 %, the FPGA flags a converter clock fault. Lead's hard rule: the amp does not start, or ramps to zero and mutes; the fault is latched and reported over the network** (E-interfaces.md). The 768 kHz degraded mode is only a possible later firmware option. Block D hardware is unchanged.
B's VBUS-facing side is unchanged: CC limits 0.44 / 0.94 / 1.30 A, the overvoltage scheme as agreed, bulk ripple 0.35–0.55 A pp at 737 kHz.


## Second-pass review (design/gates/rereview-phase1-CGD.md, 2026-11-08): block D PASS
- m-3: the ≤ 1 nH commutation loop, verified by phase 6 extraction, is a hard placement rule; optional DNP RC snubber per half-bridge (470 pF + 2.2 Ω; 0.62 W each if fitted) (D-bridge-decoupling.md).
- m-5: short-detector notes recorded (D-short-detect.md): ripple 1.5 V/µs at 576 kHz, real fast-step threshold ≈ 1.5 V, path ≈ 51 ns, speaker-lead open at ≥ ≈ 14 A is a benign trip, start-up duty must ramp (gateware item 1 updated).
- n-1: VBST 5.32 V condition stated (long LO and ≥ 14 A reverse LS current at once) (D-bootstrap.md).
- Stale text: the 448 kHz noise-shaper paragraph and the IGC033 "Proposed changes 1" are marked superseded here; D-current-sense.md open question 1 is marked superseded.

## VDRV re-check after block C's ripple-network change (2026-11-08): 7.01–7.12 V typ, 6.87–7.27 V worst, LM5017 at 230–410 kHz
- LMG1210 VIN ROC 6–18 V (abs 20 V): 6.87–7.27 V ✓.
- Internal LDO headroom at 6.87 V: 6.87 − 5.25 (VDD max) = **1.62 V** ≥ 0.75 V max dropout at 100 mA (LMG1210 p.5) ✓; at 12 mA per driver the dropout is far lower.
- VDD stays 4.75–5.25 V (LDO-regulated, independent of VIN), so the bootstrap figures are **unchanged: HB−HS min 4.09 V, worst-case max 5.32 V** (VBST is set by VDD, VF and IL·Rds(on), not by VIN).
- LDO dissipation at 7.27 V: (7.27 − 5.0) × 12 mA = 27 mW per driver; driver Tj rise ≤ 4 °C ✓.
- The LM5017's ripple at 230–410 kHz on VIN is attenuated by the LMG1210's internal LDO and the VDD caps. Its harmonic interaction with the 576 kHz amp carrier is block C's beat check.

**PoE-loss and VBUS-valid gateware rule (third-pass MAJOR-1, lead 2026-11-08; identical text in B-, D- and E-interfaces.md):**
1. **VBUS valid.** The FPGA reads VBUS from block D's ADS7042 (576 kS/s). `VBUS_VALID` is **set** when VBUS > 44.0 V continuously for ≥ 10 ms after start-up. It is **cleared** only when PoE loss is declared, or when VBUS < 40.5 V by the ADC rule below. Normal burst sag (≥ 43.2 V, R-33) does not clear it.
2. **Hardware detector.** `POE_LOSS_N` (block B, open-drain into FPGA A6) is low when VBUS < 39.5 V (38.5–40.5 V), releasing above 41.1 V (40.0–42.2 V), 0.31 ms filter (B-vbus-droop.md). It is also asserted during every start-up ramp, so the FPGA **ignores `POE_LOSS_N` until `VBUS_VALID` has first been set**. After that, `POE_LOSS_N` low (level or falling edge) means PoE lost, and the FPGA latches it.
3. **ADC detector.** VBUS < 40.5 V on every ADS7042 sample for ≥ 0.5 ms (≥ 288 consecutive samples), while `VBUS_VALID` is set, ⇒ PoE lost.
4. **PoE lost = `POE_LOSS_N` low (after the step-2 gate) OR the step-3 ADC rule OR `PD_PG_N` high.** The FPGA latches the event. `PD_PG_N` rises 45–140 ms after LINEUV, so it is a slow backstop, not a prompt trigger; `POE_LOSS_N` and the ADC rule are the prompt paths.
5. **Action**, in gateware, independent of the RP2350:
   - drop `HP_EN` and `LO_EN` at once (relays open);
   - start block D's R-34 mute ramp to zero, completing in ≤ 5 ms, then stop switching;
   - report the event to the RP2350 over the link, and from there to the network.
   Restart only through the normal start-up sequence, after `VBUS_VALID` is set again.
6. **Calibration (block D, 2026-11-08).** The 44.0 V and 40.5 V thresholds apply to **calibrated** VBUS readings: the same one-time gain calibration as bus feed-forward (`D-vbus-adc.md`). Until a gain is stored, the ADS7042 divider's ±2 % error (≈ ±0.8 V at 40 V) is covered by **widened thresholds**:
   - set `VBUS_VALID` at raw > **44.9 V** (= 44.0 V × 1.02), so the flag can never be set early;
   - clear at raw < **39.7 V** (= 40.5 V / 1.02), so normal sag can never trip it.
   A real loss is still caught as VBUS keeps falling, and `POE_LOSS_N` (39.5 V hardware) and `PD_PG_N` act independently. Amp start is allowed on the widened thresholds (bring-up); the calibrated values take over once stored. **Agreed by the lead, 2026-11-08** (44.9 V stays below the 47.0 V static VBUS minimum, 48 V − 2 %).

Block D check of the rule against its hardware: the ADS7042 divider (÷ 25.8, LSB 20.8 mV) puts 40.5 V at 1.570 V and 44.0 V at 1.705 V, both well inside the 3.3 V range. Its ±2 % gain tolerance (≈ ±0.8 V at 40 V) is covered by the one-time calibration already required for feedforward (D-vbus-adc.md). 288 samples at 576 kS/s = 0.5 ms ✓.

**Block B hardware droop comparator (B, 2026-11-08), next to the 55/52 V overvoltage stop:** `POE_LOSS_N` goes low below **39.5 V (38.5–40.5 V)** and is released above 41.1 V (40.0–42.2 V; ±2.6 %, fourth pass; output FET 2N7002), filtered at 0.31 ms. It never asserts in the ≤ 10 % burst sag (≥ 43.2 V). After PoE loss at 60 W it asserts in 18–41 ms, and the rails then hold **≈ 150 ms** (B's fourth-pass figure: from the 38.5 V worst-case assert level down to block C's ≈ 30.2 V UVLO-off including divider tolerance; supersedes ≈ 160 ms to 29.6 V), with the amp muted within 5 ms. The shared rule text (step 2) now carries these figures (lead update 2026-11-08). B's earlier 45.0/43.0 V VBUS_VALID proposal is **withdrawn**: B-interfaces.md now carries the shared rule verbatim (items 1–6).
