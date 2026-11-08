# Phase 2 parts cross-check — blocks E (mcu, fpga, ethernet), F (audio_out, audio_in), G (io)

Date: 2026-11-08. Independent reviewer; inputs were `design/renders/netlist.xml`, `design/renders/bom-sch.csv`,
the phase 1 audits in `design/parts/`, the datasheets in `design/datasheets/` (pdftotext), the Lattice
`lattice-ECP5U-25-pinout.csv`, and the project libraries `hw/satellite/a/lib/studio_{E,F,G}.kicad_sym` / `.pretty`.
Every connection below was traced in the netlist by script (scratch: `xchk-EFG/nl.py`, `ecp5chk.py`), not read off labels.

## Findings

### BLOCKER

**B-1 — D1005, D1011 (BAV99, audio_out): the −15 V rail is shorted to GND through a diode.**
Nets: D1005 pin 1 (A1) → `Net-(D1005-A1)` (Q1002 base, R1051); pin 2 (K2) → `-15V`; **pin 3 (K1/A2) → `GND`**. D1011 is
the same on the R channel (Q1008 base, R1066). Per Nexperia BAV99 Table 2 (datasheet p. 2, "Pinning information")
pin 3 is the internal junction: cathode of diode 1 and anode of diode 2. With pin 3 on GND, diode 2 sits
anode = GND, cathode = −15 V: forward-biased with 15 V across it and nothing in series. It will carry whatever the
−15 V LDO can source (IF max 215 mA, IFSM 4 A) until the diode or the LDO gives up, and the −15 V rail collapses.
The intended circuit (`F-hp-output-stage.md`, "Bias string": Q_SB base at −15 V + 2 VF, 15 kΩ to GND) is the
mirror of the top reference D1004/D1010, which is drawn correctly (A1 → +15 V, K2 → base, pin 3 **no-connect**).
Fix: remove the GND connection from D1005.3 and D1011.3 and leave the pin no-connect; the series pair is then
pin 1 (base) → junction → pin 2 (−15 V), as on the top side.

### MAJOR

**M-1 — FB1001, FB1002 (BLM18AG601, audio_out): both ferrite pads are on the same net, so the ESD bead is bypassed.**
`Net-(D1019-A1)` contains D1019.1, J1001.T, K1001.4 (NO1) **and FB1001.1 and FB1001.2**; likewise
`Net-(D1020-A1)` for the ring. `F-esd.md` ("Layout guidance" and "Phase 2 correction") requires jack pin → TVS →
ferrite → relay NO so that the 44 V TVS residue does not reach the BAV99 clamp through 4.7 Ω. As drawn the bead is
in the BOM but does nothing. Fix: put J1001.T and D1019 on one net, FB1001 between that net and K1001.4; same for
R/D1020/FB1002/K1001.5.

### MINOR

- **m-1 — MK1101 PDM_CLK (audio_in): no 33 Ω source series resistor.** `PDM_CLK` runs from U801.L14 straight to MK1101.4.
  `F-mems-t3902.md` ("Required external parts") asks for 33 Ω at the FPGA; the E pin map has no series R on L14 either.
  Add 33 Ω 0402 at the ECP5 end.
- **m-2 — U1202 TCA9617B (io): VCCB (pin 8) has no bypass capacitor.** Only C1203 (100 nF, `Decouples=U1202.1`) is
  fitted, on VCCA. `G-qwiic.md` "Layout guidance" says 100 nF on each VCC pin; the TI datasheet's power-supply
  recommendations bypass both. Add a 100 nF at pin 8.

### NOTE

- **n-1 — C1020 (+3V3_Q bulk) is X5R** (CL21A106KAYNNNE, 25 V) where `F-dac-74lvc74.md` says "one 10 µF X7R per group of
  four packages". On a 3.3 V rail against 25 V this is harmless; either change the part or the text.
- **n-2 — U801 symbol pad names:** five bank-8 pins carry an abbreviated dual-function name (N8 `PB15A/HOLDN/DI` vs CSV
  `HOLDN/DI/BUSY/CSSPIN/CEN`; P7, R7, T7, T8 drop the `IOn` suffix). Cosmetic; the ball numbers are all correct.
- **n-3 — T3902 footprint:** the ring pad (pad 3) is centred at x = −0.6625 mm, the Ø0.8 NPTH sound hole at −0.71 mm
  (the datasheet's 1.252 mm column offset). 47 µm eccentricity; make them concentric when the footprint is next touched.
- **n-4 — `F-jacks.md` RCJ-01 numbering is self-contradictory:** the body text says pin 1 = centre, pin 2 = shell; the
  phase 2 note, the symbol `studio_F:RCJ-01` (1 = S, 2 = T) and the footprint (pad 1 = three Ø2.6 shell holes, pad 2 =
  Ø1.7 centre) say the opposite. Symbol and footprint agree, so the netlist is right; fix the text.
- **n-5 — `G-led-out.md` says `LED_EN` is an "RP2350 GPIO"**; `E-pinmap.md` and the netlist put it on ECP5 H15 (with
  R1219 100 kΩ pull-down). Netlist follows the pin map; update the G text.
- **n-6 — HFD4 footprint:** pad rows 6.35 mm centre-to-centre, pads 2.15 mm long (copper from 2.1 to 4.25 mm from the
  centreline) against the datasheet S-type terminal span 5.08 (inner) / 7.5 (outer) mm. Adequate; the audit's "rows
  7.5 mm apart" is the outer terminal span, not the pad pitch.
- **n-7 — FG 1.0-3PWT vs the KiCad SM03B footprint** (J1203, J1204) could not be checked here: the FG drawing is image-only.
  `G-debug-jtag.md` already lists it as a phase 2 overlay task; it is still open.

## What was checked and found correct

### Block E — mcu sheet (U701 RP2350B, U702, Y701)
- All 80 pins + EP match `E-pinmap.md` (GPIO0–3 UART/I2C, 4/5 LED, 6/7 and 20/21 encoders, 8–15 LINK_D0–7, 16–19
  LINK_CLK/DIR/STB/IRQ, 22–28 SSPI set PROGRAMN/INITN/MISO/SN/CCLK/MOSI/DONE, 33–36 VDRV_PG/ILIM_SEL0/1/VDRV_EN,
  40–44 KNOB1–4/IBUS_SENSE, spares 29–32, 37–39, 45–47 open). Pin numbering agrees with the datasheet QFN-80 figure
  (§1.2.1.2: 1 GPIO4, 33/34 SWCLK/SWDIO, 55 GPIO44_ADC4, 59 ADC_AVDD, 61–75 VREG/USB/QSPI group).
- Regulator per RP2350B Minimal / `chips/rp2350.md`: L701 AOTA-B201610S3R3 (pad 1 → DVDD_RP, pad 2 → VREG_LX),
  C702 CIN 4.7 µF (RPi small-pad footprint), C703 COUT 4.7 µF at VREG_FB/DVDD_RP, R701 33 Ω + C701 4.7 µF on VREG_AVDD,
  second 4.7 µF C707 on DVDD pin 51, 100 nF on each DVDD (10, 32, 51) and IOVDD (5, 15, 24, 29, 41, 50, 60, 76),
  C717 shared by 68/69, C708 10 µF bulk, VREG_PGND to GND.
- Crystal: ABM8-272-T3, XIN ← Y701.3 with C721 15 pF; XOUT → R704 1 kΩ → Y701.1 with C722 15 pF at the crystal; GND pads.
- QSPI: SS/SD0–3/SCLK to W25Q128JVSIQ CS/DI/DO/WP/HOLD/CLK; R706 10 kΩ pull-up DNP; R707 1 kΩ to SW702 BOOTSEL; C723 100 nF.
- USB: R708/R709 27 Ω to USB_DM/USB_DP (io sheet USBLC6). RUN: R705 10 kΩ, SW701, TP1217.
- ADC_AVDD: R702 10 Ω + C718 4.7 µF + C719 100 nF, shared with G's KNOB_REF. IBUS_SENSE C720 100 nF.
- MPN/LCSC: RP2350B C42415655, W25Q128JVSIQ C97521, ABM8-272-T3 C20625731, C1548, C23733, C1525, C19702, C25105,
  C25077, C11702, C25744, C25100, C42411119, TS-1187A C318884 — all as audited.

### Block E — fpga sheet (U801 LFE5U-25F-7BG256I)
- Script: all 256 balls present once; every ball's name and bank agree with the Lattice CSV (CABGA256 column); every
  signal ball matches `E-pinmap.md` (function, bank, ball), seen through the series resistors. All 27 GND balls on GND,
  6 VCC on `+1V1`, VCCAUX G11/L7 on `/fpga/VCCAUX` behind FB801 BLM18PG121 from `+2V5`, all 13 VCCIO balls on `+3V3`.
- Decoupling per TN-02038 Tab 3.1: VCC 3 × 10 µF + 6 × 100 nF; VCCAUX 10 µF + 2 × 100 nF; each VCCIO bank 10 µF + 100 nF
  per ball, bank 6 with 22 µF (C825). All caps on the right rails.
- Configuration for slave SPI: CFG0 N10 4.7 kΩ → +3V3, CFG1 P10 and CFG2 R10 → GND (001); CCLK N9 ← R703 33 Ω at the
  RP2350 + R825 1 kΩ pull-up; MOSI T8 ← GPIO27; MISO T7 → GPIO24; SN R8 ← GPIO25 + 4.7 kΩ; HOLDN N8 4.7 kΩ, not driven;
  PROGRAMN R9 ← GPIO22 + 4.7 kΩ; INITN T9 → GPIO23 + 4.7 kΩ; DONE P9 → GPIO28 + 4.7 kΩ. JTAG: TCK 4.7 kΩ down,
  TDI/TMS/TDO 4.7 kΩ up, 33 Ω to J1207 (1 +3V3, 2 GND, 3 TCK, 4 TDO, 5 TDI, 6 TMS) with SRV05-4.
- Series resistors as audited: 1 kΩ on A2–A6, B3–B5, C14, E14, K16, K13, P11, G1, J1; 330 Ω on L16, N13, L1, M1;
  4.7 kΩ on B6 (ACF_PULSE); POE_LOSS_N 4.7 kΩ pull-up (R810); CS pull-ups 4.7 kΩ on L3, K4, P4; 10 kΩ pull-down on
  RMII_TXEN and PHY_NRST; 10 kΩ pull-up on PHY_NINT; 1.5 kΩ on MDIO; 4.7 kΩ MODE straps on A11/A12/B11.
- Hot-socket partner rule: every "partner NC" ball named in the pin map (D14, F14, K15, K12, L15, P14, P12, L2, M2, P5,
  H2, J2) is unconnected; T3 unconnected. Pairs with both balls used are all FPGA outputs, RP2350-driven link lines, or
  ADC SDO lines held tri-state by pulled-up CS, as the pin map allows. All other unused I/O left open (ECP5 default
  tri-state + weak pull-down, TN-02039 §5.2). CLK_AUX K1 → TP801 only.
- Link: GPIO8–15 ↔ M7, N7, P7, R7, R6, T6, P8, M8; GPIO16/17/18/19 ↔ M16/R15/T15/M9.
- Footprint `Lattice_caBGA-256_14x14mm_Layout16x16_P0.8mm`: 256 pads A1…T16, A1 at (−6, −6), 0.8 mm pitch, Ø0.40 mm.

### Block E — ethernet sheet (U901 LAN8720AI, Y901, Y902)
- LAN8720AI symbol pins 1–24 + EP agree with datasheet Table 2-8 (1 VDD2A … 24 RBIAS). RBIAS 12.1 kΩ 1 %; VDDCR 1 µF
  + 470 pF; VDDIO 100 nF + 4.7 µF; VDD1A/VDD2A on `ETH_AVDD` behind FB901 BLM18PG221 with 4.7 µF + 100 nF each;
  4 × 49.9 Ω 0603 to ETH_AVDD with two 100 nF; CT bypass 100 nF ×2 (J101.12, J101.6 on ETH_AVDD).
- MDI: TXP 21 → ETH_TXP → J101.11, TXN 20 → J101.10, RXP 23 → J101.4, RXN 22 → J101.5 (block A's magjack map).
- Straps: MODE[2:0] = 111 by 4.7 kΩ pull-ups on RXD0/RXD1/CRS_DV; RXER/PHYAD0 to TP901 only (PHYAD0 = 0);
  LED1/REGOFF → 270 Ω → green anode J101.20, J101.19 → GND (REGOFF = 0); LED2/nINTSEL → 270 Ω → yellow cathode J101.17,
  anode J101.18 on ETH_AVDD (nINTSEL = 1, REF_CLK In mode). XTAL2 open. nRST 10 kΩ down to B12; nINT 10 kΩ up to B13;
  MDC A13; MDIO A14 1.5 kΩ.
- Y901 OT2EL 50 MHz: EN and VDD on +3V3 with 100 nF; OUT → 33 Ω → XTAL1/CLKIN and → 33 Ω → RMII_REFCLK (C8).
- Y902 SX3V VCXO: Vc ← R919 0 Ω ← 100 kΩ/1 µF ×2 ← VCXO_TUNE (N4); OUT → VCXO_CLK → P6 (no series R) and → R921 33 Ω →
  MCLK_Q → U1004 inputs; VDD behind FB902 with 4.7 µF + 100 nF. R920 0 Ω to VDD is DNP (XO option). Footprint
  `Oscillator_SMD_3225-4Pin_YXC_SX3V`: 4 pads 1.3 × 1.2 at 2.1 × 1.9 mm, numbered 1 BL, 2 BR, 3 TR, 4 TL.
- MPN/LCSC: C17146, C25852, C52923, C1537, C19666, C80165, C23185, C25867, C25099, C5203552, C5179997, C25741.

### Block F — audio_out
- DAC chain: DAC_L0–3 (N16, P15, P16, R16) and DAC_R0–3 (R13, T14, R12, T13) → 33 Ω (R1001…) → D inputs of U1005–U1008
  (74LVC74APW, KiCad 74HC74 symbol pinout checked against the 74LVC74A Table 2: 1 RD, 2 D, 3 CP, 4 SD, 5 Q, 6 Q̄, 7 GND,
  8 Q̄, 9 Q, 10 SD, 11 CP, 12 D, 13 RD, 14 VCC). nSD/nRD all on +3V3_Q; 100 nF per package + C1020 10 µF. Q → 2.2 kΩ
  0.1 % → P+, Q̄ → 2.2 kΩ → P−, four taps each side, both channels.
- Clock: MCLK_Q → U1004 SN74LVC2G34 (1A, 2A tied; VCC +3V3_Q, 100 nF) → 1Y → 22 Ω → MCLK_FF to all eight CP pins;
  2Y → 33 Ω → MCLK_ADC → PCM1808 SCKI.
- Filter values and topology per `F-filter-passives.md`: C0 15 nF, R1 560, C1 8.2 nF, R2 750, C2 330 pF, R3 3.9 kΩ
  (+ side to GND, − side to output), R_INJ 20 kΩ from SERVO_x to X+, R_BAL 20 kΩ X− to GND; all RT0603 0.1 % and
  C0G 50 V. SA5532A U1001 on ±15 V with 100 nF + 10 µF X7R 1206 per rail.
- Servo U1003 OPA2277UA: R_S 1 MΩ from FILT_x to −, C_S 100 nF C0G 1206 to output, + to GND, outputs to R_INJ.
- Line out: R_BO 100 Ω 1206 0.25 W from FILT_x to K1002 COM, BAV99 clamp on the op-amp side, NO → RCA centre with
  PESD15VL1BA and 100 kΩ to GND.
- HP stage per `F-hp-output-stage.md`: Q1001/Q1007 BC857B and Q1002/Q1008 BC847B 4 mA sources (180 Ω, 15 kΩ, BAV99
  2-VF references D1004/D1010 correct); spreader BAV99 D1003/D1009 with R_SPR 10 Ω; R_D 1 kΩ 1206 from U1002 out;
  BCP56/BCP53 outputs with 100 Ω base stoppers, 15 Ω 0.1 % emitters, 1N4148WS anti-parallel B-E (D1006/D1007/D1012/D1013,
  polarity as audited), BC847B/BC857B limiters; Zobel 10 Ω + 4.7 nF C0G; R_OUT 4.7 Ω 0805; BAV99 clamp at HPA_x;
  Rf 1 kΩ ‖ 1 nF, Rg 3.3 kΩ (gain 1.303), 100 Ω input stopper. Transistor pinouts checked against Nexperia Table 2/3.
- Relays K1001/K1002 HFD4/5-SR: coil + (1) on +5V, − (8) to AO3400A drain, 1N4148WS flyback; COM 3/6 on the amplifier
  side, NO 4/5 to the jacks, NC open. Gates: FPGA HP_EN (M14) / LO_EN (N14) → 10 kΩ → gate, 100 kΩ to GND; BAT54A
  D1016/D1018 (datasheet Table 2: 1 K1, 2 K2, 3 common anode) anode on the gate, K1 → HP_FAULT_N, K2 → POE_LOSS_N.
- DC detector: 47 kΩ from HPA_L, HPA_R, FILT_L, FILT_R to N_DC; 10 µF X7R 1206; Q1015 (B via 10 kΩ, E GND) and Q1016
  (E via 10 kΩ, B GND) collectors on HP_FAULT_N; R1090 4.7 kΩ pull-up; 1 kΩ (R815) to P11.
- HP jack J1001 NMJ6HCD2: T/R from relay NO, S GND, SN → HP_DET with 47 kΩ pull-up, PESD, 1 kΩ to K13; TN/RN open.
- MPN/LCSC all as audited (C6100, C347589, C861295/472/551, C728592, C723637, C97907/8, C62784, C97946, C326730,
  C83716, C24460, C92221, C85085, C57668, C59205, C2500, C705727, C64399, C20917, C2128, C130910, C70462, C85378,
  C19330, C368502, C4991844, C17901, C4410, C2907327, C576818, C309653, C110776).

### Block F — audio_in
- PCM1808 symbol pins match datasheet p. 5 (1 VREF … 14 VINR). VREF 100 nF + 10 µF Al; VCC +5V_A 100 nF + 10 µF;
  VDD +3V3 100 nF + 10 µF; MD0, MD1, FMT → GND (slave, I2S); SCKI ← MCLK_ADC; LRCK ← R14; BCK ← P13; DOUT → 330 Ω → L16.
- Inputs: preamp out → 1 µF PET film → 2.2 kΩ → BAT54S junction (pin 1 GND, pin 2 +5V_A, pin 3 junction; Table 2
  pinning confirmed) → 1 kΩ → VINL with 1 nF C0G. VINR path identical, with C1116 and R1110 DNP as the audit says
  (loopback 10 kΩ / 2.2 kΩ from FILT_L).
- Mic chain: tip PESD, 2.2 kΩ bias, 1 µF film, 470 Ω, 470 kΩ to GND, BAV99 rail clamp, SA5532A gain 1 + 3 kΩ/1 kΩ with
  1 nF; bias node 47 µF Al, 2.2 kΩ to +5V_A, 2.2 kΩ to ring (with PESD).
- T3902 pins per Table 9 (1 DATA, 2 SELECT, 3 GND, 4 CLK, 5 VDD): DATA → 330 Ω → N13, SELECT GND, VDD via 10 Ω with
  100 nF. Footprint pads 0.522 × 0.725 at 0.822 / 1.675 mm, ring Ø1.025/1.625, Ø0.8 NPTH (see n-3).
- MPN/LCSC: C55513, C92673, C106246, C4747957, C4747968, C47546, C3171752, C20182914, C4190, C23179, C23178, C21190, C4211.

### Block G — io
- USB-C J1201: CC1/CC2 separate 5.1 kΩ to GND; D+ A6/B6 and D− A7/B7 through USBLC6-2SC6 (1/6 I/O1 → USB_DM,
  3/4 I/O2 → USB_DP, 5 VBUS → VUSB, 2 GND); SMF5.0A on VUSB; VUSB_DET 15 kΩ / 22 kΩ + 100 nF → 1 kΩ → E14; shield
  R1201 0 Ω fitted, R1202 1 MΩ and C1201 4.7 nF 2 kV DNP; SBU open.
- Qwiic: TCA9617B pins per datasheet (1 VCCA, 2 SCLA, 3 SDAA, 4 GND, 5 EN, 6 SDAB, 7 SCLB, 8 VCCB); A side on I2C1 with
  4.7 kΩ pull-ups (R1209/R1210, the only ones on that bus); EN = QWIIC_PWR_EN (J16) with R1211 10 kΩ pull-down; B side
  direct to J1202 pins 3/4 with 2.2 kΩ to QWIIC_PU behind bridged JP1201 from QWIIC_3V3. TPS2553DBV (1 IN, 2 GND, 3 EN,
  4 FAULT, 5 ILIM, 6 OUT): IN +3V3 with 1 µF, ILIM 150 kΩ, FAULT → 10 kΩ pull-up → 1 kΩ → C14, OUT QWIIC_3V3 with
  10 µF and 100 kΩ discharge; SRV05-4 on SDA/SCL with VP = QWIIC_3V3. J1202 order GND, 3V3, SDA, SCL.
- LED out: TPS2553DRV (1 OUT, 2 ILIM, 3 FAULT, 4 EN, 5 GND, 6 IN, 7 pad GND): IN +5V_BUCK with 1 µF, EN = LED_EN (H15)
  with 100 kΩ pull-down, ILIM 23.2 kΩ, FAULT → 10 kΩ → 1 kΩ → K16, OUT +5V_LED with 22 µF → BLM31KN601 → SMF6.0A →
  J1205.1; SN74LV1T125 ×2 (OE GND, A ← LED_DATA/LED_CLK, VCC +5V_LED with 100 nF each) → 47 Ω → PESD5V0S1BL → pins 3/4;
  pin 2 GND.
- Display: J1208 pins 1–8 → DISP_P1–8 → 47 Ω → F15, F16, B16, C16, C15, D16, E15, E16 (the `G-display.md` phase 2 order);
  every pin has a jumper to GND, to DISP_VCC and to DISP_BL_SW (24 jumpers), defaults bridged JP1204 (P1-GND),
  JP1205 (P2-VCC), JP1224 (P8-BL_SW); SRV05-4 ×2 with VP +3V3; DISP_VCC via BLM18PG221 + 1 µF. Backlight: AO3401A
  S = DISP_VCC, D = DISP_BL_SW, 100 kΩ G-S; 2N7002 G ← 100 Ω ← G15, 100 kΩ to GND.
- Knob header J1206: 1 KNOB_REF (100 Ω from ADC_AVDD, 1 µF), 2/12 GND, 3–6 KNOB1–4 (PESD, 1 kΩ, 100 nF at the ADC pins),
  7–10 ENC1A/B, ENC2A/B (PESD, 1 kΩ, 10 kΩ up, 10 nF), 11 +3V3 via 47 Ω.
- Debug: J1203 SWD 1 SWCLK, 2 GND, 3 SWDIO (33 Ω + PESD); J1204 UART 1 → UART0_RX (target RX), 2 GND, 3 ← UART0_TX
  (100 Ω + PESD) — the Debug Probe convention as recorded in `G-debug-jtag.md`.
- MPN/LCSC: C165948, C7519, C193402, C123790, C84374, C13612, C160404, C527429, C55266, C138719, C473338, C131334,
  C668306, C2763613, C492405, C492423, C27438, C80165, C15127, C8545, C2906768, C21189, C22935, C41017.

### Symbols and footprints (check 8)
- Project symbols checked pin-for-pin against the datasheet package: LFE5U-25F-7BG256I (CSV), RP2350B (QFN-80 figure),
  LAN8720AI (Table 2-8), VCXO_3225 (SX3V p. 2), PCM1808 (p. 5), T3902 (Table 9), HFD4 (wiring diagram p. 70),
  RCJ-01, NMJ6HCD2_F (KiCad footprint pads), BAV99_NXP and BAT54S_NXP (Table 2), TCA9617B, TPS2553 (DBV) and
  TPS2553DRV (DRV). Stock KiCad symbols used for AO3400A/AO3401A/2N7002 (1 G, 2 S, 3 D), BC847/BC857 (1 B, 2 E, 3 C),
  BCP56/BCP53 (1 B, 2 C, 3 E, 4 C), BAT54A (1 K1, 2 K2, 3 A), 74HC74-as-74LVC74, 74LVC2G34, 74LVC1G125-as-SN74LV1T125,
  USBLC6-2SC6, SRV05-4, ASE oscillator, Crystal_GND24 — all consistent with the datasheets.
- Custom footprints: caBGA-256 (256 pads, correct grid), RPi small-pad 0402 (2), AOTA inductor (2), YXC/SX3V 3225 (4),
  RCJ-01 (3 × pad 1 Ø2.6 at (±5, 0)/(0, −4.5), pad 2 Ø1.7), HFD4-S (8 pads, 3.2/2.2/2.2 pitch; see n-6), T3902 LGA-5
  (5 pads + NPTH; see n-3).

## Verdicts

| Block | Verdict | Reason |
|---|---|---|
| E (mcu, fpga, ethernet) | **PASS** | No blocker or major. n-2 cosmetic. |
| F (audio_out, audio_in) | **FAIL — fix and re-check** | B-1 shorts −15 V to GND through D1005/D1011; M-1 bypasses the HP ESD beads; m-1 PDM_CLK series R. |
| G (io) | **PASS with one minor** | m-2 TCA9617B VCCB bypass; n-5 text. |

## Fix verification (2026-11-08, re-exported netlist.xml / bom-sch.csv, 1261 components)

| Item | Status | Evidence in the netlist |
|---|---|---|
| B-1 D1005/D1011 pin 3 on GND | **CLOSED** | D1005.3 and D1011.3 are `unconnected-…`; pins 1/2 unchanged (base node / `-15V`). Swept every BAV99/BAT54x on the board: all middle pins are the intended signal node or NC (D1001/2/8/14/1103 clamps, D1003/9 spreaders, D1004/10 NC, D1016/18 gates, D1104/5 and D405/411/505/511 junctions). No rail or GND on a middle pin anywhere. |
| M-1 FB1001/FB1002 shorted | **CLOSED** | K1001.4 → `Net-(K1001-NO1)` → FB1001.1; FB1001.2 → `Net-(D1019-A1)` with D1019.1 and J1001.T only. Same for NO2/FB1002/D1020/J1001.R. Relay NO → bead → TVS + jack, as `F-esd.md` requires. |
| m-1 PDM_CLK series R | **CLOSED** | R1114 33 Ω (0603WAF330JT5E, C23140, note "place at ECP5 ball"): U801.L14 → R1114 → MK1101.4. The mic VDD filter resistor was renumbered; MK1101.5 still has its 10 Ω + 100 nF. |
| m-2 U1202 VCCB bypass | **CLOSED** | C1203 100 nF `Decouples=U1202.8`, C1204 100 nF `Decouples=U1202.1`; TPS2553 U1203 IN keeps its 1 µF (now C1205). |
| n-1 C1020 X5R | **CLOSED** | C1020 is now 10 µF 25 V X7R 1206, CC1206KKX7R8BB106 (C70462). |
| n-7 FG 1.0-3PWT vs KiCad SM03B footprint | **CLOSED** | `G-debug-jtag.md` "Phase 2: FG 1.0-3PWT land pattern check": drawing pads 0.60 × 1.55 at 1.00 mm, MP 1.20 × 1.80 at ±2.30 mm, 5.55 mm MP-to-pad span, matching the KiCad footprint used on J1203/J1204. Accepted on the audit's reading of the image-only drawing. |

Remaining notes n-2…n-6 are cosmetic/documentation and do not gate.

### Final verdicts

| Block | Verdict |
|---|---|
| E (mcu, fpga, ethernet) | **PASS** |
| F (audio_out, audio_in) | **PASS** (B-1, M-1, m-1, n-1 closed) |
| G (io) | **PASS** (m-2, n-7 closed) |
