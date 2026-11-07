# U (block A) — LT4321 dual PoE ideal-diode bridge controller (both pair sets)

Datasheet: `datasheets/A-lt4321.pdf` (Linear Technology LT4321 rev "4321f", 2013). Read: all 12 pages.
MPN: LT4321IUF#TRPBF (alternate LT4321IUF#PBF, same die, tray)
Supplier:
- `C580183 LT4321IUF#TRPBF (ADI, QFN-16-EP(4x4)): extended, JLC stock 52, lifecycle normal, checked 2026-11-07`
- `C580182 LT4321IUF#PBF (ADI, QFN-16-EP(4x4)): extended, JLC stock 46, lifecycle normal, checked 2026-11-07`

Enable-network zener: `C173421 BZT52C27 (MDD(Microdiode Semiconductor), SOD-123): extended, JLC stock 20714, lifecycle normal, checked 2026-11-07`
(datasheet `datasheets/A-bzt52c24-mdd.pdf`, the MDD BZT52C series sheet; C27 row: Vz 25.65–28.35 V at 5 mA,
IR ≤ 0.1 µA at 21 V, 500 mW). 100 kΩ: `C25803 0603WAF1003T5E (UNI-ROYAL, 0603): basic, JLC stock 16189427, lifecycle normal, checked 2026-11-07`.

Build need: 1 per board ⇒ 5 + 2 attrition = 7; 98 across the two listings. OK, but single maker.
Footprint: UF16, 4 x 4 mm QFN, 0.65 mm pitch, EP 2.15 x 2.15 mm = OUTN, must be soldered (p.2, p.11
recommended land: 4.35 mm pad-ring outer, 0.30 x 0.70 mm pads, EP 2.15 mm). KiCad
`QFN-16-1EP_4x4mm_P0.65mm_EP2.15x2.15mm` matches; check pad length against p.11 in phase 2.

## Choice: why a controller-driven FET bridge

R-31 asks for two ideal-diode bridges. Options checked on LCSC 2026-11-07:

| Option | Part(s) | Stock | Path R / drop | Loss, Class 8 (1.73 A, two pair sets) | Loss, Class 6 (1.2 A) |
|---|---|---|---|---|---|
| **LT4321 + 8 N-FETs** (chosen) | LT4321IUF + 8 x PSMN040-100MSE | 98 / 1051 | 2 x 36.6 mΩ max at 25 °C, 2 x 66 mΩ at 100 °C | **0.11 W (25 °C max R), 0.20 W hot** + 0.03 W Iq | 0.05–0.10 W |
| Integrated FET bridge | PD70224ILQ-TR (Microchip) | 28 | 2 x 0.16 Ω (datasheet p.1) | 2 x 2 x 0.865² x 0.16 = 0.48 W (25 °C) | 0.23 W |
| Schottky bridge | 8 x SS310 (MDD) | 337 k | VF ≈ 0.67 V at 0.87 A (`A-ss310-mdd.pdf` Fig. 3, typ 25 °C) | 2 x 2 x 0.67 x 0.865 = **2.32 W** | 1.49 W |
| Discrete self-driven FET bridge | — | — | — | — | rejected: LT4321 p.6 warns discrete ideal bridges latch up on PCB leakage and turn on unpowered pairs |

Saving over Schottky at Class 8: ≈ 2.1 W, which is the difference between meeting and missing R-33a's
1.5 W front-end budget. PD70224 is simpler but stock (28) is thin and its loss is 4x higher.
`datasheets/A-pd70224.pdf` was read for the comparison (pp.1–5).

## Absolute max vs our worst case (p.2, all to OUTN)

| Parameter | Abs max | Our worst case | Margin |
|---|---|---|---|
| OUTP–OUTN | –0.3…100 V | 57 V; 93.6 V TVS clamp (SMBJ58A at the LT4321, as p.8 requires) | OK |
| IN12/36/45/78 | –2 V…OUTP + 2 V | CT nets; a reverse-biased pair sits at ≤ OUTP | OK |
| TGx–INx | 12 V | TG drive 7.7–11 V (p.3) | internal |
| EN, EN̅ | 100 V | EN at ≤ 0.71 x (57 – 25.65) = 22 V; EN̅ tied to OUTP (57 V) | OK |
| Ambient | –40…85 °C (I grade) | 55 °C cabinet air | OK |
| TJ | 125 °C | 0.8 mA x 57 V = 46 mW ⇒ negligible rise | OK |

## Required external parts (from datasheet)

- 8 x N-FET, BVDSS ≥ 100 V, VGS(th) ≥ 2 V min, RDS(on) for 20–70 mV drop at IAVG (p.8) → `A-bridge-fets.md`.
- 0.1 µF ceramic across OUTP–OUTN at the pins (**must**, p.7) — shared with TPS2373's C_PD; total C_PD
  ≤ 0.12 µF, or split 2 x 47 nF (p.7) → `A-pd-passives.md`.
- ≥ 10 µF across OUTP–OUTN once enabled (**must**, p.7); satisfied by block B's CBULK switched in by the
  TPS2373 hot-swap (allowed explicitly, p.7).
- Unidirectional TVS "such as SMAJ60A" OUTP–OUTN "as close as possible to the LT4321" (**must**, p.8) →
  `A-tvs.md` (SMBJ58A).
- Enable network (below): BZT52C27 zener + 100 kΩ into EN; EN̅ tied to OUTP (pin description p.5:
  "Tie to OUTP if the application circuit uses the EN pin").

## Calculations

1. **FET RDS(on) target** (p.8 Eq.): RDS(on) = VF / IAVG with VF 20–70 mV. IAVG per pair set at Class 8 =
   1.731 A / 2 = 0.865 A (balanced) ⇒ 23–81 mΩ. PSMN040-100MSE: 29.4 typ / 36.6 max at 25 °C, 66 max at
   100 °C ⇒ VF = 25 / 32 / 57 mV. Inside the window across temperature. Under 2-pair power (one bridge
   carries everything, Type 1/2 PSE, ≤ 25.5 W ⇒ 0.60 A) VF = 18–40 mV: fine.

2. **Bridge loss** (two FETs conduct per active pair set): P = 2 · N_sets · I_set² · R.
   - Class 8: 2 x 2 x 0.865² x R = 0.088 W (29.4 mΩ), 0.110 W (36.6 mΩ), **0.198 W (66 mΩ, hot)**.
   - Class 6: 2 x 2 x 0.60² x R = 0.042 / 0.053 / 0.095 W.
   - Quiescent: IS(ON) 0.8 mA max x 57 V = 46 mW.
   Per FET at Class 8 hot: 0.865² x 0.066 = 49 mW — no thermal design needed (LFPAK33).

3. **Enable threshold — keep the LT4321 off through detection and classification** (Figs 3–4 p.9 show
   it enabled "after detection and classification are complete"; operating current 0.5–0.8 mA would
   otherwise add to the class signature). EN: VIH 2.6 V max, VIL 0.5 V min, internal pull-down
   Rpd = 160–310 kΩ to OUTN, pins high-Z below OUTP = 12 V (p.3, p.8). Network: OUTP → BZT52C27 (cathode
   at OUTP) → 100 kΩ → EN.
   - Turn-on (guaranteed): OUTP ≥ Vz,max + VIH·(1 + 100 k / Rpd,min) = 28.35 + 2.6 x 1.625 = **32.6 V**.
     (Vz at 5 mA, `A-bzt52c24-mdd.pdf` table; at the ~10 µA used here Vz is lower, so real turn-on is
     earlier.)
   - Turn-off (guaranteed): zener leakage IR ≤ 0.1 µA up to VR = 21 V ⇒ VEN ≤ 0.1 µA x 310 kΩ = 0.03 V
     < VIL ⇒ off for **OUTP ≤ 21 V**, above the 20.5 V PSE class-event maximum and 802.3 class range
     (TPS2373 Fig. 22 p.22).
   - Above 32.6 V and before the TPS2373 closes its hot-swap (UVLO rising 36.3 V min) the bridge is
     active, so inrush already flows through the FET channels. In brownout the bridge drops to body
     diodes below ~29–33 V, while the PD runs to 30.5 V: ≈ 1.2 W per conducting bridge in the body diodes during a
     brownout (`A-bridge-fets.md` calc 4), never in normal operation (Type 4 PI ≥ 41.2 V).
   - Stress at OUTP = 57 V, Vz ≈ 26 V: I = 31 V / (100 k + 250 k) = 89 µA; P_zener = 2.3 mW;
     P_100k = 0.8 mW; VEN ≈ 22 V (< 100 V abs).

4. **Detection leakage** (p.3): IS(DET) ≤ 5 µA below 10 V — 0.2 % of the ~400 µA detection current at
   10 V into 24.9 kΩ. Shutdown current ≤ 60 µA at > 12 V (class region): 0.2 % of a 26.5 mA class
   signature. OK.

## Fine print / gotchas

- p.6: inputs are grouped (IN12/IN36, IN45/IN78); a pair's FETs turn on only when one input is above OUTP
  and the other below OUTN. The CT-to-pin mapping must be right: IN12 = CT of RJ45 pins 1-2, IN36 = 3-6,
  IN45 = 4-5, IN78 = 7-8 (p.5). See `A-poe-magjack.md` for the magjack pin numbers.
- p.7: shutting the LT4321 down leaves the body diodes as two ordinary bridges — the load is never
  disconnected. Fail-safe.
- p.8: FET VGS(th) "must be a minimum of 2 V" — see the temperature caveat in `A-bridge-fets.md`.
- p.6: "Smooth crossover between channels is guaranteed by the enforced dropout ∆VSD" (2–18 mV).
  With a 4-pair PSE both bridges conduct; current sharing is set by cable/magnetics resistance.
- Exposed pad = OUTN; it is the bridge's negative output, i.e. the TPS2373 VSS net (`VPD_N`).

## Layout guidance from datasheet

- TVS and 0.1 µF "as close as possible" to the LT4321 OUTP/OUTN (p.7–8).
- Keep the TG/BG gate traces short to each FET; FETs of one pair set grouped as an H-bridge around the
  CT pins. Gate nets have no series resistors in any ADI example (pp.1, 10, 12).
- Treat OUTP/IN* copper as 57 V, 100 V transient: ≥ 0.64 mm to VSS-referenced low-voltage copper
  (matches the TPS2373 rule).

## Open questions

- Only 98 parts in stock from a single maker; if stock falls below 7 before ordering, fall back to
  PD70224ILQ-TR (28 in stock, 0.48 W) and re-run the budget.
