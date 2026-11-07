# Q (×8) — power-stage GaN FET: Infineon IGC033S10S1 (CoolGaN 100 V G3, 3.3 mΩ) — **user decision 2026-11-07**

Datasheet: datasheets/igc033s10s1.pdf (Final datasheet, Rev 1.1, 2025-04-22). Read: all sections, diagrams 9–16 rendered and read off the curves, footprint Fig. 2 p.14, package outline p.13.
MPN: IGC033S10S1. Supplier: `C41381300 IGC033S10S1 (Infineon, PG-TSON-6): extended, JLC stock 985, lifecycle normal, checked 2026-11-07`. Build need 8 × 5 + 4 = 44 ≪ 985 ✓.
Footprint: **PG-TSON-6, 3 × 5 mm** (project footprint from Fig. 2 p.14). The copper is 3.2 mm wide (2 × 1.6 mm). From the top: a drain row with 4 × 0.2 mm mask necks; then source/drain bars of 0.35 mm at 1.075 mm pitch (5 rows total, 2.175 mm between drain row centres); then a bottom row split into the gate pad (pin 1, 0.5 × 0.53 mm, bottom-left) and a source pad. Stencil apertures 0.8–0.9 × 0.29–0.34 mm (×9, ×3), for a 0.13 mm stencil. Pins (p.1): **1 = gate; 2, 4 = drain; 3, 5, 6 = source**. Solder-mask-defined pads. The top side is exposed silicon at source potential, "not recommended to use as an electrical connection".

Chosen by the user over the earlier recommendation IGB070S10S1: IGB070 had 80 in stock for a 44-part build, and IGC033 has 985. The cost is higher switching-charge loss. The IGB070 analysis is kept below as the rejected alternative.

## Operating point (with block E's ECP5 grid; D-interfaces.md)
fsw **448 kHz** baseline (512 / 672 kHz per-build options), BD, **dead time 16 ns** (raised from 12 ns for this part: its larger Qoss gains more soft-switching from a longer dead time; the extra dead-time error is calibrated out with the post-filter sense, which the user decided to fit on all prototypes), L = 10 µH, VBUS 48 V.

## Absolute max vs our worst case
| Parameter | Rating (p.3–4) | Our worst case | Margin |
|---|---|---|---|
| VDS | 100 V continuous; 120 V pulsed (1 h total) | 48 V normal, 55 V gateware stop; **SMBJ51A clamp 82.4 V at 7.3 A** + switching overshoot ≈ 10 V = 92 V (D-vbus-tvs.md) | normal ≥ 45 V; clamp event 8 V; Infineon's 80 %-of-max guidance (80 V) is met except during a TVS clamp |
| VGS | recommended −4.0…5.0…**5.5 V**; ±6.5 V pulsed (100 h total) | HO ≤ 5.13 V (D-bootstrap.md), LO ≤ 5.25 V | 0.25 V to the recommended max |
| ID pulsed | 700 A (25 °C), 330 A (150 °C) | 16 A (14.9 A trip + 1 A overshoot) | ≫ |
| ID continuous | 76 A (TC 25 °C); 21 A (TA 25 °C, RthJA 38) | 6.0 A rms (144 W/4 Ω), 3.5 A rms continuous | ✓ |
| IS reverse | 16 A continuous, 304 A pulsed | dead-time and post-trip freewheel only | ✓ |
| Tj | 150 °C; R-40 limit 125 °C | ≤ 77 °C (4 °C/W panel path); ≤ 119 °C (no panel path, 144 W continuous upper bound) | ✓ |

## Data read off the datasheet / curves
- Rds(on) 2.4 typ / **3.3 mΩ max** at 25 °C, VGS 5 V, 20 A. Diagram 11: ×1.65 at 100 °C, ×2.0 at 125 °C → 5.4 mΩ max at 100 °C (used in the model).
- Qoss (Diagram 15): 20 nC at 15 V, 30 at 25, 38 at 40, 43 at 50 (47 max), 67 at 100 V. Fit 43 nC × (V/50)^0.62 → **41.9 nC at 48 V**. Eoss(48 V) ≈ 0.85 µJ (Diagram 16).
- Gate: Qg 11 typ / **14 nC max**; Qgs 2.8, Qgd 2.6, Qg(th) 2.1 nC; **Vplateau 2.6 V**; Ciss 1200 / 1400 max pF; Crss 6.1 / 8.0 max pF; Rg,int 0.5 Ω; Vth 1.2 / 1.9 / 2.9 V (min/typ/max).
- VSD: 2.0 V at 0.5 A, 2.4 typ / 3.1 max V at 20 A (Table 8) → model 2.2 V + 0.045 Ω·I.
- Thermal: RthJC(top) 0.5/0.6, **RthJC(bottom) 1.9 typ / 2.8 max °C/W**; RthJA 38 °C/W (2s2p with vias).

## Loss model (same model and script as for the rejected part below)
Switching-edge time t_sw = 8 ns: plateau gate current (5 − 2.6 V)/(3.2 Ω driver + 2.2 Ω Rg + 0.5 Ω) = 0.41 A → Qgd 2.6 nC/0.41 A = 6.4 ns, plus ≈ 1.7 ns current rise ((Qgs − Qg(th))/0.41 A).

**Idle (zero signal), both channels (4 half-bridges), L = 10 µH:**
| fsw | td 12 ns | **td 16 ns** | td 20 ns |
|---|---|---|---|
| **448 kHz** | 4.62 W | **3.86 W** | 3.16 W |
| 512 kHz | 5.62 W | 4.83 W | 4.09 W |
| 672 kHz | 8.15 W | 7.32 W | 6.52 W |

**Loaded, per channel (2 legs), 448 kHz, td 16 ns, Rds at 100 °C:**
| Case | FET loss / channel | per FET | Tj, 4 °C/W region | Tj, 15 °C/W (no panel) |
|---|---|---|---|---|
| idle | 1.93 W | 0.48 W | 68 °C | 91 °C |
| 50 W / 8 Ω | 2.29 W | 0.57 W | 70 °C | 98 °C |
| **46 W / 4 Ω (continuous case)** | **2.42 W** | 0.60 W | **71 °C** | 101 °C |
| 144 W / 4 Ω (burst; upper bound if continuous) | 3.23 W | 0.81 W | 77 °C | **119 °C** |
At 512 kHz, td 16 ns: 46 W/4 Ω → 2.82 W/ch, Tj 74 / 108 °C; 144 W/4 Ω → 3.69 W, Tj 80 / 127 °C (no-panel case exceeds 125 °C, so the panel path is required).
At 672 kHz: 46 W/4 Ω → 3.83 W/ch, Tj 80 / 125 °C; 144 W/4 Ω → Tj 87 / 146 °C. **The 672 kHz build needs the R-61 back-panel path** (≤ 4 °C/W per channel region).
Tj = 55 °C + P_region·R_region + P_FET·R_jb, with R_jb = RthJC(bottom) 2.8 max + 6 °C/W solder/via/plane spreading = 8.8 °C/W, and P_region = channel FETs + 2 drivers (0.09 W each) + 2 shunts.

Comparison at the same point (448 kHz, td 16 ns, idle both channels): IGB070S10S1 1.14 W vs IGC033S10S1 3.86 W. That is the +2.7 W cost of the user's sourcing choice.

### Gate-drive margins
- Gate loop: √(L/C) = √(2 nH/1.4 nF) = 1.2 Ω; R_total on 5.9 Ω / off 4.3 Ω ≥ 2.4 Ω → over-damped with **Rg = 2.2 Ω** (unchanged; D-driver-passives.md).
- dV/dt ≈ 48 V/6.4 ns = 7.5 V/ns ≪ LMG1210 CMTI 300 V/ns.
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
1. Idle VBUS power is now ≈ 3.9 W of FET loss alone at 448 kHz. Gateware auto-idle is strongly recommended (D-interfaces.md).
2. The 672 kHz option requires the back-panel thermal path (phase 4).

---

# Rejected alternative: Infineon IGB070S10S1 (original recommendation, kept for the record)

Datasheet: datasheets/igb070s10s1.pdf (Final datasheet, Rev 1.0, 2025-01-27). Read: all sections, including diagrams 9–16 (rendered and read off the curves) and the footprint drawing (Fig. 2, p.14).
MPN: IGB070S10S1XTMA1. Supplier: `C44179579 IGB070S10S1XTMA1 (Infineon, PG-TSON-4-2): extended, JLC stock 80, lifecycle normal, checked 2026-11-07`
Build need: 8 per board × 5 boards = 40, plus 10 % attrition = 44. Stock 80 ≥ 44: **passes, but thin** (see Open questions).
Footprint: PG-TSON-4 (3.2 × 3.0 mm, three pad rows, solder-mask-defined pads). This needs a project footprint drawn from Fig. 2 p.14 (copper 1.6 + 1.6 mm wide rows, 1.505 mm row pitch; stencil apertures 3× 0.93 × 0.36 mm, etc.). Pin 1 = gate (small pad, bottom-left in the top view), pin 2 = drain (top row), pins 3–4 = source (middle and bottom rows). The top side is exposed silicon tied to source, and the datasheet says it is "not recommended to use as an electrical connection".

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
