# Output-short detector (×4, one per output node): RC differentiator + TLV3502 window → channel fault node

> **UPDATE 2026-11-08 (IGB070S10S1):** turn-off ≈ 4.5 ns instead of 7 ns → short to all gates off **≈ 48 ns**; peak ≤ pre-fault + 0.24 A ≤ 13.3 A (legitimate peak at 576 kHz is 13.0 A, D-output-inductor.md).

Added after the phase 1 review (M2). The INA241 "holds the output for 1 µs" after a large common-mode ΔV/Δt (INA241 §7.3.1.1, p.15–16; threshold not published). A hard output short is exactly such a step at the shunt's common mode, so the current-sense path is blind for ≈ 1 µs in the fault it exists for. This detector catches the step itself, in ≈ 55 ns, independently of the current path.

Datasheets: datasheets/tlv3501.pdf (TLV3501/3502); datasheets/yageo-cc-npo.pdf (Yageo CC series NP0/C0G, voltage code 0 = 100 V); datasheets/bat54s-nexperia.pdf (BAT54S); datasheets/uniroyal-0402wgf.pdf; datasheets/bat46wj.pdf. Read: electrical tables, ratings, part-number keys.

| Ref (per output node; 4 per board) | Part | Supplier (`show`, 2026-11-07) |
|---|---|---|
| C_D (differentiator) | 47 pF ±5 % NP0 **100 V** 0603, Yageo CC0603JRNPO0BN470 | `C327115 CC0603JRNPO0BN470 (YAGEO, 0603): extended, JLC stock 9906, lifecycle normal` |
| R_D, R_S (2 per node) | 1.00 kΩ 1 % 0402 (Uni-Royal 0402WGF1001TCE family); R_S in series with each comparator input | basic Uni-Royal 0402 1 % (LCSC number fixed in phase 2) |
| D_CL (clamp to 3V3_A and GND) | Nexperia BAT54S (series pair) | `C47546 BAT54S,215 (Nexperia, SOT-23): extended, JLC stock 301527, lifecycle normal` |
| U_SD (window comparator) | TLV3502AIDCNR | `C48618` (D-ocp-logic.md) |
| Bias V_B = 1.65 V (one per channel) | 2 × 20.0 kΩ divider from 3V3_A + 100 nF | C25765 / C60474 |
| Window thresholds (one per channel) | ladder from 3V3_A: 2.65 V / 0.65 V | Uni-Royal 0402 1 %: 6.2 k / 12.0 k / 6.2 k (sum 24.4 kΩ) + 100 nF each node |
| Diodes into FAULT_RAW_n | 2 × BAT46WJ per node (8 per board) | C114696 |

## Circuit
Output node (the filter-capacitor node, OUT_P or OUT_N, bridge side of the tweeter HPF) → C_D 47 pF → node X → R_D 1 kΩ → V_B (1.65 V). D_CL (BAT54S) clamps X to 3V3_A and GND. A TLV3502 window compares X with 2.65 V and 0.65 V; each output (active-high "OK") goes through a BAT46WJ into the channel's FAULT_RAW_n wired-AND (D-ocp-logic.md). Any step ≥ 1 V, or a slew faster than ≈ 21 V/µs, at either output terminal of a channel clears that channel's latch.

## Calculations
- τ = R_D·C_D = 1 kΩ × 47 pF = **47 ns**. For a ramp of slope S, X settles at V_B ± S·τ; trip at |S·τ| = 1.0 V → **S_trip = 21 V/µs**. For a step faster than τ, X jumps by the full step (clamped) → **any step ≥ 1.0 V trips** within ≈ 2 ns.
- Normal operation (no trip):
  - full-scale 20 kHz audio per node: 2π × 20 kHz × 24 V = 3.0 V/µs → 0.14 V;
  - CM switching ripple 1.07 V pp triangle at 448 kHz: ≈ 2.4 V/µs → 0.11 V;
  - switch-node edges coupled through inductor winding capacitance (≈ 30 pF into 700 nF): a 48 V edge gives ≈ 2 mV steps → 0.002 V.
  - Worst sum ≈ 0.27 V against a 1.0 V threshold → margin ≥ 3.7×.
  - Plugging or unplugging a speaker does not step the node: the caps feed the voice-coil inductance.
- Fault (hard short at a terminal): the 700 nF node collapses through the short in tens of ns, at ≥ 0.5 V/ns over 24–48 V → trip.
- Delay, short to all gates off: step detection ≈ 2 ns + TLV3502 7 ns (≥ 20 mV overdrive) + BAT46WJ 2 ns + 74LVC1G17 4.6 ns + 74LVC1G74 5.9 ns + 1 ns + LMG1210 tEN 20 ns + IGC033 turn-off 7 ns = **≈ 50 ns**.
- FET/inductor current at gates-off = pre-fault current + inductor-limited rise over 50 ns: + 4.9 A/µs × 50 ns = +0.25 A → **≤ 13.4 + 0.25 ≈ 13.7 A** (13.4 A = maximum legitimate peak). The filter-capacitor discharge flows in the external short, not through the FETs.
- Clamp current: a 48 V step at 1 V/ns through 47 pF = 47 mA for ≈ 50 ns → BAT54S IFRM 300 mA, IFSM 600 mA ✓; charge into 3V3_A 2.4 nC → 0.5 mV on its 4.7 µF ✓. VF at 47 mA ≈ 0.55 V (BAT54S: 500 mV max at 30 mA, 800 mV at 100 mA) → X stays within −0.55 … 3.85 V. TLV3502 abs max (p.4): input (V−) − 0.3 … (V+) + 0.3 V, **input current ≤ 10 mA**. With a series **R_S 1 kΩ** between X and each comparator input (same 0402 family), the current is ≤ (0.55 − 0.3)/1 kΩ = 0.25 mA ✓. The 1 kΩ adds ≈ 3 pF × 1 kΩ = 3 ns, which is negligible.
- C_D voltage: ≤ 48 V DC (55 V stop; 82.4 V TVS transient) on a 100 V NP0 ✓.
- Supply: TLV3502 ≤ 5 mA per comparator × 8 = 40 mA max more on +3V3 (block D +3V3 total ≤ 85 mA; D-interfaces.md).

## Coverage, and the residual gap
| Event | Who trips | Trip current / delay |
|---|---|---|
| Hard short at a terminal (to GND, to VBUS, across), with a node step ≥ 1 V | **this detector** | ≤ 13.7 A, ≈ 50 ns from the short |
| Overcurrent without a CM step (speaker impedance collapse, a short applied when the node is already at the short's potential) | INA241 path (no hold, because there is no CM step) | 14.9 ± 0.7 A, ≈ 218 ns from threshold (D-current-sense.md) |
| A CM step < 1 V that still triggers the INA241 hold, followed by a current ramp | INA241 after its 1 µs hold | up to ≈ 21 A (review M2). The hold threshold is unpublished; a sub-1 V step is far below PWM-edge scale, so this case is unlikely. Bring-up: measure the INA241 hold threshold with a CM step generator. If it is below 1 V, lower this detector's threshold (R_D or C_D) |

## Layout guidance
C_D at the filter-capacitor node (100 V spacing); X, R_D and the clamp next to the comparator; keep X (a 1 kΩ node) away from the switch nodes and inductors.

## Open questions
1. INA241 common-mode hold threshold (bench, as above).
