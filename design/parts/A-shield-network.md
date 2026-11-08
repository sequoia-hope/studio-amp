# Block A — RJ45 shield network (R-10, R-32)

Serves: J1 shield tabs (`A-poe-magjack.md`).
Datasheets: `datasheets/A-fh-1206b102k202.pdf` (FH MLCC catalogue; "202" = 20 x 10² = 2000 V rating
code, X7R ±15 % –55…125 °C), `datasheets/A-fojan-frc0805.pdf` (FOJAN FRC thick-film series rating table:
1206 = 1/4 W at 70 °C, 200 V max working, 400 V max overload, 500 V dielectric withstand).

## Parts (revised after review A-M3 / A-m4)

| Ref (prov.) | Value | Package | MPN | Supplier line (checked 2026-11-07) |
|---|---|---|---|---|
| C_SH | 1 nF 2 kV X7R 10 % | 1206 | 1206B102K202NT | `C9196 1206B102K202NT (FH, 1206): basic, JLC stock 1573531, lifecycle normal` |
| R_SH1…R_SH5 (series) | 2.0 MΩ 1 % each (10.0 MΩ total) | 1206 | FRC1206F2004TS | `C2907380 FRC1206F2004TS (FOJAN, 1206): extended, JLC stock 149219, lifecycle normal` |

Topology: `RJ45_SHIELD` → (C_SH ∥ 5 x 2.0 MΩ string) → secondary `GND`. No chassis (wooden cabinet). The
shell is user-touchable, so it stays on the secondary side.

**Change from the reviewer's option E**: E proposed 4 x 2.49 MΩ (≈ 10 MΩ). I used 5 x 2.0 MΩ (10.0 MΩ):
same impedance, but with C_SH derated by DC bias each resistor would see 218 Vrms in the 4-resistor
string (above the 200 V working rating); with five it is ≤ 174 Vrms.

## Why ~10 MΩ (review A-M3)

The magjack's internal Bob Smith node reaches SHIELD through an internal **1000 pF / 2 kV** capacitor
(`A-lpjk6078ahnl.pdf` sheet 1). With the old 1.02 MΩ bleed, |Xc(1 nF, 60 Hz)| = 2.65 MΩ ≫ 1 MΩ held the
shield near GND in a cable-to-secondary hipot, leaving ≈ 1.8 kVpk of the 2121 Vpk (1500 Vrms) test across
the internal cap. At ~10 MΩ the string no longer dominates: the internal cap and C_SH form a capacitive
divider and share the test voltage. This replaces the earlier "accept the risk" decision.

## Calculations

Test: R-32, 1500 Vrms (2121 Vpk) for 60 s, 50 or 60 Hz, cable (primary) to secondary GND. C_i = internal
1000 pF (in series with 4 x (22 nF + 75 Ω) in parallel ≈ 88 nF, negligible). Z_SH = 10 MΩ ∥ C_SH.
V_i = V·|Z_i / (Z_i + Z_SH)|, V_SH = V·|Z_SH / (Z_i + Z_SH)| (complex).

| Case | f | C_SH (effective) | |Z_SH| | V across internal 1 nF | V across C_SH / string | Per resistor (5) |
|---|---|---|---|---|---|---|
| nominal | 60 Hz | 1.0 nF | 2.56 MΩ | **1088 Vpk** | 1051 Vpk | 210 Vpk = 149 Vrms |
| nominal | 50 Hz | 1.0 nF | 3.03 MΩ | 1099 Vpk | 1047 Vpk | 148 Vrms |
| C_SH –30 % (X7R DC bias at ~1 kV) | 60 Hz | 0.7 nF | 3.54 MΩ | 923 Vpk | **1233 Vpk** | 247 Vpk = **174 Vrms** |
| C_SH –30 % | 50 Hz | 0.7 nF | 4.14 MΩ | 944 Vpk | 1226 Vpk | 173 Vrms |

(The tolerance case where the internal cap is low or C_SH high pushes more onto the internal cap; at
C_SH = 1.1 nF (+10 %) and C_i = 0.9 nF the internal cap sees ≈ 1.2 kVpk. Still ≤ 60 % of its 2 kV mark.)

- **Internal cap**: ≤ 1.2 kVpk against its 2 kV marking in every case (was ≈ 1.8 kVpk). Its AC rating is
  still unstated — ask LINK-PP.
- **C_SH**: ≤ 1.23 kVpk against 2 kV (62 %); X7R HV parts are DC-rated, so 62 % for 60 s is acceptable.
- **Resistors**: ≤ 174 Vrms each against 200 V working (87 %); 3.0 mW each at 174 Vrms.
- **AC hipot only.** A 2250 VDC hipot would put the full voltage across the internal cap at steady state
  (the 10 MΩ holds the shield at GND for DC). R-32 is specified as 1500 Vrms, so AC it is; record this in
  the bring-up/test notes.
- **ESD on the shell, ±8 kV contact** (R-10, R-42; IEC 61000-4-2, 150 pF source): charge sharing into
  C_SH gives V = 8 kV x 150 pF / (150 pF + C_SH): 1.04 kV at 1 nF, **1.33 kV** with C_SH derated to
  0.75 nF (review A-m4). C_SH: 67 % of 2 kV. Resistors: 1.33 kV / 5 = **267 V each**, under the 400 V
  overload rating (a 5 s test, so this ns–ms pulse is comfortably inside it). Energy ½·C·V² ≈ 0.66 mJ,
  ≈ 0.13 mJ per resistor. (The internal 1 nF to the cable side also takes some of the charge, which only
  lowers these numbers.)
- **Static bleed**: τ = 1 nF x 10 MΩ = **10 ms**. Fast enough for any static charge on the shell.
- **Normal operation**: no DC on the shield (the Bob Smith network is AC-coupled). Dissipation ≈ 0.
- Block B's Y-cap (VPRI_RTN ↔ GND) sits in parallel for common-mode currents; at 10 MΩ the shield
  network adds only 1 nF at HF, so B's sizing is unaffected.

## Layout

- C_SH and the 5-resistor string within 5 mm of a shield tab, on the secondary side of the barrier; GND
  end with a via array to the plane.
- String laid out in a straight line with ≥ 1 mm between adjacent resistor ends (each joint is at up to
  ~1.2 kVpk relative to GND during hipot at the shield end).
- Shield copper keeps the R-32 barrier distance from any primary copper (CT nets, VDD, VSS, RTN).

## Open questions

- Ask LINK-PP for the internal 1000 pF capacitor's AC rating and the jack's shield-to-line isolation
  (only PHY-to-line, 1500 Vrms, is stated).
