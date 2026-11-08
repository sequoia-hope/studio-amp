# U (2V5) — TPS7A9401 2.5 V LDO for ECP5 VCCAUX (block E)

Datasheet: datasheets/tps7a94.pdf (English, ti.com), already read in full for 3V3_Q
(C-3v3q-ldo.md). ECP5 requirements: datasheets/lattice-FPGA-DS-02012.pdf (§3.2 note 4, Table 3.3)
and block E's E-interfaces.md.
MPN: TPS7A9401DSCR (second instance; it replaces the withdrawn +1V8 TPS7A2018P, which block E no
longer needs after the ECP5 switch)
Supplier: `C5220127 TPS7A9401DSCR (TI, WSON-10(3x3)): extended, JLC stock 2441, lifecycle normal, checked 2026-11-07`
TI's fixed 2.5 V parts are out of stock (TPS7A2025PDBVR C2869949: 0; TLV75525PDBVR C2867155: 0),
so the adjustable TPS7A94 already on the BOM is used. Footprint WSON-10 3 × 3: 1–2 IN, 3 EN_UV, 4 PG,
5 FB_PG, 6 GND, 7 NR/SS, 8 SNS, 9–10 OUT, EP GND.

## Requirement

VCCAUX 2.375–2.625 V, 50 mA design. Ramp ≤ 30 mV/µs (DS §3.2 note 4: "VCCAUX ramp rate must not
exceed 30 mV/µs during power-up", over 0–3 V) and within 0.01–10 V/ms (Table 3.3). PLL noise target
< 0.25 % peak (≈ 6 mV). Block E fits a 120 Ω bead + 10 µF at the pins. It must be up on USB power
(all block E rails are).

## Absolute max vs our worst case

| Parameter | Abs max / ROC | Ours | Margin |
|---|---|---|---|
| IN, EN_UV, PG | 6.0 V; VIN 1.7–5.7 V | +3V3 3.42 V max | OK |
| IOUT | ICL 0.96–1.12 A, set to 60 % by FB_PG | 50 mA | OK |
| COUT | 4.7–1000 µF, ESR 1–20 mΩ | 10 µF X7R | OK |
| CNR/SS | 1–100 µF | 1.0 µF | OK |

## Calculations

- **Output** (VOUT = 150 µA × RNR/SS, ±1 %): RNR/SS = 16.7 kΩ 0.1 % → **2.505 V** (2.48–2.53 V),
  inside 2.375–2.625 V.
- **Headroom**: VIN 3.22–3.42 V less 2.5 V gives ≥ 0.72 V, above the 0.5 V at which TI quotes the
  high-PSRR figures. Dissipation 0.82 × 50 mA = 41 mW.
- **Noise**: 0.46 µVrms (10 Hz–100 kHz), far below the 6 mV peak target. NR filter fc =
  1/(2π × 16.7 k × 1 µF) = 9.5 Hz.
- **Ramp** (corrected after review, TPS7A94 p. 37): IFAST_SS = 2.1 mA charges CNR/SS only to ≈ 93 %
  of VOUT, then INR/SS = 150 µA finishes: 2.33 V × 1 µF / 2.1 mA = 1.1 ms + 0.18 V × 1 µF / 150 µA =
  1.2 ms → **≈ 2.3 ms**. The steepest part is ≈ 2 mV/µs, within ≤ 30 mV/µs and 0.01–10 V/ms. 2V5
  reaches regulation ≈ 1.3 ms after 1V1, still "together with or after 3V3".
- **Enable**: EN_UV = `PG_3V3` (open drain, 100 kΩ to +3V3; 3.3 V ≥ 1.25 V trip). 2V5 therefore
  starts together with 1V1, after 3V3, as block E's order requires.
- **FB_PG** (must not float, §8.1.5): RTOP 715 kΩ, RBOTTOM 68.1 kΩ → parallel 62 kΩ (60 % ICL
  ≈ 0.62 A); PG trip 0.2 × (1 + 715/68.1) = 2.30 V. PG open drain → `PG_2V5` (optional FPGA/RP2350
  input, 100 kΩ to +3V3), or leave it unconnected (permitted).
- CIN 10 µF, COUT 10 µF X7R ≤ 20 mΩ ESR. SNS to OUT at the bead input.
- Load on +3V3: 50 mA, included in the 0.79 A design.

## Phase 2 (parts cross-check C-m3, 2026-11-07)

CNR/SS raised from 1.0 µF (the 1 µF minimum) to **2.2 µF X7R 10 V 0603 (CC0603KRX7R6BB225, C513691)**;
at 2.5 V bias it still sits well above 1 µF. Ramp: 2.33 V × 2.2 µF / 2.1 mA = 2.4 ms fast charge +
0.18 V × 2.2 µF / 150 µA = 2.6 ms → **≈ 5 ms** to regulation, steepest ≈ 1 mV/µs (≤ 30 mV/µs,
0.01–10 V/ms OK). 2V5 now settles ≈ 4 ms after 1V1, still after 3V3 as block E requires (ECP5 sets
no VCCAUX-to-VCC order).
