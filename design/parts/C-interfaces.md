# Block C — secondary rails: topology, budget, interfaces

Phase 1 audit summary for block C (sheet `rails`). Per-part audits:
`C-5v-buck.md`, `C-5v-mux.md`, `C-3v3-1v1-bucks.md`, `C-2v5-ldo.md`, `C-3v3a-ldo.md`, `C-3v3q-ldo.md`, `C-vdrv-buck.md`,
`C-pm15-flybuck.md`, `C-pm15-ldos.md`, `C-sequencing.md`. All datasheets are in
`design/datasheets/` and listed in `design/datasheets/sources-CG.csv`. Checked 2026-11-07.

## Rail tree

```
VBUS 48 V (43–56 V working; 100 V parts throughout)
 ├─ U  LM5013 (100 V, 3.5 A non-sync COT)  → +5V_BUCK 5.05 V, ≤ 2.0 A design
 │     ├─ TPS2553 (1.1 A limit)           → +5V_LED  → JST PH LED connector   (off on USB)
 │     └─ TPS2116 power mux, VIN1 priority → +5V  (logic 5 V)
 │            VIN2 ← VUSB (USB-C)            ├─ TPS62A02AP (FPWM) → +3V3 (0.66 A design, 1 A peak, ±2.4 %)
 │                                           │     ├─ (PG_3V3 →) TPS7A9401 → +2V5 (ECP5 VCCAUX, 50 mA)
 │                                           │     └─ PG_3V3 → EN of 1V1 buck and 2V5 LDO
 │                                           ├─ TPS62A02AP (FPWM) → +1V1 = 1.101 V (ECP5 VCC, 400 mA, < 1 mV ripple)
 │                                           ├─ TPS7A2033P → +3V3_A (block D sense reference, 15 mA, always on)
│                                           └─ (relay coils, block F, 56 mA; block D 25 mA)
 ├─ U  LM5017 (100 V, 600 mA sync COT)     → VDRV 7.0 V, 200 mA design (LMG1210 VIN ×4)
 │     enabled only by VDRV_EN (firmware); TLV6703 → VDRV_PG
 └─ U  LM5017 Fly-Buck, 1:1 coupled L      → +18V4_PRE / −17V8_PRE
           ├─ TPS7A4901 → +15V (120 mA design, 62 mA avg)
           │     ├─ TPS7A4901 → +5V_A (≤ 15 mA, ADC analog / mic bias)
           │     └─ EN_UV of TPS7A9401 → +3V3_Q (35 mA, 0.46 µVrms; from +5V)
           └─ TPS7A3001 → −15V (110 mA design, 50 mA avg)
```

Every converter fed from VBUS is rated 100 V (LM5013, LM5017; their caps and diodes 100 V),
the same rating as the GaN FETs, so they survive anything the VBUS TVS lets through (block B).

## Part list (block C)

| Function | MPN | LCSC | Stock 2026-11-07 | Lib |
|---|---|---|---|---|
| 5 V buck (fsw ≈ 200 kHz, beat rule below) | LM5013DDAR (TI); LM5013QDDARQ(TOKMAS) is a **clone, not a second source** (unaudited) | C5383001 / (C7589228) | 11098 / 1334 | ext |
| 5 V buck inductor 47 µH | SRP1265A-470M (Bourns); alt MDA1365-470M (KOHER) | C840530 / C2847587 | 1561 / 2507 | ext |
| 5 V buck diode 100 V 5 A | SS5P10-M3/86A (Vishay); SS5P10-M3(TOKMAS) C52941004 is a clone (audit before use) | C46986 | 44365 | ext |
| 5 V power mux | TPS2116DRLR | C3235557 | 53288 | ext |
| 3V3 and 1V1 bucks (forced PWM) | TPS62A02APDDCR ×2 | C25687169 | 2304 | ext |
| 3V3/1V1 inductor 1.0 µH | SRP4020TA-1R0M (Bourns); 2nd MDA4020-1R0M (KOHER) | C913245 / C2847468 | 5040 / 1077 | ext |
| +2V5 LDO (ECP5 VCCAUX) | TPS7A9401DSCR (2nd instance) | C5220127 | 2441 | ext |
| 3V3_Q LDO (input +5V, enabled by +15V) | TPS7A9401DSCR | C5220127 | 2441 | ext |
| 3V3_A LDO (block D reference) | TPS7A2033PDBVR | C2862740 | 129111 | ext |
| VDRV buck | LM5017MRX/NOPB | C34355 | 12815 | ext |
| VDRV inductor 47 µH | SRN6045TA-470M (Bourns) | C5151734 | 4173 | ext |
| VDRV power-good | TLV6703DDCT | C2877614 | 538 | ext |
| ±15 V Fly-Buck | LM5017MRX/NOPB (second instance) | C34355 | 12815 | ext |
| Fly-Buck coupled inductor 68 µH 1:1 (3rd review: L tolerance) | PSSCAQ7048M-680M (PROD Tech; single source) | C56266204 | 932 | ext |
| Fly-Buck secondary diode | B1100-13-F (Diodes) | C110106 | 29855 | ext |
| +15 V and +5V_A LDOs | TPS7A4901DGNR ×2 | C16430 | 5633 | ext |
| −15 V LDO | TPS7A3001DGNR | C33835 | 5267 | ext |

Build quantity 5 boards: every line above has ≥ 40× the need except SRF0703-470M (second source
only) and TLV6703 (538, need 5).

## The ±15 V decision (R-33a)

**Chosen: an LM5017 Fly-Buck (isolated-buck topology, used non-isolated) from VBUS, 1:1 coupled
inductor, primary regulated at +18.0 V, secondary rectified to ≈ −17.4 V, then TPS7A4901 /
TPS7A3001 low-noise LDOs to ±15 V.** Assumes no aux winding on the forward transformer (block B).

Why:
- One controller and one 7.6 mm coupled inductor make both polarities. The secondary tracks the
  regulated primary (AN-2292 eq. 2: VOUT2 = N2/N1·VOUT1 − VF), so the negative rail needs no second
  loop. Its looser regulation (leakage, diode drop) is absorbed by the LDO headroom (≥ 2.3 V).
- Fed from VBUS, so the analog load stays off the 5 V buck and the USB path, and the rails are off
  on USB-only power (R-23) without extra switching.
- 100 V part, rated like the GaN. LM5017 is in stock (12815). The same IC is reused for VDRV, which
  cuts the BOM by one part type.
- The LDOs are 15–20 µVrms, 72 dB PSRR at 120 Hz, and above 55 dB from 10 Hz to 700 kHz
  (TPS7A30 datasheet, "Maximum AC performance"), which covers the ≈ 500 kHz Fly-Buck ripple.

Alternatives rejected:
- **Buck + separate inverting buck-boost from VBUS**: the inverter's switch sees VIN + |VOUT|
  ≈ 74 V. That needs a second 100 V converter and inductor, and it doesn't make the board simpler.
- **From +5V (SN6505B push-pull + transformer, or TPS65131-class boost/inverter)**: this puts
  ≈ 3.3 W (0.7 A) more on the 5 V buck and the mux, and needs a transformer (SN6505B: 1288 stock).
  TPS65131-class parts reach only ±15 V before post-regulation, so there is no LDO headroom.
- **Isolated DC-DC module (±15 V 3 W)**: its switching frequency and noise are unknown, it is a
  single source, and it costs more.
- **Capacitance multipliers instead of LDOs**: they give no regulation against Fly-Buck
  cross-regulation drift, so they are kept only as a block F option.

## Power budget (recomputed from these parts; average, worst case)

| Rail | Load | Converter efficiency (est.) | From its source |
|---|---|---|---|
| +3V3 | design **0.66 A** (block E 350 mA + Qwiic **100** (user cap; was 300) + display 40 + block D **85** (16 × TLV3502 incl. the short detector) + 2V5 LDO 50 + small consumers ≈ 30: block F PCM1808/T3902 10, block A ISO7740 VCC2 3.2, TCA9617B ICCB ≤ 7, knob pin 11 ≤ 10, PG buffers 1.4) = 2.18 W; typ 0.36 A with Qwiic unloaded | TPS62A02A ≈ 90 % | 2.42 W (typ 1.35 W) from +5V |
| +2V5 | 50 mA (from +3V3, inside the +3V3 line) | LDO | — |
| +1V1 | design 0.40 A × 1.10 V = 0.44 W; typ ≈ 0.25 A (block E estimate) | FPWM ≈ 82 % | 0.54 W (typ 0.34 W) from +5V |
| +3V3_Q | 0.035 A | LDO from 5 V | 0.18 W from +5V |
| +3V3_A (block D sense reference) | 0.015 A | TPS7A2033P from 5 V | 0.08 W from +5V |
| block D direct | +3V3 85 mA (16 comparators, logic; inside the +3V3 row), +5V 24 mA (post-filter sense) | — | 0.12 W from +5V (3V3 part counted above) |
| relay coils (block F) | 56 mA × 5 V | — | 0.28 W from +5V |
| +5V (mux out) | total | mux 40 mΩ | **3.82 W, 0.76 A design** (2.15 W typ), incl. block D and 3V3_A |
| +5V_LED | 1.0 A firmware limit at Class 8 (hardware 1.03–1.20 A) | TPS2553 + ferrite ≈ 97 % | 5.15 W |
| +5V_BUCK | 1.55 A (1.75 A at the hardware LED limit) | LM5013 ≈ 85 % (diode-dominated) | **9.3 W from VBUS at Class 8**; 5.7 W at Class 6 (2 W LEDs) |
| VDRV | **IGB070S10S1 (user, back again 2026-11-07): 48 mA at the 576 kHz baseline** (39 at 448 kHz, 57 at 768 kHz, 78 mA at 1 MHz); spec ≤ 150 mA kept for the IGC033 fallback (76 mA at 576 kHz) | LM5017 ≈ 85 % | **0.40 W** at baseline (0.65 W at 1 MHz) from VBUS |
| ±15 V (+5V_A fed from +15V) | avg +15 V 62 + 12 (5V_A) mA, −15 V 50 mA → 1.86 W + 0.39 W LDO loss (design 135/110 mA: 4.7 W) | Fly-Buck ≈ 85 % | **2.65 W avg** from VBUS |

Against R-33a at Class 8 (it assumes logic 2.9 W, gate drive 1.0 W, analog 2.8 W, LEDs 5.8 W;
12.5 W total), revised after the phase 1 review (5 V buck at ≈ 690 kHz, η ≈ 82 % at full load; IGC033
gate drive; block F's +5V_A as a separate load):
- **Worst case** (block E design loads, Qwiic loaded to 300 mA, LEDs 1 A, block D incl. ADS8353,
  relays, 1 MHz): (4.55 + 5.15)/0.82 = 11.85 W vs 8.7 W (**+3.15 W**, of which ≈ 1.3 W is the Qwiic
  load R-33a didn't list, ≈ 0.7 W block D's sensing, ≈ 0.4 W the ECP5, ≈ 0.4 W the higher buck
  frequency); gate drive 1.05 W (**+0.05 W**); analog 2.65 W (**−0.15 W**). **Net ≈ +3.05 W**, about
  2.7 W off the speaker average at 90 %.
- **Typical** (block E typ, Qwiic idle, 576 kHz PWM baseline, LEDs 1 A): (2.15 + 5.15)/0.84 = 8.7 W
  (0 W); gate 0.63 W (−0.37 W); analog −0.15 W. **Net ≈ −0.5 W.**
- The worst case stacks every design maximum at once. The single largest lever is the Qwiic 300 mA
  allowance (R-18): capping it at 100 mA by firmware saves ≈ 0.9 W.

## Interfaces this block offers (net names per architecture.md, plus new ones)

| Net | To | Spec |
|---|---|---|
| `+5V_BUCK` (new) | LED switch, mux VIN1 | 5.05 V ±1.5 %, ≤ 2.0 A |
| `+5V` | 3V3 and 1V1 bucks, 3V3_Q and 3V3_A LDOs, relays, block D | 5.05 V (buck) or VUSB (4.75–5.25 V), 0.76 A design, mux limit 2.5 A |
| `+3V3` | RP2350, ECP5 VCCIO (all banks, max 3.465 V), PHY, Qwiic switch, display, block D, +2V5 LDO | 3.318 V ±2.4 % (0.5 % divider), 0.66 A design (Qwiic capped at 100 mA), ≤ 1 A peak |
| `+1V1` | ECP5 VCC (no bead) | 1.101 V, 1.075–1.128 V worst case (spec 1.045–1.155 V incl. noise), 0.5 mV p-p ripple, 400 mA design |
| `+2V5` (new) | ECP5 VCCAUX (block E adds a 120 Ω bead + 10 µF) | 2.505 V ±1 %, 50 mA, 0.46 µVrms, ≈ 2 mV/µs ramp, up on USB power |
| `+3V3_A` (new) | block D INA241 ×4, OCP thresholds, ADS7042/ADS7038 AVDD | 3.30 V ±1.5 %, ≤ 15 mA, 7 µVrms, always on with +5V |
| `+3V3_Q` | block F reclock FFs | 3.30 V ±1.1 %, 35 mA design, 0.46 µVrms; PG_3V3Q → block E; **present only while +15V ≥ 7 V** (block F request); FFs need Ioff inputs |
| `VDRV` | LMG1210 VIN ×4 (block D) | **7.01–7.12 V typ, 6.87–7.27 V** (2nd review, Rr 360 kΩ) (Type III offset compensated, review M1), ≤ 200 mA design; block D spec 7.0 V ±5 %, ≤ 150 mA |
| `+15V` / `-15V` | block F | 14.94 V / −15.09 V; +15 V 120 mA design / 200 mA fault including +5V_A (block F; 135/215 mA kept as margin in the thermals), −15 V 110 / 190 mA; pre-rails +18.3–18.5 / −17.7…−17.9 V |
| `+5V_A` (new) | block F ADC analog, mic bias | 5.04 V, ≤ 15 mA, 15 µVrms, from +15V |
| `PG_5V` | TPS2116 PR1 **only** | 3.24 V when the buck is in regulation, 0 V otherwise. Not loaded by the FPGA (review B2) |
| `PG_5V_N` (new) | FPGA B3 | 2N7002 buffer of PG_5V, 4.7 kΩ to +3V3; **low = good**; ≥ 2.6 V against the 150 µA pull-down when not good |
| `PG_3V3` | 1V1 EN, 2V5 EN_UV **only** | open drain, 100 kΩ to +3V3. Not loaded by the FPGA (review B1) |
| `PG_3V3_N` (new) | FPGA B4 | 2N7002 buffer of PG_3V3, 4.7 kΩ to +3V3; **low = good** |
| `VDRV_EN` | from RP2350 (or FPGA) | active high, 3.3 V, 100 k pull-down: gate drive off by default |
| `VDRV_PG` | RP2350 GPIO33 | 4.7 k/2.7 k from VDRV via the TLV6703: 2.55 V good (2.34 V at the trip), 0 V absent; ≤ 3.39 V in an LM5017 OV event |
| `AN_OFF` | from RP2350 (optional) | active high forces ±15 V off; 100 k pull-down (on by default) |

## Proposed changes to architecture

1. **Split the 5 V rail into `+5V_BUCK` and `+5V`.** LEDs take `+5V_BUCK` (before the USB OR) via
   the TPS2553 current-limit switch, so LED current never flows through the mux and the LEDs are
   off on USB-only power by construction (R-23). Logic takes `+5V` (the mux output). New nets:
   `+5V_BUCK`, `+5V_LED`.
2. **Replace "two ideal diodes" (R-23) with one TPS2116 priority power mux.** A pair of LM66100
   ideal diodes cross-wired for ORing (their datasheet §9.2.1–9.2.2) turns *both* channels off when
   the two inputs sit at the same voltage, and a 5.05 V buck against a 4.75–5.25 V USB port will do
   that. The TPS2116 in priority mode always takes the buck when `PG_5V` is high, takes USB
   otherwise, blocks reverse current both ways, and takes no USB current while PoE is up, so a PC
   port is never loaded beyond its 500 mA when both are plugged in. It still meets R-23's intent
   (neither source back-feeds the other).
3. **VDRV is a dedicated 7.0 V rail from VBUS (LM5017) into each LMG1210's VIN pin**, not 5 V into
   VDD. LMG1210 VDD abs max is 5.5 V and its bypass-LDO range is 4.75–5.25 V. Running each driver on
   its own internal LDO (6–18 V in, 100 mA) isolates the four drivers from each other and from the
   noisy 5 V LED rail, and gate drive is impossible on USB power. Per-driver LDO loss is 82 mW at
   1 MHz.
4. **Gate drive is default-off in hardware.** The VDRV buck is enabled through its UVLO pin by
   `VDRV_EN`, which firmware asserts only after FPGA DONE, `PD_PG_N` low (good, active low, block A),
   `POE_LOSS_N` high (block B) and VBUS in range (see
   `C-sequencing.md`). `VDRV_PG` reports it back.
5. **Block E rails after the ECP5 switch (2026-11-07)**: `+1V1` (VCC) replaces `+1V2`; `+2V5` (VCCAUX,
   TPS7A9401 from +3V3) is new; `+1V8` is withdrawn. 3V3 and 1V1 use forced-PWM bucks
   (TPS62A02AP) for block E's ≤ 10 mV VCC/PLL ripple limit.
6. **New signals for block E's pin budget**: inputs `PG_5V`, `VDRV_PG`, `LED_FAULT_N`,
   `QWIIC_FAULT_N`; outputs `VDRV_EN`, `LED_EN`, `QWIIC_PWR_EN`, optional `AN_OFF`. These are
   slow, so RP2350 GPIO is fine. `VDRV_PG` should also go to the FPGA so the PWM gate is in logic,
   not firmware.

## Open questions

- Block F loads received 2026-11-07 (+15 V 120 mA design, −15 V 110 mA, 3V3_Q 30 mA, +5V_A 15 mA);
  Fly-Buck and LDOs resized (C-pm15-flybuck.md, C-pm15-ldos.md). 3V3_Q changed to TPS7A9401 for
  ≤ 5 µVrms in band and gated by +15V; block F's flip-flops need Ioff inputs.
- Block D (2026-11-07, after review): IGC033S10S1, 61 mA (448 kHz) / 68 / 88 / 127 mA (1 MHz) on
  VDRV, spec ≤ 150 mA. (The IGB070S10S1 figures, 42–79 mA, are superseded.) The 200 mA design is kept as margin. 3V3_A was added for block D's sensing.
- Block E (ECP5, 2026-11-07): +1V1 400 mA design and +2V5 50 mA. The typical 1V1 current is my
  estimate is ≈ 0.25 A (no power-calculator figure yet). +3V3 must stay ≤ 3.465 V (ECP5 VCCIO), so the 3V3 divider
  uses 0.5 % resistors.
- **VBUS TVS (agreed scheme, block B review m3):** SMCJ51A at the bulk and SMBJ51A at each bridge:
  51 V stand-off, 56.7–62.7 V breakdown, **82.4 V clamp** at rated pulse current. Re-check of every
  VBUS-fed block C part against 82.4 V plus overshoot (~10 %, ≈ 91 V):

| Part | Rating | Margin at 91 V | Result |
|---|---|---|---|
| LM5013 VIN, SW, EN/UVLO | 100 V abs | 9 V | OK |
| LM5017 ×2 VIN, UVLO, RON; SW ≤ VIN + 0.3 V | 100 V abs | 9 V | OK |
| CIN 100 V X7R (LM5013 2 × 4.7 µF 1210, LM5017 1 µF 1206 + 2.2 µF 1210, 100 nF 0603) | 100 V rated | 9 V transient | OK (surge only; 56 V continuous is at 56 % of rating) |
| SS5P10 (LM5013 diode) | VRRM 100 V | 9 V | OK for the transient; continuous 56 V meets the datasheet's 1.25 × VIN rule (70 V) |
| B1100 (Fly-Buck secondary, reverse ≈ VIN) | 100 V | ≈ 9 V | OK |
| PSSCAQ7048M coupled inductor | 600 V DC coil-to-coil | — | OK |
| UVLO dividers (1 MΩ, 125 kΩ) | **0805, 150 V working** | — | OK |
| Type 3 / Type III ripple resistors on SW (LM5013 RA 100 k, LM5017 Rr 499 k ×2) | **were 0603 75 V → now 0805 150 V** | — | **changed** (0603's 75 V working < 91 V) |

  The 85 V LMR38020 alternative stays ruled out (82.4 V clamp + overshoot > 85 V).

## Signal ownership agreed with block E (E-interfaces.md, ECP5 revision 2026-11-07)

- RP2350 direct: `VDRV_EN` GPIO36 (100 kΩ pull-down, block C); `VDRV_PG` GPIO33 (driven, no
  pull-up needed).
- FPGA inputs (3.3 V bank): `PG_5V_N` B3 and `PG_3V3_N` B4: **buffered, active-low copies** (2N7002 +
  4.7 kΩ to +3V3, block C) after review B1/B2, so the power-control nets themselves never touch an
  FPGA pin. Block E: invert in gateware; set PULLMODE = NONE on B3/B4/B5 after configuration; `LED_FAULT_N` K16 and `QWIIC_FAULT_N` C14 (10 kΩ
  to +3V3, **fitted by block C/G** at the TPS2553s); `VUSB_DET` E14 (3.12 V max divider by block G);
  `PG_3V3Q` → FPGA B5 (bank 0) through block E's 1 kΩ series, with block C's 100 kΩ pull-up.
- FPGA outputs: `LED_EN` H15, `QWIIC_PWR_EN` J16. ECP5 pins default to pull-down, and the 100 kΩ
  pull-downs at both TPS2553 EN pins stay as a backstop.
- The TCA9535 expander is dropped, so I2C address 0x20 is free again.


## Review response (phase 1 review, design/gates/review-phase1-CG.md, 2026-11-07)

**B1 (PG_3V3 deadlock), fixed.** `PG_3V3` (TPS62A02A PG, 100 kΩ) now drives only the 1V1 EN and
the 2V5 EN_UV. The FPGA gets `PG_3V3_N` from a 2N7002 buffer (gate on PG_3V3, 4.7 kΩ drain pull-up
to +3V3). The reviewer's alternative, a 4.7 kΩ direct pull-up, was rejected: PG VOL ≈ 0.3 V at
0.7 mA sits close to the TPS62A02A's 0.4 V EN-off threshold. C-3v3-1v1-bucks.md and
C-sequencing.md are updated.
**B2 (PG_5V → PR1 deadlock), fixed differently.** The reviewer's 5.62 k/10 k divider breaks the LM5013's
10–100 kΩ PGOOD pull-up range (pin table). Instead PGOOD's 56 k/100 k divider now feeds only TPS2116 PR1
(≤ 0.1 µA), and the FPGA reads `PG_5V_N` through a 2N7002 buffer (C-5v-buck.md).

**Sweep of every C/G net that controls power or strapping and touches an ECP5 or RP2350 pin.**
"Unconfigured" means the ECP5's 30–150 µA pull-down. "Unpowered" means the FPGA is off while the
net is live.

| Net | Pin | Controls | Unconfigured FPGA | Unpowered FPGA | Result |
|---|---|---|---|---|---|
| PG_3V3 | none now | 1V1 EN, 2V5 EN | not connected | — | fixed (B1) |
| PG_3V3_N | ECP5 B4 | nothing | 2.6–3.3 V or ≈ 0 V, valid | FPGA's VCCIO and the pull-up share +3V3 | OK |
| PG_5V | none now | TPS2116 PR1 | not connected | — | fixed (B2) |
| PG_5V_N | ECP5 B3 | nothing | valid, as above | as above | OK |
| PG_3V3Q | ECP5 B5 (1 kΩ) | nothing (DAC hold) | reads low → DAC held low (safe) | same rail | OK; PULLMODE NONE after configuration |
| LED_EN | ECP5 H15 | TPS2553 (LED) | pulled low → off (safe) | +3V3 off ⇒ no FPGA drive; 100 kΩ holds EN low while +5V_BUCK is up | OK |
| QWIIC_PWR_EN | ECP5 J16 | TPS2553 (Qwiic) and TCA9617B EN | **10 kΩ pull-down** (2nd review MAJOR-1): ≤ 0.25 V against the TCA9617B EN's internal pull-up (−25 µA) with J16 Hi-Z or the FPGA unpowered → off, isolated | as above | OK |
| DISP_BL_PWM | ECP5 G15 | backlight FET | low → off | as above | OK |
| LED_FAULT_N / QWIIC_FAULT_N | ECP5 K16 / C14 | nothing (status) | read 1.8–3.0 V: informational only | same rail | OK |
| VUSB_DET | ECP5 E14 | nothing (status) | 1.8–3.1 V: informational | ≤ 0.2 mA via 15 kΩ before +3V3 rises (≤ ±1 mA hot-socket) | OK |
| VDRV_EN | RP2350 GPIO36 | VDRV buck | (RP2350) 100 kΩ pull-down: off | off | OK |
| VDRV_PG | RP2350 GPIO33 | nothing | 4.7 k/3.0 k keeps it valid even with a 50 kΩ pull-down | VDRV can't be on without the RP2350 | OK (divider changed) |
| AN_OFF | not assigned (optional NMOS on the Fly-Buck UVLO) | ±15 V | gate pull-down → rails on (intended) | — | OK; fitted only if block E assigns a pin |
| PG_2V5 | not connected | — | — | — | — |

**M1 (LM5017 Type III offset), fixed.** Rr = 499 kΩ on both LM5017s (FB ripple 31–40 mV for VDRV and
39–65 mV for the Fly-Buck, ≥ 25 mV), with RFB top retuned: VDRV 46.4 kΩ → 7.00–7.02 V; Fly-Buck 137 kΩ
→ 18.30–18.49 V, secondary −17.7…−17.9 V. LDO thermals redone with DGN θJA 63.4 °C/W and +5V_A on
+15V: worst 109 °C (+15 V, 215 mA fault, 18.9 V in), 85 °C at design (C-pm15-ldos.md). Blocks D and F
have been told.
**M2 (TCA9617B EN floating), fixed.** EN driven from QWIIC_PWR_EN, plus a 100 kΩ discharge on
QWIIC_3V3 (G-qwiic.md).

MINORs:
- 5 V buck fsw moved to ≈ 690 kHz (RRON 20.0 kΩ, RA 100 kΩ), clear of 376–424/448/512 kHz products
  up to the 4th harmonic by ≥ 28 kHz. Cost: ≈ +0.4 W at full load. Retune if block D picks 672 kHz.
- LM5013 CIN: 2 × 4.7 µF 100 V 1210 (≥ 4.4 µF effective).
- TPS7A49 θJA 63.4 °C/W used; +5V_A is a separate +15 V load (135/215 mA).
- +3V3 small consumers listed; with block D's 85 mA, 0.86 A design.
- VDRV loads updated to IGC033S10S1: 62/128 mA → 0.51/1.05 W from VBUS.
- 1V1: 84.5 kΩ (E96) → 1.107 V (1.080–1.134 V). Block E has been told (its record says 1.10 V; the
  difference is +0.6 %).
- TPS7A94 start-up corrected: 2V5 ≈ 2.3 ms, 3V3_Q ≈ 14 ms (C-2v5-ldo.md, C-3v3q-ldo.md,
  C-sequencing.md).
- Tokmas LM5013 and SS5P10 are labelled clones, not second sources.
- SMF6.0A on +5V_LED (C123790); SMF5.0A stays on VUSB.

NOTEs:
- TPS2116 start-up blip: recorded in C-sequencing.md.
- VDRV_PG overvoltage: the new divider limits it to 3.62 V.
- Fly-Buck fault margin and ≈ 508 kHz: recorded.
- SRP1265A rated to +150 °C: corrected.
- LM5013 PGOOD rising up to VREF: accepted.
- SN74LV1T125 back-feed: a bring-up measurement in G-led-out.md.
- USB 100 mA pre-enumeration: recorded in G-usb-c.md.
- KNOB_REF: block E's open item, unchanged.
- PG_3V3Q pull-up stays 100 kΩ (RPG 10–100 kΩ).
- TPS62A02A footprint: TSOT-23-6, recorded.

**Additional (after the review, team lead / block A A-M1):** the PD status from block A is `PD_PG_N`,
**active low (low = PD power good, high = primary dead)**, not an active-high `PD_PG`. PoE loss is
also flagged by block B's `POE_LOSS_N` (block B's VBUS-droop comparator, VBUS < 40 V; open drain, active low). The sequencing
conditions in C-sequencing.md and decision 4 above are rewritten with these polarities. Block D's
+3V3 load rose to 85 mA: +3V3 is 0.86 A design and the worst-case budget net is ≈ +3.05 W.

**+5V at block F's relays (block F request, 2026-11-07):** ≥ 4.84 V worst case (buck ≥ 4.92 V with
0.5 % divider resistors, minus ≤ 18 mV trace, 55 mV TPS2116, 6 mV distribution), against ≥ 4.76 V.
On USB-only power the relays are off. Details are in C-5v-buck.md. Block D's PWM baseline is now
576 kHz (VDRV 76 mA, 0.63 W from VBUS); the worst case (1 MHz) is unchanged.

## Qwiic capped at 100 mA (user decision, 2026-11-07)

TPS2553 RILIM 150 kΩ → 155–207 mA limit (G-qwiic.md). +3V3 design 0.86 → **0.66 A**; +5V (mux)
0.91 → **0.76 A**, 3.82 W. Budget against R-33a at Class 8:
- **Worst case:** (3.82 + 5.15)/0.82 = 10.94 W vs 8.7 W (+2.24 W); gate +0.05 W; analog −0.15 W →
  **net ≈ +2.15 W** (was +3.05 W), ≈ 1.9 W off the speaker average.
- **Typical:** unchanged (Qwiic idle) → **net ≈ −0.5 W**.
- Relay +5V re-checked at the lower mux load: TPS2116 drop 0.76 A × 60 mΩ = 46 mV → coils
  **≥ 4.85 V** worst case (buck ≥ 4.92 V with 0.5 % divider, trace ≤ 18 mV, distribution ≤ 6 mV, AO3400A
  1.5 mV; HFD4 2 × 28–31 mA). This beats the 4.76 V requirement by about 90 mV; nothing else needs to change.

## GaN back to IGB070S10S1 (user via block D, 2026-11-07)

VDRV 48 mA at 576 kHz → 0.40 W from VBUS (1 MHz: 78 mA, 0.65 W). The 200 mA design and the ≤ 150 mA
spec are unchanged, to cover the IGC033 fallback. Budget against R-33a at Class 8, with Qwiic capped
at 100 mA:
- **Worst case:** logic + LEDs +2.24 W; gate 0.65 W (−0.35 W); analog −0.15 W → **net ≈ +1.75 W**.
- **Typical:** logic + LEDs 0 W; gate 0.40 W (−0.60 W); analog −0.15 W → **net ≈ −0.75 W**.
(Block D's amp idle draw on VBUS is now ≈ 3.8 W, block D's figure, outside block C's budget lines.)

## 5 V buck beat-frequency rule (team lead decision, 2026-11-07)

**Rule:** every product |a·f_buck − b·f| with a, b ≤ 2, against f = 576 kHz (amp PWM) and 737.28 kHz
(ACF, crystal-locked), stays ≥ 40 kHz (twice the audio band) across the buck's real frequency spread,
including COT variation with VIN and load.
**Reasoning (lead):** a beat is audible only if it reaches the amp output, by VBUS ripple
amplitude-modulating the open-loop PWM. In the ACF's clock-fail fallback (590–708 kHz free-running)
the gateware mutes the amp, so that band is excluded. The buck's ripple current reaches VBUS through
≈ 6 mF of bulk, so its products are tiny, and products above 2nd order are smaller still. No sync
redesign; the LM5013 stays.
**Result:** f_buck ≈ 200 kHz (RRON 69.8 kΩ, 47 µH SRP1265A-470M, RA 330 kΩ). Worst clearance is
116 kHz at ±15 % spread. VBUS ripple at 200 kHz ≈ 2.5 mV peak (−86 dB re 48 V). Products are out of
band by construction; a hypothetical in-band one would be ≈ 5 µVrms after the output filter, ≪ R-51's
150 µV (C-5v-buck.md, Revision 2). η back to ≈ 85 %. Budget against R-33a at Class 8 (Qwiic 100 mA,
IGB070): **worst ≈ +1.35 W, typical ≈ −0.85 W**.

### Correction to the beat rule's premise (2nd review m-2, 2026-11-07): recorded as an accepted residual

The lead's rule said products above 2nd order are smaller still. **That is wrong for these
converters.** The LM5013's input current is a ≈ 2 A pulse train at D ≈ 0.10, whose harmonics fall
only as sin(nπD)/n: 2nd 0.93×, 3rd 0.85×, 4th 0.74× the fundamental (≈ 0.40 A pk). Over the buck's
170–230 kHz spread, **3·f_buck crosses 576 kHz at f_buck ≈ 192 kHz** and 4·f_buck crosses 737.28 kHz at
184 kHz, so |3 f_buck − 576| can land anywhere in 0–114 kHz, including the audio band.
- Amplitude: ≈ 0.34 A pk on the bulk's ≈ 10 mΩ (ESL-dominated at 576 kHz) ≈ 3 mV on VBUS. In BD
  modulation the differential fsw component is DSB-SC (∝ modulation), so the spur appears as
  sidebands at f_audio ± δ at ≈ **−83 dBc (≈ 0.007 %) at full scale, zero at idle.**
- The Fly-Buck (LM5017, ≈ 0.5 A pk input pulses, real 347–620 kHz after Revision 3; fundamental and
  2nd harmonic sweep 576 kHz) gives ≈ **−94 dBc**. The VDRV buck (≈ 305 kHz, 230–410 kHz; only
  ≈ 48 mA) is smaller still.
- These are **within R-51** (THD+N ≤ 0.1 % at 1 W, ≤ 0.3 % at 50 W) and even the closed-loop 0.02 %
  goal. No part change. A free-running frequency that keeps all n ≤ 4 products clear doesn't exist for
  the LM5013 (its tON ≤ 1000 ns floor blocks the only clean band below ≈ 144 kHz). **Synchronising the
  converters to the 23.04 kHz grid (C-5v-buck.md, "Open: frequency plan") remains the rigorous fix**,
  logged as an option for a later variant.
- Clock-plan bands for block E: 5 V buck 170–230 kHz; VDRV 230–410 kHz; Fly-Buck 347–620 kHz.

### Second review (rereview-phase1-CGD.md) items, 2026-11-07
- MAJOR-1: `QWIIC_PWR_EN` pull-down 100 kΩ → **10 kΩ** (G-qwiic.md; sweep row updated).
- m-1: VDRV Rr → 360 kΩ, VDRV 7.01–7.12 V typ / 6.87–7.27 V; Fly-Buck RON → 330 kΩ, Rr → 390 kΩ (switch
  current margin at the slow TON corner); real frequency bands stated (C-vdrv-buck.md,
  C-pm15-flybuck.md Revision 3).
- m-2: premise corrected and the residual recorded above.
- m-4: LM5013 tON ≈ 886 ns at the 32.6 V UVLO-off corner (≤ 1000 ns ROC), recorded in C-5v-buck.md.
- n-5: VDRV_PG divider 4.7 k/**2.7 k** (fault 3.39 V; the review's 4.7 k/3.3 k gives 3.84 V by
  calculation).
- n-7: SMF6.0A leakage wording corrected. n-8: firmware note (≥ 3 s off before re-enabling Qwiic) in
  G-qwiic.md.
- Stale text fixed: +5V 0.76 A, +3V3 0.66 A; C-sequencing VDRV; C-3v3a-ldo LM5013 frequency.

### Third review (rereview2-phase1.md), 2026-11-07
- Fly-Buck isw(pk) with L −20 %: 0.71 A > 0.7 A → coupled inductor 68 µH PSSCAQ7048M-680M → 0.56 A (C-pm15-flybuck.md Rev. 4).
- Hold-up from block B's 40 V PoE-loss trip at 60 W / 6 mF: VBUS(20 ms) = 34.6 V. LM5013 UVLO-off lowered to
  ≤ 29.6 V (RUV2 52.3 kΩ, RRON 64.9 kΩ → ≈ 213 kHz, tON ≤ 984 ns), Fly-Buck to ≤ 29.4 V (RUV1 5.36 kΩ).
  Everything holds ≥ 36 ms (C-sequencing.md). Clock-plan band for the 5 V buck becomes ≈ 181–245 kHz.
