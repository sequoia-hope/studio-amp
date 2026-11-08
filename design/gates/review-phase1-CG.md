# Phase 1 independent review — blocks C (secondary rails) and G (UI and I/O)

Date: 2026-11-07. Reviewer: independent (did not see the authors' conversation).
Scope: `design/parts/C-*.md`, `design/parts/G-*.md`, cross-checked against `design/intent.md`,
`design/architecture.md` (Phase 1 reconciliation), `D-/E-/F-interfaces.md`, and the datasheets in
`design/datasheets/` (re-read, not the audits' quotes). Every calculation below was redone from the
datasheet formulas. Sourcing lines were re-run with `jlc_parts.py show` on 2026-11-07 (all match, stock
within a few units of the audits' figures).

Page numbers refer to the PDF in `design/datasheets/`.

---

## BLOCKER

### B1. `PG_3V3` cannot rise against the ECP5's unconfigured pull-down — the 1V1 / 2V5 rails never start

- Files: `C-3v3-1v1-bucks.md` ("PG_3V3 (100 kΩ to +3V3) → EN of 1V1 and EN_UV of the 2V5 LDO"),
  `C-2v5-ldo.md`, `C-sequencing.md`, `C-interfaces.md` (signal ownership: `PG_3V3` → FPGA B4,
  "100 kΩ to +3V3, block C", "no pull-ups on our side" per E-interfaces).
- Datasheets: TN-02039 p. 23 §5 ("GPIO at power-up defaults to tristated outputs with **active weak
  input pull-downs**"); TN-02038 p. 21 Table 9.1 (pull-down current **30–150 µA** for VIL(max) ≤ VIN ≤
  VCCIO); TPS62A02A p. 5 (VEN rising 1.2 V; PG VOL 400 mV at IPG = 1 mA); TPS7A94 p. 7 (EN_UV rising
  1.20–1.25 V).
- Problem: the same net `PG_3V3` is an open-drain output with a 100 kΩ pull-up and also goes to ECP5
  ball B4. Before the FPGA is configured B4 sinks 30–150 µA. A 100 kΩ pull-up to 3.3 V can source at
  most 33 µA (at 0 V), so the node sits well below the 1.2 V EN thresholds of the 1V1 buck and the 2V5
  LDO for every part in the spread. The ECP5 core (`+1V1`) therefore never powers, the FPGA never
  configures, and the pull-down is never released: a hard deadlock at every power-up, on PoE and on USB.
  Block E caught exactly this mechanism for its ADC chip-selects (E-fpga-ecp5-passives.md: "10 kΩ would
  leave 1.8 V") but the C/E interface did not apply it to the power-good chain. `C-sequencing.md`
  still argues from the Gowin's pull-*ups*.
- Fix: pull `PG_3V3` up with **4.7 kΩ** (TPS62A02A PG sinks 0.7 mA, within its 1 mA rating; node ≥
  3.3 − 4.7 k × 150 µA = 2.6 V, above the 1.25 V EN thresholds and the 2.31 V LVCMOS33 VIH), **or**
  buffer the FPGA copy (e.g. a second open-drain/MOSFET stage) so the EN net is not shared with an FPGA
  input. Block E must also set PULLMODE = NONE on B3/B4/B5 after configuration. Re-state the
  "hardware backstops while the FPGA is unconfigured" paragraph in `C-sequencing.md` for pull-downs.

### B2. `PG_5V` → TPS2116 PR1 is dragged toward the PR1 threshold by the same pull-down — +5V may never come up on PoE

- Files: `C-5v-buck.md` (PGOOD "56 kΩ, 100 kΩ to GND, PG_5V = 3.24 V"), `C-5v-mux.md` (PR1 = PG_5V),
  `C-interfaces.md` (`PG_5V` → FPGA B3 "not open drain, so no pull-up").
- Datasheets: TN-02039 p. 23 / TN-02038 p. 21 (as above); TPS2116 p. 6 (VREF PR1 0.92–1.08 V),
  p. 10 truth table (MODE = VIN1, PR1 < VREF → VIN2 or nothing).
- Problem: the PGOOD divider's Thevenin impedance is 56 k ‖ 100 k = 36 kΩ at 3.24 V. With the
  minimum 30 µA pull-down the node is 2.15 V (fine); with 150 µA the divider can supply at most 90 µA
  even at 0 V, so the node collapses to ≈ 1 V or below, at or under the PR1 reference. On PoE-only
  power the mux then never selects the buck, `+5V` never appears, the FPGA never configures, and the
  pull-down persists. Whether a given board starts depends on where its ECP5 falls in the 30–150 µA
  spread.
- Fix: lower the PGOOD divider to **5.62 kΩ / 10 kΩ** (Thevenin 3.6 kΩ; 0.54 V drop at 150 µA → ≥ 2.7 V;
  PGOOD sinks 0.9 mA through its 25 Ω switch, LM5013 p. 14), or keep the FPGA copy on a separate
  divider from PGOOD, or let the RP2350 read PG_5V instead of the FPGA. Recheck every block C/G net that
  is both a pulled-up open-drain signal and an FPGA input: `PG_3V3Q` (100 kΩ; only read after
  configuration, so a NOTE), `LED_FAULT_N`/`QWIIC_FAULT_N` (10 kΩ; read ≈ 1.8 V before configuration,
  only informational), `VUSB_DET` (15 k/22 k; same).

---

## MAJOR

### M1. LM5017 Type III ripple injection adds a DC offset that neither LM5017 audit accounts for: Fly-Buck pre-rails run ≈ 1.5–2 V high, VDRV ≈ 0.5 V high

- Files: `C-pm15-flybuck.md` ("Rr = 100 kΩ, Cr = 1000 pF … VOUT1 18.4 V (18.0–18.8 V)"),
  `C-vdrv-buck.md` ("Rr = 100 kΩ, Cr = 1 nF … 7.04 V (6.90–7.19 V)", interface "7.04 V ±2 %"),
  `C-pm15-ldos.md` (dissipation at 18.4 / 17.8 V).
- Datasheets: LM5017 p. 9 ("a minimum of 25 mV of ripple voltage at the feedback pin is required"),
  p. 5 (TON test: 250 ns typ at 48 V, RON 100 kΩ → tON ≈ 1.2 × 10⁻¹⁰ × RON/VIN, not 1.0 × 10⁻¹⁰);
  AN-2292 p. 9 eq. 35 and "half to a fourth of this resistance"; LM5013 p. 20 §9.2.2.7 states the
  mechanism explicitly: the injected ripple "reflects as a DC error of approximately half the amplitude
  … scaled up through the FB divider". The 5 V buck audit applied it (+48 mV); the two LM5017 audits
  did not.
- Recomputed: the COT comparator trips at the ripple valley, so the FB average sits at VREF + Vr/2.
  - Fly-Buck: Vr = (VIN − VOUT1)·tON/(Rr·Cr) = (56 − 18.4) × 0.72 µs / 100 µs = **270 mV** at 56 V,
    (36 − 18.4) × 1.12 µs / 100 µs = **197 mV** at 36 V. Offset = 100–135 mV × 15.0 =
    **+1.5 to +2.0 V**, line-dependent. VOUT1 ≈ 19.9–20.4 V typ (≈ 20.8 V with the +2 % reference),
    secondary ≈ −19.3 to −19.8 V. Consequences: TPS7A4901 at the 120 mA design load dissipates
    (20.4 − 14.94) × 0.12 = 0.65 W, not 0.42 W; in the 200 mA fault 1.1 W. With the **correct DGN θJA of
    63.4 °C/W** (TPS7A49 p. 6; the audit used the 47.7 °C/W of the DRB column) that is +41 °C in
    normal use and +70 °C in the fault, i.e. TJ ≈ 125 °C at 55 °C air — at the ROC limit. TPS7A3001:
    (19.8 − 15.09) × 0.11 = 0.52 W → +29 °C (θJA 55.1, p. 2). The ±5 % line regulation of the
    pre-rails also degrades by ≈ 0.5 V between 36 and 56 V.
  - VDRV: Vr = (56 − 7)·0.41 µs/100 µs = 200 mV (56 V), (36 − 7)·0.64 µs/100 µs = 185 mV (36 V) →
    offset ≈ 0.1 V × 5.75 = **+0.55 V**, so VDRV ≈ 7.6 V, not "7.04 V ±2 %". Still inside the LMG1210's
    6–18 V VIN and above the TLV6703's 6.40 V trip, but outside the 7.0 V ±5 % promised to block D and
    it raises each driver's LDO loss by 25 %.
- Fix: (a) include the offset in both setpoints — either lower RFB(top) to pre-compensate (Fly-Buck:
  target FB DC ≈ 1.34 V → RFB(top) ≈ 127 kΩ for 18.4 V; VDRV: ≈ 43.2 kΩ) or raise Rr toward 220–300 kΩ
  (still ≥ 50 mV at 36 V per AN-2292, ≥ 25 mV per the datasheet) to shrink both the offset and its line
  dependence; (b) redo `C-pm15-ldos.md` thermals with 63.4 °C/W and the actual pre-rail voltages, and
  decide whether the +15 V LDO needs the DRB (VSON) variant or more copper; (c) correct the VDRV spec in
  `C-interfaces.md` to what the circuit makes (or trim it), and confirm with block D.

### M2. TCA9617B EN is not defined when Qwiic power is off — the repeater can float enabled and hold the RP2350's I2C bus low

- File: `G-qwiic.md` ("EN: tied to QWIIC_3V3 through 10 kΩ … It has an internal pull-up to VCCB; the
  10 kΩ to 0 V overrides it").
- Datasheets: TCA9617B p. 3 (EN "internally connected to VCCB through a weak pull-up resistor"), p. 5
  (VILB = 0.4 V: a B-side line at 0 V is a valid low and is mirrored onto the A side), p. 7 note 5 (EN
  must change only with both buses idle); TPS2553 (whole datasheet: there is **no output discharge**
  path on OUT; IREV ≤ 1 µA).
- Problem: `QWIIC_3V3` is only "0 V" if something discharges it. With the switch off, the only sinks
  are TPS2553 leakage (≤ 1 µA), SRV05-4 pin 5 leakage (≤ 5 µA, typically nA) and whatever is plugged in.
  The TCA9617B's EN pull-up sources current through the 10 kΩ into the 10 µF on `QWIIC_3V3`, so with
  nothing attached the rail drifts up until EN is at an undefined level between VIL (0.3 VCCB ≈ 1 V) and
  VIH (2.3 V). If EN reads high while the B-side pull-ups hang on a near-zero rail, SDAB/SCLB are
  "low" and the repeater drives SDAA/SCLA low — the RP2350's whole I2C bus is dead whenever Qwiic power
  is off. It also violates the EN-only-when-idle rule.
- Fix: add a **100 kΩ pull-down from `QWIIC_3V3` (or EN) to GND** so the rail and EN are held at 0 V
  with the switch off, or drive EN directly from `QWIIC_PWR_EN` (which already has a 100 kΩ pull-down;
  EN is 5.5 V tolerant) — the TPS2553's 0.7–1.5 ms rise then slightly lags EN, which is harmless because
  the far end is unpowered during those µs. Keep the firmware rule that `QWIIC_PWR_EN` changes only
  with the controller idle.

---

## MINOR

- **`C-5v-buck.md` / `C-interfaces.md` — switching-frequency rationale is stale.** "396 kHz keeps clear
  of the 768 kHz PWM's second harmonic": block D now runs **448 kHz** (D-interfaces.md) and block B's
  ACF runs 400 kHz ±6 %. A free-running COT at 396–440 kHz (the real frequency is ≈ 440 kHz once the
  diode drop is included: D = (5.05 + 0.55)/(56 + 0.55), tON 226 ns) sits on top of both, so beat
  products fall in the audio band if anything mixes them (ADC sampling, PWM feed-forward). Re-justify or
  move RRON so FSW lands well away from 400 and 448 kHz (e.g. ≈ 300 or ≈ 600 kHz; LM5013 p. 7 keeps
  tON ≥ 50 ns either way).
- **`C-5v-buck.md` — CIN below the datasheet recommendation.** LM5013 p. 20 §9.2.2.6: "recommended
  high-frequency input capacitance is 4.4 µF or higher". The audit's own derating (3 × 2.2 µF 100 V at
  48 V → ≈ 3.3 µF effective) is under that. Use 4 × 2.2 µF or 2 × 4.7 µF 100 V X7R 1210 and attach the
  bias curve.
- **`C-pm15-ldos.md` — θJA column and +5V_A accounting.** DGN (HVSSOP PowerPAD) is 63.4 °C/W, not
  47.7 (TPS7A49 p. 6). F-interfaces lists `+15V` 62/120/200 mA **and** `+5V_A` 12/15 mA as separate
  loads; if +5V_A is fed from +15V the TPS7A4901 carries 135 mA design / 215 mA fault, over its 150 mA
  ROC in the fault case. Confirm with block F whether 120 mA already includes +5V_A, then redo the
  table (see M1).
- **`C-interfaces.md` — +3V3 budget omits small consumers.** Block F 10 mA (PCM1808 VDD, T3902),
  block A ISO7740 VCC2 3.2 mA, TCA9617B ICCB 4.5–7 mA (p. 5), knob header pin 11 ≤ 10 mA, SRV05-4 ×4 and
  pull-ups. ≈ +25–30 mA → ≈ 0.81 A design; still within the 1 A peak, but list them.
- **`C-interfaces.md` / `C-vdrv-buck.md` — VDRV load figures are stale.** They quote IGB070S10S1
  (42/79 mA). D-interfaces (ECP5 revision) specifies IGC033S10S1: 62 mA at 448 kHz, 128 mA at 1 MHz,
  spec ≤ 150 mA, 0.43–0.89 W at VDRV. The 200 mA design still covers it (Ipk 0.36 A vs 0.7 A ILIM min),
  but the budget rows (0.37/0.65 W from VBUS) should become ≈ 0.51/1.05 W.
- **`C-3v3-1v1-bucks.md` — 83.5 kΩ is an E192 value.** Not a JLC basic value; 84.5 kΩ (E96) gives
  1.107 V (1.080–1.134 V worst case), which is what E-interfaces already records. Pick one and make the
  two files agree.
- **`C-2v5-ldo.md` / `C-3v3q-ldo.md` — start-up time understated.** TPS7A94 p. 37: IFAST_SS (2.1 mA)
  only charges CNR/SS to ≈ 93 % of VOUT, then INR/SS (150 µA) finishes. 2V5: 1.1 ms + 0.18 V × 1 µF /
  150 µA ≈ **2.3 ms** (not 1.2 ms); 3V3_Q: 6.9 ms + 1.5 ms ≈ **8.5 ms** plus the NR filter settle. Ramp
  rates still inside the ECP5's 0.01–10 V/ms and ≤ 30 mV/µs; update `C-sequencing.md` timing table.
- **`C-5v-buck.md` — second source LM5013QDDARQ(TOKMAS) is a third-party clone**, not a TI part. A COT
  controller's RON constant, current limit and CBST window are not guaranteed identical. Mark it "not a
  drop-in until its own datasheet is audited" rather than listing it as a second source.
- **`G-led-out.md` / `G-esd-parts.md` — SMF5.0A on +5V_LED above its stand-off.** +5V_BUCK can be
  5.12 V (5.045 V nominal plus the Type 3 offset spread) against VRWM 5.0 V (SMF5.0A p. 2, IR ≤ 400 µA at
  5.0 V, higher above it). The audit accepts the leakage; SMF6.0A (VRWM 6.0 V, VC 10.3 V) clears it
  with the TPS2553's 7 V abs max intact. Swap now rather than "if stocked in phase 2".

---

## NOTE

- **TPS2116 at PoE-only start** (TPS2116 p. 10 truth table, p. 12): while VIN1 = +5V_BUCK ramps from 0
  to ≈ 1 V, MODE is "low" and PR1 low → "higher of VIN1/VIN2 passes" → the output follows the buck up to
  ≈ 1 V, then MODE crosses its 1 V high threshold with PR1 still low → VIN2 (absent) selected → output
  collapses until PG_5V asserts 3.5 ms later. Harmless (TPS62A02A UVLO ≈ 2.5 V) but will be visible at
  bring-up; record it so it isn't chased as a fault.
- **TLV6703 `VDRV_PG` node under an LM5017 FB-overvoltage event** (LM5017 p. 5, FB OV 1.62 V → VOUT ≈
  9.3 V): 9.3 × 33/80 = 3.84 V into RP2350 GPIO33. Fault case only; a 3.6 V clamp or 39 k/33 k is cheap
  insurance.
- **Fly-Buck fault margin**: at block F's 200/190 mA short case the primary peak is 0.65 A against the
  0.7 A minimum ILIM (LM5017 p. 5; AN-2292 p. 4 eq. 6–8). Protected by the LDOs' own limits (220–500 mA,
  TPS7A49 p. 6 / TPS7A30 p. 3) and by LM5017 foldback, so acceptable, but expect the pre-rails to sag in
  that fault. The frequency also moves to ≈ 508 kHz once VOUT1 is 18.4 V (eq. 1 with K = 9 × 10⁻¹¹).
- **LM5013 inductor saturation**: SRP1265A-220M Isat 12 A, Irms 9 A, DCR 37 mΩ max confirmed (Bourns
  p. 1); rated −55…+150 °C (the audit says +125). SRP4020TA-1R0M 5.0 A / 8.5 A, SRN6045TA-470M 1.6 A /
  2.0 A, PSSCAQ7048M-470M 1.1 A / 2.0 A / 600 V coil-to-coil, SRF0703-470M 0.338 Ω all confirmed.
- **LM5013 PGOOD thresholds**: EC p. 7 gives the rising threshold as 1.10–1.20 V (max equals VREF), so
  on a slow part PG_5V may assert only when the output is fully in regulation. Fine for sequencing.
- **SN74LV1T125 inputs with VCC = 0**: abs max VI is 7 V independent of VCC (p. 6), so driving the
  shifter inputs from the RP2350 while +5V_LED is off is within rating, but no Ioff/partial-power-down
  figure is given; measure back-feed into +5V_LED at bring-up.
- **USB unconfigured current**: the board draws ≈ 0.3 A from VUSB before enumeration (USB 2.0 allows
  100 mA until configured). Normal for a bring-up port, but some hosts will complain; note it against
  R-23.
- **Knob `KNOB_REF`**: loading RP2350 ADC_AVDD with up to 1.3 mA (33 mA into a header short) through
  block E's filter is block E's open item (`G-knob.md` says so); close it before phase 2.
- **TPS7A94 RPG range is 10–100 kΩ (p. 5)**, so the `PG_3V3Q` pull-up cannot go below 10 kΩ; with
  PULLMODE = NONE after configuration the 100 kΩ is fine.
- **Package/footprint checks** (all against the exact suffix): LM5013DDAR SO-PowerPAD-8, TPS2116DRLR
  SOT-583, TPS62A02APDDCR DDC = *thin* SOT-23-6 (use a TSOT-23-6 footprint, not SOT-23-6), TPS7A9401DSCR
  WSON-10 3×3, TPS7A2033PDBVR SOT-23-5 (pins 1 IN, 2 GND, 3 EN, 4 NC, 5 OUT confirmed, p. 3),
  LM5017MRX HSOP-8, TLV6703DDCT thin SOT-23-6, TPS7A4901/3001DGNR HVSSOP-8 PowerPAD, TPS2553DRVR WSON-6
  2×2 / TPS2553DBVR SOT-23-6, TCA9617BDGKR VSSOP-8, SN74LV1T125DBVR SOT-23-5: consistent with the audits.
- **Checked and correct**: LM5013 feedback (4.997 V + 48 mV offset), RRON/tON (226 ns at 56 V, forced
  250 ns off-time), Type 3 network (CA ≥ 1.05 nF, RA·CA ≤ 565 µs, 22–23 mV FB ripple ≥ 12 mV, CB ≥ 250 pF),
  EN/UVLO 36.2/33.8 V and hold-up 0.36 s, ΔIL 0.53 A and Ipk 2.26 A vs 3.7 A, COUT ≥ 6.6 µF, SS5P10 loss
  0.89 W / RθJA 65 °C/W; TPS2116 priority wiring (MODE = VIN1), RCB, tSW dip; TPS62A02A dividers and
  tolerance stacks, Table 8-3 capacitor classes, PG 96/93.5 %; TPS7A94 setpoints (150 µA × R), FB_PG
  current-limit bands (12.5/50/100 kΩ) and PG trips; TPS7A49/TPS7A30 dividers, headroom rule, 14 ms
  soft start, DNC/PowerPAD rules; TLV6703 6.40/6.31 V trips and the pull-up-from-VDRV "absent = low"
  trick; Fly-Buck UVLO 35.9/33.4 V (hysteresis = IHYS × RUV2 exactly); TPS2553 limits 1.034/1.110/
  1.196 A and 364/406/455 mA, deglitch 5–10 ms, DRV 75 °C/W; TCA9617B pull-up/bus-capacitance budget and
  VOLB offset caveat; USB CC 5.1 kΩ ×2, VUSB_DET 3.12 V, ESD parts' VRWM/VC/capacitance; JST SH 1 A /
  PH 2 A; ECP5 sequencing (VCCIO first, 1V1/2V5 ≈ 1 ms later, ramp 0.01–10 V/ms, VCCAUX ≤ 30 mV/µs) and
  the RP2350 (no sequencing constraint) — all satisfied once B1/B2 are fixed.

---

**Verdict: FAIL — two BLOCKERs (B1, B2: the power-good chain cannot overcome the ECP5's unconfigured
30–150 µA pull-downs, so the board deadlocks at power-up) and two MAJORs (M1 LM5017 ripple-injection
DC offset / LDO thermals, M2 floating TCA9617B enable) must be fixed and re-reviewed before phase 1
closes; the rest is housekeeping.**
