# U (VDRV) — LM5017 7 V gate-drive supply from VBUS, with TLV6703 power-good

## Revision 3 (2nd review, 2026-11-07): supersedes Rr, the frequency and the VDRV_PG divider in Revision 2 below

**On-time tolerance (m-1).** LM5017 TON tests (p. 5): 188/250/336 ns at 48 V, 100 kΩ (−25 %/+34 %),
270/350/460 ns at 32 V. So tON(VDRV) = 191 kΩ scaled from those: typ ≈ 1.2 × 10⁻¹⁰ × RON/VIN, −25 %
… +34 %.
- With Rr = 499 kΩ the FB ripple at TON min fell to 24–27 mV, at the 25 mV floor (p. 9).
  **Rr → 360 kΩ** (0805, 150 V working), Cr 1 nF:
  - Vr at TON min: 36 V → (36 − 7) × 459 ns / 360 µs = **37 mV**; 48 V → 40 mV.
  - At TON max, 56 V: 49 × 550 ns / 360 µs = 75 mV.
  - So Vr = 37–75 mV, ≥ 25 mV with margin for Cr +10 % (≥ 33 mV).
- Offset Vr/2 = 18–38 mV. With RFB top 46.4 kΩ (ratio 5.64): **VDRV = 7.01–7.12 V typ**, **6.87–7.27 V**
  over the FB reference spread (1.20–1.25 V). That is inside block D's 7.0 V ±5 % (6.65–7.35 V) and
  above the 6.40 V TLV6703 trip.
- **Real switching frequency** (with the datasheet's measured constant): ≈ **305 kHz typ,
  ≈ 230–410 kHz** over the TON spread (not the 410 kHz eq. 1 gave). ΔIL at 230 kHz, 56 V: 49 × 7/(47 µ ×
  230 k × 56) = 0.57 A → Ipk = 0.15 + 0.28 = 0.43 A, < 0.7 A ILIM min. COUT ripple at 230 kHz:
  0.57/(8 × 230 k × 14 µ) = 22 mV, acceptable for an LDO input.
- Beat products: see C-interfaces.md "5 V buck beat-frequency rule" (accepted residual, smaller than
  the Fly-Buck's −94 dBc because VDRV is ≈ 48 mA).

**VDRV_PG divider (n-5): 4.7 kΩ / 2.7 kΩ** (ratio 0.365).
- Good: 7.0 V → **2.55 V**; at the 6.40 V trip → 2.34 V (2.26 V with a 50 kΩ GPIO pull-down
  enabled), ≥ VIH 2.0 V.
- LM5017 FB-overvoltage fault (VOUT ≈ 9.3 V) → **3.39 V**, under IOVDD + 0.3 V = 3.6 V.
- The 4.7 k/3.3 k suggested in the review gives 9.3 × 3.3/8.0 = 3.84 V, which does not clear it, so
  2.7 kΩ is used.
- TLV6703 sink current 7.0/4.7 k = 1.5 mA.

## Revision after phase 1 review (2026-11-07): supersedes the setpoint, ripple, load and VDRV_PG items below

**Type III ripple offset (review M1).** The COT comparator trips at the FB ripple valley, so the
FB average sits at VREF + Vr/2. That is the same mechanism LM5013 §9.2.2.7 states; the first audit
ignored it. With Rr = 100 kΩ the offset was ≈ +0.55 V (VDRV ≈ 7.6 V).
- tON uses both the eq. 3 constant (1.0 × 10⁻¹⁰) and the datasheet test point (250 ns at 48 V,
  100 kΩ → 1.2 × 10⁻¹⁰): tON = (1.0–1.2) × 10⁻¹⁰ × 191 kΩ / VIN.
- **Rr = 499 kΩ**, Cr = 1 nF (Rr·Cr = 499 µs). Vr = (VIN − 7)·tON/(Rr·Cr):
  31–37 mV at 36 V, 33–40 mV at 56 V. That is ≥ 25 mV (datasheet minimum, p. 9) everywhere and
  nearly line-independent.
- Offset Vr/2 = 15.5–20 mV at FB. **RFB top = 46.4 kΩ** (bottom 10.0 kΩ, ratio 5.64):
  VDRV = (1.225 + 0.0155…0.020) × 5.64 = **7.00–7.02 V** typ; 6.85–7.16 V over the FB reference
  spread (1.20–1.25 V). That meets block D's 7.0 V ±5 %.

**Load (latest, 2026-11-07): the user put the GaN back to IGB070S10S1: 48 mA at 576 kHz, 39 mA at
448 kHz, 57 mA at 768 kHz, 78 mA at 1 MHz (block D).** The 200 mA design is unchanged. IGC033S10S1
fallback figures follow, and the INN100 figures below are superseded: **76 mA at the 576 kHz baseline** (block D, ×12 FPGA grid); 61 mA at 448 kHz, 68 mA at 512 kHz, 88 mA at 672 kHz, 127 mA at 1 MHz; spec ≤ 150 mA. The 200 mA design covers it: Ipk = 0.15 + ΔIL/2 (0.16) = 0.31 A at
150 mA, against the 0.7 A minimum current limit. Power at VDRV 0.43 W (448 kHz) / 0.89 W (1 MHz), so
**≈ 0.51 W / 1.05 W from VBUS**. Per-driver LDO loss at 1 MHz: 2 V × 32 mA = 64 mW.

**VDRV_PG divider re-sized.** It now goes to RP2350 GPIO33 (not the FPGA). If a GPIO pull-down
(≈ 50 kΩ) is ever enabled, 47 k/33 k would sag to 2.1 V. New: **4.7 kΩ from VDRV, 3.0 kΩ to GND**:
7.0 V → 2.73 V, at the 6.40 V trip 2.49 V, 2.65 V with a 50 kΩ pull-down in parallel. In an LM5017
FB-overvoltage event (VOUT ≈ 9.3 V) the node reaches 3.62 V (review note: previously 3.84 V). TLV6703
sinks 7/4.7 k = 1.5 mA (≤ 5 mA VOL spec). VDRV absent → 0 V ("absent = not good", unchanged).

Datasheets: datasheets/lm5017.pdf (SNVS783H, Dec 2014). Read: all sections. datasheets/tlv6703.pdf
(ZHCSHG9A, Apr 2018, Chinese edition from LCSC; the tables are bilingual and the numbers were read
from them). Load requirements from datasheets/lmg1210.pdf (§6.1, §6.3, §6.5, §7.3.2, §8.2.2.5) and
the GaN Qg from datasheets/inn100ebd018dad.pdf, inn100ebd025dad.pdf, inn100ea035ead.pdf.
MPN: LM5017MRX/NOPB   Supplier: `C34355 LM5017MRX/NOPB (TI, SOIC-8-EP): extended, JLC stock 12815, lifecycle normal, checked 2026-11-07`
MPN: TLV6703DDCT     Supplier: `C2877614 TLV6703DDCT (TI, SOT-23-6): extended, JLC stock 538, lifecycle normal, checked 2026-11-07`
Footprints: LM5017 "DDA" SO PowerPAD-8 (EP to RTN/GND); TLV6703 "DDC" SOT-23-6 (thin).

## The load (LMG1210 ×4)

- LMG1210 VIN (LDO input) 6–18 V ROC, 20 V abs max. VDD (LDO output / bypass input) 5.5 V abs max,
  4.75–5.25 V if the LDO is bypassed (§6.1, §6.3). Its LDO is good for ≥ 100 mA with ≤ 750 mV dropout
  at 100 mA (§6.5) and needs ≥ 0.3 µF effective, ESR < 0.5 Ω on VDD (§7.3.2). That cap is block D's.
- Current per driver (§8.2.2.5, eq. 9, 10; EC: IDD ≤ 0.55 mA in PWM mode, IHB ≤ 0.85 mA, ILSDyn
  ≤ 1.25 mA/MHz, IHSDyn ≤ 0.7 mA/MHz): I = 2·Qg·fsw + 1.95 mA/MHz·fsw + 1.4 mA.
  - Qg = 19 nC (INN100EBD018DAD, the worst of the three candidates; 11 nC EBD025, 10.1 nC EA035).
  - At 768 kHz: 29.2 + 1.5 + 1.4 = **32.1 mA**; ×4 = 128 mA.
  - At 1 MHz (R-53 upper end): 38 + 1.95 + 1.4 = **41.4 mA**; ×4 = **165 mA** → design 200 mA.
  - **Revision 2026-11-07 (block D, D-interfaces.md):** the GaN is now Infineon IGB070S10S1
    (Qg 6.1 typ / 7.9 nC max). Block D's per-driver maxima, including 10 k gate pull-downs: 10.4 mA
    at 480 kHz (baseline) and 19.7 mA at 1 MHz → **42 / 79 mA for four drivers** (block D spec
    ≤ 100 mA). The 200 mA design above is kept as margin: the inductor, caps and LM5017 are unchanged,
    and ripple and current limit only get easier. Block D keeps LDO operation (VIN = VDRV, no VDD
    bypass) and fits the VDD caps (100 nF + 2.2 µF per driver).
- Per-driver LDO loss at VIN 7.0 V: (7.0 − 5.0) × 41 mA = 83 mW for the old 19 nC FET; 39 mW with IGB070S10S1 at 1 MHz. LDO headroom 2 V vs ≤ 0.75 V dropout.
- Why 7 V: high enough above the 6 V VIN minimum to leave margin for LM5017 tolerance (±2 %) and
  droop, low enough to keep LDO heat inside the drivers small (12 V would be 0.29 W per driver, next
  to hot GaN).

## Absolute max vs our worst case (LM5017, §6.1/6.3)

| Parameter | Abs max | Our worst case | Margin |
|---|---|---|---|
| VIN, UVLO to RTN | 100 V | 56 V (VIN); UVLO driven at 3.0 V | OK |
| SW | −1.5 V (−5 V 100 ns) … VIN + 0.3 | sync FET, no diode | OK |
| BST to SW / VCC | 13 V | VCC 7.6 V | OK |
| FB | 5 V | 1.225 V | OK |
| VIN ROC | 7.5–100 V | 33–56 V | OK |
| Peak switch current | ILIM 0.7 (min) – 1.3 A (max) | 0.32 A | OK |
| TJ | 125 °C ROC | est. +15 °C | OK |

## Required external parts (LM5017 datasheet + AN-2292)

- CVCC 1 µF 16 V on VCC (pin table); CBST 0.01 µF 16 V on BST–SW (pin table).
- RON, FB divider, UVLO network, Type III ripple network (Rr, Cr, Cac) per AN-2292 Table 2.
- CIN close to VIN–RTN; EP to RTN and the GND plane.

## Calculations

**Output** (FB 1.225 V, 1.20–1.25 V): RFB bottom 10.0 kΩ, top 47.5 kΩ →
1.225 × 5.75 = **7.04 V** (6.90–7.19 V).

**Frequency** (eq. 1: f = VOUT/(K·RON), K = 9 × 10⁻¹¹): RON = 191 kΩ → **410 kHz**.
tON = 10⁻¹⁰ × RON / VIN (eq. 3) = 341 ns at 56 V (> 100 ns minimum), 531 ns at 36 V.

**Inductor**: L = 47 µH. ΔIL = (VIN − VOUT)·VOUT/(L·f·VIN) = 0.29 A (36 V) … 0.32 A (56 V).
Ipk = 0.165 + 0.16 = **0.32 A**, against a 0.7 A minimum current limit. OK.
Part **SRN6045TA-470M** (Bourns, datasheets/bourns-srn6045ta.pdf): 47 µH ±20 %, DCR 200 mΩ typ,
Irms 1.6 A, Isat 2.0 A (−30 % L), −55…+125 °C. That is above the 1.3 A current-limit maximum, so it
survives a short. Loss 0.165² × 0.2 = 5 mW.
`C5151734 SRN6045TA-470M (BOURNS, SMD,6x6mm): extended, JLC stock 4173, lifecycle normal, checked 2026-11-07`

**COUT**: ΔV = ΔIL/(8·f·C). 10 mV needs 9.8 µF effective → 2 × 10 µF 25 V X7R 1206 (CL31B106KAHNNNE,
C14860; assume ≥ 70 % at 7 V → 14 µF, giving ≈ 7 mV). Each LMG1210 also gets its own VIN bypass
(block D).

**CIN** (AN-2292 eq. 20): ≥ IOUT/(4·f·ΔVIN) = 0.2/(4 × 410 k × 0.5) = 0.24 µF → 1 µF 100 V X7R 1206
(CL31B105KCHNNNE, C13832) + 100 nF 100 V 0603.

**Type III ripple** (AN-2292 eq. 35): Rr·Cr ≤ (VIN(min) − VOUT)·tON/50 mV = (36 − 7) × 531 ns / 50 mV
= 308 µs. Cr = 1 nF, so Rr ≤ 308 kΩ. Choose **Rr = 100 kΩ** (≈ ⅓, "half to a fourth … for margin"),
Cac = 100 nF. Rr (now 499 kΩ) sees SW, up to ≈ 91 V in a clamped surge: **0805, 150 V working**.

**Enable (default off)**: UVLO pin = `VDRV_EN` (3.3 V logic) through 10 kΩ, with 100 kΩ to GND.
When high: 3.3 × 100/110 = 3.0 V, minus the 20 µA hysteresis source × 9.1 kΩ = 0.18 V, so 2.8 V,
above the UV threshold max 1.26 V → on. When low or floating: 0 V, below the remote-shutdown
threshold min 0.32 V → shutdown (50 µA IIN). There is no VBUS-derived UVLO on this converter.
Firmware asserts VDRV_EN only with VBUS in range (VBUS_SENSE, block D), and LM5017 runs down to
7.5 V VIN, so it can't be under-volted in service.

**VDRV_PG (TLV6703)**: VDD = VDRV (1.8–18 V ROC). SENSE divider 150 kΩ / 10.0 kΩ:
VIT− = 0.3945 × 16 = 6.31 V falling, VIT+ = 0.400 × 16 = 6.40 V rising (EC: 387–400 / 396–404 mV over
temperature → 6.19–6.40 V / 6.34–6.46 V). That is above the LMG1210's 6 V VIN minimum and below the
6.90 V minimum VDRV. OUT is pulled up **from VDRV** through 47 kΩ with 33 kΩ to GND:
VDRV_PG = 7.04 × 33/80 = **2.90 V** when good (2.64 V at 6.4 V; LVCMOS33 VIH 2.0 V), **0 V when VDRV
is absent**. The datasheet leaves OUT indeterminate below V(POR) = 0.8 V and says OUT is driven low
in UVLO, so the pull-up from the monitored rail is what makes "absent" read as "not good". Sink
current 7.04/47 k = 0.15 mA, well under 5 mA. Response tpd(HL) 18 µs.

**Power (revised)**: IGB070S10S1 gives 7.04 V × 42 / 79 mA = 0.30 / 0.56 W out → **0.37 W (480 kHz) / 0.65 W (1 MHz) from VBUS**, counting ≈ 0.15 W VCC loss and ≈ 85 % at full load. The original 19 nC figures follow: **Power**: 7.04 V × 0.165 A = 1.16 W out. LM5017 VCC from 48 V at a few mA ≈ 0.15 W (§7.3.2), so
η ≈ 85 % and **1.35 W from VBUS at 1 MHz** (1.05 W at 768 kHz).

## Fine print / gotchas

- VCC can't be back-fed from VDRV (external VCC must be 8.55–14 V, §7.3.2), so VCC stays internal.
- UVLO falling below 0.66 V (typ; 0.32 V min) is remote shutdown. Keep the VDRV_EN low level solid
  (100 kΩ pull-down) so noise can't toggle it.
- LM5017 has no soft-start pin. The COT start-up runs at minimum off-time with current-limit
  foldback (§7.3.6). Inrush into the drivers' caps (4 × ≈ 1.3 µF + COUT) is bounded by the 0.7–1.3 A
  current limit.
- TLV6703 needs VDD > 1.8 V for 150 µs before OUT is valid. Firmware ignores VDRV_PG for 1 ms after
  asserting VDRV_EN.

## Layout guidance

- LM5017: CIN at VIN/RTN, short SW to L; FB divider and Rr/Cr at FB, away from SW. EP to the plane.
- Route VDRV to the four drivers as a star or plane segment with a 0 Ω/bridged-jumper link at the
  source (R-80) so each driver can be isolated at bring-up. Each LMG1210 keeps its own VIN and VDD
  caps (block D).

## Open questions

- Block D: confirm VIN-pin (LDO) operation and the final GaN Qg and fsw; VDRV current scales
  linearly.
