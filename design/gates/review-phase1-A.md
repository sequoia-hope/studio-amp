# Phase 1 independent review — block A (PoE input)

Date: 2026-11-07. Reviewer: independent (did not see the authors' conversation; judged the artifacts only).
Scope: `design/parts/A-*.md` (TPS2373-4, LT4321 + PSMN040-100MSE bridges, LPJK6078AHNL magjack, SMBJ58A,
ISO7740 + 78L05 + 2N7002, shield network, PD passives), their interfaces with blocks B and E, and the R-32
barrier across every block-A part that crosses it.
Method: re-read `tps2373.pdf`, `A-lt4321.pdf`, `A-psmn040-100mse.pdf`, `A-smbj58a-littelfuse.pdf`,
`A-iso7740.pdf`, `A-78l05-utc.pdf`, `A-2n7002-cj.pdf`, `A-lpjk6078ahnl.pdf`, `A-bzt52c24-mdd.pdf`,
`A-fojan-frc0805.pdf`, `A-uniroyal-1206w4.pdf`, `A-fh-1206b102k202.pdf` and the relevant parts of
`A-ucc2897a.pdf` (pdftotext); recomputed every calculation from the datasheet formulas with `intent.md`
conditions (71.3 W / 41.2 V Class 8, 57 V max, 55 °C air, 0 °C min); re-ran `jlc_parts.py show` on all 24
LCSC numbers (all orderable, lifecycle normal, stock ≥ build need, 2026-11-07).

## BLOCKER

None.

## MAJOR

### A-M1. `PD_PG` polarity conflict between block A and blocks E / C / F

- Files: `A-isolator-iso7740.md` (circuit), `A-interfaces.md` ("What block E receives"), vs
  `E-pinmap.md:21` (`PD_PG`, ball A2), `E-interfaces.md` ("Gateware drops HP_EN/LO_EN within µs of
  `POE_LOSS_N` or `PD_PG` falling"; F-notes "`PD_PG` low"), `F-interfaces.md:215`, `C-interfaces.md:155`
  ("VDRV_EN asserted after FPGA DONE, `PD_PG` and VBUS in range").
- Datasheet: TPS2373 p.4/p.17 (PG open-drain, active-high); ISO7740 Table 2 (default High with side 1
  unpowered); 2N7002 inverts.
- Problem: block A delivers `PD_PG_N`, **low = PD out of inrush and converter soft-start running**, high
  when the primary is dead. Blocks E/C/F still use `PD_PG` as **active-high** ("falling" = PoE loss,
  "PD_PG and VBUS in range" = good). Wired as the files stand, gateware would mute the headphone/line
  relays the moment the converter starts and would never see "good". Architecture's reconciliation
  section already names the net `PD_PG_N`; the E pinmap and the C/F gateware rules were not updated.
- Fix: one name and one sense everywhere. Recommend blocks E, C, F adopt `PD_PG_N` (low = good; the
  default-high isolator then reads "not good" with the primary unpowered, which is the safe reading) and
  rewrite the gateware rules as "`PD_PG_N` rising or `POE_LOSS_N` falling". Record it in `E-pinmap.md`.

### A-M2. LT4321 enable network violates the "10 µF when enabled" rule and ADI's enable sequencing

- File: `A-bridge-lt4321.md` calc 3 (BZT52C27 + 100 kΩ from OUTP into EN; EN̅ to OUTP).
- Datasheet: LT4321 p.7 "A 10 µF or greater capacitance **must** be connected across OUTP and OUTN pins
  when the LT4321 is enabled. In PoE applications it is sufficient for the CPORT capacitor to be connected
  by the PD interface controller's hot swap FET"; p.8–9 Figs 3–4 enable the bridge from the PD
  controller's PWRGD, i.e. only once the hot-swap has closed and CPORT is across OUTP–OUTN.
- Problem: the zener network enables at OUTP ≥ 32.6 V (guaranteed; ≈ 30.6 V typical), which is **below**
  the TPS2373 UVLO rising threshold (36.3–40 V, p.8), and it stays asserted when the hot-swap opens on
  UVLO falling (30.5–33.6 V). In both states (PSE ramp before inrush; brownout/shutdown) the bridge is in
  ideal-diode mode with only the 0.1 µF C_PD across OUTP–OUTN — the stated "must" is violated. The load in
  those states is ≈ 1 mA, so the practical risk is gate-drive chatter rather than damage, but the datasheet
  gives no behaviour for it and the audit does not analyse it. The audit's own citation of Figs 3–4 ("enabled
  after detection and classification are complete") omits that ADI enables *after inrush*, not before.
- Fix (either): (a) obtain and record ADI's statement of what the 10 µF protects and that enable-with-C_PD
  during the PSE ramp and after hot-swap opening is acceptable; or (b) gate EN on hot-swap state: keep the
  zener/100 kΩ pull-up to EN and add a 100 V small-signal N-FET (e.g. BSS123) EN→OUTN whose gate senses
  RTN–VSS through ≥ 2.2 MΩ (keeps the detection signature within 1.1 %) with a 10 V zener/100 nF clamp to
  VSS. RTN–VSS > ≈ 2 V (hot-swap open, or inrush) ⇒ FET on ⇒ EN = OUTN ⇒ disabled; hot-swap closed
  (RTN–VSS ≤ 0.38 V at 1.9 A × 0.2 Ω) ⇒ FET off ⇒ zener network enables above 32.6 V as now. Inrush then
  runs through body diodes (335 mA × ≈ 1.4 V ≈ 0.5 W for ≤ 13 ms with 61 µF — negligible), which is what
  ADI's Figs 3–4 do. A simple resistive sense of RTN into EN̅ is **not** acceptable: during detection
  RTN ≈ VDD, so anything under ≈ 1 MΩ from RTN to VSS parallels RDEN and spoils the 23.75–26.25 kΩ window.

### A-M3. R-32 hipot path through the magjack's internal 1000 pF / 2 kV Bob Smith capacitor — open user decision; a cheaper option exists

- Files: `A-shield-network.md`, `A-poe-magjack.md` fine print, `A-interfaces.md` "Needs a user decision 1".
- Datasheet: LPJK6078AHNL sheet 1 schematic (4 × 22 nF/100 V + 75 Ω → 1000 pF/2 kV → SHIELD; isolation
  rated "PHY side to line side 1500 Vrms" only).
- Problem (confirmed by recomputation): with R_SH = 1.02 MΩ, at 50/60 Hz |Xc(1 nF)| = 2.65 MΩ ≫ 1 MΩ, so
  in a cable-to-secondary 1500 Vrms test the shield sits at GND and the internal 1000 pF sees the full
  2121 Vpk against a "2KV" mark that is almost certainly a DC rating. The audit's options A–D are correct
  but miss the simplest one.
- Fix (option E, recommended for the user decision): raise R_SH to ≈ 10 MΩ as **4 × 2.49 MΩ 1206 in
  series** (185 Vrms each in the test, inside the 200 V working rating of `A-uniroyal-1206w4.pdf` p.5).
  Then Z_SH = (1 nF ∥ 10 MΩ) ≈ 2.56 MΩ∠−75°, the 2121 Vpk divides ≈ 1.1 kVpk across the internal cap and
  ≈ 1.05 kVpk across C_SH — both inside 2 kV even with 30 % DC-bias loss (the split moves to ≈ 60/40 %,
  ≈ 1.3 kVpk). ESD behaviour is unchanged (C_SH still takes the charge, A-m4 below), static bleed
  τ = 1 nF × 10 MΩ = 10 ms is still fast, and block B's Y-cap sizing is unaffected. Still ask LINK-PP for the
  internal cap's AC rating; still log that the shield-to-line isolation of the jack is unspecified.

## MINOR

### A-m1. RDEN trim direction is backwards (`A-pd-passives.md` fine print, `A-pd-tps2373.md` §7.4.4 note)
TPS2373 p.24: the bridge's incremental resistance is **in series** with RDEN ∥ (internal loading), so a
body-diode bridge (≈ 2 × 400 Ω at 100–400 µA, higher than Schottkys) makes the PI signature read **high**,
not low; the TPS2373's internal loading partially compensates downward. Fix: expect "reads high"; the
remedy is one E96 step **down** (24.3 kΩ), not up. Keep the first-board PoE-tester check.

### A-m2. Wrong justification for the PSMN040-100MSE VGS(th) margin (`A-bridge-fets.md` calc 2, header)
LT4321 p.12 (TA03, 70 W): the eight **bridge** FETs are PSMN075-100MSE; the single PSMN040-100MSE is the
LT4275 **hot-swap** FET. "ADI's own reference uses this part" as a bridge FET is not true, so it cannot carry
the "VGS(th) min crosses 2 V at ≈ 60 °C Tj" risk (recomputed: 2.3 V at 25 °C → 1.0 V at 175 °C gives
2.0 V at 60 °C). The risk stays logged as is; fix the text. If an ADI precedent is wanted, check PSMN075-100MSE's
threshold spec (not in `datasheets/`).

### A-m3. TVS clamp margin 3–4 %: SMCJ58A buys ≈ 13 V for one footprint size (`A-tvs.md`)
SMBJ58A (Littelfuse p.2): VC 93.6 V at 6.5 A; +0.103 %/°C ⇒ 97.0 V at TJ 60 °C against 100 V abs max on
TPS2373 VDD/RTN, LT4321 OUTP and PSMN040 VDS. SMCJ58A has the same VBR (64.4–71.2 V) and VC 93.6 V at
16.1 A, i.e. ≈ 80 V at 6.5 A. In stock and already in `sources.csv`: `C357975 SMCJ58A (DOWO, SMC): extended,
5908` and `C135180 SMCJ58A-13-F (Diodes, SMC): extended, 2906`, both lifecycle normal 2026-11-07. Recommend
the swap; block B already uses the SMC body.

### A-m4. Shield network: C_SH DC-bias not derated and resistor pulse rating not established (`A-shield-network.md` calc 1)
8 kV / 150 pF into a 1 nF 2 kV X7R: at ≈ 1 kV the class-II dielectric typically loses 20–30 %, so the peak is
≈ 1.3 kV, not 1.04 kV, and each 510 kΩ 1206 sees ≈ 650 V against a 400 V overload rating; Uni-Royal gives no
pulse-energy rating. Energy (≈ 0.4 mJ per resistor, 1 ms) is small, so this is a margin question. Fix: the
4-resistor string of A-M3 also solves this (≈ 330 V each); optionally 2 × 1 nF 2 kV in parallel.

### A-m5. LT4321 off-state during classification depends on 25 °C zener leakage (`A-bridge-lt4321.md` calc 3)
BZT52C27 IR ≤ 0.1 µA at 21 V is specified at 25 °C (`A-bzt52c24-mdd.pdf` p.3). VEN = IR × Rpd,max (310 kΩ)
= 0.03 V at 25 °C; a hot re-plug (zener at 55–65 °C, leakage ×10–20) puts VEN at 0.3–0.6 V against
VIL min 0.5 V, i.e. undefined, and if the LT4321 wakes during class its 0.5–0.8 mA lands on top of a
26.5–29.3 mA class-3 signature (window 26–30 mA). Fix: add 1 MΩ EN→OUTN. Rpd becomes ≤ 237 kΩ (leakage
tolerance ≥ 2.1 µA, 21× the spec) while turn-on only moves from 32.6 V to ≈ 32.8 V (28.35 + 2.6 × (1 + 100/138)).

## NOTE

- A-n1. Classification entry margin with a PN (body-diode) bridge: PI class minimum 14.5 V − 2 × ≈ 0.7 V
  (PSMN040 body diode at 40 mA, 0 °C) ≈ 13.1 V vs VCL_ON max 13.0 V (TPS2373 p.7). TI treats PN bridges as
  normal (§8.2.2.1), so accepted; bench-check class at the 14.5 V PI corner.
- A-n2. "≲ 30 mA allowance" for block B's draw during inrush (`A-interfaces.md` item 4, `B-controller.md`)
  is not a datasheet figure. TPS2373 p.7: inrush terminates when IRTN falls below 65–99 % of the inrush
  limit ⇒ the real bound is a DC load < 0.65 × 275 mA ≈ 179 mA at the end of inrush. 10 mA is fine; fix the cite.
- A-n3. PSMN040 BVDSS at 0 °C: interpolating 100 V (25 °C) / 90 V (−55 °C) gives ≈ 96.9 V; SMBJ58A clamp at
  0 °C ≈ 91.2 V. OK (≈ 6 V); `A-bridge-fets.md` says "OK at ≥ 0 °C" without the numbers — record them.
- A-n4. Barrier on the J1 footprint: shield tabs and LED pins 17–20 (secondary) share the jack with CT pins
  13–16 (primary). Phase 4 must check tab/LED-pin to CT-pin spacing against the R-32 keepout, and the
  vendor's 1500 Vrms is stated PHY↔line only (shield↔line, LED↔line unspecified).
- A-n5. Magjack OCL DC-bias tolerance (350 µH at 14 mA, 120 µH at 23 mA, sheet 1) vs 802.3bt pair-current
  unbalance at Class 8 is unchecked (clause 145 unavailable). Add to the open questions.
- A-n6. Cross-block: VB_PRI 13.5 V vs UCC2897A UVLO-on 12.2–13.2 V (`A-ucc2897a.pdf` p.7) leaves 0.3 V
  before LM5019 set-point tolerance. Block B's item; flagged for the block B reviewer. Block A is unaffected
  (VC_IN ≥ 8.5 V needs only 8–9 V).
- A-n7. `E-phy-passives.md:44` still asks where the magjack's PHY-side centre taps and LEDs land;
  `A-poe-magjack.md` answers it (MDCT1 pin 12, MDCT2 pin 6, LEDs 17–20). Close it in `E-interfaces.md`.
- A-n8. Footprints checked against drawings: TPS2373 RGW0020B (EP 2.2 ± 0.1 mm; audit correctly rejects
  KiCad's EP 3.15 variant), LT4321 UF16 (EP 2.15), LFPAK33/SOT1210, DO-214AA, SOIC-16 DW 7.5 mm, SOT-89
  O-G-I for -AB3-R, SOT-23 G-S-D. All match. PSMN040-100MSE**X** is the reel suffix of the audited die.
- A-n9. Recomputed and agreed (no change): Class 8 current 1.731 A; hot-swap 0.60 W max, TJ 78 °C;
  bridge 0.088 / 0.110 / 0.197 W; FET VF 25–57 mV inside 20–70 mV; inrush 12.6 ms for 61 µF, 0.10 J;
  C_PD 76–127 nF corner (86–116 nF at 0–55 °C) + ≤ 0.6 nF TVS; class-resistor 98.6 / 68.8 mW on 1/8 W;
  RMPS 117 mW; isolator branch 15.3 mA, 78L05 157 mW, TJ 111 °C; ISO7740 ICC1 ≤ 7.8 mA (VI = 0 V, p.13),
  ICC2 ≤ 3.2 mA; ESD charge-share 1.04 kV at nominal C_SH, τ 1 ms; EN turn-on 32.6 V. TPH/TPL/BT truth
  table matches Table 2/3. UVLO_SEL open is right (7.35 V < 7.6 V). All 24 LCSC lines re-verified; every
  datasheet is in `sources.csv`.

## Verdict

**Pass with conditions**: no blocker; A-M1 (net polarity, blocks E/C/F) and A-M3 (user decision, option E
recommended) must be closed before phase 2, and A-M2 needs either ADI's written acceptance or the EN gate.
