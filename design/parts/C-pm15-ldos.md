# U (+15), U (−15) — TPS7A4901 / TPS7A3001 low-noise post-regulators

Datasheets: datasheets/tps7a49.pdf (SBVS121E, May 2015), datasheets/tps7a30.pdf (SBVS125B, Dec 2013).
Read: all sections of both.
MPN: TPS7A4901DGNR   Supplier: `C16430 TPS7A4901DGNR (TI, HVSSOP-8): extended, JLC stock 5633, lifecycle normal, checked 2026-11-07`
MPN: TPS7A3001DGNR   Supplier: `C33835 TPS7A3001DGNR (TI, HVSSOP-8): extended, JLC stock 5267, lifecycle normal, checked 2026-11-07`
Footprint: HVSSOP-8 "DGN" with PowerPAD (MSOP-8 EP). TPS7A49 pins: 1 OUT, 2 FB, 3 NC, 4 GND, 5 EN,
6 NR/SS, 7 DNC, 8 IN. TPS7A30 has the same arrangement (pin table): 1 OUT, 2 FB, 3 NC, 4 GND, 5 EN,
6 NR/SS, 7 DNC, 8 IN.

## Absolute max vs our worst case

| Parameter | TPS7A49 abs max | Ours (+) | TPS7A30 abs max | Ours (−) |
|---|---|---|---|---|
| IN to GND | −0.3…36 V (ROC 3–35 V) | 18.4 V max | −36…+0.3 V (ROC −35…−3 V) | −20 V worst light-load |
| OUT to GND | 33 V | 14.94 V | −33 V | −15.09 V |
| EN | ≤ VIN, 36 V | tied to IN | ±36 V, \|VEN\| ≤ \|VIN\| | tied to IN |
| NR/SS to GND | 2 V | internal | −2 V | internal |
| IOUT (ROC) | 150 mA | 80 mA | 200 mA | 80 mA |
| TJ (ROC) | 125 °C | see below | 125 °C | see below |

## Calculations

**+15 V** (TPS7A49 eq. 2; VREF 1.188 V typ, 1.176–1.212 V): R2 (bottom) = 9.76 kΩ, R1 (top) =
113 kΩ → 1.188 × (1 + 113/9.76) = **14.94 V** (±2 % with 1 % resistors). R2 ≤ 237 kΩ (ROC). Divider
current 122 µA ≥ 5 µA (stability at no load, footnote 2).
**−15 V** (TPS7A30; VREF −1.179 V typ, −1.166…−1.202 V): R2 = 10.0 kΩ, R1 = 118 kΩ →
−1.179 × (1 + 11.8) = **−15.09 V**. The rails match within 1 %. If block F needs them closer, use
0.1 % resistors (datasheet note on FB current offset).

**Headroom** (TPS7A49 §9.2: "VIN − VOUT − VDO(max) … at least 1 V" for full performance):
+: 18.4 − 14.94 − 0.6 (VDO max 150 mA; 0.26 V typ at 100 mA) = 2.86 V. OK.
−: 17.8 − 15.09 − 0.6 = 2.1 V. OK; cross-regulation droop of up to 0.7 V is still fine.

**Dissipation** (revised for block F's loads; pre-reg now +18.4 / −17.8 V):
+ design 120 mA: (18.4 − 14.94) × 0.12 = 0.42 W, RθJA 47.7 °C/W (DGN) → +20 °C. Fault 200 mA (both
headphone outputs shorted): 0.69 W → +33 °C. 200 mA exceeds the 150 mA ROC rating, so the internal
current limit ("internally limited", abs max) may act. That is acceptable for a fault, per block F.
− design 110 mA: (17.8 − 15.09) × 0.11 = 0.30 W, θJA 55.1 °C/W → +16.4 °C. Fault 190 mA: 0.51 W →
+28 °C, within the 200 mA rating.
At R-40's 55 °C air, TJ ≤ 88 °C in the fault case, < 125 °C ROC. Phase 4: PowerPAD to ≥ 2 cm² of
GND copper with vias on both.

**Capacitors** (both datasheets: CIN, COUT ≥ 2.2 µF, 10 µF recommended for AC performance; ESR
< 200 mΩ; CNR/SS and CFF/CBYP 10 nF recommended; ceramic X7R/X5R):
- CIN 10 µF 50 V X7R 1210 (after the BLM18PG221 ferrite; see C-pm15-flybuck.md).
- COUT 10 µF 50 V X7R 1210 (≈ 50 % at 15 V → 5 µF effective, above the 2.2 µF stability minimum).
- CNR/SS 10 nF C0G/X7R 25 V; CFF (TPS7A49) / CBYP (TPS7A30) 10 nF across FB–OUT (R1).
- Soft start (TPS7A49 eq. 1): tSS = 1.4 ms/nF × 10 nF = **14 ms**. The TPS7A30 is similar with
  10 nF. Both rails ramp together, slowly, which helps block F's pop-free start.

**Noise / PSRR achieved**: TPS7A49 15.4 µVrms (10 Hz–100 kHz, CNR = CFF = 10 nF), 72 dB at 120 Hz.
TPS7A30 15.1 µVrms, 72 dB at 120 Hz, "above 55 dB from 10 Hz to 700 kHz" in the max-AC-performance
configuration. Fly-Buck ripple (≤ 20 mV at 498 kHz, less after the ferrite + 10 µF stage) → ≤ 30 µV
at the outputs, well below block F's needs. Its headphone stage has its own PSRR.

## Fine print / gotchas

- DNC (pin 7) on both: "Do not connect … not even GND or IN". It must be a no-connect in the
  footprint/net. NC (pin 3) open or GND.
- PowerPAD: open or GND (TPS7A30: "must either be left open or tied to GND"). Tie it to GND for heat.
- TPS7A30 EN is dual-polarity (|VEN| > 2.0 V enables). Tie it to IN (−17.4 V) or drive it from
  positive logic (a 3.3 V GPIO works, per the "Enable" section). EN stays tied to IN; the Fly-Buck's
  UVLO / AN_OFF provides the control.
- Both: "Do not place any of the capacitors on the opposite side" (TPS7A30 layout). Same side, close.

## Layout guidance

- Caps on the same side, as close as possible. Ground the output cap at the GND pin. PowerPAD to a
  plane with vias.
- Place both LDOs at the edge of block F's analog region, so the ±15 V outputs are short and the
  pre-regulator and ferrites are outside the region.

## U (+5V_A) — third TPS7A4901 (block F request): quiet +5 V from +15V, ≤ 15 mA

For the PCM1808 ADC analog supply and the mic bias (block F). It reuses the TPS7A4901, so no new part
type: `C16430 TPS7A4901DGNR (TI, HVSSOP-8): extended, JLC stock 5633, lifecycle normal, checked 2026-11-07`.
- Input +15V (post-regulated, so this rail gets cascaded PSRR); its ≤ 15 mA counts inside +15V's
  120 mA design load.
- Output (eq. 2): R2 = 10.0 kΩ, R1 = 32.4 kΩ → 1.188 × (1 + 3.24) = **5.04 V** (±2 %). Divider
  current 119 µA ≥ 5 µA.
- Headroom 15 − 5.04 − VDO (< 0.1 V at 15 mA) ≈ 9.8 V. Dissipation 9.96 × 15 mA = 0.15 W → +7 °C.
- CIN/COUT 10 µF 25 V X7R, CNR 10 nF, CFF 10 nF (same recipe as above). Noise 15.4 µVrms
  (10 Hz–100 kHz), within block F's ≤ 20 µVrms.
- EN tied to IN. It comes up with +15V (14 ms soft start of its own).
- Why not from +5V: that rail carries the LED/logic return currents and switches between the buck
  and USB. Deriving it from +15V keeps the whole analog supply on the analog converter, and it is off
  on USB power like the rest of block F.
