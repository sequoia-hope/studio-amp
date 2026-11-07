# Y (RMII reference) — 50 MHz CMOS oscillator, and the RMII timing budget

> **ECP5 update (2026-11-07).** The oscillator and its two branches are unchanged; the FPGA branch now goes to ECP5 ball **C8 (PCLKT1_0, top bank 1)**, with the RMII group on balls A9–A12, B10, B11 (`E-pinmap.md`). Budget redone with ECP5 −7 datasheet numbers (DS-02012 Tab 3.22, generic SDR from a dedicated primary clock input: tCO ≤ 6.1 ns, tSU ≥ 0, tH ≥ 3.0 ns; with input delay tSU_DEL ≥ 1.33 ns, tH_DEL ≥ 0):
> - RX setup 20.2 − 14.4 − 0 = +5.8 ns, but hold 3.4 − 3.0 = **+0.4 ns** → use DELAYG on RXD0/1, CRS_DV: setup 20.2 − 14.4 − 1.33 = **+4.5 ns**, hold **+3.4 ns**.
> - TX setup 20.2 − (0.2 + 6.1 + 0.2) − 4.0 = **+9.7 ns**; hold needs min tCO + 0.4 ns ≥ 1.7 ns (min tCO isn't in the datasheet; check the nextpnr-ecp5 timing report in phase 2).
> The Gowin-specific numbers below are superseded.


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
| FPGA GCLK input, LVCMOS33 (VIH 2.0 V) | as above | OK |
| Temperature (R-40, ≥ 85 °C) | −40…+85 °C | OK |
| Load | rated 15 pF; ours 2 inputs (PHY ~3 pF, FPGA ≤ 8 pF) + 2 short branches ≈ 15 pF | OK |
| Supply | 12 mA max at 3.3 V (41–54 MHz, 3225) | budget 12 mA on `+3V3` |

Required parts (datasheet p.3 note 1): 10 nF–100 nF from VDD to GND → 100 nF 0402 (`C1525`, basic) at pin 4. OE pin 1: "Enable = high or floating" → tie to VDD (no floating pin). Series resistor at the output: 33 Ω per branch (`C25105 0402WGF330JTCE (UNI-ROYAL, 0402): basic, JLC stock 3866748, lifecycle normal`), 2 off.

## Keeping the 50 MHz short

Place the oscillator between the PHY and the FPGA's right edge, driving **two point-to-point branches**, each with its own 33 Ω at the oscillator: → PHY XTAL1 (pin 5) and → FPGA pin 52 (GCLKT_3). Both branches **≤ 25 mm**, matched to ±5 mm, over solid GND, no vias if possible. With 4 ns rise (datasheet max) and ~6.5 ps/mm, a 25 mm branch is 0.16 ns, far below tr/6 = 0.67 ns, so each branch is lumped and the series R only damps ringing. XTAL2 of the PHY is left unconnected (LAN8720A Tab 2-5).

## RMII timing budget (REF_CLK In mode)

PHY numbers: LAN8720A Tab 5-10 (load 10–25 pF): **toval ≤ 14.0 ns, tohold ≥ 3.0 ns, tsu ≥ 4.0 ns, tihold ≥ 1.5 ns**, clock period 20 ns.
FPGA numbers: GW1NR-9 C6/I5 PCLK tree delay GCLK0–5 = 2.2 ns typ, pin–LUT–pin 4.2 ns typ (DS117 Tab 3-19). DS117 gives no IOB register setup/hold; the budget below assumes **t_su,IOB ≤ 1.0 ns, t_h,IOB ≤ 0.5 ns, IOB clock-to-pad ≤ 4.2 ns** (the pin–LUT–pin figure, which also contains an input buffer and a LUT, so it is a generous bound). nextpnr-himbaechel's timing report confirms them at the first build; that is a phase 2 check.
Board: each branch/trace ≤ 25 mm → flight ≤ 0.2 ns; clock-branch skew ≤ 0.1 ns.

**RX (PHY → FPGA; RXD[1:0], CRS_DV), captured in IOB registers on REF_CLK ↑ through the global tree:**
- Setup: data valid at FPGA ≤ 0.2 (clk to PHY) + 14.0 + 0.2 (data) = 14.4 ns after the oscillator edge. Capture edge at FPGA register = 20 + 0.2 + 2.2 = 22.4 ns. Slack = 22.4 − 14.4 − 1.0 = **+7.0 ns**.
- Hold: data changes no earlier than 0.2 + 3.0 + 0.2 = 3.4 ns; capture clock at register 0.2 + 2.2 = 2.4 ns + t_h 0.5 → slack = 3.4 − 2.9 = **+0.5 ns** (thin, because the tree delay delays the clock).
- **Fix:** static IODELAY on the three RX inputs, 50 steps × 30 ps + 0.5 ns offset ≈ 2.0 ns (DS117 Tab 2-4): hold slack +2.5 ns, setup slack +5.0 ns. Alternative: route REF_CLK through the left rPLL in phase-compensated mode (cancels the 2.2 ns tree delay; hold +2.7 ns, setup +4.8 ns). Either is in the RTL; no board change.

**TX (FPGA → PHY; TXD[1:0], TXEN), launched on REF_CLK ↑ from IOB registers:**
- Setup at PHY: data at PHY ≤ 0.2 + 2.2 + 4.2 + 0.2 = 6.8 ns; PHY capture edge 20 + 0.2 = 20.2 ns; slack = 20.2 − 6.8 − 4.0 = **+9.4 ns**.
- Hold at PHY: earliest change ≥ 0.2 + 2.2 + (min clock-to-pad, assume ≥ 0.5) + 0.2 = 3.1 ns after the edge vs tihold 1.5 ns + 0.2 → slack ≥ **+1.4 ns**.

Both directions close with margin once the RX IODELAY is set. Trace length mismatch inside the RMII group: ±10 mm (≤ 65 ps), irrelevant at this budget.

**PTP timestamp resolution**: the MAC sees the SFD at REF_CLK granularity, 20 ns; the PHY's RX/TX latency is fixed per link speed, calibrated once. Speaker-to-speaker offset target ≤ 10 µs (R-55) is 500 × this quantum.

## Fine print

- LAN8720A: "During a hardware reset, an external clock must be supplied to XTAL1/CLKIN" (§3.8.5.1) → the oscillator runs from `+3V3` unconditionally (no OE control by software).
- "Do not drive input signals without power supplied to the device" (LAN8720A §5.2): oscillator and PHY share `+3V3`, so the clock cannot reach the PHY unpowered.
- The oscillator datasheet gives jitter but no phase-noise plot; RMII doesn't need one.

## Open questions

- IOB setup/hold numbers come from the open flow's timing model, not a datasheet: check the nextpnr report in phase 2 (or the Gowin EDA report once) and record them here.
