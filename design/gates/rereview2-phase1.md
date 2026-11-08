# Phase 1 third-pass review — targeted close-out of the second-pass items

Date: 2026-11-08. Independent third-pass reviewer (artifacts only; no author conversation seen).
Scope: `rereview-phase1-AB.md` AB-B1, AB-M1…M3; `rereview-phase1-CGD.md` CG-M2/MAJOR-1; PoE-loss
coverage as a whole (R-32a, R-34); VDRV_PG and LM5017 retiming spot-checks. Every number below was
recomputed from the PDFs in `design/datasheets/` (pdftotext; the SCTF sheet rendered): UCC2897A
SLUS829E, NCP4306 rev 6, TLV3201/3202, SN74LVC1G123 SCES586D, SN74LVC1G08, SN74LVC1GU04, 74HC4017
(Nexperia), SCTF SXMH, BAT54S, TCA9617B SCPS259F, TPS2553, LM5017, TPS2373, TL431.

## 1. Item status

| Item | Status | Reason |
|---|---|---|
| **AB-B1** PoE-loss detector false trip | **NOT CLOSED** → **BLOCKER-1** | The DRV_FWD gate does remove the DCM/skip *level* false trip (NCP4306 p.5/8: VTH_CS_ON −40…−120 mV so the body diode triggers every real conduction; VTH_CS_RESET 0.4–0.6 V, so no re-trigger inside an on-time; DRV held low without VCC; LLD "D" 540 µs disables the driver after a gap and wakes in 1.5–3 µs → no pulse, no trip). But the leading-edge race was budgeted with τ ≈ 40 ns and no comparator delay. Re-derived (below) the P′·L overlap at VPRI 41–44 V is 150–455 ns against a qualifier that can be as fast as 140–250 ns: the detector can assert in normal low-line operation. The "0.1 V gap to LINEUV" is also wrong (below), though benign because LINEUV is a 45–80 ms soft-stop. |
| **PoE-loss coverage** R-32a / R-34 | **NOT CLOSED** → **MAJOR-1** | No path mutes within R-34's window in every case. `PD_PG_N` rises 45–140 ms after LINEUV (soft-stop), not "within µs"; the VBUS-droop detector named in R-32a is specified nowhere (D-interfaces, E-interfaces); "VBUS valid" has no threshold. |
| **AB-M1** SYNC above VREF + 0.3 V / VREF off | **CLOSED for the level problem**, **MAJOR-2** on the VREF budget | With VCC = VREF no logic high can exceed VREF (abs max p.5) and nothing drives SYNC while VREF is off ✓. The VREF load's largest term (LVC1GU04 in linear mode) has no datasheet figure and the stated relief resistor cannot work. |
| **AB-M2** frozen counter holds SYNC high | **CLOSED** (two MINORs) | SYNC = Q1 · CLK_OK; Q5-9 is LOW in states 5–9 (Nexperia p.2) → 737 kHz 50 % square; MR, CP1 tied low (Table 3) ✓. Pump τ = 100 µs: CLK_OK ≈ 4.4 V falls to the UCC2897A SYNC VIL 1.6 V (p.7) in ≈ 100 µs ✓; converter off ≤ 0.1 ms only if Q1 froze high. Start-up: CLK_OK = 0 until CO toggles → free-run first, sync later, no deadlock ✓. |
| **AB-M3** `ACF_PULSE` definition and gateware rule | **NOT CLOSED** (MINOR, documentation) | `ACF_PULSE` = buffered DRV_FWD is right and agreed. But the gateware rule is recorded two different ways: B-interfaces.md and E-pinmap.md B6 = run-average rule; E-interfaces.md §"Converter-clock-fault rule" = Option P grid-lock ±3 % (its own NOTE-1 row says run-average). Both catch a dead crystal and neither mutes with no pulses; pick one (m-1). |
| **CG-M2 / MAJOR-1** TCA9617B EN | **CLOSED** | II(EN) = −25 µA at VI = 0.2 V, VCCB 3.3 V (TCA9617B p.6) → Rpu,int ≈ 124 kΩ. 10 kΩ → 0.25 V (0.5 V even at twice the current) < VIL(EN) 0.3·VCCB = 0.99 V (p.5) and < TPS2553 VIL 0.66 V (p.5, IEN ±0.5 µA). States: +3V3 up / FPGA unconfigured (pull-down adds 30–150 µA, lower still) ✓; configured and Hi-Z ✓; FPGA unpowered ⇒ +3V3 absent ⇒ VCCB absent ✓; driven high 3.3 V ≥ VIH 0.7·VCCB = 2.31 V, 0.33 mA load ✓. J16's hot-socket partner K15 is NC ✓. |
| **VDRV_PG 4.7k/2.7k, LM5017 retiming** | **CLOSED** (one MINOR) | 7.0 V → 2.55 V (2.51 V at 6.87 V; 2.34 V at the TLV6703 6.40 V trip) ≥ RP2350 VIH; FB-OV fault 9.3 V → 3.39 V < IOVDD + 0.5 V abs max; TLV6703 sinks 1.5 mA ✓. LM5017 TON (p.5): 188/250/336 ns at 48 V/100 kΩ → K = 0.90/1.20/1.61 × 10⁻¹⁰. VDRV (RON 191 k, Rr 360 k, Cr 1 nF): Vr(TON min, 36 V) = 29 × 477 ns/360 µs = 38 mV ≥ 25 mV (p.9); 75 mV at TON max/56 V; offset 19–37 mV × 5.64 → 7.02–7.12 V typ, 6.87–7.26 V over the 1.20–1.25 V reference, inside 7.0 V ± 5 %; f = 7/(K·191 k) = 305 kHz (228–407) ✓. Fly-Buck (RON 330 k, Rr 390 k): f = 18.4/(1.2e-10 × 330 k) = 465 kHz (347–620); Vr 37–91 mV; VOUT1 18.3–18.7 V ✓. |

## 2. Re-derivations behind the open items

**BLOCKER-1, leading-edge race (`B-poe-loss-detect.md` "Leading edge").** Divider Thevenin 6.29 kΩ;
SWDIV stray 2–4 pF; TLV3201 input 2 pF common-mode + 4 pF differential (tlv3202 p.5) behind the 10 kΩ
series resistor. Elmore delay = 6.29 k·(Cn + Cin) + 10 k·Cin = 78–123 ns, not 40 ns. SWDIV must reach
97.4 % of its final value at VPRI = 41 V (Vf = 2.561 V): from 0 V (CCM) ln 38.8 = 3.66 τ = 285–450 ns;
from VBUS/31.8 = 1.5 V (DCM dead time) ln 16 = 2.77 τ = 215–340 ns. Add TLV3201 tPD ≤ 50 ns at 20 mV
overdrive (p.6; the overdrive here builds slowly) → L stays high 265–500 ns after the plateau rises. P′ is
valid 45–75 ns after conduction starts (tPD_ON 30–60 ns, p.6, + the 10 k/4.99 k node). Overlap P′·L:
≈ 190–455 ns at 41 V, 160–370 ns at 42 V, 150–300 ns at 44 V, 110–230 ns at 48 V, 60–150 ns at 57 V.
Qualifier: SCES586D only guarantees VIH 2.0 V / VIL 0.8 V at 3.3 V (p.4), so the B-input VT+ may lie
anywhere in 0.8–2.0 V; t = 495 ns × ln(3.3/(3.3 − VT+)) = 140–460 ns (the file's 248 ns assumes VT+ ≥
1.3 V, which is not specified). Overlap ≥ qualifier is therefore possible up to ≈ 48 V and likely below
44 V. A compliant Class 6 link at 100 m from a 50 V PSE delivers 42.5 V at the PI (802.3bt), i.e. VPRI ≈
42.3 V: normal operation, amp muted. The author's "2.1× margin" does not survive the datasheet Cin, tPD
and the unspecified Schmitt threshold.

**Threshold vs LINEUV-off.** UCC2897A p.7: VLINEUV 1.243–1.294 V, ILINEUVHYS 11.5–14.5 µA (±11.5 %);
IHYST = 0.125 V/RDEL (eq. 8). With the 1 % parts listed in `B-controller.md`: VON,max = 1.294 ×
(73.93 k + 2.346 k)/2.346 k = 42.1 V; IHYST,min = 0.125/4.575 k × 0.885 = 24.2 µA; VOFF,max = 42.1 −
24.2 µA × 73.93 k = **40.3 V** (39.5 V even with 0.1 % divider resistors), above the detector's
39.2–39.3 V minimum. The author scaled VOFF by the threshold tolerance only (39.2 V). Consequence for a
cable pull is benign: LINEUV is a soft-stop (§8.3.1.10, §8.3.1.15, §8.3.3): SS discharges at ISSD =
0.43·IRON ∝ 1/RON (p.7: 10.5–18.5 µA at 75 kΩ → 25–44 µA at 31.6 kΩ) and OUT/AUX keep switching until SS
= 2.5 V, i.e. **45–80 ms of pulses with a falling plateau**, so the detector still asserts. Correct the
text and the behaviour table. Note also: with Lo = 68 µH the DCM on-time is ton = √(Io/2.83e11 s⁻²) at
Vin 40 V, so ton ≥ 0.46 µs for Io ≥ 0.06 A (3 W); the "light-load not covered" limitation only exists
below the logic idle load — but any fix to BLOCKER-1 that lengthens the qualifier moves that line;
recompute it.

**MAJOR-1, coverage.** (1) `POE_LOSS_N`: covers CCM and DCM with ton ≳ 0.5 µs while VPRI falls through
39.2–40.7 V, latency ≤ 0.5 µs, once BLOCKER-1 is fixed. Loss during skip or LLD-disabled operation is
covered when pulses resume: PD bulk 55 µF at ≈ 12 W falls 4.5 V/ms, so ≈ 3 ms. (2) `PD_PG_N`: TPS2373 PG
stays high-Z on input loss (A-interfaces item 5); the 2N7002 on SS/SD releases only when SS < VGS(th)
1.0–2.5 V, i.e. 45–80 ms (soft-stop to 2.5 V) + 0–60 ms after LINEUV — **45–140 ms**, which no file
states; E-interfaces treats "PD_PG_N rising" as a prompt trigger. Loss of VB_PRI (ISO7740 UVLO) is
no faster: 55 µF from 38 V to the LM5019's 7.5 V at ≈ 1 W of bias is ≈ 38 ms. PD fold-back at normal
VPRI is prompt (PG pulls SS/SD low through 1 kΩ) ✓. (3) Block F's D_PL diode acts on `POE_LOSS_N` only.
(4) VBUS droop: R-32a says "rectified pulse loss **or VBUS droop**, whichever trips first". No VBUS
undervoltage trigger exists in `D-interfaces.md` (ADS7042 is used for the 55/52 V OVP and feed-forward
only) or in E's gateware rules; "VBUS valid" (gates `POE_LOSS_N` and the clock check at start-up) has
no number anywhere. **Uncovered case:** a slow brown-out that settles between the detector band and
VOFF at the tolerance corner (≈ 39.3–40.3 V): soft-stop runs 45–80 ms with the amp unmuted while VBUS
collapses under load — 6 mF from 48 V to the LM5013's ≈ 32–36 V UVLO at 60 W is ≈ 50 ms — so the rails
drop before `PD_PG_N` rises: pop, R-34 broken. With BLOCKER-1 unfixed the same hole exists at any load
where the leading-edge race happens *not* to trip. **Fix:** add the backstop: "VBUS below ≈ 42 V
(under the 10 % sag `architecture.md` allows, above the LM5013 UVLO) for ≥ 0.5 ms ⇒ PoE lost: ramp to
zero, relays off" in `D-interfaces.md` (ADS7042, 576 kS/s) and `E-interfaces.md`; define "VBUS valid"
(e.g. > 45 V for 10 ms); state `PD_PG_N`'s 45–140 ms delay in `A-interfaces.md` and `E-interfaces.md`;
hold-up check: ½·6 mF·(42² − 36²) = 1.4 J ≥ 8 W × 20 ms ✓.

**MAJOR-2, VREF budget (`B-sync-clock.md`).** VREF: "approximately 5 mA", internally current-limited,
and "provides the supply rail for internal logic" (p.4, §8.3.1.4); 4.75–5.25 V for 0–5 mA (p.6). Loads:
74HC4017 CPD 35 pF (Nexperia p.9) → 35 pF × 25 V² × 7.37 MHz = 6.4 mW = 1.3 mA ✓; LVC1G08 ≈ 0; FB
pull-up ≤ 0.5 mA; SN74LVC1GU04: the datasheet gives ICC 10 µA static and Fig. 5 (≈ 1.4 mA at 5 V,
digital switching) — nothing for an inverter biased at VCC/2 by Rf, which conducts its shoot-through
current continuously. For a 32 mA-class output at 5 V that is plausibly 3–8 mA, i.e. possibly the whole
budget by itself, and an overloaded VREF starves the controller's own logic. The stated relief ("fit a
2.2 kΩ in the inverter's VCC") cannot work: 2.2 kΩ × 2 mA = 4.4 V of drop; at < 3 V the oscillator
output cannot reach the 74HC4017's VIH = 0.7·VCC = 3.15 V at 4.5 V (Nexperia p.7). **Fix:** put only the
SN74LVC1G08 on VREF — its VOH ≤ VCC = VREF keeps the abs max, its inputs are 5.5 V-tolerant with Ioff
(p.3–4), so the oscillator, counter and pump can run from a primary 5 V rail (HT7550 reinstated, or
block A's VISO_P5V 78L05 if its 118 °C TJ at 14.8 V tolerates +≈ 50 mW); add 10 kΩ SYNC-to-GND for the
VREF-off state (the UCC2897A's own ±600 µA SYNC driver, p.7, is overridden either way: 60 mV across
100 Ω). Alternatively measure the LVC1GU04's current at 5 V in Pierce mode before committing. CVREF
0.22 µF ✓ (§8.3.1.4, 1:10 to VDD's 11 µF ✓).

## 3. New findings

### BLOCKER
- **BLOCKER-1.** `B-poe-loss-detect.md` (Circuit 1, 4, 6; "Leading edge"). Datasheets: tlv3202 p.5
  (2 ‖ 4 pF input), p.6 (tPD 50 ns max at 20 mV overdrive); SCES586D p.4 (VIH 2.0 V / VIL 0.8 V only);
  NCP4306 p.6 (tPD_ON 30–60 ns). Problem and numbers in §2: the qualifier RC can be charged to VT+ by the
  leading-edge P′·L overlap at VPRI ≲ 44–48 V, muting the amp in normal low-line operation. Fix (any
  one, then redo the budget with the datasheet figures and bench it at 41–44 V, full load and 8 W):
  (a) compensate the divider — a 3.3 pF 250 V C0G across the 200 kΩ with ≈ 100 pF at SWDIV
  (200 k × 3.3 p ≈ 6.29 k × 103 p ≈ 0.65 µs) so SWDIV follows the plateau within the comparator's own
  tPD and L settles before P′ is valid; (b) delay only P′'s rising edge ≈ 300 ns (RC with a BAT54 for a
  fast fall) through an SN74LVC1G17 Schmitt before the AND; (c) replace the RC qualifier by a sampler
  (one-shot ≈ 350 ns from P′↑, flip-flop samples L·P′ at its end). Whichever is chosen, bound VT+ by
  VIH/VIL, not by an assumed 1.3–2.0 V, and quote the minimum detectable on-time that results.

### MAJOR
- **MAJOR-1.** PoE-loss coverage — `A-interfaces.md` (timing item 4–5), `D-interfaces.md`,
  `E-interfaces.md` (gateware rules), `B-poe-loss-detect.md`. UCC2897A §8.3.1.10/8.3.1.15/8.3.3, p.7
  (ISSD, ILINEUVHYS); TPS2373 PG behaviour on input loss. Problem and fix in §2.
- **MAJOR-2.** VREF budget — `B-sync-clock.md` (chain items 1–2, "VREF budget"). UCC2897A p.4/6,
  §8.3.1.4; SN74LVC1GU04 p.5 (no linear-mode ICC); 74HC4017 p.7 (VIH). Problem and fix in §2.

### MINOR
- **m-1.** One `ACF_PULSE` gateware rule, not two: B-interfaces.md and E-pinmap.md B6 say run-average
  (runs ≥ 64 intervals in 0.8–1.3 T averaging T ± 0.5 %), E-interfaces.md says Option P (grid ±3 %).
  Prefer the run-average rule: Option P's ±40 ns window against a stated ±30 ns edge movement leaves
  10 ns, and an interval is the difference of two edges. Add to the run-average rule: "≥ 64 consecutive
  intervals all < 0.8 T, or all in 1.3–1.9 T, is also a FAULT" — today a converter synchronised to an
  overtone (SYNC at 3 × 737 kHz → intervals 0.33 T) gives "no verdict" and the amp may start. Mirror in
  B, E (both tables), E-pinmap and D-interfaces.
- **m-2.** `E-interfaces.md` signal table and `E-pinmap.md` B6 still say `ACF_PULSE` comes from a
  "TLV3202 on +3V3"; it is 74LVC2G08 gate B. And `design/datasheets/` has no 74LVC2G08 sheet (only
  sn74lvc2g34.pdf): the 5.5 V-tolerant-input claim (P′ = 3.66 V at VDRVMAX 11 V with VCC 3.3 V) is
  unverified. Add the Nexperia sheet to sources-B.csv.
- **m-3.** `B-poe-loss-detect.md` threshold text: VOFF,max is 40.3 V (1 % parts) / 39.5 V (0.1 %), not
  39.2 V; the detector may trip *after* LINEUV at the corner and relies on the 45–80 ms soft-stop. Say
  so in "Calculations" and in rows 8–9 of the behaviour table; add the soft-stop to the bench case list.
- **m-4.** `B-sync-clock.md` CLK_OK into SN74LVC1G08: the pump node ramps ≈ 2.8 V in ≈ 100 µs on a
  clock loss, against the LVC input Δt/Δv ROC of 5 ns/V at 5 V (p.4). Harmless for the SYNC comparator
  (VIH 3 V / VIL 1.6 V), but out of spec; buffer CLK_OK with an SN74LVC1G17, or make the clock-OK detector
  a retriggerable SN74LVC1G123 on CO (tw ≈ 3 µs: clean edge, fallback in 3 µs instead of 100 µs).
- **m-5.** Crystal MPN decode (SCTF sheet p.2): SXMH7.3728**F2020F30** = AT fundamental, CL **20 pF**,
  **±20 ppm** tolerance, F = **−40…+85 °C**, **±30 ppm** drift: total ≈ ±50 ppm + 3 ppm/yr, not the
  "±10 ppm ± 20 ppm" written. Immaterial (≈ 40 Hz) but quote the sheet. ESR ≤ 60 Ω (6–10 MHz), DL 100
  typ / 500 µW max, C0 7 pF, 12.5 × 4.5 × 4.1 mm ✓; 33/33 pF + 5 pF stray = 21.5 pF vs 20 pF ✓; drive
  ≈ 1.1 mA rms × 60 Ω ≈ 70 µW ✓.
- **m-6.** `C-pm15-flybuck.md` Revision 3: the 0.61 A peak vs 0.7 A ILIM minimum ignores the 47 µH
  tolerance. At −20 % L, 56 V, TON max: ΔIL 0.95 A → Ipk 0.71 A at the design load (≈ 0.98 A at the
  200/190 mA fault load). Benign (COT inserts off-time) but state it, or RON 360 kΩ.
- **m-7.** During crystal start-up (ms) CP0 sees a growing near-sine; the counter may count irregularly
  while CLK_OK is partly charged, giving occasional long SYNC highs ("outputs off", §8.3.6) inside the
  60 ms soft-start. Harmless; state it and keep the bench item.

### NOTE
- n-1. NCP4306 LLD (internal 540 µs, position 6 "D"): after any gap > 540 µs the first 1.5–3 µs of
  pulses carry no DRV (p.6, tLLD_DIS_REC), so `ACF_PULSE` misses 1–2 edges after a long skip and the
  detector is blind for those cycles. Consistent with both files' "no verdict / no trip" logic; record it.
- n-2. The 74HC4017 runs at 7.37 MHz against fmax ≥ 24 MHz at 4.5 V (p.9) ✓; CP0 edge rate from the
  Pierce output ≈ 10 ns/V ≪ the HC limit ✓.
- n-3. UCC2897A SYNC in stand-alone mode is an *output* (≈ 5 V, ±600 µA, p.7); holding it low through
  100 Ω from the LVC1G08 is a 60 mV, 0.6 mA override and leaves the controller free-running ✓.

## 4. Verdict

**Phase 1 cannot pass yet.** Blocks A (as far as touched), C, D and G: no new blocking items; G's
MAJOR-1 is closed; the C spot-checks re-derive. Block B carries **BLOCKER-1** (the detector's
leading-edge race reproduces the AB-B1 symptom at low line), **MAJOR-2** (VREF budget rests on an
undocumented current and an unworkable relief), and the cross-block **MAJOR-1** (no VBUS-droop
backstop, `PD_PG_N` 45–140 ms late) that blocks A, D and E must also act on. Fix those three, correct
m-1…m-3, and re-review the detector and the sync chain; the rest is text.
