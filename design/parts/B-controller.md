# U (B) — UCC2897A active-clamp forward PWM controller

Datasheet: datasheets/ucc2897a.pdf (TI SLUS829E, Aug 2008 rev. Apr 2015). Read: all sections.
Also read: TPS2373 datasheet sections 7.3.7 and 7.4.8 (datasheets/tps2373.pdf, block A's file) for the
start-up interface; PMP20878 schematic/BOM/test report (datasheets/ti-pmp20878-*.pdf).
MPN: UCC2897APWR (TSSOP-20)
Supplier: `C54444 UCC2897APWR (TI, TSSOP-20): extended, JLC stock 3944, lifecycle normal, checked 2026-11-07`
Alternate: `C469850 UCC2897ARGPR (TI, QFN-20-EP(4x4)): extended, JLC stock 183, lifecycle normal, checked 2026-11-07`
Choice: **TSSOP-20 (PW)**: 20× the stock, and TI's TSSOP pin-out is in Fig. 28. The QFN has better
θJA (34 vs 92 °C/W), not needed here: dissipation is the gate drive, ≈ 73 nC × 14.3 V × 737 kHz
≈ 0.77 W split between die, gate resistors and FET gates; ≈ 0.38 W in the die → ΔTj ≈ 35 °C
(θJA 92 °C/W) → Tj ≈ 90 °C at 55 °C air. OK; the QFN (34 °C/W) is the alternate if bring-up shows heat.
Footprint: TSSOP-20 4.4 mm body, 0.65 mm pitch ("PW" package, datasheet p.36+ mechanical).
Pin numbers below are TSSOP (PW).

## Absolute max vs worst case

| Parameter | Abs max | Our worst case | Margin |
|---|---|---|---|
| VIN | 120 V | VPRI ≤ 57 V through 100 kΩ (recommended 18–110 V; review n3) | OK |
| VDD | 16.5 V | 14.3 V nominal, 13.8–14.9 V worst case (LM5019, review M1) | OK |
| FB, CS, SYNC, LINEOV, LINEUV | −0.3 to VREF + 0.3 V | LINEUV divider ≤ 1.8 V at 57 V; LINEOV ≤ 2.6 V at 57 V × DMAX | OK; LINEUV at 57 V = 1.79 V < 5.3 V |
| OUT/AUX peak | ±2.5 A | gate driven through 2.2 Ω; peak < 2 A | OK |
| Tj | 150 °C | ≈ 90 °C (55 °C air + 35 °C) | OK |

Recommended: VDD 8.5–16 V (we run 14.3 V); VDD bypass ≥ 1 µF; VREF ≥ 0.1 µF; Tj ≤ 125 °C.

## Required external parts (from datasheet)

| Pin | Part | Datasheet basis |
|---|---|---|
| VDD (17) | 1 µF X7R 25 V 0603 at the pin to PGND | p.4 pin table, §10 |
| PVDD (16) | 10 µF X7R 25 V 1206 to PGND; 0 Ω PVDD↔VDD at the IC | §10, §11.1 |
| VREF (6) | **0.22 µF** X7R to GND (recommended value; VREF also supplies the SYNC-driving SN74LVC1G08 only, ≤ 0.6 mA total with the FB pull-up; VREF:VDD 0.22 : 11 µF ≥ 1:10 ✓) | §8.3.1.4, `B-sync-clock.md` (AB-M1, MAJOR-2) |
| OUT (15) | 10 kΩ OUT→PGND; 2.2 Ω series to main FET gate | §8.3.1.13 |
| AUX (14) | 100 nF 25 V coupling cap + BAS316 clamp diode (anode gate, cathode clamp-FET source = RTN) + 10 kΩ gate–source, P-channel low-side clamp | §8.3.7, Fig. 24 |
| CS (9) | RF 1.00 kΩ + CF 82 pF C0G to GND (range 50–270 pF) | §9.2.2.6 |
| RSLOPE (10) | 316 kΩ to GND | eq. 28 |
| RON (4) / ROFF (5) / RDEL (3) | 31.6 k / 14.3 k / 4.53 k, 1 %, at the pins to GND | eq. 2, 3, 19 |
| SS/SD (12) | 1.0 µF X7R 16 V to GND (60 ms soft-start, review M5); TPS2373 PG drives this pin | eq. 13, 14 |
| FB (11) | 4.99 kΩ to VREF (pull-up), opto collector, 6.8 nF to GND | §8.3.1.9, `B-feedback.md` |
| LINEUV (18) | 73.2 k / 2.37 k divider from VPRI | eq. 21–25 |
| LINEOV (19) | output OVP: N5 → BAV21W → 47 k / 470 k / 23.7 k ‖ 47 nF (see below) | eq. 9, VBUS scheme |
| SYNC (7) | 737.28 kHz: 74HC4017 Q1 AND clock-OK (SN74LVC1G08 powered from VREF, so SYNC ≤ VREF; oscillator/counter on `V5_CLK`) through 100 Ω; **10 kΩ SYNC to GND** (VREF-off state); no capacitor (§8.3.1.5). Clock loss → SYNC forced low within 4 µs → free-running | `B-sync-clock.md` (AB-M1, AB-M2) |
| GND (8) / PGND (13) | separate small-signal ground island, joined to PGND only at the IC (net tie) | §8.3.1.6, §11.1 |
| VIN (1) | 100 kΩ to VPRI (fitted); 0 Ω to VDD (DNP) — agreed with block A (review n3/n10) | see "Start-up" |

## Calculations

**Oscillator (eq. 2–5) and SYNC: synchronised at 737.28 kHz, free-running ≈ 656 kHz.** The converter
must sit in 712–775 kHz over all tolerances (amp beat rule). The UCC2897A free-running oscillator is
±10 % over temperature with an internal timing capacitor, so it is synchronised to a crystal clock
(`B-sync-clock.md`, §8.3.6):
- RDEL = tDEL × 0.91e11 (eq. 19): 50 ns → **4.53 kΩ** (Fig. 15: 110 ns at 10 kΩ follows eq. 19).
- tOFF sets DMAX in sync: DMAX = 1 − tOFF/TSYNC. For 0.68 at TSYNC = 1.356 µs, tOFF = 0.434 µs →
  ROFF = (0.434 − 0.050 − 0.170) µs/15e-12 (eq. 12) = 14.3 kΩ → **14.3 kΩ**.
- RON sets the free-running frequency below the sync frequency: tON = 1.081 µs → RON = (1.081 +
  0.050)/36.1e-12 (eq. 11) = 31.3 kΩ → **31.6 kΩ**. Check: tON = 1.091 µs, tOFF = 0.435 µs → free-running
  **656 kHz**, 590–708 kHz with −10/+8 % (p.7), always below 737 kHz (4 % margin) ✓. Free-running DMAX
  = 0.715 (≈ 0.68–0.75).
- SYNC: 136 ns pulses (74HC4017 Q1 gated by clock-OK; only the LVC1G08 on VREF) through 100 Ω, 10 kΩ to GND; ≥ 50 ns ✓; < (1 − DMAX)·TSYNC = (1 − 0.73) × 1.356 = 0.37 µs ✓
  (eq. 10). No capacitor on SYNC.
- Synced DMAX: between 0.680 (1 − tOFF/TSYNC) and 0.715 (RON/ROFF ratio, which the datasheet says
  sync preserves; n-AB1); 0.664–0.73 with tolerances. Needed 0.64 at 38.4 V and 0.655 at 37.6 V ✓.
  Bench check.
- Turn-on delay 50 ns: the drain falls from Vc to Vin with ≈ 0.66 A of magnetizing current into
  ≈ 600 pF → ≈ 45 ns. That is near the 50 ns setting; footprint RDEL 3.3–6.8 k and tune on the bench.

**Soft-start (eq. 13, 14), lengthened for the PSE start-up limit (review M5):**
ISS = 0.43 × 2.5 V/31.6 kΩ = 34.0 µA; CSS = **1.0 µF** → tSS = 1.0 µF × 2 V/34 µA = **59 ms**
(ISS ±28 % → 46–82 ms). Why 60 ms: below VBUS ≈ 7.5 V the secondary control is unpowered, so only
this ramp bounds the input current; see `B-converter-design.md` start-up item 6 (≤ 0.51 A at 42 V,
under a Type 2 PSE's ≈ 0.6 A). Fault discharge is at ISSD (same magnitude), so a hiccup cycle is
≈ 0.1 s, which also keeps the average short-circuit input low. SS/SD shutdown threshold 0.4–0.6 V:
the TPS2373 PG pulls it low while sinking only the ≈ 34 µA soft-start current, so VOL is tens of mV
against its 0.27–0.5 V at 2 mA (review n5) ✓.

**VDD bypass (eq. 15–18):** eq. 15 is printed as Qg(main)×Qg(aux)/0.1 V, which is dimensionally a
sum (charge/voltage): (45 nC + 28 nC)/0.1 V = 0.73 µF → 1 µF at VDD + 10 µF at PVDD.
CBIAS (eq. 18) is not needed: VDD comes from the 14.3 V primary bias buck from the start, so there is
no bootstrap hold-up interval. PBIAS = [3 mA + 73 nC × 737 kHz] × 14.3 V = 0.81 W (56.8 mA from the
LM5019, plus 4 mA for the sync clock; `B-bias.md`; the same rail also feeds block A's isolator primary, 15.3 mA).

**LINEUV (eq. 21–25):** IHYST = 2.5 V/4.53 kΩ × 0.05 = 27.6 µA. The off threshold is set by the
PD's input-current limit, not by regulation: TPS2373 RTN current ≤ 1.85 A recommended, and above
1.9 A for > 1.65 ms the PD folds back and drops PG (block A). At the Class 8 CC limit (now 1.30 A → 62.4 W) the input is
62.4 W/(η·Vin) = 1.85 A at Vin = 36.3 V (η 93 %) or 37.1 V (η 91 %). **VOFF ≈ 38.4 V, VON ≈ 40.4 V**
(kept; the POE_LOSS_N threshold sits just above it):
RIN1 = 2 V/27.6 µA = 72.5 k → **73.2 k**; RIN2 = 1.27 × 73.2k/(40.5 − 1.27) = 2.37 k → **2.37 k**.
Check: VON = 1.268 × 75.57/2.37 = 40.4 V; VOFF = 40.4 − 27.6 µA × 73.2 k = 38.4 V. Tolerance (threshold
1.243–1.294 V, IHYST ±11 %) → VOFF 37.6–39.2 V; at 37.6 V and η 91 % the input is 1.82 A, under
1.85 A at every corner. Both thresholds are below the 41 V
Class 8 minimum at the PD, so normal operation never trips it; VON 40.4 V is above the PD's 38.1 V
UVLO-on. Gotcha: at full Class 8 load on a long cable, stopping removes the cable drop, so VPRI can
bounce over VON and retry; 2 V hysteresis plus soft-start make this a slow hiccup, not a fault.
Divider power at 57 V: 43 mW (73.2 k 0805, 0.125 W rated) ✓.

**LINEOV = converter output OVP (agreed VBUS scheme, `B-output.md`).** Input OV is not needed
(PoE ≤ 57 V, block A's TVS; Vc ≈ 100 V regardless of Vin), so LINEOV watches VBUS from the primary,
independently of the opto: the T1 aux winding N5 (4 T, primary-side insulation, dot as N1) carries Vin
during the on-time, so its rectified average is ≈ Vin·D ≈ (VBUS + 0.25 V)/n in CCM.
- N5 → **BAV21W** (250 V; review n2: N5 reverse voltage is Vc − Vin ≈ 50–70 V normally but follows
  the clamp in the DMAX-at-57 V transient, up to ≈ 150 V) → node A; 47 k node A → RTN (discharges it in the off-time; 57²/47 k × 0.43 = 30 mW).
- node A → 470 k → LINEOV; 23.7 k + 47 nF LINEOV → RTN (τ = 22.6 k × 47 nF = 1.06 ms; averages the
  737 kHz pulses and ignores the few-cycle duty transients of a load step).
- Trip at node-A average = 1.268 × 493.7/23.7 = 26.41 V. Node A ≈ (Vin − 0.7 V)·D, so VBUS trip
  ≈ 2 × 26.41/0.986 − 0.25 = **53.3 V** (51.2–55.4 V: threshold ±2 %, resistors ±1.5 %, diode
  ±0.4 %). Normal VBUS max 48.6 V; load-dump overshoot 24 mV ✓.
- Feedback failure (D = DMAX): trips whenever Vin·DMAX > 26.4 V → Vin ≥ 41.9 V (DMAX 0.63) or 38.8 V
  (DMAX 0.68). LINEOV disables OUT and AUX at once; its hysteresis current (27.6 µA × 22.6 k =
  +0.62 V) holds it until the average decays (≈ 1 ms after switching stops), then soft-start
  retries → hiccup.
- In DCM (light load) the average under-reads VBUS, so it never false-trips; it can miss a DCM
  over-voltage only in the residual window recorded in `B-output.md`.
- Pin check: max average 57 V × 0.72 = 41 V → 2.0 V (+0.62 V) at LINEOV < 5.3 V abs max ✓.
- The OVP band (51.2–55.4 V) overlaps the 55 V gateware stop, so on many units the gateware acts
  first; that is intended (review n1). OVP is the backstop for a feedback failure.
- Custom transformer (B option, N5 = 2 T): node A then carries Vin/4; rescale Rb to 95.3 k.

**Current sense (eq. 26–28):** Rcs = 68 mΩ (`B-primary-power.md`); RF 1.00 k, CF 82 pF → 1.94 MHz
filter, 82 ns time constant for leading-edge blanking of the drain-discharge spike.
Slope: magnetizing upslope already gives m > 1 (`B-converter-design.md`); add m = 0.5:
RSLOPE = 5 × 2 V × RF/(tON × m × dVL/dt) = 10 V × 1 k/(0.656 µs × 0.5 × 96 mV/µs) = 318 k → **316 k**
(tON at 50 V, 737 kHz).
CS filter vs the SR commutation spike (review n12): 1 k / 82 pF is inside PMP20878's 1 k / 47–100 pF;
bench-check that the start-of-on-time spike stays below 0.43 V at full load (CF footprint 47–150 pF).

**FB:** 4.99 k pull-up to VREF → opto current at FB = 2.5 V (zero duty) is 0.5 mA, at 4.5 V (DMAX)
0.1 mA; VREF load ≤ 0.5 mA (5 mA available). Usable range 2.5–4.5 V.

## Start-up interface with the TPS2373-4 (block A owns the PD)

Two ways exist (TPS2373 §7.3.7, §7.4.8). B uses the second:

1. *Advanced start-up (TI's PMP20878 way):* VC_OUT → PWM VDD, VC_IN ← bias winding. Rejected here:
   after start-up the PWM's whole bias current flows VC_IN → VC switch (13 Ω) → VC_OUT, and ours is
   ≈ 57 mA (73 nC × 737 kHz + 3 mA) against a recommended VC_OUT sourcing limit of 20 mA (TPS2373
   recommended operating conditions); and with a 4-turn primary there is no usable bias winding.
2. ***Used: VC_OUT unused, VC_IN = the PWM bias supply*** ("If VC_OUT is not used, VC_IN must be
   connected to the low voltage bias supply of the PWM controller", §7.3.7):
   - **VDD/PVDD ← B's primary LM5019 buck, 14.3 V** (`B-bias.md`; review M1). Worst case 13.8–14.9 V
     (LM5019 VFB 1.200–1.250 V, 1 % resistors): above UCC2897A UVLO-on max 13.2 V by ≥ 0.6 V, below
     its 16 V recommended maximum, and below TPS2373 VC_IN's 15 V recommended maximum.
   - **TPS2373 VC_IN ← the same 14.3 V**; VC_OUT keeps its 1 µF and nothing else; UVLO_SEL open
     (block A).
   - The LM5019 starts at VPRI–RTN ≈ 30 V (its UVLO divider), i.e. during the PD inrush; its load
     then is the idle UCC2897A (≈ 3 mA) plus block A's isolator primary (≤ 15.3 mA): ≈ 0.26 W at 14.3 V,
     ≈ 11 mA from VPRI at 30 V. Datasheet bound (TPS2373 p.7, confirmed by block A): inrush ends when
     IRTN falls below 65–99 % of the inrush limit, so the DC load at the end of inrush must stay below
     0.65 × 275 mA ≈ 179 mA. B's 11 mA is well under it (m-AB10).
   - **Line surge:** block A's input TVS is SMCJ58A (≤ 93.6 V at 16 A, ≈ 80 V at 6.5 A). B's VPRI
     parts are rated for it: ceramics and electrolytic 100 V, LM5019 100 V, UCC2897A VIN 120 V via
     100 k. The main FET is protected by peak-current mode's inherent line feed-forward: when Vin
     steps up, the current ramp steepens and each pulse ends at the same peak, so D falls within one
     cycle. Vc ≈ Vin²/(Vin − 24.4 V) = 127 V at 94 V, under the 150 V rating. Bench item: differential
     surge at full load, main-FET Vds.
   - **TPS2373 PG → UCC2897A SS/SD** through 1 kΩ. PG is open-drain, active-high, referenced to RTN,
     0–57 V rated: low during inrush holds SS < 0.5 V (shutdown); release starts the soft-start.
   - **VIN pin → VPRI through 100 kΩ (fitted); 0 Ω VIN–VDD footprint DNP** (review n3; agreed with
     block A, n10). This keeps VIN inside its recommended 18–110 V. The JFET is not needed (VDD comes
     from the buck). During inrush it can draw at most (VPRI − VDD)/100 k ≤ 0.5 mA, which is
     negligible against the 335 mA inrush limit, and it switches off once VDD ≥ 12.7 V.
- Common reference: UCC2897A PGND/GND, Rcs, the LM5019 RTN and the clamp all return to `VPRI_RTN`
  (= TPS2373 RTN).

## Fine print / gotchas

- JFET must not be used while gate drives switch (§8.3.1.16); it is off whenever VDD ≥ 12.7 V (the
  buck holds 14.3 V), and the 100 k limits it to ≤ 0.5 mA anyway.
- CS needs the RC filter; never connect CS directly to Rcs (§8.3.1.7).
- SYNC: no capacitor (§8.3.1.5). Sync must be faster than free-running (§8.3.1.5) and its pulse shorter than (1 − DMAX)·TSYNC (eq. 10), both met.
- Pulse skipping blanks both OUT and AUX (§8.3.5): prevents reverse saturation at light load.
- Soft-stop on LINEUV discharges the clamp cap safely (§8.3.3); LINEOV stops the outputs at once.
- OUT 10 kΩ to PGND recommended (§8.3.1.13).
- PGND/GND: one connection, at the IC (§8.3.1.6, §11.1).
- "Maximum pulse width needs to be less than DMAX" (EC note 5).

## Layout guidance from datasheet (§11)

- Net-tie GND–PGND between pins 8 and 13; RDEL, RON, ROFF, RSLOPE, CVREF, CF, CSS and the opto emitter
  on the GND island, next to their pins.
- VDD and VREF caps at the pins; PVDD 10 µF at PVDD–PGND; 0 Ω PVDD–VDD at the IC.
- OUT and AUX to the FET gates by short, wide, overlapping traces with their return; controller
  next to the FETs.
- RSLOPE node: minimise parasitic C and L.

## Open questions

1. Synced DMAX (tOFF tolerance at 737 kHz) is extrapolated; measure at bring-up.
2. Controller heating at 737 kHz (≈ 0.38 W in the die, TSSOP): check at bring-up; QFN is the alternate.

## Phase 2 schematic notes (iso_dcdc, 2026-11-08)

- UCC2897A symbol made in `lib/studio_B` (TSSOP-20 pin table p.4–5): line inputs left (VIN,
  LINEUV, SYNC, FB, LINEOV), supplies top (VDD, PVDD, VREF), drivers and CS right, SS/SD and the
  timing pins plus GND/PGND on the bottom; NC pins 2 and 20 hidden.
- Parts picked: CF 82 pF C0G `0603CG820J500NT` (FH, `C1683`); FB cap 6.8 nF X7R `0603B682K500NT`
  (FH, `C1631`) — the Samsung equivalents had no stock. OUT → 2.2 Ω `RC0603FR-072R2L` (`C112307`).
