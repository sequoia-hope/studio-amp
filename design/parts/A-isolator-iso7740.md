# U (block A) — ISO7740 4-channel digital isolator for PD status (R-32a), with its primary supply and PG buffer

Datasheets:
- `datasheets/A-iso7740.pdf` (TI ISO7740/41/42, ZHCSF48F, May 2019 — Chinese-language edition served by
  LCSC; tables and figures identical to SLLSEP3). Read: features, pinout (p.6–7), §7.1–7.6 ratings and
  insulation (pp.8–10), §7.10/7.12 supply current (pp.13, 15), switching and default-output (§7.x, p.~18),
  function table (§9.4).
- `datasheets/A-78l05-utc.pdf` (UTC 78LXX, QW-R101-001.R). Read: all 8 pages.
- `datasheets/A-2n7002-cj.pdf` (JSCJ 2N7002, Sep 2016). Read: all pages.

| Part | MPN | Supplier line (checked 2026-11-07) |
|---|---|---|
| Isolator | ISO7740DWR (SOIC-16 wide, default-high outputs) | `C529547 ISO7740DWR (TI, SOIC-16-300mil): extended, JLC stock 8551, lifecycle normal` |
| Primary 5 V LDO | 78L05G-AB3-R (SOT-89) | `C71136 78L05G-AB3-R (UTC, SOT-89-3): basic, JLC stock 235078, lifecycle normal` |
| PG buffer FET | 2N7002 (SOT-23) | `C8545 2N7002 (JSCJ, SOT-23): basic, JLC stock 5965613, lifecycle normal` |
| Pull-ups (4) | 10 kΩ 1 % 0603 | `C25804 0603WAF1002T5E (UNI-ROYAL, 0603): basic, JLC stock 43393018, lifecycle normal` |
| Decoupling | 100 nF 50 V X7R 0603 (VCC1, VCC2, LDO out) | `C14663 CC0603KRX7R9BB104 (YAGEO, 0603): basic, JLC stock 34235460, lifecycle normal` |
| LDO input cap | 330 nF 50 V X7R 0805 | `C1740 0805B334K500NT (FH, 0805): preferred, JLC stock 107110, lifecycle normal` |

Second source for the isolator, same pinout class (not audited): Chipanalog CA-IS3740HW (C528653,
3717 stock, wide body, "H" = default high). Only if TI stock fails.
Footprints: SOIC-16W 7.5 mm body (DW), KiCad `SOIC-16W_7.5x10.3mm_P1.27mm`; SOT-89-3 (pinout for
-AB3-R: **1 = O, 2 = G, 3 = I**, `A-78l05-utc.pdf` p.1 — not the usual I-G-O); SOT-23 (1 G, 2 S, 3 D).

## Circuit (what phase 2 draws)

Primary side (ground = `VPRI_RTN`, the TPS2373 RTN):

- `VB_PRI` (= TPS2373 VC_IN; block B's 13.5 V LM5019 bias buck on VPRI) → 330 nF → 78L05 → `VISO_P5V` (5 V) → 100 nF → ISO7740 VCC1 (pin 1),
  GND1 (pins 2, 8) to RTN.
- TPS2373 TPH → INA (pin 3), TPL → INB (pin 4), BT → INC (pin 5), each with 10 kΩ to `VISO_P5V`.
- PG buffer: TPS2373 PG → 1 kΩ (block B) → UCC2897A SS/SD. The 2N7002 gate sits on the **SS/SD side** of that 1 kΩ; drain → IND
  (pin 6) with 10 kΩ to `VISO_P5V`; source to RTN.

Secondary side (ground = `GND`): VCC2 (pin 16) = `+3V3` with 100 nF; GND2 (pins 9, 15); EN2 (pin 10)
tied to VCC2; OUTA–OUTD (pins 14, 13, 12, 11) → `PD_TPH_N`, `PD_TPL_N`, `PD_BT_N`, `PD_PG_N` to the FPGA
(block E). Pin 7 NC.

All four signals are **active low**, and the default-high ISO7740 reads "not asserted / not good" whenever
the primary side is unpowered (function table: "When VCCI is unpowered, a channel output assumes the
logic state based on the selected default option. Default is High for ISO774x"). That is the safe
reading: the secondary only runs when the converter runs anyway.

## Why each choice

- **ISO7740 (4 forward channels, default high, DW)**: R-32a needs 4 signals one way. DW package: VISO
  5000 Vrms, VIORM 2121 Vpk, CLR/CPG > 8 mm, CTI > 600 V (insulation table p.10) — well above R-32's
  1500 Vrms, and the 8 mm creepage sets the minimum barrier width at this part. The DBQ version
  (3000 Vrms, 3.7 mm) would also meet R-32 but gives no margin for a product spin.
- **Fed from VB_PRI (= VC_IN)**: block B's bias buck, which also powers the UCC2897A; the TPS2373
  startup source is not used at all (`A-pd-tps2373.md` calc 6). Block B must budget ≤ 15.3 mA for this
  branch. TPH/TPL/BT are not valid until 24 ms after PG releases
  rises anyway (TPS2373 p.19). Before that the outputs sit at their default (high).
- **PG buffered by a 2N7002**: TPS2373 PG is wired to the UCC2897A SS/SD pin (TI's Figure 21 interface,
  TPS2373 p.17). SS/SD is an analog soft-start ramp (0 → ~5 V, controlled by an internal current of
  ~14 µA, UCC2897A §8.3.1.10). Hanging an isolator input on it would load the ramp through the input's
  clamp diodes and leave the logic level undefined during the ramp. A MOSFET gate draws ≤ 80 nA
  (IGSS, `A-2n7002-cj.pdf` p.2), so the soft-start is unaffected, and its 1.0–2.5 V threshold turns the
  ramp into a clean logic edge. Inversion is fine: PD_PG_N low = "PD out of inrush and the converter's
  soft start past ~2.5 V". It also goes high whenever the UCC2897A discharges SS/SD (its own UVLO or
  line-UV), so PD_PG_N reads "primary converter enabled", which is what the FPGA needs.

## Absolute max vs our worst case

| Part / parameter | Abs max | Worst case | Margin |
|---|---|---|---|
| ISO7740 VCC1, VCC2 | 6 V | 5.25 V (78L05 max, p.3); 3.3 V ±5 % | OK |
| ISO7740 INx | VCC1 + 0.5 V (≤ 6 V) | pulled up to VCC1 | OK |
| ISO7740 OUTx current | ±15 mA abs; IOH/IOL 2 mA at 3.3 V rec | FPGA CMOS input | OK |
| ISO7740 isolation | 5000 Vrms 60 s; VIORM 2121 Vpk | 1500 Vrms test; working ≈ 0 V | OK |
| 78L05 VIN | 30 V | VB_PRI 13.5 V | OK |
| 78L05 PD (SOT-89) | 350 mW at 25 °C | 157 mW at 13.5 V | see calc 3 |
| 2N7002 VDS | 60 V | 5 V | OK |
| 2N7002 VGS | ±20 V | SS/SD ≤ ~5 V | OK |
| TPS2373 TPx/PG sink | 3 mA rec | 5 V / 10 kΩ = 0.5 mA | OK |

## Calculations

1. **Logic levels, primary**: VIH ≥ 0.7 x VCC1 = 3.5 V, VIL ≤ 0.3 x VCC1 = 1.5 V (rec. operating p.8).
   TPx low: VOL ≤ 0.5 V at 2 mA (TPS2373 p.8) — at 0.5 mA lower still ⇒ < 1.5 V OK. TPx open:
   leakage ≤ 1 µA x 10 kΩ = 10 mV drop ⇒ ≈ 5 V ≥ 3.5 V OK. 2N7002 on: RDS(on) ≤ 7 Ω at VGS = 5 V
   (p.2) ⇒ 0.5 mA x 7 Ω = 3.5 mV ≪ 1.5 V. 2N7002 off: IDSS ≤ 80 nA ⇒ ≈ 5 V. OK.
2. **2N7002 switching point on the SS/SD ramp**: Vth 1.0–2.5 V (p.2). With VGS at ~2.5–3 V the
   channel is far below 7 Ω but far above the 10 kΩ / 0.3 x VCC1 requirement: drain falls below 1.5 V
   once the FET sinks ≥ 0.35 mA — just above threshold. PD_PG_N therefore asserts somewhere in the
   1–3 V part of the ramp, i.e. inside UCC2897A's 2.5–4.5 V useful soft-start range or just before it.
   Glitch-free: the ramp is monotonic.
3. **Primary supply current and LDO dissipation** (worst case, all inputs low):
   ISO7740 ICC1 ≤ 7.8 mA (5 V table, ISO7740 "VI = 0 V", p.13) + 78L05 IQ ≤ 5.5 mA (p.3) + 4 pull-ups x
   0.5 mA = **15.3 mA** from VB_PRI (9.8 mA through the regulator, 5.5 mA quiescent).
   P_LDO = (VIN – VOUT)·IOUT + VIN·IQ: at VB_PRI = 13.5 V, 8.5 x 9.8 + 13.5 x 5.5 = **157 mW**.
   SOT-89 350 mW rating at 25 °C (p.3) ⇒ implied θ ≈ 357 °C/W (125 K / 350 mW); TJ = 55 + 0.157 x 357 =
   **111 °C** < 150 °C abs. Accepted with tab copper (pin 2 = GND = RTN); typical IQ is 2 mA, which gives
   TJ ≈ 90 °C.
   78L05 regulation needs VIN ≥ 7 V (p.3, 4.75–5.25 V for 7 V ≤ VIN ≤ 20 V); at the UCC2897A's 7.6 V
   minimum running bias it still regulates. Below that the converter is off anyway.
4. **Secondary supply**: ICC2 ≤ 3.2 mA (DC, 5 V table; less at 3.3 V) from `+3V3` — block C budget.
5. **Timing**: propagation ≈ 11 ns, default-output delay ≤ 0.3 µs on VCC1 loss (§7.x tDO). TPx are
   enabled 20–28 ms after PG releases, because VC_IN (VB_PRI) is already up (TPS2373 §7.3.6 p.19). The FPGA should read the code ≥ 30 ms after
   PD_PG_N asserts, and re-read on any change (TPS2373 p.30 "Applications must monitor the state of TPH,
   TPL and BT").

## Fine print / gotchas

- ISO7740 default **high** (no "F" suffix) — do not let a substitution swap in ISO7740F (default low
  would read "Class 8, power good" with the primary dead).
- EN2 low puts the outputs in high-Z; it is tied high, so no pull resistors are needed on the FPGA side
  for normal use. When `+3V3` is off the FPGA is off too.
- 78L05G-AB3-R pinout O-G-I (p.1); the -AB3-C-R variant is G-I-O. Order exactly AB3-R.
- 78L05 is characterised with C1 = 0.33 µF in, Co = 0.1 µF out (p.3); we use those values.
- ISO7740 recommends a 0.1 µF bypass per supply at the pins (layout section) — placed.

## Layout guidance

- The ISO7740 straddles the R-32 barrier: pins 1–8 on the primary (RTN) side, 9–16 on the secondary.
  No copper of either side under the package body between the rows; the barrier keepout is ≥ 8 mm
  (package CPG) and phase 4 sets the board value from R-32.
- 78L05, 2N7002 and pull-ups on the RTN plane next to the TPS2373; keep TPx traces short.
- VCC2 bypass at pin 16, VCC1 bypass at pin 1.

## Open questions

- None for this block. Block B must confirm the bias winding can source the extra 15 mA (`A-interfaces.md`).
