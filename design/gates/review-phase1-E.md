# Phase 1 independent review — block E (compute, network, clocks)

Date: 2026-11-07. Reviewer: independent (did not see the authors' conversation).
Scope: `design/parts/E-fpga-ecp5.md`, `E-fpga-ecp5-passives.md`, `E-pinmap.md`, `E-interfaces.md`,
`E-mcu-rp2350b.md`, `E-mcu-passives.md`, `E-flash-w25q128.md`, `E-xtal-12mhz.md`, `E-phy-lan8720.md`,
`E-phy-passives.md`, `E-clk-rmii-50mhz.md`, `E-clk-audio-vcxo.md`, `E-link.md`. Gowin files and the
level-translator / expander files are marked superseded and were ignored.
Datasheets re-read (pdftotext, or rendered pages for the image-only oscillator sheets):
FPGA-DS-02012-3.4, FPGA-TN-02039-2.6, FPGA-TN-02038-2.1, FPGA-TN-02035, FPGA-TN-02200, DS-02053,
ECP5U-25 pinout CSV (every ball re-checked by my own script), LAN8720A DS00002165B, RP2350 datasheet
and "Hardware design with RP2350" r3, W25Q128JV rev J, ABM8-272-T3, SX3V VCXO, YXC YSO110TR.
Sourcing lines re-run with `jlc_parts.py show` on 2026-11-07: all 25 parts checked are `lifecycle normal`,
stock ≥ need (ECP5 1125, RP2350B 2170, LAN8720AI 9259, SX3V 155, AOTA inductor 1752).

## What checks out (recomputed, no finding)

- ECP5 abs max / recommended (DS p.51): VCC 1.045–1.155 V vs block C 1.075–1.128 V; VCCAUX 2.375–2.625 V
  vs 2.505 ± 1 %; VCCIO ≤ 3.465 V vs 3.24–3.40 V; VCCAUX ramp 2 mV/µs ≪ 30 mV/µs; all rails 0.01–10 V/ms
  (p.52); VCCIO first, VCC/VCCAUX ≈ 1 ms later (TN-02038 §4 p.13). POR thresholds and tICFG ≤ 33 ms (p.85) as stated.
- Decoupling exactly per TN-02038 Tab 3.1 (p.10): VCC 3 × 10 µF + 6 × 100 nF; VCCAUX 120 Ω bead + 10 µF
  + 2 × 100 nF; VCCIO 10 µF/bank + 13 × 100 nF, 22 µF on bank 6. Cap voltage ≥ 1.8 × rail (§3.5.2 p.12) met.
  Bead drop 50 mA × 0.05 Ω = 0.1 % < 0.25 % PLL target. MLCC bias: 10 µF/10 V/0603 at 3.3 V keeps
  ≈ 70–80 %; 4.7 µF/10 V/0402 at 3.3 V ≈ 60 % (Raspberry Pi reference values, accepted).
- Config straps per TN-02038 Tab 6.1/6.2 (p.15) and TN-02039 Tab 4.5 (p.14): PROGRAMN/INITN/SN 4.7 kΩ up,
  CFG0 4.7 kΩ up, CFG1/2 hard to GND (< 500 Ω rule), JTAG TDI/TMS/TDO up, TCK down. CFGMDN = 001 = SSPI
  (Tab 4.6 p.15). SSPI: fCCLK ≤ 60 MHz, tCCLKH/L ≥ 6 ns, setup/hold 1 ns, MOSI on CCLK↑, MISO on CCLK↓
  = SPI mode 0 (DS p.85; TN-02039 §6.2). 37.5 MHz write path: 13.3 ns setup vs 1 ns needed.
- Bitstream: LFE5-25 max-EBR uncompressed 5.42 Mb = 677.5 KB (TN-02039 Tab 4.1 p.11); two 1 MB slots
  + two 6 MB RP2350 images + 8 KB tables = 14.0 MB ≤ 16 MB. Load 5.42 Mb / 37.5 MHz = 0.145 s. R-56 holds.
- GPIO default during/after configuration = tri-state + weak pull-down, D[7:0] no pull, DONE/INITN/
  PROGRAMN/SN/CCLK/HOLDN/CS1N/WRITEN pull-up (TN-02039 §5 p.23, Tab 4.5). ADC-CS pull-up 4.7 kΩ vs 150 µA:
  CS ≥ 2.6 V, correct.
- Hot socketing (DS §3.6, Tab 3.5 p.52–53): left/right A/B and C/D pairs short while VCC < VPORUP. Every
  "partner NC" claim in `E-pinmap.md` verified against the CSV differential column (14/14 correct).
- Pin legality: all 108 balls exist in the CABGA256 column with the stated pad, bank and dual function;
  no ball used twice; power/GND lists (27 GND, 6 VCC, 2 VCCAUX, 13 VCCIO) match the CSV; spare lists
  contain no used ball. Clock inputs are on PCLK/GPLL pads (C8 PCLKT1_0, M16 PCLKT3_0, P6 LLC_GPLL0T_IN,
  K1 PCLKT7_0). ODDRX2F 4:1 gearing "is available on each pin on the left and right" (TN-02035 §8.7), so
  N1/P1/R2/R4 in bank 6 are legal. VREF pads R16/R1 used as outputs are fine (no referenced I/O in banks 3/6).
- PLL (DS Tab 3.23 p.72): fIN 24.576 MHz ≥ 8, fPFD 24.576 ≥ 10, VCO 688.128 in 400–800, CLKOP 344.064 ≤ 400,
  ECLK 344.064 ≤ 350 (−7), GDDRX2_TX 688.128 ≤ 700 Mb/s (−7) — arithmetic correct; see MAJOR-1 on grade.
- RMII (LAN8720A Tab 5-10 p.61, REF_CLK-in: toval ≤ 14.0, tohold ≥ 3.0, tsu ≥ 4.0, tihold ≥ 1.5 ns;
  ECP5 Tab 3.22 p.66: tCO ≤ 6.1, tSU 0, tH 3.0, tSU_DEL 1.33, tH_DEL 0 ns, −7). RX without delay: setup
  +5.8 ns, hold 3.4 − (0.2 clock flight + 3.0) = **+0.2 ns** (the audit's +0.4 forgot the clock flight) →
  DELAYG required, as the audit concludes: setup +4.5, hold +3.2 ns. TX: setup +9.7 ns; hold needs
  min tCO ≥ 1.3 ns (not in the datasheet) — same open item as the audit. XO: ±33 ppm ≤ ±50, 0.7 ps rms
  ≤ 150 ps p-p, duty 45–55 % in 40–60 % (Tab 5-11 p.62).
- RP2350B QFN-80 pin numbers (Fig. 3) and SPI1 on GPIO24 RX / 25 CSn / 26 SCK / 27 TX (GPIO function
  table) match `E-pinmap.md`; ADC on GPIO40–47; PIO link on GPIO8–19 legal; HSTX overlap noted and unused.
- Crystal: 15 pF/2 + 3 pF = 10.5 pF vs CL 10 pF (ABM8 p.1; guide §4), C0 ≤ 3 pF, ESR ≤ 50 Ω with 1 kΩ:
  the Raspberry Pi circuit verbatim. W25Q128JVSIQ: 3.0–3.6 V for FR 133 MHz (§9.6), 75 MHz QMI clock fine.
- Link: 8 × 37.5 MHz = 37.5 MB/s vs 30.9 MB/s worst (82 %) — recomputed, agrees. Read round trip
  ≈ 10.4 ns vs 20 ns sample point: fine.
- Package: caBGA-256, 14.00 mm, 0.80 mm pitch, JEDEC MO-275 (DS-02053 §94). Footprint claim correct.

## Findings

### BLOCKER

None.

### MAJOR

**MAJOR-1 — PWM gearing at 98 % of a *commercial* limit on an *industrial* part.**
Files: `E-fpga-ecp5.md` (Clocking section), `E-clk-audio-vcxo.md` header, `E-interfaces.md` item 4,
`design/intent.md` R-53. Datasheet: FPGA-DS-02012 Tab 3.22, header "Over recommended commercial operating
conditions" (p.66) and note "Commercial timing numbers are shown. Industrial numbers are typically slower
and can be extracted from the Diamond software" (p.69). The 700 Mb/s GDDRX2_TX and 350 MHz fMAX_EDGE used
to justify 688.128 Mb/s / 344.064 MHz ECLK are commercial numbers; the chosen MPN is LFE5U-25F-7BG256**I**.
A 2 % margin against a limit the datasheet says is lower for this grade is not a verified design point, and
the open flow (nextpnr-ecp5) has no industrial timing model to check it with. The 1.453 ns grid was accepted
by the user on this basis.
Fix: make the ×12 setting (589.8 Mb/s, ECLK 294.9 MHz, 84 % of the commercial limits; grid 1.695 ns)
the baseline in R-53 and in block D's noise-shaper inputs, with ×14 as a bring-up option; or obtain the
−7I ECLK/GDDRX2 numbers from Diamond (free licence) and record them in the audit before keeping 1.453 ns.
Note that the same note applies to tCO 6.1 ns, used in the RMII, DAC and link budgets — those have ≥ 4 ns
of slack and survive, but say so in the audit.

**MAJOR-2 — LAN8720A MODE straps vs ECP5 pull-downs; no external strap resistors.**
Files: `E-phy-lan8720.md` (Configuration table), `E-phy-passives.md`, `E-pinmap.md` A11/A12/B11.
Datasheet: LAN8720A §3.7 p.26 "If a particular configuration strap is connected to a load, an external
pull-up or pull-down resistor should be used to augment the internal resistor"; pin table p.12: internal
pull-up is 50 µA typical; TN-02039 §5 p.23: ECP5 GPIO default is a weak pull-down of 30–150 µA (DS Tab 3.7
p.54) before and after configuration unless the design says otherwise. The audit states the FPGA pins
"idle with weak pull-ups during configuration → consistent" — that is the Gowin behaviour, not the ECP5's.
RXD0/RXD1/CRS_DV are loaded by FPGA inputs whose pull-down is up to 3× the PHY's pull-up, so MODE[2:0]
reads 000 (10BASE-T half-duplex, no auto-negotiation) at any strap latch where the FPGA pulls are down
(POR, and nRST release if the gateware leaves PULLMODE at a DOWN default — Diamond's default for LVCMOS).
Fix: fit 10 kΩ pull-ups to VDDIO on RXD0, RXD1 and CRS_DV (datasheet "should"), and add an explicit
gateware rule: PULLMODE=UP (or NONE) on A11, A12, B11 in the LPF; correct the audit text. Keep nRST
released only after configuration (already the case) so the final latch sees defined levels.

**MAJOR-3 — Block B ↔ E interface not in the pin map; `POE_LOSS_N` has no owner.**
Files: `E-pinmap.md`, `E-interfaces.md`; cross-check `design/architecture.md` "Phase 1 reconciliation",
`B-interfaces.md` (new nets table and item 4/5), `F-interfaces.md` ("POE_LOSS_N net owner is known" is
left open), `C-interfaces.md` (does not define a PoE-loss net). The reconciled architecture records
`ILIM_SEL0/1` (E → B, 3.3 V GPIO), `IBUS_SENSE` (B → E/D, 0–3 V analog) and optional `ACF_PULSE` (B → E).
None of the three appears in `E-pinmap.md` or `E-interfaces.md`. Conversely `E-pinmap.md` assigns ball A6
to `POE_LOSS_N` "from B/C", but no block B or C audit produces such a net; R-32a's "fast comparator on
the converter's secondary" is not designed anywhere. Block F's R-34 mute rule and the gateware PWM gate
hang on this signal.
Fix: (a) add `ILIM_SEL0/1` (two spare RP2350 GPIOs or bank-0 balls), `ACF_PULSE` (top-bank input, 1 kΩ
series — it is an always-powered driver) and `IBUS_SENSE` (RP2350 ADC4–7 are spare; or a 9th channel is
not available on the full ADS7038) to the pin map and the rail/signal tables; (b) either name an owner
for a hardware PoE-loss comparator (B or C) or replace `POE_LOSS_N` with the detection scheme the
architecture already has (PD_PG_N from A, ACF_PULSE loss and VBUS droop from the ADS7042 in gateware)
and say so in `E-interfaces.md` and `F-interfaces.md`.

### MINOR

**MINOR-1 — Slave-SPI persistence is read-only; audit implies re-load without PROGRAMN.**
`E-fpga-ecp5.md` ("To keep SSPI usable in user mode (re-load without PROGRAMN, read status), the design sets
SLAVE_SPI_PORT=ENABLE"; load flow "pulse PROGRAMN or send REFRESH 0x79"). TN-02039 §6.2.1 (p.33): "A port
enabled by persistence is capable of reading commands only ... is not a configuration port." Re-load always
needs the PROGRAMN pulse (wired to GPIO22, so the hardware is fine). Fix the text; keep SLAVE_SPI_PORT=ENABLE
for status read-back only.

**MINOR-2 — CCLK pull-up omitted.** `E-fpga-ecp5-passives.md`. TN-02038 Tab 6.2 (p.15): "MCLK/CCLK: 510 Ω to
1 kΩ pull-up to VCCIO8, serial resistor near TX side" (note 1: 22–80 Ω); TN-02039 Tab 4.5 note 6 (p.14):
"MCLK should have a 1 kΩ pull-up". The 33 Ω is there, the pull-up is not. With the RP2350 in reset (pad
pulled down 36–113 kΩ) against the ECP5's 30–150 µA pull-up the CCLK node floats near mid-rail. Fit 1 kΩ to
VCCIO8 and set the RP2350 SCK drive to 8 mA.

**MINOR-3 — SSPI read commands at 37.5 MHz do not close on paper.** `E-fpga-ecp5.md`, `E-pinmap.md` GPIO26.
Writes are fine (13.3 ns vs 1 ns). Reads: RP2350 SCK pad delay (≈ 3–4 ns, assumed; not in Tab 1436) + 33 Ω RC
≈ 0.4 ns + ECP5 tSTCO ≤ 10 ns (DS p.85) + flight 0.3 ns + RP2350 input pad ≈ 2 ns ≈ 16 ns > the 13.3 ns
half-period to the sampling edge. Run LSC_READ_STATUS / ID reads at ≤ 18.75 MHz (clk_peri/8) and the
LSC_BITSTREAM_BURST at 37.5 MHz, or sample MISO on the following edge. Firmware rule; record it.

**MINOR-4 — PLL input edge rate.** `E-clk-audio-vcxo.md` table row "Rise/fall ≤ 5 ns ... OK" is Gowin text.
ECP5 Tab 3.23 (p.72–73): tR/tF input clock 10–90 % max **1 ns**. The SX3V guarantees only ≤ 5 ns (p.1) into
15 pF, and the 33 Ω + branch capacitance slows it further. Not a functional failure (slow edges raise
supply-noise-to-jitter conversion at the PLL input), but it is a datasheet condition the design violates.
Keep the FPGA branch the shortest and lightest load, consider dropping the 33 Ω on that branch, and
measure at bring-up; record as a known deviation.

**MINOR-5 — `PD_PG` polarity/name mismatch with block A.** `E-pinmap.md` A2 `PD_PG`, `E-interfaces.md`
("drop HP_EN/LO_EN when PD_PG falls"). `A-interfaces.md`: the isolator output is `PD_PG_N`, active low,
default high when the primary is unpowered. Rename to `PD_PG_N` and invert the gateware rule, or the
phase 2 netlist will not connect and the mute logic will be inverted.

**MINOR-6 — DOUT/CSON (M8 = `LINK_D7`) drives high from power-up until the bitstream's Bypass instruction**
(TN-02039 §4.7.2 p.18–19); WRITEN (M9 = `LINK_IRQ`) and CS1N (P8 = `LINK_D6`) are pulled up during
configuration (Tab 4.5). The RP2350 must keep GPIO8–19 Hi-Z until DONE *and* tri-state them before every
PROGRAMN pulse (A/B reload). `E-link.md` states the first rule only; add the second.

**MINOR-7 — Hot-socket pair with a pull-up on a PWM partner.** `E-pinmap.md` T3 `VB_CS_n` (4.7 kΩ pull-up)
is the C/D partner of R4 `PWM_T_B` (CSV: PL41D/PL41C). In the window (VCCIO up, VCC < VPORUP) the pair
short lets the pull-up lift PWM_T_B toward 3.3 V against block D's pull-down. Harmless only because VDRV is
off then (block C sequencing). Swap `VB_CS_n` with a pin whose partner is not a PWM/EN line (e.g. use P4
or M6, both spare in bank 6) so the safety does not rest on sequencing alone.

**MINOR-8 — Stale text inside updated files** (the header notes are right, the bodies are not):
`E-mcu-rp2350b.md` ("1.8 V signals ... translated", `FPGA_JTAG_OE_N`, "47 of 48 GPIO used", "4 knobs +
4 NTCs"; header says 39 used/9 spare, pin map says 35/13 — the pin map is right); `E-flash-w25q128.md`
flash-map table (512 KB slots, "UG290 Tab 3-1", "FPGA's own configuration flash holds the golden
bitstream"); `E-phy-lan8720.md` ("nRST driven by the RP2350 GPIO30", "MDC from the RP2350", "≤ 25 mm from
the FPGA's right edge" — RMII is on the top bank); `E-phy-passives.md` ("nRST pull-down vs RP2350 drive");
`E-clk-rmii-50mhz.md` body ("FPGA pin 52 GCLKT_3"); `E-clk-audio-vcxo.md` body ("pin 63", "bank 1",
"VCXO_TUNE pin 61, bank 1" — it is N4, bank 6; Gowin PLL/OSER paragraphs). Rewrite or delete the superseded
paragraphs so phase 2 does not build from them.

**MINOR-9 — `HP_EN`/`LO_EN` series resistors disagree.** `F-interfaces.md` ECP5 table lists "1 kΩ (block E)"
on HP_EN and LO_EN; `E-pinmap.md` and `E-fpga-ecp5-passives.md` fit none (only on the two inputs). Agree one
way; they are outputs into 10 kΩ gate resistors, so none is needed — fix block F's table or add two parts.

### NOTE

- NOTE-1 `E-fpga-ecp5.md`: "Top/bottom have ODDRX1F only" — TN-02035 §8.7: the bottom side (bank 8) has no
  DDR registers at all on non-SerDes parts. Bank 8 carries only SDR link pins, so no impact.
- NOTE-2 DS Tab 3.22 note (p.69): general I/O timing is for LVCMOS25, 12 mA, fast slew, 0 pF. The 6.1 ns
  tCO will be ≈ 1–2 ns longer at LVCMOS33 into 10–15 pF; RMII TX (+9.7), link read (+9.6) and DAC (12 ns
  budget) still close. Say so where 6.1 ns is quoted.
- NOTE-3 L1/M1 (PCLKT6_1/PCLKT6_0) and K4/L4 (GR_PCLK6_0/1) spend bank 6's only clock-capable inputs on
  slow fault/CS lines; G16 (GR_PCLK2_1) on a test point. Legal; consider moving them to P4/M6 or bank 7
  spares if a bank-6 edge/primary clock input is ever needed.
- NOTE-4 Block C offers `VDRV_PG` to the FPGA and an optional `AN_OFF`; E takes `VDRV_PG` only on GPIO33
  and does not list `AN_OFF`. Acceptable (D accepted the link path); record the two decisions in
  `E-interfaces.md`.
- NOTE-5 SX3V MPN decode "30 = ±30 ppm drift": page 1 lists ±25 ppm (conditional) and ±50 ppm for
  −40…+85 °C; APR ±50 ppm is what the design relies on, so no impact. The phase-noise gap vs block F's
  ≤ 1 ps requirement is correctly declared unverifiable; the 0.7 ps YXC fallback (p.1, 12 kHz–20 MHz) is
  confirmed.
- NOTE-6 `E-fpga-ecp5.md` fan-out: 0.09 mm trace between 0.40 mm NSMD pads leaves 0.155 mm; JLC's 6-layer
  minimum is 0.09/0.09. Correct but at the limit; confirm against the JLC capability page in phase 5.
- NOTE-7 RP2350 "open-drain" on GPIO22 (PROGRAMN) is emulated by output-enable toggling; fine, state it.

## Verdict

**Not yet passable:** fix MAJOR-1 (industrial-grade timing margin for the 1.453 ns grid), MAJOR-2 (PHY strap
pull-ups and PULLMODE) and MAJOR-3 (B ↔ E nets and `POE_LOSS_N` ownership in the pin map), then the block
passes with the MINOR items closed as text/firmware notes.
