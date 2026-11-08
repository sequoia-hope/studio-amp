# Block E — interfaces, rail loads and proposed changes (ECP5 version)

FPGA is now the Lattice **LFE5U-25F-7BG256I** (user, 2026-11-07). The Gowin version of this file is `E-interfaces-gowin.md` (superseded).
Block E: RP2350B + W25Q128JVSIQ + 12 MHz crystal (`E-mcu-*.md`, `E-flash-w25q128.md`, `E-xtal-12mhz.md`); ECP5 (`E-fpga-ecp5.md`, `E-fpga-ecp5-passives.md`); LAN8720AI (`E-phy-*.md`); 50 MHz RMII oscillator (`E-clk-rmii-50mhz.md`); 24.576 MHz VCXO (`E-clk-audio-vcxo.md`); link (`E-link.md`); pins (`E-pinmap.md`).

## Proposed changes to architecture

1. **FPGA: ECP5 LFE5U-25F-7BG256I (C1550762), configured over slave SPI from the RP2350** (CFGMDN = 001). This is architecture decision 2 as first written: no FPGA flash, A/B bitstreams in the RP2350's QSPI flash. Bitstream ≤ 5.42 Mb (677.5 KB) → 2 × 1 MB slots + 2 × 6 MB RP2350 images fit 16 MB (R-56). Load ≈ 0.15 s at 37.5 MHz. Update the block diagram's FPGA box ("GW1NR-LV9QN88" → "LFE5U-25F caBGA-256"). The Gowin golden-image/JTAG scheme, the 1.8 V bank and the level translators are dropped.
2. **Rails change for block C:** `+1V1` (new, ECP5 core) replaces `+1V2`; `+2V5` (new, VCCAUX); **`+1V8` is no longer needed** by block E. All FPGA I/O banks on `+3V3`.
3. **PCB: 6 layers recommended** for the caBGA-256 fan-out (0.8 mm pitch; configuration/JTAG balls the silicon fixes sit in ball rings 3–4). No via-in-pad; dog-bone vias 0.20/0.45 mm (JLC's smallest without surcharge). Decision for phase 4/5 (R-70 already allows 6). A 4-layer board is possible but loses the under-BGA decoupling side.
4. **PWM edge grid 1.695 ns baseline** (PLL ×12, ODDRX2F at 589.8 Mb/s, 84 % of the −7 commercial limit; review MAJOR-1). The 1.453 ns ×14 setting (98 % of a commercial limit, on an industrial part) is a bring-up option only. R-53's "≤ 1 ns" physical target is not met. Allowed audio-locked fsw on the baseline: **576 kHz** (N = 1024) or 768 kHz (N = 768). **448 kHz is not reachable** as an integer division of ×12 (`E-fpga-ecp5.md`). Block D is told.
5. **Slow status and enables move onto FPGA pins** (the ECP5 has 101 spare I/O): PD class bits, PG_5V/PG_3V3, LED/Qwiic enables and faults, HP/LO enables, HP fault/detect, VUSB_DET. **The TCA9535 expander is dropped.** PHY MDC/MDIO/nRST/nINT also move to the FPGA (it hosts the MAC). VDRV_EN/VDRV_PG stay on the RP2350.
6. **Hot-socketing rule** (ECP5 DS §3.6): while `+3V3` is up and `+1V1` is still below POR, left/right-bank A/B pins have a low-impedance path between them. Always-powered drivers therefore go to top banks where possible; on left/right banks their pair partner is left unconnected and a series resistor is fitted (`E-pinmap.md`). For block C: keep the 3V3-PG → 1V1-EN delay short (it already is: about 1 ms soft-start).
7. **Default pin state is now pull-*down*** (ECP5 GPIO tri-stated with weak pull-down until configured). Block D's PWM/enable pull-downs remain as backstops; active-low chip selects get 4.7 kΩ pull-ups.
8. Carried over from the Gowin version: VCXO audio clock (PTP-trimmed by the FPGA) with block F's MCLK_Q taken straight from it; 8-bit PIO link (now to bank 8/3 pins); PD status into the FPGA; RP2350 ADC0–3 knobs, ADC4–7 NTCs.

## Rail loads from block E (for block C)

| Rail | Consumer | Typical | Design (worst) | Requirement | Source |
|---|---|---|---|---|---|
| **`+1V1`** (new) | ECP5 VCC (6 pins) | ≈ 250 mA (77 mA static + dynamic, estimated) | **400 mA** | 1.045–1.155 V incl. noise; regulator accuracy ≤ 3 %; monotonic ramp 0.01–10 V/ms; up together with or after `+3V3` | DS-02012 Tab 3.2, 3.3, 3.8; TN-02038 §2, §4 |
| **`+2V5`** (new) | ECP5 VCCAUX (2 pins, via 120 Ω bead) | ≈ 20 mA (16 mA static) | **50 mA** | 2.375–2.625 V; ramp ≤ 30 mV/µs and 0.01–10 V/ms; PLL noise target < 0.25 % peak (6 mV); up with or after `+3V3` | DS Tab 3.2 note 4, Tab 3.8; TN-02038 §2.2 |
| **`+3V3`** | ECP5 VCCIO0–3, 6–8 | 10 mA | 50 mA | **≤ 3.465 V** (VCCIO max) incl. ripple → regulate 3.3 V ± 3 %; first rail up | DS Tab 3.2 |
| | RP2350 | 45 mA | 100 mA | | RP2350 Tab 1446 |
| | W25Q128JV | 10 mA | 25 mA | | W25Q §9.5 |
| | LAN8720AI incl. magnetics centre tap | 91 mA | 150 mA (10BASE-T) | ≤ 3.6 V abs | LAN8720A Tab 5-1, Note 5-7 |
| | 50 MHz XO + VCXO | 14 mA | 22 mA | | oscillator datasheets |
| | pull-ups, PHY LEDs | 2 mA | 5 mA | | |
| | **Total `+3V3` from block E** | **≈ 170 mA** | **≈ 350 mA** | | |
| `+1V8`, `+1V2` | — | 0 | 0 | **not needed by block E** any more | |

Block E power ≈ 0.9 W typical (0.28 W core, 0.05 W aux, 0.56 W on 3V3), ≈ 1.7 W worst — inside R-33a's 2.5 W logic allowance.
Sequencing: `+3V3` first; `+1V1` and `+2V5` after or together (block C's chain from 3V3 PG meets it). POR needs VCC ≥ 0.9–1.0 V, VCCAUX ≥ 2.0–2.2 V, VCCIO8 ≥ 0.95–1.06 V; tICFG ≤ 33 ms to INITN↑.
USB-only mode (R-23): `+3V3`, `+1V1`, `+2V5` all come up on USB power, so the FPGA and PHY run.

## Signals to/from other blocks

| Block | Net(s) | Where | Level / notes |
|---|---|---|---|
| A | `PD_PG_N`, `PD_TPH_N`, `PD_TPL_N`, `PD_BT_N` | FPGA A2–A5 (top bank 0) | 3.3 V from the isolator, all active low, high when the primary is unpowered (`A-interfaces.md`); 1 kΩ series |
| A | MDI pairs | PHY ↔ RJ45 magnetics | unchanged (`E-phy-*.md`) |
| B | `POE_LOSS_N` | FPGA A6 (top bank 0) | **owner: block B**: VBUS-droop comparator, active low at VBUS < 40 V (third-pass MAJOR-1; the earlier pulse detector is retired), open-drain (2N7002, VOL ≤ 10 mV at 1.37 mA; fourth-pass change), active low; asserts ≥ 16 µs before the converter stops and holds ≈ 10 ms. 4.7 kΩ pull-up on the net (block E; sized against the ECP5 pre-configuration pull-down), 1 kΩ series into the FPGA; the net also drives block F's separate BAT54C (D_PL) to the two relay gates. **This is not an OR into /DC_TRIP** (`F-mute-relay.md`). Total load at the B FET: 3.3 V/4.7 kΩ + 2 × 3.3 V/10 kΩ ≈ 1.37 mA |
| B | `ILIM_SEL0`, `ILIM_SEL1` | RP2350 GPIO34, GPIO35 → B | 3.3 V GPIO into B's 2N7002 gates; B's 100 kΩ pull-downs → reset 00 = 0.44 A (Type 2); 01 = 0.94 A (Class 6), 10 = 0.80 A (spare), 11 = 1.30 A (Class 8). Firmware sets them from the PD class bits (via the FPGA) or LLDP |
| B | `IBUS_SENSE` | B → RP2350 ADC4 (GPIO44) | 0–3.0 V for 0–1.5 A (2.0 V/A), ≈ 67 kΩ source (INA281 on B's VSR 10 V from VBUS, 100 Ω/470 nF, 200 k/100 k divider), RC-filtered at 3.4 kHz; **VSR can be up before +3V3: ≤ 45 µA pad injection, accepted**; 100 nF at the pin; pad leakage error ≤ 67 mV worst case (telemetry only) |
| B | `ACF_PULSE` | B → FPGA B6 (top bank 0) | 3.3 V push-pull copy of the forward-SR NCP4306 gate drive from block B's 74LVC2G08 gate B (on +3V3, same rail as the FPGA, so no injection): one rising edge per real conduction pulse, none during pulse-skip, ±30 ns jitter against the sync clock; pulses down to ≈ 0.25–0.3 µs at light load. **737.28 kHz crystal-locked (± 40 ppm)**; 4.7 kΩ series (agreed with block B). The gateware applies the AB-M3 run-average rule below |
| C | `PG_5V_N`, `PG_3V3_N` | FPGA B3, B4 | **buffered, active-low copies** (block C: 2N7002 on PG_5V/PG_3V3 pulling a 4.7 kΩ pull-up to +3V3 low; low = good). The real PG nets (PG_3V3 = 1V1 EN) no longer reach the FPGA, which ends the pull-down deadlock. Gateware inverts them; LPF PULLMODE=NONE on B3, B4, B5 |
| C/F | `PG_3V3Q` | FPGA B5 (top bank 0) | TPS7A94 PG, open-drain, block C's 100 kΩ pull-up; 1 kΩ series. **Gateware rule:** hold `DAC_L0–3`, `DAC_R0–3` low while PG_3V3Q is low (74LVC74A has no Ioff); start the streams only after it goes high. Before configuration the ECP5's weak pull-downs keep them low as well |
| C | `VDRV_EN`, `VDRV_PG` | RP2350 GPIO36, GPIO33 | VDRV_EN with block C's 100 kΩ pull-down |
| C/G | `LED_EN`, `QWIIC_PWR_EN` | FPGA H15, J16 | default low (FPGA pull-down). Backstops: LED_EN 100 kΩ; **QWIIC_PWR_EN 10 kΩ**, because the TCA9617B EN's −25 µA internal pull-up held 100 kΩ at ≈ 1.47 V. J16 sources 0.33 mA when high. QWIIC_PWR_EN drives both the TPS2553 EN and the TCA9617B EN |
| C/G | `LED_FAULT_N`, `QWIIC_FAULT_N` | FPGA K16, C14 | open-drain; block C fits the 10 kΩ pull-ups at the TPS2553s; 1 kΩ series |
| D | `PWM_W_A`, `PWM_W_B`, `PWM_T_A`, `PWM_T_B` | FPGA N1, P1, R2, R4 (bank 6) | LMG1210 PWM mode (high = HS on), ODDRX2F, **1.695 ns grid (×12 baseline)**, matched routing, 100 Ω at the driver (block D); fsw 576 kHz (N = 1024) baseline, 768 kHz option; 448/512/672 kHz only on the ×14 bring-up option |
| D | `FAULT_W_n`, `FAULT_T_n` | FPGA L1, M1 | from block D's 74LVC1G74 fault latch path (gates already off in hardware when low); 330 Ω series, partners NC |
| D | `DC_W_n`, `DC_T_n` | FPGA J1, G1 (bank 7) | open-drain + 10 kΩ pull-up at D; 1 kΩ series, partners NC |
| D | `AMP_CLK_W`, `AMP_CLK_T`, `AMP_ARM` | FPGA P2, T2, R1 | ARM has block D's 10 kΩ pull-down (agrees with the ECP5 default pull-down) |
| D | `AMP_EN_W/T` | FPGA R5, T4 | fault-latch D inputs; default low |
| D | ADS7042 `VB_CS_n/VB_SCLK/VB_SDO` | FPGA P4, N3, M4 (VB_CS_n moved from T3, review MINOR-7) | ≤ 16 MHz, own bus, PWM-synchronous |
| D | ADS7038-Q1 `IS_CS_n/IS_SCLK/IS_SDI/IS_SDO` | FPGA L3, M3, R3, P3 | ≤ 60 MHz; channels 4–7 carry the four NTCs (block D's proposal, accepted) |
| D | 2 × ADS8353 `PF_CS_n/PF_SCLK/PF_SDI/PF_SDO_WA/WB/TA/TB` | FPGA K4, L4, K5, L5, M5, N5, N6 | optional population; pins reserved (R-51). All three CS lines have 4.7 kΩ pull-ups |
| D | NTCs ×4 | via the ADS7038-Q1 to the FPGA | RP2350 ADC4–7 are now spare |
| F | `DAC_L0–3`, `DAC_R0–3` | FPGA bank 3 (N16, P15, P16, R16, R13, T14, R12, T13) | launched on MCLK↓, tCO ≤ 6.1 ns (≤ 12 ns asked) |
| F | VCXO → `MCLK_Q` buffer → FFs + PCM1808 SCKI | E → F, own 33 Ω branch | phase noise not specified by the VCXO datasheet (see `E-clk-audio-vcxo.md`) |
| F | `MADC_BCK`, `MADC_LRCK` (out), `MADC_DOUT` (in) | FPGA P13, R14, L16 | DOUT 330 Ω series, partner NC |
| F | `PDM_CLK` (out), `PDM_DAT` (in) | FPGA L14, N13 | DAT 330 Ω series, partner NC |
| F | `HP_EN`, `LO_EN` (out), `HP_FAULT_N`, `HP_DET` (in) | FPGA M14, N14, P11, K13 | relay enables are FPGA pins (no expander); block F drives each gate through 10 kΩ with 100 kΩ pull-downs. **Gateware drops HP_EN/LO_EN within µs of `POE_LOSS_N` low or `PD_PG_N` high** (both are FPGA inputs, no firmware in the path). Block F's diode-OR of PoE-loss into /DC_TRIP is also welcome as a hardware backstop. Inputs 1 kΩ series, partners NC |
| G | display ×8 header positions | FPGA B16, C16, C15, D16, E15, E16, F15, F16 | 3.3 V direct (no translator); series R at the header |
| G | `DISP_BL_PWM` | FPGA G15 (bank 2) | drives block G's 2N7002 → AO3401A high-side backlight switch; 4 mA, default low (ECP5 pull-down + G's 100 kΩ), PWM ≤ 2 kHz. **Gateware rule:** whichever header line is jumpered to DISP_BLK (pin 8 by default) is constrained Hi-Z |
| G | `PTP_PPS` | FPGA G16 | test point |
| G | `VUSB_DET` | FPGA E14 | block C's 15k/22k divider (≤ 3.12 V) + 100 nF; 1 kΩ series |
| G | FPGA JTAG header (R-22) | FPGA T10, R11, M10, T11 | 3.3 V direct, 4.7 kΩ pulls per TN-02038 |
| G | I2C, LED data/clock, encoders, knobs, UART, SWD, USB | RP2350 | unchanged |

## Notes from blocks C and F (2026-11-07), against the ECP5 plan

- Block C's TPS62A02A (forced PWM, 2.4 MHz) is right for the ECP5 core. Retarget the "1V2" buck to **+1V1**. The ECP5 checklist puts no bead in VCC, so set **1.10 V** at the pins (1.045–1.155 V window, ±3 % regulator). Block C's 2 × 22 µF plus my 3 × 10 µF + 6 × 100 nF form the PDN.
- **+1V8** (TPS7A2018) is no longer needed by block E. The PSRAM was Gowin-only. Delete it unless another block uses it.
- **+2V5** is needed: 50 mA, an LDO from `+3V3` is fine, ramp ≤ 30 mV/µs, up with or after 3V3.
- 2.4 MHz switching (3V3/1V1 bucks; the 5 V buck is now ≈ 200 kHz): harmless to the 12 MHz crystal, 50 MHz XO and 24.576 MHz VCXO. Keep the bucks' switch nodes away from the VCXO tune RC and the oscillators' supply pins.
- 3V3 total: superseded by the final figure below (0.66 A design, Qwiic capped at 100 mA). Block E's share stays ≈ 350 mA design.
- The I2C address 0x20 reservation can be released: the TCA9535 is dropped with the ECP5.
- Block F's MCLK_Q buffer (SN74LVC2G34, Ioff-rated) puts about 3.5 pF on our VCXO branch: fine within the 15 pF budget.

### Block C/G update received 2026-11-07 (accepted)

- `+1V1` TPS62A02AP at 1.107 V (1.088–1.127 V), `+2V5` TPS7A9401 at 2.505 V ± 1 % (ramp ≈ 2 mV/µs), both enabled from PG_3V3 ≈ 1 ms after 3V3 (final: +1V1 at 1.107 V, 1.080–1.134 V worst case with the E96 84.5 kΩ; +5V design 0.76 A; +3V3 design total 0.66 A: Qwiic capped at 100 mA by the user (switch limit 155–207 mA, firmware enforces 100 mA), block D comparators 85 mA): meets DS-02012 Tab 3.2/3.3 and TN-02038 §4. `+3V3` at 3.24–3.40 V with 0.5 % resistors: under VCCIO max 3.465 V. `+1V8` withdrawn.
- Typical `+1V1`: my estimate is ≈ 250 mA (77 mA static + dynamic; not from a power calculator). Block C's 0.2 A assumption is a little low; size for the 400 mA design figure.
- JTAG pulls (TDI/TMS/TDO 4.7 kΩ up, TCK 4.7 kΩ down) are on **this** block's sheet, at the FPGA (`E-fpga-ecp5-passives.md`); block G should not fit a second set at the header.
- Display BLK through 47 Ω at 16 mA: within the LVCMOS33 16 mA drive setting (VOH ≥ VCCIO − 0.4 V at 16 mA, DS-02012 Tab 3.12). The sysI/O guide (TN-02032 §4.11.1) says to respect "the maximum allowable current per bank" but none of the documents in hand gives a number. Bank 2's DC load is BLK ≤ 16 mA + µA-level CMOS inputs, so ≈ 17 mA. Block G adopted a FET backlight switch driven by `DISP_BL_PWM` (G15, 4 mA), so the steady 16 mA is off VCCIO2.
- USB-only mode (≈ 0.48 A at 5 V at design load): block E's typical share is ≈ 0.9 W (≈ 0.2 A at 5 V). Firmware should keep the PHY in reset (−90 mA on 3V3) and LEDs/Qwiic off when only USB is present.

## Gateware rules collected from other blocks

- **Block F:** hold `DAC_L0–3`, `DAC_R0–3` low until `PG_3V3Q` (B5) is high. PoE loss: see the **PoE-loss and VBUS-valid gateware rule** below; it drops `HP_EN`/`LO_EN` within ≤ 1 ms (R-34).

**PoE-loss and VBUS-valid gateware rule (third-pass MAJOR-1, lead 2026-11-08; identical text in B-, D- and E-interfaces.md):**
1. **VBUS valid.** The FPGA reads VBUS from block D's ADS7042 (576 kS/s). `VBUS_VALID` is **set** when VBUS > 44.0 V continuously for ≥ 10 ms after start-up. It is **cleared** only when PoE loss is declared, or when VBUS < 40.5 V by the ADC rule below. Normal burst sag (≥ 43.2 V, R-33) does not clear it.
2. **Hardware detector.** `POE_LOSS_N` (block B, open-drain into FPGA A6) is low when VBUS < 39.5 V (38.5–40.5 V), releasing above 41.1 V (40.0–42.2 V), 0.31 ms filter (B-vbus-droop.md). It is also asserted during every start-up ramp, so the FPGA **ignores `POE_LOSS_N` until `VBUS_VALID` has first been set**. After that, `POE_LOSS_N` low (level or falling edge) means PoE lost, and the FPGA latches it.
3. **ADC detector.** VBUS < 40.5 V on every ADS7042 sample for ≥ 0.5 ms (≥ 288 consecutive samples), while `VBUS_VALID` is set, ⇒ PoE lost.
4. **PoE lost = `POE_LOSS_N` low (after the step-2 gate) OR the step-3 ADC rule OR `PD_PG_N` high.** The FPGA latches the event. `PD_PG_N` rises 45–140 ms after LINEUV, so it is a slow backstop, not a prompt trigger; `POE_LOSS_N` and the ADC rule are the prompt paths.
5. **Action**, in gateware, independent of the RP2350:
   - drop `HP_EN` and `LO_EN` at once (relays open);
   - start block D's R-34 mute ramp to zero, completing in ≤ 5 ms, then stop switching;
   - report the event to the RP2350 over the link, and from there to the network.
   Restart only through the normal start-up sequence, after `VBUS_VALID` is set again.
6. **Calibration (block D, 2026-11-08).** The 44.0 V and 40.5 V thresholds apply to **calibrated** VBUS readings: the same one-time gain calibration as bus feed-forward (`D-vbus-adc.md`). Until a gain is stored, the ADS7042 divider's ±2 % error (≈ ±0.8 V at 40 V) is covered by **widened thresholds**:
   - set `VBUS_VALID` at raw > **44.9 V** (= 44.0 V × 1.02), so the flag can never be set early;
   - clear at raw < **39.7 V** (= 40.5 V / 1.02), so normal sag can never trip it.
   A real loss is still caught as VBUS keeps falling, and `POE_LOSS_N` (39.5 V hardware) and `PD_PG_N` act independently. Amp start is allowed on the widened thresholds (bring-up); the calibrated values take over once stored. **Agreed by the lead, 2026-11-08** (44.9 V stays below the 47.0 V static VBUS minimum, 48 V − 2 %).

- **Block F DAC noise shaper (F review m2):** in-band quantisation noise ≤ −140 dB re m = 1, A-weighted, 20 Hz–20 kHz (0.82 µV at line out); 6.144 Mb/s, ≥ 5th order, m ≤ 0.487.
- **Block D:** the 11 items in `D-interfaces.md` "Gateware requirements arising from block D". In short:
  - start-up only ≥ 200 µs after `VDRV_PG`, through ARM → EN → latch clock, then PWM held low ≥ 50 µs (all low sides on), then **ramp the duty from 0 % to 50 % over ≥ 1 ms, never a step** (block D re-review m-5). A step slews both outputs 0 → 24 V at ≈ 9 V/µs, which uses 0.42 V of the short detector's 1 V threshold and pops;
  - a speaker lead opening under ≳ 14 A trips the short detector: benign, and the FPGA re-arms per the fault policy;
  - re-arm only after `FAULT_x_n` is high again;
  - **duty clamp 8–92 % per leg (M ≤ 0.84): minimum leg pulse ≥ 139 ns at 576 kHz (= 82 steps of 1.695 ns; 8 % of the 1.736 µs period)**. This is hardware safety: at 3–97 % the bootstrap supply sagged to 3.6–4.0 V (block D review response);
  - GaN back to **IGB070S10S1** (user): effective dead time ≈ 18 ns (spread 14–24 ns), uncompensated H3 ≈ 1.5 % at 50 W into 8 Ω, so calibrate the compensation per board from the post-filter sense ADCs; idle power-stage loss ≈ 3.4 W at 576 kHz (auto-idle still worthwhile);
  - `FAULT_x_n` ORs two hardware paths, hard-short detection (≈ 48 ns) and the INA241 ramp path at 14.9 A (≈ 216 ns), so it can't say which tripped;
  - the hardware DC detector trips in 23 ms at 48 V, so the ≥ 15 Hz subsonic high-pass is still required;
  - at 576 kHz: ADS7042 VBUS sampled once per PWM period (576 kS/s, since 2 × fsw exceeds its 1 MSPS); I-sense legs rotate at ≈ 250 kS/s each; the uncompensated dead-time error is ≈ 0.41 V per leg (≈ 1.25 % H3 at 50 W into 8 Ω), so the dead-time compensation calibration is essential;
  - dead-time compensation from the current sign;
  - bus feed-forward from the ADS7042;
  - software DC detector, ≥ 15 Hz subsonic high-pass, HF/Zobel limiter;
  - thermal derate/shutdown from the NTCs;
  - auto-idle.
  `VDRV_PG` is an RP2350 input (GPIO33) only; the RP2350 passes "VDRV good" to the FPGA over the link (block D agreed). Block C's optional `AN_OFF` is **not** taken by block E (review NOTE-4); the analog mute is block F's hardware plus the HP_EN/LO_EN rule above.
- **PHY straps (review MAJOR-2):** LPF `PULLMODE=UP` on A11, A12, B11 (RMII RXD0/RXD1/CRS_DV = LAN8720A MODE straps), together with the 4.7 kΩ external pull-ups; release `PHY_NRST` only after configuration and ≥ 25 ms after the rails.
- **Link and SSPI (review MINOR-3, MINOR-6):** the RP2350 keeps GPIO8–19 Hi-Z until DONE is high, and puts them back to Hi-Z **before every PROGRAMN pulse** (A/B reload). DOUT/CSON (M8) drives high and WRITEN/CS1N (M9/P8) are pulled up during configuration (TN-02039 §4.7.2, Tab 4.5). SSPI read commands run at ≤ 18.75 MHz; bitstream bursts run at 37.5 MHz.
- **Display:** the header line jumpered to DISP_BLK is constrained Hi-Z.

## PWM fsw choice and noise-shaper estimate on the 1.695 ns grid (lead's request; agreed with block D: **576 kHz**)

Ideal estimate of the PWM noise shaper's in-band quantisation noise at the speaker terminals:
- **Model:** BTL, 48 V; each leg's duty quantised to 1/N of the period (step = 48 V / N); two independent legs; one modulator update per PWM period (sampling rate = fsw); NTF = (1 − z⁻¹)^L; integrated numerically over 20 Hz–20 kHz, unweighted and A-weighted.
- **Multi-level quantiser:** with N ≥ 768 levels the loop is stable at these orders, so the pure-differentiator NTF is a fair bound.
- **Left out on purpose:** NTF zero optimisation (worth a further 10–20 dB at L = 5), PWM uniform-sampling distortion, dead time and jitter. Those belong to block D and the RTL work.

| fsw (N on ×12) | OSR | L = 3 | L = 4 | L = 5 |
|---|---|---|---|---|
| 384 kHz (1536) | 9.6 | 54 µV (23 µV A) | 16 µV (6.3 µV A) | 4.6 µV (1.8 µV A) |
| 512 kHz (1152) | 12.8 | 26 µV (11 µV A) | 5.7 µV (2.3 µV A) | 1.3 µV (0.5 µV A) |
| **576 kHz (1024)** | 14.4 | 20 µV (8.4 µV A) | 3.8 µV (1.5 µV A) | **0.75 µV (0.29 µV A)** |
| 768 kHz (768) | 19.2 | 9.6 µV (4.1 µV A) | 1.4 µV (0.56 µV A) | 0.21 µV (0.08 µV A) |

Reading the table:
- Against R-51's ≤ 150 µV A-weighted (open-loop), and even the closed-loop ≤ 60 µV, **edge quantisation at 1.695 ns is not the limiting noise source at any of these fsw with a 4th- or 5th-order shaper**. The 1.453 → 1.695 ns change costs 1.3 dB of an already large margin.
- 384 kHz is 15.7 dB worse than 576 kHz at L = 5, consistent with block D's Δ²/OSR¹¹ scaling.
- The fsw choice is therefore driven by GaN loss, B-converter beat frequencies and R-53's 400 kHz floor, not by the noise shaper.
- **Confirmed: 576 kHz** (N = 1024): reopened by block B's move to 620 kHz, then re-confirmed after B's crystal sync at 737.28 kHz (next subsection). Block D's original reasons: the beat with block B's 376–424 kHz stays at 152–200 kHz; 384 kHz is below R-53's 400 kHz and inside B's band; 512 kHz beats at 88–136 kHz. Recommend L = 5 for margin against the real-world terms above.

**Non-48 kHz-multiple carriers in the gateware:** acceptable when fsw/48 kHz is a small rational. For example 512 kHz = 32/3 × 48 kHz needs a 32-phase polyphase interpolator with decimate-by-3, which fits in a few EBRs and multipliers. Not acceptable for large ratios: 448.2 kHz = 3072/329 × 48 kHz needs too many phases for the gain. 576 kHz is an integer ×12, so the question doesn't arise for the chosen baseline.

### PWM fsw vs block B's converter — **resolved: ACF crystal-synced at 737.28 kHz, fsw stays 576 kHz** (block B, 2026-11-07)

Block B implemented option 1. The UCC2897A is now synchronised to a primary-side 7.3728 MHz crystal ÷ 10 → **737.28 kHz ± 40 ppm**. ±5 % free-running wasn't achievable: the internal timing capacitor gives −10/+8 % over temperature.
- **Beats with 576 kHz**, checked for all a, b ≤ 3: the smallest is 161 kHz (f − 576). The others are 415 (2·576 − f), 253 (3·576 − 2f) and 323 kHz (2f − 2·576). All are ≥ 100 kHz. **fsw = 576 kHz (N = 1024, ×12 grid) is locked.**
- **Sync failure:** the controller free-runs at 590–708 kHz (656 nominal). Against 576 kHz the beat can then fall to 14 kHz, inside the audio band.
- **ACF_PULSE definition (block B, AB-M3):** a 3.3 V buffered copy of the forward-SR NCP4306 gate drive. It gives exactly one rising edge per real conduction pulse and none during pulse-skip; the edge jitters about ±30 ns against the sync clock.

**ACF_PULSE converter-clock-fault rule (AB-M3, one rule agreed by blocks B and E, 2026-11-07; identical text in B-interfaces.md and E-interfaces.md):**
1. Timestamp every ACF_PULSE rising edge at 147.456 MHz (6.8 ns). T = 1/737.28 kHz = 1.3563 µs.
2. A **run** is a sequence of consecutive rising-to-rising intervals, each within 0.8–1.3 T. Any interval outside that range (a skip of ≈ 2T, a gap, DCM dead time) ends the run.
3. A run of **≥ 64 intervals** is qualifying. It **passes** if its average interval is within **T ± 0.5 %**, and **fails** otherwise. Averaging 64 intervals reduces B's edge jitter and shift (tens of ns) to ≤ 0.07 %.
4. Each **10 ms window**, judged on the qualifying runs that complete inside it, gives one verdict:
   - **LOCKED**: at least one qualifying run, and all of them pass.
   - **FAULT**: any qualifying run fails.
   - **UNKNOWN**: no qualifying run (deep skip, burst, stopped, start-up).
5. **Clock fault** = 3 consecutive FAULT windows. The amp does not start, or ramps to zero and mutes (R-34 path). The fault is latched, readable by the RP2350, and reported over the network.
6. The amp starts on **LOCKED or UNKNOWN only**.
7. The whole check is gated by **VBUS valid** (ADS7042), so USB-only power never reports a fault.
8. Margin: a free-running converter (590–708 kHz) has intervals of 1.041–1.25 T. Its runs qualify, and their average misses T by ≥ 4.1 %, so it reads FAULT.
9. ≥ 64 consecutive intervals all < 0.8 T, or all within 1.3–1.9 T, is also a FAULT window.

- **On a clock fault (hard rule, lead):** the amp does not start, or ramps to zero and mutes (the R-34 path). The fault is latched, readable by the RP2350 over the link, and reported over the network. Block D's 768 kHz degraded mode remains a possible later firmware option only.
- PoE loss: see the PoE-loss and VBUS-valid gateware rule above (POE_LOSS_N low OR the ADC rule OR PD_PG_N high).

History of the conflict. **Superseded:** the 620 kHz figures below are block B's withdrawn plan, kept for the record only. Current values: 737.28 kHz crystal-locked, 4.7 kΩ series.


Block B moved the ACF from ≈ 400 to **620 kHz ± 10 % (558–682 kHz)**. It asks that no product |a · f_acf − b · f_amp| with a, b ≤ 3 fall below 100 kHz. Checked by script over the full tolerance band:
- **576 kHz fails:** with a = b = 1 the beat can reach 0 Hz (f_acf = 576 kHz lies inside the band). In fact **no f_amp keeps every product ≥ 100 kHz for a ±10 % ACF**, except a 782–787 kHz sliver (e.g. 785.4 kHz, N = 751), which isn't audio-locked and has ≈ 9 W idle loss.
- With **±5 % ACF tolerance**:
  - 576 kHz works only if B's nominal sits at 712–775 kHz (or 440–453 kHz);
  - 768 kHz (N = 768, 16 × 48 kHz) works for nominal 575–636 kHz, which covers 620 kHz;
  - 480 kHz works too, but isn't an integer N on ×12.
- With the **ACF frequency measured per board** (ACF_PULSE), at exactly 620 kHz the allowed f_amp bands are 447–520, 720–880 and 980–1000 kHz: 448 kHz, 480 kHz and 768 kHz pass, 576 kHz does not (44 kHz beat).

Options, for block B, block D and the lead (not for block E alone):
1. **Block B tightens the ACF to ±5 % and moves its nominal to ≈ 740 kHz.** 576 kHz stays (lowest-loss audio-locked choice on ×12). This costs B switching loss.
2. **Keep ACF 620 kHz ± 5 %, go to fsw 768 kHz** (N = 768, 1.695 ns grid, noise −11 dB vs 576 kHz). Block D's IGB070 figures:
   - idle FET loss 3.34 vs 1.80 W, idle VBUS draw ≈ 5.5 vs 3.8 W;
   - efficiency at 46 W into 4 Ω ≈ 87 vs 90 %;
   - Tj at 144 W into 4 Ω 90/149 vs 83/129 °C (with panel / without);
   - bootstrap 4.03 V at the 8–92 % clamp, VDRV 57 mA.
   Acceptable fallback with no block D part changes.
3. **Keep ACF 620 kHz, go to fsw 448/480 kHz on the ×14 option** (1.453 ns). 448 kHz is 1536 steps on ×14 and passes at an exact 620 kHz (104 kHz). That needs the ×14 gearing (bring-up option, 98 % of the commercial limit) and a ±≈2 % ACF.
4. Relax B's rule (e.g. only products that land below ~25 kHz in the audio band, or a, b ≤ 2).

Blocks E and D both recommend **option 1** (block D, 2026-11-07); 768 kHz is the agreed fallback if block B can't move. **Awaiting block B's answer.** Block E recommends **option 1**: it keeps the agreed 576 kHz, the ×12 margin and the lowest GaN loss. The gateware can confirm f_acf on every board through ACF_PULSE and refuse to start the amplifier if a product falls below the limit.

**Other clocks in the system (clock plan):**

| Source | Frequency |
|---|---|
| Block C VDRV converter | ≈ 305 kHz (230–410 kHz) |
| Block C Fly-Buck (LM5017, RON 330 kΩ) | ≈ 465 kHz (347–620 kHz): sweeps across 576 kHz; accepted residual ≈ −94 dBc (C-interfaces.md) |
| Block C 5 V buck (LM5013, COT, RRON 64.9 kΩ) | **≈ 213 kHz (181–245 kHz spread)**; earlier ≈ 690 kHz, then 170–230 kHz. Its 3rd harmonic (543–735 kHz) crosses 576 kHz near 192 kHz: accepted residual ≈ −83 dBc (block C). Worst beat (a·f − b·f′ in magnitude, a, b ≤ 2) against 576 kHz and 737.28 kHz: 84 kHz per block C (86 kHz by my check at the band edges) |
| 3V3 and 1V1 bucks | 2.4 MHz |
| Block B ACF | **737.28 kHz ± 40 ppm**, crystal-synced (free-run fallback 590–708 kHz, flagged by the gateware) |
| PWM | 576 kHz |
| Reference clocks | 12, 24.576 and 50 MHz |

- Audio-band products:
  - ACF beats are ≥ 161 kHz.
  - The 5 V buck's fundamental and 2nd harmonic beat with PWM and the ACF at ≥ 84 kHz, but its **3rd harmonic** (543–735 kHz) and the **Fly-Buck** (347–620 kHz) can cross 576 kHz and produce audio-band beats. Block C accepts these as residuals at ≈ −83 and −94 dBc (C-interfaces.md).
  - Bring-up check: measure the idle output spectrum for these tones.
- The bucks' harmonics near the reference clocks (e.g. 2.4 MHz × 5 = 12 MHz, the RP2350 crystal): no lock-in issue for crystals or XOs. Keep switch nodes away from the oscillator supply pins and the VCXO tune RC, as block C has noted.

## Things needing a user decision

- **6-layer board** for the BGA (proposed; no via-in-pad, no via surcharge).
- **Edge resolution 1.695 ns baseline (1.453 ns bring-up option) vs R-53's ≤ 1 ns**, and **fsw 576 kHz** (agreed with block D). The noise-shaper estimate shows edge quantisation is not the noise limiter. The cost of 576 kHz is GaN loss: block D gives ≈ 2 W more idle than the ×14/448 kHz option, which goes to the user as a budget decision.
- **MCLK_Q jitter** (block F): the VCXO datasheet gives no phase-noise figure, so ≤ 1 ps over 20 kHz–12 MHz is unverified. The fallback is a land shared with a 0.7 ps fixed XO (C5203547), which loses the PTP lock of the DAC clock.

## Review response (design/gates/review-phase1-E.md, 2026-11-07)

| Finding | Resolution |
|---|---|
| MAJOR-1 gearing at 98 % of a commercial limit | **Fixed.** ×12 is the baseline: CLKOP/ECLK 294.912 MHz, 589.824 Mb/s, **1.695 ns** grid, 84 % of the −7 commercial limits. ×14 (1.453 ns) is a bring-up option until −7I numbers come from Diamond or characterisation. Allowed audio-locked fsw: **576 kHz** (N = 1024), 768 kHz (N = 768). **448 kHz is not reachable** on ×12 (N = 1316.57); 448.2 kHz needs a non-integer fsw/fs interpolator (not recommended). The commercial-tCO caveat is stated with ≥ 4 ns slack kept (≈ 8 ns derated tCO) in `E-fpga-ecp5.md`, `E-clk-rmii-50mhz.md`, `E-link.md`, `E-clk-audio-vcxo.md`. Block D told. |
| MAJOR-2 PHY straps vs ECP5 pull-downs | **Fixed.** 4.7 kΩ pull-ups to +3V3 on RMII_RXD0/RXD1/CRS_DV (A11/A12/B11), sized against 150 µA (≥ 2.6 V vs VIHT ≤ 1.90 V; 10 kΩ would give only 1.8 V). Gateware rule PULLMODE=UP on those balls; nRST released after configuration. The Gowin "consistent pull-ups" text is replaced (`E-phy-lan8720.md`, `E-fpga-ecp5-passives.md`). |
| MAJOR-3 B ↔ E nets, POE_LOSS_N owner | **Fixed.** `ILIM_SEL0/1` → RP2350 GPIO34/35 (B's 100 kΩ pull-downs: reset = 0.44 A). `IBUS_SENSE` → RP2350 ADC4 (GPIO44) + 100 nF. `ACF_PULSE` → FPGA B6, 4.7 kΩ. `POE_LOSS_N`: owner block B (lead's decision), open-drain active low → FPGA A6, 4.7 kΩ pull-up on the net (E), 1 kΩ series; the net also drives block F's BAT54C (D_PL) to the relay gates. |
| MINOR-1 SSPI persistence read-only | **Fixed.** Every reload starts with PROGRAMN; SLAVE_SPI_PORT=ENABLE is kept for status reads only. |
| MINOR-2 CCLK pull-up | **Fixed.** 1 kΩ to VCCIO8 added; RP2350 SCK at 8 mA. |
| MINOR-3 SSPI reads at 37.5 MHz | **Fixed (firmware rule).** Reads ≤ 18.75 MHz, bitstream bursts at 37.5 MHz. |
| MINOR-4 PLL input tR/tF ≤ 1 ns | **Recorded as a known deviation.** No series R on the FPGA branch, shortest and lightest load; measure at bring-up (`E-clk-audio-vcxo.md`). No stocked VCXO guarantees ≤ 1 ns. |
| MINOR-5 PD_PG vs PD_PG_N | **Fixed.** Renamed `PD_PG_N` (active low); mute rule is now "PD_PG_N high". |
| MINOR-6 link pins during reconfiguration | **Fixed.** Rule added: tri-state GPIO8–19 before every PROGRAMN, re-enable after DONE (`E-link.md`). |
| MINOR-7 VB_CS_n pull-up on the PWM_T_B pair | **Fixed.** VB_CS_n moved T3 → P4 (partner R3 = IS_SDI); T3 must stay unconnected. |
| MINOR-8 stale Gowin text | **Fixed.** Bodies rewritten in `E-mcu-rp2350b.md`, `E-flash-w25q128.md` (1 MB slots, no golden image), `E-phy-lan8720.md`, `E-phy-passives.md`, `E-clk-rmii-50mhz.md`, `E-clk-audio-vcxo.md`, `E-link.md`. Gowin-only files stay, marked superseded. |
| Pre-configuration pull-down sweep (lead, after C+G review) | Done: new columns in `E-pinmap.md`. POE_LOSS_N pull-up → 4.7 kΩ. Actions: block D DC_x_n pull-ups ≤ 4.7 kΩ if read in hardware; block C fixing PG_3V3/PG_5V; LPF PULLMODE rules listed. |
| MINOR-9 HP_EN/LO_EN series R | **No resistor:** they are outputs into block F's 10 kΩ gate resistors; block F to drop "1 kΩ (block E)" from its table (told). |
| NOTE-1 bank 8 has no DDR | Text corrected in `E-fpga-ecp5.md`. |
| NOTE-2 tCO test conditions | Stated where 6.1 ns is used (≈ 8 ns derated). |
| NOTE-3 clock-capable pins on slow lines | Kept: bank 6 needs no external clock input (the PWM ECLK comes from the PLL fed by P6). K1 remains the spare clock input. |
| NOTE-4 VDRV_PG / AN_OFF | Recorded: VDRV_PG on RP2350 GPIO33 only, AN_OFF not taken. |
| NOTE-5 SX3V drift decode | Corrected; the design relies on APR ±50 ppm only. |
| NOTE-6 0.09 mm trace in the BGA field | Agreed; re-check against JLC's capability page in phase 5. |
| NOTE-7 emulated open-drain on PROGRAMN | Stated in `E-fpga-ecp5.md`. |

## Second-pass review response (design/gates/rereview-phase1-EF.md, 2026-11-07)

| Finding | Resolution |
|---|---|
| MINOR-1 POE_LOSS_N pull-up / F load | 4.7 kΩ everywhere in E. F's load is described as its separate BAT54C (D_PL) to the relay gates, not an OR into /DC_TRIP. Block F agrees (4.7 kΩ, D_PL as the only F load). |
| MINOR-4 PROGRAMN mechanism | Firmware gate in `E-fpga-ecp5.md`: wait for INITN (GPIO23) high, then ≥ 10 ms, before the first PROGRAMN pulse; the same gate before every A/B reload. |
| MINOR-5 D[7:2] no pull during config | `E-link.md` rule: RP2350 pad pull-downs (36–113 kΩ) stay **enabled** whenever GPIO8–15 are tri-stated (before DONE, and before/through every PROGRAMN). |
| MINOR-6 ACF_PULSE text and series R | 737.28 kHz crystal-locked; 4.7 kΩ series in E. Block B agrees: single 4.7 kΩ at B6, B's 100 Ω removed. |
| MINOR-7 IBUS_SENSE cap | **100 nF** (24 Hz pole, fine for telemetry); E and B aligned (τ ≈ 6.7 ms with 67 kΩ). |
| MINOR-8 stale E text | `E-fpga-ecp5.md` CS pull-ups → 4.7 kΩ; open question → 1.695 ns; `E-pinmap.md` headroom excludes T3 (held NC). |
| NOTE-1 clock-fault check on USB-only | Gated on VBUS valid; superseded by the AB-M3 run-average rule (no qualifying run ⇒ UNKNOWN, no mute). |
| NOTE-2 100 kΩ pull-ups into FPGA inputs | Agreed: ≥ 2.24 V with PULLMODE=NONE (IIH ≤ 10 µA); pass. 47 kΩ would be more comfortable; left to blocks C/F. |
| MINOR-3 (/DC_TRIP 10 kΩ) | Closed: block F fitted 4.7 kΩ on HP_FAULT_N; HP_DET pull-up is now 47 kΩ. |
| MINOR-2 (B's FET on POE_LOSS_N) | Closed by block B: AO3400A at the time (also on ILIM). The fourth-pass change returned POE_LOSS_N to a 2N7002, VOL ≤ 10 mV at 1.37 mA per block B. |
