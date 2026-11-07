# U (Ethernet PHY) — Microchip LAN8720AI-CP-TR

> **ECP5 update (2026-11-07).** MDC, MDIO, nRST and nINT now go to the FPGA (balls A13, A14, B12, B13; it hosts the MAC), not the RP2350. nRST keeps its 10 kΩ pull-down (the ECP5 also pulls unconfigured pins down), so the PHY stays in reset until the FPGA design releases it ≥ 25 ms after the rails. The RMII group sits on ECP5 top bank 1 (`E-clk-rmii-50mhz.md`). Everything else below is unchanged.


Datasheet: `datasheets/lan8720a.pdf` (LAN8720A/LAN8720AI DS00002165B, 2016). Read: all sections (pin description, RMII, SMI, interrupts, straps, LEDs, variable I/O, resets, application diagrams, ratings, power, DC/AC tables, clock circuit, application notes).
MPN: LAN8720AI-CP-TR (I = industrial, −40…+85 °C; CP = 24-QFN 4 × 4 mm)
Supplier: `C17146 LAN8720AI-CP-TR (MICROCHIP, QFN-24-EP(4x4)): extended, JLC stock 9257, lifecycle normal, checked 2026-11-07`
Footprint: 24-QFN 4 × 4 mm, 0.5 mm pitch, terminals 0.25 × 0.40 mm, **exposed pad 2.5 × 2.5 mm (2.40–2.60)**, terminal-to-EP ≥ 0.25 mm (§6.1, punch package); exposed pad to GND ("must be connected to the ground plane with a via array", Tab 2-7). Pin map Tab 2-8. KiCad `QFN-24-1EP_4x4mm_P0.5mm_EP2.5x2.5mm` (check pad length against L = 0.40 in phase 2).

## PHY choice: LAN8720AI, not RTL8201F-VB-CG

| | LAN8720AI (C17146) | RTL8201F-VB-CG (C45044) |
|---|---|---|
| Ambient rating | **−40…+85 °C** (Note 5-4, industrial) | **0…+70 °C** (`datasheets/rtl8201f.pdf` §: "Ambient Operating Temperature TA 0…70 °C"; crystal spec Ta 0–70 °C) |
| R-40 (parts ≥ 85 °C ambient; cabinet air 55 °C) | meets | **fails** |
| Stock | 9257 | 42934 |
| Package | 24-QFN 4×4 | 32-QFN 5×5 |
| RMII REF_CLK in, compliant timing | yes (Tab 5-10) | yes |
| VDDIO | 1.62–3.6 V | — |
| Internal 1.2 V regulator | yes (REGOFF strap) | yes |
| Ubiquity / open MAC references | very common (ESP32, STM32, LiteEth boards) | common |

The temperature grade decides it. No pin-compatible second source in stock (JL1101 has 0); accepted as a single-source part with 9257 in stock against a need of 7.

## Absolute max vs our worst case (§5.1, §5.2)

| Parameter | Abs max | Operating | Ours | OK |
|---|---|---|---|---|
| VDDIO, VDD1A, VDD2A | −0.5…3.6 V | VDDIO 1.62–3.6; VDDA 3.0–3.6 V | `+3V3` ±3 % = 3.40 V max | OK (3.6 V abs — keep the 3V3 buck's overshoot < 0.2 V) |
| VDDCR | 1.5 V | 1.08–1.32 V | internal regulator | OK |
| Signal pins | +6 V / −0.5 V | | 3.3 V CMOS | OK |
| XTAL1/CLKIN | +3.6 V | | 3.3 V CMOS osc | OK |
| Magnetics supply | 3.6 V | 2.25–3.6 V | 3.3 V | OK |
| TA | | −40…+85 °C | ≤ 55 °C + rise; θJA 59.8 °C/W × 0.16 W = +10 °C | OK |
| ESD | HBM class 3A; IEC 61000-4-2 ±8 kV contact (3rd-party tested, on the line side) | | block A's RJ45/magnetics take the strike | OK |

## Configuration (straps latched at POR and nRST release, §3.7)

| Strap | Pin | Wanted | How |
|---|---|---|---|
| MODE[2:0] = 111 (all capable, auto-neg) | RXD0 (8), RXD1 (7), CRS_DV (11) | 111 | internal pull-ups; the FPGA pins they connect to also idle with weak pull-ups during configuration → consistent. No external resistor. |
| PHYAD0 = 0 | RXER (10) | 0 | internal pull-down; **RXER left unconnected** (optional in RMII; frame errors are caught by FCS) → test point only |
| REGOFF = 0 (internal 1.2 V regulator on) | LED1 (3) | 0 | internal pull-down; LED1 then active-high: LED + 270 Ω **to GND** (Fig 3-10) |
| nINTSEL = 1 (REF_CLK In mode, nINT available) | LED2 (2) | 1 | LED2 then active-low: LED + 270 Ω **to VDD2A** (Fig 3-11); this also pulls the strap high. Pull-ups for LED pins go to VDD2A, not VDDIO (§3.8.1 note) |

Strap timing (Tab 5-8): nRST held low ≥ 25 ms after supplies reach 80 % (tpurstd), assertion ≥ 100 µs, straps valid 200 ns before release. nRST is driven by the RP2350 (`PHY_NRST`, GPIO30) with a 10 kΩ pull-down so it is low from power-up until firmware releases it; RP2350 GPIOs reset to "pulled low" (RP2350 §9.3) as well.
After reset the RMII runs at 2.5 MHz for 16 µs, then 25 MHz (§3.8.5 note) — the MAC must tolerate that.

## Required external parts (datasheet application diagrams §3.9, §7.1) → `E-phy-passives.md`

- RBIAS: 12.1 kΩ 1 % to GND (Tab 2-6).
- VDDCR: 1 µF + 470 pF to GND (Tab 2-7 note).
- VDD1A, VDD2A, VDDIO: CBYPASS each (100 nF) + bulk; VDDIO "CF" bulk.
- TXP/TXN/RXP/RXN: 4 × 49.9 Ω to the 3.3 V analog supply through a ferrite bead, with CBYPASS (Fig 3-18 / 7-5); magnetics centre taps (PHY side) to the same filtered 3.3 V. The 75 Ω Bob Smith network and 1000 pF 3 kV on the line side belong to block A's RJ45/magnetics (LPJK6078AHNL).
- nRST pull-down 10 kΩ (ours, above). nINT pull-up to VDDIO ("place an external resistor pull-up to VDDIO", Tab 2-5): 10 kΩ.
- MDIO pull-up: SMI is open-drain output (VOD8) → 1.5 kΩ to 3.3 V (802.3 clause 22 practice; the datasheet only says VOD8). MDC ≤ 2.5 MHz (period ≥ 400 ns, Tab 5-12) from the RP2350.

## Calculations

- **Power (§5.3.1, REF_CLK In, 100BASE-TX with traffic, max):** VDDA 28 mA + VDDCR 21 mA (drawn from VDD2A by the internal regulator) + VDDIO 0.6 mA = 49.6 mA at 3.3 V = 164 mW. **Magnetics centre-tap current**: typ 41 mA in 100BASE-TX, **100 mA in 10BASE-T** (Note 5-7). Worst case 10BASE-T: VDDA ~10 + VDDCR 13 + 100 = ~123 mA; worst case 100BASE-TX: 49.6 + 41 = 91 mA. **Design: 150 mA on `+3V3`.**
- **Junction temperature:** P ≈ 0.16 W (chip; centre-tap current dissipates in the line drivers' load, mostly outside) × 59.8 °C/W = +10 °C → Tj ≈ 70 °C at 55 °C air + 5 °C board. OK.
- **Ferrite for the analog 3.3 V**: carries VDD1A + VDD2A + centre taps ≤ 130 mA → BLM18PG221SN1D (1.4 A, 0.10 Ω) drop 13 mV. OK.
- **RMII timing**: in `E-clk-rmii-50mhz.md` (closes with +5.0 / +2.5 ns RX after IODELAY, +9.4 / +1.4 ns TX).
- **I/O levels** (Tab 5-4, VDDIO 3.3 V): VIS inputs VIHT ≤ 1.90 V, VILT ≥ 1.41 V (Schmitt) — the FPGA's 3.3 V outputs (VOH ≥ VCCIO − 0.4 V) drive them. VO8 outputs VOH ≥ VDDIO − 0.4 V at 8 mA — meets FPGA LVCMOS33 VIH 2.0 V.

## Fine print / gotchas

- "Do not drive input signals without power supplied to the device" (§5.2) and "input signals must not be driven high before power is applied" (§3.8.2): PHY, FPGA bank 1 and the 50 MHz oscillator all on `+3V3` → OK. On USB-only power (R-23) the PHY is powered too, so nothing back-drives it.
- VDDIO and magnetics supply must stay within ±10 % after power-up (§5.2).
- Power sequencing: all supplies within 50 ms of each other (tpon, Tab 5-7) — single rail, trivially met.
- Straps "must only be pulled high or low and must not be driven as inputs" (Note 5-22): the FPGA must not drive RXD/CRS_DV (they're FPGA inputs; constrain them as inputs in the CST).
- REF_CLK In mode: XTAL2 unconnected.

## Layout guidance (datasheet + domains/high-speed.md)

- PHY close to block A's RJ45 (MDI pairs short, 100 Ω differential, symmetric, no vias, over solid GND) and ≤ 25 mm from the FPGA's right edge (RMII group, 50 Ω single-ended, matched ±10 mm).
- 49.9 Ω resistors and their CBYPASS at the PHY pins; ferrite + bulk between `+3V3` and the analog island.
- EP to GND with a via array; RBIAS resistor at pin 24 with its own short GND return.

## Open questions

- MDIO pull-up value: the datasheet states open-drain only; 1.5 kΩ is the IEEE 802.3 clause 22 figure (not in this datasheet) — confirm against the RP2350's 2.5 MHz MDC with ~20 pF: τ = 30 ns ≪ 200 ns half-period.
