# U (3V3_Q) — TPS7A9401 ultra-low-noise 3.3 V LDO (DAC reclock flip-flops)

Datasheet: datasheets/tps7a94.pdf (English, ti.com). Read: features, pins, abs max, ROC, EC,
§7.3.1 output setting, NR/SS, EN_UV, PG, application.
MPN: TPS7A9401DSCR   Supplier: `C5220127 TPS7A9401DSCR (TI, WSON-10(3x3)): extended, JLC stock 2441, lifecycle normal, checked 2026-11-07`
Footprint: WSON-10 3 × 3 mm "DSC" with EP. Pins: 1–2 IN, 3 EN_UV, 4 PG, 5 FB_PG, 6 GND,
7 NR/SS, 8 SNS, 9–10 OUT, thermal pad to GND.

**Changed from TPS7A2033 (revision after block F's requirements, 2026-11-07).** Block F needs
≤ 5 µVrms over 20 Hz–20 kHz, Zout ≤ 0.1 Ω from 20 Hz to 50 kHz, and 30 mA. The DAC output level is
VDD × modulation, so supply noise and load-dependent droop appear directly in the audio.
TPS7A20 (datasheets/tps7a20.pdf, Fig. 5-65) shows ≈ 0.6 µV/√Hz at 10 Hz, falling to ≈ 0.03 µV/√Hz
above 1 kHz. Read by eye, that integrates to roughly 4–6 µVrms in 20 Hz–20 kHz, out of 6.7 µVrms over
10 Hz–100 kHz: marginal against 5 µV. TPS7A94 is 0.46 µVrms (10 Hz–100 kHz), with 102/110/95 dB PSRR
at 100 Hz/1 kHz/10 kHz, so it has a 10× margin.

## Absolute max vs our worst case

| Parameter | Abs max / ROC | Ours | Margin |
|---|---|---|---|
| IN, EN_UV, PG | 6.0 V abs; VIN 1.7–5.7 V ROC | +5V 5.12 V max (buck) / 5.25 V (USB) | OK |
| OUT | VIN + 0.3 V | 3.3 V | OK |
| FB_PG | 1.5 V | divider ≤ 0.3 V | OK |
| IOUT | ICL 0.96–1.12 A nominal, set to 60 % ≈ 0.62 A by FB_PG | 35 mA design (block F: FFs + SN74LVC2G34 buffer) | OK |
| COUT | 4.7–1000 µF, ESR 1–20 mΩ | 2 × 22 µF X7R/X5R ceramic | OK |
| CNR/SS | 1–100 µF (4.7 µF typ) | 4.7 µF | OK |
| RPG | 10–100 kΩ | 100 kΩ | OK |

## Calculations

- **Output** (§7.3.1, VOUT = INR/SS × RNR/SS, INR/SS = 150 µA, ±1 % for 1.2–5.1 V): RNR/SS = 22.0 kΩ
  0.1 % → **3.30 V** ±1.1 %. 0.1 % so the resistor doesn't dominate the tolerance (§7.3.1).
- **Noise filter** (eq. 4): fc = 1/(2π × 22 k × 4.7 µF) = 1.5 Hz, so the reference noise is
  filtered below the audio band.
- **Headroom / dissipation**: VIN − VOUT = 1.75 V (buck) / ≥ 1.4 V (USB minimum) against a 150 mV
  dropout at 1 A. PSRR is quoted for ≥ 500 mV headroom. Loss 1.75 × 35 mA = 61 mW; RθJA 46 °C/W →
  +2.4 °C.
- **Zout ≤ 0.1 Ω, 20 Hz–50 kHz**: DC load regulation 1 mA–1 A at 3.3 V is a few mV over 1 A (EC
  table), i.e. mΩ. At the top of the band the output caps alone meet it: 2 × 22 µF (≥ 30 µF effective
  at 3.3 V, assumed) → 1/(2π × 50 kHz × 30 µF) = 0.11 Ω, falling below 0.1 Ω above ≈ 55 kHz. The
  wide-bandwidth unity-gain loop holds it lower in between. **Phase 8: confirm with the datasheet's
  load-transient figures or a simulation of the PSRR/Zout model.**
- **Enable gating (block F's request)**: EN_UV from **+15V** through 47 kΩ / 10.0 kΩ. EN =
  15 × 10/57 = 2.63 V on, below the 6 V abs max. Turn-on at 1.22 V (1.20–1.25) → +15V ≥ 7.1 V.
  Turn-off at 1.22 − 0.15 V hysteresis → +15V < 6.1 V. So 3V3_Q exists only while ±15 V does
  (the Fly-Buck makes both together), and it is off on USB-only power, so the flip-flop outputs
  can't drive unpowered SA5532 inputs.
- **PG / FB_PG (now required; block F needs PG_3V3Q)**: §8.1.5 says FB_PG must not float (its
  impedance is sampled at start-up), and the divider's parallel impedance also sets the current
  limit: < 12.5 kΩ gives 100 % ICL, 12.5–50 kΩ 80 %, 50–100 kΩ 60 %. Chosen: RFB_PG(TOP) = 931 kΩ,
  RFB_PG(BOTTOM) = 68.1 kΩ. The parallel value 63.5 kΩ gives 60 % of 1.04 A ≈ 0.62 A, enough current
  limit for a 35 mA load and gentler into a fault. PG asserts at 0.2 V × (1 + 931/68.1) = 2.93 V
  (89 % of 3.3 V; 0.19–0.21 V trip → 2.78–3.07 V). PG is open drain, 100 kΩ to +3V3 (RPG 10–100 kΩ),
  giving `PG_3V3Q` → FPGA ball B5 (bank 0, through block E's 1 kΩ series). The
  FPGA gateware holds the DAC flip-flop inputs low until PG_3V3Q is high, because the 74LVC74A has
  no Ioff spec (block F).

## Consequence for block F (gating)

With 3V3_Q off while the FPGA (on +3V3) can drive the flip-flops' D/CLK inputs, **those
flip-flops must be a family with Ioff / partial-power-down inputs** (e.g. 74LVC/74AUP), or the FPGA
must hold those pins low until `PG_3V3Q` (or the ±15 V state) is high. Otherwise the inputs
back-power 3V3_Q through their clamp diodes. This is block F's part choice.

## Fine print

- COUT ESR must be ≤ 20 mΩ: ceramic only, no tantalum.
- The NR/SS cap sets the start-up time (TPS7A94 p. 37, corrected after review): fast charge 2.1 mA to
  ≈ 93 % (3.07 V × 4.7 µF / 2.1 mA = 6.9 ms), then 150 µA for the last 0.23 V (0.23 V × 4.7 µF / 150 µA =
  7.2 ms) → **≈ 14 ms** to regulation, then the 1.5 Hz NR filter settles. A slow, monotonic, quiet start. That is slow and monotonic, which
  suits a quiet audio start.
- SNS (pin 8) is the remote-sense input: connect it to OUT at the flip-flops' supply point (Kelvin)
  to keep trace resistance out of Zout.

## Layout

- In block F's analog region, with its own GND return. CIN 10 µF, COUT 2 × 22 µF and CNR at the pins;
  route SNS separately to the load. EP to GND with vias.
