# Block B feedback across the barrier — TL431 voltage loop, TL431 + INA281 current loop, optocoupler, Y-capacitor

Loop design and CC rationale: `B-converter-design.md`. Everything here is on the secondary except
the opto's phototransistor (primary, at UCC2897A FB) and the Y-cap (across the barrier).
Secondary bias `VSR` = 12 V from B's secondary LM5019 (`B-bias.md`).

---

## U (CV) — TL431BIDBZR, voltage error amplifier

Datasheet: datasheets/tl431.pdf (TI TL431/TL432). Read: all.
Supplier: `C41283 TL431BIDBZR (TI, SOT-23-3): extended, JLC stock 149263, lifecycle normal, checked 2026-11-07`
(B grade = 0.5 %; A grade TL431AIDBZR C23892 is 1 % and would eat half of the ±2 % budget.)

| Parameter | Datasheet | Our case |
|---|---|---|
| VKA | 37 V abs max, 36 V recommended | cathode ≤ VSR = 12 V ✓ |
| Vref | 2.495 V; B grade ±0.5 % at 25 °C | |
| Iref | 2 µA typ, 4 µA max | through Rtop 47.5 k → 0.10–0.19 V (0.2–0.4 %) |
| IKA(min) | 1 mA (max) | 1 kΩ across the LED gives ≥ 1.1 mA |

Divider: **Rtop 47.5 k, Rbot 2.61 k, 0.1 % 0603** → Vout = 2.495 × (1 + 47.5/2.61) = **47.90 V**
(+ Iref·Rtop ≈ +0.1 V typ → 48.0 V). Divider current 0.96 mA, 46 mW total (Rtop 44 mW: 0603 is
0.1 W → use 0805 0.125 W for Rtop). Voltage across Rtop 45.4 V < 0805 rating (150 V) ✓.
Static error budget: Vref ±0.5 % + temperature drift (6–16 mV over range, ±0.6 %) + dividers
±0.2 % + Iref uncertainty ±0.2 % → **±1.5 %** ✓ R-33 (±2 %).

Compensation (type II, starting values, `B-converter-design.md`): R1 = 1.78 × Rtop = **84.5 k**
in series with **C1 = 3.9 nF** from cathode to REF (zero at 483 Hz); LED series **RLED 1.00 k** from
`VSR`; **1.00 k** across the LED (TL431 bias). On the primary: FB pull-up 4.99 k to VREF, **6.8 nF**
FB to GND (pole 4.7 kHz). Expected fc ≈ 1.5 kHz, PM 55–65 °.

---

## U (CC) — TL431BIDBZR current error amplifier + INA281A4 current-sense amplifier + 27 mΩ shunt

INA281 datasheet: datasheets/ina281.pdf (TI INA281). Read: all.
`C2864421 INA281A4IDBVR (TI, SOT-23-5): extended, JLC stock 60, lifecycle normal, checked 2026-11-07`
(60 in stock: enough for 5 boards + attrition; INA281A3 C1517407 (167, gain 100) is the fallback
with a 54 mΩ shunt.)
Shunt: Yageo PA2512FKF7T0R027E, 27 mΩ 1 % 2512 (datasheets/yageo-pa2512-r027.pdf).
`C6141173 PA2512FKF7T0R027E (YAGEO, 2512): extended, JLC stock 4076, lifecycle normal, checked 2026-11-07`

| INA281 parameter | Datasheet | Our case |
|---|---|---|
| Common-mode | −4…110 V (survival −20…120 V) | VBUS 48 V, ≤ 64 V at TVS breakdown ✓ |
| VS | 2.7–20 V | VSR 12 V ✓ |
| Gain (A4) | 200 V/V, ±0.5 % | 5.4 V/A with 27 mΩ |
| Output swing | to VS − 0.15 V (max, 10 kΩ) | 7.3 V at 1.36 A ✓; 9.7 V at 1.8 A |
| Bandwidth | 1.3 MHz | |

Shunt power 1.36² × 0.027 = 50 mW (1 W part) ✓. Placed high-side between the output ceramics and the
bulk node, so it measures converter output current, not the amp's pulsed current.

**Set-points** (INA out → Rtop 4.99 k → TL431(CC) REF; Rbot 280 k to GND; Rsel0 4.87 k and Rsel1
5.76 k to GND through 2N7002 switches driven by `ILIM_SEL0`/`ILIM_SEL1`, 100 k pull-downs so the
reset state is 00):

| ILIM_SEL1:0 | Rbot effective | Ratio | Limit | Use |
|---|---|---|---|---|
| 00 (reset) | 280 k | 0.9825 | **0.470 A** (22.6 W) | Type 2 / start-up |
| 01 | 4.79 k | 0.4896 | **0.944 A** (45.3 W) | Class 6 |
| 10 | 5.63 k | 0.530 | 0.872 A | (spare; ≤ Class 6) |
| 11 | 2.61 k | 0.344 | **1.344 A** (64.5 W) | Class 8 |

Every state is ≤ the Class 8 budget, so no GPIO combination can overload the PSE. Tolerance: INA
±0.5 %, shunt ±1 %, TL431B ±0.5 %, dividers ±0.2 %, 2N7002 Rds (≤ 5 Ω vs 4.87 k) → ≈ ±2.5 %.
CC TL431 cathode → BAS316 → opto LED cathode (diode-OR with the CV TL431). Compensation: 100 k +
10 nF from CC cathode to REF (integrator, crossover ≈ 300 Hz; slow on purpose).
`IBUS_SENSE` for telemetry: INA out → 16.9 k / 10.0 k → 3.0 V at 1.5 A, to an ADC (block D/E).
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
- Leakage during a 1500 Vrms 60 Hz hipot: 2π × 60 × 2.2 nF × 1500 = 1.2 mA (hipot testers usually
  trip at ≥ 5 mA) ✓. At 2250 V DC: none after charging.
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
