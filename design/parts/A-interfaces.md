# Block A — interfaces, loss budget, proposed architecture changes

Audits behind this file: `A-poe-magjack.md`, `A-shield-network.md`, `A-bridge-lt4321.md`,
`A-bridge-fets.md`, `A-tvs.md`, `A-pd-tps2373.md`, `A-pd-passives.md`, `A-isolator-iso7740.md`.
Datasheet list: `datasheets/sources-A.csv`.

## Signal chain

J1 LPJK6078AHNL (4 line-side CTs: pins 13/14/15/16) → `POE_CT12`, `POE_CT36`, `POE_CT45`, `POE_CT78`
→ LT4321 + 8 x PSMN040-100MSE (two ideal-diode bridges; EN from BZT52C27 + 100 kΩ, 1 MΩ to OUTN, and
held off by a BSS123 whenever the TPS2373 hot-swap is open, so the bridge is active only with CBULK
connected) → `VPRI` (= OUTP = TPS2373 VDD) and `VPD_N` (= OUTN = TPS2373 VSS) → SMCJ58A + 100 nF C_PD across
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
| VDD (1) | `VPRI` | converter input +, CBULK +, UCC2897A VIN through 100 kΩ (block B; 0 Ω VIN–VDD footprint DNP) — item 7 | VPRI is the bridge output; it is **not** switched |
| RTN (11, 12) | `VPRI_RTN` | converter input return, CBULK –, UCC2897A GND/PGND, primary FET source/sense return | hot-swap is in the return |
| VSS (4, 5, EP) | `VPD_N` | **nothing** in block B | VSS-referenced parts are block A only; block B must not tie anything to VSS |
| VC_OUT (14) | `VC_OUT` | **not used** — 1 µF to RTN only (block A part) | UCC2897A needs ≈ 32 mA bias (`B-interfaces.md`), over VC_OUT's 20 mA rec. sourcing (p.6) |
| VC_IN (15) | `VB_PRI` | block B's 14.3 V (13.9–14.8 V) LM5019 bias buck (also UCC2897A VDD); 100 nF local bypass is block A's. **VB_PRI must also supply the isolator branch, ≤ 15.3 mA** | §7.3.7 p.20: "If VC_OUT is not used, VC_IN must be connected to the low voltage bias supply of the PWM controller"; rec. max 15 V |
| PG (13) | `PD_PG` | → 1 kΩ (block B) → UCC2897A **SS/SD** (`UCC_SS`), with block B's CSS to RTN. Block A hangs the 2N7002 gate on the SS/SD side | TPS2373 Fig. 21 p.17; SS/SD < 0.4–0.6 V = UCC2897A shutdown |
| UVLO_SEL (16) | open | — | VC_OUT UV 7.35 V max < UCC2897A min stop 7.6 V |
| TPH/TPL/BT, APD, CLSx, DEN, REF, AMPS_CTL, MPS_DUTY | block A | — | — |

Block B constraints from the PD — all four **closed with block B on 2026-11-07** (`B-interfaces.md`,
`B-primary-power.md`, `B-controller.md`, `B-bias.md`):

1. **Input current ≤ 1.85 A** (TPS2373 RTN recommended max). B moved LINEUV to 40.4 V on / 38.4 V off
   (73.2 k / 2.37 k) and limits Class 8 output to 64.5 W, so input stays ≤ 1.85 A across the run range.
   Residual: worst tolerance corner 1.89 A at 37.6 V (91 % efficiency), just above 1.85 A rec. max and
   below the 1.9 A current-limit minimum (p.7), at the LINEUV-off edge only. Accepted.
2. **VPRI range**: B runs from LINEUV-off (38.4 V nom, ≈ 37.6 V worst) to 57 V; survives ≤ 96 V (SMCJ58A at its full 16 A rating, hot; ≈ 83 V at 6.5 A).
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
4. **VB_PRI**: 14.3 V nominal, 13.9–14.8 V worst case (block B, 0.5 % divider), under TPS2373 VC_IN's
   15 V recommended max. Budget 64 mA (48.5 mA UCC2897A at 620 kHz + 15.3 mA isolator primary), inside the
   LM5019's 100 mA rating. While SS/SD holds the UCC2897A off during inrush, B's idle load is ≈ 11 mA
   from VPRI at 30 V. The datasheet bound (review A-n2): inrush ends when IRTN falls below 65–99 % of the
   inrush limit (TPS2373 p.7), so a DC load must stay < 0.65 x 275 mA ≈ 179 mA at the end of inrush.
   11 mA (plus ≤ 0.57 mA through the UCC2897A VIN resistor, item 7) is far inside that (the earlier "≲ 30 mA allowance" was my own margin, not a datasheet figure).
5. Block B's Y-cap VPRI_RTN ↔ GND sits in parallel with the RJ45 shield network (1 nF ∥ 10 MΩ to GND);
   size it knowing that.
6. (Review A-n6, closed by block B) VB_PRI raised to 14.3 V: worst-case minimum 13.9 V clears the UCC2897A
   UVLO-on maximum of 13.2 V by 0.7 V. Block A: 78L05 dissipation at 14.8 V is 177 mW, TJ 118 °C
   (`A-isolator-iso7740.md`).
7. **UCC2897A VIN** (block B, review notes n3/n10): VIN → 100 kΩ → VPRI, keeping VIN in its 18–110 V
   recommended range; 0 Ω VIN–VDD footprint DNP. JFET draw ≤ (57 V – 0) / 100 kΩ = 0.57 mA during PD
   inrush, and it stops once VDD ≥ 12.7 V (B's buck holds 14.3 V). Against the 179 mA end-of-inrush bound
   this is negligible. Agreed by block A.

## What block E receives (from the isolator, 3.3 V CMOS, active low, default high)

**Polarity, stated once for every block (review A-M1): all four nets are active LOW. `PD_PG_N` LOW = good.
HIGH = not good, including "primary side unpowered" (ISO7740 default-high output).** Blocks C, E and F use
the same name and sense; the gateware rule is "`PD_PG_N` rising **or** `POE_LOSS_N` falling ⇒ PoE lost".

| Net | LOW means | HIGH means |
|---|---|---|
| `PD_TPH_N` | TPS2373 TPH asserted | TPH released, or primary unpowered |
| `PD_TPL_N` | TPL asserted | TPL released, or primary unpowered |
| `PD_BT_N` | 802.3bt (Type 3/4) PSE identified | not identified, or primary unpowered |
| `PD_PG_N` | PD out of inrush **and** UCC2897A SS/SD above the 2N7002 threshold (1.0–2.5 V) — primary converter enabled | inrush, PD fold-back, UCC2897A shut down/soft-stopped, or primary unpowered |

Decode TPH/TPL/BT per the truth table in `A-pd-tps2373.md`.

**Timing** (from PSE power-up, TPS2373 pp.7–8, UCC2897A §8.3.1.10, ISO7740 tDO):

1. t = 0: PSE applies operating voltage; TPS2373 UVLO rises (36.3–40 V), inrush starts. All four nets HIGH
   (primary side may already be powered from VB_PRI, but PG is low ⇒ 2N7002 off; TPx high-Z).
2. t = 78–87 ms: inrush delay ends (tINR_DEL) and PG releases; UCC2897A soft-start begins. `PD_PG_N`
   **falls** when SS/SD crosses the 2N7002 threshold, early in the soft-start ramp (block B's CSS sets the
   exact time; the converter's secondary output is not yet in regulation at that instant).
3. t = PG release + 20–28 ms (tTPLHBT, VC_IN already up): TPH/TPL/BT become valid. **Firmware reads the
   class ≥ 30 ms after `PD_PG_N` falls**, and re-reads on every change.
4. Loss/fault: PD fold-back pulls PG (and through block B's 1 kΩ, SS/SD) low within µs ⇒ `PD_PG_N` rises
   within µs. UCC2897A UVLO / LINEUV soft-stop discharges SS/SD; switching stops at 2.5 V and `PD_PG_N`
   rises when SS/SD falls below the 2N7002 threshold (after switching has stopped). Loss of VB_PRI ⇒ all
   four HIGH within tDO ≤ 0.3 µs of ISO7740 VCC1 UVLO (1.7–1.8 V).
5. **PoE input loss does not by itself release PG** (TPS2373 p.28: hot-swap opens, PG stays high-Z), so
   `PD_PG_N` stays LOW until the UCC2897A stops on LINEUV (38.4 V off, block B). TPH/TPL/BT return to
   high-Z when VDD–VSS < ~32 V (p.19). The secondary-side comparator (`POE_LOSS_N`, R-32a) stays the
   primary PoE-loss detector.

- Isolator VCC2 = `+3V3`, ≤ 3.2 mA (block C budget).

## Proposed changes to architecture

1. **Rail table**: replace `VPOE_A`, `VPOE_B` ("pair-set centre taps, before the bridges") by four nets
   `POE_CT12`, `POE_CT36`, `POE_CT45`, `POE_CT78` — each pair set has two centre taps, and the LT4321
   senses all four.
2. **Rail table**: `VPRI` is the bridge output (OUTP = TPS2373 VDD), **not** "after the PD hot-swap FET";
   the TPS2373 switches the return. `VPRI_RTN` = TPS2373 RTN (after the hot-swap). Add `VPD_N`
   (bridge OUTN = TPS2373 VSS, primary, block A only).
3. **Rail table**: add `VB_PRI` (block B's 14.3 V primary bias, RTN-referenced; = TPS2373 VC_IN) and
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
- **Shield-to-line isolation of the jack** is unspecified by the vendor; with the 10 MΩ shield bleed the
  internal 1000 pF sees ≤ 1.2 kVpk in an AC hipot (`A-shield-network.md`). Ask LINK-PP for its AC rating.
- **LT4321 stock** 98 from one maker (need 7); PD70224 (28) is the fallback.
- **PSMN040 VGS(th)** falls below LT4321's 2 V rule above ≈ 60 °C Tj. No ADI precedent (ADI's bridge FET
  is PSMN075-100MSE); accepted as a known margin because the LT4321 actively clamps off-state gates.
- Hot-swap inrush SOA for CBULK > 120 µF not specified.
- 802.3bt clause 145 not available; limits taken from the TI and ADI datasheets' summaries.

## Needs a user decision

1. Accept LPJK6078AHNL's 4 % current margin at the Class 8 unbalance corner (recommended, since full
   performance is specified at Class 6), or take the discrete LP6090ANL route now.

(The shield-treatment decision is closed: option E, 10 MΩ bleed, adopted per review A-M3.)

## Review response (design/gates/review-phase1-A.md, 2026-11-07)

| Finding | Response |
|---|---|
| A-M1 PD_PG_N polarity | Fixed on A's side: polarity and timing stated above ("What block E receives"). Blocks C/E/F adopting `PD_PG_N` (team lead). |
| A-M2 LT4321 enabled without CPORT | Fixed: added BSS123 that holds EN at OUTN whenever RTN–VSS > ~1–2.8 V (hot-swap open or in inrush), gate from RTN via 2.2 MΩ, BZT52C10 + 1 nF clamp/filter; zener network kept. Bridge active only with the hot-swap closed and CBULK across OUTP–OUTN (LT4321 p.7). Detection signature 24.38–24.87 kΩ. Residual: ≤ 0.4 ms of enabled-without-CBULK after an unexpected hot-swap opening. `A-bridge-lt4321.md` calc 3. |
| A-M3 hipot via internal Bob Smith cap | Fixed: option E, but **5 x 2.0 MΩ** 1206 (10 MΩ) instead of 4 x 2.49 MΩ, so each resistor stays ≤ 174 Vrms (< 200 V) with C_SH derated 30 %. Internal cap ≤ 1.2 kVpk, C_SH ≤ 1.23 kVpk, ESD 1.33 kV ⇒ 267 V per resistor, bleed τ 10 ms. AC hipot only. `A-shield-network.md`. |
| A-m1 RDEN trim direction | Fixed: signature reads high; trim down to 24.3 kΩ. `A-pd-tps2373.md`, `A-pd-passives.md`. |
| A-m2 PSMN040 "ADI reference" | Fixed: claim withdrawn (ADI's bridge FET is PSMN075-100MSE); margin stays logged. `A-bridge-fets.md`. |
| A-m3 TVS margin | Fixed: SMCJ58A-13-F (C135180) / DOWO SMCJ58A (C357975); ≈ 80 V at 6.5 A, ≤ 93.6 V at 16 A. `A-tvs.md`, references updated. |
| A-m4 C_SH bias / resistor pulse | Fixed by the A-M3 string: 1.33 kV derated peak, 267 V per resistor < 400 V overload. |
| A-m5 zener leakage hot | Fixed: 1 MΩ EN→OUTN; leakage tolerance 2.1 µA (21x spec); turn-on ≤ 32.8 V. Also covered by the BSS123. |
| A-n1 class entry with body-diode bridge | Accepted as noted; bench-check classification at the 14.5 V PI corner. |
| A-n2 "30 mA allowance" | Fixed: replaced by the datasheet bound (< 179 mA DC at end of inrush). |
| A-n3 BVDSS at 0 °C | Recorded: ≈ 96.9 V vs SMCJ58A ≤ 91.2 V at 0 °C. `A-bridge-fets.md`, `A-tvs.md`. |
| A-n4 barrier on J1 footprint | Added to `A-poe-magjack.md` open questions for phase 4. |
| A-n5 OCL under unbalance | Added to `A-poe-magjack.md` open questions; bench check. |
| A-n6 VB_PRI vs UCC2897A UVLO-on | Closed by block B: VB_PRI now 14.3 V (min 13.9 V > 13.2 V); item 6 above. |
| A-n7 E-phy-passives centre-tap question | Block E's file; answer is in `A-poe-magjack.md` pin map (MDCT1 pin 12, MDCT2 pin 6, LEDs 17–20). Team lead to close in `E-interfaces.md`. |
| A-n8, A-n9 | No action. |
