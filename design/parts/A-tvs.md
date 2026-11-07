# D (block A) — SMBJ58A input TVS (rectified PoE, VDD–VSS)

Datasheet: `datasheets/A-smbj58a-littelfuse.pdf` (Littelfuse SMBJ series, rev JC.07/04/25 v4). Read: all 6 pages.
MPN: SMBJ58A (Littelfuse). Second source: SMBJ58A-13-F (Diodes Inc.).
Supplier:
- `C157526 SMBJ58A (Littelfuse, DO-214AA): extended, JLC stock 7844, lifecycle normal, checked 2026-11-07`
- `C135085 SMBJ58A-13-F (DIODES, SMB): extended, JLC stock 31848, lifecycle normal, checked 2026-11-07`
Footprint: DO-214AA (SMB), unidirectional, cathode band to VDD/OUTP. KiCad `D_SMB`.

## Why this part

TPS2373 §8.2.2.2 (p.33) **requires** a TVS across the rectified PoE voltage ("SMAJ58A, or equivalent");
LT4321 p.8 asks for a unidirectional TVS "such as SMAJ60A" at its OUTP–OUTN. One TVS between the two ICs
serves both. SMBJ (600 W 10/1000 µs) instead of SMAJ (400 W): same clamp, 1.5x the energy, for the
IEC 61000-4-5 differential residue (R-10), at negligible cost.

## Ratings vs our worst case (p.2 table, SMBJ58A row)

| Parameter | Value | Our need | Margin |
|---|---|---|---|
| VRWM | 58 V, IR ≤ 1 µA | 57 V max PoE (802.3bt) | 1 V; leakage at 57 V ≤ 1 µA |
| VBR | 64.4–71.2 V at 1 mA | must not conduct in normal operation | OK |
| VC at IPP | 93.6 V at 6.5 A (10/1000 µs) | < 100 V abs max of TPS2373 VDD/RTN, LT4321 OUTP, PSMN040 VDS | 6.4 V (6.4 %) |
| PPPM | 600 W (10/1000 µs), derated linearly to 60 % at 150 °C (Fig. 3) | 55 °C ⇒ ≈ 88 % ⇒ 530 W | OK |
| Temp coefficient of VBR | 0.103 %/°C | at 55 °C VBR rises ≈ 3 %, clamp ≈ +3 V | VC ≈ 96 V hot — still < 100 V, margin 4 % |
| Cj | ≈ 550 pF at 0 V, ≈ 100 pF at VRWM (Fig. 5, VBR = 64 V) | adds to 802.3 C_PD (≤ 0.12 µF) | < 1 % |

## Calculations

- **Surge**: R-10's 1 kV common-mode surge appears across the isolation barrier (magnetics 1500 Vrms,
  isolator 5 kVrms), not across this TVS. What reaches VDD–VSS is the differential residue between pair
  sets, plus cable hot-plug ringing. TI calls SMAJ58A adequate "for general indoor applications" and says
  "outdoor transient levels … require additional protection" (TPS2373 p.33). Indoor only (R-40); the SMB
  part doubles as margin. A line-to-line surge test is not part of R-10 and is not claimed.
- **Clamp margin**: 93.6 V at 6.5 A; the temperature coefficient raises this to ≈ 96 V at 55 °C. The
  margin to 100 V is the thinnest number in block A. The next lower part, SMBJ54A (VC 87.1 V), has
  VRWM 54 V, below the 57 V PSE maximum, so its leakage is not guaranteed in normal service. Keep
  SMBJ58A.

## Layout

- Directly across OUTP–OUTN at the LT4321, sharing the C_PD placement; the TPS2373 VDD/VSS within ~5 mm.
- Short wide VSS return; vias into the VSS plane next to the anode pad.

## Open questions

- 802.3bt clause 145 surge requirements were not available; indoor-only use assumed (R-40).
