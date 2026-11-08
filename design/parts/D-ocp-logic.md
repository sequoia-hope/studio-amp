# OCP / fault path (per channel): TLV3502 window comparators, diode-AND, 74LVC1G17 Schmitt, 74LVC1G74 latch → LMG1210 EN

> **UPDATE 2026-11-08 (IGB070S10S1):** the GaN turn-off term becomes ≈ 4.5 ns (Ciss 740 pF to the 2.8 V plateau ≈ 1.9 ns + Qgd 1.7 nC at 0.65 A ≈ 2.6 ns), instead of 7 ns for IGC033. **Ramp-regime total ≈ 216 ns** (was 218 ns).

Datasheets (all read in full for the electrical tables and timing): datasheets/tlv3501.pdf (TLV3501/TLV3502, TI); datasheets/sn74lvc1g17.pdf; datasheets/sn74lvc1g74.pdf; datasheets/bat46wj.pdf; datasheets/uniroyal-0402wgf.pdf (resistors); datasheets/sn74lvc1g11.pdf and datasheets/sn74lvc1g08.pdf (read, considered, not used, see below).

| Ref (per channel) | Part | Qty/ch | Supplier (`show`, 2026-11-07) |
|---|---|---|---|
| U_CMP | TI TLV3502AIDCNR dual 4.5 ns comparator, push-pull, SOT-23-8 | 2 (one per leg) | `C48618 TLV3502AIDCNR (TI, SOT-23-8): extended, JLC stock 3023, lifecycle normal` |
| D_AND | Nexperia BAT46WJ | 10 (4 OCP + 4 short-detect (D-short-detect.md) + DC + ARM) | `C114696 …` (D-bootstrap.md) |
| U_ST | TI SN74LVC1G17DBVR Schmitt buffer | 1 | `C7836 SN74LVC1G17DBVR (TI, SOT-23-5): extended, JLC stock 18921, lifecycle normal` |
| U_LAT | TI SN74LVC1G74DCUR D flip-flop with PRE/CLR | 1 | `C70285 SN74LVC1G74DCUR (TI, VSSOP-8): extended, JLC stock 21448, lifecycle normal` |
| R_TH1/R_TH2/R_TH3 | threshold ladder 9.09 k / 15.0 k / 9.09 k 1 % 0402 (Uni-Royal 0402WGF) | 3 | 0402WGF9091TCE / 0402WGF1502TCE: basic Uni-Royal 0402 1 % series, same datasheet as C25744; LCSC numbers fixed in phase 2 from `jlc_parts.py search` |
| C_TH | 100 nF 0402 on each threshold node | 2 | C60474 |
| R_PU | 2.2 kΩ pull-up on FAULT_RAW_n | 1 | Uni-Royal 0402WGF2201TCE (basic family) |
| R_ARM | 10 kΩ pull-down on FPGA ARM line (shared by both channels) | ½ | C25744 |

Supplies: comparators, logic and pull-up on **+3V3**; threshold ladder on **3V3_A**, the same rail as the INA241 supply and the ADC reference, so thresholds track the INA241 midpoint ratiometrically.

## Circuit (per channel)
1. Each leg's INA241 output V_I (1.65 V + 0.05 V/A) goes to one TLV3502. Channel A: IN+ = V_TH_HI (2.40 V), IN− = V_I → output **high while I < +15 A**. Channel B: IN+ = V_I, IN− = V_TH_LO (0.90 V) → output **high while I > −15 A**. So each comparator output is an active-high "OK".
2. The 4 OK outputs (2 legs × 2) go through BAT46WJ diodes (cathode at the comparator) to node FAULT_RAW_n, pulled up by 2.2 kΩ to +3V3. Also on that node, each through its own BAT46WJ: the channel's **DC_n** node (LMV393 open-drain outputs with their own 4.7 kΩ pull-up, also read by the FPGA; D-dc-detect.md) and the shared FPGA **AMP_ARM** line. Plus 4 more from the channel's two output-short detectors (D-short-detect.md). Ten diodes per channel. Any input going low pulls FAULT_RAW_n low ("wired-AND" of OK signals).
3. FAULT_RAW_n → 74LVC1G17 (Schmitt, needed because the RC release edge is slower than the LVC 10 ns/V input rule) → **FAULT_n** → (a) CLR̄ of the 74LVC1G74, (b) FPGA input.
4. 74LVC1G74: D = FPGA **AMP_EN_x**, CLK = FPGA **AMP_CLK_x**, PRE̅ = +3V3 (inactive). Q → 100 Ω → EN of both LMG1210s in the channel. A fault clears Q asynchronously; EN goes low and all 4 gates go off. While FAULT_n is low, clock edges are ignored (CLR dominates, datasheet function table). The FPGA re-arms by clocking D = 1 once FAULT_n is high again. That is cycle-by-cycle when gateware re-arms at the next PWM period; R-54's "cycle-by-cycle" policy belongs in gateware.
5. Power-up: FPGA pins Hi-Z → R_ARM pulls AMP_ARM low → FAULT_n low → Q = 0 → EN low until the FPGA is configured and drives AMP_ARM high. The LMG1210 stays disabled whatever the flip-flop's random power-up state.

Considered and not used: a 74LVC1G11 3-input AND tree. Six inputs need two cascaded gates (2 × 6.2 ns max), and the AND output would re-enable the bridge as soon as the current fell, with no latch. The diode-AND + Schmitt is one 4.6 ns stage and is extendable.

## Ratings vs worst case
| Parameter | Rating | Worst case | OK |
|---|---|---|---|
| TLV3502 VS | 2.7–5.5 V | 3.3 V | ✓ |
| TLV3502 input CM range | (V−) − 0.2 … (V+) + 0.2 V (rail-to-rail, p.5 CMRR conditions) | 0.05–3.1 V (INA241 swing) | ✓ |
| 74LVC1G17 / 1G74 VCC | 1.65–5.5 V | 3.3 V | ✓ |
| 74LVC1G74 → LMG1210 EN | EN VIR 1.70–2.45 V, VIF 0.70–1.30 V; EN abs max 10 V | VOH ≥ 2.3 V at 24 mA (≥ 3.2 V at the tiny EN load), VOL ≈ 0.1 V | ✓ |
| FAULT_RAW_n low level | 74LVC1G17 VT− at VCC 3 V: 0.89 V min (p.6) | VF(BAT46, 1.5 mA) ≈ 0.25 V + TLV3502 VOL ≈ 0.05 V = 0.3 V | ✓ (0.6 V margin) |
| FAULT_RAW_n high level | VT+ at 3 V: 1.92 V max | 3.3 V via 2.2 kΩ; diode reverse leakage ≤ 10 × 1 µA (25 °C; ≤ 10 × 20 µA hot → 0.44 V) → FAULT_RAW_n ≥ 2.86 V > VT+ 1.92 V ✓ | ✓ |

## Calculations
### Thresholds
Ladder from 3V3_A: R_TH1 (top) 9.09 k, R_TH2 15.0 k, R_TH3 (bottom) 9.09 k; total 33.18 kΩ, 99 µA.
V_TH_HI = 3.3 × (15.0 + 9.09)/33.18 = **2.396 V** → +14.9 A; V_TH_LO = 3.3 × 9.09/33.18 = **0.904 V** → −14.9 A.
Tolerance with 1 % resistors (worst-case combination): V_TH_HI shifts by ≤ ±(1 % × 2.4 V × (1 − 2.4/3.3)) ≈ ±7 mV → ±0.14 A, plus the TLV3502 offset ±6.5 mV → ±0.13 A. Total ±0.27 A plus the shunt/INA chain ±0.42 A (D-current-sense.md) → **trip at 14.9 A ± 0.7 A** (14.2–15.6 A), above the 13.4 A legitimate peak (12 A + ripple/2) ✓.
Internal hysteresis 6 mV (= 0.12 A); enough because the latch holds after the first edge.
The 100 nF on each threshold node: impedance of the 3V3_A divider ≈ 6 kΩ → τ = 0.6 ms, filters any 3V3_A ripple. A 3V3_A step moves V_I's midpoint and the thresholds together.

### Delay, threshold to gates off (R-54 ≤ 200 ns)
| Stage | Max delay | Source |
|---|---|---|
| INA241 ramp lag (1.1 MHz pole) | 145 ns | D-current-sense.md |
| Overdrive build-up: INA241 output slews 0.25 V/µs at 4.9 A/µs, so 5 mV of overdrive arrives 20 ns after the crossing (review m5) | 20 ns | — |
| TLV3502, 5 mV overdrive, −40…125 °C | 12 ns (7 ns at 20 mV) | TLV3501 p.6 switching table |
| BAT46WJ diode-AND (falling edge, comparator sinking) | ≈ 2 ns (node C ≈ 10 × Cd(3 V) ≈ 10 × 15 pF ≈ 150 pF driven by the comparator's ≈ 30 Ω output) | estimated (Cd at 3 V not in the datasheet; 39 pF max at 0 V) |
| 74LVC1G17 tpd at 3.3 V | 4.6 ns | 1G17 p.7 |
| 74LVC1G74 PRE/CLR→Q at 3.3 V | 5.9 ns | 1G74 p.1/p.8 |
| 100 Ω + EN input C | ≈ 1 ns | — |
| LMG1210 tEN (EN → outputs low) | 20 ns | LMG1210 p.7 |
| GaN turn-off (IGC033S10S1: 5 V → 2.6 V plateau at ≈ 1.2 A avg through 1.6 Ω + 2.7 Ω ≈ 3 ns, then Qgd 2.6 nC at 2.6 V/4.3 Ω = 0.6 A ≈ 4.3 ns) | ≈ 7 ns | D-gan-fet.md |
| **Total (ramp regime)** | **≈ 218 ns** (≈ 190 ns typ) | above R-54's 200 ns; proposed wording ≤ 250 ns (D-current-sense.md). Hard shorts take the ≈ 50 ns path (D-short-detect.md) |

### Release (re-arm) timing
FAULT_RAW_n rising: τ = 2.2 kΩ × (≈ 150 pF diodes + 5 pF input) ≈ 340 ns (worst case with Cd = 39 pF: 2.2 kΩ × 395 pF = 870 ns) → the Schmitt switches at ≈ 1.9 V after ≈ 0.9τ. The FPGA must wait for FAULT_n high and then ≥ 100 ns before clocking re-arm (it reads FAULT_n, so no fixed delay is needed). At 480 kHz (2.08 µs period) that fits within the next period.

### Supply current
TLV3502: 3.2 mA typ / 5 mA max per comparator (p.5; taken per channel, conservatively) × 8 (OCP) + 8 (short detect) = **51 mA typ / 80 mA max on +3V3**. Logic ≤ 10 µA each. Pull-ups 1.5 mA each only during a fault. Ladder 0.1 mA × 2 from 3V3_A.

## Fine print
- TLV3502 has no SHDN pin (TLV3501 only). Its outputs are push-pull, which is why the diodes are needed for the wired-AND.
- 74LVC1G74: "When PRE and CLR are inactive (high), data at D meeting setup is transferred on the positive CLK edge"; PRE and CLR low together is a non-stable state (function table note). PRE̅ is hard-tied high, so that state cannot occur.
- 74LVC1G74 setup 1.9 ns / recovery from CLR (tsu "PRE or CLR inactive") 1.9 ns at 3.3 V → the FPGA's D and CLK timing is easy.
- The Schmitt is required: LVC inputs specify Δt/Δv ≤ 10 ns/V (1G74 p.6), and the RC release is ≈ 60 ns/V.

## Layout guidance
- Comparators next to their INA241s; threshold ladder and 100 nF caps at the comparator pins.
- The fault node is local to the channel; the 1G74 sits between the two LMG1210s, with Q fanned out through 100 Ω to each EN pin, short and equal.
- FAULT_n, AMP_EN_x, AMP_CLK_x and AMP_ARM go to the FPGA as ordinary 3.3 V signals.

## Open questions
None beyond D-current-sense.md's 200 ns margin note.
