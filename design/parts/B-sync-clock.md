# Block B primary-side sync clock — 737.28 kHz into UCC2897A SYNC

Revised 2026-11-08 for the second-pass review (`design/gates/rereview-phase1-AB.md`, AB-M1, AB-M2,
m-AB8, n-AB1, n-AB3).

Lead decision (2026-11-07, beat conflict with the 576 kHz amp PWM): converter nominal ≈ 740 kHz,
held in **712–775 kHz across all tolerances** (block E's beat check: every |a·f_acf − b·576 kHz|,
a, b ≤ 3, ≥ 100 kHz).

## Why the UCC2897A oscillator alone cannot do it

UCC2897A datasheet p.7 (EC table, RON = ROFF = 75 k): fOSC 237–265 kHz at TJ = 25 °C (−5.2/+6.0 %),
and **225–270 kHz over −40…125 °C and VDD 8.5–14.5 V (−10/+8 %)**. The timing capacitor is
internal (§8.3.1.3), so precision RON/ROFF (1 %) do not remove that spread, and there is no external
CT to make C0G. Free-running ±5 % cannot be guaranteed.

## Solution: crystal clock on the primary into SYNC, gated by clock-OK, with only the SYNC driver on VREF

The UCC2897A SYNC pin (§8.3.1.5, §8.3.6) synchronises to an external clock faster than its free-running
frequency, with a pulse width ≥ 50 ns and < (1 − DMAX) × TSYNC. **If SYNC stays high, both outputs
are off** (§8.3.6), so a stopped clock must never leave SYNC high.

Revised again 2026-11-08 for the third-pass review (`design/gates/rereview2-phase1.md` MAJOR-2, m-4,
m-5, m-7). **Only the SYNC driver (SN74LVC1G08) runs from the UCC2897A VREF.** The oscillator, counter
and clock-OK one-shot run from a small primary 5 V rail (`V5_CLK`, HT7550 reinstated) off `VB_PRI`.
Reason: the Pierce inverter's linear-mode current is not in its datasheet (plausibly 3–8 mA at 5 V),
which could take the whole ≈ 5 mA VREF budget that also feeds the controller's own logic.

All parts on the primary, referenced to the UCC2897A GND island (`VPRI_RTN`):

0. **HT7550-1** 5 V LDO from `VB_PRI` (14.3 V; VIN max 30 V, IOUT ≥ 60 mA) → `V5_CLK` (4.85–5.15 V),
   1 µF in and out.
1. **Pierce oscillator: SN74LVC1GU04** (VCC = `V5_CLK`) + **7.3728 MHz crystal, SCTF
   SXMH7.3728F2020F30**. Decoded from the SCTF sheet p.2 (m-5): HC-49SMD, AT fundamental, **CL 20 pF,
   ±20 ppm tolerance, −40…+85 °C ("F"), ±30 ppm over temperature**, ESR ≤ 60 Ω (6–10 MHz), drive
   100 µW typ / 500 µW max, C0 7 pF. C1 = C2 = 33 pF C0G (33 × 33/66 + ≈ 5 pF stray ≈ 21.5 pF),
   Rf 1 MΩ, Rs 1 kΩ (drive ≈ 70 µW ✓).
2. **74HC4017** (VCC = `V5_CLK`): CP0 ← oscillator output (no Schmitt input is claimed; the 7.4 MHz
   Pierce output is near-square, bench-check), **CP1 and MR tied to GND**. **Q1** is high for one clock
   period in ten → 737.28 kHz, 136 ns.
3. **Clock-OK one-shot (m-4): SN74LVC1G123** (VCC = `V5_CLK`), retriggerable, B ← CO (Q5-9, toggles at
   737 kHz while counting), A tied low, CLR high; Rext 10 kΩ / **Cext 470 pF** → tw ≈ 4.5 µs (SCES586D graphs; K ≈ 1 only above ≈ 1 nF, so
   220 pF gave only ≈ 2.0–2.5 µs against the 1.356 µs CO period; fourth-pass m-1). It must be
   > 1.36 µs and ≤ 10 µs. Q = `CLK_OK`: high while CO keeps retriggering, falls with a clean logic edge
   ≈ 4.5 µs after CO stops. This replaces the BAT54S pump, whose 100 µs ramp violated the LVC input
   transition-time limit.
4. **SN74LVC1G08, VCC = VREF** (the only part on VREF): SYNC_DRV = Q1 AND `CLK_OK` → 100 Ω → UCC2897A
   SYNC (pin 7); **10 kΩ SYNC to GND**. No capacitor on SYNC.

**SYNC ≤ VREF + 0.3 V in every state:**
- VREF on: the LVC1G08's VOH ≤ VCC = VREF ✓. Its inputs (Q1, `CLK_OK` at up to 5.15 V) are
  5.5 V-tolerant independent of VCC ✓.
- VREF off (below UVLO, during the VB_PRI ramp, after a UVLO trip) while `V5_CLK` is up: the LVC1G08
  has VCC = 0, and its IOFF circuit keeps the output from driving (no path from inputs to output or
  VCC). The 10 kΩ holds SYNC at 0 V ≤ 0.3 V ✓. The UCC2897A's own ±600 µA SYNC driver (p.7), when
  active, is overridden by nothing larger than 60 mV across the 100 Ω ✓.
- VREF ramping: VOH tracks VCC ✓.
- `V5_CLK` off, VREF on: impossible in normal operation, since both derive from VB_PRI. If it
  happens, the inputs are low and SYNC is low → free-run ✓.

Fallback (AB-M2): if the crystal or inverter stops, the counter freezes, CO stops, `CLK_OK` falls ≈ 4.5 µs
later and SYNC is forced low even if Q1 froze high → free-run at 590–708 kHz (converter off ≤ 5 µs).
Start-up: `V5_CLK` comes up with VB_PRI; the crystal starts in a few ms. During crystal start-up
CP0 sees a growing near-sine, and the counter may count irregularly. With `CLK_OK` already retriggered,
that can give occasional long SYNC highs (outputs off, §8.3.6) inside the 60 ms soft-start. This is
harmless (m-7); bench item.

## Calculations

- Frequency: 7.3728 MHz/10 = **737.28 kHz**, ±20 ppm (25 °C) ± 30 ppm (−40…85 °C) + 3 ppm/yr
  aging (≈ ±50 ppm, ≈ 40 Hz; m-5). Inside 712–775 kHz with ≥ 3.4 % margin. Beats with 576 kHz: f − 576 = 161 kHz, 2·576 − f =
  415 kHz, 3·576 − 2f = 253 kHz, 2f − 576 = 899 kHz: all ≥ 100 kHz ✓.
- Pulse width 136 ns: ≥ 50 ns ✓; < (1 − DMAX) × TSYNC = (1 − 0.715) × 1.356 µs = 0.39 µs ✓.
- Free-running must stay below the sync frequency: RON 31.6 k / ROFF 14.3 k → tON 1.091 µs,
  tOFF 0.435 µs → 656 kHz nominal, 590–708 kHz (−10/+8 %), always below 737 kHz (4 % margin). The
  ±10/+8 % spread is specified at 75 k/75 k, and the fixed delay terms shift the proportions at these
  values. **Bench: measure the free-running frequency on the first board before relying on sync**
  (n-AB3).
- **DMAX in sync** (n-AB1): the datasheet says the sync edge ends the charge, the discharge follows at
  the same slope, and "DMAX is the same in free-running and synchronized modes", i.e. the RON/ROFF
  value, 0.715. A literal 1 − tOFF/TSYNC reading gives 0.680. The fixed 50/170 ns terms of eq. 11–12
  do not scale, so the truth lies **between 0.680 and 0.715** (±5 % on tOFF: 0.664–0.73).
  Regulation needs 0.655 at 37.6 V ✓. Worst volt-seconds 57 × 0.73/737 kHz = 56 Vµs (47 % cold,
  ≈ 63 % hot) ✓. Shortest SR off-time (1 − 0.73) × 1.356 = 0.37 µs against MIN_TOFF 256 ns ✓.
  Bench check.
- **VREF budget:** SN74LVC1G08 static ≤ 10 µA plus its 737 kHz output into 10 kΩ ∥ the SYNC pin
  (≈ 0.05 mA average) + FB pull-up ≤ 0.5 mA → **≤ 0.6 mA of ≈ 5 mA** ✓. CVREF stays 0.22 µF.
- **`V5_CLK` budget:** 74HC4017 CPD 35 pF × 25 V² × 7.37 MHz → 1.3 mA; LVC1GU04 Pierce: not specified,
  budget 3–8 mA; LVC1G123 ≈ 0.1 mA → ≤ 10 mA from the HT7550 (≥ 60 mA) ✓. Dissipation
  (14.8 − 5) × 10 mA = 0.1 W in SOT-89 ✓.
- Power ≈ 0.14 W from VB_PRI at 14.3 V (≤ 10 mA; in the `B-bias.md` budget).
- **Clock failure, beyond the fallback:** block E measures the converter period from `ACF_PULSE`
  (rule in `B-interfaces.md`) and flags a converter clock fault. A free-running converter can beat with
  576 kHz in the audio band, so the amp mutes.

## Parts

| Part | Supplier line | Datasheet |
|---|---|---|
| SN74LVC1GU04DBVR | `C81934 SN74LVC1GU04DBVR (TI, SOT-23-5): extended, JLC stock 7291, lifecycle normal, checked 2026-11-07` | datasheets/sn74lvc1gu04.pdf |
| 7.3728 MHz crystal, HC-49SMD, −40…+85 °C, CL 20 pF | `C2901749 SXMH7.3728F2020F30 (SCTF, HC-49S-SMD): extended, JLC stock 559, lifecycle normal, checked 2026-11-07` (LCSC params: CL 20 pF, ESR 60 Ω, −40…+85 °C) | datasheets/sctf-sxmh-7m3728.pdf |
| 74HC4017D | `C148206 74HC4017D,653 (Nexperia, SOIC-16): extended, JLC stock 5188, lifecycle normal, checked 2026-11-07` | datasheets/74hc4017-nexperia.pdf |
| SN74LVC1G08DBVR (SYNC gate) | `C7666 SN74LVC1G08DBVR (TI, SOT-23-5): extended, JLC stock 91131, lifecycle normal, checked 2026-11-07` | datasheets/sn74lvc1g08.pdf |
| SN74LVC1G123DCTR (clock-OK one-shot) | `C123302 SN74LVC1G123DCTR (TI, SSOP-8): extended, JLC stock 7685, lifecycle normal, checked 2026-11-07` | datasheets/sn74lvc1g123.pdf |
| HT7550-1 (5 V LDO, SOT-89) | `C16106 HT7550-1 (HOLTEK, SOT-89-3): preferred, JLC stock 184039, lifecycle normal, checked 2026-11-07` | datasheets/ht7550-umw.pdf (UMW second source C347189; Holtek's sheet not on LCSC) |

Replaced: YXC X49SM73728MSD2SC (C2242). LCSC lists it as −20…+70 °C, which fails R-40's 85 °C
(m-AB8). The BAT54S pump is replaced by the LVC1G123 (m-4). HT7550-1 reinstated for `V5_CLK` (MAJOR-2).

## Layout

The clock sits next to the UCC2897A on its GND island (SYNC and VREF are small-signal pins), with the
crystal and its caps tight to the inverter, away from the main-FET drain and T1. VREF decoupling
(0.22 µF) at the pin, plus 100 nF at each logic IC.
