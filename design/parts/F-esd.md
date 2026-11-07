# D_ESD1–D_ESD7: PESD15VL1BA jack ESD protection (R-42), plus rail clamps

Datasheet: `datasheets/pesd15vl1ba.pdf` (NXP/Nexperia PESDxL1BA series, Rev. 02, 20 Aug 2009).
Read in full: features, pinning, limiting values, ESD ratings, characteristics, curves and
application notes.
MPN: PESD15VL1BA,115 (Nexperia). `C85378 PESD15VL1BA,115 (Nexperia, SOD-323): extended, JLC stock 17151, lifecycle normal, checked 2026-11-07`
Second sources with the same MPN in SOD-323: `C2831526 PESD15VL1BA (UMW, SOD-323): extended, JLC stock 74090, lifecycle normal, checked 2026-11-07`, plus FUXINSEMI C18723438 (96k) and BORN C314262.
Footprint: SOD-323. The part is bidirectional, so it has no polarity.

Quantity per board: 7.
- HP jack: tip and ring (2).
- RCA L and R centre pins (2).
- Mic jack: tip and ring (2).
- One spare on the HP_DET normal contact (1).

Sleeves and shells go directly to GND (see `F-jacks.md`).

## Choice

| Requirement | Value | PESD15VL1BA | OK |
|---|---|---|---|
| Stand-off ≥ max normal swing | HP/line op-amp can clip at ±13.5 V | VRWM 15 V; V(BR) 17.1 V min / 18.9 typ / 20.3 max | OK, 1.5 V margin at clipping |
| Leakage at the working voltage (audio linearity) | ≪ 1 µA | IRM < 1 nA typ, 50 nA max at 15 V | OK |
| IEC 61000-4-2 ±8 kV contact (R-42) | 8 kV | 30 kV rated (ten pulses); level 4 | OK |
| Capacitance (audio, 100 Ω build-out) | not critical | Cd 16 pF typ at 0 V | OK: the pole with 100 Ω is ≈ 100 MHz |
| Clamp | ≤ downstream rating, after series R | 25 V at 1 A, 44 V at 5 A (8/20 µs) | see below |

**Downstream after the clamp:**
- HP: a 44 V transient reaches OUT_HP through the closed relay. R_OUT 4.7 Ω then feeds the BAV99
  rail clamps on OUT_HP, which hold it to ±(15 + 0.86) V. The clamp current is
  (44 − 16)/4.7 Ω ≈ 6 A for nanoseconds. BAV99 IFSM is 4 A at 1 µs, which is marginal for an
  8 kV event. However, the ESD pulse is 1 ns rise, ~60 ns long, with 30 A initial at 8 kV into the
  TVS. The TVS takes the bulk of it, and the residue through 4.7 Ω and the trace inductance into
  the BAV99 is short.
  **Mitigation: a ferrite bead (600 Ω at 100 MHz, ≤ 0.1 Ω DC) between the TVS and the relay
  NO pin.** It blocks the ns-scale ESD energy and does nothing at audio frequencies. Phase 2
  picks the LCSC part.
  Rejected: 10 Ω in series, which would raise Zout to 15 Ω. That is still fine for 300–600 Ω
  headphones, but it costs damping and level for no further benefit.
- Line out: R_BO 100 Ω plus the BAV99 on the op-amp side: (44 − 16)/100 = 0.28 A peak. Fine.
- Mic: the TVS, then 470 Ω, then BAV99 to the ±15 V rails at the preamp input:
  (44 − 16)/470 = 60 mA. Fine. SA5532 input ±10 mA abs max: the BAV99 takes the current.

**Rail clamps:** BAV99 (C2500, basic; datasheet `datasheets/bav99.pdf`), one package per
output node, connected as a series pair across the rails:
- pin 2 (K2) to +15 V
- pin 1 (A1) to −15 V
- pin 3 (K1/A2) to the node

This clamps the node between −15 − VF and +15 + VF.
- VR = 100 V. At a node swing of ±7.4 V each diode sees 7.6–22.4 V of reverse bias. The leakage
  is ≤ 30 nA (at 25 V, 25 °C).
- Cd ≤ 1.5 pF into a 4.7 Ω/100 Ω source. Its voltage dependence adds negligible distortion.

## Fine print / gotchas

- The ESD rating assumes the TVS is the first thing the pulse reaches. Put it **at the jack pin**,
  with its own GND via within 1 mm and no shared narrow ground trace.
- Bidirectional is required: the audio swings both ways.
- PESD15VL1BA has a different V(BR) from PESD12VL1BA (12 V parts would conduct when a clipping
  op-amp hits 13.5 V). Do not substitute the 12 V part.

## Layout guidance

- Jack pin → TVS → ferrite (HP only) → relay NO. The TVS ground goes straight to the GND plane
  near the jack sleeve's GND via.
