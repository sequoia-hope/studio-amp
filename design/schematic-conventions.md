# Schematic conventions — satellite variant A (phase 2)

Every block's sheet follows these rules so the 13 sheets read as one schematic. They come from the
skill (`.claude/skills/pcb-design/references/schematic-style.md`, `tools/kicad.md`,
`LESSONS.md`); read those first.

## Files and generators

- KiCad project: `hw/satellite/a/satellite.kicad_pro`, root `satellite.kicad_sch` (written by
  `gen/root.py`; don't edit it).
- **One generator per sheet:** `hw/satellite/a/gen/<sheet>.py`, built on `gen/hier.py`
  (`hier.SubSheet("<sheet>")`), which wraps the skill's `kicad_write.Schematic`. Run it from the repo
  root: `python3 hw/satellite/a/gen/<sheet>.py`. It writes `hw/satellite/a/<sheet>.kicad_sch`.
  Don't hand-edit the `.kicad_sch`; change the generator and re-run.
- Sheets and owners (from `gen/hier.py` SHEETS):

| Sheet | Block | Reference range |
|---|---|---|
| poe_in | A | 100–199 |
| iso_dcdc | B | 200–249 |
| iso_aux (sync clock, VBUS droop) | B | 250–299 |
| rails | C | 300–399 |
| amp_woofer | D | 400–499 |
| amp_tweeter | D | 500–599 (same generator as woofer, parameterised) |
| amp_sense (VBUS/current/NTC ADCs, VBUS TVS if not per bridge) | D | 600–699 |
| mcu | E | 700–799 |
| fpga | E | 800–899 |
| ethernet (PHY, 50 MHz, VCXO, clock buffer if E's) | E | 900–999 |
| audio_out | F | 1000–1099 |
| audio_in | F | 1100–1199 |
| io (USB-C, Qwiic, LED, display, knob, debug, JTAG, test points) | G (block C/G agent) | 1200–1299 |

  References are per type within the range: R101, R102 …, C101 …, U101 …, Q101 …, D101 …, J101 ….
  Power-symbol references are allocated by `hier` automatically.
- If a block needs more room than one A3 sheet, use A2 (`SubSheet(name, paper="A2")`) rather than
  cramming. Ask the lead before adding a sheet.

## Symbols and footprints

- Use KiCad's own symbol where one exists and its pin arrangement reads well. Otherwise make a
  project symbol in **your block's library only**: `hw/satellite/a/lib/studio_<X>.kicad_sym`
  (A–G; block C/G uses `studio_C` and `studio_G`). Pins by function, not package number: inputs and
  control on the left, outputs on the right, power on top, ground on the bottom. Split big parts
  (ECP5, RP2350B) into units by function. Every pin number and electrical type must be taken from
  the datasheet in `design/datasheets/` (cite the page in the audit).
- Footprints: KiCad's own where the land pattern matches the exact MPN's package drawing; otherwise
  make one in `hw/satellite/a/lib/studio_<X>.pretty` from the datasheet's recommended land pattern,
  and say so in the part audit. A footprint you make must have its pad numbers matching the symbol.
  3D models are optional.
- Every placed part has these fields: **Value** (meaningful, e.g. `100n 100V X7R 0805`, `LMG1210`),
  **Footprint**, **MPN**, **Manufacturer**, **LCSC** (the C-number from the audit; for a part bought
  outside LCSC, `LCSC` = `HAND` plus a `Supplier` field, e.g. `Würth direct`). Decoupling caps also
  get **Decouples** = `U301.5` (reference.pin they serve). DNP parts are `dnp=True` with a note.
- The values, MPNs and LCSC numbers come from your block's audits in `design/parts/`, which are the
  source of truth until the schematic exists; from then on the schematic is. If drawing a sheet shows
  that an audit is wrong, fix the audit too, and say so in your report.

## Drawing

- 1.27 mm grid; put symbol origins on multiples of 2.54 mm so every pin lands on the grid.
- Signal flow left to right; higher voltage at the top, ground at the bottom; power symbols point up,
  ground symbols point down.
- Wires within a block. Local labels only to avoid a wire crossing the page. Supporting parts next to
  the pin they serve: decoupling at the power pin, pull-ups at the pin, divider at FB, crystal at its
  pins. Group sub-blocks with `box()` and a title ("FORWARD SR, NCP4306").
- Never place symbols in a loop with a fixed step (that is the grid look the style check fails).
- Annotate with `text()`: layout-critical notes ("≤ 1 nH loop: C412–Q401–Q402"), why a value is what
  it is (with the audit file), DNP/jumper options, test points, rail voltage and current at sources.
- **Isolation:** primary-side nets (`VPRI`, `VPRI_RTN`, `VB_PRI` and the like) get their own ground
  symbol, `VPRI_RTN`, never `GND`. Draw the barrier as a dashed line on the sheets that cross it.

## Nets

- Rails are power symbols, named as in `design/architecture.md` (reconciliation section): `VBUS`,
  `+5V_BUCK`, `+5V`, `VUSB`, `+3V3`, `+3V3_Q`, `+3V3_A`, `+2V5`, `+1V1`, `+15V`, `-15V`, `+5V_A`,
  `VDRV`, `GND`; primary `VPRI`, `VPRI_RTN`, `VB_PRI`, and any block-local rail. Use
  `power:<std>` where the name matches, else `power:VCC` / `power:GND` with `value=` set to the net
  name (`sch.power("power:VCC", at, value="VBUS")`).
- **Inter-sheet signals are global labels** (`kind="global_label"`) with the exact names in the
  `*-interfaces.md` files and `E-pinmap.md` (FPGA and RP2350 pins). A global label must appear on at
  least two sheets. Every global label you use goes in `hw/satellite/a/gen/labels_<sheet>.txt`, one
  name per line with its direction (`in`/`out`/`bidir`) as seen from your sheet, so the lead can
  cross-check both ends.
- Name every net that leaves a block or matters for layout (`SW_W_A`, `VDRV`, `BST_W_A`, `FB_5V`).
  These names feed `nets.csv` in phase 3.

## Checks before reporting

From the repo root:

```sh
python3 hw/satellite/a/gen/<sheet>.py
kicad-cli sch erc --severity-all -o /tmp/<sheet>-erc.rpt hw/satellite/a/satellite.kicad_sch
python3 .claude/skills/pcb-design/scripts/schematic_style_check.py hw/satellite/a
kicad-cli sch export pdf -o /tmp/<sheet>.pdf hw/satellite/a/satellite.kicad_sch
```

ERC runs on the whole project, so other sheets' issues will show up too: fix only yours, and leave
expected cross-sheet ones (a global label whose other end isn't drawn yet) for the lead. Render your
page to PNG (`pdftoppm -f <page> -l <page> -r 80 -png`) and **look at it** before reporting. Fix
overlaps, cramped areas and anything that reads like a list instead of a circuit.

No `rm -rf` or wildcard deletes; no git commits; write only your own generator(s), your own
`labels_<sheet>.txt`, your own `lib/studio_<X>.*` and your own `design/parts/<X>-*.md` audits.
