# Phase 1 independent review — block B (isolated active-clamp forward)

Date: 2026-11-07. Reviewer: independent (artifacts only; authors' conversation not seen).
Scope: `design/parts/B-*.md` (converter design, transformer, controller, primary power, sync
rectifiers, output, feedback, bias, interfaces) against the datasheets in `design/datasheets/`,
`design/intent.md`, `design/architecture.md` (phase 1 reconciliation), `A/C/D-interfaces.md`,
and the phase 1 gate checklist. Every datasheet named below was re-read (pdftotext / rendered
page); every converter number was recomputed from the datasheet formulas, not checked for
arithmetic. LCSC lines re-run with `jlc_parts.py show` on 2026-11-07 (all 21 parts: lifecycle
normal, stock as stated; INA281A4 60 pcs and the 47 pF 250 V C0G 99 pcs are the thin ones).

Page numbers: UCC2897A = SLUS829E; NCP4306 = NCP4306/D rev. 6; LM5019 = SNVS788G;
T1 = Würth 750343576 rev. 003.001; TPS2373 = SLUSCD1C.

---

## BLOCKER

None.

## MAJOR

### M1. UCC2897A may not start: VB_PRI 13.5 V is below the UVLO-on tolerance band
- Files: `B-bias.md` (VB_PRI 13.48 V, 100 k / 10.0 k), `B-controller.md` ("13.5 V is above UVLO-on 12.2–13.2 V").
- Datasheet: UCC2897A p.6, UVLO start threshold **12.2 / 12.7 / 13.2 V**; LM5019 p.6 FB regulation 1.200–1.250 V (±2 %).
- Recomputed: VB_PRI = VFB·(1 + 100 k/10 k) with ±2 % reference and 1 % resistors → **12.96–14.0 V**.
  Worst-case low rail (12.96 V) is below the worst-case UVLO-on (13.2 V): the converter never
  starts. Even typical (13.48 V) leaves 0.28 V to the UVLO-on maximum, before buck ripple and the
  isolator load step. The controller also stops at 7.6–8.4 V, so there is no need to sit this close.
- Fix: raise VB_PRI to ≈ 14.1–14.3 V (RFB2 105–107 k with 10.0 k): worst-case band 13.55–14.9 V,
  above 13.2 V and inside TPS2373 VC_IN's 15 V recommended max (TPS2373 p.6) and UCC2897A VDD
  16 V. Re-check the 78L05 / ISO7740 branch and the PBIAS figures at the new voltage.

### M2. Voltage-loop plant gain is 4× too high (n applied in the wrong direction); compensation values do not give the stated crossover
- File: `B-converter-design.md` "Loop compensation": "ΔIout/ΔV_FB = 0.2 × n / Rcs = 5.9 A/V".
- With n = Ns/Np = 2 the **secondary** current is the primary current divided by n (the audit
  itself uses Ipri = 2·Isec everywhere else). Plant = 0.2 / Rcs / n = 0.2 / 0.068 / 2 = **1.47 A/V**
  (ignoring the extra attenuation from the m ≈ 1.7 slope ramp, which lowers it further).
- Consequence: loop gain at 1.5 kHz is 0.24, not 0.94; crossover falls to ≈ 350–400 Hz, below the
  483 Hz TL431 zero, so the phase boost is incomplete (PM ≈ 35–40°, not 55–65°), and the 4.7 kHz FB
  pole / 6.6 kHz ESR-zero pairing no longer sits above fc as intended.
- Fix: redo the type-II design with the 1.47 A/V plant (≈ 4× more mid-band gain: e.g. RLED
  1.0 k → 499 Ω and/or R1 84.5 k → ~169 k, zero moved to ≈ fc/3), and re-check the opto current
  range (FB pull-up 4.99 k gives ≤ 0.5 mA collector current) and the CC-loop hand-over. Then the
  phase 8 simulation as planned.

### M3. Transformer volt-second margin disappears at the tolerance corners and hot core
- Files: `B-converter-design.md` "Switching frequency", `B-transformer.md`.
- Datasheet: T1 p.1, ∫Udt = **240 Vµs on N1+N2, bipolar**, test conditions +20 °C (p.1 footer);
  UCC2897A p.7 DMAX 66–74 % (RON = ROFF = 75 k), p.7 oscillator −10/+8 % over temperature.
- Recomputed (4-turn primary → 120 Vµs at 20 °C): nominal DMAX at 57 V = 57 × 0.683 / 400 kHz =
  97 Vµs (81 %, as the audit says). At DMAX 0.74 and fsw −10 %: 57 × 0.74 / 360 kHz = **117 Vµs
  (98 %)**. MnZn Bsat falls ≈ 20–25 % from 20 °C to 100 °C, so the hot rating is ≈ 90–96 Vµs —
  below even the nominal DMAX case. Any excursion to DMAX at high line (feedback fault, start-up
  before the opto takes over, load step) saturates the core; the only protection is then the
  cycle-by-cycle CS limit (no leading-edge blanking, 82 ns RC) and the 150 V main FET.
- Fix (one of): confirm core material, Ae and Bsat(100 °C) with Würth and show the hot margin;
  raise fsw toward 500 kHz (gives ≈ 94 Vµs at the same corner — still only at the hot limit); or
  treat this as the argument for option B (8 T primary) and state that the 750343576 build
  depends on the CS limit for saturation protection, with a bring-up test of DMAX at 57 V.

### M4. SR drain and NCP4306 CS-pin stress understated at low line; 200 V abs max has no margin before snubber tuning
- Files: `B-sync-rect.md` (forward SR "116 V at 42 V"), `B-converter-design.md` stress table.
- Datasheets: NCP4306 p.6 CS abs max **200 V**; BSC500N20NS3 p.3 V(BR)DSS 200 V; PMP20878 test
  report p.4 (Q13 90 V vs 74 V plateau at 38 V in: +22 %; Q15 94 V vs 57 V: +65 %).
- Recomputed: the forward SR blocks n·Vin·D/(1−D) during reset. The audit's own LINEUV lets the
  converter run down to 38.4 V (37.6 V at tolerance), where D = 0.635–0.65 and the plateau is
  **134–139 V**, not 116 V. With the audit's +32 % ringing factor: 177–184 V; with PMP's measured
  +22 %: 164–170 V. Freewheel SR at 57 V: 114 V plateau, +65 % → 188 V. Both SR drains (and both
  NCP4306 CS pins) approach 200 V unsnubbed; the 47 pF RC snubber is "tuned at bring-up", so the
  first power-up of a prototype happens at 94 % of an absolute maximum.
- Fix: fit the RCD clamp footprints on **both** SRs as the baseline (clamp ≈ 150–160 V), not DNP on
  one; recompute the forward-SR stress table at 38.4 / 37.6 V; size the forward snubber resistor
  for 47 pF × 139² × 400 kHz = 0.36 W (the 2010 0.5 W part is marginal at 85 °C); or justify a
  higher LINEUV-off (≈ 40 V) if the PD budget allows, which also eases M3 and the DMAX margin.

### M5. Start-up: no current limit until VBUS ≈ 20 V — the Type 2 / Class 6 PSE sees the primary peak-current limit, not the 0.47 A default
- Files: `B-converter-design.md` "Soft-start" item 5 ("VBUS ramps in CC (0.47 A) to 48 V"),
  `B-bias.md` (VSR LM5019 UVLO start 20.1 V), `B-feedback.md`.
- Both TL431s, the INA281 and the opto LED are powered from VSR; VSR starts at VBUS = 20.1 V
  (LM5019 UVLO 154 k / 10 k). Below that there is no CV and no CC: FB is pulled to VREF and the
  converter runs at the UCC2897A cycle-by-cycle limit (0.43–0.53 V / 68 mΩ = 6.3–7.8 A primary →
  ≈ 2.4–3.1 A secondary after magnetizing current). Charging 6 mF from 0 to 20 V at that current
  takes ≈ 40–50 ms, with input current rising to ≈ 20 V × 3 A / (0.85 × 42 V) ≈ **1.7 A** at the
  end — above a Type 2 PSE's ICUT (≈ 0.6 A) and a Class 6 PSE's (≈ 1.2 A) for 20–30 ms, inside the
  PSE TCUT window (50–75 ms) but with no margin for a slow PSE or a second attempt. The soft-start
  (9 ms) does not help: it only ramps the peak-current limit, which reaches full value long before
  VBUS reaches 20 V. R-30 requires start-up on Type 2.
- Fix: power the secondary control earlier — set the VSR buck's UVLO just above its output (LM5019
  runs from 7.5 V and tolerates near-dropout; e.g. VSR UVLO ≈ 13 V, or VSR = 10 V with UVLO ≈ 11 V,
  which the NCP4306 10 V clamp, TL431 and INA281 all accept) — and/or add a primary-side start-up
  current limit; recompute the input current profile for Type 2 and Class 6 and add a Type 2 PSE
  start-up to the bring-up list. Fix the "CC from 0 V" statement in the start-up sequence.

### M6. B ↔ E interface not reconciled: `ILIM_SEL0/1`, `IBUS_SENSE` absent from block E; E expects a `POE_LOSS_N` that B does not define
- Files: `B-interfaces.md` ("From block E"), `design/parts/E-interfaces.md`, `E-pinmap.md`
  (only "Block B/C POE_LOSS_N → FPGA A6").
- `grep` of E-interfaces.md and E-pinmap.md finds no `ILIM_SEL`, `IBUS_SENSE` or `ACF_PULSE`; the
  architecture reconciliation says they exist. Without `ILIM_SEL` the converter is fixed at 0.47 A
  (22.6 W) — the amp would never get Class 6/8 power. Conversely E's `POE_LOSS_N` (R-32a secondary
  PoE-loss comparator) has no owner in B (B offers `ACF_PULSE` instead, and its own text says it is
  unreliable in pulse-skipping).
- Fix: E to allocate 2 GPIO + 1 ADC input (or RP2350 GPIO/ADC) for `ILIM_SEL0/1`, `IBUS_SENSE`;
  B and E to agree who builds the R-32a secondary detector (VBUS-droop comparator in B or D is the
  robust option) and name the net in both files.

## MINOR

- **m1. Class budgets at the efficiency floor.** `B-feedback.md` set-points: Class 8 1.344 A → 64.5 W /
  0.91 + block A worst 1.12 W = 72.0 W at the PD (> 71.3 W); Type 2 0.470 A → 22.6 W / ≈ 0.89 (light
  load) + 0.8 W = 26.2 W (> 25.5 W). Class 6 is fine (50.4 W). Set the limits from the 91 % floor
  (≈ 1.30 A / 0.44 A) or trim them in firmware from `IBUS_SENSE`.
- **m2. INA281 sees the 400 kHz inductor ripple.** `B-output.md` places the 3 × 4.7 µF ceramics
  (|Z| ≈ 57 mΩ at 400 kHz) upstream of the 27 mΩ shunt and the 6 mF bulk (ESR ≈ 4 mΩ + ESL)
  downstream, so most of the 0.7–1.0 A p-p ripple flows through the shunt: 3–5 V p-p at the INA281
  output (1.3 MHz BW). Add an RC at the INA output (or move part of the ceramic bank after the
  shunt), and filter `IBUS_SENSE` before the ADC.
- **m3. `B-bias.md` VSR abs-max row is stale**: "64–71 V TVS breakdown, 93.6 V clamp" are the SMCJ58A
  figures; with SMCJ51A it is 56.7–62.7 V / 82.4 V (+ overshoot). Same stale text in
  `C-interfaces.md` ("Block B chose an SMCJ58A"). Update both.
- **m4. NCP4306 MIN_TON 300 ns permits reverse current at very light load.** With the freewheel SR
  conduction shrinking toward zero in DCM, MIN_TON holds it on while the inductor current reverses
  at Vo/Lo = 0.7 A/µs → up to ≈ 0.2 A reverse per cycle (datasheet p.36 warns of exactly this).
  Against R-33 ("must not run in reverse"). Use the shortest MIN_TON that still blanks the turn-on
  ring (0–1 kΩ → 55–150 ns), or show the dV/dt detector covers it.
- **m5. Snubber loss bookkeeping.** With the stated 100 pF the model term should be C·V²·f summed
  over both SRs ≈ 0.94 W at 50 V, not 0.58 W; with 47 pF ≈ 0.44 W (+0.1 W at low line for the
  forward SR). Efficiency estimate moves by ≈ −0.5 %; still 92–93 % nominal. State one consistent C.
- **m6. 400 kHz ACF vs 448 kHz amp PWM: 48 kHz beat, free-running ±10 %.** The oscillator tolerance
  (p.7, 225–270 kHz at 250 kHz) puts the beat anywhere in 8–88 kHz, i.e. into the audio band at the
  +8 % corner. Block D/E should pick an amp fsw ≥ 500 kHz away or accept and measure the VBUS
  ripple component (open-loop PWM has no PSRR beyond feedforward).
- **m7. Datasheet / MPN mismatches.** `taiyo-hmk325c7475.pdf` is the HMJ-series catalog (lists
  HMJ325KC7475MHPE); the LCSC part is HMK325C7475KMHPE — fetch the HMK sheet or state the series
  equivalence. `sxn-sm5845-221.pdf` lists SM5845-**221K** (±10 %) while the LCSC MPN is SM5845-221MT
  (±20 %); the audit quotes the K tolerance. Ratings (220 µH, 1.57 Ω, Isat 0.36 A, Irms 0.35 A)
  confirmed on p.14.
- **m8. Forward-SR snubber resistor power** at 38.4 V: 47 pF × 139² × 400 kHz = 0.36 W on a 0.5 W
  2010 at up to 85 °C board temperature — derate or use 2 × 1206 in series (also under M4).

## NOTE

- **n1. VBUS overvoltage scheme — judged sound.** 63 V bulk (KZN p.2: 1000 µF / 63 V / 16 × 25:
  0.024 Ω, 2.89 A at 105 °C, 10,000 h, confirmed) behind SMCJ51A (VWM 51 V, VBR 56.7–62.7 V at 1 mA,
  VC 82.4 V at 18.2 A — MDD p.3 confirmed), gateware stop 55 V, converter OVP 53.3 V. The energy
  argument (0.57 J to lift 6 mF from 55 to 56.7 V vs ≤ 12.4 mJ returned) holds; the residual
  DCM/feedback-fault window is correctly recorded. Two remarks: the OVP band (51.2–55.4 V) overlaps
  the gateware threshold, so in many units the gateware acts first — fine, but say so; and at a
  sustained 55 V the SMCJ51A sits at 97 % of its minimum VBR, so its hot leakage (not specified above
  VWM) should be measured, not assumed 1 µA.
- **n2. LINEOV-as-output-OVP recomputed and agreed** (node A ≈ (Vin − 0.7)·D; trip 26.4 V → VBUS
  ≈ 53.3 V; hysteresis current 0.125/RDEL = 27.6 µA per eq. 9, p.20 — consistent with the EC's
  13 µA at 10 kΩ). BAS316 on N5 sees Vc − Vin ≈ 60–70 V reverse in normal operation (100 V rated)
  but > 100 V in the DMAX-at-57 V transient the audit already flags for the main FET; fine as long
  as that case is excluded, note it in the same place.
- **n3. VIN pin tied to VDD** is outside the recommended VIN range (18–110 V, p.5). Harmless with the
  JFET unused, but the audit's alternative (VIN ← VPRI via 100 k, fitted) stays inside the datasheet
  and is the safer default; keep the 0 Ω-to-VDD as the DNP.
- **n4. LM5019 current limit 150–300 mA (p.6) confirmed**; primary peak 112 mA OK. UVLO shutdown
  < 0.66 V noted correctly.
- **n5. TPS2373 PG → SS/SD**: PG VOL 0.27–0.5 V at 2 mA (p.8) vs SS/SD shutdown 0.4–0.6 V looks tight,
  but at ISS = 22 µA the VOL is tens of mV. OK; state the current in the audit.
- **n6. Isolation (R-32).** IEEE 802.3 clause 33.4.1 / 145.4.1 lists 2250 V DC for 60 s as the
  alternative to 1500 Vrms 60 s, so T1's 2250 V DC rating is the right class; the open item is only
  the test duration (ask Würth, or hipot the board). T1 land pattern (p.1): primary pads 1–6 and
  secondary pads 7–11 are ≈ 18 mm apart edge-to-edge. Winding pins for phase 2: N1 2(dot)–4, N2
  3(dot)–5 → parallel 2+3 / 4+5; N3 7(dot)–10, N4 8(dot)–11 → series 10→8, output 7/11; N5 1(dot)–6.
  LTV-217 SOP-4 creepage is not in its datasheet — measure the package for the phase 4 keepout.
- **n7. NCP4306DADZZDASNT1G decoded** (p.2 ordering, p.4 pin table, p.7–8 EC): pin-out D, 10 V
  clamp, dV/dt detector, external MIN_TON/TOFF, and — not mentioned in the audit — position 6 "D" =
  internal LLD timer 540 µs (p.39 Table 6). Harmless here (conduction every 2.5 µs; in pulse-skip it
  sleeps and the first pulse goes through the body diode). Variant is correct for a CCM forward.
- **n8. Efficiency recomputed** from the stated inputs at 50 V / 64.3 W: 4.8–5.3 W of loss → 92.3–93 %
  with 1.75 W of core loss. Agrees with the audit within the core-loss uncertainty, which remains
  the open item (ask Würth for material / Ae; measure ΔT at bring-up). Turn-on Eoss at Vin with
  ≈ 600 pF total switch-node capacitance is ≈ 0.75 µJ (0.3 W), a little above the 0.45 µJ used.
- **n9. Bulk ripple statements differ between blocks**: `B-output.md` sizes 0.75 A rms sustained /
  2.3 A bursts; `D-interfaces.md` says "B sizes for ≈ 2.2 A rms continuous and 4.2 A rms in bursts".
  Both are far inside 6 × 2.89 × 0.6 = 10.4 A at 120 Hz; make the two files quote one number.
- **n10. `A-interfaces.md` still routes "UCC2897A VIN" to VPRI** while B ties it to VDD (see n3).
  Align after deciding n3.
- **n11. DMAX vs LINEUV corner**: at 37.6 V the required D is 0.655; a DMAX-min (0.63) unit droops
  VBUS ≈ 2 % there. Acceptable, but the audit's "needs 0.59 at 41 V" should quote the 38.4 / 37.6 V
  case it allows.
- **n12. CCM SR commutation spike.** With Lleak(sec) ≈ 0.4 µH and n·Vin ≈ 100 V the freewheel-to-
  forward hand-over slews at ≈ 250 A/µs; the NCP4306's 13–23 ns turn-off delay lets a few amps of
  circulating current build (≈ 2× on the primary) before it opens. This is the source of the +65 %
  ring (M4) and also appears at the CS pin at the start of each on-time; confirm the 1 k / 82 pF
  filter (PMP20878 uses 1 k with C0G 47–100 pF) keeps it below the 0.43 V limit at full load.
- **n13. Packages vs MPN suffixes all check**: UCC2897APWR TSSOP-20 PW; FDMS86200 Power 56; IRFR6215TRLPBF
  DPAK; BSC500N20NS3GATMA1 PG-TDSON-8; NCP4306…SNT1G TSOP-6; LM5019MRX/NOPB SO-8 PowerPAD (DDA);
  TL431BIDBZR SOT-23-3; INA281A4IDBVR SOT-23-5; LTV-217-B-G SOP-4; GA355QR7GF222KW01L 2220; GRM31CR72E104KW03L
  1206 / DC 250 V (Murata p.1 confirmed); EKZN630ELL102ML25S φ16 × 25, F = 7.5 mm (KZN p.1 dimension
  table); SMCJ51A DO-214AB.
- **n14. MLCC DC-bias figures are still assumptions** (clamp 70 % at 100 V on 250 V X7R; input 45 % at
  57 V and output 50 % at 48 V on 100 V X7S 1210; PVDD/COUT 50 % at 13.5 V) — plausible, and the
  audit lists them as open; close them with maker curves before the gate as the checklist requires.

---

**Verdict:** not passed — no blocker, but six MAJORs (bias-rail UVLO margin, loop-gain factor-of-4
error, hot volt-second margin, SR/NCP4306 200 V stress at low line, uncontrolled start-up current
below VSR, and the missing B↔E nets) must be resolved and the affected audit files recomputed
before block B clears phase 1.
