# Block A — interfaces, loss budget, proposed architecture changes

Audits behind this file: `A-poe-magjack.md`, `A-shield-network.md`, `A-bridge-lt4321.md`,
`A-bridge-fets.md`, `A-tvs.md`, `A-pd-tps2373.md`, `A-pd-passives.md`, `A-isolator-iso7740.md`.
Datasheet list: `datasheets/sources-A.csv`.

## Signal chain

J1 LPJK6078AHNL (4 line-side CTs: pins 13/14/15/16) → `POE_CT12`, `POE_CT36`, `POE_CT45`, `POE_CT78`
→ LT4321 + 8 x PSMN040-100MSE (two ideal-diode bridges, enabled above ~29–33 V by BZT52C27 + 100 kΩ into
EN) → `VPRI` (= OUTP = TPS2373 VDD) and `VPD_N` (= OUTN = TPS2373 VSS) → SMBJ58A + 100 nF C_PD across
them → TPS2373-4 (Class 8: 63.4 Ω / 90.9 Ω; RDEN 24.9 kΩ; RREF 49.9 kΩ) → hot-swap in the return:
`VPRI_RTN` (= RTN) → block B.

## Block loss budget (R-33a line "Bridges + PD + hot-swap loss")

| Item | Class 8 (1.73 A) typ / worst | Class 6 (1.20 A) typ / worst | Source |
|---|---|---|---|
| Magjack CT windings (estimate, no DCR in datasheet) | 0.22 / 0.22 W | 0.11 W | `A-poe-magjack.md` calc 2 |
| FET bridges | 0.09 / 0.20 W | 0.04 / 0.10 W | `A-bridge-lt4321.md` calc 2 |
| LT4321 quiescent | 0.03 / 0.05 W | same | LT4321 p.3 |
| TPS2373 hot-swap + bias | 0.33 / 0.65 W | 0.17 / 0.33 W | `A-pd-tps2373.md` calc 2 |
| **Total** | **0.67 / 1.12 W** | **0.35 / 0.60 W** | budget 1.5 W / 1.2 W: **met** |
| Same with a Schottky bridge (SS310) | 2.9 / 3.2 W | 1.8 / 1.9 W | would **miss** the budget |

The isolator branch (≤ 15.3 mA from VB_PRI ≈ 0.2 W) belongs to block B's bias budget, not this line.

## What block B must connect (UCC2897A side)

| TPS2373 pin | Net | Block B connects | Rule / reason |
|---|---|---|---|
| VDD (1) | `VPRI` | converter input +, CBULK +, UCC2897A VIN (see below) | VPRI is the bridge output; it is **not** switched |
| RTN (11, 12) | `VPRI_RTN` | converter input return, CBULK –, UCC2897A GND/PGND, primary FET source/sense return | hot-swap is in the return |
| VSS (4, 5, EP) | `VPD_N` | **nothing** in block B | VSS-referenced parts are block A only; block B must not tie anything to VSS |
| VC_OUT (14) | `VC_OUT` | **not used** — 1 µF to RTN only (block A part) | UCC2897A needs ≈ 32 mA bias (`B-interfaces.md`), over VC_OUT's 20 mA rec. sourcing (p.6) |
| VC_IN (15) | `VB_PRI` | block B's 13.5 V LM5019 bias buck (also UCC2897A VDD); 100 nF local bypass is block A's. **VB_PRI must also supply the isolator branch, ≤ 15.3 mA** | §7.3.7 p.20: "If VC_OUT is not used, VC_IN must be connected to the low voltage bias supply of the PWM controller"; rec. max 15 V |
| PG (13) | `PD_PG` | → 1 kΩ (block B) → UCC2897A **SS/SD** (`UCC_SS`), with block B's CSS to RTN. Block A hangs the 2N7002 gate on the SS/SD side | TPS2373 Fig. 21 p.17; SS/SD < 0.4–0.6 V = UCC2897A shutdown |
| UVLO_SEL (16) | open | — | VC_OUT UV 7.35 V max < UCC2897A min stop 7.6 V |
| TPH/TPL/BT, APD, CLSx, DEN, REF, AMPS_CTL, MPS_DUTY | block A | — | — |

Block B constraints from the PD — all four **closed with block B on 2026-11-07** (`B-interfaces.md`,
`B-primary-power.md`, `B-controller.md`, `B-bias.md`):

1. **Input current ≤ 1.85 A** (TPS2373 RTN recommended max). B moved LINEUV to 40.4 V on / 38.4 V off
   (73.2 k / 2.37 k) and limits Class 8 output to 64.5 W, so input stays ≤ 1.85 A across the run range.
   Residual: worst tolerance corner 1.89 A at 37.6 V (91 % efficiency), just above 1.85 A rec. max and
   below the 1.9 A current-limit minimum (p.7), at the LINEUV-off edge only. Accepted.
2. **VPRI range**: B runs from LINEUV-off (38.4 V nom, ≈ 37.6 V worst) to 57 V; survives 96 V (TVS, hot).
   - Start: B's 40.4 V on is above the PD's rising UVLO (36.3–40 V), so the PD always closes first. At
     start-up the PI sits at the PSE's no-load voltage (≥ 50 V Type 2/3, ≥ 52 V Type 4, TPS2373 Table 6),
     well above 40.4 V.
   - Run: lowest compliant full-load VPRI is 40.8 V (Type 4 PI 41.2 V minus drops), 2.4 V above B's off.
   - Consequence: a **Type 1 PSE** (PI allowed down to 37 V at ≤ 13 W) can fall under B's off threshold.
     R-30 only requires Type 2 and up, so this is accepted.
3. **CBULK** on VPRI–VPRI_RTN: 3 x 4.7 µF 100 V X7S + 47 µF 100 V electrolytic (Honor RVT2A470M1010,
   C87862, 105 °C) = **61 µF nominal**. ≥ 10 µF effective at 57 V (LT4321 p.7) ✓; ≤ 120 µF recommended
   ✓. Inrush: 61 µF x 57 V / 0.275 A = 12.7 ms at the minimum inrush limit; hot-swap energy ½CV² = 0.10 J.
   These are not part of the 802.3 C_PD (VDD–VSS, block A's 100 nF only).
4. **VB_PRI**: budgets 47 mA (32 mA UCC2897A + gate drive, 15.3 mA isolator primary), inside the LM5019's
   100 mA rating. While SS/SD holds the UCC2897A off during inrush, B's idle load is ≈ 0.27 W ⇒ ≈ 10 mA
   from VPRI at 30 V, inside the ≲ 30 mA allowance, so the inrush can still finish (TPS2373 p.18).
5. Block B's Y-cap VPRI_RTN ↔ GND sits in parallel with the RJ45 shield network (1 nF to GND); size it
   knowing that.

## What block E receives (from the isolator, 3.3 V CMOS, active low, default high)

| Net | Low means | Notes |
|---|---|---|
| `PD_TPH_N` | TPH asserted | decode with TPL/BT per `A-pd-tps2373.md` truth table |
| `PD_TPL_N` | TPL asserted | |
| `PD_BT_N` | 802.3bt (Type 3/4) PSE | |
| `PD_PG_N` | PD out of inrush **and** UCC2897A soft-start past ~2.5 V | goes high if the PD folds back or the UCC2897A shuts down |

- All four read high ("nothing granted / not good") until the primary is up; TPH/TPL/BT become valid
  20–28 ms after PG releases (VC_IN is already up). Read the class ≥ 30 ms after PD_PG_N falls, and watch for changes.
- **PoE-loss detection (R-32a)**: TPS2373 PG does **not** fall on input loss (hot-swap opens, PG stays
  high-Z, p.28). But TPH/TPL/BT return to high-Z when VDD–VSS < ~32 V (p.19). So "any of TPH/TPL/BT
  de-asserting after having been asserted" is the early primary-side loss flag, and it exists for every
  Type 2/3/4 grant. With a Type 1 PSE (all high) only the secondary comparator (R-32a) and PD_PG_N
  remain. Block E/C must keep the secondary comparator as the primary loss detector.
- Isolator VCC2 = `+3V3`, ≤ 3.2 mA (block C budget).

## Proposed changes to architecture

1. **Rail table**: replace `VPOE_A`, `VPOE_B` ("pair-set centre taps, before the bridges") by four nets
   `POE_CT12`, `POE_CT36`, `POE_CT45`, `POE_CT78` — each pair set has two centre taps, and the LT4321
   senses all four.
2. **Rail table**: `VPRI` is the bridge output (OUTP = TPS2373 VDD), **not** "after the PD hot-swap FET";
   the TPS2373 switches the return. `VPRI_RTN` = TPS2373 RTN (after the hot-swap). Add `VPD_N`
   (bridge OUTN = TPS2373 VSS, primary, block A only).
3. **Rail table**: add `VB_PRI` (block B's 13.5 V primary bias, RTN-referenced; = TPS2373 VC_IN) and
   `VISO_P5V` (primary 5 V for the isolator, from VB_PRI through a 78L05). TPS2373 VC_OUT is a local
   unused net.
4. **A → E interface**: names become `PD_TPH_N`, `PD_TPL_N`, `PD_BT_N`, `PD_PG_N` (active low; default
   high when the primary is unpowered). `PD_PG_N` means "PD out of inrush and primary converter enabled"
   (taken from the PG/SS node through a 2N7002), not raw PG.
5. **A → B interface**: "PD power-good gating the UCC2897A start" is implemented as TPS2373 PG wired to
   UCC2897A SS/SD through 1 kΩ (TI Fig. 21); UCC2897A VDD, TPS2373 VC_IN and the isolator branch all run
   from block B's VB_PRI buck (VC_OUT unused); converter runs from 38.4 V (LINEUV off) to 57 V, starts at
   40.4 V, full power ≥ 40.8 V; not "42–57 V".
6. **R-32a / decision 4** stays as written (one digital isolator), with the note that PoE-loss is flagged
   on the primary by TPx de-asserting, not by PG.
7. **Block A contents**: "J1 RJ45 with integrated 4-pair PoE-rated magnetics" — confirmed (LPJK6078AHNL);
   the Bob Smith network is inside the jack, so there is no separate Bob Smith part on the sheet.

## Open issues

- **J1 current margin**: 1.0 A per CT vs 0.96 A worst unbalanced at Class 8 (4 %), rated at 25 °C, no
  derating curve. Fine at Class 6 (0.60 A). Fallback: LP6090ANL discrete (1.2 A, 187 stock) + shielded RJ45.
- **J1 CT pin mapping** read from drawing dots; confirm by continuity on the first part.
- **Hipot through the magjack's internal 1000 pF / 2 kV Bob Smith cap** when the shield is on GND
  (`A-shield-network.md`): risk if R-32's 1500 Vrms test is ever applied cable-to-secondary.
- **LT4321 stock** 98 from one maker (need 7); PD70224 (28) is the fallback.
- **PSMN040 VGS(th)** falls below LT4321's 2 V rule above ≈ 60 °C Tj; ADI uses the part in its own
  reference; accepted.
- Hot-swap inrush SOA for CBULK > 120 µF not specified.
- 802.3bt clause 145 not available; limits taken from the TI and ADI datasheets' summaries.

## Needs a user decision

1. Shield treatment: keep R-10's 1 nF / 1 MΩ to GND and accept the hipot risk through the magjack's
   internal Bob Smith cap for this uncertified spin (recommended), or move to discrete magnetics
   (LP6090ANL + plain RJ45 + our own Bob Smith cap rated for the hipot).
2. Accept LPJK6078AHNL's 4 % current margin at the Class 8 unbalance corner (recommended, since full
   performance is specified at Class 6), or take the discrete LP6090ANL route now.
