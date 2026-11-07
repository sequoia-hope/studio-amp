> **SUPERSEDED by ECP5 (user, 2026-11-07).** The FPGA is now the Lattice LFE5U-25F-7BG256I; see `E-fpga-ecp5.md`, `E-pinmap.md`, `E-interfaces.md`. Kept for the record; do not build from this file.

# U (FPGA JTAG translator) — TI SN74AVC4T774PWR

Datasheet: `datasheets/sn74avc4t774.pdf` (SCES693D, rev 2015). Read: §1–7 (features, pin functions, abs max, recommended operating, electrical, switching), §8 (Ioff, power-up OE note, function table), §10–11 (application, power supply), §12 layout.
MPN: SN74AVC4T774PWR (TSSOP-16)
Supplier: `C129363 SN74AVC4T774PWR (TI, TSSOP-16): extended, JLC stock 20278, lifecycle normal, checked 2026-11-07`
Footprint: TSSOP-16 4.4 mm, 0.65 mm pitch (PW). Pins: DIR1 1, DIR2 2, A1–A4 3–6, DIR3 7, DIR4 8, OE 9, GND 10, B4–B1 11–14, VCCB 15, VCCA 16.

## Why

FPGA JTAG (TMS 5, TCK 6, TDI 7, TDO 8) is in bank 3 at 1.8 V (`E-fpga-gw1nr9.md`). The RP2350 at IOVDD 3.3 V needs VIH ≥ 2.0 V (RP2350 Tab 1436); the FPGA's TDO gives VOH ≥ VCCIO − 0.4 = 1.4 V. Driving 3.3 V into the dedicated JTAG inputs before configuration relies on an undocumented clamp state, so all four lines are translated. Per-bit DIR lets one 4-bit part carry 3 lines one way and TDO the other.

## Connection

- **A port = 3.3 V side** (VCCA = `+3V3`): RP2350 GPIO22 TCK, GPIO23 TMS, GPIO24 TDI, GPIO25 TDO; **and the JTAG header (R-22, block G) on these same A-side nets**, so a standard 3.3 V probe works.
- **B port = 1.8 V side** (VCCB = `+1V8`): FPGA TCK, TMS, TDI, TDO.
- DIR1–3 = H (A→B: TCK, TMS, TDI) tied to VCCA; DIR4 = L (B→A: TDO) tied to GND. Control pins are referenced to VCCA (§5), so 3.3 V straps are correct.
- **OE**: 10 kΩ pull-up to VCCA (datasheet §5: "OE should be tied to VCCA through a pull-up" to stay Hi-Z through power-up) and driven low by RP2350 GPIO27 `FPGA_JTAG_OE_N` when the RP2350 or an external probe needs the port. RP2350 resets "pulled low" (36–113 kΩ) vs the 10 kΩ pull-up → OE reads ≥ 3.3 × 36/46 = 2.58 V ≥ VIH 2.0 V: isolated at reset. When an external probe is used, firmware drives OE low and puts GPIO22–24 in Hi-Z (or holds the RP2350 in BOOTSEL/reset with OE strapped by a solder jumper — block G's choice).
- A-side inputs must not float (§7.3 note 3): 10 kΩ pull-down on TCK (A1), 10 kΩ pull-ups on TMS (A2) and TDI (A3) to `+3V3`. B-side TCK keeps the FPGA's required 4.7 kΩ pull-down (UG284), which is also the defined state while the translator is isolated.

## Ratings vs use

| Parameter | Datasheet | Ours | OK |
|---|---|---|---|
| VCCA, VCCB | 1.2–3.6 V (§7.3) | 3.3 V / 1.8 V | OK |
| VIH data, VCCI 2.7–3.6 V | ≥ 2.0 V | RP2350 VOH ≥ 2.62 V | OK |
| VIH data, VCCI 1.2–1.95 V | ≥ 0.65 × VCCI = 1.17 V | FPGA VOH ≥ 1.4 V | OK |
| Data rate 1.8 ↔ 3.3 V | 380 Mbps typ (features) | TCK ≤ 25 MHz | OK |
| I/O tolerance | 4.6 V; Ioff partial power-down (§8.3.3) | if either rail is down, both ports Hi-Z ("VCC isolation", §5) | OK |

## Calculations

- Pull-ups/-downs: 3.3 V / 10 kΩ = 0.33 mA static where opposed — only while driven against; negligible.
- Delay ≈ few ns (switching table, 1.8 ↔ 3.3 V) ≪ the 40 ns TCK period at 25 MHz; JTAG timing (Tjps 10 ns, Ttckftco ≤ 10 ns, UG290 Tab 7-5) has slack at the 10–20 MHz we use.
- Decoupling: 100 nF on VCCA and on VCCB (`C1525`, basic).

## Fine print

- "To ensure the high-impedance state during power-up or power-down, OE should be tied to VCCA through a pull-up resistor" (§5).
- Control inputs referenced to VCCA — never strap DIR to VCCB.
- RECONFIG_N is **not** through this part: the RP2350 drives it open-drain directly (`E-fpga-gw1nr9.md`).

## Layout

Translator between the RP2350 and the FPGA's left edge; B-side traces ≤ 20 mm to FPGA pins 5–8; header on the A side.
