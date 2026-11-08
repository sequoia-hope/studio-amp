# ECP5 passives — decoupling, VCCAUX filter, sysCONFIG/JTAG straps, input series resistors

Serves: U-FPGA (`E-fpga-ecp5.md`). Sources: `datasheets/lattice-FPGA-TN-02038.pdf` (Tab 3.1 filtering, §3.2 bead selection, §3.5 capacitors, Tab 6.1–6.3 configuration/JTAG pins), `datasheets/lattice-FPGA-TN-02039.pdf` (Tab 4.5/6.3 notes), `datasheets/lattice-FPGA-DS-02012.pdf` §3.6 (hot socketing). Part data: `datasheets/murata-blm18pg221sn1d.pdf` (Murata BLM18 reference specification; the table covers BLM18PG121SN1D as well), `datasheets/samsung-mlcc-catalog.pdf`, `datasheets/uniroyal-0402wgf.pdf`.

## Parts

| Function | Value | Part | Supplier line (2026-11-07) | Qty |
|---|---|---|---|---|
| VCC (1.1 V) per-pin (G6, G7, G9, L8, L9, L10) | 100 nF X7R 16 V 0402 | CL05B104KO5NNNC | `C1525 … basic, JLC stock 34321739, lifecycle normal` | 6 |
| VCC bulk | 10 µF X5R 10 V 0603 | CL10A106KP8NNNC | `C19702 CL10A106KP8NNNC (Samsung Electro-Mechanics, 0603): basic, JLC stock 10318619, lifecycle normal` | 3 |
| VCCAUX (2.5 V) bead | 120 Ω @ 100 MHz, 2 A, 0.05 Ω max | BLM18PG121SN1D | `C14709 BLM18PG121SN1D (muRata, 0603): basic, JLC stock 1968621, lifecycle normal` | 1 |
| VCCAUX bulk after bead | 10 µF 0603 | C19702 | as above | 1 |
| VCCAUX per-pin (G11, L7) | 100 nF 0402 | C1525 | as above | 2 |
| VCCIO0–3, 7, 8 bulk | 10 µF 0603 | C19702 | as above | 6 |
| VCCIO6 bulk (8 PWM outputs + SPI; "banks with lots of outputs") | 22 µF X5R 25 V 0805 | CL21A226MAQNNNE | `C45783 CL21A226MAQNNNE (Samsung Electro-Mechanics, 0805): basic, JLC stock 3392859, lifecycle normal` | 1 |
| VCCIO per-pin (F6, F7, F10, F11, H11, J11, K11, L11, J6, J7, H6, H7, L6) | 100 nF 0402 | C1525 | as above | 13 |
| SN, HOLDN, PROGRAMN, INITN, DONE pull-ups; CFG0 pull-up; TDI, TMS, TDO pull-ups; TCK pull-down; VB_CS_n, IS_CS_n, PF_CS_n pull-ups; **LAN8720A MODE strap pull-ups on RMII_RXD0, RMII_RXD1, RMII_CRSDV to +3V3** (review MAJOR-2); `POE_LOSS_N` pull-up (pre-configuration sweep); `ACF_PULSE` series | 4.7 kΩ 0402 | 0402WGF4701TCE | `C25900 0402WGF4701TCE (UNI-ROYAL, 0402): basic, JLC stock 15759181, lifecycle normal` | 18 |
| CFG1, CFG2 to GND | 0 Ω / direct | — | — | — |
| CCLK series at the RP2350 | 33 Ω 0402 | 0402WGF330JTCE | `C25105 0402WGF330JTCE (UNI-ROYAL, 0402): basic, JLC stock 3866666, lifecycle normal` | 1 |
| CCLK pull-up to VCCIO8 (TN-02038 Tab 6.2 "510 Ω to 1 kΩ"; TN-02039 Tab 4.5 note 6) — review MINOR-2 | 1 kΩ 0402 | 0402WGF1001TCE | `C11702` (below) | 1 |
| `IBUS_SENSE` hold-up cap at RP2350 ADC4 | 100 nF X7R 16 V 0402 | CL05B104KO5NNNC | `C1525` (above) | 1 |
| RMII_TXEN pull-down. (PHY_NRST pull-down and PHY_NINT pull-up are counted in `E-phy-passives.md`.) | 10 kΩ 0402 | 0402WGF1002TCE | `C25744 0402WGF1002TCE (UNI-ROYAL, 0402): basic, JLC stock 22766675, lifecycle normal` | 1 |
| Series R, fast always-driven inputs on left/right banks (FAULT_W_n, FAULT_T_n, MADC_DOUT, PDM_DAT) | 330 Ω 0402 | 0402WGF3300TCE | `C25104 0402WGF3300TCE (UNI-ROYAL, 0402): basic, JLC stock 1951308, lifecycle normal` | 4 |
| Series R, slow always-driven inputs (PD_PG_N, PD_TPH_N, PD_TPL_N, PD_BT_N, POE_LOSS_N on top bank; PG_5V, PG_3V3, PG_3V3Q on top; HP_FAULT_N, HP_DET, LED_FAULT_N, QWIIC_FAULT_N, VUSB_DET on right; DC_W_n, DC_T_n on left) | 1 kΩ 0402 | 0402WGF1001TCE | `C11702 0402WGF1001TCE (UNI-ROYAL, 0402): basic, JLC stock 33762806, lifecycle normal` | 15 |

All basic parts. Pull-ups go to VCCIO8 = `+3V3`.

## Calculations

- **Decoupling** exactly per TN-02038 Tab 3.1: VCC 3 × 10 µF + 100 nF/pin; VCCAUX 120 Ω bead + 10 µF + 100 nF/pin; VCCIO 10 µF + 100 nF/pin (22 µF for the busy PWM bank).
- **Bead drop** (TN-02038 §3.2: ESR × I < 1 % of rail for non-analog, < 0.25 % sensitive): VCCAUX 50 mA × 0.05 Ω = 2.5 mV = **0.10 %** of 2.5 V. OK even for the PLL target. Murata rating 2 A @ 85 °C (BLM18PG121SN1D row).
- **Capacitor voltage** (TN-02038 §3.5.2: ≥ 80 % above the rail): 3.3 V → ≥ 5.94 V → 10 V or 16 V parts used (10 µF 10 V on 1.1/2.5 V rails is 4–9×; on 3.3 V use the 10 V part = 3.0×, OK). DC-bias loss of the 10 µF 0603 10 V X5R at 3.3 V: not in the catalogue in hand; the 3 × 10 µF + 100 nF network has margin, and the phase 8 PDN check is where it gets verified.
- **Config pull-ups**: TN-02038 Tab 6.2 (PROGRAMN, INITN 4.7 kΩ; CFG 1–10 kΩ), TN-02039 Tab 4.5 note 1 (SN 4.7 kΩ), Tab 6.1 (JTAG). DONE is open-drain with weak pull-up (TN-02039 §4.6.4); 4.7 kΩ so the RP2350 reads it cleanly. CFG0 high via 4.7 kΩ ≫ internal pull-up; CFG1/2 tied to GND (TN-02039 §4.6.1: external < 500 Ω pulls low; direct GND is simplest).
- **CCLK series and pull-up**: 22–80 Ω range (TN-02038 Tab 6.2 note 1) → 33 Ω at the RP2350 driver. Plus a **1 kΩ pull-up to VCCIO8** (Tab 6.2; TN-02039 Tab 4.5 note 6), so CCLK is defined while the RP2350 is in reset (its pad pull-down 36–113 kΩ would otherwise fight the ECP5's weak pull-up near mid-rail). The RP2350 SCK pad is set to 8 mA: it sinks 3.3 mA into the 1 kΩ when low, and VOL ≤ 0.5 V holds.
- **LAN8720A MODE straps** (review MAJOR-2): RXD0/RXD1/CRS_DV carry the PHY's MODE[2:0] straps, which have internal pull-ups of ~50 µA typ (LAN8720A Note 5-12/5-14). The ECP5 input pull-down (30–150 µA) would win and latch MODE = 000 (10BASE-T half-duplex, no auto-negotiation). The datasheet says a loaded strap "should" get an external resistor (§3.7). 4.7 kΩ to +3V3: against a 150 µA pull-down the pin sits at ≥ 3.3 − 0.7 = 2.6 V ≥ VIHT max 1.90 V (Tab 5-4). 10 kΩ would give only 1.8 V, below 1.90 V. Gateware also sets **PULLMODE=UP on A11, A12, B11** in the LPF, and releases nRST only after configuration.
- **POE_LOSS_N pull-up**: block B's comparator output is open-drain → **4.7 kΩ** to +3V3 on the net, ahead of the FPGA's 1 kΩ series and block F's OR diode; 0.7 mA when asserted. 10 kΩ would sit at only 1.8 V against the ECP5's pre-configuration 150 µA pull-down (`E-pinmap.md` sweep).
- **IBUS_SENSE 100 nF** (block B's final source ≈ 67 kΩ, already RC-filtered at 3.4 kHz): the reservoir keeps the RP2350 S/H charge-sharing error ≈ C_SH / 100 nF, negligible. The added pole is 1/(2π · 67 kΩ · 100 nF) = 24 Hz, which is fine for telemetry; the CC limit itself is block B's hardware. RP2350 pad leakage ≤ 1 µA (Tab 1436) × 67 kΩ ≤ 67 mV worst case (2.2 % of FS; typical is far lower). Acceptable for telemetry; if better is wanted, block B lowers its divider to ≤ 20 kΩ Thevenin.
- **ACF_PULSE 4.7 kΩ series**: the source is block B's 74LVC2G08 gate B on +3V3, the same rail as the FPGA, so there is no injection; 4.7 kΩ is kept as harmless margin. RC with 8 pF = 38 ns against pulses as short as ≈ 0.25 µs (light-load DCM) at a 1.36 µs period: fine.
- **ADC CS pull-ups vs FPGA pull-down during configuration**: the pull-up must hold CS above VIH (0.7 × 3.3 V = 2.31 V for a CMOS ADC input) against the FPGA's ≤ 150 µA weak pull-down: R ≤ (3.3 − 2.31) V / 150 µA = 6.6 kΩ → **4.7 kΩ** (CS ≥ 2.6 V). 10 kΩ would leave 1.8 V, which isn't a valid high.
- **RMII_TXEN pull-down**: the FPGA's own weak pull-down already holds it low; 10 kΩ is a backstop (also covers the unpowered-FPGA case).
- **PHY_NRST pull-down**: 10 kΩ holds the PHY in reset until the FPGA design releases it. The FPGA design must wait ≥ 25 ms after the rails (LAN8720A tpurstd).
- **Hot-socket series resistors** (DS §3.6, Tab 3.5: left/right A/B pairs present a low-impedance path while VCC < POR; IDK up to ±33 mA): partner pins are left unconnected, so there is no second driver. The series R limits any residual current to (3.3 V)/R: 10 mA at 330 Ω, 3.3 mA at 1 kΩ. RC with ~8 pF: 2.6 ns (330 Ω) on the 200 ns OC-trip budget and 3.072 MHz audio data; 8 ns (1 kΩ) on slow lines. On the top bank (IDK ≤ ±1 mA) the 1 kΩ is belt and braces.

## Layout

- 100 nF per power ball on the bottom side under the ball field, between dog-bone vias (6-layer stack, `E-fpga-ecp5.md` fan-out); 10/22 µF just outside the package outline.
- VCCAUX bead + 10 µF at the 2V5 entry; keep VCCAUX away from PWM-bank return currents.
- Straps near bank 8 (bottom edge), on the RP2350 side.
