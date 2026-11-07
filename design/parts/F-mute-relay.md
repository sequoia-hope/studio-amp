# K1, K2: HFD4/5-SR output mute relays, with Q_K1/Q_K2 2N7002 drivers and the DC detector

Datasheets:
- `datasheets/hfd4.pdf`: Hongfa HFD4, 2024 Rev. 1.00. Read: contact and coil data, ordering
  code, outline/wiring (p.70, rendered and read), characteristic curves, notices.
- `datasheets/2n7002-cj.pdf`: JSCJ 2N7002.
- `datasheets/1n4148ws-cj.pdf`: JSCJ 1N4148WS.
- `datasheets/g6k.pdf`: Omron G6K, the alternative that was **rejected**.

| Ref | MPN | show line |
|---|---|---|
| K1 (HP L/R), K2 (line L/R) | HFD4/5-SR | `C64399 HFD4/5-SR (HONGFA, SMD,10x6.5mm): extended, JLC stock 40182, lifecycle normal, checked 2026-11-07` |
| Q_K1, Q_K2 | 2N7002 (JSCJ) | `C8545 2N7002 (JSCJ, SOT-23): basic, JLC stock 5965613, lifecycle normal, checked 2026-11-07` |
| D_K1, D_K2 (flyback) | 1N4148WS (JSCJ) | `C2128 1N4148WS (JSCJ, SOD-323): basic, JLC stock 2859608, lifecycle normal, checked 2026-11-07` |
| Q_DN, Q_DP (DC detect) | BC847B (both) | see `F-hp-output-stage.md` (C57668) |

Footprint: "Standard SMT type" (S), 10 × 6.5 mm body, 8 pads on a 3.2/2.2/2.2 mm pitch with
rows 7.5 mm apart (outline p.70). Take the footprint from the S-type drawing, not the J-leg one.

**Why not Omron G6K-2F-Y (C47190, 65k in stock):** its ambient rating is −40 to +70 °C, which
fails R-40 (≥ 85 °C). The HFD4 is −40 to +85 °C, with AgNi + Au-plated contacts and a minimum
load of 10 mV/10 µA, which suits dry audio switching.

## Pinout (wiring diagram, bottom view, single-side stable, de-energised)

- Coil: 1 (+), 8 (−). **The coil is polarised** (notice 1: "highly sensitive polarized relay").
- Pole 1: COM 3, NC 2, NO 4.
- Pole 2: COM 6, NC 7, NO 5.

Audio uses **COM → NO**. The amplifier side goes to COM and the jack to NO, so the output is
open whenever the coil is off (power loss, FPGA unconfigured, DC fault).

## Absolute max vs worst case

| Parameter | Rating | Worst case | OK |
|---|---|---|---|
| Contact switching voltage/current | 220 VDC, 2 A max; 1 A 30 VDC rated | ≤ 7.4 Vpk, ≤ 41 mA (HP short) | OK |
| Minimum load (reference) | 10 mV / 10 µA | idle audio: below this. The relay always switches with silence, and the contact is held. Dry-circuit reliability relies on the Au plating | OK |
| Coil max voltage | 10 V (5 V type) | 5 V ± 5 % | OK |
| Ambient | −40 to +85 °C | 55 °C | OK |
| Dielectric between open contacts | 1000 VAC | ESD at the jack is clamped by the TVS to ≤ 44 V | OK |

## Calculations

**Coil current:** 5 V/178 Ω (±10 %) = 28 mA (25.5–31 mA). Two relays: 56 mA from +5V (to block C).

**Driver:** 2N7002, VGS = 3.3 V from the FPGA, through 100 Ω, with 100 kΩ gate-to-source as a
pull-down (off by default).
- The datasheet gives RDS(on) ≤ 7 Ω at VGS = 5 V, 50 mA. At 3.3 V no figure is given. Vth is 1.0
  min, 1.6 typ, 2.5 max, so at Vth max the 0.8 V overdrive is marginal.
- Worst case, Vth = 2.5 V: estimated RDS ≈ 20 Ω at 28 mA, so VDS ≈ 0.56 V and the coil sees
  4.44 V. Pick-up is ≤ 3.75 V, so it still operates (margin 0.7 V).
- Hongfa note 3 recommends the 4.5 V coil for a 5 V transistor drive. With a 3.3 V logic gate
  drive and a 2N7002, that note doesn't apply: the FET is a switch with ≤ 0.6 V drop. Phase 8 or
  bring-up checks the margin. **Alternative:** if the margin is doubtful, use HFD4/4.5-SR (if
  stocked) or drive the gate from 5 V through a level shift. Logged as an open item.

**Flyback:** a 1N4148WS across the coil. Peak current 31 mA ≪ 150 mA rating. Release time is
3 ms max (the datasheet value; a plain diode lengthens it by roughly 1–3 ms).
- R-34: on PoE loss the FPGA drops HP_EN/LO_EN at once. The contacts are open within ≈ 6 ms.
  The rails are held for ≥ 20 ms, so the outputs are disconnected while the ±15 V rails are still
  good. No power-down thump.
- If faster release is needed, a 6.2 V zener in series with the diode gives ≈ 1 ms. Not required.

**Pop-free sequence (to block E/firmware, R-34):**
1. Rails come up; relays are off (default pulldown).
2. The FPGA configures and starts the DAC streams with the idle (zero) pattern.
3. Wait ≥ 3 s for the servo (τ = 0.51 s).
4. Close K2 (line) and K1 (HP, only if HP_DET shows a plug, optionally).
5. Shutdown, or PoE loss: open the relays first, then ramp the DAC.

**DC detector (hardware, R-42 spirit / headphone safety):**
- Inputs: HP_L, HP_R, LO_L and LO_R, each through 47 kΩ into the node N_DC, which has 10 µF X7R
  (non-polar) to GND.
- Q_DN BC847B: B on N_DC (through 10 kΩ), E to GND. It conducts when N_DC > +0.6 V.
- Q_DP BC847B, inverted sense: E on N_DC (through 10 kΩ), B to GND. It conducts when
  N_DC < −0.6 V. (Using a second NPN with base and emitter swapped is the classic two-polarity
  detector.)
- Both collectors pull node /DC_TRIP low. It connects through 1N4148WS diodes to each 2N7002
  gate, which is fed from the FPGA through 10 kΩ (not 100 Ω, so the detector can overpower it).
  So a trip turns both relay FETs off. /DC_TRIP also goes to the FPGA as HP_FAULT_N, with a
  10 kΩ pull-up to +3V3.
- Threshold: one channel's DC must reach 0.6 V × 4 = 2.4 V (the 47 k ×4 divider; only that
  channel drives the node) for a single-channel fault.
- Reaction to a ±13 V fault on one output: N_DC → 13/4 × (1 − e^(−t/τ)), with τ =
  (47k∥47k∥47k∥47k = 11.75 kΩ) × 10 µF = 0.12 s. It reaches 0.6 V at t = 0.12 × ln(1/(1 −
  0.185)) = 24 ms, plus 6 ms relay release: **≈ 30 ms**.
- Music rejection: a 20 Hz full-scale sine on all four outputs in phase (worst case, 7.35 Vpk
  HP) gives N_DC ≈ the average of 7.35/5.65 Vpk ≈ 6.5 Vpk × 1/(2π·20·0.12) = 0.43 Vpk, which
  stays below 0.6 V. For 10 Hz content at full scale it would trip (0.86 V). Acceptable:
  full-scale content below 15 Hz is subsonic, and firmware high-passes the HP/line feeds at
  ≤ 10 Hz. Phase 8 confirms. The 10 µF X7R (CC1206KKX7R8BB106, 25 V) derates to ≈ 8 µF at ±1 V,
  which raises the trip-sensitivity margin slightly. Its non-linearity is irrelevant here.
  `C70462 CC1206KKX7R8BB106 (YAGEO, 1206): extended, JLC stock 210788, lifecycle normal, checked 2026-11-07`
  (datasheet `datasheets/yageo-cc1206-x7r.pdf`).

## Fine print / gotchas

- Notice 3: relays ship in the "reset" state; this applies to latching types. Ours is single-side
  stable.
- Notes 7 and 2: apply a step voltage to the coil, never a slow ramp. The FET switch does that.
- Polarised coil: pin 1 to +5 V, pin 8 to the drain.
- MSL 3 (SMT type): JLC handles it.
- Contact resistance 100 mΩ max, in series with 4.7 Ω (HP) and 100 Ω (line). Negligible.

## Layout guidance

- Put the relays next to the jacks. The amplifier side and the jack side must be laid out so
  that the NO trace to the jack is short and sits after the TVS.
- Keep the coil and flyback loop small and away from the mic preamp.

## Open questions

- 2N7002 RDS(on) at 3.3 V gate drive is not in the datasheet. Bring-up check, or a level-shift
  option. A footprint-compatible alternative with Vth ≤ 1.5 V (e.g. a logic-level SOT-23 NMOS)
  can be picked in phase 2 if the margin is wanted on paper.
