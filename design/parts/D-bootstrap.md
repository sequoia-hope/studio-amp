# D/C (×4 each) — LMG1210 bootstrap: BAT46WJ Schottky + 220 nF bootstrap capacitor

> **UPDATE 2026-11-07 (supersedes the C_BST value below): GaN = IGC033S10S1, fsw 448 kHz.**
> Q per cycle = 0.5 nC + QgH 14 nC (max) + IHB 0.85 mA × 2.17 µs (1.84 nC) + 10 kΩ pull-down 0.5 mA × 2.17 µs (1.08 nC) = **17.4 nC** → CBST,min (ΔV 0.1 V) = **174 nF**.
> C_BST becomes **470 nF 25 V X7R 0603, Samsung CL10B474KA8NNNC** (`C1623`, basic, 1.53 M in stock, search 2026-11-07; same Samsung CL datasheet) → ≈ 375 nF effective at 5 V → droop **46 mV**.
> VDD cap ≥ 5 × 375 nF = 1.9 µF effective → **2 × 2.2 µF X5R 0603 + 100 nF** (≈ 2.9 µF effective; D-driver-passives.md).
> Refresh at the 67 ns minimum LS on-time: τ ≈ 0.9 Ω × 375 nF = 340 ns → 18 % of the deficit restored per cycle → worst equilibrium droop at sustained max duty 17.4 nC/(0.18 × 375 nF) = 0.26 V → HB−HS ≥ 4.6 − 0.26 = 4.34 V > 3.65 V UVLO-falling max ✓.
> VBST max = 5.25 − 0.21 + 16 A × 5.4 mΩ (IGC033 Rds at 100 °C) = **5.13 V** ≤ 5.25 V LMG1210 recommended, ≤ 5.5 V GaN recommended ✓. Min: 4.75 − 0.475 − 0.09 = 4.19 V (Diagram 10: Rds flat above 4 V at 25 °C) ✓.
> BAT46WJ: average current 17.4 nC × 448 kHz = 7.8 mA ≪ 250 mA ✓; unchanged.

> **fsw update 2026-11-07 (FPGA changed to ECP5, edge grid 1.453 ns = 688.128 Mb/s ODDRX2F, E-fpga-ecp5.md):** baseline fsw is now **448 kHz** (1536 grid steps; 448 kHz = 48 kHz × 28/3, audio-locked but not an integer multiple). 480 kHz is not on the grid. Option per build: 672 kHz (14 × 48 kHz, 1024 steps). ton(max) = 0.97/448 kHz = 2.17 µs → Q = 0.5 + 7.9 + 1.84 + 1.08 = 11.3 nC → CBST,min 113 nF; 220 nF (≈ 175 nF effective, 65 mV droop) unchanged.

## D_BST — Nexperia BAT46WJ (100 V Schottky)
Datasheet: datasheets/bat46wj.pdf (Nexperia BAT46WJ product data sheet). Read: all.
MPN: BAT46WJ,115. Supplier: `C114696 BAT46WJ,115 (Nexperia, SOD-323F): extended, JLC stock 57004, lifecycle normal, checked 2026-11-07`
Footprint: SOD-323F (flat leads). Use the SOD-323F land pattern, not SOD-323.

| Parameter | Rating | Our worst case | Margin |
|---|---|---|---|
| VR | 100 V | the switch node swings to VBUS: 48 V normal, 87 V TVS clamp + ringing ≈ 97 V; TI: "rated blocking voltage equal to the maximum Vds of the GaN FET" (§8.2.2.2) → 100 V | OK (matches the GaN rating, as TI asks) |
| IF continuous | 250 mA | average recharge current = Q_cycle × fsw = 11.1 nC × 480 kHz = 5.3 mA (10.6 mA at 1 MHz) | ≫ |
| IFSM | 2.5 A (tp < 10 ms) | start-up pre-charge goes through the internal 1 kΩ; the recharge pulse is limited by the 0.4 Ω internal switch + diode + loop: ΔV ≈ 0.1 V / 0.5 Ω ≈ 0.2 A | OK |
| VF | 315 mV typ / 350 max at 10 mA; 415/475 at 50 mA | used in the VBST calculation below | — |
| Cd | 39 pF max at VR = 0 V | much less at 48 V reverse; adds about ½·C·V²·f = ½ × ~10 pF × 48² × 480 k = 5.5 mW | negligible |
| IR | 4 µA at 75 V (25 °C); 44 µA at 50 V, 60 °C | discharges CBST by 44 µA × 2 µs = 0.09 nC per cycle | negligible |
| Tj | 150 °C | ≪ | OK |

Why a Schottky: TI recommends one "for high-frequency operation" (§8.2.2.2), and the internal bootstrap switch already blocks overcharge during dead time. A fast silicon diode (1N4148W) would add Qrr loss at 480 kHz.

## C_BST — Samsung CL10B224KA8NNNC (220 nF, 25 V, X7R, 0603)
Datasheet: datasheets/cl10b224ka8.pdf (Samsung CL series MLCC general specification). Read: ratings, X7R characteristics.
Supplier: `C21120 CL10B224KA8NNNC (Samsung Electro-Mechanics, 0603): basic, JLC stock 883157, lifecycle normal, checked 2026-11-07`

### Calculation (LMG1210 Eq. 7, p.17)
CBST,min = (0.5 nC + Qrr + QgH + IHB·ton + I_pulldown·ton)/ΔV
- 0.5 nC: per-cycle charge from the HS dynamic current (Eq. 7 note)
- Qrr = 0 (Schottky)
- QgH = 7.9 nC (IGB070S10S1 Qg max)
- ton(max) = 97 % duty clamp / 480 kHz = 2.02 µs. IHB = 0.85 mA max → 1.72 nC
- HS gate pull-down 10 kΩ at 5 V = 0.5 mA × 2.02 µs → 1.01 nC
- Total Q = 0.5 + 7.9 + 1.72 + 1.01 = **11.1 nC per cycle**
- ΔV allowed 0.1 V → CBST,min = **111 nF**

Chosen **220 nF nominal**. X7R 0603 at 5 V DC bias (20 % of its 25 V rating) keeps roughly ≥ 80 % → ≈ 175 nF effective → droop 11.1 nC / 175 nF = **63 mV**.
- Ratio rule: the VDD cap must be ≥ 5 × CBST, so ≥ 5 × 175 nF = 0.88 µF effective. VDD has 2.2 µF 16 V X5R 0603, ≈ 1.4 µF effective at 5 V, plus 100 nF → 1.5 µF ✓ (D-driver-passives.md).
- Voltage rating: 25 V ≥ 5× the 5.2 V across it ✓ (1.5–2× minimum rule).
- Recharge time: τ ≈ (0.4 Ω switch + ≈ 0.5 Ω diode/ESR/loop) × 175 nF ≈ 160 ns. Recovering a 63 mV droop to within 5 mV takes about 2.5τ = 0.4 µs. **Per-cycle refresh at the 3 % minimum LS on-time is only 62 ns ≈ 0.4τ**, which restores about a third of the droop per cycle. Duty near the clamp lasts only for the sine peaks (a few cycles at 20 Hz), so droop builds over consecutive cycles to roughly 3× steady droop ≈ 0.2 V; at max duty for 1 ms the HB−HS minimum is ≈ 4.6 − 0.2 = 4.4 V, above the 3.65 V UVLO-falling max (p.5). OK, but gateware should not hold max duty for long; at M = 0.94 the LS on-time averages far more.

### VBST worst case (LMG1210 Eq. 3, §7.3.1)
VBST = VDD − VF + IL × Rds(on), with IL positive when flowing out of the bridge, i.e. LS in reverse conduction while LO is on.
- Max: VDD 5.25 V − VF(min at ~5 mA ≈ 0.25 V, from the 0.1 mA / 10 mA points 175/315 mV) + 16 A × 10.5 mΩ (Rds at 100 °C) = 5.25 − 0.25 + 0.17 = **5.17 V** (the internal switch drop of ≈ 0.4 Ω × few mA is ignored, which is conservative). With VF at its lowest plausible 0.21 V: 5.21 V.
- Limits: LMG1210 VHB−VHS recommended max 5.25 V; IGB070S10S1 VGS recommended max 5.5 V ✓.
- Min: VDD 4.75 − VF 0.475 (50 mA, max) − 16 A × 10.5 mΩ (negative IL) = **4.11 V** → still on the IGB070 Rds(on) plateau (Diagram 10 is flat from ≈ 4 V at 25 °C; ≈ +10 % Rds at 4.1 V hot). That is acceptable briefly, only at full current.

## Fine print
- TI: for LS on-times < 20 ns use a synchronous GaN bootstrap instead (§8.2.2.2). Our clamp keeps the LS on-time ≥ 62 ns.
- Place D_BST and C_BST as close as possible: the BST→HB loop and the HB–HS cap at the pins (§10.1).

## Open questions
None.
