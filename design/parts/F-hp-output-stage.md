# Q_HP1–Q_HP4, Q_L1–Q_L4, D_B1–D_B2: discrete class-AB headphone output stage (R-13)

Datasheets (all read in full: limiting values, thermal, characteristics, curves, package):
- `datasheets/bcp56.pdf`: Nexperia BCP56 series, Rev. 11, 1 Jul 2022 (NPN, 80 V, 1 A).
- `datasheets/bcp53.pdf`: Nexperia BCP53/BCX53/BC53PA series (PNP, 80 V, 1 A).
- `datasheets/bc847.pdf`, `datasheets/bc857.pdf`: Nexperia BC847B / BC857B.
- `datasheets/bav99.pdf`: Nexperia BAV99.

| Ref (per channel) | Part | show line |
|---|---|---|
| Q_N (output NPN) | BCP56-16,115 | `C92221 BCP56-16,115 (Nexperia, SOT-223): extended, JLC stock 52391, lifecycle normal, checked 2026-11-07` |
| Q_P (output PNP) | BCP53-16,115 | `C85085 BCP53-16,115 (Nexperia, SOT-223): extended, JLC stock 31822, lifecycle normal, checked 2026-11-07` |
| Q_LN (NPN limiter) | BC847B,215 | `C57668 BC847B,215 (Nexperia, SOT-23): extended, JLC stock 359317, lifecycle normal, checked 2026-11-07` |
| Q_LP (PNP limiter) | BC857B,215 | `C59205 BC857B,215 (Nexperia, SOT-23): extended, JLC stock 126459, lifecycle normal, checked 2026-11-07` |
| D_B (bias spreader), D_CL (rail clamp) | BAV99,215 | `C2500 BAV99,215 (Nexperia, SOT-23): basic, JLC stock 1251380, lifecycle normal, checked 2026-11-07` |
| R_E (×2) | 15 Ω 0.1 % 0603 | `C705727 RT0603BRD0715RL (YAGEO, 0603): extended, JLC stock 10013, lifecycle normal, checked 2026-11-07` |

Multi-sourced: BCP56-16 is also made by onsemi (C16602), Slkor, Yangjie and others; BCP53-16 by
onsemi, CJ and JSMSEMI; BC847B/BC857B and BAV99 by everyone. Footprints: SOT-223 (SC-73, 4 leads;
tab = collector = pin 2/4) and SOT-23.
Pinning (datasheet Table 2/3):
- BCP56 and BCP53: 1 = B, 2 = C, 3 = E, 4 (tab) = C.
- BAV99: 1 = A1, 2 = K2, 3 = K1/A2 (two diodes in series).

## Circuit (per channel)

```
 +15V ─ R_T 2.2k ─┬────────────── 100Ω ─ B(Q_N BCP56)   C ─ +15V
                  │  Q_LN C       ┌─ B(Q_LN) ─ E(Q_N) ─┐
             BAV99 pin1(A1)       │                    R_E 15Ω
 U_HP out ── BAV99 pin3 (mid)     └─ E(Q_LN) ─────────┤OUT_INT ── Rf 1k (‖1nF) ─► U_HP IN−
             BAV99 pin2(K2)                            │                          Rg 3.3k to GND
                  │  Q_LP C       ┌─ E(Q_LP) ──────────┤
 −15V ─ R_B 2.2k ─┴────────────── 100Ω ─ B(Q_P BCP53) R_E 15Ω
                                                       │
                                 OUT_INT ─ Zobel 10Ω+10nF C0G ─ GND
                                 OUT_INT ─ R_OUT 4.7Ω ─ OUT_HP ─ BAV99 clamp to ±15V ─ relay K1 NO ─ jack (TVS)
```
Limiter Q_LN: base to Q_N's emitter (top of R_E), emitter to OUT_INT, collector to Q_N's base
node. It steals R_T's current when I·R_E > V_BE. Q_LP is the mirror image. There is an optional
series trim position R_SPR (0 Ω fitted) inside the BAV99 string, for adjusting Iq.

## Absolute max vs worst case

| Part / parameter | Abs max | Worst case | Margin |
|---|---|---|---|
| BCP56/53 VCEO | 80 V | 30 V (rail to rail when the opposite device conducts at full swing; normally ≤ 15 V + 7.4 V = 22.4 V) | OK |
| BCP56/53 VEBO | 5 V | ESD transient at the emitter while the base is held: limited by R_OUT + clamp. In normal operation ≤ 0.7 V reverse | OK |
| BCP56/53 IC | 1 A (2 A pk) | 41 mA (limited) | OK |
| BCP56/53 Tj | 150 °C | 133 °C in a sustained short (below) | 17 K |
| BC847/857 VCEO | 45 V | ≤ 2 V when active; ≤ 15 V reverse-case | OK |
| BC847/857 IC | 100 mA | ≤ R_T current, 6.5 mA | OK |
| BAV99 IF | 215 mA | 6.5 mA string; clamp diodes carry ESD residue | OK |
| BAV99 VR | 100 V | 30 V | OK |

## Calculations

**Output level (R-13):** 5.2 Vrms = 7.35 Vpk at 0 dBFS. Into 300 Ω: 24.5 mA pk (≤ 25 mA, OK);
into 600 Ω: 12.3 mA pk. The swing needs 7.35 V + R_E·I (0.37 V) + Vbe (0.7 V) + R_T drop. The
top base node needs ≥ 8.4 V while R_T must still deliver base current, so the headroom to +15 V
is 6.6 V. OK.

**Current limit:** Q_LN turns on when I_E·R_E ≈ 0.62 V (BC847B at about 100 µA, enough to steal
R_T's current at the BCP56 base drive). I_lim = 0.62/15 = **41 mA at 25 °C**. At the 24.5 mA
operating peak the limiter's Vbe is 0.37 V, about 7 decades below conduction (Ic ∝ e^(Vbe/26 mV)),
so it is inactive in normal use. With Vbe falling 2 mV/K, the limit drops to ≈ 33 mA at 100 °C
board temperature. That is self-protecting.

**Base drive:** at +7.35 V out and 24.5 mA, I_B = 24.5 mA/hFE. The worst-case hFE ≥ 63 (BCP56-16
at 5 mA; ≥ 100 at 150 mA), giving 0.39 mA. R_T supplies (15 − 7.35 − 0.37 − 0.65 − ~0.75)/2.2k
= 2.7 mA at that peak. OK, 7× margin. The SA5532 supplies the difference between the R_T and R_B
string currents: ≤ (6.2 − 2.7) = 3.5 mA. That is well inside its drive.

**Quiescent current (bias):** The string current at idle is (15 − 0.64 − 0.72)/2.2 kΩ = 6.2 mA.
- The BAV99 spreads 2·VF. VF ≈ 0.72 V typ at 6 mA, from the Table 7 maxima (715 mV at 1 mA,
  855 mV at 10 mA) and the usual 60 mV/decade.
- BCP56 VBE at 5 mA, 25 °C: 0.64 V (Fig. 7, curve 2). BCP53 is similar.
- Iq = 2(VF − VBE)/(2·R_E) = 2 × 0.08/30 = **≈ 5.3 mA**.
- Spread: VF − VBE ranges over 0 to 0.15 V, so Iq is 0–10 mA. Below ≈ 2 mA the crossover
  distortion rises (the loop corrects it). The R_SPR trim position (0–22 Ω) adds 6.2 mA × R_SPR,
  i.e. +2 mA per 10 Ω.
- Thermal stability: the diodes are on the board and the transistors heat at ≈ 125 K/W. At Iq =
  5 mA, P = 75 mW, ΔT = 9 K, ΔVBE = −19 mV, so ΔIq = +0.6 mA. Stable, because R_E degeneration
  dominates.

**Dissipation per output transistor (Tamb 55 °C):**
- Idle: 15 V × 5.3 mA = 80 mW (worst Iq 10 mA: 150 mW).
- Full-scale sine into 300 Ω: P = VCC·Vp/(πR) − Vp²/(4R) = 15 × 7.35/(π·300) − 7.35²/1200
  = 0.117 − 0.045 = 72 mW, plus the bias share, about 0.15 W.
- **Sustained short at the jack** (only one device conducts per half-cycle; for a DC-like fault
  one device conducts continuously): 15 V × 41 mA = **0.62 W**. With ≥ 1 cm² collector copper
  (Rth(j-a) = 125 K/W, Table 6 note 2): Tj = 55 + 0.62 × 125 = **133 °C** < 150 °C. With 6 cm²
  (93 K/W): 113 °C. **Layout requirement: ≥ 2 cm² of copper on each tab**, which can be inner or
  bottom pour stitched with vias.
- SOA: the datasheet has no SOA curve. 15 V at 41 mA DC is 0.6 W, against Ptot 0.65–1.35 W, and
  far below the 1 A/80 V corners. There is no second-breakdown concern at 0.6 W and 15 V for this
  1 A die.

**Emitter resistors:** R_E = 15 Ω. In a short, P = 41 mA² × 15 = 25 mW; at full output into
300 Ω the average is ≈ 4.5 mW. A 1/10 W 0603 is fine.

**R_T, R_B:** 2.2 kΩ.
- Idle: 6.2 mA² × 2.2 kΩ = 85 mW.
- Worst case: R_B at the positive output peak (+7.35 V out). Its node then sits at ≈ +7.35 − 1.4
  = 5.95 V, so it sees 15 + 5.95 = 20.95 V, which is 0.20 W at the peak.
- Average for a full-scale sine: ≈ 0.12 W.
- **Use 1206 thick film, 1 %, 0.25 W** (≤ 80 % at the peak, 48 % average).

**Output resistor:** R_OUT = 4.7 Ω, 0805, outside the loop.
- Stability with cable capacitance: it isolates up to 10 nF; the pole at 3.4 MHz is beyond the
  10 MHz-GBW loop's crossover/1.3.
- Damping: Zout ≈ 4.8 Ω including the relay, so damping factor 62 at 300 Ω.
- Level loss: −0.14 dB at 300 Ω.
- Power in a short: 41 mA² × 4.7 = 8 mW.

**Zobel:** 10 Ω + 10 nF C0G (0805, 50 V), from OUT_INT to GND.
- Its job is the high-frequency load that keeps the emitter followers stable. It is mostly a
  resistive 10 Ω load above 1.6 MHz.
- Audio-band load: at 20 kHz and full scale it draws 7.35 V × 2π × 20 kHz × 10 nF = 9.2 mA pk.
  Music has little energy there.
- Rejected: 100 nF, which would draw 92 mA pk at 20 kHz, over the 41 mA limit.

**HP driver gain:** 1 + 1k/3.3k = 1.303. Cf = 1 nF across Rf gives a 159 kHz zero/pole (gain
→ 1 at HF), the 4th filter pole for the HP path.

## Fine print / gotchas

- BCP56 Fig. 5: hFE falls past 0.5 A. Not relevant here.
- BCP53 datasheet: "BC53PA" has different thermal values. We use the SOT-223 BCP53 row:
  192/125/93 K/W.
- Emitter followers can oscillate in the 100 MHz range with long base traces. Use 100 Ω base
  stoppers right at the base pins.
- Plugging a TRS plug in momentarily shorts tip, ring and sleeve. The limiter covers it.
- 32 Ω headphones (outside R-13): the limiter clips at 41 mA × 32 Ω = 1.3 Vpk. No damage.

## Layout guidance

- Put Q_N and Q_P next to each other with their tabs on separate pours (+15 V and −15 V are the
  collectors), each ≥ 2 cm².
- Put the BAV99 string between them and touching both, to give some thermal coupling to the
  diodes.
- Put the limiter transistors at the R_E resistors.
- Take the feedback from OUT_INT at the junction of the two R_E. Put the Zobel at OUT_INT.

## Open questions

- Phase 8: the Iq distribution and the crossover THD. If Iq < 2 mA in simulation with worst-case
  models, fit R_SPR = 10 Ω.
