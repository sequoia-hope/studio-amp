# MK1: TDK InvenSense T3902, bottom-port PDM MEMS microphone (R-16)

Datasheet: `datasheets/t3902.pdf` (DS-000357 rev. 1.0, 15 Apr 2020). Read in full:
specifications (Tables 1–6), timing, abs max, soldering, pins, theory of operation, PDM format,
sensitivity, applications (modes, connection, sleep, start-up), land pattern, handling and
outline.
MPN: MMICT3902-00-012. `C3171752 MMICT390200012 (TDK InvenSense, LGA-5(3.5x2.7)): extended, JLC stock 6675, lifecycle normal, checked 2026-11-07`
Footprint: 5-terminal LGA cavity package, 3.50 × 2.65 × 0.98 mm. Land pattern per Fig. 14 (1:1
pads 0.522 × 0.725 mm ×4, Ø1.625/Ø1.025 ring) and stencil per Fig. 15. **PCB sound hole
0.5–1.0 mm diameter** (the package port is Ø0.375 mm). Keep paste off the hole.

Alternatives looked at: MMICT5837 (C6909259, LCSC lists no datasheet and its lifecycle is
unknown, so it fails); Knowles SPH0641LU4H-1 (181 in stock, OK as a fallback, different
footprint); MSM261D3526 (0 stock).

## Performance (operating mode chosen: Standard, PDM_CLK = 3.072 MHz = MCLK/8)

| Parameter | Standard mode (Table 3) | High-performance (4.1–4.8 MHz) |
|---|---|---|
| Sensitivity | −26 dBFS ±1 dB (94 dB SPL, 1 kHz) | −32 dBFS ±1 |
| SNR (20 kHz, A-weighted) | 64.5 dBA | 64 dBA |
| EIN | 29.5 dBA SPL | 30 dBA SPL |
| AOP (10 % THD) / full scale | 120 dB SPL | 126 dB SPL |
| DR | 90.5 dB | 96 dB |
| THD at 105 dB SPL | 0.2 % typ, 1 % max | same |
| LF −3 dB | 36 Hz | 36 Hz |
| Supply current (1.8 V) | 430 µA typ, 500 max | 650 / 750 µA |
| Clock range | 1.0–3.3 MHz, 40–60 % duty | 4.1–4.8 MHz, 48–52 % duty |

3.072 MHz is inside the Standard range and comes from MCLK by an integer divide (÷8, 50 %
duty).

High-performance mode needs 4.1–4.8 MHz at 48–52 % duty, and no integer divide of 24.576 MHz
lands in that window: ÷6 gives 4.096 MHz, which is 4 kHz below the minimum, and ÷5 gives
4.915 MHz, above the maximum with an odd-divide duty. It would need a separate PLL output, with
PLL jitter that is harmless for a PDM mic. **Baseline: Standard mode, 120 dB SPL AOP.** If
block E has a spare PLL output at 4.608 MHz (= 96 × 48 kHz), High-performance mode is a firmware
option.

The on-board mic is good for room presence, voice and as a rough reference. Its EIN of 29.5 dBA
and 36 Hz LF corner make the ext-mic path the one used for measurement-grade room correction.

## Absolute max vs worst case

| Parameter | Abs max | Ours | OK |
|---|---|---|---|
| VDD | −0.3 to 3.63 V | +3V3 (3.3 V ± 3 % = 3.40 V max) | OK, 0.23 V |
| Digital pins | −0.3 to VDD + 0.3 V or 3.63 V | FPGA 3.3 V I/O on the same +3V3 | OK |
| Temperature (biased) | −40 to +85 °C | 55 °C | OK |
| Shock | 10,000 g | | OK |

## Required external parts

- 100 nF X7R from VDD (pin 5) to GND (pin 3), "as close to pin 5 as possible".
- Supply filtering is optional (PSR −97 dBFS at 217 Hz). Fit a 10 Ω series resistor from +3V3,
  which drops 4.3 mV at 430 µA.
- SELECT (pin 2): to GND, so data is output on the right channel (DATA1, driven after the
  falling clock edge). The FPGA samples on the rising edge.
- **No pull-up or pull-down on DATA** (datasheet: it would pull the tristated line to a wrong
  state).
- PDM_CLK: a 33 Ω source series resistor at the FPGA. Keep the trace < 15 cm (the datasheet
  needs a buffer beyond that).

Pins (Table 9): 1 DATA, 2 SELECT, 3 GND, 4 CLK, 5 VDD.

## Calculations

- Timing: DATA1 is valid ≤ 50 ns after CLK falls and disabled 5–40 ns after CLK rises. At
  3.072 MHz the half-period is 163 ns, so sampling at the next CLK rising edge leaves ≥ 113 ns.
  OK. For a single mic the line holds its state through the tristate time (datasheet Fig. 9).
- CLK rise/fall ≤ 25 ns: the FPGA edge is a few ns. OK.
- Wake-up 20 ms; mode switching 10 ms. Firmware discards the first 20 ms.
- Decimation in the FPGA: CIC plus FIR with ≥ 106 dB filter dynamic range (≥ 18 bits), per
  "Dynamic range considerations", so the system noise degrades by only 0.4 dB.

## Mechanical/acoustic (R-16, to phase 4)

- **Open issue:** the board sits inside a sealed speaker cabinet. A bottom-port mic needs its PCB
  hole to see room air, not cabinet air. So it must sit on the back-panel side of the board, under
  an acoustic port through the back panel, with a gasket that seals the port path from the
  cabinet interior. Otherwise it measures the inside of the box.
  - Alternative: mount the mic on the panel-facing side next to the jacks, with a tube or gasket
    to a panel hole.
  - Phase 4 decides. If neither works, the MEMS mic is of limited use and the ext mic carries the
    function.
- Handling: do not pull a vacuum or blow air through the port, and no ultrasonic or wash on the
  port side. JLC must be told: "no wash on MK1".
- PCB thickness doesn't matter (datasheet).

## Open questions

- The port location and seal, above, for phase 4 and the user.
