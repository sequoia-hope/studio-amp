# PoE++ GaN Speaker Amplifier — System Specification

Open, hackable whole-home audio. Each speaker contains its own amplifier board, powered and networked over a single Ethernet cable. Personal project first; designed so it could later be packaged and sold (e.g. Crowd Supply). Intended for automated design in Boardroom with UltraRoute, with many variants spun in parallel.

## Design principles

- Source parts from LCSC; prefer multi-sourced jellybean parts.
- Prefer discrete circuits over dedicated chips where practical (supply chain); integrated-chip versions are built as parallel variants for comparison.
- Shared functional blocks reused across boards; variants swap individual blocks.
- Electronically tunable: all crossover, EQ and room correction in software, controllable over the network.
- Target quality: studio-monitor class.

## Board family

1. **Satellite board** — mounts in each speaker; two bi-amped outputs (woofer + tweeter); powered by PoE++.
2. **Subwoofer board** — reuses the shared blocks; higher-power GaN stage; powered from an external DC supply (e.g. 48 V brick); PoE used for data and sync only.
3. **Torture tester** — separate board (or test variant) that abuses the device under test under software control.

## Power input: PoE++

- IEEE 802.3bt, Type 3/4, \~70 W available at the device.
- Four-pair PoE-rated magnetics with centre taps on all pairs; two input bridges (MOSFET ideal-diode bridges preferred for efficiency).
- **Variant A (integrated):** TI TPS2373-4 (LCSC C470963) or Kinetic KTA1142 (integrated PD + DC-DC controller). Check stock and pin compatibility before committing.
- **Variant B (discrete):** analog PD front end built from jellybean parts:
  - Detection: 25 kΩ signature, 1% resistor.
  - Classification: TL431-referenced current source (class 8).
  - Multi-event classification and mark-event logic using comparators, transistors and RC timing.
  - UVLO comparator and slew-limited inrush MOSFET.
  - Maintain power signature (MPS); after power-up the microcontroller can take this over, along with LLDP power negotiation.
  - Validation: agent-run SPICE Monte Carlo over component tolerance and temperature.
- Open item: SVG schematic of the discrete PD front end (to be drawn in text chat).

## Isolated DC-DC

- Baseline: isolated converter, \~70 W.
- Topology candidates: active-clamp forward (preferred for efficiency) and flyback (simpler).
- Try a planar transformer embedded in the PCB as a variant.
- Outputs: main amp rail \~36–48 V; ±12–15 V auxiliary winding for the headphone and analog stages; logic buck to 3.3 V, plus FPGA core rail (\~1.2 V).
- Bulk capacitance on the amp rail, after the inrush limiter, to cover audio peaks.
- Experimental variant: non-isolated buck, only for enclosures with no user-accessible conductors (check 802.3 isolation requirements).

## Compute

- **RP2350:** network stack, DSP (crossover, EQ, room correction), control, UI, protection supervision.
- **Small FPGA** (e.g. Gowin GW1N, open toolchain Yosys/Apicula; Lattice iCE40 as an alternative): PWM generation with fine edge placement, noise shaping and 1-bit modulator, RMII Ethernet MAC, hardware PTP timestamping, fast cycle-by-cycle overcurrent shutdown, remappable display pins.
- Firmware and HDL written by agents.

## Networking and sync

- 10/100 Ethernet over RMII. PHY candidates: Microchip LAN8720A; Realtek RTL8201F with JLSemi JL1101 as a possible pin-compatible second source (verify).
- Time sync: PTP (IEEE 1588), hardware timestamps in the FPGA. Target: under 10–20 µs between speakers in the same room; under 1 ms between rooms.
- Audio clock disciplined to PTP (PLL trim or fractional resampler).
- Keep the 50 MHz reference clock short and the PHY area away from the class D switch nodes.
- Verify sync by toggling a GPIO on the PTP second on two boards and measuring the offset on a scope.

## Amplifier power stage

- Full GaN. Two full bridges (BTL) per satellite: woofer channel and tweeter channel. Total: 8 GaN FETs and 4 half-bridge drivers.
- GaN FETs: Innoscience 100 V parts (e.g. INN100 series), cross-referenced against EPC.
- Gate driver: uPI uP1966 (chosen).
- Switching frequency: \~400 kHz to 1 MHz+, to be tuned per variant.
- LC output filter on each channel; size it together with the noise-shaper order.
- Control variant: a silicon MOSFET version, to measure whether GaN actually improves results.
- Expected peak output: over 100 W into 8 Ω from a 36–48 V rail; average power stays within the PoE++ budget.

## Modulation

- **Baseline: fully digital.** The FPGA generates PWM with fine edge placement, three-level BD modulation, and noise shaping that pushes quantization noise above 20 kHz.
- Bus-voltage feedforward at minimum (fast ADC on the rail). Investigate closing a feedback loop after the output filter.
- **Variant: self-oscillating analog loop** (UcD / Eigentakt style), with feedback after the LC filter. Driven by a 1-bit stream from the FPGA, reclocked through a flip-flop on a quiet reference rail, then an analog filter.
- Measure and compare the digital and analog variants.

## Protection

- GaN gate: regulated gate supply from the driver; tight gate loops.
- GaN drain: tight power loop, snubbers, TVS clamp on the bus, handling for bus pumping.
- Overcurrent: fast comparator per bridge, with FPGA cycle-by-cycle shutdown in nanoseconds.
- Speaker driver protection: DC detection and output disconnect/shutdown; protective high-pass filter on the tweeter channel.
- Pop-free startup and shutdown: mute and soft-start sequencing, including on sudden PoE loss.

## Audio I/O and DSP

- On-board MEMS microphone, plus a jack for an external measurement mic, for self-calibration and room correction.
- Line out to feed a powered subwoofer.
- Headphone output for high-impedance headphones (300–600 Ω): discrete class AB stage on the ±12–15 V rails. Shares the analog DAC path with the line out.
- DSP on the RP2350: crossover, driver EQ, room correction; new filters pushed over the network (e.g. from a web page).

## User interface and expansion

- Knob header: RP2350 ADC inputs with a clean reference and RC filtering; spare GPIO for rotary encoders. Optional population.
- I2C (Qwiic-style) connector for LED driver boards; I2C buffer for longer runs. Agent should reference Sequoia's repo of LED panel designs.
- Addressable LED output: 5 V level-shifted, one connector, firmware-selectable between single-wire (WS2812) and data + clock (APA102/SK9822).
- Colour OLED header: 7-pin, 0.1-inch female header (GND, VCC, SCK, MOSI, RES, DC, CS) for SSD1331/SSD1351-type SPI modules. Signal pins routed to the FPGA so they can be remapped; solder jumpers on GND/VCC.
- Budget LED power from the PoE total; keep LED and display lines away from the class D section.

## Firmware, debug and thermals

- Safe network firmware updates for both the RP2350 and the FPGA bitstream (A/B images, rollback).
- Debug: standard Raspberry Pi Debug Probe header format (agent should use samples from Sequoia's library), FPGA JTAG, and test points on rails and switch nodes.
- Thermal plan for the GaN and inductors inside a sealed enclosure; board shape that mounts to the speaker's back panel.

## Subwoofer board

- Reuses the RP2350, FPGA, PHY/PTP and gate-driver blocks unchanged.
- Higher-power GaN stage with larger FETs and inductors; several hundred watts.
- External DC input (e.g. 48 V brick); PoE used for data and sync only.
- Optional line input.

## Torture tester

- Network-controlled, so agents can run thousands of abuse cycles unattended and produce a report.
- Switchable PoE source: cut or brown out power at chosen points in the audio.
- Output short: a MOSFET across each speaker output, fired at random or chosen times.
- Load emulator: resistive dummy loads plus a switchable reactive network emulating a woofer at resonance.
- Fast capture of bus voltage, output current and switch nodes, logged with waveforms.
- Stimulus: test tones and worst-case bass over the network; post-test health check of the device under test.

## Compliance

- Design for FCC and CE emissions from the start (class D switching, Ethernet cable, LED cables).
- PoE isolation per 802.3; the isolated supply makes user-touchable knobs and jacks legitimate.

## Open items

- [ ] Sequoia: pick the specific colour OLED module so the header pinout matches it.
- [ ] Draw an SVG schematic of the discrete PoE PD front end.
- [ ] Run SPICE Monte Carlo on the discrete PD front end.
- [ ] Check LCSC stock for the KTA1142 and alternative PD chips.
- [ ] Choose the isolated DC-DC topology and the output voltage within 36–48 V.
- [ ] Verify pin compatibility for the JL1101 / RTL8201F second source.
