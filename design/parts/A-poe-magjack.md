# J1 — LPJK6078AHNL RJ45 with integrated 4-pair PoE++ magnetics and Bob Smith termination

Datasheet: `datasheets/A-lpjk6078ahnl.pdf` (LINK-PP drawing LP23032002 rev A6, 2023-03-20, 2 sheets).
Read: both sheets (schematic, electrical spec, mechanical, suggested PCB layout).
MPN: LPJK6078AHNL ("RJ45 Connector with 1000 Base-T Integrated Magnetics For PoE++ Application")
Supplier: `C49274795 LPJK6078AHNL (LINK-PP, Through Hole): extended, JLC stock 58, lifecycle normal, checked 2026-11-07`
Build need: 5 + 2 = 7. OK (58). Through-hole: hand-solder allowed (R-70).
Footprint: custom from sheet 2 "Suggested PCB Layout (Top View)": 16 x Ø0.89 mm signal pins (2.03 mm
row pitch, two staggered rows 1.02 mm offset), 4 x Ø1.03 mm LED pins, 2 x Ø3.20 mm plastic posts,
2 x Ø1.57 mm shield tabs; body 16.30 x 23.5 mm, 13.50 mm tall. Phase 2 builds it from the drawing and
checks pin 1 against the schematic numbering (pins 1–16, LEDs 17–20).

## Why this part

R-10 needs centre taps on all four pairs, 802.3bt Type 4 current (≤ 960 mA per pair set), and Bob Smith.
LCSC candidates checked 2026-11-07, with their datasheets read for the current rating:

| Part | Kind | Stock | DC current rating (datasheet) | Verdict |
|---|---|---|---|---|
| **LPJK6078AHNL** | 1000BASE-T magjack, 4 CTs out, PoE++ | 58 | **1.0 A continuous, 1.2 A for 200 ms, at 57 V** | chosen |
| LP6090ANL | discrete 4-ch SMD transformer, PoE++, 802.3bt | 187 | 1.2 A continuous | fallback (needs a separate RJ45 + discrete Bob Smith) |
| LPJG0926HENL / LPJG4926HENL | magjack PoE+ | 1262 / 42 | 720 mA | fails Class 8 (OK for Class 6 only) |
| LPJK6071BONL | magjack | 45 | 720 mA | fails Class 8 |
| HY931147C (HanRun) | 10/100 magjack with internal diode bridges | 5627 | 802.3af | fails |
| Würth 7499111446 / 7499111121A | magjacks | 28 / 20 | — | lifecycle "unknown" on LCSC, no datasheet on LCSC: fails sourcing rule |
| Mentech G2401CG / H4001CG, HanRun HR913129C | plain magnetics | many | no PoE rating; 0–70 °C | fail |

## Ratings vs our worst case (sheet 1, "Electrical Specifications @25 °C")

| Parameter | Rating | Our worst case | Margin |
|---|---|---|---|
| Balanced DC line current (per CT) | 1.0 A continuous @ 57 VDC; 1.2 A for 200 ms | Class 8 balanced 0.865 A; R-10 ≤ 0.96 A per pair set (pair-to-pair unbalance) | **4 % at 0.96 A**; 16 % balanced. Class 6 (0.60 A): 67 % |
| Isolation PHY side to line side | 1500 Vrms | R-32: 1500 Vrms, 60 s | meets, no margin (802.3 value) |
| Operating temperature | –40…+85 °C | 55 °C cabinet air + self-heating | OK |
| OCL | 350 µH min @ 100 kHz, 14 mA DC bias; 120 µH @ 23 mA bias | 100BASE-TX needs 350 µH at 8 mA (IEEE 802.3 baseline) | OK |
| Insertion loss / RL / CMR | –1.0 dB to 100 MHz; RL –18 dB to 40 MHz; CMR –30 dB | 100BASE-TX | OK |
| Bob Smith (internal) | 4 x 75 Ω, each through 22 nF 100 V, common node to SHIELD via 1000 pF / 2 kV | R-90 | provided |
| LEDs | green 565 nm, yellow 585 nm, VF 1.8–2.6 V at 20 mA | block E drives them (PHY LED pins), ≤ 20 mA | — |
| Note 2 on sheet 2 | "Meets IEEE 802.3af specification" | contradicts the title ("PoE++") and spec line 7 | the 1.0 A line rating governs; flagged |

## Pin map (from the sheet 1 schematic)

| Pin | Name | Connect to | Note |
|---|---|---|---|
| 11 / 10 | MD1+ / MD1– | PHY TX± (block E) | transformer to RJ45 J1/J2 (pair 1-2) |
| 12 | MDCT1 | PHY-side CT per PHY datasheet (block E) | |
| 4 / 5 | MD2+ / MD2– | PHY RX± (block E) | to J3/J6 (pair 3-6) |
| 6 | MDCT2 | PHY-side CT (block E) | |
| 3 / 2, 1 | MD3± , MDCT3 | not used by 100BASE-TX: leave open | pair 4-5 carries power only |
| 8 / 9, 7 | MD4± , MDCT4 | not used: leave open | pair 7-8 |
| 13 | VC+ | `POE_CT12` → LT4321 IN12 + bridge FETs | line-side CT of J1/J2 |
| 14 | VC– | `POE_CT36` → LT4321 IN36 | CT of J3/J6 |
| 15 | VC+ | `POE_CT45` → LT4321 IN45 | CT of J4/J5 |
| 16 | VC– | `POE_CT78` → LT4321 IN78 | CT of J7/J8 |
| 17–20 | LEDs | block E | right LED 18(+)/17(–) yellow, left LED 20(+)/19(–) green |
| shield tabs | SHIELD | `RJ45_SHIELD` → shield network (`A-shield-network.md`) | |

The VC+/VC– labels are the vendor's polarity for Mode A/B; with ideal-diode bridges polarity does not
matter. **The CT-to-pin assignment of 13–16 is read off the drawing's junction dots; verify by
continuity on the first part (RJ45 pin 1 ↔ pin 13 through the winding, etc.) before phase 2 freezes the
symbol.** Getting a pair-set grouping wrong (e.g. 13 with 15 on one LT4321 input group) would stop that
pair set's FETs from ever turning on (LT4321 p.6).

## Calculations

1. **CT current** at Class 8: I_set = 71.3 W / 41.2 V / 2 = 0.865 A balanced; up to 0.96 A with
   pair-set unbalance (R-10). Rating 1.0 A ⇒ margin 4–16 %. At Class 6: 0.60 A. The rating is at
   "@25 °C"; no derating curve is given (open question).
2. **Winding loss** (no DCR given for this part). LP6090ANL, the same maker's PoE++ transformer, lists
   0.30 Ω typ per winding; with a CT, each half carries I/2 through ≈ 0.15 Ω: P_CT = 2 x (I/2)² x 0.15 =
   0.075·I² = 56 mW per CT at 0.865 A, **≈ 0.22 W for all four CTs** at Class 8 (estimate). Included
   in the block A loss budget (`A-interfaces.md`).

## Fine print / gotchas

- The internal Bob Smith cap (1000 pF / 2 kV) ties the cable's common mode to the shield. With the shield
  on secondary GND (R-10), this cap and the magnetics' winding insulation together form the
  cable-to-secondary barrier. The magjack's 1500 Vrms rating is stated PHY-side to line-side only; the
  2 kV cap's rating presumably DC, so a 1500 Vrms (2121 Vpk) hipot from cable to secondary GND would
  exceed it. **R-32 hipot on the assembled board is at risk through this cap**; see
  `A-shield-network.md` for the options.
- 100BASE-TX only uses MD1/MD2; the two unused windings stay open on the PHY side. Their line side
  carries power through the CT.

## Layout guidance

- J1 on the board edge (R-60). Everything on the line side and the CT nets is primary; the PHY-side pins
  (1–12) and LEDs are secondary — the R-32 barrier keepout runs **through the jack body**, between the
  pin rows: confirm in phase 4 that the vendor's pin rows give the needed creepage (rows are 2.03 mm
  apart on the drawing, which is far less than a 1500 Vrms creepage; the isolation sits inside the jack).
  CT pins 13–16 and LED pins 17–20 must be routed so CT copper never comes near PHY-side or LED copper.
- CT traces to the bridges ≥ 0.6 mm wide (1 A, 10 °C rise, 1 oz external; phase 3/5 confirms).

## Open questions

- CT current derating over temperature: not given. 4 % margin at the 0.96 A unbalanced corner. If the
  first board runs hot at Class 8, LP6090ANL (1.2 A) + plain shielded RJ45 is the fallback.
- Datasheet note 2 ("802.3af") contradicts the PoE++ title and the 1.0 A rating. Ask LINK-PP or accept.
- Verify CT pin mapping by continuity (above).
