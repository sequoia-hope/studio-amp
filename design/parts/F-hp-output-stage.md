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

## Circuit (per channel), revised after review M1

```
 +15V ─ R_ES 180Ω ─ E(Q_ST BC857B) C ─┬──────────── 100Ω ─ B(Q_N BCP56)   C ─ +15V      Q_ST base: BAV99 (2 VF) from +15V,
                                      │  Q_LN C    ┌─ B(Q_LN) ─ E(Q_N) ─┐ D_RN        15 kΩ from base to GND
                                BAV99 pin1(A1)     │                    R_E 15Ω (D_RN: 1N4148WS, A=E(Q_N), K=B(Q_N))
 U_HP out ─ R_D 1.0k ─ BAV99 pin3 (mid) + R_SPR    └─ E(Q_LN) ─────────┤OUT_INT ── Rf 1k (‖1nF) ─► U_HP IN−
                                BAV99 pin2(K2)                          │                          Rg 3.3k to GND
                                      │  Q_LP C    ┌─ E(Q_LP) ──────────┤
 −15V ─ R_ES 180Ω ─ E(Q_SB BC847B) C ─┴──────────── 100Ω ─ B(Q_P BCP53) R_E 15Ω (D_RP: 1N4148WS, A=B(Q_P), K=E(Q_P))
                                                                        │
                                 OUT_INT ─ Zobel 10Ω + 4.7nF C0G ─ GND
                                 OUT_INT ─ R_OUT 4.7Ω ─ OUT_HP ─ BAV99 clamp to ±15V ─ relay K1 COM→NO ─ ferrite ─ jack (TVS)
```

- **Bias string:** the R_T/R_B resistors are replaced by two ≈ 4 mA current sources.
  - Top: Q_ST BC857B, with emitter R_ES 180 Ω to +15 V. Its base is held at +15 V − 2 VF by a
    BAV99 series pair, with 15 kΩ from the base to GND (≈ 0.9 mA reference).
  - Bottom: Q_SB BC847B, the mirror image to −15 V.
- **R_D = 1.0 kΩ** between the op-amp output and the spreader midpoint.
- **D_RN, D_RP** (1N4148WS): anti-parallel across each output transistor's B-E junction. They
  stop the op-amp from reverse-biasing the off device's E-B junction during a short.
- **Limiter:** Q_LN's base goes to Q_N's emitter (top of R_E), its emitter to OUT_INT, and its
  collector to Q_N's base node. It steals Q_ST's current when I·R_E > VBE. Q_LP is the mirror
  image.
- **R_SPR:** 10 Ω fitted in the BAV99 spreader string (Iq trim; see below).

## Absolute max vs worst case

| Part / parameter | Abs max | Worst case | Margin |
|---|---|---|---|
| BCP56/53 VCEO | 80 V | 30 V (rail to rail when the opposite device conducts at full swing; normally ≤ 15 V + 7.4 V = 22.4 V) | OK |
| BCP56/53 VEBO | 5 V | ESD transient at the emitter while the base is held: limited by R_OUT + clamp. In normal operation ≤ 0.7 V reverse | OK |
| BCP56/53 IC | 1 A (2 A pk) | 43 mA (limited) | OK |
| BCP56/53 Tj | 150 °C | 133 °C in a sustained short at 1 cm² copper (below) | 17 K |
| BCP56/53 VEBO in a short | 5 V | clamped to 0.7 V by D_RN/D_RP | OK |
| BC847/857 VCEO | 45 V | ≤ 2 V when active; ≤ 15 V reverse-case | OK |
| BC847/857 IC | 100 mA | limiter: ≤ 4 mA (the current source); current sources: 4 mA | OK |
| BC857/847 current source, Ptot 250 mW | 250 mW | ≤ 21.6 V × 4 mA = 86 mW (output at the opposite peak). Tj ≈ 55 + 0.086 × 500 K/W = 98 °C | OK |
| 1N4148WS (D_RN/D_RP) | 150 mA | ≤ 8 mA in a short | OK |
| BAV99 IF | 215 mA | 4 mA string; ≤ 11.3 mA in a short; clamp diodes carry ESD residue | OK |
| BAV99 VR | 100 V | 30 V | OK |

## Calculations

**Output level (R-13):** 5.2 Vrms = 7.35 Vpk at 0 dBFS. Into 300 Ω: 24.5 mA pk (≤ 25 mA, OK);
into 600 Ω: 12.3 mA pk. The top base node needs 7.35 + R_E·I (0.37) + VBE (0.65) = 8.4 V,
which is within the top current source's compliance (VCE 5.9 V at that point). OK.

**Current limit:** Q_LN turns on when I_E·R_E ≈ VBE(BC847B at the 4 mA it must sink) ≈ 0.65 V.
I_lim ≈ **43 mA at 25 °C**.
- At the 24.5 mA operating peak, the limiter's VBE is 0.37 V. That is about 5 decades below the
  4 mA conduction point (Ic ∝ e^(VBE/26 mV)), so it is inactive in normal use.
- VBE falls 2 mV/K, so the limit drops to ≈ 35 mA at 100 °C board temperature. That is
  self-protecting.
- The 300 Ω load (24.5 mA) plus the Zobel (4.3 mA) = 28.8 mA stays below the hot limit.

**Base drive (review m1 resolved):** At +7.35 V out and 24.5 mA, I_B = 24.5 mA/hFE(min 63)
= 0.39 mA, taken from the 4 mA top source. The bottom source still sinks 4 mA, so the op-amp
supplies only the base-current difference: **≤ 0.4 mA** (it was ≈ 7 mA with the old 2.2 kΩ
resistors, per the review). The drop across R_D is ≤ 0.4 V.
- Op-amp output at the peak = base node − VF + 0.4 V = 8.37 − 0.69 + 0.4 = **8.1 V**, against a
  ±12 V minimum swing. OK.
- Current-source compliance: the top base node reaches 8.37 V, and Q_ST's emitter sits at
  15 − 0.73 V. VCE = 5.9 V. OK.

**Current sources:** VR = 2 × VF(BAV99 at 0.9 mA) ≈ 1.38 V (VF ≤ 715 mV max at 1 mA).
VBE(BC857B at 4 mA) ≈ 0.65 V. I = (1.38 − 0.65)/180 Ω = **4.0 mA**.
- Tempco: (−4 + 2 mV/K)/0.73 V = −0.27 %/K, so −8 % from 25 to 55 °C. Harmless.
- Each source dissipates ≤ 86 mW (table).

**Quiescent current (bias):** String current 4.0 mA.
- VF(BAV99 at 4 mA) ≈ 0.69 V typ, from the Table 7 maxima (715 mV at 1 mA, 855 mV at 10 mA) and
  the usual 60 mV/decade.
- BCP56 VBE at ≈ 4 mA, 25 °C: 0.64 V (Fig. 7, curve 2). BCP53 is similar.
- Iq = [2(VF − VBE) + 4 mA × R_SPR]/(2·R_E) = (0.10 + 0.04)/30 = **≈ 4.7 mA** with R_SPR = 10 Ω.
- Spread: VF − VBE ranges over 0 to 0.12 V, so Iq is 1.3–9 mA. R_SPR is selectable 0–22 Ω, and
  phase 8 picks the value from worst-case models.
- Thermal stability: the transistors heat at ≈ 125 K/W. At 5 mA, P = 75 mW, ΔT = 9 K,
  ΔVBE = −19 mV, so ΔIq = +0.6 mA. Stable, because R_E degeneration dominates.

**Dissipation per output transistor (Tamb 55 °C):**
- Idle: 15 V × 5.3 mA = 80 mW (worst Iq 10 mA: 150 mW).
- Full-scale sine into 300 Ω: P = VCC·Vp/(πR) − Vp²/(4R) = 15 × 7.35/(π·300) − 7.35²/1200
  = 0.117 − 0.045 = 72 mW, plus the bias share, about 0.15 W.
- **Sustained short at the jack** (review M1): one device conducts continuously for a DC-like
  fault, or alternately per half-cycle.
  - Limit current: Q_LN sinks Q_ST's 4 mA at VBE ≈ 0.65 V, so I_lim ≈ 0.65/15 = **43 mA** at
    25 °C (≈ 39 mA at 55 °C).
  - P = (15 − 0.65) × 43 mA = **0.62 W**. With 1 cm² collector copper (125 K/W):
    Tj = 55 + 78 = **133 °C**. With 6 cm² (93 K/W): 113 °C.
  - **Layout requirement: ≥ 2 cm² of copper per tab.**
- **The SA5532 in the same short:**
  - The loop drives the op-amp to its rail (+13 V). Q_N's base node is clamped by Q_LN at
    ≈ 1.3 V, so the upper spreader diode is reverse-biased (the midpoint sits at ≈ 1.7 V). The
    op-amp cannot feed Q_LN, and Q_LN sinks only the 4 mA source.
  - The op-amp current flows through R_D, the lower spreader diode and D_RP into R_E and the
    short: (13 − 1.7 V)/1.0 kΩ = **11.3 mA**. A part with IOS near its 10 mA minimum may limit
    slightly below that, which only lowers the dissipation. Either way the current is set by R_D,
    not by the op-amp's current limit.
  - The op-amp output stage dissipates (15 − 13) × 11.3 mA = **23 mW**. R_D dissipates
    11.3² × 1 kΩ = **0.13 W**: use 1206 0.25 W (51 %).
  - **SA5532 Tj** (θJA 97 °C/W, ICC max 16 mA, so 0.48 W quiescent):
    - one channel shorted: 55 + (0.48 + 0.023) × 97 = **104 °C**;
    - both shorted: 55 + (0.48 + 0.046) × 97 = **106 °C**.
    Both are < 150 °C. With typical ICC (8 mA) the figures are 81/83 °C.
  - D_RP holds Q_P's base within 0.7 V of its emitter (VEBO 5 V protected). It carries
    11.3 − 4 = 7.3 mA. The mirror case (negative short) uses D_RN.
- SOA: the datasheet has no SOA curve. 15 V at 43 mA DC is 0.62 W, against Ptot 0.65–1.35 W, and
  far below the 1 A/80 V corners. There is no second-breakdown concern at 0.6 W and 15 V for this
  1 A die.

**Emitter resistors:** R_E = 15 Ω. In a short, P = 43 mA² × 15 = 28 mW; at full output into
300 Ω the average is ≈ 4.5 mW. A 1/10 W 0603 is fine.

**Current-source resistors:** R_ES = 180 Ω, 4 mA, so 2.9 mW. Reference resistor 15 kΩ: 14 mW.
0603 1 %.

**Output resistor:** R_OUT = 4.7 Ω, 0805, outside the loop.
- Stability with cable capacitance: it isolates up to 10 nF; the pole at 3.4 MHz is beyond the
  10 MHz-GBW loop's crossover/1.3.
- Damping: Zout ≈ 4.8 Ω including the relay, so damping factor 62 at 300 Ω.
- Level loss: −0.14 dB at 300 Ω.
- Power in a short: 43 mA² × 4.7 = 9 mW.

**Zobel (review m5):** 10 Ω + **4.7 nF** C0G (0603/0805, 50 V), from OUT_INT to GND. It is
mostly a resistive 10 Ω load above 3.4 MHz, which keeps the emitter followers stable.
- At 20 kHz full scale it draws 7.35 V × 2π × 20 kHz × 4.7 nF = 4.3 mA pk.
- Load plus Zobel: 24.5 + 4.3 = **28.8 mA**, against a hot limiter at ≥ 33 mA (100 °C board). No
  clipping.
- Rejected: 10 nF (34 mA, which clips when hot) and 100 nF.

**HP driver gain:** 1 + 1k/3.3k = 1.303. Cf = 1 nF across Rf gives a 159 kHz zero/pole (gain
→ 1 at HF), the 4th filter pole for the HP path.

## Fine print / gotchas

- BCP56 Fig. 5: hFE falls past 0.5 A. Not relevant here.
- BCP53 datasheet: "BC53PA" has different thermal values. We use the SOT-223 BCP53 row:
  192/125/93 K/W.
- Emitter followers can oscillate in the 100 MHz range with long base traces. Use 100 Ω base
  stoppers right at the base pins.
- Plugging a TRS plug in momentarily shorts tip, ring and sleeve. The limiter covers it.
- 32 Ω headphones (outside R-13): the limiter clips at 43 mA × 32 Ω = 1.4 Vpk. No damage.

## Layout guidance

- Put Q_N and Q_P next to each other with their tabs on separate pours (+15 V and −15 V are the
  collectors), each ≥ 2 cm².
- Put the BAV99 string between them and touching both, to give some thermal coupling to the
  diodes.
- Put the limiter transistors at the R_E resistors.
- Take the feedback from OUT_INT at the junction of the two R_E. Put the Zobel at OUT_INT.

## Open questions

- Phase 8 (added to the `F-overview.md` list):
  - the Iq distribution (choose R_SPR);
  - crossover THD;
  - the sustained-short case with both channels, checking the 43 mA limit, the 11.3 mA op-amp
    current and the Tj figures above;
  - stability with 4.7 nF Zobel and 0–10 nF cable.
