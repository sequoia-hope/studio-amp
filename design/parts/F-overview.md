# Block F: analog audio, design overview and budgets

Phase 1, block F (sheets `audio_out`, `audio_in`). Requirements covered: R-13, R-14, R-15, R-16, R-34,
R-40, R-42, R-52. Part audits are in `design/parts/F-*.md`, and each one gives its datasheet and its
`jlc_parts.py show` line. Interface changes are in `F-interfaces.md`.

## Signal chain (per channel, L and R identical)

```
FPGA (MCLK domain)                      +3V3_Q                                    ±15 V
 DAC_x0..x3 ──► 4 × 74LVC74 FF (tap k) ──Q──► 2.2k ×4 ─┐P+  ┌───────────────┐
 (bit stream    clocked by MCLK_Q      ──Q̄─► 2.2k ×4 ─┘P−  │ differential   │ FILT_x  ┌─► 100 Ω ─► relay K2 ─► RCA (line out, R-14)
  + 3 delays)   24.576 MHz, from XO                         │ MFB, SA5532    ├─────────┤
                                                            │ 3rd order 48 k │         └─► HP driver: SA5532 + BCP56/BCP53
                                                            └──────▲─────────┘              class AB, I-limit ─► 4.7 Ω ─► relay K1 ─► 6.35 mm
                                                                   │ DC servo OPA2277 (0.3 Hz)
```

- **DAC: 4-tap FIR 1-bit DAC** (semi-digital FIR). The FPGA's noise shaper produces one bit
  stream per channel at 128 × 48 kHz = 6.144 Mb/s. The FPGA also outputs the same stream delayed by
  1, 2 and 3 bit periods, so there are 4 tap lines per channel. Each tap is reclocked by one
  74LVC74 flip-flop on `+3V3_Q`, clocked directly by the 24.576 MHz audio master clock (MCLK) from
  the oscillator. Both outputs, Q and Q̄, are used. Each tap drives 2.2 kΩ into the filter's input
  node on each side, which sums the four taps into a 4-tap boxcar FIR. Population option: fit only
  tap 0, with 560 Ω on each side in place of the four 2.2 kΩ, to get a plain single-FF DAC (2 FPGA
  pins instead of 8; the jitter requirement tightens as shown below).
- **Why differential Q/Q̄:** Vdiff = VDD·(2d−1). Supply noise at idle is common-mode and is
  rejected by the 0.1 % resistor match. Rise/fall-time asymmetry gives an equal and opposite error
  on the up and down transitions, which acts as a pure delay, so the first-order ISI is cancelled
  (see `F-dac-74lvc74.md`).
- **Reconstruction filter:** a passive RC pole on each side (R0 = 4 × 2.2 kΩ ∥ = 550 Ω, C0 = 15 nF
  C0G), followed by a differential multiple-feedback biquad on one SA5532 half. Together they form
  a 3rd-order Butterworth, −3 dB at 47.4 kHz, with a gain of 3.51 V/V per differential volt
  (`F-filter-passives.md`). The filter output drives the line out directly, through a 100 Ω
  build-out resistor.
- **DC servo:** an OPA2277 integrator senses FILT_x and injects into the + network, giving a
  0.3 Hz high-pass. The output offset is then ≤ 1.1 mV (`F-servo-opa2277.md`).
- **Headphone stage:** one SA5532 half, gain 1.30, with a BCP56-16/BCP53-16 complementary emitter
  follower inside the loop. The bias spreader is one BAV99, the emitter resistors are 15 Ω, and a
  BC847/BC857 limiter trips at about 41 mA. A 4.7 Ω resistor sits outside the loop
  (`F-hp-output-stage.md`).
- **Mute:** two HFD4/5 DPDT signal relays (HP L/R and line L/R) on their normally-open contacts,
  so the output is disconnected whenever the coil is unpowered. They are driven from the FPGA
  through 2N7002 FETs. A hardware DC detector on all four outputs opens both relays
  (`F-mute-relay.md`).
- **Inputs:** a 3.5 mm ext-mic jack, then the electret plug-in power bias, an SA5532 preamp
  (+12 dB) and a PCM1808 I2S ADC. Its R channel is an optional loopback of line-out L
  (`F-mic-adc-pcm1808.md`). The on-board MEMS mic is a T3902 bottom-port PDM part
  (`F-mems-t3902.md`).

## Gain staging (digital full scale = modulation index m = 0.487)

| Point | At 0 dBFS (m = 0.487) | At −6 dBFS | Notes |
|---|---|---|---|
| FF differential (Q−Q̄), peak | 3.3 × 0.487 = 1.61 V | 0.80 V | 1-bit levels ±3.3 V diff |
| Filter / line out | 1.61 × 3.51 = 5.65 Vpk = **4.0 Vrms** | **2.0 Vrms** (R-14 nominal) | R-14 limit is ≤ 4 Vrms. The FPGA caps m at 0.487 |
| Headphone out | 4.0 × 1.30 = **5.2 Vrms** = 7.35 Vpk | 2.6 Vrms | R-13 asks for ≥ 5 Vrms. Into 300 Ω that is 24.5 mA pk, inside the 25 mA limit |

A 5th-order single-bit modulator is normally stable up to m ≈ 0.5–0.6, so m = 0.487 keeps it
inside its stable range (block E verifies this in simulation).

## Noise budget versus R-52 (≤ 10 µV A-weighted)

Calculation: nodal noise analysis of the actual filter values. Each resistor's thermal noise is
included, along with the SA5532's en = 5 nV/√Hz and in = 0.7 pA/√Hz (datasheet typicals at 1 kHz).
The analysis is integrated over 20 Hz–20 kHz, with and without A-weighting. Script:
`scratchpad/fcalc/noise2.py`; the output is below.

| Source | Line out, µV A-wt | Notes |
|---|---|---|
| Filter resistors + SA5532 en/in | 5.14 | en × noise gain 4.5 dominates (4.35 µV unweighted); R2 750 Ω is next |
| Clock jitter, 4-tap, σ = 1 ps (block E requirement) | 1.6 | see jitter section; 2.0 µV unweighted |
| Modulator quantisation noise, OSR 128, ≥ 5th order | ≤ 0.5 | requirement on block E: ≤ −135 dB re m = 1 in band |
| +3V3_Q noise (idle, common-mode, 0.1 % match) | < 0.1 | 5 µV × CMRR ≈ 46 dB |
| Servo injection (OPA2277 en, low-passed) | < 0.2 | |
| **Line out total** | **≈ 5.4 µV A-wt** | target 10 µV, margin 5.4 dB |
| HP: 1.30 × line + HP stage (en 5 nV, Rf∥Rg 767 Ω → 0.95 µV) | **≈ 7.1 µV A-wt** | margin 3 dB |

Calculation output (filter only):
```
TOTAL 7.22 uV rms 20Hz-20kHz, 5.14 uV A-weighted
diff gain 1000 Hz: 7.027 (two-sided drive; = 3.51 per differential volt)
```

## THD+N estimate versus R-52 (≤ 0.01 % at 1 Vrms)

At 1 Vrms (−12 dBFS):
- Noise ≈ 9 µV unweighted on line out (filter 7.2, jitter 2, other 1), or ≈ 0.0009 %.
- SA5532 distortion in the filter and line driver: typically well below 0.001 % at 4 Vrms into
  ≥ 600 Ω. TI's datasheet gives no THD figure; phase 8 checks this with the macromodel.
- First-order rise/fall ISI is cancelled by the differential Q/Q̄ topology; the residual comes
  from Q vs Q̄ mismatch. The 4-tap FIR cuts the transition count each output sees by about 4×.
- Supply modulation from the data-dependent current: ΔI_DD ≈ 0.37 mA at 2f at full scale. With
  Zout(3V3_Q) ≤ 0.1 Ω this gives ≈ −120 dB.
- HP crossover distortion inside the loop: the loop gain at 20 kHz is ≈ 10 MHz / 20 kHz / 1.3 ≈
  51 dB. Iq ≈ 5 mA, and the stage stays class A up to 10 mA.

**Estimate: THD+N ≈ 0.001–0.003 % line, 0.002–0.005 % headphone into 300 Ω, against the 0.01 %
target.** These are estimates only. R-52 says phase 8 proves the figure by simulation.

## Clock-jitter requirement (to block E)

The model: each output transition carries a timing error δ. That produces an error impulse of
area ΔV·δ, where ΔV is the step in the summed DAC output. For white (edge-to-edge uncorrelated)
jitter σ, the in-band error power at the DAC is F·E[Δy²]·σ²·f_B, with F = 6.144 MHz and
f_B = 20 kHz.
- **Single tap**: ΔV = 6.6 V diff and transition probability ≈ 0.5, so E[Δy²] = 21.8 V². The
  output noise is G·sqrt(F·E·f_B)·σ = 3.51 × sqrt(6.144e6 × 21.8 × 2e4) × σ = **7.9 µV per ps**
  (20 kHz, unweighted).
- **4-tap boxcar**: Δy = (s_k − s_{k−4})·3.3/4, so E[Δy²] is 1/16 of the single-tap value. The
  noise is **2.0 µV per ps**.

Requirement to block E (the 4-tap build is the baseline):
- MCLK 24.576 MHz, 3.3 V CMOS, **integrated phase jitter ≤ 1 ps rms over 20 kHz–12 MHz offset**.
  That is roughly a phase-noise floor ≤ −150 dBc/Hz. If only the single-tap option is fitted, this
  tightens to ≤ 0.3 ps and a floor of ≤ −155 dBc/Hz.
- Close-in phase noise (< 20 kHz offset) only puts sidebands on the signal itself. It is lenient:
  ≤ −100 dBc/Hz at 1 kHz is ample.
- **The flip-flop clock must come straight from the oscillator.** No FPGA PLL, fabric or I/O
  buffer may be in the path; their jitter is tens of ps or more. Use a point-to-point trace with a
  source series resistor. If the oscillator also has to feed the FPGA, PCM1808 SCKI and others,
  give the FF clock its own branch: a dedicated low-jitter buffer output, powered from `+3V3_Q` or
  its own quiet rail. A VCXO is acceptable only if its datasheet meets the floor above.
- The FPGA launches DAC data on the **falling** MCLK edge, and the FF captures on the next rising
  edge. That gives 20.3 ns for the FPGA tco plus the trace, against the FF's tsu = 2.0 ns and
  th = 1.0 ns (74LVC74A Table 8).

## Modulator rate recommendation

**128 × 48 kHz = 6.144 Mb/s per channel** (MCLK/4), with a 5th-order single-bit noise shaper
using optimized NTF zeros, plus dither.
- 64× (3.072 Mb/s) would reduce the jitter noise by 3 dB. But a 5th-order single-bit modulator at
  OSR 64 has a peak SQNR of only about 100–105 dB, which at 4 Vrms full scale means tens of µV in
  band: it fails R-52.
- 128× gives about 30 dB more SQNR, and the analog filter needs only 3rd order.
- The PWM clock domain (R-53) is not used for this path.

## Rail loads (to block C)

| Rail | Typical | Worst continuous | Peak / fault | Main contributors |
|---|---|---|---|---|
| +15 V | 62 mA | 120 mA | 200 mA (both HP shorted) | 3 × SA5532 (8 typ / 16 max mA each), OPA2277 1.6 mA, HP bias strings 2 × 6.2 mA, HP Iq 2 × 5 mA (10 max), +5V_A LDO input 12 mA (if derived from +15 V), signal: HP 2 × 7.8 mA average, line 2 × 3 mA average |
| −15 V | 50 mA | 110 mA | 190 mA | the same, without the +5V_A LDO |
| +3V3_Q | 20 mA | 30 mA | — | 4 × 74LVC74. CPD 19.1 pF × 3.3 V × 24.576 MHz × 8 FF = 12.4 mA, plus tap loads 8 × 0.9 mA. Single-tap build: ≈ 7 mA |
| +5V_A (new) | 12 mA | 15 mA | — | PCM1808 VCC 8.6 / 11 mA + electret bias 0.5 mA |
| +3V3 | 8 mA | 10 mA | — | PCM1808 VDD 5.9 / 8 mA, T3902 0.43 mA |
| +5V | 56 mA | 62 mA | — | two HFD4/5 coils at 28 mA (178 Ω ±10 %) |

Noise and impedance requirements: +3V3_Q ≤ 5 µVrms (20 Hz–20 kHz), Zout ≤ 0.1 Ω from 20 Hz to
50 kHz, PSRR ≥ 60 dB at 1 kHz. Basis: an output-referred AM noise of 3.51 × m × δVDD ≤ 2 µV at
1 Vrms. ±15 V: ripple ≤ 1 mVpp and noise ≤ 50 µVrms (SA5532 kSVR ≥ 80 dB). +5V_A: ≤ 20 µVrms.

## FPGA pins (to block E)

| Signal | Dir | Pins | Notes |
|---|---|---|---|
| DAC_L0..L3, DAC_R0..R3 | out | 8 | 6.144 Mb/s, launched on the MCLK falling edge; taps 1–3 are 1, 2, 3 bit delays of tap 0. Single-tap option: 2 pins |
| ADC_BCK, ADC_LRCK | out | 2 | PCM1808 slave mode, 64 BCK/frame (3.072 MHz), synchronous with MCLK |
| ADC_DOUT | in | 1 | |
| PDM_CLK | out | 1 | 3.072 MHz (MCLK/8), T3902 standard mode |
| PDM_DAT | in | 1 | no pull resistor (T3902 datasheet) |
| HP_EN, LO_EN | out | 2 | relay enable, active high, external 100 kΩ pulldown |
| HP_FAULT_N | in | 1 | DC detector, open collector; optional, can go to the RP2350 instead |
| HP_DET | in | (1) | Neutrik normal contact; RP2350 GPIO preferred |
| **Total** | | **16** (9 with the single-tap DAC; HP_DET extra) | |

Also from block E: MCLK_Q (to the FF clocks) and MCLK to the PCM1808 SCKI. Neither is an FPGA pin.

## What phase 8 must simulate (R-52)

1. Bit-true noise shaper plus 4-tap FIR into a behavioural FF model: finite, unequal tr/tf, Q/Q̄
   skew, Ron(H/L), Zout(3V3_Q) with the data-dependent supply current, and white jitter σ = 0.5,
   1 and 2 ps. Then the SPICE filter with SA5532 and OPA2277 macromodels. Report THD+N at 1 Vrms
   and at full scale, A-weighted noise at idle, and idle tones.
2. HP stage into 300 Ω, 600 Ω, 32 Ω and a short, plus a 1 nF cable: THD vs level, stability
   (phase margin), limiter behaviour, the BCP56/53 junction temperature in a short.
3. Iq spread over BAV99 Vf and BCP56/53 Vbe tolerance and temperature.
4. Out-of-band residue at line out: the actual MFB stopband with the op-amp Zout, out to 30 MHz.
5. Power-up and power-down transients at the outputs with the relay sequence (R-34).
6. Mic preamp: line-level overload into the PCM1808 input clamp currents.

## Requirement deviations needing a decision

- **R-40 (parts rated ≥ 85 °C):** every LCSC-stocked 6.35 mm jack checked is rated to +70 °C
  only. Neutrik NMJ6HCD2: −25 to +70 °C. HOOYA PJ-612: −20 to +70 °C. Worst-case air inside the
  cabinet is 55 °C, and the jack sits at the back-panel edge. Proposal: accept NMJ6HCD2 with a
  logged waiver. The other parts in this block are rated ≥ 85 °C (the Omron G6K relay was rejected
  for its 70 °C rating, and HFD4 was chosen at 85 °C).
