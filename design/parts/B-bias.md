# Block B bias supplies — 2 × LM5019 100 V synchronous buck (primary `VB_PRI` 13.5 V, secondary `VSR` 12 V)

Datasheet: datasheets/lm5019.pdf (TI SNVS788G, Nov 2017). Read: all.
MPN: LM5019MRX/NOPB (SO-8 PowerPAD)
Supplier: `C471034 LM5019MRX/NOPB (TI, SO-8-EP): extended, JLC stock 4250, lifecycle normal, checked 2026-11-07`
Inductor: SXN SM5845-221MT, 220 µH (datasheets/sxn-sm5845-221.pdf: 220 µH ±10 %, DCR 1.57 Ω, Isat
0.36 A, Irms 0.35 A, −40…+125 °C)
`C10123 SM5845-221MT (Shun Xiang Nuo, SMD,5.8x5.2mm): extended, JLC stock 80148, lifecycle normal, checked 2026-11-07`
(Würth 74404054221, 220 µH, Isat 0.55 A, 1.4 Ω, rated 120 V, datasheets/we-74404054221.pdf, is the
alternate: LCSC C5521506, 411 stock, lifecycle not returned by the tool.)

## Why B has its own bias bucks

- **Primary:** with T1's primary at 4 turns, the only spare winding (N5, 4 T) carries ≈ Vin
  (42–57 V). A linear drop to 13.5 V at 32 mA wastes 0.9–1.4 W (1.5–2 % efficiency); the PMP20878
  linear scheme only works there because its aux sees Vin/2. TPS2373 VC_OUT cannot carry 32 mA
  continuously (20 mA recommended). A 100 V buck costs ≈ 0.08 W of its own loss.
- **Secondary:** the NCP4306 drivers, the two TL431s, the opto LED and the INA281 need ≈ 20 mA at
  ≈ 12 V. From VBUS by a linear regulator that is 0.7 W; by buck ≈ 0.28 W. Block C has no 12 V rail
  (`architecture.md` rails), and 5 V would need logic-level 200 V SRs.

## Absolute max vs worst case

| Parameter | Abs max | Primary (`VB_PRI`) | Secondary (`VSR`) |
|---|---|---|---|
| VIN, UVLO to RTN | 100 V | VPRI ≤ 57 V (62 V LINEOV surge) | VBUS ≤ 55 V firmware, 64–71 V TVS breakdown, 93.6 V clamp transient |
| BST to SW | 13 V | internal VCC (7.6 V) | same |
| VCC | 13 V | internal | internal |
| Output current | 100 mA rated, current limit 150–300 mA | 32 mA | 20 mA |

## Calculations (equations from datasheet §7.3, §8.2)

Constants: VFB = 1.225 V (±2 %); fsw = VOUT/(K·RON), K = 9e-11; TON = 1e-10 × RON/VIN;
minimum off-time 144 ns; UVLO 1.225 V with 20 µA hysteresis current.

| | Primary `VB_PRI` | Secondary `VSR` |
|---|---|---|
| VIN range | 30 V (start) … 57 V, running 33–57 V | 20 V (start) … 55 V |
| VOUT | 1.225 × (1 + 100 k/10.0 k) = **13.48 V** | 1.225 × (1 + 88.7 k/10.0 k) = **12.09 V** |
| RFB2 / RFB1 | 100 k / 10.0 k | 88.7 k / 10.0 k |
| RON for 400 kHz | 13.5/(9e-11 × 400 k) = 375 k → **374 k** | 12/(9e-11 × 400 k) = 333 k → **332 k** |
| TON at VIN min / max | 1.13 µs (33 V) / 0.66 µs (57 V) | 1.66 µs (20 V) / 0.60 µs (55 V) |
| Max duty check (1 − 144 ns/T) | 0.94 ≥ 13.5/33 = 0.41 ✓ | 0.94 ≥ 12/20 = 0.60 ✓ |
| L | 220 µH | 220 µH |
| ΔIL = (VIN − VOUT)·TON/L | 0.13 A p-p (57 V) | 0.13 A p-p (55 V) |
| Peak IL | 47 + 65 = 112 mA < 150 mA limit min, < 0.36 A Isat ✓ (≤ 100 mA rated ✓) | 20 + 65 = 85 mA ✓ |
| Load | UCC2897A 3 mA + gates 73 nC × 400 kHz = 32 mA, + block A's isolator primary (78L05 + ISO7740 + pull-ups) ≤ 15.3 mA = **47 mA** | 2 × NCP4306 (1.8 mA + 13 nC × 400 kHz) + 2 × TL431 (≈ 1.2 mA) + opto LED ≤ 1 mA + INA281 ≈ 1 mA ≈ 20 mA |
| Power out | 0.63 W (0.21 W of it is block A's isolator) | 0.24 W |
| UVLO divider (RUV2/RUV1) | 237 k / 10.0 k → start 30.3 V, hysteresis 20 µA × 237 k = 4.7 V | 154 k / 10.0 k → start 20.1 V, hysteresis 3.1 V |
| Type III ripple (eq. 26) | Cr 1 nF, Cac 100 nF; RrCr ≤ (33 − 13.5) × 1.13 µs / 50 mV → Rr ≤ 441 k → **Rr 300 k** | (20 − 12) × 1.66 µs / 50 mV → Rr ≤ 266 k → **Rr 200 k** |
| COUT | 10 µF 25 V X7R 1206 (+ UCC2897A's 1 µF VDD and 10 µF PVDD on the same rail) | 10 µF 25 V X7R 1206 |
| CIN | 1 µF 100 V X7R 0805 at VIN–RTN + 0.1 µF | same, from VBUS |
| CVCC / CBST | 1 µF 16 V / 10 nF 16 V | same |

COUT DC bias: 10 µF 25 V 1206 X7R at 13.5 V, **assumed** 50 % → 5 µF (confirm). Output ripple with
Type III injection: ΔIL/(8·f·C) = 0.13/(8 × 400 k × 5 µ) ≈ 8 mV p-p.

Ripple injection: Type III is used because the output caps are ceramic (no ESR ripple) and the
datasheet requires FB ripple to fall monotonically in phase with IL (§7.3.11).

Efficiency: LM5019 assumed ≈ 85 % at 20–32 mA (estimate; datasheet Fig. 14 is a curve for its own 10 V design, not read numerically) → losses 0.08 W
(primary) + 0.04 W (secondary), included in `B-converter-design.md`.

Idle draw during PD inrush (block A limit ≤ 30 mA from VPRI): UCC2897A held off by SS/SD ≈ 3 mA +
isolator primary ≤ 15.3 mA + LM5019 1.75 mA → ≈ 0.27 W → ≈ 10 mA at VPRI = 30 V (85 %) ✓. The
start-up charge of the 13.5 V rail's ≈ 22 µF is ≈ 0.3 mC, inside the buck's current limit.

## Fine print / gotchas

- No diode emulation (§7.3.1): runs forced-CCM at light load; fine at 20–32 mA.
- UVLO pin below 0.66 V = shutdown; leave the dividers as computed.
- EP must connect to RTN (pin table). RTN = `VPRI_RTN` (primary) or `GND` (secondary).
- Min on-time recommendation 100 ns at max VIN: 0.60 µs ✓.
- VSR start-up: until VBUS > 20 V the SRs run as body diodes (NCP4306 holds DRV low with no VCC).
  The TL431s and opto also need VSR: during the very first ms of VBUS rise the loop is open, but the
  UCC2897A soft-start and the CC limit bound the ramp; regulation starts when VSR > ≈ 6 V
  (TL431 + LED headroom). The CV target (48 V) is far above 20 V, so there is no overshoot path.

## Layout guidance

- Small SW loop: CIN at VIN/RTN pins, inductor next to SW. Rr/Cr across the inductor, Cac to FB.
- Primary buck sits on the primary side next to the UCC2897A; secondary buck on the secondary side
  next to the SR cell. Each referenced to its own side's return.

## Open questions

1. 10 µF 25 V 1206 X7R part number to be picked with the shared passive list (generic; many basic
   options).
