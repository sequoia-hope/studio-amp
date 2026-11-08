# Optional-population post-filter output sense (R-51): 4 dividers → 4 × OPA836 → 2 × ADS8353 (16-bit, 2-ch simultaneous)

> **UPDATE 2026-11-07 (user decision E): populate on all 5 prototypes.** Build quantities: 2 × ADS8353 × 5 = 10 + 2 ≤ 881 ✓; 4 × OPA836 × 5 = 20 + 2 ≤ 7848 ✓. +5V load ≈ 24 mA becomes part of the baseline (block C). The thin-film divider LCSC numbers must be fixed in phase 2.

**Population: DNP on the baseline build. Recommended to populate on all 5 prototypes** for dead-time calibration and THD measurement (D-lmg1210.md open question 1). The footprints and FPGA pins are mandatory (R-51: "without a respin").

Datasheets: datasheets/ads8353.pdf (TI SBAS584B, Aug 2014; read: all sections incl. the analog-input §8.3.2, reference §8.3.1, interface modes); datasheets/opa836.pdf (TI OPA836/OPA2836; read: features, ROC, 5 V electrical table, ADC-driver application section).

| Ref | Part | Qty/board | Supplier (`show`, 2026-11-07) |
|---|---|---|---|
| U_PF (one per amp channel) | TI ADS8353IPWR, TSSOP-16 | 2 | `C701691 ADS8353IPWR (TI, TSSOP-16): extended, JLC stock 881, lifecycle normal` |
| U_DRV (one per output terminal) | TI OPA836IDBVR, SOT-23-6, the ADC driver the ADS8353 datasheet itself shows | 4 | `C111589 OPA836IDBVR (TI, SOT-23-6): extended, JLC stock 7848, lifecycle normal` |
| R_PT / R_PB | divider 140 kΩ / 10.0 kΩ, **thin film 0.1 %, 25 ppm** 0603 (Yageo RT0603B family, whose 2.43 kΩ member C861815 is in stock; exact LCSC numbers in phase 2) | 4 + 4 | family checked: `C861815 RT0603BRE072K43L (YAGEO, 0603): extended, JLC stock 3699, lifecycle normal` |
| R/C kickback filter | 20 Ω + 1 nF C0G per ADC input | 4 + 4 | C237166 (C0G) |
| C_REF | 10 µF on REFIO_A and REFIO_B (datasheet §8.3.1) | 4 | Samsung CL10A106KP8NNNC, X5R 0603 10 µF 10 V: `C19702` (basic; phase 2) |

Each ADS8353 samples OUT_P (channel A) and OUT_N (channel B) of one amplifier channel **simultaneously**, and gateware forms OUT_P − OUT_N. Common-mode ripple and the 24 V BD common mode cancel exactly because the samples are simultaneous. The fully differential ADS8354 (one ADC per channel, no subtraction) has only 13 in stock and fails sourcing.

## Ratings vs worst case
| Parameter | Rating | Worst case | OK |
|---|---|---|---|
| ADS8353 AVDD / DVDD | 6 V abs; AVDD 5 V nom (4.5–5.5), DVDD 3.3 V | +5V / +3V3 | ✓ |
| ADS8353 AINP | REFGND − 0.3 … AVDD + 0.3 | ≤ OPA836 output ≤ 5 V | ✓ |
| ADS8353 FSR | 0…2 × VREF = 0…5 V (CFR range bit, internal VREF 2.5 V) | 55 V/15 = 3.67 V; TVS event 87/15 = 5.8 V → the OPA836 saturates at its 5 V rail | ✓ |
| OPA836 VS | 2.5–5.5 V | +5V | ✓ |
| OPA836 input range | −0.2 … +3.9 V at 5 V supply (p.1) | 0 … 3.67 V (55 V) | ✓ (48 V → 3.20 V) |
| Divider top 0603 | 75 V working (thin-film 0603 typ. 75 V; confirm in the phase 2 part datasheet) | 48 V; 87 V transient | ✓ |
| Back-powering when the rails are off | input ≤ (VS + 0.3 V) when unpowered | OUT at 48 V through 140 kΩ → ≤ 0.34 mA into the OPA836 ESD diodes | ✓ within typical 10 mA input-current abs max (confirm in phase 2) |

## Calculations
- Divider: 150 k/10 k = **15.0** → 48 V → 3.20 V; FS 5 V → 75 V; LSB 76.3 µV × 15 = **1.14 mV** at the output (16-bit, 0.0024 % of 48 V).
- Divider Thevenin 9.33 kΩ into the OPA836 input (follower, G = 1): no loading.
- Bandwidth: divider + OPA836 205 MHz GBW, so the 20 Ω/1 nF kickback filter (8 MHz) sets it. **Sample at 600 kSPS** (ADS8353 max): with fsw 480 kHz the PWM ripple aliases. The audio-band measurement needs the LC-filtered output only up to ~20 kHz. Gateware samples synchronously to the PWM (e.g. 480 kSPS, once per period at a fixed phase) so the residual ripple aliases to DC.
- Noise: ADS8353 SNR 89 dB → referred to the 48 V output span: 3.20 V × 10^(−89/20) × 15 ≈ 1.7 mV rms broadband at 600 kSPS → in 20 kHz: 1.7 × √(20/300) = 0.44 mV rms. That is well below R-51's 150 µV goal only after averaging, and above the 60 µV studio target. It suits a feedback loop's error input at high signal levels and THD measurement (−100 dB THD ADC); output-noise measurement needs an external analyser.
- Divider linearity: thin film VCR ≪ 1 ppm/V; 0.1 % match between the P and N dividers gives a CM rejection of ≈ 60 dB at the 24 V BD common mode (24 mV of error, a fixed offset calibrated out in gateware).
- Power: ADS8353 42.5 mW typ / 50 mW max each (internal ref, fastest throughput); OPA836 1 mA each at 5 V. **+5V load if populated: 2 × 10 mA + 4 × 1 mA ≈ 24 mA.**

## Fine print
- ADS8353 REFIO_A/B "should be decoupled … with 10-µF" capacitors (§8.3.1).
- The ADS8353 sampling capacitor is ≈ 40 pF (§8.3.2.1): the reason for the driver and the 20 Ω/1 nF filter.
- Simultaneous sampling of A and B on the CS falling edge.

## Layout guidance
Dividers at the output-filter caps, the driver and ADC near the FPGA side of the amp region, with 3V3/5V analog decoupling. Route as analog, away from the inductors.

## Open questions
1. For a true closed-loop variant, a lower-noise differential front end (a precision difference amplifier per channel) may be needed. That belongs to the closed-loop variant; this footprint set gives measurement and calibration now.
