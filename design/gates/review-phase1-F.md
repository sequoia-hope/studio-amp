# Phase 1 review, block F (analog audio)

Date: 2026-11-07. Independent reviewer; judged from the artifacts only.
Scope: `design/parts/F-*.md` (4-tap FIR 1-bit DAC on 74LVC74A with SN74LVC2G34 clock buffer,
SA5532 MFB reconstruction filter and line driver, OPA2277 DC servo, BCP56/BCP53 class-AB headphone
stage with BC847/BC857 limiter, HFD4 mute relays with DC detector, PCM1808 mic ADC with preamp and
plug-in power, T3902 PDM mic, jacks, PESD15VL1BA ESD) against `design/intent.md` (R-13..R-16,
R-34, R-40, R-41, R-42, R-52), `design/architecture.md` (phase 1 reconciliation),
`design/parts/{C,E,F}-interfaces.md`, and the datasheets in `design/datasheets/` (re-read via
pdftotext, not the audits' quotes). Recomputation script: scratchpad `calc/filt.py` (MNA nodal
analysis of the differential MFB with resistor, en and in noise, A-weighted, at 55 °C).

What was verified and agrees with the audits (no finding): filter gain 3.51 V/V per differential
volt and a Butterworth-like response with −3 dB at 46 kHz (audit 47.4 kHz), no peaking; gain staging
m = 0.487 → 4.0 Vrms line / 5.2 Vrms HP (5.12 Vrms at the jack after 4.7 Ω into 300 Ω, meets R-13);
servo corner 0.31 Hz (R3/R_INJ = 0.195 confirmed by nodal solution); 74LVC74A timing (tsu 2.0,
th 1.0 ns at 3.0–3.6 V, Table 8), CPD 19.1 pF → 12.4 mA for 8 FFs; SN74LVC2G34 Ioff ±10 µA and
5.5 V-tolerant inputs; PCM1808 abs max, slave mode MD1 = MD0 = L, LRCK setup 50 ns / hold 10 ns,
sync ±5 BCK, clock-halt reset 4 µs; T3902 VDD 1.65–3.63 V, Standard-mode clock 1.0–3.3 MHz,
"no pull-up or pull-down on DATA" (p. 727 of text), 0.5–1 mm sound hole; PESD15VL1BA VRWM 15 V,
V(BR) 17.1 V min, 16 pF, IEC 61000-4-2 level 4 > 8 kV contact; BAV99 IF 215 mA, IFSM 4 A/1 µs,
VF 715/855 mV at 1/10 mA; BCP56/53 Ptot 0.65/1.0/1.35 W and Rth(j-a) 192/125/93 K/W for
standard/1 cm²/6 cm² pads, hFE(-16) ≥ 63 at 5 mA; HFD4/5 coil 178 Ω ±10 %, pick-up 3.75 V,
release 3 ms, min load 10 mV/10 µA, −40 to +85 °C; RT0603 "B/D" = ±0.1 %/25 ppm valid 1 Ω–1 MΩ
(so R_S = 1 MΩ is in range); GRM2195C1H153 is 0805 C0G 50 V; CC1206KKX7R8BB106 (10 µF/25 V/1206
X7R) exists in the Yageo table; package suffixes match footprints for every MPN; all 26 `show`
lines re-run 2026-11-07 agree (stock changes of a few units only). Interface figures (+15 V 120 /
−15 V 110 mA, +3V3_Q 34–35 mA, +5V_A ≤ 15 mA, +5V 56 mA, FPGA balls, 330 Ω on DOUT/PDM_DAT, 1 kΩ on
HP_EN/LO_EN, PG_3V3Q gateware rule) are consistent between F-, C- and E-interfaces.

## BLOCKER

### B1. Relay driver cannot be shown to energise the coil (F-mute-relay.md, 2n7002-cj.pdf p. 1–2, hfd4.pdf coil data p. 2)
- Problem: The 2N7002 (JSCJ) specifies Vth(GS) 1.0–2.5 V and RDS(on) only at VGS = 5 V and 10 V.
  The gate is fed from the FPGA through 1 kΩ (block E) + 10 kΩ (block F) against a 100 kΩ
  pull-down, so VGS = 3.3 × 100/111 ≈ **2.97 V**. Worst-case overdrive is 0.47 V. From the
  datasheet corner RDS(on) ≤ 7 Ω at VGS = 5 V with Vth = 2.5 V, K ≈ 1/(7 × 2.5) = 0.057 A/V², so the
  saturation current at VGS = 2.97 V is ≈ 0.057/2 × 0.47² ≈ **6 mA**, and even at Vth = 1.6 V
  typical it is ≈ 50–100 mA only if the typical RDS(on) is assumed. The coil needs 28 mA (31 mA at
  −10 % resistance) and Hongfa note 2 requires the rated step voltage at the coil; note 3 already
  recommends the 4.5 V coil for a 5 V transistor drive. On paper the relays may never pull in, and a
  relay that does not pull in means no headphone or line output at all (R-13, R-14). The audit's
  own text calls the margin "not in the datasheet, bring-up check", which is not a phase 1 pass.
- Fix: use a logic-level FET with RDS(on) specified at VGS ≤ 2.5 V and Vth(max) ≤ 1.5 V (e.g.
  AO3400A, C20917, basic; or any SOT-23 NMOS with RDS(on) ≤ 0.5 Ω at 2.5 V), or an NPN switch
  (BC847B, base 2.2 kΩ from the FPGA; 1 mA base for 28 mA at hFE ≥ 200) which is immune to the
  divider. Then re-check the DC-detector override: with /DC_TRIP pulled to ≈ 0.1 V through a
  1N4148WS the gate sits at ≈ 0.8 V, which is above the AO3400A's Vth(min) 0.65 V. Use BAT54
  Schottky OR diodes (gate ≤ 0.45 V) or let the detector pull each gate through its own
  transistor. Recompute the coil voltage ≥ 4.75 V (buck +5V 5.05 V minus switch drop) and log the
  result; remove the "bring-up" dependency.

## MAJOR

### M1. Headphone short: SA5532 output short-circuit current into the bias string is not in the thermal analysis (F-hp-output-stage.md, F-opamp-sa5532.md; ne5532.pdf p. 3 abs max, p. 4 IOS 10/38/60 mA, θJA 97 °C/W)
- Problem: In a sustained short (a TS mono plug permanently shorts ring to sleeve, i.e. the R
  channel, a realistic sustained case; a shorted cable shorts both), the limiter Q_LN clamps the Q_N
  base node at ≈ 1.3 V. The op-amp output connects to that node only through the upper BAV99, so
  the loop drives the op-amp into current limit: it sources IOS = 38 mA typ / **60 mA max** at an
  output voltage of ≈ 0.6 V, i.e. (15 − 0.6) × 0.06 = **0.86 W per half**, 0.55 W typical. One
  channel shorted: 0.86 + 0.24 (other half quiescent) = 1.1 W → Tj = 55 + 97 × 1.1 = **162 °C**
  (132 °C typical). Both shorted: 1.7 W → > 200 °C. The audit's short analysis covers only the
  BCP56 (0.62 W) and the op-amp line-out case. Also, Q_LN must then sink IOS plus R_T's current
  (≈ 66 mA, inside BC847B's 100 mA, 73 mW: OK), and its VBE rises to ≈ 0.75 V, so the output limit
  is ≈ 50 mA rather than 41 mA: BCP56 dissipation 0.75 W → Tj 149 °C at 1 cm² copper, ≈ 137 °C at
  the 2 cm² the audit asks for. R-13 says "short-circuit proof"; the SA5532 is not shown to be.
- Fix: make the bias string a pair of ≈ 3–4 mA current sources (BC857/BC847 + emitter resistor)
  in place of R_T/R_B, so the op-amp's normal peak drive falls from ≈ 7 mA (see m1 below) to ≈ 1 mA,
  and add 330–470 Ω between the op-amp output and the BAV99 midpoint. In a short the op-amp then
  swings to the rail (≈ 13 V) and dissipates ≈ 40 mW while the resistor takes ≈ 0.3–0.4 W (use
  1206 ≥ 0.5 W or 2010). Re-check headroom (7.7 V + I·R ≤ 12 V min swing). Alternatively fold the
  limiter back onto the op-amp output node with a second transistor pair, or accept and show Tj
  < 150 °C with IOS max for both channels shorted. Add this case to the phase 8 list.

### M2. X7R capacitors in the measurement-mic signal path with DC bias, on a board bolted to a loudspeaker (F-mic-adc-pcm1808.md; R-15, R-41)
- Problem: C_IN (4.7 µF X7R 50 V, 5 V DC bias) is in series with the mic signal, and the 10 µF X7R
  25 V coupling capacitors (2.5 V bias) are in series with both ADC inputs. X7R is piezoelectric,
  more so under DC bias; the board is mounted to the back panel of a cabinet playing the very test
  signal the mic is measuring (R-41: vibration at high SPL). The resulting voltage is correlated
  with the stimulus and lands directly on a ~mV-level microphone signal, corrupting room-correction
  sweeps. The audit itself forbids X7R in the DAC filter for "voltage coefficient and microphonics"
  (F-filter-passives.md) but applies none of that reasoning here.
- Fix: use non-piezoelectric parts: film (PET/PP, e.g. 1–2.2 µF 1206/1210 with the input bias
  resistor raised to 220–470 kΩ to keep the corner ≤ 2 Hz), or polymer/aluminium electrolytic, or
  C0G where the value allows. The same applies to the 47 µF bias-node capacitor only if a ceramic is
  chosen (prefer the tantalum/polymer option the audit lists). Document the dielectric choice per
  position in the mic chain.

## MINOR

- m1. HP stage op-amp drive current understated (F-hp-output-stage.md "Base drive"): at +7.35 V
  out, R_B pulls (15 + 6.3)/2.2 kΩ ≈ 9.7 mA while R_T supplies ≈ 3.0 mA, so the SA5532 sources ≈ 7 mA
  at the peak, not ≤ 3.5 mA. Still inside the 600 Ω drive spec; conclusion stands, fix the number
  (and see M1).
- m2. Noise budget is thinner than stated (F-overview.md): my recomputation at 55 °C gives the
  filter 5.45 µV A-wt with en = 5 nV typ and 5.8 µV with the SA5532A's en(max) = 6 nV at 1 kHz
  (ne5532.pdf p. 4); the quantisation-noise line is internally inconsistent (−135 dB re m = 1 is
  8.19 Vrms × 10^(−135/20) = 1.46 µV, not ≤ 0.5 µV). Line total ≈ 6.2 µV, HP ≈ 1.303 × 6.2 ⊕ 1.0
  ≈ 8.2 µV A-wt: still under R-52's 10 µV but with ≈ 1.7 dB margin, not 3 dB. Use en(max) and the
  consistent quantisation figure in the table.
- m3. PCM1808 anti-alias source resistance 2.2 kΩ is outside the datasheet's "100 Ω/0.01 µF to
  1 kΩ/1000 pF" (pcm1808.pdf p. 23), and the misuse clamp lets VIN reach VCC + 0.37 V against an
  abs max of VCC + 0.3 V (p. 2). Prefer splitting into 1 kΩ (pin side) + 1.2 kΩ with the BAT54S
  at the junction: the pin then sees ≤ VCC + 0.3 V with the datasheet-range source impedance, and the
  clamp current stays ≈ 5 mA.
- m4. DC detector sense point not specified (F-mute-relay.md): the four 47 kΩ inputs must be on the
  amplifier side of the relays (OUT_HP, line op-amp output), otherwise opening the relay removes the
  DC, N_DC decays and the relay re-closes (≈ 0.1–0.5 s chatter into a fault). Also note that with
  N_DC > 6 V the inverted BC847B (Q_DP) E-B junction avalanches (VEBO 6 V); the 10 kΩ limits it to
  ≤ 0.7 mA, harmless, but say so.
- m5. Zobel plus load at 20 kHz full scale draws 9.2 + 24.5 ≈ 34 mA pk against a 41 mA (33 mA at
  100 °C) limiter: the limiter can clip 20 kHz full-scale tones into 300 Ω when hot. Consider 4.7 nF
  in the Zobel or confirm in phase 8.
- m6. HFD4 coil "step voltage" (notes 2, 7) and the 4.5 V-coil recommendation (note 3) should be
  closed numerically once B1 is fixed (coil ≥ 4.75 V at +5V = 5.05 V).

## NOTE

- n1. R-40: NMJ6HCD2 is −25 to +70 °C (nmj6hcd2-spec.pdf): the waiver the audit requests is
  needed; the SJ1-3523N (85 °C) and RCJ-014 (85 °C) comply.
- n2. architecture.md "Phase 1 reconciliation" still lists +3V3_Q as TPS7A2033; C-interfaces.md and
  F-interfaces.md say TPS7A9401. Lead to align the text.
- n3. The YXC datasheet on file (`yxc-ot2el-50m.pdf`, C5203552) is the 50 MHz part; the 0.7 ps
  figure block F relies on for the 24.576 MHz C5203547 is not on file, and both oscillator PDFs are
  image-only (pdftotext returns nothing). Block E scope, but F's 1 ps requirement rests on it.
- n4. Jitter model: the text formula F·E[Δy²]·σ²·f_B omits the one-sided factor 2, yet the quoted
  7.9 / 2.0 µV per ps match the correct 8.1 / 2.0; harmless.
- n5. 74LVC74A (Nexperia) has no Ioff; the gateware "DAC lines low until PG_3V3Q" rule is the right
  mitigation. Confirm the TI SN74LVC74APWR second source in phase 2 as planned; the JSMSEMI
  SN74LVC2G34 clone's Ioff is likewise unverified.
- n6. Mic plug-in power is 5 V open-circuit through 4.4 kΩ (2.8–3.7 V loaded) against R-15's
  "~2.5 V": fine for electret capsules, but record the deviation.
- n7. SA5532 input bias (≤ 1 µA) through the 100 kΩ preamp bias resistor gives ≤ 0.4 V DC at the
  preamp output; harmless behind the coupling capacitor, worth a line in the audit.

## Verdict

**Not passed as submitted**: fix B1 (relay driver provably energises the coil, with the detector
override re-checked) and M1/M2 (headphone-short op-amp dissipation; non-piezoelectric capacitors
in the mic path); the remainder of block F is datasheet-consistent and recomputes correctly.
