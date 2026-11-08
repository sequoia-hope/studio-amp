# D_TVS (×2, one at each channel's bridge) — VBUS clamp: Littelfuse SMBJ51A (600 W, 51 V stand-off)

> **Review m3, n6:** switching overshoot is ≈ 21 V at 16 A with a 1 nH loop (I·√(L/Coss)), not ≈ 10 V. At the TVS clamp the GaN therefore sees ≈ 103 V for nanoseconds, which rests on its 120 V pulsed rating. This is accepted because a 7.3 A TVS pulse and a hard edge at the trip current are independent rare events; the phase 6 loop target is ≤ 1 nH. Between the 52 V restart and the 55 V stop, VBUS sits between VWM (51 V) and VBR(min) (56.7 V), where leakage is unspecified but sub-mA and thermally harmless.

Datasheet: datasheets/smbj-littelfuse.pdf (Littelfuse SMBJ series, 600 W; read: the electrical table rows SMBJ45A–SMBJ60A, ratings, curves). The LCSC fetch was for SMBJ58A (C157526), and the series sheet covers 51A.
MPN: SMBJ51A (unidirectional). Supplier: `C1973217 SMBJ51A (Littelfuse, DO-214AA): extended, JLC stock 7604, lifecycle normal, checked 2026-11-07`. Footprint DO-214AA (SMB).
Superseded: SMBJ54A (C151266), proposed earlier and accepted in principle by the user. It clamps above the 63 V bulk-capacitor rating; see the VBUS overvoltage scheme below and in D-interfaces.md.

## VBUS overvoltage scheme (one scheme for every part on VBUS; **agreed with block B 2026-11-07**, recorded in D-interfaces.md and B-interfaces.md / B-output.md)
The weakest VBUS part is block B's bulk: 6 × 1000 µF / **63 V** Chemi-Con KZN (EKZN630ELL102ML25S). Neither the KZN sheet (datasheets/chemicon-kzn.pdf) nor Chemi-Con's technical note gives a surge rating. The note (§5-6-1, "Overvoltage") says only that voltage above rated causes leakage, heating and gas. **63 V is therefore treated as an absolute limit.**

| Layer | Mechanism | Level |
|---|---|---|
| 1. Energy budget | All returning energy goes into the 6 mF bulk | see below: ΔV ≈ 0.03 V |
| 2. Gateware stop (R-35) | FPGA stops switching (all gates off via AMP_EN) when the ADS7042 reads VBUS ≥ **55 V**; restart < **52 V** | < 5 µs reaction at 896 kS/s |
| 3. Converter output OVP (block B) | UCC2897A LINEOV from the averaged N5 forward voltage (≈ VBUS/2), independent of the opto; hiccup | trips ≈ 53.3 V (51.2–55.4 V) |
| 4. TVS (fast spikes only) | **SMBJ51A** at each bridge (block D) + **SMCJ51A** at the bulk (block B, replacing SMCJ58A) | VBR 56.7–62.7 V at 1 mA; VC 82.4 V at 7.3 A |

### Energy that can be returned to VBUS (block D's estimate)
- OCP or gateware stop with all 4 output inductors at the 16 A trip-plus-overshoot level: ½ × 10 µH × 16² × 4 = **5.1 mJ**.
- Regen during the stop latency: ≤ 15 A × 55 V × 5 µs = **4.1 mJ** (worst sign, both channels).
- Output-filter capacitor energy: 4 × ½ × 700 nF × 48² = 3.2 mJ (bounded by the same discharge path).
- After the stop, with gates off, the GaN bridge can only return speaker back-EMF energy if the back-EMF exceeds VBUS (> 48 V across the voice coil). That is not reachable from cone motion at these drive levels.
- Total ≤ 12.4 mJ into 6 mF at 55 V → ΔV = E/(C·V) = 12.4 mJ/(6 mF × 55 V) = **0.04 V**. VBUS stays ≤ 55.04 V, below 63 V and below the TVS's VBR(min) 56.7 V.
- Steady supply pumping in BTL is small and is caught by layer 2 long before 63 V. ACF load dump: block B confirms ≤ 24 mV overshoot (the converter is current-limited to 1.34 A; the bulk supplies the rest). Residual risk recorded by B: a feedback failure at Vin 38.4–41.9 V in DCM could pass 56.7 V (SMCJ51A could fail short).

### Why SMBJ51A
| Part | VWM | VBR (min–max) at 1 mA | VC at IPP | vs bulk 63 V | vs GaN 100 V (clamp + ≈ 10 V overshoot) |
|---|---|---|---|---|---|
| SMBJ48A | 48.0 | 53.3–58.9 | 77.4 V at 7.8 A | ✓ | 98 V |
| **SMBJ51A** | **51.0** | **56.7–62.7** | **82.4 V at 7.3 A** | ✓ VBR max 62.7 ≤ 63 | 82.4 + 21 V overshoot = **103 V**: on the GaN's 120 V pulsed rating (review m3; D-gan-fet.md) |
| SMBJ54A | 54.0 | 60.0–66.3 | 87.1 V at 6.9 A | ✗ VBR max 66.3 | ✓ 97 V |
| SMBJ58A / B's SMCJ58A | 58.0 | 64.4–71.2 | 93.6 V | ✗ | ✗ 104 V |
SMBJ48A would start conducting (53.3 V min) below the 55 V gateware stop, and dissipate continuously if VBUS rests at 54–55 V. SMBJ51A's VBR(min) 56.7 V is above the stop, and its VBR(max) 62.7 V is at or below the caps' 63 V at conduction onset. VWM 51 V > 48 V × 1.015 (B's static max 48.7 V) → IR ≤ 1 µA in normal running.
Limitation: at high pulse current the clamp rises to 82.4 V, above 63 V. That happens only for fast, low-energy spikes, which the bulk's ESL keeps from reaching the bulk in full. Layer 1 shows no amp-side energy source can drive such a current for longer than nanoseconds.

### Other VBUS parts at the 82.4 V clamp
LM5013/LM5017 bucks (block C, 100 V) ✓; GaN 100 V (92 V with overshoot) ✓; bridge ceramics 100 V ✓; ADS7042 divider → 82.4/25.8 = 3.19 V ≤ AVDD (3.25 V min) + 0.3 ✓; INA241 CM ≤ 110 V ✓; DC-detect dividers → LMV393 input 3.6 V for ≪ τ (RC-filtered) ✓; output filter C0G 100 V ✓.

## Ratings vs worst case (SMBJ51A)
| Parameter | Rating | Worst case | OK |
|---|---|---|---|
| PPPM | 600 W (10/1000 µs) | fast spikes only (layer 1) | ✓ |
| IR at VWM | 1 µA | ≤ 48.7 V static | ✓ |

## Layout guidance
Cathode on VBUS, anode on GND, directly beside each bridge's 2.2 µF ceramics, with a short wide return to the LS-source GND.

## Open questions
1. KZN surge rating: none published. If block B finds one (e.g. 79 V on another Chemi-Con sheet), the scheme gains margin; no change needed.
