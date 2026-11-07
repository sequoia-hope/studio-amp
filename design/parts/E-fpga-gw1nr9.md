> **SUPERSEDED by ECP5 (user, 2026-11-07).** The FPGA is now the Lattice LFE5U-25F-7BG256I; see `E-fpga-ecp5.md`, `E-pinmap.md`, `E-interfaces.md`. Kept for the record; do not build from this file.

# U (FPGA) — Gowin GW1NR-LV9QN88PC6/I5

Datasheets (all read for the sections cited; text extracted with pdftotext):
- `datasheets/gowin-DS117E.pdf` — GW1NR series datasheet DS117-3.2.5E. Read: §1 (features, resources, packages), §2.2 (PSRAM), §2.4 (I/O standards, IODELAY, SER/DES), §3 (abs max, recommended operating, ramp, POR, DC, static current, gearbox, I/O Fmax, PLL, oscillator), §4 (part naming).
- `datasheets/gowin-UG803E.pdf` — GW1NR-9 Pinout UG803-1.6.5E. Read: all (pin definitions, power table per package, full pin list; QN88P column extracted by script and checked by hand for every bonded pin).
- `datasheets/gowin-UG119E.pdf` — GW1NR Package & Pinout UG119-1.8.4E. Read: §2.4.3 pin quantities, §3.3.2 QN88P other pins, §4.1 package outline and recommended land pattern.
- `datasheets/gowin-UG290E.pdf` — Programming & configuration UG290-2.9.2E. Read: §3.3–3.5 (bitstream size, load time, background upgrade), §4 (config pins, reuse, function), §5.1 (LittleBee modes), §7.2 (JTAG mode, timing, TCK limits, SRAM/eFlash flows), §7.4 (SSPI), Appendix A (pin states per stage).
- `datasheets/gowin-UG284E.pdf` — GW1N/GW1NR Schematic Manual UG284-2.0.8E. Read: all (power ramp, filtering, JTAG, MSPI, SSPI, clock pins, READY/RECONFIG_N/DONE, MODE, JTAGSEL_N).
- `datasheets/gowin-UG286E.pdf` — Clock UG286-2.0.2E. Read: §5.1 rPLL (formulas, parameter ranges).
- `datasheets/gowin-UG289E.pdf` — Programmable IO UG289-2.2.1E. Read: §3 (banking), §4 (I/O logic, OSER4/8/10/16, IDES, device support notes).
- `datasheets/gw1nr-9-lcsc.pdf` — LCSC's copy (Chinese edition of DS117), kept as the supplier record only.

MPN: GW1NR-LV9QN88PC6/I5
Supplier: `C5799578 GW1NR-LV9QN88PC6/I5 (GOWIN, QFN-88): extended, JLC stock 124, lifecycle normal, checked 2026-11-07`
Build quantity: 5 boards + attrition → 7. Stock 124: OK, but it is the **only** GW1N(R)-9 in stock on LCSC; buy the 7 (plus spares for a Tang Nano 9K-style test board if wanted) at order time.

Decoding the MPN (DS117 §4.1 Fig 4-2): GW1NR · **LV = 1.2 V core** · 9 = 8,640 LUT4 · **QN88P = QFN-88 with embedded PSRAM** (64 Mbit, 2 × 32 Mbit) · C6/I5 speed grade. This is the Sipeed Tang Nano 9K part. **Core voltage confirmed 1.2 V (LV)**: VCC rec. 1.14–1.26 V, abs max 1.32 V (DS117 Tab 3-1/3-2).

Footprint: QFN-88, 10 × 10 mm, 0.4 mm pitch, 0.20 × 0.85 mm leads, **EP land 6.8 × 6.8 mm** (UG119 Fig 4-2, D2 = E2 = 6.8, P = 9.90, L = 0.85, b = 0.20). Body height 0.75 mm nom for the QN88P (UG119 §4.1 note). KiCad has no stock QFN-88 10×10 with this EP; build a project footprint from UG119 Fig 4-2 in phase 2 and check it against the outline drawing.

## Resources (DS117 Tab 1-1, 1-3; UG119 Tab 2-6)

| | GW1NR-9 QN88P |
|---|---|
| LUT4 / FF | 8,640 / 6,480 |
| BSRAM | 26 × 18 kbit = 468 kbit; SSRAM 16 kbit |
| User flash | 608 kbit (plus the configuration flash used by AUTOBOOT) |
| Multipliers 18×18 | 20 |
| PLLs | 2 (rPLL left, right) |
| PSRAM | 64 Mbit embedded, on bank 3 (1.8 V) |
| User I/O | 71 incl. configuration pins: bank 1 = 25, bank 2 = 23, bank 3 = 23 (of which 8 are JTAG/JTAGSEL_N/RECONFIG_N/MODE) |

## Absolute max vs our worst case

| Parameter | Abs max (DS117 Tab 3-1) | Our worst case | Margin |
|---|---|---|---|
| VCC (LV) | 1.32 V | 1.2 V + 2 % reg + 3 % ripple ≈ 1.26 V | OK, 60 mV |
| VCCIO1/2, VCCX/VCCIO0 | 3.75 V | 3.3 V + 3 % = 3.40 V | OK |
| VCCIO3 | 3.75 V abs, but **1.71–1.89 V operating** because VCCIO3 powers the PSRAM die (UG803 power sheet, QN88P) | 1.8 V ± 3 % | OK only on a 1.8 V rail |
| I/O voltage applied | 3.75 V; overshoot −2 V to VIHMAX+2 V for < 20 ns | 3.3 V signals into bank-3 inputs (overdrive mode, below) | OK; leakage ≤ 210 µA per pin (Tab 3-8, VCCIO < VIN < VIH(MAX)) |
| Tj | −40…+125 °C abs; I-grade operating −40…+100 °C | 55 °C cabinet air + self-heating (< 0.5 W) | OK |
| ESD | HBM > 1 kV, CDM > 500 V (QN88, Tab 3-6/3-7) | inward headers only; RJ45/USB are not on FPGA pins | OK with series R on header lines (block G) |

## Power pins and rails (UG119 Tab 3-8; UG803 power sheet "QN88P")

| Pin(s) | Rail | Range | Notes |
|---|---|---|---|
| 1, 22, 45, 66 | VCC → `+1V2` | 1.14–1.26 V, ripple ≤ 3 % | via ferrite bead + 4.7 µF (UG284 Fig 2) |
| 64, 67, 78 | VCCX/VCCIO0 → `+3V3` | 2.375–3.6 V; **VCCX ≥ VCCIO** | VCCX and VCCIO0 are internally shorted in QN88P; bank 0 has no bonded I/O |
| 58 | VCCIO1 → `+3V3` | 1.14–3.6 V | bank 1 (right side + top-right) |
| 23, 44 | VCCIO2 → `+3V3` | 1.14–3.6 V | bank 2 (bottom) |
| 12 | VCCIO3 → **`+1V8` (new rail)** | **1.71–1.89 V** | bank 3 (left + top-left) and the embedded PSRAM |
| 2, 21, 24, 43, 46, 65, EPAD | GND | | EPAD "highly recommended" to GND (UG803) |

Ramp (DS117 Tab 3-3): VCC 0.6–6 mV/µs (**1.2 V in 0.2–2 ms**), VCCX 0.6–10 mV/µs (3.3 V in 0.33–5.5 ms), VCCIO 0.1–10 mV/µs; all **monotonic**. All rails in range before configuration starts (§3.1.3). POR trip: VCC 0.75–1 V, VCCX 1.8–2 V, VCCIO 0.85–0.98 V (Tab 3-5). Internal flash read needs VCC ≥ 1.08 V and VCCX ≥ 1.62 V at T1 + 0.5–1 ms POR delay (UG284 "Power ramping"); with the ramp limits above this holds. → requirements for block C, listed in `E-interfaces.md`.

## Configuration — the architecture's SSPI plan does not work on this package

UG803 pin list, QN88P column (checked pin by pin):
- **SCLK (IOL12A) — not bonded. SI (IOR13B) — not bonded.** SSPI needs SCLK, SI, SO, SSPI_CS_N (UG290 Tab 4-1, §7.4.1). SERIAL and CPU modes also need SCLK. **SSPI, SERIAL and CPU configuration are impossible on any QN88/QN88P part**, whatever the toolchain.
- **DONE (IOL14A) and READY (IOL14B) — not bonded** in QN88P (DONE is pin 10 only in the SDRAM QN88). The RP2350 checks configuration through the JTAG status register instead (bit 13 `DONE_FINAL`, as openFPGALoader does).
- **MODE2 not bonded → internally GND** (UG290 Tab 5-1 note 1). MODE0 = pin 88, MODE1 = pin 87. Reachable modes: 000 AUTOBOOT (internal flash), 010 MSPI (FPGA masters an external SPI flash), 001 SSPI (unusable, pins missing). JTAG is independent of MODE.
- Bonded: TMS 5, TCK 6, TDI 7, TDO 8, RECONFIG_N 9, JTAGSEL_N 4 (all bank 3, 1.8 V), MSPI pins MCLK 59 / MCS_N 60 / MO 61 / MI 62 / FASTRD_N 57, and SSPI_CS_N 55, SO 56 (bank 1).

**Chosen scheme (proposed change to architecture decision 2, see `E-interfaces.md`):**
1. MODE[1:0] = 00 → **AUTOBOOT** from the GW1NR-9's own configuration flash, which holds a **golden** bitstream (safe: PWM off, amp muted, PHY/MAC and RP2350 link up). MODE0/MODE1 each pulled down with 1 kΩ (UG284 "MODE": 4.7 k up / 1 k down recommended).
2. The RP2350 then loads the **A or B** bitstream from its 16 MB QSPI flash into FPGA **SRAM over JTAG** (Gowin JTAG SRAM flow: ConfigEnable 0x15, erase SRAM, InitAddr 0x12, XferWrite 0x17, ConfigDisable 0x3A, Noop 0x02; UG290 §7.2.4; the same sequence as openFPGALoader `src/gowin.cpp`). If it fails (status register shows no DONE_FINAL), the RP2350 pulses RECONFIG_N (≥ 25 ns, UG284) and the golden image autoboots again.
3. The golden image itself is updated, rarely, over the same JTAG port with the eFlash flow (erase 0x75, program; TCK 1.3–30 MHz during eFlash programming for GW1N-9, UG290 Tab 7-9) while the FPGA keeps running ("background upgrade", UG290 §3.5), then RECONFIG_N.

This keeps R-56 (A/B for both chips, rollback, both in the RP2350 flash) and adds a third, recovery image the RP2350 cannot brick by a bad network update.

JTAG timing (UG290 Tab 7-5): TCK period ≥ 40 ns (**≤ 25 MHz**), high/low ≥ 20 ns, setup 10 ns, hold 8 ns, TCK↓→TDO ≤ 10 ns. UG290 §7.2.2 note: JTAG configuration clock ≤ 40 MHz; we use 10–20 MHz.

SRAM load time (bitstream 435 KB max, UG290 Tab 3-1): 435 × 1024 × 8 bit / 15 MHz = **0.24 s** at 15 MHz TCK, plus SRAM erase and status reads. AUTOBOOT of the golden image: 14–178 ms depending on loading clock (UG290 Tab 3-4).

The JTAG pins are on **bank 3 at 1.8 V**; the RP2350's VIH is 2.0 V at IOVDD 3.3 V (RP2350 Tab 1436), so TDO (VOH ≥ 1.4 V) cannot drive it directly → SN74AVC4T774 translator, `E-level-jtag.md`. RECONFIG_N is driven open-drain by the RP2350 directly (GPIO only ever pulls low; the node idles at 1.8 V through 4.7 kΩ to `+1V8`).

## Pin states during power-up and configuration (UG290 Appendix A, Tab A-1)

- Power-on → POR: all GPIO Hi-Z, no pull. **POR → end of configuration: all GPIO Hi-Z with weak pull-up** (30–150 µA, DS117 Tab 3-8 IPU), except MCLK/D4 (pin 59) and DOUT/WE_N (pin 53), which have weak **pull-down**. Unused GPIO after configuration: weak pull-up unless the design says otherwise.
- **Consequence for block D:** every gate-driver input and enable driven by the FPGA must have an external pull-down strong enough to hold it below the driver's VIL against 150 µA: R ≤ VIL / 150 µA (e.g. ≤ 4.7 kΩ gives ≤ 0.7 V; 2.2 kΩ gives 0.33 V). Same for `RMII_TXEN` (PHY would transmit garbage): 2.2 kΩ pull-down, and it sits on pin 53 (internal pull-down) anyway.
- TCK: external **4.7 kΩ pull-down** required (UG284 JTAG note 2). TMS, TDI internal weak pull-ups. RECONFIG_N: 4.7 kΩ pull-up to the bank voltage (UG284 Fig 6) = `+1V8`, and it must be high from power-up until loading completes (UG290 §6).
- JTAGSEL_N (pin 4): keep JTAG dedicated (never set "JTAG as GPIO"); 4.7 kΩ pull-up to `+1V8`, no other connection. Not used as LPLL input.
- Dual-purpose MSPI/SSPI pins (53–57, 59–62) become user I/O only with `gowin_pack --mspi_as_gpio --sspi_as_gpio` (Apicula `apycula/gowin_pack.py` arguments, checked 2026-11-07).

## Bank 3 is 1.8 V — overdrive inputs

UG803 power sheet, QN88P: VCCIO3 "connected to PSRAM and provides power for PSRAM", 1.71–1.89 V. So bank 3's 15 user pins output 1.8 V only. DS117 §2.4 input table: **LVCMOS33OD18** — a 3.3 V LVCMOS input on a 1.8 V bank, allowed with Pull Mode = NONE and PCI clamp OFF (note 3); VIH max 3.6 V; leakage ≤ 210 µA when VIN > VCCIO (Tab 3-8). Apicula knows the attribute (`LVCMOS33OD18` and `CLAMP` in `apycula/attrids.py`).
Use of bank 3 in `E-pinmap.md`: 3.3 V *inputs* in overdrive (with series resistors), and 1.8 V *outputs* only into the SN74AVC4T774 up-translators (display + 2 spare outputs, `E-level-display.md`) and the JTAG translator — nothing else.
Worst-case injection into `+1V8` from 7 overdriven inputs: 7 × 210 µA = 1.5 mA → the 1V8 regulator needs ≥ 2 mA of standing load (a 1 kΩ bleeder = 1.8 mA) so this current cannot pump the rail up. Before configuration the clamp state of these pins is not documented; series resistors (4.7 kΩ on slow inputs, 100 Ω on `LINK_CLK`) bound the current either way.
**Verify on a Tang Nano 9K** (same die, bank 3 also 1.8 V) before phase 2: build a bitstream with an `LVCMOS33OD18` input and check nextpnr/gowin_pack accept it and the pin reads correctly.

## Clocks, PLL and the PWM edge grid

- rPLL (UG286 §5.1): fCLKOUT = fCLKIN × FBDIV / IDIV; fVCO = fCLKOUT × ODIV; IDIV, FBDIV = 1…64; ODIV ∈ {2, 4, 8, …, 128}. Limits GW1NR-9 C6/I5 (DS117 Tab 3-21): fIN 3–400 MHz, fPFD 3–400 MHz, **VCO 400–1200 MHz, fOUT ≤ 600 MHz**, lock ≤ 1 ms, input jitter < 20 % of period or 1 ns, **output cycle-to-cycle jitter < 300 ps (HCLK ≥ 100 MHz), period jitter < 300 ps** — "based on a low-jitter crystal oscillator input".
- Audio PLL (right PLL, input on its dedicated pin 63 `IOR5A/RPLL_T_in`, UG284 "Clock input selection"): 24.576 MHz × 20 / 1 = **491.52 MHz** FCLK (FBDIV_SEL = 19, IDIV_SEL = 0), ODIV = 2 → VCO 983.04 MHz (in range). PCLK = FCLK / 5 = 98.304 MHz (CLKDIV, DIV_MODE 5).
- Gearbox (DS117 Tab 3-17, GW1NR-4/9): OSER10 ≤ 1000 Mbps, OSER4 ≤ 800 Mbps, ODDR ≤ 400 Mbps. OSER10 at 491.52 MHz DDR = **983.04 Mbps → edge grid 1.017 ns** (98 % of the datasheet maximum). Fallback ×16 (393.216 MHz, 786 Mbps) → 1.272 ns with 21 % margin.
- Single-ended I/O Fmax (Tab 3-18): LVCMOS33 ≥ 300 MHz with drive > 4 mA (30 pF). This limits *toggle* rate, not edge *placement*: the modulator must keep every pulse ≥ ~10 ns (≫ 1.7 ns), which the gate drivers need anyway.
- IODELAY (DS117 Tab 2-4): 0–127 steps × 30 ps (+ 450–550 ps offset), static or dynamic; one direction per pin. Use: static per-pin deskew of the 8 PWM lines (trim board/driver skew to ~30 ps). It cannot place individual edges cycle by cycle, so it does not refine the 1.017 ns grid.
- Effective edge resolution, jitter and the clocking choice: `E-clk-audio-vcxo.md`.

Open-toolchain evidence (Apicula README, `examples/Makefile`, 2026-11-07, release 0.35 of 2026-10-20): Tang Nano 9K (GW1NR-LV9QN88PC6/I5, family GW1N-9C) is a supported board; the 9K example set builds `oser4/8/10/16`, `iodelay`, `ides4/8/10`, `pll-nanolcd`, `dvi-example` (rPLL + OSER10 at 742.5 Mbps), BSRAM, DSP (mult 9/18/36, ALU54, multadd), user flash. Flow: `yosys synth_gowin` → `nextpnr-himbaechel --device GW1NR-LV9QN88PC6/I5 --vopt family=GW1N-9C --vopt cst=…` → `gowin_pack -d GW1N-9C [-c] [--mspi_as_gpio --sspi_as_gpio]`. openFPGALoader (`doc/FPGAs.yml`, `src/part.hpp`) lists GW1NR-9 (IDCODE 0x0100581B) and GW1N(R)-9C (0x0100481B): memory (SRAM) OK, flash = internal.

## Bitstream size vs R-56

UG290 Tab 3-1: GW1N-9/GW1NR-9 max uncompressed configuration file **435 KB** (binary). Apicula can compress (`gowin_pack -c`), so 435 KB is the worst case. Flash plan in `E-flash-w25q128.md`: 2 × 512 KB bitstream slots = 1 MB of 16 MB. **R-56 holds.**

## Power estimate (no Gowin power estimator in the open flow)

DS117 Tab 3-9 static (typ, C6, 25 °C): ICC 3.5 mA @ 1.2 V, ICCX 5 mA @ 3.3 V, ICCIO 2 mA @ 2.5 V. Flash programming max: VCC 2.19 mA, VCCX 12 mA, VCCIO 2 mA (Tab 3-10).
Dynamic, estimated (not a datasheet figure — firm up with the Gowin EDA power analyser on the real design during firmware bring-up): ~70 % LUT use at ~100 MHz plus 8 OSER10 at 491 MHz and one PLL → **VCC ≈ 100 mA typ; design 250 mA** on `+1V2`. VCCX + VCCIO1/2 at 3.3 V: static 5–7 mA + output switching (8 link lines at 37.5 MHz × 15 pF × 3.3 V × 0.5 ≈ 7 mA, RMII/PWM/display ≈ 5 mA) → **40 mA design**. VCCIO3 at 1.8 V: PSRAM (unused, held in reset/deep power-down by the design) + 6 slow outputs → **30 mA design**.

## Required external parts (from datasheets)

- Each FPGA power pin: 0.1 µF to GND (UG284 "Power filter") → 4 × VCC, 3 × VCCX/VCCIO0, 1 × VCCIO1, 2 × VCCIO2, 1 × VCCIO3 = 11 × 100 nF 0402 (`E-fpga-passives.md`).
- VCC input: ferrite bead + 4.7 µF (UG284 Fig 2; reference bead 220 Ω @ 100 MHz) → BLM18PG221SN1D + 4.7 µF.
- TCK 4.7 kΩ pull-down; RECONFIG_N 4.7 kΩ pull-up to +1V8; JTAGSEL_N 4.7 kΩ pull-up to +1V8; MODE0, MODE1 1 kΩ pull-downs.
- Series resistors on bank-3 overdrive inputs (above).
- Pull-downs on FPGA-driven safety-critical outputs (PWM, enables, TXEN) — the PWM ones belong to block D's gate-driver inputs.

## Calculations

- VCC drop in the bead: 250 mA × 0.10 Ω (BLM18PG221SN1D DCR max) = 25 mV → 1.2 V − 1 % (regulator) − 25 mV = 1.163 V > 1.14 V min. OK; better, block C senses after the bead or sets 1.21 V.
- VCC ripple allowance 3 % of 1.2 V = 36 mV p-p (DS117 §3.1.2 note): the 1V2 regulator ripple plus load steps must stay inside it; ripple on VCC "can affect PLL output jitter" (same note), which matters for the PWM (see VCXO file). Ask block C for ≤ 10 mV p-p.
- Bitstream SRAM load at 15 MHz TCK: 0.24 s (above). AUTOBOOT golden: ≤ 178 ms.
- Overdrive leakage: 7 × 210 µA = 1.47 mA → 1V8 bleeder ≥ 2 mA.
- Weak pull-up vs gate-driver input: 150 µA max × 2.2 kΩ = 0.33 V.

## Fine print / gotchas

- QN88P ≠ QN88: different pin 10/11/13/15 bonding (UG803). Use the **QN88P** column everywhere; the LCSC part is QN88**P**.
- "VCCX should be ≥ VCCIO" (UG803 power note): VCCX is on `+3V3`, the highest I/O rail, so this holds; never power bank 1/2 from a rail that can exceed `+3V3`.
- When JTAGSEL_N and JTAG pins are both GPIO, a low JTAGSEL_N forces the JTAG pins back (DS117 §1.3 note). We never make JTAG pins GPIO.
- RECONFIG_N must stay high from power-up to load completion; never let the RP2350 reset state pull it low (RP2350 reset state is "pulled low", §9.3, pull-down 36–113 kΩ at IOVDD 3.3 V, Tab 1436 — against 4.7 kΩ to 1.8 V gives ≥ 1.8 × 36/40.7 = 1.59 V: high; OK).
- "C" vs non-C die: the "C" is only in the date code (Apicula README note 1). openFPGALoader distinguishes them by IDCODE; firmware must accept both IDCODEs (0x0100481B, 0x0100581B) and Apicula must be told the family that matches (GW1N-9C for the Tang Nano 9K part).
- Hot socketing / overdrive: IHS ≤ 150 µA for 0 < VIN < VIH(MAX) (Tab 3-4).
- PSRAM: 1.8 V only; keep it in deep power-down (or use it later as a frame/delay buffer — it's free memory: 64 Mbit at 166 MHz DDR, §2.2.2).

## Layout guidance (feeds phases 4–6)

- One 0.1 µF per power pin at the pin; the 4.7 µF and bead on the VCC feed. EPAD to GND with a via array (≥ 9 vias in the 6.8 mm pad; split paste into windows).
- PLL input pin 63 (`VCXO_CLK`): short, guarded, no crossing of the PWM or switch-node area; RMII ref clock on pin 52 (GCLKT_3).
- Bank 2 (bottom edge) faces the power stage (PWM/OC/ADC); bank 1 right edge faces the PHY and audio clocking; top edge (bank 1 top + bank 3 top) faces the RP2350 (link + display); left edge (bank 3) carries JTAG, isolated status inputs, mic data.

## Open questions

- Dynamic power is an estimate; measure on a Tang Nano 9K with the real design before freezing the 1V2 regulator.
- `LVCMOS33OD18` and dual-purpose-pin options in nextpnr-himbaechel: confirm with a test build (attributes exist in Apicula).
- OSER10 at 983 Mbps is at 98 % of the gearbox spec; bring-up must confirm it on this speed grade (C6/I5) or fall back to 786 Mbps (1.27 ns).
