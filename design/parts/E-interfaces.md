# Block E — interfaces, rail loads and proposed changes (ECP5 version)

FPGA is now the Lattice **LFE5U-25F-7BG256I** (user, 2026-11-07). The Gowin version of this file is `E-interfaces-gowin.md` (superseded).
Block E: RP2350B + W25Q128JVSIQ + 12 MHz crystal (`E-mcu-*.md`, `E-flash-w25q128.md`, `E-xtal-12mhz.md`); ECP5 (`E-fpga-ecp5.md`, `E-fpga-ecp5-passives.md`); LAN8720AI (`E-phy-*.md`); 50 MHz RMII oscillator (`E-clk-rmii-50mhz.md`); 24.576 MHz VCXO (`E-clk-audio-vcxo.md`); link (`E-link.md`); pins (`E-pinmap.md`).

## Proposed changes to architecture

1. **FPGA: ECP5 LFE5U-25F-7BG256I (C1550762), configured over slave SPI from the RP2350** (CFGMDN = 001). This is architecture decision 2 as first written: no FPGA flash, A/B bitstreams in the RP2350's QSPI flash. Bitstream ≤ 5.42 Mb (677.5 KB) → 2 × 1 MB slots + 2 × 6 MB RP2350 images fit 16 MB (R-56). Load ≈ 0.15 s at 37.5 MHz. Update the block diagram's FPGA box ("GW1NR-LV9QN88" → "LFE5U-25F caBGA-256"). The Gowin golden-image/JTAG scheme, the 1.8 V bank and the level translators are dropped.
2. **Rails change for block C:** `+1V1` (new, ECP5 core) replaces `+1V2`; `+2V5` (new, VCCAUX); **`+1V8` is no longer needed** by block E. All FPGA I/O banks on `+3V3`.
3. **PCB: 6 layers recommended** for the caBGA-256 fan-out (0.8 mm pitch; configuration/JTAG balls the silicon fixes sit in ball rings 3–4). No via-in-pad; dog-bone vias 0.20/0.45 mm (JLC's smallest without surcharge). Decision for phase 4/5 (R-70 already allows 6). A 4-layer board is possible but loses the under-BGA decoupling side.
4. **PWM edge grid 1.453 ns** (ODDRX2F at 688 Mb/s on the −7 grade; 700 Mb/s limit) instead of the Gowin's 1.017 ns. R-53's "≤ 1 ns" physical target is not met; block D's noise-shaper analysis must take 1.453 ns (≈ 3 dB more raw quantisation noise than 1.017 ns). PWM frequencies on this grid: 672, 512 or 448 kHz.
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
| A | `PD_PG`, `PD_TPH_N`, `PD_TPL_N`, `PD_BT_N` | FPGA A2–A5 (top bank 0) | 3.3 V from the isolator, 1 kΩ series |
| A | MDI pairs | PHY ↔ RJ45 magnetics | unchanged (`E-phy-*.md`) |
| B/C | `POE_LOSS_N` | FPGA A6 | 3.3 V, 1 kΩ series |
| C | `PG_5V`, `PG_3V3` | FPGA B3, B4 | PG_5V is a 3.24 V divider (not open-drain); PG_3V3 has block C's 100 kΩ pull-up. No pull-ups on our side |
| C/F | `PG_3V3Q` | FPGA B5 (top bank 0) | TPS7A94 PG, open-drain, block C's 100 kΩ pull-up; 1 kΩ series. **Gateware rule:** hold `DAC_L0–3`, `DAC_R0–3` low while PG_3V3Q is low (74LVC74A has no Ioff); start the streams only after it goes high. Before configuration the ECP5's weak pull-downs keep them low as well |
| C | `VDRV_EN`, `VDRV_PG` | RP2350 GPIO36, GPIO33 | VDRV_EN with block C's 100 kΩ pull-down |
| C/G | `LED_EN`, `QWIIC_PWR_EN` | FPGA H15, J16 | default low (FPGA pull-down); 100 kΩ pull-down at EN as backstop |
| C/G | `LED_FAULT_N`, `QWIIC_FAULT_N` | FPGA K16, C14 | open-drain; block C fits the 10 kΩ pull-ups at the TPS2553s; 1 kΩ series |
| D | `PWM_W_A`, `PWM_W_B`, `PWM_T_A`, `PWM_T_B` | FPGA N1, P1, R2, R4 (bank 6) | LMG1210 PWM mode (high = HS on), ODDRX2F, 1.453 ns grid, matched routing, 100 Ω at the driver (block D); baseline fsw 448 kHz (1536 steps), 672 kHz per-build option |
| D | `FAULT_W_n`, `FAULT_T_n` | FPGA L1, M1 | from block D's 74LVC1G74 fault latch path (gates already off in hardware when low); 330 Ω series, partners NC |
| D | `DC_W_n`, `DC_T_n` | FPGA J1, G1 (bank 7) | open-drain + 10 kΩ pull-up at D; 1 kΩ series, partners NC |
| D | `AMP_CLK_W`, `AMP_CLK_T`, `AMP_ARM` | FPGA P2, T2, R1 | ARM has block D's 10 kΩ pull-down (agrees with the ECP5 default pull-down) |
| D | `AMP_EN_W/T` | FPGA R5, T4 | fault-latch D inputs; default low |
| D | ADS7042 `VB_CS_n/VB_SCLK/VB_SDO` | FPGA T3, N3, M4 | ≤ 16 MHz, own bus, PWM-synchronous |
| D | ADS7038-Q1 `IS_CS_n/IS_SCLK/IS_SDI/IS_SDO` | FPGA L3, M3, R3, P3 | ≤ 60 MHz; channels 4–7 carry the four NTCs (block D's proposal, accepted) |
| D | 2 × ADS8353 `PF_CS_n/PF_SCLK/PF_SDI/PF_SDO_WA/WB/TA/TB` | FPGA K4, L4, K5, L5, M5, N5, N6 | optional population; pins reserved (R-51). All three CS lines have 4.7 kΩ pull-ups |
| D | NTCs ×4 | via the ADS7038-Q1 to the FPGA | RP2350 ADC4–7 are now spare |
| F | `DAC_L0–3`, `DAC_R0–3` | FPGA bank 3 (N16, P15, P16, R16, R13, T14, R12, T13) | launched on MCLK↓, tCO ≤ 6.1 ns (≤ 12 ns asked) |
| F | VCXO → `MCLK_Q` buffer → FFs + PCM1808 SCKI | E → F, own 33 Ω branch | phase noise not specified by the VCXO datasheet (see `E-clk-audio-vcxo.md`) |
| F | `MADC_BCK`, `MADC_LRCK` (out), `MADC_DOUT` (in) | FPGA P13, R14, L16 | DOUT 330 Ω series, partner NC |
| F | `PDM_CLK` (out), `PDM_DAT` (in) | FPGA L14, N13 | DAT 330 Ω series, partner NC |
| F | `HP_EN`, `LO_EN` (out), `HP_FAULT_N`, `HP_DET` (in) | FPGA M14, N14, P11, K13 | relay enables are FPGA pins (no expander); block F drives each gate through 10 kΩ with 100 kΩ pull-downs. **Gateware drops HP_EN/LO_EN within µs of `POE_LOSS_N` or `PD_PG` falling** (both are FPGA inputs, no firmware in the path). Block F's diode-OR of PoE-loss into /DC_TRIP is also welcome as a hardware backstop. Inputs 1 kΩ series, partners NC |
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
- 2.4 MHz switching: harmless to the 12 MHz crystal, 50 MHz XO and 24.576 MHz VCXO. Keep the bucks' switch nodes away from the VCXO tune RC and the oscillators' supply pins.
- 3V3 total 0.72 A with Qwiic and display (block C's figure): OK. Block E's share stays ≈ 350 mA design.
- The I2C address 0x20 reservation can be released: the TCA9535 is dropped with the ECP5.
- Block F's MCLK_Q buffer (SN74LVC2G34, Ioff-rated) puts about 3.5 pF on our VCXO branch: fine within the 15 pF budget.

### Block C/G update received 2026-11-07 (accepted)

- `+1V1` TPS62A02AP at 1.107 V (1.088–1.127 V), `+2V5` TPS7A9401 at 2.505 V ± 1 % (ramp ≈ 2 mV/µs), both enabled from PG_3V3 ≈ 1 ms after 3V3: meets DS-02012 Tab 3.2/3.3 and TN-02038 §4. `+3V3` at 3.24–3.40 V with 0.5 % resistors: under VCCIO max 3.465 V. `+1V8` withdrawn.
- Typical `+1V1`: my estimate is ≈ 250 mA (77 mA static + dynamic; not from a power calculator). Block C's 0.2 A assumption is a little low; size for the 400 mA design figure.
- JTAG pulls (TDI/TMS/TDO 4.7 kΩ up, TCK 4.7 kΩ down) are on **this** block's sheet, at the FPGA (`E-fpga-ecp5-passives.md`); block G should not fit a second set at the header.
- Display BLK through 47 Ω at 16 mA: within the LVCMOS33 16 mA drive setting (VOH ≥ VCCIO − 0.4 V at 16 mA, DS-02012 Tab 3.12). The sysI/O guide (TN-02032 §4.11.1) says to respect "the maximum allowable current per bank" but none of the documents in hand gives a number. Bank 2's DC load is BLK ≤ 16 mA + µA-level CMOS inputs, so ≈ 17 mA. Block G adopted a FET backlight switch driven by `DISP_BL_PWM` (G15, 4 mA), so the steady 16 mA is off VCCIO2.
- USB-only mode (≈ 0.48 A at 5 V at design load): block E's typical share is ≈ 0.9 W (≈ 0.2 A at 5 V). Firmware should keep the PHY in reset (−90 mA on 3V3) and LEDs/Qwiic off when only USB is present.

## Gateware rules collected from other blocks

- **Block F:** hold `DAC_L0–3`, `DAC_R0–3` low until `PG_3V3Q` (B5) is high. **Drop `HP_EN` and `LO_EN` within ≤ 1 ms of `PD_PG` low or `POE_LOSS_N` low**, in gateware, independent of the RP2350 (R-34). In practice this is a combinational/registered path of a few clock cycles: µs.
- **Block D:** the 11 items in `D-interfaces.md` "Gateware requirements arising from block D". In short:
  - start-up only ≥ 200 µs after `VDRV_PG`, through ARM → EN → latch clock, then PWM held low ≥ 50 µs, then 50 % duty;
  - re-arm only after `FAULT_x_n` is high again;
  - duty clamp 3–97 %, minimum leg pulse ≥ 36 ns (= 25 steps of 1.453 ns);
  - dead-time compensation from the current sign;
  - bus feed-forward from the ADS7042;
  - software DC detector, ≥ 15 Hz subsonic high-pass, HF/Zobel limiter;
  - thermal derate/shutdown from the NTCs;
  - auto-idle.
  `VDRV_PG` is an RP2350 input (GPIO33), so the RP2350 passes "VDRV good" to the FPGA over the link, or the FPGA can take a copy on a spare top-bank ball. That is a phase 2 detail with no pin cost.

## Noise shaper at 448 kHz (block D's question)

At fixed shaper order L, in-band quantisation noise scales as Δ² / OSR^(2L+1), where Δ is the duty-cycle step relative to full scale.
- Going from 672 to 448 kHz: Δ falls by 1.5 (1/1536 instead of 1/1024 of the period), and OSR falls by 1.5.
- Net change: 1.5^(2L+1) / 1.5² = **1.5^(2L−1)**. That is +12.3 dB at L = 4 and **+15.8 dB at L = 5**. One more shaper order recovers it: at an OSR of about 11 (448 kHz / 2 / 20 kHz) each added order lowers ideal in-band noise by roughly OSR² ≈ 20 dB, less the order-dependent constant.
- The absolute in-band level, and whether a 5th–7th-order shaper stays stable with the LC filter response, have to come from the phase 1 noise-shaper simulation; they can't be settled from datasheets.
- Recommendation: keep 448 kHz as block D's baseline for losses. **Size the shaper for 448 kHz first**, and fall back to 512 kHz (better by (512/448)^(2L−1) = 1.143^9 ≈ 5.2 dB at L = 5) if the 448 kHz design can't hold the R-51 noise floor. This is now an open item for the noise-shaper analysis, with block D.

## Things needing a user decision

- **6-layer board** for the BGA (proposed; no via-in-pad, no via surcharge).
- **Edge resolution 1.453 ns vs R-53's ≤ 1 ns**: accept, and let the noise shaper make it up, or ask for a −8 part (800 Mb/s, 1.25 ns), which has only 5 in stock at LCSC.
- **MCLK_Q jitter** (block F): the VCXO datasheet gives no phase-noise figure, so ≤ 1 ps over 20 kHz–12 MHz is unverified. The fallback is a land shared with a 0.7 ps fixed XO (C5203547), which loses the PTP lock of the DAC clock.
