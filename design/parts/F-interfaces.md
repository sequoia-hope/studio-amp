# Block F interfaces

## What block F needs from other blocks

### From block C (rails)

| Net | Spec | Load (typ / design / peak) | Notes |
|---|---|---|---|
| `+15V` | ±5 %; ripple ≤ 1 mVpp; noise ≤ 50 µVrms (20 Hz–20 kHz) | 62 / 120 / 200 mA | peak = both HP outputs into a short plus full signal |
| `−15V` | as above | 50 / 110 / 190 mA | |
| `+3V3_Q` | 3.3 V ±3 %; **≤ 5 µVrms 20 Hz–20 kHz**; **Zout ≤ 0.1 Ω, 20 Hz–50 kHz**; PSRR ≥ 60 dB at 1 kHz; feeds only the DAC flip-flops (and the MCLK_Q buffer, if block E uses one) | 20 / 30 mA (single-tap build: 7 mA) | supply noise appears as AM on the output; Zout sets the data-dependent THD (`F-dac-74lvc74.md`) |
| `+5V_A` (**new**) | 5.0 V ±5 %; ≤ 20 µVrms; from `+15V` by a low-noise LDO, or from `+5V` through a filter plus LDO | 12 / 15 mA | PCM1808 VCC and the electret plug-in power |
| `+3V3` | logic | 8 / 10 mA | PCM1808 VDD, T3902 |
| `+5V` | logic | 56 / 62 mA | two relay coils |

### From block E (compute and clock)

- **MCLK_Q**: 24.576 MHz, 3.3 V CMOS, straight from the audio oscillator to the 74LVC74 CP pins,
  with nothing in between except an optional dedicated low-jitter buffer on a quiet rail.
  **Integrated phase jitter ≤ 1 ps rms (20 kHz–12 MHz offset), phase-noise floor ≤ −150 dBc/Hz**
  for the 4-tap DAC (≤ 0.3 ps / −155 dBc/Hz if the single-tap option is fitted).
- **MCLK** (another branch of the same oscillator) to PCM1808 SCKI, synchronous with the FPGA's
  I2S clocks.
- Noise shaper: 6.144 Mb/s (128 × 48 kHz), ≥ 5th order, single bit, dithered; in-band
  quantisation noise ≤ −135 dB re m = 1; modulation index capped at **m ≤ 0.487** (= 4.0 Vrms
  line out); taps 1–3 delayed by 1, 2, 3 bits; data launched on the falling MCLK edge; FPGA clock
  insertion plus tco ≤ 12 ns.
- FPGA pins (16): DAC_L0..3, DAC_R0..3 (out); ADC_BCK, ADC_LRCK (out); ADC_DOUT (in); PDM_CLK
  (out, 3.072 MHz); PDM_DAT (in); HP_EN, LO_EN (out); HP_FAULT_N (in). HP_DET can go to an
  RP2350 GPIO.
- Firmware/gateware sequencing (R-34): relays open until the DAC has streamed the idle pattern
  for ≥ 3 s; on PoE loss, open the relays before stopping the streams; high-pass the HP/line
  feeds at ≤ 10 Hz; mono sum or L/R for line out in DSP (R-14).

### To blocks D/G and phase 4

- Phase 4: Neutrik NMJ6HCD2 (rear-mount, 11.4 mm panel hole), 2 × RCA, 3.5 mm jack on the
  back-panel edge; HFD4 relays and the TVS parts next to the jacks; the MEMS mic acoustic port
  through the back panel; ≥ 2 cm² collector copper per BCP56/BCP53; the analog region kept away
  from the GaN stage's return currents (architecture decision 5).

## Proposed changes to architecture

1. **4-tap FIR DAC instead of a single flip-flop per channel.** Each channel gets 4 FFs (2 ×
   74LVC74 per channel), each summed through 2.2 kΩ into the filter.
   - Effect: the jitter-induced noise falls 4× (12 dB), and the 6 MHz energy reaching the op-amp
     falls too.
   - Cost: 6 extra FPGA pins (8 instead of 2), 3 extra 74LVC74 and 12 extra resistors per
     board.
   - The board keeps a single-tap population option.
   - **Decision for the lead/user, because it trades FPGA pins against the oscillator spec.**
     Single-tap needs ≤ 0.3 ps jitter (≈ −155 dBc/Hz floor).
2. **±15 V load is 120 mA continuous / 200 mA peak per rail**, not the "≤ 80 mA" in R-33a. That
   raises the ±15 V power line from 2.8 W to ≈ 3.6 W design. Typical use is ≈ 62/50 mA.
3. **New rail `+5V_A`** (5 V, 15 mA, quiet) for the PCM1808 analog supply and mic bias. Block C
   owns it.
4. **Two relay coils on `+5V`** (56 mA). They add to block C's +5V budget.
5. **Architecture block diagram, F block:**
   - "1-bit stream ×2" becomes "1-bit stream, 4 taps × 2 channels (8 lines) + MCLK_Q direct from
     the XO".
   - Add "PCM1808 I2S ADC (slave), SCKI = MCLK".
   - Add "HFD4 mute relays ×2 with a hardware DC detector".
6. **E → F interface line:** add MCLK_Q (oscillator direct), MCLK to the ADC SCKI, relay
   enables, HP_FAULT_N and HP_DET.

## Decisions needing the user

- **R-40 waiver for the 6.35 mm jack:** every stocked 6.35 mm jack is rated +70 °C max
  (Neutrik NMJ6HCD2 −25/+70 °C), against "≥ 85 °C" in R-40. The cabinet's worst case is 55 °C.
  Proposal: accept the Neutrik.
- **Shared DAC path (R-14):** HP and line out carry the same two streams. Mono-sum for a sub
  applies to the headphones too, and so does volume. Options:
  - (a) accept it (headphones and sub aren't used at the same time). **Recommended for variant A.**
  - (b) add 2 more DAC channels for line out (+2–8 FPGA pins, +1 SA5532, +2–4 74LVC74).
- **Single-tap vs 4-tap DAC** (above).
- **MEMS mic port:** the bottom-port T3902 must vent through the back panel with a sealed path.
  If phase 4 can't provide that, the on-board mic only hears the inside of the cabinet.

## Cross-checks against the other blocks' audits (read 2026-11-07, not edited)

- `C-3v3q-ldo.md`: TPS7A2033P. Its noise is 7 µVrms over 10 Hz–100 kHz; the 20 Hz–20 kHz figure
  will be lower, so it is likely inside the ≤ 5 µVrms requirement. Block C should confirm from
  the noise-density curve. Budget: 20 mA, part allowed up to 50 mA. Block F's design value of
  30 mA fits.
- `C-pm15-ldos.md`: TPS7A4901 (150 mA ROC) and TPS7A3001 (200 mA ROC), sized there for 80 mA.
  Block F's 120 mA continuous fits both. The 200 mA HP-short peak on +15 V exceeds the TPS7A49's
  150 mA ROC, but it is a fault case and the regulator current-limits. Block C should confirm the
  upstream ±15 V source and the LDO dissipation at 120 mA.
- `E-clk-audio-vcxo.md`: SX3V 24.576 MHz VCXO, "standard phase noise". **Its phase-noise floor
  and jitter must be checked against the MCLK_Q requirement above** (block E was messaged). If
  it doesn't meet it, the options are a low-jitter XO for the DAC with the FPGA resampling, or a
  better VCXO.

## Block C proposal (audit-CG message, 2026-11-07) and block F's reply

Block C's plan:
- ±15 V from an LM5017 Fly-Buck off VBUS, post-regulated by TPS7A4901/TPS7A3001 with 10 nF NR
  (15–20 µVrms, 72 dB PSRR at 120 Hz). The rails come up whenever VBUS > ~36 V and are **off on
  USB-only** power.
- +3V3_Q from a TPS7A2033 on +5V, always up with logic, 20 mA budget.

Block F's reply:
- Loads as in the table above: ±15 V at 120 mA continuous and 200/190 mA peak (fault);
  +3V3_Q at 30 mA design. The noise and PSRR meet the ±15 V requirement.
- **New requirement: gate the +3V3_Q LDO's EN from ±15 V power-good.** On USB-only power a live
  3V3_Q drives the flip-flop outputs (Q or Q̄ is always high). That pushes ≈ 1.5 mA per input,
  (3.3 − 0.6 V)/(550 + 560 + 750 Ω), into the inputs of an unpowered SA5532. This violates its
  abs max note 3 (the input must never exceed the supply), although it is inside its ±10 mA
  input-current rating.
  - Fallback if EN gating is refused: a BAV99 clamp from each filter input node to the ±15 V
    rails will not help, because the rails are at 0 V. Instead the FPGA must hold the DAC
    flip-flops so that both outputs are low. That is not possible with a 74LVC74, since
    nSD = nRD = L gives Q = Q̄ = H. So EN gating is the clean fix.
- Mute and pop: the relays are off on USB-only power and stay open until the DAC has streamed the
  idle pattern for ≥ 3 s. That covers "rails up while the DAC is idle".

## Block E reply (audit-E message, 2026-11-07) and block F's response

- **MCLK_Q:** block E gives F a dedicated VCXO branch (33 Ω at the source). Block F fans it out
  with a SN74LVC2G34 on +3V3_Q (`F-clk-buffer.md`): one output for the 8 FF clocks, one for
  PCM1808 SCKI. +3V3_Q design load becomes ≈ 34 mA.
- **Phase noise:** the SX3V datasheet gives no figure, so the requirement can't be verified on
  paper. Block E's proposal:
  - fit the VCXO, with a shared 3225 land for the YXC OT2EL4C4JI-111OLP-24.576M XO
    (C5203547; 0.7 ps rms over 12 kHz–20 MHz);
  - measure the DAC noise floor at bring-up.

  Block F agrees. The XO meets the 4-tap 1 ps requirement, but not the single-tap 0.3 ps one,
  **so the 4-tap DAC is the baseline**. Bring-up test: idle A-weighted noise at line out
  ≤ 6 µV with the VCXO. At the 2.0 µV/ps sensitivity, a VCXO at ≥ 2 ps would show up as
  ≥ 7 µV.
- **DAC timing:** clock insertion plus tco is ≤ 6.4 ns, within 12 ns. OK.
- **Pins:**
  - DAC_L0–3 on FPGA 17–20 and DAC_R0–3 on 48–51.
  - BCK on 62.
  - MADC_LRCK from pin 3 through an SN74AVC4T774 (a few ns of delay; the PCM1808 needs LRCK
    setup ≥ 50 ns to BCK, so that is OK).
  - MADC_DOUT on 15 and PDM_DAT on 14. Both are 3.3 V into the 1.8 V bank through 1 kΩ, no pull.
    - T3902 DATA then sources ≈ (3.3 − 1.8 − 0.6)/1 kΩ ≈ 0.9 mA into the clamp when high. That
      is above the 0.5 mA VOH test load, but VOH still exceeds the 1.8 V bank's VIH.
    - With ≈ 5 pF, the RC is ≈ 5 ns, against a 163 ns half-period. OK.
  - PDM_CLK on 77.
- **HP_EN, LO_EN, HP_FAULT_N, HP_DET on a TCA9535 I2C expander (P12–P15).**
  - The 100 kΩ gate pull-downs on both 2N7002 gates are already in `F-mute-relay.md`, so the
    relays stay off while the expander pins are Hi-Z. The expander drives each gate through
    10 kΩ, so the DC detector can override it.
  - The hardware DC detector opens the relays directly, so HP_FAULT_N latency doesn't matter.
  - **R-34 concern:** muting on PoE loss now depends on firmware: the RP2350 detects the loss,
    writes over I2C, and the relay releases in ≤ 6 ms. Hold-up is ≥ 20 ms. That works if
    firmware acts within ≈ 10 ms, but a hung firmware would leave the relays closed as the rails
    collapse (a thump). **Proposed:** wire the hardware PoE-loss signal, active low and open
    drain (the R-32a fast comparator / PD power-good on the secondary, from block A/B/C), into
    block F's /DC_TRIP node through a diode. The relays then drop in hardware within µs of PoE
    loss, with no firmware or FPGA pin needed. **The lead needs to name that net and its owner.**

## Block C update (audit-CG message, 2026-11-07): accepted

- ±15 V is resized to 120/110 mA continuous. At block F's 200/190 mA short case, the Fly-Buck
  peak switch current is 0.65 A against the LM5017's 0.7 A minimum limit, which leaves little
  margin. The TPS7A4901 may current-limit in that fault, which block F accepts.
- +5V_A: a third TPS7A4901 from +15 V, 5.04 V, 15.4 µVrms (requirement ≤ 20). Accepted.
- **+3V3_Q is now a TPS7A9401** (0.46 µVrms, 110 dB PSRR at 1 kHz), with 2 × 22 µF (ESR
  ≤ 20 mΩ), giving ≈ 0.11 Ω at 50 kHz from the caps alone.
  - Phase 8 must confirm Zout ≤ 0.1 Ω from 20 Hz to 50 kHz.
  - Block F layout: run SNS as a Kelvin trace to the VCC pins of the 74LVC74 row (at the middle
    package). The 4 × 100 nF plus 10 µF at the FFs sit after the sense point.
  - Load: 34 mA including the clock buffer (`F-clk-buffer.md`), against block C's 30 mA budget.
    **Block C: please budget 35 mA.**
- **3V3_Q is gated by +15 V** (on above 7.1 V, off below 6.1 V), so it is off on USB-only power.
  Partial power-down:
  - The SN74LVC2G34 buffer specifies Ioff (≤ ±10 µA with VI or VO up to 5.5 V at VCC = 0), so the
    VCXO can keep running into it.
  - The Nexperia 74LVC74A datasheet has 5 V-tolerant inputs but does **not** specify Ioff.
  - **Rule for gateware (block E): drive DAC_L0..3 and DAC_R0..3 low whenever ±15 V/3V3_Q is not
    up.** Use PG_3V3Q via the TCA9535 or firmware, and start the streams only after PG.
  - The Gowin weak pull-ups during configuration are ≤ ~0.1 mA. That is harmless, since the
    5 V-tolerant LVC inputs have no clamp to VCC.
  - TI's SN74LVC74APWR (the listed second source) may be preferred if its datasheet specifies
    Ioff. Check it in phase 2.
- The PCM1808 on USB-only power: VDD (+3V3) is up, VCC (+5V_A) is down, and SCKI is 0 (the buffer
  is off). The ADC sits in clock-halt reset. Digital pins are referenced to the powered VDD. OK.
- Relay coils: 56 mA added to +5V. Done.
- Follow-up (audit-CG, 2026-11-07): 3V3_Q is budgeted at 35 mA. PG_3V3Q comes from the
  TPS7A94's PG pin with a 100 kΩ pull-up, asserts at 2.93 V (89 %), and goes to block E (TCA9535
  or an FPGA pin; block E chooses). The LDO's current limit is ≈ 0.62 A, so block F's DAC rule
  stands as written: DAC lines low until PG.

## FPGA change to ECP5 LFE5U-25F (audit-E message, 2026-11-07): new pin map

| Signal | Ball | Series R (block E) | Block F side |
|---|---|---|---|
| DAC_L0..L3 | N16, P15, P16, R16 | — | 33 Ω at the FPGA (`F-dac-74lvc74.md`); tCO ≤ 6.1 ns, within the 12 ns limit |
| DAC_R0..R3 | R13, T14, R12, T13 | — | as above |
| MADC_BCK / MADC_LRCK | P13 / R14 | — | PCM1808 pins 8/7, slave mode |
| MADC_DOUT | L16 | 330 Ω | PCM1808 pin 9. Drop block F's own 33 Ω at DOUT, since block E's 330 Ω replaces it (RC ≈ 330 Ω × 10 pF = 3.3 ns ≪ 163 ns) |
| PDM_CLK / PDM_DAT | L14 / N13 | — / 330 Ω | T3902 pins 4 / 1. No pull resistor on DATA, still true |
| HP_EN / LO_EN | M14 / N14 | 1 kΩ | then block F's 10 kΩ to each 2N7002 gate, with 100 kΩ pull-downs kept as the backstop. The DC detector can still override |
| HP_FAULT_N | P11 | 1 kΩ | /DC_TRIP, with a 10 kΩ pull-up to +3V3 |
| HP_DET | K13 | 1 kΩ | Neutrik TN normal, 100 kΩ pull-up |

- The I2C expander is dropped. ECP5 pins are all 3.3 V, with no translators.
- **Hot-socket rule (block E):** these always-powered nets (MADC_DOUT, PDM_DAT, HP_FAULT_N,
  HP_DET) land on balls whose differential partners stay unconnected. Block F adds nothing else
  to them.
- **R-34 mute on PoE loss:** with the relay enables back on FPGA pins, gateware can drop
  HP_EN/LO_EN within µs of the FPGA's PD power-good or PoE-loss input. That resolves the
  firmware-latency concern. **Requirement to block E:** gateware drops both enables within ≤ 1 ms
  of PoE loss, independent of the RP2350.
- The hardware diode-OR of the PoE-loss signal into /DC_TRIP is now optional (a backstop against
  an unconfigured or hung FPGA, though the pull-downs already make an unconfigured FPGA safe).
- **Still open with block E:** where PG_3V3Q is read (the expander is gone). Gateware must hold
  the DAC lines low until PG_3V3Q.
- Follow-up (audit-E, 2026-11-07): **PG_3V3Q goes to FPGA ball B5.** Gateware holds the DAC lines
  low until PG_3V3Q is high; before configuration the ECP5 pull-downs keep them low. POE_LOSS_N
  and PD_PG are FPGA inputs, and the gateware drops HP_EN/LO_EN within µs of PoE loss. The
  hardware diode-OR into /DC_TRIP stays an optional backstop (decided in phase 2, when the
  POE_LOSS_N net owner is known). Block F's interface items with block E are closed.
