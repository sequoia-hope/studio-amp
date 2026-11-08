# SUPERSEDED — Block B PoE-loss detector, version 2 (primary pulse height) — kept for the record

> **Superseded 2026-11-08 by `B-vbus-droop.md`** (lead decision after the third-pass review,
> `design/gates/rereview2-phase1.md` BLOCKER-1: leading-edge race between the TLV3201 delay/input C
> and the LVC1G123 thresholds at low line; MAJOR-1: coverage). Nothing below is built, except the
> `ACF_PULSE` path (DRV_FWD divider + 74LVC2G08 gate B), which `B-vbus-droop.md` keeps.

# (old) Block B PoE-loss detector — `POE_LOSS_N` (R-32a, R-34)

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

## Principle used: measure Vin from the plateau, but only while the forward SR conducts

PoE loss shows up on the primary as `VPRI` falling: the PD bulk (≈ 55 µF) discharges into the
converter until LINEUV stops it at 38.4 V (37.6–39.2 V). **While the forward SR conducts**, the
secondary switch node `SW_SEC` (freewheel-SR drain = output-inductor input) sits at
n·Vin − drops = 2·Vin − ≈ 0.5 V. A conduction pulse whose plateau is below the threshold (2 × 40 V)
means the PoE input is collapsing, and the circuit asserts on the first such pulse, *before* switching
stops.

**Second-pass review AB-B1 (BLOCKER), fixed here.** The first version qualified "pulse present" by the
level SW_SEC > 16 V. But whenever both SRs are off with zero inductor current (every DCM dead time,
and the whole of every pulse-skip interval), SW_SEC rests at **VBUS ≈ 48 V** through the inductor.
That read as "a pulse whose plateau is too low", so the detector fired continuously at amplifier
idle. "Pulse present" is now the **forward-SR gate drive** `DRV_FWD` (NCP4306 DRV of the forward SR):
- it is high only while the forward SR conducts, i.e. during a real transformer on-time (NCP4306
  turns on at −75 mV Vds, off at 0 mV, p.7–8; DRV held low with VCC absent);
- it is low in every DCM dead time (the forward SR is reverse-biased by the transformer reset
  voltage, then has no current), in the whole of every skip interval (no pulses) and in a hiccup;
- the NCP4306 "D" variant's dV/dt detector stops turn-on on the DCM ring, and MIN_TON (125 ns)
  blanks re-triggering within a pulse. So there is **exactly one DRV pulse per real conduction pulse**.

## Circuit

All on the secondary, supplied from block C's +3V3 (it stays up while VBUS holds, R-34):

1. **`SW_SEC` divider**: Rtop 2 × 100 k 0.1 % 0805 in series (200 k; 114 V plateau and 190 V ringing
   peaks shared by two parts), **Rbot 6.49 k** 0.1 % → `SWDIV` (ratio 1/31.82). No added capacitor:
   τ ≈ 6.3 k × ≈ 3 pF ≈ 20 ns.
2. **`DRV_FWD` divider**: forward-SR NCP4306 DRV → 10.0 k → node `P′` → 4.99 k → GND: 10 V → 3.33 V
   (VDRVMAX 11 V → 3.66 V, inside the LVC inputs' 5.5 V tolerance, powered or not, Ioff). Load on
   DRV ≈ 0.7 mA, negligible against the 2 A driver.
3. **Reference**: TL431BIDBZR (C41283, as in `B-feedback.md`) as a 2.495 V shunt from +3V3 through
   680 Ω (1.18 mA).
4. **TLV3201** single comparator, push-pull, 40 ns (inputs through 10 k series resistors): 2.495 V >
   `SWDIV` → **L** = "plateau low" (SW_SEC < 79.4 V). The second comparator of the old TLV3202 is
   no longer needed.
5. **SN74LVC2G08** dual AND (VCC +3V3):
   - gate A: **LA = P′ · L** = "the forward SR is conducting, and the plateau is too low";
   - gate B: **`ACF_PULSE` = P′ · 1** (other input tied to +3V3), a clean 3.3 V copy of the forward-SR
     conduction, exactly one rising edge per real pulse (AB-M3). Block E's single 4.7 kΩ series
     resistor sits at FPGA B6.
6. **Qualifier** RC: **1.50 k + 330 pF (τ = 495 ns)** into the Schmitt B input of an
   **SN74LVC1G123** retriggerable monostable.
7. **Monostable**: Rext 100 k / Cext 100 nF, A tied low, CLR high → Q high for ≈ 10 ms after the last
   qualified low pulse. Q drives an **AO3400A** (VGS(th) 0.65–1.45 V, RDS(on) < 48 mΩ at VGS 2.5 V;
   E+F review MINOR-2), whose drain is `POE_LOSS_N` (open-drain to the FPGA's +3V3 pull-up). The
   FPGA latches the falling edge (block E).

## Calculations

**Threshold (VPRI, after the bridges; m-AB7 re-centred):**
SW_SEC threshold = 2.495 V × 206.49 k/6.49 k = 79.38 V. Plateau = 2·Vin − (2 × Ipri·(Rds + Rcs) ≈
0.4 V) − forward-SR drop (≈ 0.1 V) ≈ 2·Vin − 0.5 V → **VPRI threshold 39.94 V**.
Tolerance: TL431B ±0.5 % (+ ≈ 0.5 % over temperature), dividers 0.1 % each, TLV3201 VIO ≤ 6 mV
(0.24 %), drop estimate ±0.3 V (0.4 %) → ±1.6 % → **39.3–40.6 V at VPRI**.
- Above LINEUV off (37.6–39.2 V), so a collapsing input always produces low-plateau conduction pulses
  before the converter stops ✓ (worst-corner gap 0.1 V; nominal gap 1.5 V).
- Below a compliant Class 8 PI minimum of 41.1 V less bridge and jack drops (≈ 41.0 V at VPRI) by
  ≥ 0.4 V, and below R-30's 42 V operating minimum ✓.

**Lead time before the stop:** at full load the PD bulk falls at P/(C·V) = 70 W/(55 µF × 40 V) ≈
32 V/ms; from the nominal threshold (39.9 V) to nominal LINEUV off (38.4 V) is 1.5 V = 47 µs ≈ 35
pulses (worst corners 0.1 V ≈ 3 µs ≈ 2 pulses). At light load the decay is ≈ 0.24 V/ms and there
are hundreds of pulses. **POE_LOSS_N asserts before switching stops** at every load where the
forward-SR conduction lasts ≥ 0.46 µs (below).

**Leading edge, must not qualify normal pulses:** at the start of an on-time `SW_SEC` rises to the
plateau in ≈ 20 ns; `SWDIV` (τ ≈ 40 ns incl. the 10 k input RC) crosses the threshold from zero in
τ·ln(Vf/(Vf − 2.495)). At the lowest normal plateau (VPRI 41.0 V → Vf = 2.561 V) that is
40 ns × ln(38.8) = 146 ns; at 42 V (Vf 2.624 V) 120 ns. DRV_FWD rises 30–60 ns after the forward
SR's body diode starts conducting (tPD_ON, p.7), so P′·L overlaps for **≤ 146 − 30 = 116 ns**.
The qualifier needs τ·ln(3.3/(3.3 − VT+)) = 495 ns × (0.50 … 0.93) = **248–460 ns** (Schmitt VT+
1.3–2.0 V at 3.3 V) ✓, a 2.1× margin.
**Trailing edge:** at main-FET turn-off the forward-SR current commutates to the freewheel SR in
≈ Lleak(sec)·I/V = 0.4 µH × 1.5 A/100 V ≈ 6 ns. DRV_FWD follows 13–23 ns later (tPD_OFF), so the
overlap with `SW_SEC` falling is ≤ ≈ 50 ns ✓.
**Plateau ringing** (≈ 20–25 MHz, troughs < 25 ns) can glitch L, but the 495 ns RC integrates the
glitches to ≪ VT+ ✓.

**Detection (low plateau):** P′·L high for the whole conduction time minus ≈ 45 ns. At VPRI ≈ 40 V in
CCM, D ≈ 0.6 → 0.81 µs at 737 kHz → 0.77 µs ≥ 0.46 µs ✓. At light load in DCM the on-time shrinks
(≈ 0.23–0.31 µs at Io ≈ 0.06 A), below 0.46 µs, so no detection there. `PD_PG_N` (block A's
isolator, R-32a's other source) and the slow decay at light load cover it. Recorded as a limitation.

**Latency from the first low pulse:** 248–460 ns qualifier + LVC 5 ns + monostable ≈ 10 ns +
AO3400A ≈ 20 ns → **≤ 0.5 µs**.

**Divider power:** (2·Vin)²/206 k × D: 114²/206 k × 0.42 = 26 mW, 13 mW per 100 k resistor ✓; each
100 k (0805, 150 V) sees ≤ 95 V of the 190 V ringing peak ✓.
**Input protection (n-AB5):** at 190 V peaks `SWDIV` reaches 6.0 V. Through the 10 k series
resistor ≤ 0.27 mA flows into the TLV3201's input clamp (datasheet: limit to 10 mA) ✓. Before +3V3 is
up it injects ≤ 0.4 mA into the unpowered rail, which is harmless.

**Monostable width:** ≈ K·Rext·Cext with K ≈ 1 (datasheet figure; a graph, not read numerically)
→ ≈ 10 ms; not critical because the FPGA latches the edge.

## Behaviour by case (load 0 to full)

| Case | DRV_FWD | Plateau | Result |
|---|---|---|---|
| Normal CCM, VPRI ≥ 41 V | high during each on-time | ≥ 81.5 V → L = 0 | no trip ✓ |
| Light load / DCM, any VPRI ≥ 41 V | high only during on-time; low in the dead time while SW_SEC rests at VBUS | L = 0 during conduction | no trip ✓ (the AB-B1 case) |
| Pulse skip (light/no load, VBUS above set-point after regen or load dump) | low (no pulses) | SW_SEC = VBUS | no trip ✓ |
| Burst / regen into VBUS | skip → low | — | no trip ✓ |
| CC current limit (secondary loop) | normal pulses | full plateau | no trip ✓ |
| Primary cycle-by-cycle limit / hiccup, LINEOV OVP hiccup | pulses short or stopped, plateau full | L = 0 | no trip ✓ (converter fault seen via `ACF_PULSE` and VBUS) |
| Start-up before VSR (VBUS < 7.5 V) | NCP4306 unpowered, DRV low | — | no trip (detector blind; amp muted anyway) |
| PoE removed / PSE drops power, CCM | high | falls below 79.4 V | **asserts ≥ 1 pulse before LINEUV stops switching** ✓ |
| PoE removed at light load (DCM on-time < 0.46 µs) | short | low | may not assert → `PD_PG_N` rising covers it |
| PD fold-back or PG drop at normal VPRI | stops | full | not detected here → `PD_PG_N` rising covers it |
| Start-up with VPRI between LINEUV on (40.4 V) and the threshold band (≤ 40.6 V) | normal | near threshold | can assert during soft-start; firmware ignores `POE_LOSS_N` until VBUS is valid |

Bench cases (added, AB-B1): light-load DCM at 57 V in; skip after a regen step into VBUS; VPRI ramped
down slowly at 10 %, 50 % and 100 % load; PSE disconnect at full load (assertion time against the
LINEUV stop).

## Parts

| Ref | Part | Supplier line |
|---|---|---|
| Comparator | TLV3201AIDBVR, single, push-pull, 40 ns, 2.7–5.5 V, VIO ≤ 6 mV (datasheets/tlv3202.pdf covers TLV3201/3202) | `C105188 TLV3201AIDBVR (TI, SOT-23-5): extended, JLC stock 15490, lifecycle normal, checked 2026-11-07` |
| Dual AND | 74LVC2G08DP (inputs 5.5 V tolerant, Ioff) | `C406037 74LVC2G08DP,125 (Nexperia, TSSOP-8): extended, JLC stock 56760, lifecycle normal, checked 2026-11-07` |
| Monostable | SN74LVC1G123DCTR, retriggerable, Schmitt A/B inputs (datasheets/sn74lvc1g123.pdf) | `C123302 SN74LVC1G123DCTR (TI, SSOP-8): extended, JLC stock 7685, lifecycle normal, checked 2026-11-07` |
| Reference | TL431BIDBZR | `C41283 TL431BIDBZR (TI, SOT-23-3): extended, JLC stock 149263, lifecycle normal, checked 2026-11-07` |
| Output FET | AO3400A (datasheets/ao3400a.pdf). Load on `POE_LOSS_N` ≈ 1.37 mA (block E's 4.7 k pull-up + block F's BAT54C diodes): VOL ≤ 1.37 mA × 48 mΩ ≈ 0.07 mV at VGS 3.3 V | `C20917 AO3400A (AOS, SOT-23): basic, JLC stock 1065196, lifecycle normal, checked 2026-11-07` |
| Dividers | 2 × 100 k + 6.49 k (0.1 %), 10.0 k + 4.99 k (1 %) | generic, picked with the passive list |

Removed: TLV3202 (second comparator no longer used), SN74LVC1G08 (replaced by the dual LVC2G08).

## Layout guidance

- Take `SW_SEC` from the freewheel-SR drain pad, with the 200 k top resistors at the SR. Take
  `DRV_FWD` at the forward-SR gate resistor (the NCP4306 side), with the 10 k at the source. Run both
  low-voltage nodes short to the comparator and gate, over the secondary GND, away from the switch-node
  copper.
- Comparator, gates and monostable next to each other, with 100 nF decoupling at each and Cext at
  the 1G123's pins.

## Open questions

1. The plateau drop (≈ 0.5 V) and the ringing are estimates; check `SW_SEC` at VPRI 40–42 V on the
   bench and trim Rbot if needed.
2. The light-load DCM limitation is covered by `PD_PG_N`; block E ORs the two
   ("`PD_PG_N` rising or `POE_LOSS_N` falling ⇒ PoE lost").
