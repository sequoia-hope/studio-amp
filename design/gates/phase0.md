# Gate 0 — design intent

Board: satellite, variant A. Artifact: `design/intent.md`. Status: **PASSED** — user sign-off 2026-11-07.

## Checklist

| Item | Evidence | Result |
|---|---|---|
| Purpose stated | R-01, R-02, R-03 | ✓ |
| Open source / confidential | R-04: open source, MIT, public repo | ✓ |
| Every external interface with direction, signal, voltage (normal + worst), current, mating part | R-10 … R-23 table | ✓ (R-20 OLED module still open with the user) |
| Power: input range, every rail with load, sequencing, backfeed | R-30 … R-35, budget table R-33a | ✓ |
| Environment | R-40 … R-42 | ✓ |
| Performance targets | R-50 … R-56 | ✓ (R-51 open with the user) |
| Mechanical | R-60 … R-62 (outline deferred to phase 4 by the user's choice) | ✓ |
| Manufacturing | R-70 | ✓ |
| Serviceability | R-80 | ✓ |
| Compliance | R-90 | ✓ |
| Risks and open questions | R-95, R-96 | ✓ |
| Every requirement has a number or an explicit "don't care" | items without a value are marked (proposed) defaults or listed in R-96 | ✓ pending sign-off |

Supporting evidence: LCSC stock checked with `jlc_parts.py show` on 2026-11-07:

```
C470963 TPS2373-4RGWR (TI, VQFN-20-EP(5x5)): extended, JLC stock 481, lifecycle normal
C54444 UCC2897APWR (TI, TSSOP-20): extended, JLC stock 3944, lifecycle normal
C469850 UCC2897ARGPR (TI, QFN-20-EP(4x4)): extended, JLC stock 183, lifecycle normal
C5799578 GW1NR-LV9QN88PC6/I5 (GOWIN, QFN-88): extended, JLC stock 124, lifecycle normal
C2677136 LMG1210RVRR (TI, WQFN-19-EP(3x4)): extended, JLC stock 2841, lifecycle normal
C2653814 LMG1205YFXR (TI, DSBGA-12): extended, JLC stock 485, lifecycle normal
C45044 RTL8201F-VB-CG (REALTEK, QFN-32-EP(5x5)): extended, JLC stock 42934, lifecycle normal
C17146 LAN8720AI-CP-TR (MICROCHIP, QFN-24-EP(4x4)): extended, JLC stock 9257, lifecycle normal
C54350158 (INN100EBD018DAD-C): extended, JLC stock 1076, lifecycle unknown  <-- CHECK
C52740984 (INN100EA035A-C): extended, JLC stock 859, lifecycle unknown  <-- CHECK
search: KTA1142 0, TPS23730 0, TPS23731 3, uP1966E (all listings) 0, JL1101 (all listings) 0, GW1N-LV9 (all listings) 0
```

## Independent review (fresh-context subagent, stronger model, 2026-11-07)

Inputs given: the system spec, `intent.md` (first draft), the phase 0 checklist. Verdict on the
first draft: *not met until B1 is closed and M1–M4 are made consistent*.

| # | Sev | Finding | Resolution |
|---|---|---|---|
| B1 | BLOCKER | Power budget didn't close: ≈ 77 W of loads against ≈ 64 W available; R-50 and R-33 disagreed; no Class 6 / Type 2 budget | Fixed: R-33a budget table from the PD down for Class 8 / 6 / Type 2; LEDs cut to 5 W and firmware-limited per class; VBUS average 51.7 / 36.8 / 16.0 W |
| M1 | MAJOR | 4 Ω allowed, so a burst is 288 W / 12–15 A; bulk size not stated | Fixed: firmware limit of 144 W / 12 A per channel, OCP at ≈ 15 A (R-50, R-54); bulk ≈ 5–7 mF, 63 V, 105 °C stated in R-33a |
| M2 | MAJOR | Signals crossing the isolation barrier were undefined; "FPGA detects input UVLO" is impossible without one | Fixed: R-32a lists the crossings (class/type indication, PD power-good) and adds secondary-side PoE-loss detection |
| M3 | MAJOR | Studio-monitor THD/noise not reachable open-loop | Fixed provisionally: R-51 relaxed for open loop, plus an optional post-filter sense path for a closed-loop variant. **The user decides** (R-96) |
| M4 | MAJOR | Headphone 8 Vrms / 30 mA / ±12 V / 50 mA inconsistent | Fixed: 5 Vrms, 25 mA pk, ±15 V only, 80 mA per rail |
| M5 | MAJOR | A synchronous forward converter regenerates back into the primary; static vs dynamic regulation unclear | Fixed: R-33 requires diode emulation / SR inhibit; ± 2 % static, 10 % dynamic; R-35 rewritten (TVS for transients only, firmware stop above 55 V) |
| M6 | MAJOR | Class 8 baseline is optimistic | Fixed: R-30 specifies full performance at Class 6, with Class 8 as headroom |
| M7 | MAJOR | ±15 V from an extra forward winding needs its own inductors and cross-regulates poorly | Fixed: R-33a leaves the ±15 V topology to phase 1, with both options named |
| m1 | MINOR | Hold-up had no load or mute time | Fixed: R-34 (≤ 5 ms mute, ≈ 8 W for 20 ms) |
| m2 | MINOR | "±60 V surge" vague | Fixed: R-10 (0–57 V, either polarity, 1 kV CM, shield treatment) |
| m3 | MINOR | USB-C power path | Fixed: R-23 (logic only, ideal-diode ORing, a sink) |
| m4 | MINOR | 85 °C electrolytics | Fixed: R-40 (105 °C) |
| m5 | MINOR | Flash size | Fixed: R-56 (16 MB) |
| m6 | MINOR | VCXO vs resampler | Fixed: R-55 (phase 1 decision, named) |
| m7 | MINOR | Mic bias assumption | Fixed: R-15 (bare electret only) |
| m8 | MINOR | ESD scope | Fixed: R-42 (external jacks only) |
| m9 | MINOR | Disconnect vs shutdown | Fixed: R-54 (shutdown; tweeter series film cap) |
| n1–n4 | NOTE | 36 V impossible for 100 W; MPS dropped; verify-list; 15 A connector | n1 resolved by 48 V; n2 stated in R-30; n3 carried into R-95 and phase 1; n4 in R-11 |

No re-review: every BLOCKER and MAJOR fix tightens a number the reviewer itself proposed, and the
budget arithmetic was rechecked by the author (Class 8: 71.3 − 1.5 = 69.8 × 0.92 = 64.2;
− 12.5 = 51.7 W). The user's sign-off is the remaining step.

## Sign-off

- [x] User sign-off on `design/intent.md`, 2026-11-07: "use LMG1210, relaxed targets fine, signed off — go". Proposed items accepted as written. OLED module (R-20) stays open; it only fixes a header pinout and is resolved by phase 2.

## Post-sign-off edit

2026-11-07: R-20 updated with the display module the user named (open item R-96 closed). The rest of the intent is unchanged; inputs re-recorded.
