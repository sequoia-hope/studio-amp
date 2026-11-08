# Y (RMII reference) — 50 MHz CMOS oscillator, and the RMII timing budget (ECP5)

Datasheet: `datasheets/yxc-ot2el-50m.pdf` (YXC YSO110TR "Wide Voltage" crystal oscillator series, 4 pp, image-only; read as rendered pages: specifications, current, pin-out, land patterns, test circuit). LCSC parameter list fetched 2026-11-07.
MPN: OT2EL4C4JI-111OLP-50M (YSO110TR series, 3.2 × 2.5 mm)
Supplier: `C5203552 OT2EL4C4JI-111OLP-50M (YXC Crystal Oscillators, SMD3225-4P): extended, JLC stock 105893, lifecycle normal, checked 2026-11-07`
LCSC parameters: 50 MHz, ±10 ppm at 25 °C, ±20 ppm stability, CMOS, 1.8–3.3 V, −40…+85 °C.
Footprint: 3.2 × 2.5 mm 4-pad; land 1.3 × 1.2 mm pads, 0.8 mm gap / 0.7 mm gap (datasheet p.3, "3.2*2.5" recommended pattern). Pins: 1 Tri-state (OE), 2 GND, 3 OUT, 4 VDD.

## Why this mode

LAN8720A in **REF_CLK In mode** (nINTSEL strap = 1, its default): the 50 MHz clock is driven into the PHY's XTAL1/CLKIN and into the FPGA. This is the RMII-standard arrangement; the PHY's REF_CLK Out mode (25 MHz crystal, PHY makes 50 MHz) is "not part of the RMII specification… timing not compliant" (LAN8720A §3.7.4.2 note) and also takes away nINT. One extra oscillator buys a compliant, analysable interface.

## Requirements vs part

| Requirement (LAN8720A Tab 5-11, RMII CLKIN) | Part (datasheet / LCSC) | OK |
|---|---|---|
| 50 MHz, drift ≤ ±50 ppm (IEEE budget; Note 5-26 ≈ ±45 ppm incl. ageing) | ±10 ppm + ±20 ppm + ≤ ±3 ppm/yr ageing = ±33 ppm (yr 1) | OK |
| Duty 40–60 % | 45–55 % | OK |
| Jitter ≤ 150 ps p-p | 0.7 ps rms phase jitter (12 kHz–20 MHz) ≈ 10 ps p-p (×14) | OK |
| XTAL1 VIH 0.9–3.6 V, VIL ≤ 0.35 V (Tab 5-3, ICLK) | CMOS 0–3.3 V, VOH ≥ 90 % VDD, VOL ≤ 10 % VDD | OK |
| ECP5 PCLKT1_0 input (C8), LVCMOS33 (VIH 2.0 V, DS-02012 Tab 3.12) | as above | OK |
| Temperature (R-40, ≥ 85 °C) | −40…+85 °C | OK |
| Load | rated 15 pF; ours 2 inputs (PHY ~3 pF, FPGA ≤ 8 pF) + 2 short branches ≈ 15 pF | OK |
| Supply | 12 mA max at 3.3 V (41–54 MHz, 3225) | budget 12 mA on `+3V3` |

Required parts (datasheet p.3 note 1): 10 nF–100 nF from VDD to GND → 100 nF 0402 (`C1525`, basic) at pin 4. OE pin 1: "Enable = high or floating" → tie to VDD (no floating pin). Series resistor at the output: 33 Ω per branch (`C25105 0402WGF330JTCE (UNI-ROYAL, 0402): basic, JLC stock 3866748, lifecycle normal`), 2 off.

## Keeping the 50 MHz short

Place the oscillator between the PHY and the ECP5's top edge (bank 1), driving **two point-to-point branches**, each with its own 33 Ω at the oscillator: → PHY XTAL1 (pin 5) and → ECP5 ball C8 (PCLKT1_0). Both branches **≤ 25 mm**, matched to ±5 mm, over solid GND, no vias if possible. With 4 ns rise (datasheet max) and ~6.5 ps/mm, a 25 mm branch is 0.16 ns, far below tr/6 = 0.67 ns, so each branch is lumped and the series R only damps ringing. XTAL2 of the PHY is left unconnected (LAN8720A Tab 2-5).

## RMII timing budget (REF_CLK In mode, ECP5 −7)

PHY (LAN8720A Tab 5-10, load 10–25 pF): **toval ≤ 14.0 ns, tohold ≥ 3.0 ns, tsu ≥ 4.0 ns, tihold ≥ 1.5 ns**, period 20 ns.
FPGA (DS-02012 Tab 3.22, generic SDR from a dedicated primary clock input, −7): **tCO ≤ 6.1 ns, tSU ≥ 0, tH ≥ 3.0 ns; with input delay tSU_DEL ≥ 1.33 ns, tH_DEL ≥ 0**. These are commercial figures for LVCMOS25 / 12 mA / 0 pF; for the −7I part at LVCMOS33 into ~10 pF, allow tCO ≈ 8 ns (`E-fpga-ecp5.md`).
Board: each branch/trace ≤ 25 mm → flight ≤ 0.2 ns; clock-branch skew ≤ 0.1 ns.

**RX (PHY → FPGA; RXD[1:0], CRS_DV on A11, A12, B11):**
- Without delay: setup 20.2 − (0.2 + 14.0 + 0.2) − 0 = +5.8 ns; hold 3.4 − (0.2 + 3.0) = **+0.2 ns**: too thin.
- **With DELAYG** (static input delay): setup 20.2 − 14.4 − 1.33 = **+4.5 ns**, hold 3.4 − 0.2 − 0 = **+3.2 ns**. RTL rule: DELAYG on all three RX inputs.

**TX (FPGA → PHY; TXD[1:0], TXEN on A10, B10, A9):**
- Setup at PHY: 20.2 − (0.2 + 6.1 + 0.2) − 4.0 = **+9.7 ns** (+7.7 ns with the 8 ns derated tCO).
- Hold at PHY: needs min tCO ≥ 1.5 − 0.2 + 0.2 ≈ 1.5 ns. The datasheet gives no minimum tCO; check the nextpnr-ecp5 timing report in phase 2. Fallback: launch on the falling edge, which makes setup 10 − 8 − 0.2 − 4.0 ≈ −2.2 ns with derating — so the rising edge stays, with the report as the check.

Trace length mismatch inside the RMII group: ±10 mm (≤ 65 ps), irrelevant at this budget.

**PTP timestamp resolution**: the MAC sees the SFD at REF_CLK granularity, 20 ns; the PHY's RX/TX latency is fixed per link speed, calibrated once. Speaker-to-speaker offset target ≤ 10 µs (R-55) is 500 × this quantum.

## Fine print

- LAN8720A: "During a hardware reset, an external clock must be supplied to XTAL1/CLKIN" (§3.8.5.1) → the oscillator runs from `+3V3` unconditionally (no OE control by software).
- "Do not drive input signals without power supplied to the device" (LAN8720A §5.2): oscillator and PHY share `+3V3`, so the clock cannot reach the PHY unpowered.
- The oscillator datasheet gives jitter but no phase-noise plot; RMII doesn't need one.

## Open questions

- Minimum ECP5 tCO for the TX hold check: nextpnr-ecp5 timing report, phase 2.

## Phase 2 schematic notes (2026-11-08)

- Footprint `studio_E:Oscillator_SMD_3225-4Pin_YXC_SX3V` (YXC's recommended land exactly; shared with the VCXO).
- Branches: 33 Ω → PHY XTAL1; 33 Ω → `RMII_REFCLK` (ECP5 C8).
