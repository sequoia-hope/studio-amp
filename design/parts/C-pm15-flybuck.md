# U (AN) — LM5017 Fly-Buck: VBUS → +18.4 V / −17.8 V pre-regulated analog rails

## Revision 4 (3rd review, 2026-11-07): inductor tolerance and UVLO for hold-up

**Peak current with L at −20 %.** With 47 µH −20 % = 37.6 µH, at 347 kHz and 56 V: ΔIL = 0.95 A →
isw(pk) = 0.71 A, over the 0.7 A ILIM minimum. **Coupled inductor → PSSCAQ7048M-680M** (68 µH ±20 %
per winding, DCR ≤ 0.7 Ω, Irms 0.7 A, Isat 1.8 A, 600 V coil-to-coil; datasheets/prod-psscaq7048m.pdf,
same 7.6 mm footprint):
- At −20 % (54.4 µH): ΔIL = 37.6 × 18.4/(54.4 µ × 347 k × 56) = 0.65 A → **isw(pk) = 0.122 + 0.112 + 0.33 =
  0.56 A**, 140 mA under ILIM min.
- Winding loss ≈ (0.25² + 0.15²) × 0.7 = 0.06 W. Irms ≪ 0.7 A.
- `C56266204 PSSCAQ7048M-680M (PROD Tech, SMD-4P,7.6x7.6mm): extended, JLC stock 932, lifecycle normal, checked 2026-11-07`
- No stocked Bourns equivalent (SRF0703-680M: 1 in stock), so this part is single-source for the prototypes.
- RON 330 kΩ, Rr 390 kΩ and RFB 137 kΩ are unchanged. Ripple injection doesn't depend on L.

**UVLO lowered for the PoE-loss hold-up** (C-sequencing.md): RUV1 4.42 kΩ → **5.36 kΩ** (RUV2 125 kΩ).
Rising = 1.225 × (1 + 125/5.36) = **29.8 V** (28.9–30.6 V); falling = 29.8 − 20 µA × 125 kΩ = **27.3 V**
(≤ 29.4 V worst case with 1.25 V minimum hysteresis). At 27 V the duty is 0.68 with off-time ≈ 0.7 µs
(≥ 144 ns min off), so it still regulates. The ±15 V LDOs keep their headroom while VOUT1 regulates.

## Revision 3 (2nd review, 2026-11-07): TON tolerance and real frequency

- LM5017 TON is −25 %/+34 % (p. 5). With Rr = 499 kΩ the FB ripple is 34–87 mV (≥ 25 mV), so Rr stays.
- VOUT1 worst case (TON max at 56 V, reference max): ≈ 19.0 V. The +15 V LDO fault dissipation
  becomes 0.81–0.87 W → TJ 106–110 °C at 55 °C air, < 125 °C. VOUT1 minimum 17.9 V leaves the
  TPS7A3001 2.2 V of headroom before cross-regulation droop. Fine.
- **Real switching frequency ≈ 380 kHz typ, ≈ 280–510 kHz** over the TON spread (the measured
  constant 1.2 × 10⁻¹⁰, not eq. 1's 508 kHz). ΔIL at 280 kHz, 56 V: (56 − 18.4) × 18.4/(47 µ × 280 k ×
  56) = 0.94 A → isw(pk) = 0.122 + 0.112 + 0.47 = **0.70 A at the design load**, at the 0.7 A minimum
  limit at the slowest corner. Fault case: current-limit foldback, already accepted.
  **Lower RON to 330 kΩ**: f = VOUT1/(1.2 × 10⁻¹⁰ × 330 k) = 465 kHz typ, **≈ 347–620 kHz** over the TON
  spread. ΔIL at 347 kHz, 56 V = 37.6 × 18.4/(47 µ × 347 k × 56) = 0.76 A → isw(pk) = 0.122 + 0.112 +
  0.38 = **0.61 A** at design, giving ≈ 90 mA of margin to the 0.7 A limit. tON at 56 V, TON min =
  0.75 × 1.2e-10 × 330 k/56 = 0.53 µs ≥ 100 ns.
  **Rr → 390 kΩ** (0805, 150 V): Vr at TON min, 36 V = 17.6 × 0.83 µs/390 µs = **37 mV**; at TON max,
  56 V = 37.6 × 0.95 µs/390 µs = 91 mV. Offset +18…46 mV × 14.7 → **VOUT1 ≈ 18.3–18.7 V typ**
  (≈ 17.9–19.1 V with the reference spread); secondary ≈ −17.7…−18.1 V. **RFB top stays 137 kΩ.**
  The +15 V LDO fault-case TJ stays ≤ ≈ 110 °C (the 19.0–19.1 V worst case above).
- Beat products: the Fly-Buck fundamental and 2nd harmonic sweep across 576 kHz. Its input pulse
  (≈ 0.5 A pk) gives ≈ −94 dBc sidebands (2nd review estimate), an accepted residual (C-interfaces.md).

## Revision after phase 1 review (2026-11-07): supersedes the VOUT1, Rr and frequency items below

**Type III ripple offset (review M1).** With Rr = 100 kΩ the FB ripple was 197–270 mV, an offset of
+1.5 to +2.0 V on VOUT1 (≈ 20 V, line-dependent).
- **Rr = 499 kΩ** (0805, 150 V working: it sees SW up to the 82.4 V TVS clamp), Cr = 1 nF, Cac 0.1 µF. tON = (1.0–1.2) × 10⁻¹⁰ × 402 kΩ / VIN.
- Vr = (VIN − 18.4)·tON/499 µs = 39–47 mV at 36 V, 54–65 mV at 56 V, 36–43 mV at the 33.4 V UVLO.
  That is ≥ 25 mV (datasheet). The capacitive ripple at FB is < 1 mV (13 mV ÷ 15), so the injected
  ripple dominates, which is AN-2292's stability criterion.
- Offset Vr/2 = 20–33 mV at FB. **RFB top = 137 kΩ** (bottom 10.0 kΩ, ratio 14.7):
  VOUT1 = (1.225 + 0.020…0.033) × 14.7 = **18.30–18.49 V** typ (≈ 0.2 V of line dependence);
  17.9–18.9 V over the reference spread. Secondary ≈ −(VOUT1 − 0.6) = **−17.7 to −17.9 V**.
- Frequency (eq. 1, K = 9 × 10⁻¹¹): 18.4/(9e-11 × 402 k) ≈ **508 kHz** (review note).
- Block F's design loads with +5V_A drawn from +15V: primary 120 + 15 = 135 mA, secondary 110 mA.
  isw(pk) = 0.137 + 0.112 + 0.26 = **0.51 A**. In the fault (215 + 190 mA) it is 0.67 A, against the
  0.7 A minimum limit: no margin left. The LM5017 current limit and foldback, plus the LDOs' own
  limits, carry the fault and the pre-rails sag; accepted by block F.

Revision 2026-11-07: resized for block F's real loads (F-interfaces.md): +15 V 62 mA avg / 120 mA design / 200 mA fault; −15 V 50 / 110 / 190 mA. VOUT1 raised to 18.4 V, so the secondary is ≈ −17.8 V wherever −17.4 V appears below.

Datasheets: datasheets/lm5017.pdf (SNVS783H). Read: all. datasheets/ti-snva674-flybuck.pdf (TI
AN-2292 "Designing an Isolated Buck (Fly-Buck) Converter", SNVA674C, Dec 2014). Read: all; it is
the LM5017 Fly-Buck design procedure (eq. 1–35, Table 2). Coupled inductor:
datasheets/prod-psscaq7048m.pdf (PSSCAQ7048M series, A3.0) and datasheets/bourns-srf0703.pdf
(second source). Diode: datasheets/diodes-b1100.pdf.
MPN: LM5017MRX/NOPB   Supplier: `C34355 LM5017MRX/NOPB (TI, SOIC-8-EP): extended, JLC stock 12815, lifecycle normal, checked 2026-11-07`

Topology decision and alternatives: see `C-interfaces.md` ("The ±15 V decision"). The secondary is
**not isolated here**. Its positive end is tied to GND so the rectified output is negative. The
AN-2292 isolation cap (C9, 2200 pF 2 kV) is therefore omitted.

## Polarity (how the negative rail is made)

During TON the primary winding sees VIN − VOUT1 (dot at SW positive). During TOFF it sees −VOUT1.
The secondary (1:1, same dot sense) is wired with its **non-dot end to GND**. During TOFF its dot end
goes to −VOUT1. D1 has its **cathode on the dot end and its anode on the −17.4 V node**, and conducts
during TOFF, charging COUT2 to −(VOUT1 − VF). During TON the dot end is at +(VIN − VOUT1), so D1's
reverse voltage is (VIN − VOUT1) + |VOUT2| ≈ VIN, which matches AN-2292 eq. 28 (VD1 = N2/N1 · VIN).

## Absolute max vs our worst case

| Parameter | Abs max | Our worst case | Margin |
|---|---|---|---|
| LM5017 VIN, UVLO | 100 V | 56 V | OK |
| BST–SW, VCC | 13 V | 7.6 V | OK |
| Peak switch current | ILIM min 0.7 A | 0.50 A at 56 V (120 + 110 mA design); 0.65 A in the 200/190 mA fault case | OK (fault case relies on the 0.7 A minimum limit) |
| D1 VR | 100 V (B1100) | 56 V + ringing | ≈ 1.8× |
| D1 IO | 1 A at TT 125 °C | 110 mA avg (190 mA fault), ≈ 0.4 A pk | OK |
| Coupled L Isat | 2.0 A (single winding; same in parallel) | 0.50 A (0.65 A fault) | OK |
| Coupled L coil-to-coil | 600 V DC (1 mA, 3 s) | ≈ 56 V | OK |
| TPS7A4901 VIN / TPS7A3001 VIN | 36 V / −36 V abs | +18 V / −17.4 V (light-load peak-charge ≤ −20 V with preload) | OK |

## Calculations

**Primary output VOUT1** (eq. 18): RFB bottom 10.0 kΩ, top 140 kΩ → 1.225 × 15.0 = **18.4 V**
(18.0–18.8 V; raised from 18.0 V for the 120 mA loads, to keep the negative side's headroom under heavier cross-regulation droop). This gives the TPS7A4901 an 18.4 − 14.94 = 3.4 V drop, above the datasheet's
"VDO(max) + 1 V = 1.6 V for optimal performance" (TPS7A49 §9.2).

**Secondary** (eq. 2): VOUT2 = −(18.0 − VF) ≈ **−17.4 V** (B1100 VF ≈ 0.6 V at ≈ 0.15 A conduction
current). The TPS7A3001 drop is 17.4 − 15.09 = 2.3 V, above the 1.6 V target with margin for
cross-regulation droop at full secondary load.

**Frequency** (LM5017 eq. 1, K = 9 × 10⁻¹¹): RON = 402 kΩ → f = 18.0/(9e-11 × 402 k) = **498 kHz**.
tON = 10⁻¹⁰ × 402 k / VIN = 718 ns (56 V), 935 ns (43 V), 1117 ns (36 V); all > 100 ns.

**Coupled inductor** (Table 1 eq. 16–17): L1 = 47 µH (per winding; 1:1).
ΔIL1 = (VIN − VOUT1)·VOUT1/(L1·f·VIN) = 0.385 A (36 V), 0.448 A (43 V), 0.522 A (56 V).
isw(peak) = IOUT1 + IOUT2·N2/N1 + ΔIL1/2 = (0.12 + 0.002) + (0.11 + 0.002) + 0.26 = **0.50 A at 56 V** for block F's design loads (+15 V 120 mA incl. +5V_A, −15 V 110 mA), 0.65 A in the both-headphones-shorted fault (200/190 mA),
below the 0.7 A minimum current limit, as eq. 7/8 require. The design load ceiling is
0.7 − 0.26 = 0.44 A total (≈ 2 × 200 mA); the LDOs' 150/200 mA ratings bind first.
Part **PSSCAQ7048M-470M** (PROD Tech, 7.6 × 7.6 × 4.8 mm): 47 µH ±20 % per winding, coupling 97.3 %,
DCR 0.45 Ω max, Irms 1.1 A (single winding, ΔT 40 °C), Isat 2.0 A (−30 % L), −40…+125 °C,
coil-to-coil 600 V DC. Leakage ≈ (1 − 0.973) × 47 µH ≈ 1.3 µH, which sets the secondary's resonant
current shape (AN-2292 §1) and its droop under load. The LDO headroom covers it.
`C56266203 PSSCAQ7048M-470M (PROD Tech, SMD-4P,7.6x7.6mm): extended, JLC stock 996, lifecycle normal, checked 2026-11-07`
Second source, same 7.6 mm 4-pad body: **SRF0703-470M** (Bourns): 47 µH, DCR 0.338 Ω, Irms 1.08 A,
Isat 1.14 A (parallel rating), hi-pot 500 Vrms.
`C3273458 SRF0703-470M (BOURNS, SMD-4P,7.6x7.6mm): extended, JLC stock 204, lifecycle normal, checked 2026-11-07`
**Phase 2: pad geometry and pin-1/dot positions differ between the two datasheets.** Draw the
footprint from the PSSCAQ drawing and check the SRF0703 against it before calling it a drop-in. The
symbol must show the dots.
Winding loss: primary rms ≈ 0.2 A, secondary ≈ 0.13 A → (0.2² + 0.13²) × 0.45 = 25 mW.

**D1 (secondary rectifier)**: VR ≈ 56 V (+ leakage ringing) → 100 V. **B1100-13-F**
(datasheets/diodes-b1100.pdf): 100 V, 1 A at TT 125 °C, VF 0.79 V at 1 A (25 °C), IR ≤ 0.5 mA
(25 °C) / 5 mA (100 °C) at 100 V, CT 80 pF.
Loss ≈ 0.6 V × 0.08 A + leakage 56 V × ~1 mA × 0.4 (on-time fraction, 100 °C worst) ≈ 0.07 W.
`C110106 B1100-13-F (DIODES, SMA(DO-214AC)): extended, JLC stock 29855, lifecycle normal, checked 2026-11-07`
An RC snubber footprint across D1 (e.g. 100 Ω + 220 pF, DNP) lets bring-up tame leakage ringing.

**COUT1 (+18 V)** (eq. 30): ΔVOUT1 ≈ (IOUT2·N2/N1)·TON(max)/COUT1 = 0.08 × 1117 ns / C. For ≤ 20 mV
for ≤ 20 mV at 120 mA that needs C ≥ 6.7 µF effective → **2 ×** 10 µF 50 V X7R 1210 (UMK325AB7106KM / GRM32ER71H106KA12L class;
assume ≥ 50 % at 18 V → 5 µF, giving ≈ 18 mV at 36 V and 11 mV at 56 V).
**COUT2 (−17.4 V)** (eq. 33): ΔVOUT2 = IOUT2·TON(max)/COUT2: same numbers → **2 ×** 10 µF 50 V X7R 1210 (≈ 12 mV at 110 mA, 36 V).
Each pre-regulated rail then passes a BLM18PG221SN1D ferrite (220 Ω at 100 MHz, 1.4 A, ≤ 0.14 Ω;
datasheets/murata-blm18pg.pdf) and 10 µF into its LDO. That 2nd-order filter (≈ 500 kHz content
attenuated further) adds to the LDO's ≥ 55 dB at 700 kHz.
`C80165 BLM18PG221SN1D (muRata, 0603): extended, JLC stock 218690, lifecycle normal, checked 2026-11-07`

**Preload**: 10 kΩ 0603 on −17.4 V (1.7 mA, 30 mW) limits light-load peak-charging of the secondary
by leakage spikes. +18 V already carries the FB divider (0.12 mA) plus the LDO quiescent current.

**Type III ripple** (AN-2292 Table 2, eq. 35): Rr·Cr ≤ (VIN(min) − VOUT1)·TON/50 mV
= (36 − 18) × 1117 ns / 50 mV = 402 µs. Cr = 1000 pF → Rr ≤ 402 kΩ. Choose **Rr = 100 kΩ** (¼, per
"half to a fourth … for robust operation"), Cac = 0.1 µF 25 V. AN-2292 says Type III is preferred for
Fly-Buck because Types I/II jitter from the reflected secondary current.

**UVLO** (AN-2292 eq. 22–23; LM5017 UV 1.19–1.26 V, IHYS 10–29 µA): RUV2 (top) = 125 kΩ,
RUV1 = 4.42 kΩ → rising = 1.225 × (1 + 125/4.42) = **35.9 V** (34.8–36.9 V), falling = 35.9 − 20 µA
× 125 kΩ = **33.4 V** (hysteresis 1.25–3.6 V). The analog rails come up whenever VBUS is up and are off
on USB-only power. Optional firmware kill: a 2N7002-class NMOS from UVLO to GND, gate = `AN_OFF`
with 100 kΩ pull-down (on by default). Pulling UVLO below 0.32 V is remote shutdown.

**CIN**: 1 µF 100 V X7R 1206 + 2.2 µF 100 V 1210 (AN-2292 example 0.47 + 2.2 µF; eq. 20 gives
≥ 0.2 µF). CVCC 1 µF 16 V, CBST 0.01 µF 16 V (datasheet).

**Optional D2** (AN-2292): VOUT1 = 18 V is above the 14 V VCC limit (13 V abs max), so **no** D2 from
VOUT1 to VCC. VCC stays internal: ≈ 3 mA × 48 V = 0.15 W.

**Efficiency / budget** (block F averages: +15 V 62 mA, −15 V 50 mA): out 15 V × 0.112 A = 1.68 W; LDO drop 3.4 × 0.062 + 2.7 × 0.05 = 0.35 W; pre-reg 2.03 W → **2.4 W from VBUS on average**. At the 120/110 mA design load: 3.45 + 0.71 = 4.2 W → 4.9 W from VBUS (short-term only). Superseded figure: out 2 × 15 V × 80 mA = 2.4 W; LDO drop 0.43 W; pre-reg 2.83 W. Fly-Buck η
≈ 85 % (VCC 0.15 W, switching and conduction ≈ 0.3 W) → **3.33 W from VBUS** at full analog load.

## Fine print / gotchas

- Primary and secondary ripple are not those of a plain buck. AN-2292 says the COUT values from
  eq. 29 are starting points, "Actual optimization … must be done experimentally". Plan a bring-up
  step with both rails loaded 0–120 mA at 43 and 56 V.
- Cross-regulation: the secondary droops with its own load, and rises when the primary is heavily
  loaded and the secondary lightly. Check at bring-up that −17.4 V stays within −16.6 V (LDO
  headroom) to −20 V (under 35 V; harmless).
- The secondary current flows only during TOFF, so at high duty (low VIN) the secondary peak rises.
  At 36 V, D = 0.5 is still fine.

## Layout guidance

- Two hot loops: primary (CIN–VIN–SW–L–COUT1–RTN) and secondary (winding–D1–COUT2–GND). Keep both
  tight. Put the coupled inductor between them.
- FB, Rr/Cr/Cac at the FB pin, away from SW and the secondary diode node.
- Phase 4: keep this converter outside the block F analog region, with its GND return into the main
  plane at the converter, not under the audio.

## Open questions

- Block F's real ±15 V load. Above ≈ 120 mA per rail, revisit the LDO dissipation (3 V × I).

## Phase 2 correction (schematic, 2026-11-07)

125 kΩ 0805 is not stocked. **RUV2 = 124 kΩ 0805 (C17440)** with RUV1 5.36 kΩ: rising
1.225 × (1 + 124/5.36) = **29.6 V**, falling 29.6 − 20 µA × 124 kΩ = **27.1 V** (typ). The PoE-loss
hold-up margin in C-sequencing.md is unchanged to within 0.2 V. The RC snubber across D1 is
drawn DNP: 100 Ω 1206 (C17901; ≈ 0.27 W at 50 V, 498 kHz) + 220 pF C0G 100 V 0603
(AC0603JRNPO0BN221, C2982813). The 50 V-rated 220 pF parts are too low for the 56 V reverse swing.
