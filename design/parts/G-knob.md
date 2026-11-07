# J (KNOB) — optional knob/encoder header: 4 ADC + 4 encoder GPIO (R-17)

Datasheets: datasheets/xfcn-pz254v-12.pdf (2.54 mm 2-row male header), datasheets/pesd5v0s1bl.pdf,
datasheets/rp2350-lcsc.pdf (§6.1.5 ADC_AVDD; §12.4 ADC).
Footprint: KiCad `Connector_PinHeader_2.54mm:PinHeader_2x06_P2.54mm_Vertical`.

| Part | MPN | Supplier line |
|---|---|---|
| 2×6 male header 2.54 mm (optional population) | PZ254V-12-12P | `C492423 PZ254V-12-12P (XFCN, Through Hole,P=2.54mm): extended, JLC stock 33440, lifecycle normal, checked 2026-11-07` |
| ESD ×8 | PESD5V0S1BL,315 | `C84374 PESD5V0S1BL,315 (Nexperia, DFN1006-2): extended, JLC stock 76124, lifecycle normal, checked 2026-11-07` |
| RC and pull-ups | 0402 1 % / X7R (basic) | phase 2 |

## Pinout (proposed)

| Pin | Net | Pin | Net |
|---|---|---|---|
| 1 | KNOB_REF | 2 | GND |
| 3 | KNOB1 | 4 | KNOB2 |
| 5 | KNOB3 | 6 | KNOB4 |
| 7 | ENC1A | 8 | ENC1B |
| 9 | ENC2A | 10 | ENC2B |
| 11 | +3V3 through 47 Ω (for encoder pull-ups/indicator LEDs ≤ 10 mA; a short draws 70 mA, which +3V3 tolerates) | 12 | GND |

## Circuit

- **KNOB_REF**: from the RP2350's `ADC_AVDD` node (block E's filtered supply) through 100 Ω to
  pin 1, with 1 µF to GND at the header. The pots run between KNOB_REF and GND, so readings are
  ratiometric to the ADC's own reference (the RP2350 ADC is referenced to ADC_AVDD, §6.1.5).
- **KNOBn**: header → PESD5V0S1BL → 1 kΩ series → 100 nF X7R to GND at the RP2350 ADC pin (ADC0…3
  on the RP2350B, block E's map).
- **ENCnA/B**: header → PESD5V0S1BL → 1 kΩ series → RP2350 GPIO, 10 kΩ pull-up to +3V3 on the GPIO
  side, 10 nF to GND (debounce).

## Calculations

- ADC filter: source = pot Thevenin (≤ 2.5 kΩ for 10 kΩ pots at mid-travel) + 1 kΩ = 3.5 kΩ;
  τ = 3.5 kΩ × 100 nF = 0.35 ms, fc ≈ 450 Hz (1.6 kHz with the 1 kΩ alone). Knob bandwidth needs
  < 50 Hz, and the 100 nF is a charge reservoir for the SAR's sample capacitor (error ≪ 1 LSB).
- KNOB_REF drop: 4 × 10 kΩ pots in parallel = 2.5 kΩ → 3.3 V × 100/2600 = 0.13 V (3.8 %). Because
  KNOB_REF is lower than the ADC reference, full-scale reads 96 %; firmware calibrates the end
  points. 50 kΩ pots cut this to 0.8 %. Short-circuit current at the header is 33 mA, which the
  ADC_AVDD filter (block E) must tolerate; otherwise raise to 220 Ω.
- Encoder RC: 10 kΩ × 10 nF = 100 µs rise, which passes hand-turned detent rates (< 1 kHz edges)
  and rejects contact bounce.
- Input protection: the 1 kΩ limits current into the RP2350's ESD diodes to (V − 3.6 V)/1 kΩ. A 12 V
  miswire gives 8 mA: survivable for the PESD (VRWM 5 V, clamps ≈ 14 V at 1 A) and the pin.
- PESD5V0S1BL: 35 pF typ, irrelevant at these bandwidths (it adds to the 100 nF / 10 nF).

## Fine print

- RP2350 §6.1.5: ADC input voltage must not exceed IOVDD. KNOB_REF ≤ ADC_AVDD = 3.3 V = IOVDD. OK.
- The header is optional population. The RC, ESD and pull-up parts are always fitted (cheap), so an
  unpopulated header leaves the ADC pins at 0 V and the encoder inputs pulled high.

## Open questions

- Block E: confirm ADC0–ADC3 are free for knobs (NTCs and VBUS sense also want ADC inputs) and that
  ADC_AVDD can source ≈ 1.3 mA of pot current.
