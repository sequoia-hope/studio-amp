# Gate-driver passives (per LMG1210, ×4): supply bypass, dead-time resistors, gate resistors, gate pull-downs, input filters — IGC033S10S1

> **UPDATE 2026-11-08 — GaN back to IGB070S10S1 (user), fsw 576 kHz. This block supersedes the IGC033 figures below where they differ; part values are unchanged and remain valid for the IGC033 fallback.**
> - Rg 2.2 Ω for IGB070: gate loop √(2 nH/0.74 nF) = 1.64 Ω → ≥ 3.3 Ω needed; R_total on 5.9–8.6 Ω, off 4.3–5.2 Ω ✓; dV/dt 7–10 V/ns; Miller 4.7 pF × 10 V/ns × 4.3 Ω = 0.20 V ≪ Vth(min) 1.2 V ✓; Rg power ≤ 12 mW ✓.
> - All values in this file (20.0 kΩ DT, 2 × 2.2 µF + 100 nF VDD, 470 nF C_BST, 10 kΩ / 100 kΩ pull-downs) are kept: they suit both IGB070 and the IGC033 fallback.

Revision note: rewritten after the phase 1 review for IGC033S10S1 (dead-time setting 20 ns, 2 × 2.2 µF VDD, HS pull-down 100 kΩ, ECP5 pin defaults). Reference datasheet: datasheets/lmg1210.pdf (§7.3.2, §7.3.3, §8.2.2.1, §8.2.2.3, §9, §10). Part datasheets per row.

| Ref (per driver) | Function | Value / part | LCSC (`show`/search, 2026-11-07) | Datasheet |
|---|---|---|---|---|
| C_VDD1 | VDD–VSS HF bypass at the pins | 100 nF 16 V X7R 0402, CC0402KRX7R7BB104 | `C60474 CC0402KRX7R7BB104 (YAGEO, 0402): extended, JLC stock 11227872, lifecycle normal` | yageo-cc0402-x7r-100v.pdf (Yageo CC X7R general spec) |
| C_VDD2, C_VDD3 | VDD–VSS bulk / LDO stability | 2 × 2.2 µF 16 V X5R 0603, CL10A225KO8NNNC | `C23630 CL10A225KO8NNNC (Samsung Electro-Mechanics, 0603): basic, JLC stock 2325526, lifecycle normal` | cl10a225ko8.pdf |
| C_VIN | VIN–VSS bypass | 1 µF 25 V X5R 0603, CL10A105KA8NNNC | `C5673 CL10A105KA8NNNC (Samsung Electro-Mechanics, 0603): extended, JLC stock 3747093, lifecycle normal` | cl10a225ko8.pdf (Samsung CL general spec) |
| C_BST | bootstrap | 470 nF 25 V X7R 0603 | `C1623` (D-bootstrap.md) | cl10b224ka8.pdf |
| R_DHL, R_DLH | dead time 20 ns setting | **20.0 kΩ 1 % 0402, 0402WGF2002TCE** | `C25765 0402WGF2002TCE (UNI-ROYAL, 0402): basic, JLC stock 2395536, lifecycle normal` | uniroyal-0402wgf.pdf |
| R_GH, R_GL | gate series resistor | 2.2 Ω 1 % 0402, FRC0402F2R20TS | `C2909330 FRC0402F2R20TS (FOJAN, 0402): extended, JLC stock 2468908, lifecycle normal` | fojan-frc0402.pdf |
| R_GSL | LS gate–source pull-down | 10 kΩ 1 % 0402, 0402WGF1002TCE | `C25744 0402WGF1002TCE (UNI-ROYAL, 0402): basic, JLC stock 22766835, lifecycle normal` | uniroyal-0402wgf.pdf |
| R_GSH | HS gate–source pull-down (bootstrap-powered) | **100 kΩ 1 % 0402, 0402WGF1003TCE** | `C25741 0402WGF1003TCE (UNI-ROYAL, 0402): basic, JLC stock 8784280, lifecycle normal` | uniroyal-0402wgf.pdf |
| R_PWM, R_EN | input series (ground-bounce filter) | 100 Ω 1 % 0402, RC0402FR-07100RL | `C106232 RC0402FR-07100RL (YAGEO, 0402): extended, JLC stock 18521669, lifecycle normal` | yageo-rc0402.pdf |
| R_PD_PWM | PWM-line pull-down at the LMG1210 input (backstop) | 4.7 kΩ 1 % 0402, 0402WGF4701TCE | `C25900 0402WGF4701TCE (UNI-ROYAL, 0402): basic, 15.8 M in stock (search)` | uniroyal-0402wgf.pdf |
| C_PWM, C_EN | optional input filter cap, **DNP** | 10 pF C0G 50 V 0402, 0402N100J500CT | `C301961 0402N100J500CT (Walsin, 0402): extended, JLC stock 53393, lifecycle normal` | walsin-0402n102.pdf |
| D_off (DNP) | optional split turn-off path parallel to R_G | footprint only (SOD-323) + 0 Ω DNP | — | — |

## Calculations
### VDD capacitance (§7.3.2, §8.2.2.1, §9)
Required ≥ 0.3 µF effective (ESR < 0.5 Ω) and ≥ 5 × CBST,eff (375 nF) = 1.9 µF. 2 × 2.2 µF 16 V X5R 0603 at 5 V: taken as ≈ 35 % DC-bias loss (Samsung CL gives no per-part curve) → ≈ 2.8 µF, plus 100 nF X7R (≈ 90 nF) → **≈ 2.9 µF ≥ 1.9 µF ✓**. If the real loss were 50 %, 2.3 µF still passes. 16 V ≥ 3× 5.25 V ✓.

### VIN capacitance (§9)
1 µF 25 V at 7.35 V → ≈ 0.7 µF effective; block C's rail has its own bulk. 25 V ≥ 3.4× ✓.

### Dead-time resistors
Rext = 900/20 − 25 = 20.0 kΩ (the minimum allowed value and the characterised point: 16/20/26 ns, p.7). Resistor tolerance 1 % is negligible against the chip's spread. Power 40 µA² × 20 kΩ = 32 nW. Effective window at the FETs ≈ 15 ns (D-lmg1210.md).

### Gate resistor R_G = 2.2 Ω (IGC033S10S1)
- Gate loop: Ciss 1.4 nF max, ≈ 2 nH → √(L/C) = 1.2 Ω; critical damping needs ≥ 2.4 Ω. R_total on = driver source (VDD/IOH: 5/1.58 = 3.2 Ω typ; 5/0.85 = 5.9 Ω at IOH min) + 2.2 + 0.5 = 5.9–8.6 Ω; off = 5/3.1 = 1.6 Ω typ (2.5 Ω at IOL min 2.0 A) + 2.2 + 0.5 = 4.3–5.2 Ω → over-damped ✓.
- Edge: plateau current (5 − 2.6 V)/5.9 Ω = 0.41 A typ → Qgd 2.6 nC/0.41 A = 6.4 ns; at IOH min 0.28 A → 9.3 ns (+1.7 ns current rise → t_sw 8–11 ns; the loss model uses 11 ns, review m2). dV/dt 5–7.5 V/ns ≪ 300 V/ns CMTI ✓.
- Miller at the 0 V off state: Crss 8 pF × 7.5 V/ns × 4.3 Ω = 0.26 V ≪ Vth(min) 1.2 V ✓.
- Power: Qg·V·fsw = 14 nC × 5 V × 448 kHz = 31 mW per gate; R_G share ≤ 2.2/4.3 → 16 mW ≪ 62.5 mW (0402) ✓ (34 mW at 1 MHz ✓). Peak pulse 1.6 A × 2.2 Ω for ≈ 5 ns: energy ≈ 30 nJ, inside thick-film pulse capability.
- D_off (DNP) lets the bench split on/off resistance if ringing or dv/dt needs tuning.

### Gate pull-downs
- LS 10 kΩ: holds the gate at 0 V while the driver is unpowered or in UVLO (the LMG1210 also clamps unpowered outputs to ≤ 0.8 V at 1 mA, p.6). Load 0.5 mA at 5 V while LO is on, from VDD (counted in VDRV).
- HS 100 kΩ: the HS gate pull-down is fed from the bootstrap cap while HO is on, so 10 kΩ would cost 1.0 nC per cycle (review M1, fix 3). 100 kΩ costs 0.1 nC and still discharges Ciss (1.4 nF) in τ = 140 µs when the driver is unpowered. It serves as a static hold only; the LMG1210's clamp does the fast work.

### PWM pull-down 4.7 kΩ (review n1)
The FPGA is now an ECP5, whose unconfigured pins default to tri-state with a weak **pull-down** (E-interfaces.md item 7). The PWM lines are therefore low before configuration, and the 4.7 kΩ is a backstop only (e.g. a reworked or missing FPGA). The real guarantee is EN held low by the fault latch (AMP_ARM pull-down, D-ocp-logic.md). Load when the FPGA drives high: 3.3 V/4.7 kΩ = 0.7 mA ✓.

### Input series 100 Ω (+ optional 10 pF)
§8.2.2.3: series resistor close to the inputs; with a CMC TI suggests 100 Ω. Input C of a few pF → τ < 1 ns; identical on all PWM/EN lines, so the delay is matched. 10 pF DNP → τ = 1 ns if bring-up shows ground bounce.

## Fine print
- Never tie DLH to VDD (that selects IIM); both DT resistors go to VSS. Do not ground VIN (§7.3.2).
- 20 kΩ is the datasheet minimum for Rext (p.4 RDHL/RDLH 20–1800 kΩ): do not go lower to get more dead time.

## Layout guidance
C_VDD1 directly at pins 4/3, C_VDD2/3 next; C_VIN at pin 2 (lower priority than VDD, §10.1). R_G at the GaN gate pad; R_GS directly gate-to-source at the FET. R_PWM/R_EN/R_PD_PWM at the LMG1210 input pins. R_DHL/R_DLH next to pins 5/6 with short returns to VSS.
