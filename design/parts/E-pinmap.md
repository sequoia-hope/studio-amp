# Block E pin budget — ECP5 LFE5U-25F-7BG256I (caBGA-256) and RP2350B (QFN-80)

ECP5 version (user, 2026-11-07). The GW1NR-9 version is kept in `E-pinmap-gowin.md` (superseded).
Sources: `datasheets/lattice-ECP5U-25-pinout.csv` (CABGA256 column: ball, pad, bank, dual function, differential pair), `datasheets/lattice-FPGA-TN-02039.pdf` (sysCONFIG pins), `datasheets/lattice-FPGA-DS-02012.pdf` (DDR gearing sides, hot socketing), `datasheets/rp2350-lcsc.pdf` Fig 3 / Tab 3. The FPGA table below was generated and checked by script against the CSV: every ball exists, none is used twice, no net is duplicated, and every "partner NC" ball is the true differential partner and is unused.

All seven FPGA banks run at **VCCIO = 3.3 V**, so there is no level translation anywhere in block E.

## Floorplan this pin-out assumes

- **Left (banks 7, 6):** power stage (block D). The PWM needs ODDRX2F, which exists only on left/right banks. The VCXO enters the lower-left PLL (P6).
- **Top (banks 0, 1):** PHY/RJ45 (block A) and the isolated PD status. Top/bottom banks tolerate hot socketing, so always-driven inputs go here.
- **Right (banks 2, 3):** audio (block F) and display/LED/Qwiic (block G).
- **Bottom (bank 8):** configuration. The RP2350 and its flash sit below the FPGA, with the link and SSPI as short traces.

## FPGA signal assignments (109 balls incl. configuration/JTAG)

Rules (see `E-fpga-ecp5.md`): always-driven inputs on left/right banks have their differential pair partner left **NC** and a series resistor; outputs default to tri-state + weak pull-down until configured.

| Ball | Pad / dual function | Bank | Net | Dir | Block | Notes | Needed before configuration / with the ECP5 unpowered | Guaranteed by |
|---|---|---|---|---|---|---|---|---|
| A2 | PT4A | 0 | `PD_PG_N` | in | A | isolator, active low, high when primary unpowered; 1 kΩ series | don't care (FPGA input) | ISO7740 push-pull outputs on +3V3, default high when primary unpowered |
| A3 | PT6A | 0 | `PD_TPH_N` | in | A | 1 kΩ series | don't care (FPGA input) | ISO7740 push-pull outputs on +3V3, default high when primary unpowered |
| A4 | PT6B | 0 | `PD_TPL_N` | in | A | 1 kΩ series | don't care (FPGA input) | ISO7740 push-pull outputs on +3V3, default high when primary unpowered |
| A5 | PT18A | 0 | `PD_BT_N` | in | A | 1 kΩ series | don't care (FPGA input) | ISO7740 push-pull outputs on +3V3, default high when primary unpowered |
| A6 | PT18B | 0 | `POE_LOSS_N` | in | B | block B VBUS-droop comparator (low at VBUS < 39.5 V (38.5–40.5), release > 41.1 V (40.0–42.2), 0.31 ms filter; asserted during start-up), 2N7002 open drain (VOL ≤ 10 mV at 1.37 mA), active low, ignored until VBUS_VALID; 4.7 kΩ pull-up to +3V3 on the net (E), 1 kΩ series; net also drives block F’s separate BAT54C (D_PL) to the two relay gates (not an OR into /DC_TRIP) | low during start-up ramp (expected); ignored by the gateware until VBUS_VALID; the net also drives block F's BAT54C (D_PL) to the relay gates | **pull-up changed to 4.7 kΩ** (≥ 2.6 V vs 150 µA; 10 kΩ gave 1.8 V); LPF PULLMODE=NONE |
| B3 | PT4B | 0 | `PG_5V_N` | in | C | buffered active-low copy (block C 2N7002 + 4.7 kΩ pull-up): low = 5 V good | high (= not good) until 5 V good; FPGA-only reader | block C buffer: 2N7002 + 4.7 kΩ pull-up; LPF PULLMODE=NONE |
| B4 | PT11B | 0 | `PG_3V3_N` | in | C | buffered active-low copy (block C 2N7002 + 4.7 kΩ pull-up): low = 3V3 good | high (= not good) until 3V3 good; FPGA-only reader | block C buffer: 2N7002 + 4.7 kΩ pull-up (≥ 2.6 V vs 150 µA); real PG_3V3 (1V1 EN) no longer reaches the FPGA; LPF PULLMODE=NONE |
| B5 | PT15B | 0 | `PG_3V3Q` | in | C/F | TPS7A94 PG, open-drain, block C 100 kΩ pull-up; 1 kΩ series; gateware holds DAC_* low until high | high when 3V3_Q good (FPGA-only reader) | block C 100 kΩ pull-up dragged low before config → reads "not good", which is the safe state (DAC lines held low); after config **LPF PULLMODE=NONE**. If any other block reads it in hardware, its pull-up must be ≤ 4.7 kΩ |
| B6 | PT22B | 0 | `ACF_PULSE` | in | B | 3.3 V copy of the NCP4306 SR gate (74LVC2G08 on +3V3, same rail, no injection): one edge per conduction pulse, none in skip; 737.28 kHz crystal-locked; 4.7 kΩ series; gateware AB-M3 run-average clock-fault rule | don't care before config | push-pull 74LVC2G08 on +3V3 (same rail): no injection; LPF PULLMODE=NONE |
| A10 | PT42B | 1 | `RMII_TXD0` | out | E |  | don't care (TXEN low) | ECP5 weak pull-down (TN-02039 §5.2) |
| A11 | PT53A | 1 | `RMII_RXD0` | in | E | DELAYG; PHY MODE0 strap: 4.7 kΩ pull-up to 3V3, LPF PULLMODE=UP | **high (LAN8720A MODE = 111 strap)** | 4.7 kΩ pull-ups (≥ 2.6 V) + LPF PULLMODE=UP; PHY held in reset until after config |
| A12 | PT53B | 1 | `RMII_RXD1` | in | E | DELAYG; MODE1 strap: 4.7 kΩ pull-up, PULLMODE=UP | **high (LAN8720A MODE = 111 strap)** | 4.7 kΩ pull-ups (≥ 2.6 V) + LPF PULLMODE=UP; PHY held in reset until after config |
| A13 | PT65A | 1 | `PHY_MDC` | out | E |  | don't care | ECP5 weak pull-down (TN-02039 §5.2) |
| A14 | PT65B | 1 | `PHY_MDIO` | io | E | 1.5 kΩ pull-up | idle high | 1.5 kΩ pull-up (3.08 V vs 150 µA) |
| A9 | PT42A | 1 | `RMII_TXEN` | out | E | 10 kΩ pull-down | low (PHY not transmitting) | ECP5 weak pull-down (TN-02039 §5.2) + 10 kΩ pull-down |
| B10 | PT44A | 1 | `RMII_TXD1` | out | E |  | don't care (TXEN low) | ECP5 weak pull-down (TN-02039 §5.2) |
| B11 | PT49A | 1 | `RMII_CRSDV` | in | E | DELAYG; MODE2 strap: 4.7 kΩ pull-up, PULLMODE=UP | **high (LAN8720A MODE = 111 strap)** | 4.7 kΩ pull-ups (≥ 2.6 V) + LPF PULLMODE=UP; PHY held in reset until after config |
| B12 | PT56A | 1 | `PHY_NRST` | out | E | 10 kΩ pull-down | low (PHY in reset) | ECP5 weak pull-down (TN-02039 §5.2) + 10 kΩ pull-down |
| B13 | PT60A | 1 | `PHY_NINT` | in | E | 10 kΩ pull-up | don't care (PHY in reset) | 10 kΩ pull-up; LPF PULLMODE=NONE after config |
| C8 | PT35A/PCLKT1_0 | 1 | `RMII_REFCLK` | in | E | PCLKT1_0, 50 MHz | don't care (driven by XO) | push-pull source |
| B16 | PR2A | 2 | `DISP_SCL` | out | G | series R at header | low (RES low = display held in reset; harmless) | ECP5 weak pull-down (TN-02039 §5.2) |
| C14 | PR2C | 2 | `QWIIC_FAULT_N` | in | C/G | open-drain; 1 kΩ series, partner D14 NC | don't care (FPGA-only readers) | block C 10 kΩ pull-ups → 1.8 V before config; **LPF PULLMODE=NONE** after config |
| C15 | PR5B | 2 | `DISP_RES` | out | G |  | low (RES low = display held in reset; harmless) | ECP5 weak pull-down (TN-02039 §5.2) |
| C16 | PR5A | 2 | `DISP_SDA` | out | G |  | low (RES low = display held in reset; harmless) | ECP5 weak pull-down (TN-02039 §5.2) |
| D16 | PR8A | 2 | `DISP_DC` | out | G |  | low (RES low = display held in reset; harmless) | ECP5 weak pull-down (TN-02039 §5.2) |
| E14 | PR5C | 2 | `VUSB_DET` | in | G | 1 kΩ series, partner F14 NC | don't care (FPGA-only reader) | block C 15k/22k divider (8.9 kΩ Thevenin) → **LPF PULLMODE=NONE** after config |
| E15 | PR8B | 2 | `DISP_CS` | out | G |  | low (RES low = display held in reset; harmless) | ECP5 weak pull-down (TN-02039 §5.2) |
| E16 | PR11D | 2 | `DISP_BLK` | out | G |  | low (RES low = display held in reset; harmless) | ECP5 weak pull-down (TN-02039 §5.2) |
| F15 | PR11C | 2 | `DISP_AUX7` | out | G | header position 7 (pin-order remap) | low (RES low = display held in reset; harmless) | ECP5 weak pull-down (TN-02039 §5.2) |
| F16 | PR14A | 2 | `DISP_AUX8` | out | G | header position 8 | low (RES low = display held in reset; harmless) | ECP5 weak pull-down (TN-02039 §5.2) |
| G15 | PR14B | 2 | `DISP_BL_PWM` | out | G | backlight FET switch gate (2N7002, 100 kΩ pull-down at G); 4 mA drive, PWM ≤ 2 kHz, default low | low (backlight off) | ECP5 weak pull-down (TN-02039 §5.2) + block G 100 kΩ pull-down |
| G16 | PR20A/GR_PCLK2_1 | 2 | `PTP_PPS` | out | G | PTP-second test point | don't care | ECP5 weak pull-down (TN-02039 §5.2) |
| H15 | PR20B | 2 | `LED_EN` | out | C/G | 100 kΩ pull-down at EN | low (switch off) | ECP5 weak pull-down (TN-02039 §5.2) + block C 100 kΩ pull-down |
| J16 | PR23A/PCLKT2_1 | 2 | `QWIIC_PWR_EN` | out | C/G | TPS2553 EN and TCA9617B EN; 10 kΩ pull-down (block C; beats the TCA9617B EN internal −25 µA pull-up); sources 0.33 mA when high | low (Qwiic power and I2C buffer off) | ECP5 weak pull-down (TN-02039 §5.2) + block C 10 kΩ pull-down (TCA9617B EN has a −25 µA internal pull-up: 100 kΩ held it at ≈ 1.47 V; 10 kΩ gives ≤ 0.25 V) |
| K16 | PR23C/PCLKT2_0 | 2 | `LED_FAULT_N` | in | C/G | open-drain, 10 kΩ pull-up; 1 kΩ series, partner K15 NC | don't care (FPGA-only readers) | block C 10 kΩ pull-ups → 1.8 V before config; **LPF PULLMODE=NONE** after config |
| K13 | PR29A/GR_PCLK3_0 | 3 | `HP_DET` | in | F | always driven: 1 kΩ series, partner K12 NC | don't care (FPGA-only reader) | block F 47 kΩ pull-up: ≥ 2.8 V after config with PULLMODE=NONE (IIH ≤ 10 µA) |
| L14 | PR32C | 3 | `PDM_CLK` | out | F | 3.072 MHz | low (clocks halted; PCM1808/mic on +3V3, same rail) | ECP5 weak pull-down (TN-02039 §5.2) |
| L16 | PR26A/PCLKT3_1 | 3 | `MADC_DOUT` | in | F | always driven: 330 Ω series, partner L15 NC | don't care (FPGA input) | driven/tri-stated by F parts; pull-down harmless |
| M14 | PR32D | 3 | `HP_EN` | out | F | pull-down at block F | low (relays open, outputs muted) | ECP5 weak pull-down (TN-02039 §5.2) + block F 100 kΩ gate pull-downs |
| M16 | PR26C/PCLKT3_0 | 3 | `LINK_CLK` | in | E | PCLKT3_0 | don't care (RP2350 Hi-Z until DONE) | ECP5 weak pull-down (TN-02039 §5.2) |
| N13 | PR38A | 3 | `PDM_DAT` | in | F | always driven: 330 Ω series, partner P14 NC | don't care (FPGA input) | driven/tri-stated by F parts; pull-down harmless |
| N14 | PR35D | 3 | `LO_EN` | out | F | pull-down at block F | low (relays open, outputs muted) | ECP5 weak pull-down (TN-02039 §5.2) + block F 100 kΩ gate pull-downs |
| N16 | PR32A | 3 | `DAC_L0` | out | F |  | **low** (74LVC74 on 3V3_Q has no Ioff) | ECP5 weak pull-down (TN-02039 §5.2); gateware holds low until PG_3V3Q |
| P11 | PR47C/LRC_GPLL0T_IN | 3 | `HP_FAULT_N` | in | F | always driven: 1 kΩ series, partner P12 NC | high when no fault: **read in hardware** by block F (/DC_TRIP BAT54C OR) | block F 4.7 kΩ pull-up (≥ 2.6 V vs 150 µA); LPF PULLMODE=NONE |
| P13 | PR41A | 3 | `MADC_BCK` | out | F | PCM1808 BCK 3.072 MHz | low (clocks halted; PCM1808/mic on +3V3, same rail) | ECP5 weak pull-down (TN-02039 §5.2) |
| P15 | PR32B | 3 | `DAC_L1` | out | F |  | **low** (74LVC74 on 3V3_Q has no Ioff) | ECP5 weak pull-down (TN-02039 §5.2); gateware holds low until PG_3V3Q |
| P16 | PR35A | 3 | `DAC_L2` | out | F |  | **low** (74LVC74 on 3V3_Q has no Ioff) | ECP5 weak pull-down (TN-02039 §5.2); gateware holds low until PG_3V3Q |
| R12 | PR44A | 3 | `DAC_R2` | out | F |  | **low** (74LVC74 on 3V3_Q has no Ioff) | ECP5 weak pull-down (TN-02039 §5.2); gateware holds low until PG_3V3Q |
| R13 | PR41C | 3 | `DAC_R0` | out | F |  | **low** (74LVC74 on 3V3_Q has no Ioff) | ECP5 weak pull-down (TN-02039 §5.2); gateware holds low until PG_3V3Q |
| R14 | PR41B | 3 | `MADC_LRCK` | out | F | 48 kHz | low (clocks halted; PCM1808/mic on +3V3, same rail) | ECP5 weak pull-down (TN-02039 §5.2) |
| R15 | PR38C | 3 | `LINK_DIR` | in | E |  | don't care (RP2350 Hi-Z until DONE) | ECP5 weak pull-down (TN-02039 §5.2) |
| R16 | PR35B/VREF1_3 | 3 | `DAC_L3` | out | F |  | **low** (74LVC74 on 3V3_Q has no Ioff) | ECP5 weak pull-down (TN-02039 §5.2); gateware holds low until PG_3V3Q |
| T13 | PR44B | 3 | `DAC_R3` | out | F |  | **low** (74LVC74 on 3V3_Q has no Ioff) | ECP5 weak pull-down (TN-02039 §5.2); gateware holds low until PG_3V3Q |
| T14 | PR41D | 3 | `DAC_R1` | out | F |  | **low** (74LVC74 on 3V3_Q has no Ioff) | ECP5 weak pull-down (TN-02039 §5.2); gateware holds low until PG_3V3Q |
| T15 | PR38D | 3 | `LINK_STB` | in | E |  | don't care (RP2350 Hi-Z until DONE) | ECP5 weak pull-down (TN-02039 §5.2) |
| M10 | TDO | 40 | `FPGA_TDO` | out | G | 4.7 kΩ pull-up | high | 4.7 kΩ pull-up |
| R11 | TDI | 40 | `FPGA_TDI` | in | G | 4.7 kΩ pull-up | high | 4.7 kΩ pull-up |
| T10 | TCK | 40 | `FPGA_TCK` | in | G | JTAG header; 4.7 kΩ pull-down | low | 4.7 kΩ pull-down |
| T11 | TMS | 40 | `FPGA_TMS` | in | G | 4.7 kΩ pull-up | high | 4.7 kΩ pull-up |
| K4 | PL29A/GR_PCLK6_0 | 6 | `PF_CS_n` | out | D | reserved, optional 2 × ADS8353 (R-51); 4.7 kΩ pull-up | high (ADC deselected, SDO tri-stated) | 4.7 kΩ pull-up (≥ 2.6 V vs 150 µA) |
| K5 | PL29B | 6 | `PF_SDI` | out | D | reserved | don't care (CS high) | ECP5 weak pull-down (TN-02039 §5.2) |
| L1 | PL26A/PCLKT6_1 | 6 | `FAULT_W_n` | in | D | always driven: 330 Ω series, partner L2 NC | don't care (FPGA input; comparator push-pull output) | driven by block D; pull-down cannot move it |
| L3 | PL32C | 6 | `IS_CS_n` | out | D | ADS7038-Q1; 4.7 kΩ pull-up | high (ADC deselected, SDO tri-stated) | 4.7 kΩ pull-up (≥ 2.6 V vs 150 µA) |
| L4 | PL29C/GR_PCLK6_1 | 6 | `PF_SCLK` | out | D | reserved | don't care (CS high) | ECP5 weak pull-down (TN-02039 §5.2) |
| L5 | PL29D | 6 | `PF_SDO_WA` | in | D | reserved | don't care (ADC tri-stated) | ECP5 weak pull-down (TN-02039 §5.2) |
| M1 | PL26C/PCLKT6_0 | 6 | `FAULT_T_n` | in | D | always driven: 330 Ω series, partner M2 NC | don't care (FPGA input; comparator push-pull output) | driven by block D; pull-down cannot move it |
| M3 | PL32D | 6 | `IS_SCLK` | out | D | ≤ 60 MHz | don't care (CS high) | ECP5 weak pull-down (TN-02039 §5.2) |
| M4 | PL35C | 6 | `VB_SDO` | in | D | partner N3 is an FPGA output | don't care (ADC tri-stated) | ECP5 weak pull-down (TN-02039 §5.2) |
| M5 | PL44C | 6 | `PF_SDO_WB` | in | D | reserved | don't care (ADC tri-stated) | ECP5 weak pull-down (TN-02039 §5.2) |
| N1 | PL32A | 6 | `PWM_W_A` | out | D | ODDRX2F; LMG1210 PWM mode, high = HS on; matched routing, 100 Ω at driver | low (bridge legs off) | ECP5 weak pull-down (TN-02039 §5.2) + block D pull-down; latch also held off by AMP_ARM low |
| N3 | PL35D | 6 | `VB_SCLK` | out | D | ≤ 16 MHz | don't care (CS high) | ECP5 weak pull-down (TN-02039 §5.2) |
| N4 | PL38A | 6 | `VCXO_TUNE` | out | E | ΔΣ → 2-pole RC → VCXO Vc | any (Vc 0 V = VCXO at its pull limit; servo recentres after config) | ECP5 weak pull-down (TN-02039 §5.2) pulls the RC to 0 V; harmless |
| N5 | PL44D | 6 | `PF_SDO_TA` | in | D | reserved | don't care (ADC tri-stated) | ECP5 weak pull-down (TN-02039 §5.2) |
| N6 | PL47B | 6 | `PF_SDO_TB` | in | D | reserved | don't care (ADC tri-stated) | ECP5 weak pull-down (TN-02039 §5.2) |
| P1 | PL35A | 6 | `PWM_W_B` | out | D | ODDRX2F | low (bridge legs off) | ECP5 weak pull-down (TN-02039 §5.2) + block D pull-down; latch also held off by AMP_ARM low |
| P2 | PL32B | 6 | `AMP_CLK_W` | out | D | fault-latch clock | low, no rising edge | ECP5 weak pull-down (TN-02039 §5.2); latch ignores CLK while AMP_ARM is low |
| P3 | PL38B | 6 | `IS_SDO` | in | D | partner N4 is an FPGA output | don't care (ADC tri-stated) | ECP5 weak pull-down (TN-02039 §5.2) |
| P4 | PL41A | 6 | `VB_CS_n` | out | D | ADS7042; 4.7 kΩ pull-up (moved from T3, which pairs with PWM_T_B and is now left unused) | high (ADC deselected, SDO tri-stated) | 4.7 kΩ pull-up (≥ 2.6 V vs 150 µA) |
| P6 | PL47C/LLC_GPLL0T_IN | 6 | `VCXO_CLK` | in | E | LLC_GPLL0T_IN: PWM/audio PLL reference; partner P5 left NC | don't care (driven by VCXO) | push-pull source |
| R1 | PL35B/VREF1_6 | 6 | `AMP_ARM` | out | D | block D 10 kΩ pull-down | low (both bridges disarmed) | ECP5 weak pull-down (TN-02039 §5.2) + block D 10 kΩ pull-down |
| R2 | PL38C | 6 | `PWM_T_A` | out | D | ODDRX2F | low (bridge legs off) | ECP5 weak pull-down (TN-02039 §5.2) + block D pull-down; latch also held off by AMP_ARM low |
| R3 | PL41B | 6 | `IS_SDI` | out | D |  | don't care (CS high) | ECP5 weak pull-down (TN-02039 §5.2) |
| R4 | PL41C | 6 | `PWM_T_B` | out | D | ODDRX2F | low (bridge legs off) | ECP5 weak pull-down (TN-02039 §5.2) + block D pull-down; latch also held off by AMP_ARM low |
| R5 | PL44A | 6 | `AMP_EN_W` | out | D | fault-latch D input | low, no rising edge | ECP5 weak pull-down (TN-02039 §5.2); latch ignores CLK while AMP_ARM is low |
| T2 | PL38D | 6 | `AMP_CLK_T` | out | D | fault-latch clock | low, no rising edge | ECP5 weak pull-down (TN-02039 §5.2); latch ignores CLK while AMP_ARM is low |
| T4 | PL44B | 6 | `AMP_EN_T` | out | D | fault-latch D input | low, no rising edge | ECP5 weak pull-down (TN-02039 §5.2); latch ignores CLK while AMP_ARM is low |
| G1 | PL20A/GR_PCLK7_1 | 7 | `DC_T_n` | in | D | open-drain + 4.7 kΩ pull-up at D; 1 kΩ series, partner H2 NC | high when idle (D hardware reads it through a diode into the fault node) | block D 4.7 kΩ pull-up (changed from 10 kΩ; ≥ 2.6 V vs 150 µA); fault node also held by AMP_ARM low; LPF PULLMODE=NONE |
| J1 | PL23A/PCLKT7_1 | 7 | `DC_W_n` | in | D | open-drain + 4.7 kΩ pull-up at D; 1 kΩ series, partner J2 NC | high when idle (D hardware reads it through a diode into the fault node) | block D 4.7 kΩ pull-up (changed from 10 kΩ; ≥ 2.6 V vs 150 µA); fault node also held by AMP_ARM low; LPF PULLMODE=NONE |
| K1 | PL23C/PCLKT7_0 | 7 | `CLK_AUX` | in | E | PCLKT7_0, spare clock input (external low-jitter clock option) | unconnected unless the option is fitted | — |
| M7 | PB9B/D2/IO2 | 8 | `LINK_D0` | io | E | D2 | don't care (RP2350 Hi-Z until DONE) | bank 8 D-pins: no pull; M8 drives high during config (TN-02039 §4.7.2) → RP2350 keeps Hi-Z |
| M8 | PB15B/DOUT/CSON | 8 | `LINK_D7` | io | E | DOUT/CSON | don't care (RP2350 Hi-Z until DONE) | bank 8 D-pins: no pull; M8 drives high during config (TN-02039 §4.7.2) → RP2350 keeps Hi-Z |
| M9 | PB18A/WRITEN | 8 | `LINK_IRQ` | out | E | WRITEN | ignored until DONE | WRITEN pulled up during config (Tab 4.5) |
| N10 | CFG_0 | 8 | `FPGA_CFG0` | in | E | 4.7 kΩ to VCCIO8 (CFG = 001 SSPI) | high (CFG = 001) | 4.7 kΩ pull-up |
| N7 | PB9A/D3/IO3 | 8 | `LINK_D1` | io | E | D3 | don't care (RP2350 Hi-Z until DONE) | bank 8 D-pins: no pull; M8 drives high during config (TN-02039 §4.7.2) → RP2350 keeps Hi-Z |
| N8 | PB15A/HOLDN/DI/BUSY/CSSPIN/CEN | 8 | `FPGA_HOLDN` | in | E | 4.7 kΩ pull-up, not driven | high | 4.7 kΩ pull-up (TN-02038 Tab 6.2) |
| N9 | CCLK/MCLK/SCK | 8 | `FPGA_CCLK` | in | E | SSPI clock from RP2350 SPI1 SCK (8 mA); 33 Ω series at RP2350, 1 kΩ pull-up to VCCIO8 | high/defined | 1 kΩ pull-up to VCCIO8 |
| P10 | CFG_1 | 8 | `FPGA_CFG1` | in | E | to GND | low | tied to GND |
| P7 | PB6B/D4/MOSI2/IO4 | 8 | `LINK_D2` | io | E | D4 | don't care (RP2350 Hi-Z until DONE) | bank 8 D-pins: no pull; M8 drives high during config (TN-02039 §4.7.2) → RP2350 keeps Hi-Z |
| P8 | PB13B/CS1N | 8 | `LINK_D6` | io | E | CS1N | don't care (RP2350 Hi-Z until DONE) | bank 8 D-pins: no pull; M8 drives high during config (TN-02039 §4.7.2) → RP2350 keeps Hi-Z |
| P9 | DONE | 8 | `FPGA_DONE` | io | E | 4.7 kΩ pull-up | high | 4.7 kΩ pull-up (TN-02038 Tab 6.2) |
| R10 | CFG_2 | 8 | `FPGA_CFG2` | in | E | to GND | low | tied to GND |
| R6 | PB4B/D6/IO6 | 8 | `LINK_D4` | io | E | D6 | don't care (RP2350 Hi-Z until DONE) | bank 8 D-pins: no pull; M8 drives high during config (TN-02039 §4.7.2) → RP2350 keeps Hi-Z |
| R7 | PB6A/D5/MISO2/IO5 | 8 | `LINK_D3` | io | E | D5 | don't care (RP2350 Hi-Z until DONE) | bank 8 D-pins: no pull; M8 drives high during config (TN-02039 §4.7.2) → RP2350 keeps Hi-Z |
| R8 | PB13A/SN/CSN | 8 | `FPGA_SN` | in | E | SSPI chip select, 4.7 kΩ pull-up | high | 4.7 kΩ pull-up (TN-02038 Tab 6.2) |
| R9 | PROGRAMN | 8 | `FPGA_PROGRAMN` | in | E | 4.7 kΩ pull-up; RP2350 open-drain | high | 4.7 kΩ pull-up (TN-02038 Tab 6.2) |
| T6 | PB4A/D7/IO7 | 8 | `LINK_D5` | io | E | D7 | don't care (RP2350 Hi-Z until DONE) | bank 8 D-pins: no pull; M8 drives high during config (TN-02039 §4.7.2) → RP2350 keeps Hi-Z |
| T7 | PB11A/D1/MISO/IO1 | 8 | `FPGA_MISO` | out | E | SSPI MISO (D1) | don't care (SN high) | — |
| T8 | PB11B/D0/MOSI/IO0 | 8 | `FPGA_MOSI` | in | E | SSPI MOSI (D0) | don't care (SN high) | — |
| T9 | INITN | 8 | `FPGA_INITN` | io | E | 4.7 kΩ pull-up | high | 4.7 kΩ pull-up (TN-02038 Tab 6.2) |

## Pre-configuration sweep (lead's request after the C+G review, 2026-11-07)

Every FPGA ball above now has two extra columns: the level its external circuit needs before configuration (and while the ECP5 core is unpowered), and what guarantees it. The hazard is the ECP5 default: before configuration and on unused pins, a **weak pull-down of 30–150 µA** (TN-02039 §5.2; TN-02038 Tab 9.1). A pull-up of R_pu is dragged to 3.3 V − 150 µA × R_pu, so **any pull-up above ~4.7 kΩ on a net that hardware reads before configuration fails** (VIH 2.31 V for 0.7·VCC CMOS needs R_pu ≤ 6.6 kΩ).

Findings:
1. **PG_3V3, PG_5V** (block C): deadlock, since PG_3V3 also enables 1V1. **Fixed by block C**: B3/B4 now carry buffered active-low copies `PG_5V_N`/`PG_3V3_N` (2N7002 + 4.7 kΩ), and the real PG nets no longer reach the FPGA. Gateware inverts them.
2. **RMII_RXD0/RXD1/CRS_DV** (LAN8720A straps): fixed with 4.7 kΩ pull-ups + PULLMODE=UP (review MAJOR-2).
3. **POE_LOSS_N**: my own 10 kΩ pull-up gave 1.8 V, and the net also drives block F's BAT54C (D_PL) to the relay gates. It fails safe (mutes), but it is wrong: **changed to 4.7 kΩ** (2.6 V).
4. **DC_W_n, DC_T_n**: block D's hardware reads them through a diode into the fault node. **Fixed by block D**: pull-up now 4.7 kΩ (≥ 2.6 V).
5. **PG_3V3Q** (block C 100 kΩ): reads "not good" before configuration, which is the safe direction (DAC lines low). Fine as long as only the FPGA reads it; otherwise ≤ 4.7 kΩ.
6. **FPGA-only readers with weak pull-ups or dividers** (LED_FAULT_N, QWIIC_FAULT_N, PHY_NINT, HP_DET, VUSB_DET, ACF_PULSE). `HP_FAULT_N` (= /DC_TRIP) is **read in hardware** by block F's BAT54C OR, and block F has fitted a 4.7 kΩ pull-up (re-review MINOR-3, closed). no pre-configuration consequence, but the gateware must set **PULLMODE=NONE** on them in the LPF, or the post-configuration pull-down leaves them at 1–1.8 V.
7. Enables, resets, chip-selects and PWM lines: the pull-down puts each in its safe state (bridge off, relays open, PHY in reset, LED/Qwiic power off, backlight off). ADC chip-selects have 4.7 kΩ pull-ups so the ADCs stay deselected. No action.
8. **VCXO_TUNE**: the pull-down discharges the 2-pole RC to 0 V → VCXO at its pull limit until the servo runs. Harmless.

**Unpowered ECP5 / clamp back-powering:** every external part on an FPGA ball runs from `+3V3`, the same rail as all VCCIO banks. The exceptions:
- **DAC flip-flops on +3V3_Q** (the reverse case): the FPGA drives low or pulls down until PG_3V3Q.
- **ACF_PULSE**: closed. Block B drives it from a 74LVC2G08 gate on +3V3, the same rail as the FPGA, so nothing is injected.
- **IBUS_SENSE** into RP2350 ADC4 (not an FPGA pin): block B's INA281 runs from VSR (10 V, from VBUS), which can be up before +3V3. Its final source impedance is ≈ 67 kΩ, so the worst injection into an unpowered RP2350 pad is 3 V / 67 kΩ ≈ 45 µA. **Accepted**, closed.

The left/right-bank A/B-pair window (VCCIO up, VCC below POR) was already handled: partner-NC rule, review MINOR-7.

**Gateware LPF rules collected here:**
- PULLMODE=UP on A11, A12, B11.
- PULLMODE=NONE on A6, B3, B4, B5, B6, K16, C14, E14, B13, P11, K13, J1, G1.
- All other inputs keep the default.

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
| 0 | 24 | 9 | 0 | 15 | A7 A8 B7 C4 C5 C6 C7 D4 D5 D6 D7 E4 E5 E6 E7 |
| 1 | 32 | 11 | 0 | 21 | A15 B14 B8 B9 C10 C11 C12 C13 C9 D10 D11 D12 D13 D8 D9 E13 E10 E11 E12 E8 E9 |
| 2 | 32 | 15 | 3 | 14 | B15 J15 G14 H14 J14 K14 F13 G13 H13 J13 F12 G12 H12 J12 |
| 3 | 32 | 20 | 4 | 8 | M15 L13 M13 N11 N12 L12 M11 M12 |
| 6 | 32 | 27 | 4 | 1 | M6 (T3 held NC: pairs with PWM_T_B) |
| 7 | 32 | 3 | 2 | 27 | B1 C1 D1 E1 F1 B2 C2 E2 F2 G2 K2 C3 D3 E3 F3 G3 H3 J3 K3 F4 G4 H4 J4 F5 G5 H5 J5 |
| 8 | 13 | 13 | 0 | 0 |  |

**86 spare I/O** (T3 excluded). B15 (PR2B, dual function "S0_IN") is listed as spare but best left unused. **T3 must stay unconnected** (it pairs with `PWM_T_B` R4; review MINOR-7). All slow status and enables that went to a TCA9535 expander in the Gowin version are now on FPGA pins; the expander is dropped (`E-ioexp-tca9535.md` superseded).

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
| 10 | DVDD | `DVDD_RP` | P | 100 nF (RP2350's own 1.1 V from its regulator; not the ECP5 `+1V1`) |
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
| 32 | DVDD | `DVDD_RP` | P | 100 nF |
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
| 43 | GPIO34 | `ILIM_SEL0` | out | block B CC-limit select bit 0; B fits 100 kΩ pull-down |
| 44 | GPIO35 | `ILIM_SEL1` | out | block B CC-limit select bit 1; B fits 100 kΩ pull-down |
| 45 | GPIO36 | `VDRV_EN` | out | block C gate-drive supply enable (pull-down = off) |
| 46 | GPIO37 | `SPARE_MCU_G` | io | spare |
| 47 | GPIO38 | `SPARE_MCU_H` | io | spare |
| 48 | GPIO39 | `SPARE_MCU_I` | io | spare |
| 49 | GPIO40/ADC0 | `KNOB1` | ain | R-17 knob header, RC filtered (block G) |
| 50 | IOVDD | `+3V3` | P | 100 nF |
| 51 | DVDD | `DVDD_RP` | P | 100 nF + 4.7 µF (second DVDD cap rule) |
| 52 | GPIO41/ADC1 | `KNOB2` | ain | |
| 53 | GPIO42/ADC2 | `KNOB3` | ain | |
| 54 | GPIO43/ADC3 | `KNOB4` | ain | |
| 55 | GPIO44/ADC4 | `IBUS_SENSE` | ain | block B converter output current, 0–3.0 V for 0–1.5 A (2.0 V/A), ≈ 67 kΩ source; 100 nF at the pin |
| 56 | GPIO45/ADC5 | `SPARE_ADC5` | ain | spare analog input (NTCs moved to block D's ADS7038) |
| 57 | GPIO46/ADC6 | `SPARE_ADC6` | ain | spare analog input (NTCs moved to block D's ADS7038) |
| 58 | GPIO47/ADC7 | `SPARE_ADC7` | ain | spare analog input (NTCs moved to block D's ADS7038) |
| 59 | ADC_AVDD | `ADC_AVDD` | P | +3V3 → 10 Ω → 4.7 µF + 100 nF at the pin; power net shared with block G's KNOB_REF (phase 2) |
| 60 | IOVDD | `+3V3` | P | 100 nF |
| 61 | VREG_AVDD | `VREG_AVDD` (+3V3 via 33 Ω / 4.7 µF) | P | |
| 62 | VREG_PGND | GND (two vias, one point) | P | |
| 63 | VREG_LX | L1 | P | |
| 64 | VREG_VIN | `+3V3` | P | C6 4.7 µF |
| 65 | VREG_FB | `DVDD_RP` at COUT | | |
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

### RP2350 pre-boot states (same sweep)

RP2350 pads reset to Hi-Z with a 36–113 kΩ pull-down (§9.3):
- `VDRV_EN`: off via block C's 100 kΩ pull-down.
- `ILIM_SEL0/1`: 00 = 0.44 A via block B's 100 kΩ pull-downs.
- `FPGA_PROGRAMN`: held high by its 4.7 kΩ pull-up (≥ 2.92 V against the pad pull-down).
- `FPGA_SN`: high via its 4.7 kΩ pull-up.
- `FPGA_CCLK`: high via its 1 kΩ pull-up.
- Link pins: Hi-Z.
- `IBUS_SENSE`: ≤ 45 µA into an unpowered pad (closed).

### RP2350 headroom

48 GPIO: 38 used, **10 spare** (GPIO29–32, 37–39, and ADC5–7 / GPIO45–47), freed by moving PHY management and the slow status to the FPGA. The SSPI configuration uses SPI1 (GPIO24–27) with PROGRAMN/INITN/DONE on GPIO22, 23, 28.

## Interface cross-check

| Interface | Needed | Where |
|---|---|---|
| Block D PWM (LMG1210 PWM mode) | 4 | FPGA N1, P1, R2, R4 (bank 6, ODDRX2F) |
| Block D fault latch: AMP_EN ×2, AMP_CLK ×2, AMP_ARM, FAULT_n ×2, DC_n ×2 | 9 | FPGA R5, T4, P2, T2, R1, L1, M1 (bank 6); J1, G1 (bank 7) |
| Block D ADS7042 (VBUS) | CS, SCLK, SDO | FPGA P4, N3, M4 |
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
| Block C PG_5V_N, PG_3V3_N (buffered, active low), PG_3V3Q | 3 | FPGA B3, B4, B5 |
| Block B ILIM_SEL0, ILIM_SEL1 (E → B) | 2 | RP2350 GPIO34, GPIO35 (block B's 100 kΩ pull-downs → reset state 00 = 0.44 A) |
| Block B IBUS_SENSE (B → E, 0–3.0 V = 0–1.5 A, ≈ 67 kΩ source, RC-filtered 3.4 kHz) | 1 analog | RP2350 ADC4 (GPIO44), 100 nF at the pin |
| Block B ACF_PULSE (3.3 V buffered SR-gate copy, 737.28 kHz crystal-locked, one edge per conduction pulse, none in skip) | 1 | FPGA B6 (top bank 0), 4.7 kΩ series (agreed with B); gateware measures f_acf |
| Block C VDRV_EN, VDRV_PG | 2 | RP2350 GPIO36, GPIO33 |
| Block A PD_PG_N, PD_TPH_N, PD_TPL_N, PD_BT_N | 4 | FPGA A2–A5 |
| Block B POE_LOSS_N (VBUS-droop comparator < 39.5 V, open-drain, active low) | 1 | FPGA A6; 4.7 kΩ pull-up on the net (E), 1 kΩ series; the net also drives block F's separate BAT54C (D_PL) to the two relay gates, not an OR into /DC_TRIP |
| PHY RMII + SMI + reset/int | 7 + 4 | FPGA C8, A9–A12, B10, B11; A13, A14, B12, B13 |
| VCXO clock + tune | 2 | FPGA P6, N4 |
| RP2350 ↔ FPGA link | 12 | RP2350 GPIO8–19 ↔ FPGA M7, N7, P7, R7, R6, T6, P8, M8 (D0–D7), M9 (IRQ), M16 (CLK), R15 (DIR), T15 (STB) |
| FPGA configuration (SSPI) | 7 | RP2350 GPIO22–28 ↔ FPGA R9, T9, T7, R8, N9, T8, P9 |
| FPGA JTAG header (R-22) | 4 | FPGA T10, R11, M10, T11 (direct, 3.3 V) |
| Block G I2C, LED data/clock, encoders, knobs, UART, SWD, USB | | RP2350 (unchanged from the Gowin version) |

## Phase 2 schematic (2026-11-08)

The sheets `mcu`, `fpga` and `ethernet` are generated from this file (`hw/satellite/a/gen/e_pins.py`
parses both tables; `lib_E.py` checks every ECP5 ball against the Lattice CSV and every RP2350B pin
name against the table above). Corrections made while drawing:
- RP2350 core net renamed `DVDD_RP` (was written `+1V1`, which is the ECP5 core rail).
- `ADC_AVDD` is now a filtered net: +3V3 → 10 Ω → 4.7 µF + 100 nF (`E-mcu-passives.md`).
- The VCXO's block F branch is the net `MCLK_Q` (block F's existing name).
- MDI centre taps and the yellow LED anode are the power net `ETH_AVDD` (block A asked to use the
  power symbol in place of three labels).
