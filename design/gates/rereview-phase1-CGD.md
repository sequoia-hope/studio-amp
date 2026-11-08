# Phase 1 second-pass review — blocks C (secondary rails), G (UI and I/O) and D (GaN class-D stage)

Date: 2026-11-08. Independent second-pass reviewer; did not see the authors' conversation.
Scope: close-out of every BLOCKER/MAJOR in `review-phase1-CG.md` and `review-phase1-D.md`; a first
review of what changed since (IGB070S10S1 at 576 kHz, `D-short-detect.md`, the LM5013 at ≈ 200 kHz,
the LM5017 ripple-offset fix and LDO thermals, the TCA9617B EN fix, the Qwiic 100 mA cap); a
spot-check of the MINORs; C↔D↔E↔F consistency. Every number below was re-derived from the PDFs in
`design/datasheets/` (pdftotext), not from the audits' quotes. Page numbers are PDF pages.

---

## 1. First-pass BLOCKER / MAJOR close-out

| Item | Status | Re-derivation and reason |
|---|---|---|
| **CG-B1** `PG_3V3` vs ECP5 pull-down (1V1/2V5 never start) | **CLOSED** | `PG_3V3` (TPS62A02A PG, 100 kΩ to +3V3) now drives only the 1V1 EN (TPS62A02A p. 6: VEN(R) ≤ 1.2 V, VEN(F) ≥ 0.4 V, input leakage nA) and the 2V5 EN_UV (TPS7A94 p. 8: IEN_UV ±1 µA, VIH 1.20–1.25 V): a 100 kΩ pull-up still has ≥ 20 µA at 1.25 V. The FPGA copy `PG_3V3_N` is a 2N7002 (Vth 1.0–2.5 V, p. 1; VGS 3.3 V) draining a 4.7 kΩ pull-up: ≥ 3.3 − 4.7 k × 150 µA = 2.6 V when not good, ≈ 0 V when good. B4 = PT11B, bank 0 (pinout CSV), so the ECP5 hot-socket A/B pair path does not apply. The author's reason for rejecting a direct 4.7 kΩ (PG VOL 0.4 V at 1 mA against the 0.4 V EN-off threshold) is right. |
| **CG-B2** `PG_5V` → TPS2116 PR1 dragged down | **CLOSED** | PGOOD's 56 k/100 k divider now loads only PR1 (TPS2116 p. 6: IPR1 ≤ 0.1 µA). LM5013 p. 743 gives the PGOOD pull-up as a "typical range of 10 kΩ to 100 kΩ", so the first reviewer's 5.62 k/10 k alternative was indeed out of range; the buffered `PG_5V_N` to B3 (PT4B, bank 0) is the right fix and reads 2.6 V / 0 V as for B1. |
| **CG-M1** LM5017 Type III DC offset; LDO thermals | **CLOSED** (setpoints and thermals), with a new MINOR (§2 M-1) | VDRV: Rr 499 kΩ, Cr 1 nF, RON 191 kΩ: Vr = (VIN − 7)·tON/499 µs = 31–40 mV with the author's tON band; offset 15–20 mV × 5.64 → **7.00–7.02 V** typ, 6.85–7.16 V over the 1.20–1.25 V reference (p. 5) ✓ inside D's 7.0 V ± 5 %. Fly-Buck: RON 402 kΩ, RFB 137 k/10 k: Vr 39–65 mV, offset 20–33 mV × 14.7 → **18.30–18.49 V**, 17.9–18.9 V over the reference ✓. θJA confirmed: TPS7A49 DGN **63.4 °C/W** (p. 6), TPS7A30 DGN **55.09 °C/W** (p. 3). TJ: 0.48 W → 85 °C design; 0.85 W → 109 °C in the 215 mA fault (≤ 125 °C) ✓. But the author's tON band (K = 1.0–1.2 × 10⁻¹⁰) is narrower than the datasheet's EC spread: see M-1. |
| **CG-M2** TCA9617B EN undefined with Qwiic power off | **NOT CLOSED** → §2 **MAJOR-1** | The fix (EN from `QWIIC_PWR_EN`, 100 kΩ pull-down, 100 kΩ discharge on `QWIIC_3V3`) relies on the 100 kΩ overriding the TCA9617B's internal EN pull-up. TCA9617B EC p. 6 specifies **II(EN) = −25 µA at VI = 0.2 V, VCCB = 3.3 V**, i.e. the pull-up is ≈ 124 kΩ at its strongest. With the FPGA pin tri-stated and the 100 kΩ alone, EN sits at 3.3 × 100/224 = **1.47 V**, above VIL = 0.3 × VCCB = 0.99 V (p. 5): the repeater can be enabled while the B-side pull-ups hang on a 0 V rail, which is exactly the fault M2 described (SDAB/SCLB read low → SDAA/SCLA driven low → the RP2350's I2C bus is dead). With the ECP5's pre-configuration pull-down present the node settles below 0.8 V, so the failure is confined to the case the "100 kΩ backstop" exists for: J16 configured but not driven (PULLMODE=NONE, tri-stated), or an FPGA otherwise Hi-Z. |
| **D-M1** Bootstrap refresh at the duty clamp | **CLOSED** | IGB070, 576 kHz, 8–92 %: Q/cycle = 0.5 + 7.9 (Qg max, p. 8) + 0.85 mA × 1.60 µs (IHB max, LMG1210 p. 6) + 0.08 (100 kΩ pull-down) = **9.8 nC**. LO ≥ 0.08 × 1.736 µs − 26 ns (tDEAD max at 20 kΩ, p. 7) = **113 ns** → 87 mA. BAT46WJ VF log-interpolated between 415/475 mV at 50 mA and 710/850 mV at 250 mA (p. 4) = 0.52/0.60 V; RSW 0.4 Ω typ at 100 mA (p. 6, no max) → **HB−HS ≥ 4.75 − 0.60 − 0.035 − 0.026 = 4.09 V** worst, ≥ 3.80 V ROC (p. 5), ≥ 0.44 V above VHBF max 3.65 V ✓. Even RSW = 1 Ω keeps ≥ 4.0 V. 768 kHz fallback: LO ≥ 78 ns, 0.12 A, ≈ 4.0 V ✓. |
| **D-M2** INA241 1 µs CM hold vs R-54 | **CLOSED** by the new detector | `D-short-detect.md` catches the CM step itself (re-derived in §2 m-5: 21 V/µs trip, ≈ 50 ns path, no false trip at full scale). Two regimes are stated in `D-current-sense.md` and `D-interfaces.md`; `intent.md` R-54 now reads ≤ 100 ns / 15 A ± 1 A, ≤ 250 ns / ≤ 17 A with the 21 A bench check ✓. |

MINORs spot-checked as fixed: 5 V buck frequency rationale (now a lead decision, see m-2), CIN 2 × 4.7 µF
100 V ✓, θJA 63.4 and +5V_A accounting ✓ (F says 120/200 mA already includes +5V_A; C keeps 135/215 as
margin, documented), +3V3 small consumers listed ✓, VDRV load rows updated ✓ (48 mA), 84.5 kΩ E96 →
1.107 V (1.080–1.134 V) ✓, TPS7A94 start-up 2.3 / 14 ms ✓, Tokmas clones labelled ✓, SMF6.0A on
+5V_LED ✓ (MDD table p. 2: VRWM 6.0 V, VBR 6.67–7.37 V, IR 400 µA at 6 V, VC 10.3 V at 19.4 A). D's
m1–m8 and n1–n7 are all reflected in the files (IGB070 edges 4.5/2.4 ns → ≈ 18 ns effective; t_sw at
IOH min 0.85 A; 27 V overshoot; LMV393 R_bot 82.0 k/88.7 k → 2.21 V ≤ 2.5 V; +20 ns overdrive; core
placeholder 0.4 W; 5.24 → 5.32 V VBST; stock notes).

---

## 2. New findings

### BLOCKER
None.

### MAJOR

**MAJOR-1. `QWIIC_PWR_EN` pull-down cannot hold the TCA9617B EN low** (reopens CG-M2).
- Files: `G-qwiic.md` (Circuit, "100 kΩ pull-down holds EN low, overriding the weak internal pull-up"), `E-interfaces.md` ("100 kΩ pull-down as backstop"), `C-interfaces.md` sweep row `QWIIC_PWR_EN`.
- Datasheet: TCA9617B SCPS259F p. 6, II(EN) = −25 µA at VI = 0.2 V (VCCB 3.3 V); p. 5 VIL(EN) = 0.3 × VCCB; p. 12 §7.4 (EN must change only with both buses idle).
- Problem: as in the table above. Node = 1.47 V worst case with J16 Hi-Z (≥ VIL 0.99 V); the sweep's "low → off, isolated (safe)" claim holds only while the ECP5's pre-configuration pull-down is active.
- Fix: **10 kΩ pull-down on `QWIIC_PWR_EN`** (node ≤ 3.3 × 10/134 = 0.25 V with the FPGA Hi-Z; 0.33 mA when the FPGA drives high, fine for a 4 mA LVCMOS33 output; TPS2553 EN VIH 1.1 V / VIL 0.66 V, p. 5 ✓). Keep the 100 kΩ discharge on `QWIIC_3V3`. Update the sweep row and E's backstop note. (`LED_EN`'s 100 kΩ is fine: the TPS2553 EN has no internal pull-up.)

### MINOR

**m-1. LM5017 on-time tolerance (±25–34 %) not applied; VDRV ripple injection is at the 25 mV minimum.**
- Files: `C-vdrv-buck.md`, `C-pm15-flybuck.md` (both use tON = (1.0–1.2) × 10⁻¹⁰ × RON/VIN).
- Datasheet: LM5017 p. 5 TON tests: 188/250/336 ns at 48 V, 100 kΩ (−25 %/+34 %); 270/350/460 ns at 32 V (−23 %/+31 %); p. 9 "minimum of 25 mV of ripple voltage at FB".
- Problem: VDRV at the TON minimum: 36 V → 459 ns → Vr 26.7 mV; 43 V → 29 mV; 48 V → 29.5 mV. With Cr +10 % / Rr +1 % that is **24–27 mV**, at or under the 25 mV floor. The offset band also widens: VDRV 6.99–7.06 V typ-reference, 6.85–7.21 V over the reference spread (still inside ± 5 % ✓). Fly-Buck: Vr 34–87 mV ✓; VOUT1 top rises to ≈ 19.0 V (TON max at 56 V, ref max) → +15 V LDO fault 0.81–0.87 W → 106–110 °C ✓; VOUT1 bottom 17.9 V → TPS7A3001 headroom 2.2 V minus cross-regulation droop, fine. Real frequencies with the datasheet's measured constant (250 ns at 48 V/100 k): Fly-Buck ≈ 380 kHz typ (≈ 280–510 kHz over the spread), VDRV ≈ 305 kHz (≈ 230–410 kHz), not the 508/410 kHz stated.
- Fix: VDRV Rr → **330–390 kΩ** (Vr ≥ 36 mV at TON min; offset 20–35 mV → VDRV ≤ 7.10 V typ, still ± 5 %); state the TON spread and the real frequency bands in both files and in E's clock plan (see m-2).

**m-2. The 5 V-buck beat rule's premise ("products above 2nd order are smaller still") is wrong for a D ≈ 0.1 pulse train; the two LM5017s are not in the rule at all.**
- Files: `C-interfaces.md` ("5 V buck beat-frequency rule"), `C-5v-buck.md` Revision 2, `E-interfaces.md` clock plan.
- Re-derivation: the LM5013 input current is a ≈ 2 A, D ≈ 0.104 pulse train; harmonic amplitudes ∝ sin(nπD)/n → n = 2: 0.93×, **n = 3: 0.85×, n = 4: 0.74×** the fundamental (≈ 0.40 A pk). Over the stated 170–230 kHz spread, 3·f_buck sweeps 510–690 kHz and crosses **576 kHz at f_buck = 192 kHz**; 4·f_buck crosses 737.28 kHz at 184 kHz. So |3 f_buck − 576| can sit anywhere in 0–114 kHz, including the audio band. Amplitude: ≈ 0.34 A pk on the bulk's ≈ 10 mΩ (ESL-dominated at 576 kHz) ≈ 3 mV on VBUS. In BD modulation the differential fsw component is DSB-SC (∝ M), so the spur appears as sidebands at f_audio ± δ at ≈ R/VBUS ≈ **−83 dBc (≈ 0.007 %)**, zero at idle. The Fly-Buck (≈ 0.5 A pk at 280–510 kHz; fundamental and 2nd harmonic sweep across 576 kHz) gives ≈ −94 dBc; VDRV is smaller still. Both are inside R-51 (0.1 %/0.3 %) and the closed-loop 0.02 %. A free-running frequency that keeps n ≤ 4 products clear does not exist (checked: the LM5013 tON ≤ 1000 ns floor, ≈ 165 kHz, blocks the only clean band below 144 kHz), so the earlier sync recommendation was the rigorous answer.
- Fix: no part change required; record the premise correctly and the ≈ −83 dBc wandering sideband as an accepted residual in `C-interfaces.md` and the clock plan, or revisit sync. Add the Fly-Buck/VDRV bands to the clock plan.

**m-3. Commutation-loop target of 1 nH is load-bearing and should be stated as an obligation.**
- Files: `D-gan-fet.md` abs-max table, `D-vbus-tvs.md`. Datasheet: IGB070 p. 8 Coss 310/340 pF at 50 V; p. 3 80 %-of-max guidance; 120 V pulsed, 1 h.
- Re-derived: 16 A × √(1 nH/340 pF) = **27 V** ✓ → 75 V normal, 109 V in the clamp case (on the 120 V pulsed rating, accepted as independent rare events). At a realistic 2 nH for a PG-TSON-4 pair plus 0603 caps the ring is 38 V → 86 V at the trip current and **79 V at the 13 A legitimate peak**, right at Infineon's 80 V continuous guidance.
- Fix: phase 6 extracts the loop and shows ≤ 1 nH (or ≤ 1.5 nH with a documented margin), with an RC snubber footprint across each half-bridge as the fallback.

**m-4. LM5013 on-time margin at the UVLO corner.**
- File: `C-5v-buck.md` Revision 2 ("847 ns at 32.6 V"). Datasheet: LM5013 p. 7 tON3–tON6 (625/245/330/128 ns vs the formula's 625/208/300/100 ns): tON ≈ RRON/(2.5·VIN) + ≈ 30 ns; ROC tON ≤ 1000 ns (p. 6), no tolerance stated.
- Re-derived: 69.8 kΩ at 32.6 V → **≈ 886 ns**, 11 % under the ROC maximum; 801 ns at the 36.2 V turn-on. Acceptable (the corner exists only during the UVLO-off ramp); record the +30 ns term. Everything else in Revision 2 re-derives: tON > 300 ns so the forced 250 ns off-time does not apply (p. 700); ΔIL 0.48 A, Ipk 2.25 A < 3.7 A; SRP1265A-470M 47 µH / 90 mΩ / 6.5 A / 9.5 A (Bourns p. 1); COUT ≥ 12 µF; CA 3.3 nF ≥ 2.1 nF; RA·CA 1.09 ms ≤ 1.20 ms; FB ripple 22–23 mV ≥ 12 mV; +47 mV offset; η ≈ 85 %; worst a, b ≤ 2 clearance 116 kHz ✓.

**m-5. Short detector: two normal-operation cases to state, and small corrections.**
- File: `D-short-detect.md`. Datasheets: TLV3501 p. 6 (tPD 7 ns max at 20 mV overdrive, 12 ns at 5 mV, −40…125 °C); LMG1210 p. 7 tEN 20 ns max; 74LVC1G17 4.6 ns; 74LVC1G74 5.9 ns.
- Re-derived: τ = 47 ns (± 6 % with 5 % C0G and 1 % R) → trip 21 V/µs (19.7–22.3) ✓; full-scale 20 kHz 3.0 V/µs → 0.14 V ✓; the ripple term at 576 kHz is Ipk/C = 1.04 A/700 nF = 1.5 V/µs → 0.07 V (the file still quotes 448 kHz, 2.4 V/µs). Path ≈ 48 ns ✓ plus ≈ 3 ns for R_S·C_in not counted → ≈ 51 ns ≪ 100 ns. Node X capacitance (two BAT54S + inputs ≈ 20–25 pF) divides a fast step to ≈ 65 %, so "any step ≥ 1 V" is really ≥ ≈ 1.5 V, irrelevant for 24–48 V shorts.
- Not listed: (a) **speaker lead opening under current**: the inductor current dumps into the 700 nF node at I/C = 18.6 V/µs at the 13 A legitimate peak → X = 0.87 V (0.94 V at τ + 6 %), so the detector trips at ≥ ≈ 14 A of interrupted current. Benign (latch, re-arm), but say so and keep the 1 V threshold rather than lowering it. (b) **start from "all LS on" to 50 % duty** steps both nodes 0 → 24 V with peak slope ≈ V·ω0 = 24 V × 2π × 60 kHz = 9 V/µs → 0.42 V: no trip, but gateware item 1 should ramp the duty rather than step it.
- Fix: text only.

**m-6. Stale or contradictory text across blocks** (consistency check, §3): see the list there; none changes a part, several change a number another block relies on.

### NOTE

- n-1. **VBST 5.32 V vs the LMG1210 ROC 5.25 V** (abs 5.5 V; IGB070 recommended VGS 5.5 V): re-derived 5.25 − 0.10 + 16 A × 10.5 mΩ = 5.32 V. The condition is narrower than stated: it needs a long LO (low duty, so VF → 0.1 V) *and* ≥ 14 A flowing out of the switch node through the LS in reverse at the same time, i.e. reactive or fault current against the drive direction, not the normal high-duty peak. Accepted; state the condition.
- n-2. **Effective dead time and shoot-through** re-derived: outgoing IGB070 fully off (below Vth min 1.2 V) in ≈ 7 ns, incoming reaches Vth min in ≈ 1.2 ns → ≥ 10 ns of margin at tDEAD min 16 ns ✓; ≈ 18 ns effective (14–24) for the loss model ✓. Idle 1.80 W / 46 W-4 Ω 2.29 W / 144 W-4 Ω 3.74 W are consistent with the sensitivity table and with Tj 72/100 and 83/129 °C (RthJC bottom 3.7/5.4 °C/W, p. 7): the **R-61 panel path is mandatory for the 144 W bound**, as stated ✓. VDRV 12.0 mA/driver, 48 mA ✓ (Qg 7.9, ILSDyn 1.25 + IHSDyn 0.7 mA/MHz, IDD 0.55, IHB 0.85).
- n-3. **ECP5 hot-socket pairs on bank 2** (DS-02012 §3.6 p. 52: A/B and C/D pins present a low-impedance path to each other while VCC < Vporup). Pinout CSV: H15/J16/G15/K16/C14/E14 are right-bank-2 balls. Partners J15, K15, F14, D14 are NC ✓; H15's partner G16 = `PTP_PPS` (no pull, harmless) ✓; **G15 (`DISP_BL_PWM`) pairs with F16 = `DISP_AUX8`** (header position 8). With the default JP8_B this is harmless; if a user ever bridges JP8_V, the backlight switch sees ≈ 3.3 V for the ≈ 1 ms POR window at every power-up (a blip). Either move `DISP_BL_PWM` to a ball whose partner is NC, or record the rule in `G-display.md`. B3/B4/B5/A6 are bank 0 (top) and hot-socket tolerant ✓.
- n-4. **Pre-configuration sweep confirmed** for every C/G net in the `C-interfaces.md` table, with TN-02038 Table 9.1 (30–150 µA for VIL(max) ≤ VIN ≤ VCCIO): `PG_3V3_N`/`PG_5V_N` 2.6 V or 0 V, informational; `PG_3V3Q` reads low → DAC held low (safe); `LED_EN`/`DISP_BL_PWM` low; `QWIIC_PWR_EN` low *only while the pull-down is active* (MAJOR-1); `VDRV_EN` on RP2350 GPIO36: pads reset to pull-down plus C's 100 kΩ ✓; `VDRV_PG` 2.73 V good / 0 V absent; `AN_OFF` not assigned. Unpowered FPGA: every FPGA-facing pull-up is on +3V3, the FPGA's own VCCIO, so nothing is back-driven.
- n-5. **`VDRV_PG` in an LM5017 FB-overvoltage event**: 9.3 × 3.0/7.7 = 3.62 V into RP2350 GPIO33, 20 mV above IOVDD + 0.3 V; fault only. 4.7 k/3.3 k (2.59 V good, 3.33 V in the fault) would clear it.
- n-6. **Qwiic 100 mA cap** re-derived: RILIM 150 kΩ inside 15–232 kΩ (TPS2553 p. 5); eq. 1 → 155/179/207 mA, consistent with the 210 kΩ EC row (110/130/150 mA) ✓. The firmware cap is the only thing holding 100 mA; the hardware trips at ≥ 155 mA.
- n-7. **SMF6.0A** "no standing leakage": IR is specified ≤ 400 µA *at* VRWM 6.0 V (MDD p. 2); at 5.12 V it is lower, not zero. Wording only.
- n-8. **TCA9617B B-side on a dead `QWIIC_3V3`**: with MAJOR-1 fixed, EN = 0 → both sides Hi-Z (Table 7-1) ✓; the 100 kΩ discharge gives τ = 1 s on the 10 µF, so `QWIIC_PWR_EN` must stay low ≥ 3 s before re-enabling if a defined 0 V is wanted at the far end (firmware note).
- n-9. **D-short-detect clamp into 3V3_A**: 47 mA for ≈ 50 ns → 2.4 nC → 0.5 mV on 4.7 µF ✓; TLV3502 input current through R_S ≤ 0.25 mA ✓ (abs max 10 mA, p. 4).

---

## 3. C↔D↔E↔F consistency

Agree: VDRV 7.00–7.02 V typ / 6.85–7.16 V vs D's 7.0 V ± 5 % ✓; VDRV load 48 mA (D) = 48 mA (C) ✓, spec ≤ 150 mA kept for the IGC033 fallback (76 mA) ✓; `VDRV_PG` → RP2350 GPIO33 in C, D and E ✓; 3V3_A ≤ 15 mA ✓; +3V3 to D ≤ 85 mA ✓; +5V to D 24 mA ✓; +15 V / −15 V 120/110 design, 200/190 fault (F) with C's 135/215 kept as margin ✓; 3V3_Q 35 mA ✓ gated by +15 V ≥ 7.1 V ✓; +5V at the relays ≥ 4.84 V vs ≥ 4.76 V ✓; +1V1 1.107 V (1.080–1.134) ✓; +2V5 2.505 V, 50 mA ✓; `PG_5V_N`/`PG_3V3_N` low = good in C, E and `C-sequencing.md` ✓; `PD_PG_N` active low in C/E/F ✓; `AMP_ARM` 10 kΩ pull-down, PWM 4.7 kΩ pull-downs, `DC_x_n` 4.7 kΩ (D, E-pinmap) ✓; fsw 576 kHz and the 8–92 % clamp (139 ns, 82 steps) in D and E ✓; VBUS overvoltage scheme identical in D and B ✓.

Stale (fix the text; the first-named file is the stale one):
- `E-interfaces.md` signal table: `DC_W_n`/`DC_T_n` "10 kΩ pull-up" → 4.7 kΩ (D-dc-detect, E-pinmap).
- `F-interfaces.md` (update section) and `F-mute-relay.md`: `POE_LOSS_N` "10 kΩ pull-up" → 4.7 kΩ (E-interfaces, E-pinmap row A6); `E-pinmap.md` line "10 kΩ pull-up on the net (E)" in its summary table is also stale.
- `C-interfaces.md` interfaces table: `+5V` "0.86 A design" and `+3V3` "0.79 A design" → 0.76 / 0.66 A (its own budget); `C-sequencing.md` "VDRV 7.04 V" → 7.00–7.02 V; `C-3v3a-ldo.md` "LM5013 396 kHz" → ≈ 200 kHz.
- `D-interfaces.md`: "E sizes the noise shaper for 448 kHz, with 512 kHz as the fallback" and "Proposed changes 1" (IGC033 then IGB070 in one paragraph) are superseded by its own later sections; `D-current-sense.md` open question 1 ("200 ns met with 2 ns margin") is superseded; `D-short-detect.md` body still quotes 448 kHz ripple and the IGC033 7 ns turn-off (the header UPDATE supersedes).
- `architecture.md` (re-read after its 2026-11-08 update; the block D line is now current except for one number): rails line "TLV62569P / TPS62A02A" (the TLV62569 was dropped); block D line "16 ns dead time" → 20 ns setting (≈ 18 ns effective); Mermaid still shows "4× IGC033S10S1" and "forward 400 kHz" (now 737.28 kHz). `intent.md` R-02 still names IGC033S10S1 (R-33, R-50, R-53, R-54 are current). Lead's files.

---

## 4. Verdicts

- **Block C: PASS**, subject to recording m-1 (LM5017 TON spread; VDRV Rr → 330–390 kΩ recommended), m-2 (beat-rule premise and the ≈ −83 dBc residual, Fly-Buck/VDRV bands in the clock plan), m-4 and the stale numbers in §3. B1, B2 and M1 are closed.
- **Block G: NOT YET** — one resistor: `QWIIC_PWR_EN` pull-down 100 kΩ → **10 kΩ** (MAJOR-1 reopens CG-M2); then PASS. Qwiic cap, SMF6.0A, USB and display items re-derive.
- **Block D: PASS** — D-M1 and D-M2 are closed and the IGB070/576 kHz numbers re-derive (losses, Tj, dead time, bootstrap 4.09/5.32 V, VDRV 48 mA, short detector). m-3 (1 nH loop) becomes a phase 6 obligation; m-5 and n-1 are wording.
