> **SUPERSEDED by ECP5 (user, 2026-11-07).** The FPGA is now the Lattice LFE5U-25F-7BG256I; see `E-fpga-ecp5.md`, `E-pinmap.md`, `E-interfaces.md`. Kept for the record; do not build from this file.

# Block E pin budget — GW1NR-LV9QN88PC6/I5 (QN88P) and RP2350B (QFN-80)

Sources: `datasheets/gowin-UG803E.pdf` (QN88P column of the pin list, checked pin by pin), `datasheets/gowin-UG119E.pdf` Tab 2-6 / 3-8 (bank counts, power pins), `datasheets/gowin-UG290E.pdf` App. A (pin states), `datasheets/rp2350-lcsc.pdf` Fig 3 (QFN-80 pinout) and Tab 3 (GPIO functions). Interfaces from `design/architecture.md`; changes proposed in `E-interfaces.md`.

Conventions: `_N` = active low. "OD in" = 3.3 V input on a 1.8 V bank-3 pin in `LVCMOS33OD18` mode (series R per `E-fpga-passives.md`). Bank 1 and 2 are LVCMOS33. Pin numbers are package pins.

## FPGA — QN88P, all 88 pins + EPAD

| Pin | Pad (UG803) | Bank | Net | Dir | Notes |
|---|---|---|---|---|---|
| 1 | VCC | — | `+1V2` (after bead) | P | 100 nF |
| 2 | VSS | — | GND | P | |
| 3 | IOT2A | 3 | `MADC_LRCK_1V8` → translator ch 7 → `MADC_LRCK` | out | PCM1808 LRCK 48 kHz (block F), via display translator part 2 |
| 4 | IOL5A/JTAGSEL_N/LPLL_T_in | 3 | `FPGA_JTAGSEL_N` | in | 4.7 kΩ to `+1V8`; JTAG stays dedicated |
| 5 | IOL11A/TMS | 3 | `FPGA_TMS_1V8` | in | from translator B2 |
| 6 | IOL11B/TCK | 3 | `FPGA_TCK_1V8` | in | 4.7 kΩ pull-down; translator B1 |
| 7 | IOL12B/TDI | 3 | `FPGA_TDI_1V8` | in | translator B3 |
| 8 | IOL13A/TDO | 3 | `FPGA_TDO_1V8` | out | translator B4 |
| 9 | IOL13B/RECONFIG_N | 3 | `FPGA_RECONFIG_N` | in | 4.7 kΩ to `+1V8`; RP2350 GPIO26 open-drain |
| 10 | IOL15A/GCLKT_6 | 3 | `LINK_CLK` | OD in | 100 Ω series; global clock pin |
| 11 | IOL16B | 3 | `PD_PG` | OD in | 4.7 kΩ series; from block A isolator |
| 12 | VCCIO3 | — | `+1V8` | P | 100 nF + 4.7 µF |
| 13 | IOL21B | 3 | `POE_LOSS_N` | OD in | 4.7 kΩ series; block B/C fast comparator |
| 14 | IOL22B | 3 | `PDM_DAT` | OD in | 1 kΩ series, no pull (block F MEMS mic) |
| 15 | IOL25B | 3 | `MADC_DOUT` | OD in | 1 kΩ series; PCM1808 DOUT (block F) |
| 16 | IOL26B | 3 | `SPARE_B3_B` → display translator ch 8 | out 1.8 V | spare 3.3 V output via translator |
| 17 | IOB2A | 2 | `DAC_L0` | out | 1-bit DAC L, FIR tap 0 → reclock FFs (block F); launched on MCLK↓ |
| 18 | IOB2B | 2 | `DAC_L1` | out | tap 1 |
| 19 | IOB4A | 2 | `DAC_L2` | out | tap 2 |
| 20 | IOB4B | 2 | `DAC_L3` | out | tap 3 |
| 21 | VSS | — | GND | P | |
| 22 | VCC | — | `+1V2` | P | 100 nF |
| 23 | VCCIO2 | — | `+3V3` | P | 100 nF |
| 24 | VSS | — | GND | P | |
| 25 | IOB8A | 2 | `PWM_W_AH` | out | OSER10; woofer leg A high input (block D) |
| 26 | IOB8B | 2 | `PWM_W_AL` | out | woofer leg A low |
| 27 | IOB11A | 2 | `PWM_W_BH` | out | woofer leg B high |
| 28 | IOB11B | 2 | `PWM_W_BL` | out | woofer leg B low |
| 29 | IOB13A | 2 | `OC_TRIP_W_N` | in | block D comparator, woofer |
| 30 | IOB13B | 2 | `AMP_EN_W` | out | block D driver enable (if LMG1210 EN used), pull-down at driver |
| 31 | IOB15A | 2 | `ADC_CS0_N` | out | sense ADC #0 (block D) |
| 32 | IOB15B | 2 | `ADC_CS1_N` | out | sense ADC #1 |
| 33 | IOB23A | 2 | `ADC_SCLK` | out | shared SPI to block D ADCs |
| 34 | IOB23B | 2 | `ADC_MOSI` | out | |
| 35 | IOB29A/GCLKT_4 | 2 | `CLK_AUX` | in | **spare global-clock input**: option to clock OSER from an external low-jitter source (`E-clk-audio-vcxo.md`) |
| 36 | IOB29B/GCLKC_4 | 2 | `ADC_MISO` | in | (GCLKC unused as clock when 35 is single-ended) |
| 37 | IOB31A | 2 | `ADC_CS2_N` | out | VBUS ADC (block D) |
| 38 | IOB31B | 2 | `OC_TRIP_T_N` | in | block D comparator, tweeter |
| 39 | IOB33A | 2 | `PWM_T_AH` | out | tweeter leg A high |
| 40 | IOB33B | 2 | `PWM_T_AL` | out | tweeter leg A low |
| 41 | IOB41A | 2 | `PWM_T_BH` | out | tweeter leg B high |
| 42 | IOB41B | 2 | `PWM_T_BL` | out | tweeter leg B low |
| 43 | VSS | — | GND | P | |
| 44 | VCCIO2 | — | `+3V3` | P | 100 nF |
| 45 | VCC | — | `+1V2` | P | 100 nF |
| 46 | VSS | — | GND | P | |
| 47 | IOB43B | 2 | `AMP_EN_T` | out | tweeter driver enable |
| 48 | IOR24B | 1 | `DAC_R0` | out | 1-bit DAC R, tap 0 |
| 49 | IOR24A | 1 | `DAC_R1` | out | tap 1 |
| 50 | IOR22B | 1 | `DAC_R2` | out | tap 2 |
| 51 | IOR17B/GCLKC_3 | 1 | `DAC_R3` | out | tap 3 (GCLKC_3 used as plain I/O) |
| 52 | IOR17A/GCLKT_3 | 1 | `RMII_REFCLK` | in | 50 MHz from the XO, ≤ 25 mm |
| 53 | IOR15B/DOUT/WE_N | 1 | `RMII_TXEN` | out | internal pull-down during config + 2.2 kΩ ext |
| 54 | IOR15A/DIN/CLKHOLD_N | 1 | `RMII_TXD0` | out | |
| 55 | IOR14B/SSPI_CS_N/D0 | 1 | `RMII_TXD1` | out | `--sspi_as_gpio` |
| 56 | IOR14A/SO/D1 | 1 | `RMII_RXD0` | in | IODELAY ≈ 2 ns (hold) |
| 57 | IOR13A/FASTRD_N/D3 | 1 | `RMII_RXD1` | in | IODELAY |
| 58 | VCCIO1 | — | `+3V3` | P | 100 nF |
| 59 | IOR12B/MCLK/D4 | 1 | `RMII_CRSDV` | in | IODELAY; `--mspi_as_gpio` |
| 60 | IOR12A/MCS_N/D5 | 1 | `PTP_PPS` | out | to the PTP-second test point (R-55, R-80) |
| 61 | IOR11B/MO/D6 | 1 | `VCXO_TUNE` | out | ΔΣ → 2-pole RC → VCXO Vc |
| 62 | IOR11A/MI/D7 | 1 | `MADC_BCK` | out | PCM1808 BCK 3.072 MHz (slave mode) |
| 63 | IOR5A/RPLL_T_in | 1 | `VCXO_CLK` | in | 24.576 MHz → right rPLL (PWM FCLK 491.52 MHz) |
| 64 | VCCX/VCCIO0 | — | `+3V3` | P | 100 nF |
| 65 | VSS | — | GND | P | |
| 66 | VCC | — | `+1V2` | P | 100 nF |
| 67 | VCCX/VCCIO0 | — | `+3V3` | P | 100 nF |
| 68 | IOT42B | 1 | `LINK_IRQ` | out | to RP2350 GPIO19 |
| 69 | IOT42A | 1 | `LINK_D7` | io | |
| 70 | IOT41B | 1 | `LINK_D6` | io | |
| 71 | IOT41A | 1 | `LINK_D5` | io | |
| 72 | IOT39B | 1 | `LINK_D4` | io | |
| 73 | IOT39A | 1 | `LINK_D3` | io | |
| 74 | IOT38B | 1 | `LINK_D2` | io | |
| 75 | IOT38A | 1 | `LINK_D1` | io | |
| 76 | IOT37B | 1 | `LINK_D0` | io | |
| 77 | IOT37A | 1 | `PDM_CLK` | out | MEMS mic clock 3.072 MHz = MCLK/8 |
| 78 | VCCX/VCCIO0 | — | `+3V3` | P | 100 nF |
| 79 | IOT12B | 3 | `LINK_DIR` | OD in | 100 Ω series |
| 80 | IOT12A | 3 | `LINK_STB` | OD in | 100 Ω series |
| 81 | IOT11B | 3 | `DISP_SCL_1V8` | out | → translator → header |
| 82 | IOT11A | 3 | `DISP_SDA_1V8` | out | |
| 83 | IOT10B | 3 | `DISP_DC_1V8` | out | |
| 84 | IOT10A | 3 | `DISP_CS_1V8` | out | |
| 85 | IOT8B | 3 | `DISP_RES_1V8` | out | |
| 86 | IOT8A | 3 | `DISP_BLK_1V8` | out | backlight PWM |
| 87 | IOT6B/MODE1 | 3 | `FPGA_MODE1` | in | 1 kΩ to GND |
| 88 | IOT5A/MODE0 | 3 | `FPGA_MODE0` | in | 1 kΩ to GND (MODE = 000 AUTOBOOT; MODE2 internally GND) |
| EPAD | — | — | GND | P | via array |

### FPGA headroom

| Bank | User pins | Used | Spare |
|---|---|---|---|
| 1 (3.3 V) | 25 | 25 | 0 |
| 2 (3.3 V) | 23 | 22 | 1 (35 = GCLKT_4, reserved as `CLK_AUX`, usable as I/O) |
| 3 (1.8 V) | 15 + 8 config | 15 | 1 as a 3.3 V output via translator ch 8 (pin 16) |
| **Total** | **63 user + 8 config** | | **2** (+ `CLK_AUX`) |

Block F's 4-tap FIR DAC (8 data pins) uses the headroom. Ways to get pins back, in order:
- block D's LMG1210 single-input PWM mode frees 26, 28, 40, 42 → **+4**;
- block F's single-tap DAC frees 19, 20, 50, 51 (and keeps 17, 48) → **+4**, or more;
- slow outputs can always move to the I2C expander (`E-ioexp-tca9535.md`).
Block F's slow signals (`HP_EN`, `LO_EN`, `HP_FAULT_N`, `HP_DET`) are on the expander, not the FPGA.

Resource notes for the RTL: OSER10 on all 8 PWM pins (bank 2, any IO supports OSER10 on GW1N-9, UG289 §4); IODELAY on RMII RX (56, 57, 59); right rPLL fed from pin 63; left rPLL free (phase-compensated 50 MHz / 100 MHz timestamp clock).

## RP2350B — QFN-80, all 80 pins + EP

| Pin | Name | Net | Dir | Notes |
|---|---|---|---|---|
| 1 | GPIO4 | `LED_DATA` | out | PIO; block G 5 V level shifter (WS2812 data / APA102 data) |
| 2 | GPIO5 | `LED_CLK` | out | PIO; APA102/SK9822 clock |
| 3 | GPIO6 | `ENC1_A` | in | rotary encoder 1 (R-17), PIO quadrature |
| 4 | GPIO7 | `ENC1_B` | in | |
| 5 | IOVDD | `+3V3` | P | 100 nF |
| 6 | GPIO8 | `LINK_D0` | io | PIO link (`E-link.md`) |
| 7 | GPIO9 | `LINK_D1` | io | |
| 8 | GPIO10 | `LINK_D2` | io | |
| 9 | GPIO11 | `LINK_D3` | io | |
| 10 | DVDD | `+1V1` | P | 100 nF |
| 11 | GPIO12 | `LINK_D4` | io | |
| 12 | GPIO13 | `LINK_D5` | io | |
| 13 | GPIO14 | `LINK_D6` | io | |
| 14 | GPIO15 | `LINK_D7` | io | |
| 15 | IOVDD | `+3V3` | P | 100 nF |
| 16 | GPIO16 | `LINK_CLK` | out | PIO side-set, 37.5 MHz |
| 17 | GPIO17 | `LINK_DIR` | out | |
| 18 | GPIO18 | `LINK_STB` | out | |
| 19 | GPIO19 | `LINK_IRQ` | in | |
| 20 | GPIO20 | `ENC2_A` | in | rotary encoder 2 |
| 21 | GPIO21 | `ENC2_B` | in | |
| 22 | GPIO22 | `FPGA_TCK` | out | → SN74AVC4T774 A1 (+ JTAG header, block G) |
| 23 | GPIO23 | `FPGA_TMS` | out | → A2 |
| 24 | IOVDD | `+3V3` | P | 100 nF |
| 25 | GPIO24 | `FPGA_TDI` | out | → A3 |
| 26 | GPIO25 | `FPGA_TDO` | in | ← A4 |
| 27 | GPIO26 | `FPGA_RECONFIG_N` | od out | drive low only; node pulled to 1.8 V |
| 28 | GPIO27 | `FPGA_JTAG_OE_N` | out | translator OE, 10 kΩ pull-up to `+3V3` |
| 29 | IOVDD | `+3V3` | P | 100 nF |
| 30 | XIN | 12 MHz crystal | | `E-xtal-12mhz.md` |
| 31 | XOUT | 12 MHz crystal via 1 kΩ | | |
| 32 | DVDD | `+1V1` | P | 100 nF |
| 33 | SWCLK | `SWCLK` | in | Debug Probe header (R-21, block G) |
| 34 | SWDIO | `SWDIO` | io | |
| 35 | RUN | `RUN` | in | 10 kΩ pull-up, reset button / debug |
| 36 | GPIO28 | `PHY_MDC` | out | SMI, ≤ 2.5 MHz |
| 37 | GPIO29 | `PHY_MDIO` | io | 1.5 kΩ pull-up |
| 38 | GPIO30 | `PHY_NRST` | out | 10 kΩ pull-down |
| 39 | GPIO31 | `PHY_NINT` | in | 10 kΩ pull-up; optional (polling works) |
| 40 | GPIO32 | `EXP_INT_N` | in | TCA9535 INT (open-drain), 10 kΩ pull-up (`E-ioexp-tca9535.md`) |
| 41 | IOVDD | `+3V3` | P | 100 nF |
| 42 | GPIO33 | `VDRV_PG` | in | block C gate-drive supply power-good (direct: gates amp start) |
| 43 | GPIO34 | `SPARE_MCU_A` | io | spare (was PD_BT_N, now on the expander) |
| 44 | GPIO35 | `SPARE_MCU_B` | io | spare (status moved to the expander) |
| 45 | GPIO36 | `VDRV_EN` | out | block C gate-drive supply enable (pull-down = off) |
| 46 | GPIO37 | `SPARE_MCU_C` | io | spare (LED enable moved to the expander) |
| 47 | GPIO38 | `SPARE_MCU_D` | io | spare (VUSB_DET moved to the expander) |
| 48 | GPIO39 | `SPARE_MCU` | io | **spare** |
| 49 | GPIO40/ADC0 | `KNOB1` | ain | R-17 knob header, RC filtered (block G) |
| 50 | IOVDD | `+3V3` | P | 100 nF |
| 51 | DVDD | `+1V1` | P | 100 nF + 4.7 µF (second DVDD cap rule) |
| 52 | GPIO41/ADC1 | `KNOB2` | ain | |
| 53 | GPIO42/ADC2 | `KNOB3` | ain | |
| 54 | GPIO43/ADC3 | `KNOB4` | ain | |
| 55 | GPIO44/ADC4 | `NTC_GAN_W` | ain | block D: GaN temperature, woofer |
| 56 | GPIO45/ADC5 | `NTC_GAN_T` | ain | tweeter |
| 57 | GPIO46/ADC6 | `NTC_IND_W` | ain | output inductor, woofer |
| 58 | GPIO47/ADC7 | `NTC_IND_T` | ain | output inductor, tweeter |
| 59 | ADC_AVDD | `+3V3` (or filtered ref, block G/C) | P | 100 nF |
| 60 | IOVDD | `+3V3` | P | 100 nF |
| 61 | VREG_AVDD | `+3V3` via 33 Ω / 4.7 µF | P | |
| 62 | VREG_PGND | GND (two vias, one point) | P | |
| 63 | VREG_LX | L1 | P | |
| 64 | VREG_VIN | `+3V3` | P | C6 4.7 µF |
| 65 | VREG_FB | `+1V1` at COUT | | |
| 66 | USB_DM | 27 Ω → USB-C D− | io | block G |
| 67 | USB_DP | 27 Ω → USB-C D+ | io | |
| 68 | USB_OTP_VDD | `+3V3` | P | 100 nF shared with 69 |
| 69 | QSPI_IOVDD | `+3V3` | P | |
| 70 | QSPI_SD3 | flash IO3 (/HOLD) | io | |
| 71 | QSPI_SCLK | flash CLK | out | |
| 72 | QSPI_SD0 | flash DI/IO0 | io | |
| 73 | QSPI_SD2 | flash IO2 (/WP) | io | |
| 74 | QSPI_SD1 | flash DO/IO1 | io | |
| 75 | QSPI_SS | flash /CS; BOOTSEL via 1 kΩ | out | |
| 76 | IOVDD | `+3V3` | P | 100 nF |
| 77 | GPIO0 | `UART0_TX` | out | Debug Probe UART (R-21) |
| 78 | GPIO1 | `UART0_RX` | in | |
| 79 | GPIO2 | `I2C1_SDA` | io | internal I2C → Qwiic buffer (block G) |
| 80 | GPIO3 | `I2C1_SCL` | io | |
| EP | GND | GND | P | |

### RP2350 headroom

48 GPIO: 43 used, **5 spare** (GPIO34, 35, 37, 38, 39) after moving slow status/enables to a TCA9535 16-bit I2C expander on the internal I2C1 bus (address 0x20). Soft spares: GPIO31 (`PHY_NINT`), GPIO27 (`FPGA_JTAG_OE_N`).

### I2C expander TCA9535 (internal I2C1, 0x20) — `E-ioexp-tca9535.md`

| Port | Net | Dir | Block | Default at power-up (expander pins are inputs, no internal pull) |
|---|---|---|---|---|
| P00 | `PD_TPH_N` | in | A | isolator drives |
| P01 | `PD_TPL_N` | in | A | |
| P02 | `PD_BT_N` | in | A | |
| P03 | `PG_5V` | in | C | |
| P04 | `PG_3V3` | in | C | |
| P05 | `VDRV_PG_EXP` | in | C | copy of `VDRV_PG` for logging; may be left as spare |
| P06 | `LED_FAULT_N` | in | C/G | open-drain, 10 kΩ pull-up |
| P07 | `QWIIC_FAULT_N` | in | C/G | open-drain, 10 kΩ pull-up |
| P10 | `LED_EN` | out | C/G | **100 kΩ pull-down at the TPS2553 EN → off** |
| P11 | `QWIIC_PWR_EN` | out | C/G | 100 kΩ pull-down → off |
| P12 | `HP_EN` | out | F | pull-down → off (block F) |
| P13 | `LO_EN` | out | F | pull-down → off |
| P14 | `HP_FAULT_N` | in | F | open-drain, 10 kΩ pull-up |
| P15 | `HP_DET` | in | F | jack switch |
| P16 | `VUSB_DET` | in | G | divider from VUSB |
| P17 | `SPARE_EXP` | — | — | 100 kΩ pull-down (unused inputs must not float) |

## Cross-check of interface counts (brief from team lead → assigned)

| Interface | Needed | Where |
|---|---|---|
| Block D PWM | 8 (4 in single-PWM mode) | FPGA 25–28, 39–42 |
| Block D OC trip | 2 | FPGA 29, 38 |
| Block D SPI ADC (VBUS + sense) | SCLK, MOSI, MISO, 3 × CS | FPGA 31–34, 36, 37 |
| Block D driver enables | 2 (assumed) | FPGA 30, 47 |
| Block D NTCs | 4 analog | RP2350 ADC4–7 |
| Block F 1-bit FIR DAC, 2 ch × 4 taps | 8 | FPGA 17–20 (L), 48–51 (R); MCLK_Q straight from the VCXO, not an FPGA pin |
| Block F MEMS PDM | CLK, DATA | FPGA 77, 14 |
| Block F ext-mic ADC PCM1808 (slave) | BCK, LRCK, DOUT (SCKI from the VCXO) | FPGA 62, 3 (via translator), 15 |
| Block F HP_EN, LO_EN, HP_FAULT_N, HP_DET | 4 slow | TCA9535 P12–P15 |
| Block G I2C | 2 | RP2350 GPIO2/3 |
| Block G LED data + clock | 2 | RP2350 GPIO4/5 |
| I2C expander interrupt | 1 | RP2350 GPIO32 |
| Block G display (SCL, SDA, RES, DC, CS, BLK) | 6 on FPGA | FPGA 81–86 → translators |
| Block G knobs (4 ADC) + encoders (4 GPIO) | 8 | RP2350 ADC0–3, GPIO6/7/20/21 |
| Block G SWD, UART, USB | 2 + 2 + 2 | RP2350 SWCLK/SWDIO, GPIO0/1, USB_DP/DM |
| Block G FPGA JTAG header | 4 | translator A side (shared with RP2350 GPIO22–25) |
| Block A PD status | 4 | `PD_PG` → FPGA 11; `PD_TPH_N/TPL_N/BT_N` → TCA9535 P00–P02 |
| Block B/C PoE-loss comparator | 1 | FPGA 13 |
| PHY RMII + SMI | 7 + 4 | FPGA 52–57, 59; RP2350 GPIO28–31 |
| PTP-second test point | 1 | FPGA 60 |
| VCXO clock + tune | 2 | FPGA 63, 61 |
| RP2350 ↔ FPGA link | 12 | RP2350 GPIO8–19 ↔ FPGA 68–76, 10, 79, 80 |
| FPGA configuration | 5 | RP2350 GPIO22–27 (via translator / open-drain) |
| Block C rails/power control | VDRV_EN, VDRV_PG direct; PG_5V, PG_3V3, LED_EN, QWIIC_PWR_EN, LED_FAULT_N, QWIIC_FAULT_N on the expander | RP2350 GPIO36, GPIO33; TCA9535 P03–P11 |
