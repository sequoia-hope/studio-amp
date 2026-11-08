# Phase 1 review — block D (GaN class-D power stage)

Date: 2026-11-07. Independent reviewer; judged from the artifacts only.
Scope: `design/parts/D-*.md` against `design/datasheets/*.pdf` (re-read by the reviewer, not the audit's quotes), `design/intent.md`, `design/architecture.md` ("Phase 1 reconciliation"), and `B-/C-/E-interfaces.md`. Method: `datasheet-audit.md` gate checklist and `review-protocol.md` datasheet cross-check. Every calculation below was redone from the datasheet values; stock was re-queried with `jlc_parts.py show` on 2026-11-07.

Recomputed and agreeing with the audit (no finding): IGC033S10S1 loss model (idle 1.93 W/channel, 2.29 W at 50 W/8 Ω, 2.42 W at 46 W/4 Ω, 3.23 W at 144 W/4 Ω, from Diagram 15/16 Qoss/Eoss, VSD Table 8, Diagram 11 Rds(on) ×1.65 at 100 °C); Tj 71 °C (4 °C/W region) at 46 W/4 Ω; dead-time resistor 31.6 kΩ → 15.9 ns (Eq. 4/5, inside 20 kΩ–1.8 MΩ); VDRV 15.4 mA per driver, 62 mA for four at 448 kHz (Eq. 8–10, Qg 14 nC max); CBST,min 174 nF (Eq. 7); VDD cap ≥ 5 × CBST; OCP threshold 2.396 V → 14.9 A, ±0.7 A; LC filter f0 60.2 kHz, Z0 7.56 Ω, Q 0.53/1.06 at 4/8 Ω, open-load peak +23 dB at 54 kHz with the 10 Ω/100 nF Zobel (+52 dB without), −47 dB at 896 kHz, CM ripple 1.07 V pp; Zobel 1.79 W at full-scale 20 kHz; SER2915H Isat 18/21.5/23.4 A, Irms 20 A, DCR 2.05 mΩ max; tweeter HPF corners 904/603/452 Hz, B32774D4226K 450 V, 14.5 A rms, 22 × 36.5 × 31.5 mm, 27.5 mm pitch; SMBJ51A/SMCJ51A VBR 56.7–62.7 V, VC 82.4 V; HMK325B7225KN −50 % at 48 V, HMK107B7104KA −65 %; ADS7042 divider 25.8, 3.19 V at 82.4 V ≤ AVDD + 0.3; LMV393 trip 28 ms at 48 V DC; MX2EDGRC 15 A; INA241 CM −5…110 V, swing 0.05–3.1 V; all packages match the MPN suffixes (PG-TSON-6, RVR, DDF, DCN, DCU, DBV, RTE, PW, D, SOD-323F, DO-214AA). Interfaces: PWM polarity (high = HS on), FAULT_x_n / DC_x_n / AMP_ARM polarities and pull-downs agree with `E-interfaces.md`; VDRV, 3V3_A, +3V3, +5V loads fit `C-interfaces.md`; the 51 V TVS scheme is identical in `B-interfaces.md`.

---

## BLOCKER

None.

## MAJOR

### M1. Bootstrap refresh at the 3 % duty clamp: HB−HS falls to ≈ 3.6–4.0 V at sustained maximum duty (below the 3.8 V recommended minimum, 0–0.3 V above UVLO)
- Files: `D-bootstrap.md` (UPDATE block, "Refresh at the 67 ns minimum LS on-time"), `D-lmg1210.md` ("Minimum pulse and duty limits"), `D-interfaces.md` (duty clamp 3–97 %).
- Datasheet: LMG1210 p.5 RSW 0.4 Ω typ at 100 mA (no max); p.4 VHB−VHS recommended 3.80–5.25 V; p.5 VHBF 3.30–3.65 V; p.11 §7.3.3 "the pulse widths of HO and LO are decreased from the PWM input by the chosen dead-times"; BAT46WJ VF 415/475 mV at 50 mA, 710/850 mV at 250 mA (typ/max).
- Problem: the audit models the recharge as an RC with 0.9 Ω and concludes an equilibrium droop of 0.26 V (HB−HS ≥ 4.34 V). Two datasheet facts are missing. (a) The LO pulse is the PWM low time minus the dead time: 67 ns − 16 ns = **51 ns** of bootstrap-switch conduction (47 ns at td max). (b) Replacing 17.4 nC in 51 ns needs an average of **0.34 A** (0.26 A even at 67 ns), at which the BAT46WJ drops ≈ 0.85 V typ (0.95 V max) and the switch ≈ 0.14 V; τ = (0.4 + ≈1.5 Ω diode slope) × 375 nF ≈ 0.7 µs ≫ 51 ns, so the current is set by that voltage headroom, not by τ. The equilibrium bootstrap voltage at sustained 97 % HS duty is then VDD − VF(0.34 A) − RSW·I ≈ VDD − 1.0 V: **≈ 4.0 V at VDD 5.0 V, ≈ 3.75 V at VDD min 4.75 V, ≈ 3.6 V with VF max** — below the 3.80 V recommended minimum and within 0–0.3 V of the HS UVLO falling threshold (3.30–3.65 V). Duty stays above 95 % for ≈ 9 % of a full-scale 20 Hz cycle (≈ 2100 PWM periods; the equilibrium is reached in ≈ 12), so this is the normal full-scale LF condition, not a corner. If HS UVLO trips, HO stops for tSTHS (up to 28 µs) at every signal peak; short of that, VGS 3.6–4.0 V at the peaks raises Rds(on) (Diagram 10: ×1.2 at 4 V, hot) and slows the hard edge (plateau current (3.8 − 2.6)/5.9 Ω ≈ 0.2 A → ≈ 13 ns), a signal-dependent edge error the open-loop THD budget does not include.
- Fix (any one, (1) preferred, (2) cheap to add): (1) widen the gateware clamp to ≈ 8–92 % (LS conduction ≥ 160 ns → I ≈ 0.11 A → HB−HS ≈ VDD − 0.55 V ≥ 4.2 V at VDD min; M ≤ 0.84 still gives 40.3 V pk = 101 W into 8 Ω, so R-50 holds; R-11/R-50's 144 W/12 A into 4 Ω is unaffected since 12 A × 4 Ω = 48 V is M = 1 anyway and already unreachable); (2) a lower-VF 100 V Schottky for D_BST (e.g. a 1 A SOD-123F part with VF ≤ 0.5 V at 0.3 A; check stock); (3) drop the per-cycle charge: HS gate pull-down 100 kΩ (−1.0 nC). Recompute the equilibrium with the chosen clamp and VF(I) in `D-bootstrap.md`, and add "scope HB−HS at 20 Hz full scale" to the bring-up list.

### M2. INA241 holds its output for 1 µs after a large common-mode ΔV/Δt — the ≤ 198 ns OCP claim does not hold for a hard output short
- Files: `D-current-sense.md` ("Speed", "PWM rejection"), `D-ocp-logic.md` (delay table), `D-interfaces.md` (OCP ≤ 198 ns), `D-output-inductor.md` (16 A worst case).
- Datasheet: INA241 §7.3.1.1 (p.15–16): "When INA241x senses the large common-mode ΔV/Δt transients, the device holds the output for 1 µs … if another common-mode transient occurs during the following 3 µs, the INA241x relies on high BW and AC CMRR". The ΔV/Δt threshold is not published.
- Problem: the audit treats the INA241 as a 1.1 MHz single pole (145 ns lag) and dismisses PWM rejection because the shunt's common mode is the filtered output (≈ 1 V pp ripple). That is true in normal running, but the fault R-54 exists for — output shorted to GND, to VBUS, or the two outputs together — collapses the 700 nF filter node through the short in tens of ns: a 24–48 V step at ≈ 0.5–1 V/ns at the shunt, exactly the "large ΔV/Δt" the hold is designed to catch. During the hold the comparators see a frozen 1.65 V while the current ramps at 4.9 A/µs; the trip then happens at ≈ 15 + 4.9 + 1.0 (198 ns) ≈ **20–21 A**, roughly 1.2 µs after the threshold. Consequences: SER2915H at 21 A is at its −20 % point (21.5 A at 25 °C; derating with temperature unpublished, open question 3), so dI/dt rises further; IGC033 (700 A pulsed) and the TVS energy budget (½·10 µH·21² = 2.2 mJ per inductor, within the 12.4 mJ scheme) survive; R-54's "≤ 200 ns" is not met for the fault it is written for.
- Fix: (1) state the two regimes in `D-current-sense.md` and `D-interfaces.md`: ramp faults (speaker impedance collapse, no CM step) ≤ ≈ 220 ns (see m5); hard shorts ≈ 1.2 µs / ≈ 21 A peak, and verify the inductor stays ≥ 70 % L at 21 A hot from Coilcraft's derating page; (2) ask TI for the ΔV/Δt threshold or measure it on the bench with a deliberate output short at bring-up; (3) if 21 A is not acceptable, lower the trip to 14 A (legitimate peak 13.4 A) or add an inductor-independent fast detector; (4) R-54 wording in `intent.md` should be revised to match whichever is chosen.

## MINOR

### m1. Effective dead time at the FETs is shorter than the 16 ns set by the resistors
- `D-lmg1210.md` "Dead time" still argues from IGB070 ("LO/HO sink 3 A into Qg 6.1 nC → < 2 ns"); the UPDATE says "edges 6–8 ns". LMG1210 tDEAD is specified at unloaded outputs (p.7). With IGC033 (Ciss 1.4 nF max, Qgd 2.6 nC, plateau 2.6 V) through 4.3 Ω: 5 V → plateau ≈ 4 ns, plateau ≈ 4.3 ns → ≈ 8 ns turn-off; turn-on to Vth ≈ 3 ns. Effective dead time ≈ 11 ns nominal, ≈ 7–8 ns at tDEAD −20 % (Table p.7: 16/20/26 ns at 20 kΩ). No shoot-through, but the ZVS window the loss model credits is ≈ 11 ns, not 16 (idle loss moves toward the audit's 12 ns column, +0.5 W both channels). Fix: correct the text; keep td = 16 ns; measure at bring-up.

### m2. Loss model uses the typical driver source current
- `D-gan-fet.md` "Loss model": plateau current 0.41 A from VDD/IOH = 5/1.58 Ω. IOH min is 0.85 A (p.6) → ≈ 0.28 A → t_sw ≈ 11 ns. Re-running the same model: 46 W/4 Ω 2.54 W/ch (+5 %), 144 W/4 Ω 3.52 W/ch (+9 %) → Tj ≈ 123 °C with no panel path at 448 kHz. Fix: state that the R-61 panel path is required at every fsw for the 144 W upper bound, not only at 512/672 kHz.

### m3. Switching overshoot budget of "≈ 10 V" is optimistic
- `D-gan-fet.md` abs-max table, `D-vbus-tvs.md` "vs GaN 100 V". With the stated 1 nH loop and Coss 590 pF (Table 6), I·√(L/Coss) ≈ 16 A × 1.3 Ω ≈ 21 V (12 A: 16 V). Normal 48 + 21 = 69 V ✓ (80 % rule met); TVS clamp 82.4 + 21 = 103 V exceeds the 100 V continuous rating and rests on the 120 V / 1 h pulsed rating (Table 2 note 1). Acceptable only because a 7.3 A TVS pulse and a hard edge at the trip current are independent rare events; say so, and set the phase-6 loop target from this number.

### m4. LMV393 input common-mode range at 3.3 V
- `D-dc-detect.md` ratings table says ≈ −0.1…2.6 V. The datasheet gives VICR −0.1…2.0 V at 2.7 V and −0.1…4.2 V at 5 V, i.e. VCC − 0.7…0.8 V → ≈ 2.5 V at 3.3 V. The offset node reaches 2.3 V at full modulation (0.2 V margin) and 2.63 V at the 55 V gateware stop. Beyond VICR the comparator output is undefined (a false DC trip at the stop level is harmless, but the table is wrong). Fix: R_bot 82 kΩ / R_bot' 91 kΩ (gain ≈ 1/27.8, threshold re-scaled), or state the exclusion.

### m5. OCP delay budget omits comparator overdrive build-up
- `D-ocp-logic.md` delay table uses TLV3502 12 ns at 5 mV overdrive. The INA241 output moves at 0.25 V/µs for a 4.9 A/µs ramp, so 5 mV of overdrive exists only 20 ns after the crossing. Worst case ≈ 218 ns even without M2. Fix: add the term; with M2 the "≤ 200 ns" statement in `D-interfaces.md` baseline line 9 must change.

### m6. Inductor core loss placeholder (0.2 W per part) is unverified and may dominate idle loss
- `D-output-inductor.md` open question 1. The SER2915H sheet gives no core-loss data (p.1 "See www.coilcraft.com/coreloss"). At 448 kHz with 2.68 A pp in a gapped ferrite sized for DC current, several hundred mW per part is plausible; four parts could add 1–2 W to the ≈ 5.2 W idle figure that R-33a is already 0.5 W short on. Fix: run the Coilcraft calculator (448 kHz, 2.68 A pp, 0/3.5/6 A DC) for SER2915H-103 and XAL1510-103 before the budget is frozen, as the audit intends; record the result in the file.

### m7. VBST maximum uses VF(min) = 0.21 V
- `D-bootstrap.md` UPDATE: 5.25 − 0.21 + 0.09 = 5.13 V. At equilibrium the recharge current tends to zero and VF → ≈ 0.10–0.17 V (BAT46WJ 175 mV typ at 0.1 mA), so VBST max ≈ 5.24 V: at the LMG1210 recommended 5.25 V, 0.26 V inside the 5.5 V abs max and the GaN recommended max. Acceptable; state the real margin.

### m8. Thin single-source stock on the inductor
- SER2915H-103KL: 63 in stock for 22 needed (2.9×), one supplier line; XAL1510-103MED 191. Order or reserve early (same instruction as for the FETs).

## NOTE

- n1. `D-driver-passives.md` PWM pull-down rationale cites a "Gowin weak pull-up ≤ 150 µA"; the ECP5 defaults to pull-down (`E-interfaces.md` item 7). The 4.7 kΩ is still a sensible backstop; update the text.
- n2. `C-interfaces.md` line 100/170 still carries the IGB070 VDRV figures (42–79 mA); D now specifies 62–128 mA, ≤ 150 mA. C's 200 mA design covers it; C's table should be updated.
- n3. ADS7042 back-power clamp D_VCL: BAT46WJ IR at 125 °C is up to 12 µA at 1.5 V reverse → 12 µA × 2.12 kΩ ≈ 25 mV ≈ 1.2 LSB of gain error at high temperature. Note it in `D-vbus-adc.md`; calibration covers it.
- n4. The LMG1210's 1 kΩ across the bootstrap switch (§7.3.1) also charges CBST during dead times when VHS ≈ −VSD ≈ −3 V (≈ 3 mA × 16 ns × 2 ≈ 0.1 nC/cycle): negligible overcharge, but worth one line in `D-bootstrap.md` since it is the only overcharge path.
- n5. Shunt parasitic inductance (≈ 1 nH) adds ≈ 2.4 mV of triangle to the 6.7 mV ripple signal (ripple dI/dt ≈ 2.4 A/µs); zero-mean, but it biases the edge-sampled current used for dead-time compensation. Kelvin layout and a bench check of the ripple reading are enough.
- n6. SMBJ51A sits between 51 V (VWM) and 56.7 V (VBR min) whenever VBUS is between the 52 V restart and 55 V stop levels; leakage there is unspecified but sub-mA, thermally harmless. Note only.
- n7. Gateware dependencies carried by block D that are load-bearing for hardware safety or ratings: duty clamp (M1), subsonic HPF ≥ 15 Hz (DC detector), Zobel power limiter ≤ 1 W, VBUS stop at 55 V. `E-interfaces.md` lists them; the clamp value must be updated if M1 fix (1) is taken.

---

**Verdict: block D does not pass phase 1 as written — resolve M1 (bootstrap refresh margin at the duty clamp) and M2 (INA241 1 µs hold vs the R-54 claim), correct the stated numbers in m1–m5, then re-gate; no part change is forced, the fixes are a clamp value, optionally a diode, and honest requirement wording.**
