# U_IS — current and temperature telemetry ADC: TI ADS7038-Q1 (8-ch, 12-bit, 1 MSPS, SPI)

> **fsw update 2026-11-07 (FPGA changed to ECP5, edge grid 1.453 ns = 688.128 Mb/s ODDRX2F, E-fpga-ecp5.md):** baseline fsw is now **448 kHz** (1536 grid steps; 448 kHz = 48 kHz × 28/3, audio-locked but not an integer multiple). 480 kHz is not on the grid. Option per build: 672 kHz (14 × 48 kHz, 1024 steps). Current channels at 2 samples per PWM period: 4 × 896 kS/s exceeds 1 MSPS, so use 1 sample per period per leg (4 × 448 kS/s = 896 kS/s total), alternating phase.

Datasheet: datasheets/ads7038q1.pdf (TI SBAS981A, Nov 2020). Read: all sections (specs, timing, modes, GPIO, CRC, layout).
MPN: ADS7038QRTERQ1. Supplier: `C2876384 ADS7038QRTERQ1 (TI, WQFN-16-EP(3x3)): extended, JLC stock 1777, lifecycle normal, checked 2026-11-07`. The non-Q1 ADS7038IRTER has 0 stock; the -Q1 (AEC-Q100) part is identical in pinout and function. Footprint: WQFN-16 RTE 3 × 3 mm with thermal pad to GND.

## Channel map
| AIN | Signal | Source / front end |
|---|---|---|
| 0 | I_WOOF_A | INA241 (leg A) → 100 Ω → AIN, 1 nF C0G at the pin |
| 1 | I_WOOF_B | same, leg B |
| 2 | I_TWT_A | same |
| 3 | I_TWT_B | same |
| 4 | T_WOOF_FET | NTC divider (D-ntc.md), 100 nF at the pin |
| 5 | T_WOOF_IND | NTC divider |
| 6 | T_TWT_FET | NTC divider |
| 7 | T_TWT_IND | NTC divider |
Supplies: AVDD = 3V3_A (reference; same rail as the INA241 supply and mid-point, so readings are ratiometric) with 1 µF; DVDD = +3V3 with 1 µF; DECAP 1 µF (pin descriptions p.4).
Moving the four NTCs here (instead of the RP2350's ADC as architecture.md assumed) puts over-temperature in the FPGA's hands, next to the bridge enable. It also frees RP2350 ADC inputs for the knobs (proposed in D-interfaces.md).

## Ratings vs worst case
| Parameter | Abs max / ROC (p.5–6) | Worst case | OK |
|---|---|---|---|
| AVDD, DVDD | 5.5 V; ROC 2.35–5.5 / 1.65–5.5 V | 3.3 V | ✓ |
| AINx | GND − 0.3 … AVDD + 0.3 | INA241 output 0.05–3.1 V (it runs from the same 3V3_A, so it cannot exceed AVDD); NTC divider ≤ 3.3 V | ✓ (both are powered from 3V3_A, so no back-powering) |
| fSCLK | 60 MHz | ≤ 48 MHz from the FPGA | ✓ |

## Calculations
### Front end for the INA241 channels
Sampling cap CSH 12 pF (p.6). Muxed: the worst-case channel-to-channel step is 3 V → kickback ΔV = 3 V × 12 pF/(1 nF + 12 pF) = 36 mV, recovered through 100 Ω × 1 nF = 100 ns plus the INA241's closed-loop output (1.1 MHz) in tACQ ≥ 400 ns (p.6) → e^(−4) × 36 mV = 0.66 mV ≈ 0.8 LSB ✓.
INA241 capacitive load: 1 nF behind 100 Ω, within its "1 nF, no isolation resistor" limit (INA241 p.7) ✓.
Bandwidth of the RC: 1.6 MHz, above the INA241's 1.1 MHz → the telemetry sees the inductor current including the 480 kHz ripple. Gateware samples at fixed PWM phases: mid-pulse → average current; at the edges → the current at each transition, which the dead-time compensation needs (D-lmg1210.md).
Scale: 0.050 V/A, 0.806 mV/LSB → **16 mA/LSB**, range −32…+29 A.

### Throughput plan (gateware)
1 MSPS total in manual mode (CS rising edge starts the conversion of the channel chosen in the previous frame; frame ≥ 16 SCLK + tCONV 600 ns). Suggested: I channels round-robin at ≈ 240 kS/s each (4 × 240 k = 960 kS/s, 2 per channel per PWM period), with one NTC slot every 1024 frames (≈ 1 kS/s per NTC, ample).
SNR 70.2 dB min (p.6) → ≈ 1.2 LSB rms ≈ 20 mA rms per sample.
The analog watchdog (per-channel high/low thresholds with event counter, §8.4) can flag over-temperature on AIN4–7 autonomously. It is optional; the gateware reads the values anyway.

### Power
IAVDD 600 µA max at full throughput, AVDD 5 V (p.6); less at 3.3 V ✓.

## Fine print
- "The device starts converting the active input channel on the rising edge of CS", and SDO is Hi-Z when CS is high (p.4). Each conversion's result comes out in the *next* frame.
- tPU 5 ms after power-up with CDECAP = 1 µF (p.8): gateware waits before configuring.
- The CRC on read/write and the power-up configuration are optional (they can stay disabled).
- GPIO function on unused channels: not needed; all 8 are analog.

## Layout guidance
1 µF on AVDD, DVDD and DECAP at the pins; thermal pad to GND with vias. The INA241 traces are ≤ 30 mm, routed as analog (not alongside the PWM lines).

## Open questions
None.
