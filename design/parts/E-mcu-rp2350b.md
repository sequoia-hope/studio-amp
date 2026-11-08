# U (MCU) — Raspberry Pi RP2350B (QFN-80)

> **ECP5 update (2026-11-07).** GPIO use changes (`E-pinmap.md`): GPIO22–28 now carry the ECP5 slave-SPI configuration (PROGRAMN, INITN, SPI1 MISO/SN/SCK/MOSI, DONE) instead of JTAG; PHY management moved to the FPGA; the I2C expander is dropped. After the review fixes: 38 of 48 GPIO used, 10 spare (`E-pinmap.md` is authoritative).


Datasheets: `datasheets/rp2350-lcsc.pdf` (RP2350 Datasheet, 1380 pp). Read: Ch.1 (pinout QFN-80 Fig 3, pin descriptions Tab 2, GPIO function tables Tab 3–5), §6 power (IOVDD/QSPI_IOVDD, regulator), §9.3 GPIO reset state, §14.9 electrical (abs max Tab 1433, ESD, thermal, IO DC Tab 1436, supplies Tab 1441, power consumption Tab 1443–1446), §6.3.8 regulator layout rules (as summarised in `chips/rp2350.md`). `datasheets/hardware-design-with-rp2350.pdf` (Release 3, 2026-08-20). Read: all (power, regulator, decoupling, flash, crystal, USB, debug, buttons, both schematics).
MPN: RP2350B (no internal flash)
Supplier: `C42415655 RP2350B (Raspberry Pi, QFN-80-EP(10x10)): extended, JLC stock 2205, lifecycle normal, checked 2026-11-07`
Footprint: QFN-80 10 × 10 mm, 0.4 mm pitch, EP 3.4 × 3.4 mm — KiCad `QFN-80-1EP_10x10mm_P0.4mm_EP3.4x3.4mm` (matches the vendor footprint by translation, `chips/rp2350.md`; pad inner ends ±4.55 mm vs vendor ±4.51 mm). The power block is **transplanted from the RP2350B Minimal Board (RP-006442-DD)**, per `chips/rp2350.md`.

## Absolute max vs our worst case (Tab 1433, 1441)

| Parameter | Limit | Ours | OK |
|---|---|---|---|
| IOVDD, QSPI_IOVDD | 1.62–3.63 V operating | `+3V3` ≤ 3.40 V | OK |
| VREG_VIN | 2.7–5.5 V | `+3V3` | OK |
| VREG_AVDD, USB_OTP_VDD | 3.135–3.63 V | `+3V3` via 33 Ω/4.7 µF RC (AVDD) | OK |
| ADC_AVDD | 1.62–3.63 V (≥ 2.97 V for full ADC performance) | `+3V3` (block G's clean reference proposal R-17; see interfaces) | OK |
| DVDD | 1.05–1.16 V | internal regulator 1.1 V | OK |
| Pin voltage (standard IO) | −0.5 … IOVDD + 0.5 V | ≤ 3.3 V everywhere (all ECP5 banks at 3.3 V) | OK |
| Pin voltage (FT pins) at IOVDD 3.3 V | 5.5 V | not used above 3.3 V | OK |
| Tj | −40…125 °C; ambient (TC) −40…85 °C | ≤ 60 °C | OK |
| Total IOVDD source current | 100 mA | link 8 lines + LED/ENC/etc. ≪ 100 mA | OK |
| QSPI_IOVDD total | 20 mA | one flash | OK |
| ESD | HBM 2 kV (4 kV FT), CDM 500 V | USB (block G ESD), debug header (series R) | OK |

## I/O levels relevant to the interfaces (Tab 1436, IOVDD 3.3 V)

VIH ≥ 2.0 V, VIL ≤ 0.8 V, VOH ≥ 2.62 V, VOL ≤ 0.5 V, pull-up 32–86 kΩ, pull-down 36–113 kΩ. → every signal to/from the ECP5 is 3.3 V LVCMOS; no translation is needed.
Reset state (§9.3): output Hi-Z, input buffer disabled, **pulled low**, isolation latched. → `VDRV_EN` and `ILIM_SEL0/1` default to their safe state (off / 0.44 A), with the external pull-downs blocks C and B fit; `FPGA_PROGRAMN` is never driven low by reset (the 4.7 kΩ pull-up wins over the 36–113 kΩ pad pull-down).

## Required external parts (Hardware design with RP2350 + `chips/rp2350.md`) → `E-mcu-passives.md`, `E-xtal-12mhz.md`, `E-flash-w25q128.md`

- Regulator: L1 AOTA-B201610S3R3-101-T 3.3 µH (polarity-marked, reference rotation), C6 CIN 4.7 µF 0402, C7 COUT 4.7 µF 0402, C9 CFILT 4.7 µF 0402, R RFILT 33 Ω 0402 (VREG_AVDD), second 4.7 µF on the DVDD pin opposite the regulator.
- Decoupling: 100 nF per IOVDD/DVDD pin; pins 68 (USB_OTP_VDD) and 69 (QSPI_IOVDD) may share one 100 nF (guide §2.2.1).
- USB_DP/DM: 27 Ω series each, close to the chip (guide §5.1); 90 Ω differential.
- Crystal 12 MHz ABM8-272-T3 with 15 pF ×2 and 1 kΩ series in XOUT (guide §4).
- QSPI flash W25Q128JVSIQ; QSPI_SS: 10 kΩ pull-up position (DNF per guide) and 1 kΩ to the BOOTSEL button.
- RUN: 10 kΩ pull-up + reset button/test pad (guide §5.4); SWD to the Debug Probe header (block G).

## Calculations

- **3V3 current (Tab 1446 measured; regulator max 200 mA)**: typical VREG_VIN 11–15 mA at 150 MHz (CoreMark, hello_*), IOVDD ~0.5 mA idle + switching; USB_OTP_VDD ≤ 6 mA during boot. Worst case: DVDD 200 mA × 1.1 V / (3.3 V × 0.8 assumed efficiency) = 83 mA at VREG_VIN. IOVDD with the link at 37.5 MHz: 8 × 15 pF × 3.3 V × 37.5 MHz × 0.5 = 7.4 mA, + LED/encoders/I2C ≈ 5 mA. **Design 100 mA worst, 45 mA typical on `+3V3`.**
- **GPIO budget**: `E-pinmap.md` — 38 of 48 GPIO used, 10 spare (GPIO29–32, 37–39, ADC5–7).
- **ADC**: 8 inputs on GPIO40–47 (QFN-80 only, §1.2.3 note) = 4 knobs (ADC0–3) + `IBUS_SENSE` (ADC4, block B) + 3 spare. The NTCs moved to block D's ADS7038.

## Fine print / gotchas

- RP2350B ADC pins are GPIO40–47 (not 26–29 as on the A).
- If IOVDD < 2.5 V the VOLTAGE_SELECT registers must change; we run 3.3 V, defaults are right (Tab 1441 note a). Never set the 1.8 V thresholds at 3.3 V ("may result in damage", §9.6 Pads).
- QSPI XIP "continuous read" modes: the bootrom's XIP-exit sequence works with W25Q; keep boot2 standard (guide §3.3).
- GPIO0 defaults low at power-up — irrelevant (we don't use QMI CS1 on GPIO0).
- Inductor orientation matters (guide §2.1); thin JLC stock historically (`chips/rp2350.md`): today 1758 in stock.

## Layout (from `chips/rp2350.md`; transplant, don't redraw)

- Regulator corner (pins 61–65): L1, C6, C7, C9, R on the chip's side, at reference positions; LX cut-out on the adjacent plane; PGND to GND through two adjacent vias only; CFILT its own GND via.
- 1V1 ring and 3V3 band zones; stubs to every IOVDD pin (5, 15, 24, 29, 41, 50, 60, 76), plus 64 (VREG_VIN), 68, 69.
- Keep the PIO link bank (GPIO8–19, pins 6–19 left edge) facing the FPGA; QSPI (pins 69–75, top) to the flash ≤ 15 mm; USB (66/67) toward block G's USB-C.

## Open questions

- None for the chip; the board-level decisions are in `E-link.md` and `E-pinmap.md`.
