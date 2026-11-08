# Block B bias supplies — 2 × LM5019 100 V synchronous buck (primary `VB_PRI` 14.3 V, secondary `VSR` 10 V)

Datasheet: datasheets/lm5019.pdf (TI SNVS788G, Nov 2017). Read: all.
MPN: LM5019MRX/NOPB (SO-8 PowerPAD)
Supplier: `C471034 LM5019MRX/NOPB (TI, SO-8-EP): extended, JLC stock 4250, lifecycle normal, checked 2026-11-07`
Inductor: SXN SM5845-221MT, 220 µH ±20 % (datasheets/sxn-sm5845-221.pdf p.14 lists SM5845-221K, ±10 %,
with the same ratings: DCR 1.57 Ω, Isat 0.36 A, Irms 0.35 A, −40…+125 °C; calculations use −20 %)
`C10123 SM5845-221MT (Shun Xiang Nuo, SMD,5.8x5.2mm): extended, JLC stock 80148, lifecycle normal, checked 2026-11-07` (secondary)
`C10124 SM5845-331MT (Shun Xiang Nuo, SMD,5.8x5.2mm): extended, JLC stock 3076, lifecycle normal, checked 2026-11-07` (primary)
(Würth 74404054221, 220 µH, Isat 0.55 A, 1.4 Ω, rated 120 V, datasheets/we-74404054221.pdf, is the
alternate: LCSC C5521506, 411 stock, lifecycle not returned by the tool.)

## Why B has its own bias bucks

- **Primary:** with T1's primary at 4 turns, the only spare winding (N5, 4 T) carries ≈ Vin
  (42–57 V). A linear drop to 14.3 V at 64 mA would waste 1.8–2.7 W; the PMP20878 linear scheme
  only works there because its aux sees Vin/2. TPS2373 VC_OUT cannot carry 48 mA continuously
  (20 mA recommended). A 100 V buck costs ≈ 0.16 W of its own loss.
- **Secondary:** the NCP4306 drivers, the two TL431s, the opto LED and the INA281 need ≈ 25 mA at
  10 V. From VBUS by a linear regulator that would be 1.2 W; by buck ≈ 0.3 W. Block C has no 12 V rail
  (`architecture.md` rails), and 5 V would need logic-level 200 V SRs.

## Absolute max vs worst case

| Parameter | Abs max | Primary (`VB_PRI`) | Secondary (`VSR`) |
|---|---|---|---|
| VIN, UVLO to RTN | 100 V | VPRI ≤ 57 V | VBUS ≤ 55 V (gateware stop); SMCJ51A VBR 56.7–62.7 V, clamp 82.4 V at 18.2 A (review m3; VBUS scheme in `B-output.md`) |
| BST to SW | 13 V | internal VCC (7.6 V) | same |
| VCC | 13 V | internal | internal |
| Output current | 100 mA rated, current limit 150–300 mA | 64 mA | 25 mA typ, 37 mA max |

## Calculations (equations from datasheet §7.3, §8.2), revised for review M1 and M5

Constants: VFB = 1.225 V (1.200–1.250 V); fsw = VOUT/(K·RON), K = 9e-11; TON = 1e-10 × RON/VIN;
minimum off-time 144 ns; UVLO 1.225 V with 20 µA hysteresis current.

| | Primary `VB_PRI` | Secondary `VSR` |
|---|---|---|
| VIN range | 30 V (start) … 57 V | **7.5 V (start)** … 55 V; in dropout VSR ≈ 0.9·VBUS below ≈ 11 V |
| VOUT | 1.225 × (1 + 107 k/10.0 k) = **14.33 V** | 1.225 × (1 + 71.5 k/10.0 k) = **9.98 V** |
| Worst case (VFB ±2 %, **0.5 %** resistors) | 1.200 × (1 + 107 × 0.995/10.05) = **13.91 V** … 1.250 × (1 + 107 × 1.005/9.95) = **14.76 V** | 9.7–10.3 V |
| Check | > UCC2897A UVLO-on max 13.2 V by 0.71 V; < TPS2373 VC_IN 15 V recommended; < UCC2897A VDD 16 V (review M1) | NCP4306 VCC ≥ 4.2 V UVLO; 10 V clamp driver; INA281 VS 2.7–20 V and swing to VS − 0.15 V = 9.55 V min ≥ 7.8 V (Class 8 CC point) ✓ |
| RFB2 / RFB1 | 107 k / 10.0 k, 0.5 % | 71.5 k / 10.0 k |
| RON | 14.3/(9e-11 × 600 kHz) = 265 k → **267 k** (600 kHz) | 10/(9e-11 × 400 kHz) = 278 k → **280 k** (400 kHz) |
| TON at VIN min / max | 0.81 µs (33 V) / 0.47 µs (57 V) | 1.87 µs (15 V) / 0.51 µs (55 V) |
| Max duty check (1 − 144 ns/T) | 0.91 ≥ 14.3/33 = 0.43 ✓ | 0.94; below VBUS ≈ 10.6 V the buck is in dropout, intended |
| L | **330 µH** ± 20 % (SM5845-331MT: 330 µH, DCR 1.76 Ω, Isat 0.34 A, Irms 0.28 A per the K-version row, p.14), raised from 220 µH for the higher load | 220 µH ± 20 % (SM5845-221**M**T; datasheet lists the K version, same ratings, review m7) |
| ΔIL = (VIN − VOUT)·TON/L(min) | (57 − 14.3) × 0.47 µs/264 µH = 0.076 A p-p | (55 − 10) × 0.51 µs/176 µH = 0.13 A p-p |
| Peak IL | 76 + 38 = **114 mA** < 150 mA limit min (76 %), < 0.34 A Isat ✓; Irms 76 mA < 0.28 A ✓ | 37 + 65 = 102 mA ✓ |
| Load | UCC2897A 3 mA + gates 73 nC × 737 kHz = 56.8 mA, + block A's isolator primary (78L05 + ISO7740 + pull-ups) ≤ 15.3 mA + sync clock 4 mA (`B-sync-clock.md`) = **76 mA** (≤ 100 mA rated) | 2 × NCP4306 (1.8 mA + 13 nC × 623 kHz) = 20 mA + 2 × TL431 2.4 mA + opto LED 1–2 mA (12.8 mA max at loop saturation) + INA281 1 mA ≈ **25 mA typ, 37 mA max** |
| Power out | 1.09 W (0.22 W of it block A's isolator, 0.06 W the sync clock) | 0.25 W |
| UVLO divider (RUV2/RUV1) | 237 k / 10.0 k → start 30.3 V, hysteresis 4.7 V | **51.1 k / 10.0 k → start 7.48 V**, hysteresis 20 µA × 51.1 k = 1.0 V (review M5) |
| Type III ripple (eq. 26) | Cr 1 nF, Cac 100 nF; Rr ≤ (33 − 14.3) × 0.81 µs/(1 nF × 50 mV) = 303 k → **Rr 200 k** | Rr ≤ (15 − 10) × 1.87 µs/(1 nF × 50 mV) = 187 k → **Rr 82 k** |
| COUT | 10 µF 25 V X7R 1206 (+ UCC2897A's 1 µF VDD and 10 µF PVDD on the same rail) | 10 µF 25 V X7R 1206 |
| CIN | 1 µF 100 V X7R 0805 at VIN–RTN + 0.1 µF | same, from VBUS |
| CVCC / CBST | 1 µF 16 V / 10 nF 16 V | same |

COUT DC bias: 10 µF 25 V 1206 X7R at 14.3 V, **assumed** 50 % → 5 µF (confirm). Output ripple with
Type III injection: ΔIL/(8·f·C) = 0.076/(8 × 600 k × 5 µ) ≈ 3 mV p-p.

Ripple injection: Type III is used because the output caps are ceramic (no ESR ripple) and the
datasheet requires FB ripple to fall monotonically in phase with IL (§7.3.11).

Efficiency: LM5019 assumed ≈ 85 % (estimate; datasheet Fig. 14 is a curve for its own 10 V design, not
read numerically) → losses 0.19 W (primary) + 0.04 W (secondary), included in
`B-converter-design.md`. LM5019 die dissipation ≈ 0.16 W on the SO-8 PowerPAD: negligible rise.

Idle draw during PD inrush (datasheet bound: DC load < 0.65 × 275 mA ≈ 179 mA at the end of inrush, TPS2373 p.7; block A's own margin is 30 mA): UCC2897A held off by SS/SD ≈ 3 mA +
isolator primary ≤ 15.3 mA + LM5019 1.75 mA → ≈ 0.29 W → ≈ 11 mA at VPRI = 30 V (85 %) ✓. Charging
the rail's ≈ 22 µF to 14.3 V takes ≈ 0.3 mC, inside the buck's current limit.

**Why VSR = 10 V and starts at 7.5 V (review M5):** the secondary control (CV and CC TL431s, opto,
INA281) runs from VSR. With VSR starting at 20 V, nothing limited the output current while VBUS rose
from 0 to 20 V. Now the CC loop works from VBUS ≈ 7.5 V (in dropout VSR ≈ 7 V: TL431 2.5 V + LED
1.1 V + RLED drop fits; INA281 swing ≥ 6.8 V covers the 2.64 V Type 2 set-point). Below 7.5 V the
UCC2897A's 60 ms soft-start bounds the current (`B-converter-design.md`). The NCP4306 needs ≈ 10.5 V
for its full 10 V clamp; at VSR 9.7–10 V the SR gates get ≈ 9.5 V, which is above the BSC500N20NS3
Rds(on) test condition region (VGS(th) ≤ 4 V). Rds rises a few %, which is accepted.

## Fine print / gotchas

- No diode emulation (§7.3.1): runs forced-CCM at light load; fine at 25–64 mA.
- UVLO pin below 0.66 V = shutdown; leave the dividers as computed.
- EP must connect to RTN (pin table). RTN = `VPRI_RTN` (primary) or `GND` (secondary).
- Min on-time recommendation 100 ns at max VIN: 0.47 µs ✓.
- VSR start-up: until VBUS ≈ 7.5 V the SRs run as body diodes (NCP4306 holds DRV low with no VCC)
  and the loop is open; the UCC2897A's 60 ms soft-start bounds the current (review M5).

## Layout guidance

- Small SW loop: CIN at VIN/RTN pins, inductor next to SW. Rr/Cr across the inductor, Cac to FB.
- Primary buck sits on the primary side next to the UCC2897A; secondary buck on the secondary side
  next to the SR cell. Each referenced to its own side's return.

## Open questions

1. 10 µF 25 V 1206 X7R part number to be picked with the shared passive list (generic; many basic
   options).
