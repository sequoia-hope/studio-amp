# Block B PoE-loss detector, version 3 — VBUS-droop comparator driving `POE_LOSS_N` (R-32a, R-34)

Lead decision 2026-11-08 (third-pass review `design/gates/rereview2-phase1.md`, BLOCKER-1, MAJOR-1):
the primary-pulse-height detector (`B-poe-loss-detect.md`) is **retired**; that file stays,
marked superseded. `POE_LOSS_N` is now a plain secondary-side **VBUS-droop comparator**: open-drain,
active low (2N7002 output since the fourth-pass review, MAJOR-1), pulled up to +3V3 at the FPGA (block E's 4.7 kΩ, FPGA A6; block F's
/DC_TRIP OR diode also hangs on it).

`ACF_PULSE` is unchanged: forward-SR NCP4306 DRV → 10.0 k/4.99 k → 74LVC2G08 gate B (VCC +3V3; the
other input tied high) → FPGA B6 through block E's 4.7 kΩ. The gate A half, the TLV3201, the
`SW_SEC` divider, the qualifier and the LVC1G123 of version 2 are deleted.

## Circuit

Supplied from `VSR` (B's 10 V secondary bias, LM5019 from VBUS). VSR is regulated for VBUS ≥ ≈ 10.6 V
and present down to VBUS ≈ 6.5 V (LM5019 UVLO off), so the comparator works throughout the
whole droop range, far below 33 V.

1. **Reference**: TL431BIDBZR, 2.495 V, fed from VSR through **3.9 kΩ** (1.92 mA at 10 V, 1.85 mA at
   9.7 V, ≥ 1.8× the 1.0 mA Imin max; 14 mW; fourth-pass m-2). **No capacitor on the TL431 node**:
   1 nF–1 µF is the TL431's unstable region, and it is stable bare (n-1).
2. **VBUS divider + filter**: VBUS → 150 kΩ (**0805**, 150 V working; it sees 57 V continuously and
   82.4 V at the TVS clamp; m-6) → node `VBD` → 10.0 kΩ → GND (0.1 %); **33 nF** at `VBD`
   (Thevenin 9.38 kΩ → **τ = 0.31 ms**).
3. **Comparator: LM393 (half A)**, open collector, VCC = VSR: − input ← `VBD`; + input ← reference
   through 10.0 kΩ, with **866 kΩ** hysteresis feedback from the output node to + input. Output
   node pulled up to VSR by **3.3 kΩ** (sink 3.0 mA when low, inside the 4 mA VOL test condition).
4. **Output stage (fourth-pass MAJOR-1):** output node → **10 kΩ series → 2N7002 gate, 15 kΩ gate to
   source**. Drain = `POE_LOSS_N`.
   - Comparator low (normal): gate = VOL × 15/25 ≤ 0.7 V × 0.6 = **0.42 V** (LM393 VOL ≤ 0.7 V hot at
     ≤ 4 mA), against the 2N7002's VGS(th) **1.0 V min** (JSCJ sheet), which is ≈ 0.75 V at a hot
     junction. Off ✓. (The AO3400A, VGS(th) 0.65 V min and ≈ 0.45 V hot, could be held partly on by
     0.7 V. That was the finding.)
   - Comparator high (asserted): node = VSR × 25 k/28.3 k = 8.57–9.10 V (VSR 9.7–10.3 V) → gate
     **5.14–5.46 V** ≥ 5 V, where the JSCJ 2N7002's RDS(on) is specified **≤ 7 Ω at VGS 5 V** →
     VOL(`POE_LOSS_N`) ≤ 1.37 mA × 7 Ω = **9.6 mV** (block F needs ≤ 0.1 V) ✓. VGS ≤ 20 V abs max ✓.
5. LM393 half B unused: + to GND, − to the reference, output open (held low).

## Calculations

**Thresholds** (Vref 2.495 V, divider ratio 16.00, + input = Vref via 10.0 k and output node via 866 k):
- Comparator low (normal, VBUS high; node at VOL 0–0.7 V): + = 2.495 − (2.495 − VOL) × 10 k/876 k =
  2.4665–2.4745 V → **asserts when VBUS falls below 39.5 V** (39.46–39.59 V from VOL alone).
- Comparator high (asserted; node 8.57–9.10 V): + = 2.495 + (Vnode − 2.495) × 10 k/876 k =
  2.5644–2.5704 V → **releases when VBUS rises above 41.1 V** (41.03–41.13 V from VSR alone).
  Hysteresis ≈ 1.6 V.
- **Tolerance, re-derived per the fourth-pass review (m-4):** TL431**BI** SOT-23-3: 0.5 % initial plus
  VI(dev) 34 mV max over −40…85 °C (1.4 %); dividers 0.1 % each (0.2 %); LM393 VIO 9 mV over
  temperature (0.36 %); LM393 IIB 400 nA × 9.38 kΩ = 4 mV (0.15 %) → **≈ ±2.6 %**.

| Corner | Assert (falling) | Release (rising) |
|---|---|---|
| Nominal | 39.5 V | 41.1 V |
| All tolerances low | 38.5 V | 40.0 V |
| All tolerances high | **40.5 V** | **42.2 V** |

  The hysteresis tracks within one unit (same reference), so release > assert on every unit.
- **Never asserts in a legitimate burst sag:** the allowed sag floor is 43.2 V (R-33), 2.7 V above
  the highest assert point (40.5 V) ✓. The Type 2 burst from 4.8 mF at the 0.44 A limit bottoms at
  ≈ 42.3 V (reviewer), 1.8 V above it ✓.
- **Always releases before `VBUS_VALID` can set:** highest release 42.2 V, against the 44.0 V
  calibrated set point (1.8 V margin) and 44.9 V uncalibrated (2.7 V) ✓.
- The ADC rule (40.5 V calibrated) normally trips first; the comparator is the FPGA-independent
  hardware path for block F's D_PL diode and for an ADC failure (n-4). Both are intended.
- Above the downstream UVLOs (block C's UVLO-off ≈ 30.2 V including 1 % dividers, m-3) ✓.

**Filter:** τ 0.31 ms (≈ 0.3 ms to cross a 1 V overdrive step); the LM393 adds ≈ 1 µs. It ignores
switching ripple and the µs spikes of the amp's PWM. A real droop is ms-scale, so the filter adds
≤ 0.5 ms.

**Start-up qualification (stated choice):** the comparator asserts `POE_LOSS_N` whenever VBUS is below
41.1 V, including during every start-up ramp. There is no hardware qualification. **The FPGA ignores
`POE_LOSS_N` until `VBUS_VALID` has first been set: VBUS > 44.0 V continuously for ≥ 10 ms** on block
D's ADS7042 (> 44.9 V before the gain calibration is stored). This is the lead's B/D/E rule, reproduced verbatim in `B-interfaces.md`, together with
the parallel ADC detector (VBUS < 40.5 V for ≥ 0.5 ms) and `PD_PG_N` high. 44.0 V lies above the
comparator's 42.2 V maximum release. Block F's relay OR on `POE_LOSS_N` keeps its relays off until
VBUS passes 41.1 V, which helps pop-free start-up. That holds only for VBUS ≳ 7.5 V, where VSR
exists; below that, and on USB-only power, `POE_LOSS_N` reads high and the relays rely on the
HP_EN/LO_EN gateware default (n-3).

**Timing, PoE loss → assertion** (6 mF nominal, 4.8 mF at −20 %; constant-power load;
t = C·(V1² − V2²)/(2P)):
1. After the PSE removes power, the converter keeps running from the PD bulk (≈ 55 µF) until LINEUV
   stops it at 38.4 V: ½ × 55 µF × (50² − 38.4²) = 28 mJ → **0.5 ms at 60 W, 2.8 ms at 10 W**.
   VBUS is held up during this time.
2. VBUS then falls from its operating point to the assert point (38.5–40.5 V; worst = latest =
   38.5 V):
   - **60 W**, from 48 V: 6 mF × (48² − 38.5²)/120 W = **41.1 ms** (32.9 ms at −20 % C); from a sagged
     43.2 V: **19.2 ms**.
   - **Idle ≈ 10 W** (rails 8 W + amp idle): 6 mF × (48² − 38.5²)/20 W = **247 ms**.
3. Filter + comparator ≤ 0.5 ms.
**Total: ≈ 20–42 ms at 60 W, ≈ 250 ms at idle.** At idle nothing audible is lost; the amp output is
already near zero.
Other paths for comparison: `PD_PG_N` rises **45–140 ms after LINEUV** (soft-stop 45–80 ms until SS
falls to the 2N7002 threshold, plus 0–60 ms; review MAJOR-1). That is *not* a prompt trigger.
VB_PRI loss takes ≈ 38 ms. The VBUS-droop comparator is the first to trip at load.

**Hold-up after assertion (R-34: ≥ 20 ms of logic, gate-drive and analog rails, output at zero):**
worst case is assertion at 38.5 V and −20 % bulk (4.8 mF). Block C's 5 V buck and Fly-Buck UVLO-off
is ≈ 30.2 V including 1 % divider tolerance (≤ 29.6 V from the IC limits alone; fourth-pass m-3).
Energy available: ½ × 4.8 mF × (38.5² − 30.2²) = 1.37 J. The FPGA's ≤ 5 ms ramp to zero from 60 W
uses ≤ 0.15 J (triangular). The remaining 1.22 J at 8 W of rails gives **≈ 150 ms ≥ 20 ms** ✓.
(Loss during a 144 W burst at 43.2 V: 5.9 ms to the assert point, ramp 0.36 J, and VBUS is still
≈ 36 V after 20 ms at 8 W ≫ 30.2 V ✓, reviewer.)

## Behaviour by case (load 0 to full)

| Case | VBUS | `POE_LOSS_N` |
|---|---|---|
| Regulation, any load | 47.2–48.6 V | high ✓ |
| Burst sag (CC limit, bulk supplying) | ≥ 43.2 V | high ✓ (2.7 V margin) |
| DCM, skip, regen, overvoltage hiccup | ≥ 47 V | high ✓ |
| Converter clock fault (free-running) | regulated | high (clock fault handled by the `ACF_PULSE` rule) |
| Start-up ramp | 0 → 48 V | low until 41.1 V; ignored by the FPGA until `VBUS_VALID` (> 44.0 V for ≥ 10 ms) |
| PoE loss at 60 W | falls | **low ≈ 20–42 ms after loss**, then ≈ 150 ms of rail hold-up |
| PoE loss at idle | falls slowly | low ≈ 250 ms after loss (no audio consequence) |
| Converter fault / short (VBUS collapses) | falls | low ✓ (any cause of VBUS loss is reported) |

## Parts

| Ref | Part | Supplier line |
|---|---|---|
| Comparator | LM393DR2G (dual, open collector, 2–36 V, VIO ≤ 5 mV, VICR to VCC − 1.5 V; datasheets/lm393-onsemi.pdf) | `C7955 LM393DR2G (onsemi, SOIC-8): basic, JLC stock 348306, lifecycle normal, checked 2026-11-07` |
| Reference | TL431BIDBZR | `C41283 TL431BIDBZR (TI, SOT-23-3): extended, JLC stock 149263, lifecycle normal, checked 2026-11-07` |
| Output FET | 2N7002 (JSCJ; VGS(th) 1.0–2.5 V, RDS(on) ≤ 7 Ω at VGS 5 V; datasheets/2n7002-jscj.pdf). Replaces the AO3400A (fourth-pass MAJOR-1) | `C8545 2N7002 (JSCJ, SOT-23): basic, JLC stock 5965601, lifecycle normal, checked 2026-11-07` |
| ACF_PULSE buffer | 74LVC2G08DP (inputs tolerant to 5.5 V, IOFF; datasheets/74lvc2g08-nexperia.pdf, m-2) | `C406037 74LVC2G08DP,125 (Nexperia, TSSOP-8): extended, JLC stock 56760, lifecycle normal, checked 2026-11-07` |
| Passives | 150 k 0.1 % **0805** + 10.0 k 0.1 %, 33 nF, 10.0 k (+ input), 866 k (hysteresis), 3.9 k (TL431), 3.3 k (pull-up), 10 k + 15 k (gate divider) | generic |

## Bench cases

PSE unplugged at 0 W, 10 W and 60 W: time to `POE_LOSS_N`, then VBUS and +3V3/VDRV/±15 V for ≥ 20 ms.
Burst sag to 43.2 V: must not assert. Start-up: `POE_LOSS_N` releases at ≈ 41.1 V.
