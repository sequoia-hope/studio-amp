# T1 — forward transformer, Würth 750343576 (WE-PoE++), re-wired 1:2

Datasheet: datasheets/we-750343576.pdf (Würth Midcom, rev 003.001, 2024-02-16). Read: all 8 pages.
MPN: 750343576   Supplier: **not on LCSC** (`jlc_parts.py search 750343576` returns nothing;
findchips shows no distributor stock on 2026-11-07). Source: Würth Elektronik direct (samples) or
Digi-Key/Mouser order; hand-soldered or consigned to JLC (R-70 allows hand-soldered magnetics).
Footprint: Würth recommended land pattern, datasheet p.1 (SMD, ER19/4.8/15 core; TI's BOM TIDRRG4
gives the body as 23.37 × 21.08 mm). Drawn from the datasheet drawing in phase 2.
Reference use: TI PMP20878 (TPS2373-4 + UCC2897A, 40–57 V → 24 V / 3 A, 93.1 % converter
efficiency, TIDUDB0 test report, BOM TIDRRG4, schematic TIDRRG3).

**User decision needed: this is the only usable off-the-shelf forward transformer found, it is not
on LCSC, and its stock at distributors is unconfirmed.** See "Sourcing outcome" below.

## Datasheet values

| Property | Value |
|---|---|
| Windings | N1 : N2 : N3 : N4 : N5 = 4 : 4 : 4 : 4 : 4 |
| Inductance | 100 µH ± 20 % (N1+N2, 10 kHz/1 V) |
| DCR | N1, N2 6.5 mΩ; N3, N4 10.5 mΩ; N5 120 mΩ (max, 20 °C) |
| Volt-second | 240 Vµs, N1+N2, bipolar |
| Leakage | 400 nH max (N1+N2, 100 kHz/100 mV) |
| Insulation | 2250 V DC, N1, N2, N5 ⇒ N3, N4 |
| Typical application | Forward, 40–57 V in, 24 V / 3 A out, 12 V aux, 200–700 kHz, input N1+N2, output N3+N4, aux N5 |
| Temperature | −40 to +125 °C |
| MSL | 1 |

Primary side = N1, N2, N5; secondary side = N3, N4 (from the insulation-test line).

## Configuration for 48 V

| Option | Pri : Sec | D at 42 V | Verdict |
|---|---|---|---|
| Datasheet wiring N1+N2 : N3+N4 | 8 : 8 (1:1) | 48.8/(1×41.7) > 1 | impossible |
| N1‖N2 : N3+N4 | **4 : 8 (1:2)** | 0.575 | **used** |
| N1‖N2 : N3+N4+N5 | 4 : 12 | — | N5 has primary-side insulation; not allowed on the secondary |

Consequences of 4-turn primary (all computed in `B-converter-design.md`):
- Lm = 25 µH (±20 %); magnetizing ripple 1.32 A p-p at 737 kHz (constant over line).
- Volt-second rating on 4 T = 120 Vµs at 20 °C (datasheet test condition); **≈ 90 Vµs assumed at
  100 °C** (MnZn Bsat −20…−25 %). Review M3: at 400 kHz the worst corner (57 V, DMAX 0.74,
  fsw −10 %) was 117 Vµs, 98 % cold and over the hot rating. fsw went to 620 kHz, then (amp beat rule)
  to **737.28 kHz, crystal-synchronised**: worst corner 57 × 0.73/737 kHz = 56 Vµs → 47 % cold,
  ≈ 63 % hot; clock-failed fallback 72 Vµs (60 % / ≈ 80 %); steady 33 Vµs. The off-the-shelf part is
  now safe unless Würth's hot rating is below ≈ 72 Vµs on 4 T (`B-converter-design.md`).
- Core loss: Bpk 68 mT at 737 kHz, estimated ≈ 0.84 W (≈ 0.7 W in PMP20878 at 200 kHz on 8 T).
- **737 kHz is 5 % above Würth's 200–700 kHz typical application range** for this part. That is
  not a stated limit; it is asked in the email.
- Winding pins (datasheet p.1 land pattern, review n6): N1 2(dot)–4, N2 3(dot)–5 → parallel 2+3 and
  4+5; N3 7(dot)–10, N4 8(dot)–11 → series by linking 10–8, output on 7 and 11; N5 1(dot)–6.
  Primary pads 1–6 and secondary pads 7–11 are ≈ 18 mm apart edge to edge.
- Copper is lightly loaded: primary 2.0 A rms through 3.25 mΩ, secondary 0.95 A rms through 21 mΩ
  (PMP20878 ran 3 A through the same secondary). Winding loss ≈ 0.1 W.
- Paralleled N1‖N2: identical 4-turn windings on one core (the datasheet already series-connects
  them as one primary, so they are wound together). Connect them at the pins with equal-length,
  wide copper so they share current; any imbalance only adds a few mW.

## Isolation (R-32)

The datasheet gives 2250 V DC primary ⇒ secondary (TI's PMP20878, rated "1500 VRMS isolated",
uses this part). R-32 asks 1500 Vrms 60 s; IEEE 802.3 is understood to accept 2250 V DC as the DC
equivalent of that test, **but this was not checked against the standard text in this audit**
(block A and the reviewer: confirm against 802.3 clause 145 isolation). The datasheet does not state
the duration either: ask Würth to confirm 60 s, or hipot the finished board. **Open item.** Creepage/clearance across the footprint feed the phase 4 barrier keepout.

## ±15 V auxiliary winding (R-33a question)

Not possible with this part: N3 and N4 are both needed in series for 48 V, and the only spare
winding (N5) is insulated as a primary winding. Even with a custom part, a forward-converter
auxiliary output needs its own rectifiers and output inductor per rail and cross-regulates with
load (its voltage tracks Vin·D, held only by the 48 V loop). **Recommendation to block C: do not use a
transformer winding; derive ±15 V on the secondary from VBUS (or 5 V) and post-regulate.**

N5 use: leave open, or use as a primary-side sense winding (its forward voltage is Vin on 4 T).
It is **not** used for VDD bias: on a 4-turn primary its voltage is ≈ Vin (42–57 V), and a linear
drop to 12 V would waste 0.6–0.9 W. Primary bias comes from a small buck (`B-bias.md`).

## Sourcing outcome (searched 2026-11-07)

LCSC (`jlc_parts.py search`) terms tried: PoE transformer, PoE++ transformer, forward transformer,
active clamp transformer, transformer 48V, PoE 60W/90W, planar transformer, SMPS/switching
transformer, Würth 7508/750313/750315/750316/750317/750318/750319/750341/750342/750343/750370/
750811/749196 series, 7503435xx–7503439xx, Coilcraft POE13/POE70/POE120/POE300/POE40Q/POE51Q/
POE71F/POExxPR, Pulse PA2467 and PA-series, Bourns POE0xx and transformer, Sumida, TDK, Sunlord,
Mentech, YDS, XR and CND-tek EFD20/EFD25/EP13/ER/PQ cores.

| Candidate | Type | Fits 48 V forward? | LCSC stock | Datasheet read |
|---|---|---|---|---|
| **Würth 750343576** | ACF 24 V/3 A, 4:4:4:4:4 | **yes, rewired 1:2** | none | we-750343576.pdf |
| Würth 750321159 / 750321158 | CCM **flyback**, 48 V / 1.45 A, 0.5:1:0.25, 15.5 µH gapped | no (gapped, forward needs high Lm); yes for an active-clamp *flyback* | none | we-750321159.pdf |
| Würth 750320237 | forward 24 V / 2.5 A (60 W), 2:2:1, EFD20, Isat 1.8 A | no (best step-up is 1:1) | none | we-750320237.pdf |
| Würth 750341794, 750343164, 750316336, 750319032 | forward/flyback 5–12 V | no (step-down) | 0 | fetched |
| Coilcraft POE70PR-50ED | forward 70 W, 1:0.25:0.25 | no (step-down; series secs 1:0.5) | 10 | coilcraft-poe70pr.pdf |
| Coilcraft POE72PR-12ED | forward 72 W, 1:0.583:0.583 | no (1:1.17 series) | not listed | same doc |
| Coilcraft POE120PL-24L | planar ACF 120 W 1:1:0.5 | no (no 48 V version; "factory order only") | 0 | fetched, not kept |
| Coilcraft POE71F-48 | flyback 48 V 71 W | no (flyback) | 0 | web listing only |
| Bourns POE060-FD20120S | forward 60 W 12 V, 1.71:1 | no | 3 | bourns-poe060.pdf |
| Pulse PA2467NL | flyback 12 V | no | 106 | pulse-pa2467nl.pdf |
| Würth 750343725, 750313626 | push-pull 1:3.9 / 1:2, 9–10 Vµs | no (≈1 W) | 435 / 122 | fetched |
| Würth 749196108 | 6 × 1:1, 0.5 A, 49 Vµs | no (power) | 80 | fetched |
| XR XREFD20-S251004, CND-tek EFD2053S-12 | customer-specific flyback, 1 kV hipot | no | 88 / 59 | fetched |

Reference designs: TI PMP20878 (TPS2373-4 + UCC2897A, 72 W, 24 V) uses 750343576; TI TIDT301
(TPS2373-4 + UCC2897A, 71 W ACF, 5 V) and TPS2373-4EVM-758 are 5 V; PMP23365 is 24 V/3 A with
TPS23730; Maxim MAXREFDES1273 is the only 48 V-output ACF found (802.3at, 41 W, MAX5974C) and uses a
custom EFD20 16 T : 32 T transformer. **No 48 V-output, ≈ 70 W forward transformer exists off the
shelf.**

### Options for the user

| # | Option | Efficiency (est.) | Effort / risk |
|---|---|---|---|
| **A (recommended)** | 750343576 rewired 1:2 at 737 kHz, bought from Würth/Digi-Key/Mouser and hand-soldered | ≈ 93 % (91–93.5 %) | proven 72 W part in a TI design; core loss unverified at this flux/frequency; stock unconfirmed (Würth samples are free in small numbers) |
| B | Custom Würth Midcom (or Coilcraft) part on the same ER core: 8 T : 16 T + spare winding | ≈ 94 % | custom lead time (weeks), NRE possible; best long-term part, and the route to production |
| C | Two 750343576 with primaries in parallel (8 T each) and secondaries in series (16 T total), 1:2, at 300 kHz | ≈ 93 % | twice the area and hand-soldering; each core carries half the power |
| D | Hand-wound on an LCSC ferrite core/bobbin (EFD25/ER25) with triple-insulated secondary | ≈ 93 % | 1500 Vrms by construction is on us; repeatability across 5 boards |
| E | Change topology to active-clamp flyback with Würth 750321159 (48 V/1.45 A, made for this) on the same UCC2897A | ≈ 90–91 % | contradicts R-02 / R-33 (ACF); higher bulk and SR ripple; still not on LCSC |

Recommendation: **A for this spin, with B started in parallel** if the board is meant to sell
(R-01). Ask Würth Midcom for samples of 750343576 now (and a quote for B).

**User decision (2026-11-07): A for this spin, B quoted in parallel. 92 % efficiency becomes
"verify at bring-up"; 91 % is acceptable.**

## Request to Würth (paste into an email to Würth Elektronik Midcom, midcom@we-online.com)

> Subject: Samples of 750343576 and quote for a custom 48 V-output variant (PoE++ active-clamp forward)
>
> Hello,
>
> We are building an IEEE 802.3bt Class 8 powered device (TI TPS2373-4 PD + UCC2897A active-clamp
> forward controller, the same pair as TI reference design PMP20878, which uses your 750343576).
> Our output is 48 V rather than 24 V.
>
> **1. Samples:** please send at least **7 pcs of 750343576** (5 prototype boards plus spares), and
> please confirm:
> (a) the duration of the 2250 V DC insulation test (we need 60 s, IEEE 802.3 isolation);
> (b) the **core material, Ae, Ve and le**, and the **saturation flux density Bsat at 100 °C** (and at
>     25 °C) for that material;
> (c) how the 240 Vµs "bipolar" volt-second rating is defined (peak-to-peak flux swing? at which
>     temperature and which B?), and the volt-second limit on N1+N2 at 100 °C and 125 °C;
> (d) core loss data for the material at 600 kHz and 50–100 mT, or the expected core loss in our use;
> (e) whether the part is stocked or made to order, with lead time.
> We will connect it N1‖N2 : N3+N4 (1:2) at 737 kHz (crystal-synchronised), so the 4-turn primary
> sees up to 57 V × 0.73 / 737 kHz = 56 Vµs (72 Vµs if our clock fails and the controller free-runs
> at 590 kHz). Please confirm (f) that operation at 737 kHz is acceptable (your typical application
> lists 200–700 kHz), (g) that those volt-seconds are within the part's hot rating, and (h) that
> paralleling N1 and N2 is acceptable for this construction.
>
> **2. Quote for a custom part:** a pin-compatible variant of 750343576 for a 48 V output, ideally
> on the same ER19/4.8/15 core and footprint, so it drops onto the same PCB:
>
> | Item | Requirement |
> |---|---|
> | Topology | Active-clamp forward, low-side P-channel clamp, peak-current mode |
> | Input | 36–57 V DC (PoE), max duty 0.73 |
> | Output | 48 V, 1.5 A (72 W); synchronous rectification |
> | Switching frequency | 737 kHz (crystal-synchronised; fallback 590–710 kHz free-running) |
> | Windings, same pins as 750343576 | **N1 = N2 = 8 T** (paralleled by us → 8 T primary); **N3 = N4 = 8 T** (in series by us → 16 T secondary); **N5 = 2 T** primary-side bias winding (forward-mode: 10.5–14.3 V at 50 mA) |
> | Turns ratio | Np : Ns : Naux = 8 : 16 : 2 |
> | Primary inductance | ≥ 100 µH (8 T), ±20 % |
> | Leakage inductance | ≤ 0.4 µH, primary with secondary shorted |
> | Volt-seconds | ≥ 130 Vµs on the 8 T primary at 125 °C, without saturation (57 V × 0.74 / 360 kHz = 117 Vµs worst case at 400 kHz − 10 %) |
> | Currents | primary 2.0 A rms / 5.0 A peak; secondary 1.0 A rms / 2.5 A peak; aux 50 mA |
> | Wire | your choice (stranded / Litz on the primary preferred at 737 kHz); copper loss target ≤ 0.2 W |
> | Insulation | 1500 Vrms 60 s (or 2250 V DC 60 s) from N1, N2, N5 to N3, N4 (IEEE 802.3 PoE isolation); 500 Vrms N5 to N1/N2 is not needed (same side) |
> | Thermal | 55 °C ambient at full load, temperature rise ≤ 40 K; operating −40…+125 °C |
> | Losses | total ≤ 1.0 W at 72 W, 50 V input |
> | Mounting | SMD, reflow-compatible, MSL 1; land pattern of 750343576 if at all possible |
> | Quantities | 10 samples; price for 100 and 1000 pcs; NRE if any |
>
> Thank you.

Notes for us (not part of the email): with a 2-turn aux on an 8-turn primary, N5 gives Vin/4 =
10.5–14.3 V, inside UCC2897A VDD (8.5–16 V) and TPS2373 VC_IN (≤ 15 V), so the custom part could
replace the primary LM5019 (keep its footprint for the 750343576 build). With 8 T on the primary
the flux per turn halves: at 400 kHz the estimated core loss is ≈ 0.6 W (efficiency ≈ 94 %), and the
volt-second margin is twice that of the 750343576 build.

## Layout guidance (feeds phase 4/6)

- N1 and N2 paralleled with short, symmetric copper at the pins; primary loop (VPRI ceramics → T1
  → main FET → Rcs → RTN) as small as possible.
- Secondary loop (T1 → forward SR → GND → freewheel SR → T1) minimal; SR snubbers at the SR pins.
- The transformer straddles the isolation keepout; nothing else crosses except the opto, the Y-cap
  and block A's digital isolator (R-32).
- Mechanically secure (adhesive) per R-41; it is ≈ 11 g class (PMP photo), SMD.

## Open questions

1. Distributor stock and lead time for 750343576 (findchips shows none). User to request samples.
2. Hipot duration of the 2250 V DC rating (60 s?), for R-32.
3. Core material, Ae/Ve and Bsat(100 °C): decide whether the 750343576 is safe at 57 V hot
   (review M3); asked in the email above. Measure ΔT and run the forced-DMAX test at bring-up.
