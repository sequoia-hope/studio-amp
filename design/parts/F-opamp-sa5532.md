# U_F1, U_HP1, U_MIC1: SA5532A dual low-noise op-amp (filter, HP driver, mic preamp)

Datasheet: `datasheets/ne5532.pdf` (TI SLOS075I, NE5532/NE5532A/SA5532/SA5532A, rev. Apr 2009).
Read in full: features, schematic, abs max, recommended conditions, electrical and operating
characteristics, and the package addendum.
MPN: **SA5532ADR** (TI). `C83716 SA5532ADR (TI, SOIC-8): extended, JLC stock 2779, lifecycle normal, checked 2026-11-07`
Alternates: `C56153412 SA5532ADR-TUDI` (Tudi, 3970 in stock) and HGSEMI SA5532 (other packages).
Quantity: 3 per board, 15 for 5 boards, 18 with attrition. Stock 2779: OK.
Footprint: SOIC-8 D package (3.9 mm body, 1.27 mm pitch).

**Why SA5532A and not NE5532 (basic part C7426, 223k stock):** the datasheet's ordering table
rates NE5532 for 0–70 °C, and SA5532 for −40 to +85 °C. R-40 requires parts rated ≥ 85 °C
ambient, so the NE5532 basic part fails. The "A" grade has a specified maximum input noise.
Pinout and electricals are otherwise identical. The cost is an extended-part fee.

## Uses

| Ref | Half A | Half B |
|---|---|---|
| U_F1 | L differential MFB filter + line driver | R differential MFB filter + line driver |
| U_HP1 | L HP driver (class-AB stage inside the loop) | R HP driver |
| U_MIC1 | ext-mic preamp, +12 dB | loopback buffer (line-out L → PCM1808 VINR), optional |

## Absolute max vs our worst case

| Parameter | Abs max | Our worst case | Margin |
|---|---|---|---|
| VCC± | ±22 V | ±15 V nominal; ±15.75 V if the block C post-regulator tolerance is 5 % | OK, 6 V |
| Input voltage | ±VCC (note 3: never exceed the supply magnitude) | filter inputs ≤ 3.3 V; HP input ≤ ±13.5 V; mic input clamped by BAV99 to the rails behind 470 Ω | OK |
| Differential input | note 4: current flows above ~0.6 V unless limited | can occur in the mic preamp when overdriven by line level (output clips). Limited by 470 Ω + Rf/Rg | OK |
| Input current | ±10 mA | mic: ESD residue through 470 Ω is clamped by BAV99 | OK |
| Output short | unlimited (note 5: within dissipation) | line out to a short through 47 Ω gives IOS ≤ 60 mA max | see dissipation |
| Tj | 150 °C | below | OK |

**Dissipation at Tamb 55 °C, θJA 97 °C/W (D package):**
- Quiescent: 30 V × ICC.
  - ICC 8 mA typ: 0.24 W, Tj = 78 °C.
  - ICC 16 mA max: 0.48 W, Tj = 102 °C.
- **Line out shorted (both channels, U_F1).** The feedback is taken at the op-amp pin, before
  the build-out resistor R_BO, so the pin still follows the signal (≤ 5.65 Vpk at 0 dBFS). The
  current into the short is Vpk/R_BO.
- With R_BO = 100 Ω: Ipk = 56.5 mA. That is below IOS max (60 mA) but above IOS typ (38 mA), so a
  typical part current-limits and clips. Harmless.
  - Per-half dissipation for a sine:
    P = VCC·Ipk/π − Ipk²·R/4 = 15 × 0.0565/π − 0.0565² × 100/4 = 0.27 − 0.08 = **0.19 W**.
  - Both halves at full scale plus max quiescent: 0.38 + 0.48 = 0.86 W, so
    **Tj = 55 + 83 = 138 °C < 150 °C**. This is the abuse case: a sustained full-scale sine into a
    shorted cable. Music has ≥ 10 dB crest factor, and its average is far lower.
- **Chosen: R_BO = 100 Ω, 1206, 0.25 W.** In a short at full-scale sine it dissipates
  4.0²/100 = 0.16 W (64 % of rating). Output impedance is 100 Ω, which loses 1.3 dB into
  600 Ω (the R-14 minimum) and 0.09 dB into a typical 10 kΩ sub input. The loss is calibrated in
  DSP. A 47 Ω build-out was considered: it gives IOS-limited clipping at 120 mA demand and
  0.25 W per half. Rejected for the thermal margin.

## Electrical characteristics used (±15 V, 25 °C)

| Parameter | Typ | Max | Used for |
|---|---|---|---|
| VIO | 0.5 mV | 4 mV (5 full range) | offset (servo removes it in the filter; HP stage: ≤ 5 mV × 1.3) |
| IIB | 200 nA | 800 nA (1000 full range) | HP stage offset: 1 µA × 767 Ω = 0.8 mV |
| en | 5 nV/√Hz (1 kHz) | 8 at 30 Hz typ | noise budget |
| in | 0.7 pA/√Hz | | noise budget |
| GBW | 10 MHz | | filter f0 = 50 kHz at Q ≈ 1: GBW/(f0·Q·noise gain 4.5) ≈ 44. OK. HP loop gain at 20 kHz ≈ 51 dB |
| SR | 9 V/µs | | 4 Vrms at 20 kHz needs 0.71 V/µs; HF residue at the op-amp input is ≤ −60 dB at 500 kHz after the passive pole. OK |
| VOPP, RL ≥ 600 Ω | 26 V | 24 V min | line out 11.3 Vpp needed. OK |
| IOS | 38 mA | 60 mA | short-circuit analysis above |
| ICC (both amps) | 8 mA | 16 mA | rail budget |
| kSVR | 100 dB | 80 dB min | ±15 V ripple requirement: 1 mVpp → ≤ 0.1 µV input-referred |
| zo | 0.3 Ω at 10 kHz, AVD = 30 dB | | |

Unity-gain stable ("compensated internally for unity-gain operation"), so the MFB (noise gain
≥ 4.5 at DC, approaching 1 + C2/(…) at HF) and the HP stage (gain 1.3) are fine.

## Required external parts

- 100 nF X7R on each supply pin to GND (pins 8 and 4), plus 10 µF per package (X7R 25 V 1206,
  derated to ≈ 4 µF at 15 V; acceptable as local bulk), within 3 mm.
- Line driver: 100 Ω build-out (R_BO), 1206, 1 %, 0.25 W (0.16 W worst case, above). Feedback
  stays at the op-amp pin. Phase 2 picks the LCSC part.
- HP driver: input stopper 100 Ω; Rf = 1.0 kΩ and Rg = 3.3 kΩ (0.1 %, gain 1.303); Cf = 1 nF C0G
  across Rf (pole at 159 kHz, which gives the HP path a 4th pole).
- Mic preamp: Rf = 3.0 kΩ, Rg = 1.0 kΩ (gain 4.0 = +12 dB), Cf = 1 nF (53 kHz pole).

## Fine print / gotchas

- Note 4: the input-protection diodes conduct above ~0.6 V differential, so an overdriven
  follower draws input current. The mic preamp has 470 Ω in series. The HP driver's input sees
  the filter output (low Z) with the 100 Ω stopper, and in a clipped/limited condition the
  differential input can reach several volts: ≤ (13 − 7)/1.1 kΩ ≈ 5 mA. That is within ±10 mA.
  OK.
- The "PS" package and NE-grade parts are 0–70 °C. Order only SA5532A.
- The datasheet gives no THD figure. Phase 8 uses TI's macromodel.

## Layout guidance

- Supply decoupling right at the pins. A ground return for the MFB + side network (R3+, C1+, C2+)
  that is mirror-symmetric with the − side.
- Keep the HP feedback (Rf from OUT_INT) short and the bias string tight.
- Keep U_MIC1 well away from U_F1 and the relay coils.
