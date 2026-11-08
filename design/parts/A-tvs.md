# D (block A) — SMCJ58A input TVS (rectified PoE, VDD–VSS)

Datasheet: `datasheets/A-smcj58a-diodes.pdf` (Diodes Inc. SMCJ5.0(C)A–SMCJ200(C)A, DS19003 rev 20-2,
June 2023). Read: all 6 pages. Earlier choice SMBJ58A (`datasheets/A-smbj58a-littelfuse.pdf`) replaced
after review A-m3.
MPN: SMCJ58A-13-F (Diodes Inc.). Second source: SMCJ58A (DOWO).
Supplier:
- `C135180 SMCJ58A-13-F (DIODES, SMC(DO-214AB)): extended, JLC stock 2906, lifecycle normal, checked 2026-11-07`
- `C357975 SMCJ58A (DOWO, SMC(DO-214AB)): extended, JLC stock 5908, lifecycle normal, checked 2026-11-07`
Footprint: DO-214AB (SMC), unidirectional, cathode band to VDD/OUTP. KiCad `D_SMC`. Block B already uses
the SMC body.

## Why this part

TPS2373 §8.2.2.2 (p.33) **requires** a TVS across the rectified PoE voltage ("SMAJ58A, or equivalent");
LT4321 p.8 asks for a unidirectional TVS "such as SMAJ60A" at its OUTP–OUTN. One TVS between the two ICs
serves both. Review A-m3 showed the SMB part's clamp margin to the 100 V parts was 3–4 % hot; the SMC part
has the same breakdown but 2.5x the current capability, so at any given surge current it clamps lower.

## Ratings vs our worst case (p.3 table, SMCJ58(C)A row; curves p.4)

| Parameter | Value | Our need | Margin |
|---|---|---|---|
| VRWM | 58 V, IR ≤ 5 µA | 57 V max PoE | 1 V; ≤ 5 µA leakage = 0.02 % of a 26.5 mA class current |
| VBR | 64.4–71.2 V at 1 mA | no conduction in service | OK |
| VC at IPP | 93.6 V at 16.0 A (10/1000 µs) | < 100 V abs max: TPS2373 VDD/RTN, LT4321 OUTP, PSMN040 VDS | see calc |
| PPK | 1500 W (10/1000 µs), derated linearly to 0 at 150 °C ambient (Fig. 1) | at 55 °C ≈ 76 % ⇒ 1.14 kW | OK |
| CT | ≈ 200 pF at zero bias for VRWM 58 V (Fig. 2) | 802.3 C_PD ≤ 0.12 µF | < 0.3 % |

## Calculations

- **Clamp vs current**: dynamic resistance from the table, (VC – VBR,max) / IPP = (93.6 – 71.2) / 16.0 =
  1.4 Ω. At the 6.5 A where the SMBJ58A reached 93.6 V: 71.2 + 6.5 x 1.4 ≈ **80 V**. VBR temperature
  coefficient is not given in this sheet; using the Littelfuse figure for the same VBR class
  (0.103 %/°C, `A-smbj58a-littelfuse.pdf` p.2) at 55–60 °C: ≈ +3.5 % ⇒ 83 V at 6.5 A, ≈ 97 V at the full
  16 A. Margin to 100 V is **≈ 17 V at SMB-class currents** and ≈ 3 V only at the SMC's own 16 A rating.
- **At 0 °C** (R-40 minimum, review A-n3): clamp falls ≈ 2.6 % ⇒ 91.2 V at 16 A; PSMN040 BVDSS
  interpolated at 0 °C ≈ 96.9 V (`A-bridge-fets.md`) ⇒ ≈ 6 V margin at full TVS rating.
- **Surge**: R-10's 1 kV common-mode surge appears across the isolation barrier (magnetics 1500 Vrms,
  isolator 5 kVrms), not across this TVS. What reaches VDD–VSS is the differential residue between pair
  sets plus cable hot-plug ringing. TI calls SMAJ58A adequate "for general indoor applications" and says
  "outdoor transient levels … require additional protection" (TPS2373 p.33). Indoor only (R-40). A
  line-to-line surge test is not part of R-10 and is not claimed.

## Layout

- Directly across OUTP–OUTN at the LT4321, sharing the C_PD placement; TPS2373 VDD/VSS within ~5 mm.
- Short wide VSS return; vias into the VSS plane next to the anode pad.

## Open questions

- 802.3bt clause 145 surge requirements were not available; indoor-only use assumed (R-40).
