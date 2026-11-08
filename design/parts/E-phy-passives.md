# PHY passives — LAN8720AI support network

Serves: U-PHY (`E-phy-lan8720.md`). Datasheets: `datasheets/lan8720a.pdf` (Tab 2-5…2-7, §3.7, §3.8.1, Fig 3-16/3-18/7-3/7-5, Tab 5-8), `datasheets/murata-blm18pg221sn1d.pdf`, `datasheets/samsung-mlcc-catalog.pdf`, `datasheets/fh-0402cg150j500nt.pdf` (FH C0G 0402 series), `datasheets/uniroyal-0402wgf.pdf`.

## Parts

| Ref/function | Value | Part | Supplier line (2026-11-07) | Qty |
|---|---|---|---|---|
| RBIAS (pin 24) | 12.1 kΩ 1 % 0402 | 0402WGF1212TCE | `C25852 0402WGF1212TCE (UNI-ROYAL, 0402): extended, JLC stock 538022, lifecycle normal` | 1 |
| VDDCR (pin 6) | 1 µF X5R 25 V 0402 ∥ 470 pF X7R 50 V 0402 | CL05A105KA5NQNC / 0402B471K500NT | `C52923 … basic, JLC stock 11554041, lifecycle normal`; `C1537 0402B471K500NT (FH, 0402): preferred, JLC stock 568810, lifecycle normal` | 1 + 1 |
| VDD1A (19), VDD2A (1), VDDIO (9) CBYPASS | 100 nF X7R 16 V 0402 | CL05B104KO5NNNC | `C1525 … basic, JLC stock 34322291, lifecycle normal` | 3 |
| VDDIO CF bulk; analog-island bulk | 4.7 µF X5R 16 V 0603 | CL10A475KO8NNNC | `C19666 … basic, JLC stock 3850946, lifecycle normal` | 2 |
| Analog 3.3 V island feed (VDD1A, VDD2A, 49.9 Ω, centre taps) | 220 Ω @ 100 MHz bead | BLM18PG221SN1D | `C80165 … extended, JLC stock 218690, lifecycle normal` | 1 |
| MDI terminations TXP, TXN, RXP, RXN → filtered 3.3 V | 49.9 Ω 1 % **0603** | 0603WAF499JT5E | `C23185 0603WAF499JT5E (UNI-ROYAL, 0603): basic, JLC stock 1638012, lifecycle normal` | 4 |
| MDI termination centre bypass (Fig 7-5 CBYPASS at the 49.9 Ω junctions) | 100 nF 0402 | C1525 | as above | 2 |
| Magnetics PHY-side centre taps bypass | 100 nF 0402 | C1525 | as above | 2 (block A's RJ45 pins; placed here) |
| nRST pull-down | 10 kΩ 0402 | 0402WGF1002TCE | `C25744 0402WGF1002TCE (UNI-ROYAL, 0402): basic, JLC stock 22766926, lifecycle normal` | 1 |
| nINT pull-up to VDDIO (now an FPGA input, B13) | 10 kΩ | C25744 | as above | 1 |
| MDIO pull-up to 3.3 V | 1.5 kΩ 0402 | 0402WGF1501TCE | `C25867 0402WGF1501TCE (UNI-ROYAL, 0402): basic, JLC stock 1388505, lifecycle normal` | 1 |
| LED1 (active-high, to GND), LED2 (active-low, to VDD2A) series R | 270 Ω (datasheet "~270 Ω") | 0402WGF2700TCE | `C25099 0402WGF2700TCE (UNI-ROYAL, 0402): extended, JLC stock 1106178, lifecycle normal` | 2 (J1 has LEDs: green on LED1, yellow on LED2) |

## Calculations

- **RBIAS**: "requires 12.1 kΩ (1 %) to ground… dissipates ≈ 1 mW" at 1.2 V nominal (Tab 2-6): P = 1.2² / 12.1 k = 0.12 mW. (The datasheet's "≈ 1 mW" is the device's bias, not the resistor's; the 0402's 62.5 mW rating covers either.)
- **49.9 Ω terminations**: per Fig 7-5 they tie each MDI line to the analog 3.3 V; DC current per line ≈ half the line-driver current; total through the bead ≤ 41 mA (100BASE-TX) / 100 mA (10BASE-T) (Note 5-7). Power per resistor worst (10BASE-T, 25 mA each, assumed even split): 25 mA² × 49.9 Ω = 31 mW < 62.5 mW (1/16 W, Uniroyal). In 100BASE-TX ≈ 10 mA² × 49.9 = 5 mW. OK; 0603 (1/10 W) is safer for 10BASE-T if the split is uneven — **use 0603 for the four 49.9 Ω**.
- **Bead**: ≤ 130 mA × 0.10 Ω = 13 mV drop; rated 1.4 A.
- **VDDCR caps**: 1 µF + 470 pF exactly as Tab 2-7 note. DC bias on 1 µF 25 V at 1.2 V is < 5 % of rating → negligible.
- **nRST pull-down vs FPGA drive** (ball B12): 3.3 V / 10 kΩ = 0.33 mA when released high — fine. Holds the PHY in reset until the gateware releases it ≥ 25 ms after `+3V3` is good (Tab 5-8 tpurstd).
- **MODE straps**: the 4.7 kΩ pull-ups on RXD0/RXD1/CRS_DV are listed with the FPGA passives (`E-fpga-ecp5-passives.md`, review MAJOR-2).
- **MDIO**: 1.5 kΩ with ~20 pF → τ = 30 ns; MDC period ≥ 400 ns (Tab 5-12) → rise < 100 ns, fine. Sink current 3.3 V / 1.5 kΩ = 2.2 mA < VOD8 8 mA.
- **LED/strap**: with LED2 + 270 Ω to VDD2A, the strap sees VDD2A minus the LED's leakage → reads 1 (nINTSEL = REF_CLK In). With LED1 + 270 Ω to GND, REGOFF reads 0 (regulator on). Straps follow Fig 3-10/3-11 exactly.

## Fine print

- LED/strap pull-ups go to VDD2A, not VDDIO (§3.8.1 note; Note 3-3).
- Straps must not be driven (Note 5-22).

## Layout

- 49.9 Ω and their bypass at the PHY's MDI pins, symmetric per pair; the bead + 4.7 µF where the analog island meets `+3V3`.
- VDDCR caps at pin 6; RBIAS at pin 24 with a short, private GND return.

## Open questions

- **Closed (block A review A-n7)** from `A-poe-magjack.md`'s pin map of J1 LPJK6078AHNL:
  - **Pairs and centre taps:** PHY TX± → pins 11/10 (MD1±, CT pin 12); PHY RX± → pins 4/5 (MD2±, CT pin 6). The 49.9 Ω terminations and CT bypasses go on those nets. The PHY-side CTs 12 and 6 go to the filtered analog 3.3 V. Pins 1–3 and 7–9 (MD3/MD4 and their CTs) stay open.
  - **LEDs:** green 20(+)/19(−) on LAN8720A **LED1** (link/activity, active-high): LED1 → 270 Ω → pin 20, pin 19 → GND. Yellow 18(+)/17(−) on **LED2** (100 Mb/s, active-low): VDD2A → pin 18, pin 17 → 270 Ω → LED2. This is exactly Fig 3-10/3-11, so REGOFF reads 0 and nINTSEL reads 1.
  - **LED current:** (3.3 − VF 1.8–2.6 V) / 270 Ω = 2.6–5.6 mA, within the LED2/LED1 O12 drive. The LED pins sit on the secondary side, inside A's barrier note: route them away from CT pins 13–16.
