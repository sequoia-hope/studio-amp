# J_HP, J_LO_L, J_LO_R, J_MIC: audio jacks (R-13, R-14, R-15, R-42, R-60)

All of these are through-hole edge connectors on the back-panel edge (R-60). R-70 allows hand
soldering or JLC THT assembly.

## J_HP: Neutrik NMJ6HCD2, 6.35 mm stereo jack, switched

Datasheets:
- `datasheets/nmj6hcd2.pdf`: drawing ST-NMJ6HCD2, 2021; rendered and read.
- `datasheets/nmj6hcd2-spec.pdf`: Neutrik product data sheet, read in full.

`C368502 NMJ6HCD2 (Neutrik, Through Hole): extended, JLC stock 870, lifecycle normal, checked 2026-11-07`

| Item | Datasheet | Ours | OK |
|---|---|---|---|
| Contacts | T, R, S + 3 normals (TN, RN, SN), Ø1.4 mm holes; pitch 16.7/10.35/4 mm along, 16.23 mm across | 6 pads | — |
| Rated current per contact | 3 A; switch contacts 0.5 A at 50 V | ≤ 43 mA | OK |
| Contact resistance | < 15 mΩ / < 30 mΩ | — | OK |
| Dielectric / insulation | 1 kVdc; ≥ 1 GΩ at 500 Vdc | — | OK |
| Mating | A-gauge stereo plugs per EIA RS-453 (standard 1/4 in TRS headphone plugs) | — | OK |
| Panel | rear mounting, panel ≤ 4.7 mm, 11.4 mm cut-out, 11 mm A/F nut | enclosure (phase 4) | note |
| Temperature | **−25 to +70 °C** | 55 °C cabinet air | **fails R-40's ≥ 85 °C wording; margin 15 K over the worst case** |

Why this part: every LCSC-stocked 6.35 mm jack checked is rated to 70 °C or less. HOOYA PJ-612
(C309284, 1058 in stock, `datasheets/pj-612.pdf`) is −20 to +70 °C, rated 30 VDC 0.5 A, and
50 mΩ. CAX PJ-612-5P (`datasheets/pj-612-5p.pdf`) gives no temperature rating. The Neutrik has
the best contacts (2 µm Ag on CuSn6, > 10,000 cycles) and normalling contacts. **The R-40 waiver is logged in
`decisions.md` (user, 2026-11-07).**

Normals: TN and RN open when a plug is inserted (normalling contacts; confirm the sense on the
part with a meter at bring-up, since the drawing doesn't state it). SN goes to GND. TN goes to
HP_DET (FPGA ball K13, 1 kΩ series on block E's side) with a 47 kΩ pull-up to +3V3 (re-review
NOTE-2: ≥ 2.8 V against the ECP5's 10 µA input leakage), read as plug present/absent. The PESD spare
sits on it.

Sleeve: to GND (the analog ground, near where the HP stage returns). The ferrule is plastic
(PA 6.6), so there is no chassis contact.

## J_LO_L, J_LO_R: CUI RCJ-01x right-angle RCA jacks (×2)

Datasheet: `datasheets/rcj-014.pdf` (CUI RCJ-01 series, 11/07/2019). Read in full.
`C4991844 RCJ-014 (CUI, Through Hole): extended, JLC stock 159, lifecycle normal, checked 2026-11-07` (black, ×2)
Colour option: `C4991691 RCJ-012 (CUI, -): extended, JLC stock 24, lifecycle normal, checked 2026-11-07` (red). Its
stock of 24 covers 5 boards plus attrition but is thin. **Baseline: 2 × RCJ-014 black, with "L"
and "R" on the silk.**

| Item | Datasheet | Ours | OK |
|---|---|---|---|
| Rated | 12 Vdc, 1 A | ≤ 5.7 Vpk, ≤ 57 mA | OK |
| Contact resistance | 30 mΩ | in series with 100 Ω | OK |
| Withstand | 500 Vac 1 min | — | OK |
| Temperature | −40 to +85 °C | 55 °C | OK |
| Life | 1500 cycles | — | OK |
| Shell | tinned iron, pin 2 | GND | — |
| Footprint | p.2 recommended layout (pin positions at 5.0 and 10.0 mm spacing, hole sizes per drawing) | built from the drawing in phase 2 | phase 2 |

Pin 1 is the centre (signal) and pin 2 the shell/ground (schematic, p.2). The metal shell is
reachable, so it gets a direct GND via cluster next to the TVS.

## J_MIC: CUI SJ1-3523N, 3.5 mm TRS jack, no switch

Datasheet: `datasheets/sj1-3523n.pdf` (CUI SJ1-352XN, 10/05/2022). Read in full.
`C20182914 SJ1-3523N (CUI, Through Hole,12x11mm): extended, JLC stock 302, lifecycle normal, checked 2026-11-07`

| Item | Datasheet | Ours | OK |
|---|---|---|---|
| Rated | 12 Vdc, 1 A | 5 V bias, < 1 mA | OK |
| Temperature | −25 to +85 °C | 55 °C | OK |
| Pins | 1 sleeve, 2 tip, 3 ring (SJ1-3523N has no switch pins) | sleeve = GND; tip = mic signal + bias; ring = bias only, through R_RING (see below) | — |
| Bushing | nickel-plated brass (panel nut) | GND via sleeve only | — |

Ring handling: common plug-in-power mics and capsules on TRS cables wire tip = signal and
ring = bias (often bridged), or a TS plug shorts ring to sleeve. Ours feeds the bias through
2.2 kΩ to both tip and ring (R_RING 2.2 kΩ from the bias node), and takes the signal from the
tip. A TS plug shorting ring to sleeve then draws only 5 V/4.4 kΩ ≈ 1.1 mA. Harmless.

## Fine print / gotchas

- The Neutrik is a "rear mounting" part (it is panel-mounted from behind with a nut). Phase 4
  must align its nose with the back-panel cut-out and allow for the 4 mm board-to-pin stand-off.
- None of these jacks is SMT. JLC THT or hand soldering (R-70).
- R-42 ESD on every signal pin: see `F-esd.md`.

## Phase 2 corrections (schematic, 2026-11-08)

- **Plug detect uses SN, not TN.** With no plug, SN is shorted to S (GND), so HP_DET reads low.
  Inserting a plug opens SN, and the 47 kΩ pull-up to +3V3 takes HP_DET high. TN and RN are not
  connected (no-connect flags). The spare PESD15VL1BA sits on the HP_DET node.
  - Using TN would have tied HP_DET to the tip line through the normal contact.
  - Bring-up still confirms the normal's sense on the part in hand.
- J_HP uses the project symbol `studio_F:NMJ6HCD2_F`. Its pins are ordered TN, RN, T, R, SN, S so
  the wiring has no crossings. The pin names match KiCad's
  `Jack_6.35mm_Neutrik_NMJ6HCD2_Horizontal` pads, which were checked against the Neutrik drawing:
  - T–R–S pitch 6.35 mm;
  - normals row 16.23 mm away.
- RCA: 2 × RCJ-014 (black), symbol `studio_F:RCJ-01`. Footprint `studio_F:RCA_CUI_RCJ-01_Horizontal`
  is built from rcj-014.pdf p.2:
  - pin 1 (shell): Ø2.6 at (±5, 0) and (0, −4.5);
  - pin 2 (centre): Ø1.7 at (0, 0).
  Each jack has its own 100 kΩ to GND and a PESD15VL1BA.
- Mic jack: KiCad `Jack_3.5mm_CUI_SJ1-3523N_Horizontal`, pads T/R/S.
