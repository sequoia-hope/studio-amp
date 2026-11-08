# Gate 1 — architecture and parts

Board: satellite, variant A. Status: **PASSED 2026-11-08** (independent review, four passes; no user
sign-off required for this gate).

Artifacts: `design/architecture.md` (block diagram, "Phase 1 reconciliation" and frequency plan),
`design/parts/` (92 audit files across blocks A–G, with the superseded Gowin and IGC033/pulse-detector
material kept and marked), `design/datasheets/sources.csv` (253 datasheets, all read),
`design/decisions.md`.

## Checklist

| Item | Evidence | Result |
|---|---|---|
| Block diagram exists and every block maps to parts | `architecture.md` mermaid diagram plus a block table; reconciliation section lists the chosen parts per block | ✓ |
| Every non-trivial part has an audit with its datasheet in `datasheets/` | 92 files in `design/parts/`; `sources.csv` has 253 rows, 0 listed files missing on disk. One unlisted PDF (`sctf-sx3m-7m3728.pdf`) belongs to a crystal that was replaced, not used | ✓ |
| Every abs max checked against the worst case from `intent.md` | per-part abs-max tables; VBUS parts re-checked against the 82.4 V TVS clamp plus overshoot (C-interfaces, D-vbus-tvs); PoE input against 57 V plus SMCJ58A clamp (A-tvs) | ✓ |
| Every chosen value has a shown calculation | each audit's "Calculations" section, recomputed independently by the reviewers (below) | ✓ |
| MLCC derating checked | per audit; makers' DC-bias curves are not yet in hand for several Samsung/Murata parts, so those figures are stated assumptions (open item, below) | ✓ with open item |
| Footprint matches the exact package suffix | checked per part by the first-pass reviewers ("all packages match MPN suffixes", reviews A, B, D, E, F) | ✓ |
| Sourcing confirmed with `jlc_parts.py show` and date | sweep below | ✓ |
| Every datasheet listed in `sources.csv` | merged from `sources-{A,B,CG,D,E,F}.csv` | ✓ |
| Independent reviewer re-read each datasheet and recomputed each calculation | reviews below | ✓ |

### Sourcing sweep (2026-11-08)

`jlc_parts.py show` over every LCSC number named in `design/parts/*.md` (285 numbers, chosen parts
and rejected alternatives alike): 277 lifecycle `normal` with stock. The 11 flagged lines are all
rejected alternatives or alternates, and none is a chosen part:

```
C160403 SM03B-SRSS-TB (JST): stock 0            → G-debug-jtag: genuine JST rejected, clone C2763613 used
C2867155 TLV75525PDBVR: stock 0                 → C-2v5-ldo: rejected, TPS7A9401 used
C2869949 TPS7A2025PDBVR: stock 0                → C-2v5-ldo: rejected
C49274913 / C52740984 / C54350158 / C54350159 / C55014508  (Innoscience, lifecycle unknown) → D-gan-fet: rejected
C5155055 Würth 7447709680: stock 68, unknown    → B-output: alternate only; Sumida CDRH127 used
C5521506: lifecycle unknown                     → B-bias: alternate only
C6909259 MMICT5837: lifecycle unknown           → F-mems: rejected, T3902 C3171752 used
```

Thin stock on chosen parts (order early): IGB070S10S1 (80 for 44), SER2915H (63 for 22),
PSSCAQ7048M-680M (932, single source), LT4321 (52 + 46), LPJK6078AHNL (58). Bought outside LCSC:
Würth 750343576 transformer (samples requested by the user).

## Independent reviews

Fresh-context reviewers on the stronger model, given only the artifacts and the checklist:

| Pass | Scope | File | Result |
|---|---|---|---|
| 1 | A, B, C+G, D, E, F (six reviewers) | `review-phase1-{A,B,CG,D,E,F}.md` | 5 BLOCKER, 18 MAJOR in total; every one fixed or disputed by the block owner ("Review response" in each `*-interfaces.md`) |
| 2 | A+B, C+G+D, E+F (three reviewers) | `rereview-phase1-{AB,CGD,EF}.md` | first-pass items CLOSED except CG-M2; new: 1 BLOCKER and 3 MAJOR in B's new circuits (PoE-loss pulse detector, sync clock, ACF_PULSE), 1 MAJOR in G |
| 3 | B's new circuits, PoE-loss coverage, G, C retiming | `rereview2-phase1.md` | 1 BLOCKER (pulse detector race), 2 MAJOR (coverage hole, VREF budget). Lead decision: pulse detector retired, VBUS-droop comparator plus ADC rule |
| 4 | droop comparator, coverage end to end, sync supply, clock-fault rule, Fly-Buck | `rereview3-phase1.md` | all CLOSED except MAJOR-1 (LM393 VOL against AO3400A Vth, hot); fixed (2N7002 with gate divider) and verified in the same file's "Fix verification": **phase 1 passes** |

Highlights of what the reviews changed: the ECP5 PG and strap deadlocks against its default
pull-downs; relay drive at a 3 V gate; the headphone short-circuit thermal; X7R out of the mic path;
the bootstrap at the duty clamp; a hard-short detector; the converter loop gain, bias UVLO,
volt-seconds, SR clamps and start-up current; the hipot through the magjack; PD_PG_N polarity;
the ECP5 gearing margin; the frequency plan (amp 576 kHz, converter crystal-locked at 737.28 kHz);
and PoE-loss detection by VBUS droop.

## User decisions taken in this phase

All in `decisions.md`: LMG1210 gate driver; ECP5 LFE5U-25F (debugger-free loading from the RP2350);
6 layers; the Würth transformer with a custom part quoted in parallel; 92 % efficiency verified on the
bench; IGB070S10S1 GaN (after IGC033 at 576 kHz); 1.695 ns edge grid; polypropylene tweeter cap; Qwiic
capped at 100 mA; the 6.35 mm jack waiver; shared headphone/line DAC path; LED connector order.

## Open items carried forward (none blocks phase 2)

- MLCC DC-bias figures for parts without maker curves: assumptions until the curves are read (phase 2
  part placement can proceed; values are re-checked when the schematic fixes each part).
- Würth data: Bsat at 100 °C, Ae, and operation at 737 kHz. If Bsat is below ≈ 80 V·µs on the 4-turn
  primary, the custom transformer becomes required.
- Measured at bring-up: transformer core loss and efficiency, the VCXO's jitter (DAC noise floor), the
  INA241 blanking case, SER2915H core loss, bootstrap at a 20 Hz full-scale tone, the VREF clock-chain
  current, and PSE start-up on Type 2 and Class 6.
- Phase 4/6 obligations: power loop ≤ 1 nH by extraction; IGC033 courtyard reserved at each GaN site;
  ≥ 2 cm² of copper on each BCP56/53 tab; back-panel heat path for the GaN; the MEMS mic vent; the
  isolation keepout; trace from the 5 V buck to the mux ≤ 10 mΩ.
- Display module pin order (user, when the module arrives).
