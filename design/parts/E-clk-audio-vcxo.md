# Y (audio master clock) — 24.576 MHz VCXO, PTP-disciplined by the FPGA


Datasheet: `datasheets/sx3v-vcxo.pdf` (SCTF "3V Series" VCXO, 3.2 × 2.5 mm, dated 2024-11-28; image-only PDF, read as rendered pages 1–6: specifications, dimensions/pinout, part decoding, stability curve, reflow). LCSC parameter list fetched 2026-11-07.
MPN: SX3V24.576B20100F30TNN
Supplier: `C5179997 SX3V24.576B20100F30TNN (SCTF, SMD3225-4P): extended, JLC stock 155, lifecycle normal, checked 2026-11-07`
Second source (same maker, 6-pad 3225): `C21547585 SX3V24.576B20100F30TNNS`, 184 in stock (pin-out differs; footprint not interchangeable — note only).
Footprint: 3.2 × 2.5 mm 4-pad; pads 1.2 × 0.95 mm on a 2.2 × 1.75 mm grid (datasheet "Solder pad layout"). Pin 1 Vcon, 2 GND, 3 Output, 4 Vdd.

MPN decode (datasheet p.2): 3V = 3.2 × 2.5 mm · 24.576 MHz · B = 3.3 V · 20 = ±20 ppm tolerance · 100 = ±100 ppm pullability code · F = −40…+85 °C · 30 = frequency-drift code (the p.1 table lists ±25 ppm conditional and ±50 ppm over −40…+85 °C; review NOTE-5 — the design relies only on APR) · T = CMOS · N standard current · N standard phase noise. LCSC lists APR = ±50 ppm (the datasheet's guaranteed APR minimum).

## Recommendation: VCXO trimmed by the FPGA (not a fixed XO + resampler)

| | VCXO, FPGA ΔΣ trim | Fixed XO + fractional resampler |
|---|---|---|
| PWM edge timing | PWM, 1-bit DAC, mic clocks all on one clock that *is* PTP-locked | PWM runs on a free XO; audio is resampled into it |
| Signal path | bit-exact, no interpolation error | ASRC adds image/aliasing residue and filter delay; must be ≥ 120 dB clean to be invisible next to R-52 |
| Resources | a 1-pin ΔΣ + 2-pole RC; servo in firmware | polyphase ASRC for 4 output + 2 input channels: in the FPGA it competes with the noise shaper for the 28 multipliers and EBR; in the RP2350 it takes CPU from DSP/network |
| Multi-speaker measurement (room correction, R-15/R-16 mics) | every speaker's ADC/PDM sampling is locked to PTP time → coherent captures | captures need resampling too |
| BOM | one VCXO (C5179997), 2 R, 2 C | one XO, no RC |
| Risk | pull range ±50 ppm (APR) bounds what master it can follow | none on range |

Phase noise / jitter reasoning for R-53: the PWM edges are produced by the ECP5 PLL (24.576 MHz × 12) and ODDRX2F. In-loop the PLL tracks its reference, so reference phase noise inside the PLL bandwidth reaches the edges either way (VCXO or XO, similar class of 3225 oscillator). The VCXO's control input adds FM only through its tune voltage, and that is filtered to < 2 Hz (below). Above the PLL bandwidth, the PLL's own VCO noise dominates in both options. So **jitter does not separate the two options; resampler cost and artefacts do**, and the VCXO wins.

## Absolute max / operating vs our worst case

| Parameter | Datasheet | Ours | OK |
|---|---|---|---|
| Vdd | 2.97–3.63 V | `+3V3` (filtered, below) | OK |
| Temperature | −40…+85 °C (F code) | ≤ 55 °C cabinet + board rise | OK (R-40) |
| Load | 15 pF CMOS | two branches: ECP5 ball P6, LLC_GPLL0T_IN (≤ 8 pF) + block F's MCLK_Q buffer input (~3 pF; it fans out to the 8 reclock FFs and the PCM1808 SCKI) + traces ≈ 14 pF | OK, with each branch ≤ 15 mm and its own 33 Ω |
| Vc range | 0.3–3.0 V, centre 1.65 V, Rin ≥ 5 MΩ, modulation BW ≥ 15 kHz | ΔΣ + RC from ECP5 ball N4, bank 6 (0–3.3 V) | clamp the code range in firmware to 0.3–3.0 V |
| Current | ≤ 10 mA (2–36 MHz) | 10 mA on `+3V3` | |
| Duty | 45–55 % | PLL input spec: ≥ 25 % (3–49 MHz) | OK |
| Rise/fall | ≤ 5 ns (10–90 %, into 15 pF) | ECP5 PLL input tR/tF ≤ **1 ns** (DS-02012 Tab 3.23) | **known deviation** (review MINOR-4): no stocked 24.576 MHz VCXO in hand guarantees ≤ 1 ns. Mitigation: FPGA branch shortest and lightest, **no series resistor on the FPGA branch** (block F's branch keeps its own buffer); measure edge rate and PLL jitter at bring-up. A slow edge raises the conversion of supply noise to jitter at the PLL input; it isn't a lock failure |
| Start-up | ≤ 2 ms | FPGA PLL lock ≤ 1 ms after | OK |

## Calculations

**Pull range and what master it can follow.** APR ±50 ppm absolute (includes tolerance, drift, ageing). A PTP master that is itself one of our speakers runs PTP time from its 50 MHz RMII XO (±10 ppm + ±20 ppm, `E-clk-rmii-50mhz.md`) → the slaves' VCXOs must reach true ±30 ppm: inside ±50 ppm. An external grandmaster whose clock is off by more than ±50 ppm (802.3 allows ±100 ppm) cannot be followed by the VCXO alone; firmware then falls back to a slow sample slip/fine resampler in the RP2350, flagged as a warning. Ordinary switches and PCs sit within ±50 ppm; noted as a residual risk.

**Tuning gain.** Kv ≥ 100 ppm / 2.7 V = **37 ppm/V** (APR over 0.3–3.0 V); up to ≈ 74 ppm/V if the "100" code's ±100 ppm is reached. Resolution needed: 0.01 ppm steady-state steps → 0.01/74 = 135 µV → 3.3 V / 135 µV = 24,400 levels ≈ **15 bits**. A 1-bit ΔΣ from the FPGA (2nd order, clocked at 24.576 MHz / 4 = 6.144 MHz) followed by the RC filter gives > 16 bits at < 2 Hz.

**Tune filter.** Two RC sections, 100 kΩ / 1 µF each (fc = 1/(2π·0.1 s) = 1.59 Hz per pole). PTP servo bandwidth ≈ 0.05–0.1 Hz, so the filter adds < 4° phase at 0.1 Hz — negligible in the loop. Source impedance 200 kΩ into Rin ≥ 5 MΩ → ≤ 4 % gain error, which the servo absorbs.
- ΔΣ shaped noise near 1 MHz: attenuation (1 MHz/1.59 Hz)² ≈ 4 × 10¹¹ → irrelevant.
- **Supply noise on the FPGA pin** (the ΔΣ output swings between GND and VCCIO6 = `+3V3`, so 3V3 ripple multiplies into Vc by the duty): 10 mV p-p of 3V3 ripple at 100 Hz × 0.5 duty → 5 mV, × (1.59/100)² = 1.3 µV at Vc → Δf/f = 74 ppm/V × 1.3 µV = 9.4 × 10⁻¹¹; phase modulation peak = Δf / fm in cycles: 9.4e-11 × 24.576 MHz / 100 Hz / (2π·24.576 MHz) → time deviation = Kv·ΔV / (2π fm) = 9.4e-11 / 628 = **0.15 fs**. Negligible. At 1 Hz (inside the filter) the same ripple would give larger wander, but a 1 Hz component on 3V3 is a regulator-loop matter and is tracked out by the PTP servo.
- Parts: 2 × 100 kΩ 0402 (`C25741 0402WGF1003TCE (UNI-ROYAL, 0402): basic, JLC stock 8785570, lifecycle normal`), 2 × 1 µF X5R 25 V 0402 (`C52923 CL05A105KA5NQNC (Samsung Electro-Mechanics, 0402): basic, JLC stock 11554041, lifecycle normal`). The 1 µF's DC-bias loss (at ≤ 3 V on a 25 V part, ≤ 12 % of rating) only moves the pole; not critical. X5R leakage ≪ 100 kΩ path.

**PLL setting from this clock (ECP5, `E-fpga-ecp5.md`).** Baseline ×12: CLKOP 294.912 MHz (VCO 589.824 MHz, DS-02012 Tab 3.23 VCO 400–800 MHz, fPFD 24.576 MHz ≥ 10 MHz) → ODDRX2F at 589.824 Mb/s. Bring-up option ×14: 344.064 MHz → 688.128 Mb/s.

## Edge resolution (R-53)

- **Physical grid: 1/589.824 Mb/s = 1.695 ns** (×12 baseline, 84 % of the −7 commercial GDDRX2/ECLK limits); 1.453 ns on the ×14 bring-up option (98 %). Both miss R-53's ≤ 1 ns physical target. DELAYF adds ~25 ps static/dynamic per-pin deskew only.
- Audio-locked fsw on ×12: **576 kHz** (N = 1024 steps, 12 × 48 kHz) or 768 kHz (N = 768). 448 kHz isn't an integer division on ×12 (`E-fpga-ecp5.md`). The *effective* in-band resolution comes from the noise shaper (block D / RTL analysis, with these inputs).

**Jitter → output noise (feeds R-51's ≤ 150 µV A-weighted).** An edge displaced by Δt adds an error pulse of area Vs·Δt. For independent edge errors at rate r, the in-band noise is
  vₙ² = 2 · BW · r · Vs² · σₜ².
With Vs = 48 V, BW = 20 kHz, r = 4 edges × 480 kHz = 1.92 × 10⁶ s⁻¹ (worked at 480 kHz; at 576 kHz multiply vₙ by √1.2 = 1.10) (BTL, two legs, two edges each per period): vₙ = 48 · σₜ · √(2 · 2×10⁴ · 1.92×10⁶) = 48 · σₜ · 2.77 × 10⁵.
| σₜ (independent, rms) | vₙ (20 kHz, unweighted) |
|---|---|
| 100 ps (pessimistic; ECP5 PLL period jitter ≤ 100 ps p-p, DS Tab 3.23) | 1.33 mV |
| 20 ps | 266 µV |
| 10 ps | 133 µV |
| 5 ps | 67 µV |
**But in BD modulation the PLL jitter is largely common to both legs.** Both ODDRX2F outputs share one edge clock (ECLK skew within a bank ≤ 180 ps, static); at idle, legs A and B switch on the *same* FCLK edge, so a common timing error cancels in the differential output. With signal, the error is the jitter *difference* across the pulse-width separation (tens of ns to a few µs); PLL phase noise below 1/(separation) cancels. What reaches the speaker at idle is the **uncorrelated** part: output-buffer and clock-tree skew jitter per pin, plus each LMG1210's propagation jitter (block D). The ≤ 150 µV target needs that uncorrelated part ≲ 10 ps rms. Large-signal jitter noise rises with modulation but is then masked by the signal (it scales like PLL phase noise over the pulse-width interval).
**Status:** DS-02012 gives period and cycle-to-cycle jitter (≤ 100/200 ps p-p) but no rms TIE and no per-pin jitter. Not provable from datasheets → bring-up measurement (two ODDRX2F pins on one ECLK, differential edge jitter). If it fails: (a) the spare PCLKT7_0 ball K1 (`CLK_AUX`) can bring in an external low-jitter clock; (b) the closed-loop variant corrects it. Open item for the noise-shaper analysis.

## Required external parts

- 100 nF at Vdd (pin 4) + 4.7 µF local; Vdd through a ferrite bead from `+3V3` (BLM18PG221SN1D, as the FPGA core bead) so PWM-stage noise on 3V3 does not modulate the oscillator.
- Output: a 33 Ω series resistor on block F's branch only, at the VCXO; **the FPGA branch has none** (MINOR-4: edge rate) (`C25105 0402WGF330JTCE (UNI-ROYAL, 0402): basic, JLC stock 3866748, lifecycle normal`).
- Vc: the 2-pole RC above, driven from FPGA `VCXO_TUNE` (ball N4, bank 6, 3.3 V).

## Block F's MCLK_Q requirement (F-interfaces.md, received 2026-11-07)

Block F needs MCLK_Q for the DAC reclock flip-flops taken straight from this VCXO, with only a dedicated low-jitter buffer on a quiet rail in between: **integrated phase jitter ≤ 1 ps rms over 20 kHz–12 MHz offset** (≈ −150 dBc/Hz floor) for the 4-tap FIR DAC, or ≤ 0.3 ps (≈ −155 dBc/Hz) for a single-FF DAC.

**Verdict: can't be verified.** The SX3V datasheet gives "N = standard phase noise" and no phase-noise curve, floor or jitter figure (pages 1–6 read). So this part is **unproven against block F's requirement**: it neither passes nor fails on paper. I searched LCSC on 2026-11-07 for a stocked VCXO with a specified figure and found none at 24.576 MHz: SiTime SiT3808 has no 24.576 MHz part in stock; Crystek CVHD-950 has 0 stock; Abracon ABLNO only comes at 96/100 MHz with 2–3 pieces.

Proposed handling, for the lead to decide with block F:
1. Fit the SX3V VCXO (PTP lock is kept). Measure MCLK_Q phase noise at bring-up, or measure the DAC's in-band noise floor directly, which is what matters.
2. Give the same site a **footprint option for a fixed XO**: YXC OT2EL4C4JI-111OLP-24.576M, `C5203547 OT2EL4C4JI-111OLP-24.576M (YXC Crystal Oscillators, SMD3225-4P): extended, JLC stock 6498, lifecycle normal, checked 2026-11-07`, ±10 ppm. It is the same YSO110TR series as the 50 MHz RMII clock: **0.7 ps rms phase jitter, 12 kHz–20 MHz** (datasheet `yxc-ot2el-50m.pdf` p.1). That band contains block F's 20 kHz–12 MHz band, so the XO is ≤ 0.7 ps there and meets the 4-tap figure, but not the 0.3 ps single-FF figure. The XO's pin 1 is OE (enable ≥ 70 % VDD or floating), where the VCXO's is Vcon. A 0 Ω option from pin 1 to VDD (DNP with the VCXO fitted) and a 0 Ω in series with the tune RC (DNP with the XO fitted) let either part populate one shared 3225 land; build the land from both drawings. In XO mode the audio clock is no longer PTP-locked, and the RP2350 must do the sample-rate tracking in software (the resampler option). That costs CPU and fidelity, so it is a fallback only.
3. Either way the PLL path is irrelevant to MCLK_Q: block F's FFs never see the FPGA clock.

**DAC data timing (block F item 2).** The FPGA launches DAC data on MCLK↓ and the FFs capture on MCLK↑, so the budget is half a period, 20.3 ns. ECP5 tCO ≤ 6.1 ns from the clock pin (DS-02012 Tab 3.22, −7 commercial, LVCMOS25/0 pF) → ≈ 8 ns allowing for −7I and LVCMOS33 into 10 pF, within block F's 12 ns. Data arrive ≤ 8.2 ns after MCLK↓ including the trace; setup slack at the FF ≈ 20.3 + t_buffer − 8.2 − t_su(FF) ≥ 8 ns (t_su from block F's 74LVC74 audit). Gateware holds the DAC lines low until `PG_3V3Q` (B5) is high.

## Fine print

- Phase noise is "standard" with no numbers in the datasheet → block F's ≤ 1 ps requirement is unverified (section above).
- Linearity ≤ 10 %: the servo is a PI loop and doesn't care.
- 15 pF CMOS load: three branches are at the limit; keep the stubs < 15 mm and the series R at the source. If block F's ADC takes MCLK from the FPGA instead, two branches remain (FPGA PLL pin, reclock FF).

## Layout

- VCXO within 10 mm of ECP5 ball P6 (lower-left), on the FPGA side, over unbroken GND; the RC filter beside the Vc pin, away from switching nodes; nothing switching under the 1 µF caps.
- The reclock FF branch (block F) runs on the quiet side; keep it away from the PWM lines.

## Open questions

- PLL + ODDRX2F uncorrelated jitter and the slow (≤ 5 ns) PLL input edge: measure (above).
- The master-clock policy (speaker as grandmaster, BMCA priority) is firmware's job; it keeps the VCXO inside its APR.
