# Phase 2 visual review — satellite variant A schematic

Date: 2026-11-08
Reviewer: independent visual pass (fresh context, authors' conversation not seen)
Inputs: `design/renders/sch/page-01.png … page-14.png` (A2/A3 at 110 dpi), `design/renders/schematic.pdf`.
Checklist: `.claude/skills/pcb-design/references/schematic-style.md` ("Visual review"), `design/schematic-conventions.md`.
Method: every page viewed whole, then cropped and enlarged (175–300 %) region by region.

## The six questions

1. **Can I follow the main power path from input connector to every load?**
   Mostly yes. J101 → bridges → TPS2373 → `VPRI` (p2) → T201 → SRs → L202 → `VBUS` (p3) → LM5013 `+5V_BUCK` → TPS2116 `+5V` → 3V3 / 1V1 / 2V5 / VDRV / ±15 V (p5) is traceable, and every regulator box names its source rail and output. Two gaps: the **root sheet (p1) shows no connections between sheets at all** (sheet symbols with no pins and no lines), so the only way to follow power across sheets is to know the rail names; and `VBUS` to the two bridges (p6, p7) is only a power symbol at C410/C408, with no "from iso_dcdc" note.
2. **Can I follow each signal from source to destination?**
   Within a sheet, yes; the signal boxes flow left to right and the global labels carry the `*-interfaces.md` names. Across sheets you have to search for the label name because the root sheet carries none. PWM → LMG1210 → GaN → LC → J401 reads cleanly; the PD-status → ISO7740 → FPGA path is traceable with long but tidy verticals on p2.
3. **Does any region look like a grid or a list rather than a circuit?**
   The root sheet is a 4 × 2 + 4 × 2 grid of boxes. Elsewhere the list look appears only where the circuit is literally a bank: the 6 + 6 VBUS caps (p3), the 7 × 100 n LC caps (p6/p7), the MCU/FPGA power units with cap rows (p9/p10), the 8-position display jumper matrix and the TP row (p14). Those are acceptable. The rails sheet (p5) is a 3 × 4 grid of regulator boxes, but each box is a drawn circuit; acceptable.
4. **Is every passive next to what it serves?**
   Almost everywhere: decoupling at pins, FB dividers at FB, bootstrap at BST, pull-ups at the pin. Exceptions: p12 draws two separate "74LVC74 SUPPLY" and "OP-AMP SUPPLIES" boxes (power units of multi-unit symbols, so defensible, but the style rule says no separate decoupling section); p8 puts the ADS7038 input RC filters 50 mm from the AIN pins; p14 USB-C CC resistors reached via `CC1`/`CC2` labels instead of a 10 mm wire.
5. **Is anything cramped, overlapping or hard to read?**
   Yes, and this is the main defect class. The A2 sheets at print scale have very small text, and in dense spots text sits on text or on wires: the whole rails sheet (p5), the CS/AUX/OUT corner of the UCC2897A (p3), the relay/ferrite corner of audio_out (p12), every DNP part whose red X is drawn over its own value, and most "power symbol + test-point + reference" clusters. Details below.
6. **Would a senior engineer be comfortable presenting this in a design review?**
   The block sheets, yes, after the text collisions are cleared; they read like a person drew them, with good boxes, annotations that cite the audits, and the isolation barrier drawn where it is crossed (p2, p3, p4). The root sheet, no: it is a table of contents, not a block diagram.

## Findings

### BLOCKER

None. Nothing is unreadable to the point of hiding a connection, and I found no wiring that is clearly wrong.

### MAJOR

- **M1 — p1 root sheet is a list of boxes, not a block diagram.** No hierarchical pins, no lines between sheets, boxes on a regular 4-column grid. The style rule asks for a top sheet "roughly matching the block diagram". Add at least the rails (`VPRI`, `VBUS`, `+5V`, `+3V3`, `VDRV`, `±15V`) and the main signal buses (PWM/FAULT, RMII, PIO link, DAC bits, PD status) as sheet pins with lines, in flow order left to right; or, if the generator can't do sheet pins, draw the block diagram as lines and text so the reader has the map. Also: the "Open source, MIT…" comment overlaps the title-block frame and runs past the right page edge (bottom right), and the "COMPUTE, NETWORK…" dashed box runs under the title block.
- **M2 — p5 rails: pervasive text-on-text.** Every regulator box has collisions at the same spots: input "VBUS / R3xx 0R 1206" ref over the power symbol (R301, R320, R339); output "+5V_BUCK / TP302 / TP +5V_BUCK", "+3V3 / TP304", "+1V1 / TP305", "+2V5 / TP306", "+3V3_Q / TP309", "+3V3_A / TP310" three strings in one spot; "+3V3 / PWR_FLAG / JP30x bridged" at the solder jumpers; value text ("LM5013", "TPS62A02A", "TPS7A2033P 3.3V", "TLV6703") drawn over GND/EP pins; R305/R306 "0.5 %" values over "FB_5V"; D301 "SS310" over the diode; "FB301 BLM18PG221" over the "+18V_PRE" power label (and FB302 / "−18V_PRE"); R313/R316 "100k 0.1 %" over PG pin 5; "L305 68u 1:1 PSSCA07048M" over GND/C345. Move refs/values off the pins and give each box 20–30 % more width; the sheet's lower 40 % is empty, so there is room.
- **M3 — DNP parts: the red X hides the value, everywhere.** p2 R113 "1.3k DNP" tangled with the UVLO_SEL no-connect; p3 R219 "0R 0603 DNP", C224 "2.2n Y2 DNP", C247 "1000u 63V KZN 105C DNP" over C246's text; p5 R346/C347 X's drawn across D302 and its wire; p6/p7 C401/C402/C412/R410 (and 5xx); p9 R706 X over the +3V3 power symbol; p11 R920; p13 R1110/C1116; p14 R1202 and the 4n7 2 kV cap at the USB shield — the reference under the X is not legible, so I cannot confirm it isn't a duplicate of C1202 (100 n at VUSB_DET). Place DNP values beside, not under, the body; confirm the shield cap's reference.
- **M4 — p3 iso_dcdc, UCC2897A OUT/AUX/CS corner (sheet column 4–5, row C).** R212, R213, R214, C204, R205, C208 and the vertical "CS_PRI" label are packed at 2.54 mm pitch with rotated values overlapping each other and the pin-9 wire; "C204 82p 50V C0G" is unreadable without zoom. Also in the feedback box: "D207 BAS316" drawn over U208 TL431B's body; R247/R248 vertical values overlap; "IBUS_F" label over R237's value. Spread the CS network to the right of the IC.
- **M5 — p12 audio_out, output relays box.** "FB1002 600R@100MHz" drawn over "D1015 1N4148WS"; K1001/K1002 pin names (COM1/COM2/NO1/NC1) drawn over the relay's coil/contact graphic; J1001 pin names "TN/RN" over their no-connect X's. In the headphone stage, "+15V" over "HPA_L" at R1057/D1008.
- **M6 — Connector pins without function text.** J401 (p6), J501 (p7) show pins "1, 2" only, with the function in a free-text note 10 mm away; J1205 LED (p14) pins "1–4" with the pin-out only in a note at the bottom of the box; J1208 display socket pins "1–8" (acceptable since each row is labelled DISP_Pn, but say "1 = GND default" etc.); J1202/J1203/J1204 are fine (the note gives the pin-out). The style rule asks for the function next to each pin so the schematic can be checked against a wiring diagram.

### MINOR

- p2 U101 LT4321 right-side pins: pin numbers "16/14/1/13/4/8/5/7" run into the TG/BG label text. Two pins both read "EN" (10 with overline, 11 without) — make the bar visible or rename `EN_N`.
- p2 uses the top 55 % of an A2; A3 would do and would double the print size. Same for p5 (60 %), p9 (55 %), p10 (65 %).
- p3 T201: "4T each" text overlaps pin 11; the pin 2 → pin 3 parallel-winding loop drawn around the `VPRI` symbol is confusing at a glance — state "N1 ∥ N2" at the symbol. "SW_SEC" label sits on the output-filter box border.
- p3 bias buck: "C216 1n 50V C0G 0603" over "PWR_FLAG" and its ref.
- p4: "C264 470p 50V C0G 0603" on the pin-2 wire of U255A; otherwise the cleanest sheet.
- p6/p7 LMG1210: "VDRV" power label over "GND" at C403; "D401 BAT46WJ" over the diode body; "OUT_W_A" label over "C423 100n 16V X7R" in the short detector; D405 BAT54S rotated pin names over the "VSDB_W" vertical label; U403/U407 TLV3502 pin names "+INA/−INA" cramped; "C420 100n 16V X7R" over "+3V3".
- p8: ADS7038 AIN0–AIN3 wires stair-step into the pins from a stack of parallel verticals; the 1 n filters are far from the pins. Move the RC to the pin side.
- p9: "POWER" unit name over the GND pin-81 name; `VREG_PGND` fine. Lower 45 % of sheet empty while the GPIO units are small.
- p10: unused-ball stacks (Bank 1 left, Bank 3 left/right, Bank 6) have ball names "E8 D8 B9 D9 …" overlapping their no-connect X's; "CORE POWER" unit name over the GND pin names. Readable only at 200 %.
- p11: Y902 VCXO symbol too small — "Vc / VDD / OUT / GND" pin names and the "VCXO" value overlap inside a 10 mm box.
- p12: separate "74LVC74 SUPPLY" and "OP-AMP SUPPLIES" boxes (style rule: decoupling at the IC). Acceptable for multi-unit symbols, but say so in a note or move the C units next to their A/B units. `FILT_L` is a global label while `FILT_R` is a local label in the same DC-detector box: correct (FILT_L goes to audio_in) but looks like an error — add a note.
- p12 HP stage: "R1058 … 0.1 %" over "C1016"; `-15V` power symbols on p13 (U1101C) point up under the V− pin while on p12 they point down — pick one.
- p14 USB-C: `CC1`/`CC2` labels where a short wire would do; "VUSB_DET" R1205/R1206 vertical values touch. Qwiic: "PWR_FLAG" over the "QWIIC_PU" label. Knob header J1206: 12 wires fanned as nested loops around the header; consider drawing the header vertically with the RC/ESD cells to its right.
- Rail current notes at the source are missing on `VBUS` (voltage only), `+5V_BUCK`, `+3V3`, `+1V1`, `+2V5`, `VDRV`, `±18V_PRE`, `+15V/−15V` (p3, p5). `VSR`, `VB_PRI`, `VISO_P5V`, `+5V_A` have them.
- Vertical (rotated) value text on every vertical resistor/cap across all sheets; it is KiCad-normal but with 0603/tolerance/voltage strings it is the main reason the A2 sheets need zoom.

### NOTE (electrical, seen in passing — not readability)

- p6/p7 U401/U405 (LMG1210): NC1 (pin 14) is wired to HS. Verify against the datasheet that this pin may be tied to HS; if it is a true NC, leave it open.
- p5 3V3_Q LDO: EN_UV is taken from `+15V` through R333/R334 (47k/10k). Matches the sequencing note ("+15V ≥ 7.1 V enables 3V3_Q"); flagging only because it is easy to misread as a wiring slip.
- p12 D1004/D1005 BAV99 pin 3 marked NC while pins 1–2 are used in series: fine, state "BAV99 as single series diode" if that is the intent.
- p2 ISO7740 EN2 (pin 10) tied to VCC2; GND1 pin 8 / GND2 pin 15 presence not legible at this scale — confirm both grounds are connected.
- p5 TPS62A02A 1V1 PG (pin 5) is a no-connect; 3V3's PG is used. Intentional per the sequencing note.
- p14 J1205 pin-out (1 = +5 V, 2 = GND, 3 = D, 4 = C) matches the wiring; no issue.

## Rating and verdict

**Rating: 7 / 10 for readability.** The block sheets are organised, annotated and drawn as circuits, with the barrier marked and the audits cited at the point of use. What drags the score down is mechanical: text collisions concentrated on the rails sheet, DNP crosses that hide their own values, a handful of cramped corners, and a root sheet that doesn't show how the sheets connect.

**Verdict: PASS WITH REQUIRED FIXES.** Fix M1–M6 and re-render before Gate 2; the MINOR items can be rolled into the same generator pass but should not block. Re-check with the style script after the fixes, since the text collisions it should catch (M2–M5) are present in this render.

## Re-check (2026-11-08, after owners' fixes and the redrawn root)

Re-rendered pages 1–14 viewed whole and in 175–250 % crops of every region named above.

### MAJOR

- **M1 root sheet — CLOSED.** p1 is now a block diagram: sheets in flow order inside two labelled regions, blue flow lines with labelled arrows (VPRI 42–57 V, VBUS 48 V, VBUS/VDRV, PD status, RMII + 50 MHz, PIO link, PWM/FAULT/ARM, 1-bit DAC, I2S mic/PDM, USB/SWD/I2C/LED/display), a one-line summary at the top and a note on where net names live. Title-block comment no longer overflows. Residual (MINOR): the "ETH pairs, LEDs" and "POE_LOSS_N, ACF_PULSE" lines run through the "COMPUTE, NETWORK, AUDIO AND I/O" region title; the "1-bit DAC, MCLK_Q, relays" arrowhead lands on audio_out's "File:" text.
- **M2 rails text-on-text — CLOSED.** All listed collisions cleared: TP/rail labels separated, IC values moved off GND/EP pins, FB bead values off the pre-rail labels, R305/R306 off FB_5V, L305 off GND/C345. Boxes widened; sheet now uses ~75 % of the A2 with a sequencing box. New small issues under NEW below.
- **M3 DNP values hidden — CLOSED.** DNP parts now carry their reference and value in grey beside the X on every sheet (R113, R219, C224, C247, R346/C347, C401/C402/C412/R410 and the 5xx twins, R706, R920, R1110/C1116, R1202, C1201). The USB shield cap is C1201 "4n7 2kV", distinct from C1202 — the duplicate concern is resolved.
- **M4 UCC2897A CS/AUX/OUT corner — CLOSED.** R212/R213/R214/C204/R205/C208 spread out, every value legible at 175 %; D207 sits beside U208, not over it; IBUS_F clear of R237.
- **M5 audio_out relay box — CLOSED.** FB1001/FB1002 clear of D1015; K1001/K1002 pin names outside the relay graphic; J1001 TN/RN X's clear. "+15V" and the rotated "HPA_L" label at R1057/D1008 still touch (MINOR).
- **M6 connector pin functions — CLOSED.** J401/J501 pins read OUT+/OUT−; J1205 pins read +5V/GND/D/C; J1208 has a default-function column (GND VCC SCL SDA RES DC CS BLK) beside the pins; J1206 pins named on the symbol; J1202/J1203/J1204/J1207 carry the pin-out in the box header.

### MINOR from the first pass

| Item | Status |
|---|---|
| p2 LT4321 pin numbers vs TG/BG text; two "EN" pins | CLOSED (clear; pins now EN_N / EN) |
| p2/p5/p9/p10 under-used A2 | NOT CLOSED, cosmetic — p9 (A3) still has an empty band between the POWER unit and the rest; p10 uses ~55 % |
| p3 T201 "4T each" on pin 11; N1∥N2 loop; SW_SEC on box border; C216 over PWR_FLAG | CLOSED (per-winding "N1 4T / N2 4T" + note "dots 2+3 → VPRI, 4+5 → SW_PRI") |
| p4 C264 value on wire | CLOSED |
| p6/p7 VDRV over GND at C403; D401 text on body; OUT_W_A over C423; BAT54S names over VSDB_W; TLV3502 names cramped; C420 over +3V3 | CLOSED (TLV3502 +INA/−INA still small but clear of wires) |
| p8 ADS7038 stair-step wires, filters far from pins | CLOSED (R/C now at each AIN pin, straight runs) |
| p9 POWER unit name over pin 81 | CLOSED |
| p10 unused-ball names over X's; CORE POWER over GND names | CLOSED |
| p11 Y902 VCXO symbol too small | CLOSED (larger symbol, names clear) |
| p12 separate supply boxes; FILT_L global vs FILT_R local | CLOSED by annotation (box header explains the power units and the Decouples field; DC-detector note explains FILT_L) |
| p12 R1058 over C1016; −15V symbol direction p12 vs p13 | CLOSED (negative rails consistently drawn arrow-up below the stage) |
| p14 CC1/CC2 labels instead of wires | NOT CLOSED — still labels at A5/B5 and at R1203/R1204 (10 mm apart); accept or wire |
| p14 PWR_FLAG over QWIIC_PU; R1205/R1206 touching; knob header fan-out | CLOSED (knob header redrawn vertically with one RC/ESD cell per row) |
| Rail V/I notes at sources | CLOSED (VBUS 47.9 V ≤ 1.30 A; +5V_BUCK 0.91 A; +3V3 0.79 A; +1V1 0.40 A; +2V5 50 mA; VDRV 200 mA; ±18V_PRE 135/110 mA; +15V 120 mA; −15V 110 mA; +3V3_Q 35 mA; +3V3_A 15 mA) |
| Rotated values on vertical passives | NOT CLOSED, inherent to KiCad; acceptable |

### NEW (introduced by the moves)

- **N1 (MINOR) p5 VDRV box, input:** the `VDRV_EN` global label is drawn over the "GND" text of C322/C323's ground symbols (left of R320). Drop the label one grid step.
- **N2 (MINOR) p5, all three VBUS-input cap banks** (C301–C303, C321–C323, C338–C340) and the R340/R341 pair: rotated values ("1u 100V", "2u2 100V", "100n 100V"; "124k 0805", "330k 0805") sit at 2.54 mm pitch and overlap each other. Legible at 250 %, not at print scale. Spread to 5.08 mm or put the values horizontal.
- **N3 (MINOR) p5 TPS2116:** "PG_5V" label text touches the R309 wire.
- **N4 (MINOR) p1:** flow lines through the lower region's title and an arrowhead on a "File:" string (see M1 residual).
- **N5 (NOTE) p6/p7:** LMG1210 NC1 (pin 14) is still wired to HS. Still needs a datasheet check; not a readability item.

### Updated rating and verdict

**Rating: 8.5 / 10.** Every MAJOR is closed; the root page now tells the story of the board; the rails sheet is readable; DNP parts are identifiable. What remains is a handful of small text touches (N1–N4), two style items the owners chose to keep (CC labels, A2 head-room), and the rotated-value density that any A2 KiCad sheet has.

**Verdict: PASS.** N1–N3 are two-minute generator fixes and can go in with the next regeneration; none blocks Gate 2. Re-run the style script after N1–N3 so its text-overlap check agrees with this render.
