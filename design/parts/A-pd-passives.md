# Block A — TPS2373 programming and bypass passives

Serves: TPS2373-4 (`A-pd-tps2373.md`) and the LT4321 OUTP–OUTN bypass (`A-bridge-lt4321.md`).
Datasheets: `datasheets/tps2373.pdf` (values and windows), `datasheets/A-fojan-frc0805.pdf` (FRC 0805
power/voltage), `datasheets/A-uniroyal-1206w4.pdf` (Uni-Royal chip-resistor ratings, same family as
0603WAF), `datasheets/A-fh-1206b102k202.pdf` (FH MLCC catalogue: part-number coding, X7R class II).
Samsung CL21 caps: generic MLCC, ratings from the part number; no DC-bias curve in the LCSC sheet
(see open questions).

## Parts

| Ref (prov.) | Job | Value | Package | MPN | Supplier line (checked 2026-11-07) |
|---|---|---|---|---|---|
| R_DEN | detection signature | 24.9 kΩ 1 % | 0603 | 0603WAF2492T5E | `C25962 0603WAF2492T5E (UNI-ROYAL, 0603): extended, JLC stock 711866, lifecycle normal` |
| R_REF | REF bias | 49.9 kΩ 1 % | 0603 | 0603WAF4992T5E | `C23184 0603WAF4992T5E (UNI-ROYAL, 0603): basic, JLC stock 1426605, lifecycle normal` |
| R_CLSA | class sig. A (Class 4) | 63.4 Ω 1 % | 0805 | FRC0805F63R4TS | `C5159721 FRC0805F63R4TS (FOJAN, 0805): extended, JLC stock 33646, lifecycle normal` |
| R_CLSB | class sig. B (Class 3) | 90.9 Ω 1 % | 0805 | FRC0805F90R9TS | `C3000584 FRC0805F90R9TS (FOJAN, 0805): extended, JLC stock 8956, lifecycle normal` |
| C_PD | VDD–VSS bypass, 802.3 CPD; shared with LT4321 | 100 nF 100 V X7R 10 % | 0805 | CL21B104KCFNNNE | `C28233 CL21B104KCFNNNE (Samsung Electro-Mechanics, 0805): basic, JLC stock 3257627, lifecycle normal` |
| C_VCIN | VC_IN–RTN | 100 nF 50 V X7R | 0603 | CC0603KRX7R9BB104 | `C14663 CC0603KRX7R9BB104 (YAGEO, 0603): basic, JLC stock 34235460, lifecycle normal` |
| C_VCOUT | VC_OUT–RTN (VC_OUT unused) | 1 µF 50 V X7R | 0805 | CL21B105KBFNNNE | `C28323 CL21B105KBFNNNE (Samsung Electro-Mechanics, 0805): basic, JLC stock 4309664, lifecycle normal` |
| R_MPS | auto-MPS, **DNP** | 1.3 kΩ 1 % | 1206 | FRC1206F1301TS | `C2933592 FRC1206F1301TS` (search hit, extended, 76436 stock; DNP so not ordered) |

## Calculations

1. **R_DEN** — 802.3 detection signature 23.7–26.3 kΩ (TPS2373 §7.4.4 p.24, §8.2.2.4 p.34); TI
   recommends 24.9 kΩ ± 1 %. Stress: "about 5 mW" (p.24): (10.1 V)² / 24.9 kΩ = 4.1 mW. Outside the
   detection range DEN is open (p.18), so no operating dissipation. Voltage ≤ 10.1 V. 0603 (1/10 W, 75 V)
   is ample.
2. **R_REF** — 49.9 kΩ, recommended range 48.9–50.9 kΩ (p.6). 1 % worst case 49.4–50.4 kΩ: inside.
   1.5 V across ⇒ 45 µW.
3. **R_CLSA / R_CLSB** — values from Table 1 (p.18) for Class 8. ~2.5 V across during class events
   (§7.3.3 p.17): P_A = 2.5² / 63.4 = **98.6 mW**, P_B = 2.5² / 90.9 = **68.8 mW**. FRC 0805 rated
   1/8 W at 70 °C (`A-fojan-frc0805.pdf`, power-rating table: 0805 = 1/8 W at 70 °C, 150 V working) ⇒ 79 % / 55 % at ≤ 55 °C air, for class events only
   (≤ ~90 ms each, 5 events). Continuous worst case is still under rating; 0805 accepted. Tolerance:
   1 % on 63.4 Ω moves class A current by ±0.4 mA inside TI's 38–42 mA test band (Table 7 p.33).
4. **C_PD** — 802.3 window 0.05–0.12 µF (p.33; LT4321 p.7 "≤ 0.12 µF"). 100 nF ±10 % = 90–110 nF.
   DC bias at the detection/class voltages (≤ 23 V) on a 100 V-rated part is small; X7R tempco ±15 %
   over –55…125 °C (FH catalogue, X7R row) ⇒ worst ≈ 76–127 nF across temperature. The upper corner
   (cold + tolerance) touches 0.12 µF only in combination; at 0…55 °C the X7R shift is < 5 % ⇒
   86–116 nF. Accepted. Add the SMBJ58A junction capacitance (`A-smbj58a-littelfuse.pdf` Fig. 5 p.4: ≈ 550 pF at
   0 V, ≈ 100 pF at VRWM for VBR = 64 V) — ≤ 0.6 nF, under 1 % of C_PD. Voltage: 57 V steady, 93.6 V clamp on a 100 V cap. **Only one
   C_PD on the whole VDD–VSS node**; if the LT4321 and TPS2373 can't share it, use 2 x 47 nF
   (LT4321 p.7).
5. **C_VCIN / C_VCOUT** — VC_OUT is unused (block B powers the UCC2897A from its own VB_PRI buck,
   `A-pd-tps2373.md` calc 6), so the 10x ratio rule for the advanced-startup hold-up (§8.2.2.8 p.35) no
   longer carries the UCC2897A. VC_OUT keeps the 1 µF bypass to RTN the pin table asks for (p.4); VC_IN
   gets a local 100 nF, since VB_PRI is a stiff buck output with its own capacitance (block B). Both are
   50 V parts at 13.5 V (27 % of rating). Effective values after DC bias (class-typical, ≥ 0.6 µF and
   ≥ 80 nF) still give ratio ≈ 7.5; that is now harmless, because the startup source only charges
   C_VCOUT up to an already-present 13.5 V before the VC switch closes.
6. **R_MPS (DNP)** — 1.3 kΩ (§8.2.2.10 p.35); P = 24² / 1300 x 0.264 = 117 mW < 250 mW (1206).

## Fine print

- R_CLSA, R_CLSB, R_REF, R_DEN return to **VSS** (not RTN). C_VCIN and C_VCOUT return to **RTN**.
- CLSA/CLSB are current-limited but "should not be shorted to VSS for long periods" (p.25): keep
  their pads apart from VSS copper and test points off these nets.
- Detection resistance seen at the PI includes the bridge body-diode resistance (p.24); RDEN may need to
  rise one E96 step (25.5 kΩ) if the first board's signature reads low. Footprint stays.

## Layout

- R_CLSA/R_CLSB/R_REF/R_DEN within 3 mm of their pins, on the VSS plane side.
- C_PD between LT4321 OUTP/OUTN and TPS2373 VDD/VSS, both connections ≤ 5 mm; SMBJ58A beside it.
- C_VCOUT/C_VCIN at the TPS2373 pins, returned to the RTN plane.

## Open questions

- DC-bias curves for the FH/Samsung class-II MLCCs are not in the LCSC sheets; the effective-capacitance
  figures above are class-typical estimates. Confirm C_VCOUT with the maker's DC-bias tool in phase 2.
