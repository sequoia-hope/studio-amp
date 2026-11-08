# Phase 1 re-review — blocks E (compute, network, clocks) and F (analog audio)

Date: 2026-11-08. Independent second-pass reviewer; saw the artifacts only (first-pass reviews,
the authors' "Review response" sections, the `E-*`/`F-*` audits, `intent.md`, `architecture.md`,
the A/B/C/D interface files) and re-derived every closed item from the datasheets in
`design/datasheets/` (pdftotext; the two image-only oscillator sheets rendered and read).
Gowin files marked superseded were ignored. ECP5 balls re-checked against
`lattice-ECP5U-25-pinout.csv`.

## First-pass BLOCKER / MAJOR items

| Item | Status | Reason (re-derived) |
|---|---|---|
| E MAJOR-1 — ×14 gearing at 98 % of a commercial limit | **CLOSED** | Baseline is now PLL ×12: VCO 589.824 MHz (400–800 ✓), CLKOP/ECLK 294.912 MHz, ODDRX2F 589.824 Mb/s, grid 1.695 ns, N = 1024 → exactly 576 kHz = 12 × 48 kHz. Against DS-02012 Tab 3.22 (p.66–69): −7C fMAX_EDGE / GDDRX2_TX 350 MHz → 84 %. The −6C column is 312 MHz, so even if the −7I part is a full grade slower the ×12 setting still has 5.5 % margin, whereas ×14 (344 MHz) would exceed it — the demotion of ×14 to a bring-up option is the right call. R-53, `E-fpga-ecp5.md`, `E-clk-audio-vcxo.md`, `E-interfaces.md`, D's file agree on 576 kHz / 1.695 ns. |
| E MAJOR-2 — LAN8720A straps vs ECP5 pull-downs | **CLOSED** | 4.7 kΩ to +3V3 on RXD0/RXD1/CRS_DV (`E-fpga-ecp5-passives.md`). ECP5 IPD ≤ 150 µA (DS Tab 3.7 p.53–54) → 3.24 V − 0.7 V = 2.53 V worst case vs VIS VIHT max 1.90 V at 3.3 V (LAN8720A Tab 5-4 p.62) ✓; PHY internal pull is ±50 µA typ (Note 5-12). The "should" of §3.7 (p.26) is met; PHY driving low into 4.7 kΩ is 0.7 mA ≪ VO8. PULLMODE=UP on A11/A12/B11 and "nRST only after configuration, ≥ 25 ms after rails" are recorded as gateware rules. Gowin "pull-up" text is gone. |
| E MAJOR-3 — B↔E nets, POE_LOSS_N owner | **CLOSED** (text nits below) | `ILIM_SEL0/1` RP2350 GPIO34/35 (reset pull-down 36–113 kΩ + B's 100 kΩ → 00 = 0.44 A ✓); `IBUS_SENSE` ADC4/GPIO44 (RP2350 datasheet p.1 feature list: GPIOs "3.3 V-failsafe (unpowered)", so the ≤ 45 µA pre-3V3 case is datasheet-permitted, not just "accepted"); `ACF_PULSE` B6 (top bank); `POE_LOSS_N` A6 with block B as owner and a full detector design (`B-poe-loss-detect.md`), 4.7 kΩ pull-up (3.3 − 0.7 = 2.6 V pre-configuration ✓). |
| F B1 — relay driver | **CLOSED** | AO3400A: VGS(th) 0.65/1.05/1.45 V, RDS(on) ≤ 48 mΩ at VGS = 2.5 V (ao3400a.pdf p.1–2). Gate = 3.24 V × 100/110 = 2.95 V ≥ 2.5 V ✓. Coil ≥ 4.85 − 0.0015 = 4.85 V (block C's worst case) vs HFD4/5 pick-up 3.75 V, max 10 V (hfd4.pdf coil table) ✓. Override: BC847B saturated ≤ 0.1 V + BAT54C VF ≤ 0.24–0.32 V at 0.1–1 mA (bat54c.pdf Tab 7) → gate ≤ 0.4 V < Vth(min) 0.65 V (≈ 0.58 V at 55 °C) ✓; drop-out needs 0.5 V/178 Ω = 2.8 mA, sub-threshold current is µA ✓. 1N4148WS flyback 150 mA ≫ 31 mA ✓. |
| F M1 — SA5532 in a headphone short | **CLOSED** | Re-derived: in a short Q_LN clamps the top base node ≈ 1.5 V, D1 of the spreader is reverse-biased, so the op-amp's only path is R_D → D2 → D_RP → R_E → short: (13 − 1.7)/1 kΩ = 11.3 mA (a 10 mA IOS(min) part limits earlier; p.4). Op-amp output stage ≤ 33 mW; θJA 97 °C/W (D package, p.3): Tj ≤ 55 + 97 × (0.48 + 0.05) ≈ 106 °C at ICC max, both channels ✓. R_D 0.13 W in 1206 0.25 W ✓. BCP56: BC847B VBE 0.58–0.70 V at 2 mA (bc847.pdf Tab 7) → limit 39–47 mA → P ≤ (15 − 0.7 − 0.2) × 47 mA = 0.66 W → Tj 138 °C at 125 K/W (1 cm²), 116 °C at 93 K/W; the audit's 133 °C uses VBE = 0.65 V. Still < 150 °C; the ≥ 2 cm² layout requirement is what buys the margin (see NOTE-3). Headroom 8.1 V vs ±12 V ✓; normal op-amp drive ≤ 0.4 mA with the 4 mA sources (spread 2.7–4.6 mA over BAV99/BC857 VF/VBE, still ≥ the 0.39 mA base need) ✓. |
| F M2 — X7R in the mic path | **CLOSED** | WIMA MKS2C041001F00: 1.0 µF 63 VDC PET, 5 × 10 × 7.2 mm, PCM 5 (wima-mks2.pdf table p.3) at C_IN and both ADC couplings; 470 kΩ bias → 0.34 Hz; ADC 1 µF × 60 kΩ (pcm1808.pdf Zin 60 kΩ) = 2.65 Hz ✓. KNSCHA RST47UF16V034 47 µF 16 V 105 °C 2000 h aluminium at N_B ✓. Dielectric table per position present. (The 10 µF X7R at N_DC is in the DC detector, not the audio path: fine.) |

## New findings

### BLOCKER

None.

### MAJOR

None.

### MINOR

**MINOR-1 — `POE_LOSS_N` pull-up value and topology disagree between E, F and B.**
Files: `E-pinmap.md` line 312 ("10 kΩ pull-up on the net") vs the A6 row and `E-fpga-ecp5-passives.md`
(4.7 kΩ); `F-mute-relay.md` ("10 kΩ pull-up to +3V3, block E") and `F-interfaces.md` "Update"
section (10 kΩ). E and B also describe the F load as "the OR diode into /DC_TRIP", while
`F-mute-relay.md` fits a separate BAT54C (D_PL) straight to the two gates and says explicitly it is
*not* an OR into /DC_TRIP; `F-interfaces.md` lines 209/217 still call it "optional" while the Update
section says "now fitted". Electrically all agree (4.7 kΩ + two diode anodes), only the text differs.
Fix: 4.7 kΩ everywhere; describe D_PL once; mark the older F-interfaces paragraphs superseded.

**MINOR-2 — Block B's 2N7002 on `POE_LOSS_N` now sinks 1.37 mA at VGS = 3.3 V, and its RDS(on) is
specified only at VGS ≥ 5 V.** `B-interfaces.md` ("sinks the 0.7 mA easily"), `B-poe-loss-detect.md`,
`F-mute-relay.md` (assumes ≤ 0.1 V when tripped). Load = 3.3 V/4.7 kΩ + 2 × 3.3 V/10 kΩ = 1.37 mA;
F's gate ≤ 0.4 V claim needs VDS ≤ 0.1 V ⇒ RDS ≤ 73 Ω. JSCJ 2N7002 (2n7002-cj.pdf p.1): Vth 1.0–2.5 V,
RDS(on) ≤ 7 Ω only at VGS = 5 V. At Vth(max) the overdrive is 0.8 V; it almost certainly works, but
it is the same datasheet gap that failed F's B1. Fix (block B): drive the FET from the 1G123 and use
an AO3400A (already in F's BOM, basic part), or state the worst-case VDS from the datasheet curves.

**MINOR-3 — `/DC_TRIP` (= `HP_FAULT_N`) is read in hardware by block F's BAT54C OR but has a 10 kΩ
pull-up.** `F-mute-relay.md`; `E-pinmap.md` sweep item 5/6 says any net read in hardware needs
≤ 4.7 kΩ against the ECP5's 150 µA pull-down. With 10 kΩ the net sits at 1.8 V whenever the ECP5
pull-down is active (before configuration, or if PULLMODE=NONE on P11 is omitted); after
configuration with HP_EN high the OR diode then clamps the gates to ≈ 2.1 V, below the 2.5 V at
which RDS(on) is specified (still above Vth(max) 1.45 V, so the relays would probably still pull in).
Fix: 4.7 kΩ pull-up on /DC_TRIP (BC847B then sinks ≈ 1.4 mA, trivial), which removes the dependency
on an LPF line.

**MINOR-4 — PROGRAMN "after all rails stable" rule has no stated mechanism.** `E-fpga-ecp5.md`
fine print; TN-02039 §4.6.2 (p.16): "PROGRAMN must not be toggled low until after all power rails have
reached stable operation", and no falling edge during initialisation. The RP2350 boots from +3V3
alone and has no +1V1/+2V5 power-good input (PG_3V3_N goes to the FPGA). Fix: state the firmware
gate as "wait for INITN (GPIO23) high — which requires VCC, VCCAUX and VCCIO8 above POR and the
init phase finished (tICFG) — then a fixed delay (≥ 10 ms) before the first PROGRAMN pulse"; the
same gate before every A/B reload.

**MINOR-5 — D[7:2] have no internal pull during configuration (TN-02039 §5.2 p.23 and §6.3 p.40:
"the PCB design should include them").** `E-pinmap.md` relies on the RP2350 pads' reset pull-downs
(36–113 kΩ) on GPIO8–15. That is sound only while firmware leaves the pad pull-downs enabled when it
tri-states the link (before DONE and before every PROGRAMN pulse). Add that line to the `E-link.md`
firmware rules, or fit 100 kΩ pull-downs on the six non-SPI D lines.

**MINOR-6 — `ACF_PULSE` description is stale and the series value disagrees.** `E-pinmap.md` B6 row
and line 309, `E-interfaces.md` signals table: "620 kHz ± 10 %"; block B is crystal-locked at
737.28 kHz (`B-sync-clock.md`), the pulse is the converter on-time (≈ 0.6–0.9 µs). E fits 4.7 kΩ
series; `B-interfaces.md` says "1 k series". RC = 4.7 kΩ × 8 pF = 38 ns, fine either way; agree one
value and frequency.

**MINOR-7 — `IBUS_SENSE` pin capacitor: 10 nF (E review-response row, `B-interfaces.md`) vs 100 nF
(`E-pinmap.md`, `E-fpga-ecp5-passives.md`).** Either works (24 Hz or 240 Hz pole with 67 kΩ); pick one.

**MINOR-8 — Residual stale text.** `E-fpga-ecp5.md` line 40 "ADC CS get 10 kΩ pull-ups" (passives
and pin map: 4.7 kΩ) and open question "1.453 vs 1.017 ns"; `E-pinmap.md` headroom table lists T3 as
a bank-6 spare while the text says T3 must stay NC; `F-overview.md` line 46 "driven through 2N7002
FETs", its FPGA-pin table (HP_DET "RP2350 GPIO preferred", HP_FAULT_N "optional") and its rail table
(+3V3_Q 20/30 mA vs the agreed 35 mA); `F-interfaces.md` lines 29–33 and 143–154 (TCA9535, 2N7002)
not marked superseded.

**MINOR-9 — Lead's files out of step with R-53.** `architecture.md` reconciliation (the section that
"wins") still says "PWM edge grid 1.453 ns" and "448 kHz baseline (512/672 options)";
`D-interfaces.md` line 28 "E sizes the noise shaper for 448 kHz" (its line 78 says 576 kHz).
`intent.md` R-53 and `decisions.md` (2026-11-08) are right: 576 kHz, 1.695 ns.

### NOTE

- NOTE-1 Converter clock-fault rule (`E-interfaces.md`): with no PoE (USB-only, R-23) there are no
  ACF pulses, so the counter must be qualified by "VBUS valid / amp start requested" or it reports a
  spurious converter fault over the network on every USB-only session.
- NOTE-2 100 kΩ pull-ups into FPGA inputs after configuration (`PG_3V3Q` from C, `HP_DET` from F):
  ECP5 IIL/IIH ≤ 10 µA (DS Tab 3.7 p.53) → ≥ 2.24 V at a 3.24 V rail vs LVCMOS33 VIH 2.0 V (Tab 3.12
  p.58). Passes with 0.24 V; 47 kΩ would be more comfortable (TPS7A94 RPG range 10–100 kΩ allows it).
- NOTE-3 `F-hp-output-stage.md`: the limiter is 39–47 mA over the BC847B VBE spread, so the stated
  17 K Tj margin at 1 cm² is 12 K at the high corner; the "≥ 2 cm² per tab" layout line is therefore
  a real requirement for phase 4/6, not a nicety. Add the VBE spread to the phase 8 short-circuit case.
- NOTE-4 F m3 dispute (PCM1808 pin ≤ 70 mV over VCC + 0.3 V in the misuse case): the author's
  argument is correct (BAT54S VF ≥ 0.3 V at mA; bat54s.pdf), but review-protocol.md says disputes go in
  `decisions.md`; it is only in the audit. Log it.
- NOTE-5 Jitter claims vs the sheets on file: `F-yxc-ot2el-24m576.pdf` p.1 (YSO110TR) states
  phase jitter 0.7 ps max, 12 kHz–20 MHz, tr/tf ≤ 4 ns, VDD 1.8–3.3 V — block F's 4-tap ≤ 1 ps claim
  holds for the fallback XO (ordering-code caveat correctly recorded). `sx3v-vcxo.pdf` p.1 gives no
  phase-noise figure (APR ±50 ppm, Vc 0.3–3.0 V, Rin ≥ 5 MΩ, tr/tf ≤ 5 ns): "UNVERIFIED" is the right
  label, and the fallback XO's 4 ns edge also misses the ECP5 PLL's 1 ns tR/tF, so MINOR-4 (first
  pass) stays a deviation on either part.
- NOTE-6 Hot-socket check of the moved/new balls (CSV): P4 PL41A pairs with R3 PL41B (`IS_SDI`, an
  FPGA output; a pull-up leaking into SDI while CS is high is harmless); G15 PR14B pairs with F16
  PR14A (both outputs); A6/B3/B4/B6 are top-bank (IDK ≤ ±1 mA). K13/K12 and P11/P12 partners NC ✓.
- NOTE-7 PCM1808 SCKI from the 3.3 V buffer: VIH 2.0 V min, Schmitt, 5 V-tolerant (pcm1808.pdf p.3
  note 2) ✓; its clock-halt reset covers the +5V_A-off / +3V3-on USB-only state.
- NOTE-8 RMII TX hold still depends on an unspecified min tCO (first-pass open item); carried to
  the nextpnr timing report, as the audit says.

## Cross-block consistency (E ↔ F ↔ C ↔ D)

- `PD_PG_N`: active low, high = primary dead, in `A-interfaces.md`, `E-pinmap.md` A2, `E-interfaces.md`
  gateware rules, `F-mute-relay.md`, `F-interfaces.md` Update, `C-sequencing.md` (both the firmware
  checklist and the fabric gate `!PD_PG_N & POE_LOSS_N`). Consistent; the mute trigger is
  "PD_PG_N rising or POE_LOSS_N falling" everywhere.
- `PG_3V3Q`: TPS7A94 PG, 100 kΩ pull-up (C) → 1 kΩ series → ECP5 B5; DAC lines held low until high;
  pre-configuration reads low = safe. C, E, F and architecture agree.
- Relay enables: E M14/N14 with no series R; F 10 kΩ gate + 100 kΩ pull-down; AO3400A. Agree
  (apart from the stale text in MINOR-8).
- DAC clock path: VCXO → 33 Ω (E) → SN74LVC2G34 on +3V3_Q (F) → 22 Ω → 8 × 74LVC74A CP, and → 33 Ω →
  PCM1808 SCKI; FPGA PLL input P6 on its own unresistored branch. E and F agree; the FFs never see
  the FPGA clock (R-55). Timing: FPGA ≤ 8 ns derated vs F's 12 ns budget ✓.
- Rail loads: E → C +3V3 350 mA, +1V1 400 mA, +2V5 50 mA; F → C +15 V 120/200 mA, −15 V 110/190 mA,
  +3V3_Q 35 mA, +5V 56 mA (relays), +5V_A 15 mA, +3V3 10 mA. All appear with the same numbers in
  `C-interfaces.md` (C carries 135/215 mA on +15 V as margin). Agree.
- D ↔ E: 27 signals, 330 Ω on FAULT_x_n, 1 kΩ on DC_x_n, DC_x_n pull-ups 4.7 kΩ, three CS pull-ups
  4.7 kΩ, VB_CS_n on P4, VDRV good over the link, fsw 576 kHz. Agree except `D-interfaces.md` line 28
  (MINOR-9).

## Verdict

- **Block E: PASS.** MAJOR-1/2/3 are closed on re-derivation; the remaining items are text
  consistency and two firmware-rule statements (MINOR-4, MINOR-5).
- **Block F: PASS.** B1, M1 and M2 are closed on re-derivation; MINOR-3 (4.7 kΩ on /DC_TRIP) is
  the one cheap part change, the rest is text. MINOR-2 is for block B.
