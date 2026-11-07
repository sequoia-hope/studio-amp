> **SUPERSEDED by ECP5 (user, 2026-11-07).** The FPGA is now the Lattice LFE5U-25F-7BG256I; see `E-fpga-ecp5.md`, `E-pinmap.md`, `E-interfaces.md`. Kept for the record; do not build from this file.

# U (I/O expander) — TI TCA9535PWR, 16-bit I2C GPIO

Datasheet: `datasheets/tca9535.pdf` (TI TCA9535). Read: §1–7 (features, description, pin functions, abs max, recommended operating, electrical, I2C timing, switching), §8 (detailed description: registers, address byte, power-on reset, interrupt), §9–11 (application, power, layout).
MPN: TCA9535PWR (TSSOP-24)
Supplier: `C130204 TCA9535PWR (TI, TSSOP-24): extended, JLC stock 19437, lifecycle normal, checked 2026-11-07`
Footprint: TSSOP-24 4.4 mm, 0.65 mm pitch (PW).

## Why

Block C asked for 8 signals (PG_5V, PG_3V3, VDRV_EN, VDRV_PG, LED_EN, QWIIC_PWR_EN, LED_FAULT_N, QWIIC_FAULT_N). Block F asked for HP_EN, LO_EN, HP_FAULT_N and HP_DET in addition to its 12 fast FPGA pins. Both MCU and FPGA were already near full (`E-pinmap.md`). Everything slow (ms response is enough) goes onto one expander on the RP2350's internal I2C1 bus, on the RP2350 side of block G's Qwiic buffer. `VDRV_EN` and `VDRV_PG` stay on direct RP2350 GPIOs because they gate amplifier start-up.
**TCA9535, not TCA9555:** the '9535 "does not include the internal I/O pull-up resistor" (§1 description). At power-on all I/Os are inputs (pin table: "At power on, Pxx is configured as an input"), so every output-role pin is Hi-Z until firmware sets it. An external pull-down therefore defines the off state of each enable. The '9555's internal pull-ups would fight those pull-downs.

## Ratings vs use

| Parameter | Datasheet | Ours | OK |
|---|---|---|---|
| VCC | 1.65–5.5 V | `+3V3` | OK |
| P-port VIH / VIL | ≥ 0.7 × VCC = 2.31 V / ≤ 0.3 × VCC = 0.99 V | 3.3 V CMOS / open-drain with 10 kΩ pull-ups | OK |
| P-port tolerance | 5.5 V ("5-V tolerant I/O ports") | ≤ 3.3 V (VUSB_DET divided) | OK |
| IOL per pin | 18 mA (Tj ≤ 85 °C) | µA (enable inputs) | OK |
| I2C | 400 kHz fast mode | 400 kHz | OK |
| TA | −40…85 °C | ≤ 60 °C | OK |
| Power-on reset | VPORR 1.2–1.5 V | — | |

## Configuration

- Address: byte 0 1 0 0 A2 A1 A0 (§8 address figures); A2 = A1 = A0 = GND → **0x20**. Block G must not put another 0x20 device on the internal side.
- INT (open-drain, active low): 10 kΩ pull-up to `+3V3` → RP2350 GPIO32 `EXP_INT_N`. Interrupt valid ≤ 4 µs after a port change (tiv); firmware reads both input ports within ~100 µs at 400 kHz.
- Port allocation: table in `E-pinmap.md`.
- Pull resistors (`C25741` 100 kΩ, `C25744` 10 kΩ, basic; listed in `E-pinmap.md`): 100 kΩ pull-downs on LED_EN, QWIIC_PWR_EN, HP_EN, LO_EN and the spare P17; 10 kΩ pull-ups on the open-drain faults (block C/F may already fit them at the source; fit once only).
- Decoupling: 100 nF at VCC (`C1525`, basic).

## Calculations

- Off-state of the enables: Hi-Z expander pin + 100 kΩ to GND → 0 V. The TPS2553 EN threshold sits in block C's audit. Leakage ≤ ±1 µA (IIH/IIL) × 100 kΩ = 0.1 V worst case.
- I2C load: one more device on the internal bus, CI ≤ 8 pF.
- Latency for `HP_FAULT_N`: 4 µs INT + ~70 µs I2C read + ISR → < 0.2 ms. Block F's headphone stage must protect itself in hardware (current limit). This line only reports and shuts down.
- ICC: standby µA, < 1 mA at 400 kHz.

## Fine print

- "Requires pull-ups and pull-downs on unused I/O pins when configured as an input and undriven" (§1) → P17 has a pull-down.
- Outputs are push-pull once configured. Never connect an expander output to an open-drain bus.
