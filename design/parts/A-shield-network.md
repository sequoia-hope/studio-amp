# Block A — RJ45 shield network (R-10)

Serves: J1 shield tabs (`A-poe-magjack.md`).
Datasheets: `datasheets/A-fh-1206b102k202.pdf` (FH MLCC catalogue; "202" = 20 x 10² = 2000 V rating
code, X7R ±15 % –55…125 °C), `datasheets/A-uniroyal-1206w4.pdf` (Uni-Royal 1206: 1/4 W, 200 V
working, 400 V overload, 500 V dielectric withstand).

## Parts

| Ref (prov.) | Value | Package | MPN | Supplier line (checked 2026-11-07) |
|---|---|---|---|---|
| C_SH | 1 nF 2 kV X7R 10 % | 1206 | 1206B102K202NT | `C9196 1206B102K202NT (FH, 1206): basic, JLC stock 1573531, lifecycle normal` |
| R_SH1, R_SH2 (series) | 510 kΩ 1 % each (1.02 MΩ total) | 1206 | 1206W4F5103T5E | `C17990 1206W4F5103T5E (UNI-ROYAL, 1206): extended, JLC stock 137504, lifecycle normal` |

Topology (R-10 proposal, kept): `RJ45_SHIELD` → (C_SH ∥ R_SH1 + R_SH2) → secondary `GND`. No chassis
(wooden cabinet). Shield is user-touchable, so it must be on the secondary side, never the primary.

## Calculations

1. **ESD on the shield, ±8 kV contact (R-10, R-42)**: IEC 61000-4-2 source 150 pF. Charge sharing into
   C_SH: V = 8 kV x 150 pF / (150 pF + 1 nF) = **1.04 kV** peak across C_SH and the resistor string,
   decaying with τ = 1 nF x 1.02 MΩ ≈ 1 ms.
   - C_SH 2 kV rating: 1.04 kV ⇒ 52 %. OK.
   - Resistors: two in series share 520 V each, above the 400 V overload rating (a 5 s test) for a
     µs–ms pulse. Energy in the string ≈ ½ x 1 nF x 1.04² kV² = 0.54 mJ. Accepted for a ns-rise,
     ms-decay pulse; three in series (347 V each) would be inside the overload rating if a reviewer
     prefers.
2. **Static bleed**: 1.02 MΩ discharges the shield to GND with τ ≈ 1 ms; a cable dragged across carpet
   cannot hold the shell at kV.
3. **Normal operation**: no DC on the shield (the magjack's Bob Smith network is AC-coupled through
   22 nF + 1000 pF). Resistor dissipation ≈ 0.

## Fine print / gotchas — isolation (R-32)

The path cable → 22 nF / 75 Ω → **internal 1000 pF / 2 kV** → shield → C_SH ∥ 1 MΩ → GND makes the magjack's
internal Bob Smith capacitor part of the primary-to-secondary barrier. In a 1500 Vrms hipot between the
cable/primary and secondary GND, the 1 MΩ holds the shield at GND, so the internal cap sees the full
2121 Vpk. Its "2KV" marking (sheet 1) is most likely a DC rating. Options:

| Option | Hipot | ESD | Comment |
|---|---|---|---|
| A. as drawn (R-10) | internal cap stressed at 2.1 kVpk (≥ its 2 kV mark) | good | no formal certification on this spin (R-90), so a production hipot is not planned; risk is only if someone tests it |
| B. omit R_SH (C_SH only) | C_SH (2 kV) and internal cap share the AC voltage ~equally (≈ 1.06 kVpk each) | same peak; no static bleed except leakage | shield DC-floats |
| C. 2 x C_SH in series (2 kV each) + R_SH | AC still across the internal cap via R at DC; at 60 Hz Xc(1 nF) = 2.65 MΩ vs R 1 MΩ, little relief | — | not effective |
| D. fallback magnetics LP6090ANL + plain RJ45 + discrete Bob Smith with a 3 kV cap we choose | clean | good | more parts and area |

Recommendation: **A for this spin** (R-90: no formal certification) with the risk logged; revisit for a
product spin (D). Flagged for the user in `A-interfaces.md`.

Block B owns the Y-cap from `VPRI_RTN` to `GND` (architecture block list). That Y-cap and C_SH are
in parallel paths for common-mode currents; block B's value should be chosen knowing C_SH exists.

## Layout

- C_SH and R_SH within 5 mm of a shield tab, on the secondary side of the barrier, with a short wide
  path to the GND plane (via array).
- The other shield tab: same net, no second network needed.
- Keep shield copper ≥ the R-32 barrier distance from any primary copper (CT nets, VDD, VSS, RTN).

## Open questions

- Ask LINK-PP whether the internal 1000 pF is rated 2 kV DC or AC (decides option A's hipot risk).
