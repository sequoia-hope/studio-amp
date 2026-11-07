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
| VDS | 200 V | forward SR 116 V (42 V in) / freewheel 114 V (57 V in) steady; ringing scaled from PMP20878 → 153 V / 188 V unsnubbed | **needs snubber**; target ≤ 160 V with RC (80 %) |
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

Losses (400 kHz, 50 V): forward SR Irms = Io√D = 0.93 A, freewheel Io√(1−D) = 0.96 A, plus ripple
→ (0.93² + 0.96² + ΔIL²/12) × 0.08 = 0.15 W total conduction; body diode 2 edges × 40 ns × 0.9 V ×
1.34 A × 400 kHz × 2 SRs = 0.08 W; gate (via VSR buck) 2 × 13 nC × 10 V × 400 kHz / 0.85 + IC
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
| VCC | −0.3…37 V (op ≤ 35 V) | VSR = 12 V | OK |
| CS | −4…200 V (dyn −10 V, 200 ns) | SR drain ≤ 160 V with snubber | **depends on snubber**; 188 V unsnubbed is too close |
| DRV | 17 V | 10 V clamp | OK |
| VCC UVLO | 4.0 V on / 3.5 V off | SRs stay off (DRV held low even unpowered) until VSR up; body diodes carry start-up | OK |
| Turn-off threshold | −1…0 mV (true zero current) | diode emulation | R-33 ✓ |
| Turn-on threshold | −120…−40 mV | body diode drop | |
| tPD_OFF | 13 typ / 23 max ns | CCM commutation at main-FET turn-off | OK |
| tPD_ON | 30 typ / 60 max ns | body-diode time budget used in the loss model | |
| fmax | 1 MHz | 400 kHz | OK |

Calculations:
- **MIN_TON** (blanks the turn-on ringing): datasheet: 10 kΩ → 1.0 µs, 50 kΩ → 5.0 µs, 0 Ω →
  55 ns (≈ 100 ns/kΩ). Shortest SR conduction: forward SR D·T = 0.424 × 2.5 µs = 1.06 µs; freewheel
  (1−D)·T = 0.317 × 2.5 = 0.79 µs at DMAX 0.683. Set **3.0 kΩ → ≈ 300 ns** (both).
- **MIN_TOFF** (blanks the turn-off ringing): must end before the next conduction: forward SR off for
  (1−D)T ≥ 0.79 µs, freewheel off for D·T ≥ 1.06 µs. Set **4.3 kΩ → ≈ 430 ns**.
- **Driver loss** (eq. 7: P = VCC × VCLAMP × Cg_ZVS × fsw, i.e. VCC × Qg_ZVS × fsw), Qg_ZVS ≈ 13 nC at 10 V:
  12 V × 13 nC × 400 kHz = 62 mW per controller, most in the IC's clamp (TSOP-6 ≈ 200 °C/W → +12 °C).
  ICC 1.8 mA × 12 V = 22 mW. OK.
- **VCC decoupling**: 1 µF X7R 25 V 0603 at VCC–GND (Kelvin to the SR source).

Fine print:
- GND pin must be Kelvin-connected to the SR source pad (datasheet pin table); CS to the drain at
  the package.
- Light load: the dV/dt detector stops false turn-on on the DCM ringing after the inductor current
  reaches zero (below ≈ 0.45 A output).
- The NCP4306 holds DRV low with no VCC, so the SRs cannot turn on from drain dV/dt before VSR is up.

---

## Snubbers (RC across each SR, drain–source)

Starting values, tuned at bring-up: **47 pF C0G 250 V 0805 + 22 Ω 1206 0.25 W**, footprint also for
an RCD clamp on the freewheel SR (diode + 10 nF + 10 kΩ to GND-referenced clamp, DNP).
- Loss per snubber ≈ C·V²·f = 47 pF × 114² × 400 kHz = 0.24 W; resistor 0.25 W rating marginal →
  **use 2010 0.5 W** (or 2 × 1206 in series).
- The converter-design loss table used 100 pF (pessimistic). If ringing at 47 pF is too high, the
  alternative is less loop inductance (layout), not more C.
- Ringing frequency estimate: Lleak(sec-referred, n² × 0.1 µH = 0.4 µH) with Coss 90 pF + winding C →
  ≈ 20–25 MHz; R ≈ √(L/C) ≈ 50–70 Ω for critical damping: try 22–68 Ω.

Parts (look-ups): 47 pF 250 V C0G 0805 `C340107 CC0805JRNPOYBN470` (99 in stock — enough for 5
boards; alternative 100 pF `C576984 CC0805JRNPOYBN101`, 7823 stock).

## Layout guidance

- Each SR, its NCP4306 and its VCC cap form one cell; NCP4306 GND to the SR source pad, CS to the
  drain pad, DRV trace short, gate return next to it.
- The secondary power loop (T1 secondary → forward SR → GND → freewheel SR → T1) minimal; snubber
  at the SR pins.
- `SW_SEC` is the 114 V high-dV/dt node: small, away from FB/TL431, opto and the INA281.

## Open questions

1. Measure SR Vds peaks at 57 V and full load; must stay < 180 V for the NCP4306 CS pin with margin.
2. 47 pF 250 V C0G stock is thin (99); confirm before ordering or use the 100 pF part.
