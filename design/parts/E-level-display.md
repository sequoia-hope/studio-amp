> **SUPERSEDED by ECP5 (user, 2026-11-07).** The FPGA is now the Lattice LFE5U-25F-7BG256I; see `E-fpga-ecp5.md`, `E-pinmap.md`, `E-interfaces.md`. Kept for the record; do not build from this file.

# U (display up-translator) — TI SN74AVC4T774PWR ×2

Datasheet: `datasheets/sn74avc4t774.pdf` (SCES693D, 2015). Read: as in `E-level-jtag.md` (same part).
MPN: SN74AVC4T774PWR (TSSOP-16)
Supplier: `C129363 SN74AVC4T774PWR (TI, TSSOP-16): extended, JLC stock 20278, lifecycle normal, checked 2026-11-07`
Qty: 2 (8 channels). Same part as the JTAG translator → one BOM line, 3 off per board (21 for 7 boards, 20278 in stock).

## Why

The 8-pin ST7735S display header (R-20) needs SCL, SDA, RES, DC, CS, BLK from FPGA I/O at 3.3 V. The 3.3 V FPGA banks (1, 2) are full (`E-pinmap.md`), so the display signals come from bank 3, which outputs 1.8 V, and are up-translated.

Considered and rejected: the single-supply SN74LV4T125 (C90755, inputs "designed to match 1.8-V logic at VCC = 3.3 V", DC VIH ≤ 1.35 V). Its §7.7 noise characteristics give a **dynamic VIH(D) ≥ 2.31 V** under simultaneous switching (VCC 3.3 V, 50 pF), which 1.8 V inputs cannot meet; with four display lines switching together that is a real margin problem. The dual-supply AVC4T774 references its inputs to the 1.8 V side and has no such limit.

## Connection

- **A port = 1.8 V (FPGA)**: VCCA = `+1V8`; A1–A4 from FPGA pins 81–86 (bank 3). **B port = 3.3 V (display header)**: VCCB = `+3V3`.
- DIR1–4 = H (A → B) tied to VCCA (control pins are referenced to VCCA, §5). **OE tied to GND through a 0 Ω link** (always enabled; the power-up Hi-Z pull-up of §5 isn't needed here because the B side only drives display inputs). During FPGA configuration the A inputs see the FPGA's weak pull-ups (UG290 App. A), so the display lines idle high: CS deasserted, RES released, BLK on. If block G wants the backlight off during boot, a pull-down on the A side of BLK must beat the FPGA's ≤ 150 µA weak pull-up and stay below VIL = 0.35 × 1.8 V = 0.63 V: R ≤ 0.63 V / 150 µA = 4.2 kΩ → **2.2 kΩ** (0.33 V).
- Channel allocation: part 1 = SCL, SDA, DC, CS; part 2 = RES, BLK, `MADC_LRCK` (ch 7, from FPGA pin 3: the PCM1808 LRCK at 48 kHz for block F; a few ns of translator delay is negligible against its 325 ns BCK period), `SPARE_3V3_OUT` (ch 8, from FPGA pin 16: a spare 3.3 V FPGA output; block G may route it to a header position for pin-order remapping, R-20). Give the ch 8 A input a 100 kΩ pull-down as a backstop (unused CMOS inputs must not float, §7.3 note 3).

## Ratings vs use

| Parameter | Datasheet (§7.3, §7.5) | Ours | OK |
|---|---|---|---|
| VCCA / VCCB | 1.2–3.6 V | 1.8 / 3.3 V | OK |
| VIH data, VCCI 1.2–1.95 V | ≥ 0.65 × VCCI = 1.17 V | FPGA VOH ≥ 1.4 V | OK, ≥ 0.23 V |
| VIL data, VCCI 1.2–1.95 V | ≤ 0.35 × VCCI = 0.63 V | FPGA VOL ≤ 0.4 V | OK |
| Output VOH at VCCB 3.0 V, −8 mA (B port) | per §7.5 table (≥ 2.3 V class) | display input + 100 Ω series (block G), µA DC | OK |
| Data rate 1.8 → 3.3 V | 380 Mbps typ | SPI ≤ 15 MHz, BLK PWM ≤ 100 kHz | OK |
| Ioff / VCC isolation | if either VCC = 0, both ports Hi-Z | display may be powered while 1V8 is not, safely | OK |

## Calculations

- Decoupling: 100 nF on each VCCA and VCCB per part (`C1525`, basic) → 4.
- Current: static ICC µA-class; switching at 15 MHz × 4 lines × 15 pF × 3.3 V × 0.5 ≈ 1.5 mA from `+3V3`.
- Bank-3 drive: set 4 mA (enough for one CMOS input; slower edges, less ground bounce on the 1.8 V rail).

## Layout

Translators next to the display header (block G), series resistors (block G) after the B outputs; the 1.8 V traces from FPGA pins 81–86 run along the FPGA's top edge.
