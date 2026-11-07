# Gate-driver passives (per LMG1210, ×4): supply bypass, dead-time resistors, gate resistors, gate pull-downs, input filters

> **UPDATE 2026-11-07: GaN = IGC033S10S1, fsw 448 kHz, td 16 ns.** Changes: DT resistors 31.6 kΩ; VDD bulk 2 × 2.2 µF (≥ 5 × C_BST 375 nF effective = 1.9 µF; 2 × 2.2 µF X5R ≈ 2.8 µF + 100 nF ≈ 2.9 µF ✓); C_BST 470 nF (D-bootstrap.md). Rg 2.2 Ω re-checked for IGC033: gate loop √(2 nH/1.4 nF) = 1.2 Ω → R_total on 5.9 / off 4.3 Ω over-damped ✓; plateau current (5 − 2.6)/5.9 = 0.41 A → 6.4 ns VDS edge, 7.5 V/ns ✓; Miller 8 pF × 7.5 V/ns × 4.3 Ω = 0.26 V < Vth(min) 1.2 V ✓; Rg power ≤ 2.2/4.3 × 14 nC × 5 V × 448 kHz = 16 mW ≪ 62.5 mW ✓. Gate pull-down 10 kΩ unchanged.

Reference datasheet: datasheets/lmg1210.pdf (§7.3.2, §7.3.3, §8.2.2.1, §8.2.2.3, §9, §10). Part datasheets as listed per row.

| Ref (per driver) | Function | Value / part | LCSC (`show`, checked 2026-11-07) | Datasheet |
|---|---|---|---|---|
| C_VDD1 | VDD–VSS HF bypass, at the pins | 100 nF 16 V X7R 0402, CC0402KRX7R7BB104 | `C60474 CC0402KRX7R7BB104 (YAGEO, 0402): extended, JLC stock 11227872, lifecycle normal` | yageo-cc0402-x7r-100v.pdf (Yageo CC series X7R general spec) |
| C_VDD2, C_VDD3 (2 parts, updated for IGC033) | VDD–VSS bulk / LDO stability | 2 × 2.2 µF 16 V X5R 0603, CL10A225KO8NNNC | `C23630 CL10A225KO8NNNC (Samsung Electro-Mechanics, 0603): basic, JLC stock 2325526, lifecycle normal` | cl10a225ko8.pdf |
| C_VIN | VIN–VSS bypass | 1 µF 25 V X5R 0603, CL10A105KA8NNNC | `C5673 CL10A105KA8NNNC (Samsung Electro-Mechanics, 0603): extended, JLC stock 3747093, lifecycle normal` | cl10a225ko8.pdf (same Samsung CL general spec) |
| R_DHL, R_DLH | dead time **15.9 ns** (updated for IGC033; 12 ns was 49.9 kΩ C137969) | 31.6 kΩ 1 % 0402, 0402WGF3162TCE | `C11463 0402WGF3162TCE (UNI-ROYAL, 0402): extended, JLC stock 131251, lifecycle normal` | uniroyal-0402wgf.pdf |
| R_GH, R_GL | gate series resistor | 2.2 Ω 1 % 0402, FRC0402F2R20TS | `C2909330 FRC0402F2R20TS (FOJAN, 0402): extended, JLC stock 2468908, lifecycle normal` | fojan-frc0402.pdf |
| R_GSH, R_GSL | gate–source pull-down | 10 kΩ 1 % 0402, 0402WGF1002TCE | `C25744 0402WGF1002TCE (UNI-ROYAL, 0402): basic, JLC stock 22766835, lifecycle normal` | uniroyal-0402wgf.pdf |
| R_PWM, R_EN | input series (ground-bounce filter) | 100 Ω 1 % 0402, RC0402FR-07100RL | `C106232 RC0402FR-07100RL (YAGEO, 0402): extended, JLC stock 18521669, lifecycle normal` | yageo-rc0402.pdf |
| R_PD_PWM | PWM-line pull-down at the LMG1210 input (FPGA unconfigured: Gowin weak pull-up ≤ 150 µA) | 4.7 kΩ 1 % 0402, 0402WGF4701TCE | `C25900 0402WGF4701TCE (UNI-ROYAL, 0402): basic, 15.8 M in stock (search 2026-11-07)` | uniroyal-0402wgf.pdf |
| C_PWM, C_EN | optional input filter cap, **DNP** | 10 pF C0G 50 V 0402, 0402N100J500CT | `C301961 0402N100J500CT (Walsin, 0402): extended, JLC stock 53393, lifecycle normal` | walsin-0402n102.pdf (Walsin 0402N C0G series) |
| D_off (optional, DNP) | split turn-off path in parallel with R_G | footprint only, SOD-323, plus a 0 Ω DNP | — | — |

Build quantities are all ≤ 8 per board × 5; every line has ≥ 50k in stock except C301961 (53k, DNP).

## Calculations

### VDD capacitance (§7.3.2, §8.2.2.1, §9)
- Required: ≥ 0.3 µF *effective at bias*, ESR < 0.5 Ω; ≥ 5 × CBST(eff 175 nF) = 0.88 µF; TI recommends 100 nF + 220 nF…10 µF.
- 2.2 µF 16 V X5R 0603 at 5 V: Samsung's X5R 0603 parts typically lose about 30–40 % at 5 V/16 V → **≈ 1.4 µF**. Plus 100 nF X7R (≈ 90 nF at 5 V/16 V) → **1.5 µF ≥ 0.88 µF ✓**. ESR ≪ 0.5 Ω (MLCC) ✓. Voltage rating 16 V ≥ 3× 5.25 V ✓.

### VIN capacitance (§9)
1 µF 25 V at 7.35 V (29 % of rating) → ≈ 0.7 µF effective. The block C rail has its own bulk. Rating 25 V ≥ 3.4× ✓.

### Dead-time resistors
See D-lmg1210.md: Rext = 900/12 − 25 = 50.0 kΩ → 49.9 kΩ 1 % → td = 12.02 ns. Resistor tolerance (1 %) is negligible against the chip's ±25–30 %. Power: 24 µA² × 50 kΩ = 29 nW.

### Gate resistor R_G = 2.2 Ω (each gate, on and off)
- Gate loop: Ciss 650 pF (740 max); loop inductance ≈ 2 nH (driver ≤ 5 mm from the gate, return on the next layer). Characteristic impedance √(L/C) = √(2 nH/0.74 nF) = 1.64 Ω. Critical damping needs R_total ≥ 2 × 1.64 = 3.3 Ω.
- R_total(on) = driver source ≈ VDD/IOH = 5/1.58 = 3.2 Ω typ + 2.2 Ω + Rg_int 0.5 Ω = 5.9 Ω (over-damped ✓). R_total(off) = sink ≈ 5/3.1 = 1.6 Ω + 2.2 + 0.5 = 4.3 Ω ✓ (over-damped, keeps VGS overshoot well below the 5.5 V recommended / 6.5 V pulsed limits).
- Switching speed: plateau gate current (5 − 2.8 V)/5.9 Ω = 0.37 A → Qgd 1.7 nC / 0.37 A = 4.6 ns VDS fall → dV/dt ≈ 10 V/ns ≪ LMG1210 CMTI 300 V/ns ✓. The loss model's t_sw = 4 ns is consistent (D-gan-fet.md).
- Miller margin at the off state: 4.7 pF × 13 V/ns × 4.3 Ω = 0.26 V ≪ Vth(min) 1.2 V ✓.
- Power: Qg·V·fsw = 7.9 nC × 5 V × 480 kHz = 19 mW per gate, shared between the driver and Rg. Rg takes ≤ 2.2/4.3 × 19 = 10 mW (≤ 20 mW at 1 MHz) ≪ 62.5 mW (0402) ✓. Pulse: 1.6 A peak × 2.2 Ω → 5.6 W for ≈ 2 ns. That is an energy of 11 nJ, far inside the thick-film pulse envelope.
- The D_off footprint (Schottky + 0 Ω, DNP) lets the bench split on/off resistance if ringing or dv/dt needs tuning; R_G can be changed independently.

### Gate pull-down 10 kΩ
Keeps the gate at 0 V while the driver is unpowered or in UVLO; the LMG1210's own unpowered clamp holds ≤ 0.8 V at 1 mA (p.6). Load: 0.5 mA at 5 V (counted in the VDRV and CBST budgets); 2.5 mW ✓.

### PWM pull-down 4.7 kΩ
LMG1210 internal RIPD is 100–300 kΩ (p.6), which a 150 µA FPGA weak pull-up would overcome (15–45 V open-circuit equivalent, so the pin floats high). 4.7 kΩ × 150 µA = 0.71 V ≤ VIF(min) 0.70 V, marginal, so the guarantee remains EN held low by the fault latch (D-ocp-logic.md: AMP_ARM pull-down). The pull-down keeps the PWM pins defined. Load on the FPGA when driving high: 3.3 V/4.7 k = 0.7 mA ✓.

### Input series 100 Ω (+ optional 10 pF)
- §8.2.2.3: "a simple resistor in series with the inputs … close to the inputs"; with a CMC, TI suggests 100 Ω. Input capacitance ≈ a few pF → τ < 1 ns, negligible delay. All PWM and EN lines are identical, so the delay matches across channels (R-53 edge timing is unaffected).
- 10 pF DNP: τ = 1 ns if ground bounce proves worse at bring-up.

## Fine print
- Never tie DLH to VDD, which would select IIM. Both resistors go to VSS. "Do not ground the VIN pin" (§7.3.2; this applies when the LDO is bypassed, and we use the LDO).
- MLCC DC bias is taken from Samsung CL generic X5R behaviour. Samsung's CL datasheet gives no DC-bias curve per part number; the margin (1.5 µF vs 0.88 µF needed) covers a 60 % loss as well.

## Layout guidance
- C_VDD1 100 nF directly at pins 4/3; C_VDD2 next; C_VIN at pin 2, lower priority than VDD (§10.1).
- R_G at the GaN gate pad; R_GS directly gate-to-source at the FET.
- R_PWM/R_EN at the LMG1210 input pins, not at the FPGA.
- R_DHL/R_DLH next to pins 5/6, with short returns to VSS (pin 7 / pad 20).
