# U (QSPI flash) — Winbond W25Q128JVSIQ, 16 MB

> **ECP5 update (2026-11-07).** FPGA bitstream ≤ 5.42 Mb = 677.5 KB uncompressed (LFE5-25, max EBR; TN-02039 Tab 4.1). The two bitstream slots become **1 MB each**: map = 8 KB tables + 2 × 6 MB RP2350 + 2 × 1 MB ECP5 + 1.9 MB config/log = 16 MB. **R-56 holds.** There is no FPGA-internal golden image any more; recovery is the A/B rollback plus USB/SWD reflash of the RP2350 flash.


Datasheet: `datasheets/w25q128jv.pdf` (W25Q128JV rev J, 2024-04-25). Read: §1–4 (features, pinout, pin description), §7.1 status registers (QE), §8 instructions used by RP2350 (03h, 0Bh, EBh, 02h, 05h, 06h, 20h, 66h/99h), §9 (abs max, operating ranges, power-up timing, DC, AC), §10 package (SOIC-8 208 mil), §11 ordering. Context: `datasheets/hardware-design-with-rp2350.pdf` §3.
MPN: W25Q128JVSIQ (SOIC-8 208 mil, Industrial −40…+85 °C, "Q" = QE = 1 fixed)
Supplier: `C97521 W25Q128JVSIQ (Winbond Elec, SOIC-8-208mil): basic, JLC stock 69432, lifecycle normal, checked 2026-11-07` (basic part — no setup fee)
Footprint: SOIC-8 5.3 mm (208 mil) body, 1.27 mm pitch (datasheet §10.1, 8-pin SOIC 208-mil, package code S). KiCad `SOIC-8_5.3x5.3mm_P1.27mm`.

This is the reference design's flash (guide §3.1: "W25Q128JVS… the largest memory size that RP2350 can support").

## Absolute max / operating vs our worst case (§9.1, §9.2)

| Parameter | Limit | Ours | OK |
|---|---|---|---|
| VCC | −0.6…4.6 V abs; 3.0–3.6 V for FR = 133 MHz | `+3V3` (QSPI_IOVDD also 3.3 V) | OK |
| Any pin | −0.6 … VCC + 0.4 V | RP2350 QSPI at 3.3 V | OK |
| TA | −40…+85 °C (I) | ≤ 60 °C | OK |
| Read voltage vs program voltage | ±10 % (§9.2 note) | single rail | OK |
| ESD HBM | ±2 kV | on-board only | OK |

## Calculations

**QSPI timing.** RP2350 at 150 MHz, QMI CLKDIV 2 → SCK 75 MHz (period 13.33 ns, high/low 6.67 ns ≥ 45 % PC = 6.0 ns, §9.6 tCLH/tCLL). Fast Read Quad I/O (EBh) allowed to **FR = 133 MHz** at 3.0–3.6 V (§9.6). Read data: tCLQV ≤ 6 ns after SCK↓, hold tCLQX ≥ 1.5 ns. Round trip at the RP2350: SCK output delay + trace (≤ 15 mm, 0.1 ns each way) + 6 ns ≈ 7–8 ns, sampled by QMI on the next SCK↑ with RXDELAY tuned (one sys-clock step = 6.67 ns) → comfortable. Write data: tDVCH ≥ 1 ns, tCHDX ≥ 2 ns — QMI launches on SCK↓, half a period (6.67 ns) setup. 03h (boot probe at ~1 MHz) ≤ fR 50 MHz. OK.
**Bandwidth for streaming bitstreams to the FPGA**: QSPI XIP at 75 MHz × 4 bit = 37.5 MB/s ≫ JTAG at 15 Mbit/s (1.9 MB/s). The flash is not the bottleneck.

**Power-up (§9.3):** VCC(min) to /CS low ≥ tVSL 20 µs; write inhibited below VWI 1.0–2.0 V; tPUW 5 ms before writes. The RP2350 boots well after 20 µs; firmware delays flash writes ≥ 5 ms after reset (trivial).

**Current (§9.5):** standby ICC1 ≤ 60 µA; quad read @104 MHz ICC3 ≤ 20 mA; program/erase ICC4–7 ≤ 25 mA → **design 25 mA** on `+3V3` (through QSPI_IOVDD/VCC).

**Decoupling:** 100 nF X7R 0402 at pin 8 (`C1525`, basic) — as the reference.

**QE bit:** "IQ" parts ship with QE = 1 fixed (§11 ordering note (5); §7.1.4: factory fixed default for IQ/IN/JQ) → /WP and /HOLD are IO2/IO3 from power-up; no pull-ups needed on IO2/IO3 (the reference has none).

**Flash map (R-56: two RP2350 images + two FPGA bitstreams in 16 MB):**

| Region | Size | Contents |
|---|---|---|
| 0x000000 | 8 KB | RP2350 partition table + boot metadata (RP2350 bootrom partition/A-B support) |
| RP2350 image A | 6 MB | firmware slot A |
| RP2350 image B | 6 MB | firmware slot B |
| FPGA bitstream A | 512 KB | ≤ 435 KB max uncompressed (UG290 Tab 3-1), + header/CRC/version |
| FPGA bitstream B | 512 KB | same |
| Config / calibration / room-correction filters | 2 MB | wear-levelled store |
| Log / spare | ~1.5 MB | |
| Total | 16 MB | |

The FPGA's own configuration flash holds the **golden** bitstream (AUTOBOOT), so a third FPGA image exists without using QSPI space (`E-fpga-gw1nr9.md`). 6 MB per RP2350 slot is far above any plausible firmware (RP2350 SRAM is 520 KB; code runs XIP). **R-56 holds** with > 3 MB spare.

## Fine print

- Continuous-read (XIP "M5-4 = 10") mode: the RP2350 bootrom's exit sequence handles W25Q (guide §3.3); keep the SDK's w25q boot2.
- Sector erase 4 KB (20h) and 256 B page program (02h) are what the bootrom flash routines need (guide §3.3) — supported.
- Endurance / retention (§1 features): ≥ 100k erase/program cycles per sector, > 20-year retention — fine for A/B updates.

## Layout

QSPI traces ≤ 15 mm, matched loosely (±3 mm), short stubs; R1/R6 at the flash (guide §3.1); no other nets between flash and RP2350.
