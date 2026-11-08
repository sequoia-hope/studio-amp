# U (3V3), U (1V1) — TPS62A02AP forced-PWM bucks from +5V, with inductors and capacitors

Datasheet: datasheets/tps62a02a.pdf (SLUSEG9E, Jun 2024, ti.com). Read: all sections.
MPN: TPS62A02APDDCR (2 A, **forced PWM**, power good, ×2)   Supplier: `C25687169 TPS62A02APDDCR (TI, TSOT-23-6): extended, JLC stock 2304, lifecycle normal, checked 2026-11-07`
Footprint: **TSOT-23-6 (thin) "DDC"**. Use a TSOT-23-6 footprint, not SOT-23-6 (review note). Pins (Table 5-1, SOT23-6 column): 1 EN, 2 GND, 3 SW, 4 VIN, 5 PG, 6 FB.

History:
- TLV62569 was replaced because it is PSM-only (its Fig. 15 shows ≈ 60 mV p-p at 0.1 A), and the
  FPGA PLL needs low core ripple.
- **2026-11-07: the user switched the FPGA to an ECP5 LFE5U-25F (block E), so +1V2 became +1V1 and
  the +1V8 rail was dropped.**

FPGA requirements: datasheets/lattice-FPGA-DS-02012.pdf (ECP5 family data sheet) §3.2/3.3 and
block E's E-interfaces.md:
- VCC 1.045–1.155 V including noise; regulator accuracy ≤ 3 %.
- VCCIO (all banks, on +3V3) ≤ 3.465 V (LVCMOS33 table); block E asks for 3V3 within ±3 % including
  ripple.
- All supplies ramp monotonically at 0.01–10 V/ms (Table 3.3).
- Order: +3V3 first, then 1V1 and 2V5 after or together, with a short gap (≈ 1 ms), because
  left/right bank pin pairs are low-impedance while VCCIO is up and VCC isn't.

## Loads

- +1V1: **400 mA design** (block E).
- +3V3: block E 350 mA (FPGA VCCIO, RP2350, PHY…) + Qwiic 100 mA (user cap; limit 155–207 mA) +
  display 40 mA + block D 85 mA + the +2V5 LDO 50 mA + ≈ 30 mA of small loads → **≈ 0.66 A design**, 1 A
  peak. IL,peak = 0.66 + 0.26 = 0.92 A, under the 2.7 A minimum limit.

## Absolute max vs our worst case

| Parameter | Abs max / ROC | Ours | Margin |
|---|---|---|---|
| VIN, EN, PG | 6.5 V abs; 2.5–5.5 V ROC | +5V ≤ 5.25 V | OK |
| FB | 3 V | 0.6 V | OK |
| IOUT | 2 A ROC | 0.79 A (3V3), 0.40 A (1V1) | OK |
| HS peak current limit | 2.7 A min | 1.05 A (3V3), 0.60 A (1V1) | OK |
| L effective | 1.0 µH (+20/−30 %) | 1.0 µH | OK |
| COUT range | 10–47 µF (§8.2.2.3); Table 8-3 by VOUT | see below | OK |

## Calculations

**+1V1 divider** (eq. 2, R2 ≤ 100 kΩ; VFB 0.594–0.606 V at 0–125 °C, 0.591–0.609 V over the full
range): R2 = 100 kΩ, R1 = **84.5 kΩ** (E96; 83.5 kΩ is E192 and not a JLC basic value, per the review) →
0.6 × 1.845 = **1.107 V** (block E asked for 1.10 V; +0.6 %). Tolerance stack (VFB full range, 1 %
resistors): 0.591 × (1 + 84.5·0.99/101) = 1.080 V to 0.609 × (1 + 84.5·1.01/99) = 1.134 V, inside
1.045–1.155 V with ≥ 21 mV margin each side for ripple (0.5 mV) and load steps.
**+3V3 divider**: R2 = 100 kΩ, R1 = 453 kΩ → **3.318 V**. Worst case:
0.609 × (1 + 453·1.01/(100·0.99)) = 3.42 V high and 0.591 × (1 + 453·0.99/(100·1.01)) = 3.22 V low,
i.e. −2.6 %/+3.7 % of 3.30 V. The high end sits under the ECP5 VCCIO max of 3.465 V with 45 mV
margin, and ripple is 2.4 mV. **Use 0.5 % resistors on the 3V3 divider** (the +3.7 % worst case
just exceeds block E's ±3 %): that gives 3.24–3.40 V, ±2.4 %.

**Inductor** (fSW 2.4 MHz, VIN 5.25 V max, L = 1.0 µH, Table 8-3 standard):
- 1V1: ΔIL = 1.1 × (1 − 1.1/5.25)/(1 µ × 2.4 M) = 0.36 A; IL,peak = 0.40 + 0.18 = 0.58 A.
- 3V3: ΔIL = 0.51 A; IL,peak = 0.79 + 0.26 = 1.05 A.
- **SRP4020TA-1R0M** (Bourns): 1.0 µH ±20 %, DCR ≤ 27 mΩ, Irms 5.0 A, Isat 8.5 A.
  `C913245 SRP4020TA-1R0M (BOURNS, SMD,4.5x4.1mm): extended, JLC stock 5040, lifecycle normal, checked 2026-11-07`
  Second source `C2847468 MDA4020-1R0M (KOHERelec, 4.5x4.1mm, 1077 stock)`; verify its Isat ≥ 3.5 A.

**Output capacitors** (Table 8-3; the effective value may be −50 %):
- 1V1 (0.6 ≤ VOUT < 1.2 V: "++" = 2 × 22 µF, the ROC's 44 µF nominal): 2 × 22 µF 10 V X5R 0805
  (CL21A226MPQNNNE, C29277). Ripple ΔIL/(8·f·C) with ≥ 35 µF effective = 0.36/(8 × 2.4 M × 35 µ) =
  **0.5 mV p-p**. Block E's local VCC decoupling sits beyond the board copper.
- 3V3 (≥ 1.8 V: "++" = 22 µF): 1 × 22 µF 10 V X5R 0805 (≥ 11 µF effective). Ripple 2.4 mV.
- C3 feed-forward: footprint, DNP (not needed in FPWM).
- CIN: 4.7 µF X5R ≥ 10 V each.

**Ramps and order**: internal soft start ≤ 1 ms (EN → VFB 0.56 V) gives 1V1 ≈ 1.1 V/ms and 3V3
≈ 3.3 V/ms, inside 0.01–10 V/ms, and monotonic (it starts into pre-bias). 3V3 EN = +5V. 3V3 PG →
`PG_3V3` (100 kΩ to +3V3) → EN of 1V1 and EN_UV of the 2V5 LDO (C-2v5-ldo.md). **`PG_3V3` does not
go to the FPGA** (review B1): the ECP5's unconfigured 30–150 µA pull-down would hold it below the 1.2 V
EN thresholds, so 1V1 would never start and the FPGA could never configure, a deadlock. The FPGA
reads a buffered, inverted copy: a 2N7002 with its gate on PG_3V3 drains a 4.7 kΩ pull-up to +3V3 →
`PG_3V3_N` → FPGA B4 (active low = good; 2.6 V worst case against 150 µA when not good). PG rises at 96 % of
3V3, so 1V1 begins ≈ 1 ms after 3V3 starts and is in regulation ≈ 1 ms later. That is the ≈ 1 ms gap
block E asked for. On the way down, 1V1 drops when PG_3V3 falls (93.5 %), so VCC follows VCCIO
within ≈ 1 ms.

**Efficiency**: 3V3 at 0.79 A ≈ 90 %; 1V1 at 0.4 A ≈ 82 % (FPWM, estimated from 1.8 V curves).

## Fine print

- R2 ≤ 100 kΩ. Do not leave EN floating. PG pull-up ≤ 5.5 V.
- HICCUP short-circuit protection: shorts don't latch.
- 2.4 MHz switching: block E accepts it for its clocks. **Layout: keep both SW nodes and inductors
  away from the VCXO tune RC and the oscillators' supply pins** (block E).

## Layout

- CIN across VIN–GND first; short SW to L; FB divider at FB. Place the 1V1 converter next to the
  ECP5's VCC balls.

## Phase 2 correction (schematic, 2026-11-07)

453 kΩ 0.5 % 0603 is not stocked at LCSC. The +3V3 divider is now **R1 = 100 kΩ 0.1 % (C122538)
over R2 = 22.0 kΩ 0.1 % (C469656)**: 0.6 V × (1 + 100/22.0) = **3.327 V** (±0.2 % from the
resistors, plus the VFB tolerance above). Schematic: rails sheet, U-buck "3V3".
