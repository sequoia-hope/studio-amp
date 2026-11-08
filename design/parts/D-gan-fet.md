# Q (×8) — power-stage GaN FET: Infineon IGB070S10S1 (CoolGaN 100 V G3, 7 mΩ) — **user decision 2026-11-08**, at fsw 576 kHz

Datasheet: datasheets/igb070s10s1.pdf (Final datasheet, Rev 1.0, 2025-01-27). Read: all sections; diagrams 9–16 rendered and read off the curves; footprint Fig. 2 p.14.
MPN: IGB070S10S1XTMA1. Supplier: `C44179579 IGB070S10S1XTMA1 (Infineon, PG-TSON-4-2): extended, JLC stock 80, lifecycle normal, checked 2026-11-07`.
**Order early: 8 per board × 5 boards = 40, + 10 % attrition = 44 needed, against 80 in stock (1.8×). Reserve or buy ≈ 50 now.** Fallback IGC033S10S1 (C41381300, 985 in stock), analysed in the second section of this file.
History: IGB070 was recommended on 2026-11-07; the user chose IGC033 for stock; on 2026-11-08 the user reverted to IGB070 to cut idle loss at the 576 kHz baseline (block E's ×12 FPGA grid).

## Footprint: one land pattern or two?
**Two land patterns are needed.**
- IGB070S10S1: PG-TSON-4, **3.2 × 3.0 mm**, three pad rows (top: source, pin 3; middle: drain bar, pin 2; bottom: gate pin 1 + source pin 4; Fig. 2 p.14 of its datasheet).
- IGC033S10S1: PG-TSON-6, **3 × 5 mm**, five rows alternating drain/source plus a gate + source row (Fig. 2 p.14 of its datasheet).
The pad rows do not coincide (row pitch 1.505 vs 1.075 mm, different row counts), and both use solder-mask-defined pads with split stencil apertures, so a combined "dual" pattern would leave unsoldered exposed copper under either part. Plan: draw the IGB070 footprint; in phase 6, **reserve the 3 × 5 mm IGC033 courtyard** at each FET site (≈ 2 mm extra length along the drain/source axis), so a fallback variant swaps footprints without moving neighbours. Pinouts: IGB070 pin 1 gate, 2 drain, 3–4 source; IGC033 pin 1 gate, 2/4 drain, 3/5/6 source.

## Operating point
fsw **576 kHz** (12 × 48 kHz; D-interfaces.md), BD, duty clamp 8–92 %, L = 10 µH, VBUS 48 V, LMG1210 dead-time setting **20 ns** (20.0 kΩ; datasheet spread 16–26 ns).

### Effective dead time with IGB070's edges
- Outgoing FET turn-off: Ciss 740 pF max from 5 V to the 2.8 V plateau through 1.6 Ω sink + 2.2 Ω Rg + 0.5 Ω Rg,int = 4.3 Ω → 4.3 × 0.74 nF × ln(5/2.8) = 1.9 ns. Then Qgd 1.7 nC at 2.8 V/4.3 Ω = 0.65 A → 2.6 ns. **≈ 4.5 ns.**
- Incoming FET to Vth (2.1 V): 5.9 Ω × 0.74 nF × ln(5/2.9) = **2.4 ns**.
- Effective window ≈ td − 4.5 + 2.4 ≈ td − 2 ns → **≈ 18 ns nominal (14–24 ns over the spread)**. ≥ 14 ns, so no shoot-through.
- Idle loss vs effective window (576 kHz, both channels): 14 ns 2.43 W, **18 ns 1.80 W**, 22 ns 1.26 W. 20 ns is kept: it is the characterised point and the same resistor as for the IGC033 fallback. The dead-time error grows (per leg 48 V × 18 ns × 576 kHz = 0.50 V; ≈ 1.5 % H3 at 50 W/8 Ω uncompensated) and is compensated in gateware with per-board calibration via the post-filter sense.

## Absolute max vs our worst case
| Parameter | Rating (p.3–4) | Our worst case | Margin |
|---|---|---|---|
| VDS | 100 V; 120 V pulsed (1 h total) | normal 48 V + overshoot I·√(L_loop/Coss) = 16 A × √(1 nH/340 pF) = **27 V** (13 A: 22 V) → ≤ 75 V; 55 V stop → 82 V; SMBJ51A clamp 82.4 V + 27 = **109 V** | normal ✓ (Infineon's 80 V guidance met at 48 V); the clamp case relies on the 120 V pulsed rating, as for IGC033 (review m3; independent rare events). **Phase 6 loop target ≤ 1 nH** (lower Coss → more ringing per nH than IGC033) |
| VGS | recommended −4.0…5.0…**5.5 V**; ±6.5 V pulsed (100 h) | LO ≤ 5.25 V; HO ≤ **5.32 V** worst case (VDD 5.25 V − VF 0.10 V + 16 A × 10.5 mΩ; D-bootstrap.md) | 0.18 V to the recommended max ✓ (but above the LMG1210 HB−HS ROC 5.25 V: see D-bootstrap.md) |
| ID pulsed | 360 A (25 °C), 170 A (150 °C) | ≤ 16.7 A (ramp OCP), ≤ 13.7 A (hard short), residual ≤ 21 A | ≫ |
| ID continuous | 38 A (TC 25 °C), 13 A (TA 25 °C, RthJA 48) | 6.0 A rms burst, 3.5 A rms continuous | ✓ |
| IS reverse | 7.4 A continuous, 152 A pulsed | dead-time and post-trip freewheel only (≤ 16 A for ≈ 3 µs) | ✓ (pulsed) |
| Tj | 150 °C; R-40 limit 125 °C | ≤ 83 °C with the panel path; **129 °C at 144 W/4 Ω without it** (upper bound) | panel path (R-61) **required** for the 144 W case, as before |

## Losses at 576 kHz (model as below; t_sw = 9 ns at the LMG1210's minimum source current: plateau current (5 − 2.8 V)/8.6 Ω = 0.26 A → Qgd 1.7 nC/0.26 A = 6.6 ns + ≈ 2 ns current rise; ZVS window 18 ns; Rds(on) 7.0 mΩ × 1.5 = 10.5 mΩ at 100 °C)
| Case | Coss+overlap / leg | dead time / leg | conduction / leg | **FET loss / channel** | per FET | Tj, 4 °C/W region | Tj, 15 °C/W (no panel) |
|---|---|---|---|---|---|---|---|
| idle | 0.446 W | 0 | 0.004 | **0.90 W** | 0.22 W | 62 °C | 73 °C |
| 1 W / 8 Ω | 0.476 | 0 | 0.005 | 0.96 W | 0.24 W | 62 °C | 74 °C |
| 50 W / 8 Ω | 0.822 | 0.062 | 0.068 | 1.90 W | 0.48 W | 69 °C | 92 °C |
| **46 W / 4 Ω (continuous case)** | 0.912 | 0.107 | 0.124 | **2.29 W** | 0.57 W | **72 °C** | **100 °C** |
| 144 W / 8 Ω | 1.064 | 0.155 | 0.190 | 2.82 W | 0.70 W | 76 °C | 110 °C |
| 144 W / 4 Ω (burst; upper bound if continuous) | 1.230 | 0.260 | 0.380 | **3.74 W** | 0.94 W | **83 °C** | **129 °C** |
**Idle FET loss, both channels: 1.80 W at 576 kHz** (448 kHz: 0.89 W; 768 kHz: 3.34 W). IGC033S10S1 at the same point: 6.02 W → the switch back saves **4.2 W** at idle.
Tj = 55 °C + P_region·R_region + P_FET·R_jb, with R_jb = RthJC(bottom) 5.4 max + 6 °C/W = 11.4 °C/W; P_region = channel FETs + 2 drivers (0.07 W) + 2 shunts.

## Gate drive (IGB070S10S1: Qg 6.1 / 7.9 nC max, Ciss 650 / 740 pF, Crss 3.6 / 4.7 pF, Vplateau 2.8 V, Vth 1.2 / 2.1 / 2.9 V)
- Gate loop √(2 nH/0.74 nF) = 1.64 Ω → critical damping needs ≥ 3.3 Ω; on 5.9–8.6 Ω, off 4.3–5.2 Ω (Rg 2.2 Ω) → over-damped ✓.
- dV/dt 48 V/(1.7 nC/0.37 A = 4.6 ns) ≈ 10 V/ns (7 V/ns at IOH min) ≪ 300 V/ns CMTI ✓. Miller: 4.7 pF × 10 V/ns × 4.3 Ω = 0.20 V ≪ Vth(min) 1.2 V ✓.
- Rg power 7.9 nC × 5 V × 576 kHz = 23 mW per gate, ≤ 12 mW in the 0402 Rg ✓.

## Fine print, layout
As in the sections below: 80 %-of-max guidance; recommended VGS 5.5 V (6.5 V pulsed only); exposed top die at source potential (insulating TIM if top-cooled; the baseline is bottom/board cooling); MSL1; solder-mask-defined pads (Fig. 2). HS/LS side by side, 2 × 100 nF 0603 across each half-bridge, return on L2, driver ≤ 5 mm, loop ≤ 1 nH.

## Open questions
1. Order early (above).
2. HO worst-case 5.32 V vs the LMG1210 HB−HS ROC of 5.25 V (D-bootstrap.md).

---

# Fallback: Infineon IGC033S10S1 (CoolGaN 100 V G3, 3.3 mΩ) — chosen 2026-11-07, reverted to fallback by the user 2026-11-08

> **fsw update (block E review, ECP5 −7I grid now 1.695 ns, PLL ×12): baseline fsw = 576 kHz (12 × 48 kHz, 1024 steps); 768 kHz option; 448/512/672 kHz only with E's ×14 bring-up option.** IGC033S10S1 at 576 kHz (20 ns setting ≈ 15 ns effective, t_sw 11 ns, 10 µH): **idle 6.02 W both channels** (448 kHz: 4.04 W; 768 kHz: 9.04 W). Per channel: idle 3.01 W (Tj 74 / 110 °C), 50 W/8 Ω 3.28 W (76 / 115 °C), **46 W/4 Ω 3.43 W (78 / 119 °C)**, 144 W/8 Ω 3.88 W (81 / 127 °C), 144 W/4 Ω 4.52 W (85 / **141** °C) — Tj with 4 °C/W panel path / 15 °C/W no panel. **The R-61 panel path is mandatory at 576 kHz.** Option: XAL1510-682MED 6.8 µH (C3911560, 152 in stock; SER2915H-682 has 0 stock) → idle 4.69 W (D-interfaces.md, user decision). Tables below are at 448 kHz.

Datasheet: datasheets/igc033s10s1.pdf (Final datasheet, Rev 1.1, 2025-04-22). Read: all sections, diagrams 9–16 rendered and read off the curves, footprint Fig. 2 p.14, package outline p.13.
MPN: IGC033S10S1. Supplier: `C41381300 IGC033S10S1 (Infineon, PG-TSON-6): extended, JLC stock 985, lifecycle normal, checked 2026-11-07`. Build need 8 × 5 + 4 = 44 ≪ 985 ✓.
Footprint: **PG-TSON-6, 3 × 5 mm** (project footprint from Fig. 2 p.14). The copper is 3.2 mm wide (2 × 1.6 mm). From the top: a drain row with 4 × 0.2 mm mask necks; then source/drain bars of 0.35 mm at 1.075 mm pitch (5 rows total, 2.175 mm between drain row centres); then a bottom row split into the gate pad (pin 1, 0.5 × 0.53 mm, bottom-left) and a source pad. Stencil apertures 0.8–0.9 × 0.29–0.34 mm (×9, ×3), for a 0.13 mm stencil. Pins (p.1): **1 = gate; 2, 4 = drain; 3, 5, 6 = source**. Solder-mask-defined pads. The top side is exposed silicon at source potential, "not recommended to use as an electrical connection".

Chosen by the user over the earlier recommendation IGB070S10S1: IGB070 had 80 in stock for a 44-part build, and IGC033 has 985. The cost is higher switching-charge loss. The IGB070 analysis is kept below as the rejected alternative.

## Operating point (with block E's ECP5 grid; D-interfaces.md)
fsw **448 kHz** baseline (512 / 672 kHz per-build options), BD, duty clamp 8–92 %, L = 10 µH, VBUS 48 V. **Dead-time setting 20 ns** (LMG1210 20.0 kΩ), which gives an **effective ≈ 15 ns** window at the FETs once IGC033's ≈ 8 ns turn-off and ≈ 3 ns turn-on-to-Vth are accounted for (review m1; D-lmg1210.md). The earlier 16 ns setting would have left an ≈ 11 ns window. The dead-time error is calibrated out with the post-filter sense, fitted on all prototypes.

## Absolute max vs our worst case
| Parameter | Rating (p.3–4) | Our worst case | Margin |
|---|---|---|---|
| VDS | 100 V continuous; 120 V pulsed (1 h total life) | normal: 48 V + switching overshoot I·√(L_loop/Coss) = 16 A × √(1 nH/590 pF) = **21 V** (12 A: 16 V) → ≤ 69 V; gateware stop 55 V + 21 = 76 V; **SMBJ51A clamp 82.4 V + 21 V = 103 V** | normal ✓ and within Infineon's 80 %-of-max guidance; the clamp case exceeds 100 V continuous and rests on the 120 V pulsed rating (review m3). Accepted because a 7.3 A TVS pulse and a hard edge at the trip current are independent rare events. **Phase 6 target: commutation loop ≤ 1 nH** |
| VGS | recommended −4.0…5.0…**5.5 V**; ±6.5 V pulsed (100 h) | HO ≤ 5.24 V (D-bootstrap.md), LO ≤ 5.25 V; HO ≥ 4.03 V at sustained max duty | 0.26 V to the recommended max |
| ID pulsed | 700 A (25 °C), 330 A (150 °C) | ≤ 16.7 A (ramp-regime OCP), ≤ 13.7 A (hard short), residual ≤ 21 A (D-current-sense.md) | ≫ |
| ID continuous | 76 A (TC 25 °C); 21 A (TA 25 °C, RthJA 38) | 6.0 A rms (144 W/4 Ω), 3.5 A rms continuous | ✓ |
| IS reverse | 16 A continuous, 304 A pulsed | dead-time and post-trip freewheel only | ✓ |
| Tj | 150 °C; R-40 limit 125 °C | ≤ 79 °C with the panel path; **124 °C** with no panel path at 144 W/4 Ω (upper bound) | ✓, with 1 °C of margin in the no-panel case: the R-61 panel path is **required** (below) |

## Data read off the datasheet / curves
- Rds(on) 2.4 typ / **3.3 mΩ max** at 25 °C, VGS 5 V, 20 A. Diagram 11: ×1.65 at 100 °C, ×2.0 at 125 °C → 5.4 mΩ max at 100 °C (used in the model).
- Qoss (Diagram 15): 20 nC at 15 V, 30 at 25, 38 at 40, 43 at 50 (47 max), 67 at 100 V. Fit 43 nC × (V/50)^0.62 → **41.9 nC at 48 V**. Eoss(48 V) ≈ 0.85 µJ (Diagram 16). Coss 540 / 590 pF max at 50 V (Table 6).
- Gate: Qg 11 typ / **14 nC max**; Qgs 2.8, Qgd 2.6, Qg(th) 2.1 nC; **Vplateau 2.6 V**; Ciss 1200 / 1400 max pF; Crss 6.1 / 8.0 max pF; Rg,int 0.5 Ω; Vth 1.2 / 1.9 / 2.9 V.
- VSD: 2.0 V at 0.5 A, 2.4 typ / 3.1 max V at 20 A (Table 8) → model 2.2 V + 0.045 Ω·I.
- Thermal: RthJC(top) 0.5/0.6, **RthJC(bottom) 1.9 typ / 2.8 max °C/W**; RthJA 38 °C/W (2s2p with vias).

## Loss model
Same model and script as for the rejected part below. **Switching-edge time t_sw = 11 ns, at the LMG1210's minimum source current** (review m2): IOH min 0.85 A (p.6) → ≈ 5.9 Ω source + 2.2 Ω Rg + 0.5 Ω → plateau current (5 − 2.6 V)/8.6 Ω = 0.28 A → Qgd 2.6 nC/0.28 A = 9.3 ns, plus ≈ 1.7 ns current rise. (With typical IOH: 8 ns.) ZVS window = effective dead time 15 ns.

**Idle (zero signal), both channels (4 half-bridges), L = 10 µH, t_sw 11 ns:**
| fsw | 16 ns setting (≈ 11 ns effective) | **20 ns setting (≈ 15 ns effective)** |
|---|---|---|
| **448 kHz** | 4.82 W | **4.04 W** |
| 512 kHz | 5.82 W | 5.02 W |
| 672 kHz | 8.36 W | 7.52 W |

**Loaded, per channel (2 legs), 448 kHz, 20 ns setting, Rds at 100 °C:**
| Case | FET loss / channel | per FET | Tj, 4 °C/W region | Tj, 15 °C/W (no panel) |
|---|---|---|---|---|
| idle | 2.02 W | 0.51 W | 68 °C | 92 °C |
| 50 W / 8 Ω | 2.42 W | 0.60 W | 71 °C | 100 °C |
| **46 W / 4 Ω (continuous case)** | **2.57 W** | 0.64 W | **72 °C** | 104 °C |
| 144 W / 8 Ω | 2.98 W | 0.74 W | 75 °C | 112 °C |
| 144 W / 4 Ω (burst; upper bound if continuous) | 3.52 W | 0.88 W | 79 °C | **124 °C** |
512 kHz: 46 W/4 Ω 3.00 W/ch (Tj 75/111 °C), 144 W/4 Ω 4.02 W (82/**132** °C). 672 kHz: 4.09 W (82/130 °C), 5.28 W (90/154 °C).
**The R-61 back-panel path (≤ 4 °C/W per channel region) is required at every fsw** for the 144 W upper bound (review m2), and for continuous operation at 512/672 kHz. Phase 4 must provide it.
Tj = 55 °C + P_region·R_region + P_FET·R_jb, with R_jb = 2.8 + 6 = 8.8 °C/W; P_region = channel FETs + 2 drivers (0.09 W) + 2 shunts.

Comparison at the same point (448 kHz, idle, both channels): IGB070S10S1 ≈ 1.1–1.4 W vs IGC033S10S1 4.04 W. That is the ≈ +2.7 W cost of the user's sourcing choice.

### Gate-drive margins
- Gate loop: √(L/C) = √(2 nH/1.4 nF) = 1.2 Ω; R_total on 5.9 Ω / off 4.3 Ω ≥ 2.4 Ω → over-damped with **Rg = 2.2 Ω** (unchanged; D-driver-passives.md).
- dV/dt ≈ 48 V/6.4–9.3 ns = 5–7.5 V/ns ≪ LMG1210 CMTI 300 V/ns.
- Miller at the 0 V off state: Crss 8 pF × 7.5 V/ns × 4.3 Ω = 0.26 V ≪ Vth(min) 1.2 V ✓.
- Gate power: Qg·V·f = 14 nC × 5 V × 448 kHz = 31 mW per gate, ≤ 16 mW of it in the 0402 Rg ✓.

## Fine print (IGC033S10S1)
- Recommended VGS max 5.5 V; the 6.5 V figure is pulsed (100 h total), "not recommended for normal operation".
- The exposed top die is at source potential (the switch node for the HS). Any top-side thermal interface must be insulating; the baseline cools through the bottom and the board (R-61).
- MSL1; JEDEC industrial qualification.
- Infineon: "do not continuously exceed 80 % of the maximum ratings" → continuous VDS ≤ 80 V ✓.

## Layout guidance
As below for the rejected part, with the 3 × 5 mm package: HS and LS side by side, 2 × 100 nF 0603 across each half-bridge, return on L2, driver ≤ 5 mm from the gates, via arrays per nets.csv, thermal pad / plate path under the bridge (R-61). The bottom-side RthJC is half of IGB070's, so the board path matters more.

## Open questions
1. Idle VBUS power is ≈ 4.0 W of FET loss alone at 448 kHz. Gateware auto-idle is strongly recommended (D-interfaces.md).
2. The back-panel thermal path (R-61) is required at every fsw for the 144 W upper bound (phase 4).

---

---

# Earlier IGB070S10S1 analysis at 480 kHz (2026-11-07; superseded by the 576 kHz section at the top; the selection table and datasheet readings remain valid)

Datasheet: datasheets/igb070s10s1.pdf (Final datasheet, Rev 1.0, 2025-01-27). Read: all sections, including diagrams 9–16 (rendered and read off the curves) and the footprint drawing (Fig. 2, p.14).
MPN: IGB070S10S1XTMA1. Supplier: `C44179579 IGB070S10S1XTMA1 (Infineon, PG-TSON-4-2): extended, JLC stock 80, lifecycle normal, checked 2026-11-07`
Build need: 8 per board × 5 boards = 40, plus 10 % attrition = 44. Stock 80 ≥ 44: **passes, but thin** (see Open questions).
Footprint: PG-TSON-4 (3.2 × 3.0 mm, three pad rows, solder-mask-defined pads). This needs a project footprint drawn from Fig. 2 p.14 (copper 1.6 + 1.6 mm wide rows, 1.505 mm row pitch; stencil apertures 3× 0.93 × 0.36 mm, etc.). Pins (Fig. 1 p.13, Fig. 2 p.14, top view): **top full-width row = pin 3 (source); middle bar = pin 2 (drain); bottom row = pin 1 (gate, small pad, bottom-left) and pin 4 (source, bottom-right)**. *(Corrected 2026-11-08, phase 2 parts review D-m3; the earlier text "pin 2 = drain (top row), pins 3–4 = source (middle and bottom rows)" was wrong. The footprint `studio_D:IGB070S10S1_PG-TSON-4` and the netlist already follow the datasheet: Q_H pin 2 on VBUS, pins 3/4 on SW; Q_L pin 2 on SW, pins 3/4 on GND.)* The top side is exposed silicon tied to source, and the datasheet says it is "not recommended to use as an electrical connection". *(Phase 2, review D-m1: `studio_D:IGB070S10S1_PG-TSON-4` is now solder-mask-defined per Fig. 2: copper-only pads (Fig. 2 copper + 0.05 mm), separate F.Mask windows (0.4 mm inner windows on the outer rows, 0.35 mm on the drain bar; the outer-edge mask notches are left closed), and Fig. 2's split stencil apertures on F.Paste.)*

Used as: 4 half-bridges (2 per BTL channel: woofer, tweeter), HS and LS each one IGB070S10S1, driven by an LMG1210 (D-lmg1210.md).

### Selection record (written when IGB070S10S1 was recommended)

The power stage peaks at 12 A (R-50), with the OCP trip at 15 A. Rds(on) hardly matters at that current: conduction loss at the R-33a continuous level is 0.13 W per leg with a 7 mΩ part. **Output charge Qoss dominates.** The half-bridge has to swing 2 × Qoss on every transition, and every edge that the ripple current cannot finish costs up to Qoss·VBUS. So the right FET is the smallest one whose Rds(on) and pulse rating still cover 15 A.

| Candidate (datasheet read) | LCSC / stock / lifecycle | Rds(on) max 25 °C | Qoss @50 V | Qg typ | Vth typ | Idle FET loss, both channels (480 kHz, 10 µH, 12 ns)¹ |
|---|---|---|---|---|---|---|
| **IGB070S10S1** (Infineon) | C44179579 / 80 / normal | 7.0 mΩ | 25 nC (28 max) | 6.1 nC | 2.1 V | **2.0 W** |
| IGC033S10S1 (Infineon) | C41381300 / 985 / normal | 3.3 mΩ | 43 nC (47 max) | 11 nC | 1.9 V | 5.1 W |
| INN100EA035EAD (Innoscience) | C55014508 / 393 / **unknown** | 3.5 mΩ | 41 nC | 10.1 nC | 1.2 V | 4.8 W |
| INN100W032A (Innoscience) | C49274913 / 737 / **unknown** | 3.2 mΩ | 50 nC | 9.2 nC | 1.1 V | > 5 W (larger Qoss) |
| INN100EBD025DAD (Innoscience) | C54350159 / 839 / **unknown** | 2.5 mΩ | 56 nC | 11 nC | 1.2 V | > 5 W |
| INN100EBD018DAD (Innoscience) | C54350158 / 1076 / **unknown** | 1.5 mΩ | 100 nC | 19 nC | 1.1 V | ≫ 5 W |
| INN100EA035A-C (Innoscience) | C52740984 / 859 / **unknown** | — | — | — | — | **no datasheet found** (the "A-C" suffix exists on no maker or distributor page); the EAD datasheet is a different ordering code |
| EPC2307 (EPC; checked as the EPC cross-reference) | C44009358 / 417 / normal | 10 mΩ | 58 nC @100 V | 10.1 nC | 1.5 V | worse: it is a 200 V die, with more Qoss per mΩ |
| EPC2045 / EPC2204 / EPC2218 / EPC2016C (EPC equivalents of a 7–16 mΩ 100 V class-D FET) | 0 stock on every listing | | | | | fails sourcing |

¹ From the loss model below, same conditions for every part (Coss stored energy curve fitted to each datasheet).

**Innoscience lifecycle check (by hand, as datasheet-audit.md asks):** `jlc_parts.py show` returns manufacturer None / lifecycle unknown for all five Innoscience parts. The JLCPCB part page for C55014508 has no lifecycle field. The LCSC product page `lcsc.com/product-detail/C55014508.html` returns "Part not found". LCSC has no datasheet for any of them. Innoscience's site has no product page that a search finds. The datasheets were fetched from Bonchip (a distributor), and for INN100W032A from Oneyac. Result: lifecycle cannot be confirmed, so under the phase-1 rule **they fail sourcing** on top of losing on Qoss.

### Absolute max vs our worst case

| Parameter | Abs max / rating (p.3–4) | Our worst case | Margin |
|---|---|---|---|
| VDS continuous | 100 V | VBUS 48 V nominal; 55 V firmware cut (R-35); TVS clamp 87.1 V max at 6.9 A (SMBJ54A, D-vbus-tvs.md) + switching overshoot ≈ 10 V with a tight loop | OK in normal running (≥ 45 V margin). In a TVS clamping event, 87 + 10 = 97 V < 100 V, and the 120 V pulsed rating (1 h total) covers ringing above that. Margin is thin only while the TVS conducts. |
| VDS pulsed | 120 V, 1 h total life | rare transients only | OK |
| VGS recommended | −4.0 … 5.0 … **5.5 V** (p.4) | HO: VHB−VHS ≤ 5.21 V (D-bootstrap.md); LO: VDD ≤ 5.25 V (LMG1210 LDO max) | 0.25 V to the recommended max; the 6.5 V pulsed rating (100 h total) covers gate ringing. Gate ringing must be kept below 6.5 V (Rg, short gate loop). |
| VGS negative | −4 V recommended min | 0 V off (LMG1210 has no negative drive) | OK |
| ID pulsed | 360 A at 25 °C, 170 A at Tj 150 °C | 16 A (15 A trip plus about 1 A overshoot, D-current-sense.md) | ≫ |
| ID continuous | 38 A (TC 25 °C); 13 A (TA 25 °C, RthJA 48) | 8.5 A rms at the 144 W burst; 3.5 A rms at the R-33a continuous level | OK |
| IS reverse continuous | 7.4 A (TC 25 °C) | conducts only inside the 12 ns dead times (≤ 1.2 % of the period); at 15 A trip all gates off: reverse conduction until the inductor current decays, 10 µH × 16 A / (48 V + 2.7 V) ≈ 3.2 µs | OK (pulsed reverse 152 A) |
| Tj | 150 °C max; R-40 limits us to 125 °C | 74 °C (4 °C/W board-to-panel), 108 °C (no panel path), at a continuous 144 W | OK |

### Required external parts (from datasheet)

The datasheet requires none beyond a gate driver. From the application context (LMG1210 datasheet §8.2 and motor-drive.md):
- Gate series resistor on each gate (D-driver-passives.md), to damp the gate loop. Rg_int is 0.5 Ω (p.6).
- Gate–source pull-down 10 kΩ (D-driver-passives.md), so the gate cannot float while the driver is unpowered. The LMG1210 also clamps an unpowered gate to ≤ 0.8 V (VCLAMP, p.6).
- HF ceramics directly across each half-bridge (D-bridge-decoupling.md).

### Calculations

### Data read off the curves (IGB070S10S1)
- Qoss(VDS) (Diagram 15): 11 nC at 15 V, 14 at 20, 18 at 30, 21.5 at 40, 24.5 at 50, 38.5 at 100 V. Fit Qoss = 24.5 nC·(V/50)^0.62 (error < 10 % from 15 to 100 V). Qoss(48 V) = 24.0 nC.
- Eoss(48 V) (Diagram 16) ≈ 0.50 µJ; the fit integral gives 0.44 µJ.
- Rds(on)(Tj)/Rds(25 °C) (Diagram 11): 1.25 at 50 °C, 1.5 at 100 °C, 1.85 at 125 °C. Rds(on) max at 100 °C = 7.0 × 1.5 = 10.5 mΩ (used in all loss numbers).
- Rds(on) vs VGS (Diagram 10): flat from 4.5 to 5 V at 25 °C, so the 4.6–5.2 V gate drive costs < 3 %.
- VSD reverse: 2.3 V at 0.5 A, 2.7 V typ / 3.5 V max at 13 A (Table 8). Model: 2.5 V + 0.077 Ω·I (3.5 V at 13 A, conservative).
- Gate: Qg 6.1 nC typ / 7.9 nC max at 5 V; Vplateau 2.8 V; Qgd 1.7 nC.

### Loss model (script: shown in full in the reviewer brief; inputs are all above)
For each switching period over a sine cycle: per leg, duty D = 0.5 ± M/2·sin (BD modulation), leg current = ±I_load + triangle ripple ΔI = VBUS·D(1−D)/(L·fsw).
- **Edge where the inductor current helps** (current flowing into the node at the LS→HS edge, out of it at the HS→LS edge): the current delivers q = |i|·td in the dead time. Swing reached: [Qoss(V) − Qoss(V−Vs)] + Qoss(Vs) = q. If the swing is incomplete, the remaining Vn is switched hard, with loss Eoss(Vn) + V·[Qoss(V) − Qoss(V−Vn)] − Eoss(V) + Eoss(V−Vn). That is 0 for full ZVS and V·Qoss(V) for none.
- **Edge where the current opposes:** loss = V·Qoss(V) + ½·V·|i|·t_sw, with t_sw = 4 ns (Qgd 1.7 nC at ≈ 0.47 A plateau gate current = (5 − 2.8 V)/(≈ 2 Ω driver + 2.2 Ω Rg + 0.5 Ω Rg_int), plus about 0.5 ns current rise). Add dead-time reverse conduction VSD·|i|·td.
- Conduction: (I² + ΔI²/12)·Rds(on, 100 °C), one FET conducting at any time.

Conditions: VBUS 48 V, fsw 480 kHz, L 10 µH, td 12 ns (D-lmg1210.md), BTL, per channel = 2 legs.

| Case | Ipk | M | Coss + overlap / leg | Dead time / leg | Conduction / leg | **FET loss per channel** | **per FET** |
|---|---|---|---|---|---|---|---|
| Idle (zero signal) | 0 | 0 | 0.489 W | 0 | 0.005 W | **0.99 W** | 0.25 W |
| 1 W into 8 Ω | 0.50 A | 0.08 | 0.501 | 0 | 0.007 | 1.01 W | 0.25 W |
| 50 W into 8 Ω (R-51 point) | 3.54 A | 0.59 | 0.617 | 0.022 | 0.069 | 1.42 W | 0.35 W |
| **46 W into 4 Ω** (R-33a Class 8 average, all in one channel: the continuous thermal case) | 4.80 A | 0.40 | 0.644 | 0.044 | 0.125 | **1.63 W** | **0.41 W** |
| 144 W into 8 Ω (M = 1, limit) | 6.00 A | 1.00 | 0.703 | 0.069 | 0.191 | 1.93 W | 0.48 W |
| 144 W into 4 Ω (firmware maximum; bursts only, PoE cannot sustain it) | 8.49 A | 0.71 | 0.759 | 0.125 | 0.381 | 2.53 W | 0.63 W |

Idle, both channels: 2 × 0.99 = **1.98 W** of FET loss. For comparison, IGC033S10S1 at the same point gives 2 × 2.56 = 5.1 W. That is the main reason for the choice.

Sensitivity (idle, both channels, IGB070S10S1): td 8/12/16/20 ns → 2.7/2.0/1.4/0.9 W; fsw 432/480/576/768 kHz at 16 ns → 1.0/1.4/2.1/3.7 W; L 6.8/10/15 µH at 16 ns → 0.56/1.36/2.2 W.

### Junction temperature (R-40: Tj ≤ 125 °C at 55 °C internal air; R-61 heat path into board copper and the back panel)
Tj = 55 °C + P_region·R_region + P_FET·R_jb, where:
- R_jb = RthJC(bottom) 5.4 °C/W max (Table 4) + 6 °C/W assumed for solder, via arrays and plane spreading = 11.4 °C/W. The FET sits on the VBUS plane (HS drain) or the GND plane (LS source) on one side and on switch-node copper on the other.
- P_region = one channel's FETs + 2 drivers (0.07 W each) + 2 shunts.
- R_region = the channel's board area to 55 °C air: 4 °C/W with the thermal pad / aluminium plate to the back panel (R-61, sized in phase 4), 15 °C/W with no panel path (board copper only).

| Case | P_region | Tj, R_region 4 °C/W | Tj, R_region 15 °C/W |
|---|---|---|---|
| Idle | 1.1 W | 62 °C | 75 °C |
| 46 W / 4 Ω continuous | 1.9 W | **67 °C** | 88 °C |
| 144 W / 4 Ω, continuous (upper bound; PoE limits this to bursts) | 3.1 W | 74 °C | **108 °C** |

All are below 125 °C, even with no panel path. Rds(on) was taken at 100 °C, which is conservative for the 67–74 °C results.

### Gate drive margin
- Turn-on: HO = VHB−VHS ≈ 4.6–5.2 V and LO = VDD 4.75–5.25 V, against Vth 2.1 V typ (2.9 V max, 25 °C) and a Diagram 10 plateau that is flat from 4.5 V. OK.
- Miller-induced turn-on at the 0 V off state: dV/dt ≈ VBUS/t_sw = 48 V / 3.6 ns = 13 V/ns. Crss 4.7 pF max × 13 V/ns = 63 mA through the LMG1210's 3 A sink (≈ 1.7 Ω) plus 2.2 Ω Rg → 0.25 V bump, against Vth(min) 1.2 V. OK; this is why the off path keeps Rg small.

### Fine print / gotchas
- "For optimum lifetime and reliability, Infineon recommends operating conditions that do not continuously exceed 80 % of the maximum ratings" (p.3). 80 % of 100 V is 80 V. Our continuous VDS is 48 V (55 V firmware cut), which complies. The TVS clamp level exceeds 80 V only during a transient.
- VGS: the *recommended* max is 5.5 V. The ±6.5 V figure is a pulsed rating of 100 h total, "not recommended for normal operation".
- The top-side exposed die is at source potential. For the HS that is the switch node (0–48 V at 480 kHz). Any top-side thermal interface must be electrically insulating. The baseline thermal path is bottom-side, through the board (R-61).
- Pulsed current is "limited by transfer characteristic" (footnote 3): not a concern at 16 A.
- MSL1; package PG-TSON-4 with solder-mask-defined pads (Fig. 2): the KiCad footprint must reproduce SMD pads and the split stencil apertures.
- No reverse recovery (Qrr = 0), but VSD is high (2.3–3.5 V) with the gate at 0 V. Dead-time conduction costs about 3× a silicon body diode, which is why td is kept at 12 ns.

### Layout guidance (feeds phase 4/6)
- HS and LS of each leg side by side, with 2 × 100 nF 0603 directly across HS drain and LS source, and the return on the next inner layer (LMG1210 do's #2/#3): smallest commutation loop. Target < 1 nH, so ringing on 48 V stays ≤ 10 V.
- LMG1210 within about 5 mm of both gates. The gate loop returns to the Kelvin side of the source (the LS gate returns to VSS, which ties to the LS source pad; the HS gate returns to HS at the HS source pad).
- Drain/source copper on several layers with via arrays sized from the current in nets.csv: 8.5 A rms burst, 16 A peak.
- Heat goes into the VBUS and GND planes; leave room under the bridge for the back-panel thermal pad (R-61).

### Open questions
1. **Stock is 80 against 44 needed.** Ask the user to order or reserve the FETs early, or accept IGC033S10S1 (985 in stock, PG-TSON-6 3 × 5 mm, a different footprint) as the fallback, at about +3 W idle loss. This is a user decision.
2. The loss model's Coss and overlap terms need confirming on the bench: idle VBUS current per channel at bring-up, expected 0.99 W / 48 V ≈ 21 mA per channel (FETs only).
