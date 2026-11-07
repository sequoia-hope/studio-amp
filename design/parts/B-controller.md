# U (B) — UCC2897A active-clamp forward PWM controller

Datasheet: datasheets/ucc2897a.pdf (TI SLUS829E, Aug 2008 rev. Apr 2015). Read: all sections.
Also read: TPS2373 datasheet sections 7.3.7 and 7.4.8 (datasheets/tps2373.pdf, block A's file) for the
start-up interface; PMP20878 schematic/BOM/test report (datasheets/ti-pmp20878-*.pdf).
MPN: UCC2897APWR (TSSOP-20)
Supplier: `C54444 UCC2897APWR (TI, TSSOP-20): extended, JLC stock 3944, lifecycle normal, checked 2026-11-07`
Alternate: `C469850 UCC2897ARGPR (TI, QFN-20-EP(4x4)): extended, JLC stock 183, lifecycle normal, checked 2026-11-07`
Choice: **TSSOP-20 (PW)**: 20× the stock, and TI's TSSOP pin-out is in Fig. 28. The QFN has better
θJA (34 vs 92 °C/W), not needed here: dissipation is the gate drive, ≈ 73 nC × 13.5 V × 400 kHz
≈ 0.39 W split between die, gate resistors and FET gates, ≈ 0.2 W in the die → ΔTj ≈ 18 °C
(θJA 92 °C/W).
Footprint: TSSOP-20 4.4 mm body, 0.65 mm pitch ("PW" package, datasheet p.36+ mechanical).
Pin numbers below are TSSOP (PW).

## Absolute max vs worst case

| Parameter | Abs max | Our worst case | Margin |
|---|---|---|---|
| VIN | 120 V | tied to VDD (13.5 V) — JFET start-up not used | OK |
| VDD | 16.5 V | 13.5 V ± 2 % (LM5019) | OK |
| FB, CS, SYNC, LINEOV, LINEUV | −0.3 to VREF + 0.3 V | LINEUV divider ≤ 1.8 V at 57 V; LINEOV ≤ 2.6 V at 57 V × DMAX | OK; LINEUV at 57 V = 1.79 V < 5.3 V |
| OUT/AUX peak | ±2.5 A | gate driven through 2.2 Ω; peak < 2 A | OK |
| Tj | 150 °C | ≈ 75 °C (55 °C air + 18 °C) | OK |

Recommended: VDD 8.5–16 V (we run 13.5 V); VDD bypass ≥ 1 µF; VREF ≥ 0.1 µF; Tj ≤ 125 °C.

## Required external parts (from datasheet)

| Pin | Part | Datasheet basis |
|---|---|---|
| VDD (17) | 1 µF X7R 25 V 0603 at the pin to PGND | p.4 pin table, §10 |
| PVDD (16) | 10 µF X7R 25 V 1206 to PGND; 0 Ω PVDD↔VDD at the IC | §10, §11.1 |
| VREF (6) | 0.1 µF X7R to GND (≥ 0.022, ≤ 22 µF; VREF:VDD ≥ 1:10 → 0.1 : 11 µF OK) | §8.3.1.4 |
| OUT (15) | 10 kΩ OUT→PGND; 2.2 Ω series to main FET gate | §8.3.1.13 |
| AUX (14) | 100 nF 25 V coupling cap + BAS316 clamp diode (anode gate, cathode clamp-FET source = RTN) + 10 kΩ gate–source, P-channel low-side clamp | §8.3.7, Fig. 24 |
| CS (9) | RF 1.00 kΩ + CF 82 pF C0G to GND (range 50–270 pF) | §9.2.2.6 |
| RSLOPE (10) | 180 kΩ to GND | eq. 28 |
| RON (4) / ROFF (5) / RDEL (3) | 48.7 k / 38.3 k / 4.53 k, 1 %, at the pins to GND | eq. 2, 3, 19 |
| SS/SD (12) | 100 nF X7R to GND; TPS2373 PG drives this pin (see below) | eq. 13, 14 |
| FB (11) | 4.99 kΩ to VREF (pull-up), opto collector, 6.8 nF to GND | §8.3.1.9, `B-feedback.md` |
| LINEUV (18) | 73.2 k / 2.37 k divider from VPRI | eq. 21–25 |
| LINEOV (19) | output OVP: N5 → BAS316 → 47 k / 470 k / 23.7 k ‖ 47 nF (see below) | eq. 9, VBUS scheme |
| SYNC (7) | open (no capacitance, §8.3.1.5) | |
| GND (8) / PGND (13) | separate small-signal ground island, joined to PGND only at the IC (net tie) | §8.3.1.6, §11.1 |
| VIN (1) | tied to VDD (JFET unused) | see "Start-up" |

## Calculations

**Oscillator (eq. 2–5), fsw = 400 kHz, DMAX = 0.68, tDEL = 50 ns:**
- RDEL = tDEL × 0.91e11 (eq. 19) = 4.55 kΩ → **4.53 kΩ** → tDEL = 49.8 ns. (Eq. 1 prints a 15 ns
  offset; Fig. 15 and the table value 110 ns at 10 kΩ follow eq. 19.)
- RON = (tON + tDEL)/36.1e-12 (eq. 11) = (1.700 + 0.050) µs / 36.1e-12 = 48.5 kΩ → **48.7 kΩ**.
- ROFF = (tOFF − tDEL − 170 ns)/15e-12 (eq. 12) = (0.800 − 0.050 − 0.170)/15e-12 = 38.7 kΩ → **38.3 kΩ**.
- Check: tON = 36.1p × 48.7k − 50n = 1.708 µs; tOFF = 15p × 38.3k + 50n + 170n = 0.795 µs;
  TSW = 2.503 µs → **399.6 kHz**, **DMAX = 0.683**.
- Tolerance: datasheet DMAX 66–74 % at 250 kHz for 70 % nominal; assume 0.63–0.73 here. Needed:
  0.59 at 41 V (`B-converter-design.md`).
- Turn-on delay 50 ns: main-FET drain falls from Vc to Vin with ≈ 1.2 A magnetizing current into
  ≈ 600 pF (main Coss + clamp Coss + winding) → ≈ 25 ns; rises at turn-off in ≈ 15 ns. 50 ns covers
  both; tune on the bench (RDEL 3.3–6.8 k footprint values).

**Soft-start (eq. 13, 14):** ISS = 0.43 × 2.5 V/48.7 kΩ = 22.1 µA; tSS = 10 ms →
CSS = 22.1 µA × 10 ms / 2 V = 110 nF → **100 nF** (tSS = 9.0 ms). ISS range ±28 % (ISSC
10.5–18.5 µA at RON 75 k) → 6.5–12 ms. tSS is the time to full current capability, not the VBUS
ramp; VBUS ramps in CC (`B-converter-design.md`).

**VDD bypass (eq. 15–18):** eq. 15 is printed as Qg(main)×Qg(aux)/0.1 V, which is dimensionally a
sum (charge/voltage): (40 nC + 25 nC)/0.1 V = 0.65 µF → 1 µF at VDD + 10 µF at PVDD.
CBIAS (eq. 18) is not needed: VDD comes from the 13.5 V primary bias buck from the start, so there is
no bootstrap hold-up interval. PBIAS = [3 mA + 73 nC × 400 kHz] × 13.5 V = 0.43 W (from the LM5019,
`B-bias.md`; the same rail also feeds block A's isolator primary, 15.3 mA).

**LINEUV (eq. 21–25):** IHYST = 2.5 V/4.53 kΩ × 0.05 = 27.6 µA. The off threshold is set by the
PD's input-current limit, not by regulation: TPS2373 RTN current ≤ 1.85 A recommended, and above
1.9 A for > 1.65 ms the PD folds back and drops PG (block A). At the Class 8 CC limit the input is
64.5 W/(η·Vin) = 1.85 A at Vin = 37.5 V (η 93 %) or 38.3 V (η 91 %). So **VOFF ≈ 38.4 V, VON ≈ 40.4 V**:
RIN1 = 2 V/27.6 µA = 72.5 k → **73.2 k**; RIN2 = 1.27 × 73.2k/(40.5 − 1.27) = 2.37 k → **2.37 k**.
Check: VON = 1.268 × 75.57/2.37 = 40.4 V; VOFF = 40.4 − 27.6 µA × 73.2 k = 38.4 V. Tolerance (threshold
1.243–1.294 V, IHYST ±11 %) → VOFF 37.6–39.2 V; at 37.6 V and η 91 % the input is 1.89 A, at the
fold-back edge but only at the worst corner of both tolerances. Both thresholds are below the 41 V
Class 8 minimum at the PD, so normal operation never trips it; VON 40.4 V is above the PD's 38.1 V
UVLO-on. Gotcha: at full Class 8 load on a long cable, stopping removes the cable drop, so VPRI can
bounce over VON and retry; 2 V hysteresis plus soft-start make this a slow hiccup, not a fault.
Divider power at 57 V: 43 mW (73.2 k 0805, 0.125 W rated) ✓.

**LINEOV = converter output OVP (agreed VBUS scheme, `B-output.md`).** Input OV is not needed
(PoE ≤ 57 V, block A's TVS; Vc ≈ 100 V regardless of Vin), so LINEOV watches VBUS from the primary,
independently of the opto: the T1 aux winding N5 (4 T, primary-side insulation, dot as N1) carries Vin
during the on-time, so its rectified average is ≈ Vin·D ≈ (VBUS + 0.25 V)/n in CCM.
- N5 → BAS316 → node A; 47 k node A → RTN (discharges it in the off-time; 57²/47 k × 0.43 = 30 mW).
- node A → 470 k → LINEOV; 23.7 k + 47 nF LINEOV → RTN (τ = 22.6 k × 47 nF = 1.06 ms; averages the
  400 kHz pulses and ignores the few-cycle duty transients of a load step).
- Trip at node-A average = 1.268 × 493.7/23.7 = 26.41 V. Node A ≈ (Vin − 0.7 V)·D, so VBUS trip
  ≈ 2 × 26.41/0.986 − 0.25 = **53.3 V** (51.2–55.4 V: threshold ±2 %, resistors ±1.5 %, diode
  ±0.4 %). Normal VBUS max 48.6 V; load-dump overshoot 24 mV ✓.
- Feedback failure (D = DMAX): trips whenever Vin·DMAX > 26.4 V → Vin ≥ 41.9 V (DMAX 0.63) or 38.8 V
  (DMAX 0.68). LINEOV disables OUT and AUX at once; its hysteresis current (27.6 µA × 22.6 k =
  +0.62 V) holds it until the average decays (≈ 1 ms after switching stops), then soft-start
  retries → hiccup.
- In DCM (light load) the average under-reads VBUS, so it never false-trips; it can miss a DCM
  over-voltage only in the residual window recorded in `B-output.md`.
- Pin check: max average 57 V × 0.73 = 41.6 V → 2.0 V (+0.62 V) at LINEOV < 5.3 V abs max ✓.
- Custom transformer (B option, N5 = 2 T): node A then carries Vin/4; rescale Rb to 95.3 k.

**Current sense (eq. 26–28):** Rcs = 68 mΩ (`B-primary-power.md`); RF 1.00 k, CF 82 pF → 1.94 MHz
filter, 82 ns time constant for leading-edge blanking of the drain-discharge spike.
Slope: magnetizing upslope already gives m > 1 (`B-converter-design.md`); add m = 0.5:
RSLOPE = 5 × 2 V × RF/(tON × m × dVL/dt) = 10 V × 1 k/(1.2 µs × 0.5 × 96 mV/µs) = 174 k → **180 k**.

**FB:** 4.99 k pull-up to VREF → opto current at FB = 2.5 V (zero duty) is 0.5 mA, at 4.5 V (DMAX)
0.1 mA; VREF load ≤ 0.5 mA (5 mA available). Usable range 2.5–4.5 V.

## Start-up interface with the TPS2373-4 (block A owns the PD)

Two ways exist (TPS2373 §7.3.7, §7.4.8). B uses the second:

1. *Advanced start-up (TI's PMP20878 way):* VC_OUT → PWM VDD, VC_IN ← bias winding. Rejected here:
   after start-up the PWM's whole bias current flows VC_IN → VC switch (13 Ω) → VC_OUT, and ours is
   ≈ 32 mA (73 nC × 400 kHz + 3 mA) against a recommended VC_OUT sourcing limit of 20 mA (TPS2373
   recommended operating conditions); and with a 4-turn primary there is no usable bias winding.
2. ***Used: VC_OUT unused, VC_IN = the PWM bias supply*** ("If VC_OUT is not used, VC_IN must be
   connected to the low voltage bias supply of the PWM controller", §7.3.7):
   - **VDD/PVDD ← B's primary LM5019 buck, 13.5 V** (`B-bias.md`). 13.5 V is above UCC2897A UVLO-on
     (12.2–13.2 V) and below its 16 V recommended maximum; TPS2373 VC_IN 13.5 V < 15 V recommended.
   - **TPS2373 VC_IN ← the same 13.5 V**; VC_OUT keeps its 1 µF and nothing else; UVLO_SEL open
     (block A).
   - The LM5019 starts at VPRI–RTN ≈ 30 V (its UVLO divider), i.e. during the PD inrush; its load
     then is the idle UCC2897A (≈ 3 mA) plus block A's isolator primary (≤ 15.3 mA): ≈ 0.25 W at 13.5 V,
     ≈ 10 mA from VPRI at 30 V — within block A's ≤ 30 mA allowance against the 335 mA inrush limit
     (TPS2373 ends inrush when its current falls below 90 % of the limit, p.18).
   - **TPS2373 PG → UCC2897A SS/SD** through 1 kΩ. PG is open-drain, active-high, referenced to RTN,
     0–57 V rated: low during inrush holds SS < 0.5 V (shutdown); release starts the soft-start.
   - **VIN pin tied to VDD.** The JFET is not needed (VDD comes from the buck), and VIN on VPRI would let
     the JFET draw from VPRI during inrush.
- Common reference: UCC2897A PGND/GND, Rcs, the LM5019 RTN and the clamp all return to `VPRI_RTN`
  (= TPS2373 RTN).

## Fine print / gotchas

- JFET must not be used while gate drives switch (§8.3.1.16); irrelevant with VIN = VDD.
- CS needs the RC filter; never connect CS directly to Rcs (§8.3.1.7).
- SYNC: no capacitor; must stay open (§8.3.1.5).
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

1. Confirm VIN-to-VDD is acceptable to TI (the pin table says VIN connects to the input rail when the
   JFET is used; nothing forbids tying it to VDD). Alternative: VIN to VPRI through 100 kΩ, which
   limits JFET current to < 0.5 mA during inrush. Footprint both (0 Ω to VDD fitted, 100 k DNP).
2. DMAX tolerance at 400 kHz is extrapolated; measure at bring-up.
