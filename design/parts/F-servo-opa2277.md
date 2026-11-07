# U_SV1: OPA2277UA, DC servo for both filter/line outputs

Datasheet: `datasheets/opa2277.pdf` (TI OPA277/OPA2277/OPA4277). Read: features, abs max,
electrical characteristics (OPA2277UA column, boldface = −40 to +85 °C), typical curves and
applications.
MPN: OPA2277UA/2K5 (TI). `C24460 OPA2277UA/2K5 (TI, SOIC-8): extended, JLC stock 10316, lifecycle normal, checked 2026-11-07`
Alternate: `C565338 OPA2277UAM/TR` (HGSEMI, 4846 in stock, from the search). Fallback with the
same footprint and function, but up to 13 mV of output offset: TL072IDR (C6962, 95834).
Quantity: 1 per board.
Footprint: SOIC-8 (D), standard dual op-amp pinout.

## Why a servo

The filter's DC output has these contributions:
- CMRR × the 1.65 V Q/Q̄ common mode: ≤ 23 mV with 0.1 % resistors.
- SA5532 VIO × noise gain 4.5: ≤ 22 mV over the full temperature range.
- FF VOH/VOL asymmetry: a few mV.

The worst case is about ±50 mV. Switching that through the mute relay would click, and it would
put ≥ 0.2 mA of DC through 300 Ω headphones. Coupling capacitors at the output would put X7R or a
large film part in the signal path. The servo keeps the signal path DC-coupled and capacitor-free.

## Circuit (per channel)

FILT_x → R_S 1 MΩ → inverting input of the OPA2277 half. C_S 100 nF C0G goes from that input to
its output. The + input goes to GND through 1 MΩ, to match bias currents. The output V_S drives
R_INJ (20 kΩ) into the filter's X+ node. R_BAL (20 kΩ) goes from X− to GND, to keep the two
networks matched (`F-filter-passives.md`).

## Absolute max vs worst case

| Parameter | Abs max | Worst case | OK |
|---|---|---|---|
| Supply | 36 V total | 30 V (±15) | OK |
| Inputs | within the supplies | ≤ FILT swing ±5.65 V through 1 MΩ | OK |
| Output short | continuous, one amp per package (note 2) | no short path (it drives 20 kΩ) | OK |
| Temp | −40 to +85 °C specified | 55 °C | OK |

## Calculations

- **Loop gain/sign:** A current into X+ raises the output by R3 (at DC, V+ = I·(R3 ∥ R_eq); noise
  gain ≈ 1 + R3/R_eq, so Vout ≈ I·R3). The inverting integrator gives V_S = −Vout/(sτ), with
  τ = R_S·C_S. The injection adds (R3/R_INJ)·V_S to the output, which is negative feedback.
- **High-pass corner:** f_HP = (R3/R_INJ)/(2π·R_S·C_S) = (3.9k/20k)/(2π × 1 MΩ × 100 nF)
  = 0.195/0.628 = **0.31 Hz**, first order.
  - At 20 Hz: amplitude error −0.0001 dB, phase lead +0.9°.
  - Settling: τ_loop = 1/(2π·0.31) = 0.51 s. Allow 3 s (≈ 6τ) from DAC start before the relays
    close (R-34 sequence, `F-mute-relay.md`).
- **Servo range:** correcting ±50 mV needs V_S = 50 mV × R_INJ/R3 = ±0.26 V. The OPA2277 swings
  ±13 V, so it has ±2.5 V of correction range: plenty, but also enough to hide a fault, which is
  why the DC detector exists.
- **Residual output offset:** VOS (UA, 25 °C) ±50 µV max, plus IB ±2.8 nA (full range) × 1 MΩ
  (the + input carries 1 MΩ too, so only IOS matters, ±2.8 nA worst case) = 2.8 mV. Total
  **≤ 2.9 mV worst**, typically < 0.6 mV. HP output: ×1.3, plus the SA5532 HP stage's own
  5 mV + 0.8 mV, so ≤ 9.6 mV worst case at the headphone jack.
- **AC signal at the injection point:** V_S at 20 Hz for 5.65 Vpk out = 5.65/(2π·20·0.1 s) =
  0.45 Vpk. It is attenuated by the R_INJ/R3 ratio and is already accounted for in the 0.31 Hz
  high-pass. At 1 kHz, V_S = 9 mVpk. The integrator op-amp's distortion at these levels is
  negligible (OPA2277 THD+N 0.002 % at 3.5 Vrms).
- **Noise:** OPA2277 en is 12 nV/√Hz at 10 Hz, and 0.22 µVpp from 0.1–10 Hz. It is integrated,
  so it is −28 dB at 20 Hz relative to unity and falls 6 dB/oct. Through R3/R_INJ = 0.195 it
  contributes < 0.2 µV in band. OK.
- **C_S = 100 nF C0G 1206, 50 V** (GRM31C5C1H104JA01L). The voltage across it is
  ≤ ±0.5 V at LF.
  `C97946 GRM31C5C1H104JA01L (muRata, 1206): extended, JLC stock 95724, lifecycle normal, checked 2026-11-07`
  Datasheet: `datasheets/murata-grm31c5c1h104.pdf`. C0G is used to avoid X7R dielectric
  absorption and its voltage coefficient in the servo, which would otherwise show up as LF
  distortion.
- **R_S = 1 MΩ 0.1 %** (RT0603BRD071ML, C326730, 104762 in stock; inside the ±0.1 %/25 ppm range
  of 1 Ω–1 MΩ). Thin film keeps the leakage and noise low. Its tolerance isn't critical.

## Fine print

- Abs max note 2: the short-circuit rating is for one amplifier per package. There is no short
  path here.
- If R_S picks up surface leakage on a dirty board, the offset shifts. Keep the 1 MΩ node short,
  surround it with a guard of the + input's potential (GND), and avoid flux residue.

## Open questions

- None.
