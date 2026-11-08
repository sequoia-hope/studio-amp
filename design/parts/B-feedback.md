# Block B feedback across the barrier — TL431 voltage loop, TL431 + INA281 current loop, optocoupler, Y-capacitor

Loop design and CC rationale: `B-converter-design.md`. Everything here is on the secondary except
the opto's phototransistor (primary, at UCC2897A FB) and the Y-cap (across the barrier).
Secondary bias `VSR` = 10 V from B's secondary LM5019, running from VBUS ≥ 7.5 V (`B-bias.md`).

---

## U (CV) — TL431BIDBZR, voltage error amplifier

Datasheet: datasheets/tl431.pdf (TI TL431/TL432). Read: all.
Supplier: `C41283 TL431BIDBZR (TI, SOT-23-3): extended, JLC stock 149263, lifecycle normal, checked 2026-11-07`
(B grade = 0.5 %; A grade TL431AIDBZR C23892 is 1 % and would eat half of the ±2 % budget.)

| Parameter | Datasheet | Our case |
|---|---|---|
| VKA | 37 V abs max, 36 V recommended | cathode ≤ VSR = 10 V ✓ |
| Vref | 2.495 V; B grade ±0.5 % at 25 °C | |
| Iref | 2 µA typ, 4 µA max | through Rtop 47.5 k → 0.10–0.19 V (0.2–0.4 %) |
| IKA(min) | 1 mA (max) | 1 kΩ across the LED gives ≥ 1.1 mA |

Divider: **Rtop 47.5 k, Rbot 2.61 k, 0.1 % 0603** → Vout = 2.495 × (1 + 47.5/2.61) = **47.90 V**
(+ Iref·Rtop ≈ +0.1 V typ → 48.0 V). Divider current 0.96 mA, 46 mW total (Rtop 44 mW: 0603 is
0.1 W → use 0805 0.125 W for Rtop). Voltage across Rtop 45.4 V < 0805 rating (150 V) ✓.
Static error budget: Vref ±0.5 % + temperature drift (6–16 mV over range, ±0.6 %) + dividers
±0.2 % + Iref uncertainty ±0.2 % → **±1.5 %** ✓ R-33 (±2 %).

Compensation (type II, redone for review M2 with the 1.47 A/V plant, `B-converter-design.md`):
**R1 = 115 k** in series with **C1 = 4.7 nF** from cathode to REF (zero at 294 Hz); LED series
**RLED 499 Ω** from `VSR`; **1.00 k** across the LED (TL431 bias). On the primary: FB pull-up 4.99 k
to VREF, **6.8 nF** FB to GND (pole 4.7 kHz). **fc ≈ 1.0 kHz (0.5–2 kHz over CTR 0.5–2), phase margin
≈ 66° (56–68°)**.

---

## U (CC) — TL431BIDBZR current error amplifier + INA281A4 current-sense amplifier + 30 mΩ shunt

INA281 datasheet: datasheets/ina281.pdf (TI INA281). Read: all.
`C2864421 INA281A4IDBVR (TI, SOT-23-5): extended, JLC stock 60, lifecycle normal, checked 2026-11-07`
(60 in stock: enough for 5 boards + attrition; INA281A3 C1517407 (167, gain 100) is the fallback
with a 60 mΩ shunt.)
Shunt: **30 mΩ** 1 % 2512, UNI-ROYAL LR122WF300MT4E (LR12 series, 2 W; datasheets/uniroyal-lr122wf300.pdf).
Raised from 27 mΩ so the 0.44 A Type 2 set-point (review m1) still puts ≥ 2.495 V on the TL431.
`C2941066 LR122WF300MT4E (UNI-ROYAL, 2512): extended, JLC stock 10228, lifecycle normal, checked 2026-11-07`

| INA281 parameter | Datasheet | Our case |
|---|---|---|
| Common-mode | −4…110 V (survival −20…120 V) | VBUS 48 V; ≤ 82.4 V at the SMCJ51A clamp ✓ |
| VS | 2.7–20 V | VSR 10 V (≈ 7 V at start-up, in the buck's dropout) ✓ |
| Gain (A4) | 200 V/V, ±0.5 % | 6.0 V/A with 30 mΩ |
| Output swing | to VS − 0.15 V (max, 10 kΩ) | 7.8 V at the 1.30 A set-point ≤ 9.55 V ✓; 2.64 V (Type 2) works from VSR ≥ 2.8 V |
| Bandwidth | 1.3 MHz | |

Shunt power 1.30² × 0.030 = 51 mW (2 W part) ✓. Placed high-side between the output ceramics and the
bulk node, so it measures converter output current, not the amp's pulsed current.

**737 kHz ripple in the shunt (review m2).** The inductor ripple (0.55 A p-p at 57 V) divides
between the ceramics upstream of the shunt and the bulk downstream. Fixes:
1. **Six** 4.7 µF 100 V 1210 upstream of the shunt instead of three (≈ 14 µF effective → |Z| ≈ 18 mΩ
   at 620 kHz and ≈ 15 mΩ at 737 kHz, against 30 mΩ + ≈ 15 mΩ (bulk ESR + ESL) downstream). About
   25 % of the ripple, ≈ 0.15 A p-p, reaches the shunt → ≈ 1.2 V p-p at the INA281 output. At the Class 8 set-point (7.8 V)
   the peaks reach 8.4 V, under the 9.55 V swing limit, so there is no clipping and no bias in the
   average.
2. **RC at the INA281 output: 100 Ω + 470 nF** (τ 47 µs, pole 3.4 kHz; 737 kHz attenuated ≈ 215×
   → ≈ 7 mV). The 100 Ω is part of the CC divider's top resistor (below), so the set-points include
   it.
3. `IBUS_SENSE` is taken after the RC and divided 200 k / 100 k → 3.0 V at 1.5 A (source ≈ 67 kΩ).
   Block E fits 10 nF at RP2350 ADC4/GPIO44 (τ 0.67 ms, fine for telemetry). The INA281 runs from
   `VSR` (from VBUS), which can be up before +3V3. Pad injection is then ≤ 3.0 V/67 kΩ ≈ 45 µA,
   limited by the 200 k (block E records it as accepted).

**Set-points**, from the 91 % efficiency floor (review m1). Path: INA out → 100 Ω (RC) → Rtop
4.99 k (Rtop_eff 5.09 k) → TL431(CC) REF; Rbot 88.7 k to GND; Rsel0 4.22 k and Rsel1 5.90 k to GND
through 2N7002 switches driven by `ILIM_SEL0`/`ILIM_SEL1`, 100 k pull-downs, so the reset state is 00.
Check against the PD budget at 91 % (plus block A's worst 1.12 W, or 0.8 W at Type 2):
Class 8 1.30 × 48/0.91 + 1.12 = 69.7 W ≤ 71.3 W ✓; Type 2 0.44 × 48/0.89 + 0.8 = 24.5 W ≤ 25.5 W ✓;
Class 6 0.941 × 48/0.91 + 1.0 = 50.6 W ≤ 51 W ✓.

| ILIM_SEL1:0 | Rbot effective | Ratio | Limit | Use |
|---|---|---|---|---|
| 00 (reset) | 88.7 k | 0.9457 | **0.440 A** (21.1 W) | Type 2 / start-up |
| 01 | 4.02 k | 0.4417 | **0.941 A** (45.2 W) | Class 6 |
| 10 | 5.53 k | 0.5208 | 0.798 A | (spare; ≤ Class 6) |
| 11 | 2.39 k | 0.3198 | **1.300 A** (62.4 W) | Class 8 |

Every state is ≤ the Class 8 budget, so no GPIO combination can overload the PSE. Tolerance: INA
±0.5 %, shunt ±1 %, TL431B ±0.5 %, dividers ±0.2 %, 2N7002 Rds (≤ 5 Ω vs 4.22 k) → ≈ ±2.5 %. Firmware can trim further from `IBUS_SENSE`.
CC TL431 cathode → BAS316 → opto LED cathode (diode-OR with the CV TL431). Compensation: 100 k +
10 nF from CC cathode to REF (integrator, crossover ≈ 200–300 Hz; slow on purpose).
2N7002: `C8545 2N7002 (JSCJ, SOT-23): basic, JLC stock 5965601, lifecycle normal, checked 2026-11-07`.

---

## U (opto) — Lite-On LTV-217-B-G

Datasheet: datasheets/ltv-217.pdf. Read: all.
Supplier: `C115450 LTV-217-B-G (LITEON, SOP-4-175mil): basic, JLC stock 401833, lifecycle normal, checked 2026-11-07`
(basic part: no extended fee). PMP20878 used onsemi HMHA2801A (C258256, 3558 stock) — alternate.

| Parameter | Datasheet | Need |
|---|---|---|
| Isolation | 3000 Vrms (1 min) | 1500 Vrms (R-32) ✓ |
| CTR, rank B | 130–260 % at IF 5 mA, VCE 5 V | operating IF ≈ 0.2–1 mA, CTR lower there (~0.8–1.5); loop gain set for CTR ≈ 1, tolerates 0.5–2 (±6 dB on fc) |
| VCE | (≥ 35 V class) | FB ≤ 5 V ✓ |

The opto's own pole (CTR × RPU × Cce) with 4.99 k pull-up sits around 10–20 kHz (typical for this
class; not specified in the datasheet) — above fc = 1.5 kHz. CTR degrades with age and temperature;
the margin above covers a 2× fall.

---

## C (Y) — 2.2 nF Y2/X1 250 VAC, Murata GA355QR7GF222KW01L (2220)

Datasheet: datasheets/murata-ga355qr7gf222.pdf. Read: all.
Supplier: `C91600 GA355QR7GF222KW01L (muRata, 2220): extended, JLC stock 4992, lifecycle normal, checked 2026-11-07`
Between `VPRI_RTN` and secondary `GND`, at T1, to return the transformer's interwinding displacement
current (EMI, R-90).
- Class Y2 / X1 (IEC 60384-14), UL 60384-14 / VDE certified.
- Voltage proof 2000 Vrms for 60 s (datasheet test 3) ≥ R-32's 1500 Vrms 60 s ✓.
- Leakage during a 1500 Vrms 60 Hz hipot: block A's RJ45 shield network (1 nF ‖ 10 MΩ) sits in
  parallel with this Y-cap for the hipot, so the total is 3.2 nF: 2π × 60 × 3.2 nF × 1500 = 1.8 mA
  (hipot testers usually trip at ≥ 5 mA) ✓; with the DNP second Y-cap fitted, 2.6 mA ✓. At
  2250 V DC: 10 MΩ → 0.23 mA steady after charging ✓.
- Value: 2.2 nF is the typical PoE choice; footprint a second one (DNP) for EMI tuning. Block A's
  shield RC (R-10) is separate.

## Layout guidance

- Opto across the isolation keepout, its creepage counted in the phase 4 barrier; the Y-cap
  straddles it too (2220 body: terminations 5.7 mm long body, check creepage against the keepout).
- TL431s, dividers and the INA281 away from `SW_SEC` and the SR cell; divider Rbot and the TL431
  REF node short.
- Opto emitter and the FB cap return to the UCC2897A GND island.

## Open questions

1. CTR at 0.2–1 mA is not in the datasheet table (only at 5 mA); measure, or bench-check fc.
2. Loop values are starting points; phase 8 simulation and bench Bode plot.
