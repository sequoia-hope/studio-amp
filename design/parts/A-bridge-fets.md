# Q (block A, 8 pcs) — PSMN040-100MSE bridge N-FETs

Datasheet: `datasheets/A-psmn040-100mse.pdf` (Nexperia product data sheet, 26 March 2013). Read: pp.1–13.
MPN: PSMN040-100MSEX
Supplier: `C458214 PSMN040-100MSEX (Nexperia, LFPAK33-8): extended, JLC stock 1051, lifecycle normal, checked 2026-11-07`
Build need: 8 per board x 5 = 40 + attrition ≈ 45. OK.
Alternate (same footprint, LT4321's own 25 W example): `C478016 PSMN075-100MSEX (Nexperia, LFPAK33-8): extended, JLC stock 333, lifecycle normal, checked 2026-11-07` — 75 mΩ class, VF 65 mV at 0.865 A, still in the 20–70 mV window at 25 °C but not hot; second choice only.
Footprint: LFPAK33 (SOT1210), pins 1–3 source, 4 gate, mounting base = drain (p.2). Use Nexperia's
SOT1210 land pattern; KiCad `Nexperia_LFPAK33` / `LFPAK33` footprint, check against the SOT1210 drawing
in phase 2.

The part is marketed for "high power PoE applications" (p.1) and ADI uses this exact MPN in the LT4321
70 W reference (LT4321 p.12).

## Absolute max vs our worst case

| Parameter | Abs max | Our worst case | Margin |
|---|---|---|---|
| VDS | 100 V (Tj 25…175 °C); BVDSS ≥ 90 V at –55 °C (p.5) | 57 V; 93.6 V TVS clamp | OK at ≥ 0 °C; cabinet minimum is 0 °C (R-40) |
| VGS | ±20 V | TG–IN ≤ 11 V, BG ≤ 13 V (LT4321 p.3) | OK |
| ID | 30 A (Tj 25 °C), 21 A (Tmb 100 °C) | 0.96 A per pair set, peak 1.75 A x 75 ms PSE template (TPS2373 p.29) | ≫ |
| IDM | 121 A, 10 µs | PSE template 50 A for 10 µs per 2-pair (TPS2373 p.29) | OK |
| Tj | 175 °C | 55 °C + 49 mW (negligible) | OK |

## Calculations

1. **Conduction loss**, see `A-bridge-lt4321.md` calc 2: 49 mW per FET at Class 8 with RDS(on) = 66 mΩ
   (max, Tj = 100 °C, p.5). VGS from the LT4321 is 7.7 V min (TG) / 10 V min (BG); the output curves (Fig. 13)
   show RDS(on) at VGS = 7 V within a few % of the 10 V value at these sub-amp currents, and VGS(pl) is
   5.6 V typ (p.6), so 7.7 V is well into enhancement.
2. **VGS(th) requirement** (LT4321 p.8: "gate threshold must be a minimum of 2 V"): PSMN040 VGS(th) =
   2.3 V min at 25 °C, 1 V min at 175 °C (p.5). Interpolating linearly, the minimum crosses 2.0 V at
   ≈ 60 °C Tj. The FETs dissipate < 50 mW so Tj ≈ board temperature, ≤ 55–65 °C in the cabinet.
   Marginal but ADI's own reference uses this part (LT4321 p.12). Recorded as a known margin; the
   LT4321 actively holds off FETs (TG pulled to IN, BG to OUTN, p.3), so the 2 V rule protects against
   leakage-induced turn-on, not normal operation.
3. **Backfeed** (TPS2373 §8.2.2.1 p.33: ≤ 2.8 V across 100 kΩ on an unpowered pair set): unpowered
   bridge's FETs are off; leakage = IDSS ≤ 1 µA at 25 °C, ≤ 500 µA at 175 °C (p.5); at ≤ 65 °C, a
   class-typical doubling per 10 °C gives ≲ 20 µA ⇒ 2 µA–20 µA x 100 kΩ = 0.1–2 V (two FETs in the
   path, so per-path leakage is that of one off FET). Under 2.8 V. Verify on the first board (100 kΩ
   on the unpowered pair, PSE on the other).
4. **Body-diode operation** (LT4321 disabled / brownout): VSD ≤ 1.2 V at 20 A, 0.82 typ (p.6); at 0.87 A
   ≈ 0.7 V ⇒ 2 x 0.7 x 0.87 = 1.2 W per bridge, transient only.

## Fine print

- Drain = mounting base: the tab is the CT-side or OUTP-side net depending on position in the bridge —
  it carries 57 V. Keep tab copper ≥ 0.64 mm from VSS-referenced low-voltage copper.
- High-side (TG) FETs: drain to OUTP, source to IN*; low-side (BG) FETs: drain to IN*, source to OUTN
  (LT4321 p.1 typical application).

## Layout

- Group the four FETs of each pair set round their two CT pins, gates ≤ 5 mm from LT4321 TG/BG pins.
- Modest copper on drains; no heatsinking needed.

## Open questions

- None beyond the VGS(th)-vs-temperature margin above.
