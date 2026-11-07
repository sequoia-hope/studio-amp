# U (block A) — TPS2373-4 PoE PD interface

Datasheet: `datasheets/tps2373.pdf` (TI SLUSCD1C, rev C, Nov 2018). Read: all sections, pp.1–41.
MPN: TPS2373-4RGWR
Supplier: `C470963 TPS2373-4RGWR (TI, VQFN-20-EP(5x5)): extended, JLC stock 481, lifecycle normal, checked 2026-11-07`
Build need: 5 boards x 1 + attrition = 7. OK. Single source (TI only); no pin-compatible second source in stock
(TPS2372-4RGWR C470955 has 49 in stock but no TPH/TPL/BT advanced start; it is not a drop-in).
Footprint: RGW0020B VQFN-20, 5.0 x 5.0 mm, 0.65 mm pitch, exposed pad 2.2 x 2.2 mm (p.40 package outline,
p.41 land pattern: pads 0.75 x 0.31 mm, EP land 2.2 mm, 3 x 3 vias of 0.2 mm on 0.85 mm pitch). **KiCad's
stock `VQFN-20-1EP_5x5mm_P0.65mm_EP3.15x3.15mm` does not match this EP**; phase 2 must use or make a
footprint to TI's land pattern (EP 2.2 mm, stencil 4 x 0.98 mm windows, p.42).

## Role

Single-signature 802.3bt PD for both pair sets (after the two ideal-diode bridges, see
`A-bridge-lt4321.md`). Detection, 5-event Class 8 signature, internal 0.1 ohm hot-swap switch in the
RTN (low) side, 81.5 ms inrush delay, PG (converter
enable), TPH/TPL/BT allocated-power outputs.

## Absolute max vs our worst case

All voltages to VSS unless noted (p.5).

| Parameter | Abs max | Our worst case | Margin |
|---|---|---|---|
| VDD, DEN | 100 V | 57 V steady; TVS clamp 93.6 V at 6.5 A (SMBJ58A, `A-tvs.md`) | 6.4 V on surge — OK, TVS placed beside U |
| RTN | 100 V (SOA limited to 80 V at 2.5 A, note 4) | 57 V; during inrush RTN falls from VDD at 335 mA | OK |
| RTN current, recommended | 1.85 A (TPS2373-4, p.6) | 71.3 W / 41.2 V = **1.73 A** (Class 8, min Type-4 PI voltage, Table 6 p.22) | 6.5 % — block B must hold input current below 1.85 A (see interfaces) |
| Current limit | 1.9 A min / 2.2 typ (p.7) | 1.73 A | above load |
| VC_IN to RTN | 25 V abs, 15 V recommended max | `VB_PRI` 13.5 V from block B's LM5019 bias buck (`B-interfaces.md`) | 1.5 V to rec. max: OK |
| VC_OUT | internally limited, 13.5–15 V startup | **not used** (block B, 2026-11-07): 1 µF to RTN only; after the VC switch closes it simply follows VC_IN | OK |
| PG, TPH, TPL, BT to RTN | 100 V abs, 57 V rec; sink 3 mA rec | pulled up to 5 V (VISO1) through 10 k ⇒ 0.5 mA | OK |
| APD, UVLO_SEL to RTN | 6.5 V | APD tied to RTN; UVLO_SEL open | OK |
| CLSA, CLSB, REF, MPS_DUTY | 6.5 V; no external voltage | resistors only | OK |
| TJ | 150 °C abs, 125 °C rec | 55 °C air + 0.6 W x 38 °C/W = 78 °C | OK (see calc) |

## Required external parts (from datasheet)

| Ref | Value | Pins | Source |
|---|---|---|---|
| RDEN | 24.9 kΩ 1 % | VDD–DEN | p.4, §8.2.2.4 p.34 |
| C1 (CPD) | 0.1 µF 100 V X7R (0.05–0.12 µF window) | VDD–VSS, shared with LT4321 | §8.2.2.3 p.33; LT4321 p.7 |
| RCLSA | 63.4 Ω 1 % | CLSA–VSS | Table 1 p.18, Class 8 |
| RCLSB | 90.9 Ω 1 % | CLSB–VSS | Table 1 p.18, Class 8 |
| RREF | 49.9 kΩ 1 % (48.9–50.9 kΩ allowed) | REF–VSS | p.4, p.6 |
| D1 TVS | SMAJ58A "or equivalent" — we use SMBJ58A | VDD–VSS (after bridges) | §8.2.2.2 p.33, **must** |
| CVC_OUT | 1 µF (VC_OUT unused, p.4 "bypass with a 1 µF to RTN") | VC_OUT–RTN | p.4, §7.3.7 p.20 |
| CVC_IN | 0.1 µF local bypass (VC_IN is driven by VB_PRI) | VC_IN–RTN | p.4 |
| APD | tie to RTN | — | p.4 "If not used, connect APD to RTN" |
| UVLO_SEL | open | — | §8.2.2.9 p.35 (UCC2897A) |
| AMPS_CTL | open (MPS disabled, R-30); DNP footprint for RMPS 1.3 kΩ 1206 | AMPS_CTL–VSS | p.4, §8.2.2.10 |
| MPS_DUTY | open | — | Table 4 p.20 (no effect with AMPS_CTL open) |
| NC (pin 20) | leave open | — | p.4 |
| Exposed pad | VSS, large copper, 9 vias | — | p.4, §10.1 p.37 |

Values, packages and power checks for these passives: `A-pd-passives.md`.

## Calculations

1. **Class 8 programming** (Table 1, p.18): Class 8 = class signature 4 on events 1–2 (CLSA 63.4 Ω),
   class 3 on events 3–5 (CLSB 90.9 Ω); 5 events grant 71 W (Table 2, p.19). Class current at
   RCLSB = 90.9 Ω is 26.5–29.3 mA (p.7), at 63.4 Ω 38–42 mA (Table 7 p.33).

2. **Input current and hot-swap loss** (p.7 rDS(on) 0.1 Ω typ, 0.2 Ω max over –40…125 °C):
   - Class 8: I = 71.3 W / 41.2 V = 1.731 A. P = I²R = 0.30 W typ, **0.60 W max**.
   - Class 6: I = 51 W / 42.5 V = 1.20 A. P = 0.14 W typ, 0.29 W max.
   - Thermal: RθJA = 38.0 °C/W (p.6, JEDEC board). TJ = 55 °C + 0.60 W x 38 = **78 °C** < 125 °C.
     The bias current adds 0.8 mA x 57 V = 0.05 W; ignored. §10.4: keep the GaN stage and the ACF
     primary FET away; OTSD at 140 °C min can be tripped by neighbours.

3. **UVLO and the operating window handed to block B** (p.8): rising 36.3–40.0 V, falling 30.5–33.6 V,
   hysteresis 6.1 V typ. With PI minima (Table 6 p.22) of 41.2 V (Type 4) / 42.5 V (Type 3) and
   ≤ 0.06 V bridge drop + 0.35 V hot-swap drop at 1.73 A, VPRI at full load is **≥ 40.8 V**. Block B
   must run (at reduced power) down to the PD falling UVLO, 30.5 V, and survive 93.6 V transients.

4. **Inrush and CBULK** (p.7: inrush 275–395 mA; tINR_DEL 78–87 ms; §7.4.6 p.27):
   - The PSE inrush limit is ≥ 400 mA for every class (p.27), so 395 mA max is compatible.
   - Charge time t = C·V / I_inrush,min. For 100 µF: 100 µF x 57 V / 0.275 A = **20.7 ms**; for
     300 µF: 62 ms. Both under the 78 ms minimum inrush delay, so PG releases at ~81.5 ms either way.
   - Energy in the hot-swap FET during inrush ≈ ½CV² = 0.16 J for 100 µF at 57 V, spread over ~21 ms.
     The datasheet gives no single-pulse SOA beyond "80 V at 2.5 A"; Table 5 (p.20) discusses CBULK up
     to 300 µF as a normal system condition. Block B fits 3 x 4.7 µF 100 V ceramics + a 47 µF 100 V electrolytic (61 µF nominal, 12.7 ms
     charge, 0.10 J) on VPRI–VPRI_RTN; these sit behind the hot-swap, so they are **not** part of the 802.3 detection C_PD
     (≤ 0.12 µF, VDD–VSS) but they are part of CBULK. **Recommendation to block B: CBULK (VPRI–VPRI_RTN) 47–120 µF,
     never above 300 µF; ≥ 10 µF is required by the LT4321 (p.7 of its datasheet).**
   - 802.3bt Type 3 PDs must draw < 400 mA until 80 ms after power-up; Type 4 "should" (p.22 items 5–6).
     PG is held low ≥ 78 ms, and the UCC2897A soft-start adds more, so the converter's draw starts later.

5. **UVLO_SEL** (§7.3.7 p.20, p.8): VC_OUT UV falling = 6.45–7.35 V with UVLO_SEL open, 3.45–4.25 V
   with it tied to RTN. It must be below the PWM's minimum falling UVLO. UCC2897A "minimum operating
   voltage after start" = 7.6–8.4 V (`A-ucc2897a.pdf` p.7). 7.35 V < 7.6 V ⇒ **UVLO_SEL open**
   (also TI's own choice for this exact pairing, §8.2.2.9).

6. **Bias arrangement (changed 2026-11-07 after block B's audit)**: the UCC2897A needs ≈ 32 mA of bias
   (73 nC at 400 kHz, `B-interfaces.md`), above VC_OUT's 20 mA recommended sourcing (p.6) and the
   21.5 mA minimum startup source (p.8). So VC_OUT is **not used**: block B powers UCC2897A VDD from its
   own 13.5 V LM5019 buck on VPRI (`VB_PRI`), and **VC_IN is tied to VB_PRI**, as §7.3.7 p.20 requires
   ("If VC_OUT is not used, VC_IN must be connected to the low voltage bias supply of the PWM
   controller"). Consequences: (a) VC_IN is already above 8.5 V when inrush ends, so the VC switch
   closes at once and the startup source turns off 24 ms later; (b) TPH/TPL/BT then become valid
   **24 ms after PG releases** (§7.3.6 p.19, "In applications where VC_IN is tied to a DC voltage already
   present before end of inrush, the 24-ms delay applies from when PG output went from low to open");
   (c) the VC_OUT UV comparator watches VB_PRI (via the closed VC switch), threshold 6.45–7.35 V with
   UVLO_SEL open, still below UCC2897A's 7.6 V minimum stop — UVLO_SEL stays open.
   The isolator primary also runs from VB_PRI (`A-isolator-iso7740.md`).

7. **MPS** (§7.4.7 p.29): the PSE needs ≥ 16 mA at the PSE for Class 5–8. Idle draw (logic ≈ 2.5 W
   + gate drive + ±15 V ≈ 6 W at the PD, R-33a) / 57 V ≈ 105 mA ≫ 28 mA auto-MPS threshold.
   AMPS_CTL open disables auto-MPS (p.4). DNP 1.3 kΩ 1206 footprint keeps the option:
   P = 24² / 1.3 kΩ x 26.4 % = 117 mW (Eq. 7 p.35) < 250 mW (1206).

## Fine print / gotchas

- p.4/§7.3.6: TPH, TPL, BT are **open-drain to RTN, active low**, and are **only enabled 20–28 ms after
  VC_IN rises above 8.5 V** (tTPLHBT) — here VC_IN (VB_PRI) is up before inrush ends, so 24 ms after
  PG releases. They return to high-Z if
  VDD–VSS < ~32 V, on OTSD, or if VC_OUT falls below its UV threshold; the latched class is remembered
  until VDD < mark-reset (3–5 V). So on the secondary they read "not asserted" until 24 ms after the
  converter starts, and they double as an early PoE-brownout flag (they go high-Z at 32 V while the
  converter can still run).
- §7.4.8 p.28: when VDD falls below UVLO the hot-swap opens **but PG stays high-Z**, so PG is *not* a
  PoE-loss signal. R-32a's PoE-loss detection must rely on TPx going inactive and on the secondary
  comparator. Recorded in `A-interfaces.md`.
- Truth table (Table 2 p.19, Table 3 p.19) — for firmware (block E):

  | TPH | TPL | BT | Meaning |
  |---|---|---|---|
  | H | H | H | Type 1/2 PSE, 13 W (1 event) — or isolator unpowered |
  | H | L | H | Type 2 PSE, 25.5 W |
  | H | H | L | Type 3/4 PSE, 1 event, 13 W (demoted) |
  | H | L | L | Type 3/4 PSE, 2–3 events, 25.5 W (demoted) |
  | L | H | L | Type 3/4 PSE, 4 events, **51 W (Class 6 grant)** |
  | L | L | L | Type 4 PSE, 5 events, **71 W (Class 8 grant)** |
  | L | L | H | non-standard PoE++ PSE, full power (§7.4.10 p.30) |
  | L | H | H | APD (adapter) — cannot occur, APD tied to RTN |

  "L" here = pin pulled low = asserted. Across the isolator they arrive as PD_TPH_N etc. with the same
  sense (low = asserted).
- p.22 items 8–10: the PD must not exceed the granted power — firmware sets amp/LED limits from this
  code (R-30, R-33a).
- §7.3.5 p.18 / §7.4.9 p.29: if RTN rises above 14.5 V for > 1.65 ms (overload), current limit drops to
  inrush level and **PG is forced low**, which (through UCC2897A SS/SD) shuts the converter. Block B's
  peak input current must not drive the hot-swap into current limit (≥ 1.9 A) for > 1.65 ms.
- §7.4.8: VC_IN remains connected to VC_OUT after startup. With VC_IN driven by block B's VB_PRI buck
  there is no DVC diode; block B owns VB_PRI's hold-up.
- §7.3.11 p.21: 0.025 in (0.64 mm) clearance between VSS copper and VDD/high-voltage nets.
- §7.3.4 p.18: pulling DEN to VSS during operation kills the hot-swap. We do not use it; RDEN is a
  single resistor (no tap).
- §7.4.4 p.24: bridge incremental resistance adds to the detection signature; FET body diodes are in
  circuit during detection (LT4321 is off below 15 V). The 24.9 kΩ value is TI's recommendation; verify
  the signature on the first board with a PoE tester.
- §8.2.2.1 p.33: Schottky bridges need care for backfeed (2.8 V max into 100 kΩ) and ESD robustness;
  not used here (FET bridges), but the FETs' body diodes and IDSS carry the same backfeed requirement —
  see `A-bridge-fets.md`.

## Layout guidance from datasheet (§10.1–10.3, pp.37–38)

- Power flow point to point: RJ45 → magnetics → bridges → TVS + 0.1 µF → TPS2373. No crossovers.
- Split local planes: VSS plane under the input side and the IC; RTN plane under the switched output.
- Exposed pad: 9 vias to every layer's VSS copper, ≥ 80 % paste coverage. Large VSS pour for heat.
- 0.64 mm minimum VSS–VDD spacing; IEC 60950-style spacing between the 48 V rails and to the secondary
  (the R-32 barrier keepout).
- Use the Bob Smith termination/plane, optional ferrites on the input, keep input copper small.
- RCLSA/RCLSB/RREF next to their pins, returned to VSS (not RTN).

## Open questions

- Hot-swap single-pulse energy with the chosen CBULK: not specified beyond OTSD. Keep CBULK ≤ 120 µF
  unless block B shows otherwise; verify first inrush on the bench (scope RTN–VSS and IPI).
- 802.3bt clause 145 limits (C_PD window, inrush, MPS, backfeed) are taken from this datasheet's summary
  (pp.21–29); the standard itself was not available to read.
