# Block E pin budget — ECP5 LFE5U-25F-7BG256I (caBGA-256) and RP2350B (QFN-80)

ECP5 version (user, 2026-11-07). The GW1NR-9 version is kept in `E-pinmap-gowin.md` (superseded).
Sources: `datasheets/lattice-ECP5U-25-pinout.csv` (CABGA256 column: ball, pad, bank, dual function, differential pair), `datasheets/lattice-FPGA-TN-02039.pdf` (sysCONFIG pins), `datasheets/lattice-FPGA-DS-02012.pdf` (DDR gearing sides, hot socketing), `datasheets/rp2350-lcsc.pdf` Fig 3 / Tab 3. The FPGA table below was generated and checked by script against the CSV: every ball exists, none is used twice, no net is duplicated, and every "partner NC" ball is the true differential partner and is unused.

All seven FPGA banks run at **VCCIO = 3.3 V**, so there is no level translation anywhere in block E.

## Floorplan this pin-out assumes

- **Left (banks 7, 6):** power stage (block D). The PWM needs ODDRX2F, which exists only on left/right banks. The VCXO enters the lower-left PLL (P6).
- **Top (banks 0, 1):** PHY/RJ45 (block A) and the isolated PD status. Top/bottom banks tolerate hot socketing, so always-driven inputs go here.
- **Right (banks 2, 3):** audio (block F) and display/LED/Qwiic (block G).
- **Bottom (bank 8):** configuration. The RP2350 and its flash sit below the FPGA, with the link and SSPI as short traces.

## FPGA signal assignments (108 balls incl. configuration/JTAG)

Rules (see `E-fpga-ecp5.md`): always-driven inputs on left/right banks have their differential pair partner left **NC** and a series resistor; outputs default to tri-state + weak pull-down until configured.

| Ball | Pad / dual function | Bank | Net | Dir | Block | Notes |
|---|---|---|---|---|---|---|
| A2 | PT4A | 0 | `PD_PG` | in | A | isolator, 1 kΩ series |
| A3 | PT6A | 0 | `PD_TPH_N` | in | A | 1 kΩ series |
| A4 | PT6B | 0 | `PD_TPL_N` | in | A | 1 kΩ series |
| A5 | PT18A | 0 | `PD_BT_N` | in | A | 1 kΩ series |
| A6 | PT18B | 0 | `POE_LOSS_N` | in | B/C | 1 kΩ series |
| B3 | PT4B | 0 | `PG_5V` | in | C | divided from +5V_BUCK to 3.24 V (not open-drain) |
| B4 | PT11B | 0 | `PG_3V3` | in | C | block C 100 kΩ pull-up already fitted |
| B5 | PT15B | 0 | `PG_3V3Q` | in | C/F | TPS7A94 PG, open-drain, block C 100 kΩ pull-up; 1 kΩ series; gateware holds DAC_* low until high |
| A10 | PT42B | 1 | `RMII_TXD0` | out | E |  |
| A11 | PT53A | 1 | `RMII_RXD0` | in | E | input delay (DELAYG) |
| A12 | PT53B | 1 | `RMII_RXD1` | in | E | input delay |
| A13 | PT65A | 1 | `PHY_MDC` | out | E |  |
| A14 | PT65B | 1 | `PHY_MDIO` | io | E | 1.5 kΩ pull-up |
| A9 | PT42A | 1 | `RMII_TXEN` | out | E | 10 kΩ pull-down |
| B10 | PT44A | 1 | `RMII_TXD1` | out | E |  |
| B11 | PT49A | 1 | `RMII_CRSDV` | in | E | input delay |
| B12 | PT56A | 1 | `PHY_NRST` | out | E | 10 kΩ pull-down |
| B13 | PT60A | 1 | `PHY_NINT` | in | E | 10 kΩ pull-up |
| C8 | PT35A/PCLKT1_0 | 1 | `RMII_REFCLK` | in | E | PCLKT1_0, 50 MHz |
| B16 | PR2A | 2 | `DISP_SCL` | out | G | series R at header |
| C14 | PR2C | 2 | `QWIIC_FAULT_N` | in | C/G | open-drain; 1 kΩ series, partner D14 NC |
| C15 | PR5B | 2 | `DISP_RES` | out | G |  |
| C16 | PR5A | 2 | `DISP_SDA` | out | G |  |
| D16 | PR8A | 2 | `DISP_DC` | out | G |  |
| E14 | PR5C | 2 | `VUSB_DET` | in | G | 1 kΩ series, partner F14 NC |
| E15 | PR8B | 2 | `DISP_CS` | out | G |  |
| E16 | PR11D | 2 | `DISP_BLK` | out | G |  |
| F15 | PR11C | 2 | `DISP_AUX7` | out | G | header position 7 (pin-order remap) |
| F16 | PR14A | 2 | `DISP_AUX8` | out | G | header position 8 |
| G15 | PR14B | 2 | `DISP_BL_PWM` | out | G | backlight FET switch gate (2N7002, 100 kΩ pull-down at G); 4 mA drive, PWM ≤ 2 kHz, default low |
| G16 | PR20A/GR_PCLK2_1 | 2 | `PTP_PPS` | out | G | PTP-second test point |
| H15 | PR20B | 2 | `LED_EN` | out | C/G | 100 kΩ pull-down at EN |
| J16 | PR23A/PCLKT2_1 | 2 | `QWIIC_PWR_EN` | out | C/G | 100 kΩ pull-down at EN |
| K16 | PR23C/PCLKT2_0 | 2 | `LED_FAULT_N` | in | C/G | open-drain, 10 kΩ pull-up; 1 kΩ series, partner K15 NC |
| K13 | PR29A/GR_PCLK3_0 | 3 | `HP_DET` | in | F | always driven: 1 kΩ series, partner K12 NC |
| L14 | PR32C | 3 | `PDM_CLK` | out | F | 3.072 MHz |
| L16 | PR26A/PCLKT3_1 | 3 | `MADC_DOUT` | in | F | always driven: 330 Ω series, partner L15 NC |
| M14 | PR32D | 3 | `HP_EN` | out | F | pull-down at block F |
| M16 | PR26C/PCLKT3_0 | 3 | `LINK_CLK` | in | E | PCLKT3_0 |
| N13 | PR38A | 3 | `PDM_DAT` | in | F | always driven: 330 Ω series, partner P14 NC |
| N14 | PR35D | 3 | `LO_EN` | out | F | pull-down at block F |
| N16 | PR32A | 3 | `DAC_L0` | out | F |  |
| P11 | PR47C/LRC_GPLL0T_IN | 3 | `HP_FAULT_N` | in | F | always driven: 1 kΩ series, partner P12 NC |
| P13 | PR41A | 3 | `MADC_BCK` | out | F | PCM1808 BCK 3.072 MHz |
| P15 | PR32B | 3 | `DAC_L1` | out | F |  |
| P16 | PR35A | 3 | `DAC_L2` | out | F |  |
| R12 | PR44A | 3 | `DAC_R2` | out | F |  |
| R13 | PR41C | 3 | `DAC_R0` | out | F |  |
| R14 | PR41B | 3 | `MADC_LRCK` | out | F | 48 kHz |
| R15 | PR38C | 3 | `LINK_DIR` | in | E |  |
| R16 | PR35B/VREF1_3 | 3 | `DAC_L3` | out | F |  |
| T13 | PR44B | 3 | `DAC_R3` | out | F |  |
| T14 | PR41D | 3 | `DAC_R1` | out | F |  |
| T15 | PR38D | 3 | `LINK_STB` | in | E |  |
| M10 | TDO | 40 | `FPGA_TDO` | out | G | 4.7 kΩ pull-up |
| R11 | TDI | 40 | `FPGA_TDI` | in | G | 4.7 kΩ pull-up |
| T10 | TCK | 40 | `FPGA_TCK` | in | G | JTAG header; 4.7 kΩ pull-down |
| T11 | TMS | 40 | `FPGA_TMS` | in | G | 4.7 kΩ pull-up |
| K4 | PL29A/GR_PCLK6_0 | 6 | `PF_CS_n` | out | D | reserved, optional 2 × ADS8353 (R-51); 4.7 kΩ pull-up |
| K5 | PL29B | 6 | `PF_SDI` | out | D | reserved |
| L1 | PL26A/PCLKT6_1 | 6 | `FAULT_W_n` | in | D | always driven: 330 Ω series, partner L2 NC |
| L3 | PL32C | 6 | `IS_CS_n` | out | D | ADS7038-Q1; 4.7 kΩ pull-up |
| L4 | PL29C/GR_PCLK6_1 | 6 | `PF_SCLK` | out | D | reserved |
| L5 | PL29D | 6 | `PF_SDO_WA` | in | D | reserved |
| M1 | PL26C/PCLKT6_0 | 6 | `FAULT_T_n` | in | D | always driven: 330 Ω series, partner M2 NC |
| M3 | PL32D | 6 | `IS_SCLK` | out | D | ≤ 60 MHz |
| M4 | PL35C | 6 | `VB_SDO` | in | D | partner N3 is an FPGA output |
| M5 | PL44C | 6 | `PF_SDO_WB` | in | D | reserved |
| N1 | PL32A | 6 | `PWM_W_A` | out | D | ODDRX2F; LMG1210 PWM mode, high = HS on; matched routing, 100 Ω at driver |
| N3 | PL35D | 6 | `VB_SCLK` | out | D | ≤ 16 MHz |
| N4 | PL38A | 6 | `VCXO_TUNE` | out | E | ΔΣ → 2-pole RC → VCXO Vc |
| N5 | PL44D | 6 | `PF_SDO_TA` | in | D | reserved |
| N6 | PL47B | 6 | `PF_SDO_TB` | in | D | reserved |
| P1 | PL35A | 6 | `PWM_W_B` | out | D | ODDRX2F |
| P2 | PL32B | 6 | `AMP_CLK_W` | out | D | fault-latch clock |
| P3 | PL38B | 6 | `IS_SDO` | in | D | partner N4 is an FPGA output |
| P6 | PL47C/LLC_GPLL0T_IN | 6 | `VCXO_CLK` | in | E | LLC_GPLL0T_IN: PWM/audio PLL reference; partner P5 left NC |
| R1 | PL35B/VREF1_6 | 6 | `AMP_ARM` | out | D | block D 10 kΩ pull-down |
| R2 | PL38C | 6 | `PWM_T_A` | out | D | ODDRX2F |
| R3 | PL41B | 6 | `IS_SDI` | out | D |  |
| R4 | PL41C | 6 | `PWM_T_B` | out | D | ODDRX2F |
| R5 | PL44A | 6 | `AMP_EN_W` | out | D | fault-latch D input |
| T2 | PL38D | 6 | `AMP_CLK_T` | out | D | fault-latch clock |
| T3 | PL41D | 6 | `VB_CS_n` | out | D | ADS7042; 4.7 kΩ pull-up |
| T4 | PL44B | 6 | `AMP_EN_T` | out | D | fault-latch D input |
| G1 | PL20A/GR_PCLK7_1 | 7 | `DC_T_n` | in | D | open-drain + 10 kΩ pull-up at D; 1 kΩ series, partner H2 NC |
| J1 | PL23A/PCLKT7_1 | 7 | `DC_W_n` | in | D | open-drain + 10 kΩ pull-up at D; 1 kΩ series, partner J2 NC |
| K1 | PL23C/PCLKT7_0 | 7 | `CLK_AUX` | in | E | PCLKT7_0, spare clock input (external low-jitter clock option) |
| M7 | PB9B/D2/IO2 | 8 | `LINK_D0` | io | E | D2 |
| M8 | PB15B/DOUT/CSON | 8 | `LINK_D7` | io | E | DOUT/CSON |
| M9 | PB18A/WRITEN | 8 | `LINK_IRQ` | out | E | WRITEN |
| N10 | CFG_0 | 8 | `FPGA_CFG0` | in | E | 4.7 kΩ to VCCIO8 (CFG = 001 SSPI) |
| N7 | PB9A/D3/IO3 | 8 | `LINK_D1` | io | E | D3 |
| N8 | PB15A/HOLDN/DI/BUSY/CSSPIN/CEN | 8 | `FPGA_HOLDN` | in | E | 4.7 kΩ pull-up, not driven |
| N9 | CCLK/MCLK/SCK | 8 | `FPGA_CCLK` | in | E | SSPI clock from RP2350 SPI1 SCK; 33 Ω series at RP2350 |
| P10 | CFG_1 | 8 | `FPGA_CFG1` | in | E | to GND |
| P7 | PB6B/D4/MOSI2/IO4 | 8 | `LINK_D2` | io | E | D4 |
| P8 | PB13B/CS1N | 8 | `LINK_D6` | io | E | CS1N |
| P9 | DONE | 8 | `FPGA_DONE` | io | E | 4.7 kΩ pull-up |
| R10 | CFG_2 | 8 | `FPGA_CFG2` | in | E | to GND |
| R6 | PB4B/D6/IO6 | 8 | `LINK_D4` | io | E | D6 |
| R7 | PB6A/D5/MISO2/IO5 | 8 | `LINK_D3` | io | E | D5 |
| R8 | PB13A/SN/CSN | 8 | `FPGA_SN` | in | E | SSPI chip select, 4.7 kΩ pull-up |
| R9 | PROGRAMN | 8 | `FPGA_PROGRAMN` | in | E | 4.7 kΩ pull-up; RP2350 open-drain |
| T6 | PB4A/D7/IO7 | 8 | `LINK_D5` | io | E | D7 |
| T7 | PB11A/D1/MISO/IO1 | 8 | `FPGA_MISO` | out | E | SSPI MISO (D1) |
| T8 | PB11B/D0/MOSI/IO0 | 8 | `FPGA_MOSI` | in | E | SSPI MOSI (D0) |
| T9 | INITN | 8 | `FPGA_INITN` | io | E | 4.7 kΩ pull-up |

## FPGA power and dedicated balls

| Function | Count | Balls |
|---|---|---|
| GND | 27 | A1 A16 D15 D2 F8 F9 G10 G8 H1 H10 H16 H8 H9 J10 J8 J9 K10 K6 K7 K8 K9 N15 N2 T1 T12 T16 T5 |
| VCC | 6 | G6 G7 G9 L10 L8 L9 |
| VCCAUX | 2 | G11 L7 |
| VCCIO0 | 2 | F6 F7 |
| VCCIO1 | 2 | F10 F11 |
| VCCIO2 | 2 | H11 J11 |
| VCCIO3 | 2 | K11 L11 |
| VCCIO6 | 2 | J6 J7 |
| VCCIO7 | 2 | H6 H7 |
| VCCIO8 | 1 | L6 |

(Dedicated configuration/JTAG balls N9, N10, P9, P10, R10, T9, T10, R11, M10, T11 are in the signal table.) VCC → `+1V1`, VCCAUX → `+2V5` via bead, all VCCIO → `+3V3`.

## FPGA headroom (spare user I/O, excluding balls deliberately left NC as hot-socket partners)

| Bank | User I/O | Used | Held NC (partner) | Spare | Spare balls (outer ring first) |
|---|---|---|---|---|---|
| 0 | 24 | 8 | 0 | 16 | A7 A8 B6 B7 C4 C5 C6 C7 D4 D5 D6 D7 E4 E5 E6 E7 |
| 1 | 32 | 11 | 0 | 21 | A15 B14 B8 B9 C10 C11 C12 C13 C9 D10 D11 D12 D13 D8 D9 E13 E10 E11 E12 E8 E9 |
| 2 | 32 | 15 | 3 | 14 | B15 J15 G14 H14 J14 K14 F13 G13 H13 J13 F12 G12 H12 J12 |
| 3 | 32 | 20 | 4 | 8 | M15 L13 M13 N11 N12 L12 M11 M12 |
| 6 | 32 | 27 | 3 | 2 | P4 M6 |
| 7 | 32 | 3 | 2 | 27 | B1 C1 D1 E1 F1 B2 C2 E2 F2 G2 K2 C3 D3 E3 F3 G3 H3 J3 K3 F4 G4 H4 J4 F5 G5 H5 J5 |
| 8 | 13 | 13 | 0 | 0 |  |

**88 spare I/O.** B15 (PR2B, dual function "S0_IN") is listed as spare but best left unused. All slow status and enables that went to a TCA9535 expander in the Gowin version are now on FPGA pins; the expander is dropped (`E-ioexp-tca9535.md` superseded).

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
| 22 | GPIO22 | `FPGA_PROGRAMN` | od out | drive low only (≥ 110 ns pulse); 4.7 kΩ pull-up at the FPGA |
| 23 | GPIO23 | `FPGA_INITN` | in | open-drain from the FPGA, 4.7 kΩ pull-up |
| 24 | IOVDD | `+3V3` | P | 100 nF |
| 25 | GPIO24 | `FPGA_MISO` | in | SPI1 RX ← ECP5 T7 |
| 26 | GPIO25 | `FPGA_SN` | out | SPI1 CSn (driven as GPIO) → ECP5 R8, 4.7 kΩ pull-up |
| 27 | GPIO26 | `FPGA_CCLK` | out | SPI1 SCK, 37.5 MHz (≤ 60 MHz), 33 Ω series → ECP5 N9 |
| 28 | GPIO27 | `FPGA_MOSI` | out | SPI1 TX → ECP5 T8 |
| 29 | IOVDD | `+3V3` | P | 100 nF |
| 30 | XIN | 12 MHz crystal | | `E-xtal-12mhz.md` |
| 31 | XOUT | 12 MHz crystal via 1 kΩ | | |
| 32 | DVDD | `+1V1` | P | 100 nF |
| 33 | SWCLK | `SWCLK` | in | Debug Probe header (R-21, block G) |
| 34 | SWDIO | `SWDIO` | io | |
| 35 | RUN | `RUN` | in | 10 kΩ pull-up, reset button / debug |
| 36 | GPIO28 | `FPGA_DONE` | in | open-drain from the FPGA, 4.7 kΩ pull-up |
| 37 | GPIO29 | `SPARE_MCU_A` | io | spare (PHY management moved to the FPGA) |
| 38 | GPIO30 | `SPARE_MCU_B` | io | spare |
| 39 | GPIO31 | `SPARE_MCU_C` | io | spare |
| 40 | GPIO32 | `SPARE_MCU_D` | io | spare (no I2C expander with the ECP5) |
| 41 | IOVDD | `+3V3` | P | 100 nF |
| 42 | GPIO33 | `VDRV_PG` | in | block C gate-drive supply power-good (direct: gates amp start) |
| 43 | GPIO34 | `SPARE_MCU_E` | io | spare |
| 44 | GPIO35 | `SPARE_MCU_F` | io | spare |
| 45 | GPIO36 | `VDRV_EN` | out | block C gate-drive supply enable (pull-down = off) |
| 46 | GPIO37 | `SPARE_MCU_G` | io | spare |
| 47 | GPIO38 | `SPARE_MCU_H` | io | spare |
| 48 | GPIO39 | `SPARE_MCU_I` | io | spare |
| 49 | GPIO40/ADC0 | `KNOB1` | ain | R-17 knob header, RC filtered (block G) |
| 50 | IOVDD | `+3V3` | P | 100 nF |
| 51 | DVDD | `+1V1` | P | 100 nF + 4.7 µF (second DVDD cap rule) |
| 52 | GPIO41/ADC1 | `KNOB2` | ain | |
| 53 | GPIO42/ADC2 | `KNOB3` | ain | |
| 54 | GPIO43/ADC3 | `KNOB4` | ain | |
| 55 | GPIO44/ADC4 | `SPARE_ADC4` | ain | spare analog input (NTCs moved to block D's ADS7038) |
| 56 | GPIO45/ADC5 | `SPARE_ADC5` | ain | spare analog input (NTCs moved to block D's ADS7038) |
| 57 | GPIO46/ADC6 | `SPARE_ADC6` | ain | spare analog input (NTCs moved to block D's ADS7038) |
| 58 | GPIO47/ADC7 | `SPARE_ADC7` | ain | spare analog input (NTCs moved to block D's ADS7038) |
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

48 GPIO: 35 used, **13 spare** (GPIO29–32, 34, 35, 37–39, and ADC4–7 / GPIO44–47), freed by moving PHY management and the slow status to the FPGA. The SSPI configuration uses SPI1 (GPIO24–27) with PROGRAMN/INITN/DONE on GPIO22, 23, 28.

## Interface cross-check

| Interface | Needed | Where |
|---|---|---|
| Block D PWM (LMG1210 PWM mode) | 4 | FPGA N1, P1, R2, R4 (bank 6, ODDRX2F) |
| Block D fault latch: AMP_EN ×2, AMP_CLK ×2, AMP_ARM, FAULT_n ×2, DC_n ×2 | 9 | FPGA R5, T4, P2, T2, R1, L1, M1 (bank 6); J1, G1 (bank 7) |
| Block D ADS7042 (VBUS) | CS, SCLK, SDO | FPGA T3, N3, M4 |
| Block D ADS7038-Q1 (I-sense ×4, NTC ×4) | CS, SCLK, SDI, SDO | FPGA L3, M3, R3, P3 |
| Block D 2 × ADS8353 (optional, pins reserved) | CS, SCLK, SDI, 4 × SDO | FPGA K4, L4, K5, L5, M5, N5, N6 |
| Block D NTCs | 4 | on the ADS7038-Q1 channels 4–7 (block D's proposal, accepted); RP2350 ADC4–7 now spare |
| Block F 4-tap FIR DAC, 2 ch | 8 | FPGA N16, P15, P16, R16 (L); R13, T14, R12, T13 (R) |
| Block F PCM1808 BCK, LRCK, DOUT | 3 | FPGA P13, R14, L16 |
| Block F MEMS PDM CLK, DAT | 2 | FPGA L14, N13 |
| Block F HP_EN, LO_EN, HP_FAULT_N, HP_DET | 4 | FPGA M14, N14, P11, K13 |
| Block G display (8 header positions) + backlight switch | 8 + 1 | FPGA B16, C16, C15, D16, E15, E16, F15, F16; `DISP_BL_PWM` G15. The header line jumpered to DISP_BLK must be constrained Hi-Z in the gateware |
| Block G PTP-second test point | 1 | FPGA G16 |
| Block C/G LED_EN, QWIIC_PWR_EN, LED_FAULT_N, QWIIC_FAULT_N, VUSB_DET | 5 | FPGA H15, J16, K16, C14, E14 |
| Block C PG_5V, PG_3V3, PG_3V3Q | 3 | FPGA B3, B4, B5 |
| Block C VDRV_EN, VDRV_PG | 2 | RP2350 GPIO36, GPIO33 |
| Block A PD_PG, PD_TPH_N, PD_TPL_N, PD_BT_N | 4 | FPGA A2–A5 |
| Block B/C POE_LOSS_N | 1 | FPGA A6 |
| PHY RMII + SMI + reset/int | 7 + 4 | FPGA C8, A9–A12, B10, B11; A13, A14, B12, B13 |
| VCXO clock + tune | 2 | FPGA P6, N4 |
| RP2350 ↔ FPGA link | 12 | RP2350 GPIO8–19 ↔ FPGA M7, N7, P7, R7, R6, T6, P8, M8 (D0–D7), M9 (IRQ), M16 (CLK), R15 (DIR), T15 (STB) |
| FPGA configuration (SSPI) | 7 | RP2350 GPIO22–28 ↔ FPGA R9, T9, T7, R8, N9, T8, P9 |
| FPGA JTAG header (R-22) | 4 | FPGA T10, R11, M10, T11 (direct, 3.3 V) |
| Block G I2C, LED data/clock, encoders, knobs, UART, SWD, USB | | RP2350 (unchanged from the Gowin version) |
