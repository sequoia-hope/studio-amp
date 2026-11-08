# K1, K2: HFD4/5-SR output mute relays, with Q_K1/Q_K2 AO3400A drivers and the DC detector

Datasheets:
- `datasheets/hfd4.pdf`: Hongfa HFD4, 2024 Rev. 1.00. Read: contact and coil data, ordering
  code, outline/wiring (p.70, rendered and read), characteristic curves, notices.
- `datasheets/ao3400a.pdf`: AOS AO3400A (replaces the 2N7002 after review B1).
- `datasheets/bat54c.pdf`: Nexperia BAT54C (detector OR diodes).
- `datasheets/2n7002-cj.pdf`: JSCJ 2N7002, **rejected** (RDS(on) is specified only at VGS ≥ 5 V).
- `datasheets/1n4148ws-cj.pdf`: JSCJ 1N4148WS.
- `datasheets/g6k.pdf`: Omron G6K, the alternative that was **rejected**.

| Ref | MPN | show line |
|---|---|---|
| K1 (HP L/R), K2 (line L/R) | HFD4/5-SR | `C64399 HFD4/5-SR (HONGFA, SMD,10x6.5mm): extended, JLC stock 40182, lifecycle normal, checked 2026-11-07` |
| Q_K1, Q_K2 | AO3400A (AOS) | `C20917 AO3400A (AOS, SOT-23): basic, JLC stock 1065206, lifecycle normal, checked 2026-11-07` |
| D_OR (detector OR, one dual part) | BAT54C,215 | `C37704 BAT54C,215 (Nexperia, SOT-23): preferred, JLC stock 411535, lifecycle normal, checked 2026-11-07` |
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
| Contact switching voltage/current | 220 VDC, 2 A max; 1 A 30 VDC rated | ≤ 7.4 Vpk, ≤ 43 mA (HP short) | OK |
| Minimum load (reference) | 10 mV / 10 µA | idle audio: below this. The relay always switches with silence, and the contact is held. Dry-circuit reliability relies on the Au plating | OK |
| Coil max voltage | 10 V (5 V type) | 5 V ± 5 % | OK |
| Ambient | −40 to +85 °C | 55 °C | OK |
| Dielectric between open contacts | 1000 VAC | ESD at the jack is clamped by the TVS to ≤ 44 V | OK |

## Calculations

**Coil current:** 5 V/178 Ω (±10 %) = 28 mA (25.5–31 mA). Two relays: 56 mA from +5V (to block C).

**Driver (revised after review B1):** AO3400A, a logic-level N-MOSFET.
- Datasheet: VGS(th) 0.65 min / 1.05 typ / 1.45 max V at 250 µA; RDS(on) ≤ 48 mΩ at
  VGS = 2.5 V, ≤ 32 mΩ at 4.5 V; VDS 30 V; VGS ±12 V.
- Gate network: FPGA ball (3.3 V, no series resistor on block E's side) → 10 kΩ (block F) →
  gate, with 100 kΩ gate-to-source. VGS = 3.3 × 100/110 = **3.00 V**. That is ≥ 2.5 V, so the ≤ 48 mΩ RDS(on)
  rating applies.
- **Coil voltage:** V_coil = V(+5V) − 31 mA × 48 mΩ = V(+5V) − 1.5 mV. With +5V ≥ 4.76 V, the
  coil sees **≥ 4.75 V**, against a 3.75 V
  pick-up. The rated step voltage is applied per Hongfa notes 2/7. **Requirement to block C:
  +5V ≥ 4.76 V at the relays**, worst case.
- Hongfa note 3 (use the 4.5 V coil with a 5 V transistor drive) is about a BJT's VCE(sat). With
  a 1.5 mV FET drop it doesn't apply.
- Switching speed: gate charge through 10 kΩ takes ≈ 10 µs. That counts as a step for the relay.
- The 2N7002 was rejected: at VGS ≈ 3.0 V and Vth(max) = 2.5 V it can be shown to sink only
  ≈ 6 mA (review B1).

**Flyback:** a 1N4148WS across the coil. Peak current 31 mA ≪ 150 mA rating. Release time is
3 ms max (the datasheet value; a plain diode lengthens it by roughly 1–3 ms).
- R-34: on PoE loss the FPGA drops HP_EN/LO_EN at once: within ≤ 1 ms of **PD_PG_N rising**
  (active low, from block A through the isolator; it reads high when the primary is dead) **or
  POE_LOSS_N falling** (block B's VBUS-droop comparator, which asserts below ≈ 39.5 V;
  open-drain, active low). The
  contacts are open within ≈ 6 ms.
- **Hardware backstop (fitted):** a second BAT54C, D_PL (common cathode, pin 3, to POE_LOSS_N;
  anodes pins 1 and 2 to the Q_K1 and Q_K2 gates). When POE_LOSS_N is pulled low (≤ 0.1 V), the
  gates go to ≤ 0.1 + 0.27 = 0.37 V, below Vth(min). The relays drop even with the FPGA hung.
  - Limit (fourth-pass review): this backstop works only while VBUS is above ≈ 7.5 V, where
    block B's comparator rail is up. Below that, +5V (the buck from VBUS) and the relay coils
    have no supply anyway, so the relays are already released. On USB-only power the relays are
    off by design.
  - It is a separate diode pair, not an OR into /DC_TRIP: that would add a second diode drop
    (gate ≈ 0.6 V, marginal at 55 °C) and merge HP_FAULT_N with POE_LOSS_N.
  - Load on block B's open drain: 2 × 0.33 mA gate feed plus block E's **4.7 kΩ** pull-up
    (0.70 mA), so 1.37 mA in total. The gate ≤ 0.37 V claim needs block B's pull-down at
    VDS ≤ 0.1 V at 1.37 mA (RDS ≤ 73 Ω); that is block B's re-review MINOR-2. When POE_LOSS_N is
    high (4.7 kΩ pull-up to +3V3), the diodes are reverse-biased (3.3 V vs a 3.0 V gate).
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
  - **Sense points (review m4): on the amplifier side of the relays.** HP: OUT_HP, after R_OUT
    and before relay COM. Line: the SA5532 output pin, before R_BO.
  - If the sense points were on the jack side, opening the relay would remove the DC, N_DC
    would decay, and the relay would chatter into a fault. With amplifier-side sensing the trip
    latches for as long as the fault lasts.
  - The detector is not a stored latch. Gateware latches HP_FAULT_N and keeps HP_EN/LO_EN low
    until the next power cycle or a firmware clear.
- Q_DN BC847B: B on N_DC (through 10 kΩ), E to GND. It conducts when N_DC > +0.6 V.
- Q_DP BC847B, inverted sense: E on N_DC (through 10 kΩ), B to GND. It conducts when
  N_DC < −0.6 V. (Using a second NPN with base and emitter swapped is the classic two-polarity
  detector.)
  - N_DC is at most 13.5/4 = 3.4 V for a single-channel fault, and at most 13.5 V if all four
    outputs fault the same way. Above +6 V, Q_DP's E-B junction avalanches (VEBO 6 V, BC847B).
    The 10 kΩ limits that to ≤ (13.5 − 6)/10 kΩ = 0.75 mA. Harmless (review m4).
- Both collectors pull node /DC_TRIP low. **A BAT54C** (common cathode, pin 3, to /DC_TRIP;
  anodes pin 1 → Q_K1 gate, pin 2 → Q_K2 gate) pulls both gates down. Each gate is fed through
  10 kΩ, so the detector overpowers the FPGA.
  - Tripped: /DC_TRIP ≤ 0.1 V (BC847B saturated at ≈ 1.4 mA: 2 × 0.33 mA of gate feed plus the
    0.70 mA from the 4.7 kΩ pull-up; VCE(sat) ≤ 0.1 V at that current). BAT54C VF ≤ 240 mV at 0.1 mA and ≤ 320 mV at 1 mA, so ≈ 0.27 V at 0.27 mA.
    **Gate ≤ 0.37 V**, below the AO3400A's Vth(min) of 0.65 V (≈ 0.58 V at 55 °C with the
    usual −2.5 mV/K). The FET is off: sub-threshold µA, against the relay's drop-out at ≤ 10 %
    of rated voltage.
  - Not tripped: /DC_TRIP sits at 3.3 V (**4.7 kΩ pull-up**, re-review MINOR-3: it holds against
    the ECP5's ≤ 150 µA pull-down, 3.3 − 0.7 = 2.6 V worst case), above the 3.0 V gate, so the diode is
    reverse-biased (leakage ≤ 2 µA). No effect.
  - So a trip turns both relay FETs off. /DC_TRIP also goes to the FPGA as HP_FAULT_N (ball P11),
  with a **4.7 kΩ** pull-up to +3V3.
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

- None. Block C confirmed +5V ≥ 4.84 V worst case at the relays (5.20 V max; `C-5v-buck.md`).
  Coil voltage ≥ 4.84 − 0.0015 = **4.84 V ≥ 4.75 V**. Max coil voltage 5.20 V < 10 V. Relays are
  off on USB-only power. The driver question is closed by the AO3400A (review B1).

## Phase 2 correction (schematic, 2026-11-08)

- **The gate OR diodes are one BAT54A per relay gate**, not two BAT54C shared across the gates.
  - Common anode (pin 3) on the gate.
  - K1 (pin 1) to the /DC_TRIP = HP_FAULT_N bus.
  - K2 (pin 2) to the POE_LOSS_N bus.
  - It is the same Schottky die, so VF is the same: datasheet `bat54a.pdf`, VF ≤ 240 mV at 0.1 mA
    and ≤ 320 mV at 1 mA. The trip analysis above (gate ≤ 0.37 V) is unchanged.
  - Why: with one part per gate the two buses run straight under both drivers, with no crossings.
  - `C130910 BAT54A,215 (Nexperia, SOT-23): extended, JLC stock 110105, lifecycle normal, checked 2026-11-07`
- Gate drive: FPGA → 10 kΩ → gate, with 100 kΩ to GND (no series resistor at block E): 3.0 V.
- DC detector inputs, all on the amplifier side of the relays:
  - HPA_L and HPA_R (OUT_HP, after R_OUT);
  - FILT_L and FILT_R (op-amp pins, before R_BO).
- Schematic: `hw/satellite/a/audio_out.kicad_sch` (K1001 HP, K1002 line; Q1013/Q1014; D1016/D1018
  BAT54A; detector Q1015/Q1016, C1037, R1084-R1090).
