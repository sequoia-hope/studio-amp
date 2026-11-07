# C_HPF1, C_HPF2 — tweeter protective high-pass: 2 × 22 µF polypropylene in parallel = 44 µF (TDK B32774D4226K) — **user decision 2026-11-07**

Datasheet: datasheets/b32774.pdf (TDK/EPCOS B32774…B32778 "MKP DC link – high density series"). Read: general data, climatic, construction, the 2-pin dimensional drawing for B32774D, the ordering table for 27.5 mm lead spacing, and the derating/ripple notes.
MPN: B32774D4226K (22 µF, K = ±10 %, 450 V DC; untaped "000" suffix on LCSC as B32774D4226K). Supplier: `C531089 B32774D4226K (TDK, Through Hole,P=27.5mm): extended, JLC stock 745, lifecycle normal, checked 2026-11-07`. Need 2 per board × 5 + 1 = 11 ≤ 745 ✓.
Footprint: 2-pin radial box, **lead spacing 27.5 ± 0.4 mm, lead Ø0.8 ± 0.05 mm** (hole 1.1–1.2 mm); body (w × h × l) **22.0 × 36.5 × 31.5 mm max**. Two of them occupy ≈ 2 × 22 × 31.5 mm = 14 cm² of board, 36.5 mm tall on the inward side (R-62 "don't care" there). Hand-soldered or JLC THT.
Rejected by the user: KYET MEB336K2A2701 (33 µF metallized polyester, 32 × 28 × 14 mm, 100 V), the earlier baseline; datasheets/meb336k2a.pdf. That analysis is summarised at the end.

## Function (R-54)
In series with the tweeter output, between the filter/Zobel node and the tweeter connector. It blocks DC, so **the tweeter is protected even if a bridge leg fails shorted**. It is a *protective* first-order high-pass well below a typical 2–3 kHz crossover. The real crossover is DSP, which also corrects this pole's in-band magnitude and phase for the known tweeter impedance.

## Value: 44 µF
fc = 1/(2π·R·C), C = 2 × 22 µF = 44 µF (±10 %):
| Tweeter nominal | fc | at 2 kHz | at 3 kHz |
|---|---|---|---|
| 4 Ω | 904 Hz | -0.81 dB, 24° | -0.38 dB, 17° |
| 6 Ω | 603 Hz | -0.38 dB, 17° | -0.17 dB, 11° |
| 8 Ω | 452 Hz | -0.22 dB, 13° | -0.10 dB, 9° |
(|H| = (f/fc)/√(1 + (f/fc)²); phase = atan(fc/f).) The corner is 1.1–2.7 octaves below a 2–3 kHz crossover for 4–8 Ω tweeters ✓. LF protection: at 200 Hz into 6 Ω, −10 dB; at 50 Hz, −21.6 dB; DC blocked.

## Ratings vs worst case
| Parameter | Rating (datasheet) | Worst case | OK |
|---|---|---|---|
| DC voltage | VR = 450 V DC at 70 °C; Vop = 450 V DC at 85 °C | bridge failed shorted: ≤ 55 V DC (gateware stop), ≤ 82 V at a TVS clamp; DC detector trips within 28–60 ms | ≫ |
| AC voltage across the cap | (DC-link series, no separate AC rating; ripple-limited) | ≤ 34 V rms below fc; in band ≪ | ✓ |
| Ripple current | IRMS,max 14.5 A at 70 °C, 10 kHz (per cap) | tweeter current ≤ 6 A rms at the 144 W limit (shared by 2 caps → ≤ 3 A each); realistic HF programme ≪ 1 A | ✓ (≥ 4.8×) |
| ESR | 5.4 mΩ typ (70 °C, 10 kHz); tanδ 1.3 × 10⁻³ at 1 kHz, 12.1 × 10⁻³ at 10 kHz | 2 in parallel: 2.7 mΩ → ≤ 6² × 2.7 mΩ = 0.1 W at the 144 W limit | ✓ |
| Temperature | max operating 105 °C (case); climatic 40/105/56 | 55 °C air + self-heating ≪ | ✓ |
| ESL | 30 nH typ | irrelevant at audio; with 44 µF, SRF ≈ 110 kHz (each part 30 nH; two in parallel 15 nH) | ✓ |
| Tolerance | ±10 % (K) | fc ±10 %, corrected in DSP | ✓ |

Dielectric: polypropylene (MKP): tanδ 1.3 × 10⁻³ at 1 kHz against ≤ 8 × 10⁻³ for the rejected PET part, with lower dielectric absorption. Construction: plastic case and epoxy seal, UL 94 V-0.

## Mechanical (R-41)
Two 22 × 36.5 × 31.5 mm boxes on 0.8 mm leads must be glued to the board (vibration on the speaker back panel). Place them standing side by side, both with leads in the tweeter output path. Wire them in parallel with short wide copper (≈ 6 A peak), and keep them away from the inductors' gap field and the switch nodes.

## Layout guidance
Tweeter channel only: filter caps → Zobel → **C_HPF1 ∥ C_HPF2** → J_TWT pin +. The DC-detect tap stays on the bridge side of these caps (D-dc-detect.md).

## Rejected alternative (summary): KYET MEB336K2A2701, 33 µF PET
`C49215601 … stock 204, lifecycle normal`. 100 V DC, tanδ ≤ 0.8 % at 1 kHz, 32 × 28 × 14 mm, 27.5 mm pitch; fc 1.21 kHz/804 Hz/603 Hz at 4/6/8 Ω. Smaller (one part, ≈ 9 cm²), but PET has the higher loss and absorption. The user chose PP.

## Open questions
None.
