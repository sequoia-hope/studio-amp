> **SUPERSEDED by ECP5 (user, 2026-11-07).** The FPGA is now the Lattice LFE5U-25F-7BG256I; see `E-fpga-ecp5.md`, `E-pinmap.md`, `E-interfaces.md`. Kept for the record; do not build from this file.

# Block E — interfaces to other blocks, rail loads, and proposed changes to the architecture

Block E: RP2350B + W25Q128JVSIQ + 12 MHz crystal (`E-mcu-*.md`, `E-flash-w25q128.md`, `E-xtal-12mhz.md`); GW1NR-LV9QN88PC6/I5 (`E-fpga-*.md`); LAN8720AI PHY (`E-phy-*.md`); 50 MHz RMII oscillator (`E-clk-rmii-50mhz.md`); 24.576 MHz VCXO (`E-clk-audio-vcxo.md`); 3 × SN74AVC4T774 (`E-level-jtag.md`, `E-level-display.md`); link (`E-link.md`); pins (`E-pinmap.md`).

## Proposed changes to architecture

1. **FPGA configuration: JTAG + internal golden image, not SSPI** (changes architecture decision 2 and the block-diagram edge "SSPI config").
   In QN88/QN88P packages the SSPI pins **SCLK and SI are not bonded** (UG803 pin list), so SSPI (and SERIAL/CPU) configuration is impossible on the only GW1N(R)-9 in stock. DONE and READY are not bonded either. New scheme: MODE = 000 (AUTOBOOT) loads a **golden** bitstream from the GW1NR-9's own configuration flash at power-up; the RP2350 then loads the **A/B** bitstream from its QSPI flash into FPGA SRAM over **JTAG** (openFPGALoader's Gowin sequence; TCK 10–20 MHz, ≤ 25 MHz), checks DONE in the JTAG status register, and falls back by pulsing RECONFIG_N. The golden image is rewritten over the same JTAG port (background eFlash programming). Decision 2's "The FPGA has no flash of its own" becomes "the FPGA's internal flash holds only a recovery image; A/B images live in the RP2350 flash". R-56 still holds (`E-flash-w25q128.md`).
2. **New rail `+1V8`** for FPGA bank 3 (VCCIO3), which also powers the embedded PSRAM: **1.71–1.89 V** (UG803). Bank 3 carries JTAG, RECONFIG_N, MODE and 15 user pins; it outputs 1.8 V and accepts 3.3 V inputs only in overdrive mode. Add to the rails table: `+1V8`, secondary, from `+3V3` by an LDO, ≤ 30 mA, with ≥ 2 mA standing load (1 kΩ bleeder) to absorb up to 1.5 mA of overdrive-input leakage.
3. **PD status split** (changes "A → E: PD_TPL, PD_TPH, PD_BT and PD_PG into the FPGA"): `PD_PG` → FPGA (fast PoE-loss path with `POE_LOSS_N`); `PD_TPH_N`, `PD_TPL_N`, `PD_BT_N` → TCA9535 I2C expander P00–P02 (read after start-up; they are slow, and the FPGA's and MCU's pins are full). Isolator outputs at 3.3 V (block A's ISO7740 secondary side on `+3V3`).
4. **PHY management on the RP2350**: MDC, MDIO, nRST, nINT on RP2350 GPIO28–31 (not the FPGA). RMII data/clock stay on the FPGA. RXER is not connected (optional in RMII).
5. **Display signals pass through two SN74AVC4T774 (1.8 V → 3.3 V)** between FPGA bank 3 and the header. Block G's header, series resistors and GND/VCC jumpers are unchanged; two extra translated FPGA outputs are available for header positions 7/8 (R-20 pin-order remap).
6. **FPGA JTAG header (R-22) on the 3.3 V side** of the JTAG translator, shared with the RP2350's GPIO22–25, so standard 3.3 V probes work. The RP2350 tri-states those pins and enables the translator (`FPGA_JTAG_OE_N` low) while a probe is used.
7. **Gate-driver inputs need strong pull-downs** (block D): during FPGA power-up and every (re)configuration all FPGA user pins sit Hi-Z **with a weak pull-up of 30–150 µA** (UG290 App. A, DS117 Tab 3-8). Every PWM and enable input must be held below the driver's VIL by an external pull-down: R ≤ VIL / 150 µA (≤ 4.7 kΩ for VIL ≥ 0.7 V; 2.2 kΩ recommended). Same for anything else the FPGA drives that must default off.
8. **Audio clock: VCXO (24.576 MHz, SCTF SX3V, C5179997), FPGA-trimmed**, not fixed XO + resampler (R-55's open choice). Block F: clock the 1-bit DAC reclock flip-flop (and optionally the ext-mic ADC MCLK) **directly from the VCXO** through its own 33 Ω branch, not from an FPGA pin; the FPGA's `DAC_*` data are synchronous to the same clock.
9. **Link: 8-bit parallel PIO bus**, 12 RP2350 GPIO, 37.5 MHz, 37.5 MB/s (`E-link.md`).
10. **RP2350 ADC allocation**: ADC0–3 knobs (R-17), ADC4–7 NTCs for block D (GaN ×2, inductors ×2). ADC_AVDD from `+3V3` or a filtered reference (R-17 "clean reference" — block G/C decide).
11. **Slow status and enables on a TCA9535 I2C expander** (internal I2C1, 0x20, INT → RP2350 GPIO32, `E-ioexp-tca9535.md`): PD class bits, PG_5V, PG_3V3, LED_EN, QWIIC_PWR_EN, LED_FAULT_N, QWIIC_FAULT_N (block C/G) and HP_EN, LO_EN, HP_FAULT_N, HP_DET (block F). The expander pins are Hi-Z at power-on with no internal pull, so **every enable on it needs a 100 kΩ pull-down at its destination**. `VDRV_EN` (GPIO36) and `VDRV_PG` (GPIO33) stay direct.
12. **Block F's 4-tap FIR DAC (8 data pins) fits** on FPGA pins 17–20 and 48–51. That uses up the FPGA's spare pins, leaving 2 (+ `CLK_AUX`). Block D's single-input PWM mode would give 4 back.

## Rail loads from block E (for block C)

| Rail | Consumer | Typical | Design (worst) | Source of figure |
|---|---|---|---|---|
| **`+3V3`** | RP2350 (VREG_VIN, IOVDD, USB/OTP, ADC, VREG_AVDD) | 45 mA | 100 mA | RP2350 Tab 1446; 200 mA × 1.1 V / (3.3 V × 0.8) |
| | W25Q128JV | 10 mA | 25 mA | W25Q §9.5 ICC3–7 |
| | LAN8720AI incl. magnetics centre-tap current | 91 mA | 150 mA (10BASE-T) | LAN8720A Tab 5-1 + Note 5-7 |
| | FPGA VCCX/VCCIO0, VCCIO1, VCCIO2 | 20 mA | 40 mA | DS117 Tab 3-9 + switching estimate |
| | 50 MHz XO | 8 mA | 12 mA | YSO110TR current table |
| | VCXO | 6 mA | 10 mA | SX3V spec |
| | 3 × SN74AVC4T774 (B/A 3.3 V sides), TCA9535, pull-ups, LEDs of PHY | 3 mA | 7 mA | |
| | **Total `+3V3`, block E** | **≈ 185 mA** | **≈ 345 mA → budget 350 mA** | |
| **`+1V2`** | FPGA VCC (core, PLLs) | ≈ 100 mA (estimate) | **250 mA** (block C budgets 300 mA: agreed) | DS117 static 3.5 mA + dynamic estimate; measure on a Tang Nano 9K |
| **`+1V8`** (new) | FPGA VCCIO3 + embedded PSRAM (kept in deep power-down) + JTAG/display translator A/B 1.8 V sides + 1 kΩ bleeder | ≈ 10 mA | **30 mA** | |
| `+1V1` | RP2350 DVDD | internal regulator | — | |

Power from block E: ≈ 0.75 W typical, ≈ 1.5 W worst — inside R-33a's 2.5 W logic allowance.
**Block C's TLV62569 (2 A) with a 1 A peak assumption** covers block E's 350 mA plus the Qwiic port's ~0.4 A limit and the display's 40 mA (≈ 0.8 A); R-33a's 600 mA line should be updated to match. On VCC filtering (block C's question): the QN88P has no separate PLL supply pin, so the PLL runs from VCC. The FPGA side therefore takes the BLM18PG221 bead + 10 µF ∥ 4.7 µF at the VCC entry (`E-fpga-passives.md`), with 100 nF at each VCC pin.

### Requirements on the rails (from the datasheets)

| Rail | Requirement | Source |
|---|---|---|
| `+1V2` | 1.14–1.26 V at the FPGA pins after the BLM18PG221 bead (≤ 25 mV drop); ripple ≤ 3 % (36 mV p-p) — ask for ≤ 10 mV p-p, VCC ripple feeds PLL jitter and so PWM edge jitter; **ramp 0.6–6 mV/µs (0 → 1.2 V in 0.2–2 ms), monotonic** | DS117 §3.1.2 note, Tab 3-3 |
| `+3V3` (as FPGA VCCX) | 2.375–3.6 V, ramp 0.6–10 mV/µs (0.33–5.5 ms), monotonic; VCCX ≥ every VCCIO; ≤ 3.6 V incl. overshoot (LAN8720A abs max 3.6 V) | DS117 Tab 3-2/3-3, UG803, LAN8720A §5.1 |
| `+1V8` | 1.71–1.89 V (PSRAM); ripple ≤ 5 %; ramp 0.1–10 mV/µs; monotonic; ≥ 2 mA minimum load | UG803, DS117 Tab 3-3 |
| all | in range before FPGA configuration starts; internal-flash read needs VCC ≥ 1.08 V and VCCX ≥ 1.62 V at POR + 0.5–1 ms | DS117 §3.1.3, UG284 |
| `+3V3` vs PHY | all PHY supplies up within 50 ms of each other (single rail: met) | LAN8720A Tab 5-7 |
| USB-only mode (R-23) | `+3V3`, `+1V2`, `+1V8` all come up on USB power (FPGA and PHY run) | intent R-23 |

## Signals to/from other blocks

| Block | Net(s) | Direction | Level / timing | Agreed here |
|---|---|---|---|---|
| A | `PD_PG` | A → FPGA pin 11 | 3.3 V CMOS from isolator, 4.7 kΩ series | yes (change 3) |
| A | `PD_TPH_N`, `PD_TPL_N`, `PD_BT_N` | A → TCA9535 P00–P02 | 3.3 V, active low | yes (change 3, 11) |
| A | MDI pairs TX±, RX± | PHY ↔ RJ45 magnetics | 100 Ω diff; PHY-side centre taps to the PHY's filtered `+3V3` (`E-phy-passives.md`); Bob Smith 75 Ω + 1000 pF/3 kV on the line side are block A's | block A to confirm its RJ45 PHY-side pins and LEDs |
| B/C | `POE_LOSS_N` | → FPGA pin 13 | 3.3 V, active low, 4.7 kΩ series | yes |
| C | `PG_5V`, `PG_3V3` | C → TCA9535 P03, P04 | 3.3 V logic (PG_5V divided from the 5 V buck output, so it reads low when the buck is unpowered) | yes (block C's proposal) |
| C | `VDRV_PG` | C → RP2350 GPIO33 | 3.3 V | yes |
| C/G | `LED_EN`, `QWIIC_PWR_EN` | TCA9535 P10, P11 → TPS2553 EN | 3.3 V push-pull once set; **100 kΩ pull-down at EN** (expander is Hi-Z at power-on) | yes |
| C/G | `LED_FAULT_N`, `QWIIC_FAULT_N` | → TCA9535 P06, P07 | open-drain, 10 kΩ pull-up (fit once) | yes |
| C | `VDRV_EN` | RP2350 GPIO36 → C | 3.3 V, 100 kΩ pull-down = off (block C's) | yes |
| D | `PWM_W_AH/AL/BH/BL`, `PWM_T_AH/AL/BH/BL` | FPGA → drivers | LVCMOS33, 8 mA, OSER10; ≥ 10 ns min pulse; pull-downs at driver (change 7) | yes |
| D | `OC_TRIP_W_N`, `OC_TRIP_T_N` | D → FPGA 29, 38 | 3.3 V, active low; the FPGA turns all PWM outputs off through a combinational path (pin → LUT → output reset/disable, no clock in the path; DS117 pin–LUT–pin 4.2 ns typ) and latches the fault; the drivers' pull-downs (change 7) hold the gates off if the pins are tri-stated. FPGA share of R-54's 200 ns ≈ 10 ns; exact primitive (OSER RESET vs IOB tristate) chosen in RTL and checked in simulation | yes |
| D | `AMP_EN_W`, `AMP_EN_T` | FPGA → D | 3.3 V; pull-down = off | assumed — block D confirms |
| D | `ADC_SCLK/MOSI/MISO/CS0_N/CS1_N/CS2_N` | FPGA ↔ D ADCs | 3.3 V SPI, SCLK ≤ 50 MHz (bank-2 LVCMOS33) | yes; block D picks the ADCs |
| D | `NTC_*` ×4 | D → RP2350 ADC4–7 | 0–3.3 V | yes |
| F | `DAC_L0–3`, `DAC_R0–3` | FPGA 17–20, 48–51 → reclock FFs | 3.3 V; launched on MCLK↓, clock insertion + tco ≤ 6.4 ns (≤ 12 ns asked) | yes |
| F | VCXO 24.576 MHz → `MCLK_Q` buffer (block F) → 8 FFs + PCM1808 SCKI | E → F | 3.3 V CMOS, own branch, 33 Ω at source; **phase noise vs ≤ 1 ps (20 k–12 MHz) not verifiable from the SX3V datasheet** — see `E-clk-audio-vcxo.md` | open, needs a lead decision |
| F | `PDM_CLK` (out, pin 77, 3.072 MHz) / `PDM_DAT` (in, pin 14, 1 kΩ series, no pull) | | 3.3 V | yes |
| F | `MADC_BCK` (out, pin 62), `MADC_LRCK` (out, pin 3 via display translator ch 7), `MADC_DOUT` (in, pin 15, 1 kΩ) — PCM1808 slave, SCKI from MCLK_Q | | 3.3 V | yes |
| F | `HP_EN`, `LO_EN` (out), `HP_FAULT_N`, `HP_DET` (in) | TCA9535 P12–P15 | 3.3 V; enables need pull-downs; fault latency < 0.2 ms, hardware current limit is block F's | yes |
| G | `I2C1_SDA/SCL`, `LED_DATA/CLK`, `ENC1_A/B`, `ENC2_A/B`, `KNOB1–4`, `UART0_TX/RX`, `SWCLK/SWDIO/RUN`, `USB_DP/DM` (after 27 Ω) | RP2350 | 3.3 V | yes |
| G | `VUSB_DET` | → TCA9535 P16 | ≤ 3.3 V divider | yes |
| G | display B-side outputs ×8 (6 + 2 spare) | translators → header | 3.3 V | yes (change 5) |
| G | FPGA JTAG header (TCK, TMS, TDI, TDO, 3V3, GND) | translator A side | 3.3 V | yes (change 6) |
| G | `PTP_PPS` | FPGA 60 → test point | 3.3 V | yes |

## Things needing a user decision

- **MCLK_Q jitter (block F):** the VCXO's phase noise is unspecified, so block F's ≤ 1 ps (20 k–12 MHz) can't be verified on paper. Options are in `E-clk-audio-vcxo.md`: fit the VCXO and measure, with a fallback land for a 0.7 ps fixed XO (which loses the PTP lock of the DAC clock). This needs a lead/user decision.
- Otherwise none blocking. The configuration-scheme change (1) and the new `+1V8` rail (2) are forced by the only stocked FPGA; they need sign-off in `decisions.md` by the lead.
