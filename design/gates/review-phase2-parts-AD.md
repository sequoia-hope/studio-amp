# Phase 2 parts cross-check, blocks A–D — independent review

Date: 2026-11-08. Reviewer did not see the authors' conversation.
Inputs: `design/renders/netlist.xml` (traced pin by pin, labels not trusted), `design/renders/bom-sch.csv`,
`design/parts/{A,B,C,D}-*.md` (superseded sections ignored), `design/datasheets/*.pdf` (pdftotext / rendered pages),
`hw/satellite/a/lib/studio_{A,B,C,D}.kicad_sym` and `.pretty`, `design/intent.md`.
Scratch scripts: `<session scratchpad>/xchk-AD/` (nl.py, sym.py, fp.py, iso.py).

## Findings

### BLOCKER

None.

### MAJOR

**B-M1 — T201 footprint `studio_B:Wurth_750343576_ER19` is the mirror image of the datasheet land pattern.**
Refs T201; nets VPRI, SW_PRI, SW_SEC, SR_FWD_D, Net-(D202-A). Datasheet we-750343576.pdf p.1,
"Recommended Land Pattern" (top view): pin 1 upper-left, 6 lower-left, 11 upper-right, 7 lower-right.
Footprint (KiCad, y positive = down): pad 1 at (−9.05, +7) = lower-left, 6 at (−9.05, −7) = upper-left,
11 at (+9.05, +7) = lower-right, 7 at (+9.05, −7) = upper-right. `gen/studio_B_lib.py` line 218 comments
"bottom to top (y down = +)", i.e. the pad-side (bottom) view on the left of p.1 was copied instead of the
land pattern. A mirrored pattern cannot be matched by any rotation of the part: placed one way, physical
pins 1–6 (N5, N1, N2 — primary) land on pads 7/8/10/11 (secondary nets) and the barrier is bridged; placed
the other way the columns are right but every winding is reversed (electrically harmless, since all five
reverse together). There is no pin-1 mark on silk or fab to disambiguate. Pad size 3.13 × 1.89, pitch 2.8,
row centres ±9.05 (21.23 − 3.13 = 18.10) and the 7/8/10/11-only right column are all correct.
Fix: negate the pad y coordinates (1 at (−9.05, −7) … 6 at (−9.05, +7); 11 at (+9.05, −7), 10 at
(+9.05, −4.2), 8 at (+9.05, +4.2), 7 at (+9.05, +7)), add a pin-1 marker, regenerate. The symbol and
netlist already follow the datasheet dots (2, 3 → VPRI; 4, 5 → SW_PRI; 7 (dot) → SW_SEC; 10–8 series;
11 → SR_FWD_D; 1 (dot) → D202 anode; 6 → VPRI_RTN) and need no change.

**D-M1 — Short-detector window ladder does not give the audited ±1.0 V threshold.**
Refs R448/R449/R450 (woofer), R548/R549/R550 (tweeter); nets SDH_x / SDL_x. 6.2 k / 12 k / 6.2 k from
3V3_A gives SDH = 3.3 × 18.2/24.4 = 2.46 V and SDL = 0.84 V, a ±0.81 V window about the 1.65 V bias
(VSDB 20 k/20 k is correct), not the 2.65 / 0.65 V in `D-short-detect.md`. The audit lists both the
2.65/0.65 V targets and the 6.2/12/6.2 k parts; they are inconsistent and the schematic followed the parts.
Consequences: trip slew 17 V/µs (not 21), lead-open trip from ≈ 12.1 A (0.81 V × 700 nF / 47 ns), below
the 13.0 A legitimate peak; nuisance margin vs the normal worst sum (0.21–0.27 V) falls from 3.7× to ≈ 3×.
Fix: 4.99 k / 15 k / 4.99 k (→ 2.641 / 0.659 V; 15 k C25756 already in the BOM, 4.99 k basic
0402WGF4991TCE) on both sheets and correct the audit's parts row — or, if 0.81 V is intended, update the
audit's threshold, slew and lead-open figures.

### MINOR

- **B-m1** — High-voltage 0603 resistors where the audit says 0805 or where the stress is near the rating.
  R206 73.2 k (LINEUV top, 57 V; `B-controller.md` line 96 specifies 0805), R221 267 k (LM5019 RON, ≈ 57 V),
  R224 237 k (UVLO top, 55 V), R218 100 k (UCC2897A VIN, ≈ 45 V), R208 47 k and R209 470 k (LINEOV node A:
  57 V steady, ≈ 150 V in the DMAX-at-57 V transient per the audit's review n2). Uni-Royal 0603 is rated
  75 V working / 150 V overload (uniroyal-0402wgf.pdf p.4), so steady state is inside the rating (76 %),
  but R208/R209 touch the overload figure on the transient. Fix: 0805 for R206, R208, R209 (and R221/R224 for
  margin) or record the 75 V acceptance in the audits.
- **B-m2** — `Wurth_750343576_ER19` has no pin-1 marker on F.SilkS/F.Fab (compounds B-M1).
- **C-m1** — U303/U304 (TPS62A02A) feed-forward cap footprint missing. `C-3v3-1v1-bucks.md` reserves a DNP
  cap across the top FB resistor; Net-(U304-FB) has only R315 100 k / R316 84.5 k (same for U303). Not
  functional (FPWM, tps62a02a p.3). Fix: add a DNP 0603 across R316/R313, or strike the audit line.
- **C-m2** — U313 (+5V_A TPS7A4901) CIN C358 = 10 µF 25 V X7R 1206 at 15 V bias (≈ 5 µF effective, still
  ≥ 2.2 µF minimum, tps7a49 p.5). Matches the audit; optionally the 50 V UMK325AB7106KM-P already used.
- **C-m3** — U305 NR/SS C320 1 µF 50 V X5R 0603 sits at the TPS7A94 1 µF floor (tps7a94 p.5); only noise
  and start-up depend on it. Optional 2.2 µF.
- **D-m1** — `IGB070S10S1_PG-TSON-4` footprint is NSMD with one shrunk paste aperture; igb070s10s1.pdf Fig. 2
  p.14 is solder-mask-defined with split apertures (0.4-tall mask windows on the 0.605 rows; stencil
  3 × 0.93 × 0.36 on pad 3, 3 × 0.76 × 0.31 on pad 2, 2 × 0.88 × 0.36 on pad 4, 1 × 0.71 × 0.36 on pad 1,
  0.13 mm). Positions and copper sizes match (rows ±1.2025, pin 1 bottom-left). Fix before phase 6:
  per-pad mask margin −0.1 on the 0.605 rows (or draw the Fig. 2 windows) and paste primitives per the stencil.
- **D-m2** — Post-filter divider TCR mismatch: R420/R441/R520/R541 140 k = RT0603**BRE**07140KL (50 ppm/°C)
  vs partners R421/R442/R521/R542 10 k = RT0603**BRD**0710KL (25 ppm). `D-postfilter-sense.md` asks
  0.1 % / 25 ppm for both; ratio drift up to 75 ppm/°C. RT0603BRD07140KL exists. Fix: swap if stocked, else
  record 50 ppm in the audit.
- **D-m3** — `D-gan-fet.md` pin/row text is wrong (footprint right): it says "pin 2 = drain (top row), pins 3–4 =
  source". igb070s10s1.pdf Fig. 1 p.13 / Fig. 2 p.14: top full row = pin 3 (S), middle bar = pin 2 (D),
  bottom-left = pin 1 (G), bottom-right = pin 4 (S). Footprint and netlist (Q401.2 VBUS, Q402.2 SW, 3/4
  SW/GND) are correct. Fix the audit so phase 6 does not "correct" the footprint.

### NOTE

- **A-n1** — J101 CT-to-pin mapping (13 → CT12 / IN12, 14 → CT36, 15 → CT45, 16 → CT78) matches
  `A-poe-magjack.md`, which itself reads it off the sheet-1 junction dots and asks for a continuity check on
  the first part. Not independently verifiable from the drawing text; keep the bring-up item.
- **A-n2** — Stock `LFPAK33` footprint for Q101–Q108 (5 pads: 1–3 S, 4 G, 5 D) matches the symbol; the
  audit's "check against the SOT1210 drawing" is still open for phase 4.
- **B-n1** — UCC2897A GND (8) and PGND (13) are one net (VPRI_RTN) in the schematic; the audit's single-point
  GND–PGND join at the IC (§8.3.1.6) has no net-tie part and must be done in layout. Same for NCP4306 GND
  Kelvin to the SR source pad.
- **B-n2** — 74LVC2G08 (U259): KiCad's symbol puts 2Y on pin 3 and 1Y on pin 7, matching the Nexperia DP
  pinout (74lvc2g08-nexperia.pdf p.3: 1A 1, 1B 2, 2Y 3, GND 4, 2A 5, 2B 6, 1Y 7, VCC 8). ACF_PULSE is on
  pin 3 = 2Y with 2A = +3V3, 2B = DRV_FWD divider; gate 1 inputs grounded, 1Y open. Correct, though it
  reads as if the grounded gate drove ACF_PULSE.
- **B-n3** — KiCad `LM5017MR` symbol (used for U202/U251 LM5019 and U306/U310 LM5017) spells pin 3 "ULVO";
  number and net are right. LM5019 on `SOIC-8-1EP_3.9x4.9mm … EP2.95x4.9mm` matches the DDA pad (4.89 × 2.95).
- **B-n4** — T201 LCSC field "HAND": consistent with `B-transformer.md` (not on LCSC; Würth/Digi-Key sample).
- **C-n1** — U302 ST (`PWR_FROM_POE`) has only the R311 100 k pull-up and no destination (audit: optional).
- **C-n2** — LM5013 PGOOD pull-up R309 sits after the R308 0 Ω link (TPS2116 VIN1 net); lifting R308 at bring-up
  makes PG_5V read "not good". Expected; record it.
- **C-n3** — R346/C347 snubber DNP confirmed; AN_OFF NMOS not fitted (audit: only if block E assigns a pin).
- **D-n1** — PWM pull-downs R401/R422/R501/R522 are on the FPGA side of the 100 Ω (net PWM_x_y), not at the
  LMG1210 pin as worded; electrically equivalent.
- **D-n2** — INA241 IN+ (pin 8) is on the inductor-side Kelvin tap, IN− on the output side, all four legs
  alike: positive output = current bridge → speaker. Record for the gateware sign.
- **D-n3** — Snubbers (C412/R410, C437/R431, C512/R510, C537/R531) and the 10 pF input filters are DNP in
  netlist and BOM, as audited.

## Checked and found correct

### Block A (poe_in)
- **Isolation**: BFS over the netlist from VPRI_RTN with T201, U203, U103, C223/C224, J101 excluded reaches 85
  primary nets and 110 components and none of GND, +3V3, VBUS, VSR, +5V. The only straddling parts are
  T201, U203 (LTV-217), U103 (ISO7740), C223/C224 (Y, VPRI_RTN ↔ GND) and J101 (CT pins primary, PHY/LED
  pins secondary). VPD_N carries nothing from block B.
- **Symbols vs datasheet**: TPS2373-4 RGW (tps2373.pdf p.4: VDD 1, DEN 2, CLSA 3, VSS 4/5, CLSB 6, REF 7,
  AMPS_CTL 8, MPS_DUTY 9, APD 10, RTN 11/12, PG 13, VC_OUT 14, VC_IN 15, UVLO_SEL 16, TPL 17, TPH 18, BT 19,
  NC 20, EP 21 = VSS); LT4321 UF (A-lt4321.pdf p.2: TG36 1, IN36 2, IN45 3, TG45 4, TG78 5, IN78 6, BG78 7,
  BG45 8, OUTN 9, EN̅ 10, EN 11, OUTP 12, BG36 13, BG12 14, IN12 15, TG12 16, EP 17 = OUTN); ISO7740 DW
  (A-iso7740.pdf p.6: VCC1 1, GND1 2/8, INA–IND 3–6, NC 7, GND2 9/15, EN2 10, OUTD–OUTA 11–14, VCC2 16);
  78L05G-AB3-R (A-78l05-utc.pdf p.1: O-G-I = 1 VISO_P5V, 2 RTN, 3 VB_PRI); PSMN040-100MSE LFPAK33 (1–3 S,
  4 G, 5 D); LPJK6078AHNL (pins 1–20 + SH per sheet 1).
- **Footprints**: `TI_RGW0020B_VQFN-20` — 20 pads 0.75 × 0.31 at ±2.325 (the (4.65) on p.41 is
  centre-to-centre), 0.65 pitch, CCW from pin 1 top-left, EP 2.2 with 3 × 3 vias on 0.85 and four 0.98 paste
  windows: matches tps2373.pdf p.41–42. `LINKPP_LPJK6078AHNL_RJ45_PoE` — every coordinate matches sheet 2
  "Suggested PCB Layout": shield Ø1.57 at (0, ±8.15) (16.30), posts Ø3.20 at (3.18, ±6.35) (12.70), CT pins
  13–16 at x 9.81/11.31 (6.63 + 3.18, +1.50), y ±5.59 (11.18), signal rows at x 18.42/20.96, 2.03 pitch,
  1.02 stagger, pin 1 bottom / 6 top, 7 bottom / 12 top, LEDs at x 23.5, y ±6.09 and ±3.55, 20 top / 17
  bottom; 16 × Ø0.89, 4 × Ø1.03 pins.
- **Bridges**: high-side Q101/103/105/107 D = VPRI, S = CTxx, G = TGxx; low-side Q102/104/106/108 D = CTxx,
  S = VPD_N, G = BGxx; CT12 → IN12, CT36 → IN36, CT45 → IN45, CT78 → IN78. LT4321 EN̅ = VPRI (OUTP),
  EN = Q109 drain with R106 100 k ← D101 BZT52C27 (K at VPRI) and R107 1 M → VPD_N; Q109 BSS123 gate ← R108
  2.2 M 0805 ← VPRI_RTN, D102 BZT52C10 (K gate, A VPD_N), C102 1 n; D103 SMCJ58A K = VPRI, A = VPD_N;
  C103 100 n 100 V 0805 X7R VPRI–VPD_N (the single C_PD).
- **TPS2373**: R109 24.9 k VDD–DEN; R110 63.4 Ω CLSA, R111 90.9 Ω CLSB, R112 49.9 k REF, R113 1.3 k 1206
  AMPS_CTL all to VSS; APD → RTN; UVLO_SEL, MPS_DUTY, NC open; C104 1 µ VC_OUT–RTN; VC_IN = VB_PRI with
  C105 100 n; PG → PD_PG → R217 1 k → UCC_SS (also Q110 gate); TPL/TPH/BT → ISO INB/INC/INA with R115/R114/R116
  10 k to VISO_P5V. PD_PG_N polarity: SS high → Q110 on → IND low → OUTD low = good.
- **Isolator chain**: VB_PRI → C107 330 n → 78L05 → VISO_P5V → C108, C109 → VCC1; GND1 = RTN; EN2 = VCC2 =
  +3V3 (C110); OUTA–D → PD_BT_N, PD_TPL_N, PD_TPH_N, PD_PG_N (R802–R805 at block E). Shield: J101.SH →
  C101 1 n 2 kV ∥ R101–R105 5 × 2.0 M 1206 → GND.
- **MPN/LCSC**: every block A part matches its audit (LPJK6078AHNL C49274795, LT4321IUF#TRPBF C580183,
  TPS2373-4RGWR C470963, ISO7740DWR C529547, 78L05G-AB3-R C71136, PSMN040-100MSEX C458214, BSS123 C78962,
  2N7002 C8545, BZT52C27 C173421, BZT52C10 C173431, SMCJ58A-13-F C135180, 1206B102K202NT C9196, FRC1206F2004TS
  C2907380, and the R/C lines of `A-pd-passives.md` / `A-bridge-lt4321.md` / `A-isolator-iso7740.md`).

### Block B (iso_dcdc, iso_aux)
- **Symbols vs datasheet**: UCC2897A PW (ucc2897a.pdf p.3–5, all 20 pins incl. NC 2/20); NCP4306 TSOP-6
  "D" pinout option (ncp4306.pdf Table 2 p.4: DRV 1, GND 2, CS 3, MIN_TON 4, MIN_TOFF 5, VCC 6; ordering table
  p.2 lists NCP4306DADZZDASNT1G); 750343576 (p.1 schematic: N1 2•–4, N2 3•–5, N5 1•–6, N3 7•–10, N4 8•–11);
  LM5019 on KiCad LM5017MR (lm5019.pdf p.3: RTN 1, VIN 2, UVLO 3, RON 4, FB 5, VCC 6, BST 7, SW 8, EP RTN);
  LTV-217 on PC817 (ltv-217.pdf p.2: 1 A, 2 K, 3 E, 4 C); INA281 DBV (ina281.pdf p.3: OUT 1, GND 2, IN+ 3,
  IN− 4, VS 5); HT7550-1 SOT-89 (ht7550-umw.pdf p.2: 1 GND, 2 VIN, 3 VOUT); SN74LVC1G123 DCT (p.3: A 1, B 2,
  CLR 3, GND 4, Q 5, Cext 6, Rext/Cext 7, VCC 8); 74LVC2G08 DP (see B-n2); 74HC4017, LVC1GU04, LVC1G08,
  LM393, TL431 DBZ, BAS316, BAV21, US1G, FDMS86200 / BSC500N20NS3 on the 1–3 S, 4 G, 5 D TDSON symbol,
  IRFR6215 on IRF9540N (1 G, 2 D, 3 S = DPAK).
- **Transformer wiring**: N1 ∥ N2 (2 + 3 → VPRI dots, 4 + 5 → SW_PRI); N3 + N4 in series via 10–8, 7 (dot) →
  SW_SEC → L202, 11 → SR_FWD_D (forward SR Q203 D), i.e. 4 T : 8 T = 1:2; N5 1 (dot) → D202 anode, 6 → RTN.
  With the primary dots at VPRI the secondary dot (7) goes positive in the on-time, so Q203 (source GND) on
  pin 11 is the forward SR and Q204 on SW_SEC the freewheel SR, and N5 carries +Vin in the on-time for the
  LINEOV average. Polarities correct (see B-M1 for the footprint).
- **UCC2897A**: VIN ← R218 100 k ← VPRI (R219 0 Ω DNP to VB_PRI); RDEL 4.53 k, RON 31.6 k, ROFF 14.3 k,
  RSLOPE 316 k to RTN; VREF C201 220 n; SYNC ← R260 100 Ω ← LVC1G08, R261 10 k to RTN, no cap; CS ← R205
  1.00 k ← CS_PRI, C204 82 p C0G; FB: R211 4.99 k to VREF, C206 6.8 n, opto collector; SS/SD C205 1 µ; AUX →
  C208 100 n → Q202 gate, D201 BAS316 (A gate, K RTN), R215 10 k; OUT → R213 2.2 Ω → Q201 gate, R212 10 k to
  RTN, R214 10 k gate–source; PVDD C203 10 µ + R220 0 Ω; VDD = VB_PRI, C202 1 µ; LINEUV 73.2 k / 2.37 k;
  LINEOV: D202 BAV21W → node A, R208 47 k to RTN, R209 470 k → LINEOV, R210 23.7 k ∥ C207 47 n; GND/PGND RTN.
- **Primary power**: Q201 D = SW_PRI = T201 4/5, S = CS_PRI → R216 68 mΩ 2512 → RTN; clamp C209/C210
  2 × 100 n 250 V from SW_PRI to Q202 drain, Q202 S = RTN; C211–C213 3 × 4.7 µ 100 V X7S, C214 100 n 100 V,
  C215 47 µ 100 V (+ on VPRI).
- **Secondary**: Q203/Q204 S = GND; U204/U205 CS on the respective drains, DRV direct to gates, VCC = VSR with
  C225/C226 1 µ, R227/R228 750 Ω MIN_TON (≈ 126 ns), R229/R230 2 k MIN_TOFF (≈ 256 ns); snubbers C227/C228
  22 p 250 V + R231/R232 47 Ω 2512 to GND; RCD-Z clamps D203/D204 US1G (A on drain) → C229/C230 10 n 250 V +
  D205/D206 SMBJ130A (K at node) to GND; L202 68 µ → VBUS_CONV; C231–C236 6 × 4.7 µ 100 V; R233 30 mΩ
  VBUS_CONV → VBUS; D208 SMCJ51A K = VBUS; C241–C246 1000 µ 63 V (+ C247 DNP).
- **Feedback**: CV U208 REF ← R244 47.5 k 0.1 % 0805 / R245 2.61 k 0.1 % → 47.90 V; comp R246 115 k + C240
  4.7 n K–REF; opto R247 499 Ω from VSR, R248 1 k across the LED, cathode = U208 K; CC U207 via D207 BAS316
  (A on OPTO_K); INA281 IN+ = VBUS_CONV, IN− = VBUS, VS = VSR (C238), OUT → R234 100 Ω / C237 470 n →
  R237 4.99 k → U207 REF, R238 88.7 k, R239 4.22 k / R240 5.9 k via Q205/Q206 AO3400A (ILIM_SEL0/1, R241/R242
  100 k pull-downs), comp R243 100 k + C239 10 n; IBUS_SENSE R235 200 k / R236 100 k.
- **Bias bucks**: U202 VB_PRI: R222 107 k / R223 10 k → 14.33 V, UVLO 237 k/10 k, RON 267 k, ripple R226 200 k /
  C216 1 n / C217 100 n, L201 330 µ, C218 1 µ VCC, C219 10 n BST, C220 10 µ out, C221 1 µ 100 V + C222 100 n
  100 V in, EP RTN. U251 VSR: 71.5 k / 10 k → 9.98 V, UVLO 51.1 k/10 k, RON 280 k, R256 82 k / C256 1 n /
  C257 100 n, L251 220 µ, C255 10 µ, C251/C252 in, EP GND.
- **Sync clock (iso_aux)**: HT7550 VB_PRI → V5_CLK (C258/C259); LVC1GU04 Pierce with Y251 7.3728 MHz, R257 1 M,
  R258 1 k, C260/C261 33 p; 74HC4017 CP0 ← Y, CP1 and MR → RTN, Q1 → LVC1G08 A, CO → LVC1G123 A (falling
  trigger), B and CLR high, R259 10 k / C264 470 p, Q → CLK_OK → LVC1G08 B; LVC1G08 VCC = VREF_ACF (C266).
- **POE_LOSS_N**: R263 150 k 0.1 % 0805 / R264 10.0 k 0.1 % / C267 33 n → LM393 A−; TL431 U258 via R262 3.9 k →
  R265 10 k → A+, R266 866 k hysteresis; out R267 3.3 k pull-up → R268 10 k → Q251 2N7002 gate, R269 15 k;
  drain = POE_LOSS_N; LM393 B: + GND, − VREF_D, out open. ACF_PULSE: DRV_FWD → R270 10 k / R271 4.99 k →
  2G08 2B, 2A = +3V3, 2Y → ACF_PULSE.
- **Footprints**: `L_SXN_SM5845` 2.15 × 1.7 at ±1.675 (table p.2: H 5.5, I 2.15, J 1.7); `L_Sumida_CDRH127`
  2.9 × 5.4 at ±4.95 (p.1 land pattern: 5.4 wide, 2.9 deep, 12.8 outer; 7.0 band is silk); T201 pad geometry
  (see B-M1 for orientation).
- **Ratings**: 250 V on clamp/snubber caps (100 V plateau, ≤ 165 V clamp node), 100 V on VPRI/VBUS ceramics,
  63 V bulk at 48 V, 0805 on the 47.5 k and 150 k dividers, 2512 2 W shunts.
- **MPN/LCSC**: every IC, FET, diode, inductor, transformer and non-generic passive matches `B-*.md` /
  `sources-B.csv` (UCC2897APWR C54444, LM5019MRX/NOPB C471034, LTV-217-B-G C115450, NCP4306DADZZDASNT1G
  C504885, INA281A4IDBVR C2864421, TL431BIDBZR C41283, FDMS86200 C128799, IRFR6215TRLPBF C537989,
  BSC500N20NS3GATMA1 C5381902, AO3400A C20917, SM5845-331MT C10124, SM5845-221MT C10123, CDRH127/LDNP-680MC
  C2452974, BAS316 C109218, BAV21W C113947, US1G C383015, SMBJ130A-E3/52 C553984, SMCJ51A C408371,
  GRM31CR72E104KW03L C97956, GCM32DC72A475KE02L C913445, RVT2A470M1010 C87862, EKZN630ELL102ML25S C337254,
  GA355QR7GF222KW01L C91600, RLP25FEER068 C2683389, LR122WF300MT4E C2941066, RT0805BRD0747K5L C865514,
  HT7550-1 C16106, SN74LVC1GU04DBVR C81934, 74HC4017D C148206, SN74LVC1G123DCTR C123302, SN74LVC1G08DBVR C7666,
  LM393DR2G C7955, 74LVC2G08DP C406037, SXMH7.3728F2020F30 C2901749, HMK212BC7105KGHTE C385977).

### Block C (rails)
- Symbols vs datasheet pinouts: LM5013 DDA (p.4), TPS2116 DRL (p.3), TPS62A02A DDC (p.3), TPS7A94 DSC (p.3,
  EP = 11), TPS7A4901 / TPS7A3001 DGN (p.4 / p.5), TPS7A20 DBV (p.4), TLV6703 DDC (p.3), LM5017 (p.3),
  D_Schottky_TO277A (pads 1, 2 anodes, 3 cathode tab per SS5P10), L_Coupled_13_24 (windings 1–3 / 2–4, dots at
  1 and 2 = PSSCAQ7048 p.3).
- Footprints: SRP1265A (14.2 / 8.0 / 5.0), SRP4020TA (5.2 / 2.2 / 2.4), PSSCAQ7048 (1.4 × 3.0 pads, 1.8 × 4.9
  pitch, 1 TL / 2 TR / 3 BR / 4 BL) match the datasheets' recommended layouts.
- Every regulator traced: LM5013 (UVLO 1 M / 52.3 k, RON 64.9 k, FB 100 k / 31.6 k 0.5 % → 5.0 V, Type 3
  330 k 0805 / 3.3 n / 330 p per p.20, CBST 2.2 n 50 V, CIN 2 × 4.7 µ 100 V, D301 cathode on SW, PGOOD 56 k /
  100 k → PR1 + Q301); TPS2116 (MODE = VIN1, PR1 = PG_5V, both VOUT pins, 2 × 47 µ); TPS62A02A 3V3 (100 k /
  22.0 k 0.1 % → 3.327 V, EN = VIN, PG 100 k → U304 EN, U305 EN_UV, Q302) and 1V1 (100 k / 84.5 k → 1.107 V,
  EN = PG_3V3); TPS7A94 2V5 (16.7 k → 2.505 V, FB_PG 715 k / 68.1 k, SNS → OUT) and 3V3_Q (22.0 k, EN_UV
  47 k / 10 k from +15V, FB_PG 931 k / 68.1 k, PG 100 k); TPS7A2033P (EN = IN); LM5017 VDRV (RON 191 k 0805,
  UVLO VDRV_EN / 10 k + 100 k, FB 46.4 k / 10 k, Type III 330 k 0805 / 1 n / 100 n, CVCC 1 µ, CBST 10 n,
  2 × 10 µ 25 V); TLV6703 (150 k / 10 k → 6.40 V trip, OUT 4.7 k to VDRV / 2.7 k); LM5017 Fly-Buck (RON 330 k,
  UVLO 124 k / 5.36 k, FB 137 k / 10 k, 390 k / 1 n / 100 n, L305 pin 1 dot = SW, pin 3 = +18V_PRE, pin 2 dot =
  D302 cathode, pin 4 = GND — negative-rail polarity verified, B1100 reverse ≈ VIN, 2 × 10 µ 50 V each side,
  10 k preload); TPS7A4901 / TPS7A3001 (113 k / 9.76 k → 14.94 V; 118 k / 10 k → −15.09 V; CFF 10 n, CNR 10 n,
  EN = IN, DNC open); +5V_A (32.4 k / 10 k → 5.04 V); Q301/Q302 buffers 4.7 k; isolation 0 Ω / JP links and
  test points present.
- MPN/LCSC of every IC and power part match the audits (LM5013DDAR C5383001, SRP1265A-470M C840530,
  SS5P10-M3/86A C46986, TPS2116DRLR C3235557, TPS62A02APDDCR C25687169, SRP4020TA-1R0M C913245, TPS7A9401DSCR
  C5220127, TPS7A2033PDBVR C2862740, LM5017MRX/NOPB C34355, SRN6045TA-470M C5151734, TLV6703DDCT C2877614,
  PSSCAQ7048M-680M C56266204, B1100-13-F C110106, TPS7A4901DGNR C16430, TPS7A3001DGNR C33835, BLM18PG221SN1D
  C80165, FS32X475K101EGG C381466). VBUS-side caps 100 V X7R; SW/VIN resistors 0805; ±18 V caps 50 V X7R 1210;
  no datasheet-mandated pin left floating.

### Block D (amp_woofer, amp_tweeter, amp_sense)
- The tweeter sheet was diffed mechanically against the woofer (4xx → 5xx, _W → _T): identical except
  C560/C561 (HPF) and J501.1 on OUT_T_HPF, as audited.
- Symbols vs datasheet pinout (full): LMG1210 RVR (lmg1210.pdf p.3: NC 1/11/15, VIN 2, VSS 3/7, VDD 4, DHL 5,
  DLH 6, LO 8, HS 9/13/16, HO 10, HB 12, NC1 14 → HS, BST 17, EN 18, PWM 19, pad 20 VSS, pad 21 HS; all HS
  pins on SW_x_y); IGB070S10S1 (1 G, 2 D, 3/4 S); INA241A1 DDF (Table 5-1: IN− 1, GND 2, REF2 3, NC 4 → GND,
  OUT 5, VS 6, REF1 7, IN+ 8); TLV3502 DCN (p.3: +INA 1, −INA 2, +INB 3, −INB 4, V− 5, OUTB 6, OUTA 7, V+ 8);
  SN74LVC1G74 DCU (CLK 1, D 2, Q̄ 3, GND 4, Q 5, CLR̄ 6, PRE̅ 7, VCC 8); ADS7038-Q1 RTE (sbas981 p.4, 16 + pad);
  ADS8353 PW (sbas584 p.4, 16); OPA836 DBV (OUT 1, VS− 2, IN+ 3, IN− 4, PD 5, VS+ 6); ADS7042 DCU; 74LVC1G17
  DBV; LMV393 D; BAT54S (A1 1, K2 2, common 3); KiCad D_Schottky / D_Zener K = 1, A = 2.
- Footprints: `Texas_RVR0019A` WQFN-19-2EP — 19 pads 0.6 × 0.25 at 0.5 mm pitch CCW from pin 1, gaps between
  8/9 and 16/17, EP20 (VSS) 1.2 × 1.7 at x −0.75, EP21 (HS) 0.75 × 1.7 at x +0.975, matches p.24 and the
  EP/pin-group association; IGB070 positions and sizes match Fig. 2 (see D-m1); `Coilcraft_SER2915H` pads
  5.33 × 5.59, inner edges 2.41 / 11.56 from the centrelines, 6.35 × 5.28 mounting pad ending 5.08 from centre,
  un-numbered (Doc 644-2 p.2); `MAX_MX2EDGRC` 5.08 pitch, Ø1.7 / 2.7; `C_Rect B32774` 27.5 pitch, Ø1.2 / 2.0,
  31.5 × 22; `R_2512 Kelvin NetTie` with `net_tie_pad_groups "1,2" "3,4"`.
- Both channels: LMG1210 VIN = VDRV + 1 µ 25 V; VDD 100 n + 2 × 2.2 µ 16 V; BST → BAT46WJ anode, cathode →
  HB; HB–HS 470 n 25 V X7R; DHL/DLH 20.0 k to VSS; PWM/EN via 100 Ω, 10 p DNP; EN from latch Q. GaN HS
  D = VBUS, S = SW; LS D = SW, S = GND; HO → 2.2 Ω → gate, 100 k gate–SW; LO → 2.2 Ω → gate, 10 k gate–GND.
  Bridge decoupling 2 × HMK107B7104KAHT + 2 × HMK325B7225KN-T per half-bridge; SMBJ51A cathode on VBUS. Output
  SW → SER2915H → 5 mΩ PA2512 (Kelvin to INA241) → OUT; 7 × GRM31C5C2A104 per leg; Zobel 2 × 20 Ω 2512 ∥ +
  100 n C0G; tweeter 2 × B32774D4226K between OUT_T_A and J501.1 with Zobel / DC / short taps bridge-side.
  INA241A1 on 3V3_A, REF1 = VS, REF2 = GND, 100 n at VS, output to TLV3502 and via 100 Ω + 1 n to ADS7038
  AIN0–3. OCP ladder 9.09 k / 15 k / 9.09 k → 2.396 / 0.904 V with 100 n; comparator polarity active-high;
  BAT46WJ cathodes at comparators, anodes on FAULT_RAW_x (2.2 k to +3V3); AMP_ARM (10 k pull-down R604) and
  DC_x_n (4.7 k pull-up) diode-ANDed; 1G17 → FAULT_x_n → CLR̄ and FPGA; 1G74 D = AMP_EN_x, CLK = AMP_CLK_x,
  PRE̅ = +3V3, Q → EN. Short detect 47 p 100 V C0G → X → 1 k → 1.65 V bias; BAT54S clamps X to GND / 3V3_A;
  1 k into each comparator input; polarity correct. DC detect 2.2 M / 82 k and 2.2 M / 88.7 k + 1.21 M offset
  nodes, 2.2 µ, LMV393 cross-wired for ±6 V, outputs wired-OR on DC_x_n. NTCs with 10 k to 3V3_A and 100 n at
  AIN4–7. amp_sense: ADS7042 divider 27.4 k + 27.4 k / 2.21 k, 1 n, BAT46WJ clamp to 3V3_A, AINM → GND, AVDD =
  3V3_A (1 µ + 100 n), DVDD = +3V3; ADS7038 AVDD = 3V3_A 1 µ, DVDD 1 µ, DECAP 1 µ, pad GND; ADS8353 × 2 AINM →
  GND, REFIO 10 µ, AVDD = +5V, DVDD = +3V3, shared CS/SCLK/SDI, separate SDO; OPA836 × 4 followers via 20 Ω +
  1 n, PD = +5V. All D ↔ E nets land on U801; VDRV feeds all four LMG1210 VIN. Required ties present (INA241
  NC, ADS8353 / ADS7042 AINM, OPA836 PD, LMG1210 NC1).
- MPN/LCSC of every IC, FET, inductor, diode, connector and passive on the three sheets match the audits
  (part-by-part, incl. C531089 for B32774D4226K).

## Verdicts

| Block | Verdict | Conditions |
|---|---|---|
| A (poe_in) | **PASS** | None. Keep the J101 CT continuity check (A-n1) and the LFPAK33 land check (A-n2) on the phase 4 / bring-up lists. |
| B (iso_dcdc, iso_aux) | **PASS with conditions** | Fix **B-M1** (mirror the T201 footprint back to the datasheet top view, add a pin-1 mark) before phase 4 placement; decide B-m1 (0805 for the 57 V dividers). Schematic connectivity, polarity and values are correct. |
| C (rails) | **PASS** | No blocker or major; C-m1 is a one-footprint addition or an audit edit. |
| D (amp_woofer, amp_tweeter, amp_sense) | **PASS with conditions** | Fix **D-M1** (short-detector ladder vs audit) before the gate; D-m1 and D-m2 before phase 6 fab outputs; D-m3 is a documentation fix. |

## Fix verification (2026-11-08, after the owners' fixes; netlist and BOM re-exported)

Re-derived independently from the drawings and the re-exported `netlist.xml` / `bom-sch.csv`; project files read only.

| Item | Status | Evidence |
|---|---|---|
| **B-M1** T201 footprint mirrored | **CLOSED** | `Wurth_750343576_ER19.kicad_mod` now: pads 1/2/3 at (−10.615, −7.885 / −5.085 / −2.285), 4/5/6 at (−10.615, +2.285 / +5.085 / +7.885), 11/10 at (+10.615, −6.36 / −3.18), 8/7 at (+10.615, +3.18 / +6.36), 3.13 × 1.89; pin-1 circle at (−10.615, −9.6) above pad 1. Pixel measurement of we-750343576.pdf p.1 "Recommended Land Pattern" (scale 1:1, rendered at 600 dpi): left-column pad centres at −7.8 / −5.0 / −2.26 / +2.26 / +5.0 / +7.8 mm (pitch 2.78, inner gap 4.51 ≈ the "4,57" dimension), right-column centres at −6.27 / −3.14 / +3.13 / +6.24 (pitch ≈ 3.18), column centre-to-centre 21.0 mm (drawing "21,23" is centre-to-centre; my earlier outer-to-outer reading of ±9.05 was wrong, the owners' ±10.615 is right), pin 1 upper-left, 11 upper-right, 6 lower-left, 7 lower-right. Footprint matches the top view in orientation, pitch and spacing. Primary-to-secondary copper gap = 2 × (10.615 − 1.565) = **18.1 mm**, above the 8 mm the ISO7740 DW already imposes on the R-32 keepout (intent.md R-32 gives no smaller number). Symbol dots and netlist unchanged and correct. |
| **B-m1** 0603 at 57 V | **CLOSED** | R206 73.2 k (0805W8F7322T5E C17814), R208 47 k (C17713), R209 470 k (C17709), R218 100 k (C149504), R221 267 k (C17585), R224 237 k (C17568) are now `R_0805_2012Metric` in netlist and BOM (Uni-Royal 0805: 150 V working / 300 V overload). |
| **B-m2** pin-1 marker | **CLOSED** | F.SilkS circle at (−10.615, −9.6). |
| **D-M1** short-detector ladder | **CLOSED** | R448/R449/R450 and R548/R549/R550 = 4.99 k (0402WGF4991TCE) / 15 k (0402WGF1502TCE) / 4.99 k from +3V3_A to GND, SDH_x at the R448–R449 node into U404.1/U408.1 (U504.1/U508.1), SDL_x at R449–R450 into U404.4/U408.4 (U504.4/U508.4), 100 nF C454/C455 (C554/C555) on each node. SDH = 3.3 × 19.99/24.98 = **2.641 V**, SDL = 3.3 × 4.99/24.98 = **0.659 V**, ±0.991 V about 1.650 V. Lead-open trip I = C·V/τ: 700 nF × 0.991 V / 47 ns = **14.8 A** nominal; stacked corner 665 nF × 0.95 V / 49.8 ns = **12.7 A** — both as stated in the `D-short-detect.md` phase-2 correction block (lines 12–15, parts row line 30). 12.7 A is below the 13.0 A legitimate peak only when every tolerance aligns and the lead opens at the peak; the audit records this as benign (latch opens, FPGA re-arms). Consistent. |
| **D-m1** IGB070 footprint SMD/paste | **CLOSED** | `IGB070S10S1_PG-TSON-4.kicad_mod`: copper-only pads 3.3 × 0.705 (pin 3, y −1.2025), 3.3 × 0.45 (pin 2, y 0), 0.95 × 0.705 (pin 1 at x −1.175) and 2.05 × 0.705 (pin 4 at x +0.625) at y +1.2025 = Fig. 2 p.14 copper (3.2 × 0.605, 0.35 bar, 0.85 gate, 1.95 source) + 0.05 mm per side; F.Mask windows 3.2 × 0.4 on the inner side of each outer row (−1.3…−0.9, +0.9…+1.3), 3.2 × 0.35 on the drain bar, split 0.85 / 1.95 on the bottom row; F.Paste apertures 3 × 0.93 × 0.36 (top), 3 × 0.76 × 0.31 (drain), 0.71 × 0.36 + 0.88 × 0.36 + 0.88 × 0.36 (bottom), all inside their mask windows, matching the Fig. 2 stencil table. Residual: the bottom-row middle aperture sits at x +0.11 where Fig. 2's 1.225 pitch from the gate aperture implies ≈ −0.02; 0.13 mm, no consequence for paste volume (NOTE only). |
| **D-m2** divider TCR | **CLOSED** | R420/R441/R520/R541 = RT0603BRD07140KL (C861125, 25 ppm) in netlist and BOM; `D-postfilter-sense.md` line 13 updated to BRD for both. |
| **D-m3** D-gan-fet.md pin text | **CLOSED** | Lines 10 and 141 now read top row = pin 3 (source), middle bar = pin 2 (drain), bottom = pin 1 gate + pin 4 source, with the correction dated and the footprint/netlist stated as already correct. |

### Final verdicts after fixes

| Block | Verdict |
|---|---|
| B (iso_dcdc, iso_aux) | **PASS** |
| D (amp_woofer, amp_tweeter, amp_sense) | **PASS** (D-m1 residual is a NOTE) |

Blocks A and C were PASS at the first pass and are unchanged.
