# Block B secondary rectification — 2 × BSC500N20NS3 G SR MOSFETs, 2 × NCP4306 SR controllers, snubbers

Converter numbers from `B-converter-design.md`. Both SRs are low-side (sources on secondary `GND`):
the forward SR between the T1 secondary "bottom" and GND, the freewheel SR between the
secondary switch node `SW_SEC` (T1 top / output-inductor input) and GND. Each SR has its own NCP4306,
which turns it off at zero drain current, so **current cannot reverse (R-33)**.

---

## Q (SR fwd, SR fw) — Infineon BSC500N20NS3 G, N-channel 200 V, 50 mΩ, PG-TDSON-8

Datasheet: datasheets/bsc500n20ns3.pdf (Infineon OptiMOS 3). Read: all.
Supplier: `C5381902 BSC500N20NS3GATMA1 (Infineon, TDSON-8): extended, JLC stock 2986, lifecycle normal, checked 2026-11-07`
Footprint: PG-TDSON-8 (SuperSO8 5 × 6), marking 500N20NS.

| Parameter | Datasheet | Our worst case | Margin |
|---|---|---|---|
| VDS | 200 V | forward SR **137 V at 38.4 V, 143 V at the 37.6 V LINEUV-off corner**, 84 V at 57 V; freewheel 114 V at 57 V (steady); with ringing (PMP20878 +22–65 %) 167–189 V unclamped | **RCD-Z clamp on both SRs (baseline, review M4) → ≤ ≈ 165 V (83 %)** |
| VGS | ±20 V | 10 V (NCP4306 "A" clamp) | OK |
| RDS(on) | 42 typ / 50 max mΩ at 10 V | 80 mΩ hot | |
| VGS(th) | 2–4 V | 10 V drive ✓ | |
| Qg | 15 typ / 20 max nC (0–10 V, hard-switched) | ZVS: ≈ 13 nC (Qg − Qgd 2 nC) | |
| Coss / Qoss | 90 pF at 100 V / 35 nC | sets snubber need | |
| VSD | 0.9 V | body diode during NCP4306 turn-on delay | |
| RθJA | 50 °C/W (6 cm² cooling area) | 0.15 W each → +8 °C | OK |

Why 200 V and not 150 V: PMP20878 (n = 1, 24 V out) measured its 150 V SRs at 90–94 V; our stress
is 2× (n = 2, 48 V), so a 150 V part would ring past its rating. Current is low (1.34 A), so the
higher Rds of a 200 V part costs little.
Alternative checked: BSC320N20NS3 G (C501501, 755 stock, 32 mΩ, Qg 22 nC, Qrr 429 nC): more gate
charge for conduction loss we don't have.

Losses (737 kHz, 50 V): forward SR Irms = Io√D = 0.93 A, freewheel Io√(1−D) = 0.96 A, plus ripple
→ (0.93² + 0.96² + ΔIL²/12) × 0.08 = 0.15 W total conduction; body diode 2 edges × 40 ns × 0.9 V ×
1.34 A × 737 kHz × 2 SRs (30 ns per edge: 0.10 W); gate (via VSR buck) 2 × 13 nC × 10 V × 737 kHz / 0.85 + IC
= 0.16 W.

---

## U (SR ctrl ×2) — onsemi NCP4306DADZZDASNT1G, TSOP-6

Datasheet: datasheets/ncp4306.pdf (NCP4306/D rev. 6, March 2020). Read: all.
Supplier: `C504885 NCP4306DADZZDASNT1G (onsemi, TSOP-6-1.5mm): extended, JLC stock 2143, lifecycle normal, checked 2026-11-07`
Footprint: TSOP-6 (case 318G-02).

Variant decoding (datasheet ordering table and EC table "ver." notes): **D** = TSOP-6 pin-out D
(1 DRV, 2 GND, 3 CS, 4 MIN_TON, 5 MIN_TOFF, 6 VCC; no LLD, no TRIG); **A** = 10 V driver clamp
(VDRVMAX 9–11 V), ICC 1.8 mA; **D** = dV/dt ringing detector (DCM ringing, "flyback feature");
**ZZ** = MIN_TON and MIN_TOFF set by external resistors. Rejected: DAHZZAA (C603725, 5325 stock),
"H" = LLC exception timer, not needed for a forward converter.
Datasheet: "can be used in various topologies such as DCM or CCM flyback, quasi resonant flyback,
forward and half bridge resonant LLC"; "extremely fast turn-off comparator … allows CCM
applications without any additional components or external triggering".

| Parameter | Abs max / spec | Our case | Margin |
|---|---|---|---|
| VCC | −0.3…37 V (op ≤ 35 V) | VSR = 10 V (7 V in dropout at start-up) | OK |
| CS | −4…200 V (dyn −10 V, 200 ns) | = SR drain; ≤ ≈ 165 V with the RCD-Z clamp (worst: SMBJ130A at 159 V VBR max + a few V dynamic) | 83 % of abs max |
| DRV | 17 V | 10 V clamp | OK |
| VCC UVLO | 4.0 V on / 3.5 V off | SRs stay off (DRV held low even unpowered) until VSR up; body diodes carry start-up | OK |
| Turn-off threshold | −1…0 mV (true zero current) | diode emulation | R-33 ✓ |
| Turn-on threshold | −120…−40 mV | body diode drop | |
| tPD_OFF | 13 typ / 23 max ns | CCM commutation at main-FET turn-off | OK |
| tPD_ON | 30 typ / 60 max ns | body-diode time budget used in the loss model | |
| fmax | 1 MHz | 737.28 kHz synced (590–708 kHz if the clock fails) | OK |

Calculations (737.28 kHz, T = 1.356 µs; synced DMAX 0.664–0.73 (n-AB1); also checked at clock-failed 590 kHz):
- **MIN_TON** (blanks the turn-on ringing): datasheet: 0 Ω → 55 ns, 10 kΩ → 1.0 µs, 50 kΩ → 5.0 µs
  (≈ 95 ns/kΩ above the 55 ns floor). Kept **short to limit reverse current in deep DCM (review m4)**:
  **0.75 kΩ → ≈ 125 ns**. That still blanks 2–3 periods of the 20–25 MHz turn-on ring. Reverse current
  held by MIN_TON is ≤ Vo/Lo × 125 ns = 0.09 A peak, ≈ 6 nC per cycle, only in deep DCM
  (`B-converter-design.md`, light load). Shortest required conduction: forward SR D·T = 0.424 × 1.356
  = 0.575 µs; freewheel (1 − 0.73) × 1.356 = 0.37 µs ✓ (MIN_TON 126 ns is ≤ 34 % of it).
- **MIN_TOFF** (blanks the turn-off ringing): must end before the next conduction. Forward SR is off
  for (1−D)·T ≥ 0.37 µs, freewheel for D·T ≥ 0.575 µs. Set **2.0 kΩ → ≈ 256 ns** (70 + 2.0 × 93 ns,
  n-AB7), ≈ 110 ns margin to 0.37 µs.
- **Driver loss** (eq. 7: P = VCC × VCLAMP × Cg_ZVS × fsw, i.e. VCC × Qg_ZVS × fsw), Qg_ZVS ≈ 13 nC at
  the 10 V clamp: 10 V × 13 nC × 737 kHz = 96 mW per controller, most of it in the IC's clamp
  (TSOP-6 ≈ 200 °C/W → +19 °C). ICC 1.8 mA × 10 V = 18 mW. OK.
- **VCC decoupling**: 1 µF X7R 25 V 0603 at VCC–GND (Kelvin to the SR source).

Fine print:
- GND pin must be Kelvin-connected to the SR source pad (datasheet pin table); CS to the drain at
  the package.
- Light load: the dV/dt detector stops false turn-on on the DCM ringing after the inductor current
  reaches zero (below ≈ 0.17–0.28 A output at 737 kHz).
- LLD: position 6 of the part number, "D", is the internal 540 µs light-load-detect timer (p.39
  Table 6; review n7). It is harmless: conduction happens every 1.36 µs, and in pulse-skip the first
  pulse after a sleep goes through the body diode.
- The NCP4306 holds DRV low with no VCC, so the SRs cannot turn on from drain dV/dt before VSR is up.

---

## Snubbers and clamps (both SRs, revised for review M4, m5, m8)

**Baseline, fitted on both SRs:**

1. **RC snubber** drain–source: **22 pF C0G 250 V 0805 + 2 × 22 Ω 2010 (0.5 W) in series (44 Ω)**.
   - Loss C·V²·f per SR at 737 kHz: forward 22 pF × 143² × 737 kHz = **0.33 W** (worst, 37.6 V
     corner; 0.14 W at 50 V); freewheel 22 pF × 114² × 737 kHz = **0.21 W** at 57 V. Each resistor
     carries half, ≤ 0.17 W, against 0.5 W rated (≈ 0.4 W at 85 °C board temperature) ✓ (review
     m8; 1206 would have been at 85 % of its derated rating at 737 kHz).
   - Damping: Lleak(sec) ≈ n² × 0.1 µH = 0.4 µH with Coss 90 pF + 22 pF + winding C → ≈ 20–25 MHz;
     √(L/C) ≈ 55–60 Ω, so 44 Ω is near critical. Tune 22–68 Ω on the bench.
2. **RCD-Z clamp** from the SR drain: **US1G** (400 V, 1 A, trr 50 ns) → node K → **10 nF 250 V X7R
   1206** to GND ‖ **SMBJ130A** to GND (VWM 130 V, VBR 144–159 V at 1 mA, IR 1 µA, VC 209 V at 2.9 A).
   - Node K charges to the ring peaks and is held at the TVS breakdown, so the SR drain, and the NCP4306
     CS pin, stays ≤ VBR + a few volts ≈ **150–165 V (≤ 83 % of 200 V)** from the first power-up,
     before any snubber tuning.
   - It does not touch normal operation: the freewheel plateau is 114 V and the forward plateau is
     ≤ 137 V at 38.4 V (VWM 130 V; IR ≤ 1 µA at 130 V). Only at the 37.6 V worst corner (143 V,
     forward SR) does it sit just under VBR min, conducting ≤ 1 mA → ≤ 0.14 W, and only in the last
     0.8 V before LINEUV stops the converter.
   - Energy: worst-case ring energy per edge ½ × 0.4 µH × (2 A)² = 0.8 µJ (review n12, a few amps of
     commutation overshoot); most of it goes to the RC. If all of it reached the clamp it would be
     0.6 W per SR at 737 kHz. The SMBJ datasheet gives no steady-state power rating, so check the TVS
     temperature at bring-up. The TVS footprint also takes a 22 k 2010 resistor (RCD bleed to GND,
     ≈ 150²/22 k = 1 W, only if the TVS runs hot) as an alternative.
   - Diode reverse voltage: node K (≤ 165 V) minus drain at 0 V → 165 V on a 400 V US1G ✓.
3. The converter loss table carries 22 pF RC + 0.1 W for the clamps (`B-converter-design.md`).

Parts:
- 22 pF 250 V C0G 0805: `C90626 CC0805JRNPOYBN220 (YAGEO, 0805): extended, JLC stock 5842, lifecycle normal, checked 2026-11-07` (datasheets/yageo-cc0805-npo-250v.pdf)
- US1G: `C383015 US1G (Jingdao Microelectronics, SMA): extended, JLC stock 358486, lifecycle normal, checked 2026-11-07` (datasheets/us1g-jingdao.pdf)
- 10 nF 250 V X7R 1206: `C913956 1206B103K251NT (FH, 1206): extended, JLC stock 7829, lifecycle normal, checked 2026-11-07`
- SMBJ130A: `C553984 SMBJ130A-E3/52 (VISHAY, SMB(DO-214AA)): extended, JLC stock 3085, lifecycle normal, checked 2026-11-07` (datasheets/smbj130a-vishay.pdf)
- (The 47 pF part, C340107 with only 99 in stock, is dropped.)

## Layout guidance

- Each SR, its NCP4306 and its VCC cap form one cell; NCP4306 GND to the SR source pad, CS to the
  drain pad, DRV trace short, gate return next to it.
- The secondary power loop (T1 secondary → forward SR → GND → freewheel SR → T1) minimal; snubber
  at the SR pins.
- `SW_SEC` is the 114 V high-dV/dt node: small, away from FB/TL431, opto and the INA281.

## Open questions

1. Measure SR Vds peaks at 57 V and at 38.4 V, full load; clamp node temperature and TVS dissipation.
2. If the clamps run hot, the RC snubber needs more C (loss rises with C·V²·f) or the layout less loop
   inductance.

## Phase 2 schematic notes (iso_dcdc, 2026-11-08)

- **Snubber resistor changed:** one **47 Ω 5 % 2512 1 W** (UNI-ROYAL 25121WJ0470T4E,
  `C15261`) per SR replaces the 2 × 22 Ω 2010 pair (44 Ω). Worst loss 0.33 W (forward SR, 37.6 V
  corner) is 33 % of the 1 W rating; damping 47 Ω is still near the 55–60 Ω critical value. Saves
  two parts per board and keeps iso_dcdc inside its R201–R249 range.
- NCP4306 symbol made in `lib/studio_B` (pins from Table 2 p.4: 1 DRV, 2 GND, 3 CS, 4 MIN_TON,
  5 MIN_TOFF, 6 VCC); CS is drawn on the right beside DRV. Footprint: KiCad `SOT-23-6` (TSOP-6,
  case 318G, same 0.95 mm pitch land).
- BSC500N20NS3 G uses KiCad `Infineon_PG-TDSON-8_6.15x5.15mm` (exact package).
