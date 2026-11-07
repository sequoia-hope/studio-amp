# U_VB — VBUS sense ADC for bus-voltage feedforward: TI ADS7042 (12-bit, 1 MSPS, SPI) + divider

> **fsw update 2026-11-07 (FPGA changed to ECP5, edge grid 1.453 ns = 688.128 Mb/s ODDRX2F, E-fpga-ecp5.md):** baseline fsw is now **448 kHz** (1536 grid steps; 448 kHz = 48 kHz × 28/3, audio-locked but not an integer multiple). 480 kHz is not on the grid. Option per build: 672 kHz (14 × 48 kHz, 1024 steps). PWM-synchronous VBUS sampling at 2 × fsw = **896 kS/s** (ADS7042 max 1 MSPS).

Datasheet: datasheets/ads7042.pdf (TI SBAS608C, Dec 2015). Read: all sections (specs, timing, offset calibration, layout). Divider and filter: datasheets/fojan-frc0402.pdf (FOJAN FRC thick-film series, 0402–2512), datasheets/walsin-0402n102.pdf (Walsin C0G), datasheets/bat46wj.pdf.

| Ref | Part | Supplier (`show`, 2026-11-07) |
|---|---|---|
| U_VB | ADS7042IDCUR, VSSOP-8 (DCU) | `C701641 ADS7042IDCUR (TI, VSSOP-8): extended, JLC stock 1734, lifecycle normal` |
| R_VT1, R_VT2 | 27.4 kΩ 1 % 0805 in series (top), FRC0805F2742TS | `C2930188 FRC0805F2742TS` (78k in stock, search 2026-11-07) |
| R_VB | 2.21 kΩ 1 % 0603 (bottom), FRC0603F2211TS | `C2933171 FRC0603F2211TS` (110k in stock) |
| C_VF | 1 nF C0G 50 V 0402 at AINP, 0402N102J500CT | `C237166 0402N102J500CT (Walsin, 0402): extended, JLC stock 139147, lifecycle normal` |
| D_VCL | BAT46WJ, AINP node → 3V3_A (back-power clamp) | `C114696 …` |
| C_AVDD | 1 µF 0603 + 100 nF 0402 on AVDD; 100 nF on DVDD | C5673 / C60474 |

Supplies: AVDD = **3V3_A** (also the ADC reference; block C, D-interfaces.md); DVDD = +3V3 (FPGA I/O level).
Why a dedicated ADC instead of a channel of the ADS7038: a multiplexed SAR's sampling cap carries the previous channel's voltage. With a 2 kΩ source that kickback (12–15 pF on 1 nF, ≈ 1.5 % of the inter-channel step) does not settle within a 400 ns acquisition. A single-channel ADC samples the same slowly-moving node every time, so the kickback is ≈ 0. It also gives the feedforward a fixed-latency sample stream.

## Ratings vs worst case
| Parameter | Abs max (p.7) | Worst case | OK |
|---|---|---|---|
| AVDD, DVDD | 3.9 V (rec. 1.65–3.6 V) | 3.3 V ± 3 % | ✓ |
| AINP | −0.3 … AVDD + 0.3 V | normal: 48 V/25.8 = 1.86 V; 55 V cut → 2.13 V; TVS clamp 82.4 V (SMBJ51A, updated scheme D-vbus-tvs.md) → 3.19 V ≤ 3.25 (3V3_A −1.5 %) + 0.3 = 3.55 V ✓ | ✓ |
| AINP with AVDD unpowered | AVDD + 0.3 = 0.3 V | after the logic rails drop, VBUS can stay at tens of volts for seconds (5–7 mF bulk) → the node is at ≤ 1.86 V | **✗ without a clamp** → D_VCL (BAT46WJ, VF ≈ 0.25 V at < 1 mA) steers the current, ≤ (48 V/57 k) = 0.84 mA, into the unpowered 3V3_A rail instead of the ADC's ESD diode |
| AINM | ±0.3 V | tied to GND at the divider's ground end (Kelvin) | ✓ |

## Calculations
### Divider
Ratio = (27.4 k + 27.4 k + 2.21 k)/2.21 k = 57.01/2.21 = **25.80**. Full scale (3.3 V) = **85.1 V**. LSB = 85.1 V/4096 = **20.8 mV** = 0.043 % of 48 V.
Thevenin = 2.21 k ∥ 54.8 k = **2.12 kΩ**.
Power: 48 V²/57.01 k = 40 mW total; each 27.4 kΩ 0805 dissipates 19 mW (0805 rating 1/8 W) ✓; at 87 V, 66 mW each ✓. Voltage per 0805 ≤ 44 V ≤ 150 V working ✓.
Tempco: thick film ±100 ppm/°C on top and bottom, so the ratio tracks to about ±100 ppm/°C differential worst case → 0.5 % over 50 °C. That is a gain error in the feedforward (output level), not distortion. Gateware can calibrate it against the PD's own VPRI if ever needed.
Tolerance: ±1 % → ratio ±2 % worst case → feedforward gain ±2 % (static output level error, corrected by a one-time calibration in firmware).

### Bandwidth and sampling
RC: τ = 2.12 kΩ × (1 nF + 39 pF diode) = 2.2 µs → **f−3dB = 72 kHz**. Feedforward must follow VBUS sag from the audio load (mostly < 5 kHz, at 2× the signal frequency under BTL supply pumping, and from the ACF loop). Phase lag at 5 kHz = atan(5/72) = 4.0° → residual feedforward error ≈ 7 % of the ripple component at 5 kHz, ≈ 1.4 % at 1 kHz. Gateware can compensate the known pole.
Kickback: CS (sampling cap) 15 pF (p.8) charged from the previous sample of the same node → ΔV ≈ 0. Acquisition tACQ ≥ 200 ns (p.10): the 1 nF reservoir supplies the 15 pF charge (1.5 % of a step only on the first sample).
**Rate: 1 MSPS at 16 MHz SCLK** (fSCLK max 16 MHz, tCYCLE 1 µs, tCONV = 12.5 tSCLK + tSU, p.10). Requirement: "≥ a few hundred kS/s". Gateware may run it at 960 kS/s (2 × fsw), synchronous with the PWM, so the sample lands at the same switching phase every time (the 480 kHz ripple is rejected by the RC, −16 dB, and by synchronous sampling).
Noise: SNR 70 dB at 3 V AVDD (p.1) → ≈ 1.1 LSB rms ≈ 24 mV rms on VBUS (0.05 %). Averaging two samples per PWM period → 0.035 %.
AVDD is the reference, so 3V3_A noise and drift appear as VBUS gain error. 3V3_A must be quiet (≤ 1 mV rms → 0.03 %) (D-interfaces.md).
Offset calibration: the ADS7042 has integrated offset calibration ("Calibrated" EO spec, §9.4). Gateware triggers it after power-up.

### Power
690 µW at 1 MSPS, 3 V AVDD (p.1) ✓.

## Fine print
- The sample is taken at the CS falling edge (§9.4, "sampled with the CS falling edge"). Gateware places CS low at a fixed PWM phase.
- DVDD is independent of AVDD; both ≤ 3.6 V.
- The VSSOP pinout differs from the X2QFN (Fig. 6-1/6-2): DCU pin 1 = DVDD, 2 = SCLK, 3 = SDO, 4 = CS, 5 = AINM, 6 = AINP, 7 = AVDD, 8 = GND.

## Layout guidance
- Divider tapped from VBUS at the bulk caps / bridge feed (a Kelvin tap, not along a high-current path). The bottom resistor and AINM return go to the ADC GND pin. C_VF sits at the AINP pin.
- Route the divider's high-voltage end away from the switch nodes; the 2 kΩ node is low-impedance enough not to need guarding.

## Open questions
None. The feedforward algorithm (gain, delay compensation) belongs to block E.
