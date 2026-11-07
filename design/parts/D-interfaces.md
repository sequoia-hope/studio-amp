# Block D — interfaces to the other blocks, and proposed changes to the architecture

Block D: two identical BTL GaN channels (woofer `amp_woofer`, tweeter `amp_tweeter`) plus `vbus_sense`. Per channel: 2 × LMG1210 (PWM mode), 4 × IGC033S10S1 (user decision 2026-11-07), 2 × SER2915H-103KL + 5 mΩ/INA241A1 sense, TLV3502 window OCP, diode-AND + 74LVC1G17 + 74LVC1G74 fault latch, LMV393 DC detect, 14 × 100 nF C0G filter caps, Zobel 10 Ω/100 nF, 2 × NTC, SMBJ51A. The tweeter channel adds a 2 × 22 µF polypropylene series HPF cap. Shared: ADS7042 (VBUS), ADS7038-Q1 (4 × I, 4 × NTC), 2 × ADS8353 + 4 × OPA836 (post-filter sense; fitted on all prototypes per user decision E).

## Baseline operating point
- **fsw = 448 kHz** (updated for the ECP5: 688.128 Mb/s ODDRX2F grid, 1.453 ns steps, 1536 per period; 448 kHz = 48 kHz × 28/3, audio-locked). R-53 range 400 kHz–1 MHz ✓. Per-build option **672 kHz** (14 × 48 kHz, 1024 steps): +1.9 W idle FET loss, +0.8 W per channel at 46 W. 512 kHz (1344 steps) in between. Loss model (10 µH, 12 ns): idle both channels 1.72 / 2.24 / 3.61 W at 448 / 512 / 672 kHz. The noise-shaper trade (lower OSR vs finer relative step at 448 kHz) is block E's to confirm.
- **BD modulation, both legs of a channel switching at fsw; dead time 16 ns** (LMG1210 resistors 31.6 kΩ; raised from 12 ns with the change to IGC033S10S1).
- **Duty clamp 3–97 %** per leg (M ≤ 0.94), for bootstrap refresh and minimum pulse (D-lmg1210.md).
- **OCP trip ±14.9 A ± 0.7 A per leg, ≤ 198 ns to all gates off (IGC033 turn-off included)** (hardware, latched); DC detect in hardware (|DC| ≥ 6 V, ≤ 60 ms at ≥ 24 V).

## D ↔ E: FPGA signals (3.3 V LVCMOS)

| # | Signal | Dir (FPGA) | Per | Notes |
|---|---|---|---|---|
| 1–4 | `PWM_W_A`, `PWM_W_B`, `PWM_T_A`, `PWM_T_B` | out | leg | LMG1210 PWM input (high = HS on). **Must be on DDR/OSER-capable pins with PLL-derived clock**, matched routing. 100 Ω series R at the driver. |
| 5–6 | `AMP_EN_W`, `AMP_EN_T` | out | channel | D input of the channel's fault latch (74LVC1G74). |
| 7–8 | `AMP_CLK_W`, `AMP_CLK_T` | out | channel | Latch clock: rising edge loads AMP_EN into Q = the LMG1210 EN of both drivers. Ignored while FAULT is low. |
| 9–10 | `FAULT_W_n`, `FAULT_T_n` | in | channel | Low = OCP, DC or not-armed (after the Schmitt). Gates are already off in hardware when this is low. |
| 11–12 | `DC_W_n`, `DC_T_n` | in | channel | Low = hardware DC detector tripped (distinguishes DC from OCP). Open-drain with a 10 kΩ pull-up. |
| 13 | `AMP_ARM` | out | shared | High = allow either latch to be set. A 10 kΩ pull-down holds both bridges off until the FPGA is configured. |
| 14–16 | `VB_CS_n`, `VB_SCLK`, `VB_SDO` | out/out/in | — | ADS7042 VBUS ADC, SCLK ≤ 16 MHz, 1 MSPS, sample on CS falling. |
| 17–20 | `IS_CS_n`, `IS_SCLK`, `IS_SDI`, `IS_SDO` | out/out/out/in | — | ADS7038-Q1 (I-sense ×4, NTC ×4), SCLK ≤ 60 MHz, 1 MSPS. |
| 21–27 | `PF_CS_n`, `PF_SCLK`, `PF_SDI`, `PF_SDO_WA`, `PF_SDO_WB`, `PF_SDO_TA`, `PF_SDO_TB` | out×3 / in×4 | — | Optional-population 2 × ADS8353 (shared CS/SCLK/SDI). **Pins must be reserved even when the ADCs are not fitted** (R-51 "without a respin"). |

**Pin count: 20 required + 7 reserved for the optional sense = 27.** Reductions E may take: share SCLK between the ADS7042 and ADS7038 (both run ≤ 16 MHz; −1); drop `DC_x_n` and infer DC from FAULT + I-sense data (−2). Floor: 17 + 7.
This replaces architecture.md's "8 PWM lines … 2 OC trip lines": **4 PWM** (LMG1210 PWM mode) plus the latch/fault set above.

**Agreed with block E (2026-11-07):** E-pinmap.md (ECP5 bank 6/7) now carries all 27 signals of this table, including the 7 reserved. Series resistors: 330 Ω on FAULT_x_n, 1 kΩ on DC_x_n. E adds 4.7 kΩ pull-ups on the three ADC CS lines. NTCs confirmed on ADS7038 AIN4–7; RP2350 ADC4–7 are spare. VDRV good reaches the FPGA over the RP2350 link; that is acceptable because the hardware latch keeps the bridge off independently. fsw: E sizes the noise shaper for 448 kHz, with 512 kHz as the fallback if R-51 is not met (its first-order estimate: 448 kHz is ≈ 5 dB worse than 512 kHz at order 5). The noise-shaper simulation with this LC filter is still open in block E.

### Gateware requirements arising from block D (for block E)
1. **Start-up:** VDRV good → wait ≥ 200 µs (LMG1210 tSTLS 150 µs max) → AMP_ARM high → AMP_EN = 1 + clock → hold PWM low ≥ 50 µs (bootstrap charge, BTL output 0 V) → start at 50 % duty (BD idle). Mute until VBUS, VDRV and FPGA config are valid (R-34).
2. **Fault handling:** FAULT_x_n low → gates are already off. The FPGA logs it and stops that channel's PWM. Re-arm (AMP_CLK with AMP_EN = 1) only after FAULT_x_n is high again, and then cycle-by-cycle or with back-off policy (R-54). DC fault: stay off until power cycle or user action.
3. **Duty clamp 3–97 %** and minimum leg pulse ≥ 36 ns.
4. **Dead-time compensation** (needed for R-51 open-loop THD): uncompensated, 16 ns of dead time at 448 kHz gives ≈ 1.0 % H3 at 50 W into 8 Ω (calibrate per board with the post-filter sense, now fitted on all prototypes). Shift each hard-switched edge by td (per-board calibrated; td spread 8.5–15.5 ns) using the current sign from the I-sense ADC.
5. **Bus feedforward** from the ADS7042 (≥ 480 kS/s, PWM-synchronous). Account for the 72 kHz RC pole and the ±2 % divider gain (calibrate).
6. **Software DC detector** on the I-sense data: |mean current| over 50 ms > ≈ 1 A → shut down (finer and faster than the hardware net).
7. **Subsonic high-pass ≥ 15 Hz on both channels** (otherwise full-scale content below about 5 Hz trips the hardware DC detector).
8. **HF power limiter:** Zobel dissipation ≤ 1 W (full-scale sine > 15 kHz must be limited).
9. **Thermal:** NTC FET region derate 95 °C / shut down 110 °C; inductor region derate 100 °C / shut down 115 °C (use B25/100 = 3455 K above 85 °C).
10. **Auto-idle (recommended):** after N s of digital silence, ramp to 50 % duty, then disable (AMP_EN = 0). This saves about 4.7 W of idle power-stage loss (IGC033S10S1 at 448 kHz) from VBUS (below). Wake within ≤ 10 ms with the start-up sequence (pop-free in BD).
11. **Noise shaper:** use the LC response in D-output-filter-caps.md (f0 60 kHz, Q 0.53/1.06 at 4/8 Ω, open-load peak +23 dB at 54 kHz with the Zobel).

## C → D: supplies

| Rail | Voltage | Load from block D | Notes |
|---|---|---|---|
| **VDRV** | **7.0 V ± 5 %** (any 6.0–18 V works; 7 V minimises LDO loss) | **IGC033S10S1 (Qg 14 nC max): 62 mA at 448 kHz, 69 mA at 512 kHz, 88 mA at 672 kHz, 128 mA at 1 MHz → spec ≤ 150 mA** | 4 × LMG1210 VIN (internal 5 V LDO). 0.43 W at VDRV at 448 kHz (≈ 0.51 W from VBUS through C's LM5017). C's design is 200 mA ✓. |
| **3V3_A** (agreed with block C: its own TPS7A2033PDBVR LDO from +5V, C-3v3a-ldo.md; always on with +5V, including USB-only power; **placed in block D's sensing region**, C's output caps + D's local decoupling) | 3.3 V ± 1.5 %, 7 µV rms | **≤ 15 mA** (4 × INA241 12.8 mA, threshold ladders 0.2, NTCs 0.7, ADC AVDDs 0.9) | **Ratiometric reference** for current sense, OCP thresholds and both ADCs. VBUS feedforward accuracy depends on its stability (absolute). Not shared with 3V3_Q, so sense currents cannot modulate the DAC reference. |
| +3V3 | 3.3 V | **≤ 45 mA** (TLV3502 ×8 comparators 26 typ / 40 max, logic, LMV393, ADC DVDD, pull-ups) | |
| +5V | 5 V | **≈ 24 mA** (post-filter sense now fitted on all prototypes; user decision E) | 2 × ADS8353 AVDD + 4 × OPA836 |

## B ↔ D: VBUS
- **VBUS load (amp side), IGC033S10S1, 448 kHz, td 16 ns, both channels switching:** idle **≈ 4.7 W** (FETs 3.86 W + inductor core placeholder 0.8 W + divider 0.04 W) plus gate drive ≈ 0.51 W through C's VDRV buck → **≈ 5.2 W of VBUS power at zero signal (≈ 108 mA)**. At 512 kHz ≈ 6.2 W; at 672 kHz ≈ 8.8 W. At 46 W into 4 Ω (one channel, the other idle): losses ≈ 2.42 + 1.93 + 0.8 + 0.1 + 0.51 = 5.8 W → efficiency ≈ **89 %** (R-33a assumes 90 %: about 0.5 W short at Class 6). Auto-idle (gateware item 10) is strongly recommended.
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
1. **GaN FET: Infineon IGC033S10S1 (user decision 2026-11-07; the earlier recommendation was IGB070S10S1, kept as the rejected alternative in D-gan-fet.md), not the Innoscience INN100 parts.** [Original reasoning for IGB070 follows.] Reason: Qoss dominates loss at 12 A. Idle FET loss is 2.0 W for both channels vs 4.8–5.1 W for the 3 mΩ Innoscience/IGC033 parts, and LCSC reports no lifecycle for any Innoscience part (C55014508's LCSC page is "Part not found"; no datasheet exists for INN100EA035A-C). **Stock is 80 against a build need of 44: buy early.** Fallback: IGC033S10S1 (985 in stock, different footprint, +3 W idle). → architecture.md block diagram text "4× INN100 GaN" becomes "4× IGB070S10S1".
2. **LMG1210 in PWM mode: 4 PWM lines instead of 8**, plus the latched-fault interface above (FPGA pins: 20 + 7 reserved).
3. **R-35 TVS stand-off 51 V (SMBJ51A at each bridge, SMCJ51A at the bulk; VBR 56.7–62.7 V, VC 82.4 V), not 56–58 V or the 54 V first proposed: see the VBUS overvoltage scheme above.** SMBJ58A clamps at 93.6 V, which plus switching overshoot exceeds the 100 V GaN rating. A local TVS at each bridge (block D), plus B's.
4. **Power-stage NTCs (4) go to block D's ADS7038 (read by the FPGA)**, not to the RP2350 ADC. This frees RP2350 ADC inputs for the knobs and puts over-temperature next to the bridge enable.
5. **New quiet rail 3V3_A ≤ 15 mA** for block D's ratiometric sensing: agreed with C as a dedicated TPS7A2033 from +5V.
6. **VDRV = 7.0 V ± 5 %, ≤ 150 mA** (IGC033S10S1; R-33a "Gate drive" row: 0.43 W at 448 kHz, 0.89 W at 1 MHz, at VDRV).
7. **Idle power:** ≈ 5.2 W of VBUS power at zero signal (IGC033S10S1, 448 kHz, incl. gate drive) with both channels switching. Recommend firmware auto-idle (gateware item 10) and noting it in R-33a.
8. **fsw baseline 448 kHz** (ECP5 grid), 672 kHz option, tunable per build.

## User decisions (2026-11-07)
- **A.** GaN = **IGC033S10S1** (985 in stock). D audits reworked (D-gan-fet.md, D-lmg1210.md, D-bootstrap.md, D-driver-passives.md); IGB070S10S1 kept as the rejected alternative.
- **B.** Tweeter HPF = **2 × 22 µF polypropylene TDK B32774D4226K (44 µF)** (D-tweeter-hpf.md).
- **C.** TVS: 54 V accepted in principle, then revised to **51 V** so that onset stays ≤ the 63 V bulk rating; one VBUS overvoltage scheme with block B (above).
- **D.** Inductor SER2915H vs XAL1510: deferred to the phase 4 floorplan; both stay audited.
- **E.** Post-filter sense **fitted on all 5 prototypes**.
