> **SUPERSEDED by ECP5 (user, 2026-11-07).** The FPGA is now the Lattice LFE5U-25F-7BG256I; see `E-fpga-ecp5.md`, `E-pinmap.md`, `E-interfaces.md`. Kept for the record; do not build from this file.

# FPGA passives — decoupling, core-feed bead, configuration straps

Serves: U-FPGA (`E-fpga-gw1nr9.md`). Datasheets: `datasheets/gowin-UG284E.pdf` (power filter, JTAG, MODE, RECONFIG_N), `datasheets/gowin-UG290E.pdf` App. A, `datasheets/murata-blm18pg221sn1d.pdf`, `datasheets/samsung-mlcc-catalog.pdf` (Samsung MLCC catalogue: part-number table, rated voltage, dielectric), `datasheets/uniroyal-0402wgf.pdf` (thick-film 0402: 1/16 W, 50 V working).

## Parts

| Function | Value | Part | Supplier line (`jlc_parts.py show`, 2026-11-07) | Qty |
|---|---|---|---|---|
| Per-pin decoupling (VCC ×4, VCCX/VCCIO0 ×3, VCCIO1, VCCIO2 ×2, VCCIO3) | 100 nF X7R 16 V 0402 | CL05B104KO5NNNC | `C1525 CL05B104KO5NNNC (Samsung Electro-Mechanics, 0402): basic, JLC stock 34322291, lifecycle normal` | 11 |
| VCC feed bead | 220 Ω @ 100 MHz, 1.4 A, 0.10 Ω max | BLM18PG221SN1D | `C80165 BLM18PG221SN1D (muRata, 0603): extended, JLC stock 218690, lifecycle normal` | 1 |
| VCC bulk after bead (PLL is supplied from VCC; no separate PLL pin in QN88P) | 10 µF X5R 10 V 0603 ∥ 4.7 µF X5R 16 V 0603 | CL10A106KP8NNNC + CL10A475KO8NNNC | `C19702 CL10A106KP8NNNC (Samsung Electro-Mechanics, 0603): basic, JLC stock 10318610, lifecycle normal`; `C19666 CL10A475KO8NNNC (Samsung Electro-Mechanics, 0603): basic, JLC stock 3850946, lifecycle normal` | 1 + 1 |
| VCCX/VCCIO 3.3 V bulk | 4.7 µF X5R 16 V 0603 | CL10A475KO8NNNC | as above | 2 (one per side) |
| VCCIO3 1.8 V bulk | 4.7 µF X5R 16 V 0603 | CL10A475KO8NNNC | as above | 1 |
| TCK pull-down | 4.7 kΩ 1 % 0402 | 0402WGF4701TCE | `C25900 0402WGF4701TCE (UNI-ROYAL, 0402): basic, JLC stock 15759231, lifecycle normal` | 1 |
| RECONFIG_N pull-up to +1V8 | 4.7 kΩ | 0402WGF4701TCE | as above | 1 |
| JTAGSEL_N pull-up to +1V8 | 4.7 kΩ | 0402WGF4701TCE | as above | 1 |
| MODE0, MODE1 pull-downs (AUTOBOOT = 00) | 1 kΩ | 0402WGF1001TCE | `C11702 0402WGF1001TCE (UNI-ROYAL, 0402): basic, JLC stock 33763066, lifecycle normal` | 2 |
| Series R, slow 3.3 V → bank-3 overdrive inputs (PD_PG, POE_LOSS_N, MADC_DOUT, PDM_DAT, LINK_DIR, LINK_STB) | 4.7 kΩ (PD_PG, POE_LOSS_N); 1 kΩ (PDM_DAT, MADC_DOUT); 100 Ω (LINK_DIR, LINK_STB) | 0402WGF4701TCE / 0402WGF1001TCE / 0402WGF1000TCE | C25900, C11702 as above; `C25076 0402WGF1000TCE (UNI-ROYAL, 0402): basic, JLC stock 11744639, lifecycle normal` | 2 + 2 + 2 |
| Series R, LINK_CLK into pin 10 | 100 Ω | 0402WGF1000TCE | C25076 | 1 |
| `RMII_TXEN` pull-down | 2.2 kΩ | 0402WGF2201TCE | `C25879 0402WGF2201TCE (UNI-ROYAL, 0402): basic, JLC stock 3375962, lifecycle normal` | 1 |
| `+1V8` bleeder (absorbs overdrive leakage) | 1 kΩ | 0402WGF1001TCE | C11702 | 1 (block C may own it; listed here so it isn't lost) |

All basic except the bead (one extended setup fee). Stock ≫ 7 boards.

## Calculations

- **Decoupling count**: UG284 "each FPGA power input pin is connected to the ground with a 0.1 µF ceramic capacitor" → 11. Bulk: UG284 shows 4.7 µF on VCC; 4.7 µF per 3.3 V side and on 1.8 V is our addition for local charge (the rails come from block C bucks/LDO tens of mm away).
- **MLCC DC bias**: 100 nF X7R 16 V at ≤ 3.3 V is 21 % of rated → small loss. 4.7 µF X5R 16 V 0603 at 3.3 V (21 % of rating) and at 1.2 V (7.5 %). The Samsung catalogue in hand has no DC-bias curves; the effective value is not taken from a datasheet here. It is not critical: these are bulk reservoirs, not timing parts. The reviewer should check Samsung's per-part characteristic data. Using the 16 V part (not 6.3/10 V) for the same footprint is the margin.
- **Voltage ratings**: 16 V on ≤ 3.3 V rails = 4.8× (≥ 2× rule met).
- **Bead drop**: 250 mA (design) × 0.10 Ω = 25 mV; bead rated 1.4 A @ 85 °C (Murata table) ≫ 0.25 A. 1.2 V − 1 % − 25 mV = 1.163 V ≥ 1.14 V. Bead + 4.7 µF corner: LC resonance with ~0.4 µH equivalent at low frequency (bead inductive region, value not in the Murata spec beyond 100 MHz impedance) — no ringing concern at the 1V2 buck's switching frequency because block C's output caps sit ahead of the bead; flag for the phase 8 PDN check.
- **MODE pull-downs vs internal pull-up**: IPU ≤ 150 µA × 1 kΩ = 0.15 V ≪ VIL. MODE sampled at READY rise (UG284 Tab 2).
- **TCK pull-down**: UG284 note 2: 4.7 kΩ required.
- **RECONFIG_N / JTAGSEL_N**: 4.7 kΩ to the bank voltage (UG284 Fig 6 note: "the pull-up supply is the bank voltage of the corresponding pin") = 1.8 V.
- **Overdrive inputs**: max leakage 210 µA (DS117 Tab 3-8). With 4.7 kΩ series, the extra drop is ≤ 1 V → the pin sees ≥ 2.3 V from a 3.3 V driver, above LVCMOS33 VIH 2.0 V. 100 Ω on fast lines: drop ≤ 21 mV; RC with 8 pF pin capacitance (DS117 C1 max) = 0.8 ns. If a clamp diode were on before configuration: (3.3 − 1.8 − 0.6) V / 100 Ω = 9 mA worst case on a fast line — acceptable only because the RP2350 does not drive `LINK_*` until it has confirmed the FPGA is configured (firmware rule, `E-link.md`). Slow lines driven continuously (PD_PG, POE_LOSS_N) get 4.7 kΩ: ≤ 0.2 mA. PDM_DAT and MADC_DOUT are driven by always-powered parts (block F), so they get 1 kΩ: clamp current ≤ 0.9 mA, RC = 8 ns, negligible against a 325 ns bit period at 3.072 MHz.
- **TXEN pull-down**: 150 µA × 2.2 kΩ = 0.33 V < LAN8720 VIS negative-going threshold min 1.41 V at 3.3 V (LAN8720A Tab 5-4). Resistor power: 3.3² / 2.2 k = 5 mW when driven high; 1/16 W rating OK.

## Fine print

- MODE pins and RECONFIG_N/TCK straps must not be connected to anything that drives them during power-up.
- Pull-ups for bank-3 pins go to `+1V8`, not `+3V3`.

## Layout

- 100 nF at each power pin, on the FPGA side, short via to the GND plane; bead + 4.7 µF at the VCC entry, between the 1V2 pour and the FPGA VCC pins.
- Straps and pull-ups near the FPGA, out of the way of the JTAG/link escape.
