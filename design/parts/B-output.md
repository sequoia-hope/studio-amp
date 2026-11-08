# Block B output — output inductor, output ceramics, VBUS bulk electrolytics, VBUS overvoltage scheme and TVS

Converter numbers from `B-converter-design.md` (737 kHz crystal-synced, n = 2, D 0.424–0.655).
Order on the secondary: T1 → SRs → `SW_SEC` → L_out → output ceramics → IBUS shunt (30 mΩ,
`B-feedback.md`) → `VBUS` node: bulk electrolytics, TVS, loads (blocks C, D).

---

## L (out) — 68 µH, Sumida CDRH127/LDNP-680MC

Datasheet: datasheets/sumida-cdrh127ldnp.pdf (CDRH127/LDNP series). Read: all.
Supplier: `C2452974 CDRH127/LDNP-680MC (Sumida, SMD-4P,12x12mm): extended, JLC stock 5871, lifecycle normal, checked 2026-11-07`
Footprint: 12 × 12 mm, 4-pad SMD per datasheet land pattern.

| Parameter | Datasheet | Our case | Margin |
|---|---|---|---|
| L | 68 µH ± 20 % (100 kHz) | 68 µH | |
| DCR | 120 mΩ max (92 typ) | 156 mΩ hot (×1.3) | |
| Rated current | 2.60 A (L −25 % or ΔT, whichever first; note 2) | peak 1.65 A at the 1.30 A CC limit and 57 V, L −20 %; rms 1.32 A | 1.58× on peak |
| Operating temperature | −40…+100 °C incl. self-heating | 55 °C air + ≈ 11 °C (1.37/2.6)² × 40 °C | OK; R-40 85 °C ambient case → 96 °C, marginal |

Calculation (737 kHz): ΔIL = Vo(1−D)/(L·fsw): 0.35 A p-p (38.4 V), 0.50 A (50 V), 0.55 A (57 V);
with L at −20 %: 0.69 A p-p at 57 V, peak 1.65 A at the 1.30 A CC limit. CCM boundary at
Io = ΔIL/2 ≈ 0.17–0.28 A; below it the NCP4306s give DCM.
Loss: 1.32² × 0.156 = 0.27 W + core (ferrite drum, 0.55 A p-p at 737 kHz, est. ≤ 0.07 W).
Choice of L: 100 µH halves ripple but available 100 µH parts are 2.0–2.1 A rated (Bourns SRR1280-101M
Isat 2.0 A; Sumida -101MC 2.10 A, 151 mΩ), too close to the 2.0 A worst-case peak.
Alternate (better part, weaker sourcing): Würth 7447709680 WE-PD 68 µH, Isat(10 %) 3.6 A, 89 mΩ
max, −40…+125 °C (datasheets/we-7447709680.pdf) — `C5155055: JLC stock 68, lifecycle unknown
(tool returned no detail)`; check by hand before using.
R-41: 12 × 12 × 7 mm drum, SMD; glue dot for vibration.

---

## C (out, HF) — 6 × 4.7 µF 100 V X7S 1210, Murata GCM32DC72A475KE02L

Changed from 3 × Taiyo Yuden HMK325C7475KMHPE (review m7: the fetched sheet was the HMJ catalog,
not the HMK part) and doubled for the shunt-ripple fix (review m2, `B-feedback.md`).
Datasheet: datasheets/murata-gcm32dc72a475.pdf (Murata GCM series catalog; 100 Vdc, X7S, 1210).
Supplier: `C913445 GCM32DC72A475KE02L (muRata, 1210): extended, JLC stock 9059, lifecycle normal, checked 2026-11-07`
- 48 V on 100 V (2.1×) ✓; at the SMCJ51A clamp (82.4 V) still < 100 V.
- DC bias **assumed** 50 % at 48 V → 6 × 2.35 µF ≈ 14 µF. Confirm with Murata SimSurfing (n14).
- Inductor ripple rms ΔIL/√12 = 0.16 A (57 V), about 70 % of it in these caps ✓.
- Ripple voltage (ceramics alone) ΔIL/(8·f·C) = 0.55/(8 × 737 k × 14 µ) = 7 mV p-p. These caps sit
  before the IBUS shunt, at the SR/inductor cell.

---

## C (bulk) — 6 × 1000 µF 63 V, Nippon Chemi-Con KZN, EKZN630ELL102ML25S (16 × 25 mm), + 1 DNP footprint

Datasheet: datasheets/chemicon-kzn.pdf (KZN series). Read: all.
Supplier: `C337254 EKZN630ELL102ML25S (NCC, Through Hole,D16xL25mm): extended, JLC stock 3169, lifecycle normal, checked 2026-11-07`
Footprint: radial 16 mm, 7.5 mm lead pitch (check the "ML25S" lead option in the datasheet
dimension table in phase 2). Through-hole, hand-soldered (R-70), mechanically secured (R-41).

| Parameter | Datasheet (63 V, 1000 µF, 16 × 25) | Need | Margin |
|---|---|---|---|
| Voltage | 63 V | VBUS 48 V; firmware stop 55 V (R-35) | 1.31× at 48 V; 1.15× at 55 V |
| Capacitance | 1000 µF ± 20 % | 6 mF nominal, 4.8 mF at −20 % | see bulk sizing |
| Impedance | 0.024 Ω (20 °C, 100 kHz), 0.072 Ω (−10 °C) | ESR zero ≈ 6.6 kHz (6 in parallel) | loop note |
| Ripple current | 2,890 mA rms (105 °C, 100 kHz); multiplier 0.60 at 120 Hz, 0.87 at 1 kHz | see below | |
| Endurance | 105 °C, rated ripple; 63–100 V, φ12.5 and larger: 10,000 h | 55 °C air | ≫ 100,000 h by the 10 °C rule |

**Bulk sizing (R-33a).** Usable energy at 10 % sag: ½C(48² − 43.2²) = 219 J/F.
- Class 8, CC at 1.36 A (65 W): 144 W × 10 ms burst → deficit 0.79 J → C ≥ 3.6 mF.
- Class 6, CC at 0.95 A (46 W): deficit 0.98 J → C ≥ 4.5 mF.
- R-33a's own figure (1.1 J with ≈ 50 W supplied) → 5.0 mF.
6 × 1000 µF = 6.0 mF (4.8 mF at −20 %) covers Class 8 and Class 6 at −20 %, and R-33a's 1.1 J at
nominal. The 7th footprint (DNP) gives 7 mF if bench tests want it (R-33a's "≈ 7 mF if the
converter current-limits").

**Ripple current.** The class-D bridges draw P_inst/VBUS; for a sine of average power P, the 2f
component is P/(VBUS·η·√2) rms, which the bulk carries (the converter loop is too slow).
- B's own estimate: sustained (≈ 46 W at Class 8, R-33a) 46/(48 × 0.9 × 1.414) = 0.75 A rms; 10 ms
  bursts at 2 × 100 W ≈ 2.3 A rms.
- **Design case (aligned with block D, review n9): block D's figures, 2.2 A rms continuous and
  4.2 A rms in bursts** (they include the bridges' PWM-envelope components B's sine estimate leaves
  out). Both blocks quote these numbers.
- Rating at 120 Hz, 105 °C: 6 × 2.89 × 0.60 = 10.4 A rms; at 1 kHz 15 A. Margin 4.7× continuous,
  2.5× in bursts, so self-heating is small (ΔT ∝ (I/Irated)²: ≈ 2 °C continuous) and life is set by
  ambient.
- The PWM-frequency (400 kHz–1 MHz) ripple of the bridges belongs in block D's local ceramics;
  whatever reaches the bulk is within the 100 kHz rating (block D to confirm its split).

Hold-up (R-34): 8 W for 20 ms = 0.16 J → ΔV ≈ 0.6 V from 48 V. ✓

Life: 10,000 h at 105 °C (φ16) → at 65 °C (55 °C air + 10 °C board) 10,000 × 2^4 = 160,000 h ≈ 18 years
continuous. ✓ (R-40: 105 °C parts with ripple derating ✓)

Alternatives found: Rubycon 63YXJ1000M16X25 (C432366, 7768 stock; 2.73 A, 0.032 Ω) — second source;
Rubycon 63ZLJ1500M18X25 (C5115522, 1214 stock; 18 × 25, fewer cans: 4 × 1500 µF = 6 mF) — if area is
tight, phase 4 can switch to 4 × 18 mm cans.

---

## VBUS overvoltage scheme (agreed with block D, 2026-11-07)

Rule: **every part on VBUS stays within its rating, and 63 V is the bulk's absolute limit.** The KZN
datasheet gives no surge rating (block D also checked Chemi-Con's English technical note, §5-6-1:
none), so no surge allowance is assumed.

| Layer | What | Threshold | Owner |
|---|---|---|---|
| 1. Bulk absorbs returned energy | 6 mF (4.8 mF at −20 %) | — | B |
| 2. Gateware stop (R-35) | all bridges stop switching; restart below 52 V | **55 V**, ADS7042 at 896 kS/s, reaction < 5 µs | D/E |
| 3. Converter output OVP (independent of the opto) | UCC2897A LINEOV from the averaged N5 forward voltage; hiccup | VBUS ≈ **53.3 V** (51.2–55.4 V) | B (`B-controller.md`) |
| 4. TVS, fast low-energy spikes only | **SMCJ51A at the bulk (B)**, SMBJ51A at each bridge (D) | VWM 51 V, VBR 56.7–62.7 V | B, D |

**Energy (block D's figures):** worst case is OCP/stop with all four output inductors at 16 A:
½ × 10 µH × 16² × 4 = 5.1 mJ, plus ≈ 4 mJ of regen during the < 5 µs detection latency (15 A at
55 V). After the stop the bridge body diodes can return back-EMF only while it exceeds VBUS, and BTL
supply pumping is small (R-35). ≤ 12.4 mJ (block D's final figure) into 6 mF at 55 V: ΔV ≈ E/(C·V) = 0.04 V. Amp energy alone
cannot lift VBUS from 55 V to 56.7 V (that needs ½ × 6 mF × (56.7² − 55²) = 0.57 J, 46× the event).

**Converter-side sources:**
- Load dump (amp load → 0): the converter only ever supplies ≤ 1.34 A (CC); the bulk supplies the
  rest. A 1.34 A → 0 step with fc 1.5 kHz and 6 mF: ΔV ≈ ΔI/(2π·fc·C) = 1.34/(2π × 1.5 k × 6 mF)
  = 24 mV. ✓ (< 55 V by 6.5 V)
- Feedback failure (opto LED open, TL431 open, divider open): FB goes to VREF, D = DMAX. In CCM VBUS
  would go to 2·Vin·DMAX = 53–83 V. Layer 3 trips whenever Vin·D ≥ 26.4 V, i.e. at Vin ≥ 41.9 V
  (DMAX min 0.63) / 38.8 V (DMAX nom). Residual gap: Vin 38.4–41.9 V with a low-DMAX part *and* a
  feedback failure *and* DCM (light load): VBUS can drift above 56.7 V; the SMCJ51A then conducts
  converter current (≤ primary peak limit, ≈ 3 A) and, if it lasts, fails short; the converter then
  sits in current limit / hiccup and the PD current limit backs it up. A double fault in a narrow
  window; accepted and recorded.

### D (VBUS TVS, B side) — SMCJ51A, MDD

Datasheet: datasheets/smcj51a-mdd.pdf. Read: ratings table and curves.
Supplier: `C408371 SMCJ51A (MDD(Microdiode Semiconductor), DO-214AB(SMC)): extended, JLC stock 10685, lifecycle normal, checked 2026-11-07`
Replaces the SMCJ58A (its VBR 64.4 V min was above the bulk's 63 V).

| Parameter | Datasheet | Need | |
|---|---|---|---|
| VWM | 51.0 V | > VBUS static max 48.6 V (47.9 V + 1.5 %) | ✓ |
| VBR | 56.7–62.7 V at 1 mA | min > 55 V gateware stop (no leakage heating below it); max ≤ 63 V bulk rating at onset | ✓ |
| IR | 1 µA at VWM | | ✓ |
| VC | 82.4 V at 18.2 A (10/1000 µs) | < 100 V GaN, < 100 V for LM5013/LM5017/LM5019, INA281 (110 V), 100 V ceramics | ✓ |
| PPP | 1500 W | spikes only | ✓ |

Every VBUS part at the TVS's 82.4 V worst clamp: GaN 100 V ✓; LM5013/LM5017 (block C) 100 V ✓;
LM5019 (B) 100 V ✓; INA281 110 V ✓; 100 V MLCCs ✓; block D's ADC divider → 3.2 V vs ADS7042
AVDD + 0.3 = 3.55 V ✓ (block D); the bulk only ever sees a spike at the TVS that the bulk itself does
not follow (its voltage moves only with energy, layer 1).

## Layout guidance

- Output ceramics at the inductor output, in the SR power cell; IBUS shunt after them.
- Bulk cans spread along the VBUS pour between the converter and the bridges; each bridge has its
  own ceramics (block D). The TVS at the VBUS entry to the bridges (shortest path to GaN).

## Open questions

1. MLCC DC-bias assumption (50 % at 48 V); close with Murata SimSurfing data (n14).
4. SMCJ51A leakage at a sustained 55 V (97 % of VBR min) is not specified above VWM; measure it hot
   (review n1).
2. KZN gives no surge rating; the scheme above never relies on one.
3. KZN lead option "ML25S" pitch/length for the footprint.

## Phase 2 schematic notes (iso_dcdc, 2026-11-08)

- **Footprint correction:** the CDRH127/LD land pattern (datasheet p.1, "Land pattern") is **two
  pads**, 5.4 × 2.9 mm, outer edges 12.8 mm apart; the 7.0 mm band in the drawing is silk, not
  copper. The "4-pad" line above is wrong. Made as `studio_B:L_Sumida_CDRH127`.
- Drawn as above: L202, C231–C236 (6 × 4.7 µF 100 V 1210, GCM32DC72A475KE02L `C913445`), R233
  30 mΩ shunt, C241–C247 (C247 DNP), D208 SMCJ51A.
