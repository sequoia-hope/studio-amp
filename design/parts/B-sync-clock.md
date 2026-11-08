# Block B primary-side sync clock — 737.28 kHz into UCC2897A SYNC

Lead decision (2026-11-07, beat conflict with the 576 kHz amp PWM): converter nominal ≈ 740 kHz,
held in **712–775 kHz across all tolerances** (block E's beat check: every |a·f_acf − b·576 kHz|,
a, b ≤ 3, ≥ 100 kHz).

## Why the UCC2897A oscillator alone cannot do it

UCC2897A datasheet p.7 (EC table, RON = ROFF = 75 k): fOSC 237–265 kHz at TJ = 25 °C (−5.2/+6.0 %),
and **225–270 kHz over −40…125 °C and VDD 8.5–14.5 V (−10/+8 %)**. The timing capacitor is
internal (§8.3.1.3, "internal timing capacitor"), so precision RON/ROFF (1 %) do not remove that
spread; there is no external CT to make C0G. Free-running, the guaranteed band would be ±10 %,
e.g. 666–799 kHz at 740 kHz nominal. That breaks the 712–775 kHz window. **Free-running ±5 % cannot be
guaranteed.**

## Solution: crystal clock on the primary into SYNC

The UCC2897A has a bidirectional SYNC pin (§8.3.1.5, §8.3.6). It synchronises to an external clock
whose frequency is above the free-running frequency, with a pulse width ≥ 50 ns and
< (1 − DMAX) × TSYNC. The rising edge ends the charge interval, and the discharge (tOFF, set by ROFF)
follows, so DMAX in sync = 1 − tOFF/TSYNC.

Clock chain (all on the primary, referenced to `VPRI_RTN`):
1. **HT7550-1** 5 V LDO from `VB_PRI` (14.3 V; VIN max 30 V, IOUT ≥ 60 mA) → `V5_CLK`, 1 µF in/out.
2. **Pierce oscillator: SN74LVC1GU04** (unbuffered inverter, VCC 5 V) + **7.3728 MHz crystal**
   (YXC HC-49SMD, AT-cut, ±20 ppm at 25 °C, ±20 ppm over temperature; CL 20 pF class) with 2 × 33 pF
   C0G (33 × 33/66 + ≈ 5 pF stray ≈ 21.5 pF), Rf 1 MΩ, Rs 1 kΩ (drive-level limiting; ESR ≤ 60 Ω at
   7–10 MHz).
3. **74HC4017** decade counter (fmax ≥ 24 MHz at 4.5 V, 85 °C) clocked at 7.3728 MHz: output Q0 is
   high for one clock period out of ten → **737.28 kHz, 136 ns pulse**.
4. Q0 → 100 Ω → UCC2897A SYNC (pin 7). SYNC input high ≥ 3 V ✓ (5 V CMOS); no capacitor on SYNC (§8.3.1.5).

## Calculations

- Frequency: 7.3728 MHz/10 = **737.28 kHz**, ±40 ppm (crystal) + aging ±3 ppm/yr → effectively exact;
  inside 712–775 kHz with ≥ 3.4 % margin. Beats with 576 kHz: f − 576 = 161 kHz, 2·576 − f = 415 kHz,
  3·576 − 2f = 253 kHz, 2f − 576 = 899 kHz: all ≥ 100 kHz ✓ (block E's rule).
- Pulse width 136 ns: ≥ 50 ns ✓; < (1 − 0.70) × 1.356 µs = 0.41 µs ✓.
- Free-running must stay below the sync frequency: RON 31.6 k / ROFF 14.3 k → tON 1.091 µs,
  tOFF 0.434 µs → free-running 656 kHz nominal, 590–708 kHz (−10/+8 %) < 737 kHz ✓ (4 % margin).
- DMAX in sync = 1 − tOFF/TSYNC = 1 − 0.434/1.356 = **0.680**. With ±5 % on tOFF (internal current
  and C) the range is 0.664–0.696; regulation needs 0.655 at 37.6 V ✓. The datasheet says DMAX
  "remains accurate" in sync; this design uses the more conservative tOFF-based value. Bench check.
- Supply: LVC1GU04 in a Pierce at 7.4 MHz ≈ 1–2 mA, 74HC4017 at 7.4 MHz (C_PD × V² × f) ≈ 1–2 mA,
  LDO Iq; budget **4 mA** from `VB_PRI` (in `B-bias.md`). Power ≈ 0.06 W.
- **Clock-failure fallback:** if the clock stops, the controller free-runs at 590–708 kHz and the
  converter keeps working. Volt-seconds: 57 × 0.75 (free-running DMAX max)/590 kHz = 72 Vµs (60 %
  cold, ≈ 80 % hot) ✓. The beat with 576 kHz can then fall into the audio band, so **block E
  measures f_acf from `ACF_PULSE`; if it is not 737.28 kHz ± 0.5 %, firmware flags a converter
  clock fault** and can lower amp output or warn.
- The crystal's operating range is −20…+70 °C or −40…+85 °C depending on suffix; the part number
  `X49SM73728MSD2SC` was checked as LCSC stock only. **Open item: confirm the temperature
  suffix** with YXC's part-number key (R-40 needs ≥ 85 °C; at 55 °C cabinet air the board is well
  under 70 °C, but buy the −40…+85 °C code).

## Parts

| Part | Supplier line | Datasheet |
|---|---|---|
| HT7550-1 (5 V LDO, SOT-89) | `C16106 HT7550-1 (HOLTEK, SOT-89-3): preferred, JLC stock 184039, lifecycle normal, checked 2026-11-07` | datasheets/ht7550-umw.pdf (UMW second source C347189, same pinout; Holtek's sheet not on LCSC) |
| SN74LVC1GU04DBVR | `C81934 SN74LVC1GU04DBVR (TI, SOT-23-5): extended, JLC stock 7291, lifecycle normal, checked 2026-11-07` | datasheets/sn74lvc1gu04.pdf |
| 7.3728 MHz crystal, HC-49SMD | `C2242 X49SM73728MSD2SC-1 (YXC Crystal Oscillators, HC-49S-SMD): extended, JLC stock 5863, lifecycle normal, checked 2026-11-07` | datasheets/yxc-x49sm-7m3728.pdf |
| 74HC4017D | `C148206 74HC4017D,653 (Nexperia, SOIC-16): extended, JLC stock 5188, lifecycle normal, checked 2026-11-07` | datasheets/74hc4017-nexperia.pdf |

## Layout

Clock on the primary next to the UCC2897A, on the GND island (SYNC is a small-signal pin), with the
crystal and its caps tight to the inverter, away from the main-FET drain and T1.
