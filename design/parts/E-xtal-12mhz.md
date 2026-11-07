# Y (MCU crystal) — Abracon ABM8-272-T3, 12 MHz, with load capacitors

Datasheet: `datasheets/abm8-272-t3.pdf` (Abracon drawing 456603, rev IR, 2023-11-16). Read: all 4 pages (electrical, ordering, dimensions, reflow, packaging). Circuit: `datasheets/hardware-design-with-rp2350.pdf` §4 and §4.1.
MPN: ABM8-272-T3
Supplier: `C20625731 ABM8-272-T3 (ABRACON, SMD3225-4P): extended, JLC stock 9967, lifecycle normal, checked 2026-11-07`
Footprint: 3.2 × 2.5 × 0.8 mm 4-pad ceramic (drawing p.2). Chamfer may be on pin 1, 3 or 4 (note p.2) — orient by the pad, not the chamfer.

This is the crystal Raspberry Pi tuned the RP2350 oscillator for ("We highly recommend using this crystal along with the accompanying circuitry", guide §4; "Any deviation … will require extensive testing", §4).

## Specs vs use

| Parameter | ABM8-272-T3 | RP2350 need / ours | OK |
|---|---|---|---|
| Frequency | 12.000 MHz fundamental AT | USB bootloader default 12 MHz (RP2350 Tab 2, XIN/XOUT) | OK |
| Tolerance / stability | ±30 / ±30 ppm, −40…+85 °C | USB FS ±2500 ppm; nothing else timing-critical uses it (audio runs from the VCXO, Ethernet from the 50 MHz XO) | OK |
| CL | 10 pF | circuit below gives 10.5 pF | OK |
| ESR | 50 Ω max | with 1 kΩ series, per reference | OK |
| C0 | 3.0 pF max | | |
| Drive | 10 µW typ, 200 µW max | 1 kΩ series limits drive at IOVDD 3.3 V (guide §4) | OK |
| Ageing | ±5 ppm/yr | | OK |

## Calculations

- **Load capacitance** (guide §4): CL = C3·C4/(C3 + C4) + Cstray = 15 pF/2 + 3 pF = **10.5 pF** vs 10 pF spec. Pulling from the 0.5 pF excess ≈ (C1 / 2) · (1/(C0 + CL,spec) − 1/(C0 + CL,actual)); C1 isn't in the datasheet, so take a generous 5 fF for a 12 MHz 3225 crystal: 2.5 fF × (1/13 − 1/13.5) pF⁻¹ = 7 ppm. Irrelevant for USB.
- **Load capacitors**: 15 pF C0G 50 V 0402 — `C1548 0402CG150J500NT (FH, 0402): basic, JLC stock 1205871, lifecycle normal, checked 2026-11-07` ×2. C0G: no DC-bias or temperature drift to speak of (FH datasheet, Class I). 50 V ≫ 3.3 V.
- **Series resistor**: 1 kΩ in XOUT — `C11702 0402WGF1001TCE … basic` ×1 (guide §4, R2).
- Stray 3 pF assumed by Raspberry Pi; keep the XIN/XOUT traces short (< 5 mm) so it holds.

## Layout

Crystal next to pins 30/31 (XIN/XOUT), caps at the crystal, GND guard, nothing routed under it on the adjacent layer (domains/high-speed.md "Crystals").
