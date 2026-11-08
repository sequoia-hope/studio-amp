# Current sense (×4, one per leg): 5 mΩ shunt in the inductor path + INA241A1 (gain 10)

> **UPDATE 2026-11-08 (IGB070S10S1):** ramp-regime threshold → gates off ≈ **216 ns** worst case (IGB070 turn-off ≈ 4.5 ns instead of 7 ns); overshoot 4.9 A/µs × 216 ns = 1.06 A → peak ≤ 16.7 A (unchanged); IGB070 ID pulsed 360 A (25 °C) / 170 A (150 °C) ≫. Hard-short path ≈ 48 ns (D-short-detect.md).

Datasheets: datasheets/ina241.pdf (TI SBOSA30D, Dec 2024; read: all sections incl. application §8); datasheets/yageo-pa2512.pdf (Yageo PA series "current sensor – low TCR"; read: all).

| Ref | Part | Supplier (`show`, 2026-11-07) | Footprint |
|---|---|---|---|
| R_SH (×4) | Yageo PA2512FKF070R005E: 5 mΩ ±1 %, ±100 ppm/°C, 1 W at 70 °C | `C723365 PA2512FKF070R005E (YAGEO, 2512): extended, JLC stock 4665, lifecycle normal` | 2512 (5 mΩ variant: 6.35 × 3.18 mm, terminal length 1.19 mm, Fig. 3), with **Kelvin sense traces from the inner pad edges** |
| U_CS (×4) | TI INA241A1IDDFR: gain 10 V/V, −5…110 V CM, 1.1 MHz BW | `C19712054 INA241A1IDDFR (TI, SOT-23-8): extended, JLC stock 2207, lifecycle normal` | SOT-23-8 "DDF" (Fig. 5-1) |
| C (×4) | 100 nF 0402 VS bypass, CC0402KRX7R7BB104 | `C60474 …` (D-driver-passives.md) | 0402 |

Build need: 4 × 5 + 2 = 22 of each ✓.

## Topology (why here)
Each leg: switch node → L → **R_SH** → filter caps / output. The shunt measures **inductor current = FET current** in both directions (including ripple). Every output fault passes through it: speaker short (both legs), output to GND (the leg's HS current, positive), output to VBUS (the leg's LS reverse current, negative). Its common-mode voltage is the filter-cap node: 0–48 V at audio rate, with ≈ 1 V pp ripple at 480 kHz, never the 48 V/ns switch node.
Rejected alternatives:
(a) LS-source shunts: they miss output-to-GND shorts, add inductance into the commutation loop, and lift LMG1210 VSS off the power ground (TI §8.2.2.3 then wants CMCs).
(b) VBUS-feed shunt: sees chopped current filtered by the HF ceramics, and misses output-to-VBUS shorts.
(c) Hall sensors (ACS733): the 20 A part had 17 in stock; 1 MHz bandwidth with no speed benefit.

## Ratings vs worst case
| Parameter | Rating | Worst case | Margin |
|---|---|---|---|
| INA241 VIN+/VIN− CM | −5 to 110 V operating; −20 to 120 V survival (p.4) | −0.5 V (dead-time undershoot is filtered by the LC) … 48 V + 1 V; TVS-clamp event 87 V | OK |
| INA241 differential input | ±30 V abs | 16 A × 5 mΩ = 80 mV | OK |
| INA241 VS | 2.7–20 V | 3.3 V (3V3_A, block C) | OK |
| Shunt power | 1 W at 70 °C (derated above 70 °C to 170 °C) | continuous 3.47 A rms → 60 mW; 144 W burst 6.04 A rms → 182 mW; 16 A peak for < 1 µs | OK (≤ 18 % of rating) |
| Shunt TCR drift | ±100 ppm/°C | ΔT 40 °C → ±0.4 % | OK for OCP and telemetry |

## Calculations
### Scaling (VS = 3.3 V, REF1 = VS, REF2 = GND → output mid = VS/2, Fig. 8-x reference divider)
V_out = 1.65 V + G × R_SH × I = 1.65 V + 10 × 5 mΩ × I = **1.65 V + 0.050 V/A × I**.
Linear range: output swing to within 0.2 V of VS and 0.05 V of GND (p.6) → 0.05…3.1 V → I = −32 … +29 A. The **±15 A** trip points sit at **2.40 V / 0.90 V** (±0.75 V from mid) ✓.
ADC (ADS7038, 3.3 V reference = 3V3_A): 0.81 mV/LSB → 16 mA/LSB.
Ratiometric: the output mid, the comparator thresholds (D-ocp-logic.md) and the ADC reference all come from the same 3V3_A, so supply drift cancels.

### Accuracy of the 15 A trip
Shunt ±1 % + TCR ±0.4 % + INA241A gain error ±0.015 % + REF divider ±0.15 % (p.7) + offset ±20 µV/(50 mV) = ±0.04 % + threshold divider (D-ocp-logic.md) ±1.2 % → **±2.8 % ≈ ±0.42 A**.

### Speed: why gain 10 and this part
INA241 small-signal bandwidth 1.1 MHz at all gains; slew 8 V/µs; 1 % settling 1 µs (p.8).
Fault current is slew-limited by the output inductor: output-to-GND short with the HS on gives VBUS/L = 48 V/9.8 µH = **4.9 A/µs**; speaker short gives 48 V/(2 × 9.8 µH) = 2.45 A/µs. For a ramp into a 1-pole 1.1 MHz amplifier, the output lags by τ = 1/(2π × 1.1 MHz) = **145 ns**. Output slew needed = 0.05 V/A × 4.9 A/µs = 0.25 V/µs ≪ 8 V/µs ✓, so the lag is the bandwidth term only.
End-to-end, threshold to gates off, **ramp regime** (no common-mode step): 145 ns (INA241 pole) + **20 ns overdrive build-up** (the INA241 output moves at 0.05 V/A × 4.9 A/µs = 0.25 V/µs, so the 5 mV overdrive the 12 ns TLV3502 figure assumes exists 20 ns after the crossing; review m5) + TLV3502 12 ns + BAT46WJ ≈ 2 ns + 74LVC1G17 ≤ 4.6 ns + 74LVC1G74 ≤ 5.9 ns + ≈ 1 ns + LMG1210 tEN ≤ 20 ns + IGC033 turn-off ≈ 7 ns = **≈ 218 ns worst case** (≈ 190 ns typical).
Overshoot during the delay: 4.9 A/µs × 218 ns = 1.07 A → peak ≤ 15.6 (trip max) + 1.1 = **16.7 A**, handled by the inductor (Isat −10 % at 18 A at 25 °C; hot derating open, D-output-inductor.md) and the FET (IGC033S10S1: 700 A pulsed).

### Two OCP regimes (review M2)
The INA241 "holds the output for 1 µs" after a large common-mode ΔV/Δt (§7.3.1.1, p.15–16; threshold unpublished). A hard short at an output terminal steps the shunt's CM by 24–48 V in tens of ns, which is exactly that case, so this path is blind for ≈ 1 µs in a hard short. Block D therefore has two paths into the same fault latch:
| Regime | Detector | Trip | Threshold → gates off | Peak FET/inductor current |
|---|---|---|---|---|
| **Hard short** at a terminal (to GND, VBUS, or across; node step ≥ 1 V) | dV/dt detector on each output node (D-short-detect.md) | node step ≥ 1 V or slew > 21 V/µs | **≈ 50 ns** from the short | ≤ pre-fault + 0.25 A ≤ **13.7 A** |
| **Ramp overcurrent** (no CM step: impedance collapse, soft fault) | this path (INA241 + TLV3502 window) | **14.9 ± 0.7 A** | **≈ 218 ns** worst case | ≤ **16.7 A** |
| Residual: CM step < 1 V that still triggers the INA241 hold | INA241 after the hold | 14.9 A + up to 1 µs of ramp | ≈ 1.2 µs | ≤ ≈ 21 A (inductor −20 % point at 25 °C) |
Proposed R-54 wording (for the lead/user; intent.md is not block D's to edit): *"Overcurrent: a short at an output terminal (to either rail or across the outputs) turns all four FETs of that channel off within ≤ 100 ns of the short; a gradually rising overcurrent trips at 15 A ± 1 A with ≤ 250 ns from threshold to all gates off; peak device current ≤ 17 A in both cases."*
No faster high-CM current amplifier is in stock: AD8418 250 kHz; LT1999 2 MHz but ≤ 100 units at ≤ 80 V CM; INA240/INA296 ≈ 400 kHz / 1.1 MHz with a lower CM range. INA241 is the best available.

### PWM rejection
The enhanced PWM rejection is spec'd for CM steps up to 125 kHz (p.1). Here the CM at the shunt is the LC-filtered output: ≈ 1 V pp triangle at 480 kHz, not 48 V steps. AC CMRR 89 dB at 1 MHz → 1 V × 10^(−89/20) × G 10 = 0.35 mV at the output ≈ 7 mA equivalent ✓.

### Power from 3V3_A
IQ 2.5 mA typ / 3.2 mA max (p.8) × 4 = **12.8 mA max**.

## Fine print
- Input bias current is 25–45 µA per input, flowing from the shunt into the inputs (p.6), and constant over CM (§8.3). With direct Kelvin connection (no input resistors) it causes no error. **Do not add input RC filters**: they add delay and gain error.
- Max capacitive load 1 nF with no isolation resistor (p.7). The output goes to the comparator inputs (few pF) and to the ADC through 100 Ω + 1 nF (D-isense-adc.md) ✓.
- REF1/REF2 must stay within 0…VS and are tied directly to VS and GND (bidirectional, mid-supply). They must not float.

## Layout guidance
- Kelvin: the sense traces leave from the inner edges of the shunt pads as a tight pair to the INA241, away from the switch node and inductor gap (motor-drive.md). The INA241 sits within 10 mm of the shunt.
- The INA241 GND pin goes to the solid GND plane; VS bypass at the pin.

## Open questions
1. R-54's 200 ns is met with about 2 ns of margin (IGC033S10S1 turn-off is slower than IGB070's) at worst-case datasheet delays. If the bench shows more, the remedy is setting the trip at about 14 A (the legitimate peak is 13.4 A), not a faster part.
