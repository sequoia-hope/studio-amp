# Block B interfaces — what the isolated converter needs from, and gives to, other blocks

Block B = `iso_dcdc`. Design: `B-converter-design.md`; parts: `B-*.md`.

## From block A (TPS2373-4 PD) — what the UCC2897A needs

| Net / pin | Requirement | Why |
|---|---|---|
| `VPRI` / `VPRI_RTN` (= TPS2373 VDD side after the bridges / TPS2373 RTN) | 42–57 V operating; B's LINEUV turns it on at 40.4 V, off at 38.4 V, so the input current at the Class 8 CC limit stays ≤ 1.85 A (TPS2373 RTN recommended max; fold-back > 1.9 A for 1.65 ms) | block A item 2 |
| PD bulk (CBULK) on `VPRI`–`VPRI_RTN` | block A holds the total (≤ 120 µF recommended, 300 µF abs, TPS2373 Table 5). B fits **47 µF 100 V electrolytic (Honor RVT2A470M1010)** for the LT4321's ≥ 10 µF and damping, + 3 × 4.7 µF 100 V ceramics (≈ 6 µF effective) at T1, + ≤ 2 µF in its bias buck. B's input current at Class 8: ≈ 1.7 A dc at 41 V, 1.34 A rms ripple at 400 kHz carried by B's ceramics; the bulk sees only the low-frequency part | block A should count B's ≈ 8 µF of ceramics in its inrush calculation |
| TPS2373 **PG** → UCC2897A **SS/SD** (via 1 kΩ, B side) | open-drain, active-high, RTN-referenced; low until inrush is complete (+81.5 ms), then high-Z | holds the converter off during inrush |
| TPS2373 **VC_IN** ← B's `VB_PRI` (13.5 V) | B's primary LM5019 output; VC_IN > 8.5 V; < 15 V recommended. `VB_PRI` also feeds block A's isolator primary (≤ 15.3 mA), included in B's buck budget (47 mA total). Idle draw from VPRI during inrush ≈ 10 mA (block A limit 30 mA) | TPS2373 §7.3.7: "If VC_OUT is not used, VC_IN must be connected to the low voltage bias supply of the PWM controller" |
| TPS2373 **VC_OUT** | **not used by B**: 1 µF to RTN only (block A) | its continuous current (20 mA recommended) is below the UCC2897A's 32 mA bias draw |
| TPS2373 **UVLO_SEL** | open (VC_OUT UV 6.9 V) | irrelevant with VC_OUT unused; open is the documented default for UVLO-off > 7.25 V PWMs |
| PD current limit | TPS2373-4 2.2 A typ: above B's maximum input (≈ 1.7 A at 41 V, Class 8) | B's CC loop sets the real limit |
| PD bridge / input TVS | block A; B's parts on `VPRI` are rated ≥ 100 V (ceramics), 100 V (LM5019), 120 V (UCC2897A VIN, tied to VDD anyway) | |
| Type/class signals | `PD_TPL`, `PD_TPH`, `PD_BT` via the digital isolator to block E | firmware selects B's current limit from them (below) |

## To blocks C and D (secondary)

| Net | Spec |
|---|---|
| `VBUS` | 47.9 V nominal, static ±1.5 % (TL431B + 0.1 % divider; R-33 ±2 %); bulk 6 × 1000 µF/63 V (+1 DNP); TVS SMCJ51A (see the overvoltage scheme below) |
| Output current limit (CC) | 0.470 A at reset → 0.944 A (Class 6) → 1.344 A (Class 8), firmware-selected; under CC, VBUS sags (bursts come from the bulk, R-33a) |
| Start-up | VBUS rises in ≈ 0.6–0.9 s (6 mF at 0.47 A, with ≈ 8 W of block C load); block C's rails and the amp must tolerate a slow VBUS ramp (amp muted until VBUS valid, R-34) |
| Converter switching | 400 kHz fixed (free-running, ±6 %): block D can place the amp PWM frequency away from it and its harmonics (R-53 tunable) |
| B's own secondary bias | `VSR` 12 V, ≈ 20 mA, from VBUS inside B; block C does not need to supply B |

## From block E (FPGA / RP2350), secondary side, no barrier crossing

| New net | Direction | Spec |
|---|---|---|
| `ILIM_SEL0`, `ILIM_SEL1` | E → B | 3.3 V GPIO, drive 2N7002 gates; 100 k pull-downs in B so reset state = 00 = 0.47 A. Encoding 00 = 0.47 A, 01 = 0.94 A, 10 = 0.87 A, 11 = 1.34 A. Firmware raises it after reading `PD_TPL/TPH/BT` (or LLDP). |
| `IBUS_SENSE` | B → E (or D's ADC) | 0–3.0 V for 0–1.5 A converter output current (INA281 × 5.4 V/A, divided 16.9 k/10 k; source impedance 6.3 kΩ) |
| `ACF_PULSE` (optional, proposed) | B → E | forward-SR gate (NCP4306 DRV, 10 V) through a 47 k / 22 k divider + clamp to 3.3 V: one pulse per switching cycle at 400 kHz. The FPGA flags PoE loss when ≥ 3 consecutive pulses are missing while `ILIM`/load says it should be switching (R-32a "rectified pulse loss"). Not reliable in pulse-skipping at light load: combine with VBUS droop as R-32a says. |

## VBUS overvoltage scheme (agreed B ↔ D, 2026-11-07; same wording in `D-interfaces.md`)

Every part on VBUS stays within its rating; **63 V (bulk electrolytics, no surge rating
published) is the absolute limit.**
1. **Bulk absorbs returned energy.** Block D's worst case (OCP stop with all four output inductors at
   16 A, 5.1 mJ, plus ≈ 4 mJ of regen during the < 5 µs detection latency) is ≤ 12.4 mJ (block D's final figure): ΔV ≈ 0.04 V on
   6 mF at 55 V. Lifting VBUS from 55 V to the TVS onset (56.7 V) needs 0.57 J.
2. **Gateware stop at VBUS ≥ 55 V**, restart below **52 V** (R-35), block D's ADS7042 at 896 kS/s,
   reaction < 5 µs.
3. **Converter output OVP (B)**, independent of the opto: UCC2897A LINEOV from the averaged N5
   forward voltage, trips at VBUS ≈ 53.3 V (51.2–55.4 V), hiccup. Covers feedback failure.
   Load dump of the converter (1.34 A → 0) overshoots 24 mV.
4. **TVS for fast, low-energy spikes only: SMx51A** — VWM 51 V, VBR 56.7–62.7 V, VC 82.4 V.
   B: SMCJ51A (MDD C408371) at the bulk; D: SMBJ51A (Littelfuse C1973217) at each bridge.
5. Ratings at the 82.4 V clamp (+ ≈ 10 V layout overshoot at the bridge = 92 V): GaN 100 V,
   LM5013/LM5017/LM5019 100 V, INA281 110 V, 100 V MLCCs, block D's ADC divider (3.2 V vs 3.55 V).
6. Residual (recorded): a feedback failure at Vin 38.4–41.9 V in DCM can lift VBUS above 56.7 V before
   layer 3 sees it; the SMCJ51A then takes converter current and may fail short, after which the
   converter's current limit and the PD's take over.

## ±15 V (block C owns the choice) — recommendation

**Against a transformer winding.** T1 (Würth 750343576) has no free secondary winding: N3 and N4
are both used in series for 48 V, and N5 is insulated as a primary winding. A custom transformer
could add one, but a forward auxiliary output needs its own rectifiers and output inductor per rail
and its voltage follows Vin·D, regulated only through the 48 V loop (poor cross-regulation with
the audio load). Derive ±15 V on the secondary from VBUS (or 5 V) and post-regulate.

## Proposed changes to architecture

1. **T1 is not an LCSC part.** Würth 750343576 (WE-PoE++, the transformer of TI's PMP20878) wired
   N1‖N2 : N3+N4 = 1:2, bought from Würth/a distributor and hand-soldered (R-70 already allows
   hand-soldered magnetics). Intent R-33 says "off-the-shelf wound transformer": satisfied, but
   with a non-datasheet winding connection. **User decision** (`B-transformer.md`, options A–E).
2. **fsw = 400 kHz** (set by T1's volt-seconds on a 4-turn primary).
3. **B carries two small 100 V bias bucks** (LM5019): `VB_PRI` 13.5 V on the primary (UCC2897A VDD
   and TPS2373 VC_IN) and `VSR` 12 V on the secondary (SR drivers, TL431s, opto, INA281). Add both
   nets to the rails table; TPS2373 VC_OUT unused (block A).
4. **Secondary CC loop with firmware-selected limit**: new nets `ILIM_SEL0`, `ILIM_SEL1` (E → B) and
   `IBUS_SENSE` (B → E/D). Add to the D ↔ E / B ↔ E interface list. The IBUS shunt splits the
   converter output from the bulk node: `VBUS_CONV` (converter side) → 27 mΩ → `VBUS`.
5. **Optional `ACF_PULSE`** (B → E) for the R-32a rectified-pulse-loss detector.
6. **No ±15 V winding** (above); block C derives ±15 V on the secondary.
7. Architecture decision 6 stands (silicon FETs in the converter): main FET FDMS86200 150 V, clamp
   P-FET IRFR6215 −150 V, SRs BSC500N20NS3 200 V; NCP4306 diode-emulating SR controllers meet R-33.
8. Barrier crossings from B: T1, the LTV-217 opto, one Y2 cap (2.2 nF, +1 DNP). Unchanged from
   decision 4 in spirit (the Y-cap is a passive across the barrier, not a signal).
9. Bulk: 6 × 16 × 25 mm cans (+1 DNP footprint) for phase 4 to place (R-33a said 5–7).
10. **VBUS overvoltage scheme** above replaces R-35's "≈ 56–58 V stand-off" TVS with SMx51A
    (51 V stand-off, VBR 56.7–62.7 V), so the 63 V bulk stays in rating; intent R-35 wording to be
    updated by the lead.
