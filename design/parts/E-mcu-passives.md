# RP2350B passives — core regulator, decoupling, USB, RUN/BOOTSEL

Serves: U-MCU (`E-mcu-rp2350b.md`). Datasheets: `datasheets/hardware-design-with-rp2350.pdf` §2 (regulator, decoupling), §3.1 (QSPI_SS resistors), §5 (USB, debug, buttons), Appendix B schematic (RP2350B Minimal); `datasheets/rp2350-lcsc.pdf` §6.3.8 (via `chips/rp2350.md`), Tab 1441; `datasheets/aota-b201610.pdf`; `datasheets/samsung-mlcc-catalog.pdf`; `datasheets/uniroyal-0402wgf.pdf`.
These values are the Raspberry Pi reference's, copied, not re-derived; the checks below confirm they suit our rails.

## Parts

| Ref (Minimal board) | Function | Value | Part | Supplier line (2026-11-07) | Qty |
|---|---|---|---|---|---|
| L1 | core regulator inductor | 3.3 µH, polarity-marked | AOTA-B201610S3R3-101-T | `C42411119 AOTA-B201610S3R3-101-T (ABRACON, 0806): extended, JLC stock 1758, lifecycle normal` | 1 |
| C6 | VREG_VIN CIN | 4.7 µF X5R 10 V 0402 | CL05A475MP5NRNC | `C23733 CL05A475MP5NRNC (Samsung Electro-Mechanics, 0402): basic, JLC stock 1039966, lifecycle normal` | 1 |
| C7 | COUT (1V1) | 4.7 µF 0402 | CL05A475MP5NRNC | as above | 1 |
| C9 | VREG_AVDD filter | 4.7 µF 0402 | CL05A475MP5NRNC | as above | 1 |
| — | DVDD pin opposite the regulator (second 4.7 µF, datasheet rule) | 4.7 µF 0402 | CL05A475MP5NRNC | as above | 1 |
| R3 | VREG_AVDD RFILT | 33 Ω 0402 | 0402WGF330JTCE | `C25105 0402WGF330JTCE (UNI-ROYAL, 0402): basic, JLC stock 3866748, lifecycle normal` | 1 |
| — | IOVDD ×8, DVDD ×3, ADC_AVDD, USB_OTP_VDD+QSPI_IOVDD (shared) | 100 nF X7R 0402 | CL05B104KO5NNNC | `C1525 … basic, JLC stock 34322291, lifecycle normal` | 13 |
| — | 3V3 bulk at the chip | 10 µF X5R 10 V 0603 | CL10A106KP8NNNC | `C19702 CL10A106KP8NNNC (Samsung Electro-Mechanics, 0603): basic, JLC stock 10318610, lifecycle normal` | 1 |
| R7, R8 | USB_DP/DM series | 27 Ω 0402 | 0402WGF270JTCE | `C25100 0402WGF270JTCE (UNI-ROYAL, 0402): extended, JLC stock 708587, lifecycle normal` | 2 |
| R1 | QSPI_SS pull-up (DNF in reference) | 10 kΩ 0402 | C25744 | `C25744 0402WGF1002TCE (UNI-ROYAL, 0402): basic, JLC stock 22766926, lifecycle normal` | 1 (fit footprint, DNP) |
| R6 | QSPI_SS → BOOTSEL button | 1 kΩ 0402 | C11702 | `C11702 0402WGF1001TCE (UNI-ROYAL, 0402): basic, JLC stock 33763066, lifecycle normal` | 1 |
| — | RUN pull-up | 10 kΩ 0402 | C25744 | as above | 1 |
| — | BOOTSEL and RESET buttons | — | block G (tactile switches) | — | — |

ADC_AVDD gets its own 100 nF and, per R-17, may be fed from a filtered reference (block G / C decide); the pin is on the `+3V3` net otherwise.

## Calculations / checks

- **L1 current**: regulator max 200 mA (RP2350 Tab 2 "VREG_LX max current 200 mA"); L1 Isat 2.4 A min, Irms 2.1 A min (AOTA datasheet) → ≥ 10× margin. DCR 140 mΩ max × 0.2 A = 28 mV. Operating −40…+125 °C including rise. OK.
- **C6/C7/C9 DC bias**: 4.7 µF 10 V X5R 0402 at 3.3 V (33 % of rating) and 1.1 V (11 %). The Samsung catalogue in hand has no DC-bias curve, so no number is quoted; the Raspberry Pi reference uses exactly these 0402 4.7 µF parts and tuned the regulator with them (guide §2.1: "C6, C7 and C9 — 4.7 µF (0402)"), which is the reason to keep them. Reviewer: check Samsung's characteristic data for CL05A475MP5NRNC at 3.3 V.
- **RC filter for VREG_AVDD**: VREG_AVDD draws ~200 µA (guide §2.1): drop 33 Ω × 0.2 mA = 6.6 mV; corner 1/(2π · 33 · 4.7 µF) = 1.03 kHz. As reference.
- **USB 27 Ω**: as reference; with the RP2350's FS driver impedance this meets the 90 Ω/45 Ω requirement (guide §5.1).
- **QSPI_SS / BOOTSEL**: 1 kΩ lets QSPI_SS over-drive the button's pull-down when booting (guide §3.1).
- **RUN**: 10 kΩ × 3.3 V → 0.33 mA when the button is pressed. Also brought to a test point and to the debug header (block G).

## Layout

Transplant the RP2350B Minimal Board's regulator corner and decoupler ring exactly (`chips/rp2350.md` table: L1 (2.0, −7.2), C7 (2.0, −5.55), C6 (2.0, −4.6), C9 (4.2, −5.05, −90°), R (4.2, −6.9, −90°) for the QFN-60; take the B board's own coordinates from RP-006442-DD in phase 2). C6/C7 use the "small pads" 0402 footprint. USB 27 Ω at the chip.
