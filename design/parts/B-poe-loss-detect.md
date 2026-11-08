# Block B PoE-loss detector — `POE_LOSS_N` (R-32a, R-34)

Lead's decision (2026-11-07): block B owns the secondary-side PoE-loss detector. Output
`POE_LOSS_N`: open-drain, active low, pulled up to +3V3 at the FPGA (block E). Requirements: assert
≤ 10 µs after the converter stops switching; no false trip in pulse-skip (burst/light-load) mode or at
the current-limit hiccup.

## Why not a plain missing-pulse timer

A timer that trips after two missing pulses (5 µs) does trip in normal operation. The UCC2897A skips
pulses (both OUT and AUX, datasheet §8.3.5) whenever VBUS sits above its set-point: after the amp
returns energy (≤ 12.4 mJ → +40 mV), or after a converter load dump (+24 mV). The bulk then
drains at the load current, so the skips last milliseconds (for example 0.24 mC/0.06 A ≈ 4 ms at
minimum load). Gating the timer with "VBUS below set-point" does not work either. In regulation VBUS
*is* the set-point, so no threshold that respects the ±1.5 % set-point tolerance can tell
"regulating" (pulses present) from "slightly above" (skipping). Neither of these signals carries
the primary state.

## Principle used: measure Vin from the pulse amplitude

PoE loss shows up on the primary as `VPRI` falling: the PD bulk (≈ 55 µF) discharges into the
converter until LINEUV stops it at 38.4 V (37.6–39.2 V). During every on-time the secondary switch
node `SW_SEC` (freewheel-SR drain) sits at a plateau of n·Vin − drops = 2·Vin − ≈ 0.5 V. **A pulse
whose plateau is below the 2 × 40.4 V threshold means the PoE input is collapsing.** The circuit
asserts on the first such pulse. That is *before* switching stops, so the ≤ 10 µs requirement is met
with margin. The circuit ignores missing pulses entirely, so skips, bursts and hiccups cannot trip it.

## Circuit

All on the secondary, supplied from block C's +3V3 (it stays up while VBUS holds, R-34):

1. **Divider** from `SW_SEC`: Rtop 2 × 100 k 0.1 % 0805 in series (200 k; 114 V plateau + 190 V
   ringing peaks shared by two parts), Rbot 6.42 k 0.1 % → node `SWDIV` (ratio 1/32.15).
   No added capacitor: τ ≈ 6.2 k × ≈ 3 pF ≈ 20 ns.
2. **Reference**: TL431BIDBZR (C41283, already in `B-feedback.md`) as a 2.495 V shunt, fed from +3V3
   through 680 Ω (1.18 mA ≥ 1 mA minimum). A 4.02 k / 1.00 k divider from it gives 0.497 V.
3. **TLV3202 dual comparator, push-pull, 40 ns** (inputs through 10 k series resistors for
   overvoltage current limiting):
   - CMP-P: `SWDIV` > 0.497 V → **P** = "pulse present" (SW_SEC > 16 V). Also brought out as
     `ACF_PULSE` (3.3 V push-pull, through 100 Ω) for FPGA diagnostics.
   - CMP-L: 2.495 V > `SWDIV` → **L** = "plateau low" (SW_SEC < 80.2 V).
4. **SN74LVC1G08** AND: **LA = P · L** = "a pulse is on, and it is too low".
5. **Qualifier** RC: 1.50 k + 220 pF (τ = 330 ns) into the Schmitt B input of an **SN74LVC1G123**
   retriggerable monostable. The edge transients of every normal pulse (P rises before L falls) and
   the plateau ringing are much shorter than the RC delay, so they never reach the Schmitt threshold.
6. **Monostable**: Rext 100 k / Cext 100 nF, A tied low, CLR high → Q high for ≈ 10 ms after the last
   qualified low pulse (retriggerable). Q drives a **2N7002**, whose drain is `POE_LOSS_N`
   (open-drain to the FPGA's +3V3 pull-up). The FPGA latches the first edge (block E).

## Calculations

**Threshold (Vin at the PD after the bridges):**
SW_SEC threshold = 2.495 V × 206.42 k/6.42 k = 80.22 V. Plateau = 2·Vin − (2 × Ipri·(Rds + Rcs) ≈
0.4 V) − forward-SR drop (≈ 0.1 V) ≈ 2·Vin − 0.5 V → **Vin threshold 40.36 V**.
Tolerance: TL431B ±0.5 % (+ ≈ 0.5 % over temperature), dividers 0.1 % each, TLV3202 VIO ≤ 6 mV
(0.24 %), drop estimate ±0.3 V (0.4 %) → ±1.6 % → **39.7–41.0 V**.
- Above LINEUV off (37.6–39.2 V, `B-controller.md`), so a collapsing input always produces
  low-amplitude pulses before the converter stops ✓.
- Below the 41.1 V Class 8 PD minimum and the 42 V lower operating limit of R-30, so normal
  operation never asserts it ✓ (margin 0.1 V on the worst unit at 41.1 V).

**Lead time before the stop:** at full load the PD bulk falls at P/(C·V) = 70 W/(55 µF × 40 V)
≈ 32 V/ms. The gap from the detector threshold to LINEUV off is ≥ 0.5 V (worst corners), i.e.
≥ 16 µs and ≈ 12 pulses at 737 kHz. At light load the decay is slower (≈ 0.24 V/ms at 0.6 W), giving
hundreds of pulses. **POE_LOSS_N therefore asserts before switching stops at every load** at which
the converter delivers pulses ≥ 0.45 µs long (below).

**Latency from the first low pulse:** divider τ 20 ns + input RC (10 k × 2 pF) 20 ns + CMP 40 ns +
AND 5 ns + qualifier 165–307 ns (Schmitt VT+ 1.3–2.0 V at 3.3 V: t = τ·ln(3.3/(3.3 − VT+))) +
monostable ≈ 10 ns + 2N7002 ≈ 20 ns → **≤ 0.42 µs**.

**Minimum low-pulse width that is detected:** about 0.45 µs (qualifier plus the SWDIV settling
near threshold). At Vin ≈ 40 V in CCM, D ≈ 0.6 → 0.81 µs at 737 kHz ✓. In DCM at light load (Io ≈ 0.06 A),
pulses are ≈ 0.31 µs at 737 kHz, below the 0.45 µs needed. In that case PD_PG through block A's isolator (R-32a's other source)
and the slow decay at light load cover it. Recorded as a limitation.

**Normal pulses must not qualify:** with τ ≈ 40 ns, `SWDIV` crosses the 2.495 V threshold from zero
in τ·ln(Vf/(Vf − 2.495)). At the lowest normal plateau (Vin 41.1 V → Vf = 2.540 V) that is
40 ns × ln(56) = 160 ns, plus the 40 ns of P leading L, against a qualifier ≥ 165 ns. At 42 V
(Vf 2.596 V) it is 130 ns ✓. Between 41.1 and 41.5 V the margin is thin; any trip there is an
early warning of a really marginal input (all inside the 39.7–41.0 V band ± a few %). Plateau
ringing (≈ 20–25 MHz, troughs < 25 ns) can glitch L, but the 330 ns RC integrates glitches to
≤ 0.9 V < VT+ min 1.3 V ✓.

**Divider power:** (2·Vin)²/206 k × D: 114² / 206 k × 0.42 = 26 mW, 13 mW per 100 k resistor ✓.
Each 100 k (0805, 150 V element rating) sees ≤ 95 V of the 190 V ringing peak ✓.
**Input protection:** at 190 V peaks `SWDIV` reaches 5.9 V. Through the 10 k series resistors,
≤ 0.26 mA flows into the TLV3202's input ESD diodes to the 3.3 V rail; the rail absorbs it.

**Monostable width:** ≈ K·Rext·Cext. K is about 1 from the datasheet's pulse-duration-constant figure;
that is a graph, not read numerically. 100 k × 100 nF ≈ 10 ms. The width is not critical because the
FPGA latches the edge.

## Behaviour by case

| Case | Result |
|---|---|
| PoE removed or PSE drops power (any load ≥ ≈ 0.45 A, or lighter with ≥ 0.45 µs pulses) | asserts before switching stops ✓ |
| Converter skipping (VBUS above set-point: regen, load dump, light load) | no pulses → nothing to qualify → no trip ✓ |
| CC current limit (secondary loop) | pulses continue at full amplitude → no trip ✓ |
| Primary current-limit hiccup (short), output-OVP hiccup (LINEOV) | pulses stop at normal Vin → no trip. Reported separately: `ACF_PULSE` absent plus VBUS from block D's ADC, if firmware wants it |
| PD foldback or abrupt PG drop at normal Vin (UCC2897A stopped via SS/SD) | not detected here → `PD_PG` via block A's isolator |
| Start-up with Vin between LINEUV on (40.4 V) and the threshold (≤ 41.0 V) | can assert during soft-start; firmware ignores POE_LOSS_N until VBUS is valid (amp muted, R-34) |

## Parts

| Ref | Part | Supplier line |
|---|---|---|
| Comparator | TLV3202AIDGKR, dual, push-pull, 40 ns, 2.7–5.5 V, VIO ≤ 6 mV (datasheets/tlv3202.pdf) | `C478075 TLV3202AIDGKR (TI, VSSOP-8): extended, JLC stock 2290, lifecycle normal, checked 2026-11-07` |
| AND gate | SN74LVC1G08DBVR (datasheets/sn74lvc1g08.pdf) | `C7666 SN74LVC1G08DBVR (TI, SOT-23-5): extended, JLC stock 91131, lifecycle normal, checked 2026-11-07` |
| Monostable | SN74LVC1G123DCTR, retriggerable, Schmitt A/B inputs (datasheets/sn74lvc1g123.pdf) | `C123302 SN74LVC1G123DCTR (TI, SSOP-8): extended, JLC stock 7685, lifecycle normal, checked 2026-11-07` |
| Reference | TL431BIDBZR | `C41283 … (149263, normal)`, see `B-feedback.md` |
| Output FET | 2N7002 | `C8545 2N7002 (JSCJ, SOT-23): basic, JLC stock 5965601, lifecycle normal, checked 2026-11-07` |
| Divider | 2 × 100 k + 6.42 k, 0.1 % 0805/0603 thin film | generic, picked with the passive list |

BAT54S (C47546) was considered as an input clamp and not used: its ≈ 10 pF would slow `SWDIV` (see
"Normal pulses must not qualify"). Its datasheet was fetched (datasheets/bat54s-nexperia.pdf).

## Layout guidance

- Take `SW_SEC` from the freewheel-SR drain pad. Place the 200 k top resistors at the SR. Run the
  low-voltage `SWDIV` trace short to the comparator, over the secondary GND, away from the switch
  node copper.
- Comparator, gate and monostable next to each other. 100 nF decoupling at each. Cext at the
  1G123's pins.

## Open questions

1. Plateau drop (≈ 0.5 V) and ringing are estimates; check `SW_SEC` at Vin 40–42 V on the bench and
   trim Rbot if needed.
2. The light-load DCM pulse-width limitation is covered by `PD_PG`. Block E should OR the two.
