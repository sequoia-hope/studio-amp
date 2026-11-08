# Block B interfaces — what the isolated converter needs from, and gives to, other blocks

Block B = `iso_dcdc`. Design: `B-converter-design.md`; parts: `B-*.md`.

## From block A (TPS2373-4 PD) — what the UCC2897A needs

| Net / pin | Requirement | Why |
|---|---|---|
| `VPRI` / `VPRI_RTN` (= TPS2373 VDD side after the bridges / TPS2373 RTN) | 42–57 V operating; B's LINEUV turns it on at 40.4 V, off at 38.4 V, so the input current at the Class 8 CC limit stays ≤ 1.85 A (TPS2373 RTN recommended max; fold-back > 1.9 A for 1.65 ms) | block A item 2 |
| PD bulk (CBULK) on `VPRI`–`VPRI_RTN` | block A holds the total (≤ 120 µF recommended, 300 µF abs, TPS2373 Table 5). B fits **47 µF 100 V electrolytic (Honor RVT2A470M1010)** for the LT4321's ≥ 10 µF and damping, + 3 × 4.7 µF 100 V ceramics (≈ 6 µF effective) at T1, + ≤ 2 µF in its bias buck. B's input current at Class 8: ≈ 1.7 A dc at 41 V, 1.34 A rms ripple at 620 kHz carried by B's ceramics; the bulk sees only the low-frequency part | block A should count B's ≈ 8 µF of ceramics in its inrush calculation |
| TPS2373 **PG** → UCC2897A **SS/SD** (via 1 kΩ, B side) | open-drain, active-high, RTN-referenced; low until inrush is complete (+81.5 ms), then high-Z | holds the converter off during inrush |
| TPS2373 **VC_IN** ← B's `VB_PRI` (**14.3 V**, 13.9–14.8 V worst case; review M1) | B's primary LM5019 output; VC_IN > 8.5 V; < 15 V recommended. `VB_PRI` also feeds block A's isolator primary (≤ 15.3 mA), included in B's buck budget (64 mA total). Idle draw from VPRI during inrush ≈ 11 mA (TPS2373 p.7 bound: < 0.65 × 275 mA ≈ 179 mA; block A margin 30 mA) | TPS2373 §7.3.7: "If VC_OUT is not used, VC_IN must be connected to the low voltage bias supply of the PWM controller" |
| TPS2373 **VC_OUT** | **not used by B**: 1 µF to RTN only (block A) | its continuous current (20 mA recommended) is below the UCC2897A's 57 mA bias draw at 737 kHz |
| TPS2373 **UVLO_SEL** | open (VC_OUT UV 6.9 V) | irrelevant with VC_OUT unused; open is the documented default for UVLO-off > 7.25 V PWMs |
| PD current limit | TPS2373-4 2.2 A typ: above B's maximum input (≈ 1.7 A at 41 V, Class 8) | B's CC loop sets the real limit |
| PD bridge / input TVS | block A; B's parts on `VPRI` are rated ≥ 100 V (ceramics), 100 V (LM5019), 120 V (UCC2897A VIN, **100 kΩ to VPRI**, agreed with block A, review n3/n10) | |
| Type/class signals | `PD_TPL`, `PD_TPH`, `PD_BT` via the digital isolator to block E | firmware selects B's current limit from them (below) |

## To blocks C and D (secondary)

| Net | Spec |
|---|---|
| `VBUS` | 47.9 V nominal, static ±1.5 % (TL431B + 0.1 % divider; R-33 ±2 %); bulk 6 × 1000 µF/63 V (+1 DNP); TVS SMCJ51A (see the overvoltage scheme below) |
| Output current limit (CC) | 0.440 A at reset → 0.941 A (Class 6) → 1.300 A (Class 8), firmware-selected, set from the 91 % efficiency floor (review m1); under CC, VBUS sags (bursts come from the bulk, R-33a). Class 8 output is 62.4 W, 1.8 W under R-33a's 64.2 W |
| Start-up | 60 ms soft-start up to VBUS ≈ 7.5 V, then CC at 0.44 A: VBUS reaches 48 V in ≈ 0.7–1 s (with ≈ 8 W of block C load). Input stays ≤ 0.51 A worst case (review M5). Block C's rails and the amp must tolerate a slow VBUS ramp (amp muted until VBUS valid, R-34) |
| Converter switching | **737.28 kHz, crystal-synchronised (7.3728 MHz / 10 into UCC2897A SYNC, ±40 ppm)**. Lead decision 2026-11-07: inside the 712–775 kHz window that keeps every low-order product with the 576 kHz amp PWM ≥ 100 kHz (f − 576 = 161 kHz, 2·576 − f = 415 kHz, 3·576 − 2f = 253 kHz). If the clock fails the controller free-runs at 590–708 kHz; block E checks f_acf from `ACF_PULSE` and flags anything outside 737.28 kHz ± 0.5 %. Block C's 5 V buck (≈ 690 kHz) is 47 kHz away (`B-sync-clock.md`) |
| B's own secondary bias | `VSR` 10 V, ≈ 25 mA, from VBUS ≥ 7.5 V inside B; block C does not need to supply B |

## From block E (FPGA / RP2350), secondary side, no barrier crossing

| New net | Direction | Spec |
|---|---|---|
| `ILIM_SEL0`, `ILIM_SEL1` | E → B (**RP2350 GPIO34/35**) | 3.3 V GPIO, drive 2N7002 gates; 100 k pull-downs in B so reset state = 00 = 0.44 A. Encoding 00 = 0.44 A, 01 = 0.94 A, 10 = 0.80 A, 11 = 1.30 A. Firmware raises it after reading `PD_TPL/TPH/BT` (or LLDP). |
| `IBUS_SENSE` | B → E (**RP2350 ADC4 / GPIO44**, 10 nF at the pin) | 0–3.0 V for 0–1.5 A converter output current (INA281 × 6.0 V/A, RC 100 Ω/470 nF, divided 200 k/100 k; source ≈ 67 kΩ, so E fits a 10–100 nF cap at the ADC pin or a buffer) |
| **`POE_LOSS_N`** | B → E (**FPGA A6**; E's 4.7 k pull-up and 1 k series; also to block F's /DC_TRIP OR; B's 2N7002 sinks the 0.7 mA easily) | **PoE-loss detector (lead decision; R-32a, R-34).** Open-drain (2N7002), active low, pulled up to +3V3 at the FPGA. Asserts on the first converter pulse whose secondary plateau shows Vin < 40.4 V (39.7–41.0 V), before LINEUV stops switching (37.6–39.2 V): ≥ 16 µs ahead of the stop at full load, latency ≤ 0.42 µs. Held ≈ 10 ms after the last such pulse (retriggerable), so the FPGA should latch it. Immune to pulse skipping, bursts, CC limit and hiccups (it never looks at missing pulses). Not covered: PD foldback/PG drop at normal Vin, and very light-load DCM pulses < 0.45 µs, so OR it with `PD_PG` (block A). Ignore it until VBUS is valid at start-up. `B-poe-loss-detect.md` |
| `ACF_PULSE` | B → E (**FPGA B6**, 1 k series) | 3.3 V push-pull (TLV3202 via 100 Ω): high during every converter on-time (SW_SEC > 16 V). Diagnostics only (converter stopped, hiccup); not a PoE-loss signal |

## VBUS overvoltage scheme (agreed B ↔ D, 2026-11-07; same wording in `D-interfaces.md`)

Every part on VBUS stays within its rating; **63 V (bulk electrolytics, no surge rating
published) is the absolute limit.**
1. **Bulk absorbs returned energy.** Block D's worst case (OCP stop with all four output inductors at
   16 A, 5.1 mJ, plus ≈ 4 mJ of regen during the < 5 µs detection latency) is ≤ 12.4 mJ (block D's final figure): ΔV ≈ 0.04 V on
   6 mF at 55 V. Lifting VBUS from 55 V to the TVS onset (56.7 V) needs 0.57 J.
2. **Gateware stop at VBUS ≥ 55 V**, restart below **52 V** (R-35), block D's ADS7042 at 896 kS/s,
   reaction < 5 µs.
3. **Converter output OVP (B)**, independent of the opto: UCC2897A LINEOV from the averaged N5
   forward voltage, trips at VBUS ≈ 53.3 V (51.2–55.4 V), hiccup. Covers feedback failure.
   Load dump of the converter (1.34 A → 0) overshoots 24 mV.
4. **TVS for fast, low-energy spikes only: SMx51A** — VWM 51 V, VBR 56.7–62.7 V, VC 82.4 V.
   B: SMCJ51A (MDD C408371) at the bulk; D: SMBJ51A (Littelfuse C1973217) at each bridge.
5. Ratings at the 82.4 V clamp (+ ≈ 10 V layout overshoot at the bridge = 92 V): GaN 100 V,
   LM5013/LM5017/LM5019 100 V, INA281 110 V, 100 V MLCCs, block D's ADC divider (3.2 V vs 3.55 V).
6. Residual (recorded): a feedback failure at Vin 38.4–41.9 V in DCM can lift VBUS above 56.7 V before
   layer 3 sees it; the SMCJ51A then takes converter current and may fail short, after which the
   converter's current limit and the PD's take over.

## ±15 V (block C owns the choice) — recommendation

**Against a transformer winding.** T1 (Würth 750343576) has no free secondary winding: N3 and N4
are both used in series for 48 V, and N5 is insulated as a primary winding. A custom transformer
could add one, but a forward auxiliary output needs its own rectifiers and output inductor per rail
and its voltage follows Vin·D, regulated only through the 48 V loop (poor cross-regulation with
the audio load). Derive ±15 V on the secondary from VBUS (or 5 V) and post-regulate.

## Proposed changes to architecture

1. **T1 is not an LCSC part.** Würth 750343576 (WE-PoE++, the transformer of TI's PMP20878) wired
   N1‖N2 : N3+N4 = 1:2, bought from Würth/a distributor and hand-soldered (R-70 already allows
   hand-soldered magnetics). Intent R-33 says "off-the-shelf wound transformer": satisfied, but
   with a non-datasheet winding connection. **User decision** (`B-transformer.md`, options A–E).
2. **fsw = 737.28 kHz, synchronised to a primary-side 7.3728 MHz crystal ÷ 10** (volt-seconds, review M3, then the amp beat rule; lead decision 2026-11-07). New primary-side parts: HT7550 LDO, LVC1GU04 Pierce oscillator, 74HC4017 (`B-sync-clock.md`).
3. **B carries two small 100 V bias bucks** (LM5019): `VB_PRI` 14.3 V on the primary (UCC2897A VDD
   and TPS2373 VC_IN) and `VSR` 10 V on the secondary (SR drivers, TL431s, opto, INA281). Add both
   nets to the rails table; TPS2373 VC_OUT unused (block A).
4. **Secondary CC loop with firmware-selected limit**: new nets `ILIM_SEL0`, `ILIM_SEL1` (E → B) and
   `IBUS_SENSE` (B → E/D). Add to the D ↔ E / B ↔ E interface list. The IBUS shunt splits the
   converter output from the bulk node: `VBUS_CONV` (converter side) → 30 mΩ → `VBUS`.
5. **`POE_LOSS_N` (B → E, open-drain, active low)**, the R-32a secondary-side PoE-loss detector, plus
   `ACF_PULSE` (B → E, diagnostics). Block E maps both and ORs `POE_LOSS_N` with `PD_PG`.
6. **No ±15 V winding** (above); block C derives ±15 V on the secondary.
7. Architecture decision 6 stands (silicon FETs in the converter): main FET FDMS86200 150 V, clamp
   P-FET IRFR6215 −150 V, SRs BSC500N20NS3 200 V; NCP4306 diode-emulating SR controllers meet R-33.
8. Barrier crossings from B: T1, the LTV-217 opto, one Y2 cap (2.2 nF, +1 DNP). Unchanged from
   decision 4 in spirit (the Y-cap is a passive across the barrier, not a signal).
9. Bulk: 6 × 16 × 25 mm cans (+1 DNP footprint) for phase 4 to place (R-33a said 5–7).
10. **VBUS overvoltage scheme** above replaces R-35's "≈ 56–58 V stand-off" TVS with SMx51A
    (51 V stand-off, VBR 56.7–62.7 V), so the 63 V bulk stays in rating; intent R-35 wording to be
    updated by the lead.

## Review response (phase 1 review, `design/gates/review-phase1-B.md`, 2026-11-07)

All six MAJORs are fixed; none is disputed.

| Finding | Response | Where |
|---|---|---|
| **M1** VB_PRI below UVLO-on band | Fixed. VB_PRI 14.3 V (RFB2 107 k / 10.0 k, 0.5 %): worst case 13.9–14.8 V, ≥ 0.7 V above UCC2897A UVLO-on max 13.2 V and under TPS2373 VC_IN 15 V. PBIAS, buck load (64 mA incl. block A's isolator) and inrush draw recomputed. | `B-bias.md`, `B-controller.md` |
| **M2** plant gain 4× high | Fixed: ΔIout/ΔVFB = 0.2/(Rcs·n) = 1.47 A/V. New type II: RLED 499 Ω, R1 115 k, C1 4.7 nF (zero 294 Hz), FB 6.8 nF. **fc ≈ 1.0 kHz, PM ≈ 66°**; over CTR 0.5–2: fc 0.5–2 kHz, PM 56–68°. CC loop and the LED current range rechecked. | `B-converter-design.md`, `B-feedback.md` |
| **M3** volt-seconds hot | Fixed (see the addendum below: now **737.28 kHz crystal-synced**, 45 % cold / ≈ 60 % hot). Originally fixed by **raising fsw to 620 kHz** (DMAX 0.68 nominal kept, because regulation needs 0.655 at 37.6 V; no volt-second clamp is possible on the UCC2897A). Worst corner 74 Vµs = 61 % of 120 Vµs cold, ≈ 82 % of an assumed ≈ 90 Vµs hot. **Plain statement:** the off-the-shelf part is safe at 57 V hot only if Würth's Bsat(100 °C) × Ae gives ≥ ≈ 80 Vµs on 4 T. Until Würth answers, that is an estimate; if it fails, option B (custom) is required. Würth questions added; forced-DMAX bring-up test added. Efficiency recomputed: 93.3–93.4 % (core loss 1.04 W). | `B-converter-design.md`, `B-transformer.md`, `B-controller.md` |
| **M4** SR / CS-pin stress | Fixed. Forward SR recomputed at 38.4/37.6 V (137/143 V plateau). **RCD-Z clamps (US1G + 10 nF + SMBJ130A) fitted on both SRs as the baseline** → SR drain and NCP4306 CS ≤ ≈ 165 V (83 % of 200 V) from first power-up. RC snubber 22 pF + 2 × 22 Ω 1206: 0.28 W worst, 0.14 W per resistor. | `B-sync-rect.md`, `B-converter-design.md` |
| **M5** start-up current below VSR | Fixed. VSR now 10 V with its LM5019 starting at VBUS = 7.5 V (tracks in dropout), so CV/CC work from 7.5 V. Below that, the soft-start is lengthened to 60 ms (CSS 1 µF), which bounds the input: ≤ 0.45 A at 42 V nominal, 0.51 A worst corner, under a Type 2 PSE's ≈ 0.6 A. After that, CC 0.44 A → ≤ 24.5 W. **Type 2 and Class 6 PSE start-up test added** to bring-up. | `B-converter-design.md`, `B-bias.md`, `B-controller.md` |
| **M6** B↔E nets | **Closed.** Block E mapped them (2026-11-07): `ILIM_SEL0/1` RP2350 GPIO34/35, `IBUS_SENSE` RP2350 ADC4/GPIO44, `ACF_PULSE` FPGA B6, `POE_LOSS_N` FPGA A6 (E-pinmap.md, E-interfaces.md). E was told the reset limit is 0.44 A and the IBUS source is 67 kΩ (VSR-powered INA281, ≤ 45 µA pad injection). | this file, `B-poe-loss-detect.md` |
| m1 class budgets at 91 % | Fixed: set-points 0.440 / 0.941 / 1.300 A; shunt 30 mΩ; PD budget checked at 91 % (Class 8 69.7 W, Type 2 24.5 W, Class 6 50.6 W). | `B-feedback.md` |
| m2 INA281 ripple | Fixed: 6 × 4.7 µF upstream of the shunt (≈ 0.2 A p-p through it, no clipping), 100 Ω/470 nF at the INA output (inside the CC divider), `IBUS_SENSE` taken after it. | `B-feedback.md`, `B-output.md` |
| m3 stale TVS numbers | Fixed in `B-bias.md`. `C-interfaces.md` is block C's file: lead/block C to change "SMCJ58A" to SMCJ51A. | `B-bias.md` |
| m4 MIN_TON reverse current | Fixed: RMIN_TON 0.75 k (≈ 125 ns). Reverse current ≤ 0.09 A peak, ≈ 6 nC per cycle, deep DCM only; the dV/dt variant blocks re-triggering. No sustained backfeed. MIN_TOFF 2.43 k (≈ 285 ns) for 620 kHz. | `B-sync-rect.md`, `B-converter-design.md` |
| m5 snubber bookkeeping | Fixed: one value, 22 pF, C·V²·f per SR, + 0.1 W clamps; in the loss table. | `B-converter-design.md` |
| m6 beat with the amp | Superseded by the addendum below: converter crystal-synced at 737.28 kHz on the primary (no barrier crossing), amp at 576 kHz, all low-order products ≥ 161 kHz. Earlier answer: converter fsw 620 kHz ± 10 %: beat with 448 kHz ≥ 110 kHz; no sync across the barrier (R-32a). Block E measures f_acf from `ACF_PULSE` and picks the amp fsw so that no low-order product falls below 100 kHz. | `B-converter-design.md` |
| m7 datasheet / MPN mismatches | Taiyo HMK replaced by Murata GCM32DC72A475KE02L (C913445, 9059 stock; Murata GCM catalog fetched) at input and output. SM5845-221MT: the datasheet lists the K (±10 %) version with the same ratings; the calculations now use −20 % (M). | `B-output.md`, `B-primary-power.md`, `B-bias.md` |
| m8 snubber R power | Fixed: 2 × 1206 in series, ≤ 0.14 W each at the worst corner. | `B-sync-rect.md` |
| n1 | Agreed; stated that gateware usually acts before the OVP. SMCJ51A hot leakage at 55 V added as a bring-up measurement. | `B-controller.md`, `B-output.md` |
| n2 | The N5 OVP diode is now BAV21W (250 V) for the DMAX transient. | `B-controller.md` |
| n3 / n10 | **Closed.** VIN → VPRI through 100 kΩ (fitted), 0 Ω to VDD DNP; block A confirmed (A-interfaces.md item 7). Block A review note A-n6 (VB_PRI vs UVLO-on) is the same issue as M1, already fixed (14.3 V). | `B-controller.md` |
| n5 | PG sinks only ISS ≈ 34 µA → VOL tens of mV; stated. | `B-controller.md` |
| n6 | Winding pin map added; LTV-217 creepage is to be measured in phase 4. | `B-transformer.md` |
| n7 | LLD "D" (540 µs) noted as harmless. | `B-sync-rect.md` |
| n8 | Eoss 0.75 µJ adopted in the loss model. | `B-converter-design.md` |
| n9 | Bulk ripple aligned to block D's 2.2 A rms continuous / 4.2 A bursts (rating 10.4 A). | `B-output.md` |
| n11 | Corner stated: D 0.655 at 37.6 V, ≈ 2 % VBUS droop on a DMAX(min) part. | `B-converter-design.md` |
| n12 | CS filter 1 k/82 pF kept (PMP20878 range), CF footprint 47–150 pF, bench check. | `B-controller.md` |
| n14 | MLCC DC-bias still assumptions; open until Murata SimSurfing data is in. | all |

### Addendum: converter frequency vs the 576 kHz amp PWM (lead decision, 2026-11-07)

- The 620 kHz ± 10 % free-running band collided with the 576 kHz amp PWM (beat down to 0 Hz). The UCC2897A
  oscillator cannot be held to ±5 % (p.7: −10/+8 % over temperature; internal timing capacitor, so
  precision RON/ROFF do not help).
- **Fix: SYNC from a primary-side crystal clock**, 737.28 kHz ± 40 ppm (window 712–775 kHz ✓).
  Free-running 656 kHz (590–708 kHz) stays below it, as SYNC requires, and acts as the fallback.
- At 737 kHz: volt-seconds 54 Vµs worst synced → **45 % cold, ≈ 60 % hot** (72 Vµs clock-failed: 60 % /
  ≈ 80 %); core 0.84 W; main FET 1.07–1.19 W; clamp FET 0.04 W; SR snubbers 0.21–0.33 W per SR
  (resistors moved to 2010); output ripple 0.35–0.55 A p-p; NCP4306 MIN_TON 125 ns / MIN_TOFF 245 ns
  against 0.41 µs minimum conduction/off ✓; LM5019 primary load 76 mA (inductor 330 µH).
  **Efficiency 93.0–93.1 % (≈ 92 % with core loss doubled)**, −0.3 % against 620 kHz; R-33's 92 %
  target / 91 % floor ✓.
- 737 kHz is 5 % above Würth's typical 200–700 kHz range for T1; asked in the Würth email.
- Agreed with blocks D and E (amp stays at 576 kHz); block C told the band (via the lead).
- Block E accepted (2026-11-07): the gateware counts `ACF_PULSE` over a 10 ms gate (≈ 7373 counts, 0.014 %
  resolution), before the amp starts and continuously after. Outside 737.28 kHz ± 0.5 % it flags a
  converter clock fault; firmware warns and the amp mutes or ramps down. That is the right response,
  because a free-running 590–708 kHz converter can beat with 576 kHz down to ≈ 14 kHz.
