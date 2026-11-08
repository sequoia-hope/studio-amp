# Block B primary power stage — main FET, clamp FET, clamp capacitor, current sense, input ceramics

Converter numbers (D, Vc, currents, losses) come from `B-converter-design.md` (737 kHz, crystal-synced, n = 2,
Lm = 25 µH, Io = 1.34 A). All parts return to `VPRI_RTN`.

---

## Q (main) — FDMS86200, N-channel 150 V, Power 56

Datasheet: datasheets/fdms86200.pdf (Fairchild/onsemi). Read: all.
Supplier: `C128799 FDMS86200 (onsemi, PDFN-8(4.9x5.8)): extended, JLC stock 3185, lifecycle normal, checked 2026-11-07`
Footprint: Power 56 (PQFN-8 5 × 6, exposed drain). Same part as Q16 in TI PMP20878.

| Parameter | Datasheet | Our worst case | Margin |
|---|---|---|---|
| VDS | 150 V | Vc 100 V plateau, ≈ 120 V with ringing (PMP20878 measured 126.7 V) | 80 % of rating |
| VGS | ±20 V | 14.3 V drive (VDD; 14.8 V max) | OK |
| ID | (35 A class) | 4.9 A peak, 2.0 A rms | OK |
| EAS | 220 mJ single pulse | backstop only | — |
| rDS(on) | 18 mΩ max at 10 V, 21 mΩ at 6 V | × 1.7 hot → 31 mΩ | |
| Qg(0–10 V) | 33 typ / 46 max nC | ≈ 45 nC at 14.3 V (scaled from the 10 V figure) | |
| Coss | 203 pF typ at 75 V | | |
| Qrr | 113 typ nC | body diode conducts briefly before turn-on (ZVS attempt); it is reverse-recovered by the clamp — small at 1.2 A | |
| RθJA | 50 °C/W (1 in² 2 oz) | | |

Losses (737 kHz, 50 V): conduction 1.9² × 0.031 = 0.11 W; turn-on Eoss·f ≈ 0.75 µJ × 737 kHz =
0.55 W (it turns on at ≈ Vin: magnetizing current brings Vds from Vc to Vin, and only leakage
energy is left below that; Eoss from the ≈ 600 pF switch node, review n8); turn-off
½ × Vc × Ipk × 3 ns × f = 0.41 W. Total ≈ 1.07 W (1.19 W at 57 V). With the datasheet's 1 in² 2 oz
pour (50 °C/W): ΔTj ≈ 60 °C → Tj ≈ 115 °C at 55 °C air; acceptable (150 °C max), but **give it
≈ 2 in² of 2 oz copper on two layers with thermal vias (≈ 35 °C/W → Tj ≈ 97 °C)** (phase 4/6).
Gate: 2.2 Ω series, 10 kΩ gate–source (and 10 kΩ OUT–PGND at the controller).

Alternative checked: Infineon BSC160N15NS5 (C459172, 9127 stock; 16 mΩ, Qg 19 nC, but Coss 341 pF and
Qoss 51 nC at 75 V, which raise the hard turn-on loss at ≈ Vin). Kept as a pin-compatible
(TDSON-8/Power 56) alternate for bench comparison.

---

## Q (clamp) — IRFR6215, P-channel −150 V, DPAK

Datasheet: datasheets/irfr6215.pdf (Infineon/IR). Read: all.
Supplier: `C537989 IRFR6215TRLPBF (Infineon, DPAK(TO-252AA)): extended, JLC stock 14871, lifecycle normal, checked 2026-11-07`
Footprint: DPAK (TO-252AA).

Why not PMP20878's FDMC2523P (C890927, 2852 stock, 1.5 Ω max): with a 4-turn primary Lm is 4× lower,
so the clamp carries 1.32 A p-p of magnetizing current at 737 kHz: Irms = ΔIm/√12 × √(1−D) = 0.27 A at
50 V → 0.27² × 1.5 Ω × 1.6 = 0.18 W in FDMC2523P. IRFR6215 (0.295 Ω max): 0.04 W conduction.
IRFR6215 is kept: lower total loss and its larger Coss softens the main FET's turn-off.

| Parameter | Datasheet | Our worst case | Margin |
|---|---|---|---|
| V(BR)DSS | −150 V | −Vc = −100 V, ≈ −120 V with ringing | 80 % |
| VGS | ±20 V | 0 to −13 V (AC-coupled AUX, minus the clamp diode drop) | OK |
| RDS(on) | 0.295 Ω max at −10 V | 0.47 Ω hot | |
| Qg | 66 nC max (hard-switched, Qgd 35 nC at −120 V) | ZVS operation: ≈ 28 nC per cycle (Ciss 860 pF × 14 V + Qgs) → 28 nC × 14.3 V × 737 kHz = 0.30 W gate power (mostly in the UCC2897A and gate resistor) | estimate |
| Coss | 220 pF at −25 V | adds to the switch node (helps the soft turn-off of the main FET) | |
| trr / Qrr | 160 ns / 1.2 µC | body diode conducts at the start of off-time; at AUX turn-off the channel carries current in the drain-to-source direction, so the diode is not recovering | OK |
| RθJA | 50 °C/W PCB mount | ≈ 0.1 W in the FET → +5 °C | OK |

Gate drive (UCC2897A Fig. 24): AUX → 100 nF X7R 25 V → gate; BAS316 (C109218) from gate (anode)
to source/RTN (cathode) clamps the positive swing; 10 kΩ gate–source holds it off when undriven
(τ = 1 ms ≫ 2.5 µs period).
`C109218 BAS316,115 (Nexperia, SOD-323): extended, JLC stock 179814, lifecycle normal, checked 2026-11-07`

---

## C (clamp) — 2 × 100 nF 250 V X7R 1206, Murata GRM31CR72E104KW03L

Datasheet: datasheets/murata-grm31cr72e104.pdf. Read: all.
Supplier: `C97956 GRM31CR72E104KW03L (muRata, 1206): extended, JLC stock 36517, lifecycle normal, checked 2026-11-07`

Low-side clamp: the cap sits between the main-FET drain and the clamp-FET drain and holds Vc ≈ 100 V.
- Voltage: 100 V DC on a 250 V part (2.5×). OK.
- DC-bias: not in the datasheet. **Assumed** 70 % remaining at 100 V on a 250 V X7R → 2 × 70 nF =
  140 nF effective. To confirm (Murata SimSurfing).
- Sizing (737 kHz): clamp–Lm resonance must be slow against the off-time: π√(Lm·C) =
  π√(25 µH × 140 nF) = 5.9 µs ≥ 3 × tOFF(max) = 3 × 0.78 µs = 2.3 µs ✓. Ripple ΔVc ≈ ΔIm·tOFF/(8C) =
  1.32 × 0.78 µs/(8 × 140 nF) = 0.9 V ✓ (< 1 %). Not larger: Vc must still follow D within a few
  cycles, so the transformer stays reset in transients.
- RMS current 0.27 A total, 0.14 A each: fine for a 1206 X7R at 737 kHz (self-heating ≪ 10 °C,
  estimate).

---

## R (CS) — 68 mΩ 1 % 2512, TA-I RLP25FEER068

Datasheet: datasheets/tai-rlp25-r068.pdf (RLP series). Read: ratings, construction.
Supplier: `C2683389 RLP25FEER068 (TA-I Tech, 2512): extended, JLC stock 12945, lifecycle normal, checked 2026-11-07`

- Primary peak needed at the 1.36 A CC limit, Lm −20 %: 2 × (1.36 + 0.51) + 1.53 = 5.27 A.
- Cycle-by-cycle 0.43–0.53 V → 6.3–7.8 A with 68 mΩ: margin 1.19 at the low threshold; hiccup at
  0.75 V → 11 A (short circuit).
- Power: main-FET rms 1.96 A (42 V) → 0.26 W on a 2–3 W-rated 2512 (datasheet, with 300 mm² pads):
  OK, < 15 % of rating.
- Kelvin-route the CS sense trace from the resistor pad to RF; return the RC to the GND island.
- Option for later: a current transformer would save ≈ 0.25 W (0.4 %); not on this spin.

---

## C (input) — VPRI high-frequency ceramics, 3 × 4.7 µF 100 V X7S 1210, Murata GCM32DC72A475KE02L

Changed from Taiyo Yuden HMK325C7475KMHPE (review m7: the fetched sheet was the HMJ catalog).
Datasheet: datasheets/murata-gcm32dc72a475.pdf (Murata GCM catalog; 100 Vdc, X7S, 1210).
Supplier: `C913445 GCM32DC72A475KE02L (muRata, 1210): extended, JLC stock 9059, lifecycle normal, checked 2026-11-07`

These are B's local commutation caps at T1/main FET; block A owns the PD's bulk (electrolytic) on
`VPRI`. Dielectric X7S (±22 %, −55…+125 °C).
- Voltage: 57 V on 100 V (1.75×) ✓ (MLCC guideline ≥ 1.5–2×).
- DC bias: not in the datasheet; **assumed** 45 % remaining at 57 V → 3 × 2.1 µF = 6.3 µF. Confirm.
- Ripple current: Ipri·√(D(1−D)) = 2.68 × 0.5 = 1.34 A rms total, 0.45 A each ✓.
- Ripple voltage: Ipri·D(1−D)·T/C = 2.68 × 0.25 × 1.36 µs / 6.3 µF = 0.14 V p-p ✓ (737 kHz).
- Plus 1 × 100 nF 100 V 0603 at the transformer primary pin for the highest frequencies (generic).

---

## C (input, bulk) — 47 µF 100 V aluminium electrolytic, Honor RVT2A470M1010 (SMD 10 × 10.2)

Datasheet: datasheets/honor-rvt2a470m1010.pdf (HonorCap RVT; scanned, read from rendered pages 1–2).
Supplier: `C87862 RVT2A470M1010 (Honor Elec, SMD,D10xL10.2mm): extended, JLC stock 13805, lifecycle normal, checked 2026-11-07`
Footprint: SMD can, ΦD 10, L 10.2, land per datasheet Fig. 1 (A 11.1, B/C 10.3, E 4.5 mm).

Added at block A's request (A-interfaces.md): B's ceramics sit behind the hot-swap, so they are the
PD's CBULK, and the LT4321 bridge controller needs ≥ 10 µF across OUTP–OUTN (= VPRI–RTN once the
hot-swap is on). 3 × 4.7 µF X7S at 57 V is ≈ 6 µF effective, short of that. The electrolytic also
damps cable/ceramic ringing.
- Voltage: 57 V on 100 V ✓. Category −55…+105 °C ✓ (R-40).
- Total on VPRI–RTN: 47 + ≈ 8 µF ceramics + block A's own = ≤ 120 µF recommended (TPS2373 Table 5,
  300 µF absolute) — block A holds the total.
- Ripple: 148 mA rms rated at 120 Hz, 105 °C; × 1.50 at ≥ 10 kHz = 222 mA. tanδ 0.14 → ESR ≈ 4 Ω at
  120 Hz, ≈ 0.5–1 Ω at 737 kHz (estimate) vs a few mΩ for the ceramics, so it takes ≪ 0.1 A of the
  1.34 A rms switching ripple ✓.
- Life: 2000 h at 105 °C with rated ripple → ≈ 32,000 h at 65 °C (3.6 years continuous) by the
  10 °C rule, at negligible ripple. Adequate for the prototypes; for a product, a 5000 h+ part.
- Place it beside the 3 × 4.7 µF at T1/main FET.

## Layout guidance

- Primary power loop: input ceramics → T1 N1‖N2 → main FET drain → source → Rcs → RTN → ceramics,
  as small as possible, on adjacent layers with a solid RTN plane.
- Clamp loop: main-FET drain → clamp caps → clamp FET → RTN, tight.
- Controller OUT/AUX traces short and paired with their returns.
- Switch node (main drain) is the high-dV/dt node: small area, away from the opto and FB.

## Open questions

1. MLCC DC-bias figures above are assumptions.
2. Bench: main-FET Vds peak at 57 V and in a load step (see converter design note on DMAX).

## Phase 2 schematic notes (iso_dcdc, 2026-11-08)

- FDMS86200 (Power 56) is placed on KiCad's `Infineon_PG-TDSON-8_6.15x5.15mm`: the onsemi
  recommended land (datasheet p.7: 5.10 × 6.61 mm, 0.61 × 1.27 mm leads at 1.27 mm, 3.91 × 3.75 mm
  paddle) matches the TDSON land within ≈ 0.12 mm, pin 1–3 S, 4 G, 5–8 / paddle D. Symbol:
  `Transistor_FET:BSC026N08NS5` (same 1–3 S, 4 G, 5 D).
- IRFR6215 on `TO-252-2` with the `IRF9540N` P-FET symbol (1 G, 2 D, 3 S = DPAK pin-out).
