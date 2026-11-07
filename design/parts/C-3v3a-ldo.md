# U (3V3_A) — TPS7A2033P quiet 3.3 V reference rail for block D sensing

Datasheet: datasheets/tps7a20.pdf (SBVS338H, Jul 2024, English). Read: all sections (audited first
for 3V3_Q, which later moved to TPS7A94).
MPN: TPS7A2033PDBVR   Supplier: `C2862740 TPS7A2033PDBVR (TI, SOT-23-5): extended, JLC stock 129111, lifecycle normal, checked 2026-11-07`
Footprint: SOT-23-5 "DBV". Pins (SOT-23 column): 1 IN, 2 GND, 3 EN, 4 N/C, 5 OUT.

## Requirement (block D, D-interfaces.md, 2026-11-07)

3.3 V ±3 %, ≤ 1 mV rms noise, ≤ 15 mA. It is the ratiometric reference and supply for 4 × INA241
current-sense amplifiers, the OCP thresholds, and AVDD of the ADS7042 (VBUS) and ADS7038
(currents/NTC).

## Why a separate LDO, not 3V3_Q

3V3_Q exists only while +15V is up, and its Zout and noise set the DAC output level directly.
Sharing it would couple the current-sense and ADC supply current (it follows the power stage) into
the audio reference, and would leave block D's ADCs unpowered while their SPI lines from the FPGA
are live on USB power. A dedicated 7 µVrms LDO meets block D's ≤ 1 mV with 100× margin.

## Absolute max vs our worst case

| Parameter | Abs max / ROC | Ours | Margin |
|---|---|---|---|
| VIN | 6.5 V / 1.6–6.0 V | +5V ≤ 5.25 V | OK |
| EN | 6.5 V | tied to IN | OK |
| IOUT | 300 mA | 15 mA | OK |
| COUT | 1–200 µF, ESR ≤ 100 mΩ | 4.7 µF X7R | OK |

## Calculations

- Accuracy ±1.5 % (features) → 3.25–3.35 V, inside ±3 %.
- Noise 7 µVrms (10 Hz–100 kHz) against ≤ 1 mV rms. PSRR 95 dB at 1 kHz attenuates the +5V ripple
  (LM5013 396 kHz, PSRR about 45 dB there per Fig. 5-61) to µV level.
- Dissipation: (5.05 − 3.3) × 15 mA = 26 mW, +5 °C.
- CIN 1 µF, COUT 4.7 µF X7R 0603/0805. Block D fits local decoupling at each INA241/ADC, within the
  200 µF limit.
- **EN tied to IN, so the rail is always on with +5V** (including USB-only). The ADCs and INA241 stay
  powered whenever the FPGA can drive their SPI and logic pins, so nothing back-powers them.
- Load on +5V: 15 mA.

## Layout

- Place it in block D's sensing region (near the ADCs). Its GND returns to the plane at the
  sensing region, away from the GaN switch loops.
