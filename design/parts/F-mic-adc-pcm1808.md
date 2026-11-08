# U_ADC1: PCM1808 stereo ADC, with the ext-mic bias and preamp (R-15)

Datasheet: `datasheets/pcm1808.pdf` (TI SLES177A, Apr 2006, rev. Aug 2006). Read in full:
features, abs max, recommended conditions, electrical characteristics, pins, system clock,
fade, power-on, clock-halt reset, interface modes and timing, synchronisation, application
circuit, layout.
MPN: PCM1808PWR. `C55513 PCM1808PWR (TI, TSSOP-14): extended, JLC stock 51303, lifecycle normal, checked 2026-11-07`
Footprint: TSSOP-14 PW (4.4 mm body, 0.65 mm pitch).
Single-sourced (TI). Stock is ample.

## ADC choice: I2S chip, not an FPGA delta-sigma ADC

Room correction needs about 90–100 dB of dynamic range at the mic. The PCM1808 gives 99 dB DR
and SNR typ (95 min), A-weighted, and −93 dB THD+N typ at −0.5 dBFS.

An FPGA ΔΣ ADC (LVDS comparator plus RC integrator) typically reaches 70–85 dB. It is limited by
the comparator's hysteresis/metastability, the I/O supply noise riding on its feedback level, and
FPGA ground bounce. It would need the same quiet-supply reclock trick as the DAC, plus
calibration, and its result would be uncertain.

The PCM1808 costs one TSSOP and 3 FPGA pins, and it is a known 99 dB part with stock of 51k.
Alternatives checked: CS5343, WM8782 (0 stock), ES7243E (12k, QFN-20), PCM1802 (≈ 100 stock).
**Recommendation: PCM1808.**

## Absolute max vs worst case

| Parameter | Abs max | Worst case | Margin |
|---|---|---|---|
| VCC (analog) | −0.3 to 6.5 V | +5V_A 5.0 V ± 5 % | OK |
| VDD (digital) | −0.3 to 4 V | +3V3 3.3 V ± 3 % | OK |
| AGND–DGND | ±0.1 V | tied under the package | OK |
| LRCK, BCK, DOUT | −0.3 to VDD + 0.3 V | FPGA 3.3 V LVCMOS | OK |
| SCKI, MD0, MD1, FMT | −0.3 to 6.5 V | 3.3 V | OK |
| VINL, VINR | −0.3 to VCC + 0.3 V | clamped by BAT54S at the junction of 2.2 kΩ + 1.0 kΩ; ≤ VCC + 0.37 V worst case in misuse only, pin current ≪ 1 mA (below) | accepted |
| Input current (any pin) | ±10 mA | ≤ 4.9 mA in the external Schottky; µA into the pin | OK |
| TA | −40 to +85 °C | 55 °C | OK |

## Configuration

- **Slave mode:** MD1 = MD0 = Low (Table 2). Tie both to DGND (they also have internal 50 kΩ
  pulldowns). The system clock is auto-detected at 256/384/512 fS. We use **SCKI = 24.576 MHz =
  512 fS**, from MCLK (block E). It is synchronous with the FPGA's LRCK/BCK, which the datasheet
  requires (any phase is allowed; drift must stay below ±5 BCK).
- **FMT = Low:** I2S, 24-bit.
- **BCK = 64 fS = 3.072 MHz;** LRCK = 48 kHz from the FPGA. Timing in slave mode: LRCK setup
  ≥ 50 ns and hold ≥ 10 ns to the BCK rising edge; DOUT is valid −10 to 40 ns after the BCK
  falling edge. Over a 325 ns BCK period, the FPGA samples DOUT on the BCK rising edge with
  ≥ 120 ns slack. OK.
- **Power-on and clock change:** the output is valid 1024 SCKI + 8960/fS (≈ 187 ms) after
  reset release, plus the fade-in. If MCLK is ever stopped or changed (PTP retune of a VCXO is
  fine; a frequency jump is not), halt SCKI for ≥ 4 µs to force a clock-halt reset.
- **HPF:** fixed at 0.019 fS/1000 = 0.91 Hz, which removes DC. Irrelevant for mic work; it means
  the loopback can't measure DAC DC (the servo handles that).

## Required external parts (Figure 26 and layout section)

- VCC (pin 3): 0.1 µF ceramic plus 10 µF, to AGND.
- VDD (pin 4): 0.1 µF plus 10 µF, to DGND.
- VREF (pin 1): 0.1 µF plus 10 µF to AGND, close to the pin.
- VINL, VINR: AC coupling. The datasheet example is 1 µF electrolytic, giving 2.7 Hz with 60 kΩ.
  **Ours (revised after review M2): 1 µF 63 V PET film, WIMA MKS2C041001F00JSSD**, through-hole,
  5 mm pitch. Corner 2.65 Hz, the datasheet's value. Film is non-piezoelectric and
  non-polarised, so it is safe for the reverse swings in the misuse case.
  `C92673 MKS2C041001F00JSSD (WIMA, Through Hole,P=5mm): extended, JLC stock 5985, lifecycle normal, checked 2026-11-07`
  Datasheet `datasheets/wima-mks2.pdf`: PET, 1.0 µF 63 VDC, 5 × 10 × 7.2 mm, −55 to +125 °C.
  (LCSC links the MKS 02 sheet for this part; the MKS 2 sheet was fetched from wima.de.)
- External anti-alias RC, split for the clamp (review m3): preamp → film → **R_A 2.2 kΩ** →
  junction (BAT54S clamp) → **R_B 1.0 kΩ** → VINL, with **1 nF C0G** at the pin
  (CC0603JRNPO9BN102, C106246).
  - The pin sees the datasheet's "1 kΩ and 1000 pF" (159 kHz). The 2.2 kΩ upstream adds a flat
    −0.45 dB in total against the 60 kΩ input (calibrated).
  - Fault current: ≤ 5.7 mA, all of it in the external Schottky (see line-level survival).
- AGND and DGND joined directly under the package. DOUT: block E's 330 Ω series resistor (ECP5 pin map) replaces block F's 33 Ω
  (crosstalk note: "minimize load capacitance").

## Ext-mic chain (R-15) and calculations

```
J_MIC tip ─ PESD15 ─┬─ R_BIAS 2.2k ─ N_B (47 µF Al-elec to AGND) ─ R_F 2.2k ─ +5V_A    (ring: R_RING 2.2k to N_B)
                    └─ C_IN 1 µF PET film ─ R_S 470 Ω ─ BAV99 clamp to ±15 V ─ U_MIC1A IN+ (470 kΩ to AGND)
U_MIC1A: gain 1 + 3.0k/1.0k = 4.0 (+12 dB), Cf 1 nF
U_MIC1A out ─ 1 µF PET film ─ R_A 2.2 kΩ ─┬─ R_B 1.0 kΩ ─ VINL (1 nF C0G to AGND)
                                          BAT54S to 5V_A/AGND
Loopback (optional, DNP default): line-out L (FILT_L) ─ 10k/2.7k divider ─ U_MIC1B buffer ─ 1 µF film ─ 2.2k ─┬─ 1.0k ─ VINR (same clamp)
```

**Dielectric per position (review M2; the board is bolted to a loudspeaker panel, R-41):**

| Position | Signal | Part | Why |
|---|---|---|---|
| C_IN (mic input coupling) | mic-level, 3–5 V DC across | 1 µF PET film (MKS2) | no piezo effect. With 470 kΩ bias: 0.34 Hz |
| ADC coupling (VINL, VINR) | line-level to the ADC | 1 µF PET film (MKS2) | same; also non-polarised for the misuse swing |
| Anti-alias at the pin | 1 nF | C0G | |
| Preamp Cf | 1 nF | C0G | |
| N_B bias reservoir | AC ground for the capsule bias | 47 µF 16 V aluminium electrolytic, KNSCHA RST (see below) | not piezoelectric; DC is always 3–5 V positive. X5R/X7R rejected |
| PCM1808 VCC/VDD/VREF bulk and bypass | supply and reference only | X7R/X5R allowed | not in the signal path. VREF is a reference node, so use an aluminium 10 µF for VREF bulk to be safe, with 100 nF C0G/X7R |

`C4747957 RST47UF16V034 (KNSCHA, SMD,D5xL5.4mm): extended, JLC stock 111038, lifecycle normal, checked 2026-11-07`
Datasheet `datasheets/knscha-rst47uf16v.pdf`: 47 µF ±20 %, 16 V, 105 °C 2000 h, 5 × 5.4 mm.
Life at 55 °C (10 °C rule): 2000 h × 2^5 = 64,000 h, about 7 years of continuous operation.
Wear-out lowers C and raises the bias corner, which is a soft failure. Accepted.

**Preamp input bias (review n7):** 470 kΩ to AGND, RT0603 thin film. SA5532 IIB ≤ 1 µA (full
range) gives ≤ 0.47 V at IN+, and ×4 makes ≤ 1.9 V DC at the preamp output. That leaves
13.5 − 1.9 = 11.6 V of headroom against the 1.5 Vpk the ADC needs, and the output film cap
blocks it.
- Noise: the 470 kΩ is shunted by the ≤ 2.2 kΩ source through C_IN above 0.34 Hz, so it is
  negligible in band.

**Plug-in power (R-15: bias ~2.5 V via resistor):**
- Open circuit: 5.0 V at the tip through 4.4 kΩ.
- With a typical electret drawing 0.3–0.5 mA: V_tip = 5.0 − I × 4.4 kΩ = 3.7–2.8 V, since
  R_F's DC drop is in series.
- AC load on the capsule FET: R_BIAS 2.2 kΩ (N_B is AC ground through 47 µF), the usual
  2.2 kΩ load.
- Supply filtering: R_F 2.2 kΩ with 47 µF gives 1.5 Hz, so 5V_A noise is attenuated 23 dB at
  20 Hz and 63 dB at 1 kHz.
- 47 µF: aluminium electrolytic RST (above). The X5R option (EMK316BBJ476ML) was rejected as
  piezoelectric (review M2).

**Gain staging:** PCM1808 full scale is 3 Vpp = 1.06 Vrms (0.6 VCC).
- Gain 4.0, so the input clips at 265 mVrms (−11.5 dBV).
- Capsule −28 dBV/Pa (e.g. Primo EM272 class): clips at 94 + 28 − 11.5 = **110.5 dB SPL**.
- Capsule −40 dBV/Pa: clips at 122 dB SPL.
- Noise floor: ADC 99 dB below FS gives −98.5 dBV at VINL, or −110.5 dBV input-referred. The
  capsule self-noise at 14 dBA SPL with −28 dBV/Pa is −108 dBV, which is 2.5 dB above the ADC
  floor, so the system floor rises only ~2 dB over the capsule.
- **Total DR ≈ 95 dB**, meeting the 90–100 dB target.
- The gain is set by Rf/Rg (0603, 1 %) and can be changed per build.

**Preamp noise:** en 5 nV/√Hz; Rf∥Rg = 750 Ω gives 3.5 nV; R_S 470 Ω plus R_BIAS 2.2 kΩ
(through the capsule's own output impedance, ≤ 2.2 kΩ) gives ≤ 6.6 nV; in × 2.7 kΩ = 1.9 nV.
Total ≈ 9 nV/√Hz, or 1.0 µV A-weighted input-referred. The capsule is ≈ 4 µV, so this costs
0.3 dB. OK.

**Survives line level plugged in by mistake (R-15):**
- A source of 2 Vrms nominal, up to 4 Vrms (5.7 Vpk), with ≈ 100 Ω source impedance:
  - C_IN 1 µF 63 V PET film sees the bias DC (≤ 5 V) plus ≤ 5.7 Vpk. OK.
  - The preamp input swings ±5.7 V, inside the ±13 V common-mode range of SA5532 (±12 min).
    **No current flows in the BAV99 clamps.** The preamp output clips at ±13.5 V.
  - The ADC input, after the 1 µF film: the cap holds VREF − ~1.9 V. A ±13.5 V clipped swing
    drives the R_A/R_B junction beyond the rails, and the BAT54S clamps the junction to
    −VF / 5V_A + VF.
    - The film holds 2.5 − 1.9 = 0.6 V, so the drive at R_A spans −12.9 to +14.1 V.
    - Current through R_A (2.2 kΩ):
      - up: (14.1 − 5.3)/2.2 kΩ = **4.0 mA** into 5V_A, which the ADC's own 8.6 mA load
        absorbs, so the LDO never has to sink;
      - down: (12.9 − 0.3)/2.2 kΩ = **5.7 mA** into AGND.
    - BAT54S VF at 5 mA: ≈ 0.3 V typ, ≤ 0.37 V max (between 320 mV at 1 mA and 400 mV at
      10 mA).
    - The pin connects to the junction through R_B 1 kΩ, so it reaches at most VCC + 0.37 V.
      **The abs max (VCC + 0.3 V) is exceeded by ≤ 70 mV, in this misuse case only.**
    - The pin's internal silicon diode passes ≪ 10 µA at 0.37 V, and R_B would limit it to
      ≤ 0.4 mA even at 0.4 V, far inside the ±10 mA input-current rating.
    - **Disputed with the review (m3):** the suggested split cannot by itself get below
      VCC + 0.3 V, because VF(BAT54S) ≥ 0.3 V at mA currents. The split is adopted for the
      datasheet-range source impedance, and the residual is logged as accepted.
  - The source sees ≥ 470 Ω + C_IN + 470 kΩ, plus 2.2 kΩ to the bias node: a load of ≈ 2 kΩ,
    and 5 V DC through 4.4 kΩ. Line outputs are AC-coupled or short-proof. Harmless.
- ESD: TVS at the jack, then 470 Ω, then the BAV99 rail clamps (`F-esd.md`).

**BAT54S** (Nexperia BAT54S,215): `C47546 BAT54S,215 (Nexperia, SOT-23): extended, JLC stock 301527, lifecycle normal, checked 2026-11-07`
Datasheet: `datasheets/bat54s.pdf`. VR 30 V, IF 200 mA, IFSM 600 mA (10 ms), Cd ≤ 10 pF at 1 V,
IR ≤ 2 µA at 25 V. Pinout: 1 = A1, 2 = K2, 3 = K1/A2 (series pair). Connections: pin 1 to AGND,
pin 2 to 5V_A, pin 3 to the R_A/R_B junction.
- Leakage: the two diodes are each reverse-biased by ≈ 2.5 V and their leakage currents
  largely cancel. At 85 °C the net may reach several µA. Through R_A/R_B that is ≤ 10 mV,
  which the HPF removes. Its Cd (≤ 10 pF) adds to the 1 nF anti-alias cap and is negligible.

## Power (to block C)

- VCC (+5V_A): 8.6 mA typ / 11 max, plus 0.5–1.1 mA mic bias, so ≤ 12.1 mA.
- VDD (+3V3): 5.9 typ / 8 max mA.
- Power dissipation: 62 mW typ, 81 mW max, at θJA 170 °C/W, so +14 °C. OK.
- **+5V_A must be quiet:** the mic bias feeds the capsule directly, filtered by only 23 dB at
  20 Hz, so it needs ≤ 20 µVrms (20 Hz–20 kHz). The PCM1808 VCC PSRR isn't specified, so keep it
  clean. This is a new rail (`F-interfaces.md`).

## Fine print / gotchas

- Synchronisation: if LRCK drifts ±6 BCK relative to SCKI, the ADC halts and outputs zeros. Use
  one clock domain (MCLK) for SCKI and the FPGA's I2S logic.
- MD0/MD1 must be set before power-on, which strapping gives.
- Output data is 2's complement, MSB first, 24-bit.
- The digital HPF can't be disabled.

## Layout guidance

- Put the PCM1808 next to the mic preamp, away from the class-D stage and the FPGA. VREF and VCC
  caps at the pins; AGND/DGND tie under the IC.
- Route DOUT, BCK and LRCK back to the FPGA with series resistors, not over the analog inputs.
- Keep the mic input trace from the jack short, and guard it with GND.
